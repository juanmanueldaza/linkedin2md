"""Base formatter with shared utilities.

Provides common formatting functionality that section formatters can use.
"""

from abc import ABC, abstractmethod
from typing import Any

from linkedin2md.protocols import BilingualText, SectionFormatter


class BaseFormatter(ABC, SectionFormatter):
    """Base class for section formatters.

    Provides shared utilities for Markdown formatting.
    Subclasses implement format() for their specific section.
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

    # ========================================================================
    # Shared Utilities
    # ========================================================================

    def _get_text(self, bilingual: BilingualText | dict | str | None, lang: str) -> str:
        """Extract text in preferred language with fallback."""
        if bilingual is None:
            return ""
        if isinstance(bilingual, str):
            return bilingual
        if isinstance(bilingual, BilingualText):
            return bilingual.get(lang)
        # Dict fallback for compatibility
        return bilingual.get(lang) or bilingual.get("en") or bilingual.get("es") or ""

    def _escape_pipe(self, text: str) -> str:
        """Escape pipe characters for Markdown tables."""
        return text.replace("|", "\\|")

    def _sanitize_url(self, url: str | None) -> str:
        """Sanitize URL for safe Markdown link rendering.

        Only allows http, https, and mailto schemes.
        Escapes characters that could break Markdown link syntax.

        Args:
            url: The URL to sanitize.

        Returns:
            Sanitized URL safe for Markdown, or empty string if invalid.
        """
        if not url:
            return ""

        url = url.strip()

        # Only allow safe URL schemes
        allowed_schemes = ("http://", "https://", "mailto:")
        if not url.startswith(allowed_schemes):
            return ""

        # Escape characters that could break Markdown link syntax
        return url.replace(")", "%29").replace("[", "%5B").replace("]", "%5D")
