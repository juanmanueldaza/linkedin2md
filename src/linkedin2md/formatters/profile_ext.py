"""Profile extension section formatters.

Formatters for additional profile data: causes, interests, courses,
honors/awards, test scores, patents, organizations, publications,
and volunteer experience.
"""

from linkedin2md.formatters.base import SimpleListFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class CausesFormatter(SimpleListFormatter):
    """Format causes section."""

    @property
    def section_key(self) -> str:
        return "causes"

    @property
    def title(self) -> str:
        return "Causes"

    @property
    def headers(self) -> list[str]:
        return ["Cause"]

    @property
    def fields(self) -> list[str]:
        return ["name"]


@register_formatter
class InterestsFormatter(SimpleListFormatter):
    """Format interests section."""

    @property
    def section_key(self) -> str:
        return "interests"

    @property
    def title(self) -> str:
        return "Interests"

    @property
    def headers(self) -> list[str]:
        return ["Interest"]

    @property
    def fields(self) -> list[str]:
        return ["name"]


@register_formatter
class CoursesFormatter(SimpleListFormatter):
    """Format courses section."""

    @property
    def section_key(self) -> str:
        return "courses"

    @property
    def title(self) -> str:
        return "Courses"

    @property
    def headers(self) -> list[str]:
        return ["Course", "School"]

    @property
    def fields(self) -> list[str]:
        return ["name", "school"]


@register_formatter
class HonorsAwardsFormatter(SimpleListFormatter):
    """Format honors and awards section."""

    @property
    def section_key(self) -> str:
        return "honors_awards"

    @property
    def title(self) -> str:
        return "Honors & Awards"

    @property
    def headers(self) -> list[str]:
        return ["Title", "Issuer", "Date", "Description"]

    @property
    def fields(self) -> list[str]:
        return ["title", "issuer", "date", "description"]


@register_formatter
class TestScoresFormatter(SimpleListFormatter):
    """Format test scores section."""

    __test__ = False  # pytest: not a test class despite Test* name

    @property
    def section_key(self) -> str:
        return "test_scores"

    @property
    def title(self) -> str:
        return "Test Scores"

    @property
    def headers(self) -> list[str]:
        return ["Test", "Score", "Date"]

    @property
    def fields(self) -> list[str]:
        return ["name", "score", "date"]


@register_formatter
class PatentsFormatter(SimpleListFormatter):
    """Format patents section."""

    @property
    def section_key(self) -> str:
        return "patents"

    @property
    def title(self) -> str:
        return "Patents"

    @property
    def headers(self) -> list[str]:
        return ["Title", "Status", "Number", "Date"]

    @property
    def fields(self) -> list[str]:
        return ["title", "status", "number", "date"]


@register_formatter
class OrganizationsFormatter(SimpleListFormatter):
    """Format organizations section."""

    @property
    def section_key(self) -> str:
        return "organizations"

    @property
    def title(self) -> str:
        return "Organizations"

    @property
    def headers(self) -> list[str]:
        return ["Organization", "Title", "Date"]

    @property
    def fields(self) -> list[str]:
        return ["name", "title", "date"]


@register_formatter
class PublicationsFormatter(SimpleListFormatter):
    """Format publications section."""

    @property
    def section_key(self) -> str:
        return "publications"

    @property
    def title(self) -> str:
        return "Publications"

    @property
    def headers(self) -> list[str]:
        return ["Title", "Publisher", "Date", "URL"]

    @property
    def fields(self) -> list[str]:
        return ["title", "publisher", "date", "url"]

    url_fields = frozenset({"url"})


@register_formatter
class VolunteerExperienceFormatter(SimpleListFormatter):
    """Format volunteer experience section."""

    @property
    def section_key(self) -> str:
        return "volunteer_experience"

    @property
    def title(self) -> str:
        return "Volunteer Experience"

    @property
    def headers(self) -> list[str]:
        return ["Role", "Organization", "Cause", "Start", "End"]

    @property
    def fields(self) -> list[str]:
        return ["role", "organization", "cause", "start_date", "end_date"]
