"""Job-related section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class JobApplicationsFormatter(BaseFormatter):
    """Format job applications section."""

    @property
    def section_key(self) -> str:
        return "job_applications"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Job Applications", ""]
        lines.append("| Date | Company | Position | Resume |")
        lines.append("|------|---------|----------|--------|")

        for app in data:
            date = app.get("date", "")
            company = app.get("company", "")
            title = app.get("title", "")
            resume = app.get("resume_used", "") or ""
            lines.append(f"| {date} | {company} | {title} | {resume} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class SavedJobsFormatter(BaseFormatter):
    """Format saved jobs section."""

    @property
    def section_key(self) -> str:
        return "saved_jobs"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Saved Jobs", ""]
        lines.append("| Date | Company | Position |")
        lines.append("|------|---------|----------|")

        for job in data:
            date = job.get("date", "")
            company = job.get("company", "")
            title = job.get("title", "")
            lines.append(f"| {date} | {company} | {title} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class JobPreferencesFormatter(BaseFormatter):
    """Format job preferences section."""

    @property
    def section_key(self) -> str:
        return "job_preferences"

    def format(self, data: dict | None, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Job Seeker Preferences", ""]

        if data.get("locations"):
            lines.append(f"**Locations:** {', '.join(data['locations'])}")
            lines.append("")

        if data.get("job_titles"):
            lines.append(f"**Job Titles:** {', '.join(data['job_titles'])}")
            lines.append("")

        if data.get("job_types"):
            lines.append(f"**Job Types:** {', '.join(data['job_types'])}")
            lines.append("")

        if data.get("industries"):
            lines.append(f"**Industries:** {', '.join(data['industries'])}")
            lines.append("")

        if data.get("open_to_recruiters"):
            lines.append("**Open to Recruiters:** Yes")
            lines.append("")

        if data.get("dream_companies"):
            lines.append(f"**Dream Companies:** {', '.join(data['dream_companies'])}")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class SavedJobAnswersFormatter(BaseFormatter):
    """Format saved job answers section."""

    @property
    def section_key(self) -> str:
        return "saved_job_answers"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Saved Job Application Answers", ""]

        for answer in data:
            question = answer.get("question", "")
            ans = answer.get("answer", "") or ""
            lines.append(f"**Q:** {question}")
            lines.append(f"**A:** {ans}")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class ScreeningResponsesFormatter(BaseFormatter):
    """Format screening responses section."""

    @property
    def section_key(self) -> str:
        return "screening_responses"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Screening Question Responses", ""]

        for i, response in enumerate(data, 1):
            lines.append(f"## Response {i}")
            for key, value in response.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class SavedJobAlertsFormatter(BaseFormatter):
    """Format saved job alerts section."""

    @property
    def section_key(self) -> str:
        return "saved_job_alerts"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Saved Job Alerts", ""]

        for alert in data:
            search_id = alert.get("search_id", "")
            query = alert.get("query_context", "") or ""
            lines.append(f"**Alert ID:** {search_id}")
            if query:
                lines.append(f"**Query:** {query}")
            lines.append("")

        return "\n".join(lines)
