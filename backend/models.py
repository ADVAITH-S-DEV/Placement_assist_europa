
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey,Boolean
from database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    reg_number = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True) # Used for OAuth
    
class DummyStudentRecord(Base):
    __tablename__ = "dummy_student_records"
    name = Column(String)
    id = Column(Integer, primary_key=True, index=True)
    reg_number = Column(String, unique=True, index=True)
    cgpa = Column(Float)
    address = Column(Text)
    age = Column(Integer)
    dob = Column(String) # For simplicity
    marks = Column(String) # Could be JSON in Postgres, keeping string to support SQLite simply
    # New academic fields
    branch = Column(String)  # IT, CS, EEE, EC, MECH, CIVIL
    graduation_year = Column(Integer)
    active_backlogs = Column(Boolean, default=False)
    placed = Column(Boolean, default=False)
class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    job_role = Column(String)
    description = Column(String)
    tech_skills = Column(String) # Stored as comma separated
    location = Column(String)
    min_cgpa = Column(Float)
    backlogs = Column(Boolean)

class InterviewRound(Base):
    __tablename__ = "interview_rounds"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    student_id = Column(Integer, ForeignKey("dummy_student_records.id"))
    round_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)