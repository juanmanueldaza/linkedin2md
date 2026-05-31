"""CLI for linkedin2md.

Dependency Inversion: Uses factory function, doesn't create dependencies directly.
"""

import argparse
import logging
import sys
from pathlib import Path

from linkedin2md import __version__
from linkedin2md.converter import create_converter
from linkedin2md.progress import show_progress

logger = logging.getLogger(__name__)

# Maximum allowed file size in megabytes (500 MB)
MAX_FILE_SIZE_MB = 500


def main() -> int:
    """Main entry point."""
    # Configure logging for CLI use
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    args = _parse_args(sys.argv[1:])

    if not args.source.exists():
        logger.error("File not found: %s", args.source)
        return 1

    if not args.source.suffix.lower() == ".zip":
        logger.error("Expected .zip file, got %s", args.source.suffix)
        return 1

    # Check file size to prevent resource exhaustion
    file_size_mb = args.source.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        logger.error(
            "File too large (%.1f MB). Maximum allowed is %d MB",
            file_size_mb,
            MAX_FILE_SIZE_MB,
        )
        return 1

    try:
        # Use factory to create converter with all dependencies
        converter = create_converter(args.source, args.output)
        with show_progress("Extracting and converting export..."):
            files = converter.convert(lang=args.lang)
    except Exception as e:
        logger.error("%s", e)
        return 1

    # Success messages go to stdout (user-facing output)
    print(f"Created {len(files)} files in {args.output}/")
    for f in files:
        print(f"  - {f.name}")

    # Step 4: Optional PDF Generation
    if args.pdf:
        from linkedin2md.pdf import convert_md_to_pdf

        # Sections to include in the resume PDF, in order
        resume_sections = [
            "profile",
            "experience",
            "education",
            "certifications",
            "skills",
            "languages",
            "projects",
        ]

        resume_md_parts = []
        for section in resume_sections:
            section_path = args.output / f"{section}.md"
            if section_path.exists():
                content = section_path.read_text(encoding="utf-8").strip()
                if content:
                    resume_md_parts.append(content)

        if not resume_md_parts:
            logger.warning("No profile sections found to generate PDF.")
            return 1

        pdf_path = args.output / "profile.pdf"
        print("Generating PDF Resume...")
        if convert_md_to_pdf("\n\n".join(resume_md_parts), pdf_path):
            print(f"Created PDF Resume: {pdf_path}")
        else:
            logger.error("Failed to generate PDF Resume.")
            return 1

    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="linkedin2md",
        description="Convert LinkedIn data exports to Markdown",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="LinkedIn ZIP export file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("linkedin_export"),
        help="Output directory (default: linkedin_export)",
    )
    parser.add_argument(
        "--lang",
        choices=["en", "es"],
        default="en",
        help="Output language (default: en)",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate an elegant A4 PDF resume from your profile",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
