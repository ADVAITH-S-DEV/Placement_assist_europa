"""
Resume Enhancement — Python AI Microservice
FastAPI app exposing AI-powered resume analysis and ATS scoring endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from resume_analyzer import ResumeAnalyzer
from ats_scorer import ATSScorer

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


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "python-ai-service"}


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
