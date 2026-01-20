"""Learning section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class LearningParser(BaseParser):
    """Parse LinkedIn Learning courses."""

    @property
    def section_key(self) -> str:
        return "learning"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        learning = self._get_csv(raw_data, "learning")
        result = []

        for course in learning:
            title = course.get("Content Title", "")
            if not title:
                continue

            entry = {
                "title": title,
                "description": course.get("Content Description", "") or None,
                "content_type": course.get("Content Type", "") or None,
                "last_watched": course.get("Content Last Watched Date (if viewed)", "")
                or None,
                "completed_at": course.get("Content Completed At (if completed)", "")
                or None,
                "saved": course.get("Content Saved", "").lower() == "true",
            }
            result.append(entry)

        return result


@register_parser
class LearningReviewsParser(BaseParser):
    """Parse learning content reviews."""

    @property
    def section_key(self) -> str:
        return "learning_reviews"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        reviews = self._get_csv(raw_data, "reviews")
        result = []

        for r in reviews:
            reviewee = r.get("Reviewee", "")
            if not reviewee:
                continue

            entry = {
                "content": reviewee,
                "review_type": r.get("Review Type", "") or None,
                "section": r.get("Review Section", "") or None,
                "date": r.get("Creation Date", "") or None,
                "rating": r.get("Rating", "") or None,
                "text": r.get("Review Text", "") or None,
                "reviewer": r.get("Reviewer", "") or None,
                "tags": r.get("Review Tags", "") or None,
            }
            result.append(entry)

        return result
