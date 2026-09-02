import os
import csv
import sys

# Ensure UTF-8 output encoding for Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import SessionLocal, RawFormResponse
from tasks import process_form_submission, extract_field

def is_duplicate(db, payload):
    """
    Checks if raw_form_responses table already contains an entry with the same timestamp and roll number,
    or exact JSON payload.
    """
    timestamp = extract_field(payload, "timestamp")
    roll_no = extract_field(payload, "university roll no", "university_roll_no", "roll no", "roll_no")
    
    # Query raw_form_responses
    existing_records = db.query(RawFormResponse).all()
    for rec in existing_records:
        rec_payload = rec.payload if isinstance(rec.payload, dict) else {}
        rec_timestamp = extract_field(rec_payload, "timestamp")
        rec_roll_no = extract_field(rec_payload, "university roll no", "university_roll_no", "roll no", "roll_no")
        
        # Check if timestamp & roll_no match (or payload exact match)
        if timestamp and roll_no and rec_timestamp == timestamp and rec_roll_no == roll_no:
            return True
        if rec_payload == payload:
            return True
            
    return False

def run_bulk_ingestion(csv_filepath="bulk_responses.csv"):
    if not os.path.exists(csv_filepath):
        print(f"[ERROR] File not found: {csv_filepath}")
        return

    db = SessionLocal()
    processed_count = 0
    skipped_count = 0
    total_rows = 0

    try:
        with open(csv_filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                total_rows += 1
                # Convert row to clean payload dict
                payload = {k.strip(): v.strip() for k, v in row.items() if k}
                
                timestamp = extract_field(payload, "timestamp")
                roll_no = extract_field(payload, "university roll no", "university_roll_no", "roll no", "roll_no")

                # Check for duplicate
                if is_duplicate(db, payload):
                    skipped_count += 1
                    print(f"[SKIP DUPLICATE] Row {i}: Roll No '{roll_no}' (Timestamp: {timestamp}) already exists in PostgreSQL.")
                    continue

                # Process new record
                success = process_form_submission(payload)
                if success:
                    processed_count += 1

        print("\n==========================================")
        print(f"[BULK INGESTION COMPLETED]")
        print(f"Total Rows Evaluated : {total_rows}")
        print(f"New Records Inserted : {processed_count}")
        print(f"Duplicates Skipped   : {skipped_count}")
        print("==========================================\n")

    except Exception as e:
        print(f"[BULK INGESTION ERROR] {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "bulk_responses.csv"
    run_bulk_ingestion(csv_path)
