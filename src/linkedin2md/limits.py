"""Resource limits shared by extraction and output components."""

from dataclasses import dataclass
from math import isfinite

MIB = 1024 * 1024
DEFAULT_MAX_ARCHIVE_FILE_SIZE_BYTES = 500 * MIB
DEFAULT_MAX_UNCOMPRESSED_BYTES = 500 * MIB
DEFAULT_MAX_ENTRY_BYTES = 100 * MIB
DEFAULT_MAX_FIELD_BYTES = 1 * MIB
DEFAULT_MAX_OUTPUT_BYTES = 50 * MIB
DEFAULT_MAX_ROWS_PER_CSV = 100_000
DEFAULT_MAX_ARCHIVE_ENTRIES = 10_000
DEFAULT_MAX_COMPRESSION_RATIO = 1_000


class ExtractionLimitError(ValueError):
    """Raised when an input exceeds a configured resource limit."""


class UnsafeArchiveError(ValueError):
    """Raised when an archive member violates path or type safety rules."""


class OutputLimitError(ValueError):
    """Raised when generated output exceeds a configured resource limit."""


@dataclass(frozen=True)
class ExtractionLimits:
    """Define bounded resource usage for archive extraction."""

    max_rows_per_csv: int = DEFAULT_MAX_ROWS_PER_CSV
    max_archive_entries: int = DEFAULT_MAX_ARCHIVE_ENTRIES
    max_uncompressed_bytes: int = DEFAULT_MAX_UNCOMPRESSED_BYTES
    max_entry_bytes: int = DEFAULT_MAX_ENTRY_BYTES
    max_field_bytes: int = DEFAULT_MAX_FIELD_BYTES
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO

    def validate(self) -> None:
        """Validate that every configured limit is positive."""
        values = {
            "max_rows_per_csv": self.max_rows_per_csv,
            "max_archive_entries": self.max_archive_entries,
            "max_uncompressed_bytes": self.max_uncompressed_bytes,
            "max_entry_bytes": self.max_entry_bytes,
            "max_field_bytes": self.max_field_bytes,
            "max_output_bytes": self.max_output_bytes,
        }
        for name, value in values.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ExtractionLimitError(f"{name} must be a positive integer")
        if (
            isinstance(self.max_compression_ratio, bool)
            or not isinstance(self.max_compression_ratio, (int, float))
            or not isfinite(self.max_compression_ratio)
            or self.max_compression_ratio <= 0
        ):
            raise ExtractionLimitError(
                "max_compression_ratio must be a finite positive number"
            )


DEFAULT_EXTRACTION_LIMITS = ExtractionLimits()
