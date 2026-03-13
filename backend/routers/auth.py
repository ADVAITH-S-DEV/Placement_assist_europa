from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
import os

from database import get_db
import models
import schemas
from utils import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@router.post("/admin/login", response_model=schemas.Token)
def admin_login(admin_credentials: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == admin_credentials.email).first()
    if not admin or not verify_password(admin_credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": admin.email, "role": "admin"})
    return {"access_token": access_token, "token_type": "bearer", "role": "admin"}

@router.post("/student/google", response_model=schemas.Token)
def student_google_auth(auth_data: schemas.GoogleAuthToken, db: Session = Depends(get_db)):
    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(auth_data.token, requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']
        name = idinfo.get('name', '')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google Token")

    # Check if student exists
    student = db.query(models.Student).filter(models.Student.email == email).first()

    if student:
        # User exists, log them in
        access_token = create_access_token(data={"sub": student.reg_number, "role": "student"})
        return {"access_token": access_token, "token_type": "bearer", "role": "student"}
    
    # User does not exist, they need to register
    if not auth_data.reg_number:
        raise HTTPException(
            status_code=404, 
            detail="User not found. Please provide reg_number to register."
        )
    
    # Verify the dummy record exists to ensure reg_number is valid
    dummy_record = db.query(models.DummyStudentRecord).filter(models.DummyStudentRecord.reg_number == auth_data.reg_number).first()
    if not dummy_record:
        raise HTTPException(status_code=400, detail="Invalid Registration Number. No matching student records found.")
    
    # Ensure this reg_number is not already claimed
    existing_reg = db.query(models.Student).filter(models.Student.reg_number == auth_data.reg_number).first()
    if existing_reg:
        raise HTTPException(status_code=400, detail="Registration Number already claimed by another account.")

    # Create new student user
    new_student = models.Student(
        reg_number=auth_data.reg_number,
        name=name,
        email=email
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Log them in
    access_token = create_access_token(data={"sub": new_student.reg_number, "role": "student"})
    return {"access_token": access_token, "token_type": "bearer", "role": "student"}
