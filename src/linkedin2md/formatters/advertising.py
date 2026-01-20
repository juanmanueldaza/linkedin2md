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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Ads Clicked", ""]
        lines.append("| Date | Ad ID |")
        lines.append("|------|-------|")

        for ad in data:
            date = ad.get("date", "")
            ad_id = ad.get("ad_id", "") or ""
            lines.append(f"| {date} | {ad_id} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class AdTargetingFormatter(BaseFormatter):
    """Format ad targeting section."""

    @property
    def section_key(self) -> str:
        return "ad_targeting"

    def format(self, data: dict | None, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Ad Targeting Criteria", ""]

        for key, value in data.items():
            if value:
                formatted_key = key.replace("_", " ").title()
                lines.append(f"**{formatted_key}:** {value}")
                lines.append("")

        return "\n".join(lines)


@register_formatter
class LanAdsFormatter(BaseFormatter):
    """Format LinkedIn Audience Network ads section."""

    @property
    def section_key(self) -> str:
        return "lan_ads"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# LinkedIn Audience Network Ads", ""]
        lines.append("| Date | Action | Ad ID | Page/App |")
        lines.append("|------|--------|-------|----------|")

        for ad in data:
            date = ad.get("date", "")
            action = ad.get("action", "") or ""
            ad_id = ad.get("ad_id", "") or ""
            page = ad.get("page_app", "") or ""
            lines.append(f"| {date} | {action} | {ad_id} | {page} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class InferencesFormatter(BaseFormatter):
    """Format inferences section."""

    @property
    def section_key(self) -> str:
        return "inferences"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# LinkedIn's Inferences About You", ""]
        lines.append("| Category | Type | Description | Inference |")
        lines.append("|----------|------|-------------|-----------|")

        for inf in data:
            category = inf.get("category", "") or ""
            itype = inf.get("type", "") or ""
            desc = inf.get("description", "") or ""
            inference = inf.get("inference", "") or ""
            lines.append(f"| {category} | {itype} | {desc} | {inference} |")

        lines.append("")
        return "\n".join(lines)
