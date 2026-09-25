"""Output writer implementations.

Single Responsibility: Write formatted content to files.
"""

import os
import tempfile
from pathlib import Path, PureWindowsPath

from linkedin2md.limits import DEFAULT_MAX_OUTPUT_BYTES, OutputLimitError
from linkedin2md.protocols import OutputWriter


class MarkdownFileWriter(OutputWriter):
    """Write Markdown content atomically with private permissions."""

    def __init__(
        self,
        output_dir: Path,
        max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
    ):
        if max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be positive")
        if output_dir.is_symlink():
            raise ValueError("Output directory must not be a symlink")

        self.output_dir = output_dir
        self.max_output_bytes = max_output_bytes
        created = not self.output_dir.exists()
        self.output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        if created:
            os.chmod(self.output_dir, 0o700)

    def write(self, filename: str, content: str) -> Path:
        """Write content to a Markdown file atomically."""
        self._validate_filename(filename)
        encoded_size = len(content.encode("utf-8"))
        if encoded_size > self.max_output_bytes:
            raise OutputLimitError(
                f"Output content is too large: {encoded_size} bytes, "
                f"max {self.max_output_bytes}"
            )

        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        path = self.output_dir / filename
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=self.output_dir,
                prefix=f".{path.name}.",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(content)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, path)
            os.chmod(path, 0o600)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

        return path

    def _validate_filename(self, filename: str) -> None:
        if not filename or "\x00" in filename:
            raise ValueError(f"Invalid filename: {filename}")
        if "/" in filename or "\\" in filename:
            raise ValueError(f"Invalid filename: {filename}")
        path = Path(filename)
        windows_path = PureWindowsPath(filename)
        if (
            path.is_absolute()
            or windows_path.drive
            or windows_path.is_absolute()
            or path.name != filename
            or ".." in path.parts
        ):
            raise ValueError(f"Invalid filename: {filename}")


class InMemoryWriter(OutputWriter):
    """Write content to memory (for testing)."""

    def __init__(self):
        self.files: dict[str, str] = {}

    def write(self, filename: str, content: str) -> Path:
        """Store content in memory."""
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        self.files[filename] = content
        return Path(filename)
