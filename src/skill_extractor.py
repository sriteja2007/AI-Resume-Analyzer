from __future__ import annotations

import re


TECHNICAL_SKILLS = {
    # Programming languages
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "rust",
    "php",
    "ruby",
    "kotlin",
    "swift",
    "r",

    # Web development
    "html",
    "css",
    "react",
    "react.js",
    "next.js",
    "node.js",
    "node",
    "express",
    "angular",
    "vue",
    "tailwind",
    "bootstrap",

    # Databases
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "sqlite",
    "oracle",
    "redis",
    "firebase",
    "supabase",

    # Data / AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "natural language processing",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "plotly",
    "opencv",
    "hugging face",
    "transformers",
    "generative ai",
    "llm",
    "large language models",
    "gemini",
    "openai",

    # Cloud / DevOps
    "aws",
    "azure",
    "google cloud",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "github",
    "gitlab",
    "ci/cd",
    "linux",

    # APIs / Backend
    "rest api",
    "restful api",
    "graphql",
    "api",
    "fastapi",
    "flask",
    "django",

    # Tools
    "streamlit",
    "jupyter",
    "vs code",
    "visual studio code",
    "postman",
    "figma",
}


SOFT_SKILLS = {
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "problem-solving",
    "critical thinking",
    "time management",
    "adaptability",
    "creativity",
    "collaboration",
    "decision making",
    "decision-making",
    "project management",
    "presentation",
    "interpersonal skills",
    "analytical skills",
}


SKILL_ALIASES = {
    "react.js": "React",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "c++": "C++",
    "c#": "C#",
    "nlp": "NLP",
    "gcp": "GCP",
    "aws": "AWS",
    "azure": "Azure",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "python": "Python",
    "java": "Java",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "streamlit": "Streamlit",
    "github": "GitHub",
    "git": "Git",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "natural language processing": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "generative ai": "Generative AI",
    "large language models": "Large Language Models",
    "llm": "LLM",
}


def _normalize_for_matching(text: str) -> str:
    """Normalize text for reliable skill matching."""
    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_skill(text: str, skill: str) -> bool:
    """
    Check whether a skill exists in text.

    Word boundaries are used where possible so that short skills
    such as 'r' do not match unrelated words.
    """
    normalized_text = _normalize_for_matching(text)
    normalized_skill = _normalize_for_matching(skill)

    if normalized_skill == "r":
        return bool(re.search(r"(?<![a-z0-9])r(?![a-z0-9])", normalized_text))

    escaped_skill = re.escape(normalized_skill)

    # Allow flexible whitespace between words.
    escaped_skill = escaped_skill.replace(r"\ ", r"\s+")

    pattern = rf"(?<![a-z0-9+#]){escaped_skill}(?![a-z0-9+#])"

    return bool(re.search(pattern, normalized_text))


def extract_skills(text: str) -> dict[str, list[str]]:
    """
    Extract technical and soft skills from resume text.
    """
    technical_matches = []
    soft_matches = []

    for skill in sorted(TECHNICAL_SKILLS, key=len, reverse=True):
        if _contains_skill(text, skill):
            display_name = SKILL_ALIASES.get(skill, skill.title())
            technical_matches.append(display_name)

    for skill in sorted(SOFT_SKILLS, key=len, reverse=True):
        if _contains_skill(text, skill):
            display_name = skill.title()
            soft_matches.append(display_name)

    technical_matches = sorted(set(technical_matches))
    soft_matches = sorted(set(soft_matches))

    all_skills = sorted(set(technical_matches + soft_matches))

    return {
        "technical_skills": technical_matches,
        "soft_skills": soft_matches,
        "all_skills": all_skills,
    }


def extract_skill_list(text: str) -> list[str]:
    """Return a simple sorted list of all detected skills."""
    return extract_skills(text)["all_skills"]


def compare_skills(
    resume_skills: list[str],
    required_skills: list[str],
) -> dict[str, list[str]]:
    """
    Compare resume skills against required job skills.
    """
    resume_normalized = {
        skill.strip().lower()
        for skill in resume_skills
        if skill and skill.strip()
    }

    required_normalized = {
        skill.strip().lower()
        for skill in required_skills
        if skill and skill.strip()
    }

    matched = sorted(
        skill
        for skill in required_normalized
        if skill in resume_normalized
    )

    missing = sorted(
        skill
        for skill in required_normalized
        if skill not in resume_normalized
    )

    return {
        "matched_skills": matched,
        "missing_skills": missing,
    }


def extract_skills_from_sections(
    sections: dict[str, str],
) -> dict[str, dict[str, list[str]]]:
    """
    Extract skills independently from different resume sections.
    """
    results = {}

    for section_name, section_text in sections.items():
        results[section_name] = extract_skills(section_text)

    return results