from __future__ import annotations

import json
import os
from typing import Any

from google import genai
from google.genai import types


DEFAULT_MODEL = "gemini-3.5-flash-lite"


def configure_gemini(api_key: str | None = None):
    """
    Create and return a Gemini client.

    API key priority:
    1. Explicit api_key argument
    2. GEMINI_API_KEY environment variable
    """

    key = api_key or os.getenv("GEMINI_API_KEY")

    if not key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(api_key=key)


def _get_model_client(
    api_key: str | None = None,
):
    return configure_gemini(api_key)


def build_resume_analysis_prompt(
    resume_text: str,
    job_description: str = "",
) -> str:
    """
    Build the prompt used for resume analysis.
    """

    job_context = ""

    if job_description.strip():
        job_context = f"""
TARGET JOB DESCRIPTION:
{job_description}

Analyze the resume specifically against this job description.
Identify missing skills, missing keywords and alignment gaps.
"""

    return f"""
You are an expert ATS resume analyst and career coach.

Analyze the following resume professionally.

RESUME:
{resume_text}

{job_context}

Provide a detailed but practical analysis.

Return ONLY valid JSON using exactly this structure:

{{
    "summary": "A concise professional summary of the resume.",
    "overall_assessment": "Overall assessment of the resume.",
    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2",
        "weakness 3"
    ],
    "missing_keywords": [
        "keyword 1",
        "keyword 2"
    ],
    "missing_skills": [
        "skill 1",
        "skill 2"
    ],
    "recommendations": [
        "specific recommendation 1",
        "specific recommendation 2",
        "specific recommendation 3"
    ],
    "ats_improvements": [
        "ATS improvement 1",
        "ATS improvement 2"
    ],
    "career_advice": [
        "career advice 1",
        "career advice 2"
    ]
}}

Rules:

- Do not invent experience.
- Do not invent skills that are not present.
- Do not make false claims.
- Base your analysis only on the provided resume.
- Be specific and actionable.
- Focus on improving employability.
- If a job description is provided, prioritize job-specific gaps.
- Keep each recommendation concise.
"""


def _parse_json_response(
    response_text: str,
) -> dict[str, Any]:
    """
    Safely convert Gemini JSON output into a dictionary.
    """

    if not response_text:
        return {
            "summary": "",
            "overall_assessment": "",
            "strengths": [],
            "weaknesses": [],
            "missing_keywords": [],
            "missing_skills": [],
            "recommendations": [],
            "ats_improvements": [],
            "career_advice": [],
        }

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]

    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    return {
        "summary": cleaned,
        "overall_assessment": cleaned,
        "strengths": [],
        "weaknesses": [],
        "missing_keywords": [],
        "missing_skills": [],
        "recommendations": [],
        "ats_improvements": [],
        "career_advice": [],
    }


def analyze_resume_with_ai(
    resume_text: str,
    job_description: str = "",
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    Analyze a resume using Gemini.
    """

    if not resume_text.strip():
        raise ValueError(
            "Resume text cannot be empty."
        )

    client = _get_model_client(api_key)

    prompt = build_resume_analysis_prompt(
        resume_text=resume_text,
        job_description=job_description,
    )

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=2500,
            response_mime_type="application/json",
        ),
    )

    return _parse_json_response(
        response.text
    )


def generate_resume_summary(
    resume_text: str,
    api_key: str | None = None,
) -> str:
    """
    Generate a professional resume summary.
    """

    client = _get_model_client(api_key)

    prompt = f"""
Write a professional 3-5 sentence summary of this resume.

Do not invent information.

Resume:
{resume_text}
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=500,
        ),
    )

    return response.text.strip()


def generate_job_match_recommendations(
    resume_text: str,
    job_description: str,
    api_key: str | None = None,
) -> str:
    """
    Generate personalized recommendations for a target job.
    """

    client = _get_model_client(api_key)

    prompt = f"""
Compare this resume against the target job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide:

1. Matching strengths
2. Missing skills
3. Missing keywords
4. Resume improvements
5. Specific recommendations

Do not invent experience or qualifications.
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1500,
        ),
    )

    return response.text.strip()