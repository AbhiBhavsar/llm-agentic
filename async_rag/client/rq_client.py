from redis import Redis
from rq import Queue

from async_rag.queues.worker import process_query

redis_conn = Redis(host="localhost", port=6379, db=0)
queue = Queue(connection=redis_conn)
# queue.enqueue(process_query)