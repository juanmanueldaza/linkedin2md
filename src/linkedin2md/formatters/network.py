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
            name = self._escape_table_cell(conn.get("name", ""))
            company = self._escape_table_cell(conn.get("company", ""))
            position = self._escape_table_cell(conn.get("position", ""))
            connected = self._escape_table_cell(conn.get("connected_on", ""))
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
            name = self._escape_table_cell(member.get("name", ""))
            date = self._escape_table_cell(member.get("date", ""))
            status = self._escape_table_cell(member.get("status", ""))
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
            from_name = self._escape_table_cell(inv.get("from", ""))
            to_name = self._escape_table_cell(inv.get("to", ""))
            date = self._escape_table_cell(inv.get("sent_at", ""))
            direction = self._escape_table_cell(inv.get("direction", ""))
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
            name = self._escape_table_cell(contact.get("name", ""))
            emails = self._escape_table_cell(contact.get("emails", ""))
            title = self._escape_table_cell(contact.get("title", ""))
            lines.append(f"| {name} | {emails} | {title} |")

        lines.append("")
        return "\n".join(lines)
