"""Candidate generation strategies for spelling correction."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Tuple
import os

from lespell.spellchecker.annotations import Text, Annotation


class CandidateGenerator(ABC):
    """Abstract base class for candidate generators."""

    def __init__(self, language: str = "en"):
        self.language = language

    @abstractmethod
    def generate(
        self, misspelled: str, context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Generate spelling correction candidates.

        Args:
            misspelled: Misspelled word
            context: Optional surrounding context

        Returns:
            List of (correction, cost) tuples, ordered by cost (ascending)
        """
        pass

    def get_top_candidates(
        self, misspelled: str, k: int = 3, context: Optional[str] = None
    ) -> List[str]:
        """Get top-k candidates."""
        candidates = self.generate(misspelled, context)
        return [word for word, _ in candidates[:k]]


class HunspellCandidateGenerator(CandidateGenerator):
    """Generate candidates using Hunspell dictionary."""

    def __init__(
        self,
        language: str = "en",
        dic_path: Optional[str] = None,
        aff_path: Optional[str] = None,
    ):
        super().__init__(language)
        self.dic_path = dic_path
        self.aff_path = aff_path
        self.hunspell = None

        try:
            import hunspell

            if dic_path and aff_path:
                self.hunspell = hunspell.HunSpell(dic_path, aff_path)
            else:
                # Try to use system hunspell
                self.hunspell = hunspell.HunSpell(language)
        except (ImportError, Exception) as e:
            raise ImportError(
                f"Hunspell candidate generator requires hunspell library. "
                f"Install with: pip install hunspell. Error: {e}"
            )

    def generate(
        self, misspelled: str, context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Generate candidates using Hunspell."""
        if not self.hunspell:
            return []

        suggestions = self.hunspell.suggest(misspelled)
        # All suggestions get same cost (Hunspell internal ranking)
        return [(word, 1.0) for word in suggestions]


class LevenshteinCandidateGenerator(CandidateGenerator):
    """Generate candidates using grapheme-level Levenshtein distance.

    Supports custom edit operation costs.
    REQUIRES a dictionary to function.
    """

    def __init__(
        self,
        language: str = "en",
        dictionary_path: Optional[str] = None,
        dictionary: Optional[Set[str]] = None,
        deletion_weight: float = 1.0,
        insertion_weight: float = 1.0,
        substitution_weight: float = 1.0,
        transposition_weight: float = 1.0,
        default_weight: float = 1.0,
        max_candidates: int = 10,
    ):
        """Initialize Levenshtein candidate generator.
        
        Args:
            language: Language code (default: 'en')
            dictionary_path: Path to dictionary file (one word per line)
            dictionary: Pre-loaded dictionary as set of words
            deletion_weight: Cost of character deletion
            insertion_weight: Cost of character insertion
            substitution_weight: Cost of character substitution
            transposition_weight: Cost of character transposition
            default_weight: Default edit operation cost
            max_candidates: Maximum number of suggestions to return
            
        Raises:
            ValueError: If neither dictionary_path nor dictionary is provided
        """
        super().__init__(language)
        
        # Validate that at least one dictionary source is provided
        if dictionary_path is None and dictionary is None:
            raise ValueError(
                "LevenshteinCandidateGenerator REQUIRES a dictionary. "
                "Provide either 'dictionary_path' (file path) or 'dictionary' (set of words)."
            )
        
        self.dictionary_path = dictionary_path
        self.deletion_weight = deletion_weight
        self.insertion_weight = insertion_weight
        self.substitution_weight = substitution_weight
        self.transposition_weight = transposition_weight
        self.default_weight = default_weight
        self.max_candidates = max_candidates
        
        # Load dictionary from provided source
        if dictionary is not None:
            self.dictionary = dictionary
        elif dictionary_path is not None:
            self.dictionary: Set[str] = set()
            self._load_dictionary(dictionary_path)
        else:
            self.dictionary = set()

    def _load_dictionary(self, path: str) -> None:
        """Load dictionary from file (one word per line)."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dictionary not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.dictionary = set(line.strip() for line in f if line.strip())

    def _levenshtein_distance(self, s1: str, s2: str) -> float:
        """Calculate weighted Levenshtein distance."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1) * self.deletion_weight

        previous_row = [i * self.insertion_weight for i in range(len(s2) + 1)]

        for i, c1 in enumerate(s1):
            current_row = [(i + 1) * self.deletion_weight]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + self.insertion_weight
                deletions = current_row[j] + self.deletion_weight
                substitutions = previous_row[j] + (
                    0 if c1 == c2 else self.substitution_weight
                )
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def generate(
        self, misspelled: str, context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Generate candidates using Levenshtein distance."""
        if not self.dictionary:
            return []

        # Filter by length (reasonable heuristic)
        length_range = len(misspelled)
        candidates = [
            word for word in self.dictionary if abs(len(word) - length_range) <= 2
        ]

        # Score candidates
        scored = [
            (word, self._levenshtein_distance(misspelled, word))
            for word in candidates
        ]

        # Sort by cost and return top candidates
        scored.sort(key=lambda x: x[1])
        return scored[: self.max_candidates]


class KeyboardDistanceCandidateGenerator(CandidateGenerator):
    """Generate candidates using keyboard proximity.

    Uses pre-computed keyboard distance matrices.
    """

    def __init__(
        self,
        language: str = "en",
        dictionary_path: Optional[str] = None,
        keyboard_matrix_path: Optional[str] = None,
        default_distance: float = 4.0,
        max_candidates: int = 10,
    ):
        super().__init__(language)
        self.dictionary_path = dictionary_path
        self.keyboard_matrix_path = keyboard_matrix_path
        self.default_distance = default_distance
        self.max_candidates = max_candidates
        self.dictionary: Set[str] = set()
        self.keyboard_distances: Dict[Tuple[str, str], float] = {}

        if dictionary_path:
            self._load_dictionary(dictionary_path)
        if keyboard_matrix_path:
            self._load_keyboard_matrix(keyboard_matrix_path)

    def _load_dictionary(self, path: str) -> None:
        """Load dictionary from file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dictionary not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.dictionary = set(line.strip() for line in f if line.strip())

    def _load_keyboard_matrix(self, path: str) -> None:
        """Load keyboard distance matrix (format: char1 TAB char2 TAB distance)."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Keyboard matrix not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    try:
                        char1, char2, distance = parts[0], parts[1], float(parts[2])
                        self.keyboard_distances[(char1, char2)] = distance
                        self.keyboard_distances[(char2, char1)] = distance
                    except (ValueError, IndexError):
                        pass

    def _keyboard_distance(self, s1: str, s2: str) -> float:
        """Calculate keyboard-proximity-weighted distance.

        TODO: Implement keyboard-based Levenshtein with keyboard distance matrix.
        For now, raise NotImplementedError.
        """
        raise NotImplementedError(
            "Keyboard distance calculation not yet implemented. "
            "TODO: Integrate with keyboard matrix for proximity-based weighting"
        )

    def generate(
        self, misspelled: str, context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Generate candidates using keyboard distance.

        TODO: Implement keyboard-based candidate generation.
        """
        raise NotImplementedError(
            "Keyboard distance candidate generation not yet fully implemented. "
            "TODO: Integrate keyboard matrix with Levenshtein distance calculation"
        )


class PhonemeCandidateGenerator(CandidateGenerator):
    """Generate candidates using phoneme-based Levenshtein distance.

    TODO: Integrate with G2P service for phoneme conversion.
    REQUIRES a dictionary to function.
    """

    def __init__(
        self,
        language: str = "en",
        dictionary_path: Optional[str] = None,
        dictionary: Optional[Set[str]] = None,
        phoneme_weight_path: Optional[str] = None,
        max_candidates: int = 10,
    ):
        """Initialize phoneme candidate generator.
        
        Args:
            language: Language code (default: 'en')
            dictionary_path: Path to dictionary file (one word per line)
            dictionary: Pre-loaded dictionary as set of words
            phoneme_weight_path: Path to phoneme weight matrix
            max_candidates: Maximum number of suggestions to return
            
        Raises:
            ValueError: If neither dictionary_path nor dictionary is provided
        """
        super().__init__(language)
        
        # Validate that at least one dictionary source is provided
        if dictionary_path is None and dictionary is None:
            raise ValueError(
                "PhonemeCandidateGenerator REQUIRES a dictionary. "
                "Provide either 'dictionary_path' (file path) or 'dictionary' (set of words)."
            )
        
        self.dictionary_path = dictionary_path
        self.phoneme_weight_path = phoneme_weight_path
        self.max_candidates = max_candidates
        self.g2p_cache: Dict[str, str] = {}
        
        # Load dictionary from provided source
        if dictionary is not None:
            self.dictionary = dictionary
        elif dictionary_path is not None:
            self.dictionary: Set[str] = set()
            self._load_dictionary(dictionary_path)
        else:
            self.dictionary = set()

    def _load_dictionary(self, path: str) -> None:
        """Load dictionary from file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dictionary not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.dictionary = set(line.strip() for line in f if line.strip())

    def _grapheme_to_phoneme(self, word: str) -> str:
        """Convert grapheme to phoneme representation.

        TODO: Integrate with G2P service (BAS or local g2p_en for English).
        Options:
          1. Call BAS G2P service (same as Java code)
          2. Use g2p_en for English
          3. Use espeak or festival
        """
        raise NotImplementedError(
            "Phoneme conversion not yet implemented. "
            "TODO: Integrate with G2P service (BAS, g2p_en, or espeak)"
        )

    def generate(
        self, misspelled: str, context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Generate candidates using phonetic distance.

        TODO: Implement phoneme-based candidate generation.
        """
        raise NotImplementedError(
            "Phoneme-based candidate generation not yet fully implemented. "
            "TODO: Implement G2P conversion and phonetic distance calculation"
        )


class MissingSpaceCandidateGenerator(CandidateGenerator):
    """Detect and suggest words with missing spaces.
    
    REQUIRES a dictionary to function.
    """

    def __init__(
        self,
        language: str = "en",
        dictionary_path: Optional[str] = None,
        dictionary: Optional[Set[str]] = None,
        min_word_length: int = 3,
        space_insertion_cost: float = 4.0,
        max_candidates: int = 5,
    ):
        """Initialize missing space candidate generator.
        
        Args:
            language: Language code (default: 'en')
            dictionary_path: Path to dictionary file (one word per line)
            dictionary: Pre-loaded dictionary as set of words
            min_word_length: Minimum word length to consider
            space_insertion_cost: Cost of insertion (used in DP)
            max_candidates: Maximum number of suggestions to return
            
        Raises:
            ValueError: If neither dictionary_path nor dictionary is provided
        """
        super().__init__(language)
        
        # Validate that at least one dictionary source is provided
        if dictionary_path is None and dictionary is None:
            raise ValueError(
                "MissingSpaceCandidateGenerator REQUIRES a dictionary. "
                "Provide either 'dictionary_path' (file path) or 'dictionary' (set of words)."
            )
        
        self.dictionary_path = dictionary_path
        self.min_word_length = min_word_length
        self.space_insertion_cost = space_insertion_cost
        self.max_candidates = max_candidates
        
        # Load dictionary from provided source
        if dictionary is not None:
            self.dictionary = dictionary
        elif dictionary_path is not None:
            self.dictionary: Set[str] = set()
            self._load_dictionary(dictionary_path)
        else:
            self.dictionary = set()

    def _load_dictionary(self, path: str) -> None:
        """Load dictionary from file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dictionary not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.dictionary = set(line.strip() for line in f if line.strip())

    def _find_segmentations(self, word: str, start: int = 0) -> List[List[str]]:
        """Find valid dictionary word segmentations using DP.

        Returns list of possible word segmentations.
        """
        if start == len(word):
            return [[]]

        segmentations = []

        for end in range(start + self.min_word_length, len(word) + 1):
            candidate = word[start:end]
            if candidate in self.dictionary:
                # Try extending with rest of word
                rest_segs = self._find_segmentations(word, end)
                for seg in rest_segs:
                    segmentations.append([candidate] + seg)

        return segmentations

    def generate(
        self, misspelled: str, context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Generate candidates for missing space."""
        if not self.dictionary:
            return []

        segmentations = self._find_segmentations(misspelled)

        candidates = []
        for seg in segmentations:
            joined = " ".join(seg)
            # Cost is number of spaces inserted
            cost = len(seg) * self.space_insertion_cost
            candidates.append((joined, cost))

        # Sort by cost and return top candidates
        candidates.sort(key=lambda x: x[1])
        return candidates[: self.max_candidates]


class CandidateEnsemble:
    """Combine multiple candidate generators."""

    def __init__(self, generators: List[CandidateGenerator]):
        self.generators = generators

    def generate(
        self, misspelled: str, context: Optional[str] = None, top_k: int = 10
    ) -> List[Tuple[str, float, str]]:
        """Generate candidates from all generators and merge results.

        Returns:
            List of (word, cost, method) tuples sorted by cost
        """
        all_candidates = []

        for generator in self.generators:
            try:
                candidates = generator.generate(misspelled, context)
                for word, cost in candidates:
                    all_candidates.append(
                        (word, cost, generator.__class__.__name__)
                    )
            except (NotImplementedError, Exception):
                # Skip generators that aren't implemented or fail
                pass

        # Remove duplicates (keep lowest cost)
        seen = {}
        for word, cost, method in all_candidates:
            if word not in seen or cost < seen[word][0]:
                seen[word] = (cost, method)

        # Convert back to list and sort
        result = [(word, cost, method) for word, (cost, method) in seen.items()]
        result.sort(key=lambda x: x[1])

        return result[:top_k]
