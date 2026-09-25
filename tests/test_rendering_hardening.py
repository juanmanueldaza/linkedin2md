import ast
import csv
import inspect
import io
import re
import zipfile
from importlib import import_module
from pathlib import Path
from urllib.parse import urlsplit

import pytest

import linkedin2md
import linkedin2md.cli as cli
import linkedin2md.formatters as formatters_package
from linkedin2md.contract import CONVERSION_CONTRACT
from linkedin2md.converter import LinkedInToMarkdownConverter, create_converter
from linkedin2md.formatters.base import BaseFormatter, SimpleListFormatter
from linkedin2md.protocols import BilingualText, SectionFormatter
from linkedin2md.registry import (
    DefaultFormatterRegistry,
    get_formatter_registry,
    get_parser_registry,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMATTER_ROOT = PROJECT_ROOT / "src" / "linkedin2md" / "formatters"

HTML_PAYLOAD = "<script>alert('xss')</script><img src=x onerror=alert(1)>"
MARKDOWN_PAYLOAD = (
    "INJECT_HEADING\n"
    "- INJECT_LIST\n"
    "1. INJECT_ORDER\n"
    "> INJECT_QUOTE\n"
    "| INJECT_TABLE |\n"
    "[safe](https://example.com/safe)"
)
CONTROL_PAYLOAD = "line\r\nnext\rthird\u2028fourth\u2029fifth\x00\x1f\x7f"
UNSAFE_URL = "javascript:alert(1)"
MALFORMED_URL = "https://example.com/%0A"
SAFE_URL = "https://example.com/safe?x=1#fragment"
UNICODE_PAYLOAD = "Café 東京 🚀 Ñandú"
ADVERSARIAL_BILINGUAL = BilingualText(
    en="English <b>*unsafe*</b>\r\nINJECT_HEADING",
    es="Español <i>Peligro</i>\n- INJECT_LIST",
)
ADVERSARIAL_SCALARS = (
    HTML_PAYLOAD,
    MARKDOWN_PAYLOAD,
    CONTROL_PAYLOAD,
    UNSAFE_URL,
    MALFORMED_URL,
    SAFE_URL,
    "C:\\path\\*literal*",
    UNICODE_PAYLOAD,
)

FORMATTER_CASES: dict[str, object] = {
    "profile": {
        "name": "Ada <b>Lovelace</b>",
        "title": ADVERSARIAL_BILINGUAL,
        "location": "London | *unsafe*",
        "email": "ada@example.com",
        "phone": "+44-20-0000-0000",
        "summary": BilingualText(
            en="English summary <b>*unsafe*</b>\nINJECT_HEADING",
            es="Resumen <i>seguro</i>\n- INJECT_LIST",
        ),
        "profile_meta": {
            "industry": HTML_PAYLOAD,
            "maiden_name": MARKDOWN_PAYLOAD,
            "public_profile_url": UNSAFE_URL,
            "address": CONTROL_PAYLOAD,
            "twitter": "[@ada](https://example.com/user)",
            "websites": [SAFE_URL, "plain.example/site"],
            "birth_date": "1815-12-10",
            "registered_at": "2024-01-01",
            "connections_count": 2,
        },
    },
    "skills": ["Python <b>", "*unsafe*", "Café 東京 🚀"],
    "experience": [
        {
            "company": HTML_PAYLOAD,
            "role": ADVERSARIAL_BILINGUAL,
            "start": CONTROL_PAYLOAD,
            "end": None,
            "location": "Remote | <em>unsafe</em>",
            "achievements": [{"text": ADVERSARIAL_BILINGUAL}],
        }
    ],
    "education": [
        {
            "institution": HTML_PAYLOAD,
            "degree": ADVERSARIAL_BILINGUAL,
            "field": "*Field* | <b>x</b>",
            "start": "2020",
            "end": "2024",
            "notes": BilingualText(en=MARKDOWN_PAYLOAD, es=CONTROL_PAYLOAD),
            "activities": "Club | line\r\nnext",
            "grade": "A+ <b>",
        }
    ],
    "certifications": [
        {
            "name": HTML_PAYLOAD,
            "issuer": MARKDOWN_PAYLOAD,
            "date": CONTROL_PAYLOAD,
            "url": UNSAFE_URL,
        }
    ],
    "languages": [{"name": "English | <b>", "proficiency": "*Native* <i>safe</i>"}],
    "projects": [
        {
            "title": HTML_PAYLOAD,
            "start": CONTROL_PAYLOAD,
            "end": "2024",
            "description": BilingualText(en=MARKDOWN_PAYLOAD, es=CONTROL_PAYLOAD),
            "url": UNSAFE_URL,
        }
    ],
    "recommendations": [
        {
            "author": HTML_PAYLOAD,
            "title": "*Recommendation*",
            "company": "Acme | <b>",
            "date": CONTROL_PAYLOAD,
            "text": BilingualText(en=MARKDOWN_PAYLOAD, es=HTML_PAYLOAD),
        }
    ],
    "recommendations_given": [
        {
            "recipient": HTML_PAYLOAD,
            "title": "*Recommendation*",
            "company": "Acme | <b>",
            "date": CONTROL_PAYLOAD,
            "text": BilingualText(en=MARKDOWN_PAYLOAD, es=HTML_PAYLOAD),
        }
    ],
    "endorsements": [
        {"skill": HTML_PAYLOAD, "endorser": "Ada | <b>", "date": CONTROL_PAYLOAD}
    ],
    "endorsements_given": [
        {"skill": HTML_PAYLOAD, "endorsee": "Grace | <b>", "date": CONTROL_PAYLOAD}
    ],
    "learning": [{"title": HTML_PAYLOAD, "completed_at": CONTROL_PAYLOAD}],
    "learning_reviews": [
        {"content": HTML_PAYLOAD, "rating": "*5* | <b>", "date": CONTROL_PAYLOAD}
    ],
    "connections": [
        {
            "name": HTML_PAYLOAD,
            "company": "Acme | <b>",
            "position": "*Engineer*",
            "connected_on": CONTROL_PAYLOAD,
        }
    ],
    "companies_followed": [{"name": HTML_PAYLOAD, "followed_on": CONTROL_PAYLOAD}],
    "members_followed": [
        {"name": HTML_PAYLOAD, "date": CONTROL_PAYLOAD, "status": "*Active* | <b>"}
    ],
    "invitations": [
        {
            "from": HTML_PAYLOAD,
            "to": "Grace | <b>",
            "sent_at": CONTROL_PAYLOAD,
            "direction": "*Incoming*",
        }
    ],
    "imported_contacts": [
        {"name": HTML_PAYLOAD, "emails": "a@example.com | <b>", "title": "*Engineer*"}
    ],
    "groups": [{"name": HTML_PAYLOAD, "url": SAFE_URL}],
    "posts": [
        {
            "date": CONTROL_PAYLOAD,
            "content": ADVERSARIAL_BILINGUAL,
            "url": UNSAFE_URL,
        }
    ],
    "comments": [
        {
            "date": CONTROL_PAYLOAD,
            "message": ADVERSARIAL_BILINGUAL,
            "url": UNSAFE_URL,
        }
    ],
    "reactions": [{"date": CONTROL_PAYLOAD, "type": HTML_PAYLOAD, "url": UNSAFE_URL}],
    "reposts": [{"date": CONTROL_PAYLOAD, "url": UNSAFE_URL}],
    "votes": [{"date": CONTROL_PAYLOAD, "option": HTML_PAYLOAD, "url": UNSAFE_URL}],
    "saved_items": [{"saved_at": CONTROL_PAYLOAD, "url": UNSAFE_URL}],
    "events": [
        {
            "name": HTML_PAYLOAD,
            "time": CONTROL_PAYLOAD,
            "status": "*Attended* | <b>",
            "url": UNSAFE_URL,
        }
    ],
    "media": [
        {
            "date": CONTROL_PAYLOAD,
            "description": HTML_PAYLOAD,
            "url": UNSAFE_URL,
        }
    ],
    "messages": [
        {
            "date": CONTROL_PAYLOAD,
            "from_name": HTML_PAYLOAD,
            "to_name": "Grace | <b>",
            "subject": "*Subject* <i>x</i>",
            "content": f"{HTML_PAYLOAD}\n{CONTROL_PAYLOAD}",
        }
    ],
    "scripts": [
        {
            "name": HTML_PAYLOAD,
            "date": CONTROL_PAYLOAD,
            "content": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}",
        }
    ],
    "articles": [
        {
            "title": HTML_PAYLOAD,
            "date": CONTROL_PAYLOAD,
            "author": "Ada | <b>",
            "summary": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}",
        }
    ],
    "job_applications": [
        {
            "date": CONTROL_PAYLOAD,
            "company": HTML_PAYLOAD,
            "title": "*Engineer* | <b>",
            "status": "Applied | <i>",
            "resume_used": "resume | <b>.pdf",
            "url": UNSAFE_URL,
        }
    ],
    "job_descriptions": [
        {
            "company": HTML_PAYLOAD,
            "title": "*Engineer* | <b>",
            "description": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}",
            "date_applied": CONTROL_PAYLOAD,
            "status": "Applied | <i>",
        }
    ],
    "saved_jobs": [
        {"date": CONTROL_PAYLOAD, "company": HTML_PAYLOAD, "title": "*Engineer*"}
    ],
    "job_preferences": {
        "locations": [ADVERSARIAL_SCALARS[index] for index in (0, 1, 2, 5, 6, 7)],
        "job_titles": [MARKDOWN_PAYLOAD, "*Engineer*"],
        "job_types": ["Full-time", "Contract | <i>"],
        "industries": [UNICODE_PAYLOAD],
        "open_to_recruiters": True,
        "dream_companies": [HTML_PAYLOAD, "Acme | <b>"],
    },
    "saved_job_answers": [
        {"question": HTML_PAYLOAD, "answer": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}"}
    ],
    "screening_responses": [
        {
            "unsafe_<key>": HTML_PAYLOAD,
            "question | <b>": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}",
        }
    ],
    "saved_job_alerts": [
        {"search_id": HTML_PAYLOAD, "query_context": MARKDOWN_PAYLOAD}
    ],
    "search_queries": [{"time": CONTROL_PAYLOAD, "query": HTML_PAYLOAD}],
    "logins": [
        {
            "date": CONTROL_PAYLOAD,
            "ip_address": "192.0.2.1 | <b>",
            "login_type": "*web* | <i>",
        }
    ],
    "security_challenges": [
        {
            "date": CONTROL_PAYLOAD,
            "ip_address": "192.0.2.1 | <b>",
            "country": "UK | <i>",
            "challenge_type": "*Captcha*",
        }
    ],
    "ads_clicked": [{"date": CONTROL_PAYLOAD, "ad_id": HTML_PAYLOAD}],
    "ad_targeting": {
        "unsafe_<key>": HTML_PAYLOAD,
        "industry | <b>": MARKDOWN_PAYLOAD,
        "locations": CONTROL_PAYLOAD,
    },
    "lan_ads": [
        {
            "date": CONTROL_PAYLOAD,
            "action": HTML_PAYLOAD,
            "ad_id": "*Ad* | <b>",
            "page_app": "Page | <i>",
        }
    ],
    "inferences": [
        {
            "category": HTML_PAYLOAD,
            "type": "*Type* | <b>",
            "description": MARKDOWN_PAYLOAD,
            "inference": CONTROL_PAYLOAD,
        }
    ],
    "receipts": [
        {
            "date": CONTROL_PAYLOAD,
            "description": HTML_PAYLOAD,
            "amount": "*10* | <b>",
            "currency": "USD | <i>",
        }
    ],
    "service_engagements": [
        {
            "date": CONTROL_PAYLOAD,
            "marketplace_type": HTML_PAYLOAD,
            "amount": "*100* | <b>",
            "currency": "USD | <i>",
        }
    ],
    "service_opportunities": [
        {
            "date": CONTROL_PAYLOAD,
            "category": HTML_PAYLOAD,
            "location": "*Remote* | <b>",
            "status": "Open | <i>",
            "questions_answers": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}",
        }
    ],
    "verifications": [
        {
            "first_name": HTML_PAYLOAD,
            "middle_name": "N/A",
            "last_name": "Lovelace | <b>",
            "verification_type": "*Identity*",
            "document_type": "Passport | <i>",
            "provider": "Example | <b>",
            "verified_date": CONTROL_PAYLOAD,
            "expiry_date": "N/A",
        }
    ],
    "identity_assets": [{"name": HTML_PAYLOAD, "has_content": True}],
    "causes": [{"name": HTML_PAYLOAD}],
    "interests": [{"name": MARKDOWN_PAYLOAD}],
    "courses": [{"name": HTML_PAYLOAD, "school": "MIT | <b>"}],
    "honors_awards": [
        {
            "title": HTML_PAYLOAD,
            "issuer": "*Issuer* | <b>",
            "date": CONTROL_PAYLOAD,
            "description": MARKDOWN_PAYLOAD,
        }
    ],
    "test_scores": [
        {"name": HTML_PAYLOAD, "score": "*100* | <b>", "date": CONTROL_PAYLOAD}
    ],
    "patents": [
        {
            "title": HTML_PAYLOAD,
            "status": "*Granted* | <b>",
            "number": "123 | <i>",
            "date": CONTROL_PAYLOAD,
        }
    ],
    "organizations": [
        {"name": HTML_PAYLOAD, "title": "*Member* | <b>", "date": CONTROL_PAYLOAD}
    ],
    "publications": [
        {
            "title": HTML_PAYLOAD,
            "publisher": "*Publisher* | <b>",
            "date": CONTROL_PAYLOAD,
            "url": SAFE_URL,
        }
    ],
    "volunteer_experience": [
        {
            "role": HTML_PAYLOAD,
            "organization": "*Org* | <b>",
            "cause": MARKDOWN_PAYLOAD,
            "start_date": CONTROL_PAYLOAD,
            "end_date": "2024",
        }
    ],
    "contact_settings": [{"setting": HTML_PAYLOAD, "value": MARKDOWN_PAYLOAD}],
    "data_export_history": [
        {"requested_at": CONTROL_PAYLOAD, "completed_at": HTML_PAYLOAD}
    ],
    "deletion_history": [{"action": HTML_PAYLOAD, "date": CONTROL_PAYLOAD}],
    "who_viewed_profile": [{"date": CONTROL_PAYLOAD, "viewer": HTML_PAYLOAD}],
    "linkedin_salary": [
        {"company": HTML_PAYLOAD, "title": "*Engineer* | <b>", "salary": "100 | <i>"}
    ],
    "profile_for_business": [{"company": HTML_PAYLOAD, "title": "*Owner* | <b>"}],
    "profile_summary": [{"summary": f"{MARKDOWN_PAYLOAD}\r\n{HTML_PAYLOAD}"}],
}

