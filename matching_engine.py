"""
matching_engine.py — AI Matching Engine for Resume Screening & Job Matching System.

Provides TF-IDF cosine similarity scoring, Jaccard-based skill matching,
candidate ranking with categorisation, professional recommendation generation,
and skill-gap analysis across candidate pools.
"""

import re
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# 1. JD Skill Extraction
# ---------------------------------------------------------------------------

def extract_jd_skills(jd_text: str, skill_database: list[str]) -> list[str]:
    """Extract recognised skills from a job-description text.

    Converts the JD to lowercase and matches every skill in
    *skill_database* that appears in the text.  Short skills (≤ 3 chars)
    are matched using word-boundary anchors to avoid false positives.

    Args:
        jd_text: Raw job-description text.
        skill_database: Iterable of canonical skill names to search for.

    Returns:
        A sorted list of matched skill names (original casing from the
        database preserved).
    """
    if not jd_text or not skill_database:
        return []

    jd_lower = jd_text.lower()
    matched_skills: list[str] = []

    for skill in skill_database:
        skill_lower = skill.lower()
        # Use word-boundary matching for short skills to avoid partial hits
        if len(skill_lower) <= 3:
            pattern = r"\b" + re.escape(skill_lower) + r"\b"
            if re.search(pattern, jd_lower):
                matched_skills.append(skill)
        else:
            if skill_lower in jd_lower:
                matched_skills.append(skill)

    return sorted(set(matched_skills), key=str.lower)


# ---------------------------------------------------------------------------
# 2. TF-IDF Cosine Similarity
# ---------------------------------------------------------------------------

