import json
import re
from database import SessionLocal, RawFormResponse, CleanedFormResponse

def normalize_key(k: str) -> str:
    """Helper to convert string key to lowercase alphanumeric string for robust matching."""
    return "".join(c for c in str(k).lower() if c.isalnum())

def extract_field(payload: dict, *target_patterns: str):
    """
    Extracts raw value from payload dictionary matching target field patterns.
    """
    if not isinstance(payload, dict):
        return None
        
    normalized_payload = {normalize_key(k): v for k, v in payload.items()}
    
    for pattern in target_patterns:
        norm_pattern = normalize_key(pattern)
        if norm_pattern in normalized_payload:
            val = normalized_payload[norm_pattern]
            return str(val) if val is not None else None
            
    # Fallback: substring matching
    for pattern in target_patterns:
        norm_pattern = normalize_key(pattern)
        for k, v in normalized_payload.items():
            if norm_pattern in k:
                return str(v) if v is not None else None
                
    return None

def clean_sgpa(raw_val):
    """
    Cleans SGPA string and bins into ranges:
    5.5 to 6, 6 to 6.5, 6.5 to 7, 7 to 7.5, 7.5 to 8, 8 to 8.5, 8.5 to 9.
    Invalid / non-numeric text returns None.
    """
    if not raw_val:
        return None
    val_str = str(raw_val).strip().replace(" ", "")
    try:
        val = float(val_str)
        if val <= 0:
            return None
        if 5.5 <= val < 6.0:
            return "5.5 to 6"
        elif 6.0 <= val < 6.5:
            return "6 to 6.5"
        elif 6.5 <= val < 7.0:
            return "6.5 to 7"
        elif 7.0 <= val < 7.5:
            return "7 to 7.5"
        elif 7.5 <= val < 8.0:
            return "7.5 to 8"
        elif 8.0 <= val < 8.5:
            return "8 to 8.5"
        elif 8.5 <= val <= 9.0:
            return "8.5 to 9"
        else:
            return None
    except ValueError:
        return None

def clean_attendance(raw_val):
    """
    Cleans attendance string and bins into ranges:
    65 to 70, 70 to 75, 75 to 80, 80 to 85, 85 to 90, 90 to 95.
    Strips %, ℅, handles range formats like '85 -90 %'.
    """
    if not raw_val:
        return None
    val_str = str(raw_val).strip()
    
    # Check for range string like "85 -90 %"
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', val_str)
    if range_match:
        n1, n2 = float(range_match.group(1)), float(range_match.group(2))
        val = (n1 + n2) / 2.0
    else:
        cleaned_num = re.sub(r'[^\d.]', '', val_str)
        try:
            val = float(cleaned_num)
        except ValueError:
            return None

    if val <= 0 or val < 60:
        return None

    if 65 <= val < 70:
        return "65 to 70"
    elif 70 <= val < 75:
        return "70 to 75"
    elif 75 <= val < 80:
        return "75 to 80"
    elif 80 <= val < 85:
        return "80 to 85"
    elif 85 <= val < 90:
        return "85 to 90"
    elif 90 <= val <= 100:
        return "90 to 95"
    else:
        return None

def process_form_submission(payload):
    """
    ETL Background Task executed by Redis Worker (worker.py).
    Applies data cleaning and range binning rules, then saves to PostgreSQL.
    Semester and branch columns are dropped. Roll No is saved as Serial No from 1 onwards.
    """
    db = SessionLocal()
    try:
        print(f"[TASK STARTED] Processing payload: {payload}")

        # 1. Store Raw Response in PostgreSQL
        raw_record = RawFormResponse(payload=payload)
        db.add(raw_record)
        db.commit()
        db.refresh(raw_record)

        # 2. Assign Serial No from 1 onwards for University Roll No column
        serial_no = str(db.query(CleanedFormResponse).count() + 1)

        # 3. Extract and Clean Data Fields
        # Note: 'semester' and 'branch' columns are intentionally dropped.
        raw_sgpa = extract_field(payload, "previous semester sgpa", "previous_semester_sgpa", "sgpa")
        raw_attendance = extract_field(payload, "previous semester attendance", "previous_semester_attendance", "attendance")
        raw_study = extract_field(payload, "average study per day", "average_study_per_day", "study hours", "study_per_day")
        raw_exam_prep = extract_field(payload, "when do you start to study for exam", "when_do_you_start_to_study_for_exam", "study for exam", "start to study")
        raw_sleep = extract_field(payload, "average sleep", "average_sleep", "sleep")
        raw_notes = extract_field(payload, "notes")
        raw_social_media = extract_field(payload, "social media", "social_media")
        raw_exercise = extract_field(payload, "exercise")

        sgpa_cleaned = clean_sgpa(raw_sgpa)
        attendance_cleaned = clean_attendance(raw_attendance)
        study_cleaned = raw_study.strip() if raw_study else None
        exam_prep_cleaned = raw_exam_prep.strip() if raw_exam_prep else None
        sleep_cleaned = raw_sleep.strip() if raw_sleep else None
        notes_cleaned = raw_notes.strip() if raw_notes else None
        social_media_cleaned = raw_social_media.strip() if raw_social_media else None
        exercise_cleaned = raw_exercise.strip() if raw_exercise else None

        # 4. Save Cleaned Data to PostgreSQL DB Table
        cleaned_record = CleanedFormResponse(
            university_roll_no=serial_no,
            previous_semester_sgpa=sgpa_cleaned,
            previous_semester_attendance=attendance_cleaned,
            average_study_per_day=study_cleaned,
            when_do_you_start_to_study_for_exam=exam_prep_cleaned,
            average_sleep=sleep_cleaned,
            notes=notes_cleaned,
            social_media=social_media_cleaned,
            exercise=exercise_cleaned
        )
        db.add(cleaned_record)
        db.commit()

        print(f"[TASK SUCCESS] Saved cleaned response | Serial No: {serial_no} | SGPA: {sgpa_cleaned} | Attendance: {attendance_cleaned}")
        return True

    except Exception as e:
        db.rollback()
        print(f"[TASK ERROR] Failed to process payload: {e}")
        raise e

    finally:
        db.close()