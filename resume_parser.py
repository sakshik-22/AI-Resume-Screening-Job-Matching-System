"""
resume_parser.py
~~~~~~~~~~~~~~~~
Resume parsing module for the AI Resume Screening & Job Matching System.

Provides functions to extract text from PDF and DOCX files, parse contact
information (name, email, phone), identify skills against a known database,
detect education qualifications, and estimate professional experience.
"""

import re
import io
import os
import tempfile

import PyPDF2
import docx2txt


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    """Extract all text content from an uploaded PDF file.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        A Streamlit UploadedFile object exposing a ``.read()`` method.

    Returns
    -------
    str
        Concatenated text from every page of the PDF.
        Returns an empty string if extraction fails.
    """
    try:
        pdf_bytes = uploaded_file.read()
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(uploaded_file):
    """Extract all text content from an uploaded DOCX file.

    The uploaded bytes are written to a temporary file so that
    ``docx2txt.process`` can read them.  The temp file is deleted
    after processing.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        A Streamlit UploadedFile object exposing a ``.read()`` method.

    Returns
    -------
    str
        Extracted text from the DOCX document.
        Returns an empty string if extraction fails.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        text = docx2txt.process(tmp_path)
        return text if text else ""
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# ---------------------------------------------------------------------------
# Contact‑information extractors
# ---------------------------------------------------------------------------

def extract_email(text):
    """Extract the first email address found in *text*.

    Parameters
    ----------
    text : str
        Raw resume text.

    Returns
    -------
    str
        The first email address matched, or ``'Not found'``.
    """
    try:
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group() if match else "Not found"
    except Exception as e:
        print(f"Error extracting email: {e}")
        return "Not found"


def extract_phone(text):
    """Extract the first phone number found in *text*.

    Supports a variety of common formats including:

    * ``+1-234-567-8901``
    * ``(234) 567-8901``
    * ``234-567-8901``
    * ``234.567.8901``
    * ``2345678901``
    * ``+91 XXXXXXXXXX`` (Indian format)

    Parameters
    ----------
    text : str
        Raw resume text.

    Returns
    -------
    str
        The first phone number matched, or ``'Not found'``.
    """
    try:
        pattern = (
            r'(?:\+?\d{1,3}[-.\s]?)?'   # optional country code
            r'(?:\(?\d{2,4}\)?[-.\s]?)?'  # optional area code
            r'\d{3,5}'                    # first digit group
            r'[-.\s]?'                    # separator
            r'\d{3,5}'                    # second digit group
            r'(?:[-.\s]?\d{1,5})?'        # optional extension
        )
        # Collect all candidates and filter for plausible phone numbers
        candidates = re.findall(pattern, text)
        for candidate in candidates:
            digits = re.sub(r'\D', '', candidate)
            if 10 <= len(digits) <= 15:
                return candidate.strip()
        return "Not found"
    except Exception as e:
        print(f"Error extracting phone number: {e}")
        return "Not found"


def extract_name(text):
    """Heuristically extract the candidate's name from the resume text.

    Strategy
    --------
    1. Take the first 5 non-empty lines of the text.
    2. Skip lines containing common non-name keywords (e.g. *email*,
       *phone*, *objective*, *summary*, *resume*, *curriculum*, etc.).
    3. Look for lines that are likely names: 2–4 words, mostly
       alphabetic characters, and written in title case.
    4. Return the best candidate or ``'Unknown Candidate'``.

    Parameters
    ----------
    text : str
        Raw resume text.

    Returns
    -------
    str
        Best-guess candidate name.
    """
    try:
        skip_keywords = {
            "email", "phone", "address", "objective", "summary",
            "resume", "curriculum", "vitae", "profile", "contact",
            "mobile", "linkedin", "github", "website", "http",
            "www", "experience", "education", "skills", "projects",
        }

        lines = text.strip().split("\n")
        non_empty_lines = [line.strip() for line in lines if line.strip()][:5]

        for line in non_empty_lines:
            lower_line = line.lower()
            # Skip lines that contain any non-name keyword
            if any(kw in lower_line for kw in skip_keywords):
                continue

            words = line.split()
            if 2 <= len(words) <= 4:
                # Check that most words are alphabetic
                alpha_words = [w for w in words if w.replace(".", "").isalpha()]
                if len(alpha_words) >= len(words) - 1:
                    # Check for title-case or all-upper (common in resumes)
                    if line.istitle() or line.isupper():
                        return line.title() if line.isupper() else line

        return "Unknown Candidate"
    except Exception as e:
        print(f"Error extracting name: {e}")
        return "Unknown Candidate"


# ---------------------------------------------------------------------------
# Skills, education & experience extractors
# ---------------------------------------------------------------------------

def extract_skills(text, skill_database):
    """Identify skills present in the resume text.

    Parameters
    ----------
    text : str
        Raw resume text.
    skill_database : list[str]
        A list of known skill names / phrases to search for.

    Returns
    -------
    list[str]
        A sorted list of skills that were found in the text.

    Notes
    -----
    * Matching is case-insensitive.
    * Single-character or single-word skills are matched using regex
      word boundaries (``\\b``) to avoid false positives (e.g. the
      skill ``'r'`` should not match inside the word *program*).
    * Multi-word skills are matched by simple substring containment
      in the lowercased text.
    """
    try:
        text_lower = text.lower()
        found_skills = []

        for skill in skill_database:
            skill_lower = skill.lower().strip()
            if not skill_lower:
                continue

            # Decide matching strategy based on whether the skill is a
            # single token or a multi-word phrase.
            if " " not in skill_lower:
                # Use word-boundary regex for single-token skills
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            else:
                # Multi-word phrase – plain substring check is sufficient
                if skill_lower in text_lower:
                    found_skills.append(skill)

        return sorted(set(found_skills), key=lambda s: s.lower())
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []


def extract_education(text):
    """Extract education qualifications mentioned in the resume.

    Looks for degree abbreviations (B.Tech, M.S., Ph.D, MBA, …),
    degree keywords (Bachelor, Master, Doctorate, Diploma, Certificate),
    university names, and graduation years.

    Parameters
    ----------
    text : str
        Raw resume text.

    Returns
    -------
    list[str]
        A list of education-related lines/entries found.
        Returns ``['Not specified']`` when nothing is detected.
    """
    try:
        degree_patterns = [
            # Undergraduate
            r'B\.?\s?Tech',
            r'B\.?\s?E\.?',
            r'B\.?\s?Sc\.?',
            r'B\.?\s?S\.?',
            r'B\.?\s?A\.?',
            r'Bachelor(?:\'?s)?',
            # Postgraduate
            r'M\.?\s?Tech',
            r'M\.?\s?E\.?',
            r'M\.?\s?Sc\.?',
            r'M\.?\s?S\.?',
            r'M\.?\s?A\.?',
            r'Master(?:\'?s)?',
            r'MBA',
            # Doctoral
            r'Ph\.?\s?D\.?',
            r'PhD',
            r'Doctorate',
            # Other
            r'Diploma',
            r'Certificate',
        ]

        # Additional contextual patterns
        university_pattern = r'(?:University|Institute|College|School|Academy)[\w\s,]+'
        year_pattern = r'(?:19|20)\d{2}'

        combined_pattern = '|'.join(degree_patterns)
        education_entries = []
        lines = text.split("\n")

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if re.search(combined_pattern, line_stripped, re.IGNORECASE):
                education_entries.append(line_stripped)
            elif re.search(university_pattern, line_stripped, re.IGNORECASE):
                education_entries.append(line_stripped)

        # Deduplicate while preserving order
        seen = set()
        unique_entries = []
        for entry in education_entries:
            normalised = entry.lower()
            if normalised not in seen:
                seen.add(normalised)
                unique_entries.append(entry)

        return unique_entries if unique_entries else ["Not specified"]
    except Exception as e:
        print(f"Error extracting education: {e}")
        return ["Not specified"]


def extract_experience(text):
    """Extract professional experience duration from the resume.

    Searches for common patterns such as:

    * ``X years of experience``
    * ``X+ years``
    * ``X years experience``
    * ``experienced for X years``

    Also attempts to identify job titles and company names when an
    explicit duration is not found.

    Parameters
    ----------
    text : str
        Raw resume text.

    Returns
    -------
    str
        A string describing the experience, or ``'Not specified'``.
    """
    try:
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+of\s+experience',
            r'(\d+)\+?\s*years?\s+experience',
            r'(\d+)\+?\s*years?\s+of\s+(?:professional\s+)?work',
            r'experienced?\s+for\s+(\d+)\+?\s*years?',
            r'over\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*(?:yrs|years?)\s+(?:in|of)',
        ]

        text_lower = text.lower()

        for pattern in experience_patterns:
            match = re.search(pattern, text_lower)
            if match:
                years = match.group(1)
                return f"{years} years of experience"

        # Fallback: look for job-title / company patterns as evidence
        job_title_patterns = [
            r'(?:Senior|Junior|Lead|Principal|Staff)?\s*'
            r'(?:Software|Data|Machine Learning|ML|AI|Web|Full[\s-]?Stack|Front[\s-]?End|Back[\s-]?End|DevOps|Cloud|QA|Test|System|Network|Database|Security)?\s*'
            r'(?:Engineer|Developer|Analyst|Scientist|Architect|Manager|Consultant|Administrator|Designer|Specialist)',
            r'(?:Project|Product|Program|Engineering|Technical)\s+Manager',
            r'(?:CTO|CEO|CIO|VP|Director)\b',
        ]

        for pattern in job_title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"Experience found (job title detected: {match.group().strip()})"

        return "Not specified"
    except Exception as e:
        print(f"Error extracting experience: {e}")
        return "Not specified"


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def parse_resume(uploaded_file, skill_database):
    """Parse an uploaded resume and return structured data.

    This is the main entry point of the module.  It determines the file
    type, extracts text, and runs every extraction function to build a
    comprehensive profile dictionary.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        A Streamlit UploadedFile object (PDF or DOCX).
    skill_database : list[str]
        A list of known skill names used for skill matching.

    Returns
    -------
    dict
        A dictionary with the following keys:

        * ``filename`` – original file name
        * ``raw_text`` – full extracted text
        * ``name``     – candidate name
        * ``email``    – email address
        * ``phone``    – phone number
        * ``skills``   – matched skills (list)
        * ``education``– education entries (list)
        * ``experience``– experience summary (str)

        Returns a dict with empty/default values if the file type
        is unsupported or processing fails.
    """
    try:
        filename = uploaded_file.name
        file_extension = os.path.splitext(filename)[1].lower()

        # --- Extract raw text based on file type ---
        if file_extension == ".pdf":
            raw_text = extract_text_from_pdf(uploaded_file)
        elif file_extension == ".docx":
            raw_text = extract_text_from_docx(uploaded_file)
        else:
            print(f"Unsupported file type: {file_extension}")
            return {
                "filename": filename,
                "raw_text": "",
                "name": "Unknown Candidate",
                "email": "Not found",
                "phone": "Not found",
                "skills": [],
                "education": ["Not specified"],
                "experience": "Not specified",
            }

        # --- Run all extractors ---
        name = extract_name(raw_text)
        email = extract_email(raw_text)
        phone = extract_phone(raw_text)
        skills = extract_skills(raw_text, skill_database)
        education = extract_education(raw_text)
        experience = extract_experience(raw_text)

        return {
            "filename": filename,
            "raw_text": raw_text,
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "experience": experience,
        }
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {
            "filename": getattr(uploaded_file, "name", "unknown"),
            "raw_text": "",
            "name": "Unknown Candidate",
            "email": "Not found",
            "phone": "Not found",
            "skills": [],
            "education": ["Not specified"],
            "experience": "Not specified",
        }
