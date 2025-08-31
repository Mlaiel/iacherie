"""
 Storage Services Configuration - IA-Influencer-Agent Platform
=================================================================
Expert: Storage Engineer + Cloud Architect + Data Management Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
=================================================================

  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL 
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Comprehensive storage services for content management, file processing,
backup systems, and distributed storage with high availability.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class StorageServicesDockerConfig:
    """Production Storage Services Configuration"""
    
    # MinIO Configuration (S3-compatible storage)
    minio_version: str = "RELEASE.2024-01-01T16-36-33Z"
    minio_access_key: str = "ia_influencer_access_key"
    minio_secret_key: str = "ultra_secure_minio_secret_key_2024"
    
    # Storage Configuration
    storage_buckets: List[str] = field(default_factory=lambda: [
        "content-uploads", "processed-content", "thumbnails", 
        "evidence-storage", "backups", "models", "reports"
    ])
    
    # Performance Configuration
    minio_memory: str = "4Gi"
    minio_cpu: str = "2000m"
    
    # Security Configuration
    enable_encryption: bool = True
    enable_versioning: bool = True
    
    def generate_minio_service(self) -> Dict[str, Any]:
        """Generate MinIO service for object storage"""



        return {
            "image": f"minio/minio:{self.minio_version}",
            "container_name": "ia-influencer-minio",
            "restart": "unless-stopped",
            "ports": ["9000:9000", "9001:9001"],
            "command": ["server", "/data", "--console-address", ":9001"],
            "environment": {
                "MINIO_ROOT_USER": self.minio_access_key,
                "MINIO_ROOT_PASSWORD": self.minio_secret_key,
                "MINIO_STORAGE_CLASS_STANDARD": "EC:2",
                "MINIO_BROWSER_REDIRECT_URL": "https://storage.ia-influencer.com",
                "MINIO_PROMETHEUS_AUTH_TYPE": "public"
            },
            "volumes": [
                "minio_data:/data",
                "./config/minio:/root/.minio:ro"
            ],
            "networks": ["ia-influencer-network"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": self.minio_cpu,
                        "memory": self.minio_memory
                    },
                    "reservations": {
                        "cpus": "1000m",
                        "memory": "2Gi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:9000/minio/health/live || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "10s"
            },
            "logging": {
                "driver": "json-file",
                "options": {
                    "max-size": "100m",
                    "max-file": "3"
                }
            }
        }
    
    def generate_file_processor_service(self) -> Dict[str, Any]:
        """Generate file processing service"""



        return {
            "build": {
                "context": "./file-processor",
                "dockerfile": "Dockerfile"
            },
            "image": "ia-influencer/file-processor:2.0.0",
            "container_name": "ia-influencer-file-processor",
            "restart": "unless-stopped",
            "environment": {
                "MINIO_ENDPOINT": "minio:9000",
                "MINIO_ACCESS_KEY": self.minio_access_key,
                "MINIO_SECRET_KEY": self.minio_secret_key,
                "REDIS_URL": "redis://redis:6379",
                "POSTGRES_URL": "postgresql://ia_user:ultra_secure_db_password_2024@postgres-master:5432/ia_influencer",
                "MAX_FILE_SIZE": "500MB",
                "SUPPORTED_FORMATS": "jpg,jpeg,png,gif,mp4,avi,mkv,mp3,wav,flac,pdf,docx,txt"
            },
            "volumes": [
                "temp_processing:/tmp/processing",
                "./config/file-processor:/app/config:ro"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": ["minio", "redis", "postgres-master"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "4000m",
                        "memory": "6Gi"
                    },
                    "reservations": {
                        "cpus": "2000m",
                        "memory": "3Gi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:8000/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
    
    def generate_backup_service(self) -> Dict[str, Any]:
        """Generate backup service for automated backups"""



        return {
            "build": {
                "context": "./backup-service",
                "dockerfile": "Dockerfile"
            },
            "image": "ia-influencer/backup-service:2.0.0",
            "container_name": "ia-influencer-backup-service",
            "restart": "unless-stopped",
            "environment": {
                "BACKUP_SCHEDULE": "0 2 * * *",  # Daily at 2 AM
                "RETENTION_DAYS": "30",
                "BACKUP_ENCRYPTION": str(self.enable_encryption).lower(),
                "MINIO_ENDPOINT": "minio:9000",
                "MINIO_ACCESS_KEY": self.minio_access_key,
                "MINIO_SECRET_KEY": self.minio_secret_key,
                "POSTGRES_URL": "postgresql://ia_user:ultra_secure_db_password_2024@postgres-master:5432/ia_influencer",
                "REDIS_URL": "redis://redis:6379",
                "ELASTICSEARCH_URL": "http://elasticsearch:9200"
            },
            "volumes": [
                "backup_storage:/backups",
                "./config/backup:/app/config:ro",
                "/var/run/docker.sock:/var/run/docker.sock:ro"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": ["minio", "postgres-master", "redis", "elasticsearch"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "1000m",
                        "memory": "2Gi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost:8000/health || exit 1",
                "interval": "60s",
                "timeout": "10s",
                "retries": 3
            }
        }
    
    def generate_cdn_service(self) -> Dict[str, Any]:
        """Generate CDN service for content delivery"""



        return {
            "image": "nginx:alpine",
            "container_name": "ia-influencer-cdn",
            "restart": "unless-stopped",
            "ports": ["8080:80"],
            "volumes": [
                "./config/cdn/nginx.conf:/etc/nginx/nginx.conf:ro",
                "./config/cdn/conf.d:/etc/nginx/conf.d:ro",
                "cdn_cache:/var/cache/nginx",
                "./logs/cdn:/var/log/nginx"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": ["minio"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "1000m",
                        "memory": "1Gi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
    
    def generate_file_processor_dockerfile(self) -> str:
        """Generate Dockerfile for file processor service"""



        return """
