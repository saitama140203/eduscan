import os
from celery import Celery

from app.core.config import settings

# Tạo instance Celery
celery = Celery(
    "eduscan_worker",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)

# Cấu hình Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=False,
    worker_hijack_root_logger=False,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
)

# Tự động import các task từ module
celery.autodiscover_tasks(["app.tasks"], force=True)

# Task routing nếu cần (ví dụ: phân loại task theo queue)
celery.conf.task_routes = {
    "app.tasks.email.*": {"queue": "email"},
    "app.tasks.pdf.*": {"queue": "pdf"},
    "*": {"queue": "default"},
}

# Định nghĩa beat schedule nếu cần (cho các task định kỳ)
celery.conf.beat_schedule = {
    "cleanup-temp-files": {
        "task": "app.tasks.maintenance.cleanup_temp_files",
        "schedule": 86400.0,  # 1 ngày
    },
}

# Khởi động Celery worker theo cách thông thường:
# celery -A app.tasks.worker worker --loglevel=info 