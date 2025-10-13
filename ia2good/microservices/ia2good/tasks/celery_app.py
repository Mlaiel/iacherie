"""
Celery application configuration for IA2GOOD module
"""
import os
from celery import Celery
from celery.schedules import crontab

# Get configuration from environment
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create Celery application
celery_app = Celery(
    'ia2good',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        'microservices.ia2good.tasks.notification_tasks',
        'microservices.ia2good.tasks.ai_tasks',
        'microservices.ia2good.tasks.analytics_tasks'
    ]
)

# Configure Celery
celery_app.conf.update(
    # Task execution settings
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Paris',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'microservices.ia2good.tasks.notification_tasks.*': {'queue': 'notifications'},
        'microservices.ia2good.tasks.ai_tasks.*': {'queue': 'ai_processing'},
        'microservices.ia2good.tasks.analytics_tasks.*': {'queue': 'analytics'},
    },
    
    # Task result settings
    result_expires=3600,  # 1 hour
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Analytics aggregation every day at 1 AM
    'aggregate-daily-metrics': {
        'task': 'microservices.ia2good.tasks.analytics_tasks.aggregate_daily_metrics',
        'schedule': crontab(hour=1, minute=0),
    },
    # Update volunteer statistics every hour
    'update-volunteer-statistics': {
        'task': 'microservices.ia2good.tasks.analytics_tasks.update_volunteer_statistics',
        'schedule': crontab(minute=0),  # Every hour
    },
    # Clean up old notifications every day at 3 AM
    'cleanup-old-notifications': {
        'task': 'microservices.ia2good.tasks.notification_tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=0),
    },
}

if __name__ == '__main__':
    celery_app.start()
