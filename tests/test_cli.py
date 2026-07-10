"""Tests for CLI module."""

import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from linkedin2md import __version__
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

    def test_parse_version_flag(self, capsys):
        """--version prints program name + version and exits with code 0."""
        with pytest.raises(SystemExit) as exc_info:
            _parse_args(["--version"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out
        assert "linkedin2md" in captured.out


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


class TestQuietFlag:
    """Tests for the --quiet flag."""

    def test_quiet_suppresses_file_listing(self, capsys, tmp_path):
        """When --quiet is passed, stdout should not contain file listing."""
        zip_path = tmp_path / "export.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(
                "Profile.csv", "First Name,Last Name,Headline\nJohn,Doe,Engineer"
            )

        output_dir = tmp_path / "output"

        with patch(
            "sys.argv", ["linkedin2md", str(zip_path), "-o", str(output_dir), "--quiet"]
        ):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_quiet_still_creates_files(self, capsys, tmp_path):
        """When --quiet is passed, output files should still be created."""
        zip_path = tmp_path / "export.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(
                "Profile.csv", "First Name,Last Name,Headline\nJohn,Doe,Engineer"
            )

        output_dir = tmp_path / "output"

        with patch(
            "sys.argv", ["linkedin2md", str(zip_path), "-o", str(output_dir), "--quiet"]
        ):
            result = main()

        assert result == 0
        assert output_dir.exists()
        assert any(output_dir.iterdir())


# =============================================================================
# PDF Flag
# =============================================================================


class TestPdfFlag:
    """Tests for the --pdf flag."""

    def test_pdf_flag_parsed(self) -> None:
        """Test --pdf argument sets pdf attribute to True."""
        args = _parse_args(["export.zip", "--pdf"])
        assert args.pdf is True

    def test_pdf_flag_absent_defaults_false(self) -> None:
        """Test pdf attribute defaults to False without --pdf flag."""
        args = _parse_args(["export.zip"])
        assert args.pdf is False

    def test_pdf_flag_with_output(self) -> None:
        """Test --pdf with -o sets both arguments."""
        args = _parse_args(["export.zip", "--pdf", "-o", "/tmp/out"])
        assert args.pdf is True
        assert args.output == Path("/tmp/out")

    def test_pdf_no_sections_returns_1(self, caplog, tmp_path) -> None:
        """Test returns 1 when no profile section .md files exist."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            ["linkedin2md", str(dummy_zip), "--pdf", "-o", str(output_dir)],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                result = main()

        assert result == 1

    def test_pdf_happy_path(self, capsys, tmp_path) -> None:
        """Test successful PDF generation prints messages and returns 0."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "profile.md").write_text("# Profile\nJohn Doe")
        (output_dir / "experience.md").write_text("# Experience\nEngineer")
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            ["linkedin2md", str(dummy_zip), "--pdf", "-o", str(output_dir)],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                with patch("linkedin2md.pdf.convert_md_to_pdf", return_value=True):
                    result = main()

        assert result == 0
        stdout = capsys.readouterr().out
        assert "Generating PDF Resume" in stdout
        assert "Created PDF Resume" in stdout

    def test_pdf_with_quiet_suppresses_stdout(self, capsys, tmp_path) -> None:
        """Test --pdf --quiet produces no stdout messages."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "profile.md").write_text("# Profile")
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            [
                "linkedin2md",
                str(dummy_zip),
                "--pdf",
                "--quiet",
                "-o",
                str(output_dir),
            ],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                with patch("linkedin2md.pdf.convert_md_to_pdf", return_value=True):
                    result = main()

        assert result == 0
        assert capsys.readouterr().out == ""

    def test_pdf_conversion_failure_returns_1(self, caplog, tmp_path) -> None:
        """Test returns 1 when convert_md_to_pdf returns False."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "profile.md").write_text("# Profile")
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            ["linkedin2md", str(dummy_zip), "--pdf", "-o", str(output_dir)],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                with patch("linkedin2md.pdf.convert_md_to_pdf", return_value=False):
                    result = main()

        assert result == 1
        assert "Failed to generate PDF" in caplog.text

    def test_pdf_concatenates_sections_in_order(self, tmp_path) -> None:
        """Test sections are joined in correct order with newlines."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "profile.md").write_text("Profile content")
        (output_dir / "experience.md").write_text("Experience content")
        (output_dir / "skills.md").write_text("Skills content")
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            ["linkedin2md", str(dummy_zip), "--pdf", "-o", str(output_dir)],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                with patch("linkedin2md.pdf.convert_md_to_pdf") as mock_pdf:
                    main()

        called_content = mock_pdf.call_args[0][0]
        assert "Profile content" in called_content
        assert "Experience content" in called_content
        assert "Skills content" in called_content
        assert "\n\n" in called_content

    def test_pdf_skips_empty_sections(self, tmp_path) -> None:
        """Test empty .md files are excluded from resume."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "profile.md").write_text("Profile content")
        (output_dir / "experience.md").write_text("   ")
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            ["linkedin2md", str(dummy_zip), "--pdf", "-o", str(output_dir)],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                with patch("linkedin2md.pdf.convert_md_to_pdf") as mock_pdf:
                    main()

        called_content = mock_pdf.call_args[0][0]
        assert "Profile content" in called_content
        assert "Experience" not in called_content

    def test_pdf_only_existing_sections_included(self, tmp_path) -> None:
        """Test only .md files that actually exist are concatenated."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "profile.md").write_text("Only section")
        dummy_zip = tmp_path / "dummy.zip"
        dummy_zip.write_text("not a real zip but exists")

        with patch(
            "sys.argv",
            ["linkedin2md", str(dummy_zip), "--pdf", "-o", str(output_dir)],
        ):
            with patch("linkedin2md.cli.create_converter") as mock_conv:
                mock_conv.return_value.convert = lambda **kwargs: []
                with patch("linkedin2md.pdf.convert_md_to_pdf") as mock_pdf:
                    main()

        called_content = mock_pdf.call_args[0][0]
        assert called_content == "Only section"
