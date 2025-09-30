# =============================================================================
# AINFLUE AUDIO QUALITY ANALYZER - PROFESSIONAL DOCKERFILE
# =============================================================================
# Multi-stage Docker build for comprehensive audio quality analysis
# including THD, SNR, dynamic range, spectral analysis, and perceptual quality.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: QUALITY ANALYSIS BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS quality-base

LABEL stage=quality-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Professional audio quality analysis service"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install audio analysis dependencies
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
        # Audio processing tools
        ffmpeg \
        sox \
        libsox-fmt-all \
        libsndfile1-dev \
        libsamplerate0-dev \
        # Professional analysis tools
        libfftw3-dev \
        libblas-dev \
        liblapack-dev \
        # Audio libraries
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libavfilter-dev \
        # Quality measurement
        libebur128-dev \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user
RUN groupadd -r qualityuser && \
    useradd -r -g qualityuser -d /app -s /bin/bash qualityuser && \
    mkdir -p /app && \
    chown -R qualityuser:qualityuser /app

# =============================================================================
# STAGE 2: ANALYSIS DEPENDENCIES
# =============================================================================
FROM quality-base AS quality-deps

# Install specialized Python packages for audio quality analysis
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir \
        librosa \
        soundfile \
        numpy \
        scipy \
        matplotlib \
        seaborn \
        plotly \
        # Audio analysis
        pyloudnorm \
        essentia \
        aubio \
        madmom \
        pyaudio-analysis \
        # Signal processing
        pyroomacoustics \
        pedalboard \
        resampy \
        # Perceptual models
        torch \
        torchaudio \
        # Quality metrics
        pesq \
        pystoi \
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
        # Data processing
        pandas \
        openpyxl

# =============================================================================
# STAGE 3: APPLICATION SETUP
# =============================================================================
FROM quality-deps AS quality-app

WORKDIR /app

# Copy application code
COPY ./audio_quality_analyzer /app/audio_quality_analyzer
COPY ./core /app/core
COPY ./config /app/config

# Create quality analysis directories
RUN mkdir -p /app/storage/quality/input \
             /app/storage/quality/analysis \
             /app/storage/quality/reports \
             /app/storage/quality/visualizations \
             /app/storage/quality/metrics \
             /app/storage/quality/comparisons \
             /app/logs \
             /app/cache \
             /app/models && \
    chown -R qualityuser:qualityuser /app

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM quality-app AS production

# Security hardening
RUN rm -rf /tmp/* /var/tmp/* \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && chmod +x /app/audio_quality_analyzer/start.sh

USER qualityuser

# Quality analysis environment variables
ENV QUALITY_SERVICE_PORT=8014
ENV QUALITY_WORKERS=2
ENV MAX_FILE_SIZE=1GB
ENV ANALYSIS_TIMEOUT=300
# Analysis settings
ENV SAMPLE_RATE=48000
ENV FFT_SIZE=2048
ENV HOP_LENGTH=512
ENV WINDOW_TYPE=hann
# Quality metrics
ENV THD_THRESHOLD=0.01
ENV SNR_THRESHOLD=60
ENV DYNAMIC_RANGE_THRESHOLD=14
ENV CLIPPING_THRESHOLD=-0.1
# Perceptual settings
ENV PERCEPTUAL_MODEL=stoi
ENV REFERENCE_LEVEL=-20
ENV CACHE_TTL=3600

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${QUALITY_SERVICE_PORT}/health || exit 1

EXPOSE ${QUALITY_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

CMD ["python3.11", "-m", "audio_quality_analyzer.main"]

# =============================================================================
# STAGE 5: DEVELOPMENT
# =============================================================================
FROM quality-app AS development

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
        # Advanced visualization
        bokeh \
        dash \
        streamlit

ENV QUALITY_SERVICE_PORT=8014
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV RELOAD=true

USER qualityuser

HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
    CMD curl -f http://localhost:${QUALITY_SERVICE_PORT}/health || exit 1

EXPOSE ${QUALITY_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/cache", "/app/models"]

CMD ["python3.11", "-m", "audio_quality_analyzer.main", "--reload"]

# =============================================================================
# METADATA
# =============================================================================
LABEL org.opencontainers.image.title="Ainflue Audio Quality Analyzer"
LABEL org.opencontainers.image.description="Professional audio quality analysis with THD, SNR, dynamic range"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>"
LABEL org.opencontainers.image.source="https://github.com/Mlaiel/Ainflue"
LABEL ainflue.service.category="audio"
LABEL ainflue.service.name="audio_quality_analyzer"
LABEL ainflue.service.port="8014"
LABEL ainflue.quality.metrics="thd,snr,dynamic_range,clipping"
LABEL ainflue.security.non-root="true"