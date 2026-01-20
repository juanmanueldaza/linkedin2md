"""Activity history section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class SearchQueriesParser(BaseParser):
    """Parse search query history."""

    @property
    def section_key(self) -> str:
        return "search_queries"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        queries = self._get_csv(raw_data, "searchqueries")
        result = []

        for q in queries:
            time = q.get("Time", "")
            query = q.get("Search Query", "")

            if not query:
                continue

            entry = {
                "time": time,
                "query": query,
            }
            result.append(entry)

        return result


@register_parser
class LoginsParser(BaseParser):
    """Parse login history."""

    @property
    def section_key(self) -> str:
        return "logins"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        logins = self._get_csv(raw_data, "logins")
        result = []

        for login in logins:
            date = login.get("Login Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "ip_address": login.get("IP Address", "") or None,
                "user_agent": login.get("User Agent", "") or None,
                "login_type": login.get("Login Type", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class SecurityChallengesParser(BaseParser):
    """Parse security challenge history."""

    @property
    def section_key(self) -> str:
        return "security_challenges"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        challenges = self._get_csv(raw_data, "security_challenges")
        result = []

        for c in challenges:
            date = c.get("Challenge Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "ip_address": c.get("IP Address", "") or None,
                "user_agent": c.get("User Agent", "") or None,
                "country": c.get("Country", "") or None,
                "challenge_type": c.get("Challenge Type", "") or None,
            }
            result.append(entry)

        return result
