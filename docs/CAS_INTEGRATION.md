# CAS Integration with dkpro-cassis

LeSpell now supports CAS (Common Analysis Structure) from [dkpro-cassis](https://github.com/dkpro/dkpro-cassis) for representing text and annotations internally.

## Overview

CAS is a standardized format from UIMA/DKPro for representing:
- Text content (the document being analyzed)
- Annotations (linguistic information like tokens, sentences, errors)
- Feature structures (attributes of annotations)

Using CAS provides:
- **Interoperability**: Works with other DKPro/UIMA tools
- **Standardization**: Industry-standard format for NLP
- **Rich annotations**: Multiple annotation layers on the same text
- **Flexibility**: Use your own tokenization or let LeSpell handle it

## API Usage

### Option 1: Plain Text Input (Automatic Tokenization)

LeSpell will tokenize the text for you:

```python
from lespell.spellchecker import (
    SpellingChecker,
    DictionaryErrorDetector,
    LevenshteinCandidateGenerator,
    create_cas,
)

# Create spell checker
dictionary = {"this", "is", "a", "test"}
detector = DictionaryErrorDetector(dictionary=dictionary)
generator = LevenshteinCandidateGenerator(language="en", dictionary=dictionary)
checker = SpellingChecker(detector=detector, candidate_generators=[generator])

# Check text with CAS
cas = create_cas("This is a tset")
cas, result = checker.check_cas(cas)

print(f"Found {result['error_count']} errors")
for error in result['errors']:
    print(f"  '{error['word']}' -> {error['suggestions'][0]}")
```

### Option 2: Pre-tokenized CAS

Provide your own tokenization:

```python
from lespell.spellchecker import create_cas, tokenize_cas

# Create CAS
cas = create_cas("This is a test")

# Add your own tokens (or use tokenize_cas for simple whitespace tokenization)
tokenize_cas(cas)  # Adds Token annotations

# Check with pre-tokenized CAS
cas, result = checker.check_cas(cas)
```

### Option 3: Traditional Text API (Still Supported)

The original API remains unchanged:

```python
# Traditional API
result = checker.check_text("This is a tset")
print(f"Found {result['error_count']} errors")
```

## CAS Utility Functions

LeSpell provides several utility functions for working with CAS:

```python
from lespell.spellchecker import (
    create_cas,           # Create a new CAS
    tokenize_cas,         # Add Token annotations
    has_tokens,           # Check if CAS has tokens
    get_tokens_from_cas,  # Extract tokens as list
    add_spelling_error,   # Add SpellingAnomaly annotation
    get_spelling_errors,  # Get all spelling errors
    cas_to_text,          # Convert CAS to Text object
    text_to_cas,          # Convert Text to CAS
)
```

## Handoff Between Detector and Corrector

The CAS-based API uses standard DKPro types for handoff:

1. **Input**: Text with optional `Token` annotations
2. **Detection**: Detector adds `SpellingAnomaly` annotations to CAS
3. **Correction**: Corrector reads `SpellingAnomaly` annotations and generates suggestions
4. **Output**: CAS with `SpellingAnomaly` annotations + results dictionary

```python
# Detector adds SpellingAnomaly annotations
cas, errors = detector.detect_cas(cas)

# Checker uses these for correction
cas, result = checker.check_cas(cas)

# CAS now has both Token and SpellingAnomaly annotations
```

## Type System

LeSpell uses DKPro Core types:
- `de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token` - word tokens
- `de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly` - spelling errors
- Custom types from `Spelling.xml` (for extended features)

## Example

See `examples/cas_spell_check.py` for a complete working example.

## Backward Compatibility

All existing APIs remain fully functional. The CAS integration is additive:
- `Text` and `Annotation` classes still work
- `check_text()` method unchanged
- `detect()` method unchanged
- New `check_cas()` and `detect_cas()` methods added

## Benefits

1. **Standard Format**: CAS is widely used in NLP tools
2. **Interoperability**: Exchange data with other DKPro tools
3. **Extensibility**: Easy to add custom annotation types
4. **Flexibility**: Support both plain text and pre-annotated input
5. **Clean Architecture**: Detector and corrector communicate via typed annotations

## Migration Guide

Existing code continues to work without changes. To adopt CAS:

### Before (Text-based):
```python
text = Text(content="This is a test")
text, errors = detector.detect(text)
result = checker.check_text(text.content)
```

### After (CAS-based):
```python
cas = create_cas("This is a test")
cas, errors = detector.detect_cas(cas)
cas, result = checker.check_cas(cas)
```

Both approaches are supported and give equivalent results.
