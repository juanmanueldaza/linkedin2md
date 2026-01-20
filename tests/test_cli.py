"""Tests for CLI module."""

import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from linkedin2md.cli import MAX_FILE_SIZE_MB, _parse_args, main


class TestParseArgs:
    """Tests for argument parsing."""

    def test_parse_source_only(self):
        """Test parsing with only source argument."""
        args = _parse_args(["export.zip"])
        assert args.source == Path("export.zip")
        assert args.output == Path("linkedin_export")
        assert args.lang == "en"

    def test_parse_with_output(self):
        """Test parsing with custom output directory."""
        args = _parse_args(["export.zip", "-o", "my-output"])
        assert args.source == Path("export.zip")
        assert args.output == Path("my-output")

    def test_parse_with_output_long(self):
        """Test parsing with --output long form."""
        args = _parse_args(["export.zip", "--output", "my-output"])
        assert args.output == Path("my-output")

    def test_parse_with_lang_en(self):
        """Test parsing with English language."""
        args = _parse_args(["export.zip", "--lang", "en"])
        assert args.lang == "en"

    def test_parse_with_lang_es(self):
        """Test parsing with Spanish language."""
        args = _parse_args(["export.zip", "--lang", "es"])
        assert args.lang == "es"

    def test_parse_invalid_lang(self):
        """Test parsing with invalid language raises error."""
        with pytest.raises(SystemExit):
            _parse_args(["export.zip", "--lang", "fr"])

    def test_parse_all_options(self):
        """Test parsing with all options."""
        args = _parse_args(["export.zip", "-o", "output", "--lang", "es"])
        assert args.source == Path("export.zip")
        assert args.output == Path("output")
        assert args.lang == "es"

    def test_parse_missing_source(self):
        """Test parsing without source raises error."""
        with pytest.raises(SystemExit):
            _parse_args([])


class TestMain:
    """Tests for main entry point."""

    def test_file_not_found(self, caplog):
        """Test error when file doesn't exist."""
        with patch("sys.argv", ["linkedin2md", "nonexistent.zip"]):
            result = main()

        assert result == 1
        assert "File not found" in caplog.text

    def test_not_a_zip_file(self, caplog):
        """Test error when file is not a ZIP."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a zip")
            temp_path = f.name

        try:
            with patch("sys.argv", ["linkedin2md", temp_path]):
                result = main()

            assert result == 1
            assert "Expected .zip file" in caplog.text
        finally:
            Path(temp_path).unlink()

    def test_file_too_large(self, caplog):
        """Test error when file exceeds size limit."""
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            temp_path = f.name

        try:
            # Mock stat to return large file size
            with patch("sys.argv", ["linkedin2md", temp_path]):
                with patch.object(Path, "exists", return_value=True):
                    with patch.object(Path, "stat") as mock_stat:
                        mock_stat.return_value.st_size = (
                            (MAX_FILE_SIZE_MB + 1) * 1024 * 1024
                        )
                        with patch.object(Path, "suffix", ".zip"):
                            result = main()

            assert result == 1
            assert "File too large" in caplog.text
        finally:
            Path(temp_path).unlink()

    def test_successful_conversion(self, capsys):
        """Test successful conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal valid ZIP
            zip_path = Path(tmpdir) / "export.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr(
                    "Profile.csv", "First Name,Last Name,Headline\nJohn,Doe,Engineer"
                )

            output_dir = Path(tmpdir) / "output"

            with patch(
                "sys.argv", ["linkedin2md", str(zip_path), "-o", str(output_dir)]
            ):
                result = main()

            assert result == 0
            captured = capsys.readouterr()
            assert "Created" in captured.out
            assert output_dir.exists()

    def test_conversion_with_spanish(self, capsys):
        """Test conversion with Spanish language option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "export.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr(
                    "Profile.csv",
                    "First Name,Last Name,Headline\nJuan,García,Ingeniero",
                )

            output_dir = Path(tmpdir) / "output"

            with patch(
                "sys.argv",
                ["linkedin2md", str(zip_path), "-o", str(output_dir), "--lang", "es"],
            ):
                result = main()

            assert result == 0

    def test_invalid_zip_file(self, caplog):
        """Test error when ZIP file is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "corrupt.zip"
            zip_path.write_text("not a valid zip")

            with patch("sys.argv", ["linkedin2md", str(zip_path)]):
                result = main()

            assert result == 1
            assert "Invalid" in caplog.text or "corrupted" in caplog.text


class TestMaxFileSize:
    """Tests for file size constant."""

    def test_max_file_size_reasonable(self):
        """Ensure MAX_FILE_SIZE_MB is reasonable."""
        assert MAX_FILE_SIZE_MB > 0
        assert MAX_FILE_SIZE_MB <= 1000  # At most 1GB
        assert MAX_FILE_SIZE_MB == 500  # Current expected value
