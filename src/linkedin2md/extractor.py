"""Data extraction implementations.

Single Responsibility: Extract raw data from sources.
"""

import csv
import io
import zipfile
from pathlib import Path

from linkedin2md.protocols import DataExtractor


class ZipDataExtractor(DataExtractor):
    """Extract CSV data from LinkedIn ZIP export.

    Single Responsibility: Only handles ZIP I/O and CSV parsing.
    Does NOT transform or interpret the data.
    """

    def __init__(self, zip_path: Path | str):
        self.zip_path = Path(zip_path)

    def extract(self) -> dict[str, list[dict]]:
        """Extract all CSVs from ZIP into raw dict format.

        Raises:
            ValueError: If the ZIP file is invalid or corrupted.
        """
        data: dict[str, list[dict]] = {}

        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                for name in zf.namelist():
                    if name.endswith(".csv"):
                        with zf.open(name) as f:
                            content = f.read().decode("utf-8")
                            content = self._skip_header_notes(content)
                            reader = csv.DictReader(io.StringIO(content))
                            key = Path(name).stem.lower().replace(" ", "_")
                            data[key] = list(reader)
        except zipfile.BadZipFile as err:
            raise ValueError(f"Invalid or corrupted ZIP file: {self.zip_path}") from err

        return data

    def _skip_header_notes(self, content: str) -> str:
        """Skip header notes in LinkedIn CSVs.

        Some files like Connections.csv start with:
        Notes:
        "When exporting your connection data..."

        First Name,Last Name,URL,...
        """
        lines = content.split("\n")

        if lines and lines[0].strip().startswith("Notes"):
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    continue
                if "," in stripped and not stripped.startswith('"'):
                    return "\n".join(lines[i:])

        return content


class DictDataExtractor(DataExtractor):
    """Extract data from a pre-loaded dict (for testing).

    Single Responsibility: Wraps existing data in extractor interface.
    """

    def __init__(self, data: dict[str, list[dict]]):
        self._data = data

    def extract(self) -> dict[str, list[dict]]:
        """Return the pre-loaded data."""
        return self._data
