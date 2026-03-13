from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from dependencies import get_current_user, get_current_admin, get_current_student

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/profile", response_model=schemas.DummyStudentResponse)
def get_student_profile(current_user = Depends(get_current_student), db: Session = Depends(get_db)):
    # Fetch details from DummyStudentRecord using student's reg_number
    dummy_record = db.query(models.DummyStudentRecord).filter(models.DummyStudentRecord.reg_number == current_user.reg_number).first()
    return dummy_record

@router.get("/students", response_model=List[schemas.StudentResponse])
def get_all_registered_students(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(models.Student).all()
