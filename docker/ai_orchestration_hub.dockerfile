# AI Orchestration Hub Service
# Advanced AI service coordination and multi-provider management
# Author: Fahed Mlaiel (mlaiel@live.de) - Lead Developer IA Role

FROM python:3.11-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue AI Orchestration Hub - Advanced AI service coordination"
LABEL version="1.0.0"

# Install AI and ML system dependencies
RUN apt-get update && apt-get install -y \
    # Core development tools
    build-essential \
    curl \
    wget \
    git \
    # AI/ML libraries dependencies
    libgomp1 \
    libomp-dev \
    libopenblas-dev \
    liblapack-dev \
    # GPU support
    ocl-icd-opencl-dev \
    # Image/Video processing for AI
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    # Audio processing for AI
    libsndfile1-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install comprehensive AI libraries
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    # Core AI frameworks
    torch torchvision torchaudio \
    tensorflow \
    transformers \
    # Multi-provider AI APIs
    openai \
    anthropic \
    google-generativeai \
    cohere \
    # Computer Vision AI
    opencv-python \
    pillow \
    scikit-image \
    # Audio AI
    librosa \
    speechrecognition \
    pydub \
    # NLP AI
    spacy \
    nltk \
    textblob \
    # AI orchestration
    langchain \
    llamaindex \
    # Model serving
    ray[serve] \
    bentoml \
    # Monitoring and logging
    mlflow \
    wandb \
    # Async processing
    asyncio \
    aiohttp \
    websockets \
    # Performance
    numba \
    accelerate

# Download essential NLP models
RUN python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" && \
    python3 -c "import spacy; spacy.cli.download('en_core_web_sm')"

# Copy AI orchestration source code
COPY ./ai_orchestration/ ./orchestration/
COPY ./ai_services/common/ ./common/

# Security: Create AI orchestration user
RUN groupadd --gid 1000 aiorchestrator && \
    useradd --uid 1000 --gid aiorchestrator --shell /bin/bash --create-home aiorchestrator

# Create AI directories
RUN mkdir -p \
    /app/models \
    /app/cache \
    /app/logs \
    /app/temp \
    /app/providers \
    /app/workflows \
    /app/monitoring \
    && chown -R aiorchestrator:aiorchestrator /app \
    && chmod 755 /app

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to AI orchestration user
USER aiorchestrator

# AI orchestration environment variables
ENV PYTHONPATH=/app \
    SERVICE_NAME=ai_orchestration_hub \
    AI_CACHE_SIZE=1000 \
    MAX_CONCURRENT_REQUESTS=10 \
    MODEL_CACHE_TTL=3600 \
    INFERENCE_TIMEOUT=30 \
    CUDA_VISIBLE_DEVICES=0

# Health check for AI orchestration service
HEALTHCHECK --interval=60s --timeout=30s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/ai/health').raise_for_status()" || exit 1

EXPOSE 8000

# Start AI orchestration hub
CMD ["python3", "-m", "uvicorn", "orchestration.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info", \
     "--timeout-keep-alive", "30"]