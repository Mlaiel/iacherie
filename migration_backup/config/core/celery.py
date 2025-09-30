"""
Celery Configuration
Celery task queue and worker configuration
"""

import os
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    """Celery-specific settings"""
    
    # Celery Broker Settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # Default to Redis if not specified
    broker_host: str = "localhost"
    broker_port: int = 6379
    broker_db: int = 1  # Use different DB than main Redis
    result_backend_db: int = 2  # Use different DB for results
    
    # Celery Worker Settings
    celery_worker_concurrency: int = 4
    celery_worker_prefetch_multiplier: int = 1
    celery_worker_max_tasks_per_child: int = 1000
    celery_worker_max_memory_per_child: int = 200000  # 200MB
    
    # Celery Task Settings
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: List[str] = ["json"]
    celery_timezone: str = "UTC"
    celery_enable_utc: bool = True
    
    # Celery Result Settings
    celery_result_expires: int = 3600  # 1 hour
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 300  # 5 minutes
    celery_task_soft_time_limit: int = 240  # 4 minutes
    
    # Celery Routing
    celery_task_routes: Dict[str, Dict[str, str]] = {
        "tasks.high_priority.*": {"queue": "high_priority"},
        "tasks.low_priority.*": {"queue": "low_priority"},
        "tasks.ai_processing.*": {"queue": "ai_processing"},
        "tasks.content_analysis.*": {"queue": "content_analysis"},
    }
    
    # Celery Beat Settings (Periodic Tasks)
    celery_beat_schedule: Dict[str, Dict[str, Any]] = {
        "cleanup-expired-tokens": {
            "task": "tasks.cleanup.cleanup_expired_tokens",
            "schedule": 3600.0,  # Every hour
        },
        "generate-analytics-reports": {
            "task": "tasks.analytics.generate_daily_reports",
            "schedule": 86400.0,  # Every day
        },
    }
    
    @property
    def broker_url(self) -> str:
        """Get Celery broker URL"""
        if self.celery_broker_url:
            return self.celery_broker_url
        return f"redis://{self.broker_host}:{self.broker_port}/{self.broker_db}"
    
    @property
    def result_backend_url(self) -> str:
        """Get Celery result backend URL"""
        if self.celery_result_backend:
            return self.celery_result_backend
        return f"redis://{self.broker_host}:{self.broker_port}/{self.result_backend_db}"
    
    class Config:
        env_file = ".env"
        extra = "allow"


# Celery configuration functions
def get_celery_config() -> dict:
    """Get Celery configuration as dictionary"""
    settings = CelerySettings()
    return {
        # Broker settings
        "broker_url": settings.broker_url,
        "result_backend": settings.result_backend_url,
        
        # Task settings
        "task_serializer": settings.celery_task_serializer,
        "result_serializer": settings.celery_result_serializer,
        "accept_content": settings.celery_accept_content,
        "timezone": settings.celery_timezone,
        "enable_utc": settings.celery_enable_utc,
        
        # Result settings
        "result_expires": settings.celery_result_expires,
        "task_track_started": settings.celery_task_track_started,
        "task_time_limit": settings.celery_task_time_limit,
        "task_soft_time_limit": settings.celery_task_soft_time_limit,
        
        # Worker settings
        "worker_concurrency": settings.celery_worker_concurrency,
        "worker_prefetch_multiplier": settings.celery_worker_prefetch_multiplier,
        "worker_max_tasks_per_child": settings.celery_worker_max_tasks_per_child,
        "worker_max_memory_per_child": settings.celery_worker_max_memory_per_child,
        
        # Routing
        "task_routes": settings.celery_task_routes,
        
        # Beat schedule
        "beat_schedule": settings.celery_beat_schedule,
    }


def create_celery_app(app_name: str = "ainflue"):
    """Create and configure Celery application"""
    try:
        from celery import Celery
        
        settings = CelerySettings()
        celery_app = Celery(app_name)
        celery_app.config_from_object(get_celery_config())
        
        return celery_app
    except ImportError:
        # Celery not installed, return None
        return None


# Celery settings instance
celery_settings = CelerySettings()

class CeleryConfiguration:
    """Celery configuration manager for Ainflue platform"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.settings = celery_settings
        
    def get_config(self) -> Dict[str, Any]:
        """Get Celery configuration"""
        return get_celery_config()
    
    def create_app(self):
        """Create Celery app"""
        return create_celery_app()

__all__ = [
    "CelerySettings", 
    "CeleryConfiguration",
    "celery_settings", 
    "get_celery_config", 
    "create_celery_app"
]