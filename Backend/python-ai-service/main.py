"""
Resume Enhancement — Python AI Microservice
FastAPI app exposing AI-powered resume analysis, ATS scoring,
and resume parsing endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
import json

from resume_analyzer import ResumeAnalyzer
from ats_scorer import ATSScorer
from resume_parser import ResumeParser
from resume_enhancer import ResumeEnhancer

app = FastAPI(
    title="Resume Enhancement AI Service",
    version="0.1.0",
)

# Allow the Express backend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = ResumeAnalyzer()
scorer = ATSScorer()
parser = ResumeParser()
enhancer = ResumeEnhancer()

# Create output directory for PDFs
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "python-ai-service"}


@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse a resume PDF/DOCX and return structured data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_extensions = (".pdf", ".doc", ".docx")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    try:
        contents = await file.read()
        result = parser.parse(contents, file.filename)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """Analyze a resume and return improvement suggestions."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()
    result = analyzer.analyze(contents, file.filename)
    return {"success": True, "data": result}


@app.post("/ats-score")
async def ats_score(file: UploadFile = File(...), job_description: str = Form("")):
    """Score a resume file against a job description."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        contents = await file.read()
        # 1. Parse the resume to get structured JSON
        parsed_data = parser.parse(contents, file.filename)
        # 2. Score the parsed JSON against the JD
        result = scorer.score(parsed_data, job_description)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to score resume: {str(e)}")


@app.post("/score-from-json")
async def score_from_json(request: dict):
    """
    Score a direct resume JSON against a job description.
    Expects: {"resume_json": {...}, "job_description": "..."}
    """
    resume_json = request.get("resume_json")
    job_description = request.get("job_description", "")
    
    if not resume_json:
        raise HTTPException(status_code=400, detail="Missing resume_json")
    
    # Auto-unwrap 'data' envelope if it exists (common if user passes parser output directly)
    if isinstance(resume_json, dict) and "data" in resume_json and "success" in resume_json:
        resume_json = resume_json["data"]
        
    try:
        result = scorer.score(resume_json, job_description)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to score JSON: {str(e)}")
@app.post("/analyze-from-json")
async def analyze_from_json(request: dict):
    """
    Analyze a direct resume JSON with high-fidelity feedback.
    Expects: {"resume_json": {...}, "job_description": "..."}
    """
    resume_json = request.get("resume_json")
    job_description = request.get("job_description", "")
    
    if not resume_json:
        raise HTTPException(status_code=400, detail="Missing resume_json")
    
    # Auto-unwrap 'data' envelope
    if isinstance(resume_json, dict) and "data" in resume_json and "success" in resume_json:
        resume_json = resume_json["data"]
        
    try:
        result = analyzer.analyze_json(resume_json, job_description)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze JSON: {str(e)}")

@app.post("/enhance-resume")
async def enhance_resume(request: dict):
    """
    Enhanced multi-stage pipeline: Baseline -> Research -> AI Upgrade -> Re-score -> PDF.
    Expects: {"resume_json": {...}, "job_description": "...", "github_username": "...", "linkedin_text": "..."}
    """
    resume_json = request.get("resume_json")
    job_description = request.get("job_description", "")
    github_username = request.get("github_username", "")
    linkedin_text = request.get("linkedin_text", "")
    
    if not resume_json:
        raise HTTPException(status_code=400, detail="Missing resume_json")
    
    # Auto-unwrap 'data' envelope
    if isinstance(resume_json, dict) and "data" in resume_json and "success" in resume_json:
        resume_json = resume_json["data"]
        
    try:
        # 1. Execute Full Enhancement Flow
        result = enhancer.enhance_full_flow(
            resume_json, 
            job_description, 
            github_username, 
            linkedin_text
        )
        
        if "error" in result:
            return {"success": False, "error": result["error"]}

        # 2. Generate PDF from enhanced data
        enhanced_data = result["enhanced_resume"]
        pdf_filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
        enhancer.generate_pdf(enhanced_data, pdf_path)
        
        return {
            "success": True, 
            "data": {
                "original_score": result["original_score"],
                "enhanced_score": result["enhanced_score"],
                "score_improvement": result["enhanced_score"] - result["original_score"],
                "enhanced_resume": enhanced_data,
                "pdf_url": f"/get-resume-pdf/{pdf_filename}",
                "research_findings": result["research_summary"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

@app.post("/parse-linkedin")
async def parse_linkedin_text(request: dict):
    """Compliant parsing of user-pasted LinkedIn profile text."""
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
    
    # In a real system, this would use an LLM to structure the pasted text
    # For now, we return it as a structured-ready object
    return {"success": True, "data": {"raw_pasted_data": text[:5000]}}

@app.get("/get-resume-pdf/{filename}")
async def get_resume_pdf(filename: str):
    """Serve the generated resume PDF."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/pdf', filename="Enhanced_Resume.pdf")


