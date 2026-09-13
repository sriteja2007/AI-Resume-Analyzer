from __future__ import annotations

import re
from collections import Counter


DEFAULT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "her",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "she",
    "that",
    "the",
    "their",
    "them",
    "this",
    "to",
    "was",
    "we",
    "were",
    "will",
    "with",
    "you",
    "your",
}


def normalize_text(text: str) -> str:
    """Normalize extracted resume text."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace unusual whitespace with standard spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove repeated blank lines.
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def clean_text(text: str) -> str:
    """Clean text while preserving useful resume characters."""
    text = normalize_text(text)

    if not text:
        return ""

    # Keep letters, numbers, common punctuation and symbols useful in resumes.
    text = re.sub(r"[^\w\s@.+#/&()\-%,:;']", " ", text, flags=re.UNICODE)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def tokenize_text(
    text: str,
    remove_stopwords: bool = True,
) -> list[str]:
    """Convert text into normalized word tokens."""
    cleaned = clean_text(text)

    if not cleaned:
        return []

    tokens = re.findall(r"[A-Za-z0-9+#@.&'-]+", cleaned.lower())

    if remove_stopwords:
        tokens = [
            token
            for token in tokens
            if token not in DEFAULT_STOPWORDS
        ]

    return tokens


def get_word_frequencies(
    text: str,
    remove_stopwords: bool = True,
) -> dict[str, int]:
    """Return word-frequency counts for the supplied text."""
    tokens = tokenize_text(
        text,
        remove_stopwords=remove_stopwords,
    )

    return dict(Counter(tokens).most_common())


def get_text_statistics(text: str) -> dict:
    """Generate useful text statistics for resume analysis."""
    cleaned = clean_text(text)
    tokens = tokenize_text(cleaned, remove_stopwords=False)
    meaningful_tokens = tokenize_text(cleaned, remove_stopwords=True)

    lines = [
        line.strip()
        for line in cleaned.splitlines()
        if line.strip()
    ]

    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?]+", cleaned)
        if sentence.strip()
    ]

    unique_words = set(meaningful_tokens)

    return {
        "characters": len(cleaned),
        "words": len(tokens),
        "unique_words": len(unique_words),
        "lines": len(lines),
        "sentences": len(sentences),
    }


def preprocess_resume(text: str) -> dict:
    """Run the complete preprocessing pipeline on resume text."""
    normalized = normalize_text(text)
    cleaned = clean_text(normalized)
    tokens = tokenize_text(cleaned)
    frequencies = get_word_frequencies(cleaned)

    return {
        "original_text": text,
        "normalized_text": normalized,
        "cleaned_text": cleaned,
        "tokens": tokens,
        "word_frequencies": frequencies,
        "statistics": get_text_statistics(cleaned),
    }