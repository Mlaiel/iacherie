# =============================================================================
# AINFLUE PROTECTION SERVICE - MAIN DOCKERFILE
# =============================================================================
# Multi-stage Docker build for comprehensive content protection and rights
# management including fingerprinting, watermarking, and monitoring.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: PROTECTION BASE ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS protection-base

LABEL stage=protection-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Content protection and rights management service"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for content protection
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        build-essential \
        pkg-config \
        curl \
        wget \
        git \
        # Media processing libraries
        ffmpeg \
        imagemagick \
        libopencv-dev \
        libmagickwand-dev \
        # Audio/video analysis
        libsndfile1-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        # Image processing
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libwebp-dev \
        # Cryptographic libraries
        libssl-dev \
        libffi-dev \
        # Document processing
        poppler-utils \
        tesseract-ocr \
        # System utilities
        sqlite3 \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r protectionuser && \
    useradd -r -g protectionuser -d /app -s /bin/bash protectionuser && \
    mkdir -p /app && \
    chown -R protectionuser:protectionuser /app

# =============================================================================
# STAGE 2: PROTECTION DEPENDENCIES
# =============================================================================
FROM protection-base AS protection-deps

# Install Python dependencies for content protection
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        # Core libraries
        numpy \
        scipy \
        pillow \
        opencv-python \
        matplotlib \
        # Audio processing
        librosa \
        soundfile \
        pydub \
        # Image processing
        scikit-image \
        imageio \
        # Cryptography
        cryptography \
        hashlib \
        pycryptodome \
        # Blockchain
        web3 \
        eth-hash \
        # Machine learning
        torch \
        torchvision \
        scikit-learn \
        # Web framework
        fastapi \
        uvicorn \
        pydantic \
        celery \
        redis \
        psycopg2-binary \
        SQLAlchemy \
        alembic \
        # Monitoring
        prometheus-client \
        structlog \
        # File handling
        aiofiles \
        python-multipart \
        # Security
        passlib \
        python-jose \
        bcrypt

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM protection-deps AS protection-app

WORKDIR /app

# Copy application code
COPY ./protection /app/protection
COPY ./core /app/core
COPY ./config /app/config

# Create protection-specific directories
RUN mkdir -p /app/storage/protection/uploads \
             /app/storage/protection/fingerprints \
             /app/storage/protection/watermarks \
             /app/storage/protection/reports \
             /app/storage/protection/evidence \
             /app/storage/protection/quarantine \
             /app/logs \
             /app/cache \
             /app/models \
             /app/keys && \
    chown -R protectionuser:protectionuser /app

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM protection-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/protection/start.sh \
    && chmod 700 /app/keys

USER protectionuser

# Protection service environment variables
ENV PROTECTION_SERVICE_PORT=8020
ENV PROTECTION_WORKERS=4
ENV MAX_FILE_SIZE=2GB
ENV PROCESSING_TIMEOUT=600
# Fingerprinting settings
ENV FINGERPRINT_ALGORITHM=perceptual_hash
ENV HASH_SIZE=64
ENV SIMILARITY_THRESHOLD=0.85
# Watermarking settings
ENV WATERMARK_STRENGTH=0.1
ENV WATERMARK_TYPE=invisible
# Monitoring settings
ENV SCAN_INTERVAL=300
ENV VIOLATION_THRESHOLD=0.9
# Security settings
ENV ENCRYPTION_ALGORITHM=AES-256
ENV KEY_ROTATION_INTERVAL=86400
ENV CACHE_TTL=3600

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PROTECTION_SERVICE_PORT}/health || exit 1

EXPOSE ${PROTECTION_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models", "/app/keys"]

CMD ["python3.11", "-m", "protection.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM protection-app AS development

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
        # Additional dev tools
        streamlit \
        plotly \
        seaborn

ENV PROTECTION_SERVICE_PORT=8020
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER protectionuser

HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${PROTECTION_SERVICE_PORT}/health || exit 1

EXPOSE ${PROTECTION_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models", "/app/keys"]

CMD ["python3.11", "-m", "protection.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Protection Service"
LABEL org.opencontainers.image.description="Content protection and rights management service"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="protection_service"
LABEL ainflue.service.port="8020"
LABEL ainflue.protection.features="fingerprinting,watermarking,monitoring"
LABEL ainflue.security.non-root="true"
LABEL ainflue.security.encrypted="true"