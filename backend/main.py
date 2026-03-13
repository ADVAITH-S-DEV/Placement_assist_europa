from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from routers import auth, users
from utils import get_password_hash

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Placement Assistance API")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)

# Seed database with dummy data if not already present
@app.on_event("startup")
def startup_event():
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
        
        # Insert dummy records
        dummy_data = [
            {"reg_number": "REG001", "cgpa": 8.5, "address": "123 Campus Dr", "age": 21, "dob": "2002-05-10", "marks": "Math: 90, Science: 85"},
            {"reg_number": "REG002", "cgpa": 7.2, "address": "456 City Line", "age": 22, "dob": "2001-11-20", "marks": "Math: 70, Science: 75"},
            {"reg_number": "REG003", "cgpa": 9.1, "address": "789 Metro Rd", "age": 20, "dob": "2003-01-15", "marks": "Math: 95, Science: 92"},
        ]
        
        for data in dummy_data:
            record = db.query(models.DummyStudentRecord).filter(models.DummyStudentRecord.reg_number == data["reg_number"]).first()
            if not record:
                new_record = models.DummyStudentRecord(**data)
                db.add(new_record)
        
        db.commit()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Placement Assistance API is running"}
