"""
resume_parser.py — Robust resume PDF/DOCX parser.

Extracts structured data from uploaded resume files:
  name, email, phone, education, skills, projects,
  experience, certifications, achievements.
"""

import io
import re
from typing import Any

import pdfplumber
import spacy
from docx import Document as DocxDocument

# ────────────────────────────────────────────────────────
# Load spaCy model once at module level
# ────────────────────────────────────────────────────────
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback: download on first use
    from spacy.cli import download

    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# ────────────────────────────────────────────────────────
# Section heading keywords (lowercased for matching)
# ────────────────────────────────────────────────────────
SECTION_HEADINGS: dict[str, list[str]] = {
    "summary": ["summary", "objective", "about me", "profile", "professional summary", "career objective", "about"],
    "education": ["education", "academic background", "qualifications", "academic details", "academics"],
    "skills": ["skills", "technical skills", "key skills", "core competencies", "technologies", "tools", "tech stack", "competencies", "programming languages", "skills & tools"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "work history", "internship", "internships"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "notable projects"],
    "certifications": ["certifications", "certificates", "licenses", "certification", "courses", "training"],
    "achievements": ["achievements", "accomplishments", "awards", "honors", "honours", "recognition"],
    "responsibilities": ["responsibilities", "duties", "key responsibilities"],
    "extracurricular": ["extracurricular", "extracurricular activities", "activities", "volunteer", "volunteering", "leadership"],
    "publications": ["publications", "papers", "research"],
    "languages": ["languages", "language proficiency"],
    "interests": ["interests", "hobbies"],
}


# ────────────────────────────────────────────────────────
# Regex patterns
# ────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?"         # optional country code
    r"(?:\(?\d{2,4}\)?[\s\-]?)?"       # optional area code
    r"\d{3,5}[\s\-]?\d{3,5}"          # main number
)
URL_RE = re.compile(r"https?://[^\s,]+|www\.[^\s,]+")
LINKEDIN_RE = re.compile(r"(?:linkedin\.com/in/|linkedin:\s*)([^\s,]+)", re.I)
GITHUB_RE = re.compile(r"(?:github\.com/|github:\s*)([^\s,]+)", re.I)

MONTHS_PAT = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)"
DATE_RE = re.compile(
    r"(?:" + MONTHS_PAT + r"[\s,]*\d{2,4}|\d{1,2}/\d{2,4}|\d{4})"
    r"\s*[-\u2013\u2014–to]+\s*"
    r"(?:" + MONTHS_PAT + r"[\s,]*\d{2,4}|\d{1,2}/\d{2,4}|\d{4}|Present|Current|Ongoing|Till Date)",
    re.IGNORECASE
)

# Added \u00f2 (ò) which appears in some PDF extractions
BULLET_RE = re.compile(r"^[\s]*[•●○◦▪▸\-\*\u2022\u2023\u25E6\u2043\u2219\u00f2]\s*")
GPA_RE = re.compile(r"(?:CGPA|GPA).{0,5}?([\d\.]+)(?:\/\d+)?", re.IGNORECASE)


