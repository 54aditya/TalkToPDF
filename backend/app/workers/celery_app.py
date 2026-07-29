from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "voice_rag_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Standard configuration optimizations for Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30-minute time limit for PDF processing
)

# Automatically look for tasks inside tasks.py
celery_app.autodiscover_tasks(["app.workers"])
