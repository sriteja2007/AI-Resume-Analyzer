from __future__ import annotations

import os

import plotly.graph_objects as go
import streamlit as st

from src.ai_analyzer import analyze_resume_with_ai
from src.ats_analyzer import analyze_ats
from src.job_matcher import analyze_job_match
from src.resume_parser import extract_resume_text, get_resume_statistics
from src.resume_scorer import analyze_resume_score
from src.skill_extractor import extract_skills, compare_skills
from src.text_preprocessor import preprocess_resume


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #0e1117;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 2rem;
            border-radius: 20px;
            background: linear-gradient(
                135deg,
                rgba(35, 39, 47, 0.95),
                rgba(20, 25, 35, 0.95)
            );
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1.5rem;
        }

        .hero h1 {
            font-size: 3rem;
            margin-bottom: 0.4rem;
        }

        .hero p {
            color: #aeb7c4;
            font-size: 1.1rem;
        }

        .metric-card {
            padding: 1.2rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            text-align: center;
        }

        .metric-title {
            color: #9ca6b4;
            font-size: 0.9rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
        }

        .success-box {
            padding: 1rem;
            border-radius: 12px;
            background: rgba(34, 197, 94, 0.10);
            border: 1px solid rgba(34, 197, 94, 0.25);
        }

        .warning-box {
            padding: 1rem;
            border-radius: 12px;
            background: rgba(245, 158, 11, 0.10);
            border: 1px solid rgba(245, 158, 11, 0.25);
        }

        .danger-box {
            padding: 1rem;
            border-radius: 12px;
            background: rgba(239, 68, 68, 0.10);
            border: 1px solid rgba(239, 68, 68, 0.25);
        }

        .tag {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            margin: 0.2rem;
            border-radius: 999px;
            background: rgba(99,102,241,0.15);
            border: 1px solid rgba(99,102,241,0.3);
            font-size: 0.85rem;
        }

        .section-title {
            margin-top: 1rem;
            margin-bottom: 0.8rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.04);
            padding: 1rem;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.07);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def score_color_class(score: float) -> str:
    if score >= 80:
        return "success-box"
    if score >= 60:
        return "warning-box"
    return "danger-box"


def display_tags(items: list[str], empty_message: str = "None detected.") -> None:
    if not items:
        st.info(empty_message)
        return

    html = "".join(
        f'<span class="tag">{str(item).replace("<", "&lt;").replace(">", "&gt;")}</span>'
        for item in items
    )

    st.markdown(html, unsafe_allow_html=True)


def create_gauge(score: float, title: str) -> go.Figure:
    score = max(0, min(100, float(score)))

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                },
                "bar": {
                    "thickness": 0.25,
                },
                "steps": [
                    {"range": [0, 50]},
                    {"range": [50, 75]},
                    {"range": [75, 100]},
                ],
            },
        )
    )

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig


def safe_list(value) -> list:
    if isinstance(value, list):
        return value
    return []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 📄 AI Resume Analyzer")

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX and TXT",
    )

    st.markdown("### 🎯 Target Job")

    job_description = st.text_area(
        "Paste job description",
        height=220,
        placeholder=(
            "Paste the target job description here...\n\n"
            "The analyzer will compare your resume against the job."
        ),
    )

    st.markdown("---")

    st.markdown(
        """
        **Analysis includes:**

        - 📊 ATS Score
        - 🧠 Skill Analysis
        - 🔎 Keyword Analysis
        - 💼 Job Matching
        - 🤖 Gemini AI Insights
        - 📈 Resume Recommendations
        """
    )

    st.markdown("---")
    st.caption("AI Resume Analyzer • Portfolio Project")


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>📄 AI Resume Analyzer</h1>
        <p>
            Analyze your resume, improve ATS compatibility,
            identify missing skills and match your resume with
            your target job using AI.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# EMPTY STATE
# ============================================================

