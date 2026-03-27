"""Celery application configuration."""

import os
from celery import Celery

app = Celery("workflow_toolkit")

app.config_from_object({
    "broker_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "result_backend": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "task_track_started": True,
    "task_acks_late": True,
    "worker_prefetch_multiplier": 1,
    "task_default_retry_delay": int(os.getenv("CELERY_RETRY_BACKOFF", "60")),
    "task_max_retries": int(os.getenv("CELERY_RETRY_MAX", "3")),
})

app.autodiscover_tasks(["workers"])
