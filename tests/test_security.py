"""Security-focused tests for linkedin2md."""

import tempfile
from pathlib import Path

import pytest

from linkedin2md.cli import MAX_FILE_SIZE_MB
from linkedin2md.extractor import ZipDataExtractor
from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.writer import MarkdownFileWriter

# =============================================================================
# Path Traversal Tests
# =============================================================================


class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention."""

    def test_reject_parent_directory_traversal(self):
        """Ensure '../' in filename is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("../etc/passwd", "malicious content")

    def test_reject_nested_parent_traversal(self):
        """Ensure nested '../' is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("foo/../../../etc/passwd", "malicious content")

    def test_reject_absolute_path_unix(self):
        """Ensure absolute Unix paths are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("/etc/passwd", "malicious content")

    def test_reject_absolute_path_windows(self):
        """Ensure absolute Windows paths are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))

            with pytest.raises(ValueError, match="Invalid filename"):
                writer.write("\\Windows\\System32\\config", "malicious content")

    def test_allow_valid_filename(self):
        """Ensure valid filenames still work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("profile", "# Test Profile")

            assert path.exists()
            assert path.name == "profile.md"

    def test_allow_filename_with_dots(self):
        """Ensure filenames with single dots are allowed (e.g., 'my.profile')."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("my.profile", "# Test")

            assert path.exists()
            assert path.name == "my.profile.md"


# =============================================================================
# ZIP File Validation Tests
# =============================================================================


class TestZipFileValidation:
    """Tests for ZIP file handling security."""

    def test_invalid_zip_raises_value_error(self):
        """Ensure corrupted ZIP files produce clear errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file that is not a valid ZIP
            fake_zip = Path(tmpdir) / "fake.zip"
            fake_zip.write_text("This is not a ZIP file")

            extractor = ZipDataExtractor(fake_zip)

            with pytest.raises(ValueError, match="Invalid or corrupted ZIP file"):
                extractor.extract()

    def test_empty_file_raises_value_error(self):
        """Ensure empty files produce clear errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_zip = Path(tmpdir) / "empty.zip"
            empty_zip.write_bytes(b"")

            extractor = ZipDataExtractor(empty_zip)

            with pytest.raises(ValueError, match="Invalid or corrupted ZIP file"):
                extractor.extract()

    def test_truncated_zip_raises_value_error(self):
        """Ensure truncated ZIP files produce clear errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            truncated_zip = Path(tmpdir) / "truncated.zip"
            # Write a partial ZIP header
            truncated_zip.write_bytes(b"PK\x03\x04")

            extractor = ZipDataExtractor(truncated_zip)

            with pytest.raises(ValueError, match="Invalid or corrupted ZIP file"):
                extractor.extract()


# =============================================================================
# File Size Limit Tests
# =============================================================================


class TestFileSizeLimit:
    """Tests for file size limits."""

    def test_max_file_size_constant_defined(self):
        """Ensure MAX_FILE_SIZE_MB is defined and reasonable."""
        assert MAX_FILE_SIZE_MB > 0
        assert MAX_FILE_SIZE_MB <= 1000  # Should be at most 1GB


# =============================================================================
# URL Sanitization Tests
# =============================================================================


class ConcreteFormatter(BaseFormatter):
    """Concrete implementation for testing base class methods."""

    @property
    def section_key(self) -> str:
        return "test"

    def format(self, data: object, lang: str) -> str:
        return ""


