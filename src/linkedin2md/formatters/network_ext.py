"""Network extension section formatters.

Formatters for additional network data: groups.
"""

from linkedin2md.formatters.base import SimpleListFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class GroupsFormatter(SimpleListFormatter):
    """Format groups section."""

    @property
    def section_key(self) -> str:
        return "groups"

    @property
    def title(self) -> str:
        return "Groups"

    @property
    def headers(self) -> list[str]:
        return ["Group", "URL"]

    @property
    def fields(self) -> list[str]:
        return ["name", "url"]

    url_fields = frozenset({"url"})
