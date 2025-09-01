"""🧠 AI Engines Docker Configuration - IA-Influencer-Agent Platform
==================================================================
Expert: ML Engineer + AI Specialist + Model Deployment Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional AI engines Docker configuration for advanced content
analysis, processing, and intelligent decision-making systems.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, field
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class AIEnginesDockerConfig:
    """
Enterprise AI Engines Docker configuration"""
    
    # Container Configuration
    image_name: str = "ia-influencer/ai-engines"
    image_tag: str = "2.0.0"
    container_name: str = "ia-influencer-ai-engines"
    
    # Application Configuration
    api_port: int = 8000
    grpc_port: int = 9000
    metrics_port: int = 9090
    
    # AI Model Configuration
    model_cache_size: str = "10Gi"
    max_batch_size: int = 32
    model_timeout: int = 300
    gpu_enabled: bool = True
    gpu_memory_fraction: float = 0.8
    
    # Performance Configuration
    workers: int = 2
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = 500
    max_requests_jitter: int = 50
    
    # Environment Configuration
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Model Configurations
    enabled_models: Dict[str, bool] = field(default_factory=lambda: {
        "audio_analysis": True,
        "video_analysis": True,
        "image_analysis": True,
        "text_analysis": True,
        "content_classification": True,
        "similarity_matching": True,
        "quality_assessment": True,
        "trend_prediction": True,
        "recommendation_engine": True,
        "sentiment_analysis": True
    })
    
    # AI Service URLs
    model_endpoints: Dict[str, str] = field(default_factory=lambda: {
        "huggingface_api": "https://api-inference.huggingface.co",
        "openai_api": "https://api.openai.com/v1",
        "stability_api": "https://api.stability.ai/v1",
        "anthropic_api": "https://api.anthropic.com/v1"
    })
    
    # Resource Limits
    cpu_limit: str = "8000m"
    memory_limit: str = "16Gi"
    gpu_limit: str = "1"
    cpu_request: str = "4000m"
    memory_request: str = "8Gi"
    
    # Storage Configuration
    model_storage_path: str = "/app/models"
    cache_storage_path: str = "/app/cache"
    temp_storage_path: str = "/app/temp"
    
    # Health Check Configuration
    health_check_enabled: bool = True
    health_check_interval: str = "60s"
    health_check_timeout: str = "30s"
    health_check_retries: int = 3
    
    def generate_dockerfile(self) -> str:
        """Generate production Dockerfile for AI Engines"""
        gpu_base = "nvidia/cuda:12.1-devel-ubuntu22.04" if self.gpu_enabled else "python:3.11-slim"
        
        return f"""# IA-Influencer AI Engines - Production Docker Image
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Professional AI/ML inference engines with GPU support

# Multi-stage build for optimization
FROM {gpu_base} AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.image_tag}"
LABEL service="ai-engines"
LABEL platform="IA-Influencer-Agent"
LABEL environment="{self.environment}"
LABEL gpu_enabled="{self.gpu_enabled}"

# System dependencies
{self._generate_system_dependencies()}

# Create non-root user
RUN groupadd -g 1001 aigroup && \\
    useradd -r -u 1001 -g aigroup aiuser

# Python environment setup
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# CUDA environment (if GPU enabled)
{self._generate_cuda_env() if self.gpu_enabled else ""}

WORKDIR /app

# Development stage
FROM base AS development
RUN pip install --upgrade pip
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Model preparation stage
FROM base AS model-prep
COPY download_models.py .
RUN python download_models.py --cache-dir={self.model_storage_path}

# Production stage
FROM base AS production

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy pre-downloaded models
COPY --from=model-prep --chown=aiuser:aigroup {self.model_storage_path} {self.model_storage_path}

# Copy application code
COPY --chown=aiuser:aigroup . .

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/temp /app/uploads && \\
    chown -R aiuser:aigroup /app && \\
    chmod -R 755 /app

# Environment variables
ENV ENVIRONMENT={self.environment}
ENV LOG_LEVEL={self.log_level}
ENV API_PORT={self.api_port}
ENV GRPC_PORT={self.grpc_port}
ENV METRICS_PORT={self.metrics_port}
ENV WORKERS={self.workers}
ENV WORKER_CLASS={self.worker_class}
ENV MAX_REQUESTS={self.max_requests}
ENV MAX_REQUESTS_JITTER={self.max_requests_jitter}
ENV MODEL_CACHE_SIZE={self.model_cache_size}
ENV MAX_BATCH_SIZE={self.max_batch_size}
ENV MODEL_TIMEOUT={self.model_timeout}
ENV GPU_ENABLED={str(self.gpu_enabled).lower()}
ENV GPU_MEMORY_FRACTION={self.gpu_memory_fraction}
ENV MODEL_STORAGE_PATH={self.model_storage_path}
ENV CACHE_STORAGE_PATH={self.cache_storage_path}
ENV TEMP_STORAGE_PATH={self.temp_storage_path}

