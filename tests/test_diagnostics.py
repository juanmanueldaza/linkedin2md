"""Tests for conversion diagnostics and strict mode."""

import json
import os
import stat
import zipfile
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from linkedin2md import (
    ConversionReport,
    ConversionResult,
    DiagnosticEvent,
    StrictConversionError,
)
from linkedin2md.cli import _parse_args, main
from linkedin2md.converter import LinkedInToMarkdownConverter
from linkedin2md.diagnostics import write_report
from linkedin2md.extractor import DictDataExtractor
from linkedin2md.limits import OutputLimitError
from linkedin2md.registry import DefaultFormatterRegistry, DefaultParserRegistry
from linkedin2md.writer import InMemoryWriter


class FailingExtractor:
    def extract(self):
        raise ValueError(
            "extractor failed at /private/source.csv password=hunter2 "
            "Authorization: Bearer fake.token email@example.com"
        )


class HostileError(Exception):
    def __str__(self):
        raise RuntimeError("exception text is unavailable")


class HostileExtractor:
    def extract(self):
        raise HostileError()


class FailingParser:
    section_key = "broken"

    def parse(self, raw_data):
        raise ValueError("parser failed at /private/source.csv SECRET=value")


class WorkingParser:
    section_key = "profile"

    def parse(self, raw_data):
        raw_data.get("profile", [])
        return {"name": "Ada"}


class ItemParser:
    section_key = "profile"

    def parse(self, raw_data):
        return {"name": raw_data["profile"][0]["name"]}


class MembershipParser:
    section_key = "profile"

    def parse(self, raw_data):
        return {"name": "Ada" if "profile" in raw_data else "Unknown"}


class IteratingParser:
    section_key = "profile"

    def parse(self, raw_data):
        list(raw_data)
        return {"name": "Ada"}


class BrokenDataParser:
    section_key = "broken"

    def parse(self, raw_data):
        return {"value": "x"}


class FailingFormatter:
    section_key = "broken"

    def format(self, data, lang):
        raise ValueError("formatter failed at /private/source.csv SECRET=value")


class WorkingFormatter:
    section_key = "profile"

    def format(self, data, lang):
        return "# Profile\nAda"


class FailingWriter(InMemoryWriter):
    def write(self, filename, content):
        raise OSError("writer failed at /private/source.csv SECRET=value")


class OutputLimitWriter(InMemoryWriter):
    def write(self, filename, content):
        raise OutputLimitError("output exceeded max_output_bytes")


def make_converter(
    raw_data,
    parsers,
    formatters,
    writer=None,
    extractor=None,
):
    parser_registry = DefaultParserRegistry()
    formatter_registry = DefaultFormatterRegistry()
    for parser in parsers:
        parser_registry.register(parser)
    for formatter in formatters:
        formatter_registry.register(formatter)
    return LinkedInToMarkdownConverter(
        extractor=extractor or DictDataExtractor(raw_data),
        parser_registry=parser_registry,
        formatter_registry=formatter_registry,
        writer=writer or InMemoryWriter(),
    )


def event_for(report, stage, section, status):
    return any(
        event.stage == stage and event.section == section and event.status == status
        for event in report.diagnostics
    )


def test_diagnostic_model_is_immutable_and_privacy_safe():
    event = DiagnosticEvent(
        "parse",
        "profile",
        "failed",
        "ValueError",
        "failure /private/source.csv SECRET=value\x00",
    )
    report = ConversionReport(
        "en",
        (event,),
        ("unknown", "another"),
        ("/private/output/profile.md",),
        "ValueError: failure /private/source.csv SECRET=value",
    )

    payload = json.loads(report.to_json())

    assert payload["schema_version"] == 1
    assert payload["output_files"] == ["profile.md"]
    assert payload["unconsumed_keys"] == ["another", "unknown"]
    assert "/private/source.csv" not in json.dumps(payload)
    assert "SECRET=value" not in json.dumps(payload)
    assert "\x00" not in json.dumps(payload)
    assert report.has_failures
    with pytest.raises(FrozenInstanceError):
        attribute = "language"
        setattr(report, attribute, "es")


