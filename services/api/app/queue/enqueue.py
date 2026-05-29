"""Job queue — uses Redis/RQ when available, falls back to sync processing."""

import os
import threading

REDIS_URL = os.getenv("REDIS_URL", "")

_redis = None
_queue = None


def _init_redis():
    global _redis, _queue
    if not REDIS_URL:
        return False
    try:
        from redis import Redis
        from rq import Queue
        _redis = Redis.from_url(REDIS_URL)
        _redis.ping()
        _queue = Queue("tabsnap", connection=_redis)
        return True
    except Exception:
        return False


_has_redis = _init_redis() if REDIS_URL else False


def enqueue_transcription(job_id: str) -> str:
    """Push a transcription job. Uses Redis if available, else runs in a thread."""
    if _has_redis and _queue is not None:
        rq_job = _queue.enqueue(
            "worker.process_job",
            job_id,
            job_timeout="10m",
            result_ttl=86400,
        )
        return rq_job.id

    # Local dev: run synchronously in a background thread
    thread = threading.Thread(
        target=_run_sync,
        args=(job_id,),
        daemon=True,
    )
    thread.start()
    return f"local-{job_id}"


def _run_sync(job_id: str) -> None:
    """Run the worker pipeline directly (no Redis needed)."""
    import sys
    from pathlib import Path

    # Add worker and packages to path
    root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(root / "services" / "worker"))
    sys.path.insert(0, str(root / "packages"))

    from worker import process_job
    try:
        process_job(job_id)
    except Exception as exc:
        print(f"[local-worker] Job {job_id} failed: {exc}")
