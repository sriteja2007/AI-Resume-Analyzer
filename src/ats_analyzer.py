from __future__ import annotations

import re
from typing import Iterable


SECTION_ALIASES = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
        "about me",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
    },
    "education": {
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
    },
    "skills": {
        "skills",
        "technical skills",
        "technical expertise",
        "core skills",
        "competencies",
    },
    "projects": {
        "projects",
        "academic projects",
        "personal projects",
        "project experience",
    },
    "certifications": {
        "certifications",
        "certificates",
        "licenses",
        "licenses & certifications",
    },
    "achievements": {
        "achievements",
        "accomplishments",
        "awards",
        "honors",
    },
    "internships": {
        "internships",
        "internship experience",
    },
}


COMMON_KEYWORDS = {
    "experience",
    "education",
    "skills",
    "project",
    "projects",
    "internship",
    "internships",
    "certification",
    "certifications",
    "achievement",
    "achievements",
    "team",
    "leadership",
    "communication",
    "developed",
    "implemented",
    "designed",
    "managed",
    "improved",
}


ACTION_VERBS = {
    "achieved",
    "analyzed",
    "automated",
    "built",
    "collaborated",
    "created",
    "deployed",
    "designed",
    "developed",
    "engineered",
    "implemented",
    "improved",
    "integrated",
    "led",
    "managed",
    "optimized",
    "programmed",
    "reduced",
    "resolved",
    "tested",
}


def _normalize(text: str) -> str:
    """Normalize text for ATS-style matching."""
    if not text:
        return ""

    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _normalize_heading(text: str) -> str:
    """Normalize a potential resume section heading."""
    heading = _normalize(text)
    heading = re.sub(r"[^a-z0-9&+/#\-\s]", "", heading)
    heading = re.sub(r"\s+", " ", heading)

    return heading.strip()


def detect_sections(text: str) -> dict[str, str]:
    """
    Detect common resume sections from headings.

    Returns a dictionary containing the recognized sections and
    their associated text.
    """
    if not text:
        return {}

    lines = text.splitlines()

    detected: dict[str, list[str]] = {}
    current_section: str | None = None

    heading_lookup: dict[str, str] = {}

    for canonical_name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            heading_lookup[_normalize_heading(alias)] = canonical_name

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        normalized_heading = _normalize_heading(line)

        if normalized_heading in heading_lookup:
            current_section = heading_lookup[normalized_heading]

            if current_section not in detected:
                detected[current_section] = []

            continue

        if current_section is not None:
            detected[current_section].append(line)

    return {
        section: "\n".join(content).strip()
        for section, content in detected.items()
        if content
    }


def find_contact_information(text: str) -> dict[str, bool]:
    """Check for common contact details."""
    email_found = bool(
        re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text,
        )
    )

    phone_found = bool(
        re.search(
            r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
            text,
        )
    )

    linkedin_found = "linkedin.com" in _normalize(text)
    github_found = "github.com" in _normalize(text)

    return {
        "email": email_found,
        "phone": phone_found,
        "linkedin": linkedin_found,
        "github": github_found,
    }


def calculate_keyword_density(
    text: str,
    keywords: Iterable[str],
) -> dict[str, float]:
    """
    Calculate approximate keyword frequency percentage.

    The returned values represent how often each keyword appears
    relative to the total number of words.
    """
    normalized_text = _normalize(text)

    words = re.findall(r"[a-z0-9+#.-]+", normalized_text)
    total_words = len(words)

    if total_words == 0:
        return {
            keyword: 0.0
            for keyword in keywords
        }

    result: dict[str, float] = {}

    for keyword in keywords:
        normalized_keyword = _normalize(keyword)

        if not normalized_keyword:
            continue

        occurrences = len(
            re.findall(
                rf"(?<![a-z0-9]){re.escape(normalized_keyword)}(?![a-z0-9])",
                normalized_text,
            )
        )

        result[keyword] = round(
            (occurrences / total_words) * 100,
            2,
        )

    return result


def find_keywords(text: str) -> list[str]:
    """Find common ATS-relevant keywords appearing in the resume."""
    normalized_text = _normalize(text)

    found = []

    for keyword in sorted(COMMON_KEYWORDS):
        pattern = rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])"

        if re.search(pattern, normalized_text):
            found.append(keyword)

    return found


def find_action_verbs(text: str) -> list[str]:
    """Find strong action verbs used in the resume."""
    normalized_text = _normalize(text)

    found = []

    for verb in sorted(ACTION_VERBS):
        pattern = rf"(?<![a-z0-9]){re.escape(verb)}(?![a-z0-9])"

        if re.search(pattern, normalized_text):
            found.append(verb)

    return found


