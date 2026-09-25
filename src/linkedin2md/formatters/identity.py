"""Identity section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class VerificationsFormatter(BaseFormatter):
    """Format verifications section."""

    @property
    def section_key(self) -> str:
        return "verifications"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Identity Verifications", ""]

        for v in data:
            name_parts = [
                v.get("first_name", ""),
                v.get("middle_name", ""),
                v.get("last_name", ""),
            ]
            name = self._escape_joined(
                " ".join(p for p in name_parts if p and p != "N/A")
            )

            lines.append(f"## {name}")
            if v.get("verification_type"):
                value = self._escape_inline(v["verification_type"]).replace("\n", " ")
                lines.append(f"**Type:** {value}")
            if v.get("document_type"):
                value = self._escape_inline(v["document_type"]).replace("\n", " ")
                lines.append(f"**Document:** {value}")
            if v.get("provider"):
                value = self._escape_inline(v["provider"]).replace("\n", " ")
                lines.append(f"**Provider:** {value}")
            if v.get("verified_date"):
                value = self._escape_inline(v["verified_date"]).replace("\n", " ")
                lines.append(f"**Verified:** {value}")
            if v.get("expiry_date") and v.get("expiry_date") != "N/A":
                value = self._escape_inline(v["expiry_date"]).replace("\n", " ")
                lines.append(f"**Expires:** {value}")

            lines.append("")

        return "\n".join(lines)


@register_formatter
class IdentityAssetsFormatter(BaseFormatter):
    """Format identity assets section."""

    @property
    def section_key(self) -> str:
        return "identity_assets"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Uploaded Documents", ""]

        for asset in data:
            name = self._escape_list_item(asset.get("name", ""))
            has_content = asset.get("has_content", False)
            status = "(with content)" if has_content else "(no content)"
            lines.append(f"- {name} {status}")

        lines.append("")
        return "\n".join(lines)
