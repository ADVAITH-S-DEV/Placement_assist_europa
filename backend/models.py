from sqlalchemy import Column, Integer, String, Float, Boolean, Text
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
    id = Column(Integer, primary_key=True, index=True)
    reg_number = Column(String, unique=True, index=True)
    cgpa = Column(Float)
    address = Column(Text)
    age = Column(Integer)
    dob = Column(String) # For simplicity
    marks = Column(String) # Could be JSON in Postgres, keeping string to support SQLite simply
