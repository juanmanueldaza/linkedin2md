"""Activity history section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class SearchQueriesFormatter(BaseFormatter):
    """Format search queries section."""

    @property
    def section_key(self) -> str:
        return "search_queries"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Search History", ""]
        lines.append("| Time | Query |")
        lines.append("|------|-------|")

        for q in data:
            time = q.get("time", "")
            query = self._escape_pipe(q.get("query", ""))
            lines.append(f"| {time} | {query} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class LoginsFormatter(BaseFormatter):
    """Format logins section."""

    @property
    def section_key(self) -> str:
        return "logins"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Login History", ""]
        lines.append("| Date | IP Address | Type |")
        lines.append("|------|------------|------|")

        for login in data:
            date = login.get("date", "")
            ip = login.get("ip_address", "") or ""
            login_type = login.get("login_type", "") or ""
            lines.append(f"| {date} | {ip} | {login_type} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class SecurityChallengesFormatter(BaseFormatter):
    """Format security challenges section."""

    @property
    def section_key(self) -> str:
        return "security_challenges"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Security Challenges", ""]
        lines.append("| Date | IP Address | Country | Type |")
        lines.append("|------|------------|---------|------|")

        for c in data:
            date = c.get("date", "")
            ip = c.get("ip_address", "") or ""
            country = c.get("country", "") or ""
            ctype = c.get("challenge_type", "") or ""
            lines.append(f"| {date} | {ip} | {country} | {ctype} |")

        lines.append("")
        return "\n".join(lines)