if uploaded_file is None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Supported Formats", "3")

    with col2:
        st.metric("Analysis Modules", "5+")

    with col3:
        st.metric("AI Powered", "Gemini")

    st.markdown("---")

    st.info(
        "👈 Upload your resume from the sidebar to start the analysis."
    )

    st.markdown(
        """
        ### 🚀 How it works

        **1. Upload Resume**  
        Upload your PDF, DOCX or TXT resume.

        **2. Resume Processing**  
        The system extracts and preprocesses your resume text.

        **3. ATS Analysis**  
        Your resume is checked for structure, keywords,
        action verbs and achievements.

        **4. Skill Analysis**  
        Technical and soft skills are identified.

        **5. Job Matching**  
        If you provide a job description, your resume is
        compared against the target role.

        **6. AI Career Insights**  
        Gemini provides personalized recommendations.
        """
    )

    st.stop()


# ============================================================
# RESUME EXTRACTION
# ============================================================

try:
    resume_text = extract_resume_text(
        uploaded_file,
        uploaded_file.name,
    )

except Exception as error:
    st.error(f"❌ Could not process the resume: {error}")
    st.stop()


if not resume_text.strip():
    st.error("❌ No readable text was found in the uploaded resume.")
    st.stop()


# ============================================================
# BASIC PROCESSING
# ============================================================

stats = get_resume_statistics(resume_text)

processed_text = preprocess_resume(resume_text)

skills = extract_skills(resume_text)

ats_result = analyze_ats(resume_text)

score_result = analyze_resume_score(resume_text)


# ============================================================
# JOB MATCHING
# ============================================================

job_match_result = None

if job_description.strip():
    try:
        job_match_result = analyze_job_match(
            resume_text,
            job_description,
        )
    except Exception as error:
        st.warning(f"Job matching could not be completed: {error}")


# ============================================================
# FILE INFORMATION
# ============================================================

st.success(
    f"✅ Successfully processed **{uploaded_file.name}**"
)

info1, info2, info3, info4 = st.columns(4)

with info1:
    st.metric(
        "Words",
        f"{stats.get('words', 0):,}",
    )

with info2:
    st.metric(
        "Characters",
        f"{stats.get('characters', 0):,}",
    )

with info3:
    st.metric(
        "Lines",
        f"{stats.get('lines', 0):,}",
    )

with info4:
    st.metric(
        "Skills Detected",
        len(skills.get("technical_skills", []))
        + len(skills.get("soft_skills", [])),
    )


# ============================================================
# MAIN SCORE
# ============================================================

st.markdown("## 📊 Resume Overview")

overview1, overview2, overview3, overview4 = st.columns(4)

ats_score = float(
    ats_result.get(
        "ats_score",
        score_result.get("score", 0),
    )
)

overall_score = float(
    score_result.get(
        "score",
        ats_score,
    )
)

section_score = float(
    ats_result.get(
        "section_completeness_score",
        0,
    )
)

keyword_score = float(
    ats_result.get(
        "keyword_score",
        0,
    )
)

with overview1:
    st.metric(
        "ATS Score",
        f"{ats_score:.0f}/100",
    )

with overview2:
    st.metric(
        "Resume Score",
        f"{overall_score:.0f}/100",
    )

with overview3:
    st.metric(
        "Section Score",
        f"{section_score:.0f}/100",
    )

with overview4:
    st.metric(
        "Keyword Score",
        f"{keyword_score:.0f}/100",
    )


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 ATS Analysis",
        "🧠 Skills",
        "💼 Job Match",
        "🤖 AI Career Insights",
        "📄 Resume Text",
    ]
)


# ============================================================
# TAB 1 — ATS ANALYSIS
# ============================================================

