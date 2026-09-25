"""Professional section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class SkillsFormatter(BaseFormatter):
    """Format skills section."""

    @property
    def section_key(self) -> str:
        return "skills"

    def _format_content(self, data: list, lang: str) -> str:
        return "# Skills\n\n" + self._escape_joined(data) + "\n"


@register_formatter
class ExperienceFormatter(BaseFormatter):
    """Format experience section."""

    @property
    def section_key(self) -> str:
        return "experience"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Experience", ""]

        for exp in data:
            company = self._escape_heading(exp.get("company", ""))
            role = self._get_text(exp.get("role"), lang)

            lines.append(f"## {company}")

            date_parts = []
            if exp.get("start"):
                date_parts.append(self._escape_inline(exp["start"]).replace("\n", " "))
            if exp.get("end"):
                date_parts.append(self._escape_inline(exp["end"]).replace("\n", " "))
            else:
                date_parts.append("Present")

            location = self._escape_inline(exp.get("location", "")).replace("\n", " ")
            role_value = self._escape_inline(role).replace("\n", " ")
            meta = f"**{role_value}**" if role else ""
            if date_parts:
                meta += " | " + " - ".join(date_parts)
            if location:
                meta += f" | {location}"
            if meta:
                lines.append(meta)
            lines.append("")

            achievements = exp.get("achievements", [])
            for ach in achievements:
                text = self._get_text(ach.get("text"), lang)
                if text:
                    lines.append(f"- {self._escape_list_item(text)}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class EducationFormatter(BaseFormatter):
    """Format education section."""

    @property
    def section_key(self) -> str:
        return "education"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Education", ""]

        for edu in data:
            institution = self._escape_heading(edu.get("institution", ""))
            degree = self._get_text(edu.get("degree"), lang)

            lines.append(f"## {institution}")

            meta_parts = []
            if degree:
                degree_value = self._escape_inline(degree).replace("\n", " ")
                meta_parts.append(f"**{degree_value}**")
            if edu.get("start"):
                date_parts = [self._escape_inline(edu["start"]).replace("\n", " ")]
                if edu.get("end"):
                    date_parts.append(
                        self._escape_inline(edu["end"]).replace("\n", " ")
                    )
                meta_parts.append(" - ".join(date_parts))
            if meta_parts:
                lines.append(" | ".join(meta_parts))
            lines.append("")

            field = edu.get("field")
            if field:
                field_value = self._escape_inline(field).replace("\n", " ")
                lines.append(f"**Field of Study:** {field_value}")
                lines.append("")

            grade = edu.get("grade")
            if grade:
                grade_value = self._escape_inline(grade).replace("\n", " ")
                lines.append(f"**Grade:** {grade_value}")
                lines.append("")

            notes = self._get_text(edu.get("notes"), lang)
            if notes:
                lines.append(self._blockquote(notes))
                lines.append("")

            activities = edu.get("activities")
            if activities:
                activity_value = self._escape_inline(activities).replace("\n", " ")
                lines.append(f"Activities: {activity_value}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class CertificationsFormatter(BaseFormatter):
    """Format certifications section."""

    @property
    def section_key(self) -> str:
        return "certifications"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Certifications", ""]

        for cert in data:
            name = self._escape_heading(cert.get("name", ""))
            lines.append(f"## {name}")

            meta_parts = []
            if cert.get("issuer"):
                issuer = self._escape_inline(cert["issuer"]).replace("\n", " ")
                meta_parts.append(f"**{issuer}**")
            if cert.get("date"):
                date = self._escape_inline(cert["date"]).replace("\n", " ")
                meta_parts.append(date)
            if meta_parts:
                lines.append(" | ".join(meta_parts))

            link = self._render_link("View Certificate", cert.get("url"))
            if link:
                lines.append("")
                lines.append(link)

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class LanguagesFormatter(BaseFormatter):
    """Format languages section."""

    @property
    def section_key(self) -> str:
        return "languages"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Languages", ""]

        for language in data:
            name = self._escape_list_item(language.get("name", ""))
            proficiency = self._escape_inline(language.get("proficiency", "")).replace(
                "\n", " "
            )
            if proficiency:
                lines.append(f"- **{name}**: {proficiency}")
            else:
                lines.append(f"- {name}")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class ProjectsFormatter(BaseFormatter):
    """Format projects section."""

    @property
    def section_key(self) -> str:
        return "projects"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Projects", ""]

        for proj in data:
            title = self._escape_heading(proj.get("title", ""))
            lines.append(f"## {title}")

            date_parts = []
            if proj.get("start"):
                date_parts.append(self._escape_inline(proj["start"]).replace("\n", " "))
            if proj.get("end"):
                date_parts.append(self._escape_inline(proj["end"]).replace("\n", " "))
            if date_parts:
                lines.append(" - ".join(date_parts))

            description = self._get_text(proj.get("description"), lang)
            if description:
                lines.append("")
                lines.append(self._escape_block(description))

            link = self._render_link("View Project", proj.get("url"))
            if link:
                lines.append("")
                lines.append(link)

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
