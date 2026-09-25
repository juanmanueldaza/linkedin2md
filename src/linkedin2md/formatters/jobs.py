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

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Job Applications", ""]
        lines.append("| Date | Company | Position | Status | Resume |")
        lines.append("|------|---------|----------|--------|--------|")

        for app in data:
            date = self._escape_table_cell(app.get("date", ""))
            company = self._escape_table_cell(app.get("company", ""))
            title = self._escape_table_cell(app.get("title", ""))
            status = self._escape_table_cell(app.get("status", ""))
            resume = self._escape_table_cell(app.get("resume_used", ""))
            lines.append(f"| {date} | {company} | {title} | {status} | {resume} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class SavedJobsFormatter(BaseFormatter):
    """Format saved jobs section."""

    @property
    def section_key(self) -> str:
        return "saved_jobs"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Saved Jobs", ""]
        lines.append("| Date | Company | Position |")
        lines.append("|------|---------|----------|")

        for job in data:
            date = self._escape_table_cell(job.get("date", ""))
            company = self._escape_table_cell(job.get("company", ""))
            title = self._escape_table_cell(job.get("title", ""))
            lines.append(f"| {date} | {company} | {title} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class JobPreferencesFormatter(BaseFormatter):
    """Format job preferences section."""

    @property
    def section_key(self) -> str:
        return "job_preferences"

    def _format_content(self, data: dict, lang: str) -> str:
        lines = ["# Job Seeker Preferences", ""]

        if data.get("locations"):
            lines.append(f"**Locations:** {self._escape_joined(data['locations'])}")
            lines.append("")

        if data.get("job_titles"):
            lines.append(f"**Job Titles:** {self._escape_joined(data['job_titles'])}")
            lines.append("")

        if data.get("job_types"):
            lines.append(f"**Job Types:** {self._escape_joined(data['job_types'])}")
            lines.append("")

        if data.get("industries"):
            lines.append(f"**Industries:** {self._escape_joined(data['industries'])}")
            lines.append("")

        if data.get("open_to_recruiters"):
            lines.append("**Open to Recruiters:** Yes")
            lines.append("")

        if data.get("dream_companies"):
            lines.append(
                f"**Dream Companies:** {self._escape_joined(data['dream_companies'])}"
            )
            lines.append("")

        return "\n".join(lines)


@register_formatter
class SavedJobAnswersFormatter(BaseFormatter):
    """Format saved job answers section."""

    @property
    def section_key(self) -> str:
        return "saved_job_answers"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Saved Job Application Answers", ""]

        for answer in data:
            question = self._escape_inline(answer.get("question", "")).replace(
                "\n", " "
            )
            ans = self._escape_inline(answer.get("answer", "") or "").replace("\n", " ")
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

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Screening Question Responses", ""]

        for i, response in enumerate(data, 1):
            lines.append(f"## Response {i}")
            for key, value in response.items():
                formatted_key = self._escape_inline(
                    str(key).replace("_", " ").title()
                ).replace("\n", " ")
                formatted_value = self._escape_list_item(value)
                lines.append(f"- **{formatted_key}:** {formatted_value}")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class SavedJobAlertsFormatter(BaseFormatter):
    """Format saved job alerts section."""

    @property
    def section_key(self) -> str:
        return "saved_job_alerts"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Saved Job Alerts", ""]

        for alert in data:
            search_id = self._escape_inline(alert.get("search_id", "")).replace(
                "\n", " "
            )
            query = self._escape_inline(alert.get("query_context", "") or "").replace(
                "\n", " "
            )
            lines.append(f"**Alert ID:** {search_id}")
            if query:
                lines.append(f"**Query:** {query}")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class JobDescriptionFormatter(BaseFormatter):
    """Format job descriptions section."""

    @property
    def section_key(self) -> str:
        return "job_descriptions"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Job Descriptions", ""]

        for job in data:
            company = job.get("company", "")
            title = job.get("title", "")
            description = job.get("description", "") or ""
            date_applied = job.get("date_applied", "") or ""
            status = job.get("status", "") or ""

            heading = self._escape_heading(company or title or "Unknown")
            lines.append(f"## {heading}")
            if company and title:
                title_value = self._escape_inline(title).replace("\n", " ")
                lines.append(f"**Title:** {title_value}")
            elif not company and title:
                lines.append("**Company:** (not specified)")
            if company and not title:
                lines.append("**Title:** (not specified)")
            if description:
                lines.append(f"**Description:** {self._escape_block(description)}")
            if date_applied:
                date_value = self._escape_inline(date_applied).replace("\n", " ")
                lines.append(f"**Date Applied:** {date_value}")
            if status:
                status_value = self._escape_inline(status).replace("\n", " ")
                lines.append(f"**Status:** {status_value}")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
