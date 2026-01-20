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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Identity Verifications", ""]

        for v in data:
            name_parts = [
                v.get("first_name", ""),
                v.get("middle_name", ""),
                v.get("last_name", ""),
            ]
            name = " ".join(p for p in name_parts if p and p != "N/A")

            lines.append(f"## {name}")
            if v.get("verification_type"):
                lines.append(f"**Type:** {v['verification_type']}")
            if v.get("document_type"):
                lines.append(f"**Document:** {v['document_type']}")
            if v.get("provider"):
                lines.append(f"**Provider:** {v['provider']}")
            if v.get("verified_date"):
                lines.append(f"**Verified:** {v['verified_date']}")
            if v.get("expiry_date") and v.get("expiry_date") != "N/A":
                lines.append(f"**Expires:** {v['expiry_date']}")

            lines.append("")

        return "\n".join(lines)


@register_formatter
class IdentityAssetsFormatter(BaseFormatter):
    """Format identity assets section."""

    @property
    def section_key(self) -> str:
        return "identity_assets"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Uploaded Documents", ""]

        for asset in data:
            name = asset.get("name", "")
            has_content = asset.get("has_content", False)
            status = "(with content)" if has_content else "(no content)"
            lines.append(f"- {name} {status}")

        lines.append("")
        return "\n".join(lines)
