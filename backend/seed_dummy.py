import sys
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def seed_dummies():
    db = SessionLocal()
    try:
        dummies = [
            models.DummyStudentRecord(
                reg_number="REG001", name="Test Student 1", cgpa=8.5, address="123 Main St", age=21, dob="2003-01-01", marks="85,90,88", branch="CS", graduation_year=2024, active_backlogs=False, placed=False
            ),
            models.DummyStudentRecord(
                reg_number="REG002", name="Test Student 2", cgpa=7.2, address="456 Oak Ave", age=22, dob="2002-05-15", marks="70,75,72", branch="IT", graduation_year=2024, active_backlogs=True, placed=False
            ),
            models.DummyStudentRecord(
                reg_number="REG003", name="Test Student 3", cgpa=9.1, address="789 Pine Rd", age=20, dob="2004-11-20", marks="92,95,91", branch="EC", graduation_year=2025, active_backlogs=False, placed=False
            )
        ]
        
        for dummy in dummies:
            existing = db.query(models.DummyStudentRecord).filter(models.DummyStudentRecord.reg_number == dummy.reg_number).first()
            if not existing:
                db.add(dummy)
                print(f"Added dummy record for {dummy.reg_number}")
            else:
                print(f"Dummy record for {dummy.reg_number} already exists")
                
        db.commit()
        print("Seeding complete.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_dummies()
