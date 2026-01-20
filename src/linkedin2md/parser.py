"""LinkedIn data export parser.

Parses the ZIP export from LinkedIn data download.
To export: Settings → Data Privacy → Get a copy of your data

Supports both Basic and Complete exports with proper bilingual handling.
Captures ALL available LinkedIn data.
"""

import csv
import io
import re
import zipfile
from pathlib import Path

# Spanish language detection patterns
SPANISH_PATTERNS = [
    r"\b(el|la|los|las|un|una|unos|unas)\b",  # Articles
    r"\b(de|del|en|con|por|para|sobre|entre)\b",  # Prepositions
    r"\b(que|como|donde|cuando|quien)\b",  # Conjunctions
    r"\b(es|son|fue|fueron|está|están)\b",  # Verbs
    r"\b(muy|más|también|además|durante)\b",  # Adverbs
    r"[áéíóúñ¿¡]",  # Spanish characters
]

# Compiled regex for Spanish detection
SPANISH_REGEX = re.compile("|".join(SPANISH_PATTERNS), re.IGNORECASE)

# Month names for date formatting (index 0 is empty for 1-based indexing)
MONTHS = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def detect_language(text: str) -> str:
    """Detect if text is Spanish or English."""
    if not text:
        return "en"
    matches = len(SPANISH_REGEX.findall(text))
    words = len(text.split())
    if words > 0 and matches / words > 0.1:
        return "es"
    return "en"


def create_bilingual(text: str, detected_lang: str | None = None) -> dict:
    """Create bilingual dict with text in detected language."""
    if not text:
        return {"en": "", "es": ""}
    lang = detected_lang or detect_language(text)
    if lang == "es":
        return {"en": "", "es": text}
    return {"en": text, "es": ""}


def merge_bilingual_entries(
    entries: list[dict],
    key_fields: list[str],
    bilingual_fields: list[str],
) -> list[dict]:
    """Merge duplicate entries with bilingual content.

    Groups entries by matching key fields and merges bilingual text from
    English and Spanish versions into complete BilingualText dicts.

    Args:
        entries: List of entry dicts to deduplicate
        key_fields: Fields to match on (e.g., ["company", "start", "end"])
        bilingual_fields: Fields to merge as BilingualText (e.g., ["role"])

    Returns:
        Deduplicated list with merged bilingual content
    """
    if not entries:
        return []

    # Group entries by key fields
    groups: dict[tuple, list[dict]] = {}
    for entry in entries:
        # Create key from key_fields (handle None values)
        key = tuple(entry.get(field) for field in key_fields)
        if key not in groups:
            groups[key] = []
        groups[key].append(entry)

    # Merge each group
    merged = []
    for group in groups.values():
        if len(group) == 1:
            # No duplicates, keep as is
            merged.append(group[0])
        else:
            # Merge bilingual content
            merged_entry = _merge_bilingual_group(group, bilingual_fields)
            merged.append(merged_entry)

    return merged


def _merge_bilingual_group(group: list[dict], bilingual_fields: list[str]) -> dict:
    """Merge a group of duplicate entries with different languages."""
    # Start with first entry as base
    merged = group[0].copy()

    # Collect all language versions for each bilingual field
    for field in bilingual_fields:
        if field == "achievements":
            # Special handling for achievements (list of dicts)
            merged[field] = _merge_achievements(group)
        elif field in merged:
            # Regular bilingual field
            merged[field] = _merge_bilingual_field(group, field)

    return merged


def _merge_bilingual_field(group: list[dict], field: str) -> dict:
    """Merge a bilingual field from multiple entries."""
    result = {"en": "", "es": ""}

    for entry in group:
        value = entry.get(field)
        if not value:
            continue

        # If already a dict (BilingualText), merge it
        if isinstance(value, dict):
            if value.get("en"):
                result["en"] = value["en"]
            if value.get("es"):
                result["es"] = value["es"]

    return result


def _merge_achievements(group: list[dict]) -> list[dict]:
    """Merge achievements lists from multiple language versions.

    Matches achievements by index and merges their bilingual text.
    """
    # Get all achievement lists
    achievement_lists = [entry.get("achievements", []) for entry in group]

    if not achievement_lists or not any(achievement_lists):
        return []

    # Use the longest list as base (should be same length, but be safe)
    max_len = max(len(lst) for lst in achievement_lists if lst)
    merged_achievements = []

    for i in range(max_len):
        merged_achievement = {"text": {"en": "", "es": ""}}

        # Merge from all versions at this index
        for achievements in achievement_lists:
            if i >= len(achievements):
                continue

            achievement = achievements[i]

            # Merge text field
            text = achievement.get("text", {})
            if isinstance(text, dict):
                if text.get("en"):
                    merged_achievement["text"]["en"] = text["en"]
                if text.get("es"):
                    merged_achievement["text"]["es"] = text["es"]

        merged_achievements.append(merged_achievement)

    return merged_achievements


