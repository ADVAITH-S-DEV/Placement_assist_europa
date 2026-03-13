from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class StudentRegister(BaseModel):
    email: EmailStr
    name: str # The name shouldn't really be sent from Google payload since we just receive the token, but we'll accept it for now
    reg_number: str

# Google Auth uses a token ID from frontend
class GoogleAuthToken(BaseModel):
    token: str
    reg_number: Optional[str] = None # Will provide if registering

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str # 'admin' or 'student'

class DummyStudentResponse(BaseModel):
    reg_number: str
    cgpa: float
    address: str
    age: int
    dob: str
    marks: str

    class Config:
        from_attributes = True  # Change 'orm_mode = True' to this

class StudentResponse(BaseModel):
    reg_number: str
    name: str
    email: str

    class Config:
        from_attributes = True  # Change 'orm_mode = True' to this
