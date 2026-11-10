"""Tests for resume heading demotion in PDF assembly."""

from linkedin2md.pdf import assemble_resume_markdown


class TestDemoteHeadings:
    """Only real ATX headings may shift a level; other content is untouched."""

    def test_demotes_real_headings(self):
        """H1/H2 section headings shift down one level, profile H1 stays."""
        sections = [
            ("profile", "# Jane Doe"),
            ("experience", "# Experience\n## Acme Corp"),
        ]
        combined = assemble_resume_markdown(sections)
        assert combined.startswith("# Jane Doe")
        assert "## Experience" in combined
        assert "### Acme Corp" in combined

    def test_leaves_hashtag_text_untouched(self):
        """A #tag line is not a heading and must not gain an extra #."""
        sections = [
            ("profile", "# Jane Doe"),
            ("experience", "# Experience\n#OpenToWork"),
        ]
        combined = assemble_resume_markdown(sections)
        assert "#OpenToWork" in combined
        assert "##OpenToWork" not in combined

    def test_leaves_fenced_code_untouched(self):
        """# comments inside fenced code blocks must not be demoted."""
        body = "# Experience\n```python\n# comment\n```"
        sections = [("profile", "# Jane Doe"), ("experience", body)]
        combined = assemble_resume_markdown(sections)
        assert "```python\n# comment\n```" in combined

    def test_h6_heading_is_not_demoted_to_invalid_h7(self):
        """H6 cannot shift down (H7 is not valid Markdown); leave it as is."""
        body = "# Experience\n###### Deep"
        sections = [("profile", "# Jane Doe"), ("experience", body)]
        combined = assemble_resume_markdown(sections)
        assert "###### Deep" in combined
        assert "#######" not in combined
