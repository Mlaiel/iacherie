"""⚡ Worker Cluster Docker Configuration - IA-Influencer-Agent Platform
=====================================================================
Expert: Backend Senior + DevOps Engineer + Scalability Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Docker configuration for distributed worker cluster
supporting high-performance async task processing, queue management,
and auto-scaling for IA-Influencer multi-format content processing.
"""

from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class WorkerClusterDockerConfig:
    """
Enterprise Worker Cluster Docker Configuration"""
    
    # Image Configuration
    image_name: str = "ia-influencer/worker-cluster"
    image_tag: str = "2.0.0"
    registry_url: str = "registry.ia-influencer.com"
    
    # Cluster Configuration
    worker_replicas: int = 8
    beat_replicas: int = 1
    flower_replicas: int = 1
    
    # Container Configuration
    base_container_name: str = "ia-influencer-worker"
    restart_policy: str = "unless-stopped"
    network_mode: str = "ia-influencer-network"
    
    # Resource Limits per Worker
    worker_cpu_limit: str = "2000m"
    worker_memory_limit: str = "4Gi"
    worker_cpu_reservation: str = "500m"
    worker_memory_reservation: str = "1Gi"
    
    # Queue Configuration
    queues: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "default": {
            "concurrency": 4,
            "max_tasks_per_child": 1000,
            "task_time_limit": 3600,
            "task_soft_time_limit": 3000
        },
        "ai_processing": {
            "concurrency": 2,
            "max_tasks_per_child": 100,
            "task_time_limit": 7200,
            "task_soft_time_limit": 6000
        },
        "fingerprinting": {
            "concurrency": 3,
            "max_tasks_per_child": 500,
            "task_time_limit": 1800,
            "task_soft_time_limit": 1500
        },
        "content_protection": {
            "concurrency": 6,
            "max_tasks_per_child": 2000,
            "task_time_limit": 900,
            "task_soft_time_limit": 600
        },
        "monetization": {
            "concurrency": 4,
            "max_tasks_per_child": 1500,
            "task_time_limit": 1200,
            "task_soft_time_limit": 900
        },
        "notifications": {
            "concurrency": 8,
            "max_tasks_per_child": 5000,
            "task_time_limit": 300,
            "task_soft_time_limit": 240
        }
    })
    
    # Environment Variables
    environment: Dict[str, str] = field(default_factory=lambda: {
        "CELERY_BROKER_URL": "redis://redis:6379/0",
        "CELERY_RESULT_BACKEND": "redis://redis:6379/1",
        "CELERY_TASK_SERIALIZER": "json",
        "CELERY_RESULT_SERIALIZER": "json",
        "CELERY_ACCEPT_CONTENT": "json",
        "CELERY_TIMEZONE": "UTC",
        "CELERY_ENABLE_UTC": "true",
        "CELERY_WORKER_HIJACK_ROOT_LOGGER": "false",
        "CELERY_WORKER_LOG_FORMAT": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        "CELERY_WORKER_TASK_LOG_FORMAT": "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
        "CELERY_WORKER_PREFETCH_MULTIPLIER": "4",
        "CELERY_TASK_ACKS_LATE": "true",
        "CELERY_WORKER_DISABLE_RATE_LIMITS": "false",
        "CELERY_TASK_REJECT_ON_WORKER_LOST": "true",
        "CELERY_TASK_IGNORE_RESULT": "false",
        "CELERY_RESULT_EXPIRES": "3600",
        "CELERY_TASK_STORE_EAGER_RESULT": "true"
    })
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for worker cluster"""
        return f"""# Multi-stage build for Worker Cluster
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    gcc \\
    g++ \\
    make \\
    pkg-config \\
    libssl-dev \\
    libffi-dev \\
    python3-dev \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements/worker-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \\
    pip install --no-cache-dir -r worker-requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    procps \\
    htop \\
    net-tools \\
    ffmpeg \\
    imagemagick \\
    ghostscript \\
    poppler-utils \\
    tesseract-ocr \\
    tesseract-ocr-fra \\
    tesseract-ocr-deu \\
    tesseract-ocr-spa \\
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create worker user
RUN groupadd -r worker && useradd -r -g worker worker

