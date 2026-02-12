"""CAS utilities for working with dkpro-cassis."""

from typing import List, Optional, Tuple, Union

from cassis import Cas, load_dkpro_core_typesystem

from lespell.spellchecker.annotations import Annotation, Text

# Lazy-load typesystem
_TYPESYSTEM = None


def get_typesystem():
    """Get or create the DKPro Core typesystem."""
    global _TYPESYSTEM
    if _TYPESYSTEM is None:
        _TYPESYSTEM = load_dkpro_core_typesystem()
    return _TYPESYSTEM


def create_cas(text: str) -> Cas:
    """Create a CAS with the given text.

    Args:
        text: Text content to add to the CAS

    Returns:
        A CAS object with the text set
    """
    cas = Cas(typesystem=get_typesystem())
    cas.sofa_string = text
    return cas


def tokenize_cas(cas: Cas) -> Cas:
    """Add simple whitespace-based tokenization to a CAS.

    Args:
        cas: CAS to tokenize (must have sofa_string set)

    Returns:
        The same CAS with Token annotations added
    """
    Token = get_typesystem().get_type("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token")

    text = cas.sofa_string
    start = 0
    for i, char in enumerate(text + " "):
        if char.isspace():
            if i > start:
                token = Token(begin=start, end=i)
                cas.add(token)
            start = i + 1

    return cas


def cas_to_text(cas: Cas) -> Text:
    """Convert a CAS to a Text object (for backward compatibility).

    Args:
        cas: CAS to convert

    Returns:
        Text object with content and annotations
    """
    text = Text(content=cas.sofa_string)

    # Convert all CAS annotations to Text annotations
    for ann in cas.select_all():
        if not hasattr(ann, "begin") or not hasattr(ann, "end"):
            continue

        # Map CAS types to our annotation types
        type_name = ann.type.name
        annotation_type = _map_cas_type_to_annotation_type(type_name)

        # Extract metadata from CAS annotation features
        metadata = {}
        for feature in ann.type.all_features:
            if feature.name not in ["begin", "end", "sofa"]:
                value = getattr(ann, feature.name, None)
                if value is not None:
                    metadata[feature.name] = value

        annotation = Annotation(
            type=annotation_type,
            start=ann.begin,
            end=ann.end,
            metadata=metadata,
        )
        text.add_annotation(annotation)

    return text


def text_to_cas(text: Text) -> Cas:
    """Convert a Text object to a CAS.

    Args:
        text: Text object to convert

    Returns:
        CAS with text content and annotations
    """
    cas = create_cas(text.content)
    ts = get_typesystem()

    # Convert Text annotations to CAS annotations
    for ann in text.annotations:
        cas_type_name = _map_annotation_type_to_cas_type(ann.type)
        try:
            CasType = ts.get_type(cas_type_name)
            cas_ann = CasType(begin=ann.start, end=ann.end)

            # Set features from metadata
            for key, value in ann.metadata.items():
                if hasattr(cas_ann, key):
                    setattr(cas_ann, key, value)

            cas.add(cas_ann)
        except Exception:
            # If type doesn't exist or can't be created, skip it
            pass

    return cas


def _map_cas_type_to_annotation_type(cas_type: str) -> str:
    """Map CAS type name to our annotation type."""
    type_mapping = {
        "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token": "token",
        "de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly": "spelling_error",
        "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS": "pos",
        "spelling.types.ExtendedSpellingAnomaly": "spelling_error",
        "spelling.types.Punctuation": "punctuation",
        "spelling.types.Numeric": "numeric",
        "spelling.types.KnownWord": "known_word",
    }
    return type_mapping.get(cas_type, cas_type.split(".")[-1].lower())


def _map_annotation_type_to_cas_type(annotation_type: str) -> str:
    """Map our annotation type to CAS type name."""
    type_mapping = {
        "token": "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
        "spelling_error": "de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly",
        "numeric": "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
        "punctuation": "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
        "known_word": "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
    }
    return type_mapping.get(annotation_type, "uima.tcas.Annotation")


def get_tokens_from_cas(cas: Cas) -> List[Tuple[int, int, str]]:
    """Extract tokens from CAS as (start, end, text) tuples.

    Args:
        cas: CAS with Token annotations

    Returns:
        List of (start, end, text) tuples
    """
    Token = get_typesystem().get_type("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token")
    tokens = []

    for token in cas.select("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"):
        text = token.get_covered_text()
        tokens.append((token.begin, token.end, text))

    return tokens


def has_tokens(cas: Cas) -> bool:
    """Check if CAS has Token annotations.

    Args:
        cas: CAS to check

    Returns:
        True if CAS has at least one Token annotation
    """
    try:
        tokens = list(cas.select("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"))
        return len(tokens) > 0
    except Exception:
        return False


def add_spelling_error(
    cas: Cas, begin: int, end: int, suggestions: Optional[List[str]] = None
) -> None:
    """Add a spelling error annotation to the CAS.

    Args:
        cas: CAS to add error to
        begin: Start offset of error
        end: End offset of error
        suggestions: Optional list of correction suggestions
    """
    SpellingAnomaly = get_typesystem().get_type(
        "de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly"
    )

    error = SpellingAnomaly(begin=begin, end=end)

    # Set suggestions if provided and feature exists
    if suggestions and hasattr(error, "suggestions"):
        error.suggestions = suggestions

    cas.add(error)


def get_spelling_errors(cas: Cas) -> List[Tuple[int, int, str]]:
    """Get spelling errors from CAS.

    Args:
        cas: CAS to extract errors from

    Returns:
        List of (start, end, text) tuples for spelling errors
    """
    errors = []

    try:
        for error in cas.select("de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly"):
            text = error.get_covered_text()
            errors.append((error.begin, error.end, text))
    except Exception:
        pass

    return errors
