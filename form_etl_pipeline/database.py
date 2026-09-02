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
    """Stores cleaned Google Form response features"""
    __tablename__ = "cleaned_form_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    previous_semester_sgpa = Column(String(100), nullable=True)
    previous_semester_attendance = Column(String(100), nullable=True)
    average_study_per_day = Column(String(100), nullable=True)
    when_do_you_start_to_study_for_exam = Column(String(200), nullable=True)
    average_sleep = Column(String(100), nullable=True)
    notes = Column(String(200), nullable=True)
    social_media = Column(String(100), nullable=True)
    exercise = Column(String(100), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import inspect, text

def init_db():
    try:
        inspector = inspect(engine)
        if "cleaned_form_responses" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("cleaned_form_responses")]
            if "university_roll_no" in columns:
                print("[DATABASE SETUP] Dropping 'university_roll_no' column from 'cleaned_form_responses' by recreating table...")
                with engine.connect() as conn:
                    conn.execute(text("DROP TABLE cleaned_form_responses CASCADE;"))
                    conn.commit()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[DATABASE SETUP ERROR] {e}")

init_db()