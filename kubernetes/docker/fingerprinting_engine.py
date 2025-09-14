"""🔍 Fingerprinting Engine Docker Configuration - IA-Influencer-Agent Platform
=============================================================================
Expert: ML Engineer + Audio Specialist + Computer Vision Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
=============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional fingerprinting engine Docker configuration for multi-format
content identification and similarity matching systems.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, field
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class FingerprintingEngineDockerConfig:
    """
Enterprise Fingerprinting Engine Docker configuration"""
    
    # Container Configuration
    image_name: str = "ia-influencer/fingerprinting-engine"
    image_tag: str = "2.0.0"
    container_name: str = "ia-influencer-fingerprinting"
    
    # Application Configuration
    api_port: int = 8000
    worker_port: int = 8001
    metrics_port: int = 9090
    grpc_port: int = 9000
    
    # Fingerprinting Configuration
    enabled_formats: Dict[str, bool] = field(default_factory=lambda: {
        "audio": True,
        "video": True,
        "image": True,
        "text": True
    })
    
    # Performance Configuration
    workers: int = 6
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = 800
    max_requests_jitter: int = 80
    batch_size: int = 64
    similarity_threshold: float = 0.85
    
    # Processing Configuration
    max_file_size: str = "500MB"
    supported_audio_formats: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "m4a", "aac", "ogg", "wma"
    ])
    supported_video_formats: List[str] = field(default_factory=lambda: [
        "mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"
    ])
    supported_image_formats: List[str] = field(default_factory=lambda: [
        "jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"
    ])
    
    # Environment Configuration
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    vector_db_url: str = "http://qdrant:6333"
    postgres_url: str = "postgresql://ia_user:secure_password@postgres:5432/ia_influencer"
    redis_url: str = "redis://redis:6379/3"
    elasticsearch_url: str = "http://elasticsearch:9200"
    
    # Resource Limits
    cpu_limit: str = "8000m"
    memory_limit: str = "16Gi"
    cpu_request: str = "4000m"
    memory_request: str = "8Gi"
    
    # Storage Configuration
    storage_backend: str = "s3"
    s3_bucket: str = "ia-influencer-fingerprints"
    s3_region: str = "eu-central-1"
    
    # AI Model Configuration
    audio_models: Dict[str, str] = field(default_factory=lambda: {
        "chromaprint": "AcoustID/chromaprint",
        "essentia": "essentia/streaming_extractor",
        "wav2vec": "facebook/wav2vec2-base-960h",
        "clap": "laion/clap-htsat-unfused"
    })
    
    video_models: Dict[str, str] = field(default_factory=lambda: {
        "clip": "openai/clip-vit-base-patch32",
        "resnet": "microsoft/resnet-50",
        "efficientnet": "google/efficientnet-b0"
    })
    
    image_models: Dict[str, str] = field(default_factory=lambda: {
        "clip": "openai/clip-vit-base-patch32",
        "vit": "google/vit-base-patch16-224",
        "dinov2": "facebook/dinov2-base"
    })
    
    text_models: Dict[str, str] = field(default_factory=lambda: {
        "sentence_transformer": "sentence-transformers/all-mpnet-base-v2",
        "bert": "bert-base-uncased",
        "roberta": "roberta-base"
    })
    
    # Health Check Configuration
    health_check_enabled: bool = True
    health_check_interval: str = "30s"
    health_check_timeout: str = "15s"
    health_check_retries: int = 3
    
    def generate_dockerfile(self) -> str:
        """Generate production Dockerfile for Fingerprinting Engine"""
        return f"""# IA-Influencer Fingerprinting Engine - Production Docker Image
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Professional multi-format content fingerprinting with AI models

# Multi-stage build for optimization
FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.image_tag}"
LABEL service="fingerprinting-engine"
LABEL platform="IA-Influencer-Agent"
LABEL environment="{self.environment}"