# Model-specific environment variables
{self._generate_model_env_vars()}

# Switch to non-root user
USER aiuser

# Health check
HEALTHCHECK --interval={self.health_check_interval} \\
           --timeout={self.health_check_timeout} \\
           --start-period=120s \\
           --retries={self.health_check_retries} \\
    CMD curl -f http://localhost:{self.api_port}/health || exit 1

# Expose ports
EXPOSE {self.api_port}
EXPOSE {self.grpc_port}
EXPOSE {self.metrics_port}

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
    def _generate_system_dependencies(self) -> str:
        """
Generate system dependencies based on configuration"""
        if self.gpu_enabled:
            return """
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
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    pkg-config \\
    git \\
    python3 \\
    python3-pip \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean
"""
        else:
            return """
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
"""
    def _generate_cuda_env(self) -> str:
        """
Generate CUDA environment variables"""
        return f"""# CUDA environment
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV CUDA_CACHE_DISABLE=1
ENV CUDA_LAUNCH_BLOCKING=0
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
"""
    def _generate_model_env_vars(self) -> str:
        """
Generate model-specific environment variables"""
        env_vars = []
        for model, enabled in self.enabled_models.items():
            env_vars.append(f"ENV MODEL_{model.upper()}_ENABLED={str(enabled).lower()}")
        
        for endpoint_name, url in self.model_endpoints.items():
            env_vars.append(f"ENV {endpoint_name.upper()}_URL={url}")
        
        return "\n".join(env_vars)

    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate docker-compose service configuration"""
        service_config = {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": self.container_name,
            "restart": "unless-stopped",
            "ports": [
                f"{self.api_port}:{self.api_port}",
                f"{self.grpc_port}:{self.grpc_port}",
                f"{self.metrics_port}:{self.metrics_port}"
            ],
            "environment": {
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": self.log_level,
                "DEBUG": str(self.debug_mode).lower(),
                "API_PORT": str(self.api_port),
                "GRPC_PORT": str(self.grpc_port),
                "METRICS_PORT": str(self.metrics_port),
                "WORKERS": str(self.workers),
                "WORKER_CLASS": self.worker_class,
                "MAX_REQUESTS": str(self.max_requests),
                "MAX_REQUESTS_JITTER": str(self.max_requests_jitter),
                "MODEL_CACHE_SIZE": self.model_cache_size,
                "MAX_BATCH_SIZE": str(self.max_batch_size),
                "MODEL_TIMEOUT": str(self.model_timeout),
                "GPU_ENABLED": str(self.gpu_enabled).lower(),
                "GPU_MEMORY_FRACTION": str(self.gpu_memory_fraction),
                "MODEL_STORAGE_PATH": self.model_storage_path,
                "CACHE_STORAGE_PATH": self.cache_storage_path,
                "TEMP_STORAGE_PATH": self.temp_storage_path,
                **{f"MODEL_{k.upper()}_ENABLED": str(v).lower() for k, v in self.enabled_models.items()},
                **{f"{k.upper()}_URL": v for k, v in self.model_endpoints.items()}
            },
            "volumes": [
                "./logs/ai-engines:/app/logs",
                "./models:/app/models",
                "./cache/ai-engines:/app/cache",
                "./config/ai-engines:/app/config:ro",
                "/tmp:/app/temp"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "redis"
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
                "start_period": "120s"
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
        
        # Add GPU configuration if enabled
        if self.gpu_enabled:
            service_config["runtime"] = "nvidia"
            service_config["deploy"]["resources"]["reservations"]["devices"] = [
                {
                    "driver": "nvidia",
                    "count": 1,
                    "capabilities": ["gpu"]
                }
            ]
        
        return service_config

    def generate_requirements_txt(self) -> str:
        """Generate AI engines requirements.txt"""
        base_requirements = """# IA-Influencer AI Engines - Production Dependencies
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Core Framework
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# AI & ML Core
torch==2.1.1
torchvision==0.16.1
torchaudio==2.1.1
transformers==4.36.0
tokenizers==0.15.0
accelerate==0.25.0
diffusers==0.25.0

# Computer Vision
opencv-python==4.8.1.78
pillow==10.1.0
imagehash==4.3.1
scikit-image==0.22.0

