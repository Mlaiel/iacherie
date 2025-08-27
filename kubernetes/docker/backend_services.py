"""
🚀 Backend Services Docker Configuration - IA-Influencer-Agent Platform
========================================================================
Expert: Backend Senior + Microservices Architect + Python Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional backend services Docker configuration for high-performance
multi-format content processing and real-time protection systems.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, field
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class BackendServicesDockerConfig:
    """Enterprise Backend Services Docker configuration"""
    
    # Container Configuration
    image_name: str = "ia-influencer/backend-services"
    image_tag: str = "2.0.0"
    container_name: str = "ia-influencer-backend"
    
    # Application Configuration
    app_port: int = 8000
    admin_port: int = 8001
    metrics_port: int = 9090
    
    # Performance Configuration
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = 1000
    max_requests_jitter: int = 100
    timeout: int = 120
    keepalive: int = 5
    
    # Environment Configuration
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    database_url: str = "postgresql://ia_user:secure_password@postgres:5432/ia_influencer"
    redis_url: str = "redis://redis:6379/0"
    elasticsearch_url: str = "http://elasticsearch:9200"
    
    # Resource Limits
    cpu_limit: str = "4000m"
    memory_limit: str = "8Gi"
    cpu_request: str = "2000m"
    memory_request: str = "4Gi"
    
    # Security Configuration
    jwt_secret_key: str = "ultra-secure-jwt-secret-key-production"
    encryption_key: str = "ultra-secure-encryption-key-32-chars"
    cors_origins: List[str] = field(default_factory=lambda: ["https://app.ia-influencer.com"])
    
    # Health Check Configuration
    health_check_enabled: bool = True
    health_check_interval: str = "30s"
    health_check_timeout: str = "10s"
    health_check_retries: int = 3
    
    # Celery Configuration
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"
    celery_workers: int = 8
    celery_max_tasks_per_child: int = 1000
    
    # File Storage Configuration
    storage_backend: str = "s3"
    s3_bucket: str = "ia-influencer-content"
    s3_region: str = "eu-central-1"
    max_upload_size: str = "500MB"
    
    # Feature Flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "ai_fingerprinting": True,
        "content_protection": True,
        "monetization_tracking": True,
        "real_time_monitoring": True,
        "advanced_analytics": True,
        "multi_tenant": True,
        "audit_logging": True,
        "rate_limiting": True
    })
    
    def generate_dockerfile(self) -> str:
        """Generate production Dockerfile for Backend Services"""
        return f"""
# IA-Influencer Backend Services - Production Docker Image
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Professional high-performance Python backend with FastAPI

# Multi-stage build for optimization
FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.image_tag}"
LABEL service="backend-services"
LABEL platform="IA-Influencer-Agent"
LABEL environment="{self.environment}"

# System dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    ca-certificates \\
    libpq-dev \\
    libffi-dev \\
    libssl-dev \\
    libsndfile1 \\
    libsndfile1-dev \\
    ffmpeg \\
    libavcodec-dev \\
    libavformat-dev \\
    libswscale-dev \\
    libavutil-dev \\
    pkg-config \\
    git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Create non-root user
RUN groupadd -g 1001 appgroup && \\
    useradd -r -u 1001 -g appgroup appuser

# Python environment setup
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Development stage
FROM base AS development
RUN pip install --upgrade pip
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Testing stage
FROM base AS testing
RUN pip install --upgrade pip
COPY requirements-test.txt .
RUN pip install -r requirements-test.txt

# Production stage
FROM base AS production

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appgroup . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/temp /app/models /app/cache && \\
    chown -R appuser:appgroup /app && \\
    chmod -R 755 /app

