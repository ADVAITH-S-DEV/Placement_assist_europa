import sys
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import utils

db = SessionLocal()
admin = db.query(models.Admin).filter(models.Admin.email == 'admin@example.com').first()
if admin:
    print(f"Admin found: {admin.email}")
    print(f"Password hash: {admin.hashed_password}")
    is_valid = utils.verify_password("admin123", admin.hashed_password)
    print(f"Password 'admin123' verification: {is_valid}")
else:
    print("Admin NOT found in database")
    
admins = db.query(models.Admin).all()
print(f"All admins in DB: {[a.email for a in admins]}")
