"""Abstract protocols (interfaces) for SOLID compliance.

Defines contracts that implementations must follow:
- Dependency Inversion Principle: depend on abstractions
- Interface Segregation Principle: focused, minimal interfaces
- Liskov Substitution Principle: subtypes are substitutable
"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

# ============================================================================
# Core Data Types
# ============================================================================


class MultilingualText:
    """Immutable multilingual text container.

    Supports any number of languages via keyword arguments.
    Backward compatible with BilingualText API (en/es properties).
    """

    __slots__ = ("_texts",)

    def __init__(self, **langs: str):
        """Create with language codes as kwargs.

        Examples:
            MultilingualText(en="Hello", es="Hola")
            MultilingualText(en="Hi", es="Hola", fr="Salut")
        """
        object.__setattr__(self, "_texts", dict(langs))

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("MultilingualText is immutable")

    @property
    def en(self) -> str:
        """Backward compatibility: get English text."""
        return self._texts.get("en", "")

    @property
    def es(self) -> str:
        """Backward compatibility: get Spanish text."""
        return self._texts.get("es", "")

    def get(
        self,
        lang: str,
        fallback_chain: list[str] | None = None,
        default: str = "",
    ) -> str:
        """Get text in specified language with fallback chain.

        Args:
            lang: Primary language code to retrieve
            fallback_chain: Languages to try if primary not found
                (default: ["en", "es"])
            default: Value if no language found

        Returns:
            Text in requested or fallback language, or default
        """
        if lang in self._texts and self._texts[lang]:
            return self._texts[lang]

        for fb in fallback_chain or ["en", "es"]:
            if fb in self._texts and self._texts[fb]:
                return self._texts[fb]

        return default

    @property
    def languages(self) -> list[str]:
        """Return list of language codes with content."""
        return [lang for lang, text in self._texts.items() if text]

    def __repr__(self) -> str:
        return f"MultilingualText({self._texts!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MultilingualText):
            return self._texts == other._texts
        return False

    def __hash__(self) -> int:
        return hash(tuple(sorted(self._texts.items())))


# Backward compatibility alias
BilingualText = MultilingualText


# ============================================================================
# Language Detection Protocol
# ============================================================================


@runtime_checkable
class LanguageDetector(Protocol):
    """Protocol for language detection."""

    @abstractmethod
    def detect(self, text: str) -> str:
        """Detect language of text. Returns ISO 639-1 code (e.g., 'en', 'es')."""
        ...

    @property
    @abstractmethod
    def supported_languages(self) -> list[str]:
        """Return list of language codes this detector can identify."""
        ...


# ============================================================================
# Data Extraction Protocols
# ============================================================================


@runtime_checkable
class DataExtractor(Protocol):
    """Protocol for extracting raw data from a source."""

    @abstractmethod
    def extract(self) -> dict[str, list[dict]]:
        """Extract raw CSV data. Returns {filename: [rows]}."""
        ...


# ============================================================================
# Section Parser Protocol
# ============================================================================


@runtime_checkable
class SectionParser(Protocol):
    """Protocol for parsing a specific section of LinkedIn data.

    Each parser handles ONE section (Single Responsibility).
    """

    @property
    @abstractmethod
    def section_key(self) -> str:
        """The key this parser produces (e.g., 'experience', 'skills')."""
        ...

    @abstractmethod
    def parse(self, raw_data: dict[str, list[dict]]) -> Any:
        """Parse raw CSV data into structured section data."""
        ...


# ============================================================================
# Section Formatter Protocol
# ============================================================================


@runtime_checkable
class SectionFormatter(Protocol):
    """Protocol for formatting a specific section to Markdown.

    Each formatter handles ONE section (Single Responsibility).
    """

    @property
    @abstractmethod
    def section_key(self) -> str:
        """The section key this formatter handles."""
        ...

    @abstractmethod
    def format(self, data: Any, lang: str) -> str:
        """Format section data to Markdown string."""
        ...


# ============================================================================
# Registry Protocol
# ============================================================================


@runtime_checkable
class ParserRegistry(Protocol):
    """Protocol for parser registration (Open/Closed Principle)."""

    @abstractmethod
    def register(self, parser: SectionParser) -> None:
        """Register a section parser."""
        ...

    @abstractmethod
    def get_all(self) -> list[SectionParser]:
        """Get all registered parsers."""
        ...


@runtime_checkable
class FormatterRegistry(Protocol):
    """Protocol for formatter registration (Open/Closed Principle)."""

    @abstractmethod
    def register(self, formatter: SectionFormatter) -> None:
        """Register a section formatter."""
        ...

    @abstractmethod
    def get(self, section_key: str) -> SectionFormatter | None:
        """Get formatter for a section key."""
        ...

    @abstractmethod
    def get_all(self) -> list[SectionFormatter]:
        """Get all registered formatters."""
        ...


# ============================================================================
# Output Writer Protocol
# ============================================================================


@runtime_checkable
class OutputWriter(Protocol):
    """Protocol for writing formatted output."""

    @abstractmethod
    def write(self, filename: str, content: str) -> Path:
        """Write content to a file. Returns the path written."""
        ...


# ============================================================================
# Main Orchestrator Protocol
# ============================================================================


@runtime_checkable
class LinkedInConverter(Protocol):
    """Protocol for the main conversion orchestrator."""

    @abstractmethod
    def convert(self, source: Path, output_dir: Path, lang: str) -> list[Path]:
        """Convert LinkedIn export to Markdown files."""
        ...
