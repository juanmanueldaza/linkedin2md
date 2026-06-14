"""Tests for all parser modules."""

from linkedin2md.parsers.jobs import JobDescriptionParser
from linkedin2md.parsers.professional import (
    CertificationsParser,
    EducationParser,
    ExperienceParser,
    LanguagesParser,
    ProjectsParser,
    SkillsParser,
)
from linkedin2md.parsers.profile import (
    EmailParser,
    LocationParser,
    NameParser,
    PhoneParser,
    ProfileMetaParser,
    SummaryParser,
    TitleParser,
)
from linkedin2md.protocols import BilingualText

# =============================================================================
# Profile Parsers
# =============================================================================


class TestNameParser:
    """Tests for NameParser."""

    def test_parse_full_name(self):
        """Test parsing full name."""
        parser = NameParser()
        data = {"profile": [{"First Name": "John", "Last Name": "Doe"}]}
        result = parser.parse(data)
        assert result == "John Doe"

    def test_parse_first_name_only(self):
        """Test parsing with only first name."""
        parser = NameParser()
        data = {"profile": [{"First Name": "John", "Last Name": ""}]}
        result = parser.parse(data)
        assert result == "John"

    def test_parse_empty_profile(self):
        """Test parsing with empty profile."""
        parser = NameParser()
        data = {"profile": []}
        result = parser.parse(data)
        assert result == ""

    def test_parse_missing_profile(self):
        """Test parsing with missing profile key."""
        parser = NameParser()
        data = {}
        result = parser.parse(data)
        assert result == ""

    def test_section_key(self):
        """Test section key is correct."""
        parser = NameParser()
        assert parser.section_key == "name"


class TestTitleParser:
    """Tests for TitleParser."""

    def test_parse_title(self):
        """Test parsing headline."""
        parser = TitleParser()
        data = {"profile": [{"Headline": "Software Engineer"}]}
        result = parser.parse(data)
        assert isinstance(result, BilingualText)
        assert result.en == "Software Engineer" or result.es == "Software Engineer"

    def test_parse_empty_title(self):
        """Test parsing empty headline."""
        parser = TitleParser()
        data = {"profile": [{"Headline": ""}]}
        result = parser.parse(data)
        assert result.en == "" and result.es == ""

    def test_parse_spanish_title(self):
        """Test parsing Spanish headline."""
        parser = TitleParser()
        data = {"profile": [{"Headline": "Desarrollador de Software con experiencia"}]}
        result = parser.parse(data)
        assert result.es == "Desarrollador de Software con experiencia"


class TestEmailParser:
    """Tests for EmailParser."""

    def test_parse_primary_email(self):
        """Test parsing primary email."""
        parser = EmailParser()
        data = {
            "email_addresses": [
                {"Email Address": "secondary@test.com", "Primary": "No"},
                {"Email Address": "primary@test.com", "Primary": "Yes"},
            ]
        }
        result = parser.parse(data)
        assert result == "primary@test.com"

    def test_parse_fallback_to_first(self):
        """Test fallback to first email when no primary."""
        parser = EmailParser()
        data = {
            "email_addresses": [
                {"Email Address": "first@test.com", "Primary": "No"},
                {"Email Address": "second@test.com", "Primary": "No"},
            ]
        }
        result = parser.parse(data)
        assert result == "first@test.com"

    def test_parse_no_emails(self):
        """Test parsing with no emails."""
        parser = EmailParser()
        data = {"email_addresses": []}
        result = parser.parse(data)
        assert result == ""


class TestPhoneParser:
    """Tests for PhoneParser."""

    def test_parse_phone(self):
        """Test parsing phone number."""
        parser = PhoneParser()
        data = {"phonenumbers": [{"Number": "+1-555-1234"}]}
        result = parser.parse(data)
        assert result == "+1-555-1234"

    def test_parse_no_phone(self):
        """Test parsing with no phone."""
        parser = PhoneParser()
        data = {"phonenumbers": []}
        result = parser.parse(data)
        assert result == ""


