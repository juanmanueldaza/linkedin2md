"""Professional section parsers (skills, experience, education, etc.).

Each parser handles ONE section (SRP).
"""

import re

from linkedin2md.parsers.base import BaseParser, merge_bilingual_entries
from linkedin2md.protocols import BilingualText
from linkedin2md.registry import register_parser


@register_parser
class SkillsParser(BaseParser):
    """Parse skills with deduplication."""

    @property
    def section_key(self) -> str:
        return "skills"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[str]:
        skills_data = self._get_csv(raw_data, "skills")
        skills = []
        seen_lower = set()

        for s in skills_data:
            name = s.get("Name", "").strip()
            if not name:
                continue

            name_lower = name.lower()

            # Extract English from parenthetical Spanish duplicate
            if "(" in name and ")" in name:
                match = re.search(r"\(([^)]+)\)", name)
                if match:
                    english_name = match.group(1).strip()
                    if english_name.lower() in seen_lower:
                        continue
                    name = english_name

            if name_lower not in seen_lower:
                skills.append(name)
                seen_lower.add(name_lower)

        return skills


@register_parser
class ExperienceParser(BaseParser):
    """Parse work experience with bilingual support."""

    @property
    def section_key(self) -> str:
        return "experience"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        positions = self._get_csv(raw_data, "positions")
        experiences = []

        for pos in positions:
            company = pos.get("Company Name", "")
            title = pos.get("Title", "")
            description = pos.get("Description", "")
            location = pos.get("Location", "")

            desc_lang = self._detect_language(description)

            exp = {
                "company": company,
                "role": self._create_bilingual(title, self._detect_language(title)),
                "location": location or None,
                "start": self._format_date(pos.get("Started On", "")),
                "end": self._format_date(pos.get("Finished On", "")) or None,
                "achievements": self._parse_achievements(description, desc_lang),
            }
            experiences.append(exp)

        return merge_bilingual_entries(
            experiences,
            key_fields=["company", "start", "end", "location"],
            bilingual_fields=["role", "achievements"],
        )

    def _parse_achievements(self, description: str, lang: str) -> list[dict]:
        if not description:
            return []

        achievements = []
        lines = re.split(r"[•\-\*]\s*|\n+|\d+\.\s*", description)

        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue

            text = BilingualText(
                en=line if lang == "en" else "",
                es=line if lang == "es" else "",
            )
            achievements.append({"text": text})

        return achievements


@register_parser
class EducationParser(BaseParser):
    """Parse education with bilingual support."""

    @property
    def section_key(self) -> str:
        return "education"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        edu_data = self._get_csv(raw_data, "education")
        education = []

        for edu in edu_data:
            school = edu.get("School Name", "")
            degree = edu.get("Degree Name", "")
            notes = edu.get("Notes", "")
            activities = edu.get("Activities", "")
            start_date = edu.get("Start Date", "")
            end_date = edu.get("End Date", "")

            degree_lang = self._detect_language(degree)
            notes_lang = self._detect_language(notes)

            entry = {
                "institution": school,
                "degree": self._create_bilingual(degree, degree_lang),
                "field": None,
                "start": start_date.split("-")[0] if start_date else "",
                "end": end_date.split("-")[0] if end_date else None,
                "location": None,
                "notes": self._create_bilingual(notes, notes_lang) if notes else None,
                "activities": activities or None,
            }
            education.append(entry)

        return merge_bilingual_entries(
            education,
            key_fields=["institution", "start", "end"],
            bilingual_fields=["degree", "notes"],
        )


@register_parser
class CertificationsParser(BaseParser):
    """Parse certifications."""

    @property
    def section_key(self) -> str:
        return "certifications"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        certs = self._get_csv(raw_data, "certifications")
        result = []

        for c in certs:
            name = c.get("Name", "")
            if not name:
                continue

            cert = {
                "name": name,
                "issuer": c.get("Authority", ""),
                "date": self._format_date(c.get("Started On", "")),
                "expires": self._format_date(c.get("Finished On", "")) or None,
                "url": c.get("Url", "") or None,
                "credential_id": c.get("License Number", "") or None,
            }
            result.append(cert)

        return result


@register_parser
class LanguagesParser(BaseParser):
    """Parse languages with deduplication."""

    @property
    def section_key(self) -> str:
        return "languages"

    # Language name mapping (Spanish -> English)
    LANG_MAP = {
        "inglés": "English",
        "español": "Spanish",
        "francés": "French",
        "alemán": "German",
        "italiano": "Italian",
        "portugués": "Portuguese",
        "chino": "Chinese",
        "japonés": "Japanese",
        "coreano": "Korean",
        "árabe": "Arabic",
        "ruso": "Russian",
        "hindi": "Hindi",
    }

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        langs = self._get_csv(raw_data, "languages")
        result = []
        seen_lower = set()

        for lang in langs:
            name = lang.get("Name", "")
            proficiency = lang.get("Proficiency", "") or None

            if not name:
                continue

            base_name = name.split("(")[0].strip()
            base_lower = base_name.lower()

            normalized_name = self.LANG_MAP.get(base_lower) or base_name
            normalized_lower = normalized_name.lower()

            if normalized_lower in seen_lower:
                continue

            seen_lower.add(normalized_lower)
            result.append(
                {
                    "name": normalized_name,
                    "proficiency": proficiency,
                }
            )

        return result


@register_parser
class ProjectsParser(BaseParser):
    """Parse projects with bilingual support."""

    @property
    def section_key(self) -> str:
        return "projects"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        projects = self._get_csv(raw_data, "projects")
        result = []

        for p in projects:
            title = p.get("Title", "")
            if not title:
                continue

            description = p.get("Description", "")
            desc_lang = self._detect_language(description) if description else "en"

            project = {
                "title": title,
                "description": self._create_bilingual(description, desc_lang)
                if description
                else None,
                "url": p.get("Url", "") or None,
                "start": self._format_date(p.get("Started On", "")),
                "end": self._format_date(p.get("Finished On", "")) or None,
            }
            result.append(project)

        return merge_bilingual_entries(
            result,
            key_fields=["title", "start", "end", "url"],
            bilingual_fields=["description"],
        )