class ResumeParser:
    """Parses a resume file (PDF / DOCX) into structured JSON."""

    # ── Public API ───────────────────────────────────────

    def parse(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        """
        Entry point. Accepts raw bytes + filename.
        Returns the full structured dict.
        """
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext == "pdf":
            raw_text = self._extract_pdf(file_bytes)
        elif ext in ("docx", "doc"):
            raw_text = self._extract_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: .{ext}")

        return self._parse_text(raw_text)

    # ── Text extraction ──────────────────────────────────

    @staticmethod
    def _extract_pdf(data: bytes) -> str:
        """Extract text from PDF using pdfplumber."""
        text_parts: list[str] = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    @staticmethod
    def _extract_docx(data: bytes) -> str:
        """Extract text from DOCX using python-docx."""
        doc = DocxDocument(io.BytesIO(data))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    # ── Main parser ──────────────────────────────────────

    def _parse_text(self, text: str) -> dict[str, Any]:
        lines = text.split("\n")

        # 1) Contact info (usually in the first ~8 lines)
        header_block = "\n".join(lines[:10])
        contact = self._extract_contact(header_block, text)

        # 2) Detect section boundaries
        sections = self._detect_sections(lines)

        # 3) Parse each section
        result: dict[str, Any] = {
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "linkedin": contact.get("linkedin", ""),
            "github": contact.get("github", ""),
            "location": contact.get("location", ""),
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {
                "languages": [],
                "frontend": [],
                "backend": [],
                "databases": [],
                "ai_ml": [],
                "tools": [],
            },
            "achievements": [],
            "certifications": [],
        }

        for section_key, section_lines in sections.items():
            raw = "\n".join(section_lines).strip()
            if not raw:
                continue

            if section_key == "education":
                result["education"] = self._parse_education(section_lines)

            elif section_key == "skills":
                result["skills"] = self._parse_skills(section_lines)

            elif section_key == "projects":
                result["projects"] = self._parse_projects(section_lines)

            elif section_key in ("experience",):
                result["experience"] = self._parse_experience(section_lines)

            elif section_key == "certifications":
                result["certifications"] = self._parse_bullet_list(section_lines)

            elif section_key == "achievements":
                result["achievements"] = self._parse_bullet_list(section_lines)

        # Basic final cleanup: remove empty project/experience stubs
        result["projects"] = [p for p in result["projects"] if p.get("title")]
        result["experience"] = [e for e in result["experience"] if e.get("role") and e.get("company")]

        return result

    # ── Contact extraction ───────────────────────────────

    def _extract_contact(self, header: str, full_text: str) -> dict[str, str]:
        contact: dict[str, str] = {}

        # Email
        email_match = EMAIL_RE.search(full_text)
        if email_match:
            contact["email"] = email_match.group()

        # Phone
        phone_match = PHONE_RE.search(header)
        if phone_match:
            contact["phone"] = phone_match.group().strip()

        # LinkedIn
        li_match = LINKEDIN_RE.search(full_text)
        if li_match:
            contact["linkedin"] = f"linkedin.com/in/{li_match.group(1)}"

        # GitHub
        gh_match = GITHUB_RE.search(full_text)
        if gh_match:
            contact["github"] = f"github.com/{gh_match.group(1)}"

        # Name — use spaCy NER on the first few lines
        contact["name"] = self._extract_name(header)

        return contact

    @staticmethod
    def _extract_name(header: str) -> str:
        """Extract the name, usually the very first prominent line."""
        lines = [line.strip() for line in header.split("\n") if line.strip()]
        
        # Heuristic: The first line is almost always the name if it doesn't contain contact info
        if lines:
            first_line = lines[0]
            if not (EMAIL_RE.search(first_line) or PHONE_RE.search(first_line) or URL_RE.search(first_line)):
                # If it's a reasonably short string of words, consider it the name
                words = first_line.split()
                if 1 <= len(words) <= 5 and all(w.isalpha() or w == "." for w in words):
                    return first_line

        # Fallback to spaCy NER
        doc = nlp(header)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

        # Final fallback: the first non-empty line that looks like a name, skipping contacts
        for line in lines:
            if EMAIL_RE.search(line) or PHONE_RE.search(line) or URL_RE.search(line) or "github" in line.lower() or "linkedin" in line.lower():
                continue
            words = line.split()
            if 1 <= len(words) <= 5 and all(w.isalpha() or w == "." for w in words):
                return line
                
        return ""

    # ── Section detection ────────────────────────────────

    @staticmethod
    def _detect_sections(lines: list[str]) -> dict[str, list[str]]:
        """
        Walk through lines, detect heading boundaries,
        assign subsequent lines to that section until the next heading.
        """
        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        for line in lines:
            stripped = line.strip()
            detected = _match_heading(stripped)

            if detected:
                current_section = detected
                if current_section not in sections:
                    sections[current_section] = []
                continue

            if current_section and stripped:
                sections[current_section].append(stripped)

        return sections

    # ── Section parsers ──────────────────────────────────

    @staticmethod
    def _parse_education(lines: list[str]) -> list[dict[str, Any]]:
        """
        Parse education entries.
        """
        entries: list[dict[str, Any]] = []
        current: dict[str, Any] = {}

        for line in lines:
            line_clean = BULLET_RE.sub("", line).strip()
            if not line_clean:
                continue

            date_match = DATE_RE.search(line_clean)
            gpa_match = GPA_RE.search(line_clean)

            if gpa_match:
                current["cgpa"] = gpa_match.group(1).strip()
                line_clean = GPA_RE.sub("", line_clean).strip().strip(",").strip()
                
            if date_match:
                current["dates"] = date_match.group().strip()
                line_clean = DATE_RE.sub("", line_clean).strip().strip(",").strip("|").strip("-–—").strip()

            if not line_clean:
                continue

            if not current.get("institution"):
                if "," in line_clean:
                    parts = line_clean.split(",", 1)
                    current["institution"] = parts[0].strip()
                    current["location"] = parts[1].strip()
                else:
                    current["institution"] = line_clean
            elif not current.get("degree"):
                current["degree"] = line_clean
            elif not current.get("location"):
                current["location"] = line_clean
            else:
                current["degree"] = f'{current["degree"]} {line_clean}'.strip()

            if current.get("dates") and (current.get("degree") or current.get("institution")):
                # In education, we usually have one entry per date block
                pass

        if current.get("degree") or current.get("institution"):
            entries.append(current)

        return entries

    @staticmethod
    def _parse_skills(lines: list[str]) -> dict[str, list[str]]:
        """
        Categorize skills.
        """
        skills_dict: dict[str, list[str]] = {
            "languages": [], "frontend": [], "backend": [], "databases": [], "ai_ml": [], "tools": []
        }
        
        for line in lines:
            line_clean = BULLET_RE.sub("", line).strip()
            if not line_clean:
                continue

            category = "tools"
            lower_line = line_clean.lower()
            if "language" in lower_line: category = "languages"
            elif any(x in lower_line for x in ["frontend", "front end", "front-end"]): category = "frontend"
            elif any(x in lower_line for x in ["backend", "back end", "back-end"]): category = "backend"
            elif "database" in lower_line: category = "databases"
            elif any(x in lower_line for x in ["ai", "ml", "machine learning"]): category = "ai_ml"

            if ":" in line_clean:
                _, _, line_clean = line_clean.partition(":")
                line_clean = line_clean.strip()

            tokens = re.split(r",", line_clean)
            for t in tokens:
                t = t.strip().strip("-–—").strip()
                if t and len(t) < 80:
                    skills_dict[category].append(t)
                    
        return skills_dict

    @staticmethod
    def _parse_projects(lines: list[str]) -> list[dict[str, Any]]:
        """
        Parse project entries.
        """
        projects: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None

        for line in lines:
            line_clean = line.strip()
            is_bullet = bool(BULLET_RE.match(line_clean))
            if is_bullet:
                line_clean = BULLET_RE.sub("", line_clean).strip()

            if not line_clean: continue
            if DATE_RE.fullmatch(line_clean.strip("–-— ")): continue

            # Project Title Detection
            if not is_bullet and ("|" in line_clean or "–" in line_clean or "—" in line_clean) and "github" not in line_clean.lower():
                if len(line_clean.split()) > 2 and not DATE_RE.search(line_clean):
                    if current and current.get("title"):
                        projects.append(current)
                        
                    title = line_clean
                    tech_str = ""
                    organization = ""
                    
                    org_match = re.search(r"\(([^)]+)\)", title)
                    if org_match:
                        organization = org_match.group(1).strip()
                        title = title.replace(org_match.group(0), "").strip()

                    for sep in ["|", "–", "—"]:
                        if sep in title:
                            parts = title.split(sep, 1)
                            if len(parts[1].split(",")) > 1 or len(parts[1].strip()) < 50:
                                title = parts[0].strip()
                                tech_str = parts[1].strip()
                                break
                        
                    tech_list = [t.strip().strip(",") for t in re.split(r"[,|]", tech_str) if t.strip()]
                    current = {
                        "title": title.strip("-–— |"),
                        "organization": organization,
                        "technologies": tech_list,
                        "description": [],
                    }
                    continue
                    
            if current is None:
                current = {"title": line_clean, "organization": "", "technologies": [], "description": []}
            elif is_bullet:
                current["description"].append(line_clean)
            else:
                # Tech stack overflow or multi-line title?
                if not current["description"] and len(line_clean) < 40:
                    extra_techs = [t.strip().strip(",") for t in re.split(r"[,|]", line_clean) if t.strip()]
                    current["technologies"].extend(extra_techs)
                else:
                    if current["description"] and not is_bullet:
                        prev = current["description"][-1]
                        sep = " " if not prev.endswith(" ") and not line_clean.startswith(" ") else ""
                        current["description"][-1] += f"{sep}{line_clean}"
                    else:
                        current["description"].append(line_clean)

        if current and current.get("title"):
            projects.append(current)
        return projects

    @staticmethod
    def _split_dates(date_str: str) -> tuple[str, str]:
        """Split a date range string into start and end dates."""
        if not date_str: return "", ""
        parts = re.split(r"[-\u2013\u2014–to]+", date_str.lower(), flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2: return parts[0].title(), parts[1].title()
        return date_str.title(), ""

    @staticmethod
    def _parse_experience(lines: list[str]) -> list[dict[str, Any]]:
        """
        Parse experience entries. Handles un-bulleted headers.
        """
        entries: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        header_buffer = []
        date_buffer = []

        for line in lines:
            line_clean = line.strip()
            is_bullet = bool(BULLET_RE.match(line_clean))
            if is_bullet:
                line_clean = BULLET_RE.sub("", line_clean).strip()

            if not line_clean: continue

            date_match = DATE_RE.search(line_clean)
            if date_match and not is_bullet:
                # If we see a new date, and we already have some header info, 
                # it might be the start of a NEW entry if the buffer is full.
                if len(header_buffer) >= 2:
                    # Flush previous
                    role = header_buffer[0]
                    company = header_buffer[1]
                    location = header_buffer[2] if len(header_buffer) > 2 else ""
                    raw_dates = date_buffer.pop(0) if date_buffer else ""
                    start_date, end_date = ResumeParser._split_dates(raw_dates)
                    entries.append({"role": role, "company": company, "location": location, "start_date": start_date, "end_date": end_date, "responsibilities": []})
                    header_buffer = []

                date_str = date_match.group()
                date_buffer.append(date_str)
                line_clean = line_clean.replace(date_str, "").strip(" -–—|,")

            if not is_bullet:
                if current:
                    entries.append(current)
                    current = None
                    header_buffer = []
                if line_clean:
                    header_buffer.append(line_clean)
            else:
                if current is None:
                    # Flush header_buffer into a new entry
                    role = ""
                    company = ""
                    location = ""
                    # Role is usually the one with "Developer", "Intern", etc., or the first line
                    if header_buffer:
                        # Try to find role in buffer
                        role_idx = 0
                        for i, h in enumerate(header_buffer):
                            if any(x in h.lower() for x in ["developer", "intern", "engineer", "lead", "manager"]):
                                role_idx = i
                                break
                        role = header_buffer.pop(role_idx)
                        if header_buffer:
                            company = header_buffer.pop(0)
                        if header_buffer:
                            location = header_buffer.pop(0)
                            
                    raw_dates = date_buffer.pop(0) if date_buffer else ""
                    start_date, end_date = ResumeParser._split_dates(raw_dates)
                    current = {"role": role, "company": company, "location": location, "start_date": start_date, "end_date": end_date, "responsibilities": []}
                    header_buffer = []
                current["responsibilities"].append(line_clean)

        if current:
            entries.append(current)
        elif header_buffer:
            # Handle remaining un-bulleted blocks (like in the user's PDF)
            while header_buffer:
                role = header_buffer.pop(0)
                company = header_buffer.pop(0) if header_buffer else ""
                if "," in company:
                    parts = company.split(",", 1)
                    company = parts[0].strip()
                    location = parts[1].strip()
                else:
                    location = ""
                raw_dates = date_buffer.pop(0) if date_buffer else ""
                start_date, end_date = ResumeParser._split_dates(raw_dates)
                entries.append({"role": role, "company": company, "location": location, "start_date": start_date, "end_date": end_date, "responsibilities": []})

        return entries

    @staticmethod
    def _parse_bullet_list(lines: list[str]) -> list[str]:
        """Generic bullet-point list parser."""
        items: list[str] = []
        for line in lines:
            line_clean = BULLET_RE.sub("", line).strip()
            if line_clean and len(line_clean) > 1: items.append(line_clean)
        return items


def _match_heading(line: str) -> str | None:
    """Detect section heading."""
    cleaned = line.strip().strip(":").strip("-–—=").strip("_").strip("*").strip("#").strip()
    lower = cleaned.lower()
    if len(cleaned) > 60: return None
    for section_key, keywords in SECTION_HEADINGS.items():
        for kw in keywords:
            if lower == kw or lower.startswith(kw + ":") or lower.startswith(kw + " :"):
                return section_key
    return None


def _split_role_company(text: str) -> tuple[str, str]:
    """
    Try to split 'Role — Company' / 'Role | Company' / 'Role at Company'.
    Returns (role, company). If can't split, returns (text, '').
    """
    for sep in [" — ", " – ", " - ", " | ", " at "]:
        if sep in text:
            parts = text.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    # Try comma
    if ", " in text:
        parts = text.split(", ", 1)
        return parts[0].strip(), parts[1].strip()
    return text.strip(), ""
