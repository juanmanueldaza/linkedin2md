"""Base parser with shared utilities.

Provides common parsing functionality that section parsers can use.
Dependency Inversion: Depends on LanguageDetector protocol.
"""

from abc import ABC, abstractmethod

from linkedin2md.language import (
    MultilingualTextFactory,
    get_default_detector,
    get_default_factory,
)
from linkedin2md.protocols import LanguageDetector, MultilingualText, SectionParser

# Backward compatibility alias
BilingualText = MultilingualText
BilingualTextFactory = MultilingualTextFactory

# Month names for date formatting
MONTHS = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


class BaseParser(ABC, SectionParser):
    """Base class for section parsers.

    Provides shared utilities for parsing LinkedIn data.
    Subclasses implement parse() for their specific section.
    """

    def __init__(
        self,
        detector: LanguageDetector | None = None,
        bilingual_factory: BilingualTextFactory | None = None,
    ):
        """Initialize with optional dependency injection."""
        self._detector = detector or get_default_detector()
        self._bilingual = bilingual_factory or get_default_factory()

    @property
    @abstractmethod
    def section_key(self) -> str:
        """The key this parser produces."""
        ...

    @abstractmethod
    def parse(self, raw_data: dict[str, list[dict]]) -> object:
        """Parse raw CSV data into structured section data."""
        ...

    # ========================================================================
    # Shared Utilities
    # ========================================================================

    def _get_csv(self, raw_data: dict[str, list[dict]], key: str) -> list[dict]:
        """Get CSV data by key."""
        return raw_data.get(key, [])

    def _merge_csv_sources(
        self, raw_data: dict[str, list[dict]], keys: list[str]
    ) -> list[dict]:
        """Merge rows from multiple CSV sources (for split files)."""
        result = []
        for key in keys:
            result.extend(raw_data.get(key, []))
        return result

    def _build_name(self, first: str, last: str) -> str:
        """Build full name from first and last name."""
        return f"{first} {last}".strip()

    def _create_bilingual(self, text: str, lang: str | None = None) -> BilingualText:
        """Create bilingual text."""
        return self._bilingual.create(text, lang)

    def _detect_language(self, text: str) -> str:
        """Detect language of text."""
        return self._detector.detect(text)

    def _format_date(self, date_str: str) -> str:
        """Format date string 'YYYY-MM-DD' to 'Jan 2024'."""
        if not date_str:
            return ""

        if " " in date_str and len(date_str.split()) == 2:
            return date_str

        parts = date_str.split("-")
        if len(parts) >= 2:
            try:
                month_idx = int(parts[1])
                return f"{MONTHS[month_idx]} {parts[0]}"
            except (ValueError, IndexError):
                return parts[0]

        return date_str

    def _parse_datetime(self, date_str: str) -> str | None:
        """Parse datetime format like '08/19/24, 11:04 PM'."""
        if not date_str:
            return None

        try:
            date_part = date_str.split(",")[0]
            parts = date_part.split("/")
            if len(parts) == 3:
                month, day, year = parts
                year = f"20{year}" if int(year) < 50 else f"19{year}"
                return f"{MONTHS[int(month)]} {year}"
        except (ValueError, IndexError):
            pass

        return date_str.split(",")[0] if date_str else None

    def _parse_utc_date(self, date_str: str) -> str | None:
        """Parse UTC date format like '2022/01/16 02:51:39 UTC'."""
        if not date_str:
            return None

        try:
            date_part = date_str.split(" ")[0]
            parts = date_part.split("/")
            if len(parts) == 3:
                year, month, day = parts
                return f"{MONTHS[int(month)]} {year}"
        except (ValueError, IndexError):
            pass

        return None


def merge_bilingual_entries(
    entries: list[dict],
    key_fields: list[str],
    bilingual_fields: list[str],
) -> list[dict]:
    """Merge duplicate entries with multilingual content.

    Groups entries by matching key fields and merges multilingual text from
    different language versions into complete MultilingualText objects.
    """
    if not entries:
        return []

    # Group entries by key fields
    groups: dict[tuple, list[dict]] = {}
    for entry in entries:
        key = tuple(entry.get(field) for field in key_fields)
        if key not in groups:
            groups[key] = []
        groups[key].append(entry)

    # Merge each group
    merged = []
    for group in groups.values():
        if len(group) == 1:
            merged.append(group[0])
        else:
            merged_entry = _merge_bilingual_group(group, bilingual_fields)
            merged.append(merged_entry)

    return merged


def _merge_bilingual_group(group: list[dict], bilingual_fields: list[str]) -> dict:
    """Merge a group of duplicate entries with different languages."""
    merged = group[0].copy()

    for field in bilingual_fields:
        if field == "achievements":
            merged[field] = _merge_achievements(group)
        elif field in merged:
            merged[field] = _merge_bilingual_field(group, field)

    return merged


def _merge_bilingual_field(group: list[dict], field: str) -> MultilingualText:
    """Merge a multilingual field from multiple entries."""
    merged: dict[str, str] = {}

    for entry in group:
        value = entry.get(field)
        if not value:
            continue

        if isinstance(value, MultilingualText):
            for lang in value.languages:
                if lang not in merged:
                    merged[lang] = value.get(lang)

    return MultilingualText(**merged)


def _merge_achievements(group: list[dict]) -> list[dict]:
    """Merge achievements lists from multiple language versions."""
    achievement_lists = [entry.get("achievements", []) for entry in group]

    if not achievement_lists or not any(achievement_lists):
        return []

    max_len = max(len(lst) for lst in achievement_lists if lst)
    merged_achievements = []

    for i in range(max_len):
        merged_text: dict[str, str] = {}

        for achievements in achievement_lists:
            if i >= len(achievements):
                continue

            achievement = achievements[i]
            text = achievement.get("text")

            if isinstance(text, MultilingualText):
                for lang in text.languages:
                    if lang not in merged_text:
                        merged_text[lang] = text.get(lang)

        merged_achievements.append({"text": MultilingualText(**merged_text)})

    return merged_achievements
