"""linkedin2md - Convert LinkedIn data exports to Markdown.

SOLID-compliant architecture:
- S: Each parser/formatter handles one section
- O: New sections added via registry decorators
- L: All parsers/formatters are substitutable via protocols
- I: Focused protocols for each concern
- D: Converter depends on abstractions, not concretions
"""

import logging
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("linkedin2md")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Development fallback

# Configure package logger (NullHandler = library best practice)
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Main public API
from linkedin2md.converter import (  # noqa: E402
    LinkedInToMarkdownConverter,
    create_converter,
)

# Backward compatibility - import old API
# (These are deprecated but kept for compatibility)
from linkedin2md.formatter import MarkdownFormatter  # noqa: E402
from linkedin2md.parser import LinkedInExportParser  # noqa: E402

# Protocols for type hints and custom implementations
from linkedin2md.protocols import (  # noqa: E402
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
from linkedin2md.registry import (  # noqa: E402
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