def test_write_report_is_private_atomic_and_deterministic(tmp_path):
    report = ConversionReport("en", output_files=("profile.md",))
    target = tmp_path / "nested" / "report.json"

    first = write_report(target, report)
    first_bytes = first.read_bytes()
    second = write_report(target, report)

    assert first == target
    assert second == target
    assert target.read_bytes() == first_bytes
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert stat.S_IMODE(target.parent.stat().st_mode) == 0o700
    assert not list(target.parent.glob(".linkedin2md-report-*"))


def test_write_report_rejects_symlink_target(tmp_path):
    target = tmp_path / "report.json"
    target.symlink_to(tmp_path / "outside.json")
    report = ConversionReport("en")

    with pytest.raises(ValueError, match="symlink"):
        write_report(target, report)


def test_converter_records_parser_failure_and_continues_by_default():
    converter = make_converter(
        {"profile": [{"name": "Ada"}], "unknown": [{"value": "x"}]},
        [FailingParser(), WorkingParser()],
        [WorkingFormatter()],
    )

    result = converter.convert_with_report()

    assert isinstance(result, ConversionResult)
    assert event_for(result.report, "parse", "broken", "failed")
    assert result.report.unconsumed_keys == ("unknown",)
    assert result.files
    assert result.report.has_failures


def test_converter_records_formatter_failure_and_continues():
    converter = make_converter(
        {"broken": [{"value": "x"}]},
        [BrokenDataParser(), WorkingParser()],
        [FailingFormatter(), WorkingFormatter()],
    )

    result = converter.convert_with_report()

    assert event_for(result.report, "format", "broken", "failed")
    assert event_for(result.report, "write", "broken", "skipped")
    assert result.report.has_failures


def test_converter_records_writer_failure_and_continues():
    converter = make_converter(
        {"profile": [{"name": "Ada"}]},
        [WorkingParser()],
        [WorkingFormatter()],
        writer=FailingWriter(),
    )

    result = converter.convert_with_report()

    assert event_for(result.report, "write", "profile", "failed")
    assert result.files == ()
    assert result.report.has_failures


def test_strict_mode_raises_after_partial_output():
    converter = make_converter(
        {"profile": [{"name": "Ada"}], "unknown": [{"value": "x"}]},
        [WorkingParser()],
        [WorkingFormatter()],
    )

    with pytest.raises(StrictConversionError) as error:
        converter.convert_with_report(strict=True)

    assert error.value.files
    assert error.value.report.unconsumed_keys == ("unknown",)
    assert error.value.report.has_failures


def test_output_limit_is_fatal_in_report_mode_and_legacy_mode():
    converter = make_converter(
        {"profile": [{"name": "Ada"}]},
        [WorkingParser()],
        [WorkingFormatter()],
        writer=OutputLimitWriter(),
    )

    result = converter.convert_with_report()
    assert result.report.fatal_error
    assert event_for(result.report, "write", "profile", "failed")
    assert result.files == ()

    with pytest.raises(OutputLimitError):
        converter.convert()


def test_item_access_is_tracked_for_strict_mode():
    converter = make_converter(
        {"profile": [{"name": "Ada"}]},
        [ItemParser()],
        [WorkingFormatter()],
    )

    result = converter.convert_with_report(strict=True)

    assert result.report.unconsumed_keys == ()
    assert not result.report.has_failures


def test_membership_and_iteration_are_tracked_for_strict_mode():
    for parser in (MembershipParser(), IteratingParser()):
        converter = make_converter(
            {"profile": [{"name": "Ada"}]},
            [parser],
            [WorkingFormatter()],
        )

        result = converter.convert_with_report(strict=True)

        assert result.report.unconsumed_keys == ()
        assert not result.report.has_failures