TABLE_LINK_KEYS = frozenset({"reactions", "reposts", "votes", "saved_items", "media"})
TABLE_FORMATTER_KEYS = frozenset(
    {
        "search_queries",
        "logins",
        "security_challenges",
        "ads_clicked",
        "lan_ads",
        "inferences",
        "reactions",
        "reposts",
        "votes",
        "saved_items",
        "events",
        "media",
        "job_applications",
        "saved_jobs",
        "learning_reviews",
        "connections",
        "members_followed",
        "invitations",
        "imported_contacts",
        "groups",
        "receipts",
        "endorsements",
        "endorsements_given",
        "service_engagements",
        "contact_settings",
        "data_export_history",
        "deletion_history",
        "who_viewed_profile",
        "linkedin_salary",
        "profile_for_business",
        "profile_summary",
        "causes",
        "interests",
        "courses",
        "honors_awards",
        "test_scores",
        "patents",
        "organizations",
        "publications",
        "volunteer_experience",
    }
)

EXPECTED_CONTRACT_KEYS = (
    "profile",
    "skills",
    "experience",
    "education",
    "certifications",
    "languages",
    "projects",
    "recommendations",
    "recommendations_given",
    "endorsements",
    "endorsements_given",
    "learning",
    "learning_reviews",
    "connections",
    "companies_followed",
    "members_followed",
    "invitations",
    "imported_contacts",
    "groups",
    "posts",
    "comments",
    "reactions",
    "reposts",
    "votes",
    "saved_items",
    "events",
    "media",
    "messages",
    "scripts",
    "articles",
    "job_applications",
    "job_descriptions",
    "saved_jobs",
    "job_preferences",
    "saved_job_answers",
    "screening_responses",
    "saved_job_alerts",
    "search_queries",
    "logins",
    "security_challenges",
    "ads_clicked",
    "ad_targeting",
    "lan_ads",
    "inferences",
    "receipts",
    "service_engagements",
    "service_opportunities",
    "verifications",
    "identity_assets",
    "causes",
    "interests",
    "courses",
    "honors_awards",
    "test_scores",
    "patents",
    "organizations",
    "publications",
    "volunteer_experience",
    "contact_settings",
    "data_export_history",
    "deletion_history",
    "who_viewed_profile",
    "linkedin_salary",
    "profile_for_business",
    "profile_summary",
)

