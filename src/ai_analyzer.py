from __future__ import annotations

import os
from typing import Any

import google.generativeai as genai


DEFAULT_MODEL = "gemini-2.0-flash"


def configure_gemini(api_key: str | None = None) -> bool:
    """
    Configure Gemini using an API key.

    The API key can be passed directly or loaded from
    the GEMINI_API_KEY environment variable.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")

    if not key:
        return False

    genai.configure(api_key=key)
    return True


def _get_model(model_name: str = DEFAULT_MODEL):
    """Create and return the Gemini model."""
    return genai.GenerativeModel(model_name)


def build_resume_analysis_prompt(
    resume_text: str,
    job_description: str | None = None,
) -> str:
    """Build a structured prompt for Gemini resume analysis."""

    job_context = ""

    if job_description:
        job_context = f"""
JOB DESCRIPTION:
{job_description}

Analyze the resume specifically against this job description.
"""

    return f"""
You are an expert ATS resume reviewer and career coach.

Analyze the following resume professionally.

{job_context}

RESUME:
{resume_text}

Provide your analysis using exactly these sections:

1. EXECUTIVE SUMMARY
Give a concise overview of the candidate's profile.

2. KEY STRENGTHS
List the strongest aspects of the resume.

3. WEAKNESSES
List important weaknesses or missing areas.

4. ATS IMPROVEMENTS
Explain how the resume can become more ATS-friendly.

5. SKILL GAPS
Identify important technical or professional skills that appear
to be missing or insufficiently demonstrated.

6. EXPERIENCE IMPROVEMENTS
Suggest how experience/project descriptions can be made stronger.

7. PROJECT IMPROVEMENTS
Suggest improvements to projects, including technologies,
impact, metrics, and outcomes where appropriate.

8. KEYWORD RECOMMENDATIONS
List relevant keywords that should be considered.

9. ACTION PLAN
Give 5 concrete actions the candidate should take next.

Rules:
- Do not invent candidate experience.
- Do not claim the candidate has a skill unless the resume supports it.
- Clearly distinguish missing information from actual weaknesses.
- Keep recommendations practical.
- Use professional and concise language.
"""


def analyze_resume_with_ai(
    resume_text: str,
    job_description: str | None = None,
    api_key: str | None = None,
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """
    Analyze a resume using Gemini.

    Returns a structured result rather than exposing raw API
    exceptions to the application.
    """
    if not resume_text.strip():
        return {
            "success": False,
            "analysis": "",
            "error": "Resume text is empty.",
        }

    if not configure_gemini(api_key):
        return {
            "success": False,
            "analysis": "",
            "error": (
                "Gemini API key was not found. "
                "Configure GEMINI_API_KEY before using AI analysis."
            ),
        }

    try:
        model = _get_model(model_name)

        prompt = build_resume_analysis_prompt(
            resume_text=resume_text,
            job_description=job_description,
        )

        response = model.generate_content(prompt)

        analysis = getattr(response, "text", "")

        if not analysis:
            return {
                "success": False,
                "analysis": "",
                "error": "Gemini returned an empty response.",
            }

        return {
            "success": True,
            "analysis": analysis.strip(),
            "error": "",
        }

    except Exception as exc:
        return {
            "success": False,
            "analysis": "",
            "error": f"AI analysis failed: {exc}",
        }


def generate_resume_summary(
    resume_text: str,
    api_key: str | None = None,
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """
    Generate a concise professional summary of a resume.
    """
    if not resume_text.strip():
        return {
            "success": False,
            "summary": "",
            "error": "Resume text is empty.",
        }

    if not configure_gemini(api_key):
        return {
            "success": False,
            "summary": "",
            "error": "Gemini API key was not found.",
        }

    prompt = f"""
You are a professional resume writer.

Create a concise professional summary based ONLY on the
information contained in this resume.

RESUME:
{resume_text}

Requirements:
- 3 to 5 sentences.
- Professional tone.
- Mention relevant technical skills.
- Mention experience or education only when present.
- Do not invent information.
"""

    try:
        model = _get_model(model_name)
        response = model.generate_content(prompt)

        summary = getattr(response, "text", "")

        if not summary:
            return {
                "success": False,
                "summary": "",
                "error": "Gemini returned an empty response.",
            }

        return {
            "success": True,
            "summary": summary.strip(),
            "error": "",
        }

    except Exception as exc:
        return {
            "success": False,
            "summary": "",
            "error": f"Summary generation failed: {exc}",
        }


def generate_job_match_recommendations(
    resume_text: str,
    job_description: str,
    api_key: str | None = None,
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """
    Generate AI recommendations for improving a resume against
    a specific job description.
    """
    if not resume_text.strip():
        return {
            "success": False,
            "recommendations": "",
            "error": "Resume text is empty.",
        }

    if not job_description.strip():
        return {
            "success": False,
            "recommendations": "",
            "error": "Job description is empty.",
        }

    if not configure_gemini(api_key):
        return {
            "success": False,
            "recommendations": "",
            "error": "Gemini API key was not found.",
        }

    prompt = f"""
You are an expert technical recruiter.

Compare this resume with the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide:

1. Top matching qualifications
2. Missing or weakly represented skills
3. Missing keywords
4. Resume sections that should be improved
5. Five specific changes that could improve job alignment

Do not invent qualifications.
Only recommend changes supported by the job description.
"""

    try:
        model = _get_model(model_name)
        response = model.generate_content(prompt)

        recommendations = getattr(response, "text", "")

        if not recommendations:
            return {
                "success": False,
                "recommendations": "",
                "error": "Gemini returned an empty response.",
            }

        return {
            "success": True,
            "recommendations": recommendations.strip(),
            "error": "",
        }

    except Exception as exc:
        return {
            "success": False,
            "recommendations": "",
            "error": f"Job matching analysis failed: {exc}",
        }