# Audio Processing
librosa==0.10.1
soundfile==0.12.1
pyaudio==0.2.11
chromaprint==0.5
essentia==2.1b6.dev1110

# Video Processing
moviepy==1.0.3
ffmpeg-python==0.2.0

# Natural Language Processing
spacy==3.7.2
nltk==3.8.1
sentence-transformers==2.2.2
textdistance==4.6.0

# Machine Learning
scikit-learn==1.3.2
xgboost==2.0.2
lightgbm==4.1.0
catboost==1.2.2

# Data Processing
numpy==1.25.2
pandas==2.1.4
scipy==1.11.4

# Vector Search & Similarity
faiss-cpu==1.7.4
hnswlib==0.8.0

# HTTP & API
httpx==0.25.2
aiohttp==3.9.1
grpcio==1.60.0
grpcio-tools==1.60.0

# Monitoring & Metrics
prometheus-client==0.19.0
structlog==23.2.0

# Configuration
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

# Caching
aiocache==0.12.2
redis==5.0.1

# Model Optimization
onnx==1.15.0
onnxruntime==1.16.3
openvino==2023.2.0
"""
        
        # Add GPU-specific requirements if enabled
        if self.gpu_enabled:
            gpu_requirements = """# GPU-specific dependencies
torch==2.1.1+cu121
torchvision==0.16.1+cu121
torchaudio==2.1.1+cu121
faiss-gpu==1.7.4
onnxruntime-gpu==1.16.3
"""
            base_requirements += gpu_requirements
        
        return base_requirements

    def generate_model_download_script(self) -> str:
        """
Generate script to download AI models"""
        return """#!/usr/bin/env python3
\"\"\"
AI Models Download Script - IA-Influencer-Agent
Creator: Fahed Mlaiel <mlaiel@live.de>
\"\"\"

import os
import sys
import argparse
from pathlib import Path
from transformers import AutoModel, AutoTokenizer, AutoProcessor
from sentence_transformers import SentenceTransformer
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models(cache_dir: str):
    \"\"\"Download and cache AI models\"\"\"
    models_to_download = [
        # Text models
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
        "microsoft/DialoGPT-medium",
        "distilbert-base-uncased",
        
        # Vision models
        "microsoft/resnet-50",
        "google/vit-base-patch16-224",
        "facebook/detr-resnet-50",
        
        # Audio models
        "facebook/wav2vec2-base-960h",
        "microsoft/speecht5_tts",
        
        # Multimodal models
        "openai/clip-vit-base-patch32",
        "microsoft/git-base",
        
        # Classification models
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "unitary/toxic-bert",
    ]
    
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    for model_name in models_to_download:
        try:
            logger.info(f"Downloading {model_name}...")
            
            # Download tokenizer/processor
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    cache_dir=cache_dir
                )
                logger.info(f"✅ Downloaded tokenizer for {model_name}")
            except:
                try:
                    processor = AutoProcessor.from_pretrained(
                        model_name,
                        cache_dir=cache_dir
                    )
                    logger.info(f"✅ Downloaded processor for {model_name}")
                except:
                    logger.warning(f"⚠️ No tokenizer/processor for {model_name}")
            
            # Download model
            model = AutoModel.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            logger.info(f"✅ Downloaded model {model_name}")
            
            # Clear memory
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")
    
    # Download sentence transformers models
    sentence_models = [
        "all-MiniLM-L6-v2",
        "all-mpnet-base-v2",
        "multi-qa-mpnet-base-dot-v1"
    ]
    
    for model_name in sentence_models:
        try:
            logger.info(f"Downloading sentence transformer {model_name}...")
            model = SentenceTransformer(model_name, cache_folder=cache_dir)
            logger.info(f"✅ Downloaded sentence transformer {model_name}")
            del model
        except Exception as e:
            logger.error(f"❌ Failed to download sentence transformer {model_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download AI models")
    parser.add_argument("--cache-dir", required=True, help="Cache directory for models")
    args = parser.parse_args()
    
    download_models(args.cache_dir)
    logger.info("✅ Model download completed")
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
        download_script_path = config_dir / "download_models.py"
        with open(download_script_path, 'w') as f:
            f.write(self.generate_model_download_script())
        files_created.append(str(download_script_path))
        
        # Save docker-compose service config
        compose_config_path = config_dir / "docker-compose.ai-engines.yml"
        service_config = {
            "version": "3.8",
            "services": {
                "ai-engines": self.generate_docker_compose_service()
            }
        }
        with open(compose_config_path, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False)
        files_created.append(str(compose_config_path))
        
        logger.info(f"✅ AI Engines configuration files saved: {files_created}")
        return files_created
