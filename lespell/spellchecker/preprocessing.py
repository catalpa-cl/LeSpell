"""Preprocessing components for spelling correction."""

import os
import re
from typing import Optional

from lespell.spellchecker.annotations import Annotation, Text


class PreprocessingPipeline:
    """Preprocessing pipeline components."""

    @staticmethod
    def mark_numerics(text: Text) -> Text:
        """Tag numeric tokens to exclude from spell checking."""
        numeric_pattern = re.compile(
            r"[:0-9\-\+\*\.,=x/\\]*[0-9]+[:0-9\-\+\*\.,=x/\\]*"
        )

        tokens = text.get_tokens()
        for start, end, token in tokens:
            if numeric_pattern.fullmatch(token):
                text.add_annotation(
                    Annotation(
                        type="numeric",
                        start=start,
                        end=end,
                        metadata={"token": token},
                    )
                )

        return text

    @staticmethod
    def mark_punctuation(text: Text) -> Text:
        """Tag punctuation tokens to exclude from spell checking."""
        tokens = text.get_tokens()
        for start, end, token in tokens:
            if len(token) > 0 and all(not c.isalnum() for c in token):
                text.add_annotation(
                    Annotation(
                        type="punctuation",
                        start=start,
                        end=end,
                        metadata={"token": token},
                    )
                )

        return text

    @staticmethod
    def mark_capitalized_words(text: Text) -> Text:
        """Mark possibly capitalized (proper nouns, sentence starts)."""
        tokens = text.get_tokens()
        for start, end, token in tokens:
            if token and token[0].isupper():
                text.add_annotation(
                    Annotation(
                        type="capitalized",
                        start=start,
                        end=end,
                        metadata={"token": token},
                    )
                )

        return text

    @staticmethod
    def check_dictionary(text: Text, dictionary_path: str) -> Text:
        """Mark tokens that appear in dictionary."""
        if not os.path.exists(dictionary_path):
            raise FileNotFoundError(f"Dictionary not found: {dictionary_path}")

        with open(dictionary_path, "r", encoding="utf-8") as f:
            dictionary = set(
                line.strip().lower() for line in f if line.strip()
            )

        tokens = text.get_tokens()
        for start, end, token in tokens:
            if token.lower() in dictionary:
                text.add_annotation(
                    Annotation(
                        type="known_word",
                        start=start,
                        end=end,
                        metadata={"token": token},
                    )
                )

        return text

    @staticmethod
    def check_hunspell(
        text: Text,
        dic_path: Optional[str] = None,
        aff_path: Optional[str] = None,
        language: str = "en",
    ) -> Text:
        """Mark tokens that pass Hunspell check."""
        try:
            import hunspell

            if dic_path and aff_path:
                spell = hunspell.HunSpell(dic_path, aff_path)
            else:
                spell = hunspell.HunSpell(language)

            tokens = text.get_tokens()
            for start, end, token in tokens:
                if spell.spell(token):
                    text.add_annotation(
                        Annotation(
                            type="known_word",
                            start=start,
                            end=end,
                            metadata={"token": token, "checker": "hunspell"},
                        )
                    )

        except ImportError:
            # TODO: Implement fallback dictionary check if Hunspell unavailable
            pass

        return text




class SimplePreprocessor:
    """Simple preprocessing pipeline."""

    def __init__(
        self,
        dictionary_path: Optional[str] = None,
        use_hunspell: bool = False,
        hunspell_dic: Optional[str] = None,
        hunspell_aff: Optional[str] = None,
        language: str = "en",
    ):
        self.dictionary_path = dictionary_path
        self.use_hunspell = use_hunspell
        self.hunspell_dic = hunspell_dic
        self.hunspell_aff = hunspell_aff
        self.language = language

    def preprocess(self, text: Text) -> Text:
        """Run preprocessing pipeline (tokenization and classification only).

        Does NOT mark spelling errors - that's the ErrorDetector's responsibility.
        """
        # Mark special token types
        text = PreprocessingPipeline.mark_numerics(text)
        text = PreprocessingPipeline.mark_punctuation(text)
        text = PreprocessingPipeline.mark_capitalized_words(text)

        # Check word validity (mark known words)
        if self.use_hunspell:
            text = PreprocessingPipeline.check_hunspell(
                text, self.hunspell_dic, self.hunspell_aff, self.language
            )
        elif self.dictionary_path:
            text = PreprocessingPipeline.check_dictionary(text, self.dictionary_path)

        return text