class TestLocationParser:
    """Tests for LocationParser."""

    def test_parse_geo_location(self):
        """Test parsing Geo Location field."""
        parser = LocationParser()
        data = {"profile": [{"Geo Location": "New York, USA"}]}
        result = parser.parse(data)
        assert result == "New York, USA"

    def test_parse_fallback_location(self):
        """Test fallback to Location field."""
        parser = LocationParser()
        data = {"profile": [{"Geo Location": "", "Location": "Los Angeles"}]}
        result = parser.parse(data)
        assert result == "Los Angeles"


class TestSummaryParser:
    """Tests for SummaryParser."""

    def test_parse_english_summary(self):
        """Test parsing English summary."""
        parser = SummaryParser()
        data = {
            "profile": [
                {"Summary": "Experienced software engineer with Python expertise."}
            ]
        }
        result = parser.parse(data)
        assert result.en == "Experienced software engineer with Python expertise."

    def test_parse_spanish_summary(self):
        """Test parsing Spanish summary."""
        parser = SummaryParser()
        spanish_summary = (
            "Desarrollador de software con experiencia en Python y JavaScript."
        )
        data = {"profile": [{"Summary": spanish_summary}]}
        result = parser.parse(data)
        assert result.es == spanish_summary


class TestProfileMetaParser:
    """Tests for ProfileMetaParser."""

    def test_parse_full_meta(self):
        """Test parsing full profile metadata."""
        parser = ProfileMetaParser()
        data = {
            "profile": [
                {
                    "Industry": "Technology",
                    "Twitter Handles": "[@johndoe]",
                    "Websites": "https://example.com, https://blog.example.com",
                    "Birth Date": "1990-01-01",
                }
            ],
            "registration": [{"Registered At": "2015-05-15"}],
            "connections": [{"Name": "Alice"}, {"Name": "Bob"}],
        }
        result = parser.parse(data)
        assert result["industry"] == "Technology"
        assert result["twitter"] == "@johndoe"
        assert len(result["websites"]) == 2
        assert result["connections_count"] == 2

    def test_parse_empty_meta(self):
        """Test parsing empty metadata."""
        parser = ProfileMetaParser()
        data = {"profile": [{}], "registration": [], "connections": []}
        result = parser.parse(data)
        assert result["industry"] is None
        assert result["twitter"] is None
        assert result["websites"] == []


# =============================================================================
# Professional Parsers
# =============================================================================


class TestSkillsParser:
    """Tests for SkillsParser."""

    def test_parse_skills(self):
        """Test parsing skills list."""
        parser = SkillsParser()
        data = {"skills": [{"Name": "Python"}, {"Name": "JavaScript"}, {"Name": "Go"}]}
        result = parser.parse(data)
        assert result == ["Python", "JavaScript", "Go"]

    def test_parse_deduplicate_skills(self):
        """Test deduplication of skills."""
        parser = SkillsParser()
        data = {"skills": [{"Name": "Python"}, {"Name": "python"}, {"Name": "PYTHON"}]}
        result = parser.parse(data)
        assert len(result) == 1

    def test_parse_skills_with_spanish_parenthetical(self):
        """Test handling of bilingual skill names."""
        parser = SkillsParser()
        data = {"skills": [{"Name": "Machine Learning (Aprendizaje Automático)"}]}
        result = parser.parse(data)
        assert "Aprendizaje Automático" in result[0] or "Machine Learning" in result[0]

    def test_parse_empty_skills(self):
        """Test parsing with no skills."""
        parser = SkillsParser()
        data = {"skills": []}
        result = parser.parse(data)
        assert result == []

    def test_parse_skip_empty_skill_names(self):
        """Test skipping empty skill names."""
        parser = SkillsParser()
        data = {"skills": [{"Name": ""}, {"Name": "Python"}, {"Name": "  "}]}
        result = parser.parse(data)
        assert result == ["Python"]


