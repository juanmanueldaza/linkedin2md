"""Identity section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class VerificationsParser(BaseParser):
    """Parse identity verifications."""

    @property
    def section_key(self) -> str:
        return "verifications"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        verifications = self._get_csv(raw_data, "verifications")
        result = []

        for v in verifications:
            entry = {
                "first_name": v.get("First name", "") or None,
                "middle_name": v.get("Middle name", "") or None,
                "last_name": v.get("Last name", "") or None,
                "verification_type": v.get("Verification type", "") or None,
                "issuing_authority": v.get("Issuing authority", "") or None,
                "document_type": v.get("Document type", "") or None,
                "provider": v.get("Verification service provider", "") or None,
                "verified_date": v.get("Verified date", "") or None,
                "expiry_date": v.get("Expiry date", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class IdentityAssetsParser(BaseParser):
    """Parse private identity assets (uploaded resumes, etc.)."""

    @property
    def section_key(self) -> str:
        return "identity_assets"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        assets = self._get_csv(raw_data, "private_identity_asset")
        result = []

        for a in assets:
            name = a.get("Private Identity Asset Name", "")
            if not name:
                continue

            entry = {
                "name": name,
                "has_content": bool(a.get("Private Identity Asset Raw Text", "")),
            }
            result.append(entry)

        return result
