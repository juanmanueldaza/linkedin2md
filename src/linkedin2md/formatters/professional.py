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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""
        return "# Skills\n\n" + ", ".join(data) + "\n"


@register_formatter
class ExperienceFormatter(BaseFormatter):
    """Format experience section."""

    @property
    def section_key(self) -> str:
        return "experience"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Experience", ""]

        for exp in data:
            company = exp.get("company", "")
            role = self._get_text(exp.get("role"), lang)

            lines.append(f"## {company}")

            date_parts = []
            if exp.get("start"):
                date_parts.append(exp["start"])
            if exp.get("end"):
                date_parts.append(exp["end"])
            else:
                date_parts.append("Present")

            location = exp.get("location", "")
            meta = f"**{role}**" if role else ""
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
                    lines.append(f"- {text}")

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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Education", ""]

        for edu in data:
            institution = edu.get("institution", "")
            degree = self._get_text(edu.get("degree"), lang)

            lines.append(f"## {institution}")

            meta_parts = []
            if degree:
                meta_parts.append(f"**{degree}**")
            if edu.get("start"):
                date_str = edu["start"]
                if edu.get("end"):
                    date_str += f" - {edu['end']}"
                meta_parts.append(date_str)
            if meta_parts:
                lines.append(" | ".join(meta_parts))
            lines.append("")

            notes = self._get_text(edu.get("notes"), lang)
            if notes:
                lines.append(f"> {notes}")
                lines.append("")

            activities = edu.get("activities")
            if activities:
                lines.append(f"Activities: {activities}")
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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Certifications", ""]

        for cert in data:
            name = cert.get("name", "")
            lines.append(f"## {name}")

            meta_parts = []
            if cert.get("issuer"):
                meta_parts.append(f"**{cert['issuer']}**")
            if cert.get("date"):
                meta_parts.append(cert["date"])
            if meta_parts:
                lines.append(" | ".join(meta_parts))

            if cert.get("url"):
                lines.append("")
                lines.append(f"[View Certificate]({cert['url']})")

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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Languages", ""]

        for language in data:
            name = language.get("name", "")
            proficiency = language.get("proficiency", "")
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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Projects", ""]

        for proj in data:
            title = proj.get("title", "")
            lines.append(f"## {title}")

            date_parts = []
            if proj.get("start"):
                date_parts.append(proj["start"])
            if proj.get("end"):
                date_parts.append(proj["end"])
            if date_parts:
                lines.append(" - ".join(date_parts))

            description = self._get_text(proj.get("description"), lang)
            if description:
                lines.append("")
                lines.append(description)

            if proj.get("url"):
                lines.append("")
                lines.append(f"[View Project]({proj['url']})")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
