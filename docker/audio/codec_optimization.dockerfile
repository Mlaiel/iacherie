# =============================================================================
# AINFLUE CODEC OPTIMIZATION ENGINE - PROFESSIONAL DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced codec optimization including
# MP3, FLAC, OPUS, AAC, OGG and modern codecs with quality optimization.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: CODEC BASE ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS codec-base

LABEL stage=codec-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced codec optimization service"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install codec libraries and tools
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
        # Core audio processing
        ffmpeg \
        sox \
        libsox-fmt-all \
        # Codec libraries
        libmp3lame-dev \
        libvorbis-dev \
        libflac-dev \
        libopus-dev \
        libaac-dev \
        libfdk-aac-dev \
        libx264-dev \
        libx265-dev \
        # Audio file format support
        libsndfile1-dev \
        libsamplerate0-dev \
        libaudiofile-dev \
        # Advanced codecs
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libswscale-dev \
        libswresample-dev \
        # Quality analysis tools
        libebur128-dev \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user
RUN groupadd -r codecuser && \
    useradd -r -g codecuser -d /app -s /bin/bash codecuser && \
    mkdir -p /app && \
    chown -R codecuser:codecuser /app

# =============================================================================
# STAGE 2: CODEC OPTIMIZATION TOOLS
# =============================================================================
FROM codec-base AS codec-deps

# Install Python packages for codec optimization
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        librosa \
        soundfile \
        pydub \
        mutagen \
        numpy \
        scipy \
        matplotlib \
        # Audio quality assessment
        pyloudnorm \
        essentia \
        aubio \
        # Advanced processing
        pedalboard \
        resampy \
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
        structlog \
        # File handling
        pathlib \
        aiofiles

# Install additional codec tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Advanced audio encoders
        vorbis-tools \
        flac \
        opus-tools \
        lame \
        # Quality measurement
        bs1770gain \
        && rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM codec-deps AS codec-app

WORKDIR /app

# Copy application code
COPY ./codec_optimization /app/codec_optimization
COPY ./core /app/core
COPY ./config /app/config

# Create codec-specific directories
RUN mkdir -p /app/storage/codec/input \
             /app/storage/codec/output \
             /app/storage/codec/mp3 \
             /app/storage/codec/flac \
             /app/storage/codec/opus \
             /app/storage/codec/aac \
             /app/storage/codec/ogg \
             /app/storage/codec/analysis \
             /app/logs \
             /app/cache \
             /app/presets && \
    chown -R codecuser:codecuser /app

# Copy codec presets and configurations
COPY ./config/codec_presets/*.json /app/presets/

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM codec-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/codec_optimization/start.sh

USER codecuser

# Codec optimization environment variables
ENV CODEC_SERVICE_PORT=8013
ENV CODEC_WORKERS=3
ENV MAX_FILE_SIZE=2GB
ENV OPTIMIZATION_TIMEOUT=900
# Quality settings
ENV DEFAULT_BITRATE=320
ENV VBR_QUALITY=0
ENV COMPRESSION_LEVEL=8
ENV SAMPLE_RATE=44100
ENV BIT_DEPTH=24
# Codec-specific settings
ENV MP3_QUALITY=0
ENV FLAC_COMPRESSION=8
ENV OPUS_BITRATE=256
ENV AAC_PROFILE=aac_low
ENV OGG_QUALITY=9
# Performance settings
ENV PARALLEL_JOBS=4
ENV CACHE_TTL=1800

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${CODEC_SERVICE_PORT}/health || exit 1

EXPOSE ${CODEC_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/presets"]

CMD ["python3.11", "-m", "codec_optimization.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM codec-app AS development

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
        # Audio analysis
        plotly \
        seaborn

ENV CODEC_SERVICE_PORT=8013
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER codecuser

HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${CODEC_SERVICE_PORT}/health || exit 1

EXPOSE ${CODEC_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/presets"]

CMD ["python3.11", "-m", "codec_optimization.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Codec Optimization Engine"
LABEL org.opencontainers.image.description="Advanced codec optimization for MP3, FLAC, OPUS, AAC, OGG"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="codec_optimization"
LABEL ainflue.service.port="8013"
LABEL ainflue.codecs.supported="mp3,flac,opus,aac,ogg"
LABEL ainflue.security.non-root="true"