from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
import models
from pydantic import BaseModel
import base64
import io

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

class JobResponse(JobCreate):
    id: int

class ApplicationCreate(BaseModel):
    student_id: int
    job_id: int
    resume_data: Optional[str] = None  # Base64 encoded file
    resume_filename: Optional[str] = None
    cover_letter: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    student_id: int
    job_id: int
    applied_at: datetime
    status: str
    resume_filename: Optional[str] = None
    cover_letter: Optional[str] = None

class ApplicationStatusUpdate(BaseModel):
    status: str

class InterviewSchedule(BaseModel):
    student_id: int
    job_id: int
    start: datetime
    end: datetime


@router.post("/jobs")
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = models.Job(
        company_name=job.company_name,
        job_role=job.job_role,
        description=job.description,
        tech_skills=",".join(job.tech_skills),
        location=job.location,
        min_cgpa=job.min_cgpa
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    eligible_count = db.query(models.DummyStudentRecord).filter(
        models.DummyStudentRecord.cgpa >= job.min_cgpa
    ).count()

    return {
        "message": "Job posted successfully",
        "job_id": new_job.id,
        "notified_count": eligible_count
    }


@router.get("/jobs", response_model=List[JobResponse])
async def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return [
        {
            "id": job.id,
            "company_name": job.company_name,
            "job_role": job.job_role,
            "description": job.description,
            "tech_skills": job.tech_skills.split(",") if job.tech_skills else [],
            "location": job.location,
            "min_cgpa": job.min_cgpa,
        }
        for job in jobs
    ]


@router.get("/calendar-events")
async def get_calendar_events(db: Session = Depends(get_db)):
    rows = (
        db.query(models.InterviewRound, models.DummyStudentRecord, models.Job)
        .join(models.DummyStudentRecord, models.InterviewRound.student_id == models.DummyStudentRecord.id)
        .join(models.Job, models.InterviewRound.job_id == models.Job.id)
        .all()
    )

    events = []
    for r, student, job in rows:
        title = f"{student.name} - {job.job_role} at {job.company_name}"
        events.append({
            "id": r.id,
            "title": title,
            "start": r.start_time.isoformat() if r.start_time else None,
            "end": r.end_time.isoformat() if r.end_time else None,
            "completed": bool(r.end_time and r.end_time < datetime.utcnow()),
        })
    return events


@router.get("/eligible-applicants")
async def get_eligible_applicants(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
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
    current_utc = datetime.utcnow()
    applicants = []
    for row in result:
        row_dict = dict(row._mapping)
        # Determine is_completed: true if end_time exists and is passed
        is_completed = False
        if row_dict.get('interview_end'):
            if row_dict['interview_end'] < current_utc:
                is_completed = True
        
        row_dict['is_completed'] = is_completed
        applicants.append(row_dict)
        
    return applicants


@router.get("/applicants")
async def get_all_applicants(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
        SELECT
            s.id AS id,
            s.reg_number AS reg_number,
            s.name AS name,
            s.branch AS branch,
            s.graduation_year AS graduation_year,
            s.placed AS placed
        FROM dummy_student_records s
        """)
    )
    return [dict(row._mapping) for row in result]


@router.post("/schedule-interview")
async def schedule_interview(payload: InterviewSchedule, db: Session = Depends(get_db)):
    student = db.query(models.DummyStudentRecord).filter(models.DummyStudentRecord.id == payload.student_id).first()
    job = db.query(models.Job).filter(models.Job.id == payload.job_id).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or job not found")

    if student.cgpa < job.min_cgpa:
        raise HTTPException(status_code=400, detail="Student not eligible for this job based on CGPA")

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


@router.post("/apply")
async def apply_for_job(payload: ApplicationCreate, db: Session = Depends(get_db)):
    """Allow a student to apply for a job if they are eligible"""
    
    # Check if student exists
    student = db.query(models.DummyStudentRecord).filter(
        models.DummyStudentRecord.id == payload.student_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if job exists
    job = db.query(models.Job).filter(
        models.Job.id == payload.job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check eligibility: CGPA and Backlogs
    if student.cgpa < job.min_cgpa:
        raise HTTPException(
            status_code=400, 
            detail=f"You don't meet the minimum CGPA requirement. Required: {job.min_cgpa}, Your CGPA: {student.cgpa}"
        )
    
    if student.active_backlogs and not job.backlogs:
        raise HTTPException(
            status_code=400, 
            detail="You have active backlogs and are not eligible for this position"
        )
    
    # Check if already applied
    existing_application = db.query(models.Application).filter(
        models.Application.student_id == payload.student_id,
        models.Application.job_id == payload.job_id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=400, 
            detail="You have already applied for this job"
        )
    
    # Create the application
    new_application = models.Application(
        student_id=payload.student_id,
        job_id=payload.job_id,
        status="applied",
        resume_data=payload.resume_data,
        resume_filename=payload.resume_filename,
        cover_letter=payload.cover_letter
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    return {
        "id": new_application.id,
        "message": "Application submitted successfully",
        "application_id": new_application.id,
        "status": new_application.status,
        "applied_at": new_application.applied_at,
        "resume_filename": new_application.resume_filename
    }


@router.get("/student/{student_id}/applications")
async def get_student_applications(student_id: int, db: Session = Depends(get_db)):
    """Get all applications for a student"""
    try:
        applications = db.query(models.Application).filter(
            models.Application.student_id == student_id
        ).all()
        
        result = []
        for app in applications:
            job = db.query(models.Job).filter(models.Job.id == app.job_id).first()
            if job:
                # Safely get optional fields that might not exist in old schema
                resume_filename = None
                cover_letter = None
                try:
                    resume_filename = app.resume_filename if hasattr(app, 'resume_filename') else None
                    cover_letter = app.cover_letter if hasattr(app, 'cover_letter') else None
                except Exception:
                    pass
                
                result.append({
                    "id": app.id,
                    "job_id": app.job_id,
                    "company_name": job.company_name,
                    "job_role": job.job_role,
                    "status": app.status,
                    "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                    "resume_filename": resume_filename,
                    "cover_letter": cover_letter
                })
        
        return result
    except Exception as e:
        print(f"Error fetching applications: {e}")
        # Return empty list if table doesn't have expected columns
        # This can happen if the database schema wasn't updated
        return []


@router.get("/applications/all")
async def get_all_applications_admin(db: Session = Depends(get_db)):
    """Get all applications for admin review with full details"""
    try:
        applications = db.query(models.Application).all()
        
        result = []
        for app in applications:
            student = db.query(models.DummyStudentRecord).filter(
                models.DummyStudentRecord.id == app.student_id
            ).first()
            job = db.query(models.Job).filter(models.Job.id == app.job_id).first()
            
            if student and job:
                # Safely get optional fields
                resume_filename = None
                cover_letter = None
                has_resume = False
                try:
                    resume_filename = app.resume_filename if hasattr(app, 'resume_filename') else None
                    cover_letter = app.cover_letter if hasattr(app, 'cover_letter') else None
                    has_resume = bool(app.resume_data) if hasattr(app, 'resume_data') else False
                except Exception:
                    pass
                
                result.append({
                    "id": app.id,
                    "student_id": app.student_id,
                    "student_name": student.name,
                    "student_email": student.reg_number,
                    "student_cgpa": student.cgpa,
                    "student_branch": student.branch,
                    "job_id": app.job_id,
                    "job_role": job.job_role,
                    "company_name": job.company_name,
                    "status": app.status,
                    "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                    "resume_filename": resume_filename,
                    "has_resume": has_resume,
                    "cover_letter": cover_letter[:200] + "..." if cover_letter and len(cover_letter) > 200 else cover_letter
                })
        
        return result
    except Exception as e:
        print(f"Error fetching all applications: {e}")
        return []


@router.get("/applications/{application_id}/resume")
async def download_resume(application_id: int, db: Session = Depends(get_db)):
    """Download resume for an application"""
    try:
        application = db.query(models.Application).filter(
            models.Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Check if resume exists
        if not hasattr(application, 'resume_data') or not application.resume_data:
            raise HTTPException(status_code=404, detail="Resume not found for this application")
        
        # Decode base64 resume
        try:
            resume_bytes = base64.b64decode(application.resume_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid resume data: {str(e)}")
        
        # Get filename
        filename = application.resume_filename if application.resume_filename else f"resume_{application_id}.pdf"
        
        # Return file using StreamingResponse
        return StreamingResponse(
            io.BytesIO(resume_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading resume: {e}")
        raise HTTPException(status_code=500, detail="Error downloading resume")


@router.get("/applications/{application_id}")
async def get_application_details(application_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific application"""
    try:
        application = db.query(models.Application).filter(
            models.Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        student = db.query(models.DummyStudentRecord).filter(
            models.DummyStudentRecord.id == application.student_id
        ).first()
        job = db.query(models.Job).filter(
            models.Job.id == application.job_id
        ).first()
        
        if not student or not job:
            raise HTTPException(status_code=404, detail="Student or job not found")
        
        # Safely get optional fields
        resume_filename = None
        cover_letter = None
        has_resume = False
        try:
            resume_filename = application.resume_filename if hasattr(application, 'resume_filename') else None
            cover_letter = application.cover_letter if hasattr(application, 'cover_letter') else None
            has_resume = bool(application.resume_data) if hasattr(application, 'resume_data') else False
        except Exception:
            pass
        
        return {
            "id": application.id,
            "student": {
                "id": student.id,
                "name": student.name,
                "reg_number": student.reg_number,
                "email": student.reg_number,
                "cgpa": student.cgpa,
                "branch": student.branch,
                "graduation_year": student.graduation_year,
                "active_backlogs": student.active_backlogs
            },
            "job": {
                "id": job.id,
                "company_name": job.company_name,
                "job_role": job.job_role,
                "description": job.description,
                "location": job.location,
                "min_cgpa": job.min_cgpa
            },
            "status": application.status,
            "applied_at": application.applied_at.isoformat() if application.applied_at else None,
            "resume_filename": resume_filename,
            "has_resume": has_resume,
            "cover_letter": cover_letter
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching application details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching application details")


@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update the status of an application (admin only)"""
    try:
        application = db.query(models.Application).filter(
            models.Application.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected', 'interview scheduled']
        if status_update.status.lower() not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update the application status
        application.status = status_update.status
        db.commit()
        db.refresh(application)
        
        return {
            "id": application.id,
            "status": application.status,
            "message": f"Application status updated to {application.status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating application status: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating application status")


@router.put("/students/{student_id}/placement-status")
async def update_placement_status(
    student_id: int,
    placed: bool,
    db: Session = Depends(get_db)
):
    """Update the placement status of a student (admin only)"""
    try:
        student = db.query(models.DummyStudentRecord).filter(
            models.DummyStudentRecord.id == student_id
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Update the placement status
        student.placed = placed
        db.commit()
        db.refresh(student)
        
        return {
            "id": student.id,
            "name": student.name,
            "placed": student.placed,
            "message": f"Student marked as {'placed' if placed else 'not placed'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating placement status: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating placement status")


@router.delete("/interviews/{interview_id}")
async def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(models.InterviewRound).filter(models.InterviewRound.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    db.delete(interview)
    db.commit()
    return {"message": "Interview deleted"}