from __future__ import annotations

import re
from collections import Counter
from typing import Iterable


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    if not text:
        return ""

    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text: str) -> list[str]:
    """Convert text into searchable tokens."""
    normalized = normalize_text(text)

    if not normalized:
        return []

    return re.findall(
        r"[a-zA-Z0-9+#./-]+",
        normalized,
    )


def extract_keywords(
    text: str,
    candidate_keywords: Iterable[str],
) -> list[str]:
    """
    Find which candidate keywords occur in a text.
    """
    normalized_text = normalize_text(text)
    found = []

    for keyword in candidate_keywords:
        normalized_keyword = normalize_text(keyword)

        if not normalized_keyword:
            continue

        escaped = re.escape(normalized_keyword)
        pattern = rf"(?<![a-z0-9+#]){escaped}(?![a-z0-9+#])"

        if re.search(pattern, normalized_text):
            found.append(keyword)

    return sorted(set(found), key=str.lower)


def calculate_keyword_overlap(
    resume_text: str,
    job_description: str,
) -> dict[str, object]:
    """
    Compare resume keywords against the words found in a job description.
    """
    resume_tokens = set(tokenize(resume_text))
    job_tokens = set(tokenize(job_description))

    if not job_tokens:
        return {
            "matched_keywords": [],
            "missing_keywords": [],
            "match_percentage": 0.0,
        }

    matched = sorted(
        resume_tokens.intersection(job_tokens)
    )

    missing = sorted(
        job_tokens.difference(resume_tokens)
    )

    percentage = round(
        (len(matched) / len(job_tokens)) * 100,
        2,
    )

    return {
        "matched_keywords": matched,
        "missing_keywords": missing,
        "match_percentage": percentage,
    }


def calculate_skill_match(
    resume_skills: Iterable[str],
    required_skills: Iterable[str],
) -> dict[str, object]:
    """
    Compare skills detected in a resume with required job skills.
    """
    resume_map = {
        skill.strip().lower(): skill.strip()
        for skill in resume_skills
        if skill and skill.strip()
    }

    required_map = {
        skill.strip().lower(): skill.strip()
        for skill in required_skills
        if skill and skill.strip()
    }

    if not required_map:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "skill_match_percentage": 0.0,
        }

    matched_keys = set(resume_map).intersection(required_map)
    missing_keys = set(required_map).difference(resume_map)

    matched_skills = sorted(
        [required_map[key] for key in matched_keys],
        key=str.lower,
    )

    missing_skills = sorted(
        [required_map[key] for key in missing_keys],
        key=str.lower,
    )

    percentage = round(
        (len(matched_keys) / len(required_map)) * 100,
        2,
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": percentage,
    }


def calculate_text_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """
    Calculate a lightweight cosine-style similarity based on word frequency.

    This does not require a machine-learning model and provides a useful
    baseline before adding semantic embeddings.
    """
    resume_tokens = tokenize(resume_text)
    job_tokens = tokenize(job_description)

    if not resume_tokens or not job_tokens:
        return 0.0

    resume_counter = Counter(resume_tokens)
    job_counter = Counter(job_tokens)

    vocabulary = set(resume_counter).union(job_counter)

    resume_vector = [
        resume_counter.get(word, 0)
        for word in vocabulary
    ]

    job_vector = [
        job_counter.get(word, 0)
        for word in vocabulary
    ]

    dot_product = sum(
        a * b
        for a, b in zip(resume_vector, job_vector)
    )

    resume_magnitude = sum(
        value * value
        for value in resume_vector
    ) ** 0.5

    job_magnitude = sum(
        value * value
        for value in job_vector
    ) ** 0.5

    if resume_magnitude == 0 or job_magnitude == 0:
        return 0.0

    similarity = (
        dot_product
        / (resume_magnitude * job_magnitude)
    )

    return round(similarity * 100, 2)


def calculate_match_score(
    skill_match_percentage: float,
    keyword_match_percentage: float,
    text_similarity: float,
) -> float:
    """
    Calculate the overall resume-to-job match score.
    """
    score = (
        skill_match_percentage * 0.50
        + keyword_match_percentage * 0.30
        + text_similarity * 0.20
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def analyze_job_match(
    resume_text: str,
    job_description: str,
    resume_skills: Iterable[str] | None = None,
    required_skills: Iterable[str] | None = None,
) -> dict[str, object]:
    """
    Run the complete resume-to-job matching analysis.
    """
    resume_skills = list(resume_skills or [])
    required_skills = list(required_skills or [])

    skill_results = calculate_skill_match(
        resume_skills,
        required_skills,
    )

    keyword_results = calculate_keyword_overlap(
        resume_text,
        job_description,
    )

    similarity = calculate_text_similarity(
        resume_text,
        job_description,
    )

    overall_score = calculate_match_score(
        skill_match_percentage=float(
            skill_results["skill_match_percentage"]
        ),
        keyword_match_percentage=float(
            keyword_results["match_percentage"]
        ),
        text_similarity=similarity,
    )

    return {
        "overall_match_score": overall_score,
        "skill_match": skill_results,
        "keyword_match": keyword_results,
        "text_similarity": similarity,
    }