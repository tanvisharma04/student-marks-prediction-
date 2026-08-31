import json
from fastapi import FastAPI, Request, HTTPException
from redis import Redis
from rq import Queue
from tasks import process_form_submission

app = FastAPI(title="Google Form ETL Pipeline")

# Connect to the Redis container
try:
    redis_conn = Redis(host="127.0.0.1", port=6379, db=0)
    task_queue = Queue("default", connection=redis_conn)
except Exception as e:
    print(f"Failed to connect to Redis: {e}")

@app.get("/")
def health_check():
    return {"status": "FastAPI is running", "redis_connected": redis_conn.ping()}

@app.post("/webhook/form-submit")
async def handle_form_webhook(request: Request):
    """
    Endpoint targeted by Google Apps Script. 
    Accepts raw JSON payload and queues it.
    """
    try:
        # Read incoming webhook JSON payload
        payload = await request.json()
        print(f"Received webhook: {json.dumps(payload)}")
        
        # Enqueue the ETL task (non-blocking)
        job = task_queue.enqueue(process_form_submission, payload)
        
        return {
            "status": "queued",
            "job_id": job.get_id(),
            "message": "Form response received and added to processing queue"
        }
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))