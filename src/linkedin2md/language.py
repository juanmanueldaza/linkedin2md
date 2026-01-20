"""Language detection implementations.

Single Responsibility: Detect language of text.
"""

import re

from linkedin2md.protocols import BilingualText, LanguageDetector


class SpanishEnglishDetector(LanguageDetector):
    """Detect Spanish vs English text.

    Single Responsibility: Only handles language detection.
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

    def __init__(self):
        self._regex = re.compile("|".join(self.SPANISH_PATTERNS), re.IGNORECASE)

    def detect(self, text: str) -> str:
        """Detect if text is Spanish or English."""
        if not text:
            return "en"

        matches = len(self._regex.findall(text))
        words = len(text.split())

        if words > 0 and matches / words > 0.1:
            return "es"
        return "en"


class BilingualTextFactory:
    """Factory for creating BilingualText objects.

    Single Responsibility: Create bilingual text with language detection.
    Dependency Inversion: Depends on LanguageDetector protocol.
    """

    def __init__(self, detector: LanguageDetector):
        self._detector = detector

    def create(self, text: str, lang: str | None = None) -> BilingualText:
        """Create BilingualText with text in detected/specified language."""
        if not text:
            return BilingualText()

        detected = lang or self._detector.detect(text)

        if detected == "es":
            return BilingualText(es=text)
        return BilingualText(en=text)

    def merge(self, *texts: BilingualText) -> BilingualText:
        """Merge multiple BilingualText objects."""
        en = ""
        es = ""
        for t in texts:
            if t.en and not en:
                en = t.en
            if t.es and not es:
                es = t.es
        return BilingualText(en=en, es=es)


# Default instances
_default_detector = SpanishEnglishDetector()
_default_factory = BilingualTextFactory(_default_detector)


def get_default_detector() -> LanguageDetector:
    """Get the default language detector."""
    return _default_detector


def get_default_factory() -> BilingualTextFactory:
    """Get the default bilingual text factory."""
    return _default_factory
