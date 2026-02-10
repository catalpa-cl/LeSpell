# LeSpell Examples

This folder contains practical examples demonstrating how to use the LeSpell spell checker.

## Running the Examples

From the repository root:

```bash
# Option 1: With PYTHONPATH
PYTHONPATH=/Users/zesch/git/aslan/lespell python3 examples/simple_spell_check.py

# Option 2: Install in development mode (one-time)
pip install -e .
python3 examples/simple_spell_check.py

# Option 3: From examples directory with explicit import
cd examples && python3 -c "import sys; sys.path.insert(0, '..'); exec(open('simple_spell_check.py').read())"
```

## Available Examples

### 1. SpellingItem Basics
**File:** `spelling_items.py`

Start here! Learn about the core `SpellingItem` data structure:

```bash
python3 examples/spelling_items.py
```

**What it covers:**
- Creating SpellingItem objects
- Accessing properties and corrections
- Batch processing items
- Grammar vs spelling errors

### 2. Simple Spell Checking
**File:** `simple_spell_check.py`

Learn how to use the spell checker:

```bash
python3 examples/simple_spell_check.py
```

**What it shows:**
- Initializing a SpellingChecker
- Checking text for errors
- Getting correction suggestions
- Checking multiple texts
- Note: Requires dictionary or returns edit-distance matches

### 3. Batch Processing
**File:** `batch_processing.py`

Process multiple documents from a corpus:

```bash
python3 examples/batch_processing.py
```

**What it shows:**
- Using SpellingItem objects in batch mode
- Combining multiple generators (Levenshtein + Hunspell)
- Comparing detected errors with gold annotations
- Full pipeline example

## Common Usage Patterns

### Pattern 1: Single Text Check
```python
from lespell.spellchecker import SpellingChecker, LevenshteinCandidateGenerator

checker = SpellingChecker(
    candidate_generators=[LevenshteinCandidateGenerator()]
)

result = checker.check_text("Your text here")
print(f"Found {result['error_count']} errors")
```

### Pattern 2: Multiple Generators
```python
from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    HunspellCandidateGenerator,
)

checker = SpellingChecker(
    candidate_generators=[
        LevenshteinCandidateGenerator(),
        HunspellCandidateGenerator(),
    ]
)
```

### Pattern 3: Custom Ranking
```python
from lespell.spellchecker import (
    SpellingChecker,
    LevenshteinCandidateGenerator,
    CostBasedRanker,
    EnsembleRanker,
)

checker = SpellingChecker(
    candidate_generators=[LevenshteinCandidateGenerator()],
    ranker=EnsembleRanker([CostBasedRanker()])  # Custom ranker
)
```

### Pattern 4: Batch Processing
```python
from lespell.spellchecker import SpellingChecker, LevenshteinCandidateGenerator
from lespell.core import SpellingItem

checker = SpellingChecker(
    candidate_generators=[LevenshteinCandidateGenerator()]
)

items = [
    SpellingItem("corpus", "id1", "text with error"),
    SpellingItem("corpus", "id2", "another text"),
]

results = checker.check_spelling_items(items)
```

## Next Steps

1. **Understand the Architecture**: Read [SPELLCHECKER_IMPLEMENTATION.md](../SPELLCHECKER_IMPLEMENTATION.md)
2. **Run Tests**: `python3 -m unittest tests.test_spellchecker -v`
3. **Explore API**: Check [lespell/spellchecker/__init__.py](../lespell/spellchecker/__init__.py)
4. **Implement Features**: See TODOs in [SESSION_SUMMARY.md](../SESSION_SUMMARY.md)

## API Quick Reference

### SpellingChecker
- `check_text(text)` - Find spelling errors in text
- `correct_text(text, auto_correct=False)` - Get corrected text
- `check_spelling_items(items)` - Batch process SpellingItem objects

### Candidate Generators
- `LevenshteinCandidateGenerator` - Edit distance based suggestions
- `HunspellCandidateGenerator` - Dictionary based suggestions
- `MissingSpaceCandidateGenerator` - Suggest compound words
- `KeyboardDistanceCandidateGenerator` - Proximity based (TODO)
- `PhonemeCandidateGenerator` - Phonetic based (TODO)

### Rankers
- `CostBasedRanker` - Simple cost-based sorting
- `EnsembleRanker` - Combine multiple rankers
- `LanguageModelReranker` - Language model scoring (TODO)

## Troubleshooting

**Error: "No module named 'lespell'"**
- Run from the repository root
- Or install: `pip install -e .`

**Spell checker returns empty results**
- Check that at least one candidate generator is initialized
- Verify the text contains actual errors

**Want faster suggestions?**
- Use `LevenshteinCandidateGenerator` alone (fastest)
- Reduce `max_candidates` parameter

**Want better suggestions?**
- Combine multiple generators (accuracy trade-off)
- Implement G2P or keyboard distance (see TODOs)
