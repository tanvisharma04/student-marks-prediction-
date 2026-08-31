import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@127.0.0.1:5432/student_marks")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. RAW DATA TABLE (Preserves raw JSON payload)
class RawFormResponse(Base):
    __tablename__ = "raw_form_responses"

    id = Column(Integer, primary_key=True, index=True)
    received_at = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON, nullable=False)

# 2. CLEANED DATA TABLE (Structured & Validated)
class CleanedFormResponse(Base):
    __tablename__ = "cleaned_form_responses"

    id = Column(Integer, primary_key=True, index=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    income = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)