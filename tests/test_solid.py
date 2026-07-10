"""Tests for SOLID-compliant architecture."""

import tempfile
import zipfile
from pathlib import Path

from linkedin2md.converter import (
    LinkedInToMarkdownConverter,
    _TrackingDict,
    create_converter,
)
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
            assert path.read_text(encoding="utf-8") == "# Hello"

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


# =============================================================================
# _TrackingDict Tests
# =============================================================================


class TestTrackingDict:
    """Tests for _TrackingDict (unconsumed-key detection)."""

    def test_tracks_accessed_keys(self):
        """Test that .get() calls record keys in accessed_keys."""
        d = _TrackingDict({"a": 1, "b": 2, "c": 3})
        d.get("a")
        d.get("b")
        assert d.accessed_keys == {"a", "b"}

    def test_unaccessed_keys_not_recorded(self):
        """Test that unaccessed keys are not in accessed_keys."""
        d = _TrackingDict({"a": 1, "b": 2})
        d.get("a")
        assert "b" not in d.accessed_keys

    def test_get_nonexistent_key_still_tracked(self):
        """Test that getting a missing key still records it."""
        d = _TrackingDict({"a": 1})
        result = d.get("missing", "default")
        assert result == "default"
        assert "missing" in d.accessed_keys

    def test_works_with_converter(self):
        """Integration: converter tracks which keys parsers consume."""
        raw_data = {
            "profile": [{"First Name": "John", "Last Name": "Doe", "Headline": "Dev"}],
            "skills": [{"Name": "Python"}],
        }
        tracked = _TrackingDict(raw_data)

        # Simulate what parsers do
        _ = tracked.get("profile", [])
        _ = tracked.get("skills", [])

        unconsumed = set(raw_data.keys()) - tracked.accessed_keys
        assert unconsumed == set()

    def test_detects_unconsumed_keys(self):
        """Test that unconsumed keys are detected."""
        raw_data = {"a": 1, "b": 2, "c": 3}
        tracked = _TrackingDict(raw_data)
        _ = tracked.get("a")
        unconsumed = set(raw_data.keys()) - tracked.accessed_keys
        assert unconsumed == {"b", "c"}


# =============================================================================
# Unconsumed CSV Warning Tests
# =============================================================================


class TestConverterUnconsumedKeys:
    """Integration test: converter warns about unconsumed CSV keys."""

    def test_warns_on_unconsumed_keys(self, caplog):
        """Test that CSV files without parsers trigger WARNING."""
        import logging

        caplog.set_level(logging.WARNING)

        raw_data = {
            "profile": [{"First Name": "Test", "Last Name": "User", "Headline": ""}],
            "unknown_csv_1": [{"Col": "val"}],
            "unknown_csv_2": [{"Col": "val"}],
        }

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
        converter.convert(lang="en")

        assert any("unknown_csv_1" in msg for msg in caplog.messages)
        assert any("unknown_csv_2" in msg for msg in caplog.messages)
        assert not any("profile" in msg for msg in caplog.messages)

    def test_known_empty_keys_not_warned(self, caplog):
        """Known-empty CSV keys do not trigger WARNING."""
        import logging

        caplog.set_level(logging.WARNING)

        raw_data = {
            "profile": [{"First Name": "Test", "Last Name": "User", "Headline": ""}],
            "guide_messages": [],
            "learning_coach_messages": [],
            "learningcoachmessages": [],
        }

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
        converter.convert(lang="en")

        assert not any("guide_messages" in msg for msg in caplog.messages)
        assert not any("learning_coach_messages" in msg for msg in caplog.messages)
        assert not any("learningcoachmessages" in msg for msg in caplog.messages)


# =============================================================================
# _get_csv Prefix Matching Tests
# =============================================================================


class _TestParser:  # Concrete subclass of BaseParser for testing _get_csv
    """Minimal test helper that exposes _get_csv."""

    def _get_csv(self, raw_data: dict, key: str) -> list:
        from linkedin2md.parsers.base import BaseParser  # noqa: E402

        # BaseParser._get_csv is a regular method; we call it via delegation.
        return BaseParser._get_csv(self, raw_data, key)  # type: ignore[arg-type]


class TestGetCsvPrefixMatch:
    """Tests for _get_csv prefix-matching fallback."""

    def test_exact_match_returns_directly(self):
        """Exact key match returns data without prefix fallback."""
        helper = _TestParser()
        result = helper._get_csv({"shares": [{"a": 1}]}, "shares")
        assert result == [{"a": 1}]

    def test_suffix_match_returns_data(self):
        """Suffixed key (key_NUMBER) is found via prefix match."""
        helper = _TestParser()
        result = helper._get_csv({"shares_12345": [{"a": 1}]}, "shares")
        assert result == [{"a": 1}]

    def test_no_match_returns_empty(self):
        """No matching key returns empty list."""
        helper = _TestParser()
        result = helper._get_csv({"other": [{"a": 1}]}, "shares")
        assert result == []

    def test_non_numeric_suffix_not_matched(self):
        """Non-numeric suffix does NOT trigger prefix match."""
        helper = _TestParser()
        result = helper._get_csv({"shares_extra": [{"a": 1}]}, "shares")
        assert result == []

    def test_exact_precedence_over_suffix(self):
        """Exact match takes precedence when both exist."""
        helper = _TestParser()
        result = helper._get_csv(
            {"shares": [{"exact": True}], "shares_12345": [{"suffix": True}]},
            "shares",
        )
        assert result == [{"exact": True}]

    def test_suffix_path_tracks_via_tracking_dict(self):
        """Prefix match path records both looked-up keys via _get()."""
        from linkedin2md.converter import _TrackingDict

        helper = _TestParser()
        raw = _TrackingDict({"shares_12345": [{"a": 1}]})
        result = helper._get_csv(raw, "shares")
        assert result == [{"a": 1}]
        # Exact-key lookup (miss) + suffixed-key lookup (hit)
        assert "shares" in raw.accessed_keys
        assert "shares_12345" in raw.accessed_keys
