"""Advertising section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class AdsClickedFormatter(BaseFormatter):
    """Format ads clicked section."""

    @property
    def section_key(self) -> str:
        return "ads_clicked"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Ads Clicked", ""]
        lines.append("| Date | Ad ID |")
        lines.append("|------|-------|")

        for ad in data:
            date = self._escape_table_cell(ad.get("date", ""))
            ad_id = self._escape_table_cell(ad.get("ad_id", ""))
            lines.append(f"| {date} | {ad_id} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class AdTargetingFormatter(BaseFormatter):
    """Format ad targeting section."""

    @property
    def section_key(self) -> str:
        return "ad_targeting"

    def _format_content(self, data: dict, lang: str) -> str:
        lines = ["# Ad Targeting Criteria", ""]

        for key, value in data.items():
            if value:
                formatted_key = self._escape_inline(
                    str(key).replace("_", " ").title()
                ).replace("\n", " ")
                formatted_value = self._escape_inline(value).replace("\n", " ")
                lines.append(f"**{formatted_key}:** {formatted_value}")
                lines.append("")

        return "\n".join(lines)


@register_formatter
class LanAdsFormatter(BaseFormatter):
    """Format LinkedIn Audience Network ads section."""

    @property
    def section_key(self) -> str:
        return "lan_ads"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# LinkedIn Audience Network Ads", ""]
        lines.append("| Date | Action | Ad ID | Page/App |")
        lines.append("|------|--------|-------|----------|")

        for ad in data:
            date = self._escape_table_cell(ad.get("date", ""))
            action = self._escape_table_cell(ad.get("action", ""))
            ad_id = self._escape_table_cell(ad.get("ad_id", ""))
            page = self._escape_table_cell(ad.get("page_app", ""))
            lines.append(f"| {date} | {action} | {ad_id} | {page} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class InferencesFormatter(BaseFormatter):
    """Format inferences section."""

    @property
    def section_key(self) -> str:
        return "inferences"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# LinkedIn's Inferences About You", ""]
        lines.append("| Category | Type | Description | Inference |")
        lines.append("|----------|------|-------------|-----------|")

        for inf in data:
            category = self._escape_table_cell(inf.get("category", ""))
            itype = self._escape_table_cell(inf.get("type", ""))
            desc = self._escape_table_cell(inf.get("description", ""))
            inference = self._escape_table_cell(inf.get("inference", ""))
            lines.append(f"| {category} | {itype} | {desc} | {inference} |")

        lines.append("")
        return "\n".join(lines)
