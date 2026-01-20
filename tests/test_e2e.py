"""End-to-end tests for linkedin2md.

These tests simulate real-world usage with complete LinkedIn export data.
"""

import zipfile
from pathlib import Path

import pytest

from linkedin2md.converter import create_converter


class TestEndToEnd:
    """End-to-end integration tests."""

    @pytest.fixture
    def sample_linkedin_export(self, tmp_path: Path) -> Path:
        """Create a comprehensive sample LinkedIn export ZIP."""
        zip_path = tmp_path / "Complete_LinkedInDataExport.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            # Profile
            profile_csv = (
                "First Name,Last Name,Headline,Summary,Industry,"
                "Geo Location,Twitter Handles,Websites,Birth Date\n"
                "John,Doe,Senior Software Engineer,"
                '"Experienced developer with 10+ years in Python and cloud '
                'technologies. I love building scalable systems.",'
                "Technology,San Francisco Bay Area,[@johndoe],"
                "https://johndoe.dev,1990-05-15"
            )
            zf.writestr("Profile.csv", profile_csv)

            # Email
            zf.writestr(
                "Email Addresses.csv",
                """Email Address,Confirmed,Primary,Updated On
john.doe@gmail.com,Yes,Yes,2020-01-01
john.doe@work.com,Yes,No,2019-06-15""",
            )

            # Phone
            zf.writestr(
                "PhoneNumbers.csv",
                """Number,Type
+1-555-123-4567,Mobile""",
            )

            # Skills
            zf.writestr(
                "Skills.csv",
                """Name
Python
JavaScript
AWS
Docker
Kubernetes
PostgreSQL
Redis
GraphQL""",
            )

            # Positions (Experience)
            positions_csv = (
                "Company Name,Title,Description,Location,Started On,Finished On\n"
                'Tech Corp,Senior Software Engineer,"• Led development of '
                "microservices architecture\n"
                "• Reduced deployment time by 80%\n"
                '• Mentored 5 junior developers",San Francisco,Jan 2020,\n'
                'Startup Inc,Software Engineer,"Built full-stack web '
                "applications using React and Python. Implemented CI/CD "
                'pipelines.",New York,Jun 2017,Dec 2019\n'
                "Big Company,Junior Developer,Entry level development work. "
                "Learned best practices.,Chicago,Jan 2015,May 2017"
            )
            zf.writestr("Positions.csv", positions_csv)

            # Education
            education_csv = (
                "School Name,Degree Name,Start Date,End Date,Notes,Activities\n"
                "MIT,B.S. Computer Science,2011-09-01,2015-05-31,"
                "Graduated with honors,ACM Club; Hackathon Team\n"
                "Stanford,Online Certificate in Machine Learning,"
                "2020-01-01,2020-06-30,,"
            )
            zf.writestr("Education.csv", education_csv)

            # Certifications
            certs_csv = (
                "Name,Url,Authority,Started On,Finished On,License Number\n"
                "AWS Solutions Architect,https://aws.amazon.com/cert,"
                "Amazon Web Services,2023-01-15,2026-01-15,AWS-123456\n"
                "Kubernetes Administrator,https://cncf.io/cert,"
                "CNCF,2022-06-01,2025-06-01,CKA-789"
            )
            zf.writestr("Certifications.csv", certs_csv)

            # Languages
            zf.writestr(
                "Languages.csv",
                """Name,Proficiency
English,Native or bilingual proficiency
Spanish,Professional working proficiency
French,Elementary proficiency""",
            )

            # Connections
            zf.writestr(
                "Connections.csv",
                """Notes:
"When exporting your connection data..."

First Name,Last Name,URL,Email Address,Company,Position,Connected On
Alice,Smith,https://linkedin.com/in/alice,alice@company.com,Google,Engineer,2020-01-15
Bob,Johnson,https://linkedin.com/in/bob,bob@startup.com,Startup,CTO,2019-06-20
Carol,Williams,https://linkedin.com/in/carol,,Microsoft,PM,2021-03-10""",
            )

            # Recommendations Received
            recs_csv = (
                "First Name,Last Name,Company,Job Title,Text,"
                "Creation Date,Status\n"
                'Alice,Smith,Google,Engineer,"John is an exceptional '
                "engineer. His technical skills and leadership are "
                'outstanding.",2023-05-15,VISIBLE\n'
                'Bob,Johnson,Startup,CTO,"I had the pleasure of working '
                'with John. Highly recommend!",2022-11-20,VISIBLE'
            )
            zf.writestr("Recommendations Received.csv", recs_csv)

            # Skills Endorsements
            zf.writestr(
                "Endorsement Received Info.csv",
                """Skill Name,Endorser First Name,Endorser Last Name,Endorsement Date
Python,Alice,Smith,2023-01-15
Python,Bob,Johnson,2023-02-20
AWS,Carol,Williams,2022-12-10""",
            )

            # Learning
            zf.writestr(
                "Learning.csv",
                """Content Title,Content Type,Content Last Watched Date,Completed Date
Python Advanced Techniques,COURSE,2023-06-15,2023-06-20
AWS Fundamentals,COURSE,2023-03-10,2023-03-15""",
            )

            # Job Applications
            jobs_csv = (
                "Application Date,Company,Job Title,Contact Email,"
                "Status,Withdraw Date,Job Url\n"
                "2023-08-15,Dream Company,Staff Engineer,hr@dreamco.com,"
                "Applied,,https://linkedin.com/jobs/123\n"
                "2023-07-01,Another Corp,Senior Dev,jobs@another.com,"
                "Withdrawn,2023-07-10,https://linkedin.com/jobs/456"
            )
            zf.writestr("Job Applications.csv", jobs_csv)

            # Saved Jobs
            zf.writestr(
                "Saved Jobs.csv",
                """Job Title,Company,Job Url,Saved Date
Principal Engineer,Top Tech,https://linkedin.com/jobs/789,2023-09-01""",
            )

            # Search Queries
            zf.writestr(
                "SearchQueries.csv",
                """Search Query,Search Date
python developer remote,2023-08-01
staff engineer bay area,2023-08-15""",
            )

            # Reactions
            zf.writestr(
                "Reactions.csv",
                """Date,Type,Link
2023-09-01,LIKE,https://linkedin.com/post/123
2023-08-20,CELEBRATE,https://linkedin.com/post/456""",
            )

            # Posts (Shares)
            shares_csv = (
                "Date,ShareLink,ShareCommentary\n"
                "2023-07-15,https://linkedin.com/post/my-post,"
                "Excited to share my thoughts on microservices architecture!"
            )
            zf.writestr("Shares.csv", shares_csv)

            # Inferences (Privacy)
            zf.writestr(
                "Inferences_about_you.csv",
                """Inference,Category
Interested in cloud computing,Interests
Likely to change jobs,Career""",
            )

            # Registration
            zf.writestr(
                "Registration.csv",
                """Registered At,Ip Address
2015-03-20,192.168.1.1""",
            )

        return zip_path

    def test_full_conversion_english(
        self, sample_linkedin_export: Path, tmp_path: Path
    ):
        """Test full conversion with English output."""
        output_dir = tmp_path / "output"

        converter = create_converter(sample_linkedin_export, output_dir)
        files = converter.convert(lang="en")

        # Verify output directory created
        assert output_dir.exists()

        # Verify multiple files created
        assert len(files) >= 10

        # Check key files exist
        file_names = [f.name for f in files]
        assert "profile.md" in file_names
        assert "skills.md" in file_names
        assert "experience.md" in file_names

        # Verify profile content
        profile_content = (output_dir / "profile.md").read_text()
        assert "John Doe" in profile_content
        assert "Senior Software Engineer" in profile_content
        assert "San Francisco" in profile_content

        # Verify skills content
        skills_content = (output_dir / "skills.md").read_text()
        assert "Python" in skills_content
        assert "AWS" in skills_content

        # Verify experience content
        experience_content = (output_dir / "experience.md").read_text()
        assert "Tech Corp" in experience_content
        assert "microservices" in experience_content

    def test_full_conversion_spanish(
        self, sample_linkedin_export: Path, tmp_path: Path
    ):
        """Test full conversion with Spanish output."""
        output_dir = tmp_path / "output"

        converter = create_converter(sample_linkedin_export, output_dir)
        files = converter.convert(lang="es")

        assert output_dir.exists()
        assert len(files) >= 10

        # Spanish headers should be used where applicable
        profile_content = (output_dir / "profile.md").read_text()
        assert "John Doe" in profile_content

    def test_connections_parsing(self, sample_linkedin_export: Path, tmp_path: Path):
        """Test that connections are parsed correctly, including header notes skip."""
        output_dir = tmp_path / "output"

        converter = create_converter(sample_linkedin_export, output_dir)
        converter.convert(lang="en")

        connections_file = output_dir / "connections.md"
        if connections_file.exists():
            content = connections_file.read_text()
            assert "Alice" in content or "Bob" in content
            # Should NOT contain the notes header
            assert "When exporting" not in content

    def test_recommendations_parsing(
        self, sample_linkedin_export: Path, tmp_path: Path
    ):
        """Test recommendations are parsed correctly."""
        output_dir = tmp_path / "output"

        converter = create_converter(sample_linkedin_export, output_dir)
        converter.convert(lang="en")

        recommendations_file = output_dir / "recommendations.md"
        if recommendations_file.exists():
            content = recommendations_file.read_text()
            assert "exceptional engineer" in content or "Alice" in content

    def test_job_applications_parsing(
        self, sample_linkedin_export: Path, tmp_path: Path
    ):
        """Test job applications are parsed correctly."""
        output_dir = tmp_path / "output"

        converter = create_converter(sample_linkedin_export, output_dir)
        converter.convert(lang="en")

        jobs_file = output_dir / "job_applications.md"
        if jobs_file.exists():
            content = jobs_file.read_text()
            assert "Dream Company" in content or "Staff Engineer" in content

    def test_empty_export(self, tmp_path: Path):
        """Test handling of empty export (minimal valid ZIP)."""
        zip_path = tmp_path / "empty.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_path, "w") as zf:
            # Just an empty Profile.csv
            zf.writestr("Profile.csv", "First Name,Last Name,Headline\n")

        converter = create_converter(zip_path, output_dir)
        converter.convert(lang="en")

        # Should still create output (even if mostly empty)
        assert output_dir.exists()

    def test_unicode_content(self, tmp_path: Path):
        """Test handling of Unicode content."""
        zip_path = tmp_path / "unicode.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_path, "w") as zf:
            unicode_csv = (
                "First Name,Last Name,Headline,Summary\n"
                "José,García,Ingeniero de Software,"
                '"Desarrollador con experiencia en tecnologías emergentes. '
                '日本語テスト. Émoji test: 🚀"'
            )
            zf.writestr("Profile.csv", unicode_csv)
            zf.writestr(
                "Skills.csv",
                """Name
Programación
日本語
C++""",
            )

        converter = create_converter(zip_path, output_dir)
        converter.convert(lang="es")

        profile_content = (output_dir / "profile.md").read_text()
        assert "José García" in profile_content
        assert "🚀" in profile_content or "Desarrollador" in profile_content

    def test_special_characters_in_descriptions(self, tmp_path: Path):
        """Test handling of special Markdown characters."""
        zip_path = tmp_path / "special.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_path, "w") as zf:
            special_csv = (
                "First Name,Last Name,Headline,Summary\n"
                "Test,User,Dev | Architect,"
                "Summary with *bold* and _italic_ and [link](url) and `code`"
            )
            zf.writestr("Profile.csv", special_csv)
            positions_csv = (
                "Company Name,Title,Description,Location,Started On,Finished On\n"
                'Company & Sons,Lead Dev,"• Task with | pipe\n'
                "• Task with * asterisk\n"
                '• Task with < angle > brackets",NYC,2020,'
            )
            zf.writestr("Positions.csv", positions_csv)

        converter = create_converter(zip_path, output_dir)
        converter.convert(lang="en")

        # Should not crash with special characters
        assert output_dir.exists()
        profile_content = (output_dir / "profile.md").read_text()
        assert "Test User" in profile_content

    def test_very_large_description(self, tmp_path: Path):
        """Test handling of very large text content."""
        zip_path = tmp_path / "large.zip"
        output_dir = tmp_path / "output"

        large_text = "A" * 100000  # 100KB of text

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(
                "Profile.csv",
                f"""First Name,Last Name,Headline,Summary
Test,User,Developer,{large_text}""",
            )

        converter = create_converter(zip_path, output_dir)
        converter.convert(lang="en")

        # Should handle large content without issues
        assert output_dir.exists()

    def test_output_directory_creation(
        self, sample_linkedin_export: Path, tmp_path: Path
    ):
        """Test that nested output directories are created."""
        output_dir = tmp_path / "deep" / "nested" / "path" / "output"

        converter = create_converter(sample_linkedin_export, output_dir)
        files = converter.convert(lang="en")

        assert output_dir.exists()
        assert len(files) > 0

    def test_idempotent_conversion(self, sample_linkedin_export: Path, tmp_path: Path):
        """Test that running conversion twice produces same results."""
        output_dir = tmp_path / "output"

        converter = create_converter(sample_linkedin_export, output_dir)

        # First run
        files1 = converter.convert(lang="en")
        content1 = (output_dir / "profile.md").read_text()

        # Second run (overwrite)
        converter2 = create_converter(sample_linkedin_export, output_dir)
        files2 = converter2.convert(lang="en")
        content2 = (output_dir / "profile.md").read_text()

        assert len(files1) == len(files2)
        assert content1 == content2


