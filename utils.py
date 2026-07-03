"""
Utilities module for the AI Resume Screening & Job Matching System.

Provides:
    - SKILL_DATABASE: comprehensive list of ~200 technical and soft skills.
    - COLOR_PALETTE: colour constants used across the application.
    - format_file_size(): human-readable byte sizes.
    - get_theme_css(): complete CSS for dark / light Streamlit themes.
    - generate_pdf_report(): professional multi-page PDF report via fpdf2.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List

from fpdf import FPDF

# ---------------------------------------------------------------------------
# SKILL_DATABASE  (~200 lowercase skills)
# ---------------------------------------------------------------------------

SKILL_DATABASE: List[str] = [
    # ── Programming Languages ──────────────────────────────────────────────
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
    "matlab", "sql", "html", "css", "perl", "lua", "dart", "shell",
    "bash", "powershell", "objective-c", "assembly", "groovy", "haskell",
    "elixir", "clojure", "fortran", "cobol", "vba",
    # ── Frameworks & Libraries ─────────────────────────────────────────────
    "react", "angular", "vue", "svelte", "next.js", "nuxt.js", "django",
    "flask", "fastapi", "spring", "spring boot", "nodejs", "express",
    "nestjs", "ruby on rails", "laravel", "asp.net", "jquery", "bootstrap",
    "tailwind css", "material ui", "redux", "webpack", "vite",
    # ── AI / ML / Data Science ─────────────────────────────────────────────
    "tensorflow", "pytorch", "keras", "pandas", "numpy", "scikit-learn",
    "opencv", "scipy", "matplotlib", "seaborn", "plotly", "nltk", "spacy",
    "hugging face", "transformers", "xgboost", "lightgbm", "catboost",
    "machine learning", "deep learning", "natural language processing",
    "nlp", "computer vision", "data science", "data analysis",
    "data engineering", "data mining", "data visualization",
    "statistical modeling", "feature engineering", "model deployment",
    "mlops", "generative ai", "large language models", "llm",
    "reinforcement learning", "neural networks", "regression",
    "classification", "clustering", "time series analysis",
    # ── Big Data ───────────────────────────────────────────────────────────
    "big data", "hadoop", "spark", "apache kafka", "apache flink",
    "apache airflow", "hive", "presto", "databricks", "snowflake",
    "etl", "data warehousing", "data lake",
    # ── BI & Reporting ─────────────────────────────────────────────────────
    "tableau", "power bi", "looker", "google data studio", "excel",
    "google sheets",
    # ── Cloud Platforms ────────────────────────────────────────────────────
    "aws", "azure", "gcp", "google cloud", "amazon web services",
    "microsoft azure", "heroku", "digitalocean", "ibm cloud",
    "oracle cloud", "cloudflare",
    # ── DevOps & CI/CD ─────────────────────────────────────────────────────
    "docker", "kubernetes", "jenkins", "terraform", "ansible",
    "ci/cd", "git", "github", "gitlab", "bitbucket", "github actions",
    "circleci", "travis ci", "argo cd", "helm", "prometheus", "grafana",
    "nagios", "elk stack", "datadog", "new relic",
    # ── Databases ──────────────────────────────────────────────────────────
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "oracle", "sqlite", "dynamodb", "mariadb",
    "couchdb", "neo4j", "firebase", "supabase", "memcached",
    "microsoft sql server", "amazon rds", "amazon redshift",
    # ── Web & API ──────────────────────────────────────────────────────────
    "rest api", "graphql", "grpc", "websockets", "soap", "json",
    "xml", "oauth", "jwt", "openapi", "swagger",
    # ── Architecture & Patterns ────────────────────────────────────────────
    "microservices", "monolithic architecture", "serverless",
    "event-driven architecture", "domain-driven design",
    "design patterns", "system design", "api design",
    # ── Mobile Development ─────────────────────────────────────────────────
    "android", "ios", "react native", "flutter", "xamarin",
    "swiftui", "jetpack compose", "mobile development",
    # ── Testing ────────────────────────────────────────────────────────────
    "unit testing", "integration testing", "selenium", "cypress",
    "jest", "pytest", "junit", "mocha", "test automation",
    "performance testing", "load testing",
    # ── Security ───────────────────────────────────────────────────────────
    "cybersecurity", "penetration testing", "encryption",
    "network security", "owasp", "soc 2", "vulnerability assessment",
    "identity management", "siem",
    # ── Networking & OS ────────────────────────────────────────────────────
    "linux", "unix", "windows server", "networking", "tcp/ip",
    "dns", "load balancing", "nginx", "apache",
    # ── Blockchain ─────────────────────────────────────────────────────────
    "blockchain", "solidity", "ethereum", "smart contracts", "web3",
    # ── Project Management & Methodologies ─────────────────────────────────
    "agile", "scrum", "kanban", "jira", "confluence", "trello",
    "project management", "product management", "waterfall",
    "lean", "six sigma",
    # ── Soft Skills ────────────────────────────────────────────────────────
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability",
    "creativity", "collaboration", "mentoring", "presentation skills",
    "negotiation", "conflict resolution", "decision making",
    "emotional intelligence", "strategic thinking",
    "stakeholder management", "cross-functional collaboration",
    # ── Other / Misc Tech ──────────────────────────────────────────────────
    "devops", "site reliability engineering", "sre", "iot",
    "embedded systems", "robotics", "ar/vr", "game development",
    "unity", "unreal engine", "figma", "adobe xd", "ui/ux design",
    "technical writing", "documentation", "version control",
]

# ---------------------------------------------------------------------------
# COLOR_PALETTE
# ---------------------------------------------------------------------------

COLOR_PALETTE: Dict[str, str] = {
    "primary": "#1a73e8",
    "primary_dark": "#174ea6",
    "primary_light": "#4285f4",
    "success": "#0f9d58",
    "warning": "#f9ab00",
    "danger": "#ea4335",
    "info": "#4fc3f7",
    "dark_bg": "#0e1117",
    "dark_card": "#1a1a2e",
    "dark_surface": "#16213e",
    "light_bg": "#f8f9fa",
    "light_card": "#ffffff",
    "light_surface": "#e8eaed",
    "text_dark": "#202124",
    "text_light": "#e8eaed",
}

# ---------------------------------------------------------------------------
# format_file_size
# ---------------------------------------------------------------------------


def format_file_size(size_bytes: int | float) -> str:
    """Convert a size in bytes to a human-readable string.

    Args:
        size_bytes: Number of bytes (non-negative).

    Returns:
        A string such as ``"1.23 MB"`` or ``"512 B"``.
    """
    if size_bytes < 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024 or unit == "GB":
            return f"{size_bytes:.2f} {unit}" if unit != "B" else f"{int(size_bytes)} B"
        size_bytes /= 1024
    # Fallback (should not be reached)
    return f"{size_bytes:.2f} GB"


# ---------------------------------------------------------------------------
# get_theme_css
# ---------------------------------------------------------------------------


def get_theme_css(mode: str = "dark") -> str:
    """Return a complete CSS stylesheet for the Streamlit app.

    Args:
        mode: ``'dark'`` or ``'light'``.

    Returns:
        A ``<style>…</style>`` wrapped CSS string ready to inject via
        ``st.markdown(css, unsafe_allow_html=True)``.
    """

    if mode == "dark":
        bg = COLOR_PALETTE["dark_bg"]
        card_bg = "rgba(26, 26, 46, 0.85)"
        card_border = "rgba(255, 255, 255, 0.08)"
        surface = COLOR_PALETTE["dark_surface"]
        text_primary = "#e8eaed"
        text_secondary = "#9aa0a6"
        sidebar_bg = "#1a1a2e"
        input_bg = "rgba(22, 33, 62, 0.9)"
        input_border = "rgba(255, 255, 255, 0.12)"
        table_header_bg = "rgba(26, 115, 232, 0.25)"
        table_stripe = "rgba(255, 255, 255, 0.03)"
        table_hover = "rgba(255, 255, 255, 0.06)"
        scrollbar_track = "#1a1a2e"
        scrollbar_thumb = "#3a3a5e"
        shadow_color = "rgba(0, 0, 0, 0.35)"
        divider = "rgba(255, 255, 255, 0.06)"
    else:
        bg = COLOR_PALETTE["light_bg"]
        card_bg = "rgba(255, 255, 255, 0.85)"
        card_border = "rgba(0, 0, 0, 0.08)"
        surface = COLOR_PALETTE["light_surface"]
        text_primary = COLOR_PALETTE["text_dark"]
        text_secondary = "#5f6368"
        sidebar_bg = "#ffffff"
        input_bg = "rgba(255, 255, 255, 0.95)"
        input_border = "rgba(0, 0, 0, 0.12)"
        table_header_bg = "rgba(26, 115, 232, 0.10)"
        table_stripe = "rgba(0, 0, 0, 0.02)"
        table_hover = "rgba(0, 0, 0, 0.04)"
        scrollbar_track = "#e8eaed"
        scrollbar_thumb = "#bdc1c6"
        shadow_color = "rgba(0, 0, 0, 0.08)"
        divider = "rgba(0, 0, 0, 0.08)"

    primary = COLOR_PALETTE["primary"]
    primary_dark = COLOR_PALETTE["primary_dark"]
    primary_light = COLOR_PALETTE["primary_light"]
    success = COLOR_PALETTE["success"]
    warning = COLOR_PALETTE["warning"]
    danger = COLOR_PALETTE["danger"]
    info = COLOR_PALETTE["info"]

    css = f"""
    <style>
    /* ===================================================================
       AI Resume Screening — Theme: {mode}
       =================================================================== */

    /* ── Google Fonts import ───────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root variables ────────────────────────────────────────────────── */
    :root {{
        --bg: {bg};
        --card-bg: {card_bg};
        --card-border: {card_border};
        --surface: {surface};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --primary: {primary};
        --primary-dark: {primary_dark};
        --primary-light: {primary_light};
        --success: {success};
        --warning: {warning};
        --danger: {danger};
        --info: {info};
        --shadow: {shadow_color};
        --divider: {divider};
        --radius: 12px;
        --transition: 0.25s cubic-bezier(.4,0,.2,1);
    }}

    /* ── Global resets ─────────────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: var(--bg) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    * {{
        scrollbar-width: thin;
        scrollbar-color: {scrollbar_thumb} {scrollbar_track};
    }}

    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {scrollbar_track};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {scrollbar_thumb};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary-light);
    }}

    /* ── Sidebar ───────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid var(--divider);
    }}
    [data-testid="stSidebar"] .stMarkdown {{
        color: var(--text-primary) !important;
    }}

    /* ── Gradient header bar ───────────────────────────────────────────── */
    .gradient-header {{
        background: linear-gradient(135deg, {primary_dark}, {primary}, {primary_light});
        padding: 2rem 2.5rem;
        border-radius: var(--radius);
        margin-bottom: 1.5rem;
        color: #ffffff;
        box-shadow: 0 4px 24px rgba(26, 115, 232, 0.30);
        position: relative;
        overflow: hidden;
    }}
    .gradient-header::after {{
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        pointer-events: none;
    }}
    .gradient-header h1 {{
        margin: 0 0 0.3rem 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    .gradient-header p {{
        margin: 0;
        opacity: 0.9;
        font-size: 1.05rem;
        font-weight: 400;
    }}

    /* ── Glassmorphism card ─────────────────────────────────────────────── */
    .glass-card {{
        background: var(--card-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 16px var(--shadow);
        transition: transform var(--transition), box-shadow var(--transition);
    }}
    .glass-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 32px var(--shadow);
    }}

    /* ── Metric cards ──────────────────────────────────────────────────── */
    .metric-card {{
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 1.25rem 1.5rem;
        text-align: center;
        transition: transform var(--transition), box-shadow var(--transition);
        box-shadow: 0 2px 12px var(--shadow);
    }}
    .metric-card:hover {{
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 28px var(--shadow);
    }}
    .metric-card .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1.2;
    }}
    .metric-card .metric-label {{
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-top: 0.35rem;
    }}
    .metric-card .metric-delta {{
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }}

    /* ── Tables ─────────────────────────────────────────────────────────── */
    .styled-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: 0 2px 12px var(--shadow);
        font-size: 0.9rem;
    }}
    .styled-table thead tr {{
        background: {table_header_bg};
    }}
    .styled-table th {{
        padding: 0.85rem 1rem;
        text-align: left;
        font-weight: 600;
        color: var(--primary);
        border-bottom: 2px solid var(--primary);
        letter-spacing: 0.3px;
    }}
    .styled-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--divider);
        color: var(--text-primary);
    }}
    .styled-table tbody tr:nth-child(even) {{
        background: {table_stripe};
    }}
    .styled-table tbody tr:hover {{
        background: {table_hover};
    }}

    /* ── Buttons ────────────────────────────────────────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {primary}, {primary_light}) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.6rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.2px;
        transition: all var(--transition) !important;
        box-shadow: 0 2px 8px rgba(26, 115, 232, 0.30) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(26, 115, 232, 0.45) !important;
        background: linear-gradient(135deg, {primary_dark}, {primary}) !important;
    }}
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    /* ── Download buttons ──────────────────────────────────────────────── */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {success}, #34a853) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all var(--transition) !important;
        box-shadow: 0 2px 8px rgba(15, 157, 88, 0.30) !important;
    }}
    .stDownloadButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(15, 157, 88, 0.45) !important;
    }}

    /* ── Status badges ─────────────────────────────────────────────────── */
    .badge {{
        display: inline-block;
        padding: 0.3rem 0.85rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}
    .badge-success {{
        background: rgba(15, 157, 88, 0.15);
        color: {success};
        border: 1px solid rgba(15, 157, 88, 0.3);
    }}
    .badge-warning {{
        background: rgba(249, 171, 0, 0.15);
        color: {warning};
        border: 1px solid rgba(249, 171, 0, 0.3);
    }}
    .badge-danger {{
        background: rgba(234, 67, 53, 0.15);
        color: {danger};
        border: 1px solid rgba(234, 67, 53, 0.3);
    }}

    /* ── Highly Suitable / Medium Fit / Not Suitable helpers ───────────── */
    .status-highly-suitable {{
        color: {success};
        font-weight: 700;
    }}
    .status-medium-fit {{
        color: {warning};
        font-weight: 700;
    }}
    .status-not-suitable {{
        color: {danger};
        font-weight: 700;
    }}

    /* ── Input fields ──────────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        transition: border-color var(--transition) !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.15) !important;
    }}

    /* ── File uploader ─────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {{
        border: 2px dashed var(--card-border);
        border-radius: var(--radius);
        padding: 1rem;
        transition: border-color var(--transition);
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: var(--primary-light);
    }}

    /* ── Tabs ───────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: background var(--transition), color var(--transition);
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--primary) !important;
        color: #ffffff !important;
    }}

    /* ── Expanders ──────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        font-weight: 600;
        font-size: 1rem;
        color: var(--text-primary);
    }}

    /* ── Progress bars ─────────────────────────────────────────────────── */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary}, {primary_light}) !important;
        border-radius: 8px;
    }}

    /* ── Tooltips / info ───────────────────────────────────────────────── */
    .info-text {{
        color: var(--text-secondary);
        font-size: 0.85rem;
        line-height: 1.5;
    }}

    /* ── Section titles ────────────────────────────────────────────────── */
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 0.8rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid var(--primary);
        display: inline-block;
    }}

    /* ── Skill chips ───────────────────────────────────────────────────── */
    .skill-chip {{
        display: inline-block;
        padding: 0.25rem 0.7rem;
        margin: 0.2rem;
        border-radius: 16px;
        font-size: 0.78rem;
        font-weight: 500;
        background: rgba(26, 115, 232, 0.12);
        color: var(--primary-light);
        border: 1px solid rgba(26, 115, 232, 0.25);
    }}
    .skill-chip.match {{
        background: rgba(15, 157, 88, 0.15);
        color: {success};
        border-color: rgba(15, 157, 88, 0.35);
    }}
    .skill-chip.missing {{
        background: rgba(234, 67, 53, 0.12);
        color: {danger};
        border-color: rgba(234, 67, 53, 0.25);
    }}

    /* ── Score ring (for candidate cards) ──────────────────────────────── */
    .score-ring {{
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0 auto;
    }}

    /* ── Animations ─────────────────────────────────────────────────────── */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(16px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{
        animation: fadeInUp 0.45s ease-out both;
    }}

    /* ── Footer ────────────────────────────────────────────────────────── */
    .app-footer {{
        text-align: center;
        padding: 1.5rem 0;
        color: var(--text-secondary);
        font-size: 0.82rem;
        border-top: 1px solid var(--divider);
        margin-top: 3rem;
    }}

    /* ── Responsive helpers ─────────────────────────────────────────────── */
    @media (max-width: 768px) {{
        .gradient-header h1 {{ font-size: 1.4rem; }}
        .metric-card .metric-value {{ font-size: 1.5rem; }}
    }}
    </style>
    """
    return css


# ---------------------------------------------------------------------------
# generate_pdf_report
# ---------------------------------------------------------------------------


def generate_pdf_report(
    candidates_data: List[Dict[str, Any]],
    jd_text: str,
    jd_skills: List[str],
) -> bytes:
    """Generate a professional multi-page PDF screening report.

    Args:
        candidates_data: List of candidate dicts.  Each dict should contain
            keys: ``name``, ``email``, ``skills``, ``education``,
            ``experience``, ``match_score``, ``category``, ``strengths``,
            ``weaknesses``, ``recommendation``, ``suggestions``.
        jd_text: The full job-description text.
        jd_skills: Skills extracted from the job description.

    Returns:
        The generated PDF file content as ``bytes``.
    """

    # Sanitise helper – strip non-latin-1 characters to avoid FPDF errors.
    def _safe(text: Any) -> str:
        if text is None:
            return ""
        s = str(text)
        return s.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Colours
    c_primary = (26, 115, 232)   # #1a73e8
    c_dark = (23, 78, 166)       # #174ea6
    c_white = (255, 255, 255)
    c_light_grey = (248, 249, 250)
    c_mid_grey = (232, 234, 237)
    c_text = (32, 33, 36)
    c_success = (15, 157, 88)
    c_warning = (249, 171, 0)
    c_danger = (234, 67, 53)

    today = datetime.date.today().strftime("%B %d, %Y")

    # ------------------------------------------------------------------
    # Helper: section header
    # ------------------------------------------------------------------
    def _section_header(title: str) -> None:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*c_primary)
        pdf.cell(0, 10, _safe(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*c_primary)
        pdf.set_line_width(0.6)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(4)
        pdf.set_text_color(*c_text)

    # ------------------------------------------------------------------
    # Page 1 — Title page
    # ------------------------------------------------------------------
    pdf.add_page()

    # Gradient-style banner (solid colour since FPDF has no gradients)
    pdf.set_fill_color(*c_primary)
    pdf.rect(0, 0, 210, 100, "F")

    # Accent stripe
    pdf.set_fill_color(*c_dark)
    pdf.rect(0, 95, 210, 5, "F")

    # Title text
    pdf.set_y(28)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*c_white)
    pdf.cell(0, 14, "AI Resume Screening Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, _safe(f"Generated on {today}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, "Powered by AI Resume Screening & Job Matching System", align="C", new_x="LMARGIN", new_y="NEXT")

    # Reset text colour
    pdf.set_text_color(*c_text)

    # ------------------------------------------------------------------
    # Summary statistics
    # ------------------------------------------------------------------
    pdf.set_y(115)
    _section_header("Executive Summary")

    total = len(candidates_data)
    scores = [c.get("match_score", 0) for c in candidates_data]
    avg_score = sum(scores) / total if total else 0
    top_candidate = max(candidates_data, key=lambda c: c.get("match_score", 0)) if total else {}

    pdf.set_font("Helvetica", "", 11)
    summary_items = [
        f"Total Candidates Evaluated: {total}",
        f"Average Match Score: {avg_score:.1f}%",
        f"Top Candidate: {top_candidate.get('name', 'N/A')} "
        f"({top_candidate.get('match_score', 0):.1f}%)",
        f"Report Date: {today}",
    ]
    for item in summary_items:
        pdf.cell(0, 7, _safe(f"  {item}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ------------------------------------------------------------------
    # Job description summary
    # ------------------------------------------------------------------
    _section_header("Job Description Summary")
    pdf.set_font("Helvetica", "", 10)
    jd_preview = jd_text[:1500] + ("..." if len(jd_text) > 1500 else "")
    pdf.multi_cell(0, 5.5, _safe(jd_preview))
    pdf.ln(4)

    # ------------------------------------------------------------------
    # Required skills
    # ------------------------------------------------------------------
    _section_header("Required Skills")
    pdf.set_font("Helvetica", "", 10)
    skills_line = ", ".join(jd_skills) if jd_skills else "None identified"
    pdf.multi_cell(0, 5.5, _safe(skills_line))
    pdf.ln(6)

    # ------------------------------------------------------------------
    # Candidate ranking table
    # ------------------------------------------------------------------
    pdf.add_page()
    _section_header("Candidate Rankings")

    sorted_candidates = sorted(candidates_data, key=lambda c: c.get("match_score", 0), reverse=True)

    col_widths = [12, 55, 25, 40, 58]
    headers = ["Rank", "Name", "Score", "Category", "Recommendation"]

    # Table header row
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*c_primary)
    pdf.set_text_color(*c_white)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 9, header, border=1, fill=True, align="C")
    pdf.ln()

    # Table body
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*c_text)
    for rank, cand in enumerate(sorted_candidates, start=1):
        if pdf.get_y() > 265:
            pdf.add_page()
        fill = rank % 2 == 0
        pdf.set_fill_color(*c_light_grey)

        row_data = [
            str(rank),
            _safe(cand.get("name", "N/A")),
            f"{cand.get('match_score', 0):.1f}%",
            _safe(cand.get("category", "N/A")),
            _safe(cand.get("recommendation", "N/A")),
        ]
        for i, val in enumerate(row_data):
            pdf.cell(col_widths[i], 8, val, border=1, fill=fill, align="C" if i in (0, 2) else "L")
        pdf.ln()

    pdf.ln(6)

    # ------------------------------------------------------------------
    # Detailed candidate profiles
    # ------------------------------------------------------------------
    for rank, cand in enumerate(sorted_candidates, start=1):
        pdf.add_page()

        # Candidate header banner
        pdf.set_fill_color(*c_primary)
        pdf.rect(10, pdf.get_y(), 190, 12, "F")
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*c_white)
        pdf.cell(0, 12, _safe(f"  #{rank}  {cand.get('name', 'N/A')}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*c_text)
        pdf.ln(4)

        # Candidate meta fields
        details: list[tuple[str, str]] = [
            ("Email", cand.get("email", "N/A")),
            ("Match Score", f"{cand.get('match_score', 0):.1f}%"),
            ("Category", cand.get("category", "N/A")),
            ("Education", cand.get("education", "N/A")),
            ("Experience", cand.get("experience", "N/A")),
        ]

        pdf.set_font("Helvetica", "", 10)
        for label, value in details:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(35, 7, _safe(f"{label}:"))
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, _safe(str(value)), new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)

        # Skills
        _sub_header("Skills")
        skills_val = cand.get("skills", [])
        if isinstance(skills_val, list):
            skills_str = ", ".join(str(s) for s in skills_val)
        else:
            skills_str = str(skills_val)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5.5, _safe(skills_str))
        pdf.ln(3)

        # Strengths
        _sub_header("Strengths")
        strengths = cand.get("strengths", [])
        if isinstance(strengths, list):
            for s in strengths:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, _safe(f"  + {s}"), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5.5, _safe(str(strengths)))
        pdf.ln(2)

        # Weaknesses
        _sub_header("Weaknesses / Gaps")
        weaknesses = cand.get("weaknesses", [])
        if isinstance(weaknesses, list):
            for w in weaknesses:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, _safe(f"  - {w}"), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5.5, _safe(str(weaknesses)))
        pdf.ln(2)

        # Recommendation
        _sub_header("Recommendation")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5.5, _safe(str(cand.get("recommendation", "N/A"))))
        pdf.ln(2)

        # Suggestions
        _sub_header("Improvement Suggestions")
        suggestions = cand.get("suggestions", [])
        if isinstance(suggestions, list):
            for sg in suggestions:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, _safe(f"  * {sg}"), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5.5, _safe(str(suggestions)))
        pdf.ln(4)

    # ------------------------------------------------------------------
    # Closure: sub-header helper (used above via closure over pdf)
    # ------------------------------------------------------------------
    # (defined as a nested function for clarity)

    # Return bytes
    return pdf.output()


# Nested helper defined at module-level so it can be referenced inside
# generate_pdf_report.  We use a small trick: because FPDF methods mutate
# the instance, we pass pdf via a wrapper.  However to keep the code
# above clean we rely on Python closure scoping — but closures inside a
# for-loop body referencing a not-yet-defined name won't work.  Instead
# we define a module-level helper that accepts pdf explicitly and rebind
# it inside the function.

def _make_sub_header(pdf_inst: FPDF, c_primary: tuple):
    """Return a sub-header printer bound to *pdf_inst*."""

    def _sub_header(title: str) -> None:
        pdf_inst.set_font("Helvetica", "B", 11)
        pdf_inst.set_text_color(*c_primary)
        safe_title = title.encode("latin-1", errors="replace").decode("latin-1")
        pdf_inst.cell(0, 7, safe_title, new_x="LMARGIN", new_y="NEXT")
        pdf_inst.set_text_color(32, 33, 36)

    return _sub_header


# Patch generate_pdf_report to use the sub-header helper properly.
# We redefine it cleanly below so that _sub_header is available inside
# the candidate loop.

_original_generate = generate_pdf_report


def generate_pdf_report(
    candidates_data: List[Dict[str, Any]],
    jd_text: str,
    jd_skills: List[str],
) -> bytes:
    """Generate a professional multi-page PDF screening report.

    Args:
        candidates_data: List of candidate dicts.  Each dict should contain
            keys: ``name``, ``email``, ``skills``, ``education``,
            ``experience``, ``match_score``, ``category``, ``strengths``,
            ``weaknesses``, ``recommendation``, ``suggestions``.
        jd_text: The full job-description text.
        jd_skills: Skills extracted from the job description.

    Returns:
        The generated PDF file content as ``bytes``.
    """

    def _safe(text: Any) -> str:
        if text is None:
            return ""
        s = str(text)
        return s.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    c_primary = (26, 115, 232)
    c_dark = (23, 78, 166)
    c_white = (255, 255, 255)
    c_light_grey = (248, 249, 250)
    c_text = (32, 33, 36)

    today = datetime.date.today().strftime("%B %d, %Y")

    def _section_header(title: str) -> None:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*c_primary)
        pdf.cell(0, 10, _safe(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*c_primary)
        pdf.set_line_width(0.6)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(4)
        pdf.set_text_color(*c_text)

    def _sub_header(title: str) -> None:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*c_primary)
        pdf.cell(0, 7, _safe(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*c_text)

    # === Title page ===
    pdf.add_page()
    pdf.set_fill_color(*c_primary)
    pdf.rect(0, 0, 210, 100, "F")
    pdf.set_fill_color(*c_dark)
    pdf.rect(0, 95, 210, 5, "F")

    pdf.set_y(28)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*c_white)
    pdf.cell(0, 14, "AI Resume Screening Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, _safe(f"Generated on {today}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, "Powered by AI Resume Screening & Job Matching System", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*c_text)

    # === Executive Summary ===
    pdf.set_y(115)
    _section_header("Executive Summary")

    total = len(candidates_data)
    scores = [c.get("match_score", 0) for c in candidates_data]
    avg_score = sum(scores) / total if total else 0
    top_candidate = max(candidates_data, key=lambda c: c.get("match_score", 0)) if total else {}

    pdf.set_font("Helvetica", "", 11)
    for item in [
        f"Total Candidates Evaluated: {total}",
        f"Average Match Score: {avg_score:.1f}%",
        f"Top Candidate: {top_candidate.get('name', 'N/A')} ({top_candidate.get('match_score', 0):.1f}%)",
        f"Report Date: {today}",
    ]:
        pdf.cell(0, 7, _safe(f"  {item}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # === Job Description ===
    _section_header("Job Description Summary")
    pdf.set_font("Helvetica", "", 10)
    jd_preview = jd_text[:1500] + ("..." if len(jd_text) > 1500 else "")
    pdf.multi_cell(0, 5.5, _safe(jd_preview))
    pdf.ln(4)

    # === Required Skills ===
    _section_header("Required Skills")
    pdf.set_font("Helvetica", "", 10)
    skills_line = ", ".join(jd_skills) if jd_skills else "None identified"
    pdf.multi_cell(0, 5.5, _safe(skills_line))
    pdf.ln(6)

    # === Ranking Table ===
    pdf.add_page()
    _section_header("Candidate Rankings")
    sorted_candidates = sorted(candidates_data, key=lambda c: c.get("match_score", 0), reverse=True)

    col_widths = [12, 55, 25, 40, 58]
    headers = ["Rank", "Name", "Score", "Category", "Recommendation"]

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*c_primary)
    pdf.set_text_color(*c_white)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 9, header, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(*c_text)

    pdf.set_font("Helvetica", "", 9)
    for rank, cand in enumerate(sorted_candidates, start=1):
        if pdf.get_y() > 265:
            pdf.add_page()
        fill = rank % 2 == 0
        pdf.set_fill_color(*c_light_grey)
        row = [
            str(rank),
            _safe(cand.get("name", "N/A")),
            f"{cand.get('match_score', 0):.1f}%",
            _safe(cand.get("category", "N/A")),
            _safe(cand.get("recommendation", "N/A")),
        ]
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 8, val, border=1, fill=fill, align="C" if i in (0, 2) else "L")
        pdf.ln()
    pdf.ln(6)

    # === Detailed Profiles ===
    for rank, cand in enumerate(sorted_candidates, start=1):
        pdf.add_page()

        pdf.set_fill_color(*c_primary)
        y_start = pdf.get_y()
        pdf.rect(10, y_start, 190, 12, "F")
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*c_white)
        pdf.cell(0, 12, _safe(f"  #{rank}  {cand.get('name', 'N/A')}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*c_text)
        pdf.ln(4)

        for label, value in [
            ("Email", cand.get("email", "N/A")),
            ("Match Score", f"{cand.get('match_score', 0):.1f}%"),
            ("Category", cand.get("category", "N/A")),
            ("Education", cand.get("education", "N/A")),
            ("Experience", cand.get("experience", "N/A")),
        ]:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(35, 7, _safe(f"{label}:"))
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, _safe(str(value)), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Skills
        _sub_header("Skills")
        skills_val = cand.get("skills", [])
        skills_str = ", ".join(str(s) for s in skills_val) if isinstance(skills_val, list) else str(skills_val)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5.5, _safe(skills_str))
        pdf.ln(3)

        # Strengths
        _sub_header("Strengths")
        strengths = cand.get("strengths", [])
        if isinstance(strengths, list):
            for s in strengths:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, _safe(f"  + {s}"), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5.5, _safe(str(strengths)))
        pdf.ln(2)

        # Weaknesses
        _sub_header("Weaknesses / Gaps")
        weaknesses = cand.get("weaknesses", [])
        if isinstance(weaknesses, list):
            for w in weaknesses:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, _safe(f"  - {w}"), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5.5, _safe(str(weaknesses)))
        pdf.ln(2)

        # Recommendation
        _sub_header("Recommendation")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5.5, _safe(str(cand.get("recommendation", "N/A"))))
        pdf.ln(2)

        # Suggestions
        _sub_header("Improvement Suggestions")
        suggestions = cand.get("suggestions", [])
        if isinstance(suggestions, list):
            for sg in suggestions:
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, _safe(f"  * {sg}"), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5.5, _safe(str(suggestions)))
        pdf.ln(4)

    # Return PDF bytes
    return pdf.output()