# IA-Influencer File Processor Dockerfile
# Multi-format content processing service
# Creator: Fahed Mlaiel <mlaiel@live.de>

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    imagemagick \\
    ghostscript \\
    libreoffice \\
    poppler-utils \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/processing \\
    && chmod 755 /tmp/processing

# Create non-root user
RUN useradd -m -u 1000 processor
RUN chown -R processor:processor /app /tmp/processing
USER processor

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def generate_file_processor_requirements(self) -> str:
        """Generate requirements.txt for file processor"""



        return """
# File Processing Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
aiofiles==23.2.1
python-multipart==0.0.6

# Storage and Database
minio==7.2.0
asyncpg==0.29.0
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.13.1

# Media Processing
pillow==10.1.0
opencv-python==4.8.1.78
moviepy==1.0.3
pydub==0.25.1

# Document Processing
python-docx==1.1.0
pypdf2==3.0.1
python-magic==0.4.27

# AI and ML
torch==2.1.1
torchvision==0.16.1
transformers==4.36.0
sentence-transformers==2.2.2

# Utilities
celery==5.3.4
kombu==5.3.4
python-dotenv==1.0.0
structlog==23.2.0
prometheus-client==0.19.0
"""
    
    def generate_backup_service_dockerfile(self) -> str:
        """Generate Dockerfile for backup service"""



        return """
# IA-Influencer Backup Service Dockerfile
# Automated backup and recovery system
# Creator: Fahed Mlaiel <mlaiel@live.de>

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    curl \\
    cron \\
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for volume backups
RUN curl -fsSL https://get.docker.com | sh

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create backup directory
RUN mkdir -p /backups \\
    && chmod 755 /backups

# Create non-root user
RUN useradd -m -u 1000 backup
RUN chown -R backup:backup /app /backups
USER backup

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application with cron
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def generate_backup_service_requirements(self) -> str:
        """Generate requirements.txt for backup service"""



        return """
# Backup Service Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
schedule==1.2.0

# Storage and Database
minio==7.2.0
asyncpg==0.29.0
redis==5.0.1
elasticsearch==8.11.0

