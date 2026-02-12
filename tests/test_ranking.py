"""Tests for ranking strategies."""

import unittest
from unittest.mock import MagicMock, patch

from lespell.spellchecker.ranking import (
    CostBasedRanker,
    EnsembleRanker,
    MaskedLanguageModelRanker,
)


class TestCostBasedRanker(unittest.TestCase):
    """Test CostBasedRanker."""

    def setUp(self):
        """Set up test fixtures."""
        self.ranker = CostBasedRanker()

    def test_rank_by_cost(self):
        """Test ranking sorts candidates by cost."""
        candidates = [("test", 0.5), ("tset", 0.3), ("text", 0.8)]
        result = self.ranker.rank(candidates)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], "tset")  # Lowest cost first
        self.assertEqual(result[1][0], "test")
        self.assertEqual(result[2][0], "text")

    def test_rank_empty_candidates(self):
        """Test ranking with empty candidate list."""
        result = self.ranker.rank([])
        self.assertEqual(result, [])

    def test_rank_single_candidate(self):
        """Test ranking with single candidate."""
        candidates = [("test", 0.5)]
        result = self.ranker.rank(candidates)
        self.assertEqual(result, candidates)

    def test_rank_ignores_context(self):
        """Test that CostBasedRanker ignores context and misspelled."""
        candidates = [("test", 0.5), ("tset", 0.3)]
        context = "This is a tset sentence"
        misspelled = "tset"
        
        result = self.ranker.rank(candidates, context=context, misspelled=misspelled)
        
        # Should still be sorted by cost, not affected by context
        self.assertEqual(result[0][0], "tset")


class TestMaskedLanguageModelRanker(unittest.TestCase):
    """Test MaskedLanguageModelRanker."""

    def setUp(self):
        """Try to create a ranker, skip tests if transformers is not available."""
        try:
            self.ranker = MaskedLanguageModelRanker()
            self.has_transformers = True
        except ImportError:
            self.has_transformers = False
            self.ranker = None

    def test_initialization_with_model_name(self):
        """Test initialization with custom model name."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        self.assertEqual(self.ranker.model_name, "distilbert-base-uncased")
        self.assertIsNone(self.ranker.pipe)  # Should be lazy-loaded

    def test_rank_without_context_fallback(self):
        """Test that rank falls back to cost-based ranking without context."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        candidates = [("test", 0.5), ("tset", 0.3), ("text", 0.8)]
        result = self.ranker.rank(candidates)
        
        # Should fall back to cost-based ranking
        self.assertEqual(result[0][0], "tset")
        self.assertEqual(result[1][0], "test")
        self.assertEqual(result[2][0], "text")

    def test_rank_without_misspelled_fallback(self):
        """Test that rank falls back to cost-based ranking without misspelled word."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        candidates = [("test", 0.5), ("tset", 0.3), ("text", 0.8)]
        context = "This is a sentence"
        
        result = self.ranker.rank(candidates, context=context, misspelled=None)
        
        # Should fall back to cost-based ranking
        self.assertEqual(result[0][0], "tset")

    def test_rank_empty_candidates(self):
        """Test ranking with empty candidate list."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        result = self.ranker.rank([])
        self.assertEqual(result, [])

    def test_rank_with_lm_scores(self):
        """Test ranking with LM scores converts probabilities to costs correctly."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        candidates = [("test", 0.5), ("tset", 0.3), ("text", 0.8)]
        context = "This is a tset sentence"
        misspelled = "tset"
        
        # Mock the _score_with_huggingface method
        mock_scores = {"test": 0.8, "tset": 0.2, "text": 0.9}
        
        with patch.object(self.ranker, '_score_with_huggingface', return_value=mock_scores):
            result = self.ranker.rank(candidates, context=context, misspelled=misspelled)
            
            # Result should be sorted by LM score (highest probability = lowest cost)
            # text: 0.9 -> cost 0.1 (best)
            # test: 0.8 -> cost 0.2
            # tset: 0.2 -> cost 0.8 (worst)
            self.assertEqual(result[0][0], "text")
            self.assertEqual(result[1][0], "test")
            self.assertEqual(result[2][0], "tset")
            
            # Check that costs are correct
            self.assertAlmostEqual(result[0][1], 0.1, places=5)
            self.assertAlmostEqual(result[1][1], 0.2, places=5)
            self.assertAlmostEqual(result[2][1], 0.8, places=5)

    def test_rank_lm_score_missing_candidate(self):
        """Test ranking when LM doesn't score all candidates."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        candidates = [("test", 0.5), ("tset", 0.3), ("text", 0.8)]
        context = "This is a sentence"
        misspelled = "word"
        
        # Mock partial scores (missing "text")
        mock_scores = {"test": 0.8, "tset": 0.2}
        
        with patch.object(self.ranker, '_score_with_huggingface', return_value=mock_scores):
            result = self.ranker.rank(candidates, context=context, misspelled=misspelled)
            
            # All candidates should be present, unscored ones get penalty
            self.assertEqual(len(result), 3)
            words = [word for word, _ in result]
            self.assertIn("test", words)
            self.assertIn("tset", words)
            self.assertIn("text", words)
            
            # Text should be last due to penalty
            self.assertEqual(result[-1][0], "text")
            self.assertEqual(result[-1][1], 1.0)

    def test_score_with_mock_pipeline(self):
        """Test _score_with_huggingface with mocked pipeline."""
        if not self.has_transformers:
            self.skipTest("transformers library not installed")
        
        # Mock the pipeline to return scores
        mock_results = [
            {"token_str": "test", "score": 0.8},
            {"token_str": "text", "score": 0.9},
            {"token_str": "best", "score": 0.3},
        ]
        
        with patch.object(self.ranker, 'pipe', create=True) as mock_pipe, \
             patch.object(self.ranker, '_MaskedLanguageModelRanker__mask_token', '[MASK]'):
            self.ranker.pipe = MagicMock(return_value=mock_results)
            self.ranker.tokenizer = MagicMock()
            
            scores = self.ranker._score_with_huggingface(
                ["test", "text", "best"],
                "This is a [MASK] sentence",
                "word"
            )
            
            self.assertIn("test", scores)
            self.assertIn("text", scores)
            self.assertIn("best", scores)
            # Scores should be extracted from mock results
            self.assertEqual(scores.get("test"), 0.8)
            self.assertEqual(scores.get("text"), 0.9)


