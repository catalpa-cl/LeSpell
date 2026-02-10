"""Preprocessing components for spelling correction."""

from typing import Dict, Optional, Set
import os
import re

from lespell.spellchecker.annotations import Text, Annotation


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

    @staticmethod
    def mark_errors(text: Text) -> Text:
        """Mark tokens that should be corrected.

        A token is an error if:
        - It's a valid token (word pattern)
        - It's NOT marked as known_word
        - It's NOT marked as numeric
        - It's NOT marked as punctuation
        """
        word_pattern = re.compile(r"^[a-zA-Z\'-]+$")
        tokens = text.get_tokens()

        for start, end, token in tokens:
            if not word_pattern.match(token):
                continue  # Not a word

            # Check if marked as known or excluded
            overlapping = text.get_overlapping_annotations(start, end)
            if any(
                a.type in {"known_word", "numeric", "punctuation"}
                for a in overlapping
            ):
                continue  # Word is known or excluded

            # Mark as spelling error
            text.add_annotation(
                Annotation(
                    type="spelling_error",
                    start=start,
                    end=end,
                    metadata={"token": token},
                )
            )

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
        """Run full preprocessing pipeline."""
        # Mark special token types
        text = PreprocessingPipeline.mark_numerics(text)
        text = PreprocessingPipeline.mark_punctuation(text)
        text = PreprocessingPipeline.mark_capitalized_words(text)

        # Check word validity
        if self.use_hunspell:
            text = PreprocessingPipeline.check_hunspell(
                text, self.hunspell_dic, self.hunspell_aff, self.language
            )
        elif self.dictionary_path:
            text = PreprocessingPipeline.check_dictionary(text, self.dictionary_path)

        # Mark spelling errors
        text = PreprocessingPipeline.mark_errors(text)

        return text
