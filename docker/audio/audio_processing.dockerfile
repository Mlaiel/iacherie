# =============================================================================
# AINFLUE AUDIO PROCESSING ENGINE - PROFESSIONAL DOCKERFILE
# =============================================================================
# Multi-stage Docker build for professional audio processing with DEMUCS
# source separation, EBU R128 compliance, and enterprise security features.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: BASE AUDIO PROCESSING ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS audio-base

LABEL stage=audio-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Audio processing base with professional tools"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for audio processing
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
        # Audio processing libraries
        ffmpeg \
        sox \
        libsox-fmt-all \
        libsndfile1 \
        libsndfile1-dev \
        libsamplerate0 \
        libsamplerate0-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libswscale-dev \
        libswresample-dev \
        # Audio analysis tools
        libaudiofile-dev \
        libmp3lame-dev \
        libvorbis-dev \
        libflac-dev \
        libopus-dev \
        # Professional audio standards
        lilv-utils \
        lv2-dev \
        liblilv-dev \
        # System utilities
        htop \
        procps \
        net-tools \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r audiouser && \
    useradd -r -g audiouser -d /app -s /bin/bash audiouser && \
    mkdir -p /app && \
    chown -R audiouser:audiouser /app

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES AND AUDIO MODELS
# =============================================================================
FROM audio-base AS audio-deps

# Install Python dependencies for audio processing
COPY requirements-audio.txt /tmp/requirements-audio.txt
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    python3.11 -m pip install --no-cache-dir \
        demucs \
        librosa \
        soundfile \
        pydub \
        scipy \
        numpy \
        scikit-learn \
        matplotlib \
        seaborn \
        pyloudnorm \
        essentia \
        aubio \
        madmom \
        pyrubberband \
        resampy \
        pedalboard \
        jams \
        mido \
        pretty_midi \
        fastapi \
        uvicorn \
        pydantic \
        celery \
        redis \
        psycopg2-binary \
        SQLAlchemy \
        alembic \
        prometheus-client \
        structlog \
        asyncio-mqtt

# Download and cache DEMUCS models
RUN python3.11 -c "import demucs.api; demucs.api.separator.load_model('htdemucs')"

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM audio-deps AS audio-app

WORKDIR /app

# Copy application code
COPY ./audio_processing /app/audio_processing
COPY ./core /app/core
COPY ./config /app/config

# Create necessary directories
RUN mkdir -p /app/storage/audio/input \
             /app/storage/audio/output \
             /app/storage/audio/processed \
             /app/storage/audio/separated \
             /app/storage/audio/mastered \
             /app/logs \
             /app/cache \
             /app/models && \
    chown -R audiouser:audiouser /app

# =============================================================================
# STAGE 4: PRODUCTION OPTIMIZED
# =============================================================================
FROM audio-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/audio_processing/start.sh

# Switch to non-root user
USER audiouser

# Environment variables
ENV AUDIO_SERVICE_PORT=8010
ENV AUDIO_WORKERS=4
ENV AUDIO_MAX_FILE_SIZE=500MB
ENV AUDIO_PROCESSING_TIMEOUT=300
ENV DEMUCS_MODEL=htdemucs
ENV SAMPLE_RATE=44100
ENV BIT_DEPTH=24
ENV LOUDNESS_TARGET=-23.0
ENV CACHE_TTL=3600

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${AUDIO_SERVICE_PORT}/health || exit 1

# Expose service port
EXPOSE ${AUDIO_SERVICE_PORT}

# Volume mounts
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

# Start command
CMD ["python3.11", "-m", "audio_processing.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT WITH DEBUGGING
# =============================================================================
FROM audio-app AS development

# Install development tools
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
        debugpy

# Development environment variables  
ENV AUDIO_SERVICE_PORT=8010
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER audiouser

# Development health check
HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${AUDIO_SERVICE_PORT}/health || exit 1

EXPOSE ${AUDIO_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

# Development start with auto-reload
CMD ["python3.11", "-m", "audio_processing.main", "--reload"]

# =============================================================================
# METADATA AND LABELS
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Audio Processing Engine"
LABEL org.opencontainers.image.description="Professional audio processing with DEMUCS separation and broadcast standards"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL org.opencontainers.image.documentation="https://docs.ainflue.com/audio-processing"
LABEL org.opencontainers.image.licenses="Proprietary"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="audio_processing"
LABEL ainflue.service.port="8010"
LABEL ainflue.security.non-root="true"
LABEL ainflue.performance.optimized="true"