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
