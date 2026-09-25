"""Content section formatters.

Each formatter handles ONE section (SRP).
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class PostsFormatter(BaseFormatter):
    """Format posts section."""

    @property
    def section_key(self) -> str:
        return "posts"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Posts", ""]

        for post in data:
            date = self._escape_heading(post.get("date", ""))
            lines.append(f"## {date}")

            content = self._get_text(post.get("content"), lang)
            if content:
                lines.append("")
                lines.append(self._escape_block(content))

            link = self._render_link("View Post", post.get("url"))
            if link:
                lines.append("")
                lines.append(link)

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class CommentsFormatter(BaseFormatter):
    """Format comments section."""

    @property
    def section_key(self) -> str:
        return "comments"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Comments", ""]

        for comment in data:
            date = self._escape_inline(comment.get("date", "")).replace("\n", " ")
            message = self._get_text(comment.get("message"), lang)
            link = self._render_link("View", comment.get("url", ""))

            lines.append(f"**{date}**")
            if message:
                lines.append(self._blockquote(message))
            if link:
                lines.append(link)
            lines.append("")

        return "\n".join(lines)


@register_formatter
class ReactionsFormatter(BaseFormatter):
    """Format reactions section."""

    @property
    def section_key(self) -> str:
        return "reactions"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Reactions", ""]
        lines.append("| Date | Type | Link |")
        lines.append("|------|------|------|")

        for reaction in data:
            date = self._escape_table_cell(reaction.get("date", ""))
            rtype = self._escape_table_cell(reaction.get("type", ""))
            link = self._render_table_link("View", reaction.get("url", ""))
            lines.append(f"| {date} | {rtype} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class RepostsFormatter(BaseFormatter):
    """Format reposts section."""

    @property
    def section_key(self) -> str:
        return "reposts"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Reposts", ""]
        lines.append("| Date | Link |")
        lines.append("|------|------|")

        for repost in data:
            date = self._escape_table_cell(repost.get("date", ""))
            link = self._render_table_link("View", repost.get("url", ""))
            lines.append(f"| {date} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class VotesFormatter(BaseFormatter):
    """Format votes section."""

    @property
    def section_key(self) -> str:
        return "votes"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Poll Votes", ""]
        lines.append("| Date | Option | Link |")
        lines.append("|------|--------|------|")

        for vote in data:
            date = self._escape_table_cell(vote.get("date", ""))
            option = self._escape_table_cell(vote.get("option", ""))
            link = self._render_table_link("View", vote.get("url", ""))
            lines.append(f"| {date} | {option} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class SavedItemsFormatter(BaseFormatter):
    """Format saved items section."""

    @property
    def section_key(self) -> str:
        return "saved_items"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Saved Items", ""]
        lines.append("| Saved At | Link |")
        lines.append("|----------|------|")

        for item in data:
            saved_at = self._escape_table_cell(item.get("saved_at", ""))
            link = self._render_table_link("View", item.get("url", ""))
            lines.append(f"| {saved_at} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class EventsFormatter(BaseFormatter):
    """Format events section."""

    @property
    def section_key(self) -> str:
        return "events"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Events", ""]
        lines.append("| Name | Time | Status |")
        lines.append("|------|------|--------|")

        for event in data:
            name = self._escape_table_cell(event.get("name", ""))
            time = self._escape_table_cell(event.get("time", ""))
            status = self._escape_table_cell(event.get("status", ""))
            lines.append(f"| {name} | {time} | {status} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class MediaFormatter(BaseFormatter):
    """Format uploaded media section."""

    @property
    def section_key(self) -> str:
        return "media"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Uploaded Media", ""]
        lines.append("| Date | Description | Link |")
        lines.append("|------|-------------|------|")

        for m in data:
            date = self._escape_table_cell(m.get("date", ""))
            desc = self._escape_table_cell(m.get("description", ""))
            link = self._render_table_link("View", m.get("url", ""))
            lines.append(f"| {date} | {desc} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class MessagesFormatter(BaseFormatter):
    """Format messages section."""

    @property
    def section_key(self) -> str:
        return "messages"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Messages", ""]

        for msg in data:
            date = self._escape_heading(msg.get("date", ""))
            from_name = self._escape_inline(msg.get("from_name", "")).replace("\n", " ")
            to_name = self._escape_inline(msg.get("to_name", "")).replace("\n", " ")
            subject = self._escape_inline(msg.get("subject", "") or "").replace(
                "\n", " "
            )
            content = msg.get("content", "") or ""

            lines.append(f"## {date}")
            lines.append(f"**From:** {from_name} → **To:** {to_name}")
            if subject:
                lines.append(f"**Subject:** {subject}")
            if content:
                lines.append("")
                truncated = self._truncate_text(content, 500, "message.content")
                lines.append(self._blockquote(truncated))
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class ScriptFormatter(BaseFormatter):
    """Format scripts section."""

    @property
    def section_key(self) -> str:
        return "scripts"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Scripts", ""]

        for script in data:
            name = self._escape_heading(script.get("name", ""))
            date = self._escape_inline(script.get("date", "")).replace("\n", " ")
            content = script.get("content", "") or ""

            lines.append(f"## {name}")
            if date:
                lines.append(f"**Date:** {date}")
            if content:
                lines.append("")
                lines.append(self._escape_block(content))
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class ArticlesFormatter(BaseFormatter):
    """Format published articles section."""

    @property
    def section_key(self) -> str:
        return "articles"

    def _format_content(self, data: list, lang: str) -> str:
        lines = ["# Published Articles", ""]

        for article in data:
            title = self._escape_heading(article.get("title", ""))
            date = self._escape_inline(article.get("date", "")).replace("\n", " ")
            author = self._escape_inline(article.get("author", "")).replace("\n", " ")
            summary = article.get("summary", "")

            lines.append(f"## {title}")
            if date:
                lines.append(f"**Date:** {date}")
            if author:
                lines.append(f"**Author:** {author}")
            if summary:
                lines.append("")
                lines.append(self._escape_block(summary))
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
