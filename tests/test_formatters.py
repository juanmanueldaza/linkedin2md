"""Tests for all formatter modules."""


from linkedin2md.formatters.professional import (
    CertificationsFormatter,
    EducationFormatter,
    ExperienceFormatter,
    LanguagesFormatter,
    ProjectsFormatter,
    SkillsFormatter,
)
from linkedin2md.formatters.profile import ProfileFormatter
from linkedin2md.protocols import BilingualText

# =============================================================================
# Profile Formatter
# =============================================================================


class TestProfileFormatter:
    """Tests for ProfileFormatter."""

    def test_format_full_profile(self):
        """Test formatting complete profile."""
        formatter = ProfileFormatter()
        data = {
            "name": "John Doe",
            "title": BilingualText(en="Software Engineer", es=""),
            "email": "john@example.com",
            "phone": "+1-555-1234",
            "location": "San Francisco",
            "summary": BilingualText(en="Experienced developer.", es=""),
            "profile_meta": {
                "industry": "Technology",
                "twitter": "@johndoe",
                "websites": ["https://johndoe.dev"],
                "connections_count": 500,
            },
        }
        result = formatter.format(data, "en")

        assert "# John Doe" in result
        assert "Software Engineer" in result
        assert "john@example.com" in result
        assert "San Francisco" in result

    def test_format_minimal_profile(self):
        """Test formatting minimal profile."""
        formatter = ProfileFormatter()
        data = {
            "name": "Jane",
            "title": BilingualText(en="", es=""),
            "email": "",
            "phone": "",
            "location": "",
            "summary": BilingualText(en="", es=""),
            "profile_meta": {},
        }
        result = formatter.format(data, "en")

        assert "# Jane" in result

    def test_format_spanish_profile(self):
        """Test formatting with Spanish language."""
        formatter = ProfileFormatter()
        data = {
            "name": "Juan García",
            "title": BilingualText(en="", es="Ingeniero de Software"),
            "email": "juan@example.com",
            "phone": "",
            "location": "Buenos Aires",
            "summary": BilingualText(en="", es="Desarrollador con experiencia."),
            "profile_meta": {},
        }
        result = formatter.format(data, "es")

        assert "# Juan García" in result
        assert "Ingeniero de Software" in result


# =============================================================================
# Skills Formatter
# =============================================================================


class TestSkillsFormatter:
    """Tests for SkillsFormatter."""

    def test_format_skills_list(self):
        """Test formatting skills list."""
        formatter = SkillsFormatter()
        data = ["Python", "JavaScript", "Go", "Rust"]
        result = formatter.format(data, "en")

        assert "# Skills" in result
        assert "Python" in result
        assert "JavaScript" in result

    def test_format_empty_skills(self):
        """Test formatting empty skills list."""
        formatter = SkillsFormatter()
        data = []
        result = formatter.format(data, "en")

        # Should return empty or minimal content
        assert result == "" or "Skills" in result

    def test_format_single_skill(self):
        """Test formatting single skill."""
        formatter = SkillsFormatter()
        data = ["Python"]
        result = formatter.format(data, "en")

        assert "Python" in result


# =============================================================================
# Experience Formatter
# =============================================================================


class TestExperienceFormatter:
    """Tests for ExperienceFormatter."""

    def test_format_experience(self):
        """Test formatting work experience."""
        formatter = ExperienceFormatter()
        data = [
            {
                "company": "Tech Corp",
                "role": BilingualText(en="Senior Engineer", es=""),
                "location": "Remote",
                "start": "Jan 2020",
                "end": None,
                "achievements": [
                    {"text": BilingualText(en="Led team of 5", es="")},
                ],
            }
        ]
        result = formatter.format(data, "en")

        assert "Tech Corp" in result
        assert "Senior Engineer" in result
        assert "Jan 2020" in result

    def test_format_current_position(self):
        """Test formatting current position (no end date)."""
        formatter = ExperienceFormatter()
        data = [
            {
                "company": "Current Co",
                "role": BilingualText(en="Developer", es=""),
                "location": None,
                "start": "2023",
                "end": None,
                "achievements": [],
            }
        ]
        result = formatter.format(data, "en")

        assert "Current Co" in result
        assert "Present" in result or "2023" in result


# =============================================================================
# Education Formatter
# =============================================================================


