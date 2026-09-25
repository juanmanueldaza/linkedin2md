"""Data extraction implementations.

Single Responsibility: Extract raw data from sources.
"""

import csv
import io
import stat
import zipfile
from dataclasses import replace
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from linkedin2md.limits import (
    DEFAULT_MAX_ROWS_PER_CSV,
    ExtractionLimitError,
    ExtractionLimits,
    UnsafeArchiveError,
)
from linkedin2md.protocols import DataExtractor


class ZipDataExtractor(DataExtractor):
    """Extract CSV data from a bounded LinkedIn ZIP export."""

    def __init__(
        self,
        zip_path: Path | str,
        max_rows: int | None = None,
        *,
        limits: ExtractionLimits | None = None,
    ):
        if limits is None:
            limits = ExtractionLimits(
                max_rows_per_csv=(
                    DEFAULT_MAX_ROWS_PER_CSV if max_rows is None else max_rows
                )
            )
        elif max_rows is not None:
            limits = replace(limits, max_rows_per_csv=max_rows)

        limits.validate()
        self.zip_path = Path(zip_path)
        self.limits = limits

    def extract(self) -> dict[str, list[dict]]:
        """Extract all CSVs from ZIP into raw dict format."""
        data: dict[str, list[dict]] = {}
        actual_uncompressed = 0

        try:
            with zipfile.ZipFile(self.zip_path, "r") as archive:
                members = self._validate_members(archive.infolist())
                declared_total = sum(info.file_size for info, _ in members)
                if declared_total > self.limits.max_uncompressed_bytes:
                    raise ExtractionLimitError(
                        "ZIP uncompressed data is too large "
                        f"({declared_total} bytes, max "
                        f"{self.limits.max_uncompressed_bytes})"
                    )

                seen_csv_keys: set[str] = set()
                for info, normalized_name in members:
                    key = self._csv_key(normalized_name)
                    if key is None:
                        continue
                    if key in seen_csv_keys:
                        raise UnsafeArchiveError(f"Duplicate normalized CSV key: {key}")
                    seen_csv_keys.add(key)

                    content, bytes_read = self._read_member(
                        archive,
                        info,
                        normalized_name,
                        actual_uncompressed,
                    )
                    actual_uncompressed += bytes_read
                    data[key] = self._parse_csv(content, normalized_name)
        except zipfile.BadZipFile as err:
            raise ValueError(f"Invalid or corrupted ZIP file: {self.zip_path}") from err

        return data

    def _validate_members(
        self, members: list[zipfile.ZipInfo]
    ) -> list[tuple[zipfile.ZipInfo, str]]:
        if len(members) > self.limits.max_archive_entries:
            raise ExtractionLimitError(
                f"ZIP has too many entries ({len(members)}, max "
                f"{self.limits.max_archive_entries})"
            )

        validated: list[tuple[zipfile.ZipInfo, str]] = []
        seen_names: set[str] = set()

        for info in members:
            normalized_name = self._validate_member(info)
            if normalized_name in seen_names:
                raise UnsafeArchiveError(f"Duplicate ZIP member: {info.filename}")
            seen_names.add(normalized_name)
            self._validate_metadata(info)
            validated.append((info, normalized_name))

        return validated

    def _validate_member(self, info: zipfile.ZipInfo) -> str:
        raw_name = info.filename
        if not raw_name or "\x00" in raw_name:
            raise UnsafeArchiveError("ZIP member has an invalid name")

        normalized_name = raw_name.replace("\\", "/")
        windows_path = PureWindowsPath(raw_name)
        posix_path = PurePosixPath(normalized_name)
        if (
            normalized_name.startswith("/")
            or windows_path.drive
            or windows_path.is_absolute()
            or ".." in posix_path.parts
        ):
            raise UnsafeArchiveError(f"Unsafe ZIP member path: {raw_name}")

        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise UnsafeArchiveError(f"ZIP symlink members are not allowed: {raw_name}")

        return str(posix_path).rstrip("/") or "."

    def _validate_metadata(self, info: zipfile.ZipInfo) -> None:
        if info.flag_bits & 0x1:
            raise UnsafeArchiveError(
                f"Encrypted ZIP members are not supported: {info.filename}"
            )

        if info.file_size > self.limits.max_entry_bytes:
            raise ExtractionLimitError(
                f"ZIP entry is too large: {info.filename} "
                f"({info.file_size} bytes, max {self.limits.max_entry_bytes})"
            )

        if info.file_size == 0:
            return
        if info.compress_size <= 0:
            raise ExtractionLimitError(
                f"ZIP entry has invalid compression metadata: {info.filename}"
            )

        ratio = info.file_size / info.compress_size
        if ratio > self.limits.max_compression_ratio:
            raise ExtractionLimitError(
                f"ZIP entry compression ratio is too high: {info.filename} "
                f"({ratio:.1f}, max {self.limits.max_compression_ratio})"
            )

    def _read_member(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        name: str,
        actual_uncompressed: int,
    ) -> tuple[str, int]:
        chunks: list[bytes] = []
        bytes_read = 0

        with archive.open(info, "r") as member:
            while True:
                chunk = member.read(1024 * 1024)
                if not chunk:
                    break
                bytes_read += len(chunk)
                if bytes_read > self.limits.max_entry_bytes:
                    raise ExtractionLimitError(
                        f"ZIP entry is too large while reading: {name} "
                        f"(max {self.limits.max_entry_bytes} bytes)"
                    )
                if (
                    actual_uncompressed + bytes_read
                    > self.limits.max_uncompressed_bytes
                ):
                    raise ExtractionLimitError(
                        "ZIP uncompressed data is too large while reading "
                        f"(max {self.limits.max_uncompressed_bytes} bytes)"
                    )
                chunks.append(chunk)

        try:
            content = b"".join(chunks).decode("utf-8-sig")
        except UnicodeDecodeError as err:
            raise ValueError(f"CSV is not valid UTF-8: {name}") from err

        return content, bytes_read

    def _parse_csv(self, content: str, name: str) -> list[dict]:
        try:
            content = self._skip_header_notes(content).replace("\x00", "")
            reader = csv.DictReader(io.StringIO(content))
            if reader.fieldnames:
                for field in reader.fieldnames:
                    self._validate_field(field, name)

            rows: list[dict] = []
            for row_number, row in enumerate(reader, start=1):
                if row_number > self.limits.max_rows_per_csv:
                    raise ExtractionLimitError(
                        f"CSV has too many rows: {name} "
                        f"(max {self.limits.max_rows_per_csv})"
                    )
                for _field, value in row.items():
                    self._validate_field(value, name)
                rows.append(row)
            return rows
        except csv.Error as err:
            raise ValueError(f"Invalid CSV data in {name}: {err}") from err

    def _validate_field(self, value: Any, name: str) -> None:
        if isinstance(value, list):
            field_value = "\x00".join(str(item) for item in value)
        elif value is None:
            field_value = ""
        else:
            field_value = str(value)

        if len(field_value.encode("utf-8")) > self.limits.max_field_bytes:
            raise ExtractionLimitError(
                f"CSV field is too large: {name} "
                f"(max {self.limits.max_field_bytes} bytes)"
            )

    def _csv_key(self, name: str) -> str | None:
        if not name.lower().endswith(".csv"):
            return None
        return PurePosixPath(name).stem.lower().replace(" ", "_")

    def _skip_header_notes(self, content: str) -> str:
        """Skip header notes in LinkedIn CSVs."""
        lines = content.split("\n")

        if lines and lines[0].strip().startswith("Notes"):
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    continue
                if "," in stripped and not stripped.startswith('"'):
                    return "\n".join(lines[i:])

        return content


class DictDataExtractor(DataExtractor):
    """Extract data from a pre-loaded dict (for testing)."""

    def __init__(self, data: dict[str, list[dict]]):
        self._data = data

    def extract(self) -> dict[str, list[dict]]:
        """Return the pre-loaded data."""
        return self._data