class TestSecurityE2E:
    """End-to-end security tests."""

    def test_no_path_traversal_in_output(self, tmp_path: Path):
        """Ensure output files are contained within output directory."""
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("Profile.csv", "First Name,Last Name\nTest,User")

        converter = create_converter(zip_path, output_dir)
        files = converter.convert(lang="en")

        # All files should be within output_dir
        for file_path in files:
            assert str(file_path).startswith(str(output_dir))

    def test_csv_with_malicious_content(self, tmp_path: Path):
        """Test handling of potentially malicious CSV content."""
        zip_path = tmp_path / "malicious.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_path, "w") as zf:
            # Content that might try to break CSV parsing
            zf.writestr(
                "Profile.csv",
                '''First Name,Last Name,Headline
"Test","User","Normal headline"
"=CMD|'/C calc'!A0","Injection","Formula injection attempt"
"<script>alert('xss')</script>","XSS","HTML injection"''',
            )

        converter = create_converter(zip_path, output_dir)
        converter.convert(lang="en")

        # Should complete without executing anything malicious
        assert output_dir.exists()

        profile_content = (output_dir / "profile.md").read_text()
        # The content should be treated as plain text, not executed
        assert "Test User" in profile_content

    def test_deeply_nested_zip_paths(self, tmp_path: Path):
        """Test handling of files with deep paths in ZIP."""
        zip_path = tmp_path / "nested.zip"
        output_dir = tmp_path / "output"

        with zipfile.ZipFile(zip_path, "w") as zf:
            # File at root level
            zf.writestr("Profile.csv", "First Name,Last Name\nTest,User")
            # File in subdirectory (should be handled or ignored gracefully)
            zf.writestr("subdir/Skills.csv", "Name\nPython")

        converter = create_converter(zip_path, output_dir)
        converter.convert(lang="en")

        # Should handle without errors
        assert output_dir.exists()