with tabs[0]:

    st.markdown("## 📊 ATS Resume Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(
            create_gauge(
                ats_score,
                "ATS Compatibility",
            ),
            width="stretch",
        )

    with col2:

        st.markdown("### Score Breakdown")

        breakdown = ats_result.get("breakdown", {})

        if isinstance(breakdown, dict) and breakdown:

            for name, value in breakdown.items():

                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    numeric_value = 0

                st.write(
                    f"**{str(name).replace('_', ' ').title()}**"
                )

                st.progress(
                    max(0.0, min(1.0, numeric_value / 100))
                )

                st.caption(
                    f"{numeric_value:.0f}/100"
                )

        else:

            metrics = {
                "Section Completeness": section_score,
                "Formatting": ats_result.get(
                    "formatting_score",
                    0,
                ),
                "Keywords": keyword_score,
                "Action Verbs": ats_result.get(
                    "action_verb_score",
                    0,
                ),
                "Achievements": ats_result.get(
                    "achievement_score",
                    0,
                ),
                "Contact Information": ats_result.get(
                    "contact_score",
                    0,
                ),
            }

            for name, value in metrics.items():

                numeric_value = float(value)

                st.write(f"**{name}**")

                st.progress(
                    max(0.0, min(1.0, numeric_value / 100))
                )

                st.caption(
                    f"{numeric_value:.0f}/100"
                )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📌 Detected Sections")

        detected_sections = safe_list(
            ats_result.get("detected_sections", [])
        )

        if detected_sections:
            for section in detected_sections:
                st.success(
                    f"✓ {str(section).title()}"
                )
        else:
            st.warning("No standard sections detected.")

    with col2:
        st.markdown("### 📈 Quantifiable Achievements")

        achievements = safe_list(
            ats_result.get(
                "quantifiable_achievements",
                [],
            )
        )

        if achievements:
            for achievement in achievements[:10]:
                st.success(
                    f"✓ {achievement}"
                )
        else:
            st.warning(
                "No quantifiable achievements detected."
            )

    st.markdown("---")

    st.markdown("### 🔑 Important Keywords")

    keywords = safe_list(
        ats_result.get("keywords", [])
    )

    display_tags(
        keywords,
        "No important keywords detected.",
    )

    st.markdown("---")

    st.markdown("### ⚡ Action Verbs")

    action_verbs = safe_list(
        ats_result.get("action_verbs", [])
    )

    display_tags(
        action_verbs,
        "No strong action verbs detected.",
    )


# ============================================================
# TAB 2 — SKILLS
# ============================================================