# Create directories
RUN mkdir -p /app/workers \\
             /app/tasks \\
             /app/logs/workers \\
             /app/config/workers \\
             /app/data/temp \\
             /app/data/processing \\
             /app/data/cache \\
             /var/log/celery

# Copy application code
COPY backend/ai_agents/ /app/ai_agents/
COPY backend/business/ /app/business/
COPY backend/ml/ /app/ml/
COPY backend/utils/ /app/utils/
COPY backend/core/ /app/core/
COPY backend/workers/ /app/workers/
COPY backend/tasks/ /app/tasks/

# Copy worker configurations
COPY backend/deployment/docker/config/workers/ /app/config/workers/
COPY backend/deployment/docker/scripts/workers/ /app/scripts/

# Set permissions
RUN chown -R worker:worker /app/ /var/log/celery
RUN chmod +x /app/scripts/*.sh

# Install ML models and dependencies
COPY scripts/workers/download-models.sh /tmp/
RUN chmod +x /tmp/download-models.sh && /tmp/download-models.sh

# Health check script
COPY scripts/workers/health-check.sh /app/scripts/
RUN chmod +x /app/scripts/health-check.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD /app/scripts/health-check.sh || exit 1

# Switch to worker user
USER worker

# Working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \\
    PYTHONUNBUFFERED=1 \\
    CELERY_CONFIG_MODULE=workers.config \\
    WORKER_LOG_LEVEL=INFO \\
    C_FORCE_ROOT=1

# Entry point
COPY scripts/workers/entrypoint.sh /app/scripts/
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["celery", "worker", "-A", "workers.celery_app", "--loglevel=info"]
"""
    def generate_docker_compose_services(self) -> Dict[str, Any]:
        """
Generate Docker Compose services for worker cluster"""
        services = {}
        
        # Generate worker services for each queue
        for queue_name, queue_config in self.queues.items():
            service_name = f"worker-{queue_name.replace('_', '-')}"
            
            services[service_name] = {
                "image": f"{self.registry_url}/{self.image_name}:{self.image_tag}",
                "container_name": f"{self.base_container_name}-{queue_name.replace('_', '-')}",
                "restart": self.restart_policy,
                "environment": {
                    **self.environment,
                    "CELERY_QUEUES": queue_name,
                    "CELERY_WORKER_CONCURRENCY": str(queue_config["concurrency"]),
                    "CELERY_WORKER_MAX_TASKS_PER_CHILD": str(queue_config["max_tasks_per_child"]),
                    "CELERY_TASK_TIME_LIMIT": str(queue_config["task_time_limit"]),
                    "CELERY_TASK_SOFT_TIME_LIMIT": str(queue_config["task_soft_time_limit"]),
                    "WORKER_QUEUE_NAME": queue_name
                },
                "volumes": [
                    "./config/workers:/app/config/workers:ro",
                    "./logs/workers:/app/logs/workers",
                    "worker_data:/app/data",
                    "model_cache:/app/models",
                    "temp_storage:/app/data/temp",
                    "processing_cache:/app/data/processing"
                ],
                "networks": [self.network_mode],
                "depends_on": [
                    "redis",
                    "postgres-master"
                ],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": self.worker_cpu_limit,
                            "memory": self.worker_memory_limit
                        },
                        "reservations": {
                            "cpus": self.worker_cpu_reservation,
                            "memory": self.worker_memory_reservation
                        }
                    },
                    "replicas": self.worker_replicas if queue_name == "default" else 2
                },
                "command": [
                    "celery", "worker",
                    "-A", "workers.celery_app",
                    "-Q", queue_name,
                    f"--concurrency={queue_config['concurrency']}",
                    f"--max-tasks-per-child={queue_config['max_tasks_per_child']}",
                    f"--time-limit={queue_config['task_time_limit']}",
                    f"--soft-time-limit={queue_config['task_soft_time_limit']}",
                    "--loglevel=info",
                    f"--hostname={queue_name}@%h"
                ],
                "healthcheck": {
                    "test": "/app/scripts/health-check.sh",
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "60s"
                }
            }
        
        # Celery Beat (Scheduler) Service
        services["celery-beat"] = {
            "image": f"{self.registry_url}/{self.image_name}:{self.image_tag}",
            "container_name": f"{self.base_container_name}-beat",
            "restart": self.restart_policy,
            "environment": self.environment,
            "volumes": [
                "./config/workers:/app/config/workers:ro",
                "./logs/workers:/app/logs/workers",
                "celery_schedule:/app/data/schedule"
            ],
            "networks": [self.network_mode],
            "depends_on": [
                "redis",
                "postgres-master"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "500m",
                        "memory": "1Gi"
                    },
                    "reservations": {
                        "cpus": "250m",
                        "memory": "512Mi"
                    }
                },
                "replicas": self.beat_replicas
            },
            "command": [
                "celery", "beat",
                "-A", "workers.celery_app",
                "--loglevel=info",
                "--schedule=/app/data/schedule/celerybeat-schedule",
                "--pidfile=/app/data/schedule/celerybeat.pid"
            ],
            "healthcheck": {
                "test": "pgrep -f 'celery beat' || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
        
        # Flower Monitoring Service
        services["celery-flower"] = {
            "image": f"{self.registry_url}/{self.image_name}:{self.image_tag}",
            "container_name": f"{self.base_container_name}-flower",
            "restart": self.restart_policy,
            "ports": ["5555:5555"],
            "environment": {
                **self.environment,
                "FLOWER_PORT": "5555",
                "FLOWER_BASIC_AUTH": "admin:ultra_secure_flower_password_2024"
            },
            "volumes": [
                "./config/workers:/app/config/workers:ro",
                "./logs/workers:/app/logs/workers"
            ],
            "networks": [self.network_mode],
            "depends_on": [
                "redis"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "500m",
                        "memory": "1Gi"
                    }
                },
                "replicas": self.flower_replicas
            },
            "command": [
                "celery", "flower",
                "-A", "workers.celery_app",
                "--port=5555",
                "--broker=redis://redis:6379/0",
                "--basic_auth=admin:ultra_secure_flower_password_2024"
            ],
            "healthcheck": {
                "test": "curl -f http://localhost:5555/api/workers || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
        
        # Worker Autoscaler Service
        services["worker-autoscaler"] = {
            "image": f"{self.registry_url}/{self.image_name}:{self.image_tag}",
            "container_name": f"{self.base_container_name}-autoscaler",
            "restart": self.restart_policy,
            "environment": {
                **self.environment,
                "AUTOSCALER_ENABLED": "true",
                "AUTOSCALER_INTERVAL": "60",
                "AUTOSCALER_MAX_WORKERS": "20",
                "AUTOSCALER_MIN_WORKERS": "2",
                "AUTOSCALER_TARGET_QUEUE_LENGTH": "10"
            },
            "volumes": [
                "./config/workers:/app/config/workers:ro",
                "./logs/workers:/app/logs/workers",
                "/var/run/docker.sock:/var/run/docker.sock:ro"
            ],
            "networks": [self.network_mode],
            "depends_on": [
                "redis",
                "celery-flower"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "500m",
                        "memory": "512Mi"
                    }
                }
            },
            "command": [
                "python", "-m", "workers.autoscaler"
            ]
        }
        
        return services
    
    def generate_worker_requirements(self) -> str:
        """Generate worker requirements.txt"""
        return """# Worker Cluster Requirements
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Core async framework
celery[redis]==5.3.4
redis==5.0.1
kombu==5.3.4
billiard==4.1.0

# Task monitoring
flower==2.0.1
celery-progress==0.3.2

# Core framework
fastapi==0.104.1
pydantic==2.5.0
pydantic-settings==2.1.0

# Database connectivity
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.1
asyncpg==0.29.0

# ML and AI frameworks
torch==2.1.1
torchvision==0.16.1
torchaudio==0.16.1
transformers==4.36.0
sentence-transformers==2.2.2
huggingface-hub==0.19.4
accelerate==0.25.0

# Audio processing
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1
essentia==2.1b6.dev1110
chromaprint==1.5.1
pyacoustid==1.2.2

# Image processing  
Pillow==10.1.0
opencv-python==4.8.1.78
imageio==2.33.1
scikit-image==0.22.0

# Video processing
moviepy==1.0.3
ffmpeg-python==0.2.0

# Text processing
nltk==3.8.1
spacy==3.7.2
textblob==0.17.1
langdetect==1.0.9

# Document processing
python-docx==1.1.0
PyPDF2==3.0.1
python-pptx==0.6.23
openpyxl==3.1.2

# Vector similarity
faiss-cpu==1.7.4
qdrant-client==1.7.0
pinecone-client==2.2.4

# Numerical computing
numpy==1.24.4
pandas==2.1.4
scipy==1.11.4
scikit-learn==1.3.2

# HTTP clients
httpx==0.25.2
requests==2.31.0
aiohttp==3.9.1

# File operations
aiofiles==23.2.1
python-magic==0.4.27
watchdog==3.0.0

# Utilities
python-dateutil==2.8.2
python-decouple==3.8
schedule==1.2.0
click==8.1.7
rich==13.7.0
typer==0.9.0

# Monitoring and logging
structlog==23.2.0
python-json-logger==2.0.7
prometheus-client==0.19.0
psutil==5.9.6

# Configuration
pyyaml==6.0.1
toml==0.10.2
python-dotenv==1.0.0

# Compression
lz4==4.3.2
zstandard==0.22.0

# Progress tracking
tqdm==4.66.1
alive-progress==3.1.5

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-celery==0.0.0a1
"""
    def generate_worker_config_files(self) -> Dict[str, str]:
        """
Generate worker configuration files"""
        configs = {}
        
        # Celery configuration
        configs["celery_config.py"] = f"""# Celery Configuration for IA-Influencer Workers
# Creator: Fahed Mlaiel <mlaiel@live.de>

from kombu import Queue, Exchange
from celery import Celery
import os

# Broker settings
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Worker settings
worker_hijack_root_logger = False
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# Task execution settings
task_acks_late = True
task_reject_on_worker_lost = True
task_ignore_result = False
task_store_eager_result = True

# Result settings
result_expires = 3600
result_cache_max = 10000

# Queue definitions
task_default_queue = 'default'
task_default_exchange_type = 'direct'
task_default_routing_key = 'default'

# Define exchanges
default_exchange = Exchange('default', type='direct')
ai_exchange = Exchange('ai_processing', type='direct')
fingerprint_exchange = Exchange('fingerprinting', type='direct')
protection_exchange = Exchange('content_protection', type='direct')
monetization_exchange = Exchange('monetization', type='direct')
notification_exchange = Exchange('notifications', type='direct')

# Define queues
task_routes = {{
    # AI Processing tasks
    'workers.ai.audio_analysis': {{'queue': 'ai_processing'}},
    'workers.ai.content_generation': {{'queue': 'ai_processing'}},
    'workers.ai.recommendation_engine': {{'queue': 'ai_processing'}},
    'workers.ai.sentiment_analysis': {{'queue': 'ai_processing'}},
    
    # Fingerprinting tasks
    'workers.fingerprinting.audio_fingerprint': {{'queue': 'fingerprinting'}},
    'workers.fingerprinting.video_fingerprint': {{'queue': 'fingerprinting'}},
    'workers.fingerprinting.image_fingerprint': {{'queue': 'fingerprinting'}},
    'workers.fingerprinting.text_fingerprint': {{'queue': 'fingerprinting'}},
    'workers.fingerprinting.similarity_search': {{'queue': 'fingerprinting'}},
    
    # Content Protection tasks
    'workers.protection.crawl_platform': {{'queue': 'content_protection'}},
    'workers.protection.detect_violation': {{'queue': 'content_protection'}},
    'workers.protection.generate_takedown': {{'queue': 'content_protection'}},
    'workers.protection.monitor_content': {{'queue': 'content_protection'}},
    
    # Monetization tasks
    'workers.monetization.calculate_revenue': {{'queue': 'monetization'}},
    'workers.monetization.process_payment': {{'queue': 'monetization'}},
    'workers.monetization.update_analytics': {{'queue': 'monetization'}},
    'workers.monetization.generate_report': {{'queue': 'monetization'}},
    
    # Notification tasks
    'workers.notifications.send_email': {{'queue': 'notifications'}},
    'workers.notifications.send_webhook': {{'queue': 'notifications'}},
    'workers.notifications.send_push': {{'queue': 'notifications'}},
    'workers.notifications.send_sms': {{'queue': 'notifications'}},
}}

# Queue configuration
task_queues = (
    Queue('default', default_exchange, routing_key='default', 
          queue_arguments={{'x-max-priority': 10}}),
    
    Queue('ai_processing', ai_exchange, routing_key='ai_processing',
          queue_arguments={{'x-max-priority': 8, 'x-message-ttl': 7200000}}),
    
    Queue('fingerprinting', fingerprint_exchange, routing_key='fingerprinting',
          queue_arguments={{'x-max-priority': 9, 'x-message-ttl': 1800000}}),
    
    Queue('content_protection', protection_exchange, routing_key='content_protection',
          queue_arguments={{'x-max-priority': 7, 'x-message-ttl': 900000}}),
    
    Queue('monetization', monetization_exchange, routing_key='monetization',
          queue_arguments={{'x-max-priority': 6, 'x-message-ttl': 1200000}}),
    
    Queue('notifications', notification_exchange, routing_key='notifications',
          queue_arguments={{'x-max-priority': 5, 'x-message-ttl': 300000}}),
)

# Beat schedule for periodic tasks
beat_schedule = {{
    'update-ai-models': {{
        'task': 'workers.ai.update_models',
        'schedule': 86400.0,  # Daily
        'options': {{'queue': 'ai_processing'}}
    }},
    'fingerprint-batch-processing': {{
        'task': 'workers.fingerprinting.batch_process',
        'schedule': 3600.0,  # Hourly
        'options': {{'queue': 'fingerprinting'}}
    }},
    'crawl-platforms': {{
        'task': 'workers.protection.crawl_all_platforms',
        'schedule': 1800.0,  # Every 30 minutes
        'options': {{'queue': 'content_protection'}}
    }},
    'generate-revenue-reports': {{
        'task': 'workers.monetization.daily_revenue_report',
        'schedule': 86400.0,  # Daily
        'options': {{'queue': 'monetization'}}
    }},
    'cleanup-expired-tasks': {{
        'task': 'workers.maintenance.cleanup_expired',
        'schedule': 3600.0,  # Hourly
        'options': {{'queue': 'default'}}
    }},
    'health-check-services': {{
        'task': 'workers.monitoring.health_check',
        'schedule': 300.0,  # Every 5 minutes
        'options': {{'queue': 'default'}}
    }}
}}

# Monitoring settings
worker_send_task_events = True
task_send_sent_event = True

# Security settings
worker_hijack_root_logger = False
worker_log_color = False

# Optimization settings
broker_connection_retry_on_startup = True
broker_connection_retry = True
broker_connection_max_retries = 100
"""
        # Autoscaler configuration
        configs["autoscaler_config.py"] = """# Worker Autoscaler Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

import os
from typing import Dict, Any

# Autoscaler settings
AUTOSCALER_CONFIG: Dict[str, Any] = {
    'enabled': os.getenv('AUTOSCALER_ENABLED', 'true').lower() == 'true',
    'interval': int(os.getenv('AUTOSCALER_INTERVAL', '60')),
    'max_workers': int(os.getenv('AUTOSCALER_MAX_WORKERS', '20')),
    'min_workers': int(os.getenv('AUTOSCALER_MIN_WORKERS', '2')),
    'target_queue_length': int(os.getenv('AUTOSCALER_TARGET_QUEUE_LENGTH', '10')),
    
    # Queue-specific scaling rules
    'queue_rules': {
        'default': {
            'min_workers': 2,
            'max_workers': 8,
            'scale_up_threshold': 20,
            'scale_down_threshold': 5,
            'scale_up_cooldown': 300,
            'scale_down_cooldown': 600
        },
        'ai_processing': {
            'min_workers': 1,
            'max_workers': 4,
            'scale_up_threshold': 5,
            'scale_down_threshold': 1,
            'scale_up_cooldown': 600,
            'scale_down_cooldown': 1200
        },
        'fingerprinting': {
            'min_workers': 2,
            'max_workers': 6,
            'scale_up_threshold': 10,
            'scale_down_threshold': 2,
            'scale_up_cooldown': 300,
            'scale_down_cooldown': 600
        },
        'content_protection': {
            'min_workers': 3,
            'max_workers': 10,
            'scale_up_threshold': 15,
            'scale_down_threshold': 3,
            'scale_up_cooldown': 180,
            'scale_down_cooldown': 300
        },
        'monetization': {
            'min_workers': 1,
            'max_workers': 4,
            'scale_up_threshold': 8,
            'scale_down_threshold': 2,
            'scale_up_cooldown': 300,
            'scale_down_cooldown': 600
        },
        'notifications': {
            'min_workers': 2,
            'max_workers': 12,
            'scale_up_threshold': 25,
            'scale_down_threshold': 5,
            'scale_up_cooldown': 120,
            'scale_down_cooldown': 240
        }
    },
    
    # Resource limits for new workers
    'resource_limits': {
        'cpu_limit': '2000m',
        'memory_limit': '4Gi',
        'cpu_request': '500m',
        'memory_request': '1Gi'
    },
    
    # Monitoring settings
    'monitoring': {
        'metrics_interval': 30,
        'health_check_interval': 60,
        'log_level': 'INFO'
    }
}
"""
        return configs
    
    def generate_scripts(self) -> Dict[str, str]:
        """
Generate worker scripts"""
        scripts = {}
        
        # Entrypoint script
        scripts["entrypoint.sh"] = """#!/bin/bash
# Worker Cluster Entrypoint Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "⚡ Starting IA-Influencer Worker Cluster..."

# Initialize directories
mkdir -p /app/logs/workers/{default,ai,fingerprinting,protection,monetization,notifications}
mkdir -p /app/data/{temp,processing,cache,schedule}
mkdir -p /var/log/celery

# Set proper permissions
chown -R worker:worker /app/logs/workers /app/data /var/log/celery

# Wait for dependencies
echo "⏳ Waiting for dependencies..."
wait-for-it redis:6379 --timeout=60 --strict
wait-for-it postgres-master:5432 --timeout=60 --strict

# Initialize worker environment
echo "🔧 Initializing worker environment..."
python -c "from workers.setup import initialize_worker_env; initialize_worker_env()"

# Download and cache ML models
echo "🤖 Downloading ML models..."
python -m workers.models.downloader

# Start worker monitoring
echo "📊 Starting worker monitoring..."
python -m workers.monitoring &

# Clear any stale celery state
echo "🧹 Clearing stale celery state..."
celery -A workers.celery_app purge -f || true

# Start the appropriate service based on command
if [ "$1" = "beat" ]; then
    echo "⏰ Starting Celery Beat scheduler..."
    exec celery -A workers.celery_app beat --loglevel=info --schedule=/app/data/schedule/celerybeat-schedule --pidfile=/app/data/schedule/celerybeat.pid
elif [ "$1" = "flower" ]; then
    echo "🌸 Starting Celery Flower monitoring..."
    exec celery -A workers.celery_app flower --port=5555 --broker=redis://redis:6379/0
elif [ "$1" = "autoscaler" ]; then
    echo "📈 Starting Worker Autoscaler..."
    exec python -m workers.autoscaler
else
    echo "👷 Starting Celery Worker..."
    exec "$@"
fi
"""
        # Health check script
        scripts["health-check.sh"] = """#!/bin/bash
# Worker Health Check Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Check if celery worker is running
if ! pgrep -f "celery worker" > /dev/null; then
    echo "❌ Celery worker process not found"
    exit 1
fi

# Check Redis connection
if ! python -c "import redis; r = redis.Redis(host='redis', port=6379, db=0); r.ping()" 2>/dev/null; then
    echo "❌ Cannot connect to Redis"
    exit 1
fi

# Check PostgreSQL connection
if ! python -c "import psycopg2; psycopg2.connect('host=postgres-master port=5432 dbname=ia_influencer user=ia_user password=${POSTGRES_PASSWORD}')" 2>/dev/null; then
    echo "❌ Cannot connect to PostgreSQL"
    exit 1
fi

# Check worker queue status
QUEUE_NAME=${WORKER_QUEUE_NAME:-default}
QUEUE_LENGTH=$(python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
print(r.llen('$QUEUE_NAME'))
" 2>/dev/null || echo "0")

if [ "$QUEUE_LENGTH" -gt 1000 ]; then
    echo "⚠️  Queue $QUEUE_NAME has $QUEUE_LENGTH pending tasks"
    exit 1
fi

# Check memory usage
MEMORY_USAGE=$(python -c "
import psutil
mem = psutil.virtual_memory()
print(mem.percent)
" 2>/dev/null || echo "0")

if [ "$(echo "$MEMORY_USAGE > 90" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
    echo "⚠️  High memory usage: ${MEMORY_USAGE}%"
    exit 1
fi

echo "✅ Worker health check passed"
exit 0
"""
        # Model downloader script
        scripts["download-models.sh"] = """#!/bin/bash
# ML Models Downloader Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "🤖 Downloading ML models for IA-Influencer workers..."

# Create models directory
mkdir -p /app/models/{text,audio,image,video}

# Download text models
echo "📝 Downloading text processing models..."
python -c "
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer

# Download BERT for text analysis
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')
tokenizer.save_pretrained('/app/models/text/bert-base-uncased')
model.save_pretrained('/app/models/text/bert-base-uncased')

# Download sentence transformers
st_model = SentenceTransformer('all-MiniLM-L6-v2')
st_model.save('/app/models/text/sentence-transformers')

print('✅ Text models downloaded')
"

# Download audio models
echo "🎵 Downloading audio processing models..."
python -c "
import librosa
import essentia.standard as es

# Download audio analysis models (these are typically downloaded on first use)
print('✅ Audio models ready')
"

# Download image models
echo "🖼️ Downloading image processing models..."
python -c "
from transformers import CLIPProcessor, CLIPModel

# Download CLIP for image analysis
processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
processor.save_pretrained('/app/models/image/clip-vit-base-patch32')
model.save_pretrained('/app/models/image/clip-vit-base-patch32')

print('✅ Image models downloaded')
"

# Set proper permissions
chown -R worker:worker /app/models/

echo "✅ All ML models downloaded successfully!"
"""
        return scripts
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """
Save all worker cluster configuration files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Dockerfile
        dockerfile_path = output_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(self.generate_dockerfile())
        files_created.append(str(dockerfile_path))
        
        # Save requirements
        requirements_path = output_path / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(self.generate_worker_requirements())
        files_created.append(str(requirements_path))
        
        # Save configuration files
        config_dir = output_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        for filename, content in self.generate_worker_config_files().items():
            config_path = config_dir / filename
            with open(config_path, 'w') as f:
                f.write(content)
            files_created.append(str(config_path))
        
        # Save scripts
        scripts_dir = output_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script_name, script_content in self.generate_scripts().items():
            script_path = scripts_dir / script_name
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)
            files_created.append(str(script_path))
        
        logger.info(f"✅ Worker cluster configuration saved: {len(files_created)} files")
        return files_created
