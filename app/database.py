from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base # Import Base from models.py

# PostgreSQL connection string from settings
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    Base.metadata.create_all(engine) # Use Base from SQLAlchemy

def get_db(): # Renamed to get_db to align with FastAPI common practice
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()