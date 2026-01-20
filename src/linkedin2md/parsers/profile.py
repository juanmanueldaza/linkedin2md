"""Profile section parsers.

Each parser handles ONE piece of profile data (SRP).
"""

import re

from linkedin2md.parsers.base import BaseParser
from linkedin2md.protocols import BilingualText
from linkedin2md.registry import register_parser


@register_parser
class NameParser(BaseParser):
    """Parse user's name."""

    @property
    def section_key(self) -> str:
        return "name"

    def parse(self, raw_data: dict[str, list[dict]]) -> str:
        profiles = self._get_csv(raw_data, "profile")
        if not profiles:
            return ""
        profile = profiles[0]
        return self._build_name(
            profile.get("First Name", ""),
            profile.get("Last Name", ""),
        )


@register_parser
class TitleParser(BaseParser):
    """Parse user's headline/title."""

    @property
    def section_key(self) -> str:
        return "title"

    def parse(self, raw_data: dict[str, list[dict]]) -> BilingualText:
        profiles = self._get_csv(raw_data, "profile")
        if not profiles:
            return BilingualText()
        title = profiles[0].get("Headline", "")
        return self._create_bilingual(title)


@register_parser
class EmailParser(BaseParser):
    """Parse user's primary email."""

    @property
    def section_key(self) -> str:
        return "email"

    def parse(self, raw_data: dict[str, list[dict]]) -> str:
        emails = self._get_csv(raw_data, "email_addresses")
        for email in emails:
            if email.get("Primary", "").lower() == "yes":
                return email.get("Email Address", "")
        if emails:
            return emails[0].get("Email Address", "")
        return ""


@register_parser
class PhoneParser(BaseParser):
    """Parse user's phone number."""

    @property
    def section_key(self) -> str:
        return "phone"

    def parse(self, raw_data: dict[str, list[dict]]) -> str:
        phones = self._get_csv(raw_data, "phonenumbers")
        if phones:
            return phones[0].get("Number", "")
        return ""


@register_parser
class LocationParser(BaseParser):
    """Parse user's location."""

    @property
    def section_key(self) -> str:
        return "location"

    def parse(self, raw_data: dict[str, list[dict]]) -> str:
        profiles = self._get_csv(raw_data, "profile")
        if not profiles:
            return ""
        profile = profiles[0]
        return profile.get("Geo Location", "") or profile.get("Location", "")


@register_parser
class SummaryParser(BaseParser):
    """Parse user's profile summary."""

    @property
    def section_key(self) -> str:
        return "summary"

    def parse(self, raw_data: dict[str, list[dict]]) -> BilingualText:
        profiles = self._get_csv(raw_data, "profile")
        if not profiles:
            return BilingualText()
        summary = profiles[0].get("Summary", "")
        return self._create_bilingual(summary)


@register_parser
class ProfileMetaParser(BaseParser):
    """Parse profile metadata (industry, twitter, websites, etc.)."""

    @property
    def section_key(self) -> str:
        return "profile_meta"

    def parse(self, raw_data: dict[str, list[dict]]) -> dict:
        profiles = self._get_csv(raw_data, "profile")
        profile = profiles[0] if profiles else {}

        reg = self._get_csv(raw_data, "registration")
        reg_date = reg[0].get("Registered At", "") if reg else None

        connections = self._get_csv(raw_data, "connections")

        return {
            "industry": profile.get("Industry", "") or None,
            "twitter": self._parse_twitter(profile.get("Twitter Handles", "")),
            "websites": self._parse_websites(profile.get("Websites", "")),
            "birth_date": profile.get("Birth Date", "") or None,
            "registered_at": reg_date or None,
            "connections_count": len(connections),
        }

    def _parse_twitter(self, twitter_str: str) -> str | None:
        if not twitter_str:
            return None
        handle = twitter_str.strip("[]")
        return handle if handle else None

    def _parse_websites(self, websites_str: str) -> list[str]:
        if not websites_str:
            return []
        sites = re.split(r"[,;]", websites_str)
        return [s.strip() for s in sites if s.strip()]