def test_extraction_failure_is_fatal_in_both_modes():
    converter = make_converter(
        {},
        [WorkingParser()],
        [WorkingFormatter()],
        extractor=FailingExtractor(),
    )

    result = converter.convert_with_report()
    assert result.report.fatal_error
    assert event_for(result.report, "extract", "extraction", "failed")
    assert result.files == ()

    with pytest.raises(ValueError, match="extractor failed"):
        converter.convert()


def test_hostile_exception_text_still_produces_a_report():
    converter = make_converter(
        {},
        [WorkingParser()],
        [WorkingFormatter()],
        extractor=HostileExtractor(),
    )

    result = converter.convert_with_report()

    assert result.report.fatal_error == "HostileError: operation failed"
    assert event_for(result.report, "extract", "extraction", "failed")


def test_parse_args_accepts_diagnostics_options():
    args = _parse_args(["export.zip", "--strict", "--report", "report.json"])

    assert args.strict is True
    assert args.report == Path("report.json")


def test_cli_writes_report_for_partial_success(tmp_path):
    source = tmp_path / "export.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("Profile.csv", "First Name,Last Name\nAda,Lovelace")
        archive.writestr("Unknown.csv", "value\nx")
    report_path = tmp_path / "report.json"

    from unittest.mock import patch

    with patch(
        "sys.argv",
        ["linkedin2md", str(source), "--report", str(report_path)],
    ):
        result = main()

    assert result == 0
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["unconsumed_keys"] == ["unknown"]
    assert payload["output_files"] == ["profile.md"]
    assert os.path.isfile(report_path)


def test_cli_strict_writes_report_and_skips_pdf(tmp_path, caplog):
    source = tmp_path / "export.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("Profile.csv", "First Name,Last Name\nAda,Lovelace")
        archive.writestr("Unknown.csv", "value\nx")
    report_path = tmp_path / "report.json"

    from unittest.mock import patch

    with patch(
        "sys.argv",
        [
            "linkedin2md",
            str(source),
            "--strict",
            "--report",
            str(report_path),
            "--pdf",
        ],
    ):
        with patch("linkedin2md.pdf.convert_md_to_pdf") as pdf:
            result = main()

    assert result == 1
    assert report_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["unconsumed_keys"] == [
        "unknown"
    ]
    pdf.assert_not_called()
    assert "Strict conversion failed" in caplog.text


def test_cli_rejects_report_path_aliasing_source(tmp_path, caplog):
    source = tmp_path / "export.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("Profile.csv", "First Name,Last Name\nAda,Lovelace")
    original = source.read_bytes()

    from unittest.mock import patch

    with patch("sys.argv", ["linkedin2md", str(source), "--report", str(source)]):
        result = main()

    assert result == 1
    assert source.read_bytes() == original
    assert "must not overwrite" in caplog.text


def test_cli_rejects_report_path_aliasing_pdf(tmp_path, caplog):
    source = tmp_path / "export.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("Profile.csv", "First Name,Last Name\nAda,Lovelace")
    output = tmp_path / "output"

    from unittest.mock import patch

    with patch(
        "sys.argv",
        [
            "linkedin2md",
            str(source),
            "--output",
            str(output),
            "--report",
            str(output / "profile.pdf"),
            "--pdf",
        ],
    ):
        result = main()

    assert result == 1
    assert not (output / "profile.pdf").exists()
    assert "must not overwrite" in caplog.text


def test_cli_report_write_failure_returns_one(tmp_path, caplog):
    source = tmp_path / "export.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("Profile.csv", "First Name,Last Name\nAda,Lovelace")

    from unittest.mock import patch

    with patch(
        "sys.argv",
        ["linkedin2md", str(source), "--report", str(tmp_path / "report.json")],
    ):
        with patch("linkedin2md.cli.write_report", side_effect=OSError("no report")):
            result = main()

    assert result == 1
    assert "Failed to write conversion report" in caplog.text
