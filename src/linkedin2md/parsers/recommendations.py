"""Recommendations and endorsements parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class RecommendationsParser(BaseParser):
    """Parse recommendations received."""

    @property
    def section_key(self) -> str:
        return "recommendations"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        recs = self._get_csv(raw_data, "recommendations_received")
        result = []

        for r in recs:
            text = r.get("Text", "")
            status = r.get("Status", "")

            if not text or status != "VISIBLE":
                continue

            text_lang = self._detect_language(text)

            rec = {
                "author": self._build_name(
                    r.get("First Name", ""), r.get("Last Name", "")
                ),
                "title": r.get("Job Title", "") or None,
                "company": r.get("Company", "") or None,
                "text": self._create_bilingual(text, text_lang),
                "date": self._parse_datetime(r.get("Creation Date", "")),
            }
            result.append(rec)

        return result


@register_parser
class RecommendationsGivenParser(BaseParser):
    """Parse recommendations given to others."""

    @property
    def section_key(self) -> str:
        return "recommendations_given"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        recs = self._get_csv(raw_data, "recommendations_given")
        result = []

        for r in recs:
            text = r.get("Text", "")
            if not text:
                continue

            text_lang = self._detect_language(text)

            rec = {
                "recipient": self._build_name(
                    r.get("First Name", ""), r.get("Last Name", "")
                ),
                "title": r.get("Job Title", "") or None,
                "company": r.get("Company", "") or None,
                "text": self._create_bilingual(text, text_lang),
                "date": self._parse_datetime(r.get("Creation Date", "")),
            }
            result.append(rec)

        return result


@register_parser
class EndorsementsParser(BaseParser):
    """Parse skill endorsements received."""

    @property
    def section_key(self) -> str:
        return "endorsements"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        endorsements = self._get_csv(raw_data, "endorsement_received_info")
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


@register_parser
class EndorsementsGivenParser(BaseParser):
    """Parse skill endorsements given to others."""

    @property
    def section_key(self) -> str:
        return "endorsements_given"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        endorsements = self._get_csv(raw_data, "endorsement_given_info")
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
