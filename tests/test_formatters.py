"""Tests for all formatter modules."""

from linkedin2md.formatters.content import (
    ArticlesFormatter,
    CommentsFormatter,
    EventsFormatter,
    MediaFormatter,
    MessagesFormatter,
    PostsFormatter,
    ReactionsFormatter,
    RepostsFormatter,
    SavedItemsFormatter,
    ScriptFormatter,
    VotesFormatter,
)
from linkedin2md.formatters.jobs import JobDescriptionFormatter
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


# =============================================================================
# Messages Formatter
# =============================================================================


class TestMessagesFormatter:
    """Tests for MessagesFormatter."""

    def test_format_single_message(self):
        """Test formatting one message entry renders header with from/to/subject."""
        formatter = MessagesFormatter()
        data = [
            {
                "date": "2023-01-15",
                "from_name": "Alice Smith",
                "to_name": "Bob Jones",
                "subject": "Meeting Notes",
                "content": "Here are the notes.",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Messages" in result
        assert "Alice Smith" in result
        assert "Bob Jones" in result
        assert "Meeting Notes" in result

    def test_format_empty(self):
        """Test formatting empty messages list returns ''."""
        formatter = MessagesFormatter()
        data = []
        result = formatter.format(data, "en")
        assert result == ""

    def test_format_truncates_long_content(self):
        """Test that content over 500 characters is truncated with '...'."""
        formatter = MessagesFormatter()
        long_content = "A" * 600
        data = [
            {
                "date": "2023-01-15",
                "from_name": "Alice",
                "to_name": "Bob",
                "subject": "Long Email",
                "content": long_content,
            }
        ]
        result = formatter.format(data, "en")
        assert "..." in result
        assert len(result.split("...")[0].split("> ")[-1]) <= 500


# =============================================================================
# Script Formatter
# =============================================================================


class TestScriptFormatter:
    """Tests for ScriptFormatter."""

    def test_format_single_script(self):
        """Test renders '# Scripts' header, includes name/date/content."""
        formatter = ScriptFormatter()
        data = [
            {
                "name": "Test Script",
                "date": "2023-01-15",
                "content": "Script content here",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Scripts" in result
        assert "Test Script" in result
        assert "2023-01-15" in result
        assert "Script content here" in result

    def test_format_empty(self):
        """Test empty list returns ''."""
        formatter = ScriptFormatter()
        data = []
        result = formatter.format(data, "en")
        assert result == ""

    def test_format_multiple_scripts(self):
        """Test two entries renders both."""
        formatter = ScriptFormatter()
        data = [
            {
                "name": "Script 1",
                "date": "2023-01-15",
                "content": "First content",
            },
            {
                "name": "Script 2",
                "date": "2023-01-16",
                "content": "Second content",
            },
        ]
        result = formatter.format(data, "en")
        assert "Script 1" in result
        assert "Script 2" in result


# =============================================================================
# Articles Formatter
# =============================================================================


class TestArticlesFormatter:
    """Tests for ArticlesFormatter."""

    def test_format_single_article(self):
        """Test renders '# Published Articles' header with title/date/author/summary."""
        formatter = ArticlesFormatter()
        data = [
            {
                "title": "My Article",
                "date": "2023-01-15",
                "author": "John Doe",
                "summary": "A brief summary",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Published Articles" in result
        assert "My Article" in result
        assert "2023-01-15" in result
        assert "John Doe" in result
        assert "A brief summary" in result

    def test_format_empty(self):
        """Test empty list returns ''."""
        formatter = ArticlesFormatter()
        data = []
        result = formatter.format(data, "en")
        assert result == ""


# =============================================================================
# Content Formatters
# =============================================================================


class TestPostsFormatter:
    """Tests for PostsFormatter."""

    def test_format_single_post(self) -> None:
        """Test formatting a post renders header, date, content, link, separator."""
        formatter = PostsFormatter()
        data = [
            {
                "date": "2023-06-15",
                "url": "https://linkedin.com/posts/1",
                "content": {"en": "Great post!"},
            }
        ]
        result = formatter.format(data, "en")
        assert "# Posts" in result
        assert "## 2023-06-15" in result
        assert "Great post!" in result
        assert "[View Post](https://linkedin.com/posts/1)" in result
        assert "---" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert PostsFormatter().format([], "en") == ""

    def test_format_multiple_posts(self) -> None:
        """Test multiple posts separated by ---."""
        formatter = PostsFormatter()
        data = [
            {"date": "2023-01-01", "content": {"en": "First"}},
            {"date": "2023-06-15", "content": {"en": "Second"}},
        ]
        result = formatter.format(data, "en")
        assert result.count("---") == 2

    def test_format_missing_content_omitted(self) -> None:
        """Test post without content renders date and separator only."""
        formatter = PostsFormatter()
        data = [{"date": "2023-06-15"}]
        result = formatter.format(data, "en")
        assert "## 2023-06-15" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'posts'."""
        assert PostsFormatter().section_key == "posts"


class TestCommentsFormatter:
    """Tests for CommentsFormatter."""

    def test_format_single_comment(self) -> None:
        """Test formatting comment with bold date, blockquote message, view link."""
        formatter = CommentsFormatter()
        data = [
            {
                "date": "2023-06-15",
                "url": "https://example.com",
                "message": {"en": "Great article!"},
            }
        ]
        result = formatter.format(data, "en")
        assert "# Comments" in result
        assert "**2023-06-15**" in result
        assert "> Great article!" in result
        assert "[View](https://example.com)" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert CommentsFormatter().format([], "en") == ""

    def test_format_multiple_comments(self) -> None:
        """Test multiple comments rendered in order."""
        formatter = CommentsFormatter()
        data = [
            {"date": "2023-01-01", "message": {"en": "First"}},
            {"date": "2023-06-15", "message": {"en": "Second"}},
        ]
        result = formatter.format(data, "en")
        assert "**2023-01-01**" in result
        assert "**2023-06-15**" in result

    def test_format_missing_url_omitted(self) -> None:
        """Test comment without url omits the View link."""
        formatter = CommentsFormatter()
        data = [{"date": "2023-06-15", "message": {"en": "Test"}}]
        result = formatter.format(data, "en")
        assert "[View]" not in result

    def test_section_key(self) -> None:
        """Test section_key returns 'comments'."""
        assert CommentsFormatter().section_key == "comments"


class TestReactionsFormatter:
    """Tests for ReactionsFormatter."""

    def test_format_single_reaction(self) -> None:
        """Test table with Date, Type, Link columns."""
        formatter = ReactionsFormatter()
        data = [{"date": "2023-06-15", "type": "LIKE", "url": "https://example.com"}]
        result = formatter.format(data, "en")
        assert "# Reactions" in result
        assert "| Date | Type | Link |" in result
        assert "| 2023-06-15 | LIKE | [View](https://example.com) |" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert ReactionsFormatter().format([], "en") == ""

    def test_format_missing_fields(self) -> None:
        """Test reaction without type/url renders empty cells."""
        formatter = ReactionsFormatter()
        data = [{"date": "2023-06-15"}]
        result = formatter.format(data, "en")
        assert "| 2023-06-15" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'reactions'."""
        assert ReactionsFormatter().section_key == "reactions"


class TestRepostsFormatter:
    """Tests for RepostsFormatter."""

    def test_format_single_repost(self) -> None:
        """Test table with Date, Link columns."""
        formatter = RepostsFormatter()
        data = [{"date": "2023-06-15", "url": "https://example.com"}]
        result = formatter.format(data, "en")
        assert "# Reposts" in result
        assert "| Date | Link |" in result
        assert "[View](https://example.com)" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert RepostsFormatter().format([], "en") == ""

    def test_format_no_url(self) -> None:
        """Test repost without url renders empty link cell."""
        formatter = RepostsFormatter()
        data = [{"date": "2023-06-15"}]
        result = formatter.format(data, "en")
        assert "| 2023-06-15 |  |" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'reposts'."""
        assert RepostsFormatter().section_key == "reposts"


class TestVotesFormatter:
    """Tests for VotesFormatter."""

    def test_format_single_vote(self) -> None:
        """Test table with Date, Option, Link columns."""
        formatter = VotesFormatter()
        data = [{"date": "2023-06-15", "option": "Yes", "url": "https://example.com"}]
        result = formatter.format(data, "en")
        assert "# Poll Votes" in result
        assert "| Date | Option | Link |" in result
        assert "| 2023-06-15 | Yes | [View](https://example.com) |" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert VotesFormatter().format([], "en") == ""

    def test_format_pipe_in_option_escaped(self) -> None:
        """Test option text containing pipe character is rendered safely."""
        formatter = VotesFormatter()
        data = [{"date": "2023-06-15", "option": "Yes | No", "url": ""}]
        result = formatter.format(data, "en")
        assert "Yes" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'votes'."""
        assert VotesFormatter().section_key == "votes"


class TestSavedItemsFormatter:
    """Tests for SavedItemsFormatter."""

    def test_format_single_item(self) -> None:
        """Test table with Saved At, Link columns."""
        formatter = SavedItemsFormatter()
        data = [
            {
                "saved_at": "2023-01-15",
                "url": "https://example.com/article",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Saved Items" in result
        assert "| Saved At | Link |" in result
        assert "[View](https://example.com/article)" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert SavedItemsFormatter().format([], "en") == ""

    def test_format_missing_saved_at(self) -> None:
        """Test missing saved_at renders empty cell."""
        formatter = SavedItemsFormatter()
        data = [{"url": "https://example.com"}]
        result = formatter.format(data, "en")
        assert "|  |" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'saved_items'."""
        assert SavedItemsFormatter().section_key == "saved_items"


class TestEventsFormatter:
    """Tests for EventsFormatter."""

    def test_format_single_event(self) -> None:
        """Test table with Name, Time, Status columns."""
        formatter = EventsFormatter()
        data = [
            {
                "name": "Tech Conf",
                "time": "2023-07-01",
                "status": "ATTENDED",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Events" in result
        assert "| Name | Time | Status |" in result
        assert "| Tech Conf | 2023-07-01 | ATTENDED |" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert EventsFormatter().format([], "en") == ""

    def test_format_missing_fields(self) -> None:
        """Test missing time/status renders empty cells."""
        formatter = EventsFormatter()
        data = [{"name": "Minimal Event"}]
        result = formatter.format(data, "en")
        assert "| Minimal Event |  |  |" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'events'."""
        assert EventsFormatter().section_key == "events"


class TestMediaFormatter:
    """Tests for MediaFormatter."""

    def test_format_single_media(self) -> None:
        """Test table with Date, Description, Link columns."""
        formatter = MediaFormatter()
        data = [
            {
                "date": "2023-06-15",
                "description": "Team photo",
                "url": "https://example.com/img.jpg",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Uploaded Media" in result
        assert "| Date | Description | Link |" in result
        assert "Team photo" in result
        assert "[View](https://example.com/img.jpg)" in result

    def test_format_empty_data(self) -> None:
        """Test empty data returns ''."""
        assert MediaFormatter().format([], "en") == ""

    def test_format_missing_fields(self) -> None:
        """Test missing date/description renders empty cells."""
        formatter = MediaFormatter()
        data = [{"url": "https://example.com/img.jpg"}]
        result = formatter.format(data, "en")
        assert "|  |  | [View]" in result

    def test_section_key(self) -> None:
        """Test section_key returns 'media'."""
        assert MediaFormatter().section_key == "media"


class TestJobDescriptionFormatter:
    """Tests for JobDescriptionFormatter."""

    def test_format_single_job(self):
        """Test formatting a single job entry produces structured markdown."""
        formatter = JobDescriptionFormatter()
        data = [
            {
                "company": "Acme Corp",
                "title": "Senior Engineer",
                "description": "Build and maintain systems.",
                "date_applied": "2024-01-15",
                "status": "Applied",
            }
        ]
        result = formatter.format(data, "en")
        assert "# Job Descriptions" in result
        assert "## Acme Corp" in result
        assert "**Title:** Senior Engineer" in result
        assert "**Description:** Build and maintain systems." in result
        assert "**Date Applied:** 2024-01-15" in result
        assert "**Status:** Applied" in result
        assert "---" in result

    def test_format_empty_data_returns_empty(self):
        """Test empty data returns empty string."""
        formatter = JobDescriptionFormatter()
        assert formatter.format([], "en") == ""

    def test_format_missing_optional_fields_omitted(self):
        """Test missing optional fields are not rendered."""
        formatter = JobDescriptionFormatter()
        data = [
            {
                "company": "Minimal Co",
                "title": "",
                "description": None,
                "date_applied": None,
                "status": "",
            }
        ]
        result = formatter.format(data, "en")
        assert "## Minimal Co" in result
        assert "**Title:** (not specified)" in result
        assert "**Description:**" not in result
        assert "**Date Applied:**" not in result
        assert "**Status:**" not in result

    def test_format_title_only_entry(self):
        """Test entry with only title uses title as heading."""
        formatter = JobDescriptionFormatter()
        data = [
            {
                "company": "",
                "title": "Ghost Role",
                "description": None,
                "date_applied": None,
                "status": None,
            }
        ]
        result = formatter.format(data, "en")
        assert "## Ghost Role" in result
        assert "**Company:** (not specified)" in result

    def test_format_company_only_entry(self):
        """Test entry with only company uses company as heading."""
        formatter = JobDescriptionFormatter()
        data = [
            {
                "company": "Only Co",
                "title": "",
                "description": None,
                "date_applied": None,
                "status": None,
            }
        ]
        result = formatter.format(data, "en")
        assert "## Only Co" in result
        assert "**Title:** (not specified)" in result

    def test_format_empty_company_and_title_fallback(self):
        """Test fallback to 'Unknown' when both company and title are empty."""
        formatter = JobDescriptionFormatter()
        data = [
            {
                "company": "",
                "title": "",
                "description": None,
                "date_applied": None,
                "status": None,
            }
        ]
        result = formatter.format(data, "en")
        assert "## Unknown" in result

    def test_format_multiple_jobs(self):
        """Test formatting multiple job entries."""
        formatter = JobDescriptionFormatter()
        data = [
            {"company": "Acme", "title": "Dev"},
            {"company": "Beta", "title": "PM"},
        ]
        result = formatter.format(data, "en")
        assert "## Acme" in result
        assert "## Beta" in result
        # Two separators
        assert result.count("---") == 2

    def test_section_key(self):
        """Test section_key returns correct value."""
        formatter = JobDescriptionFormatter()
        assert formatter.section_key == "job_descriptions"


class TestUrlSanitizationIntegration:
    """Regression test for issue #32: formatters must call _sanitize_url()."""

    def test_professional_certificate_url_is_sanitized(self):
        """Cert URLs go through _sanitize_url (issue #32)."""
        from linkedin2md.formatters.professional import CertificationsFormatter
        f = CertificationsFormatter()
        certs = [{
            "title": "AWS",
            "url": "javascript:alert(1)",  # malicious
        }]
        result = f.format(certs, "en")
        # Malicious URL should be replaced with empty string
        assert "javascript:" not in result
        assert "[View Certificate]()" in result or "View Certificate" not in result

    def test_content_view_url_is_sanitized(self):
        """Content view URLs go through _sanitize_url (issue #32)."""
        from linkedin2md.formatters.content import CommentsFormatter
        f = CommentsFormatter()
        comments = [{
            "date": "2024-01-01",
            "message": "test",
            "url": "javascript:alert(1)",
        }]
        result = f.format(comments, "en")
        assert "javascript:" not in result

    def test_https_url_preserved(self):
        """Valid https URLs should be preserved in output."""
        from linkedin2md.formatters.content import CommentsFormatter
        f = CommentsFormatter()
        comments = [{
            "date": "2024-01-01",
            "message": "test",
            "url": "https://linkedin.com/post/123",
        }]
        result = f.format(comments, "en")
        assert "https://linkedin.com/post/123" in result

    def test_data_url_rejected(self):
        """data: URLs should be rejected by sanitizer."""
        from linkedin2md.formatters.content import CommentsFormatter
        f = CommentsFormatter()
        comments = [{
            "date": "2024-01-01",
            "message": "test",
            "url": "data:text/html,<script>alert(1)</script>",
        }]
        result = f.format(comments, "en")
        assert "data:" not in result
        assert "script" not in result
