"""linkedin2md - Convert LinkedIn data exports to Markdown.

SOLID-compliant architecture:
- S: Each parser/formatter handles one section
- O: New sections added via registry decorators
- L: All parsers/formatters are substitutable via protocols
- I: Focused protocols for each concern
- D: Converter depends on abstractions, not concretions
"""

__version__ = "0.1.0"

# Main public API
from linkedin2md.converter import LinkedInToMarkdownConverter, create_converter

# Backward compatibility - import old API
# (These are deprecated but kept for compatibility)
from linkedin2md.formatter import MarkdownFormatter
from linkedin2md.parser import LinkedInExportParser

# Protocols for type hints and custom implementations
from linkedin2md.protocols import (
    BilingualText,
    DataExtractor,
    FormatterRegistry,
    LanguageDetector,
    OutputWriter,
    ParserRegistry,
    SectionFormatter,
    SectionParser,
)

# Registries for extension
from linkedin2md.registry import (
    get_formatter_registry,
    get_parser_registry,
    register_formatter,
    register_parser,
)

__all__ = [
    # Version
    "__version__",
    # Main API
    "LinkedInToMarkdownConverter",
    "create_converter",
    # Protocols
    "BilingualText",
    "DataExtractor",
    "FormatterRegistry",
    "LanguageDetector",
    "OutputWriter",
    "ParserRegistry",
    "SectionFormatter",
    "SectionParser",
    # Registry
    "get_formatter_registry",
    "get_parser_registry",
    "register_formatter",
    "register_parser",
    # Backward compatibility (deprecated)
    "LinkedInExportParser",
    "MarkdownFormatter",
]
