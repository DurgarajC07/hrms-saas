from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "hrms",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.payroll",
        "app.tasks.attendance",
        "app.tasks.email",
        "app.tasks.reports",
        "app.tasks.compliance"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'process-daily-attendance': {
        'task': 'app.tasks.attendance.process_daily_attendance',
        'schedule': 60.0 * 60 * 24,  # Daily at midnight
    },
    'generate-monthly-payroll': {
        'task': 'app.tasks.payroll.generate_monthly_payroll',
        'schedule': 60.0 * 60 * 24 * 30,  # Monthly
    },
    'send-leave-reminders': {
        'task': 'app.tasks.email.send_leave_reminders',
        'schedule': 60.0 * 60 * 24,  # Daily
    },
    'backup-database': {
        'task': 'app.tasks.compliance.backup_database',
        'schedule': 60.0 * 60 * 12,  # Twice daily
    },
}
