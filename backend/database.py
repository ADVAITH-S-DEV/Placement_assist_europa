import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# Get the URL from .env
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    raise ValueError("DATABASE_URL not found in .env file")

# 1. Safely parse the URL (This handles the @ in your password correctly)
url_object = make_url(raw_url)

# 2. Configure the Engine
if url_object.drivername.startswith("sqlite"):
    engine = create_engine(raw_url, connect_args={"check_same_thread": False})
else:
    # Use NullPool for Supabase and explicitly set the driver
    engine = create_engine(
        url_object.set(drivername="postgresql+psycopg2"), 
        poolclass=NullPool
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()