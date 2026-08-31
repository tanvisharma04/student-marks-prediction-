from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from redis import Redis
from rq import Queue
from sqlalchemy.orm import Session
from database import SessionLocal, RawFormResponse, CleanedFormResponse
from tasks import process_form_submission

app = FastAPI(title="Google Form Buffered ETL Pipeline")

# Connect to Redis
redis_conn = Redis(host="localhost", port=6379)
task_queue = Queue("form_responses", connection=redis_conn)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. WEBHOOK INGESTION ENDPOINT ---
@app.post("/webhook/form-submit")
async def receive_form_submission(payload: dict):
    """
    Receives JSON payload from Google Apps Script, enqueues it to Redis, 
    and returns 200 OK immediately.
    """
    if not payload:
        raise HTTPException(status_code=400, detail="Empty payload")

    # Enqueue task asynchronously
    job = task_queue.enqueue(process_form_submission, payload)

    return {
        "status": "accepted",
        "message": "Payload buffered in Redis queue successfully.",
        "job_id": job.id
    }

# --- 2. PIPELINE DASHBOARD ---
@app.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(db: Session = Depends(get_db)):
    raw_count = db.query(RawFormResponse).count()
    clean_count = db.query(CleanedFormResponse).count()
    queued_jobs = len(task_queue)

    return f"""
    <html>
        <head>
            <title>ETL Pipeline Status Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ font-size: 28px; font-weight: bold; color: #007bff; }}
            </style>
        </head>
        <body>
            <h1>Google Form ETL Pipeline Observability</h1>
            <div class="card">
                <h3>Redis Queue Buffer</h3>
                <p class="metric">{queued_jobs} Pending Tasks</p>
            </div>
            <div class="card">
                <h3>PostgreSQL Raw Responses (JSON)</h3>
                <p class="metric">{raw_count} Ingested Records</p>
            </div>
            <div class="card">
                <h3>PostgreSQL Cleaned Responses</h3>
                <p class="metric">{clean_count} Processed Records</p>
            </div>
        </body>
    </html>
    """