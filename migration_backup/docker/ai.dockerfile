# =============================================================================
# AINFLUE AI SERVICE - OPTIMIZED PRODUCTION DOCKERFILE
# =============================================================================
# Multi-stage Docker build optimized for AI/ML workloads with GPU support,
# model caching, and enterprise security features.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG CUDA_VERSION=11.8
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: BASE WITH GPU SUPPORT
# =============================================================================
FROM nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu22.04 AS gpu-base

LABEL stage=gpu-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="GPU-enabled base for AI services"

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        # AI/ML system dependencies
        build-essential \
        pkg-config \
        # Audio processing
        ffmpeg \
        libsndfile1 \
        libsndfile1-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libavutil-dev \
        # Computer vision
        libopencv-dev \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
        # CUDA libraries
        libcublas-11-8 \
        libcudnn8 \
        # Monitoring
        curl \
        htop \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create symbolic link for python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python

# Security: Create non-root user
RUN groupadd --gid 10001 aiservice && \
    useradd --uid 10001 --gid aiservice \
            --home-dir /home/aiservice \
            --create-home \
            --shell /bin/bash \
            aiservice

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM gpu-base AS ai-dependencies

LABEL stage=ai-dependencies
LABEL description="AI/ML Python dependencies installation"

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade \
    pip==23.3.1 \
    setuptools==68.2.2 \
    wheel==0.41.2

# Copy requirements
WORKDIR /build
COPY requirements.txt ./
COPY requirements-ai.txt ./

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir \
    torch==2.1.0+cu118 \
    torchvision==0.16.0+cu118 \
    torchaudio==2.1.0+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

# Install AI/ML specific dependencies
RUN pip install --no-cache-dir \
    transformers==4.35.0 \
    accelerate==0.24.0 \
    datasets==2.14.0 \
    tokenizers==0.14.1 \
    sentencepiece==0.1.99 \
    # Computer vision
    opencv-python-headless==4.8.1.78 \
    Pillow==10.0.1 \
    scikit-image==0.21.0 \
    # Audio processing
    librosa==0.10.1 \
    soundfile==0.12.1 \
    resampy==0.4.2 \
    # Scientific computing
    numpy==1.24.3 \
    scipy==1.11.3 \
    scikit-learn==1.3.0 \
    pandas==2.1.1 \
    # Model serving
    fastapi==0.104.1 \
    uvicorn==0.24.0

# Install main requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install AI-specific requirements if they exist
RUN if [ -f requirements-ai.txt ]; then \
        pip install --no-cache-dir -r requirements-ai.txt; \
    fi

# Clean up pip cache
RUN pip cache purge

# =============================================================================
# STAGE 3: MODEL DOWNLOADER
# =============================================================================
FROM ai-dependencies AS model-downloader

LABEL stage=model-downloader
LABEL description="Pre-download AI models for faster startup"

ENV PATH="/opt/venv/bin:$PATH"

# Create model directory
RUN mkdir -p /models

# Pre-download common models (optional, controlled by build arg)
ARG PRELOAD_MODELS=false
RUN if [ "$PRELOAD_MODELS" = "true" ]; then \
        python -c "\
import transformers; \
import torch; \
models = ['distilbert-base-uncased', 'microsoft/DialoGPT-medium', 'facebook/wav2vec2-base-960h']; \
[print(f'Downloading {model}...') or ( \
    __import__('transformers').Wav2Vec2Processor.from_pretrained(model) and \
    __import__('transformers').Wav2Vec2Model.from_pretrained(model) \
    if 'wav2vec' in model else \
    __import__('transformers').AutoTokenizer.from_pretrained(model) and \
    __import__('transformers').AutoModel.from_pretrained(model) \
) and print(f'Successfully downloaded {model}') for model in models]"; \
    fi

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM gpu-base AS production

LABEL stage=production
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue AI Service - Production Runtime"
LABEL service="ai-service"
LABEL gpu.enabled=true

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # AI Service specific
    AI_SERVICE=true \
    CUDA_VISIBLE_DEVICES=0 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    # Performance settings
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    TOKENIZERS_PARALLELISM=false \
    TRANSFORMERS_CACHE=/app/models/transformers \
    TORCH_HOME=/app/models/torch \
    # Service settings
    SERVICE_PORT=8004 \
    MAX_WORKERS=2 \
    MODEL_CACHE_SIZE=8GB

# Remove build dependencies, keep runtime
RUN apt-get remove -y \
        build-essential \
        python3.11-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from dependencies stage
COPY --from=ai-dependencies /opt/venv /opt/venv

# Copy pre-downloaded models if available
COPY --from=model-downloader /models /app/models/

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=aiservice:aiservice . .

# Create necessary directories with proper permissions
RUN mkdir -p \
        /app/models/transformers \
        /app/models/torch \
        /app/models/custom \
        /app/processed \
        /app/temp \
        /app/logs \
        /app/cache \
    && chown -R aiservice:aiservice /app \
    && chmod -R 755 /app \
    && chmod -R 777 /app/models /app/processed /app/temp /app/logs /app/cache

# Create AI service startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "=== AI Service Starting ==="\n\
echo "CUDA Available: $(python -c \"import torch; print(torch.cuda.is_available())\")"\n\
echo "GPU Count: $(python -c \"import torch; print(torch.cuda.device_count() if torch.cuda.is_available() else 0)\")"\n\
echo "Service Port: ${SERVICE_PORT}"\n\
echo "Max Workers: ${MAX_WORKERS}"\n\
echo "=============================="\n\
\n\
# GPU memory optimization\n\
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512\n\
\n\
# Start AI service\n\
exec python -m uvicorn ai_engine.service:app \\\n\
    --host 0.0.0.0 \\\n\
    --port ${SERVICE_PORT} \\\n\
    --workers ${MAX_WORKERS} \\\n\
    --worker-class uvicorn.workers.UvicornWorker \\\n\
    --log-level info \\\n\
    --access-log\n\
' > /app/start-ai.sh && chmod +x /app/start-ai.sh

# Switch to non-root user
USER aiservice

# Expose service port
EXPOSE 8004

# Health check with GPU and model validation
HEALTHCHECK --interval=45s \
            --timeout=20s \
            --start-period=120s \
            --retries=3 \
            CMD curl -f http://localhost:8004/health \
                && python -c "import torch; import sys; print(f'CUDA Available: {torch.cuda.is_available()}'); [print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB') and print(f'GPU Memory Used: {torch.cuda.memory_allocated(0) / 1024**3:.1f}GB') if torch.cuda.is_available() else None]; sys.exit(0)" || exit 1

# Start AI service
CMD ["/app/start-ai.sh"]