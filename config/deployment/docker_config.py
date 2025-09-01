"""Docker Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional Docker containerization and orchestration configuration
for multi-format content protection and AI-powered creator monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json


@dataclass
class DockerImageConfig:
    """
Docker image configuration for specific services"""
    name: str
    tag: str
    registry: str
    dockerfile_path: str
    build_context: str
    build_args: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    platforms: List[str] = field(default_factory=lambda: ["linux/amd64", "linux/arm64"])


@dataclass
class DockerServiceConfig:
    """Docker service configuration for compose"""
    image: str
    container_name: str
    ports: List[str] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    healthcheck: Optional[Dict[str, Any]] = None
    deploy: Optional[Dict[str, Any]] = None


class DockerConfig:
    """
    Professional Docker configuration manager for IA-Influencer Agent Platform.
    
    Handles containerization for:
    - AI processing microservices (audio, video, image, text fingerprinting)
    - Content protection services with ML models
    - Multi-database clusters (PostgreSQL, Redis, MongoDB)
    - Revenue tracking and monetization engines
    - Web crawlers and monitoring services
    - Real-time processing pipelines
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.registry_url = self._get_registry_url()
        self.base_images = self._get_base_images()
        
    def _get_registry_url(self) -> str:
        """Get container registry URL based on environment"""
        registry_map = {
            "development": "localhost:5000",
            "staging": "registry.staging.ia-influencer.com",
            "production": "registry.ia-influencer.com"
        }
        return registry_map.get(self.environment, "localhost:5000")
    
    def _get_base_images(self) -> Dict[str, str]:
        """Define base images for different service types"""
        return {
            "python_ai": "python:3.11-slim-bullseye",
            "python_ml": "tensorflow/tensorflow:2.13.0-gpu",
            "nodejs": "node:18-alpine",
            "nginx": "nginx:1.25-alpine",
            "redis": "redis:7.2-alpine",
            "postgres": "postgres:15.4-alpine",
            "mongodb": "mongo:7.0-jammy",
            "elasticsearch": "docker.elastic.co/elasticsearch/elasticsearch:8.9.0"
        }
    
    def get_main_api_image_config(self) -> DockerImageConfig:
        """Main FastAPI application image configuration"""
        return DockerImageConfig(
            name=f"{self.project_name}-api",
            tag=f"latest-{self.environment}",
            registry=self.registry_url,
            dockerfile_path="./docker/api/Dockerfile",
            build_context=".",
            build_args={
                "PYTHON_VERSION": "3.11",
                "ENVIRONMENT": self.environment,
                "BUILD_DATE": "${BUILD_DATE}",
                "VCS_REF": "${VCS_REF}"
            },
            labels={
                "maintainer": "Fahed Mlaiel <mlaiel@live.de>",
                "project": "IA-Influencer Agent",
                "component": "main-api",
                "environment": self.environment
            }
        )
    
    def get_ai_fingerprinting_image_config(self) -> DockerImageConfig:
        """AI Fingerprinting service image configuration"""
        return DockerImageConfig(
            name=f"{self.project_name}-ai-fingerprinting",
            tag=f"latest-{self.environment}",
            registry=self.registry_url,
            dockerfile_path="./docker/ai-fingerprinting/Dockerfile",
            build_context=".",
            build_args={
                "TENSORFLOW_VERSION": "2.13.0",
                "PYTORCH_VERSION": "2.0.1",
                "ENVIRONMENT": self.environment
            },
            labels={
                "maintainer": "Fahed Mlaiel <mlaiel@live.de>",
                "project": "IA-Influencer Agent",
                "component": "ai-fingerprinting",
                "gpu-required": "true"
            }
        )
    
    def get_content_protection_image_config(self) -> DockerImageConfig:
        """Content Protection service image configuration"""
        return DockerImageConfig(
            name=f"{self.project_name}-content-protection",
            tag=f"latest-{self.environment}",
            registry=self.registry_url,
            dockerfile_path="./docker/content-protection/Dockerfile",
            build_context=".",
            build_args={
                "OPENCV_VERSION": "4.8.0",
                "FFMPEG_VERSION": "6.0",
                "ENVIRONMENT": self.environment
            },
            labels={
                "maintainer": "Fahed Mlaiel <mlaiel@live.de>",
                "project": "IA-Influencer Agent",
                "component": "content-protection",
                "media-processing": "true"
            }
        )
    
    def get_monetization_engine_image_config(self) -> DockerImageConfig:
        """Monetization Engine service image configuration"""
        return DockerImageConfig(
            name=f"{self.project_name}-monetization",
            tag=f"latest-{self.environment}",
            registry=self.registry_url,
            dockerfile_path="./docker/monetization/Dockerfile",
            build_context=".",
            build_args={
                "ENVIRONMENT": self.environment,
                "PAYMENT_APIS": "stripe,paypal,wise"
            },
            labels={
                "maintainer": "Fahed Mlaiel <mlaiel@live.de>",
                "project": "IA-Influencer Agent",
                "component": "monetization-engine",
                "payment-processing": "true"
            }
        )
    
    def get_web_crawlers_image_config(self) -> DockerImageConfig:
        """Web Crawlers service image configuration"""
        return DockerImageConfig(
            name=f"{self.project_name}-web-crawlers",
            tag=f"latest-{self.environment}",
            registry=self.registry_url,
            dockerfile_path="./docker/crawlers/Dockerfile",
            build_context=".",
            build_args={
                "SELENIUM_VERSION": "4.11.0",
                "SCRAPY_VERSION": "2.10.0",
                "ENVIRONMENT": self.environment
            },
            labels={
                "maintainer": "Fahed Mlaiel <mlaiel@live.de>",
                "project": "IA-Influencer Agent",
                "component": "web-crawlers",
                "web-scraping": "true"
            }
        )
    
    def generate_compose_services(self) -> Dict[str, DockerServiceConfig]:
        """Generate Docker Compose services configuration"""
        services = {}
        
        # Main API Service
        services["api"] = DockerServiceConfig(
            image=f"{self.registry_url}/{self.project_name}-api:latest-{self.environment}",
            container_name=f"{self.project_name}-api-{self.environment}",
            ports=["8000:8000"],
            volumes=[
                "./backend:/app/backend:ro",
                "./logs:/app/logs",
                "./uploads:/app/uploads"
            ],
            environment={
                "ENVIRONMENT": self.environment,
                "DATABASE_URL": "postgresql://user:password@postgres:5432/ia_influencer",
                "REDIS_URL": "redis://redis:6379/0",
                "MONGODB_URL": "mongodb://mongo:27017/ia_influencer",
                "SECRET_KEY": "${SECRET_KEY}",
                "JWT_SECRET": "${JWT_SECRET}"
            },
            depends_on=["postgres", "redis", "mongo"],
            networks=["ia-network"],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "40s"
            }
        )
        
        # AI Fingerprinting Service
        services["ai-fingerprinting"] = DockerServiceConfig(
            image=f"{self.registry_url}/{self.project_name}-ai-fingerprinting:latest-{self.environment}",
            container_name=f"{self.project_name}-ai-fingerprinting-{self.environment}",
            ports=["8001:8001"],
            volumes=[
                "./models:/app/models:ro",
                "./temp:/app/temp",
                "/dev/shm:/dev/shm"
            ],
            environment={
                "ENVIRONMENT": self.environment,
                "GPU_ENABLED": "true",
                "MODEL_PATH": "/app/models",
                "TEMP_PATH": "/app/temp"
            },
            depends_on=["redis"],
            networks=["ia-network"],
            deploy={
                "resources": {
                    "reservations": {
                        "devices": [
                            {
                                "driver": "nvidia",
                                "count": 1,
                                "capabilities": ["gpu"]
                            }
                        ]
                    }
                }
            }
        )
        
        # Content Protection Service
        services["content-protection"] = DockerServiceConfig(
            image=f"{self.registry_url}/{self.project_name}-content-protection:latest-{self.environment}",
            container_name=f"{self.project_name}-content-protection-{self.environment}",
            ports=["8002:8002"],
            volumes=[
                "./content:/app/content",
                "./signatures:/app/signatures:ro",
                "/tmp:/app/tmp"
            ],
            environment={
                "ENVIRONMENT": self.environment,
                "CONTENT_PATH": "/app/content",
                "SIGNATURE_PATH": "/app/signatures"
            },
            depends_on=["postgres", "redis"],
            networks=["ia-network"]
        )
        
        # Monetization Engine Service
        services["monetization"] = DockerServiceConfig(
            image=f"{self.registry_url}/{self.project_name}-monetization:latest-{self.environment}",
            container_name=f"{self.project_name}-monetization-{self.environment}",
            ports=["8003:8003"],
            environment={
                "ENVIRONMENT": self.environment,
                "STRIPE_API_KEY": "${STRIPE_API_KEY}",
                "PAYPAL_CLIENT_ID": "${PAYPAL_CLIENT_ID}",
                "WISE_API_KEY": "${WISE_API_KEY}"
            },
            depends_on=["postgres", "redis"],
            networks=["ia-network"]
        )
        
        # Web Crawlers Service
        services["web-crawlers"] = DockerServiceConfig(
            image=f"{self.registry_url}/{self.project_name}-web-crawlers:latest-{self.environment}",
            container_name=f"{self.project_name}-crawlers-{self.environment}",
            volumes=[
                "./crawler_data:/app/data",
                "./screenshots:/app/screenshots"
            ],
            environment={
                "ENVIRONMENT": self.environment,
                "SELENIUM_HUB_URL": "http://selenium-hub:4444/wd/hub",
                "USER_AGENT": "IA-Influencer-Agent-Bot/1.0"
            },
            depends_on=["redis", "selenium-hub"],
            networks=["ia-network"]
        )
        
        # Database Services
        services.update(self._get_database_services())
        
        # Infrastructure Services
        services.update(self._get_infrastructure_services())
        
        return services
    
    def _get_database_services(self) -> Dict[str, DockerServiceConfig]:
        """Generate database services configuration"""
        return {
            "postgres": DockerServiceConfig(
                image="postgres:15.4-alpine",
                container_name=f"{self.project_name}-postgres-{self.environment}",
                ports=["5432:5432"] if self.environment == "development" else [],
                volumes=[
                    f"postgres_data_{self.environment}:/var/lib/postgresql/data",
                    "./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro"
                ],
                environment={
                    "POSTGRES_DB": "ia_influencer",
                    "POSTGRES_USER": "ia_user",
                    "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}",
                    "POSTGRES_INITDB_ARGS": "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
                },
                networks=["ia-network"],
                healthcheck={
                    "test": ["CMD-SHELL", "pg_isready -U ia_user -d ia_influencer"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            ),
            
            "redis": DockerServiceConfig(
                image="redis:7.2-alpine",
                container_name=f"{self.project_name}-redis-{self.environment}",
                ports=["6379:6379"] if self.environment == "development" else [],
                volumes=[
                    f"redis_data_{self.environment}:/data",
                    "./docker/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro"
                ],
                environment={
                    "REDIS_PASSWORD": "${REDIS_PASSWORD}"
                },
                networks=["ia-network"],
                healthcheck={
                    "test": ["CMD", "redis-cli", "ping"],
                    "interval": "10s",
                    "timeout": "3s",
                    "retries": 3
                }
            ),
            
            "mongo": DockerServiceConfig(
                image="mongo:7.0-jammy",
                container_name=f"{self.project_name}-mongo-{self.environment}",
                ports=["27017:27017"] if self.environment == "development" else [],
                volumes=[
                    f"mongo_data_{self.environment}:/data/db",
                    "./docker/mongo/mongod.conf:/etc/mongod.conf:ro"
                ],
                environment={
                    "MONGO_INITDB_ROOT_USERNAME": "ia_admin",
                    "MONGO_INITDB_ROOT_PASSWORD": "${MONGO_PASSWORD}",
                    "MONGO_INITDB_DATABASE": "ia_influencer"
                },
                networks=["ia-network"],
                healthcheck={
                    "test": ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 3
                }
            )
        }
    
    def _get_infrastructure_services(self) -> Dict[str, DockerServiceConfig]:
        """Generate infrastructure services configuration"""
        return {
            "nginx": DockerServiceConfig(
                image="nginx:1.25-alpine",
                container_name=f"{self.project_name}-nginx-{self.environment}",
                ports=["80:80", "443:443"],
                volumes=[
                    "./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
                    "./docker/nginx/ssl:/etc/nginx/ssl:ro",
                    "./static:/usr/share/nginx/html/static:ro"
                ],
                depends_on=["api"],
                networks=["ia-network"],
                healthcheck={
                    "test": ["CMD", "curl", "-f", "http://localhost/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            ),
            
            "selenium-hub": DockerServiceConfig(
                image="selenium/hub:4.11.0",
                container_name=f"{self.project_name}-selenium-hub-{self.environment}",
                ports=["4444:4444"],
                environment={
                    "GRID_MAX_SESSION": "16",
                    "GRID_BROWSER_TIMEOUT": "300",
                    "GRID_TIMEOUT": "300"
                },
                networks=["ia-network"]
            ),
            
            "selenium-chrome": DockerServiceConfig(
                image="selenium/node-chrome:4.11.0",
                container_name=f"{self.project_name}-selenium-chrome-{self.environment}",
                volumes=[
                    "/dev/shm:/dev/shm"
                ],
                environment={
                    "HUB_HOST": "selenium-hub",
                    "NODE_MAX_INSTANCES": "4",
                    "NODE_MAX_SESSION": "4"
                },
                depends_on=["selenium-hub"],
                networks=["ia-network"]
            )
        }
    
    def generate_docker_compose_file(self, output_path: str = "./docker-compose.yml") -> None:
        """Generate complete Docker Compose file"""
        services = self.generate_compose_services()
        
        compose_config = {
            "version": "3.8",
            "services": {},
            "networks": {
                "ia-network": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [
                            {"subnet": "172.20.0.0/16"}
                        ]
                    }
                }
            },
            "volumes": {}
        }
        
        # Convert service configs to compose format
        for name, service in services.items():
            compose_config["services"][name] = {
                "image": service.image,
                "container_name": service.container_name,
                "restart": service.restart_policy,
                "networks": service.networks
            }
            
            if service.ports:
                compose_config["services"][name]["ports"] = service.ports
            
            if service.volumes:
                compose_config["services"][name]["volumes"] = service.volumes
            
            if service.environment:
                compose_config["services"][name]["environment"] = service.environment
            
            if service.depends_on:
                compose_config["services"][name]["depends_on"] = service.depends_on
            
            if service.healthcheck:
                compose_config["services"][name]["healthcheck"] = service.healthcheck
            
            if service.deploy:
                compose_config["services"][name]["deploy"] = service.deploy
        
        # Add persistent volumes
        volume_names = [
            f"postgres_data_{self.environment}",
            f"redis_data_{self.environment}",
            f"mongo_data_{self.environment}"
        ]
        
        for volume_name in volume_names:
            compose_config["volumes"][volume_name] = {"driver": "local"}
        
        # Write compose file
        with open(output_path, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    def generate_dockerfile_templates(self, output_dir: str = "./docker") -> None:
        """Generate Dockerfile templates for all services"""
        dockerfiles = {
            "api/Dockerfile": self._get_api_dockerfile(),
            "ai-fingerprinting/Dockerfile": self._get_ai_fingerprinting_dockerfile(),
            "content-protection/Dockerfile": self._get_content_protection_dockerfile(),
            "monetization/Dockerfile": self._get_monetization_dockerfile(),
            "crawlers/Dockerfile": self._get_crawlers_dockerfile(),
            "nginx/nginx.conf": self._get_nginx_config(),
            "postgres/init.sql": self._get_postgres_init(),
            "redis/redis.conf": self._get_redis_config(),
            "mongo/mongod.conf": self._get_mongo_config()
        }
        
        for filepath, content in dockerfiles.items():
            full_path = Path(output_dir) / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def _get_api_dockerfile(self) -> str:
        """Generate main API Dockerfile"""
        return '''# Multi-stage build for IA-Influencer Agent API
FROM python:3.11-slim-bullseye as base

# Build arguments
ARG ENVIRONMENT=development
ARG BUILD_DATE
ARG VCS_REF

# Labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \\
      project="IA-Influencer Agent" \\
      component="main-api" \\
      build-date=$BUILD_DATE \\
      vcs-ref=$VCS_REF

# System dependencies
RUN apt-get update && apt-get install -y \\
    gcc g++ \\
    libpq-dev \\
    libffi-dev \\
    libssl-dev \\
    curl \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY backend/ ./backend/
COPY config/ ./config/

# Non-root user
RUN useradd -m -u 1001 appuser && \\
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _get_ai_fingerprinting_dockerfile(self) -> str:
        """Generate AI Fingerprinting service Dockerfile"""
        return '''# AI Fingerprinting Service with GPU support
FROM tensorflow/tensorflow:2.13.0-gpu

# Build arguments
ARG TENSORFLOW_VERSION=2.13.0
ARG PYTORCH_VERSION=2.0.1
ARG ENVIRONMENT=development

# Labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \\
      project="IA-Influencer Agent" \\
      component="ai-fingerprinting" \\
      gpu-required="true"

# System dependencies for audio/video processing
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    libsndfile1 \\
    libavcodec-dev \\
    libavformat-dev \\
    libswscale-dev \\
    libavresample-dev \\
    pkg-config \\
    python3-dev \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Python ML dependencies
WORKDIR /app
COPY requirements-ai.txt .
RUN pip install --no-cache-dir -r requirements-ai.txt

# Install PyTorch with CUDA support
RUN pip install torch==$PYTORCH_VERSION torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Application code
COPY backend/ai/ ./backend/ai/
COPY backend/content_protection/ ./backend/content_protection/
COPY models/ ./models/

# Non-root user
RUN useradd -m -u 1001 aiuser && \\
    chown -R aiuser:aiuser /app
USER aiuser

# Expose service port
EXPOSE 8001
CMD ["python", "-m", "backend.ai.fingerprinting_service"]
'''
    
    def _get_content_protection_dockerfile(self) -> str:
        """Generate Content Protection service Dockerfile"""
        return '''# Content Protection Service
FROM python:3.11-slim-bullseye

# Build arguments
ARG OPENCV_VERSION=4.8.0
ARG FFMPEG_VERSION=6.0
ARG ENVIRONMENT=development

# Labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \\
      project="IA-Influencer Agent" \\
      component="content-protection" \\
      media-processing="true"

# System dependencies for media processing
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    libopencv-dev \\
    libmagic1 \\
    file \\
    imagemagick \\
    libvips-tools \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY requirements-protection.txt .
RUN pip install --no-cache-dir -r requirements-protection.txt

# Application code
COPY backend/content_protection/ ./backend/content_protection/
COPY backend/utils/ ./backend/utils/

# Non-root user
RUN useradd -m -u 1001 protectionuser && \\
    chown -R protectionuser:protectionuser /app
USER protectionuser

# Expose service port
EXPOSE 8002
CMD ["python", "-m", "backend.content_protection.protection_service"]
'''
    
    def _get_monetization_dockerfile(self) -> str:
        """Generate Monetization Engine service Dockerfile"""
        return '''# Monetization Engine Service
FROM python:3.11-slim-bullseye

# Build arguments
ARG ENVIRONMENT=development
ARG PAYMENT_APIS=stripe,paypal,wise

# Labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \\
      project="IA-Influencer Agent" \\
      component="monetization-engine" \\
      payment-processing="true"

# System dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    libssl-dev \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY requirements-monetization.txt .
RUN pip install --no-cache-dir -r requirements-monetization.txt

# Application code
COPY backend/business/ ./backend/business/
COPY backend/integrations/ ./backend/integrations/

# Non-root user
RUN useradd -m -u 1001 monetizationuser && \\
    chown -R monetizationuser:monetizationuser /app
USER monetizationuser

# Expose service port
EXPOSE 8003
CMD ["python", "-m", "backend.business.monetization_service"]
'''
    
    def _get_crawlers_dockerfile(self) -> str:
        """Generate Web Crawlers service Dockerfile"""
        return '''# Web Crawlers Service
FROM python:3.11-slim-bullseye

# Build arguments
ARG SELENIUM_VERSION=4.11.0
ARG SCRAPY_VERSION=2.10.0
ARG ENVIRONMENT=development

# Labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \\
      project="IA-Influencer Agent" \\
      component="web-crawlers" \\
      web-scraping="true"

# System dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    curl \\
    unzip \\
    xvfb \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY requirements-crawlers.txt .
RUN pip install --no-cache-dir -r requirements-crawlers.txt

# Application code
COPY backend/integrations/crawlers/ ./backend/integrations/crawlers/
COPY backend/utils/ ./backend/utils/

# Non-root user
RUN useradd -m -u 1001 crawleruser && \\
    chown -R crawleruser:crawleruser /app
USER crawleruser

# Expose service port
EXPOSE 8004
CMD ["python", "-m", "backend.integrations.crawlers.crawler_service"]
'''
    
    def _get_nginx_config(self) -> str:
        """Generate Nginx configuration"""
        return '''# Nginx configuration for IA-Influencer Agent
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    # Upstream services
    upstream api_backend {
        server api:8000;
        keepalive 32;
    }
    
    upstream ai_backend {
        server ai-fingerprinting:8001;
        keepalive 16;
    }
    
    upstream protection_backend {
        server content-protection:8002;
        keepalive 16;
    }
    
    upstream monetization_backend {
        server monetization:8003;
        keepalive 16;
    }
    
    # Main server block
    server {
        listen 80;
        server_name localhost;
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
        
        # API routing
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # AI services routing
        location /ai/ {
            proxy_pass http://ai_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_connect_timeout 10s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
        
        # Protection services routing
        location /protection/ {
            proxy_pass http://protection_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_connect_timeout 5s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }
        
        # Monetization services routing
        location /monetization/ {
            proxy_pass http://monetization_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
        }
        
        # Static files
        location /static/ {
            alias /usr/share/nginx/html/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
'''
    
    def _get_postgres_init(self) -> str:
        """Generate PostgreSQL initialization script"""
        return '''-- PostgreSQL initialization for IA-Influencer Agent
-- Author: Fahed Mlaiel <mlaiel@live.de>

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS content_protection;
CREATE SCHEMA IF NOT EXISTS ai_fingerprinting;
CREATE SCHEMA IF NOT EXISTS monetization;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
ALTER DATABASE ia_influencer SET search_path TO public, content_protection, ai_fingerprinting, monetization, analytics;

-- Create roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ia_api_user') THEN
        CREATE ROLE ia_api_user LOGIN PASSWORD 'api_secure_pass_2025';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ia_readonly_user') THEN
        CREATE ROLE ia_readonly_user LOGIN PASSWORD 'readonly_pass_2025';
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA public, content_protection, ai_fingerprinting, monetization, analytics TO ia_api_user;
GRANT USAGE ON SCHEMA public, content_protection, ai_fingerprinting, monetization, analytics TO ia_readonly_user;

-- Grant table permissions (will be applied to future tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ia_api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA content_protection GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ia_api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_fingerprinting GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ia_api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA monetization GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ia_api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ia_api_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ia_readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA content_protection GRANT SELECT ON TABLES TO ia_readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_fingerprinting GRANT SELECT ON TABLES TO ia_readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA monetization GRANT SELECT ON TABLES TO ia_readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO ia_readonly_user;

-- Performance tuning
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '100';
SELECT pg_reload_conf();
'''
    
    def _get_redis_config(self) -> str:
        """Generate Redis configuration"""
        return '''# Redis configuration for IA-Influencer Agent
# Author: Fahed Mlaiel <mlaiel@live.de>

# Network
bind 0.0.0.0
port 6379
protected-mode yes

# Security
requirepass ${REDIS_PASSWORD}

# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfsync everysec

# Performance
tcp-keepalive 300
tcp-backlog 511
timeout 0

# Logging
loglevel notice
logfile ""

# Client management
maxclients 10000

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Key space notifications for AI processing
notify-keyspace-events Ex

# Modules loading (if needed)
# loadmodule /usr/lib/redis/modules/redisearch.so
# loadmodule /usr/lib/redis/modules/redisjson.so
'''
    
    def _get_mongo_config(self) -> str:
        """Generate MongoDB configuration"""
        return '''# MongoDB configuration for IA-Influencer Agent
# Author: Fahed Mlaiel <mlaiel@live.de>

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true

storage:
  dbPath: /data/db
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1

processManagement:
  fork: false
  pidFilePath: /var/run/mongodb/mongod.pid

net:
  bindIp: 0.0.0.0
  port: 27017

security:
  authorization: enabled

replication:
  replSetName: "ia-rs"

# Performance settings
operationProfiling:
  slowOpThresholdMs: 100
  mode: slowOp

# Connection settings
net:
  maxIncomingConnections: 1000
  compression:
    compressors: zstd,zlib,snappy
'''

    def get_build_script(self) -> str:
        """Generate build script for all Docker images"""
        return '''#!/bin/bash
# Docker build script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

REGISTRY_URL="${REGISTRY_URL:-localhost:5000}"
ENVIRONMENT="${ENVIRONMENT:-development}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD)

echo "🚀 Building IA-Influencer Agent Docker images..."
echo "Registry: $REGISTRY_URL"
echo "Environment: $ENVIRONMENT"
echo "Build Date: $BUILD_DATE"
echo "VCS Ref: $VCS_REF"

# Build main API
echo "📦 Building main API service..."
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    --build-arg BUILD_DATE=$BUILD_DATE \
    --build-arg VCS_REF=$VCS_REF \
    -t $REGISTRY_URL/ia-influencer-agent-api:latest-$ENVIRONMENT \
    -f docker/api/Dockerfile .

# Build AI fingerprinting service
echo "🧠 Building AI fingerprinting service..."
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    -t $REGISTRY_URL/ia-influencer-agent-ai-fingerprinting:latest-$ENVIRONMENT \
    -f docker/ai-fingerprinting/Dockerfile .

# Build content protection service
echo "🛡️ Building content protection service..."
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    -t $REGISTRY_URL/ia-influencer-agent-content-protection:latest-$ENVIRONMENT \
    -f docker/content-protection/Dockerfile .

# Build monetization engine
echo "💰 Building monetization engine..."
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    -t $REGISTRY_URL/ia-influencer-agent-monetization:latest-$ENVIRONMENT \
    -f docker/monetization/Dockerfile .

# Build web crawlers
echo "🕷️ Building web crawlers service..."
docker build \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    -t $REGISTRY_URL/ia-influencer-agent-web-crawlers:latest-$ENVIRONMENT \
    -f docker/crawlers/Dockerfile .

echo "✅ All images built successfully!"

# Push to registry (if not local)
if [ "$REGISTRY_URL" != "localhost:5000" ]; then
    echo "📤 Pushing images to registry..."
    docker push $REGISTRY_URL/ia-influencer-agent-api:latest-$ENVIRONMENT
    docker push $REGISTRY_URL/ia-influencer-agent-ai-fingerprinting:latest-$ENVIRONMENT
    docker push $REGISTRY_URL/ia-influencer-agent-content-protection:latest-$ENVIRONMENT
    docker push $REGISTRY_URL/ia-influencer-agent-monetization:latest-$ENVIRONMENT
    docker push $REGISTRY_URL/ia-influencer-agent-web-crawlers:latest-$ENVIRONMENT
    echo "✅ All images pushed successfully!"
fi

echo "🎉 Docker build process completed!"
'''

    def get_deployment_script(self) -> str:
        """Generate deployment script"""
        return '''#!/bin/bash
# Deployment script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="${ENVIRONMENT:-development}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

echo "🚀 Deploying IA-Influencer Agent Platform..."
echo "Environment: $ENVIRONMENT"
echo "Compose file: $COMPOSE_FILE"

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "📝 Loading environment variables from .env.$ENVIRONMENT"
    export $(cat .env.$ENVIRONMENT | xargs)
fi

# Create necessary directories
mkdir -p logs uploads models temp screenshots crawler_data

# Pull latest images (if using remote registry)
if [ "$ENVIRONMENT" != "development" ]; then
    echo "📥 Pulling latest images..."
    docker compose -f $COMPOSE_FILE pull
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker compose -f $COMPOSE_FILE down --remove-orphans

# Start services
echo "🎬 Starting services..."
docker compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "⏱️ Waiting for services to be ready..."
for service in postgres redis mongo api; do
    echo "Checking $service..."
    until docker compose -f $COMPOSE_FILE exec $service healthcheck 2>/dev/null; do
        echo "Waiting for $service to be healthy..."
        sleep 5
    done
    echo "✅ $service is healthy"
done

# Run database migrations (if needed)
echo "🗄️ Running database migrations..."
docker compose -f $COMPOSE_FILE exec api python -m backend.database.migrations.run

# Display status
echo "📊 Deployment status:"
docker compose -f $COMPOSE_FILE ps

echo "🎉 IA-Influencer Agent Platform deployed successfully!"
echo "🌐 Access the API at: http://localhost:8000"
echo "📝 API documentation: http://localhost:8000/docs"
echo "💻 Admin interface: http://localhost:8000/admin"
'''
