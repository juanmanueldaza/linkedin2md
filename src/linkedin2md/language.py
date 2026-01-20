"""Language detection implementations.

Single Responsibility: Detect language of text.
"""

import re

from linkedin2md.protocols import LanguageDetector, MultilingualText

# Backward compatibility alias
BilingualText = MultilingualText


class SpanishEnglishDetector(LanguageDetector):
    """Detect Spanish vs English text.

    Single Responsibility: Only handles language detection.
    Extensible: Implement LanguageDetector protocol for other languages.
    """

    # Spanish language detection patterns
    SPANISH_PATTERNS = [
        r"\b(el|la|los|las|un|una|unos|unas)\b",  # Articles
        r"\b(de|del|en|con|por|para|sobre|entre)\b",  # Prepositions
        r"\b(que|como|donde|cuando|quien)\b",  # Conjunctions
        r"\b(es|son|fue|fueron|está|están)\b",  # Verbs
        r"\b(muy|más|también|además|durante)\b",  # Adverbs
        r"[áéíóúñ¿¡]",  # Spanish characters
    ]

    def __init__(self) -> None:
        self._regex = re.compile("|".join(self.SPANISH_PATTERNS), re.IGNORECASE)

    @property
    def supported_languages(self) -> list[str]:
        """Return list of detectable language codes."""
        return ["en", "es"]

    def detect(self, text: str) -> str:
        """Detect if text is Spanish or English."""
        if not text:
            return "en"

        matches = len(self._regex.findall(text))
        words = len(text.split())

        if words > 0 and matches / words > 0.1:
            return "es"
        return "en"


class MultilingualTextFactory:
    """Factory for creating MultilingualText objects.

    Single Responsibility: Create multilingual text with language detection.
    Dependency Inversion: Depends on LanguageDetector protocol.
    """

    def __init__(self, detector: LanguageDetector):
        self._detector = detector

    def create(self, text: str, lang: str | None = None) -> MultilingualText:
        """Create MultilingualText with text in detected/specified language."""
        if not text:
            return MultilingualText()

        detected = lang or self._detector.detect(text)
        return MultilingualText(**{detected: text})

    def merge(self, *texts: MultilingualText) -> MultilingualText:
        """Merge multiple MultilingualText objects.

        First non-empty value for each language wins.
        """
        merged: dict[str, str] = {}
        for t in texts:
            for lang in t.languages:
                if lang not in merged:
                    merged[lang] = t.get(lang)
        return MultilingualText(**merged)


# Backward compatibility alias
BilingualTextFactory = MultilingualTextFactory


# Default instances
_default_detector = SpanishEnglishDetector()
_default_factory = BilingualTextFactory(_default_detector)


def get_default_detector() -> LanguageDetector:
    """Get the default language detector."""
    return _default_detector


def get_default_factory() -> BilingualTextFactory:
    """Get the default bilingual text factory."""
    return _default_factory