class TestEnsembleRanker(unittest.TestCase):
    """Test EnsembleRanker."""

    def setUp(self):
        """Set up test fixtures."""
        self.ranker1 = CostBasedRanker()
        self.ranker2 = CostBasedRanker()

    def test_ensemble_initialization(self):
        """Test ensemble ranker initialization."""
        ensemble = EnsembleRanker([(self.ranker1, 0.5), (self.ranker2, 0.5)])
        self.assertEqual(len(ensemble.rankers), 2)

    def test_ensemble_weight_normalization(self):
        """Test that weights are normalized."""
        ensemble = EnsembleRanker([(self.ranker1, 0.6), (self.ranker2, 0.4)])
        
        total_weight = sum(weight for _, weight in ensemble.rankers)
        self.assertAlmostEqual(total_weight, 1.0)

    def test_ensemble_rank(self):
        """Test ensemble ranking."""
        ensemble = EnsembleRanker([(self.ranker1, 0.5), (self.ranker2, 0.5)])
        candidates = [("test", 0.5), ("tset", 0.3), ("text", 0.8)]
        
        result = ensemble.rank(candidates)
        
        self.assertEqual(len(result), 3)
        # Ensemble should still return valid results
        words = [word for word, _ in result]
        self.assertEqual(set(words), {"test", "tset", "text"})


class TestRankingIntegration(unittest.TestCase):
    """Integration tests for ranking components."""

    def test_cost_based_ranker_integration(self):
        """Test CostBasedRanker in typical workflow."""
        ranker = CostBasedRanker()
        
        # Simulate candidates from different generators
        candidates = [
            ("test", 0.1),  # High cost (Levenshtein)
            ("tset", 0.05),
            ("text", 0.15),
        ]
        
        result = ranker.rank(candidates)
        
        # Best candidate should be first
        self.assertEqual(result[0][0], "tset")

    def test_ranking_preserves_word_identity(self):
        """Test that ranking doesn't modify candidate words."""
        ranker = CostBasedRanker()
        candidates = [("Test", 0.5), ("TSET", 0.3), ("text", 0.8)]
        
        result = ranker.rank(candidates)
        
        # Case should be preserved
        original_words = {word for word, _ in candidates}
        result_words = {word for word, _ in result}
        self.assertEqual(original_words, result_words)

    def test_zero_cost_candidates(self):
        """Test ranking with zero cost candidates."""
        ranker = CostBasedRanker()
        candidates = [("test", 0.0), ("tset", 0.0), ("text", 0.1)]
        
        result = ranker.rank(candidates)
        
        # Should have two with cost 0.0 first (order among them may vary)
        zero_cost_candidates = [word for word, cost in result if cost == 0.0]
        self.assertEqual(len(zero_cost_candidates), 2)


if __name__ == "__main__":
    unittest.main()
