"""Network section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class ConnectionsFormatter(BaseFormatter):
    """Format connections section."""

    @property
    def section_key(self) -> str:
        return "connections"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Connections", ""]
        lines.append("| Name | Company | Position | Connected |")
        lines.append("|------|---------|----------|-----------|")

        for conn in data:
            name = conn.get("name", "")
            company = conn.get("company", "") or ""
            position = conn.get("position", "") or ""
            connected = conn.get("connected_on", "") or ""
            lines.append(f"| {name} | {company} | {position} | {connected} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class CompaniesFollowedFormatter(BaseFormatter):
    """Format companies followed section."""

    @property
    def section_key(self) -> str:
        return "companies_followed"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Companies Followed", ""]
        for company in data:
            name = company.get("name", "")
            lines.append(f"- {name}")
        lines.append("")
        return "\n".join(lines)


@register_formatter
class MembersFollowedFormatter(BaseFormatter):
    """Format members followed section."""

    @property
    def section_key(self) -> str:
        return "members_followed"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Members Followed", ""]
        lines.append("| Name | Date | Status |")
        lines.append("|------|------|--------|")

        for member in data:
            name = member.get("name", "")
            date = member.get("date", "") or ""
            status = member.get("status", "") or ""
            lines.append(f"| {name} | {date} | {status} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class InvitationsFormatter(BaseFormatter):
    """Format invitations section."""

    @property
    def section_key(self) -> str:
        return "invitations"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Connection Invitations", ""]
        lines.append("| From | To | Date | Direction |")
        lines.append("|------|-----|------|-----------|")

        for inv in data:
            from_name = inv.get("from", "")
            to_name = inv.get("to", "")
            date = inv.get("sent_at", "") or ""
            direction = inv.get("direction", "") or ""
            lines.append(f"| {from_name} | {to_name} | {date} | {direction} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class ImportedContactsFormatter(BaseFormatter):
    """Format imported contacts section."""

    @property
    def section_key(self) -> str:
        return "imported_contacts"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Imported Contacts", ""]
        lines.append("| Name | Email | Title |")
        lines.append("|------|-------|-------|")

        for contact in data:
            name = contact.get("name", "") or ""
            emails = contact.get("emails", "") or ""
            title = contact.get("title", "") or ""
            lines.append(f"| {name} | {emails} | {title} |")

        lines.append("")
        return "\n".join(lines)
