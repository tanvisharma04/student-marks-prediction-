Real-Time Event-Driven ETL & Prediction Pipeline
An asynchronous, event-driven data engineering pipeline that captures Google Form submissions via webhooks, 
processes and cleans payload data asynchronously using a Redis task queue, generates student mark predictions, 
and persists both raw JSON payloads and cleaned ML-ready data into a Dockerized PostgreSQL database.



Event Source: User submits a response on Google Forms.

Webhook Publisher: Google Apps Script extracts response data and posts an HTTP JSON payload.

Tunneling Proxy: Ngrok securely forwards external cloud requests to the local machine.

API Gateway: FastAPI receives the payload non-blockingly and pushes an ETL task to Redis Queue (RQ).

Asynchronous Processing: A dedicated Python SimpleWorker pops tasks from Redis, cleans data, performs ML predictions, and formats data.

Data Storage: Data is stored across dual PostgreSQL tables (raw_form_responses and cleaned_form_responses).

Tech Stack
Language: Python 3.12

API Gateway: FastAPI + Uvicorn

Task Queue & Broker: Redis + RQ (Redis Queue)

Database & Infrastructure: PostgreSQL (Dockerized)

Tunneling: Ngrok

Automation: Google Apps Script

Database Schema
The pipeline segregates raw ingestion from processed datasets across two primary tables in PostgreSQL:

raw_form_responses
id (SERIAL PRIMARY KEY)

payload (JSONB)

created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

cleaned_form_responses
id (SERIAL PRIMARY KEY)

full_name (VARCHAR)

email (VARCHAR)

study_hours (FLOAT)

marks_predicted (FLOAT)

processed_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

Getting Started
Prerequisites
Docker & Docker Desktop installed

Python 3.10+

Ngrok CLI

1. Clone the Repository
Bash
git clone https://github.com/your-username/student-marks-etl-pipeline.git
cd student-marks-etl-pipeline
2. Set Up Virtual Environment & Dependencies
Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
3. Spin Up Docker Infrastructure
Start PostgreSQL and Redis containers:

Bash
docker-compose up -d
Running the Pipeline
To run the complete end-to-end pipeline locally, start each service in separate terminal windows:

Terminal 1: FastAPI Gateway
Bash
uvicorn main:app --reload --port 8000
Terminal 2: Ngrok Static Tunnel
Bash
ngrok http --url=your-ngrok-static-domain.ngrok-free.dev 8000
Terminal 3: Redis Task Worker
Bash
python worker.py
Key Technical Challenges Solved
Windows Process Forking Limitation: Standard rq.Worker depends on os.fork(), an OS call available exclusively on Unix environments. 
Resolved by implementing rq.SimpleWorker to allow single-threaded, non-forking job execution on Windows.

Webhook Payload Sanitization: Form event objects vary depending on manual vs. automated execution contexts. Updated Apps Script handlers to handle missing keys dynamically and pass standard JSON structures to FastAPI.

Database Isolation: Separated raw JSON payload logging from structured ML feature stores to enable easy data auditing and full pipeline re-playability.
