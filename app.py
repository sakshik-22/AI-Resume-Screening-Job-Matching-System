"""
AI Resume Screening & Job Matching System
==========================================
Main Streamlit application — multi-page HR SaaS dashboard.

Modules:
    - Dashboard: Overview metrics and analytics
    - Upload Resumes: Multi-file upload for PDF/DOCX
    - Job Description: JD input and skill extraction
    - Matching & Ranking: AI-powered candidate scoring
    - Candidate Details: Individual candidate deep-dive
    - Export Report: Downloadable PDF report
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils import SKILL_DATABASE, COLOR_PALETTE, format_file_size, get_theme_css, generate_pdf_report
from resume_parser import parse_resume
from matching_engine import (
    extract_jd_skills,
    rank_candidates,
    generate_recommendation,
    skill_gap_analysis,
)

# ─────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Screening & Job Matching System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────
def init_session_state():
    """Initialise all session-state keys used across pages."""
    defaults = {
        "theme_mode": "dark",
        "uploaded_files_data": [],      # list of parsed candidate dicts
        "jd_text": "",
        "jd_skills": [],
        "ranked_candidates": [],
        "recommendations": {},          # {candidate_name: recommendation_dict}
        "current_page": "Dashboard",
        "files_processed": False,
        "matching_done": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ─────────────────────────────────────────────
# Inject custom CSS
# ─────────────────────────────────────────────
st.markdown(
    f"<style>{get_theme_css(st.session_state.theme_mode)}</style>",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo / branding
    st.markdown(
        """
        <div style="text-align:center; padding: 1.2rem 0 0.5rem 0;">
            <div style="font-size:2.5rem;">🎯</div>
            <h2 style="margin:0; font-weight:800; letter-spacing:-0.5px;
                        background: linear-gradient(135deg, #4285f4, #1a73e8);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                TalentAI
            </h2>
            <p style="margin:0; font-size:0.72rem; opacity:0.6; letter-spacing:1.5px; text-transform:uppercase;">
                Resume Screening &amp; Job Matching
            </p>
        </div>
        <hr style="border:none; border-top:1px solid rgba(128,128,128,0.2); margin:0.5rem 0 1rem 0;">
        """,
        unsafe_allow_html=True,
    )

    # Navigation
    pages = [
        ("📊", "Dashboard"),
        ("📁", "Upload Resumes"),
        ("📄", "Job Description"),
        ("🤖", "Matching & Ranking"),
        ("👤", "Candidate Details"),
        ("📥", "Export Report"),
    ]

    for icon, page_name in pages:
        is_active = st.session_state.current_page == page_name
        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_page = page_name
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Theme toggle
    st.markdown(
        """
        <p style="font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;
                   opacity:0.5; margin-bottom:0.3rem;">Appearance</p>
        """,
        unsafe_allow_html=True,
    )
    theme_label = "🌙 Dark Mode" if st.session_state.theme_mode == "dark" else "☀️ Light Mode"
    if st.button(theme_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme_mode = (
            "light" if st.session_state.theme_mode == "dark" else "dark"
        )
        st.rerun()

    # Footer
    st.markdown(
        """
        <div style="position:fixed; bottom:1rem; width:inherit; text-align:center;">
            <p style="font-size:0.65rem; opacity:0.4;">
                © 2026 TalentAI v1.0<br>AI-Powered HR Analytics
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════
# PAGE RENDERERS
# ═══════════════════════════════════════════════

def render_header(title: str, subtitle: str = ""):
    """Render a gradient page header."""
    sub_html = f'<p style="margin:0; font-size:0.95rem; opacity:0.8;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-header">
            <h1 style="margin:0; font-size:1.75rem; font-weight:800;">{title}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value, icon: str = "📌", delta: str = ""):
    """Render a single metric card."""
    delta_html = f'<span style="font-size:0.75rem; color:#0f9d58;">{delta}</span>' if delta else ""
    return f"""
    <div class="metric-card">
        <div style="font-size:1.8rem; margin-bottom:0.25rem;">{icon}</div>
        <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; opacity:0.6;">{label}</div>
        <div style="font-size:1.8rem; font-weight:800; margin:0.15rem 0;">{value}</div>
        {delta_html}
    </div>
    """


