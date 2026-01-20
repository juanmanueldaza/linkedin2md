"""CLI for linkedin2md.

Dependency Inversion: Uses factory function, doesn't create dependencies directly.
"""

import argparse
import sys
from pathlib import Path

from linkedin2md.converter import create_converter

# Maximum allowed file size in megabytes (500 MB)
MAX_FILE_SIZE_MB = 500


def main() -> int:
    """Main entry point."""
    args = _parse_args(sys.argv[1:])

    if not args.source.exists():
        print(f"Error: File not found: {args.source}", file=sys.stderr)
        return 1

    if not args.source.suffix.lower() == ".zip":
        print(f"Error: Expected .zip file, got {args.source.suffix}", file=sys.stderr)
        return 1

    # Check file size to prevent resource exhaustion
    file_size_mb = args.source.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(
            f"Error: File too large ({file_size_mb:.1f} MB). "
            f"Maximum allowed is {MAX_FILE_SIZE_MB} MB",
            file=sys.stderr,
        )
        return 1

    try:
        # Use factory to create converter with all dependencies
        converter = create_converter(args.source, args.output)
        files = converter.convert(lang=args.lang)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Created {len(files)} files in {args.output}/")
    for f in files:
        print(f"  - {f.name}")

    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="linkedin2md",
        description="Convert LinkedIn data exports to Markdown",
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
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