with tabs[1]:

    st.markdown("## 🧠 Skill Analysis")

    technical_skills = safe_list(
        skills.get("technical_skills", [])
    )

    soft_skills = safe_list(
        skills.get("soft_skills", [])
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💻 Technical Skills")

        if technical_skills:
            display_tags(technical_skills)
        else:
            st.info("No technical skills detected.")

    with col2:
        st.markdown("### 🤝 Soft Skills")

        if soft_skills:
            display_tags(soft_skills)
        else:
            st.info("No soft skills detected.")

    st.markdown("---")

    st.markdown("### 📊 Skill Summary")

    skill_col1, skill_col2, skill_col3 = st.columns(3)

    with skill_col1:
        st.metric(
            "Technical Skills",
            len(technical_skills),
        )

    with skill_col2:
        st.metric(
            "Soft Skills",
            len(soft_skills),
        )

    with skill_col3:
        st.metric(
            "Total Skills",
            len(technical_skills)
            + len(soft_skills),
        )


# ============================================================
# TAB 3 — JOB MATCH
# ============================================================

with tabs[2]:

    st.markdown("## 💼 Resume ↔ Job Match")

    if not job_description.strip():

        st.info(
            "🎯 Add a target job description in the sidebar "
            "to activate job matching."
        )

        st.markdown(
            """
            ### What you'll get

            - Overall job match score
            - Keyword match score
            - Skill match score
            - Text similarity
            - Matching skills
            - Missing skills
            - Matching keywords
            - Missing keywords
            - Job recommendations
            """
        )

    elif job_match_result is None:

        st.error(
            "Unable to calculate the job match."
        )

    else:

        overall_match = float(
            job_match_result.get(
                "overall_match_score",
                0,
            )
        )

        keyword_match = float(
            job_match_result.get(
                "keyword_match_score",
                0,
            )
        )

        skill_match = float(
            job_match_result.get(
                "skill_match_score",
                0,
            )
        )

        text_similarity = float(
            job_match_result.get(
                "text_similarity_score",
                0,
            )
        )

        st.markdown("### 🎯 Match Score")

        match_col1, match_col2, match_col3, match_col4 = st.columns(4)

        with match_col1:
            st.metric(
                "Overall Match",
                f"{overall_match:.0f}%",
            )

        with match_col2:
            st.metric(
                "Keyword Match",
                f"{keyword_match:.0f}%",
            )

        with match_col3:
            st.metric(
                "Skill Match",
                f"{skill_match:.0f}%",
            )

        with match_col4:
            st.metric(
                "Text Similarity",
                f"{text_similarity:.0f}%",
            )

        st.progress(
            max(
                0.0,
                min(
                    1.0,
                    overall_match / 100,
                ),
            )
        )

        if overall_match >= 80:
            st.success(
                "🔥 Excellent match! Your resume aligns strongly with this job."
            )
        elif overall_match >= 60:
            st.warning(
                "👍 Good match, but there are areas you can improve."
            )
        else:
            st.error(
                "⚠️ Low match. Consider improving your resume for this role."
            )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### ✅ Matching Skills")

            matched_skills = safe_list(
                job_match_result.get(
                    "matched_skills",
                    [],
                )
            )

            display_tags(
                matched_skills,
                "No matching skills detected.",
            )

        with col2:

            st.markdown("### ❌ Missing Skills")

            missing_skills = safe_list(
                job_match_result.get(
                    "missing_skills",
                    [],
                )
            )

            display_tags(
                missing_skills,
                "No major missing skills detected.",
            )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### 🔑 Matching Keywords")

            matched_keywords = safe_list(
                job_match_result.get(
                    "matched_keywords",
                    [],
                )
            )

            display_tags(
                matched_keywords,
                "No matching keywords detected.",
            )

        with col2:

            st.markdown("### ⚠️ Missing Keywords")

            missing_keywords = safe_list(
                job_match_result.get(
                    "missing_keywords",
                    [],
                )
            )

            display_tags(
                missing_keywords,
                "No major missing keywords detected.",
            )

        st.markdown("---")

        st.markdown("### 📋 Required Skills")

        required_skills = safe_list(
            job_match_result.get(
                "required_skills",
                [],
            )
        )

        display_tags(
            required_skills,
            "No specific skills identified.",
        )

        st.markdown("---")

        st.markdown("### 💡 Recommendations")

        recommendations = safe_list(
            job_match_result.get(
                "recommendations",
                [],
            )
        )

        if recommendations:
            for index, recommendation in enumerate(
                recommendations,
                start=1,
            ):
                st.markdown(
                    f"**{index}.** {recommendation}"
                )
        else:
            st.info(
                "No additional recommendations generated."
            )


# ============================================================
# TAB 4 — GEMINI AI CAREER INSIGHTS
# ============================================================

with tabs[3]:

    st.markdown("## 🤖 AI Career Insights")

    st.markdown(
        """
        Gemini analyzes your resume and provides personalized
        career recommendations based on the information actually
        present in your resume.
        """
    )

    try:
        gemini_key = st.secrets.get(
            "GEMINI_API_KEY",
            os.getenv("GEMINI_API_KEY", ""),
        )
    except Exception:
        gemini_key = os.getenv(
            "GEMINI_API_KEY",
            "",
        )

    if not gemini_key:

        st.warning(
            "⚠️ Gemini API key is not configured."
        )

        st.markdown(
            """
            Add your API key to:

            `.streamlit/secrets.toml`

            Example:

            `GEMINI_API_KEY = "your-api-key"`
            """
        )

    else:

        if st.button(
            "✨ Analyze Resume with Gemini AI",
            type="primary",
            width="stretch",
        ):

            with st.spinner(
                "Gemini is analyzing your resume..."
            ):

                try:

                    ai_result = analyze_resume_with_ai(
                        resume_text=resume_text,
                        job_description=job_description,
                        api_key=gemini_key,
                    )

                    st.session_state["ai_result"] = ai_result

                except Exception as error:

                    st.error(
                        f"❌ Gemini analysis failed: {error}"
                    )

        ai_result = st.session_state.get(
            "ai_result"
        )

        if ai_result:

            st.markdown("---")

            summary = ai_result.get(
                "summary",
                "",
            )

            if summary:
                st.markdown("### 📝 AI Summary")

                st.info(summary)

            overall_assessment = ai_result.get(
                "overall_assessment",
                "",
            )

            if overall_assessment:
                st.markdown(
                    "### 🔎 Overall Assessment"
                )

                st.write(
                    overall_assessment
                )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### 💪 Strengths")

                strengths = safe_list(
                    ai_result.get(
                        "strengths",
                        [],
                    )
                )

                if strengths:
                    for item in strengths:
                        st.success(
                            f"✓ {item}"
                        )
                else:
                    st.info(
                        "No strengths returned."
                    )

            with col2:

                st.markdown("### ⚠️ Weaknesses")

                weaknesses = safe_list(
                    ai_result.get(
                        "weaknesses",
                        [],
                    )
                )

                if weaknesses:
                    for item in weaknesses:
                        st.warning(
                            f"• {item}"
                        )
                else:
                    st.info(
                        "No weaknesses returned."
                    )

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "### 🔑 Missing Keywords"
                )

                missing_keywords = safe_list(
                    ai_result.get(
                        "missing_keywords",
                        [],
                    )
                )

                display_tags(
                    missing_keywords,
                    "No missing keywords identified.",
                )

            with col2:

                st.markdown(
                    "### 🧠 Missing Skills"
                )

                missing_skills = safe_list(
                    ai_result.get(
                        "missing_skills",
                        [],
                    )
                )

                display_tags(
                    missing_skills,
                    "No missing skills identified.",
                )

            st.markdown("---")

            st.markdown(
                "### 🚀 AI Recommendations"
            )

            recommendations = safe_list(
                ai_result.get(
                    "recommendations",
                    [],
                )
            )

            if recommendations:

                for index, item in enumerate(
                    recommendations,
                    start=1,
                ):
                    st.markdown(
                        f"**{index}.** {item}"
                    )

            else:
                st.info(
                    "No recommendations returned."
                )

            st.markdown("---")

            st.markdown(
                "### 📈 ATS Improvements"
            )

            ats_improvements = safe_list(
                ai_result.get(
                    "ats_improvements",
                    [],
                )
            )

            if ats_improvements:

                for item in ats_improvements:
                    st.info(
                        f"📌 {item}"
                    )

            else:
                st.info(
                    "No additional ATS improvements returned."
                )

            st.markdown("---")

            st.markdown(
                "### 🎯 Career Advice"
            )

            career_advice = safe_list(
                ai_result.get(
                    "career_advice",
                    [],
                )
            )

            if career_advice:

                for item in career_advice:
                    st.success(
                        f"💡 {item}"
                    )

            else:
                st.info(
                    "No career advice returned."
                )


# ============================================================
# TAB 5 — RESUME TEXT
# ============================================================

with tabs[4]:

    st.markdown("## 📄 Extracted Resume Text")

    st.caption(
        "This is the text extracted from your uploaded resume."
    )

    st.text_area(
        "Resume Content",
        value=resume_text,
        height=600,
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown("### 🧹 Preprocessed Text")

    st.text_area(
        "Preprocessed Content",
        value=processed_text,
        height=400,
        label_visibility="collapsed",
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#7f8996; padding:1rem;">
        <strong>AI Resume Analyzer</strong><br>
        Resume Intelligence • ATS Analysis • Job Matching • Gemini AI
    </div>
    """,
    unsafe_allow_html=True,
)