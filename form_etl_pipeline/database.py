import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Connection string matching Docker container credentials
DATABASE_URL = "postgresql://user:password@127.0.0.1:5432/student_marks"

# Create engine and session maker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---

class RawFormResponse(Base):
    """Stores the raw, unedited JSON webhook payload from Google Forms"""
    __tablename__ = "raw_form_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CleanedFormResponse(Base):
    """Stores raw Google Form responses prior to cleaning/predictions"""
    __tablename__ = "cleaned_form_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    university_roll_no = Column(String(100), nullable=True)
    previous_semester_sgpa = Column(String(100), nullable=True)
    previous_semester_attendance = Column(String(100), nullable=True)
    average_study_per_day = Column(String(100), nullable=True)
    when_do_you_start_to_study_for_exam = Column(String(200), nullable=True)
    average_sleep = Column(String(100), nullable=True)
    notes = Column(String(200), nullable=True)
    social_media = Column(String(100), nullable=True)
    exercise = Column(String(100), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

# Auto-create tables in PostgreSQL when this file is imported
Base.metadata.create_all(bind=engine)