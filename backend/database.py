import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# Get the URL from .env, with fallback to SQLite for development
raw_url = os.getenv("DATABASE_URL", "sqlite:///./placement.db")

if raw_url.startswith("sqlite"):
    # SQLite for local development
    engine = create_engine(raw_url, connect_args={"check_same_thread": False})
else:
    # PostgreSQL/Supabase for production
    try:
        url_object = make_url(raw_url)
        engine = create_engine(
            url_object.set(drivername="postgresql+psycopg2"), 
            poolclass=NullPool,
            connect_args={"connect_timeout": 5}
        )
    except Exception as e:
        print(f"Warning: Failed to connect to PostgreSQL at {raw_url}")
        print(f"Error: {e}")
        print("Falling back to SQLite for local development...")
        engine = create_engine("sqlite:///./placement.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()