# =============================================================================
# AINFLUE EFFECT PROCESSOR - PROFESSIONAL DOCKERFILE  
# =============================================================================
# Real-time audio effects processing engine with reverb, delay, distortion,
# EQ, compression and modulation effects for professional audio production.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

# =============================================================================
# STAGE 1: EFFECTS PROCESSING BASE ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS effects-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Professional audio effects processing engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install audio effects dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        libasound2-dev \
        libportaudio2 \
        portaudio19-dev \
        libfftw3-dev \
        libsndfile1-dev \
        libsamplerate0-dev \
        libjack-jackd2-dev \
        libfreeverb3-dev \
        ladspa-sdk \
        lv2-dev \
        libvst3sdk-dev \
        curl \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM effects-base AS effects-deps

WORKDIR /tmp

# Install Python packages for effects processing
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir \
        librosa>=0.10.0 \
        soundfile>=0.12.0 \
        numpy>=1.24.0 \
        scipy>=1.10.0 \
        pedalboard>=0.8.0 \
        pydub>=0.25.0 \
        pyaudio>=0.2.11 \
        python-rtmidi>=1.5.0 \
        sounddevice>=0.4.6 \
        essentia>=2.1 \
        madmom>=0.16.1 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM effects-deps AS effects-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./audio/effect_processor/ /app/
COPY --chown=appuser:appuser ./core/audio_utils.py /app/utils/
COPY --chown=appuser:appuser ./config/audio_config.py /app/config/

# Create directories for effect presets and chains
RUN mkdir -p /app/presets /app/chains /app/plugins && \
    chown -R appuser:appuser /app/presets /app/chains /app/plugins

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expose port for API
EXPOSE 8006

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8006/health || exit 1

# Switch to non-root user
USER appuser

# Start effects processor service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006", "--workers", "2"]