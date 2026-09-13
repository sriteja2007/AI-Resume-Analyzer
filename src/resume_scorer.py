from __future__ import annotations

from typing import Any


def clamp_score(score: float) -> float:
    """Keep a score between 0 and 100."""
    return round(max(0.0, min(100.0, score)), 2)


def score_section_completeness(ats_result: dict[str, Any]) -> float:
    """Score the completeness of important resume sections."""
    section_score = ats_result.get("section_score", {})
    return clamp_score(float(section_score.get("total", 0)))


def score_formatting(ats_result: dict[str, Any]) -> float:
    """Score ATS-friendly formatting."""
    formatting = ats_result.get("formatting", {})
    return clamp_score(float(formatting.get("score", 0)))


def score_keywords(ats_result: dict[str, Any]) -> float:
    """Score the use of relevant resume keywords."""
    return clamp_score(float(ats_result.get("keyword_score", 0)))


def score_action_verbs(ats_result: dict[str, Any]) -> float:
    """Score the use of strong action verbs."""
    return clamp_score(float(ats_result.get("action_verb_score", 0)))


def score_achievements(ats_result: dict[str, Any]) -> float:
    """Score measurable achievements."""
    return clamp_score(float(ats_result.get("achievement_score", 0)))


def score_contact_information(ats_result: dict[str, Any]) -> float:
    """Score the completeness of contact information."""
    return clamp_score(float(ats_result.get("contact_score", 0)))


def calculate_overall_score(ats_result: dict[str, Any]) -> float:
    """
    Calculate a portfolio-friendly overall resume score.

    The score combines:
    - Section completeness: 30%
    - ATS formatting: 25%
    - Keywords: 15%
    - Action verbs: 10%
    - Measurable achievements: 10%
    - Contact information: 10%
    """
    section_score = score_section_completeness(ats_result)
    formatting_score = score_formatting(ats_result)
    keyword_score = score_keywords(ats_result)
    action_verb_score = score_action_verbs(ats_result)
    achievement_score = score_achievements(ats_result)
    contact_score = score_contact_information(ats_result)

    overall = (
        section_score * 0.30
        + formatting_score * 0.25
        + keyword_score * 0.15
        + action_verb_score * 0.10
        + achievement_score * 0.10
        + contact_score * 0.10
    )

    return clamp_score(overall)


def get_score_grade(score: float) -> str:
    """Convert a numerical score into a readable grade."""
    score = clamp_score(score)

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


def get_score_color(score: float) -> str:
    """Return a UI-friendly score category."""
    score = clamp_score(score)

    if score >= 80:
        return "excellent"
    if score >= 60:
        return "good"
    if score >= 40:
        return "average"

    return "weak"


def generate_score_breakdown(ats_result: dict[str, Any]) -> dict[str, float]:
    """Return all major scoring categories."""
    return {
        "Section Completeness": score_section_completeness(ats_result),
        "ATS Formatting": score_formatting(ats_result),
        "Keywords": score_keywords(ats_result),
        "Action Verbs": score_action_verbs(ats_result),
        "Achievements": score_achievements(ats_result),
        "Contact Information": score_contact_information(ats_result),
    }


def generate_strengths(
    ats_result: dict[str, Any],
) -> list[str]:
    """Identify strong areas of the resume."""
    strengths: list[str] = []

    section_score = score_section_completeness(ats_result)
    formatting_score = score_formatting(ats_result)
    keyword_score = score_keywords(ats_result)
    action_score = score_action_verbs(ats_result)
    achievement_score = score_achievements(ats_result)
    contact_score = score_contact_information(ats_result)

    if section_score >= 80:
        strengths.append(
            "Resume contains most important professional sections."
        )

    if formatting_score >= 80:
        strengths.append(
            "Resume structure appears reasonably ATS-friendly."
        )

    if keyword_score >= 50:
        strengths.append(
            "Resume contains a useful set of relevant keywords."
        )

    if action_score >= 40:
        strengths.append(
            "Resume uses strong action-oriented language."
        )

    if achievement_score >= 40:
        strengths.append(
            "Resume includes measurable achievements or results."
        )

    if contact_score >= 75:
        strengths.append(
            "Most important contact information was detected."
        )

    return strengths


def generate_improvements(
    ats_result: dict[str, Any],
) -> list[str]:
    """Identify areas that should be improved."""
    improvements: list[str] = []

    section_score = score_section_completeness(ats_result)
    formatting_score = score_formatting(ats_result)
    keyword_score = score_keywords(ats_result)
    action_score = score_action_verbs(ats_result)
    achievement_score = score_achievements(ats_result)
    contact_score = score_contact_information(ats_result)

    if section_score < 80:
        improvements.append(
            "Add or strengthen important resume sections such as "
            "Summary, Experience, Education, Skills, and Projects."
        )

    if formatting_score < 80:
        formatting = ats_result.get("formatting", {})
        issues = formatting.get("issues", [])

        if issues:
            improvements.extend(
                str(issue)
                for issue in issues[:3]
            )
        else:
            improvements.append(
                "Improve formatting and ATS readability."
            )

    if keyword_score < 50:
        improvements.append(
            "Add more relevant technical and role-specific keywords."
        )

    if action_score < 40:
        improvements.append(
            "Use stronger action verbs when describing your work."
        )

    if achievement_score < 40:
        improvements.append(
            "Add measurable results such as percentages, numbers, "
            "performance improvements, users, or project outcomes."
        )

    if contact_score < 75:
        improvements.append(
            "Complete your contact information, including email, "
            "phone, LinkedIn, or GitHub where appropriate."
        )

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(improvements))


def analyze_resume_score(
    ats_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate the complete resume scoring report.
    """
    overall_score = calculate_overall_score(ats_result)

    return {
        "overall_score": overall_score,
        "grade": get_score_grade(overall_score),
        "category": get_score_color(overall_score),
        "breakdown": generate_score_breakdown(ats_result),
        "strengths": generate_strengths(ats_result),
        "improvements": generate_improvements(ats_result),
    }