# System dependencies for multimedia processing
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    ca-certificates \\
    libpq-dev \\
    libffi-dev \\
    libssl-dev \\
    pkg-config \\
    git \\
    # Audio processing dependencies
    libsndfile1 \\
    libsndfile1-dev \\
    ffmpeg \\
    libavcodec-dev \\
    libavformat-dev \\
    libswscale-dev \\
    libavutil-dev \\
    libavfilter-dev \\
    libavdevice-dev \\
    libasound2-dev \\
    portaudio19-dev \\
    # Video processing dependencies
    libopencv-dev \\
    python3-opencv \\
    # Image processing dependencies
    libjpeg-dev \\
    libpng-dev \\
    libtiff-dev \\
    libwebp-dev \\
    # Additional libraries
    libmagic1 \\
    libmagic-dev \\
    libgomp1 \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Install Chromaprint for audio fingerprinting
RUN apt-get update && apt-get install -y \\
    libchromaprint-dev \\
    libchromaprint-tools \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1001 fpgroup && \\
    useradd -r -u 1001 -g fpgroup fpuser

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

# Model preparation stage
FROM base AS model-prep
COPY download_fingerprint_models.py .
RUN python download_fingerprint_models.py --cache-dir=/app/models

# Production stage
FROM base AS production

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy pre-downloaded models
COPY --from=model-prep --chown=fpuser:fpgroup /app/models /app/models

# Copy application code
COPY --chown=fpuser:fpgroup . .

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/temp /app/uploads /app/fingerprints && \\
    chown -R fpuser:fpgroup /app && \\
    chmod -R 755 /app

# Environment variables
ENV ENVIRONMENT={self.environment}
ENV LOG_LEVEL={self.log_level}
ENV API_PORT={self.api_port}
ENV WORKER_PORT={self.worker_port}
ENV METRICS_PORT={self.metrics_port}
ENV GRPC_PORT={self.grpc_port}
ENV WORKERS={self.workers}
ENV WORKER_CLASS={self.worker_class}
ENV MAX_REQUESTS={self.max_requests}
ENV MAX_REQUESTS_JITTER={self.max_requests_jitter}
ENV BATCH_SIZE={self.batch_size}
ENV SIMILARITY_THRESHOLD={self.similarity_threshold}
ENV MAX_FILE_SIZE={self.max_file_size}
ENV VECTOR_DB_URL={self.vector_db_url}
ENV POSTGRES_URL={self.postgres_url}
ENV REDIS_URL={self.redis_url}
ENV ELASTICSEARCH_URL={self.elasticsearch_url}
ENV STORAGE_BACKEND={self.storage_backend}
ENV S3_BUCKET={self.s3_bucket}
ENV S3_REGION={self.s3_region}

# Format-specific environment variables
{self._generate_format_env_vars()}

# Model-specific environment variables
{self._generate_model_env_vars()}

# Switch to non-root user
USER fpuser

# Health check
HEALTHCHECK --interval={self.health_check_interval} \\
           --timeout={self.health_check_timeout} \\
           --start-period=90s \\
           --retries={self.health_check_retries} \\
    CMD curl -f http://localhost:{self.api_port}/health || exit 1

# Expose ports
EXPOSE {self.api_port}
EXPOSE {self.worker_port}
EXPOSE {self.metrics_port}
EXPOSE {self.grpc_port}

# Run application
CMD ["gunicorn", \\
     "--bind", "0.0.0.0:{self.api_port}", \\
     "--workers", "{self.workers}", \\
     "--worker-class", "{self.worker_class}", \\
     "--max-requests", "{self.max_requests}", \\
     "--max-requests-jitter", "{self.max_requests_jitter}", \\
     "--timeout", "300", \\
     "--keepalive", "60", \\
     "--log-level", "{self.log_level.lower()}", \\
     "--preload", \\
     "main:app"]
"""
    def _generate_format_env_vars(self) -> str:
        """
