import os
import json
from groq import Groq
from dotenv import load_dotenv
from resume_parser import ResumeParser

# Load environment variables (expect GROQ_API_KEY)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class ResumeAnalyzer:
    """Analyzes a resume using Groq AI for professional feedback."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.parser = ResumeParser()

    def analyze(self, file_bytes: bytes, filename: str) -> dict:
        """
        Analyze resume file using Groq LLM.
        """
        # 1. Parse the resume to get structured JSON
        parsed_data = self.parser.parse(file_bytes, filename)
        return self.analyze_json(parsed_data, filename=filename)

    def analyze_json(self, resume_json: dict, job_description: str = "", filename: str = "JSON_Input") -> dict:
        """
        Perform high-fidelity analysis on pre-parsed resume JSON.
        """
        if not self.api_key:
            return {
                "filename": filename,
                "suggestions": ["GROQ_API_KEY missing. Cannot perform AI analysis."],
                "overall_quality": "N/A",
                "error": "Missing GROQ_API_KEY"
            }

        # Refined, high-impact prompt
        context_str = f"\nTarget Job Description:\n{job_description}" if job_description else "\nContext: General high-end career coaching."
        
        prompt = f"""
        You are an Elite Executive Recruiter and "Career Plastic Surgeon." 
        Analyze the following resume JSON and provide a surgical, evidence-based critique.
        {context_str}

        Resume Data:
        {json.dumps(resume_json, indent=2)}

        CRITIQUE PROTOCOLS:
        1. NO FLUFF: Every suggestion must be actionable. Replace "use stronger verbs" with specific 3-word replacements for identified lines.
        2. QUANTUM METRICS: Identify exact bullet points that lack numbers/metrics. Explain the "Risk of Ignorance"—why a recruiter would skip this role due to lack of proof.
        3. TECH STACK DENSITY: Audit the skills. If a skill is listed but not backed by a project or experience entry, mark it as "Unverified Intent."
        4. "COMPETITIVE EDGE": Identify 2-3 specific "spikes" in this profile that make the candidate win against 1000 others.
        5. "ACTION-RESULT" RECONSTRUCTION: Provide 3-5 "Before & After" rewrites of existing bullet points using the [Action] + [Context] + [Quantified Result] framework.

        Response Format (Strict JSON):
        - "suggestions": List of 7-10 hyper-specific, critical improvements.
        - "overall_quality": One of: "Needs Total Overhaul", "Technically Competent", "Impact Weak", "Market Leader", "Executive Grade".
        - "score": Numeric quality score (1.0 to 10.0).
        - "highlights": 3 specific high-value competitive advantages.
        - "action_result_rewrites": List of objects with "original" and "improved" keys.
        - "top_3_missing_skills": (Only if JD provided) The 3 most critical gaps found.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a specialized career consultant that outputs JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", # Using the supported successor model for high-quality feedback
                response_format={"type": "json_object"}
            )
            
            ai_response = json.loads(chat_completion.choices[0].message.content)
            
            return {
                "filename": filename,
                "suggestions": ai_response.get("suggestions", []),
                "overall_quality": ai_response.get("overall_quality", "N/A"),
                "quality_score": ai_response.get("score", 0),
                "highlights": ai_response.get("highlights", []),
                "action_result_rewrites": ai_response.get("action_result_rewrites", []),
                "top_gaps": ai_response.get("top_3_missing_skills", []),
                "meta": {"model": "llama-3.1-70b", "mode": "executive_recruiter"}
            }
        except Exception as e:
            return {"error": f"AI Analysis Error: {str(e)}", "overall_quality": "Error"}
