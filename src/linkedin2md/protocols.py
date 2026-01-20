"""Abstract protocols (interfaces) for SOLID compliance.

Defines contracts that implementations must follow:
- Dependency Inversion Principle: depend on abstractions
- Interface Segregation Principle: focused, minimal interfaces
- Liskov Substitution Principle: subtypes are substitutable
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable

# ============================================================================
# Core Data Types
# ============================================================================


class BilingualText:
    """Immutable bilingual text container."""

    __slots__ = ("en", "es")

    def __init__(self, en: str = "", es: str = ""):
        object.__setattr__(self, "en", en)
        object.__setattr__(self, "es", es)

    def __setattr__(self, name, value):
        raise AttributeError("BilingualText is immutable")

    def get(self, lang: str, default: str = "") -> str:
        """Get text in specified language with fallback."""
        if lang == "en":
            return self.en or self.es or default
        return self.es or self.en or default

    def __repr__(self) -> str:
        return f"BilingualText(en={self.en!r}, es={self.es!r})"


# ============================================================================
# Language Detection Protocol
# ============================================================================


@runtime_checkable
class LanguageDetector(Protocol):
    """Protocol for language detection."""

    @abstractmethod
    def detect(self, text: str) -> str:
        """Detect language of text. Returns 'en' or 'es'."""
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
    def parse(self, raw_data: dict[str, list[dict]]) -> object:
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
    def format(self, data: object, lang: str) -> str:
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
