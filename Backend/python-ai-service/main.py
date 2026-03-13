"""
Resume Enhancement — Python AI Microservice
FastAPI app exposing AI-powered resume analysis, ATS scoring,
and resume parsing endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

from resume_analyzer import ResumeAnalyzer
from ats_scorer import ATSScorer
from resume_parser import ResumeParser

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

analyzer = ResumeAnalyzer()
scorer = ATSScorer()
parser = ResumeParser()


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
