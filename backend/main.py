from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from routers import auth, users, placements
from utils import get_password_hash
from migrate_db import migrate_database

app = FastAPI(title="Placement Assistance API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(placements.router)

@app.on_event("startup")
def startup_event():
    try:
        # Create all database tables
        models.Base.metadata.create_all(bind=engine)
        # Run database migration to handle schema updates
        migrate_database()
    except Exception as e:
        print(f"Warning: Could not initialize database schema: {e}")
    
    db = SessionLocal()
    try:
        # Create default admin if not exists
        admin = db.query(models.Admin).filter(models.Admin.email == "admin@example.com").first()
        if not admin:
            new_admin = models.Admin(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123")
            )
            db.add(new_admin)

        # Seed dummy student records if none exist
        existing_count = db.query(models.DummyStudentRecord).count()
        if existing_count == 0:
            dummy_students = [
                models.DummyStudentRecord(
                    reg_number="REG001",
                    name="Alice Johnson",
                    cgpa=8.5,
                    address="123 Main Street, Chennai",
                    age=21,
                    dob="2003-01-15",
                    marks="85,90,88,92,87",
                    branch="CS",
                    graduation_year=2025,
                    active_backlogs=False,
                    placed=False
                ),
                models.DummyStudentRecord(
                    reg_number="REG002",
                    name="Bob Kumar",
                    cgpa=7.2,
                    address="456 Oak Avenue, Bangalore",
                    age=22,
                    dob="2002-05-20",
                    marks="70,75,72,68,74",
                    branch="IT",
                    graduation_year=2024,
                    active_backlogs=True,
                    placed=False
                ),
                models.DummyStudentRecord(
                    reg_number="REG003",
                    name="Carol Patel",
                    cgpa=9.1,
                    address="789 Pine Road, Mumbai",
                    age=20,
                    dob="2004-11-05",
                    marks="92,95,91,96,93",
                    branch="EC",
                    graduation_year=2025,
                    active_backlogs=False,
                    placed=False
                ),
                models.DummyStudentRecord(
                    reg_number="REG004",
                    name="David Singh",
                    cgpa=6.8,
                    address="321 Elm St, Delhi",
                    age=23,
                    dob="2001-03-12",
                    marks="65,70,68,72,66",
                    branch="MECH",
                    graduation_year=2024,
                    active_backlogs=False,
                    placed=False
                ),
                models.DummyStudentRecord(
                    reg_number="REG005",
                    name="Eva Sharma",
                    cgpa=8.9,
                    address="654 Maple Ave, Hyderabad",
                    age=21,
                    dob="2003-07-22",
                    marks="88,90,89,91,87",
                    branch="EEE",
                    graduation_year=2025,
                    active_backlogs=False,
                    placed=False
                ),
            ]
            for s in dummy_students:
                db.add(s)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Startup seed error: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Placement Assistance API is running"}