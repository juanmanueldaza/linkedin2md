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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Posts", ""]

        for post in data:
            date = post.get("date", "")
            lines.append(f"## {date}")

            content = self._get_text(post.get("content"), lang)
            if content:
                lines.append("")
                lines.append(content)

            if post.get("url"):
                lines.append("")
                lines.append(f"[View Post]({post['url']})")

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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Comments", ""]

        for comment in data:
            date = comment.get("date", "")
            message = self._get_text(comment.get("message"), lang)
            url = comment.get("url", "")

            lines.append(f"**{date}**")
            if message:
                lines.append(f"> {message}")
            if url:
                lines.append(f"[View]({url})")
            lines.append("")

        return "\n".join(lines)


@register_formatter
class ReactionsFormatter(BaseFormatter):
    """Format reactions section."""

    @property
    def section_key(self) -> str:
        return "reactions"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Reactions", ""]
        lines.append("| Date | Type | Link |")
        lines.append("|------|------|------|")

        for reaction in data:
            date = self._escape_table_cell(reaction.get("date", ""))
            rtype = self._escape_table_cell(reaction.get("type", ""))
            url = reaction.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {rtype} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class RepostsFormatter(BaseFormatter):
    """Format reposts section."""

    @property
    def section_key(self) -> str:
        return "reposts"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Reposts", ""]
        lines.append("| Date | Link |")
        lines.append("|------|------|")

        for repost in data:
            date = self._escape_table_cell(repost.get("date", ""))
            url = repost.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class VotesFormatter(BaseFormatter):
    """Format votes section."""

    @property
    def section_key(self) -> str:
        return "votes"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Poll Votes", ""]
        lines.append("| Date | Option | Link |")
        lines.append("|------|--------|------|")

        for vote in data:
            date = self._escape_table_cell(vote.get("date", ""))
            option = self._escape_table_cell(vote.get("option", ""))
            url = vote.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {option} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class SavedItemsFormatter(BaseFormatter):
    """Format saved items section."""

    @property
    def section_key(self) -> str:
        return "saved_items"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Saved Items", ""]
        lines.append("| Saved At | Link |")
        lines.append("|----------|------|")

        for item in data:
            saved_at = self._escape_table_cell(item.get("saved_at", ""))
            url = item.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {saved_at} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class EventsFormatter(BaseFormatter):
    """Format events section."""

    @property
    def section_key(self) -> str:
        return "events"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Uploaded Media", ""]
        lines.append("| Date | Description | Link |")
        lines.append("|------|-------------|------|")

        for m in data:
            date = self._escape_table_cell(m.get("date", ""))
            desc = self._escape_table_cell(m.get("description", ""))
            url = m.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {desc} | {link} |")

        lines.append("")
        return "\n".join(lines)


@register_formatter
class MessagesFormatter(BaseFormatter):
    """Format messages section."""

    @property
    def section_key(self) -> str:
        return "messages"

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Messages", ""]

        for msg in data:
            date = msg.get("date", "")
            from_name = msg.get("from_name", "")
            to_name = msg.get("to_name", "")
            subject = msg.get("subject", "") or ""
            content = msg.get("content", "") or ""

            lines.append(f"## {date}")
            lines.append(f"**From:** {from_name} → **To:** {to_name}")
            if subject:
                lines.append(f"**Subject:** {subject}")
            if content:
                lines.append("")
                truncated = content[:500] + "..." if len(content) > 500 else content
                lines.append(f"> {truncated}")
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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Scripts", ""]

        for script in data:
            name = script.get("name", "")
            date = script.get("date", "")
            content = script.get("content", "") or ""

            lines.append(f"## {name}")
            if date:
                lines.append(f"**Date:** {date}")
            if content:
                lines.append("")
                lines.append(content)
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

    def format(self, data: list, lang: str) -> str:
        if not data:
            return ""

        lines = ["# Published Articles", ""]

        for article in data:
            title = article.get("title", "")
            date = article.get("date", "")
            author = article.get("author", "")
            summary = article.get("summary", "")

            lines.append(f"## {title}")
            if date:
                lines.append(f"**Date:** {date}")
            if author:
                lines.append(f"**Author:** {author}")
            if summary:
                lines.append("")
                lines.append(summary)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
