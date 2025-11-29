from fastapi import FastAPI, Query
from .client.rq_client import queue
from .queues.worker import process_query

app = FastAPI()

@app.get('/')
def root():
    return {'status': 'Server running'}

@app.post('/chat')
def chat(query: str = Query(...,description='User chat query')):
    job = queue.enqueue(process_query, query)
    return {'status': 'Job qued', 'job_id':job.id}

@app.get('/job-status')
def get_job_status(job_id: str = Query(...,description='Job Id')):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()
    return {'result':result}