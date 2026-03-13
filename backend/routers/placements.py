from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models
from pydantic import BaseModel

router = APIRouter(prefix="/placements", tags=["placements"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas for Validation
class JobCreate(BaseModel):
    company_name: str
    job_role: str
    description: str
    tech_skills: List[str]
    location: str
    min_cgpa: float

@router.post("/jobs")
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    # 1. Save job to database
    # Note: Ensure you add a 'Job' model to your models.py
    new_job = models.Job(
        company_name=job.company_name,
        job_role=job.job_role,
        description=job.description,
        tech_skills=",".join(job.tech_skills), # Storing as comma-separated string
        location=job.location,
        min_cgpa=job.min_cgpa
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 2. Identify eligible students for notification
    eligible_count = db.query(models.DummyStudentRecord).filter(
        
        models.DummyStudentRecord.cgpa >= job.min_cgpa
    ).count()

    return {
        "message": "Job posted successfully",
        "job_id": new_job.id,
        "notified_count": eligible_count
    }

@router.get("/calendar-events")
async def get_calendar_events(db: Session = Depends(get_db)):
    # Fetch all interview rounds for the calendar
    events = db.query(models.InterviewRound).all()
    return events
@router.get("/jobs", response_model=List[JobCreate])
async def get_all_jobs(db: Session = Depends(get_db)):
    # Fetch all jobs from the database
    jobs = db.query(models.Job).all()
    return jobs
    