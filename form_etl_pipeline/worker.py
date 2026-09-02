import sys
from redis import Redis
from rq import Queue, SimpleWorker  # <-- Import SimpleWorker

# Connect to Redis
redis_conn = Redis(host="127.0.0.1", port=6379, db=0)

if __name__ == "__main__":
    # Specify the queues to listen on
    listen = ["default"]
    
    # SimpleWorker works on Windows by bypassing os.fork()
    worker = SimpleWorker(
        [Queue(name, connection=redis_conn) for name in listen],
        connection=redis_conn
    )
    
    print("[WORKER READY] Windows-compatible SimpleWorker listening on Redis...")
    worker.work()