EXPECTED_RUNTIME_FORMATTER_KEYS = (
    "search_queries",
    "logins",
    "security_challenges",
    "ads_clicked",
    "ad_targeting",
    "lan_ads",
    "inferences",
    "posts",
    "comments",
    "reactions",
    "reposts",
    "votes",
    "saved_items",
    "events",
    "media",
    "messages",
    "scripts",
    "articles",
    "verifications",
    "identity_assets",
    "job_applications",
    "saved_jobs",
    "job_preferences",
    "saved_job_answers",
    "screening_responses",
    "saved_job_alerts",
    "job_descriptions",
    "learning",
    "learning_reviews",
    "connections",
    "companies_followed",
    "members_followed",
    "invitations",
    "imported_contacts",
    "groups",
    "receipts",
    "contact_settings",
    "data_export_history",
    "deletion_history",
    "who_viewed_profile",
    "linkedin_salary",
    "profile_for_business",
    "profile_summary",
    "skills",
    "experience",
    "education",
    "certifications",
    "languages",
    "projects",
    "profile",
    "causes",
    "interests",
    "courses",
    "honors_awards",
    "test_scores",
    "patents",
    "organizations",
    "publications",
    "volunteer_experience",
    "recommendations",
    "recommendations_given",
    "endorsements",
    "endorsements_given",
    "service_engagements",
    "service_opportunities",
)

