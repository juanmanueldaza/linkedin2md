"""Services marketplace section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class ServiceEngagementsParser(BaseParser):
    """Parse services marketplace engagements."""

    @property
    def section_key(self) -> str:
        return "service_engagements"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        engagements = self._get_csv(raw_data, "engagements")
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


@register_parser
class ServiceOpportunitiesParser(BaseParser):
    """Parse services marketplace opportunities."""

    @property
    def section_key(self) -> str:
        return "service_opportunities"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        # Note: LinkedIn has a typo in the filename "Opprtunities"
        opportunities = self._get_csv(raw_data, "opprtunities")
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
