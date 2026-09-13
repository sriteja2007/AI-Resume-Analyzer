from __future__ import annotations

import re
from typing import Any

from src.skill_extractor import extract_skills


# Common job-related keywords
JOB_KEYWORDS = {
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "next.js",
    "node.js",
    "express",
    "mongodb",
    "mysql",
    "postgresql",
    "sql",
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
    "cloud computing",
    "rest api",
    "api",
    "communication",
    "leadership",
    "problem solving",
    "teamwork",
    "project management",
}


def normalize_text(text: str) -> str:
    """Normalize text for matching."""

    if not text:
        return ""

    text = text.lower()

    # Normalize common technology variations
    replacements = {
        "node js": "node.js",
        "nodejs": "node.js",
        "next js": "next.js",
        "nextjs": "next.js",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "artificial-intelligence": "artificial intelligence",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize_text(text: str) -> set[str]:
    """Convert text into normalized tokens."""

    normalized = normalize_text(text)

    if not normalized:
        return set()

    return set(
        re.findall(
            r"[a-zA-Z0-9+#.]+",
            normalized,
        )
    )


def extract_job_keywords(
    job_description: str,
) -> list[str]:
    """Extract important keywords from a job description."""

    normalized = normalize_text(
        job_description
    )

    found = []

    for keyword in JOB_KEYWORDS:
        if keyword in normalized:
            found.append(keyword)

    return sorted(
        found,
        key=len,
        reverse=True,
    )


def extract_required_skills(
    job_description: str,
) -> list[str]:
    """
    Extract technical and soft skills from the
    job description using the same skill engine
    used for resumes.
    """

    if not job_description.strip():
        return []

    extracted = extract_skills(
        job_description
    )

    technical = extracted.get(
        "technical_skills",
        [],
    )

    soft = extracted.get(
        "soft_skills",
        [],
    )

    all_skills = extracted.get(
        "all_skills",
        [],
    )

    # Prefer all_skills if available.
    if all_skills:
        return sorted(
            set(all_skills),
            key=str.lower,
        )

    return sorted(
        set(technical + soft),
        key=str.lower,
    )


def calculate_keyword_overlap(
    resume_text: str,
    job_description: str,
) -> dict[str, Any]:
    """Calculate keyword overlap between resume and job."""

    resume_normalized = normalize_text(
        resume_text
    )

    job_keywords = extract_job_keywords(
        job_description
    )

    matched = []
    missing = []

    for keyword in job_keywords:
        if keyword in resume_normalized:
            matched.append(keyword)
        else:
            missing.append(keyword)

    if job_keywords:
        score = (
            len(matched)
            / len(job_keywords)
            * 100
        )
    else:
        score = 0.0

    return {
        "job_keywords": job_keywords,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "keyword_match_score": round(
            score,
            2,
        ),
    }


def calculate_skill_match(
    resume_skills: list[str],
    required_skills: list[str],
) -> dict[str, Any]:
    """Compare resume skills with job-required skills."""

    resume_set = {
        normalize_text(skill)
        for skill in resume_skills
    }

    required_set = {
        normalize_text(skill)
        for skill in required_skills
    }

    matched = sorted(
        [
            skill
            for skill in required_set
            if skill in resume_set
        ]
    )

    missing = sorted(
        [
            skill
            for skill in required_set
            if skill not in resume_set
        ]
    )

    if required_set:
        score = (
            len(matched)
            / len(required_set)
            * 100
        )
    else:
        score = 0.0

    return {
        "required_skills": sorted(
            required_set
        ),
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_score": round(
            score,
            2,
        ),
    }


def calculate_text_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """
    Lightweight token-overlap similarity.

    This is intentionally simple and explainable.
    """

    resume_tokens = tokenize_text(
        resume_text
    )

    job_tokens = tokenize_text(
        job_description
    )

    if not resume_tokens or not job_tokens:
        return 0.0

    intersection = (
        resume_tokens & job_tokens
    )

    union = (
        resume_tokens | job_tokens
    )

    if not union:
        return 0.0

    similarity = (
        len(intersection)
        / len(union)
        * 100
    )

    return round(
        similarity,
        2,
    )