class TestExperienceParser:
    """Tests for ExperienceParser."""

    def test_parse_experience(self):
        """Test parsing work experience."""
        parser = ExperienceParser()
        description = "• Led team of 5 engineers\n• Increased performance by 50%"
        data = {
            "positions": [
                {
                    "Company Name": "Acme Corp",
                    "Title": "Senior Engineer",
                    "Description": description,
                    "Location": "Remote",
                    "Started On": "Jan 2020",
                    "Finished On": "Dec 2022",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) >= 1
        assert result[0]["company"] == "Acme Corp"

    def test_parse_current_position(self):
        """Test parsing current position (no end date)."""
        parser = ExperienceParser()
        data = {
            "positions": [
                {
                    "Company Name": "Current Co",
                    "Title": "Developer",
                    "Started On": "Jan 2023",
                    "Finished On": "",
                }
            ]
        }
        result = parser.parse(data)
        assert result[0]["end"] is None


class TestEducationParser:
    """Tests for EducationParser."""

    def test_parse_education(self):
        """Test parsing education."""
        parser = EducationParser()
        data = {
            "education": [
                {
                    "School Name": "MIT",
                    "Degree Name": "B.S. Computer Science",
                    "Start Date": "2010-09-01",
                    "End Date": "2014-06-01",
                    "Notes": "Graduated with honors",
                    "Activities": "ACM Club",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) >= 1
        assert result[0]["institution"] == "MIT"
        assert result[0]["start"] == "2010"
        assert result[0]["end"] == "2014"


class TestCertificationsParser:
    """Tests for CertificationsParser."""

    def test_parse_certification(self):
        """Test parsing certifications."""
        parser = CertificationsParser()
        data = {
            "certifications": [
                {
                    "Name": "AWS Solutions Architect",
                    "Authority": "Amazon",
                    "Started On": "2023-01-15",
                    "Finished On": "2026-01-15",
                    "Url": "https://aws.amazon.com/cert/123",
                    "License Number": "ABC123",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["name"] == "AWS Solutions Architect"
        assert result[0]["issuer"] == "Amazon"
        assert result[0]["credential_id"] == "ABC123"

    def test_parse_skip_empty_certification(self):
        """Test skipping certifications without name."""
        parser = CertificationsParser()
        data = {"certifications": [{"Name": ""}, {"Name": "Valid Cert"}]}
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["name"] == "Valid Cert"


class TestLanguagesParser:
    """Tests for LanguagesParser."""

    def test_parse_languages(self):
        """Test parsing languages."""
        parser = LanguagesParser()
        data = {
            "languages": [
                {"Name": "English", "Proficiency": "Native"},
                {"Name": "Spanish", "Proficiency": "Professional"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 2

    def test_parse_deduplicate_languages(self):
        """Test deduplication of languages."""
        parser = LanguagesParser()
        data = {
            "languages": [
                {"Name": "English", "Proficiency": "Native"},
                {"Name": "Inglés", "Proficiency": "Nativo"},
            ]
        }
        result = parser.parse(data)
        # Should deduplicate English/Inglés
        assert len(result) == 1

    def test_parse_normalize_spanish_names(self):
        """Test normalization of Spanish language names."""
        parser = LanguagesParser()
        data = {"languages": [{"Name": "inglés", "Proficiency": "Native"}]}
        result = parser.parse(data)
        assert result[0]["name"] == "English"


class TestProjectsParser:
    """Tests for ProjectsParser."""

    def test_parse_project(self):
        """Test parsing projects."""
        parser = ProjectsParser()
        data = {
            "projects": [
                {
                    "Title": "Open Source Tool",
                    "Description": "A tool for developers",
                    "Url": "https://github.com/example/tool",
                    "Started On": "2022-01-01",
                    "Finished On": "2022-12-31",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) >= 1
        assert result[0]["title"] == "Open Source Tool"
        assert result[0]["url"] == "https://github.com/example/tool"

    def test_parse_skip_empty_project(self):
        """Test skipping projects without title."""
        parser = ProjectsParser()
        data = {"projects": [{"Title": ""}, {"Title": "Valid Project"}]}
        result = parser.parse(data)
        assert len(result) == 1


# =============================================================================
# Edge Cases
# =============================================================================


class TestParserEdgeCases:
    """Tests for edge cases across parsers."""

    def test_missing_csv_key(self):
        """Test handling of missing CSV key."""
        parser = NameParser()
        result = parser.parse({})
        assert result == ""

    def test_empty_data(self):
        """Test handling of empty data."""
        parser = SkillsParser()
        result = parser.parse({"skills": []})
        assert result == []

    def test_malformed_data(self):
        """Test handling of malformed data."""
        parser = NameParser()
        # Missing expected fields
        result = parser.parse({"profile": [{"UnexpectedField": "value"}]})
        assert result == ""

    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        parser = NameParser()
        data = {"profile": [{"First Name": "José", "Last Name": "García"}]}
        result = parser.parse(data)
        assert result == "José García"

    def test_special_characters(self):
        """Test handling of special characters."""
        parser = TitleParser()
        data = {"profile": [{"Headline": "Engineer & Architect | Tech Lead"}]}
        result = parser.parse(data)
        assert "|" in result.get("en") or "|" in result.get("es")


# =============================================================================
# Job Description Parser
# =============================================================================


class TestJobDescriptionParser:
    """Tests for JobDescriptionParser."""

    def test_parse_single_job_description(self):
        """Test parsing one valid job description entry returns correct dict."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {
                    "Company Name": "Acme Corp",
                    "Job Title": "Senior Engineer",
                    "Description": "Build and maintain systems.",
                    "Application Date": "2024-01-15",
                    "Status": "Applied",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Acme Corp"
        assert result[0]["title"] == "Senior Engineer"
        assert result[0]["description"] == "Build and maintain systems."
        assert result[0]["date_applied"] == "2024-01-15"
        assert result[0]["status"] == "Applied"

    def test_parse_fallback_to_applications(self):
        """Test fallback to job_applications CSV when job_descriptions missing."""
        parser = JobDescriptionParser()
        data = {
            "job_applications": [
                {
                    "Company": "Beta Inc",
                    "Title": "Developer",
                    "Job Description": "Code stuff.",
                    "Date Applied": "2024-02-01",
                    "Status": "Interviewed",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Beta Inc"
        assert result[0]["title"] == "Developer"

    def test_parse_empty_data_returns_empty(self):
        """Test empty or missing CSV keys return empty list."""
        parser = JobDescriptionParser()
        assert parser.parse({}) == []
        assert parser.parse({"job_descriptions": []}) == []

    def test_skip_empty_company_and_title(self):
        """Test entries with both empty company and title are skipped."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {"Company Name": "", "Job Title": ""},
                {"Company Name": "Valid Co", "Job Title": "Valid Role"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Valid Co"

    def test_allow_title_only_entry(self):
        """Test entry with empty company but valid title passes through."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {"Company Name": "", "Job Title": "Ghost Role"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == ""
        assert result[0]["title"] == "Ghost Role"

    def test_unicode_in_fields(self):
        """Test handling of unicode characters in company/title/description."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {
                    "Company Name": "Café ñoño",
                    "Job Title": "Développeur",
                    "Description": "日本語の説明",
                    "Application Date": "2024-03-01",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Café ñoño"
        assert result[0]["title"] == "Développeur"
        assert result[0]["description"] == "日本語の説明"

    def test_missing_optional_fields_are_none(self):
        """Test missing optional fields return None."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {"Company Name": "Minimal Co", "Job Title": "Role"},
            ]
        }
        result = parser.parse(data)
        assert result[0]["description"] is None
        assert result[0]["date_applied"] is None
        assert result[0]["status"] is None

    def test_section_key(self):
        """Test section_key returns correct value."""
        parser = JobDescriptionParser()
        assert parser.section_key == "job_descriptions"
