# =============================================================================
# AINFLUE PITCH CORRECTOR - PROFESSIONAL DOCKERFILE
# =============================================================================
# Real-time pitch correction and auto-tune engine for professional audio
# processing with multiple algorithms and enterprise-grade performance.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

# =============================================================================
# STAGE 1: PITCH CORRECTION BASE ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS pitch-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Professional pitch correction and auto-tune engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install pitch correction dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        libasound2-dev \
        libportaudio2 \
        libportaudiocpp0 \
        portaudio19-dev \
        libfftw3-dev \
        libaubio-dev \
        librubberband-dev \
        libsndfile1-dev \
        libsamplerate0-dev \
        libjack-jackd2-dev \
        curl \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM pitch-base AS pitch-deps

WORKDIR /tmp

# Install Python packages for pitch correction
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir \
        librosa>=0.10.0 \
        soundfile>=0.12.0 \
        numpy>=1.24.0 \
        scipy>=1.10.0 \
        aubio>=0.4.9 \
        pyrubberband>=0.3.0 \
        resampy>=0.4.0 \
        psola>=0.2.0 \
        crepe>=0.0.12 \
        parselmouth>=0.4.3 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM pitch-deps AS pitch-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./audio/pitch_corrector/ /app/
COPY --chown=appuser:appuser ./core/audio_utils.py /app/utils/
COPY --chown=appuser:appuser ./config/audio_config.py /app/config/

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expose port for API
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Switch to non-root user
USER appuser

# Start pitch correction service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "2"]