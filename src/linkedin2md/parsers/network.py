"""Network section parsers (connections, follows, invitations).

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class ConnectionsParser(BaseParser):
    """Parse connections."""

    @property
    def section_key(self) -> str:
        return "connections"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        connections = self._get_csv(raw_data, "connections")
        result = []

        for conn in connections:
            first = conn.get("First Name", "")
            last = conn.get("Last Name", "")
            if not first and not last:
                continue

            entry = {
                "name": self._build_name(first, last),
                "url": conn.get("URL", "") or None,
                "email": conn.get("Email Address", "") or None,
                "company": conn.get("Company", "") or None,
                "position": conn.get("Position", "") or None,
                "connected_on": conn.get("Connected On", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class CompanyFollowsParser(BaseParser):
    """Parse companies followed."""

    @property
    def section_key(self) -> str:
        return "companies_followed"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        follows = self._get_csv(raw_data, "company_follows")
        result = []

        for f in follows:
            name = f.get("Organization", "")
            if not name:
                continue

            entry = {
                "name": name,
                "followed_on": f.get("Followed On", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class MemberFollowsParser(BaseParser):
    """Parse members followed."""

    @property
    def section_key(self) -> str:
        return "members_followed"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        follows = self._get_csv(raw_data, "member_follows")
        result = []

        for f in follows:
            name = f.get("FullName", "")
            if not name:
                continue

            entry = {
                "name": name,
                "date": f.get("Date", "") or None,
                "status": f.get("Status", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class InvitationsParser(BaseParser):
    """Parse connection invitations."""

    @property
    def section_key(self) -> str:
        return "invitations"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        invitations = self._get_csv(raw_data, "invitations")
        result = []

        for inv in invitations:
            from_name = inv.get("From", "")
            to_name = inv.get("To", "")
            if not from_name and not to_name:
                continue

            entry = {
                "from": from_name,
                "to": to_name,
                "sent_at": inv.get("Sent At", "") or None,
                "message": inv.get("Message", "") or None,
                "direction": inv.get("Direction", "") or None,
                "inviter_url": inv.get("inviterProfileUrl", "") or None,
                "invitee_url": inv.get("inviteeProfileUrl", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class ImportedContactsParser(BaseParser):
    """Parse imported contacts from address book."""

    @property
    def section_key(self) -> str:
        return "imported_contacts"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        contacts = self._get_csv(raw_data, "importedcontacts")
        result = []

        for c in contacts:
            first = c.get("FirstName", "")
            middle = c.get("MiddleName", "")
            last = c.get("LastName", "")
            name_parts = [p for p in [first, middle, last] if p]
            name = " ".join(name_parts)

            emails = c.get("Emails", "")
            phones = c.get("PhoneNumbers", "")

            if not name and not emails:
                continue

            entry = {
                "name": name or None,
                "emails": emails or None,
                "phones": phones or None,
                "title": c.get("Title", "") or None,
                "location": c.get("Location", "") or None,
                "created_at": c.get("CreatedAt", "") or None,
                "updated_at": c.get("UpdatedAt", "") or None,
            }
            result.append(entry)

        return result
