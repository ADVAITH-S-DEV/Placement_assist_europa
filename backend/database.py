import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

raw_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# To handle SQLite differences like check_same_thread
if raw_url.startswith("sqlite"):
    engine = create_engine(raw_url, connect_args={"check_same_thread": False})
else:
    # Parse the DATABASE_URL manually to safely handle special chars (e.g. @ in password)
    # Expected format: postgresql://user:password@host:port/dbname
    # Split at last @ before the host to correctly separate credentials and host
    scheme, rest = raw_url.split("://", 1)
    at_idx = rest.rfind("@")
    credentials = rest[:at_idx]
    host_part = rest[at_idx + 1:]

    colon_idx = credentials.find(":")
    db_user = credentials[:colon_idx]
    db_password = credentials[colon_idx + 1:]

    slash_idx = host_part.find("/")
    host_and_port = host_part[:slash_idx]
    db_name = host_part[slash_idx + 1:]

    if ":" in host_and_port:
        db_host, db_port = host_and_port.rsplit(":", 1)
        db_port = int(db_port)
    else:
        db_host = host_and_port
        db_port = 5432

    engine_url = URL.create(
        drivername="postgresql+psycopg2",
        username=db_user,
        password=db_password,  # SQLAlchemy URL.create handles escaping
        host=db_host,
        port=db_port,
        database=db_name,
    )
    engine = create_engine(engine_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