EXPECTED_ROOT_EXPORTS = {
    "__version__",
    "LinkedInToMarkdownConverter",
    "create_converter",
    "ConversionReport",
    "ConversionResult",
    "DiagnosticEvent",
    "StrictConversionError",
    "CONVERSION_CONTRACT",
    "ConversionContract",
    "SectionSpec",
    "DEFAULT_EXTRACTION_LIMITS",
    "ExtractionLimitError",
    "ExtractionLimits",
    "OutputLimitError",
    "UnsafeArchiveError",
    "BilingualText",
    "DataExtractor",
    "FormatterRegistry",
    "LanguageDetector",
    "OutputWriter",
    "ParserRegistry",
    "SectionFormatter",
    "SectionParser",
    "get_formatter_registry",
    "get_parser_registry",
    "register_formatter",
    "register_parser",
}

EXPECTED_FORMATTER_EXPORTS = {
    "BaseFormatter",
    "ProfileFormatter",
    "SkillsFormatter",
    "ExperienceFormatter",
    "EducationFormatter",
    "CertificationsFormatter",
    "LanguagesFormatter",
    "ProjectsFormatter",
    "RecommendationsFormatter",
    "RecommendationsGivenFormatter",
    "EndorsementsFormatter",
    "EndorsementsGivenFormatter",
    "LearningFormatter",
    "LearningReviewsFormatter",
    "ConnectionsFormatter",
    "CompaniesFollowedFormatter",
    "MembersFollowedFormatter",
    "InvitationsFormatter",
    "ImportedContactsFormatter",
    "GroupsFormatter",
    "PostsFormatter",
    "CommentsFormatter",
    "ReactionsFormatter",
    "RepostsFormatter",
    "VotesFormatter",
    "SavedItemsFormatter",
    "EventsFormatter",
    "MediaFormatter",
    "MessagesFormatter",
    "ScriptFormatter",
    "ArticlesFormatter",
    "JobDescriptionFormatter",
    "JobApplicationsFormatter",
    "SavedJobsFormatter",
    "JobPreferencesFormatter",
    "SavedJobAnswersFormatter",
    "ScreeningResponsesFormatter",
    "SavedJobAlertsFormatter",
    "SearchQueriesFormatter",
    "LoginsFormatter",
    "SecurityChallengesFormatter",
    "AdsClickedFormatter",
    "AdTargetingFormatter",
    "LanAdsFormatter",
    "InferencesFormatter",
    "ReceiptsFormatter",
    "ServiceEngagementsFormatter",
    "ServiceOpportunitiesFormatter",
    "VerificationsFormatter",
    "IdentityAssetsFormatter",
    "CausesFormatter",
    "InterestsFormatter",
    "CoursesFormatter",
    "HonorsAwardsFormatter",
    "TestScoresFormatter",
    "PatentsFormatter",
    "OrganizationsFormatter",
    "PublicationsFormatter",
    "VolunteerExperienceFormatter",
    "ContactSettingsFormatter",
    "DataExportHistoryFormatter",
    "DeletionHistoryFormatter",
    "WhoViewedProfileFormatter",
    "LinkedInSalaryFormatter",
    "ProfileForBusinessFormatter",
    "ProfileSummaryFormatter",
}

POLICY_METHODS = {
    "_escape_inline",
    "_escape_block",
    "_escape_heading",
    "_escape_list_item",
    "_escape_joined",
    "_escape_link_label",
    "_escape_table_cell",
    "_validated_markdown_url",
    "_render_link",
    "_render_table_link",
    "_blockquote",
    "_escape_pipe",
    "_sanitize_url",
    "_get_text",
}
PROHIBITED_WRAPPERS = {"_escape_pipe", "_sanitize_url"}
HTML_TAG = re.compile(r"<[A-Za-z][^>]*>")
MARKDOWN_LINK = re.compile(r"(?<!\\)\[[^\]\n]*\]\(([^)\n]*)\)")
EMPTY_LINK = re.compile(r"\]\(\s*\)")
UNSAFE_LINK = re.compile(r"(?i)(?:javascript|data|file|vbscript|http\+unix):")


class _ProbeFormatter(BaseFormatter):
    @property
    def section_key(self) -> str:
        return "probe"

    def _format_content(self, data: object, lang: str) -> str:
        return ""


def _runtime_formatter_list() -> list[SectionFormatter]:
    registry = get_formatter_registry()
    registry.instantiate_all()
    return registry.get_all()


