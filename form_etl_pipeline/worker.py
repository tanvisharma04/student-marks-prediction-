import os
import redis
from rq import Worker, Queue

# Connect to local Redis instance
redis_conn = redis.Redis(host="localhost", port=6379, db=0)

# Listen to default queue
listen = ["default"]

if __name__ == "__main__":
    # Create queues using the explicit connection parameter
    queues = [Queue(name, connection=redis_conn) for name in listen]
    
    # Initialize worker with connection and queues
    worker = Worker(queues, connection=redis_conn)
    
    print("[WORKER READY] Listening for jobs on Redis...")
    worker.work()