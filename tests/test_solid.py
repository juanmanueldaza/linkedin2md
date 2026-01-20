"""Tests for SOLID-compliant architecture."""

import tempfile
import zipfile
from pathlib import Path

from linkedin2md.converter import LinkedInToMarkdownConverter, create_converter
from linkedin2md.extractor import DictDataExtractor, ZipDataExtractor
from linkedin2md.language import BilingualTextFactory, SpanishEnglishDetector
from linkedin2md.protocols import BilingualText
from linkedin2md.registry import DefaultFormatterRegistry, DefaultParserRegistry
from linkedin2md.writer import InMemoryWriter, MarkdownFileWriter

# =============================================================================
# Protocol Tests
# =============================================================================


class TestBilingualText:
    """Tests for BilingualText immutable container."""

    def test_create_empty(self):
        text = BilingualText()
        assert text.en == ""
        assert text.es == ""

    def test_create_with_values(self):
        text = BilingualText(en="Hello", es="Hola")
        assert text.en == "Hello"
        assert text.es == "Hola"

    def test_get_preferred_language(self):
        text = BilingualText(en="Hello", es="Hola")
        assert text.get("en") == "Hello"
        assert text.get("es") == "Hola"

    def test_get_fallback(self):
        text = BilingualText(en="Hello", es="")
        assert text.get("es") == "Hello"  # Falls back to en

    def test_immutable(self):
        text = BilingualText(en="Hello")
        try:
            # Use setattr to bypass static type checking while testing runtime behavior
            setattr(text, "en", "Changed")  # noqa: B010
            raise AssertionError("Should have raised AttributeError")
        except AttributeError:
            pass


# =============================================================================
# Language Detection Tests
# =============================================================================


class TestSpanishEnglishDetector:
    """Tests for language detection."""

    def test_detect_english(self):
        detector = SpanishEnglishDetector()
        assert detector.detect("I am a software engineer") == "en"

    def test_detect_spanish(self):
        detector = SpanishEnglishDetector()
        assert detector.detect("Soy un desarrollador de software") == "es"

    def test_detect_empty(self):
        detector = SpanishEnglishDetector()
        assert detector.detect("") == "en"


class TestBilingualTextFactory:
    """Tests for bilingual text factory."""

    def test_create_english(self):
        detector = SpanishEnglishDetector()
        factory = BilingualTextFactory(detector)
        text = factory.create("Hello world")
        assert text.en == "Hello world"
        assert text.es == ""

    def test_create_spanish(self):
        detector = SpanishEnglishDetector()
        factory = BilingualTextFactory(detector)
        text = factory.create("Soy un desarrollador de software con experiencia")
        assert text.es == "Soy un desarrollador de software con experiencia"
        assert text.en == ""

    def test_create_with_explicit_lang(self):
        detector = SpanishEnglishDetector()
        factory = BilingualTextFactory(detector)
        text = factory.create("Test", lang="es")
        assert text.es == "Test"
        assert text.en == ""


# =============================================================================
# Extractor Tests
# =============================================================================


class TestZipDataExtractor:
    """Tests for ZIP data extraction."""

    def test_extract_csvs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "test.zip"

            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("Profile.csv", "First Name,Last Name\nJohn,Doe")
                zf.writestr("Skills.csv", "Name\nPython\nJava")

            extractor = ZipDataExtractor(zip_path)
            data = extractor.extract()

            assert "profile" in data
            assert len(data["profile"]) == 1
            assert data["profile"][0]["First Name"] == "John"

            assert "skills" in data
            assert len(data["skills"]) == 2


class TestDictDataExtractor:
    """Tests for dict data extractor (testing helper)."""

    def test_extract_returns_data(self):
        test_data = {"profile": [{"name": "Test"}]}
        extractor = DictDataExtractor(test_data)
        assert extractor.extract() == test_data


# =============================================================================
# Writer Tests
# =============================================================================


class TestMarkdownFileWriter:
    """Tests for file writer."""

    def test_write_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("test", "# Hello")

            assert path.exists()
            assert path.name == "test.md"
            assert path.read_text() == "# Hello"

    def test_write_adds_md_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = MarkdownFileWriter(Path(tmpdir))
            path = writer.write("test", "content")
            assert path.suffix == ".md"


class TestInMemoryWriter:
    """Tests for in-memory writer (testing helper)."""

    def test_write_stores_content(self):
        writer = InMemoryWriter()
        writer.write("test", "# Hello")

        assert "test.md" in writer.files
        assert writer.files["test.md"] == "# Hello"


# =============================================================================
# Registry Tests
# =============================================================================


class TestParserRegistry:
    """Tests for parser registry."""

    def test_register_and_get_all(self):
        registry = DefaultParserRegistry()

        class MockParser:
            section_key = "test"

            def parse(self, raw_data: dict[str, list[dict]]) -> list:
                return []

        parser = MockParser()
        registry.register(parser)

        assert parser in registry.get_all()


class TestFormatterRegistry:
    """Tests for formatter registry."""

    def test_register_and_get(self):
        registry = DefaultFormatterRegistry()

        class MockFormatter:
            section_key = "test"

            def format(self, data, lang):
                return ""

        formatter = MockFormatter()
        registry.register(formatter)

        assert registry.get("test") == formatter
        assert registry.get("nonexistent") is None


# =============================================================================
# Integration Tests
# =============================================================================


class TestLinkedInToMarkdownConverter:
    """Integration tests for the main converter."""

    def test_convert_minimal_data(self):
        # Setup test data
        raw_data = {
            "profile": [
                {"First Name": "John", "Last Name": "Doe", "Headline": "Engineer"}
            ],
            "skills": [{"Name": "Python"}, {"Name": "Go"}],
        }

        # Create converter with test dependencies
        # Trigger registration of parsers and formatters
        import linkedin2md.formatters  # noqa: F401
        import linkedin2md.parsers  # noqa: F401
        from linkedin2md.registry import get_formatter_registry, get_parser_registry

        extractor = DictDataExtractor(raw_data)
        writer = InMemoryWriter()

        converter = LinkedInToMarkdownConverter(
            extractor=extractor,
            parser_registry=get_parser_registry(),
            formatter_registry=get_formatter_registry(),
            writer=writer,
        )

        files = converter.convert(lang="en")

        # Should create profile.md and skills.md at minimum
        assert len(files) >= 2
        assert "profile.md" in writer.files
        assert "skills.md" in writer.files
        assert "John Doe" in writer.files["profile.md"]
        assert "Python" in writer.files["skills.md"]


class TestCreateConverter:
    """Tests for the factory function."""

    def test_create_converter_from_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test ZIP
            zip_path = Path(tmpdir) / "test.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("Profile.csv", "First Name,Last Name\nTest,User")

            output_dir = Path(tmpdir) / "output"

            converter = create_converter(zip_path, output_dir)
            assert isinstance(converter, LinkedInToMarkdownConverter)

            files = converter.convert()
            assert output_dir.exists()
            assert len(files) >= 1
