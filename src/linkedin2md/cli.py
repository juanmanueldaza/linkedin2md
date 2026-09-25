"""CLI for linkedin2md.

Dependency Inversion: Uses factory function, doesn't create dependencies directly.
"""

import argparse
import logging
import sys
from pathlib import Path

from linkedin2md import CONVERSION_CONTRACT, __version__
from linkedin2md.converter import create_converter
from linkedin2md.diagnostics import StrictConversionError, write_report
from linkedin2md.limits import DEFAULT_MAX_ARCHIVE_FILE_SIZE_BYTES, MIB
from linkedin2md.progress import show_progress

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = DEFAULT_MAX_ARCHIVE_FILE_SIZE_BYTES // MIB


def _paths_same(first: Path, second: Path) -> bool:
    try:
        if first.resolve() == second.resolve():
            return True
        return first.samefile(second)
    except OSError:
        return False


def _report_path_conflicts(source: Path, output_dir: Path, report: Path | None) -> bool:
    if report is None:
        return False
    if _paths_same(source, report):
        return True
    if _paths_same(output_dir / "profile.pdf", report):
        return True
    return any(
        _paths_same(output_dir / output_file, report)
        for output_file in CONVERSION_CONTRACT.output_files
    )


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

    if _report_path_conflicts(args.source, args.output, args.report):
        logger.error("Report path must not overwrite the source or generated output")
        return 1

    use_report = (
        getattr(args, "strict", False) or getattr(args, "report", None) is not None
    )
    report = None
    strict_failed = False
    try:
        converter = create_converter(args.source, args.output)
        with show_progress("Extracting and converting export..."):
            if use_report:
                try:
                    result = converter.convert_with_report(
                        lang=args.lang,
                        strict=getattr(args, "strict", False),
                    )
                except StrictConversionError as error:
                    report = error.report
                    files = list(error.files)
                    strict_failed = True
                else:
                    files = list(result.files)
                    report = result.report
            else:
                files = converter.convert(lang=args.lang)
    except Exception as error:
        logger.error("%s", error)
        return 1

    if report is not None and getattr(args, "report", None) is not None:
        try:
            write_report(args.report, report)
        except Exception as error:
            logger.error("Failed to write conversion report: %s", error)
            return 1

    fatal_failed = (
        report is not None and getattr(report, "fatal_error", None) is not None
    )

    if not args.quiet and (files or (not strict_failed and not fatal_failed)):
        print(f"Created {len(files)} files in {args.output}/")
        for file in files:
            print(f"  - {file.name}")

    if strict_failed:
        logger.error("Strict conversion failed")
        return 1

    if fatal_failed:
        logger.error("Conversion failed")
        return 1

    # Step 4: Optional PDF Generation
    if args.pdf:
        from linkedin2md.pdf import assemble_resume_markdown, convert_md_to_pdf

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
                    resume_md_parts.append((section, content))

        if not resume_md_parts:
            logger.warning("No profile sections found to generate PDF.")
            return 1

        pdf_path = args.output / "profile.pdf"
        if not args.quiet:
            print("Generating PDF Resume...")
        resume_markdown = assemble_resume_markdown(resume_md_parts)
        if convert_md_to_pdf(resume_markdown, pdf_path):
            if not args.quiet:
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
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when diagnostics report conversion problems",
    )
    parser.add_argument(
        "--report",
        type=Path,
        metavar="PATH",
        help="Write a private conversion diagnostics JSON report",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress file listing and PDF generation messages",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
