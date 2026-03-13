"""
Resume Enhancement — Python AI Microservice
FastAPI app exposing AI-powered resume analysis, ATS scoring,
and resume parsing endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
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
async def ats_score(file: UploadFile = File(...), job_description: str = ""):
    """Score a resume against a job description for ATS compatibility."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()
    result = scorer.score(contents, file.filename, job_description)
    return {"success": True, "data": result}
