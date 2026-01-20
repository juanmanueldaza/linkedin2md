"""Learning section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class LearningFormatter(BaseFormatter):
    """Format LinkedIn Learning section."""

    @property
    def section_key(self) -> str:
        return "learning"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# LinkedIn Learning", ""]

        for course in data:
            title = course.get("title", "")
            completed = course.get("completed_at")
            status = "Completed" if completed else "In Progress"
            lines.append(f"- **{title}** ({status})")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class LearningReviewsFormatter(BaseFormatter):
    """Format learning reviews section."""

    @property
    def section_key(self) -> str:
        return "learning_reviews"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Learning Reviews", ""]
        lines.append("| Content | Rating | Date |")
        lines.append("|---------|--------|------|")

        for review in data:
            content = review.get("content", "")
            rating = review.get("rating", "")
            date = review.get("date", "")
            lines.append(f"| {content} | {rating} | {date} |")

        lines.append("")
        return "\n".join(lines)
