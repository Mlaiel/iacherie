# =============================================================================
# AINFLUE BROADCAST STANDARDS COMPLIANCE - PROFESSIONAL DOCKERFILE
# =============================================================================
# Multi-stage Docker build for broadcast standards compliance including
# EBU R128, ITU-R BS.1770, ATSC A/85 loudness standards.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: BROADCAST BASE ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS broadcast-base

LABEL stage=broadcast-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Broadcast standards compliance service"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install broadcast-specific dependencies
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
        # Professional audio tools
        ffmpeg \
        sox \
        libsox-fmt-all \
        libsndfile1-dev \
        libsamplerate0-dev \
        # Broadcast standards tools
        ebur128 \
        loudness-scanner \
        # Additional audio libraries
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libavfilter-dev \
        libswscale-dev \
        libswresample-dev \
        # Professional audio analysis
        libaudiofile-dev \
        libmp3lame-dev \
        libvorbis-dev \
        libflac-dev \
        libopus-dev \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user
RUN groupadd -r broadcastuser && \
    useradd -r -g broadcastuser -d /app -s /bin/bash broadcastuser && \
    mkdir -p /app && \
    chown -R broadcastuser:broadcastuser /app

# =============================================================================
# STAGE 2: BROADCAST ANALYSIS TOOLS
# =============================================================================
FROM broadcast-base AS broadcast-deps

# Install specialized Python packages for broadcast standards
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        librosa \
        soundfile \
        numpy \
        scipy \
        matplotlib \
        seaborn \
        # Loudness analysis
        pyloudnorm \
        python-ebur128 \
        # Audio processing
        pydub \
        aubio \
        essentia \
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
        # Additional tools
        resampy \
        madmom

# Install broadcast measurement tools from source if needed
RUN git clone https://github.com/slhck/ffmpeg-normalize.git /tmp/ffmpeg-normalize && \
    cd /tmp/ffmpeg-normalize && \
    python3.11 -m pip install . && \
    rm -rf /tmp/ffmpeg-normalize

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM broadcast-deps AS broadcast-app

WORKDIR /app

# Copy application code
COPY ./broadcast_standards /app/broadcast_standards
COPY ./core /app/core
COPY ./config /app/config

# Create broadcast-specific directories
RUN mkdir -p /app/storage/broadcast/input \
             /app/storage/broadcast/output \
             /app/storage/broadcast/analysis \
             /app/storage/broadcast/reports \
             /app/storage/broadcast/compliant \
             /app/storage/broadcast/non_compliant \
             /app/logs \
             /app/cache \
             /app/standards && \
    chown -R broadcastuser:broadcastuser /app

# Copy broadcast standards configuration
COPY ./config/broadcast_standards/*.json /app/standards/

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM broadcast-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/broadcast_standards/start.sh

USER broadcastuser

# Broadcast standards environment variables
ENV BROADCAST_SERVICE_PORT=8012
ENV BROADCAST_WORKERS=2
ENV MAX_FILE_SIZE=1GB
ENV ANALYSIS_TIMEOUT=600
# EBU R128 settings
ENV EBU_TARGET_LUFS=-23.0
ENV EBU_RANGE_LU=7.0
ENV EBU_MAX_TRUE_PEAK=-1.0
# ITU-R BS.1770 settings
ENV ITU_GATE_THRESHOLD=-70.0
ENV ITU_OVERLAP_PERCENT=75
# ATSC A/85 settings  
ENV ATSC_TARGET_LUFS=-24.0
ENV ATSC_MAX_TRUE_PEAK=-2.0
# Processing settings
ENV SAMPLE_RATE=48000
ENV BIT_DEPTH=24
ENV MEASUREMENT_WINDOW=3.0
ENV CACHE_TTL=3600

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${BROADCAST_SERVICE_PORT}/health || exit 1

EXPOSE ${BROADCAST_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/standards"]

CMD ["python3.11", "-m", "broadcast_standards.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM broadcast-app AS development

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
        # Additional analysis tools
        plotly \
        dash \
        streamlit

ENV BROADCAST_SERVICE_PORT=8012
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER broadcastuser

HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${BROADCAST_SERVICE_PORT}/health || exit 1

EXPOSE ${BROADCAST_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/standards"]

CMD ["python3.11", "-m", "broadcast_standards.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Broadcast Standards Compliance"
LABEL org.opencontainers.image.description="EBU R128/ITU-R BS.1770/ATSC A/85 compliance service"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="broadcast_standards"
LABEL ainflue.service.port="8012"
LABEL ainflue.broadcast.ebu_r128="true"
LABEL ainflue.broadcast.itu_bs1770="true"
LABEL ainflue.broadcast.atsc_a85="true"
LABEL ainflue.security.non-root="true"