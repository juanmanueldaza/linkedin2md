"""Advertising section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class AdsClickedParser(BaseParser):
    """Parse ads clicked history."""

    @property
    def section_key(self) -> str:
        return "ads_clicked"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        ads = self._get_csv(raw_data, "ads_clicked")
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


@register_parser
class AdTargetingParser(BaseParser):
    """Parse ad targeting criteria."""

    @property
    def section_key(self) -> str:
        return "ad_targeting"

    def parse(self, raw_data: dict[str, list[dict]]) -> dict | None:
        targeting = self._get_csv(raw_data, "ad_targeting")
        if not targeting:
            return None

        t = targeting[0]

        result = {}
        for key, value in t.items():
            if value:
                normalized_key = key.lower().replace(" ", "_")
                result[normalized_key] = value

        return result if result else None


@register_parser
class LanAdsParser(BaseParser):
    """Parse LinkedIn Audience Network ad engagement."""

    @property
    def section_key(self) -> str:
        return "lan_ads"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        ads = self._get_csv(raw_data, "lan_ads_engagement")
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


@register_parser
class InferencesParser(BaseParser):
    """Parse LinkedIn's inferences about the user."""

    @property
    def section_key(self) -> str:
        return "inferences"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        inferences = self._get_csv(raw_data, "inferences_about_you")
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