# ─────────────────────────────────────────────
# PAGE: Dashboard
# ─────────────────────────────────────────────
def page_dashboard():
    render_header("📊 Dashboard", "AI Resume Screening & Job Matching Overview")

    candidates = st.session_state.ranked_candidates
    has_data = len(candidates) > 0 and st.session_state.matching_done

    # Metrics row
    total = len(candidates) if has_data else 0
    avg_score = round(np.mean([c["match_score"] for c in candidates]), 1) if has_data else 0
    top_name = candidates[0]["name"] if has_data else "—"
    top_score = candidates[0]["match_score"] if has_data else 0

    highly = sum(1 for c in candidates if c.get("category") == "Highly Suitable") if has_data else 0

    cols = st.columns(4)
    cards = [
        metric_card("Total Candidates", total, "👥"),
        metric_card("Average Score", f"{avg_score}%", "📈"),
        metric_card("Top Candidate", top_name, "🏆", f"{top_score}%" if has_data else ""),
        metric_card("Highly Suitable", highly, "✅"),
    ]
    for col, card_html in zip(cols, cards):
        col.markdown(card_html, unsafe_allow_html=True)

    if not has_data:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(
            "👋 **Welcome!** Start by uploading resumes, entering a Job Description, "
            "then run the AI Matching engine. Your analytics will appear here."
        )
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding:2.5rem;">
                <h3>🚀 Quick Start Guide</h3>
                <p style="opacity:0.7;">Follow these steps to screen candidates:</p>
                <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; margin-top:1.5rem;">
                    <div class="step-badge">1️⃣ Upload Resumes</div>
                    <div class="step-badge">2️⃣ Enter Job Description</div>
                    <div class="step-badge">3️⃣ Run AI Matching</div>
                    <div class="step-badge">4️⃣ Review & Export</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row
    col_bar, col_pie = st.columns(2)

    with col_bar:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Candidate Ranking")
        df_bar = pd.DataFrame(
            {"Candidate": [c["name"] for c in candidates],
             "Match Score": [c["match_score"] for c in candidates],
             "Category": [c["category"] for c in candidates]}
        )
        color_map = {
            "Highly Suitable": "#0f9d58",
            "Medium Fit": "#f9ab00",
            "Not Suitable": "#ea4335",
        }
        fig_bar = px.bar(
            df_bar, x="Candidate", y="Match Score", color="Category",
            color_discrete_map=color_map,
            text="Match Score",
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaed" if st.session_state.theme_mode == "dark" else "#202124"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[0, 110]),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_pie:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🥧 Category Distribution")
        cat_counts = pd.DataFrame(
            [c["category"] for c in candidates], columns=["Category"]
        ).value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_pie = px.pie(
            cat_counts, values="Count", names="Category",
            color="Category",
            color_discrete_map=color_map,
            hole=0.45,
        )
        fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaed" if st.session_state.theme_mode == "dark" else "#202124"),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380,
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Skill gap analysis
    if st.session_state.jd_skills:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔍 Skill Gap Analysis")
        gap = skill_gap_analysis(candidates, st.session_state.jd_skills)
        if gap:
            gap_df = pd.DataFrame(
                {"Skill": list(gap.keys()), "Candidates With Skill": list(gap.values())}
            )
            gap_df["Coverage %"] = round(gap_df["Candidates With Skill"] / total * 100, 1)
            fig_gap = px.bar(
                gap_df, x="Skill", y="Coverage %",
                text="Coverage %",
                color="Coverage %",
                color_continuous_scale=["#ea4335", "#f9ab00", "#0f9d58"],
            )
            fig_gap.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_gap.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaed" if st.session_state.theme_mode == "dark" else "#202124"),
                xaxis=dict(showgrid=False, tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[0, 115]),
                margin=dict(l=20, r=20, t=30, b=80),
                height=400,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_gap, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Top 3 candidates
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏅 Top 3 Candidates")
    top3 = candidates[:3]
    cols_top = st.columns(len(top3))
    medals = ["🥇", "🥈", "🥉"]
    for i, (col, cand) in enumerate(zip(cols_top, top3)):
        with col:
            badge_class = (
                "badge-success" if cand["category"] == "Highly Suitable"
                else "badge-warning" if cand["category"] == "Medium Fit"
                else "badge-danger"
            )
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center; padding:1.5rem;">
                    <div style="font-size:2.5rem;">{medals[i]}</div>
                    <h3 style="margin:0.5rem 0 0.2rem 0;">{cand['name']}</h3>
                    <p style="opacity:0.6; font-size:0.8rem;">{cand.get('email','')}</p>
                    <div style="font-size:2rem; font-weight:800; color:#4285f4; margin:0.5rem 0;">
                        {cand['match_score']}%
                    </div>
                    <span class="status-badge {badge_class}">{cand['category']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# PAGE: Upload Resumes
# ─────────────────────────────────────────────
def page_upload():
    render_header("📁 Upload Resumes", "Upload candidate resumes in PDF or DOCX format")

    st.markdown("<br>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drag and drop resumes here",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX. Upload one or more candidate resumes.",
    )

    if uploaded_files:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"📋 Uploaded Files ({len(uploaded_files)})")

        file_info = []
        for f in uploaded_files:
            file_info.append({
                "File Name": f.name,
                "Size": format_file_size(f.size),
                "Type": f.name.rsplit(".", 1)[-1].upper(),
                "Status": "✅ Ready",
            })

        st.dataframe(
            pd.DataFrame(file_info),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            process_btn = st.button(
                "🧠 Parse All Resumes", type="primary", use_container_width=True
            )

        if process_btn:
            parsed = []
            progress_bar = st.progress(0, text="Parsing resumes...")
            for idx, f in enumerate(uploaded_files):
                progress_bar.progress(
                    (idx + 1) / len(uploaded_files),
                    text=f"Parsing: {f.name}",
                )
                result = parse_resume(f, SKILL_DATABASE)
                parsed.append(result)

            st.session_state.uploaded_files_data = parsed
            st.session_state.files_processed = True
            st.session_state.matching_done = False
            st.session_state.ranked_candidates = []
            st.session_state.recommendations = {}
            progress_bar.progress(1.0, text="✅ All resumes parsed successfully!")
            st.success(f"Successfully parsed {len(parsed)} resume(s)!")
            st.rerun()

    # Show parsed data
    if st.session_state.files_processed and st.session_state.uploaded_files_data:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🧾 Parsed Candidate Data")

        for i, cand in enumerate(st.session_state.uploaded_files_data):
            with st.expander(f"👤 {cand['name']}  —  {cand['filename']}", expanded=(i == 0)):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**📧 Email:** {cand['email']}")
                    st.markdown(f"**📞 Phone:** {cand['phone']}")
                    st.markdown(f"**💼 Experience:** {cand['experience']}")
                with c2:
                    st.markdown("**🎓 Education:**")
                    for edu in cand["education"]:
                        st.markdown(f"  - {edu}")
                st.markdown("**🛠️ Skills:**")
                if cand["skills"]:
                    skills_html = " ".join(
                        [f'<span class="skill-tag">{s}</span>' for s in cand["skills"]]
                    )
                    st.markdown(skills_html, unsafe_allow_html=True)
                else:
                    st.markdown("_No skills detected_")

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: Job Description
# ─────────────────────────────────────────────
def page_job_description():
    render_header("📄 Job Description", "Enter the job description to match candidates against")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste the Job Description here",
        value=st.session_state.jd_text,
        height=300,
        placeholder=(
            "Example:\n\n"
            "We are looking for a Senior Python Developer with 5+ years of experience.\n"
            "Required skills: Python, Django, REST API, PostgreSQL, Docker, AWS.\n"
            "Nice to have: React, CI/CD, Kubernetes.\n"
            "Bachelor's degree in Computer Science or related field required."
        ),
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        extract_btn = st.button("🔍 Extract Skills", type="primary", use_container_width=True)

    if extract_btn and jd_text.strip():
        st.session_state.jd_text = jd_text
        skills = extract_jd_skills(jd_text, SKILL_DATABASE)
        st.session_state.jd_skills = skills
        st.session_state.matching_done = False
        st.session_state.ranked_candidates = []
        st.session_state.recommendations = {}
        st.rerun()
    elif extract_btn:
        st.warning("Please enter a job description first.")

    # Show extracted skills
    if st.session_state.jd_skills:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"🛠️ Extracted Required Skills ({len(st.session_state.jd_skills)})")
        skills_html = " ".join(
            [f'<span class="skill-tag">{s}</span>' for s in st.session_state.jd_skills]
        )
        st.markdown(skills_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: Matching & Ranking
# ─────────────────────────────────────────────
def page_matching():
    render_header("🤖 AI Matching & Ranking", "Compare candidates against the job description")

    if not st.session_state.files_processed:
        st.warning("⚠️ Please upload and parse resumes first.")
        return
    if not st.session_state.jd_skills:
        st.warning("⚠️ Please enter a Job Description and extract skills first.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        match_btn = st.button(
            "🚀 Run AI Matching", type="primary", use_container_width=True
        )

    if match_btn:
        with st.spinner("🧠 AI Matching Engine processing..."):
            candidates = st.session_state.uploaded_files_data.copy()
            ranked = rank_candidates(
                candidates, st.session_state.jd_text, st.session_state.jd_skills
            )

            # Generate recommendations
            recs = {}
            for cand in ranked:
                rec = generate_recommendation(cand, st.session_state.jd_skills)
                cand.update(rec)
                recs[cand["name"]] = rec

            st.session_state.ranked_candidates = ranked
            st.session_state.recommendations = recs
            st.session_state.matching_done = True
        st.success("✅ AI Matching complete!")
        st.rerun()

    # Show results
    if st.session_state.matching_done and st.session_state.ranked_candidates:
        candidates = st.session_state.ranked_candidates

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🏆 Candidate Rankings")

        # Build results table
        table_data = []
        for c in candidates:
            badge_class = (
                "badge-success" if c["category"] == "Highly Suitable"
                else "badge-warning" if c["category"] == "Medium Fit"
                else "badge-danger"
            )
            table_data.append({
                "Rank": c["rank"],
                "Candidate": c["name"],
                "Match Score": f"{c['match_score']}%",
                "Category": c["category"],
                "Email": c.get("email", "—"),
                "Skills Found": len(c.get("skills", [])),
                "Recommendation": c.get("recommendation", "—"),
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Category summary cards
        st.markdown("<br>", unsafe_allow_html=True)
        highly = [c for c in candidates if c["category"] == "Highly Suitable"]
        medium = [c for c in candidates if c["category"] == "Medium Fit"]
        not_suit = [c for c in candidates if c["category"] == "Not Suitable"]

        col_h, col_m, col_n = st.columns(3)
        with col_h:
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 4px solid #0f9d58; text-align:center;">
                    <h3 style="color:#0f9d58;">✅ Highly Suitable</h3>
                    <div style="font-size:2.5rem; font-weight:800;">{len(highly)}</div>
                    <p style="opacity:0.6;">candidates (80-100%)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_m:
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 4px solid #f9ab00; text-align:center;">
                    <h3 style="color:#f9ab00;">⚡ Medium Fit</h3>
                    <div style="font-size:2.5rem; font-weight:800;">{len(medium)}</div>
                    <p style="opacity:0.6;">candidates (50-79%)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_n:
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 4px solid #ea4335; text-align:center;">
                    <h3 style="color:#ea4335;">❌ Not Suitable</h3>
                    <div style="font-size:2.5rem; font-weight:800;">{len(not_suit)}</div>
                    <p style="opacity:0.6;">candidates (&lt;50%)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# PAGE: Candidate Details
# ─────────────────────────────────────────────
def page_candidate_details():
    render_header("👤 Candidate Details", "In-depth view of individual candidate profiles")

    if not st.session_state.matching_done or not st.session_state.ranked_candidates:
        st.warning("⚠️ Please run the AI Matching engine first.")
        return

    candidates = st.session_state.ranked_candidates

    st.markdown("<br>", unsafe_allow_html=True)

    # Candidate selector
    names = [f"#{c['rank']} — {c['name']} ({c['match_score']}%)" for c in candidates]
    selected_idx = st.selectbox("Select a candidate", range(len(names)), format_func=lambda i: names[i])
    cand = candidates[selected_idx]

    st.markdown("<br>", unsafe_allow_html=True)

    # Profile header
    badge_class = (
        "badge-success" if cand["category"] == "Highly Suitable"
        else "badge-warning" if cand["category"] == "Medium Fit"
        else "badge-danger"
    )

    rec_color = {"Yes": "#0f9d58", "Maybe": "#f9ab00", "No": "#ea4335"}.get(
        cand.get("recommendation", ""), "#888"
    )

    st.markdown(
        f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <h2 style="margin:0;">{cand['name']}</h2>
                    <p style="opacity:0.6; margin:0.2rem 0;">📧 {cand.get('email','')} &nbsp;|&nbsp; 📞 {cand.get('phone','')}</p>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:2.8rem; font-weight:800; color:#4285f4;">{cand['match_score']}%</div>
                    <span class="status-badge {badge_class}">{cand['category']}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Details grid
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎓 Education")
        for edu in cand.get("education", ["Not specified"]):
            st.markdown(f"- {edu}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💼 Experience")
        st.markdown(cand.get("experience", "Not specified"))
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🛠️ Skills")
        if cand.get("skills"):
            skills_html = " ".join(
                [f'<span class="skill-tag">{s}</span>' for s in cand["skills"]]
            )
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.markdown("_No skills detected_")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Skill match visual
        if st.session_state.jd_skills:
            matched = set(cand.get("skills", [])) & set(st.session_state.jd_skills)
            missing = set(st.session_state.jd_skills) - set(cand.get("skills", []))

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🎯 Skill Match Breakdown")
            st.markdown(f"**Matched ({len(matched)}):** " + ", ".join(sorted(matched)) if matched else "**Matched:** None")
            st.markdown(f"**Missing ({len(missing)}):** " + ", ".join(sorted(missing)) if missing else "**Missing:** None")
            st.markdown("</div>", unsafe_allow_html=True)

    # AI Recommendation
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🧠 AI Recommendation")

    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown(f"#### Hiring Decision: <span style='color:{rec_color}; font-weight:800;'>{cand.get('recommendation','—')}</span>", unsafe_allow_html=True)

        st.markdown("**💪 Strengths:**")
        for s in cand.get("strengths", []):
            st.markdown(f"  - ✅ {s}")

    with rec_col2:
        st.markdown("**⚠️ Weaknesses:**")
        for w in cand.get("weaknesses", []):
            st.markdown(f"  - ❌ {w}")

        st.markdown("**📚 Suggested Improvements:**")
        for sug in cand.get("suggestions", []):
            st.markdown(f"  - 💡 {sug}")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: Export Report
# ─────────────────────────────────────────────
def page_export():
    render_header("📥 Export Report", "Generate and download professional HR reports")

    if not st.session_state.matching_done or not st.session_state.ranked_candidates:
        st.warning("⚠️ Please run the AI Matching engine first before exporting.")
        return

    candidates = st.session_state.ranked_candidates

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Report Preview")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Candidates", len(candidates))
    col2.metric("Avg. Score", f"{round(np.mean([c['match_score'] for c in candidates]), 1)}%")
    col3.metric("Top Score", f"{candidates[0]['match_score']}%")
    col4.metric("Top Candidate", candidates[0]["name"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Rankings table
    st.markdown("#### 🏆 Complete Rankings")
    report_df = pd.DataFrame([
        {
            "Rank": c["rank"],
            "Name": c["name"],
            "Email": c.get("email", "—"),
            "Score": f"{c['match_score']}%",
            "Category": c["category"],
            "Recommendation": c.get("recommendation", "—"),
        }
        for c in candidates
    ])
    st.dataframe(report_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # PDF Download
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            pdf_bytes = generate_pdf_report(
                candidates,
                st.session_state.jd_text,
                st.session_state.jd_skills,
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"TalentAI_Report_{timestamp}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")


# ═══════════════════════════════════════════════
# ROUTING
# ═══════════════════════════════════════════════
page_map = {
    "Dashboard": page_dashboard,
    "Upload Resumes": page_upload,
    "Job Description": page_job_description,
    "Matching & Ranking": page_matching,
    "Candidate Details": page_candidate_details,
    "Export Report": page_export,
}

page_map[st.session_state.current_page]()
