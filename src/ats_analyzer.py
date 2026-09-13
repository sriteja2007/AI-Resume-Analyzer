from __future__ import annotations

import re
from typing import Any


SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "work history",
    ],
    "education": [
        "education",
        "academic background",
        "qualifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "competencies",
        "technical expertise",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses",
    ],
    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
    ],
}


COMMON_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "sql",
    "html",
    "css",
    "react",
    "node",
    "express",
    "mongodb",
    "mysql",
    "postgresql",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "gcp",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "nlp",
    "computer vision",
    "api",
    "rest",
    "agile",
    "communication",
    "leadership",
    "problem solving",
]


ACTION_VERBS = [
    "developed",
    "built",
    "created",
    "designed",
    "implemented",
    "engineered",
    "optimized",
    "automated",
    "analyzed",
    "managed",
    "led",
    "improved",
    "deployed",
    "integrated",
    "developed",
    "tested",
    "maintained",
    "configured",
    "programmed",
    "trained",
    "evaluated",
    "delivered",
    "launched",
    "architected",
]


def _normalize(text: str) -> str:
    """Normalize text for matching."""

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _normalize_heading(text: str) -> str:
    """Normalize a possible resume heading."""

    text = _normalize(text)
    text = re.sub(r"[^a-z0-9+#& ]", "", text)

    return text.strip()


def detect_sections(text: str) -> dict[str, bool]:
    """Detect standard resume sections."""

    normalized_text = _normalize(text)

    detected = {}

    for section, aliases in SECTION_ALIASES.items():
        detected[section] = any(
            alias in normalized_text
            for alias in aliases
        )

    return detected


def find_contact_information(text: str) -> dict[str, Any]:
    """Detect common contact information."""

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    phone_pattern = (
        r"(?:\+91[-\s]?)?"
        r"(?:\d{10}|\d{5}[-\s]\d{5})"
    )

    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/[A-Za-z0-9_/?=&%-]+"

    github_pattern = r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_/?=&%-]+"

    email_match = re.search(
        email_pattern,
        text,
        re.IGNORECASE,
    )

    phone_match = re.search(
        phone_pattern,
        text,
    )

    linkedin_match = re.search(
        linkedin_pattern,
        text,
        re.IGNORECASE,
    )

    github_match = re.search(
        github_pattern,
        text,
        re.IGNORECASE,
    )

    return {
        "email": email_match.group(0)
        if email_match
        else None,

        "phone": phone_match.group(0)
        if phone_match
        else None,

        "linkedin": linkedin_match.group(0)
        if linkedin_match
        else None,

        "github": github_match.group(0)
        if github_match
        else None,
    }


def calculate_keyword_density(
    text: str,
    keywords: list[str],
) -> float:
    """Calculate keyword density."""

    normalized_text = _normalize(text)

    if not normalized_text:
        return 0.0

    words = normalized_text.split()

    if not words:
        return 0.0

    matches = 0

    for keyword in keywords:
        keyword_normalized = _normalize(keyword)

        if keyword_normalized in normalized_text:
            matches += 1

    density = (
        matches / len(keywords) * 100
        if keywords
        else 0.0
    )

    return round(
        min(100.0, density),
        2,
    )


def find_keywords(
    text: str,
) -> list[str]:
    """Find common technical and professional keywords."""

    normalized_text = _normalize(text)

    found = []

    for keyword in COMMON_KEYWORDS:
        if keyword.lower() in normalized_text:
            found.append(keyword)

    return found


def find_action_verbs(
    text: str,
) -> list[str]:
    """Find action verbs."""

    normalized_text = _normalize(text)

    found = []

    for verb in ACTION_VERBS:
        if re.search(
            rf"\b{re.escape(verb)}\b",
            normalized_text,
        ):
            found.append(verb)

    return found


def detect_quantifiable_achievements(
    text: str,
) -> list[str]:
    """Detect resume statements containing measurable results."""

    patterns = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\s*(?:k|m|b)\b",
        r"\b\d+\+\b",
        r"\b\d+(?:\.\d+)?\s*(?:users|clients|customers|projects|employees|members)\b",
        r"\b(?:increased|decreased|improved|reduced|saved|grew|boosted)\b.{0,100}\b\d+(?:\.\d+)?",
    ]

    results = []

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        results.extend(matches)

    # Remove duplicates while preserving order.
    unique_results = []

    for result in results:
        if result not in unique_results:
            unique_results.append(result)

    return unique_results


def calculate_section_score(
    detected_sections: dict[str, bool],
) -> float:
    """Calculate section completeness score."""

    if not detected_sections:
        return 0.0

    important_sections = [
        "summary",
        "experience",
        "education",
        "skills",
        "projects",
    ]

    found = sum(
        1
        for section in important_sections
        if detected_sections.get(section, False)
    )

    return round(
        found / len(important_sections) * 100,
        2,
    )


