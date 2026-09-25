"""Main converter orchestrator with dependency injection.

Implements the Dependency Inversion Principle:
- Depends on abstractions (protocols), not concretions
- All dependencies are injected, not created internally
"""

import logging
from pathlib import Path
from typing import Any

from linkedin2md.diagnostics import (
    ConversionResult,
    StrictConversionError,
    _DiagnosticAccumulator,
)
from linkedin2md.limits import (
    DEFAULT_EXTRACTION_LIMITS,
    ExtractionLimits,
    OutputLimitError,
)
from linkedin2md.protocols import (
    DataExtractor,
    FormatterRegistry,
    OutputWriter,
    ParserRegistry,
)

logger = logging.getLogger(__name__)

# CSV keys that LinkedIn exports but are known to be always empty
# (or contain no useful data). Suppress warnings for these.
_KNOWN_EMPTY_KEYS: frozenset[str] = frozenset(
    {
        "guide_messages",
        "learning_coach_messages",
        "learning_role_play_messages",
        "learningcoachmessages",
    }
)


class _TrackingDict(dict):
    """Dict subclass that records which keys are accessed via get().

    Used to detect CSV files in the export that no parser consumed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.accessed_keys: set[str] = set()

    def __getitem__(self, key: str) -> Any:
        self.accessed_keys.add(key)
        return super().__getitem__(key)

    def __contains__(self, key: object) -> bool:
        self.accessed_keys.add(str(key))
        return super().__contains__(key)

    def __iter__(self):
        for key in super().__iter__():
            self.accessed_keys.add(key)
            yield key

    def keys(self):
        self.accessed_keys.update(dict.keys(self))
        return super().keys()

    def items(self):
        self.accessed_keys.update(dict.keys(self))
        return super().items()

    def values(self):
        self.accessed_keys.update(dict.keys(self))
        return super().values()

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        self.accessed_keys.add(key)
        return super().get(key, default)


class LinkedInToMarkdownConverter:
    """Main orchestrator for LinkedIn to Markdown conversion.

    SOLID Principles:
    - Single Responsibility: Only orchestrates the conversion process
    - Open/Closed: New parsers/formatters added via registries
    - Dependency Inversion: Depends on protocols, not implementations

    All dependencies are injected via constructor.
    """

    def __init__(
        self,
        extractor: DataExtractor,
        parser_registry: ParserRegistry,
        formatter_registry: FormatterRegistry,
        writer: OutputWriter,
    ):
        """Initialize with injected dependencies.

        Args:
            extractor: Extracts raw data from source
            parser_registry: Registry of section parsers
            formatter_registry: Registry of section formatters
            writer: Writes formatted output
        """
        self._extractor = extractor
        self._parsers = parser_registry
        self._formatters = formatter_registry
        self._writer = writer

    def convert(self, lang: str = "en") -> list[Path]:
        """Convert LinkedIn export to Markdown files."""
        result = self._run_conversion(lang, report_mode=False)
        return list(result.files)

    def convert_with_report(
        self,
        lang: str = "en",
        *,
        strict: bool = False,
    ) -> ConversionResult:
        result = self._run_conversion(lang, report_mode=True)
        if strict and result.report.has_failures:
            raise StrictConversionError(result.report, result.files)
        return result

    def _run_conversion(
        self,
        lang: str,
        *,
        report_mode: bool,
    ) -> ConversionResult:
        accumulator = _DiagnosticAccumulator(lang)

        try:
            raw_data = self._extractor.extract()
        except Exception as error:
            if report_mode:
                accumulator.record_failure(
                    "extract",
                    "extraction",
                    error,
                    fatal=True,
                )
                return ConversionResult(tuple(accumulator.files), accumulator.build())
            raise

        accumulator.record("extract", "extraction", "ok")

        try:
            tracked = _TrackingDict(raw_data)
            parsed_data = self._parse_all(
                tracked,
                accumulator if report_mode else None,
            )
            all_keys = set(raw_data.keys())
            unconsumed = all_keys - tracked.accessed_keys - _KNOWN_EMPTY_KEYS
            accumulator.set_unconsumed_keys(unconsumed)
            for key in sorted(unconsumed):
                logger.warning("No parser consumed CSV key: %s", key)
            files = self._format_and_write_all(
                parsed_data,
                lang,
                accumulator if report_mode else None,
                report_mode=report_mode,
            )
        except OutputLimitError as error:
            if report_mode:
                if accumulator.fatal_error is None:
                    accumulator.record_failure(
                        "write",
                        "conversion",
                        error,
                        fatal=True,
                    )
                return ConversionResult(tuple(accumulator.files), accumulator.build())
            raise
        except Exception as error:
            if report_mode:
                if accumulator.fatal_error is None:
                    accumulator.record_failure(
                        "parse",
                        "conversion",
                        error,
                        fatal=True,
                    )
                return ConversionResult(tuple(accumulator.files), accumulator.build())
            raise

        return ConversionResult(tuple(files), accumulator.build())

    def _parse_all(
        self,
        raw_data: dict[str, list[dict]],
        accumulator: _DiagnosticAccumulator | None = None,
    ) -> dict[str, object]:
        """Parse all sections using registered parsers."""
        parsed: dict[str, object] = {}

        try:
            parsers = self._parsers.get_all()
        except Exception as error:
            if accumulator is not None:
                accumulator.record_failure("parse", "registry", error, fatal=True)
            raise

        for parser in parsers:
            section = "unknown"
            try:
                result = parser.parse(raw_data)
                section = parser.section_key
                parsed[section] = result
                if accumulator is not None:
                    accumulator.record("parse", section, "ok")
            except OutputLimitError as error:
                if accumulator is not None:
                    try:
                        section = parser.section_key
                    except Exception:
                        pass
                    accumulator.record_failure("parse", section, error, fatal=True)
                raise
            except Exception as error:
                if accumulator is not None:
                    try:
                        section = parser.section_key
                    except Exception:
                        pass
                    accumulator.record_failure("parse", section, error)
                log_section = section
                if accumulator is None:
                    try:
                        log_section = parser.section_key
                    except Exception:
                        pass
                logger.warning("Failed to parse %s: %s", log_section, error)

        parsed["profile"] = {
            "name": parsed.get("name", ""),
            "title": parsed.get("title"),
            "location": parsed.get("location", ""),
            "email": parsed.get("email", ""),
            "phone": parsed.get("phone", ""),
            "summary": parsed.get("summary"),
            "profile_meta": parsed.get("profile_meta", {}),
        }

        return parsed

    def _format_and_write_all(
        self,
        data: dict[str, object],
        lang: str,
        accumulator: _DiagnosticAccumulator | None = None,
        *,
        report_mode: bool = False,
    ) -> list[Path]:
        """Format and write all sections."""
        files: list[Path] = []

        try:
            formatters = self._formatters.get_all()
        except Exception as error:
            if accumulator is not None:
                accumulator.record_failure("format", "registry", error, fatal=True)
            if report_mode:
                return files
            raise

        for formatter in formatters:
            if accumulator is None:
                section = formatter.section_key
            else:
                section = "unknown"
                try:
                    section = formatter.section_key
                except Exception as error:
                    accumulator.record_failure("format", section, error)
                    logger.warning("Failed to format %s: %s", section, error)
                    continue

            section_data = data.get(section)
            if not section_data:
                if accumulator is not None:
                    accumulator.record("format", section, "skipped")
                    accumulator.record("write", section, "skipped")
                continue

            try:
                content = formatter.format(section_data, lang)
                has_content = bool(content and content.strip())
            except OutputLimitError as error:
                if accumulator is not None:
                    accumulator.record_failure("format", section, error, fatal=True)
                if report_mode:
                    return files
                raise
            except Exception as error:
                if accumulator is not None:
                    accumulator.record_failure("format", section, error)
                    accumulator.record("write", section, "skipped")
                logger.warning("Failed to format %s: %s", section, error)
                continue

            if not has_content:
                if accumulator is not None:
                    accumulator.record("format", section, "skipped")
                    accumulator.record("write", section, "skipped")
                continue

            if accumulator is not None:
                accumulator.record("format", section, "ok")

            try:
                path = self._writer.write(section, content)
            except OutputLimitError as error:
                if accumulator is not None:
                    accumulator.record_failure("write", section, error, fatal=True)
                if report_mode:
                    return files
                raise
            except Exception as error:
                if accumulator is not None:
                    accumulator.record_failure("write", section, error)
                logger.warning("Failed to format %s: %s", section, error)
                continue

            files.append(path)
            if accumulator is not None:
                accumulator.record("write", section, "ok")
                accumulator.add_output(path)

        return files


def create_converter(
    source: Path,
    output_dir: Path,
    *,
    limits: ExtractionLimits | None = None,
) -> LinkedInToMarkdownConverter:
    """Factory function to create a converter with default dependencies.

    This provides a convenient way to create a fully configured converter
    while still allowing dependency injection for testing.
    """
    if limits is not None:
        limits.validate()

    # Import parsers and formatters to trigger decorator registration.
    # instantiate_all() must be called after to create instances.
    from linkedin2md import (  # noqa: F401
        formatters,
        parsers,
    )
    from linkedin2md.extractor import ZipDataExtractor
    from linkedin2md.registry import get_formatter_registry, get_parser_registry
    from linkedin2md.writer import MarkdownFileWriter

    parser_registry = get_parser_registry()
    formatter_registry = get_formatter_registry()
    output_limits = limits or DEFAULT_EXTRACTION_LIMITS

    # Instantiate all classes registered via decorators
    parser_registry.instantiate_all()
    formatter_registry.instantiate_all()

    return LinkedInToMarkdownConverter(
        extractor=ZipDataExtractor(source, limits=limits),
        parser_registry=parser_registry,
        formatter_registry=formatter_registry,
        writer=MarkdownFileWriter(
            output_dir,
            max_output_bytes=output_limits.max_output_bytes,
        ),
    )
