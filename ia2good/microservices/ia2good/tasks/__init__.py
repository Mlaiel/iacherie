"""
Celery tasks for IA2GOOD module
"""

from .celery_app import celery_app
from .notification_tasks import (
    notify_volunteers_nearby,
    notify_assignment_accepted,
    notify_case_completed,
    notify_rating_request,
    notify_case_cancelled,
    cleanup_old_notifications
)
from .ai_tasks import (
    classify_case_async,
    analyze_case_photos,
    detect_duplicate_cases,
    reindex_case_search
)
from .analytics_tasks import (
    aggregate_daily_metrics,
    update_volunteer_statistics,
    calculate_matching_metrics,
    generate_impact_report,
    cleanup_old_analytics
)

__all__ = [
    'celery_app',
    # Notification tasks
    'notify_volunteers_nearby',
    'notify_assignment_accepted',
    'notify_case_completed',
    'notify_rating_request',
    'notify_case_cancelled',
    'cleanup_old_notifications',
    # AI tasks
    'classify_case_async',
    'analyze_case_photos',
    'detect_duplicate_cases',
    'reindex_case_search',
    # Analytics tasks
    'aggregate_daily_metrics',
    'update_volunteer_statistics',
    'calculate_matching_metrics',
    'generate_impact_report',
    'cleanup_old_analytics'
]
