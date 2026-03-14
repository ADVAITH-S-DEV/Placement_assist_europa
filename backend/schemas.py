from pydantic import BaseModel, EmailStr
from typing import Optional, List

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class StudentRegister(BaseModel):
    email: EmailStr
    name: str
    reg_number: str

# Google Auth uses a token ID from frontend
class GoogleAuthToken(BaseModel):
    token: str
    reg_number: Optional[str] = None  # Will provide if registering

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str  # 'admin' or 'student'

class DummyStudentResponse(BaseModel):
    id: Optional[int] = None
    reg_number: str
    name: Optional[str] = None
    cgpa: Optional[float] = None
    address: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[str] = None
    marks: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    active_backlogs: Optional[bool] = False
    placed: Optional[bool] = False

    class Config:
        from_attributes = True

class StudentResponse(BaseModel):
    reg_number: str
    name: str
    email: str

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: int
    company_name: str
    job_role: str
    description: str
    tech_skills: str
    location: str
    min_cgpa: float
    backlogs: Optional[bool] = False

    class Config:
        from_attributes = True