class TestEducationFormatter:
    """Tests for EducationFormatter."""

    def test_format_education(self):
        """Test formatting education."""
        formatter = EducationFormatter()
        data = [
            {
                "institution": "MIT",
                "degree": BilingualText(en="B.S. Computer Science", es=""),
                "field": None,
                "start": "2010",
                "end": "2014",
                "location": None,
                "notes": BilingualText(en="Graduated with honors", es=""),
                "activities": "ACM Club",
            }
        ]
        result = formatter.format(data, "en")

        assert "MIT" in result
        assert "B.S. Computer Science" in result or "Computer Science" in result


# =============================================================================
# Certifications Formatter
# =============================================================================


class TestCertificationsFormatter:
    """Tests for CertificationsFormatter."""

    def test_format_certification(self):
        """Test formatting certifications."""
        formatter = CertificationsFormatter()
        data = [
            {
                "name": "AWS Solutions Architect",
                "issuer": "Amazon",
                "date": "2023-01",
                "expires": "2026-01",
                "url": "https://aws.amazon.com/cert",
                "credential_id": "ABC123",
            }
        ]
        result = formatter.format(data, "en")

        assert "AWS Solutions Architect" in result
        assert "Amazon" in result

    def test_format_empty_certifications(self):
        """Test formatting empty certifications."""
        formatter = CertificationsFormatter()
        data = []
        result = formatter.format(data, "en")

        assert result == "" or "Certification" in result


# =============================================================================
# Languages Formatter
# =============================================================================


class TestLanguagesFormatter:
    """Tests for LanguagesFormatter."""

    def test_format_languages(self):
        """Test formatting languages."""
        formatter = LanguagesFormatter()
        data = [
            {"name": "English", "proficiency": "Native"},
            {"name": "Spanish", "proficiency": "Professional"},
        ]
        result = formatter.format(data, "en")

        assert "English" in result
        assert "Spanish" in result

    def test_format_language_without_proficiency(self):
        """Test formatting language without proficiency level."""
        formatter = LanguagesFormatter()
        data = [{"name": "French", "proficiency": None}]
        result = formatter.format(data, "en")

        assert "French" in result


# =============================================================================
# Projects Formatter
# =============================================================================


class TestProjectsFormatter:
    """Tests for ProjectsFormatter."""

    def test_format_project(self):
        """Test formatting projects."""
        formatter = ProjectsFormatter()
        data = [
            {
                "title": "Open Source Tool",
                "description": BilingualText(en="A developer tool", es=""),
                "url": "https://github.com/example/tool",
                "start": "2022",
                "end": "2023",
            }
        ]
        result = formatter.format(data, "en")

        assert "Open Source Tool" in result

    def test_format_empty_projects(self):
        """Test formatting empty projects."""
        formatter = ProjectsFormatter()
        data = []
        result = formatter.format(data, "en")

        assert result == "" or "Project" in result


# =============================================================================
# Edge Cases
# =============================================================================


class TestFormatterEdgeCases:
    """Tests for edge cases in formatters."""

    def test_none_data(self):
        """Test handling of None data."""
        formatter = SkillsFormatter()
        # Should handle gracefully
        result = formatter.format([], "en")
        assert isinstance(result, str)

    def test_unicode_content(self):
        """Test handling of Unicode content."""
        formatter = ProfileFormatter()
        data = {
            "name": "José García",
            "title": BilingualText(en="Développeur", es=""),
            "email": "",
            "phone": "",
            "location": "日本",
            "summary": BilingualText(en="", es=""),
            "profile_meta": {},
        }
        result = formatter.format(data, "en")

        assert "José García" in result
        assert "日本" in result

    def test_special_markdown_characters(self):
        """Test that special Markdown characters are handled."""
        formatter = SkillsFormatter()
        data = ["C++", "C#", "Node.js", "Vue.js"]
        result = formatter.format(data, "en")

        # Should not break Markdown
        assert "C++" in result or "C" in result

    def test_very_long_content(self):
        """Test handling of very long content."""
        formatter = ProfileFormatter()
        long_summary = "A" * 10000
        data = {
            "name": "Test User",
            "title": BilingualText(en="Developer", es=""),
            "email": "",
            "phone": "",
            "location": "",
            "summary": BilingualText(en=long_summary, es=""),
            "profile_meta": {},
        }
        result = formatter.format(data, "en")

        # Should handle without issues
        assert "Test User" in result

    def test_empty_bilingual_text(self):
        """Test handling of empty bilingual text."""
        formatter = ProfileFormatter()
        data = {
            "name": "Test",
            "title": BilingualText(),
            "email": "",
            "phone": "",
            "location": "",
            "summary": BilingualText(),
            "profile_meta": {},
        }
        result = formatter.format(data, "en")

        assert "# Test" in result
