# =============================================================================
# AINFLUE SOURCE SEPARATION SERVICE - SPECIALIZED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced audio source separation using
# DEMUCS, Spleeter, and other state-of-the-art models.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: SOURCE SEPARATION BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS separation-base

LABEL stage=separation-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced audio source separation service"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
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
        # Audio processing
        ffmpeg \
        sox \
        libsndfile1-dev \
        libsamplerate0-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        # ML dependencies
        libblas-dev \
        liblapack-dev \
        libatlas-base-dev \
        gfortran \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user
RUN groupadd -r sepuser && \
    useradd -r -g sepuser -d /app -s /bin/bash sepuser && \
    mkdir -p /app && \
    chown -R sepuser:sepuser /app

# =============================================================================
# STAGE 2: MACHINE LEARNING MODELS
# =============================================================================
FROM separation-base AS separation-models

# Install Python ML dependencies
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    python3.11 -m pip install --no-cache-dir \
        demucs \
        spleeter \
        librosa \
        soundfile \
        numpy \
        scipy \
        scikit-learn \
        tensorflow \
        norbert \
        asteroid \
        fastapi \
        uvicorn \
        pydantic \
        celery \
        redis \
        psycopg2-binary \
        SQLAlchemy \
        prometheus-client \
        structlog

# Pre-download separation models
RUN python3.11 -c "import demucs.api; demucs.api.separator.load_model('htdemucs')" && \
    python3.11 -c "import demucs.api; demucs.api.separator.load_model('htdemucs_ft')" && \
    python3.11 -c "import demucs.api; demucs.api.separator.load_model('mdx_extra')" && \
    python3.11 -c "import spleeter; from spleeter.separator import Separator; Separator('spleeter:2stems-16kHz')" && \
    python3.11 -c "import spleeter; from spleeter.separator import Separator; Separator('spleeter:4stems-16kHz')" && \
    python3.11 -c "import spleeter; from spleeter.separator import Separator; Separator('spleeter:5stems-16kHz')"

# =============================================================================
# STAGE 3: APPLICATION LAYER
# =============================================================================
FROM separation-models AS separation-app

WORKDIR /app

# Copy application code
COPY ./source_separation /app/source_separation
COPY ./core /app/core
COPY ./config /app/config

# Create directories
RUN mkdir -p /app/storage/separation/input \
             /app/storage/separation/output \
             /app/storage/separation/vocals \
             /app/storage/separation/drums \
             /app/storage/separation/bass \
             /app/storage/separation/other \
             /app/logs \
             /app/cache \
             /app/models/demucs \
             /app/models/spleeter && \
    chown -R sepuser:sepuser /app

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM separation-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/source_separation/start.sh

USER sepuser

# Environment variables
ENV SEPARATION_SERVICE_PORT=8011
ENV SEPARATION_WORKERS=2
ENV MAX_AUDIO_LENGTH=600
ENV DEMUCS_MODEL=htdemucs
ENV SPLEETER_MODEL=spleeter:4stems-16kHz
ENV CHUNK_DURATION=60
ENV OVERLAP_DURATION=5
ENV SAMPLE_RATE=44100
ENV OUTPUT_FORMAT=wav
ENV CACHE_TTL=7200

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:${SEPARATION_SERVICE_PORT}/health || exit 1

EXPOSE ${SEPARATION_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

CMD ["python3.11", "-m", "source_separation.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM separation-app AS development

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
        matplotlib \
        seaborn

ENV SEPARATION_SERVICE_PORT=8011
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER sepuser

HEALTHCHECK --interval=60s --timeout=20s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${SEPARATION_SERVICE_PORT}/health || exit 1

EXPOSE ${SEPARATION_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

CMD ["python3.11", "-m", "source_separation.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Source Separation Service"
LABEL org.opencontainers.image.description="Advanced audio source separation with DEMUCS and Spleeter"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="source_separation"
LABEL ainflue.service.port="8011"
LABEL ainflue.security.non-root="true"