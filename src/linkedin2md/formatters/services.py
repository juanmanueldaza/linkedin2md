"""Services marketplace section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class ServiceEngagementsFormatter(BaseFormatter):
    """Format service engagements section."""

    @property
    def section_key(self) -> str:
        return "service_engagements"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Service Marketplace Engagements", ""]
        lines.append("| Date | Type | Amount | Currency |")
        lines.append("|------|------|--------|----------|")

        for e in data:
            date = e.get("date", "") or ""
            mtype = e.get("marketplace_type", "") or ""
            amount = e.get("amount", "") or ""
            currency = e.get("currency", "") or ""
            lines.append(f"| {date} | {mtype} | {amount} | {currency} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class ServiceOpportunitiesFormatter(BaseFormatter):
    """Format service opportunities section."""

    @property
    def section_key(self) -> str:
        return "service_opportunities"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Service Marketplace Opportunities", ""]

        for opp in data:
            date = opp.get("date", "") or ""
            category = opp.get("category", "") or ""
            location = opp.get("location", "") or ""
            status = opp.get("status", "") or ""

            lines.append(f"## {category}")
            lines.append(f"**Date:** {date}")
            if location:
                lines.append(f"**Location:** {location}")
            if status:
                lines.append(f"**Status:** {status}")

            qa = opp.get("questions_answers", "")
            if qa:
                lines.append("")
                lines.append("**Details:**")
                lines.append(f"> {qa}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
