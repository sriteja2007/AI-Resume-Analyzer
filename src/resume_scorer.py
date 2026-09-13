from __future__ import annotations

from typing import Dict, List, Any


def _safe_number(value: Any, default: float = 0.0) -> float:
    """Convert a value to a safe numeric value."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_section_completeness(ats_result: Dict[str, Any]) -> float:
    """Score resume section completeness."""

    section_score = ats_result.get("section_score", {})

    if isinstance(section_score, dict):
        values = [
            _safe_number(value)
            for value in section_score.values()
        ]

        if values:
            return max(0.0, min(100.0, sum(values) / len(values)))

    detected_sections = ats_result.get(
        "detected_sections",
        {},
    )

    if isinstance(detected_sections, dict):
        total = len(detected_sections)

        if total:
            found = sum(
                1
                for value in detected_sections.values()
                if value
            )

            return (found / total) * 100

    return 0.0


def score_formatting(ats_result: Dict[str, Any]) -> float:
    """Get formatting score."""

    formatting_score = ats_result.get(
        "formatting_score",
        0,
    )

    if isinstance(formatting_score, dict):
        values = [
            _safe_number(value)
            for value in formatting_score.values()
        ]

        if values:
            return sum(values) / len(values)

    return max(
        0.0,
        min(
            100.0,
            _safe_number(formatting_score),
        ),
    )


def score_keywords(ats_result: Dict[str, Any]) -> float:
    """Get keyword score."""

    return max(
        0.0,
        min(
            100.0,
            _safe_number(
                ats_result.get(
                    "keyword_score",
                    ats_result.get(
                        "keyword_match_score",
                        0,
                    ),
                )
            ),
        ),
    )


def score_action_verbs(ats_result: Dict[str, Any]) -> float:
    """Score use of action verbs."""

    action_verbs = ats_result.get(
        "action_verbs",
        [],
    )

    if isinstance(action_verbs, (list, tuple, set)):
        count = len(action_verbs)

        if count >= 10:
            return 100.0

        if count >= 7:
            return 90.0

        if count >= 5:
            return 80.0

        if count >= 3:
            return 65.0

        if count >= 1:
            return 40.0

        return 0.0

    return max(
        0.0,
        min(
            100.0,
            _safe_number(action_verbs),
        ),
    )


def score_achievements(ats_result: Dict[str, Any]) -> float:
    """Score quantifiable achievements."""

    achievements = ats_result.get(
        "quantifiable_achievements",
        [],
    )

    if isinstance(achievements, (list, tuple, set)):
        count = len(achievements)

        if count >= 5:
            return 100.0

        if count >= 4:
            return 90.0

        if count >= 3:
            return 80.0

        if count >= 2:
            return 65.0

        if count >= 1:
            return 45.0

        return 0.0

    return max(
        0.0,
        min(
            100.0,
            _safe_number(achievements),
        ),
    )


def score_contact_information(ats_result: Dict[str, Any]) -> float:
    """Score contact information completeness."""

    contact_info = ats_result.get(
        "contact_information",
        {},
    )

    if isinstance(contact_info, dict):
        fields = [
            "email",
            "phone",
            "linkedin",
            "github",
        ]

        present = sum(
            1
            for field in fields
            if contact_info.get(field)
        )

        if present == 4:
            return 100.0

        if present == 3:
            return 85.0

        if present == 2:
            return 70.0

        if present == 1:
            return 45.0

        return 0.0

    return max(
        0.0,
        min(
            100.0,
            _safe_number(contact_info),
        ),
    )


def calculate_overall_score(
    ats_result: Dict[str, Any],
) -> float:
    """
    Calculate the overall resume score.

    Weighting:
    - Section completeness: 30%
    - Formatting: 25%
    - Keywords: 15%
    - Action verbs: 10%
    - Achievements: 10%
    - Contact information: 10%
    """

    section_score = score_section_completeness(
        ats_result
    )

    formatting_score = score_formatting(
        ats_result
    )

    keyword_score = score_keywords(
        ats_result
    )

    action_verb_score = score_action_verbs(
        ats_result
    )

    achievement_score = score_achievements(
        ats_result
    )

    contact_score = score_contact_information(
        ats_result
    )

    overall_score = (
        section_score * 0.30
        + formatting_score * 0.25
        + keyword_score * 0.15
        + action_verb_score * 0.10
        + achievement_score * 0.10
        + contact_score * 0.10
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                overall_score,
            ),
        ),
        2,
    )


def get_score_grade(score: float) -> str:
    """Return a grade based on score."""

    score = _safe_number(score)

    if score >= 90:
        return "Excellent"

    if score >= 80:
        return "Very Good"

    if score >= 70:
        return "Good"

    if score >= 60:
        return "Average"

    if score >= 50:
        return "Needs Improvement"

    return "Poor"


def get_score_category(score: float) -> str:
    """Return a simple score category."""

    score = _safe_number(score)

    if score >= 80:
        return "Strong Resume"

    if score >= 65:
        return "Competitive Resume"

    if score >= 50:
        return "Needs Improvement"

    return "Weak Resume"


def build_score_breakdown(
    ats_result: Dict[str, Any],
) -> Dict[str, float]:
    """Build score breakdown for the UI."""

    return {
        "Section Completeness": round(
            score_section_completeness(ats_result),
            2,
        ),
        "Formatting": round(
            score_formatting(ats_result),
            2,
        ),
        "Keywords": round(
            score_keywords(ats_result),
            2,
        ),
        "Action Verbs": round(
            score_action_verbs(ats_result),
            2,
        ),
        "Achievements": round(
            score_achievements(ats_result),
            2,
        ),
        "Contact Information": round(
            score_contact_information(ats_result),
            2,
        ),
    }


def identify_strengths(
    breakdown: Dict[str, float],
) -> List[str]:
    """Identify strong areas."""

    strengths = []

    for category, score in breakdown.items():
        if score >= 80:
            strengths.append(
                f"Strong {category.lower()}."
            )

    return strengths


def identify_improvements(
    breakdown: Dict[str, float],
) -> List[str]:
    """Identify areas that need improvement."""

    improvements = []

    for category, score in breakdown.items():
        if score < 60:
            improvements.append(
                f"Improve {category.lower()}."
            )

    return improvements


def analyze_resume_score(
    resume_text: str,
) -> Dict[str, Any]:
    """
    Analyze the resume and return a complete
    scoring result.

    The function is intentionally independent from
    the ATS implementation so the application remains
    stable if ATS output changes.
    """

    # Import here to avoid circular imports.
    from src.ats_analyzer import analyze_ats

    ats_result = analyze_ats(resume_text)

    # Some older versions of the ATS analyzer may
    # return a string instead of a dictionary.
    # In that case, create a safe fallback structure.
    if not isinstance(ats_result, dict):
        ats_result = {
            "section_score": {},
            "formatting_score": 0,
            "keyword_score": 0,
            "action_verbs": [],
            "quantifiable_achievements": [],
            "contact_information": {},
            "detected_sections": {},
        }

    overall_score = calculate_overall_score(
        ats_result
    )

    breakdown = build_score_breakdown(
        ats_result
    )

    strengths = identify_strengths(
        breakdown
    )

    improvements = identify_improvements(
        breakdown
    )

    return {
        "overall_score": overall_score,
        "grade": get_score_grade(
            overall_score
        ),
        "category": get_score_category(
            overall_score
        ),
        "breakdown": breakdown,
        "strengths": strengths,
        "improvements": improvements,
        "ats_score": ats_result.get(
            "ats_score",
            0,
        ),
    }