"""Content section parsers (posts, comments, reactions, etc.).

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class PostsParser(BaseParser):
    """Parse posts/shares."""

    @property
    def section_key(self) -> str:
        return "posts"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        shares = self._get_csv(raw_data, "shares")
        result = []

        for s in shares:
            date = s.get("Date", "")
            if not date:
                continue

            content = s.get("ShareCommentary", "")
            content_lang = self._detect_language(content) if content else "en"

            entry = {
                "date": date,
                "url": s.get("ShareLink", "") or None,
                "content": self._create_bilingual(content, content_lang)
                if content
                else None,
                "shared_url": s.get("SharedUrl", "") or None,
                "media_url": s.get("MediaUrl", "") or None,
                "visibility": s.get("Visibility", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class CommentsParser(BaseParser):
    """Parse comments."""

    @property
    def section_key(self) -> str:
        return "comments"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        comments = self._get_csv(raw_data, "comments")
        result = []

        for c in comments:
            date = c.get("Date", "")
            if not date:
                continue

            message = c.get("Message", "")
            msg_lang = self._detect_language(message) if message else "en"

            entry = {
                "date": date,
                "url": c.get("Link", "") or None,
                "message": self._create_bilingual(message, msg_lang)
                if message
                else None,
            }
            result.append(entry)

        return result


@register_parser
class ReactionsParser(BaseParser):
    """Parse reactions (likes, etc.)."""

    @property
    def section_key(self) -> str:
        return "reactions"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        reactions = self._get_csv(raw_data, "reactions")
        result = []

        for r in reactions:
            date = r.get("Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "type": r.get("Type", "") or None,
                "url": r.get("Link", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class RepostsParser(BaseParser):
    """Parse instant reposts."""

    @property
    def section_key(self) -> str:
        return "reposts"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        reposts = self._get_csv(raw_data, "instantreposts")
        result = []

        for r in reposts:
            date = r.get("Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "url": r.get("Link", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class VotesParser(BaseParser):
    """Parse poll votes."""

    @property
    def section_key(self) -> str:
        return "votes"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        votes = self._get_csv(raw_data, "votes")
        result = []

        for v in votes:
            date = v.get("Date", "")
            if not date:
                continue

            entry = {
                "date": date,
                "url": v.get("Link", "") or None,
                "option": v.get("OptionText", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class SavedItemsParser(BaseParser):
    """Parse saved/bookmarked items."""

    @property
    def section_key(self) -> str:
        return "saved_items"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        items = self._get_csv(raw_data, "saved_items")
        result = []

        for item in items:
            url = item.get("savedItem", "")
            if not url:
                continue

            entry = {
                "url": url,
                "saved_at": item.get("CreatedTime", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class EventsParser(BaseParser):
    """Parse events."""

    @property
    def section_key(self) -> str:
        return "events"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        events = self._get_csv(raw_data, "events")
        result = []

        for e in events:
            name = e.get("Event Name", "")
            if not name:
                continue

            entry = {
                "name": name,
                "time": e.get("Event Time", "") or None,
                "status": e.get("Status", "") or None,
                "url": e.get("External Url", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class MediaParser(BaseParser):
    """Parse uploaded media."""

    @property
    def section_key(self) -> str:
        return "media"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        media = self._get_csv(raw_data, "rich_media")
        result = []

        for m in media:
            url = m.get("Media Link", "")
            if not url:
                continue

            entry = {
                "date": m.get("Date/Time", "") or None,
                "description": m.get("Media Description", "") or None,
                "url": url,
            }
            result.append(entry)

        return result


@register_parser
class MessagesParser(BaseParser):
    """Parse LinkedIn messages."""

    @property
    def section_key(self) -> str:
        return "messages"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        messages = self._get_csv(raw_data, "messages")
        result = []

        for m in messages:
            date = m.get("DATE", "")
            if not date:
                continue

            entry = {
                "conversation_id": m.get("CONVERSATION ID", ""),
                "conversation_title": m.get("CONVERSATION TITLE", "") or None,
                "from_name": m.get("FROM", ""),
                "from_url": m.get("SENDER PROFILE URL", "") or None,
                "to_name": m.get("TO", ""),
                "to_url": m.get("RECIPIENT PROFILE URLS", "") or None,
                "date": date,
                "subject": m.get("SUBJECT", "") or None,
                "content": m.get("CONTENT", "") or None,
                "folder": m.get("FOLDER", "") or None,
            }
            result.append(entry)

        return result
