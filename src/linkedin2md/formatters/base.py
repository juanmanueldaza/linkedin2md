"""Base formatter with shared utilities.

Provides common formatting functionality that section formatters can use.
"""

import ipaddress
import logging
import re
import unicodedata
from abc import ABC, abstractmethod
from collections.abc import Iterable
from email.errors import HeaderParseError
from email.headerregistry import Address
from typing import Any
from urllib.parse import unquote_to_bytes, urlsplit

from linkedin2md.protocols import MultilingualText, SectionFormatter

logger = logging.getLogger(__name__)

_PERCENT_ESCAPE = re.compile(r"%[0-9A-Fa-f]{2}")
_HOST_LABEL = re.compile(r"[A-Za-z0-9-]+")
_MARKDOWN_URL_DELIMITERS = {
    "\\": "%5C",
    "(": "%28",
    ")": "%29",
    "[": "%5B",
    "]": "%5D",
    "|": "%7C",
    "<": "%3C",
    ">": "%3E",
}


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

    def format(self, data: Any, lang: str) -> str:
        """Format section data to Markdown string.

        Provides the empty-data guard — subclasses override
        _format_content() instead.
        """
        if not data:
            return ""
        return self._format_content(data, lang)

    @abstractmethod
    def _format_content(self, data: Any, lang: str) -> str:
        """Format non-empty section data. Implemented by subclasses."""
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
        return ""

    def _escape_pipe(self, text: str | None) -> str:
        """Escape a value using the compatibility table-cell policy."""
        return self._escape_table_cell(text)

    @staticmethod
    def _normalize_line_separators(value: str) -> str:
        """Normalize physical line separators to LF."""
        return (
            value.replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\u2028", "\n")
            .replace("\u2029", "\n")
        )

    @staticmethod
    def _remove_text_controls(value: str) -> str:
        """Remove control and format characters from untrusted text."""
        cleaned: list[str] = []
        for character in value:
            if character in "\n\r\t\u2028\u2029":
                cleaned.append(character)
            elif character == "\x7f" or unicodedata.category(character).startswith("C"):
                continue
            else:
                cleaned.append(character)
        return "".join(cleaned)

    @staticmethod
    def _escape_line(value: object) -> str:
        """Escape one untrusted text line without changing line structure."""
        if value is None:
            return ""
        text = BaseFormatter._normalize_line_separators(str(value))
        text = BaseFormatter._remove_text_controls(text)
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace("\\", "\\\\")
        for delimiter in ("`", "*", "_", "[", "]", "~", "|"):
            text = text.replace(delimiter, f"\\{delimiter}")
        return text.replace("\n", " ")

    def _escape_inline(self, value: object) -> str:
        """Escape untrusted text for a Markdown inline context."""
        return self._escape_line(value).replace("\t", " ").replace("\n", " ")

    @staticmethod
    def _neutralize_block_line(line: str) -> str:
        """Prevent one escaped line from starting a Markdown block."""
        if not line:
            return line

        leading = line[: len(line) - len(line.lstrip(" \t"))]
        if len(leading.expandtabs(4)) >= 4:
            return f"\\{line}"

        if re.fullmatch(r" {0,3}(?:-[ \t]*){3,}", line):
            return f"\\{line}"
        if re.fullmatch(r" {0,3}(?:\+[ \t]*){3,}", line):
            return f"\\{line}"
        if re.fullmatch(r" {0,3}=+[ \t]*", line):
            return f"\\{line}"

        match = re.match(r"^( {0,3})(#{1,6})(?=[ \t]|$)", line)
        if match:
            return f"{match.group(1)}\\{match.group(2)}{line[match.end() :]}"
        match = re.match(r"^( {0,3})>", line)
        if match:
            return f"{match.group(1)}\\>{line[match.end() :]}"
        match = re.match(r"^( {0,3})([-+])(?=[ \t])", line)
        if match:
            return f"{match.group(1)}\\{match.group(2)}{line[match.end() :]}"
        match = re.match(r"^( {0,3})(\d{1,9})([.)])(?=[ \t])", line)
        if match:
            return (
                f"{match.group(1)}\\{match.group(2)}\\{match.group(3)}"
                f"{line[match.end() :]}"
            )
        return line

    def _escape_block(self, value: object) -> str:
        """Escape text while preserving safe line breaks in a block."""
        if value is None:
            return ""
        text = self._normalize_line_separators(str(value))
        return "\n".join(
            self._neutralize_block_line(self._escape_line(line))
            for line in text.split("\n")
        )

    def _escape_heading(self, value: object) -> str:
        """Escape a value for a single-line heading context."""
        escaped = self._escape_inline(value).replace("\n", " ")
        return self._neutralize_block_line(escaped)

    def _escape_list_item(self, value: object) -> str:
        """Escape a value for a single-line list-item context."""
        escaped = self._escape_inline(value).replace("\n", " ")
        return self._neutralize_block_line(escaped)

    def _escape_joined(self, values: object) -> str:
        """Escape and join scalar values with a comma separator."""
        if values is None:
            members: Iterable[object] = ()
        elif isinstance(values, (str, bytes, bytearray)):
            members = (values,)
        elif isinstance(values, Iterable):
            members = values
        else:
            members = (values,)

        parts = [self._escape_inline(value).replace("\n", " ") for value in members]
        return ", ".join(part for part in parts if part)

    def _escape_link_label(self, value: object) -> str:
        """Escape a value for use inside a Markdown link label."""
        return self._escape_inline(value).replace("\n", " ")

    def _blockquote(self, value: object) -> str:
        """Render escaped text as a Markdown blockquote."""
        escaped = self._escape_block(value)
        if not escaped:
            return ""
        return "\n".join(f"> {line}" for line in escaped.split("\n"))

    def _escape_table_cell(self, text: object) -> str:
        """Escape a value for safe insertion into a Markdown table cell."""
        return self._escape_inline(text).replace("\n", " ")

    def _section_separator(self) -> str:
        """Return a standard section separator string.

        Returns:
            Newline-separated horizontal rule pattern.
        """
        return "\n---\n\n"

    def _truncate_text(
        self, text: str, max_len: int = 50000, field_name: str = "text"
    ) -> str:
        """Truncate text to max_len, logging a warning if truncated.

        Args:
            text: The text to potentially truncate.
            max_len: Maximum character length (default 50KB).
            field_name: Human-readable field name for log messages.

        Returns:
            Original text if under limit, otherwise truncated with warning.
        """
        if len(text) <= max_len:
            return text
        logger.warning(
            "Truncated %s from %d to %d chars in section '%s'",
            field_name,
            len(text),
            max_len,
            self.section_key,
        )
        return text[:max_len]

    @staticmethod
    def _contains_url_control(value: str) -> bool:
        """Return whether a URL contains a control or format character."""
        return any(
            unicodedata.category(character).startswith("C")
            or character in "\u2028\u2029"
            for character in value
        )

    @staticmethod
    def _percent_encoding_is_valid(value: str) -> bool:
        """Return whether every percent sign starts a complete escape."""
        index = 0
        while index < len(value):
            if value[index] != "%":
                index += 1
                continue
            if index + 2 >= len(value):
                return False
            if _PERCENT_ESCAPE.fullmatch(value[index : index + 3]) is None:
                return False
            index += 3
        return True

    @staticmethod
    def _percent_encoding_has_control(value: str) -> bool:
        """Return whether percent-decoding exposes a control character."""
        try:
            decoded = unquote_to_bytes(value).decode("utf-8")
        except UnicodeError:
            return True
        return any(
            BaseFormatter._contains_url_control(character) for character in decoded
        )

    @staticmethod
    def _valid_hostname(hostname: str) -> bool:
        """Validate an IPv4, IPv6, IDNA, or DNS hostname."""
        if not hostname:
            return False
        if hostname.isdigit() or re.fullmatch(r"0x[0-9a-f]+", hostname, re.IGNORECASE):
            return False
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            if "." in hostname and re.fullmatch(r"[0-9.]+", hostname):
                return False
            try:
                ascii_hostname = hostname.encode("idna").decode("ascii")
            except UnicodeError:
                return False
            if len(ascii_hostname) > 253:
                return False
            labels = ascii_hostname.rstrip(".").split(".")
            if not labels or any(
                not label
                or len(label) > 63
                or _HOST_LABEL.fullmatch(label) is None
                or label.startswith("-")
                or label.endswith("-")
                for label in labels
            ):
                return False
        return True

    @staticmethod
    def _valid_http_authority(netloc: str, hostname: str | None) -> bool:
        """Validate an HTTP(S) authority without accepting ambiguity."""
        if not netloc or not hostname or "@" in netloc or "\\" in netloc:
            return False
        if any(BaseFormatter._contains_url_control(character) for character in netloc):
            return False

        if netloc.startswith("["):
            closing = netloc.find("]")
            if closing < 0:
                return False
            suffix = netloc[closing + 1 :]
            if suffix and re.fullmatch(r":[0-9]+", suffix) is None:
                return False
        else:
            if "[" in netloc or "]" in netloc:
                return False
            if ":" in netloc:
                if netloc.count(":") != 1:
                    return False
                host_part, port_part = netloc.rsplit(":", 1)
                if not host_part or re.fullmatch(r"[0-9]+", port_part) is None:
                    return False

        return BaseFormatter._valid_hostname(hostname)

    @staticmethod
    def _valid_mailto(parsed: Any) -> bool:
        """Validate one mailto addr-spec and its optional parameters."""
        if parsed.netloc or not parsed.path or "/" in parsed.path:
            return False
        try:
            address_value = unquote_to_bytes(parsed.path).decode("utf-8")
        except UnicodeError:
            return False
        if not address_value or any(
            character.isspace() or BaseFormatter._contains_url_control(character)
            for character in address_value
        ):
            return False
        if any(character in address_value for character in "/?#"):
            return False
        try:
            address = Address(addr_spec=address_value)
        except (HeaderParseError, IndexError, UnicodeError, ValueError):
            return False
        if not address.username or not address.domain:
            return False
        domain = address.domain
        if domain.startswith(".") or domain.endswith("."):
            return False
        if domain.startswith("[") and domain.endswith("]"):
            domain = domain[1:-1]
        return BaseFormatter._valid_hostname(domain)

    @staticmethod
    def _encode_markdown_url(value: str) -> str:
        """Encode characters that can terminate a Markdown destination."""
        for delimiter, encoded in _MARKDOWN_URL_DELIMITERS.items():
            value = value.replace(delimiter, encoded)
        return value

    def _validated_markdown_url(self, url: str | None) -> str:
        """Validate and encode a URL for a Markdown link destination."""
        if not isinstance(url, str):
            return ""
        candidate = url.strip(" \t")
        if not candidate:
            return ""
        if any(
            character.isspace() or self._contains_url_control(character)
            for character in candidate
        ):
            return ""
        if not self._percent_encoding_is_valid(candidate):
            return ""
        if self._percent_encoding_has_control(candidate):
            return ""

        try:
            parsed = urlsplit(candidate)
            scheme = parsed.scheme.lower()
            hostname = parsed.hostname
            port = parsed.port
        except (UnicodeError, ValueError):
            return ""

        if scheme not in {"http", "https", "mailto"}:
            return ""
        if scheme in {"http", "https"}:
            if not self._valid_http_authority(parsed.netloc, hostname):
                return ""
            if port is not None and not 1 <= port <= 65535:
                return ""
        elif not self._valid_mailto(parsed):
            return ""
        return self._encode_markdown_url(candidate)

    def _sanitize_url(self, url: str | None) -> str:
        """Delegate URL sanitization to the centralized URL policy."""
        return self._validated_markdown_url(url)

    def _render_plain_url(self, url: object) -> str:
        """Validate a URL rendered as plain text without link syntax."""
        if not isinstance(url, str):
            return ""
        destination = self._validated_markdown_url(url)
        return self._escape_table_cell(destination) if destination else ""

    def _render_link(self, label: object, url: str | None) -> str:
        """Render a complete Markdown link or an empty string when invalid."""
        destination = self._validated_markdown_url(url)
        if not destination:
            return ""
        safe_label = self._escape_link_label(label)
        if not safe_label.strip():
            return ""
        return f"[{safe_label}]({destination})"

    def _render_table_link(self, label: object, url: str | None) -> str:
        """Render a complete Markdown link for a table cell."""
        return self._render_link(label, url)


class SimpleListFormatter(BaseFormatter):
    """Base for formatters that render SimpleListParser output as markdown tables.

    Subclasses define section_key, title, and headers (list of display
    column names matching the parser output field names).
    """

    @property
    @abstractmethod
    def title(self) -> str:
        """Markdown heading for the section."""
        ...

    @property
    @abstractmethod
    def headers(self) -> list[str]:
        """Display column names for the markdown table."""
        ...

    @property
    @abstractmethod
    def fields(self) -> list[str]:
        """Field names matching parser output dict keys."""
        ...

    url_fields: frozenset[str] = frozenset()

    def _format_content(self, data: Any, lang: str) -> str:
        """Render data as a markdown table."""
        lines = [f"# {self.title}", ""]
        lines.append("| " + " | ".join(self.headers) + " |")
        lines.append("|" + "|".join(["------"] * len(self.headers)) + "|")

        for row in data:
            cells = [
                self._render_plain_url(row.get(field, ""))
                if field in self.url_fields
                else self._escape_table_cell(row.get(field, ""))
                for field in self.fields
            ]
            lines.append(f"| {' | '.join(cells)} |")

        lines.append("")
        return "\n".join(lines)
