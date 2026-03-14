import os
import json
from jinja2 import Environment, FileSystemLoader
from groq import Groq
from researcher_service import ResearcherService
from xhtml2pdf import pisa
from ats_scorer import ATSScorer
from dotenv import load_dotenv

load_dotenv()


class ResumeEnhancer:
    """
    Multi-stage enhancement:
      1  Baseline ATS score
      2  Skill-gap detection
      3  Deep GitHub/LinkedIn research
      4  Evidence-gated AI rewrite (strict — no noise)
      5  Re-score + PDF
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.researcher = ResearcherService()
        self.scorer = ATSScorer()
        tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.tpl_dir = tpl_dir
        self.env = Environment(loader=FileSystemLoader(tpl_dir))

    # ─── orchestrator ─────────────────────────────────────────

    def enhance_full_flow(
        self,
        resume_json: dict,
        job_description: str = "",
        github_username: str = "",
        linkedin_text: str = "",
    ) -> dict:

        # 1  Baseline
        baseline = self.scorer.score(resume_json, job_description)
        baseline_score = baseline.get("ats_score", 0)
        missing = baseline.get("missing_skills", [])
        matched = baseline.get("matched_skills", [])

        # 2  Research
        research = self.researcher.get_user_research(github_username, linkedin_text)

        if not self.api_key:
            return {"error": "Missing GROQ_API_KEY", "original_score": baseline_score}

        # 3  Build a TIGHT prompt
        prompt = self._build_prompt(resume_json, job_description, missing, matched, research)

        try:
            resp = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            enhanced = json.loads(resp.choices[0].message.content)

            # 4  Re-score
            final = self.scorer.score(enhanced, job_description)

            return {
                "original_score": baseline_score,
                "enhanced_score": final.get("ats_score", 0),
                "enhanced_resume": enhanced,
                "skills_added": [s for s in final.get("matched_skills", []) if s not in matched],
                "research_summary": {
                    "github_projects_found": len(research.get("github", {}).get("projects", [])),
                    "github_top_skills": research.get("github", {}).get("top_skills", [])[:8],
                    "linkedin_parsed": bool(research.get("linkedin")),
                },
            }

        except Exception as e:
            return {"error": str(e), "original_score": baseline_score}

    # ─── prompt engineering ───────────────────────────────────

    @staticmethod
    def _build_prompt(resume, jd, missing, matched, research) -> str:
        """
        Hyper-constrained prompt that prevents noise injection but forces high-quality re-writing.
        """
        gh = research.get("github", {})
        gh_projects = gh.get("projects", [])
        gh_skills = gh.get("top_skills", [])
        li = research.get("linkedin", {})

        return f"""
TASK: YOU ARE A TOP-TIER TECHNICAL RESUME ARCHITECT.
ENHANCE the provided resume for maximum ATS compatibility and recruiter impact for the target Job Description.

===========================================
INPUT DATA:
ORIGINAL RESUME: {json.dumps(resume)}
JOB DESCRIPTION: {jd}
MATCHED SKILLS: {matched}
MISSING SKILLS: {missing}
GITHUB EVIDENCE: {json.dumps(gh_projects)}
LINKEDIN EVIDENCE: {json.dumps(li)}
===========================================

STRICT OUTPUT SCHEMA (MUST FOLLOW EXACTLY):
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "linkedin": "string",
  "github": "string",
  "summary": "2-3 sentences, high impact, tailored to JD",
  "education": [
    {{ "institution": "string", "degree": "string", "location": "string", "start_date": "string", "end_date": "string" }}
  ],
  "experience": [
    {{
      "role": "string",
      "company": "string",
      "location": "string",
      "start_date": "string",
      "end_date": "string",
      "responsibilities": ["4-5 high-impact bullets starting with action verbs, quantifying results"]
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "technologies": ["list", "of", "tech"],
      "description": "2-3 detailed sentences describing the technical challenge, solution, and impact. USE GITHUB EVIDENCE TO ADD DEPTH."
    }}
  ],
  "skills": {{
    "languages": ["list"],
    "frameworks": ["list"],
    "tools_and_databases": ["list"],
    "soft_skills": ["list"]
  }},
  "certifications": ["List of certification names only"],
  "achievements": ["List of notable awards or achievements"]
}}

EXECUTION PROTOCOLS:
1. PROJECT DESCRIPTIONS: DO NOT LEAVE THEM EMPTY. Even if the original is thin, use GitHub repository descriptions, topics, and README summaries to craft professional, technical descriptions.
2. ENHANCE bullet points: Use the STAR method. "Implemented [X] using [Y] which resulted in [Z]% improvement".
3. SKILLS CATEGORIZATION: Group skills into the specified keys (languages, frameworks, etc.).
4. CERTIFICATIONS: Ensure this is a simple LIST of strings.
5. NO FABRICATION: Only use technologies or roles found in the original resume or provided evidence.
6. ATS OPTIMIZATION: Seamlessly integrate MISSING skills from the list into the appropriate sections (skills, projects, or experience) ONLY IF supported by evidence.

RETURN ONLY THE COMPLETED JSON OBJECT.
"""

    # ─── PDF ──────────────────────────────────────────────────

    def generate_pdf(self, enhanced_json: dict, output_path: str) -> str | None:
        """Render enhanced JSON → professional single-column PDF."""
        template = self.env.get_template("resume.html")
        html_content = template.render(data=enhanced_json)

        css_path = os.path.join(self.tpl_dir, "resume_style.css")
        with open(css_path, "r") as f:
            css = f.read()

        full = f"<html><head><style>{css}</style></head><body>{html_content}</body></html>"

        with open(output_path, "wb") as out:
            status = pisa.CreatePDF(full, dest=out)

        return output_path if not status.err else None


# ─── system message (kept outside class for readability) ──────

SYSTEM_MSG = """You are a professional resume writer. You output JSON only.
You NEVER fabricate experience or projects.
You ONLY use evidence provided to you.
You follow the user's structural rules exactly."""