Generate format-specific environment variables"""
        env_vars = []
        for format_type, enabled in self.enabled_formats.items():
            env_vars.append(f"ENV FORMAT_{format_type.upper()}_ENABLED={str(enabled).lower()}")
        
        # Supported formats
        env_vars.append(f"ENV SUPPORTED_AUDIO_FORMATS={','.join(self.supported_audio_formats)}")
        env_vars.append(f"ENV SUPPORTED_VIDEO_FORMATS={','.join(self.supported_video_formats)}")
        env_vars.append(f"ENV SUPPORTED_IMAGE_FORMATS={','.join(self.supported_image_formats)}")
        
        return "\n".join(env_vars)

    def _generate_model_env_vars(self) -> str:
        """Generate model-specific environment variables"""
        env_vars = []
        
        # Audio models
        for model_name, model_path in self.audio_models.items():
            env_vars.append(f"ENV AUDIO_MODEL_{model_name.upper()}={model_path}")
        
        # Video models
        for model_name, model_path in self.video_models.items():
            env_vars.append(f"ENV VIDEO_MODEL_{model_name.upper()}={model_path}")
        
        # Image models
        for model_name, model_path in self.image_models.items():
            env_vars.append(f"ENV IMAGE_MODEL_{model_name.upper()}={model_path}")
        
        # Text models
        for model_name, model_path in self.text_models.items():
            env_vars.append(f"ENV TEXT_MODEL_{model_name.upper()}={model_path}")
        
        return "\n".join(env_vars)

    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate docker-compose service configuration"""
        return {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": self.container_name,
            "restart": "unless-stopped",
            "ports": [
                f"{self.api_port}:{self.api_port}",
                f"{self.worker_port}:{self.worker_port}",
                f"{self.metrics_port}:{self.metrics_port}",
                f"{self.grpc_port}:{self.grpc_port}"
            ],
            "environment": {
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": self.log_level,
                "DEBUG": str(self.debug_mode).lower(),
                "API_PORT": str(self.api_port),
                "WORKER_PORT": str(self.worker_port),
                "METRICS_PORT": str(self.metrics_port),
                "GRPC_PORT": str(self.grpc_port),
                "WORKERS": str(self.workers),
                "WORKER_CLASS": self.worker_class,
                "MAX_REQUESTS": str(self.max_requests),
                "MAX_REQUESTS_JITTER": str(self.max_requests_jitter),
                "BATCH_SIZE": str(self.batch_size),
                "SIMILARITY_THRESHOLD": str(self.similarity_threshold),
                "MAX_FILE_SIZE": self.max_file_size,
                "VECTOR_DB_URL": self.vector_db_url,
                "POSTGRES_URL": self.postgres_url,
                "REDIS_URL": self.redis_url,
                "ELASTICSEARCH_URL": self.elasticsearch_url,
                "STORAGE_BACKEND": self.storage_backend,
                "S3_BUCKET": self.s3_bucket,
                "S3_REGION": self.s3_region,
                "SUPPORTED_AUDIO_FORMATS": ",".join(self.supported_audio_formats),
                "SUPPORTED_VIDEO_FORMATS": ",".join(self.supported_video_formats),
                "SUPPORTED_IMAGE_FORMATS": ",".join(self.supported_image_formats),
                **{f"FORMAT_{k.upper()}_ENABLED": str(v).lower() for k, v in self.enabled_formats.items()},
                **{f"AUDIO_MODEL_{k.upper()}": v for k, v in self.audio_models.items()},
                **{f"VIDEO_MODEL_{k.upper()}": v for k, v in self.video_models.items()},
                **{f"IMAGE_MODEL_{k.upper()}": v for k, v in self.image_models.items()},
                **{f"TEXT_MODEL_{k.upper()}": v for k, v in self.text_models.items()}
            },
            "volumes": [
                "./logs/fingerprinting:/app/logs",
                "./models/fingerprinting:/app/models",
                "./cache/fingerprinting:/app/cache",
                "./config/fingerprinting:/app/config:ro",
                "./uploads:/app/uploads",
                "./fingerprints:/app/fingerprints",
                "/tmp:/app/temp"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "postgres",
                "redis",
                "elasticsearch",
                "qdrant"
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
                "test": f"curl -f http://localhost:{self.api_port}/health || exit 1",
                "interval": self.health_check_interval,
                "timeout": self.health_check_timeout,
                "retries": self.health_check_retries,
                "start_period": "90s"
            },
            "security_opt": [
                "no-new-privileges:true"
            ],
            "cap_drop": ["ALL"],
            "read_only": True,
            "tmpfs": [
                "/tmp:size=4G,mode=1777",
                "/app/temp:size=4G,mode=1777"
            ]
        }

    def generate_requirements_txt(self) -> str:
        """Generate fingerprinting engine requirements.txt"""
        return """# IA-Influencer Fingerprinting Engine - Production Dependencies
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Core Framework
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Audio Processing & Fingerprinting
librosa==0.10.1
soundfile==0.12.1
pyaudio==0.2.11
chromaprint==0.5
essentia==2.1b6.dev1110
aubio==0.4.9
madmom==0.16.1
mir_eval==0.7

# Video Processing
opencv-python==4.8.1.78
moviepy==1.0.3
ffmpeg-python==0.2.0
imageio==2.32.0
imageio-ffmpeg==0.4.9

# Image Processing & Computer Vision
pillow==10.1.0
imagehash==4.3.1
scikit-image==0.22.0
pytesseract==0.3.10

# Text Processing & NLP
spacy==3.7.2
nltk==3.8.1
sentence-transformers==2.2.2
textdistance==4.6.0
rapidfuzz==3.5.2

# AI & ML Models
torch==2.1.1
torchvision==0.16.1
torchaudio==2.1.1
transformers==4.36.0
clip-by-openai==1.0
timm==0.9.12

# Vector Databases & Search
faiss-cpu==1.7.4
qdrant-client==1.7.0
hnswlib==0.8.0
annoy==1.17.3

# Database & Storage
asyncpg==0.29.0
psycopg2-binary==2.9.9
redis[hiredis]==5.0.1
elasticsearch[async]==8.11.0

# Object Storage
boto3==1.34.0
minio==7.2.0

# Data Processing
numpy==1.25.2
pandas==2.1.4
scipy==1.11.4

# Hashing & Cryptography
xxhash==3.4.1
mmh3==4.1.0
hashlib-compat==0.1.0

# HTTP & Networking
httpx==0.25.2
aiohttp==3.9.1
grpcio==1.60.0
grpcio-tools==1.60.0

# File Processing
python-magic==0.4.27
python-magic-bin==0.4.14  # For Windows compatibility
filetype==1.2.0

# Monitoring & Metrics
prometheus-client==0.19.0
structlog==23.2.0

# Configuration & Validation
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Utilities
click==8.1.7
tqdm==4.66.1
psutil==5.9.6

# Serialization
orjson==3.9.10
msgpack==1.0.7
protobuf==4.25.1

# Caching
aiocache==0.12.2

# Job Queue
celery[redis]==5.3.4

# Testing (for development)
pytest==7.4.3
pytest-asyncio==0.21.1

# Performance
numba==0.58.1
joblib==1.3.2
"""
    def generate_model_download_script(self) -> str:
        """
Generate script to download fingerprinting models"""
        return """#!/usr/bin/env python3
\"\"\"
Fingerprinting Models Download Script - IA-Influencer-Agent
Creator: Fahed Mlaiel <mlaiel@live.de>
\"\"\"

import os
import sys
import argparse
from pathlib import Path
from transformers import AutoModel, AutoTokenizer, AutoProcessor, AutoFeatureExtractor
from sentence_transformers import SentenceTransformer
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_fingerprinting_models(cache_dir -> None: str) -> None:
    \"\"\"Download and cache fingerprinting models\"\"\"
    
    # Audio models
    audio_models = [
        "facebook/wav2vec2-base-960h",
        "facebook/wav2vec2-large-960h",
        "microsoft/speecht5_asr",
        "laion/clap-htsat-unfused",
        "laion/larger_clap_music"
    ]
    
    # Video models
    video_models = [
        "openai/clip-vit-base-patch32",
        "openai/clip-vit-large-patch14",
        "microsoft/resnet-50",
        "google/vit-base-patch16-224",
        "facebook/detr-resnet-50"
    ]
    
    # Image models
    image_models = [
        "openai/clip-vit-base-patch32",
        "google/vit-base-patch16-224",
        "microsoft/resnet-50",
        "facebook/dinov2-base",
        "facebook/dinov2-small"
    ]
    
    # Text models
    text_models = [
        "sentence-transformers/all-mpnet-base-v2",
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/multi-qa-mpnet-base-dot-v1",
        "bert-base-uncased",
        "roberta-base",
        "microsoft/DialoGPT-medium"
    ]
    
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    all_models = {
        "audio": audio_models,
        "video": video_models,
        "image": image_models,
        "text": text_models
    }
    
    for category, models in all_models.items():
        logger.info(f"Downloading {category} models...")
        category_path = cache_path / category
        category_path.mkdir(exist_ok=True)
        
        for model_name in models:
            try:
                logger.info(f"Downloading {model_name}...")
                
                # Download tokenizer/processor/feature extractor
                try:
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_name, 
                        cache_dir=str(category_path)
                    )
                    logger.info(f"✅ Downloaded tokenizer for {model_name}")
                except:
                    try:
                        processor = AutoProcessor.from_pretrained(
                            model_name,
                            cache_dir=str(category_path)
                        )
                        logger.info(f"✅ Downloaded processor for {model_name}")
                    except:
                        try:
                            feature_extractor = AutoFeatureExtractor.from_pretrained(
                                model_name,
                                cache_dir=str(category_path)
                            )
                            logger.info(f"✅ Downloaded feature extractor for {model_name}")
                        except:
                            logger.warning(f"⚠️ No tokenizer/processor/feature_extractor for {model_name}")
                
                # Download model
                model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=str(category_path),
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                logger.info(f"✅ Downloaded model {model_name}")
                
                # Clear memory
                del model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                logger.error(f"❌ Failed to download {model_name}: {e}")
    
    # Download sentence transformers models separately
    sentence_models = [
        "all-mpnet-base-v2",
        "all-MiniLM-L6-v2",
        "multi-qa-mpnet-base-dot-v1",
        "paraphrase-multilingual-mpnet-base-v2"
    ]
    
    sentence_path = cache_path / "sentence_transformers"
    sentence_path.mkdir(exist_ok=True)
    
    for model_name in sentence_models:
        try:
            logger.info(f"Downloading sentence transformer {model_name}...")
            model = SentenceTransformer(model_name, cache_folder=str(sentence_path))
            logger.info(f"✅ Downloaded sentence transformer {model_name}")
            del model
        except Exception as e:
            logger.error(f"❌ Failed to download sentence transformer {model_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download fingerprinting models")
    parser.add_argument("--cache-dir", required=True, help="Cache directory for models")
    args = parser.parse_args()
    
    download_fingerprinting_models(args.cache_dir)
    logger.info("✅ Fingerprinting model download completed")
"""
    def save_config_files(self, output_dir: str) -> List[str]:
        """
Save all configuration files to output directory"""
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
        
        # Save model download script
        download_script_path = config_dir / "download_fingerprint_models.py"
        with open(download_script_path, 'w') as f:
            f.write(self.generate_model_download_script())
        files_created.append(str(download_script_path))
        
        # Save docker-compose service config
        compose_config_path = config_dir / "docker-compose.fingerprinting.yml"
        service_config = {
            "version": "3.8",
            "services": {
                "fingerprinting-engine": self.generate_docker_compose_service()
            }
        }
        with open(compose_config_path, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False)
        files_created.append(str(compose_config_path))
        
        logger.info(f"✅ Fingerprinting Engine configuration files saved: {files_created}")
        return files_created
