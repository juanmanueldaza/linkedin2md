"""Recommendations and endorsements formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class RecommendationsFormatter(BaseFormatter):
    """Format recommendations received section."""

    @property
    def section_key(self) -> str:
        return "recommendations"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Recommendations", ""]

        for rec in data:
            author = rec.get("author", "")
            lines.append(f"## From {author}")

            meta_parts = []
            if rec.get("title"):
                meta_parts.append(f"**{rec['title']}**")
            if rec.get("company"):
                meta_parts.append(f"at {rec['company']}")
            if rec.get("date"):
                meta_parts.append(f"| {rec['date']}")
            if meta_parts:
                lines.append(" ".join(meta_parts))

            text = self._get_text(rec.get("text"), lang)
            if text:
                lines.append("")
                lines.append(f"> {text}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class RecommendationsGivenFormatter(BaseFormatter):
    """Format recommendations given section."""

    @property
    def section_key(self) -> str:
        return "recommendations_given"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Recommendations Given", ""]

        for rec in data:
            recipient = rec.get("recipient", "")
            lines.append(f"## To {recipient}")

            meta_parts = []
            if rec.get("title"):
                meta_parts.append(f"**{rec['title']}**")
            if rec.get("company"):
                meta_parts.append(f"at {rec['company']}")
            if rec.get("date"):
                meta_parts.append(f"| {rec['date']}")
            if meta_parts:
                lines.append(" ".join(meta_parts))

            text = self._get_text(rec.get("text"), lang)
            if text:
                lines.append("")
                lines.append(f"> {text}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class EndorsementsFormatter(BaseFormatter):
    """Format endorsements received section."""

    @property
    def section_key(self) -> str:
        return "endorsements"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Endorsements", ""]
        lines.append("| Skill | Endorsed By | Date |")
        lines.append("|-------|-------------|------|")

        for end in data:
            skill = end.get("skill", "")
            endorser = end.get("endorser", "")
            date = end.get("date", "")
            lines.append(f"| {skill} | {endorser} | {date} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class EndorsementsGivenFormatter(BaseFormatter):
    """Format endorsements given section."""

    @property
    def section_key(self) -> str:
        return "endorsements_given"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Endorsements Given", ""]
        lines.append("| Skill | Endorsed | Date |")
        lines.append("|-------|----------|------|")

        for end in data:
            skill = end.get("skill", "")
            endorsee = end.get("endorsee", "")
            date = end.get("date", "")
            lines.append(f"| {skill} | {endorsee} | {date} |")

        lines.append("")
        return "\n".join(lines)