# Compression and Encryption
cryptography==41.0.7
tarfile==0.0.0

# Utilities
python-dotenv==1.0.0
structlog==23.2.0
prometheus-client==0.19.0
"""
    
    def generate_cdn_nginx_config(self) -> str:
        """Generate Nginx configuration for CDN service"""



        return """
# IA-Influencer CDN Nginx Configuration
# High-performance content delivery
# Creator: Fahed Mlaiel <mlaiel@live.de>

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
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

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Cache settings
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=content_cache:10m max_size=1g inactive=60m use_temp_path=off;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    # Upstream MinIO
    upstream minio {
        server minio:9000;
    }

    server {
        listen 80;
        server_name cdn.ia-influencer.com;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # Content delivery
        location / {
            proxy_pass http://minio;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Cache configuration
            proxy_cache content_cache;
            proxy_cache_valid 200 302 10m;
            proxy_cache_valid 404 1m;
            proxy_cache_use_stale error timeout invalid_header updating http_500 http_502 http_503 http_504;
            proxy_cache_lock on;
            proxy_cache_lock_timeout 5s;

            # Add cache headers
            add_header X-Cache-Status $upstream_cache_status;

            # Rate limiting
            limit_req zone=api burst=20 nodelay;

            # Content type optimization
            location ~* \\.(jpg|jpeg|png|gif|ico|webp)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }

            location ~* \\.(css|js)$ {
                expires 1M;
                add_header Cache-Control "public";
            }

            location ~* \\.(mp4|webm|ogg)$ {
                expires 1M;
                add_header Cache-Control "public";
                proxy_cache_valid 200 302 1M;
            }
        }
    }
}
"""
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all storage service configuration files"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # File processor files
        file_processor_dir = output_path / "file-processor"
        file_processor_dir.mkdir(exist_ok=True)
        
        dockerfile_fp = file_processor_dir / "Dockerfile"
        with open(dockerfile_fp, 'w') as f:
            f.write(self.generate_file_processor_dockerfile())
        files_created.append(str(dockerfile_fp))
        
        requirements_fp = file_processor_dir / "requirements.txt"
        with open(requirements_fp, 'w') as f:
            f.write(self.generate_file_processor_requirements())
        files_created.append(str(requirements_fp))
        
        # Backup service files
        backup_service_dir = output_path / "backup-service"
        backup_service_dir.mkdir(exist_ok=True)
        
        dockerfile_bs = backup_service_dir / "Dockerfile"
        with open(dockerfile_bs, 'w') as f:
            f.write(self.generate_backup_service_dockerfile())
        files_created.append(str(dockerfile_bs))
        
        requirements_bs = backup_service_dir / "requirements.txt"
        with open(requirements_bs, 'w') as f:
            f.write(self.generate_backup_service_requirements())
        files_created.append(str(requirements_bs))
        
        # CDN configuration
        cdn_dir = output_path / "config" / "cdn"
        cdn_dir.mkdir(parents=True, exist_ok=True)
        
        nginx_config = cdn_dir / "nginx.conf"
        with open(nginx_config, 'w') as f:
            f.write(self.generate_cdn_nginx_config())
        files_created.append(str(nginx_config))
        
        # Docker compose for storage services
        compose_file = output_path / "docker-compose.storage.yml"
        with open(compose_file, 'w') as f:
            import yaml
            compose_config = {
                "version": "3.8",
                "services": {
                    "minio": self.generate_minio_service(),
                    "file-processor": self.generate_file_processor_service(),
                    "backup-service": self.generate_backup_service(),
                    "cdn": self.generate_cdn_service()
                },
                "volumes": {
                    "minio_data": {},
                    "temp_processing": {},
                    "backup_storage": {},
                    "cdn_cache": {}
                },
                "networks": {
                    "ia-influencer-network": {
                        "external": True
                    }
                }
            }
            yaml.dump(compose_config, f, default_flow_style=False, indent=2)
        files_created.append(str(compose_file))
        
        logger.info(f" Storage services configuration saved: {len(files_created)} files created")
        return files_created
