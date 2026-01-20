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
            date = reaction.get("date", "")
            rtype = reaction.get("type", "") or ""
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
            date = repost.get("date", "")
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
            date = vote.get("date", "")
            option = vote.get("option", "") or ""
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
            saved_at = item.get("saved_at", "") or ""
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
            name = event.get("name", "")
            time = event.get("time", "") or ""
            status = event.get("status", "") or ""
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
            date = m.get("date", "") or ""
            desc = m.get("description", "") or ""
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