# Environment variables
ENV ENVIRONMENT={self.environment}
ENV LOG_LEVEL={self.log_level}
ENV APP_PORT={self.app_port}
ENV ADMIN_PORT={self.admin_port}
ENV METRICS_PORT={self.metrics_port}
ENV WORKERS={self.workers}
ENV WORKER_CLASS={self.worker_class}
ENV MAX_REQUESTS={self.max_requests}
ENV MAX_REQUESTS_JITTER={self.max_requests_jitter}
ENV TIMEOUT={self.timeout}
ENV KEEPALIVE={self.keepalive}
ENV DATABASE_URL={self.database_url}
ENV REDIS_URL={self.redis_url}
ENV ELASTICSEARCH_URL={self.elasticsearch_url}
ENV CELERY_BROKER_URL={self.celery_broker_url}
ENV CELERY_RESULT_BACKEND={self.celery_result_backend}
ENV JWT_SECRET_KEY={self.jwt_secret_key}
ENV ENCRYPTION_KEY={self.encryption_key}
ENV STORAGE_BACKEND={self.storage_backend}
ENV S3_BUCKET={self.s3_bucket}
ENV S3_REGION={self.s3_region}
ENV MAX_UPLOAD_SIZE={self.max_upload_size}

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval={self.health_check_interval} \\
           --timeout={self.health_check_timeout} \\
           --start-period=60s \\
           --retries={self.health_check_retries} \\
    CMD curl -f http://localhost:{self.app_port}/health || exit 1

# Expose ports
EXPOSE {self.app_port}
EXPOSE {self.admin_port}
EXPOSE {self.metrics_port}

# Run application
CMD ["gunicorn", \\
     "--bind", "0.0.0.0:{self.app_port}", \\
     "--workers", "{self.workers}", \\
     "--worker-class", "{self.worker_class}", \\
     "--max-requests", "{self.max_requests}", \\
     "--max-requests-jitter", "{self.max_requests_jitter}", \\
     "--timeout", "{self.timeout}", \\
     "--keepalive", "{self.keepalive}", \\
     "--log-level", "{self.log_level.lower()}", \\
     "--access-logfile", "-", \\
     "--error-logfile", "-", \\
     "main:app"]
