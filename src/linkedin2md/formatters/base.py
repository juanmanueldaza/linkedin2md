"""Base formatter with shared utilities.

Provides common formatting functionality that section formatters can use.
"""

from abc import ABC, abstractmethod
from typing import Any

from linkedin2md.protocols import MultilingualText, SectionFormatter

# Backward compatibility alias
BilingualText = MultilingualText


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

    def _get_text(
        self,
        multilingual: MultilingualText | dict | str | None,
        lang: str,
        fallback_chain: list[str] | None = None,
    ) -> str:
        """Extract text in preferred language with fallback chain.

        Args:
            multilingual: Text container (MultilingualText, dict, str, or None)
            lang: Preferred language code
            fallback_chain: Languages to try if preferred not found
                (default: ["en", "es"])

        Returns:
            Text in requested or fallback language
        """
        if multilingual is None:
            return ""
        if isinstance(multilingual, str):
            return multilingual
        if isinstance(multilingual, MultilingualText):
            return multilingual.get(lang, fallback_chain=fallback_chain or ["en", "es"])
        # Dict fallback for compatibility
        if lang in multilingual and multilingual[lang]:
            return multilingual[lang]
        for fb in fallback_chain or ["en", "es"]:
            if fb in multilingual and multilingual[fb]:
                return multilingual[fb]
        return ""

    def _escape_pipe(self, text: str | None) -> str:
        """Escape pipe characters for Markdown tables.

        Backward compatibility alias for :meth:`_escape_table_cell`.
        """
        return self._escape_table_cell(text)

    def _escape_table_cell(self, text: str | None) -> str:
        """Escape a value for safe insertion into a Markdown table cell.

        Replaces pipe characters with the escaped form (``\\|``) and collapses
        any embedded newlines to a single space so a single CSV value cannot
        break the row/column structure of the rendered Markdown table.

        Args:
            text: The raw cell value. ``None`` is treated as an empty cell.

        Returns:
            A string safe to embed between Markdown table pipes.
        """
        if text is None:
            return ""
        # Collapse newlines (and the whitespace around them) so a multi-line
        # CSV cell cannot break the row layout.
        cleaned = str(text).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        # Escape pipe characters — the only character with structural meaning
        # inside a Markdown table row.
        return cleaned.replace("|", "\\|")

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
