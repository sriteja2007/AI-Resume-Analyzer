from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def format_score(score: float) -> str:
    """Format a numerical score for display."""
    return f"{max(0.0, min(100.0, score)):.1f}/100"


def get_score_label(score: float) -> str:
    """Return a human-readable label for a score."""
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Very Good"
    if score >= 70:
        return "Good"
    if score >= 60:
        return "Needs Improvement"
    if score >= 50:
        return "Weak"

    return "Critical"


def truncate_text(
    text: str,
    max_length: int = 500,
) -> str:
    """Safely truncate long text."""
    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


def clean_filename(filename: str) -> str:
    """Create a safe filename."""
    if not filename:
        return "resume"

    filename = Path(filename).name

    filename = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        filename,
    )

    return filename


def get_file_extension(filename: str) -> str:
    """Return a lowercase file extension."""
    return Path(filename).suffix.lower()


def is_supported_resume(filename: str) -> bool:
    """Check whether a file is a supported resume format."""
    return get_file_extension(filename) in {
        ".pdf",
        ".docx",
        ".txt",
    }


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """Safely convert a value to integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def percentage(
    value: float,
    total: float,
) -> float:
    """Calculate a percentage safely."""
    if total <= 0:
        return 0.0

    return round(
        (value / total) * 100,
        2,
    )


def deduplicate_preserve_order(
    items: list[str],
) -> list[str]:
    """Remove duplicate strings while preserving order."""
    seen: set[str] = set()
    result: list[str] = []

    for item in items:
        normalized = item.strip().lower()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(item.strip())

    return result


def build_analysis_summary(
    ats_result: dict[str, Any],
    resume_score: dict[str, Any],
) -> dict[str, Any]:
    """Create a compact summary for the application dashboard."""
    overall_score = safe_float(
        resume_score.get("overall_score", 0)
    )

    return {
        "score": overall_score,
        "score_label": get_score_label(overall_score),
        "keywords": len(
            ats_result.get("keywords", [])
        ),
        "action_verbs": len(
            ats_result.get("action_verbs", [])
        ),
        "measurable_results": safe_int(
            ats_result.get(
                "measurable_results",
                {},
            ).get("count", 0)
        ),
        "sections_detected": len(
            ats_result.get("sections", {})
        ),
    }