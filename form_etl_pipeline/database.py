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
    """Stores cleaned data and ML predictions"""
    __tablename__ = "cleaned_form_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    study_hours = Column(Float, nullable=False)
    marks_predicted = Column(Float, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)

# Auto-create tables in PostgreSQL when this file is imported
Base.metadata.create_all(bind=engine)