"""Tests for PDF exporter module (src/linkedin2md/pdf.py)."""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

from linkedin2md.pdf import convert_md_to_pdf


def _make_mock_markdown(return_html: str = "<p>test</p>"):
    """Create a mock markdown module with markdown() function."""
    mod = types.ModuleType("markdown")
    mod.markdown = MagicMock(return_value=return_html)  # type: ignore[attr-defined]
    return mod


def _make_mock_weasyprint():
    """Create a mock weasyprint module with HTML class that does nothing."""
    mod = types.ModuleType("weasyprint")
    mock_html = MagicMock()
    mock_html.return_value.write_pdf = MagicMock()
    mod.HTML = mock_html  # type: ignore[attr-defined]
    return mod


# =============================================================================
# Import Error Handling
# =============================================================================


class TestConvertMdToPdf:
    """Tests for convert_md_to_pdf()."""

    def test_missing_weasyprint_returns_false(self, caplog) -> None:
        """Test returns False when weasyprint is not installed."""
        mock_md = _make_mock_markdown()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": None}):
            result = convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert result is False

    def test_missing_weasyprint_logs_error(self, caplog) -> None:
        """Test logs error message when weasyprint is not installed."""
        mock_md = _make_mock_markdown()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": None}):
            convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert "weasyprint" in caplog.text.lower()
        assert "markdown" in caplog.text.lower()

    def test_missing_markdown_returns_false(self, caplog) -> None:
        """Test returns False when markdown is not installed."""
        mock_wp = _make_mock_weasyprint()
        with patch.dict(
            sys.modules, {"markdown": None, "weasyprint": mock_wp}, clear=True
        ):
            result = convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert result is False

    def test_missing_markdown_logs_error(self, caplog) -> None:
        """Test logs error message when markdown is not installed."""
        mock_wp = _make_mock_weasyprint()
        with patch.dict(
            sys.modules, {"markdown": None, "weasyprint": mock_wp}, clear=True
        ):
            convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert "weasyprint" in caplog.text.lower()

    def test_both_missing_returns_false(self, caplog) -> None:
        """Test returns False when both optional deps are missing."""
        result = convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert result is False

    # =========================================================================
    # Success Path
    # =========================================================================

    def test_successful_conversion_returns_true(self) -> None:
        """Test returns True when conversion succeeds."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            result = convert_md_to_pdf("# Hello", Path("/tmp/test.pdf"))
        assert result is True

    def test_markdown_called_with_correct_args(self) -> None:
        """Test markdown.markdown() receives content and table extensions."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("# Hello World", Path("/tmp/test.pdf"))
        mock_md.markdown.assert_called_once_with(
            "# Hello World", extensions=["tables", "fenced_code"]
        )

    def test_weasyprint_write_pdf_called_with_path(self) -> None:
        """Test HTML.write_pdf() called with correct output path."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        expected_path = Path("/tmp/out.pdf")
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("# Hello", expected_path)
        mock_wp.HTML.return_value.write_pdf.assert_called_once_with(str(expected_path))

    # =========================================================================
    # HTML Template Structure
    # =========================================================================

    def test_html_wraps_content(self) -> None:
        """Test generated HTML wraps body content with correct structure."""
        mock_md = _make_mock_markdown("<p>Hello</p>")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("# Hello", Path("/tmp/test.pdf"))
        html_string = mock_wp.HTML.call_args.kwargs["string"]
        assert "<!DOCTYPE html>" in html_string
        assert '<meta charset="utf-8">' in html_string
        assert "<p>Hello</p>" in html_string

    def test_html_includes_a4_page_styling(self) -> None:
        """Test generated HTML contains A4 @page rule."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("# Hello", Path("/tmp/test.pdf"))
        html_string = mock_wp.HTML.call_args.kwargs["string"]
        assert "size: A4" in html_string
        assert "margin: 15mm" in html_string

    def test_html_includes_profile_styling(self) -> None:
        """Test generated HTML contains resume-specific CSS selectors."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        html_string = mock_wp.HTML.call_args.kwargs["string"]
        assert "h1" in html_string
        assert "text-transform: uppercase" in html_string
        assert "font-family: Arial" in html_string

    # =========================================================================
    # Edge Cases
    # =========================================================================

    def test_empty_content_handled(self) -> None:
        """Test empty markdown string does not crash."""
        mock_md = _make_mock_markdown("")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            result = convert_md_to_pdf("", Path("/tmp/test.pdf"))
        assert result is True

    def test_whitespace_only_content(self) -> None:
        """Test whitespace-only markdown string handled."""
        mock_md = _make_mock_markdown("<p>   </p>")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            result = convert_md_to_pdf("   \n\n   ", Path("/tmp/test.pdf"))
        assert result is True

    def test_unicode_content_passthrough(self) -> None:
        """Test CJK, emoji, and accented characters in content."""
        mock_md = _make_mock_markdown("<p>日本語 🚀 José</p>")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("日本語 🚀 José", Path("/tmp/test.pdf"))
        mock_md.markdown.assert_called_once_with(
            "日本語 🚀 José", extensions=["tables", "fenced_code"]
        )

    def test_template_injection_blocked(self) -> None:
        """Test markdown content containing </style> stays in body."""
        payload = "</style><script>alert(1)</script>"
        mock_md = _make_mock_markdown(f"<p>{payload}</p>")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf(payload, Path("/tmp/test.pdf"))
        html_string = mock_wp.HTML.call_args.kwargs["string"]
        # The legitimate </style> (CSS closer) appears in <head>
        # The injected payload should only be inside <body>
        body_start = html_string.index("<body>")
        head_section = html_string[:body_start]
        body_section = html_string[body_start:]
        # Legitimate CSS </style> is in head (exactly once in the CSS block)
        assert head_section.count("</style>") == 1
        # Injected payload characters only in body
        assert "alert(1)" in body_section
        assert "alert(1)" not in head_section

    # =========================================================================
    # Exception Handling
    # =========================================================================

    def test_markdown_exception_returns_false(self, caplog) -> None:
        """Test returns False when markdown.markdown() raises an exception."""
        mock_md = _make_mock_markdown()
        mock_md.markdown.side_effect = RuntimeError("conversion failed")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            result = convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert result is False

    def test_markdown_exception_logs_error(self, caplog) -> None:
        """Test logs error message when markdown raises."""
        mock_md = _make_mock_markdown()
        mock_md.markdown.side_effect = RuntimeError("boom")
        mock_wp = _make_mock_weasyprint()
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert "Failed to generate PDF" in caplog.text

    def test_weasyprint_write_pdf_failure_returns_false(self, caplog) -> None:
        """Test returns False when write_pdf() raises OSError."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        mock_wp.HTML.return_value.write_pdf.side_effect = OSError("disk full")
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            result = convert_md_to_pdf("content", Path("/tmp/deep/nested/out.pdf"))
        assert result is False
        assert "Failed to generate PDF" in caplog.text

    def test_weasyprint_runtime_error_returns_false(self, caplog) -> None:
        """Test returns False when write_pdf() raises RuntimeError."""
        mock_md = _make_mock_markdown()
        mock_wp = _make_mock_weasyprint()
        mock_wp.HTML.return_value.write_pdf.side_effect = RuntimeError("render fail")
        with patch.dict(sys.modules, {"markdown": mock_md, "weasyprint": mock_wp}):
            result = convert_md_to_pdf("content", Path("/tmp/test.pdf"))
        assert result is False
        assert "Failed to generate PDF" in caplog.text