class LinkedInExportParser:
    """Parse LinkedIn data export ZIP into comprehensive CV data.

    Captures ALL available data from LinkedIn exports including:
    - Profile, positions, education, skills, certifications
    - Languages, projects, recommendations, endorsements
    - Learning courses, connections, follows
    - Posts, comments, events, job applications
    - Invitations, reactions, search history, logins
    - Ads data, imported contacts, and more
    """

    def __init__(self, zip_path: Path | str):
        """Initialize parser with ZIP path."""
        self.zip_path = Path(zip_path)
        self._data: dict[str, list[dict]] = {}

    def parse(self) -> dict:
        """Parse ZIP and return comprehensive CV data dict."""
        self._extract_csvs()
        return self._build_cv_data()

    def _extract_csvs(self) -> None:
        """Extract and parse all CSV files from ZIP.

        Some LinkedIn CSVs (like Connections.csv) have header notes before
        the actual CSV data. We detect and skip these by finding the real
        header row.
        """
        with zipfile.ZipFile(self.zip_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".csv"):
                    with zf.open(name) as f:
                        content = f.read().decode("utf-8")
                        # Handle CSVs with header notes (like Connections.csv)
                        content = self._skip_header_notes(content)
                        reader = csv.DictReader(io.StringIO(content))
                        # Normalize key: lowercase, replace spaces with underscores
                        key = Path(name).stem.lower().replace(" ", "_")
                        self._data[key] = list(reader)

    def _skip_header_notes(self, content: str) -> str:
        """Skip header notes in LinkedIn CSVs that have them.

        Some files like Connections.csv start with:
        Notes:
        "When exporting your connection data..."

        First Name,Last Name,URL,...

        We need to find the actual header row.
        """
        lines = content.split("\n")

        # If starts with "Notes:", find the real header
        if lines and lines[0].strip().startswith("Notes"):
            for i, line in enumerate(lines):
                # Skip empty lines and note lines
                stripped = line.strip()
                if not stripped:
                    continue
                # Check if this looks like a CSV header (has commas, not a quote)
                if "," in stripped and not stripped.startswith('"'):
                    # Found the header row
                    return "\n".join(lines[i:])

        return content

    def _build_cv_data(self) -> dict:
        """Build comprehensive CV data dict from all parsed CSVs."""
        profile = self._get_profile()

        data = {
            # Core profile
            "name": self._parse_name(),
            "title": self._parse_title(),
            "email": self._parse_email(),
            "phone": self._parse_phone(),
            "location": self._parse_location(),
            "linkedin": None,  # Not in export
            "summary": self._parse_summary(),
            # Professional data
            "skills": self._parse_skills(),
            "experience": self._parse_experience(),
            "education": self._parse_education(),
            "certifications": self._parse_certifications(),
            "languages": self._parse_languages(),
            "projects": self._parse_projects(),
            # Recommendations & endorsements
            "recommendations": self._parse_recommendations(),
            "recommendations_given": self._parse_recommendations_given(),
            "endorsements": self._parse_endorsements(),
            "endorsements_given": self._parse_endorsements_given(),
            # Learning
            "learning": self._parse_learning(),
            "learning_reviews": self._parse_learning_reviews(),
            # Network
            "connections": self._parse_connections(),
            "companies_followed": self._parse_company_follows(),
            "members_followed": self._parse_member_follows(),
            "invitations": self._parse_invitations(),
            "imported_contacts": self._parse_imported_contacts(),
            # Content & activity
            "posts": self._parse_posts(),
            "comments": self._parse_comments(),
            "reactions": self._parse_reactions(),
            "reposts": self._parse_reposts(),
            "votes": self._parse_votes(),
            "saved_items": self._parse_saved_items(),
            "events": self._parse_events(),
            "media": self._parse_rich_media(),
            "messages": self._parse_messages(),
            # Job search
            "job_applications": self._parse_job_applications(),
            "saved_jobs": self._parse_saved_jobs(),
            "job_preferences": self._parse_job_preferences(),
            "saved_job_answers": self._parse_saved_job_answers(),
            "screening_responses": self._parse_screening_responses(),
            "saved_job_alerts": self._parse_saved_job_alerts(),
            # Activity history
            "search_queries": self._parse_search_queries(),
            "logins": self._parse_logins(),
            "security_challenges": self._parse_security_challenges(),
            # Advertising & privacy
            "ads_clicked": self._parse_ads_clicked(),
            "ad_targeting": self._parse_ad_targeting(),
            "lan_ads": self._parse_lan_ads(),
            "inferences": self._parse_inferences(),
            # Premium & payments
            "receipts": self._parse_receipts(),
            # Services marketplace
            "service_engagements": self._parse_service_engagements(),
            "service_opportunities": self._parse_service_opportunities(),
            # Identity & verification
            "verifications": self._parse_verifications(),
            "identity_assets": self._parse_identity_assets(),
            # Metadata
            "profile_meta": {
                "industry": profile.get("Industry", "") or None,
                "twitter": self._parse_twitter(profile.get("Twitter Handles", "")),
                "websites": self._parse_websites(profile.get("Websites", "")),
                "birth_date": profile.get("Birth Date", "") or None,
                "registered_at": self._parse_registration_date(),
                "connections_count": len(self._data.get("connections", [])),
            },
        }
        return data

    def _get_profile(self) -> dict:
        """Get profile data."""
        profiles = self._data.get("profile", [])
        return profiles[0] if profiles else {}

    def _build_name(self, first: str, last: str) -> str:
        """Build full name from first and last name."""
        return f"{first} {last}".strip()

    def _merge_csv_sources(self, keys: list[str]) -> list[dict]:
        """Merge rows from multiple CSV sources (for split files)."""
        result = []
        for key in keys:
            result.extend(self._data.get(key, []))
        return result

    def _parse_name(self) -> str:
        """Extract name from profile."""
        profile = self._get_profile()
        return self._build_name(
            profile.get("First Name", ""), profile.get("Last Name", "")
        )

    def _parse_title(self) -> dict:
        """Extract headline/title as bilingual."""
        profile = self._get_profile()
        title = profile.get("Headline", "")
        return create_bilingual(title)

    def _parse_email(self) -> str:
        """Extract primary email."""
        emails = self._data.get("email_addresses", [])
        for email in emails:
            if email.get("Primary", "").lower() == "yes":
                return email.get("Email Address", "")
        if emails:
            return emails[0].get("Email Address", "")
        return ""

    def _parse_phone(self) -> str:
        """Extract phone number."""
        phones = self._data.get("phonenumbers", [])
        if phones:
            return phones[0].get("Number", "")
        return ""

    def _parse_location(self) -> str:
        """Extract location."""
        profile = self._get_profile()
        return profile.get("Geo Location", "") or profile.get("Location", "")

    def _parse_summary(self) -> dict:
        """Extract summary as bilingual."""
        profile = self._get_profile()
        summary = profile.get("Summary", "")
        return create_bilingual(summary)

    def _parse_twitter(self, twitter_str: str) -> str | None:
        """Parse Twitter handle from profile."""
        if not twitter_str:
            return None
        # Remove brackets if present
        handle = twitter_str.strip("[]")
        return handle if handle else None

    def _parse_websites(self, websites_str: str) -> list[str]:
        """Parse websites from profile."""
        if not websites_str:
            return []
        # Split by comma or semicolon
        sites = re.split(r"[,;]", websites_str)
        return [s.strip() for s in sites if s.strip()]

    def _parse_registration_date(self) -> str | None:
        """Parse registration date."""
        reg = self._data.get("registration", [])
        if reg:
            return reg[0].get("Registered At", "") or None
        return None

    def _parse_skills(self) -> list[str]:
        """Extract skills, deduplicating English/Spanish variants."""
        skills_data = self._data.get("skills", [])
        skills = []
        seen_lower = set()

        for s in skills_data:
            name = s.get("Name", "").strip()
            if not name:
                continue

            name_lower = name.lower()

            # Check for parenthetical English name (Spanish duplicate)
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

    def _parse_experience(self) -> list[dict]:
        """Extract work experience with bilingual support."""
        positions = self._data.get("positions", [])
        experiences = []

        for pos in positions:
            company = pos.get("Company Name", "")
            title = pos.get("Title", "")
            description = pos.get("Description", "")
            location = pos.get("Location", "")

            desc_lang = detect_language(description)

            exp = {
                "company": company,
                "role": create_bilingual(title, detect_language(title)),
                "location": location or None,
                "start": self._format_date(pos.get("Started On", "")),
                "end": self._format_date(pos.get("Finished On", "")) or None,
                "achievements": self._parse_achievements(description, desc_lang),
            }
            experiences.append(exp)

        # Merge duplicate entries from bilingual profiles
        return merge_bilingual_entries(
            experiences,
            key_fields=["company", "start", "end", "location"],
            bilingual_fields=["role", "achievements"],
        )

    def _parse_achievements(self, description: str, lang: str) -> list[dict]:
        """Parse description into achievement entries."""
        if not description:
            return []

        achievements = []
        lines = re.split(r"[•\-\*]\s*|\n+|\d+\.\s*", description)

        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue

            text = {"en": "", "es": ""}
            text[lang] = line

            achievements.append({"text": text})

        return achievements

    def _parse_education(self) -> list[dict]:
        """Extract education with bilingual support."""
        edu_data = self._data.get("education", [])
        education = []

        for edu in edu_data:
            school = edu.get("School Name", "")
            degree = edu.get("Degree Name", "")
            notes = edu.get("Notes", "")
            activities = edu.get("Activities", "")
            start_date = edu.get("Start Date", "")
            end_date = edu.get("End Date", "")

            degree_lang = detect_language(degree)
            notes_lang = detect_language(notes)

            entry = {
                "institution": school,
                "degree": create_bilingual(degree, degree_lang),
                "field": None,
                "start": start_date.split("-")[0] if start_date else "",
                "end": end_date.split("-")[0] if end_date else None,
                "location": None,
                "notes": create_bilingual(notes, notes_lang) if notes else None,
                "activities": activities or None,
            }
            education.append(entry)

        # Merge duplicate entries from bilingual profiles
        return merge_bilingual_entries(
            education,
            key_fields=["institution", "start", "end"],
            bilingual_fields=["degree", "notes"],
        )

    def _parse_certifications(self) -> list[dict]:
        """Extract certifications."""
        certs = self._data.get("certifications", [])
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

    def _parse_languages(self) -> list[dict]:
        """Extract languages with proficiency, deduplicating variants."""
        langs = self._data.get("languages", [])
        result = []
        seen_lower = set()

        # Language name mapping (Spanish -> English)
        lang_map = {
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

        for lang in langs:
            name = lang.get("Name", "")
            proficiency = lang.get("Proficiency", "") or None

            if not name:
                continue

            # Extract language name from proficiency suffix like "English (Native...)"
            base_name = name.split("(")[0].strip()
            base_lower = base_name.lower()

            # Normalize Spanish to English
            normalized_name = lang_map.get(base_lower) or base_name
            normalized_lower = normalized_name.lower()

            # Skip if already seen
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

    def _parse_projects(self) -> list[dict]:
        """Extract projects with bilingual support."""
        projects = self._data.get("projects", [])
        result = []

        for p in projects:
            title = p.get("Title", "")
            if not title:
                continue

            description = p.get("Description", "")
            desc_lang = detect_language(description) if description else "en"

            project = {
                "title": title,
                "description": create_bilingual(description, desc_lang)
                if description
                else None,
                "url": p.get("Url", "") or None,
                "start": self._format_date(p.get("Started On", "")),
                "end": self._format_date(p.get("Finished On", "")) or None,
            }
            result.append(project)

        # Merge duplicate entries from bilingual profiles
        return merge_bilingual_entries(
            result,
            key_fields=["title", "start", "end", "url"],
            bilingual_fields=["description"],
        )

    def _parse_recommendations(self) -> list[dict]:
        """Extract recommendations received."""
        recs = self._data.get("recommendations_received", [])
        result = []

        for r in recs:
            text = r.get("Text", "")
            status = r.get("Status", "")

            if not text or status != "VISIBLE":
                continue

            text_lang = detect_language(text)

            rec = {
                "author": self._build_name(
                    r.get("First Name", ""), r.get("Last Name", "")
                ),
                "title": r.get("Job Title", "") or None,
                "company": r.get("Company", "") or None,
                "text": create_bilingual(text, text_lang),
                "date": self._parse_datetime(r.get("Creation Date", "")),
            }
            result.append(rec)

        return result

    def _parse_recommendations_given(self) -> list[dict]:
        """Extract recommendations given to others."""
        recs = self._data.get("recommendations_given", [])
        result = []

        for r in recs:
            text = r.get("Text", "")
            if not text:
                continue

            text_lang = detect_language(text)

            rec = {
                "recipient": self._build_name(
                    r.get("First Name", ""), r.get("Last Name", "")
                ),
                "title": r.get("Job Title", "") or None,
                "company": r.get("Company", "") or None,
                "text": create_bilingual(text, text_lang),
                "date": self._parse_datetime(r.get("Creation Date", "")),
            }
            result.append(rec)

        return result

    def _parse_endorsements(self) -> list[dict]:
        """Extract skill endorsements received."""
        endorsements = self._data.get("endorsement_received_info", [])
        result = []

        for e in endorsements:
            if e.get("Endorsement Status") != "ACCEPTED":
                continue

            endorsement = {
                "skill": e.get("Skill Name", ""),
                "endorser": self._build_name(
                    e.get("Endorser First Name", ""), e.get("Endorser Last Name", "")
                ),
                "endorser_url": e.get("Endorser Public Url", "") or None,
                "date": self._parse_utc_date(e.get("Endorsement Date", "")),
            }
            result.append(endorsement)

        return result

    def _parse_endorsements_given(self) -> list[dict]:
        """Extract skill endorsements given to others."""
        endorsements = self._data.get("endorsement_given_info", [])
        result = []

        for e in endorsements:
            if e.get("Endorsement Status") != "ACCEPTED":
                continue

            endorsement = {
                "skill": e.get("Skill Name", ""),
                "endorsee": self._build_name(
                    e.get("Endorsee First Name", ""), e.get("Endorsee Last Name", "")
                ),
                "endorsee_url": e.get("Endorsee Public Url", "") or None,
                "date": self._parse_utc_date(e.get("Endorsement Date", "")),
            }
            result.append(endorsement)

        return result

    def _parse_learning(self) -> list[dict]:
        """Extract LinkedIn Learning courses."""
        learning = self._data.get("learning", [])
        result = []

        for course in learning:
            title = course.get("Content Title", "")
            if not title:
                continue

            entry = {
                "title": title,
                "description": course.get("Content Description", "") or None,
                "content_type": course.get("Content Type", "") or None,
                "last_watched": course.get("Content Last Watched Date (if viewed)", "")
                or None,
                "completed_at": course.get("Content Completed At (if completed)", "")
                or None,
                "saved": course.get("Content Saved", "").lower() == "true",
            }
            result.append(entry)

        return result

    def _parse_learning_reviews(self) -> list[dict]:
        """Extract learning content reviews."""
        reviews = self._data.get("reviews", [])
        result = []

        for r in reviews:
            reviewee = r.get("Reviewee", "")
            if not reviewee:
                continue

            entry = {
                "content": reviewee,
                "review_type": r.get("Review Type", "") or None,
                "section": r.get("Review Section", "") or None,
                "date": r.get("Creation Date", "") or None,
                "rating": r.get("Rating", "") or None,
                "text": r.get("Review Text", "") or None,
                "reviewer": r.get("Reviewer", "") or None,
                "tags": r.get("Review Tags", "") or None,
            }
            result.append(entry)

        return result

    def _parse_connections(self) -> list[dict]:
        """Extract connections (limited data due to LinkedIn privacy)."""
        connections = self._data.get("connections", [])
        result = []

        for conn in connections:
            # Skip header rows
            first = conn.get("First Name", "")
            last = conn.get("Last Name", "")
            if not first and not last:
                continue

            entry = {
                "name": self._build_name(first, last),
                "url": conn.get("URL", "") or None,
                "email": conn.get("Email Address", "") or None,
                "company": conn.get("Company", "") or None,
                "position": conn.get("Position", "") or None,
                "connected_on": conn.get("Connected On", "") or None,
            }
            result.append(entry)

        return result

    def _parse_company_follows(self) -> list[dict]:
        """Extract companies followed."""
        follows = self._data.get("company_follows", [])
        result = []

        for f in follows:
            name = f.get("Organization", "")
            if not name:
                continue

            entry = {
                "name": name,
                "followed_on": f.get("Followed On", "") or None,
            }
            result.append(entry)

        return result

    def _parse_member_follows(self) -> list[dict]:
        """Extract members followed."""
        follows = self._data.get("member_follows", [])
        result = []

        for f in follows:
            name = f.get("FullName", "")
            if not name:
                continue

            entry = {
                "name": name,
                "date": f.get("Date", "") or None,
                "status": f.get("Status", "") or None,
            }
            result.append(entry)

        return result

    def _parse_invitations(self) -> list[dict]:
        """Extract connection invitations sent/received."""
        invitations = self._data.get("invitations", [])
        result = []

        for inv in invitations:
            from_name = inv.get("From", "")
            to_name = inv.get("To", "")
            if not from_name and not to_name:
                continue

            entry = {
                "from": from_name,
                "to": to_name,
                "sent_at": inv.get("Sent At", "") or None,
                "message": inv.get("Message", "") or None,
                "direction": inv.get("Direction", "") or None,
                "inviter_url": inv.get("inviterProfileUrl", "") or None,
                "invitee_url": inv.get("inviteeProfileUrl", "") or None,
            }
            result.append(entry)

        return result

    def _parse_imported_contacts(self) -> list[dict]:
        """Extract imported contacts from address book."""
        contacts = self._data.get("importedcontacts", [])
        result = []

        for c in contacts:
            # Build name from parts
            first = c.get("FirstName", "")
            middle = c.get("MiddleName", "")
            last = c.get("LastName", "")
            name_parts = [p for p in [first, middle, last] if p]
            name = " ".join(name_parts)

            emails = c.get("Emails", "")
            phones = c.get("PhoneNumbers", "")

            # Skip if no useful data
            if not name and not emails:
                continue

            entry = {
                "name": name or None,
                "emails": emails or None,
                "phones": phones or None,
                "title": c.get("Title", "") or None,
                "location": c.get("Location", "") or None,
                "created_at": c.get("CreatedAt", "") or None,
                "updated_at": c.get("UpdatedAt", "") or None,
            }
            result.append(entry)

        return result

    def _parse_posts(self) -> list[dict]:
        """Extract posts/shares."""
        shares = self._data.get("shares", [])
        result = []

        for s in shares:
            date = s.get("Date", "")
            if not date:
                continue

            content = s.get("ShareCommentary", "")
            content_lang = detect_language(content) if content else "en"

            entry = {
                "date": date,
                "url": s.get("ShareLink", "") or None,
                "content": create_bilingual(content, content_lang) if content else None,
                "shared_url": s.get("SharedUrl", "") or None,
                "media_url": s.get("MediaUrl", "") or None,
                "visibility": s.get("Visibility", "") or None,
            }
            result.append(entry)

        return result

    def _parse_comments(self) -> list[dict]:
        """Extract comments."""
        comments = self._data.get("comments", [])
        result = []

        for c in comments:
            date = c.get("Date", "")
            if not date:
                continue

            message = c.get("Message", "")
            msg_lang = detect_language(message) if message else "en"

            entry = {
                "date": date,
                "url": c.get("Link", "") or None,
                "message": create_bilingual(message, msg_lang) if message else None,
            }
            result.append(entry)

        return result

    def _parse_reactions(self) -> list[dict]:
        """Extract reactions (likes, etc.)."""
        reactions = self._data.get("reactions", [])
        result = []

        for r in reactions:
            date = r.get("Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "type": r.get("Type", "") or None,
                "url": r.get("Link", "") or None,
            }
            result.append(entry)

        return result

    def _parse_reposts(self) -> list[dict]:
        """Extract instant reposts."""
        reposts = self._data.get("instantreposts", [])
        result = []

        for r in reposts:
            date = r.get("Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "url": r.get("Link", "") or None,
            }
            result.append(entry)

        return result

    def _parse_votes(self) -> list[dict]:
        """Extract poll votes."""
        votes = self._data.get("votes", [])
        result = []

        for v in votes:
            date = v.get("Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "url": v.get("Link", "") or None,
                "option": v.get("OptionText", "") or None,
            }
            result.append(entry)

        return result

    def _parse_saved_items(self) -> list[dict]:
        """Extract saved/bookmarked items."""
        items = self._data.get("saved_items", [])
        result = []

        for item in items:
            url = item.get("savedItem", "")
            if not url:
                continue

            entry = {
                "url": url,
                "saved_at": item.get("CreatedTime", "") or None,
            }
            result.append(entry)

        return result

    def _parse_events(self) -> list[dict]:
        """Extract events."""
        events = self._data.get("events", [])
        result = []

        for e in events:
            name = e.get("Event Name", "")
            if not name:
                continue

            entry = {
                "name": name,
                "time": e.get("Event Time", "") or None,
                "status": e.get("Status", "") or None,
                "url": e.get("External Url", "") or None,
            }
            result.append(entry)

        return result

    def _parse_rich_media(self) -> list[dict]:
        """Extract uploaded media."""
        media = self._data.get("rich_media", [])
        result = []

        for m in media:
            url = m.get("Media Link", "")
            if not url:
                continue

            entry = {
                "date": m.get("Date/Time", "") or None,
                "description": m.get("Media Description", "") or None,
                "url": url,
            }
            result.append(entry)

        return result

    def _parse_messages(self) -> list[dict]:
        """Extract LinkedIn messages."""
        messages = self._data.get("messages", [])
        result = []

        for m in messages:
            date = m.get("DATE", "")
            if not date:
                continue

            entry = {
                "conversation_id": m.get("CONVERSATION ID", ""),
                "conversation_title": m.get("CONVERSATION TITLE", "") or None,
                "from_name": m.get("FROM", ""),
                "from_url": m.get("SENDER PROFILE URL", "") or None,
                "to_name": m.get("TO", ""),
                "to_url": m.get("RECIPIENT PROFILE URLS", "") or None,
                "date": date,
                "subject": m.get("SUBJECT", "") or None,
                "content": m.get("CONTENT", "") or None,
                "folder": m.get("FOLDER", "") or None,
            }
            result.append(entry)

        return result

    def _parse_job_applications(self) -> list[dict]:
        """Extract job applications from all split files."""
        result = []
        apps = self._merge_csv_sources(
            ["job_applications", "job_applications_1", "job_applications_2"]
        )

        for a in apps:
            date = a.get("Application Date", "")
            company = a.get("Company Name", "")
            title = a.get("Job Title", "")

            if not company and not title:
                continue

            entry = {
                "date": date,
                "company": company,
                "title": title,
                "url": a.get("Job Url", "") or None,
                "resume_used": a.get("Resume Name", "") or None,
                "contact_email": a.get("Contact Email", "") or None,
                "contact_phone": a.get("Contact Phone Number", "") or None,
                "questions_answers": a.get("Question And Answers", "") or None,
            }
            result.append(entry)

        return result

    def _parse_saved_jobs(self) -> list[dict]:
        """Extract saved jobs."""
        jobs = self._data.get("saved_jobs", [])
        result = []

        for j in jobs:
            date = j.get("Saved Date", "")
            company = j.get("Company Name", "")
            title = j.get("Job Title", "")

            if not company and not title:
                continue

            entry = {
                "date": date,
                "company": company,
                "title": title,
                "url": j.get("Job Url", "") or None,
            }
            result.append(entry)

        return result

    def _parse_job_preferences(self) -> dict | None:
        """Extract job seeker preferences."""
        prefs = self._data.get("job_seeker_preferences", [])
        if not prefs:
            return None

        p = prefs[0]

        def split_field(val: str) -> list[str]:
            if not val:
                return []
            return [x.strip() for x in val.split("|") if x.strip()]

        return {
            "locations": split_field(p.get("Locations", "")),
            "industries": split_field(p.get("Industries", "")),
            "job_types": split_field(p.get("Preferred Job Types", "")),
            "job_titles": split_field(p.get("Job Titles", "")),
            "open_to_recruiters": p.get("Open To Recruiters", "").lower() == "yes",
            "dream_companies": split_field(p.get("Dream Companies", "")),
            "profile_shared": p.get("Profile Shared With Job Poster", "").lower()
            == "yes",
            "intro_statement": p.get("Introduction Statement", "") or None,
            "phone": p.get("Phone Number", "") or None,
        }

    def _parse_saved_job_answers(self) -> list[dict]:
        """Extract saved job application answers."""
        answers = self._data.get("job_applicant_saved_answers", [])
        result = []

        for a in answers:
            question = a.get("Question", "")
            answer = a.get("Answer", "")

            if not question:
                continue

            entry = {
                "question": question,
                "answer": answer or None,
            }
            result.append(entry)

        return result

    def _parse_screening_responses(self) -> list[dict]:
        """Extract screening question responses from all files."""
        result = []
        responses = self._merge_csv_sources(
            [
                "job_applicant_saved_screening_question_responses",
                "job_applicant_saved_screening_question_responses_1",
                "job_applicant_saved_screening_question_responses_2",
            ]
        )

        for r in responses:
            # Get all available fields
            entry = {}
            for field_key, field_value in r.items():
                if field_value:
                    # Normalize key names
                    normalized_key = field_key.lower().replace(" ", "_")
                    entry[normalized_key] = field_value

            if entry:
                result.append(entry)

        return result

    def _parse_saved_job_alerts(self) -> list[dict]:
        """Extract saved job alerts."""
        alerts = self._data.get("savedjobalerts", [])
        result = []

        for a in alerts:
            search_id = a.get("SAVED_SEARCH_ID", "")

            entry = {
                "search_id": search_id or None,
                "parameters": a.get("ALERT_PARAMETERS", "") or None,
                "query_context": a.get("QUERY_CONTEXT", "") or None,
            }
            result.append(entry)

        return result

    def _parse_search_queries(self) -> list[dict]:
        """Extract search query history."""
        queries = self._data.get("searchqueries", [])
        result = []

        for q in queries:
            time = q.get("Time", "")
            query = q.get("Search Query", "")

            if not query:
                continue

            entry = {
                "time": time,
                "query": query,
            }
            result.append(entry)

        return result

    def _parse_logins(self) -> list[dict]:
        """Extract login history."""
        logins = self._data.get("logins", [])
        result = []

        for login in logins:
            date = login.get("Login Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "ip_address": login.get("IP Address", "") or None,
                "user_agent": login.get("User Agent", "") or None,
                "login_type": login.get("Login Type", "") or None,
            }
            result.append(entry)

        return result

    def _parse_security_challenges(self) -> list[dict]:
        """Extract security challenge history."""
        challenges = self._data.get("security_challenges", [])
        result = []

        for c in challenges:
            date = c.get("Challenge Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "ip_address": c.get("IP Address", "") or None,
                "user_agent": c.get("User Agent", "") or None,
                "country": c.get("Country", "") or None,
                "challenge_type": c.get("Challenge Type", "") or None,
            }
            result.append(entry)

        return result

    def _parse_ads_clicked(self) -> list[dict]:
        """Extract ads clicked history."""
        ads = self._data.get("ads_clicked", [])
        result = []

        for ad in ads:
            date = ad.get("Ad clicked Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "ad_id": ad.get("Ad Title/Id", "") or None,
            }
            result.append(entry)

        return result

    def _parse_ad_targeting(self) -> dict | None:
        """Extract ad targeting criteria."""
        targeting = self._data.get("ad_targeting", [])
        if not targeting:
            return None

        t = targeting[0]

        # Collect all non-empty targeting attributes
        result = {}
        for key, value in t.items():
            if value:
                # Normalize key
                normalized_key = key.lower().replace(" ", "_")
                result[normalized_key] = value

        return result if result else None

    def _parse_lan_ads(self) -> list[dict]:
        """Extract LinkedIn Audience Network ad engagement."""
        ads = self._data.get("lan_ads_engagement", [])
        result = []

        for ad in ads:
            date = ad.get("Date", "")
            if not date:
                continue

            entry = {
                "action": ad.get("Action", "") or None,
                "date": date,
                "ad_id": ad.get("Ad Title/Id", "") or None,
                "page_app": ad.get("Page/App", "") or None,
            }
            result.append(entry)

        return result

    def _parse_inferences(self) -> list[dict]:
        """Extract LinkedIn's inferences about the user."""
        inferences = self._data.get("inferences_about_you", [])
        result = []

        for inf in inferences:
            category = inf.get("Category", "")

            entry = {
                "category": category or None,
                "type": inf.get("Type of inference", "") or None,
                "description": inf.get("Description", "") or None,
                "inference": inf.get("Inference", "") or None,
            }
            result.append(entry)

        return result

    def _parse_receipts(self) -> list[dict]:
        """Extract payment receipts from both v1 and v2 formats."""
        result = []
        receipts = self._merge_csv_sources(["receipts", "receipts_v2"])

        for r in receipts:
            date = r.get("Transaction Made At", "")

            entry = {
                "date": date or None,
                "description": r.get("Description", "") or None,
                "amount": r.get("Total Amount", "") or None,
                "currency": r.get("Currency Code", "") or None,
                "payment_method": r.get("Payment Method Type", "") or None,
                "invoice_number": r.get("Invoice Number", "") or None,
            }
            result.append(entry)

        return result

    def _parse_service_engagements(self) -> list[dict]:
        """Extract services marketplace engagements."""
        engagements = self._data.get("engagements", [])
        result = []

        for e in engagements:
            date = e.get("Creation Time", "")

            entry = {
                "date": date or None,
                "marketplace_type": e.get("Marketplace Type", "") or None,
                "body": e.get("Body", "") or None,
                "currency": e.get("Currency Code", "") or None,
                "amount": e.get("Currency Amount", "") or None,
                "billing_unit": e.get("Billing Time Unit", "") or None,
                "free_consultation": e.get("Free Consultation included", "") or None,
            }
            result.append(entry)

        return result

    def _parse_service_opportunities(self) -> list[dict]:
        """Extract services marketplace opportunities."""
        # Note: LinkedIn has a typo in the filename "Opprtunities"
        opportunities = self._data.get("opprtunities", [])
        result = []

        for o in opportunities:
            date = o.get("Creation Time", "")

            entry = {
                "date": date or None,
                "marketplace_type": o.get("Marketplace Type", "") or None,
                "category": o.get("Service Category", "") or None,
                "location": o.get("Location", "") or None,
                "questions_answers": o.get("Questions and Answers", "") or None,
                "preferred_providers": o.get("Preferred Providers", "") or None,
                "status": o.get("Status", "") or None,
            }
            result.append(entry)

        return result

    def _parse_verifications(self) -> list[dict]:
        """Extract identity verifications."""
        verifications = self._data.get("verifications", [])
        result = []

        for v in verifications:
            entry = {
                "first_name": v.get("First name", "") or None,
                "middle_name": v.get("Middle name", "") or None,
                "last_name": v.get("Last name", "") or None,
                "verification_type": v.get("Verification type", "") or None,
                "issuing_authority": v.get("Issuing authority", "") or None,
                "document_type": v.get("Document type", "") or None,
                "provider": v.get("Verification service provider", "") or None,
                "verified_date": v.get("Verified date", "") or None,
                "expiry_date": v.get("Expiry date", "") or None,
            }
            result.append(entry)

        return result

    def _parse_identity_assets(self) -> list[dict]:
        """Extract private identity assets (uploaded resumes, etc.)."""
        assets = self._data.get("private_identity_asset", [])
        result = []

        for a in assets:
            name = a.get("Private Identity Asset Name", "")
            if not name:
                continue

            # Extract just the filename, not the full text content
            entry = {
                "name": name,
                "has_content": bool(a.get("Private Identity Asset Raw Text", "")),
            }
            result.append(entry)

        return result

    def _parse_datetime(self, date_str: str) -> str | None:
        """Parse datetime format like '08/19/24, 11:04 PM'."""
        if not date_str:
            return None

        try:
            date_part = date_str.split(",")[0]
            parts = date_part.split("/")
            if len(parts) == 3:
                month, day, year = parts
                year = f"20{year}" if int(year) < 50 else f"19{year}"
                return f"{MONTHS[int(month)]} {year}"
        except (ValueError, IndexError):
            pass

        return date_str.split(",")[0] if date_str else None

    def _parse_utc_date(self, date_str: str) -> str | None:
        """Parse UTC date format like '2022/01/16 02:51:39 UTC'."""
        if not date_str:
            return None

        try:
            date_part = date_str.split(" ")[0]
            parts = date_part.split("/")
            if len(parts) == 3:
                year, month, day = parts
                return f"{MONTHS[int(month)]} {year}"
        except (ValueError, IndexError):
            pass

        return None

    def _format_date(self, date_str: str) -> str:
        """Format date string to readable format."""
        if not date_str:
            return ""

        if " " in date_str and len(date_str.split()) == 2:
            return date_str

        parts = date_str.split("-")
        if len(parts) >= 2:
            try:
                month_idx = int(parts[1])
                return f"{MONTHS[month_idx]} {parts[0]}"
            except (ValueError, IndexError):
                return parts[0]

        return date_str