def evaluate_formatting(
    text: str,
) -> float:
    """Evaluate basic ATS-friendly formatting."""

    if not text:
        return 0.0

    score = 100.0

    lines = text.splitlines()

    if len(text) < 300:
        score -= 25

    if len(lines) < 5:
        score -= 15

    # Excessive special characters can hurt ATS parsing.
    special_characters = len(
        re.findall(
            r"[^\w\s.,@+#&%()/:-]",
            text,
            flags=re.UNICODE,
        )
    )

    if len(text) > 0:
        special_ratio = (
            special_characters / len(text)
        )

        if special_ratio > 0.05:
            score -= 15

    # Extremely long lines may indicate poor extraction.
    long_lines = sum(
        1
        for line in lines
        if len(line) > 180
    )

    if long_lines > 3:
        score -= 10

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def calculate_keyword_score(
    text: str,
    keywords: list[str],
) -> float:
    """Calculate keyword score."""

    if not keywords:
        return 0.0

    normalized_text = _normalize(text)

    matched = sum(
        1
        for keyword in keywords
        if _normalize(keyword) in normalized_text
    )

    return round(
        min(
            100.0,
            matched / len(keywords) * 100,
        ),
        2,
    )


def calculate_action_verb_score(
    action_verbs: list[str],
) -> float:
    """Calculate action verb score."""

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


def calculate_achievement_score(
    achievements: list[str],
) -> float:
    """Calculate measurable achievement score."""

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


def calculate_contact_score(
    contact_information: dict[str, Any],
) -> float:
    """Calculate contact information score."""

    fields = [
        "email",
        "phone",
        "linkedin",
        "github",
    ]

    found = sum(
        1
        for field in fields
        if contact_information.get(field)
    )

    if found == 4:
        return 100.0

    if found == 3:
        return 85.0

    if found == 2:
        return 70.0

    if found == 1:
        return 45.0

    return 0.0


def calculate_ats_score(
    section_score: float,
    formatting_score: float,
    keyword_score: float,
    action_verb_score: float,
    achievement_score: float,
    contact_score: float,
) -> float:
    """Calculate the final ATS score."""

    score = (
        section_score * 0.30
        + formatting_score * 0.25
        + keyword_score * 0.15
        + action_verb_score * 0.10
        + achievement_score * 0.10
        + contact_score * 0.10
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def analyze_ats(
    text: str,
) -> dict[str, Any]:
    """
    Complete ATS analysis.

    Returns a dictionary consumed by both the
    Streamlit application and resume scorer.
    """

    if not text or not text.strip():
        return {
            "ats_score": 0.0,
            "section_score": {},
            "section_completeness_score": 0.0,
            "formatting_score": 0.0,
            "keyword_score": 0.0,
            "action_verb_score": 0.0,
            "achievement_score": 0.0,
            "contact_score": 0.0,
            "action_verbs": [],
            "quantifiable_achievements": [],
            "keywords": [],
            "contact_information": {},
            "detected_sections": {},
            "breakdown": {},
        }

    detected_sections = detect_sections(text)

    contact_information = find_contact_information(text)

    keywords = find_keywords(text)

    action_verbs = find_action_verbs(text)

    achievements = detect_quantifiable_achievements(text)

    section_completeness_score = calculate_section_score(
        detected_sections
    )

    formatting_score = evaluate_formatting(
        text
    )

    keyword_score = calculate_keyword_score(
        text,
        COMMON_KEYWORDS,
    )

    action_verb_score = calculate_action_verb_score(
        action_verbs
    )

    achievement_score = calculate_achievement_score(
        achievements
    )

    contact_score = calculate_contact_score(
        contact_information
    )

    ats_score = calculate_ats_score(
        section_score=section_completeness_score,
        formatting_score=formatting_score,
        keyword_score=keyword_score,
        action_verb_score=action_verb_score,
        achievement_score=achievement_score,
        contact_score=contact_score,
    )

    section_score = {
        "summary": 100.0
        if detected_sections.get("summary")
        else 0.0,

        "experience": 100.0
        if detected_sections.get("experience")
        else 0.0,

        "education": 100.0
        if detected_sections.get("education")
        else 0.0,

        "skills": 100.0
        if detected_sections.get("skills")
        else 0.0,

        "projects": 100.0
        if detected_sections.get("projects")
        else 0.0,
    }

    breakdown = {
        "Section Completeness": section_completeness_score,
        "Formatting": formatting_score,
        "Keywords": keyword_score,
        "Action Verbs": action_verb_score,
        "Achievements": achievement_score,
        "Contact Information": contact_score,
    }

    return {
        "ats_score": ats_score,

        "section_score": section_score,

        "section_completeness_score": section_completeness_score,

        "formatting_score": formatting_score,

        "keyword_score": keyword_score,

        "action_verb_score": action_verb_score,

        "achievement_score": achievement_score,

        "contact_score": contact_score,

        "action_verbs": action_verbs,

        "quantifiable_achievements": achievements,

        "keywords": keywords,

        "contact_information": contact_information,

        "detected_sections": detected_sections,

        "breakdown": breakdown,
    }