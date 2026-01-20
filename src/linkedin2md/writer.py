"""Output writer implementations.

Single Responsibility: Write formatted content to files.
"""

from pathlib import Path

from linkedin2md.protocols import OutputWriter


class MarkdownFileWriter(OutputWriter):
    """Write Markdown content to files.

    Single Responsibility: Only handles file I/O.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, filename: str, content: str) -> Path:
        """Write content to a Markdown file.

        Raises:
            ValueError: If filename contains path traversal sequences.
        """
        # Defensive validation against path traversal
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            raise ValueError(f"Invalid filename: {filename}")

        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        path = self.output_dir / filename
        path.write_text(content, encoding="utf-8")
        return path


class InMemoryWriter(OutputWriter):
    """Write content to memory (for testing).

    Single Responsibility: Store output in memory.
    """

    def __init__(self):
        self.files: dict[str, str] = {}

    def write(self, filename: str, content: str) -> Path:
        """Store content in memory."""
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        self.files[filename] = content
        return Path(filename)