def calculate_overall_match_score(
    keyword_score: float,
    skill_score: float,
    similarity_score: float,
) -> float:
    """
    Calculate overall job match score.

    Weighting:
    - Skills: 45%
    - Keywords: 35%
    - Text similarity: 20%
    """

    score = (
        skill_score * 0.45
        + keyword_score * 0.35
        + similarity_score * 0.20
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        ),
        2,
    )


def generate_recommendations(
    missing_skills: list[str],
    missing_keywords: list[str],
    keyword_score: float,
    skill_score: float,
) -> list[str]:
    """Generate actionable job-match recommendations."""

    recommendations = []

    if missing_skills:
        skills_text = ", ".join(
            missing_skills[:8]
        )

        recommendations.append(
            f"Consider adding relevant skills such as {skills_text} "
            "if you genuinely have experience with them."
        )

    if missing_keywords:
        keywords_text = ", ".join(
            missing_keywords[:8]
        )

        recommendations.append(
            f"Review your resume for relevant job keywords such as "
            f"{keywords_text} and include them naturally where accurate."
        )

    if skill_score < 50:
        recommendations.append(
            "Your resume currently shows limited alignment "
            "with the required skills for this role."
        )

    elif skill_score < 75:
        recommendations.append(
            "Your skill alignment is moderate. Highlight your "
            "strongest matching technologies more prominently."
        )

    else:
        recommendations.append(
            "Your resume demonstrates strong alignment with "
            "the technical and professional skills detected."
        )

    if keyword_score < 50:
        recommendations.append(
            "Improve keyword alignment by tailoring your resume "
            "to the terminology used in the target job description."
        )

    elif keyword_score < 75:
        recommendations.append(
            "Your keyword alignment is moderate. Tailor relevant "
            "experience and project descriptions to the target role."
        )

    return recommendations


def analyze_job_match(
    resume_text: str,
    job_description: str,
    resume_skills: list[str] | None = None,
) -> dict[str, Any]:
    """Perform complete resume-to-job matching."""

    if not resume_text.strip():
        return {
            "overall_match_score": 0.0,
            "keyword_match_score": 0.0,
            "skill_match_score": 0.0,
            "text_similarity_score": 0.0,
            "job_keywords": [],
            "matched_keywords": [],
            "missing_keywords": [],
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": [],
        }

    if not job_description.strip():
        return {
            "overall_match_score": 0.0,
            "keyword_match_score": 0.0,
            "skill_match_score": 0.0,
            "text_similarity_score": 0.0,
            "job_keywords": [],
            "matched_keywords": [],
            "missing_keywords": [],
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": [
                "Add a job description to perform job matching."
            ],
        }

    if resume_skills is None:
        resume_result = extract_skills(
            resume_text
        )

        resume_skills = resume_result.get(
            "all_skills",
            [],
        )

    keyword_result = calculate_keyword_overlap(
        resume_text,
        job_description,
    )

    required_skills = extract_required_skills(
        job_description
    )

    skill_result = calculate_skill_match(
        resume_skills,
        required_skills,
    )

    similarity_score = calculate_text_similarity(
        resume_text,
        job_description,
    )

    overall_score = calculate_overall_match_score(
        keyword_score=keyword_result[
            "keyword_match_score"
        ],
        skill_score=skill_result[
            "skill_match_score"
        ],
        similarity_score=similarity_score,
    )

    recommendations = generate_recommendations(
        missing_skills=skill_result[
            "missing_skills"
        ],
        missing_keywords=keyword_result[
            "missing_keywords"
        ],
        keyword_score=keyword_result[
            "keyword_match_score"
        ],
        skill_score=skill_result[
            "skill_match_score"
        ],
    )

    return {
        "overall_match_score": overall_score,

        "keyword_match_score": keyword_result[
            "keyword_match_score"
        ],

        "skill_match_score": skill_result[
            "skill_match_score"
        ],

        "text_similarity_score": similarity_score,

        "job_keywords": keyword_result[
            "job_keywords"
        ],

        "matched_keywords": keyword_result[
            "matched_keywords"
        ],

        "missing_keywords": keyword_result[
            "missing_keywords"
        ],

        "required_skills": skill_result[
            "required_skills"
        ],

        "matched_skills": skill_result[
            "matched_skills"
        ],

        "missing_skills": skill_result[
            "missing_skills"
        ],

        "recommendations": recommendations,
    }