class TestUrlSanitization:
    """Tests for URL sanitization in formatters."""

    def setup_method(self):
        """Set up test formatter."""
        self.formatter = ConcreteFormatter()

    def test_allow_https_url(self):
        """Ensure HTTPS URLs are allowed."""
        url = "https://www.linkedin.com/profile"
        result = self.formatter._sanitize_url(url)
        assert result == url

    def test_allow_http_url(self):
        """Ensure HTTP URLs are allowed."""
        url = "http://example.com/page"
        result = self.formatter._sanitize_url(url)
        assert result == url

    def test_allow_mailto_url(self):
        """Ensure mailto URLs are allowed."""
        url = "mailto:user@example.com"
        result = self.formatter._sanitize_url(url)
        assert result == url

    def test_reject_javascript_url(self):
        """Ensure javascript: URLs are rejected."""
        url = "javascript:alert('XSS')"
        result = self.formatter._sanitize_url(url)
        assert result == ""

    def test_reject_data_url(self):
        """Ensure data: URLs are rejected."""
        url = "data:text/html,<script>alert('XSS')</script>"
        result = self.formatter._sanitize_url(url)
        assert result == ""

    def test_reject_file_url(self):
        """Ensure file: URLs are rejected."""
        url = "file:///etc/passwd"
        result = self.formatter._sanitize_url(url)
        assert result == ""

    def test_reject_vbscript_url(self):
        """Ensure vbscript: URLs are rejected."""
        url = "vbscript:msgbox('XSS')"
        result = self.formatter._sanitize_url(url)
        assert result == ""

    def test_escape_parentheses(self):
        """Ensure closing parentheses are escaped for Markdown safety."""
        url = "https://example.com/page(1)"
        result = self.formatter._sanitize_url(url)
        # Only closing parenthesis is escaped to prevent breaking Markdown link syntax
        assert result == "https://example.com/page(1%29"

    def test_escape_brackets(self):
        """Ensure square brackets are escaped for Markdown safety."""
        url = "https://example.com/page[1]"
        result = self.formatter._sanitize_url(url)
        assert result == "https://example.com/page%5B1%5D"

    def test_empty_url_returns_empty(self):
        """Ensure empty URL returns empty string."""
        assert self.formatter._sanitize_url("") == ""
        assert self.formatter._sanitize_url(None) == ""

    def test_strip_whitespace(self):
        """Ensure leading/trailing whitespace is stripped."""
        url = "  https://example.com  "
        result = self.formatter._sanitize_url(url)
        assert result == "https://example.com"


# =============================================================================
# Markdown Table Cell Escaping Tests (issue #40)
# =============================================================================


class TestTableCellEscaping:
    """Tests for Markdown table cell escaping to prevent table injection.

    See: https://github.com/juanmanueldaza/linkedin2md/issues/40
    """

    def setup_method(self) -> None:
        from linkedin2md.formatters.activity import SearchQueriesFormatter

        # ``SearchQueriesFormatter`` is a concrete subclass that uses the
        # shared escaping helpers; we use it as a stand-in to exercise the
        # ``BaseFormatter`` API without standing up an abstract instance.
        self.formatter = SearchQueriesFormatter()

    def test_escape_pipe_character(self) -> None:
        """Pipe characters in cell values must be escaped to ``\\|``."""
        assert self.formatter._escape_table_cell("CEO | Founder") == "CEO \\| Founder"
        assert self.formatter._escape_table_cell("a|b|c") == "a\\|b\\|c"
        assert self.formatter._escape_table_cell("|leading") == "\\|leading"
        assert self.formatter._escape_table_cell("trailing|") == "trailing\\|"

    def test_collapse_newlines(self) -> None:
        """Newlines in cell values must be collapsed to single spaces."""
        assert self.formatter._escape_table_cell("multi\nline") == "multi line"
        assert self.formatter._escape_table_cell("line\r\nbreak") == "line break"
        assert self.formatter._escape_table_cell("cr\ronly") == "cr only"

    def test_collapse_newlines_with_surrounding_whitespace(self) -> None:
        """Newlines collapse to single spaces; adjacent spaces are preserved."""
        result = self.formatter._escape_table_cell("first  \n  second")
        assert "\n" not in result
        assert "\r" not in result
        # Newline is replaced by a single space; surrounding whitespace
        # is preserved so a CSV cell that already had a space keeps it.
        assert "first   " in result
        assert "  second" in result

    def test_none_returns_empty(self) -> None:
        """None values render as empty cells (no 'None' literal)."""
        assert self.formatter._escape_table_cell(None) == ""

    def test_non_string_values_are_coerced(self) -> None:
        """Non-string values are stringified before escaping."""
        assert self.formatter._escape_table_cell(42) == "42"
        assert self.formatter._escape_table_cell(3.14) == "3.14"
        assert self.formatter._escape_table_cell(True) == "True"

    def test_empty_string_returns_empty(self) -> None:
        """Empty strings stay empty."""
        assert self.formatter._escape_table_cell("") == ""

    def test_pipe_and_newline_combined(self) -> None:
        """Both pipes and newlines are sanitised together."""
        result = self.formatter._escape_table_cell("CEO | Founder\nCTO | Builder")
        assert result == "CEO \\| Founder CTO \\| Builder"
        # The rendered cell must not contain raw newlines or raw pipes.
        assert "|" not in result.replace("\\|", "")
        assert "\n" not in result

    def test_escape_pipe_alias(self) -> None:
        """Backward compatibility: ``_escape_pipe`` aliases the new helper."""
        assert self.formatter._escape_pipe("a|b") == "a\\|b"
        assert self.formatter._escape_pipe("multi\nline") == "multi line"
        assert self.formatter._escape_pipe(None) == ""


