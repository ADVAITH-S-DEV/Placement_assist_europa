from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    # Fetch interview rounds, join with student + job so the calendar can show who + what
    rows = (
        db.query(models.InterviewRound, models.DummyStudentRecord, models.Job)
        .join(models.DummyStudentRecord, models.InterviewRound.student_id == models.DummyStudentRecord.id)
        .join(models.Job, models.InterviewRound.job_id == models.Job.id)
        .all()
    )

    events = []
    for r, student, job in rows:
        # DummyStudentRecord does not have a 'name' field; use reg_number to identify the student.
        title = f"{student.reg_number} - {job.job_role} at {job.company_name}"
        events.append(
            {
                "id": r.id,
                "title": title,
                "start": r.start_time.isoformat() if r.start_time else None,
                "end": r.end_time.isoformat() if r.end_time else None,
                "completed": bool(r.end_time and r.end_time < datetime.utcnow()),
            }
        )
    return events
@router.get("/jobs", response_model=List[JobCreate])
async def get_all_jobs(db: Session = Depends(get_db)):
    # Fetch all jobs from the database
    jobs = db.query(models.Job).all()
    return jobs
from datetime import datetime

@router.get("/eligible-applicants")
async def get_eligible_applicants(db: Session = Depends(get_db)):
    """
    Return eligible applicants with interview status:
    - is_scheduled: there is at least one interview_round for this student+job
    - is_completed: that interview's end_time is in the past
    """
    result = db.execute(
       # In backend/routers/placements.py

query = text("""
    SELECT 
        s.id AS id, 
        s.name AS name, 
        s.reg_number AS reg_number, 
        s.branch AS branch,
        j.job_role AS job_role, 
        j.company_name AS company_name,
        j.id AS job_id,
        ir.start_time AS interview_start,
        ir.end_time AS interview_end,
        CASE WHEN ir.id IS NOT NULL THEN 1 ELSE 0 END AS is_scheduled
    FROM dummy_student_records s
    JOIN applications a ON s.id = a.student_id
    JOIN jobs j ON a.job_id = j.id
    LEFT JOIN interview_rounds ir 
        ON ir.student_id = s.id AND ir.job_id = j.id
    WHERE CAST(s.cgpa AS DECIMAL) >= j.min_cgpa
""")
    )
    return [dict(row._mapping) for row in result]


@router.get("/applicants")
async def get_all_applicants(db: Session = Depends(get_db)):
    """
    Return all applicants (dummy student records) with academic details
    and placed status.
    """
    result = db.execute(
        text(
            """
            SELECT
                s.id AS id,
                s.reg_number AS reg_number,
                s.name AS name,
                s.branch AS branch,
                s.graduation_year AS graduation_year,
                s.placed AS placed
            FROM dummy_student_records s
            """
        )
    )
    return [dict(row._mapping) for row in result]

class InterviewSchedule(BaseModel):
    student_id: int
    job_id: int
    start: datetime
    end: datetime


@router.post("/schedule-interview")
async def schedule_interview(payload: InterviewSchedule, db: Session = Depends(get_db)):
    # Extra safety: verify student is still eligible for this job by CGPA
    student = db.query(models.DummyStudentRecord).filter(models.DummyStudentRecord.id == payload.student_id).first()
    job = db.query(models.Job).filter(models.Job.id == payload.job_id).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or job not found")

    if student.cgpa < job.min_cgpa:
        raise HTTPException(status_code=400, detail="Student not eligible for this job based on CGPA")

    # Conflict Check: Is there any interview overlapping this time?
    conflict = db.query(models.InterviewRound).filter(
        models.InterviewRound.start_time < payload.end,
        models.InterviewRound.end_time > payload.start
    ).first()

    if conflict:
        raise HTTPException(status_code=400, detail="Time slot conflict detected.")

    new_round = models.InterviewRound(
        student_id=payload.student_id,
        job_id=payload.job_id,
        start_time=payload.start,
        end_time=payload.end,
        round_name="Technical Interview",
    )
    db.add(new_round)
    db.commit()
    return {"message": "Scheduled successfully"}


@router.delete("/interviews/{interview_id}")
async def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    """Cancel/remove a scheduled interview round."""
    interview = db.query(models.InterviewRound).filter(models.InterviewRound.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    db.delete(interview)
    db.commit()
    return {"message": "Interview deleted"}