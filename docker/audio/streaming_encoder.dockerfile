# =============================================================================
# AINFLUE STREAMING ENCODER - PROFESSIONAL DOCKERFILE
# =============================================================================
# Real-time audio streaming encoder with multiple codecs and adaptive bitrate
# streaming for live broadcasting and high-quality audio distribution.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

# =============================================================================
# STAGE 1: STREAMING ENCODER BASE ENVIRONMENT
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS streaming-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Professional audio streaming encoder with adaptive bitrate"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install streaming and encoding dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        ffmpeg \
        libavformat-dev \
        libavcodec-dev \
        libavutil-dev \
        libswscale-dev \
        libswresample-dev \
        libmp3lame-dev \
        libopus-dev \
        libvorbis-dev \
        libaac-dev \
        libfdk-aac-dev \
        libx264-dev \
        libasound2-dev \
        libportaudio2 \
        portaudio19-dev \
        libsndfile1-dev \
        librtmp-dev \
        libssl-dev \
        curl \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM streaming-base AS streaming-deps

WORKDIR /tmp

# Install Python packages for streaming
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir \
        librosa>=0.10.0 \
        soundfile>=0.12.0 \
        numpy>=1.24.0 \
        scipy>=1.10.0 \
        av>=10.0.0 \
        ffmpeg-python>=0.2.0 \
        pydub>=0.25.0 \
        pyaudio>=0.2.11 \
        streamlink>=5.5.0 \
        websockets>=11.0.0 \
        aiohttp>=3.9.0 \
        aiortc>=1.6.0 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM streaming-deps AS streaming-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./audio/streaming_encoder/ /app/
COPY --chown=appuser:appuser ./core/audio_utils.py /app/utils/
COPY --chown=appuser:appuser ./config/streaming_config.py /app/config/

# Create directories for streaming profiles and temporary files
RUN mkdir -p /app/profiles /app/temp /app/logs && \
    chown -R appuser:appuser /app/profiles /app/temp /app/logs

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Environment variables for streaming
ENV STREAMING_BUFFER_SIZE=8192
ENV MAX_BITRATE=320000
ENV MIN_BITRATE=64000
ENV ADAPTIVE_STREAMING=true

# Expose ports for streaming API and WebSocket
EXPOSE 8007 9007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Switch to non-root user
USER appuser

# Start streaming encoder service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007", "--workers", "2"]