def _runtime_formatters() -> dict[str, SectionFormatter]:
    return {formatter.section_key: formatter for formatter in _runtime_formatter_list()}


def _call_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if isinstance(child.func, ast.Attribute):
            names.add(child.func.attr)
        elif isinstance(child.func, ast.Name):
            names.add(child.func.id)
    return names


def _assert_inert(output: str) -> None:
    assert output
    assert HTML_TAG.search(output) is None
    assert "\x00" not in output
    assert "\r" not in output
    assert "\u2028" not in output
    assert "\u2029" not in output
    assert EMPTY_LINK.search(output) is None
    assert UNSAFE_LINK.search(output) is None
    assert not re.search(
        r"(?m)^\s{0,3}(?:#{1,6}|>|[-+]|\d+[.)])\s+(?:INJECT_|safe\))",
        output,
    )
    for destination in MARKDOWN_LINK.findall(output):
        assert destination.strip()
        assert urlsplit(destination).scheme.lower() in {"http", "https", "mailto"}
        assert not any(character.isspace() for character in destination)


def _table_column_count(line: str) -> int:
    return re.sub(r"\\\|", "", line).count("|") + 1


def _assert_table_shape(output: str) -> None:
    table_lines = [
        line
        for line in output.splitlines()
        if line.startswith("|") and line.endswith("|")
    ]
    assert len(table_lines) >= 2
    data_lines = [
        line for line in table_lines if not all(char in "-:| " for char in line)
    ]
    assert data_lines
    assert len({_table_column_count(line) for line in data_lines}) == 1


def _table_attack_rows(section_key: str) -> list[dict[str, object]]:
    case = FORMATTER_CASES[section_key]
    assert isinstance(case, list)
    assert case
    first = case[0]
    assert isinstance(first, dict)
    fields = tuple(first)
    attack: dict[str, object] = {
        field: f"{field}|cell\r\nnext <b>*markdown*</b> [safe](https://example.com/x)"
        for field in fields
    }
    if section_key in TABLE_LINK_KEYS:
        attack["url"] = UNSAFE_URL
    empty: dict[str, object] = {field: None for field in fields}
    blank: dict[str, object] = {field: "" for field in fields}
    return [attack, empty, blank]


