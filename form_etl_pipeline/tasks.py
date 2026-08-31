import json
import numpy as np
from database import SessionLocal, RawFormResponse, CleanedFormResponse

def predict_marks(study_hours):
    """
    Simple prediction model.
    Adjust formula based on your trained model if needed.
    """
    try:
        hours = float(study_hours)
        # Example linear calculation: Marks = 10 * hours + 20 (capped at 100)
        predicted = min(100.0, max(0.0, (hours * 9.5) + 5.0))
        return round(predicted, 2)
    except (ValueError, TypeError):
        return 0.0

def process_form_submission(payload):
    """
    ETL Background Task executed by Redis Worker (worker.py)
    """
    db = SessionLocal()
    try:
        print(f"[TASK STARTED] Processing payload: {payload}")

        # 1. Store Raw Response in PostgreSQL
        raw_record = RawFormResponse(payload=payload)
        db.add(raw_record)
        db.commit()
        db.refresh(raw_record)

        # 2. Extract and Clean Data from Form Payload
        # Adjust key names below to match your Google Form field keys
        full_name = payload.get("full_name") or payload.get("Name") or "Unknown"
        email = payload.get("email") or payload.get("Email") or "N/A"
        study_hours_raw = payload.get("study_hours") or payload.get("Study Hours") or 0

        # 3. Predict Marks
        study_hours = float(study_hours_raw) if str(study_hours_raw).replace('.', '', 1).isdigit() else 0.0
        predicted_marks = predict_marks(study_hours)

        # 4. Save Cleaned & Predicted Data to PostgreSQL
        cleaned_record = CleanedFormResponse(
            full_name=str(full_name).strip(),
            email=str(email).strip().lower(),
            study_hours=study_hours,
            marks_predicted=predicted_marks
        )
        db.add(cleaned_record)
        db.commit()

        print(f"[TASK SUCCESS] Saved student: {full_name} | Hours: {study_hours} | Predicted Marks: {predicted_marks}")
        return True

    except Exception as e:
        db.rollback()
        print(f"[TASK ERROR] Failed to process payload: {e}")
        raise e

    finally:
        db.close()