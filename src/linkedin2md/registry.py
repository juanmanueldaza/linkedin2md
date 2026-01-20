"""Registry implementations for Open/Closed Principle.

Allows adding new parsers and formatters without modifying existing code.
"""

from linkedin2md.protocols import (
    FormatterRegistry,
    ParserRegistry,
    SectionFormatter,
    SectionParser,
)


class DefaultParserRegistry(ParserRegistry):
    """Default implementation of parser registry."""

    def __init__(self):
        self._parsers: list[SectionParser] = []

    def register(self, parser: SectionParser) -> None:
        """Register a section parser."""
        self._parsers.append(parser)

    def get_all(self) -> list[SectionParser]:
        """Get all registered parsers."""
        return list(self._parsers)


class DefaultFormatterRegistry(FormatterRegistry):
    """Default implementation of formatter registry."""

    def __init__(self):
        self._formatters: dict[str, SectionFormatter] = {}

    def register(self, formatter: SectionFormatter) -> None:
        """Register a section formatter."""
        self._formatters[formatter.section_key] = formatter

    def get(self, section_key: str) -> SectionFormatter | None:
        """Get formatter for a section key."""
        return self._formatters.get(section_key)

    def get_all(self) -> list[SectionFormatter]:
        """Get all registered formatters."""
        return list(self._formatters.values())


# ============================================================================
# Decorator-based registration for convenience
# ============================================================================

# Global registries (can be replaced via dependency injection)
_parser_registry = DefaultParserRegistry()
_formatter_registry = DefaultFormatterRegistry()


def get_parser_registry() -> ParserRegistry:
    """Get the global parser registry."""
    return _parser_registry


def get_formatter_registry() -> FormatterRegistry:
    """Get the global formatter registry."""
    return _formatter_registry


def register_parser(cls):
    """Decorator to register a parser class."""
    _parser_registry.register(cls())
    return cls


def register_formatter(cls):
    """Decorator to register a formatter class."""
    _formatter_registry.register(cls())
    return cls
