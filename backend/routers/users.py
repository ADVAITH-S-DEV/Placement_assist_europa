from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from dependencies import get_current_user, get_current_admin, get_current_student

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/profile", response_model=schemas.DummyStudentResponse)
def get_student_profile(current_user = Depends(get_current_student), db: Session = Depends(get_db)):
    # Fetch full details from DummyStudentRecord using student's reg_number
    dummy_record = db.query(models.DummyStudentRecord).filter(
        models.DummyStudentRecord.reg_number == current_user.reg_number
    ).first()

    if dummy_record:
        # Merge the student name from the Student table if missing in dummy record
        if not dummy_record.name:
            dummy_record.name = current_user.name
        return dummy_record

    # If no dummy record exists, return a partial profile from the Student table
    # so the dashboard doesn't break
    return schemas.DummyStudentResponse(
        reg_number=current_user.reg_number,
        name=current_user.name,
        cgpa=None,
        address=None,
        age=None,
        dob=None,
        marks=None,
        branch=None,
        graduation_year=None,
        active_backlogs=False,
        placed=False,
    )

@router.get("/students", response_model=List[schemas.StudentResponse])
def get_all_registered_students(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(models.Student).all()
