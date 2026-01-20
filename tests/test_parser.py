"""Tests for LinkedIn parser."""

import tempfile
import zipfile
from pathlib import Path

from linkedin2md.parser import (
    LinkedInExportParser,
    create_bilingual,
    detect_language,
)


def test_detect_language_english():
    """Test English detection."""
    text = "I am a software engineer with experience in Python."
    assert detect_language(text) == "en"


def test_detect_language_spanish():
    """Test Spanish detection."""
    text = "Soy un desarrollador de software con experiencia en Python."
    assert detect_language(text) == "es"


def test_detect_language_empty():
    """Test empty string."""
    assert detect_language("") == "en"


def test_create_bilingual_english():
    """Test bilingual creation for English."""
    result = create_bilingual("Hello world")
    assert result == {"en": "Hello world", "es": ""}


def test_create_bilingual_spanish():
    """Test bilingual creation for Spanish."""
    result = create_bilingual("Soy un desarrollador de software con experiencia")
    assert result == {
        "en": "",
        "es": "Soy un desarrollador de software con experiencia",
    }


def test_create_bilingual_empty():
    """Test bilingual creation for empty string."""
    result = create_bilingual("")
    assert result == {"en": "", "es": ""}


def test_parser_with_minimal_zip():
    """Test parser with minimal ZIP file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "test_export.zip"

        # Create minimal ZIP with Profile.csv
        with zipfile.ZipFile(zip_path, "w") as zf:
            profile_csv = """First Name,Last Name,Headline,Summary,Geo Location
John,Doe,Engineer,A summary,New York"""
            zf.writestr("Profile.csv", profile_csv)

            skills_csv = """Name
Python
JavaScript"""
            zf.writestr("Skills.csv", skills_csv)

        parser = LinkedInExportParser(zip_path)
        data = parser.parse()

        assert data["name"] == "John Doe"
        assert data["location"] == "New York"
        assert "Python" in data["skills"]
        assert "JavaScript" in data["skills"]
