"""Conversion diagnostics and private report persistence."""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any

from linkedin2md.limits import (
    ExtractionLimitError,
    OutputLimitError,
    UnsafeArchiveError,
)

SCHEMA_VERSION = 1
MAX_ERROR_TEXT_LENGTH = 500

__all__ = [
    "ConversionReport",
    "ConversionResult",
    "DiagnosticEvent",
    "StrictConversionError",
    "write_report",
]

_STAGES = frozenset({"extract", "parse", "format", "write"})
_STATUSES = frozenset({"ok", "skipped", "failed"})
_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:[\\/][^\s]*|\\\\[^\s]*|/(?:[^\s/]+/)*[^\s/]+)")
_ENV_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}=[^\s,;]+")
_EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(?:password|passwd|token|secret|api[_-]?key|authorization|cookie)"
    r"\s*[:=]\s*(?:[^\s,;]+|\"[^\"]*\"|'[^']*')"
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")


def _stringify(value: object) -> str:
    try:
        return str(value)
    except Exception:
        return ""


def _sanitize_error_text(value: object, limit: int = MAX_ERROR_TEXT_LENGTH) -> str:
    text = "".join(char for char in _stringify(value) if char.isprintable())
    text = _PATH_PATTERN.sub("[redacted]", text)
    text = _ENV_PATTERN.sub("[redacted]", text)
    text = _SENSITIVE_ASSIGNMENT_PATTERN.sub("[redacted]", text)
    text = _BEARER_PATTERN.sub("Bearer [redacted]", text)
    text = _EMAIL_PATTERN.sub("[redacted]", text)
    text = text.split("Traceback (most recent call last)", 1)[0]
    text = " ".join(text.split())
    return text[: max(0, limit)]


def _sanitize_token(value: object, limit: int = 128) -> str:
    return _sanitize_error_text(value, limit)


def _error_details(error: BaseException) -> tuple[str, str]:
    error_type = _sanitize_token(type(error).__name__)
    if isinstance(error, OutputLimitError):
        message = "output limit exceeded"
    elif isinstance(error, ExtractionLimitError):
        message = "extraction limit exceeded"
    elif isinstance(error, UnsafeArchiveError):
        message = "unsafe archive rejected"
    else:
        message = "operation failed"
    return error_type, message


def _format_error(error: BaseException) -> str:
    error_type, message = _error_details(error)
    if not message:
        return error_type
    return f"{error_type}: {message}"[:MAX_ERROR_TEXT_LENGTH]


def _output_name(value: object) -> str:
    text = _stringify(value)
    if not text:
        return ""
    name = PureWindowsPath(text).name
    if not name:
        name = Path(text).name
    return _sanitize_token(name, 256)


@dataclass(frozen=True, slots=True)
class DiagnosticEvent:
    """One bounded, non-sensitive conversion diagnostic event."""

    stage: str
    section: str
    status: str
    error_type: str | None = None
    message: str | None = None

    def __post_init__(self) -> None:
        if self.stage not in _STAGES:
            raise ValueError(f"Unknown diagnostic stage: {self.stage}")
        if self.status not in _STATUSES:
            raise ValueError(f"Unknown diagnostic status: {self.status}")
        object.__setattr__(self, "section", _sanitize_token(self.section))
        if self.error_type is not None:
            object.__setattr__(self, "error_type", _sanitize_token(self.error_type))
        if self.message is not None:
            object.__setattr__(self, "message", _sanitize_error_text(self.message))

    def to_dict(self) -> dict[str, str | None]:
        return {
            "stage": self.stage,
            "section": self.section,
            "status": self.status,
            "error_type": self.error_type,
            "message": self.message,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )


@dataclass(frozen=True, slots=True)
class ConversionReport:
    """Immutable machine-readable result of one conversion run."""

    language: str
    diagnostics: tuple[DiagnosticEvent, ...] = ()
    unconsumed_keys: tuple[str, ...] = ()
    output_files: tuple[str, ...] = ()
    fatal_error: str | None = None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if isinstance(self.schema_version, bool) or not isinstance(
            self.schema_version, int
        ):
            raise TypeError("schema_version must be an integer")
        object.__setattr__(self, "language", _sanitize_token(self.language, 32))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        object.__setattr__(
            self,
            "unconsumed_keys",
            tuple(
                sorted({_sanitize_error_text(key, 256) for key in self.unconsumed_keys})
            ),
        )
        normalized_output_files: list[str] = []
        for path in self.output_files:
            name = _output_name(path)
            if name:
                normalized_output_files.append(name)
        object.__setattr__(
            self,
            "output_files",
            tuple(sorted(normalized_output_files)),
        )
        fatal_error = self.fatal_error
        if isinstance(fatal_error, BaseException):
            fatal_error = _format_error(fatal_error)
        elif isinstance(fatal_error, DiagnosticEvent):
            fatal_error = _format_diagnostic_error(fatal_error)
        elif fatal_error is not None:
            fatal_error = _sanitize_error_text(fatal_error)
        object.__setattr__(self, "fatal_error", fatal_error)

    @property
    def has_failures(self) -> bool:
        return (
            bool(self.unconsumed_keys)
            or any(event.status == "failed" for event in self.diagnostics)
            or self.fatal_error is not None
        )

    def to_dict(self) -> dict[str, Any]:
        fatal_error: Any = self.fatal_error
        if isinstance(fatal_error, DiagnosticEvent):
            fatal_error = fatal_error.to_dict()
        return {
            "schema_version": self.schema_version,
            "language": self.language,
            "diagnostics": [event.to_dict() for event in self.diagnostics],
            "unconsumed_keys": list(self.unconsumed_keys),
            "output_files": list(self.output_files),
            "fatal_error": fatal_error,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )


