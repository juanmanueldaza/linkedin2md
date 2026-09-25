"""Contract and baseline export tests."""

import zipfile
from pathlib import Path

import pytest

from linkedin2md.contract import CONVERSION_CONTRACT
from linkedin2md.converter import create_converter

BASELINE_CSV_FILES = {
    "Profile.csv": (
        "First Name,Last Name,Headline,Summary,Industry,Geo Location,"
        "Twitter Handles,Websites,Birth Date\n"
        "Ada,Lovelace,Analytical Engine Programmer,"
        "Built the first algorithm intended for a machine.,"
        "Technology,London,[@adalovelace],https://example.com,1815-12-10\n"
    ),
    "Email Addresses.csv": (
        "Email Address,Confirmed,Primary,Updated On\n"
        "ada@example.com,Yes,Yes,2024-01-01\n"
    ),
    "PhoneNumbers.csv": "Number,Type\n+44-20-0000-0000,Mobile\n",
    "Skills.csv": "Name\nPython\nMathematics\n",
    "Positions.csv": (
        "Company Name,Title,Description,Location,Started On,Finished On\n"
        "Analytical Society,Programmer,"
        '"• Designed algorithms\\n• Wrote technical notes",'
        "London,1840-01-01,1852-01-01\n"
    ),
    "Education.csv": (
        "School Name,Degree Name,Start Date,End Date,Notes,Activities\n"
        "University of London,Mathematics,1830-09-01,1834-06-30,"
        "Independent study,Mathematics Society\n"
    ),
    "Connections.csv": (
        "Notes:\n"
        '"Connection export metadata"\n'
        "\n"
        "First Name,Last Name,URL,Email Address,Company,Position,Connected On\n"
        "Charles,Babbage,https://example.com/charlie,charles@example.com,"
        "Analytical Society,Mathematician,2024-02-01\n"
    ),
    "Recommendations Received.csv": (
        "First Name,Last Name,Company,Job Title,Text,Creation Date,Status\n"
        "George,Boole,Analytical Society,Mathematician,"
        "Ada demonstrated exceptional rigor.,01/15/24,VISIBLE\n"
    ),
    "Endorsement Received Info.csv": (
        "Skill Name,Endorser First Name,Endorser Last Name,"
        "Endorsement Date,Endorsement Status\n"
        "Mathematics,George,Boole,2024/01/15,ACCEPTED\n"
    ),
    "Learning.csv": (
        "Content Title,Content Type,Content Last Watched Date (if viewed),"
        "Content Completed At (if completed)\n"
        "Algorithms,COURSE,2024-03-01,2024-03-15\n"
    ),
    "Job Applications.csv": (
        "Application Date,Company Name,Job Title,Job Url,Status,Withdraw Date,"
        "Resume Name\n"
        "2024-04-01,Analytical Society,Programmer,https://example.com/job,"
        "Applied,,resume.pdf\n"
    ),
    "SearchQueries.csv": "Time,Search Query\n2024-04-02,computational machines\n",
    "Shares.csv": (
        "Date,ShareLink,ShareCommentary\n"
        "2024-04-03,https://example.com/post,Interesting historical patterns.\n"
    ),
    "Groups.csv": (
        "Group Name,Group URL\nHistory of Computing,https://example.com/group\n"
    ),
    "Contact Settings.csv": "Setting,Value\nEmail,on\n",
    "Registration.csv": "Registered At,Ip Address\n2015-03-20,192.0.2.1\n",
}

EXPECTED_BASELINE_OUTPUTS = {
    "profile.md",
    "skills.md",
    "experience.md",
    "education.md",
    "connections.md",
    "recommendations.md",
    "endorsements.md",
    "learning.md",
    "job_applications.md",
    "job_descriptions.md",
    "search_queries.md",
    "posts.md",
    "groups.md",
    "contact_settings.md",
}


@pytest.fixture
def baseline_export(tmp_path: Path) -> Path:
    """Create a sanitized export fixture for contract-level conversion."""
    zip_path = tmp_path / "baseline-export.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for name, content in BASELINE_CSV_FILES.items():
            archive.writestr(name, content)
    return zip_path


def test_contract_matches_runtime_registries(tmp_path: Path) -> None:
    """Keep the declarative contract synchronized with registrations."""
    converter = create_converter(tmp_path / "missing.zip", tmp_path / "output")

    CONVERSION_CONTRACT.validate_registries(
        (parser.section_key for parser in converter._parsers.get_all()),
        (formatter.section_key for formatter in converter._formatters.get_all()),
    )


def test_contract_declares_complete_unique_output_surface() -> None:
    """Validate the release contract's output and source metadata."""
    output_files = CONVERSION_CONTRACT.output_files
    parser_keys = CONVERSION_CONTRACT.parser_keys
    formatter_keys = CONVERSION_CONTRACT.formatter_keys

    assert CONVERSION_CONTRACT.format_version == 1
    assert CONVERSION_CONTRACT.default_language == "en"
    assert CONVERSION_CONTRACT.supported_languages == ("en", "es")
    assert len(output_files) == 65
    assert len(set(output_files)) == len(output_files)
    assert all(name.endswith(".md") for name in output_files)
    assert len(set(parser_keys)) == len(parser_keys)
    assert len(set(formatter_keys)) == len(formatter_keys)
    assert all(spec.source_keys for spec in CONVERSION_CONTRACT.sections)
    assert all(
        component.profile_component and component.formatter is None
        for component in CONVERSION_CONTRACT.profile_components
    )


def test_baseline_export_matches_declared_outputs(
    baseline_export: Path, tmp_path: Path
) -> None:
    """Convert the sanitized baseline and keep output names within contract."""
    output_dir = tmp_path / "output"
    files = create_converter(baseline_export, output_dir).convert(lang="en")
    output_names = {path.name for path in files}

    assert EXPECTED_BASELINE_OUTPUTS <= output_names
    assert output_names <= set(CONVERSION_CONTRACT.output_files)
    assert (
        (output_dir / "profile.md")
        .read_text(encoding="utf-8")
        .startswith("# Ada Lovelace")
    )
    assert "Python" in (output_dir / "skills.md").read_text(encoding="utf-8")
    assert "Built the first algorithm" in (output_dir / "profile.md").read_text(
        encoding="utf-8"
    )
