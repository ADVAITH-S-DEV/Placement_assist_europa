from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
# Import the new placement router (we will create this next)
from routers import auth, users, placements 
from utils import get_password_hash

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Placement Assistance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Included your new placement logic here
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(placements.router) 

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
        
        # Seed logic remains the same...
        db.commit()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Placement Assistance API is running"}