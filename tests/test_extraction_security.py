"""Tests for extraction limits and secure output handling."""

import stat
import zipfile
from pathlib import Path

import pytest

from linkedin2md.converter import create_converter
from linkedin2md.extractor import ZipDataExtractor
from linkedin2md.limits import (
    ExtractionLimitError,
    ExtractionLimits,
    OutputLimitError,
    UnsafeArchiveError,
)
from linkedin2md.writer import MarkdownFileWriter


def _zip_with(
    path: Path,
    entries: dict[str, str],
    compression: int = zipfile.ZIP_STORED,
) -> Path:
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return path


def test_utf8_bom_and_nested_csv_are_supported(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "bom.zip",
        {
            "nested/Profile.CSV": "\ufeffFirst Name,Last Name\nAda,Lovelace\n",
        },
    )

    data = ZipDataExtractor(zip_path).extract()

    assert data["profile"][0]["First Name"] == "Ada"


def test_max_rows_positional_argument_remains_supported(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "rows.zip",
        {"Skills.csv": "Name\nPython\nRust\n"},
    )

    with pytest.raises(ExtractionLimitError, match="too many rows"):
        ZipDataExtractor(zip_path, 1).extract()


def test_archive_entry_limit_is_enforced(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "entries.zip",
        {
            "Profile.csv": "First Name\nAda\n",
            "Skills.csv": "Name\nPython\n",
        },
    )
    limits = ExtractionLimits(max_archive_entries=1)

    with pytest.raises(ExtractionLimitError, match="too many entries"):
        ZipDataExtractor(zip_path, limits=limits).extract()


def test_uncompressed_size_limit_is_enforced(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "large.zip",
        {"Profile.csv": "First Name\nAda Lovelace\n"},
    )
    limits = ExtractionLimits(max_uncompressed_bytes=5, max_entry_bytes=100)

    with pytest.raises(ExtractionLimitError, match="uncompressed data is too large"):
        ZipDataExtractor(zip_path, limits=limits).extract()


def test_entry_size_limit_is_enforced(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "entry.zip",
        {"Profile.csv": "First Name\nAda Lovelace\n"},
    )
    limits = ExtractionLimits(max_entry_bytes=5)

    with pytest.raises(ExtractionLimitError, match="entry is too large"):
        ZipDataExtractor(zip_path, limits=limits).extract()


def test_field_size_limit_is_enforced(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "field.zip",
        {"Profile.csv": "First Name\nAda Lovelace\n"},
    )
    limits = ExtractionLimits(max_field_bytes=5)

    with pytest.raises(ExtractionLimitError, match="field is too large"):
        ZipDataExtractor(zip_path, limits=limits).extract()


def test_compression_ratio_limit_is_enforced(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "compressed.zip",
        {"Profile.csv": "First Name\n" + ("A" * 10_000) + "\n"},
        compression=zipfile.ZIP_DEFLATED,
    )
    limits = ExtractionLimits(max_compression_ratio=2)

    with pytest.raises(ExtractionLimitError, match="compression ratio is too high"):
        ZipDataExtractor(zip_path, limits=limits).extract()


def test_path_traversal_member_is_rejected(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "traversal.zip",
        {"../Profile.csv": "First Name\nAda\n"},
    )

    with pytest.raises(UnsafeArchiveError, match="Unsafe ZIP member path"):
        ZipDataExtractor(zip_path).extract()


def test_duplicate_normalized_csv_key_is_rejected(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "duplicate.zip",
        {
            "Profile.csv": "First Name\nAda\n",
            "nested/Profile.csv": "First Name\nGrace\n",
        },
    )

    with pytest.raises(UnsafeArchiveError, match="Duplicate normalized CSV key"):
        ZipDataExtractor(zip_path).extract()


def test_symlink_member_is_rejected(tmp_path: Path) -> None:
    zip_path = tmp_path / "symlink.zip"
    info = zipfile.ZipInfo("Profile.csv")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(info, "target.csv")

    with pytest.raises(UnsafeArchiveError, match="symlink"):
        ZipDataExtractor(zip_path).extract()


def test_invalid_utf8_csv_is_rejected(tmp_path: Path) -> None:
    zip_path = tmp_path / "encoding.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("Profile.csv", b"\xff\xfe")

    with pytest.raises(ValueError, match="not valid UTF-8"):
        ZipDataExtractor(zip_path).extract()


def test_writer_uses_private_permissions_and_atomic_output(tmp_path: Path) -> None:
    output_dir = tmp_path / "private-output"
    writer = MarkdownFileWriter(output_dir)

    path = writer.write("profile", "# Profile")

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(output_dir.stat().st_mode) == 0o700
    assert not list(output_dir.glob(".*"))


def test_writer_rejects_oversized_output(tmp_path: Path) -> None:
    writer = MarkdownFileWriter(tmp_path / "output", max_output_bytes=3)

    with pytest.raises(OutputLimitError, match="too large"):
        writer.write("profile", "four")


def test_writer_rejects_symlink_output_directory(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)

    with pytest.raises(ValueError, match="must not be a symlink"):
        MarkdownFileWriter(link)


def test_factory_propagates_shared_output_limit(tmp_path: Path) -> None:
    zip_path = _zip_with(
        tmp_path / "factory.zip",
        {"Profile.csv": "First Name,Last Name\nAda,Lovelace\n"},
    )
    converter = create_converter(
        zip_path,
        tmp_path / "output",
        limits=ExtractionLimits(max_output_bytes=3),
    )

    with pytest.raises(OutputLimitError, match="too large"):
        converter.convert()


def test_limits_reject_invalid_values() -> None:
    with pytest.raises(ExtractionLimitError, match="positive integer"):
        ExtractionLimits(max_rows_per_csv=0).validate()

    with pytest.raises(ExtractionLimitError, match="finite positive"):
        ExtractionLimits(max_compression_ratio=float("nan")).validate()
