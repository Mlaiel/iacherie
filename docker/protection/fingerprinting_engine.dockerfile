# =============================================================================
# AINFLUE FINGERPRINTING ENGINE - SPECIALIZED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced digital fingerprinting supporting
# audio, video, image, and document fingerprinting with ML-based similarity.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: FINGERPRINTING BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS fingerprint-base

LABEL stage=fingerprint-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced digital fingerprinting engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install fingerprinting dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        build-essential \
        pkg-config \
        curl \
        wget \
        git \
        # Audio fingerprinting
        ffmpeg \
        libsndfile1-dev \
        libavcodec-dev \
        libavformat-dev \
        # Image fingerprinting
        libopencv-dev \
        libjpeg-dev \
        libpng-dev \
        imagemagick \
        # Video fingerprinting
        libx264-dev \
        libx265-dev \
        # Document processing
        poppler-utils \
        tesseract-ocr \
        libtesseract-dev \
        # ML dependencies
        libblas-dev \
        liblapack-dev \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user
RUN groupadd -r fingerprintuser && \
    useradd -r -g fingerprintuser -d /app -s /bin/bash fingerprintuser && \
    mkdir -p /app && \
    chown -R fingerprintuser:fingerprintuser /app

# =============================================================================
# STAGE 2: FINGERPRINTING MODELS
# =============================================================================
FROM fingerprint-base AS fingerprint-deps

# Install specialized fingerprinting libraries
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        # Core libraries
        numpy \
        scipy \
        matplotlib \
        # Audio fingerprinting
        librosa \
        soundfile \
        pydub \
        dejavu-python \
        chromaprint \
        # Image fingerprinting
        opencv-python \
        pillow \
        imagehash \
        scikit-image \
        # Video fingerprinting
        moviepy \
        # Document fingerprinting
        pytesseract \
        pdf2image \
        pypdf2 \
        # Machine learning
        torch \
        torchvision \
        scikit-learn \
        faiss-cpu \
        # Hashing algorithms
        hashlib \
        mmh3 \
        xxhash \
        # Web framework
        fastapi \
        uvicorn \
        pydantic \
        celery \
        redis \
        psycopg2-binary \
        SQLAlchemy \
        # Monitoring
        prometheus-client \
        structlog

# Download pre-trained models for content fingerprinting
RUN python3.11 -c "import torch; torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)"

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM fingerprint-deps AS fingerprint-app

WORKDIR /app

# Copy application code
COPY ./fingerprinting_engine /app/fingerprinting_engine
COPY ./core /app/core
COPY ./config /app/config

# Create fingerprinting directories
RUN mkdir -p /app/storage/fingerprints/audio \
             /app/storage/fingerprints/video \
             /app/storage/fingerprints/image \
             /app/storage/fingerprints/document \
             /app/storage/fingerprints/database \
             /app/storage/fingerprints/temp \
             /app/logs \
             /app/cache \
             /app/models/audio \
             /app/models/video \
             /app/models/image && \
    chown -R fingerprintuser:fingerprintuser /app

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM fingerprint-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/fingerprinting_engine/start.sh

USER fingerprintuser

# Fingerprinting environment variables
ENV FINGERPRINT_SERVICE_PORT=8021
ENV FINGERPRINT_WORKERS=4
ENV MAX_FILE_SIZE=5GB
ENV PROCESSING_TIMEOUT=900
# Audio fingerprinting
ENV AUDIO_SAMPLE_RATE=22050
ENV AUDIO_FRAME_SIZE=2048
ENV AUDIO_HOP_LENGTH=512
# Image fingerprinting
ENV IMAGE_HASH_SIZE=64
ENV IMAGE_RESIZE_TARGET=256
# Video fingerprinting
ENV VIDEO_FPS=1
ENV VIDEO_FRAME_INTERVAL=30
# Document fingerprinting
ENV OCR_LANGUAGE=eng
ENV OCR_CONFIG=--psm 6
# Database settings
ENV SIMILARITY_THRESHOLD=0.85
ENV INDEX_UPDATE_INTERVAL=300
ENV CACHE_TTL=7200

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:${FINGERPRINT_SERVICE_PORT}/health || exit 1

EXPOSE ${FINGERPRINT_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

CMD ["python3.11", "-m", "fingerprinting_engine.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM fingerprint-app AS development

RUN python3.11 -m pip install --no-cache-dir \
        pytest \
        pytest-asyncio \
        pytest-cov \
        black \
        isort \
        flake8 \
        mypy \
        ipython \
        jupyter \
        debugpy \
        # Visualization tools
        plotly \
        seaborn \
        streamlit

ENV FINGERPRINT_SERVICE_PORT=8021
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER fingerprintuser

HEALTHCHECK --interval=60s --timeout=20s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${FINGERPRINT_SERVICE_PORT}/health || exit 1

EXPOSE ${FINGERPRINT_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

CMD ["python3.11", "-m", "fingerprinting_engine.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Fingerprinting Engine"
LABEL org.opencontainers.image.description="Advanced multi-format digital fingerprinting service"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="fingerprinting_engine"
LABEL ainflue.service.port="8021"
LABEL ainflue.fingerprinting.formats="audio,video,image,document"
LABEL ainflue.security.non-root="true"