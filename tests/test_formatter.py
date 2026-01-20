"""Tests for Markdown formatter."""

import tempfile
from pathlib import Path

from linkedin2md.formatter import MarkdownFormatter


def test_formatter_init():
    """Test formatter initialization."""
    formatter = MarkdownFormatter()
    assert formatter.lang == "en"

    formatter_es = MarkdownFormatter(lang="es")
    assert formatter_es.lang == "es"


def test_get_text_string():
    """Test _get_text with plain string."""
    formatter = MarkdownFormatter()
    assert formatter._get_text("hello") == "hello"


def test_get_text_bilingual_en():
    """Test _get_text with bilingual dict, English preferred."""
    formatter = MarkdownFormatter(lang="en")
    bilingual = {"en": "Hello", "es": "Hola"}
    assert formatter._get_text(bilingual) == "Hello"


def test_get_text_bilingual_es():
    """Test _get_text with bilingual dict, Spanish preferred."""
    formatter = MarkdownFormatter(lang="es")
    bilingual = {"en": "Hello", "es": "Hola"}
    assert formatter._get_text(bilingual) == "Hola"


def test_get_text_fallback():
    """Test _get_text fallback when preferred lang is empty."""
    formatter = MarkdownFormatter(lang="es")
    bilingual = {"en": "Hello", "es": ""}
    assert formatter._get_text(bilingual) == "Hello"


def test_get_text_none():
    """Test _get_text with None."""
    formatter = MarkdownFormatter()
    assert formatter._get_text(None) == ""


def test_format_profile():
    """Test profile formatting."""
    formatter = MarkdownFormatter()
    data = {
        "name": "John Doe",
        "title": {"en": "Software Engineer", "es": ""},
        "location": "New York",
        "email": "john@example.com",
        "summary": {"en": "A software engineer.", "es": ""},
    }
    result = formatter._format_profile(data)

    assert "# John Doe" in result
    assert "**Software Engineer**" in result
    assert "New York" in result
    assert "john@example.com" in result
    assert "A software engineer." in result


def test_format_skills():
    """Test skills formatting."""
    formatter = MarkdownFormatter()
    skills = ["Python", "JavaScript", "TypeScript"]
    result = formatter._format_skills(skills)

    assert "# Skills" in result
    assert "Python, JavaScript, TypeScript" in result


def test_format_experience():
    """Test experience formatting."""
    formatter = MarkdownFormatter()
    experiences = [
        {
            "company": "Acme Corp",
            "role": {"en": "Developer", "es": ""},
            "start": "Jan 2020",
            "end": "Dec 2022",
            "location": "Remote",
            "achievements": [
                {"text": {"en": "Built APIs", "es": ""}},
            ],
        }
    ]
    result = formatter._format_experience(experiences)

    assert "# Experience" in result
    assert "## Acme Corp" in result
    assert "**Developer**" in result
    assert "Jan 2020" in result
    assert "Dec 2022" in result
    assert "Built APIs" in result


def test_format_all_creates_files():
    """Test format_all creates files."""
    formatter = MarkdownFormatter()
    data = {
        "name": "Test User",
        "title": {"en": "Engineer", "es": ""},
        "skills": ["Python", "Go"],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        files = formatter.format_all(data, output_dir)

        assert output_dir.exists()
        assert len(files) == 2  # profile.md and skills.md

        profile_path = output_dir / "profile.md"
        assert profile_path.exists()
        assert "Test User" in profile_path.read_text()

        skills_path = output_dir / "skills.md"
        assert skills_path.exists()
        assert "Python" in skills_path.read_text()