class TestTableFormattersEscapeCells:
    """End-to-end: every table-emitting formatter must escape cell values.

    Guards against regressions of issue #40 across all section formatters.
    """

    def _assert_safe(self, output: str) -> None:
        r"""Assert the table output is well-formed and safe.

        Every row must have the same number of raw pipe boundaries
        (``column_count - 1``). Escaped pipes (``\|``) do not count.
        """
        lines = output.split("\n")
        expected_columns: int | None = None
        for line in lines:
            if not line.startswith("|") or not line.endswith("|"):
                continue
            if all(c in "-:|" for c in line):
                continue
            escaped = line.count(r"\|")
            raw = line.count("|") - escaped
            cols = raw + 1
            if expected_columns is None:
                expected_columns = cols
            elif cols != expected_columns:
                raise AssertionError(
                    f"Inconsistent column count in row: {line!r} "
                    f"(expected {expected_columns}, got {cols})"
                )

    def test_logins_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.activity import LoginsFormatter

        data = [{"date": "2026-06-15", "ip_address": "1.1.1.1", "login_type": "web|api"}]
        out = LoginsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "web\\|api" in out

    def test_inferences_formatter_escapes_pipe_and_newline(self) -> None:
        from linkedin2md.formatters.advertising import InferencesFormatter

        data = [
            {
                "category": "Career",
                "type": "Senior",
                "description": "CEO | Founder\nMulti",
                "inference": "ready",
            }
        ]
        out = InferencesFormatter().format(data, "en")
        self._assert_safe(out)
        assert "CEO \\| Founder Multi" in out

    def test_job_applications_formatter_escapes_newline(self) -> None:
        from linkedin2md.formatters.jobs import JobApplicationsFormatter

        data = [
            {
                "date": "2026-06-15",
                "company": "Acme\nInc",
                "title": "Engineer | Manager",
                "resume_used": "r.pdf",
            }
        ]
        out = JobApplicationsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "Acme Inc" in out
        assert "Engineer \\| Manager" in out

    def test_connections_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.network import ConnectionsFormatter

        data = [
            {
                "name": "Alice | Bob",
                "company": "Acme",
                "position": "Engineer",
                "connected_on": "2026-06-15",
            }
        ]
        out = ConnectionsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "Alice \\| Bob" in out

    def test_receipts_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.payments import ReceiptsFormatter

        data = [
            {
                "date": "2026-06-15",
                "description": "Subscription | Premium",
                "amount": "9.99",
                "currency": "USD",
            }
        ]
        out = ReceiptsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "Subscription \\| Premium" in out

    def test_endorsements_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.recommendations import EndorsementsFormatter

        data = [{"skill": "Python | Go", "endorser": "Alice", "date": "2026-06-15"}]
        out = EndorsementsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "Python \\| Go" in out

    def test_service_engagements_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.services import ServiceEngagementsFormatter

        data = [
            {
                "date": "2026-06-15",
                "marketplace_type": "Consulting | Advisory",
                "amount": "100",
                "currency": "USD",
            }
        ]
        out = ServiceEngagementsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "Consulting \\| Advisory" in out

    def test_security_challenges_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.activity import SecurityChallengesFormatter

        data = [
            {
                "date": "2026-06-15",
                "ip_address": "1.1.1.1",
                "country": "US | CA",
                "challenge_type": "Captcha",
            }
        ]
        out = SecurityChallengesFormatter().format(data, "en")
        self._assert_safe(out)
        assert "US \\| CA" in out

    def test_reactions_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.content import ReactionsFormatter

        data = [
            {"date": "2026-06-15", "type": "LIKE | PRAISE", "url": "https://example.com"}
        ]
        out = ReactionsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "LIKE \\| PRAISE" in out

    def test_learning_reviews_formatter_escapes_pipe(self) -> None:
        from linkedin2md.formatters.learning import LearningReviewsFormatter

        data = [
            {"content": "Great | Amazing", "rating": "5", "date": "2026-06-15"}
        ]
        out = LearningReviewsFormatter().format(data, "en")
        self._assert_safe(out)
        assert "Great \\| Amazing" in out