def _format_diagnostic_error(event: DiagnosticEvent) -> str:
    if event.error_type and event.message:
        return f"{event.error_type}: {event.message}"
    return event.error_type or event.message or "Conversion failed"


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Files produced by a conversion and its immutable report."""

    files: tuple[Path, ...]
    report: ConversionReport

    def __post_init__(self) -> None:
        object.__setattr__(self, "files", tuple(self.files))
        if not isinstance(self.report, ConversionReport):
            raise TypeError("report must be a ConversionReport")


class StrictConversionError(RuntimeError):
    """Raised when a strict conversion report contains a failure."""

    report: ConversionReport
    files: tuple[Path, ...]

    def __init__(
        self,
        report: ConversionReport,
        files: Iterable[Path] = (),
    ) -> None:
        if not isinstance(report, ConversionReport):
            raise TypeError("report must be a ConversionReport")
        object.__setattr__(self, "report", report)
        object.__setattr__(self, "files", tuple(files))
        RuntimeError.__init__(self, "Strict conversion failed")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("StrictConversionError is immutable")


class _DiagnosticAccumulator:
    def __init__(self, language: str) -> None:
        self.language = language
        self._diagnostics: list[DiagnosticEvent] = []
        self._unconsumed_keys: set[str] = set()
        self._output_files: list[str] = []
        self._files: list[Path] = []
        self.fatal_error: str | None = None

    @property
    def diagnostics(self) -> tuple[DiagnosticEvent, ...]:
        return tuple(self._diagnostics)

    @property
    def events(self) -> tuple[DiagnosticEvent, ...]:
        return self.diagnostics

    @property
    def unconsumed_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._unconsumed_keys))

    @property
    def output_files(self) -> tuple[str, ...]:
        return tuple(sorted(self._output_files))

    def record(
        self,
        stage: str,
        section: str,
        status: str,
        error_type: str | None = None,
        message: str | None = None,
    ) -> DiagnosticEvent:
        if isinstance(error_type, BaseException):
            derived_type, derived_message = _error_details(error_type)
            error_type = derived_type
            if message is None:
                message = derived_message
        event = DiagnosticEvent(
            stage=stage,
            section=section,
            status=status,
            error_type=error_type,
            message=message,
        )
        self._diagnostics.append(event)
        return event

    def add_event(self, event: DiagnosticEvent) -> DiagnosticEvent:
        if not isinstance(event, DiagnosticEvent):
            raise TypeError("event must be a DiagnosticEvent")
        self._diagnostics.append(event)
        return event

    def record_event(self, *args: Any, **kwargs: Any) -> DiagnosticEvent:
        if len(args) == 1 and not kwargs and isinstance(args[0], DiagnosticEvent):
            return self.add_event(args[0])
        return self.record(*args, **kwargs)

    def record_failure(
        self,
        stage: str,
        section: str,
        error: BaseException,
        *,
        fatal: bool = False,
    ) -> DiagnosticEvent:
        error_type, message = _error_details(error)
        event = self.record(
            stage,
            section,
            "failed",
            error_type=error_type,
            message=message,
        )
        if fatal:
            self.set_fatal_error(error)
        return event

    def set_unconsumed_keys(self, keys: Iterable[str]) -> None:
        self._unconsumed_keys = {str(key) for key in keys}

    def set_unconsumed(self, keys: Iterable[str]) -> None:
        self.set_unconsumed_keys(keys)

    @property
    def files(self) -> tuple[Path, ...]:
        return tuple(self._files)

    def add_output(self, path: object) -> None:
        name = _output_name(path)
        if name:
            self._output_files.append(name)
            self._files.append(Path(str(path)))

    def add_output_file(self, path: object) -> None:
        self.add_output(path)

    def set_fatal_error(self, error: BaseException) -> None:
        self.fatal_error = _format_error(error)

    def build(self) -> ConversionReport:
        return ConversionReport(
            language=self.language,
            diagnostics=self.diagnostics,
            unconsumed_keys=self.unconsumed_keys,
            output_files=self.output_files,
            fatal_error=self.fatal_error,
        )

    def build_report(self) -> ConversionReport:
        return self.build()


def write_report(path: Any, report: Any) -> Path:
    """Write a deterministic report privately and atomically."""

    actual_path: Any
    actual_report: Any
    if isinstance(path, ConversionReport):
        actual_path = report
        actual_report = path
    else:
        actual_path = path
        actual_report = report
    if not isinstance(actual_report, ConversionReport):
        raise TypeError("report must be a ConversionReport")

    target = Path(actual_path)
    absolute_target = Path(os.path.abspath(os.fspath(target)))
    for candidate in (absolute_target, *absolute_target.parents):
        if candidate.is_symlink():
            raise ValueError("Report target must not be a symlink")

    parent = absolute_target.parent
    missing_parents: list[Path] = []
    parent_candidate = parent
    while not parent_candidate.exists():
        missing_parents.append(parent_candidate)
        parent_candidate = parent_candidate.parent
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    for directory in reversed(missing_parents):
        os.chmod(directory, 0o700)
    for candidate in (absolute_target, parent, *parent.parents):
        if candidate.is_symlink():
            raise ValueError("Report target must not be a symlink")

    temporary_path: Path | None = None
    file_descriptor: int | None = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=".linkedin2md-report-",
            suffix=".tmp",
            dir=parent,
        )
        temporary_path = Path(temporary_name)
        os.chmod(temporary_path, 0o600)
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="") as stream:
            file_descriptor = None
            stream.write(actual_report.to_json())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, absolute_target)
        temporary_path = None
        os.chmod(absolute_target, 0o600)
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass

    return target


def write_conversion_report(path: Any, report: Any) -> Path:
    return write_report(path, report)


def _write_report(path: Any, report: Any) -> Path:
    return write_report(path, report)