def _csv_text(fields: list[str], rows: list[dict[str, object]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _write_export(
    path: Path, files: dict[str, tuple[list[str], list[dict[str, object]]]]
) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, (fields, rows) in files.items():
            archive.writestr(name, _csv_text(fields, rows))


def test_source_audit_and_formatter_inventory() -> None:
    base_path = FORMATTER_ROOT / "base.py"
    source_paths = sorted(FORMATTER_ROOT.rglob("*.py"))
    assert base_path in source_paths

    prohibited: list[tuple[str, int, str]] = []
    duplicate_policy: list[tuple[str, str]] = []
    for source_path in source_paths:
        if source_path == base_path:
            continue
        tree = ast.parse(
            source_path.read_text(encoding="utf-8"), filename=str(source_path)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in PROHIBITED_WRAPPERS
                ):
                    prohibited.append((source_path.name, node.lineno, node.func.attr))
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id in PROHIBITED_WRAPPERS
                ):
                    prohibited.append((source_path.name, node.lineno, node.func.id))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in POLICY_METHODS:
                    duplicate_policy.append((source_path.name, node.name))

    assert not prohibited
    assert not duplicate_policy

    base_tree = ast.parse(
        base_path.read_text(encoding="utf-8"), filename=str(base_path)
    )
    extraction_methods = [
        node
        for node in ast.walk(base_tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_get_text"
    ]
    assert len(extraction_methods) == 1
    assert not (_call_names(extraction_methods[0]) & POLICY_METHODS)
    raw_value = "<b>*raw*</b>"
    assert _ProbeFormatter()._get_text(raw_value, "en") == raw_value

    registry_keys = tuple(
        formatter.section_key for formatter in _runtime_formatter_list()
    )
    assert registry_keys == EXPECTED_RUNTIME_FORMATTER_KEYS
    assert len(registry_keys) == len(set(registry_keys)) == 65
    assert set(registry_keys) == set(CONVERSION_CONTRACT.formatter_keys)
    assert set(FORMATTER_CASES) == set(CONVERSION_CONTRACT.formatter_keys)


@pytest.mark.parametrize("section_key", CONVERSION_CONTRACT.formatter_keys)
def test_registry_adversarial_corpus(section_key: str) -> None:
    formatter = _runtime_formatters()[section_key]
    output = formatter.format(FORMATTER_CASES[section_key], "es")
    assert output
    _assert_inert(output)
    assert HTML_PAYLOAD not in output
    assert MARKDOWN_PAYLOAD not in output


def test_adversarial_corpus_has_exact_contract_key_set() -> None:
    assert len(FORMATTER_CASES) == 65
    assert set(FORMATTER_CASES) == set(CONVERSION_CONTRACT.formatter_keys)
    assert len(CONVERSION_CONTRACT.formatter_keys) == len(
        set(CONVERSION_CONTRACT.formatter_keys)
    )


def test_benign_links_plain_urls_unicode_and_labels() -> None:
    post_output = _runtime_formatters()["posts"].format(
        [
            {
                "date": "2024-01-01",
                "content": BilingualText(en="A post", es="Una publicación"),
                "url": SAFE_URL,
            }
        ],
        "en",
    )
    assert "[View Post](https://example.com/safe?x=1#fragment)" in post_output
    assert "A post" in post_output

    group_output = _runtime_formatters()["groups"].format(
        [{"name": "Example Group", "url": SAFE_URL}], "en"
    )
    assert "| Example Group | https://example.com/safe?x=1#fragment |" in group_output
    assert "](https://example.com/safe?x=1#fragment)" not in group_output

    invalid_group_output = _runtime_formatters()["groups"].format(
        [{"name": "Unsafe", "url": UNSAFE_URL}], "en"
    )
    assert UNSAFE_URL not in invalid_group_output

    profile_output = _runtime_formatters()["profile"].format(
        {
            "name": "José García",
            "title": BilingualText(en="Engineer", es="Ingeniero"),
            "email": "jose@example.com",
            "phone": "",
            "location": "México / Café",
            "summary": BilingualText(en="Builds useful things.", es="Construye cosas."),
            "profile_meta": {
                "websites": [SAFE_URL],
                "twitter": "@jose",
            },
        },
        "es",
    )
    assert "# José García" in profile_output
    assert "**Ingeniero**" in profile_output
    assert "Construye cosas." in profile_output
    assert "México / Café" in profile_output
    assert f"**Website:** {SAFE_URL}" in profile_output
    assert "## Summary" in profile_output

    invalid_profile_output = _runtime_formatters()["profile"].format(
        {
            "name": "Unsafe",
            "title": BilingualText(),
            "profile_meta": {"websites": [UNSAFE_URL]},
        },
        "en",
    )
    assert UNSAFE_URL not in invalid_profile_output

    experience_output = _runtime_formatters()["experience"].format(
        [
            {
                "company": "First Company",
                "role": BilingualText(en="Engineer", es="Ingeniero"),
                "start": "2020",
                "end": None,
                "location": "Remote",
                "achievements": [],
            },
            {
                "company": "Second Company",
                "role": BilingualText(en="Manager", es="Gerente"),
                "start": "2022",
                "end": "2024",
                "location": "London",
                "achievements": [],
            },
        ],
        "en",
    )
    assert experience_output.index("## First Company") < experience_output.index(
        "## Second Company"
    )
    assert "Present" in experience_output

    labels_output = _runtime_formatters()["comments"].format(
        [
            {
                "date": "2024-01-01",
                "message": BilingualText(en="A comment", es="Un comentario"),
                "url": SAFE_URL,
            }
        ],
        "en",
    )
    assert "**2024-01-01**" in labels_output
    assert "> A comment" in labels_output
    assert "[View](https://example.com/safe?x=1#fragment)" in labels_output


def test_benign_filenames_follow_registry_order(tmp_path: Path) -> None:
    zip_path = tmp_path / "benign.zip"
    _write_export(
        zip_path,
        {
            "Profile.csv": (
                ["First Name", "Last Name", "Headline"],
                [
                    {
                        "First Name": "Ada",
                        "Last Name": "Lovelace",
                        "Headline": "Engineer",
                    }
                ],
            ),
            "Skills.csv": (["Name"], [{"Name": "Python"}]),
            "Groups.csv": (
                ["Group Name", "Group URL"],
                [{"Group Name": "Example", "Group URL": SAFE_URL}],
            ),
            "Connections.csv": (
                ["First Name", "Last Name"],
                [{"First Name": "Grace", "Last Name": "Hopper"}],
            ),
        },
    )
    files = create_converter(zip_path, tmp_path / "output").convert(lang="en")
    produced = {path.name for path in files}
    assert produced == {"profile.md", "skills.md", "groups.md", "connections.md"}
    expected_order = [
        f"{key}.md"
        for key in EXPECTED_RUNTIME_FORMATTER_KEYS
        if f"{key}.md" in produced
    ]
    assert [path.name for path in files] == expected_order
    assert all(path.suffix == ".md" for path in files)


@pytest.mark.parametrize("section_key", sorted(TABLE_FORMATTER_KEYS))
def test_all_table_formatters_preserve_column_count(section_key: str) -> None:
    formatter = _runtime_formatters()[section_key]
    output = formatter.format(_table_attack_rows(section_key), "en")
    assert output
    _assert_table_shape(output)
    _assert_inert(output)
    if section_key in TABLE_LINK_KEYS:
        assert UNSAFE_URL not in output
        assert MARKDOWN_LINK.search(output) is None


def test_table_formatter_inventory_is_complete() -> None:
    formatters = _runtime_formatters()
    simple_keys = {
        key
        for key, formatter in formatters.items()
        if isinstance(formatter, SimpleListFormatter)
    }
    direct_keys = {
        key
        for key, formatter in formatters.items()
        if not isinstance(formatter, SimpleListFormatter)
        and (
            "_escape_table_cell" in inspect.getsource(type(formatter))
            or "_render_table_link" in inspect.getsource(type(formatter))
        )
    }
    assert set(TABLE_FORMATTER_KEYS) == simple_keys | direct_keys
    assert len(TABLE_FORMATTER_KEYS) == 40


def test_malicious_zip_is_inert_end_to_end(tmp_path: Path) -> None:
    attack = f"{HTML_PAYLOAD}\n{MARKDOWN_PAYLOAD}\r\n{CONTROL_PAYLOAD}"
    export_files: dict[str, tuple[list[str], list[dict[str, object]]]] = {
        "Profile.csv": (
            [
                "First Name",
                "Last Name",
                "Headline",
                "Summary",
                "Industry",
                "Geo Location",
                "Twitter Handles",
                "Websites",
                "Public Profile URL",
                "Address",
                "Birth Date",
            ],
            [
                {
                    "First Name": "Ada",
                    "Last Name": "Lovelace",
                    "Headline": HTML_PAYLOAD,
                    "Summary": attack,
                    "Industry": "*Industry* | <b>",
                    "Geo Location": "London\r\nINJECT_HEADING",
                    "Twitter Handles": "[@ada](https://example.com/user)",
                    "Websites": SAFE_URL,
                    "Public Profile URL": UNSAFE_URL,
                    "Address": CONTROL_PAYLOAD,
                    "Birth Date": "1815-12-10",
                }
            ],
        ),
        "Positions.csv": (
            [
                "Company Name",
                "Title",
                "Description",
                "Location",
                "Started On",
                "Finished On",
            ],
            [
                {
                    "Company Name": "Acme | <b>",
                    "Title": "*Engineer*",
                    "Description": attack,
                    "Location": "Remote\r\nINJECT_HEADING",
                    "Started On": "2020-01-01",
                    "Finished On": "2024-01-01",
                }
            ],
        ),
        "Education.csv": (
            [
                "School Name",
                "Degree Name",
                "Start Date",
                "End Date",
                "Notes",
                "Activities",
                "Field of Study",
                "Grade",
            ],
            [
                {
                    "School Name": "University | <b>",
                    "Degree Name": "*Computing*",
                    "Start Date": "2010-01-01",
                    "End Date": "2014-01-01",
                    "Notes": attack,
                    "Activities": "Club | <i>\r\nnext",
                    "Field of Study": "*Software*",
                    "Grade": "A+ | <b>",
                }
            ],
        ),
        "Certifications.csv": (
            ["Name", "Url", "Authority", "Started On", "Finished On", "License Number"],
            [
                {
                    "Name": "Certificate | <b>",
                    "Url": UNSAFE_URL,
                    "Authority": "Authority | <i>",
                    "Started On": "2020-01-01",
                    "Finished On": "2024-01-01",
                    "License Number": "ID | <b>",
                }
            ],
        ),
        "Projects.csv": (
            ["Title", "Description", "Url", "Started On", "Finished On"],
            [
                {
                    "Title": "Project | <b>",
                    "Description": attack,
                    "Url": UNSAFE_URL,
                    "Started On": "2020-01-01",
                    "Finished On": "2024-01-01",
                }
            ],
        ),
        "Shares.csv": (
            ["Date", "ShareLink", "ShareCommentary"],
            [
                {
                    "Date": "2024-01-01",
                    "ShareLink": UNSAFE_URL,
                    "ShareCommentary": attack,
                }
            ],
        ),
        "Comments.csv": (
            ["Date", "Link", "Message"],
            [{"Date": "2024-01-01", "Link": UNSAFE_URL, "Message": attack}],
        ),
        "Reactions.csv": (
            ["Date", "Type", "Link"],
            [{"Date": "2024-01-01", "Type": "*LIKE* | <b>", "Link": UNSAFE_URL}],
        ),
        "InstantReposts.csv": (
            ["Date", "Link"],
            [{"Date": "2024-01-01", "Link": UNSAFE_URL}],
        ),
        "Votes.csv": (
            ["Date", "OptionText", "Link"],
            [{"Date": "2024-01-01", "OptionText": "Yes | <b>", "Link": UNSAFE_URL}],
        ),
        "Saved Items.csv": (
            ["savedItem", "CreatedTime"],
            [{"savedItem": UNSAFE_URL, "CreatedTime": attack}],
        ),
        "Rich Media.csv": (
            ["Date/Time", "Media Link", "Media Description"],
            [
                {
                    "Date/Time": "2024-01-01",
                    "Media Link": UNSAFE_URL,
                    "Media Description": attack,
                }
            ],
        ),
        "Groups.csv": (
            ["Group Name", "Group URL"],
            [{"Group Name": "Group | <b>", "Group URL": SAFE_URL}],
        ),
        "SearchQueries.csv": (
            ["Time", "Search Query"],
            [{"Time": "2024-01-01", "Search Query": attack}],
        ),
        "Connections.csv": (
            ["First Name", "Last Name", "URL", "Company", "Position", "Connected On"],
            [
                {
                    "First Name": "Grace | <b>",
                    "Last Name": "Hopper",
                    "URL": SAFE_URL,
                    "Company": "Navy | <i>",
                    "Position": "*Engineer*",
                    "Connected On": "2024-01-01",
                }
            ],
        ),
        "Skills.csv": (["Name"], [{"Name": "Python | <b>*unsafe*"}]),
        "Learning.csv": (
            ["Content Title", "Content Completed At (if completed)"],
            [
                {
                    "Content Title": "Course | <b>",
                    "Content Completed At (if completed)": attack,
                }
            ],
        ),
        "Job Applications.csv": (
            [
                "Application Date",
                "Company Name",
                "Job Title",
                "Job Url",
                "Status",
                "Resume Name",
            ],
            [
                {
                    "Application Date": "2024-01-01",
                    "Company Name": "Company | <b>",
                    "Job Title": "*Engineer*",
                    "Job Url": UNSAFE_URL,
                    "Status": "Applied | <i>",
                    "Resume Name": "resume | <b>.pdf",
                }
            ],
        ),
        "Contact Settings.csv": (
            ["Setting", "Value"],
            [{"Setting": "Email | <b>", "Value": attack}],
        ),
        "Recommendations Received.csv": (
            [
                "First Name",
                "Last Name",
                "Company",
                "Job Title",
                "Text",
                "Creation Date",
                "Status",
            ],
            [
                {
                    "First Name": "George",
                    "Last Name": "Boole",
                    "Company": "Society | <b>",
                    "Job Title": "*Mathematician*",
                    "Text": attack,
                    "Creation Date": "2024-01-01",
                    "Status": "VISIBLE",
                }
            ],
        ),
        "Endorsement Received Info.csv": (
            [
                "Skill Name",
                "Endorser First Name",
                "Endorser Last Name",
                "Endorsement Date",
                "Endorsement Status",
            ],
            [
                {
                    "Skill Name": "Mathematics | <b>",
                    "Endorser First Name": "George",
                    "Endorser Last Name": "Boole",
                    "Endorsement Date": "2024-01-01 00:00:00 UTC",
                    "Endorsement Status": "ACCEPTED",
                }
            ],
        ),
        "Opprtunities.csv": (
            [
                "Creation Time",
                "Service Category",
                "Location",
                "Questions and Answers",
                "Status",
            ],
            [
                {
                    "Creation Time": "2024-01-01",
                    "Service Category": "Category | <b>",
                    "Location": "Remote | <i>",
                    "Questions and Answers": attack,
                    "Status": "Open | <b>",
                }
            ],
        ),
    }
    zip_path = tmp_path / "malicious.zip"
    _write_export(zip_path, export_files)
    output_dir = tmp_path / "output"
    files = create_converter(zip_path, output_dir).convert(lang="es")
    produced = {path.name for path in files}
    assert {
        "profile.md",
        "skills.md",
        "experience.md",
        "education.md",
        "certifications.md",
        "projects.md",
        "groups.md",
        "posts.md",
        "comments.md",
        "reactions.md",
        "reposts.md",
        "votes.md",
        "saved_items.md",
        "media.md",
        "learning.md",
        "job_applications.md",
        "job_descriptions.md",
        "connections.md",
        "search_queries.md",
        "contact_settings.md",
        "recommendations.md",
        "endorsements.md",
        "service_opportunities.md",
    } <= produced
    assert produced <= set(CONVERSION_CONTRACT.output_files)

    for path in files:
        content = path.read_text(encoding="utf-8")
        _assert_inert(content)
        assert "javascript:" not in content.lower()
        assert "\x00" not in content
        assert "\r" not in content
        if any(
            line.startswith("|") and line.endswith("|") for line in content.splitlines()
        ):
            _assert_table_shape(content)


def test_public_surface_and_dependency_contract_are_unchanged() -> None:
    assert CONVERSION_CONTRACT.format_version == 1
    assert CONVERSION_CONTRACT.default_language == "en"
    assert CONVERSION_CONTRACT.supported_languages == ("en", "es")
    assert CONVERSION_CONTRACT.output_extension == ".md"
    assert CONVERSION_CONTRACT.output_encoding == "utf-8"
    assert CONVERSION_CONTRACT.formatter_keys == EXPECTED_CONTRACT_KEYS
    assert len(CONVERSION_CONTRACT.output_files) == 65
    assert CONVERSION_CONTRACT.output_files == tuple(
        f"{key}.md" for key in EXPECTED_CONTRACT_KEYS
    )

    runtime = _runtime_formatter_list()
    runtime_keys = tuple(formatter.section_key for formatter in runtime)
    assert runtime_keys == EXPECTED_RUNTIME_FORMATTER_KEYS
    import_module("linkedin2md.parsers")
    parser_registry = get_parser_registry()
    parser_registry.instantiate_all()
    CONVERSION_CONTRACT.validate_registries(
        (parser.section_key for parser in parser_registry.get_all()),
        (formatter.section_key for formatter in runtime),
    )

    assert set(linkedin2md.__all__) == EXPECTED_ROOT_EXPORTS
    assert len(linkedin2md.__all__) == len(EXPECTED_ROOT_EXPORTS)
    assert set(formatters_package.__all__) == EXPECTED_FORMATTER_EXPORTS
    assert len(formatters_package.__all__) == len(EXPECTED_FORMATTER_EXPORTS)
    assert all(hasattr(linkedin2md, name) for name in linkedin2md.__all__)
    assert all(hasattr(formatters_package, name) for name in formatters_package.__all__)

    main_signature = inspect.signature(cli.main)
    assert tuple(main_signature.parameters) == ()
    assert main_signature.return_annotation is int
    parse_signature = inspect.signature(cli._parse_args)
    assert tuple(parse_signature.parameters) == ("argv",)
    factory_signature = inspect.signature(create_converter)
    assert tuple(factory_signature.parameters) == ("source", "output_dir", "limits")
    assert factory_signature.parameters["limits"].kind is inspect.Parameter.KEYWORD_ONLY
    assert factory_signature.parameters["limits"].default is None
    constructor_signature = inspect.signature(LinkedInToMarkdownConverter.__init__)
    assert tuple(constructor_signature.parameters) == (
        "self",
        "extractor",
        "parser_registry",
        "formatter_registry",
        "writer",
    )
    registry_get_signature = inspect.signature(DefaultFormatterRegistry.get)
    assert tuple(registry_get_signature.parameters) == ("self", "section_key")
    registry_all_signature = inspect.signature(DefaultFormatterRegistry.get_all)
    assert tuple(registry_all_signature.parameters) == ("self",)

    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'(?m)^requires-python\s*=\s*">=3\.10"\s*$', pyproject)
    assert re.search(r"(?m)^dependencies\s*=\s*\[\]\s*$", pyproject)
    assert re.search(
        r'(?m)^dev\s*=\s*\["pytest>=9\.0", "ruff>=0\.9", "pyright>=1\.1\.408"\]\s*$',
        pyproject,
    )
    assert re.search(r'(?m)^requires\s*=\s*\["hatchling>=1\.27"\]\s*$', pyproject)
    project_section = pyproject.split("[project]", 1)[1].split("[project.scripts]", 1)[
        0
    ]
    dependency_lines = [
        line.strip()
        for line in project_section.splitlines()
        if line.strip().startswith(("dependencies", "dev =", "requires ="))
    ]
    assert not any(
        re.search(
            r"(?i)\b(markdown|requests|httpx|urllib3|beautifulsoup|bs4|lxml)\b", line
        )
        for line in dependency_lines
    )

    base_tree = ast.parse(
        (FORMATTER_ROOT / "base.py").read_text(encoding="utf-8"),
        filename=str(FORMATTER_ROOT / "base.py"),
    )
    imported_modules: set[str] = set()
    for node in ast.walk(base_tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    assert imported_modules <= {
        "abc",
        "collections.abc",
        "email.errors",
        "email.headerregistry",
        "ipaddress",
        "logging",
        "re",
        "typing",
        "unicodedata",
        "urllib.parse",
        "linkedin2md.protocols",
    }