import re as _re

# Section heading patterns used to split raw JD text
_JD_SECTIONS = [
    (r"(?:position|job\s*title|role)\s*[:.]?\s*", "position"),
    (r"(?:department|team)\s*[:.]?\s*", "department"),
    (r"(?:key\s*)?responsibilities|what\s+you\s*ll\s*do|what\s+you\s+will\s+do|tasks|duties\s*[:.]?\s*", "responsibilities"),
    (r"(?:required\s*)?(?:skills|qualifications)(?:\s*&\s*|\s*and\s*|\s+)?(?:qualifications?)?|what\s+you\s*have|what\s+you\s+bring|key\s+skills\s*[:.]?\s*", "required_skills"),
    (r"(?:preferred|nice\s*to\s*have|bonus)\s*(?:skills|qualifications)?(?:\s*\(optional\))?\s*[:.]?\s*", "preferred_skills"),
    (r"(?:about\s*(?:the\s*)?(?:role|company|us)|overview|description)\s*[:.]?\s*", "about"),
    (r"(?:location|work\s*mode)\s*[:.]?\s*", "location"),
    (r"(?:experience|years)\s*[:.]?\s*", "experience"),
    # Noise/Footer sections
    (r"(?:industry|employment|education|ug:|pg:)\s*[:.]?\s*", "ignore"),
]

def _split_into_bullets(text: str) -> list[str]:
    """Split a block of text into individual bullet points."""
    # Split by newlines or dots
    lines = _re.split(r"[\n\r]|(?:\.\s+(?=[A-Z]))", text.strip())
    cleaned = []
    for line in lines:
        line = line.strip().rstrip(".").lstrip("-").lstrip("*").lstrip("•").strip()
        if len(line) > 5:
            cleaned.append(line)
    return cleaned


from fastapi import Request

@app.post("/parse-jd")
async def parse_job_description(request: Request):
    """
    High-quality JD parsing using Groq LLM.
    Converts messy pasted text into structured and canonical string format.
    """
    body_bytes = await request.body()
    raw = body_bytes.decode("utf-8")
    
    if not raw or len(raw.strip()) < 10:
        raise HTTPException(status_code=400, detail="Request body is empty or too short")

    if not enhancer.client:
        raise HTTPException(status_code=500, detail="AI Service not configured (Missing GROQ_API_KEY)")

    prompt = f"""
    TASK: Extract job details from this messy, unformatted job description text.
    
    INPUT TEXT:
    {raw[:8000]}
    
    INSTRUCTIONS:
    1. Identify the Position/Title.
    2. Identify the Department/Team.
    3. Extract Key Responsibilities as a list of bullet points.
    4. Extract Required Skills/Qualifications.
    5. Extract Preferred/Optional Skills.
    
    OUTPUT RULES:
    - IGNORE footer noise like "Industry Type", "Employment Type", "Role Category", "Education", "UG/PG".
    - CLEAN UP compressed strings (e.g., "application supportgithubGIT" -> "Application Support, GitHub, Git").
    - FORMAT: Return a JSON object with two keys:
        - "job_description": A single, high-quality concatenated string in this EXACT format:
          "Position: [Title]. Department: [Dept]. Key Responsibilities: [Bullet 1]. [Bullet 2]... Required Skills and Qualifications: [Skill 1]. [Skill 2]... Preferred Skills: [Skill 1]. [Skill 2]..."
        - "structured_data": A JSON object containing the fields: position, department, responsibilities (list), required_skills (list), preferred_skills (list).

    RETURN ONLY THE JSON OBJECT.
    """

    try:
        resp = enhancer.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional recruiting assistant. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        parse_result = json.loads(resp.choices[0].message.content)
        return {"success": True, "data": parse_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Parsing failed: {str(e)}")