def detect_quantifiable_achievements(text: str) -> dict[str, int | float]:
    """
    Estimate the presence of measurable achievements.

    Looks for:
    - percentages
    - currency values
    - numerical improvements
    - numbers followed by common units
    """
    if not text:
        return {
            "count": 0,
            "percentage_mentions": 0,
            "currency_mentions": 0,
            "number_mentions": 0,
        }

    percentages = re.findall(
        r"\b\d+(?:\.\d+)?\s*%",
        text,
    )

    currencies = re.findall(
        r"(?:₹|\$|€|£)\s?\d+(?:,\d{3})*(?:\.\d+)?",
        text,
    )

    numerical_results = re.findall(
        r"\b\d+(?:\.\d+)?\s*(?:x|k|m|b|years?|months?|days?|users?|projects?|"
        r"clients?|students?|customers?|hours?|days?|weeks?)\b",
        text,
        flags=re.IGNORECASE,
    )

    count = (
        len(percentages)
        + len(currencies)
        + len(numerical_results)
    )

    return {
        "count": count,
        "percentage_mentions": len(percentages),
        "currency_mentions": len(currencies),
        "number_mentions": len(numerical_results),
    }


def calculate_section_score(
    sections: dict[str, str],
) -> dict[str, float]:
    """
    Score the presence of important resume sections.

    This is a heuristic ATS-style score, not a guarantee of
    acceptance by a particular ATS product.
    """
    expected_sections = {
        "summary": 10,
        "experience": 25,
        "education": 20,
        "skills": 20,
        "projects": 15,
        "certifications": 10,
    }

    total_possible = sum(expected_sections.values())
    earned = 0

    breakdown: dict[str, float] = {}

    normalized_sections = {
        key.lower(): value
        for key, value in sections.items()
    }

    for section, weight in expected_sections.items():
        present = bool(
            normalized_sections.get(section, "").strip()
        )

        points = float(weight if present else 0)
        earned += points
        breakdown[section] = points

    score = (
        earned / total_possible * 100
        if total_possible
        else 0.0
    )

    breakdown["total"] = round(score, 2)

    return breakdown


def evaluate_formatting(text: str) -> dict[str, int | list[str]]:
    """
    Run basic ATS-friendly formatting checks.
    """
    issues: list[str] = []
    score = 100

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "score": 0,
            "issues": ["No readable resume text detected."],
        }

    if len(text) < 500:
        issues.append(
            "Resume appears very short and may lack sufficient detail."
        )
        score -= 20

    if len(text) > 15000:
        issues.append(
            "Resume is very long; consider reducing unnecessary content."
        )
        score -= 10

    contact = find_contact_information(text)

    if not contact["email"]:
        issues.append("Email address was not detected.")
        score -= 15

    if not contact["phone"]:
        issues.append("Phone number was not detected.")
        score -= 10

    sections = detect_sections(text)

    if "skills" not in sections:
        issues.append("Skills section was not detected.")
        score -= 15

    if "experience" not in sections and "projects" not in sections:
        issues.append(
            "Neither Experience nor Projects section was detected."
        )
        score -= 15

    if "education" not in sections:
        issues.append("Education section was not detected.")
        score -= 10

    # Excessive special-character density can indicate parsing problems.
    special_chars = len(re.findall(r"[|•►◆★■]", text))
    if len(text) > 0 and special_chars / len(text) > 0.03:
        issues.append(
            "Resume contains many decorative symbols that may affect ATS parsing."
        )
        score -= 10

    score = max(0, min(100, score))

    return {
        "score": score,
        "issues": issues,
    }


def analyze_ats(text: str) -> dict:
    """
    Run the complete ATS analysis pipeline.
    """
    sections = detect_sections(text)
    contact_information = find_contact_information(text)
    keywords = find_keywords(text)
    action_verbs = find_action_verbs(text)
    measurable_results = detect_quantifiable_achievements(text)

    section_score = calculate_section_score(sections)
    formatting = evaluate_formatting(text)

    keyword_score = min(
        100,
        round((len(keywords) / len(COMMON_KEYWORDS)) * 100, 2),
    )

    action_verb_score = min(
        100,
        round((len(action_verbs) / len(ACTION_VERBS)) * 100, 2),
    )

    achievement_score = min(
        100,
        measurable_results["count"] * 20,
    )

    contact_score = round(
        (
            sum(
                1
                for value in contact_information.values()
                if value
            )
            / len(contact_information)
        )
        * 100,
        2,
    )

    overall_score = round(
        (
            section_score["total"] * 0.35
            + formatting["score"] * 0.30
            + keyword_score * 0.15
            + action_verb_score * 0.10
            + achievement_score * 0.05
            + contact_score * 0.05
        ),
        2,
    )

    return {
        "overall_score": overall_score,
        "sections": sections,
        "section_score": section_score,
        "formatting": formatting,
        "contact_information": contact_information,
        "keywords": keywords,
        "keyword_score": keyword_score,
        "action_verbs": action_verbs,
        "action_verb_score": action_verb_score,
        "measurable_results": measurable_results,
        "achievement_score": achievement_score,
        "contact_score": contact_score,
        "keyword_density": calculate_keyword_density(
            text,
            keywords,
        ),
    }