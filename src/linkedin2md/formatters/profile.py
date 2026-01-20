"""Profile section formatter.

Single Responsibility: Format profile data to Markdown.
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class ProfileFormatter(BaseFormatter):
    """Format complete profile section."""

    @property
    def section_key(self) -> str:
        return "profile"

    def format(self, data: dict, lang: str) -> str:
        """Format profile data.

        Note: This formatter receives the full data dict to build a complete profile.
        """
        lines = []

        name = data.get("name", "")
        if name:
            lines.append(f"# {name}")
            lines.append("")

        title = self._get_text(data.get("title"), lang)
        if title:
            lines.append(f"**{title}**")
            lines.append("")

        contact_parts = []
        if data.get("location"):
            contact_parts.append(data["location"])
        if data.get("email"):
            contact_parts.append(data["email"])
        if data.get("phone"):
            contact_parts.append(data["phone"])
        if contact_parts:
            lines.append(" | ".join(contact_parts))
            lines.append("")

        summary = self._get_text(data.get("summary"), lang)
        if summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(summary)
            lines.append("")

        return "\n".join(lines)