"""

    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate docker-compose service configuration"""
        return {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": self.container_name,
            "restart": "unless-stopped",
            "ports": [
                f"{self.app_port}:{self.app_port}",
                f"{self.admin_port}:{self.admin_port}",
                f"{self.metrics_port}:{self.metrics_port}"
            ],
            "environment": {
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": self.log_level,
                "DEBUG": str(self.debug_mode).lower(),
                "APP_PORT": str(self.app_port),
                "ADMIN_PORT": str(self.admin_port),
                "METRICS_PORT": str(self.metrics_port),
                "WORKERS": str(self.workers),
                "WORKER_CLASS": self.worker_class,
                "MAX_REQUESTS": str(self.max_requests),
                "MAX_REQUESTS_JITTER": str(self.max_requests_jitter),
                "TIMEOUT": str(self.timeout),
                "KEEPALIVE": str(self.keepalive),
                "DATABASE_URL": self.database_url,
                "REDIS_URL": self.redis_url,
                "ELASTICSEARCH_URL": self.elasticsearch_url,
                "CELERY_BROKER_URL": self.celery_broker_url,
                "CELERY_RESULT_BACKEND": self.celery_result_backend,
                "CELERY_WORKERS": str(self.celery_workers),
                "CELERY_MAX_TASKS_PER_CHILD": str(self.celery_max_tasks_per_child),
                "JWT_SECRET_KEY": self.jwt_secret_key,
                "ENCRYPTION_KEY": self.encryption_key,
                "CORS_ORIGINS": ",".join(self.cors_origins),
                "STORAGE_BACKEND": self.storage_backend,
                "S3_BUCKET": self.s3_bucket,
                "S3_REGION": self.s3_region,
                "MAX_UPLOAD_SIZE": self.max_upload_size,
                **{f"FEATURE_{k.upper()}": str(v).lower() for k, v in self.features.items()}
            },
            "volumes": [
                "./logs/backend:/app/logs",
                "./uploads:/app/uploads",
                "./models:/app/models:ro",
                "./config/backend:/app/config:ro",
                "/tmp:/app/temp"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "postgres",
                "redis",
                "elasticsearch"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": self.cpu_limit,
                        "memory": self.memory_limit
                    },
                    "reservations": {
                        "cpus": self.cpu_request,
                        "memory": self.memory_request
                    }
                }
            },
            "healthcheck": {
                "test": f"curl -f http://localhost:{self.app_port}/health || exit 1",
                "interval": self.health_check_interval,
                "timeout": self.health_check_timeout,
                "retries": self.health_check_retries,
                "start_period": "60s"
            },
            "security_opt": [
                "no-new-privileges:true"
            ],
            "cap_drop": ["ALL"],
            "read_only": True,
            "tmpfs": [
                "/tmp:size=2G,mode=1777",
                "/app/temp:size=2G,mode=1777"
            ]
        }
    
    def generate_celery_worker_service(self) -> Dict[str, Any]:
        """Generate Celery worker service configuration"""
        return {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": f"{self.container_name}-worker",
            "restart": "unless-stopped",
            "command": [
                "celery",
                "--app=main.celery_app",
                "worker",
                f"--loglevel={self.log_level.lower()}",
                f"--concurrency={self.celery_workers}",
                f"--max-tasks-per-child={self.celery_max_tasks_per_child}",
                "--time-limit=7200",
                "--soft-time-limit=3600",
                "--prefetch-multiplier=1",
                "--optimization=fair"
            ],
            "environment": {
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": self.log_level,
                "DATABASE_URL": self.database_url,
                "REDIS_URL": self.redis_url,
                "ELASTICSEARCH_URL": self.elasticsearch_url,
                "CELERY_BROKER_URL": self.celery_broker_url,
                "CELERY_RESULT_BACKEND": self.celery_result_backend,
                "CELERY_WORKERS": str(self.celery_workers),
                "CELERY_MAX_TASKS_PER_CHILD": str(self.celery_max_tasks_per_child),
                **{f"FEATURE_{k.upper()}": str(v).lower() for k, v in self.features.items()}
            },
            "volumes": [
                "./logs/celery:/app/logs",
                "./uploads:/app/uploads",
                "./models:/app/models:ro",
                "./config/backend:/app/config:ro",
                "/tmp:/app/temp"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "postgres",
                "redis",
                "backend-services"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "2000m",
                        "memory": "4Gi"
                    },
                    "reservations": {
                        "cpus": "1000m",
                        "memory": "2Gi"
                    }
                }
            },
            "security_opt": [
                "no-new-privileges:true"
            ],
            "cap_drop": ["ALL"],
            "read_only": True,
            "tmpfs": [
                "/tmp:size=2G,mode=1777",
                "/app/temp:size=2G,mode=1777"
            ]
        }
    
    def generate_celery_beat_service(self) -> Dict[str, Any]:
        """Generate Celery beat scheduler service configuration"""
        return {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": f"{self.container_name}-scheduler",
            "restart": "unless-stopped",
            "command": [
                "celery",
                "--app=main.celery_app",
                "beat",
                f"--loglevel={self.log_level.lower()}",
                "--schedule=/app/celerybeat-schedule",
                "--pidfile=/app/celerybeat.pid"
            ],
            "environment": {
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": self.log_level,
                "DATABASE_URL": self.database_url,
                "REDIS_URL": self.redis_url,
                "CELERY_BROKER_URL": self.celery_broker_url,
                "CELERY_RESULT_BACKEND": self.celery_result_backend
            },
            "volumes": [
                "./logs/celery:/app/logs",
                "./config/backend:/app/config:ro",
                "celery_schedule:/app"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "postgres",
                "redis",
                "backend-services"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "500m",
                        "memory": "1Gi"
                    },
                    "reservations": {
                        "cpus": "200m",
                        "memory": "512Mi"
                    }
                }
            },
            "security_opt": [
                "no-new-privileges:true"
            ],
            "cap_drop": ["ALL"]
        }
    
    def generate_flower_monitoring_service(self) -> Dict[str, Any]:
        """Generate Flower monitoring service configuration"""
        return {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": f"{self.container_name}-flower",
            "restart": "unless-stopped",
            "ports": ["5555:5555"],
            "command": [
                "celery",
                "--app=main.celery_app",
                "flower",
                "--port=5555",
                "--broker=redis://redis:6379/1",
                "--basic_auth=admin:secure_flower_password"
            ],
            "environment": {
                "CELERY_BROKER_URL": self.celery_broker_url,
                "CELERY_RESULT_BACKEND": self.celery_result_backend
            },
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "redis",
                "backend-services-worker"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "500m",
                        "memory": "512Mi"
                    }
                }
            }
        }
    
    def generate_requirements_txt(self) -> str:
        """Generate production requirements.txt"""
        return """
# IA-Influencer Backend Services - Production Dependencies
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Core Framework
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
starlette==0.27.0

# Database & Storage
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.13.1
sqlalchemy[asyncio]==2.0.23
redis[hiredis]==5.0.1
elasticsearch[async]==8.11.0

# Task Queue
celery[redis]==5.3.4
flower==2.0.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
cryptography==41.0.8

# HTTP & Networking
httpx==0.25.2
aiohttp==3.9.1
websockets==12.0

# AI & ML
torch==2.1.1
transformers==4.36.0
scikit-learn==1.3.2
numpy==1.25.2
pandas==2.1.4

# Audio Processing
librosa==0.10.1
soundfile==0.12.1
pyaudio==0.2.11
chromaprint==0.5

# Image Processing
pillow==10.1.0
opencv-python==4.8.1.78
imagehash==4.3.1

# Video Processing
moviepy==1.0.3
ffmpeg-python==0.2.0

# Text Processing
spacy==3.7.2
nltk==3.8.1
textdistance==4.6.0

# Monitoring & Logging
prometheus-client==0.19.0
structlog==23.2.0
sentry-sdk[fastapi]==1.38.0

# Configuration & Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
click==8.1.7
typer==0.9.0

# Development Tools
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# AWS & Cloud
boto3==1.34.0
botocore==1.34.0

# Validation & Serialization
marshmallow==3.20.1
jsonschema==4.20.0

# Caching
aiocache==0.12.2

# Rate Limiting
slowapi==0.1.9

# Background Tasks
dramatiq[redis]==1.15.0

# File Processing
python-magic==0.4.27
python-docx==1.1.0
pypdf2==3.0.1

# Internationalization
babel==2.13.1

# Performance
orjson==3.9.10
msgpack==1.0.7
"""
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all configuration files to output directory"""
        import os
        from pathlib import Path
        
        config_dir = Path(output_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Dockerfile
        dockerfile_path = config_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(self.generate_dockerfile())
        files_created.append(str(dockerfile_path))
        
        # Save requirements.txt
        requirements_path = config_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(self.generate_requirements_txt())
        files_created.append(str(requirements_path))
        
        # Save docker-compose service config
        compose_config_path = config_dir / "docker-compose.backend.yml"
        service_config = {
            "version": "3.8",
            "services": {
                "backend-services": self.generate_docker_compose_service(),
                "backend-services-worker": self.generate_celery_worker_service(),
                "backend-services-scheduler": self.generate_celery_beat_service(),
                "backend-services-flower": self.generate_flower_monitoring_service()
            },
            "volumes": {
                "celery_schedule": {}
            }
        }
        with open(compose_config_path, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False)
        files_created.append(str(compose_config_path))
        
        logger.info(f"✅ Backend Services configuration files saved: {files_created}")
        return files_created