def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Compute TF-IDF cosine similarity between a résumé and a JD.

    Fits a TF-IDF vectoriser on the two documents and returns the cosine
    similarity of their vector representations.

    Args:
        resume_text: Plain-text content of the résumé.
        jd_text: Plain-text content of the job description.

    Returns:
        A float in [0.0, 1.0] representing semantic similarity.
        Returns 0.0 when either input is empty or vectorisation fails.
    """
    if not resume_text or not jd_text:
        return 0.0

    # Strip to guard against whitespace-only strings
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    try:
        vectoriser = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectoriser.fit_transform([resume_text, jd_text])

        # cosine_similarity returns a 2×2 matrix; we need [0][1]
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity[0][0])

        # Clamp to [0, 1] to guard against floating-point drift
        return float(np.clip(score, 0.0, 1.0))
    except ValueError:
        # Raised when vocabulary is empty after stop-word removal
        return 0.0


# ---------------------------------------------------------------------------
# 3. Skill-Match Score (Jaccard-like)
# ---------------------------------------------------------------------------

def compute_skill_match(resume_skills: list[str], jd_skills: list[str]) -> float:
    """Compute Jaccard-like skill overlap relative to JD requirements.

    The score equals ``|intersection| / |jd_skills|``, measuring what
    fraction of the required skills the candidate possesses.

    Args:
        resume_skills: Skills extracted from the candidate's résumé.
        jd_skills: Skills required by the job description.

    Returns:
        A float in [0.0, 1.0].  Returns 0.0 when *jd_skills* is empty.
    """
    if not jd_skills:
        return 0.0

    resume_set = {s.lower().strip() for s in resume_skills} if resume_skills else set()
    jd_set = {s.lower().strip() for s in jd_skills}

    if not jd_set:
        return 0.0

    intersection = resume_set & jd_set
    return len(intersection) / len(jd_set)


# ---------------------------------------------------------------------------
# 4. Composite Match Score
# ---------------------------------------------------------------------------

def compute_match_score(
    candidate_data: dict,
    jd_text: str,
    jd_skills: list[str],
) -> float:
    """Compute a weighted match score for one candidate against a JD.

    Combines TF-IDF similarity (40 %) and skill-match score (60 %) into
    a single percentage value in [0, 100].

    Args:
        candidate_data: Dict with at least ``'raw_text'`` and ``'skills'``
            keys (as returned by *parse_resume*).
        jd_text: Raw job-description text.
        jd_skills: Skills extracted from the job description.

    Returns:
        A float rounded to one decimal place in [0.0, 100.0].
    """
    raw_text = candidate_data.get("raw_text", "")
    resume_skills = candidate_data.get("skills", [])

    tfidf_sim = compute_tfidf_similarity(raw_text, jd_text)
    skill_match = compute_skill_match(resume_skills, jd_skills)

    score = (0.6 * skill_match + 0.4 * tfidf_sim) * 100.0

    # Clamp and round
    score = float(np.clip(score, 0.0, 100.0))
    return round(score, 1)


# ---------------------------------------------------------------------------
# 5. Candidate Categorisation
# ---------------------------------------------------------------------------

def categorize_candidate(score: float) -> str:
    """Categorise a candidate based on their match score.

    Args:
        score: Numeric match score (0–100).

    Returns:
        ``'Highly Suitable'`` for scores ≥ 80,
        ``'Medium Fit'`` for scores in [50, 80),
        ``'Not Suitable'`` for scores < 50.
    """
    if score >= 80:
        return "Highly Suitable"
    if score >= 50:
        return "Medium Fit"
    return "Not Suitable"


# ---------------------------------------------------------------------------
# 6. Candidate Ranking
# ---------------------------------------------------------------------------

def rank_candidates(
    candidates_data: list[dict],
    jd_text: str,
    jd_skills: list[str],
) -> list[dict]:
    """Rank a pool of candidates against a job description.

    Each candidate dict is augmented in-place with ``'match_score'``,
    ``'category'``, and ``'rank'`` keys, then returned sorted by
    *match_score* descending.

    Args:
        candidates_data: List of candidate dicts (as returned by
            *parse_resume*), each containing at least ``'raw_text'``
            and ``'skills'``.
        jd_text: Raw job-description text.
        jd_skills: Skills extracted from the job description.

    Returns:
        The same list, sorted descending by match score, with ranking
        metadata attached.
    """
    if not candidates_data:
        return []

    for candidate in candidates_data:
        score = compute_match_score(candidate, jd_text, jd_skills)
        candidate["match_score"] = score
        candidate["category"] = categorize_candidate(score)

    # Sort descending by match_score; ties broken by name for stability
    candidates_data.sort(
        key=lambda c: (-c["match_score"], c.get("name", "")),
    )

    for idx, candidate in enumerate(candidates_data, start=1):
        candidate["rank"] = idx

    return candidates_data


# ---------------------------------------------------------------------------
# 7. Recommendation Generation
# ---------------------------------------------------------------------------

def generate_recommendation(candidate: dict, jd_skills: list[str]) -> dict:
    """Generate a professional AI-style recommendation for a candidate.

    Produces structured feedback including strengths, weaknesses,
    an overall hiring recommendation, and actionable improvement
    suggestions.

    Args:
        candidate: Dict with keys ``'skills'``, ``'match_score'``,
            ``'category'``, ``'education'``, ``'experience'``, and
            ``'name'``.
        jd_skills: Skills required by the job description.

    Returns:
        A dict with keys:
        - ``strengths``  – list[str]
        - ``weaknesses`` – list[str]
        - ``recommendation`` – ``'Yes'`` | ``'Maybe'`` | ``'No'``
        - ``suggestions`` – list[str]
    """
    candidate_skills = candidate.get("skills", [])
    education = candidate.get("education", [])
    experience = candidate.get("experience", [])
    name = candidate.get("name", "The candidate")
    category = candidate.get("category", "Not Suitable")
    match_score = candidate.get("match_score", 0.0)

    # Normalise for comparison
    candidate_skills_lower = {s.lower().strip() for s in candidate_skills}
    jd_skills_lower = {s.lower().strip() for s in jd_skills} if jd_skills else set()

    matched = candidate_skills_lower & jd_skills_lower
    missing = jd_skills_lower - candidate_skills_lower

    # ----- Strengths -----
    strengths: list[str] = []

    if matched:
        skill_list = ", ".join(sorted(matched, key=str.lower))
        strengths.append(
            f"Demonstrates proficiency in key required skills: {skill_list}."
        )

    if education:
        edu_highlights = "; ".join(education[:3])  # Limit to top 3
        strengths.append(
            f"Educational background includes: {edu_highlights}."
        )

    if experience:
        exp_highlights = "; ".join(experience[:3])
        strengths.append(
            f"Relevant professional experience: {exp_highlights}."
        )

    if match_score >= 80:
        strengths.append(
            f"Overall match score of {match_score}% indicates an excellent "
            f"alignment with the role requirements."
        )
    elif match_score >= 50:
        strengths.append(
            f"Overall match score of {match_score}% indicates a moderate "
            f"alignment with the role requirements."
        )

    if not strengths:
        strengths.append(
            "No specific strengths could be identified from the available data."
        )

    # ----- Weaknesses -----
    weaknesses: list[str] = []

    if missing:
        missing_list = ", ".join(sorted(missing, key=str.lower))
        weaknesses.append(
            f"Missing critical skills required for the role: {missing_list}."
        )
        gap_pct = (len(missing) / len(jd_skills_lower)) * 100 if jd_skills_lower else 0
        if gap_pct > 50:
            weaknesses.append(
                f"Significant skill gap detected — {gap_pct:.0f}% of required "
                f"skills are not evidenced in the résumé."
            )

    if not education:
        weaknesses.append(
            "No formal education details were identified in the résumé."
        )

    if not experience:
        weaknesses.append(
            "No professional experience entries were identified in the résumé."
        )

    if not weaknesses:
        weaknesses.append(
            "No significant weaknesses identified based on available data."
        )

    # ----- Recommendation -----
    if category == "Highly Suitable":
        recommendation = "Yes"
    elif category == "Medium Fit":
        recommendation = "Maybe"
    else:
        recommendation = "No"

    # ----- Suggestions -----
    suggestions: list[str] = _build_suggestions(missing)

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation,
        "suggestions": suggestions,
    }


def _build_suggestions(missing_skills: set[str]) -> list[str]:
    """Create actionable skill-improvement suggestions for missing skills.

    Groups well-known skills into thematic suggestions to produce concise,
    professional advice rather than a raw list.

    Args:
        missing_skills: Set of lower-cased skill names the candidate lacks.

    Returns:
        List of human-readable suggestion strings.
    """
    if not missing_skills:
        return ["Continue developing existing skill set and stay current with industry trends."]

    suggestions: list[str] = []

    # Thematic groupings for richer suggestions
    _CERT_MAP: dict[str, str] = {
        "aws": "Consider obtaining an AWS certification (e.g., AWS Certified Solutions Architect) to validate cloud competency.",
        "azure": "Consider pursuing a Microsoft Azure certification to demonstrate cloud platform expertise.",
        "gcp": "Consider earning a Google Cloud Professional certification to strengthen cloud credentials.",
        "docker": "Gain hands-on experience with Docker and containerisation to meet modern deployment expectations.",
        "kubernetes": "Develop proficiency in Kubernetes orchestration through online labs or professional projects.",
        "terraform": "Learn Terraform for infrastructure-as-code; HashiCorp offers a structured certification path.",
        "python": "Strengthen Python skills through project-based learning or an advanced Python certification.",
        "java": "Consider completing an Oracle Java certification to formalise Java proficiency.",
        "sql": "Enhance SQL skills through structured courses and practice on platforms like LeetCode or HackerRank.",
        "machine learning": "Pursue a machine learning specialisation (e.g., Andrew Ng's Coursera course) to build foundational ML skills.",
        "deep learning": "Explore deep learning frameworks such as TensorFlow or PyTorch through hands-on projects.",
        "react": "Build proficiency in React.js through portfolio projects or a front-end development bootcamp.",
        "angular": "Consider completing an Angular certification or guided project to demonstrate front-end capability.",
        "node.js": "Gain experience with Node.js back-end development through real-world application building.",
        "javascript": "Strengthen JavaScript fundamentals and modern ES6+ features through structured coursework.",
        "typescript": "Learn TypeScript to improve code quality and align with modern development practices.",
        "git": "Develop Git version-control skills through daily practice and collaborative open-source contributions.",
        "ci/cd": "Familiarise yourself with CI/CD pipelines (e.g., Jenkins, GitHub Actions) to meet DevOps expectations.",
        "agile": "Obtain a Certified ScrumMaster (CSM) or similar Agile certification to demonstrate methodology knowledge.",
        "scrum": "Consider a Professional Scrum Master certification to validate Agile project management skills.",
        "linux": "Build Linux system administration skills through hands-on practice or an LPIC certification.",
        "data analysis": "Develop data analysis skills using tools such as pandas, Excel, or Tableau.",
        "tableau": "Learn Tableau for data visualisation through Tableau's free training resources.",
        "power bi": "Gain proficiency in Power BI for business intelligence and reporting.",
        "spark": "Explore Apache Spark for big-data processing through Databricks community resources.",
        "hadoop": "Familiarise yourself with the Hadoop ecosystem for large-scale data processing.",
        "nlp": "Study natural language processing techniques and libraries such as spaCy or NLTK.",
        "computer vision": "Explore computer vision with OpenCV or similar frameworks through guided projects.",
        "mongodb": "Learn MongoDB for NoSQL database management through MongoDB University's free courses.",
        "redis": "Gain experience with Redis for in-memory caching and real-time data handling.",
        "graphql": "Consider learning GraphQL as a modern API query language alongside REST.",
        "rest": "Strengthen understanding of RESTful API design principles and best practices.",
        "flask": "Build Flask-based web applications to demonstrate Python web-development capability.",
        "django": "Develop Django skills for full-stack Python web development through project-based learning.",
    }

    handled: set[str] = set()

    for skill in sorted(missing_skills, key=str.lower):
        if skill in _CERT_MAP:
            suggestions.append(_CERT_MAP[skill])
            handled.add(skill)

    # Generic suggestion for remaining skills
    remaining = missing_skills - handled
    if remaining:
        for skill in sorted(remaining, key=str.lower):
            suggestions.append(
                f"Consider gaining proficiency in {skill} through targeted "
                f"coursework, certifications, or hands-on projects."
            )

    return suggestions


# ---------------------------------------------------------------------------
# 8. Skill-Gap Analysis
# ---------------------------------------------------------------------------

def skill_gap_analysis(
    candidates_data: list[dict],
    jd_skills: list[str],
) -> dict[str, int]:
    """Analyse how prevalent each JD skill is across the candidate pool.

    For every skill in *jd_skills*, counts how many candidates possess it.
    The result is useful for identifying talent-market gaps on the
    dashboard.

    Args:
        candidates_data: List of candidate dicts, each with a ``'skills'``
            key.
        jd_skills: Skills required by the job description.

    Returns:
        A dict mapping each JD skill (original casing) to the number of
        candidates who possess it, sorted descending by count.
    """
    if not jd_skills or not candidates_data:
        return {}

    # Build a counter keyed on the original-cased JD skill
    skill_counts: dict[str, int] = {skill: 0 for skill in jd_skills}

    for candidate in candidates_data:
        candidate_skills_lower = {
            s.lower().strip() for s in candidate.get("skills", [])
        }
        for skill in jd_skills:
            if skill.lower().strip() in candidate_skills_lower:
                skill_counts[skill] += 1

    # Sort descending by count, then alphabetically for ties
    sorted_skills = dict(
        sorted(skill_counts.items(), key=lambda item: (-item[1], item[0].lower()))
    )

    return sorted_skills
