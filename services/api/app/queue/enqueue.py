"""Redis / RQ job queue helpers."""

import os

from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis = Redis.from_url(REDIS_URL)
task_queue = Queue("tabsnap", connection=_redis)


def enqueue_transcription(job_id: str) -> str:
    """Push a transcription job onto the queue. Returns the RQ job id."""
    rq_job = task_queue.enqueue(
        "worker.process_job",
        job_id,
        job_timeout="10m",
        result_ttl=86400,
    )
    return rq_job.id
