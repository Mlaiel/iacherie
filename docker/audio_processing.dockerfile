# =============================================================================
# AINFLUE AUDIO PROCESSING SERVICE - PROFESSIONAL DOCKERFILE
# =============================================================================
# Enterprise-grade audio processing container with professional broadcast
# standards compliance, advanced source separation, and mastering capabilities.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: AUDIO DEPENDENCIES BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS audio-base

LABEL stage=audio-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Professional audio processing base with broadcast standards"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install audio processing system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Python runtime
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        # Audio processing libraries
        ffmpeg \
        libsndfile1 \
        libsndfile1-dev \
        libfftw3-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libavutil-dev \
        libavfilter-dev \
        libswresample-dev \
        # Professional audio tools
        sox \
        lame \
        flac \
        opus-tools \
        vorbis-tools \
        # Build tools
        build-essential \
        pkg-config \
        cmake \
        git \
        wget \
        curl \
        # System utilities
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r -g 10001 ainflue && \
    useradd -r -u 10001 -g ainflue -d /app -s /bin/bash ainflue

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM audio-base AS python-deps

# Set up Python environment
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install audio processing Python packages
RUN pip install --no-cache-dir \
    # Core audio processing
    librosa>=0.10.0 \
    soundfile>=0.12.0 \
    scipy>=1.11.0 \
    numpy>=1.24.0 \
    # Professional audio analysis
    essentia>=2.1b6 \
    aubio>=0.4.9 \
    madmom>=0.16.1 \
    # Source separation (DEMUCS)
    demucs>=4.0.0 \
    torch>=2.0.0 \
    torchaudio>=2.0.0 \
    # Audio quality analysis
    pyloudnorm>=0.1.1 \
    # Format conversion
    pydub>=0.25.1 \
    mutagen>=1.47.0 \
    # Web framework for API
    fastapi>=0.104.1 \
    uvicorn[standard]>=0.24.0 \
    # Async support
    asyncio \
    aiofiles>=23.0.0 \
    # Monitoring
    prometheus-client>=0.19.0 \
    # Logging
    structlog>=23.0.0

# =============================================================================
# STAGE 3: APPLICATION LAYER
# =============================================================================
FROM python-deps AS application

WORKDIR /app

# Copy application code
COPY multimedia/ /app/multimedia/
COPY core/ /app/core/
COPY requirements.txt /app/
COPY analytics/ /app/analytics/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp /app/output \
    && chown -R ainflue:ainflue /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /app/health-check.sh \
    && chmod +x /app/health-check.sh \
    && chown ainflue:ainflue /app/health-check.sh

# Create audio processing service script
COPY <<EOF /app/audio_service.py
"""
Ainflue Audio Processing Service
Professional audio processing with broadcast standards compliance
"""

import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
from multimedia.processors import AudioProcessor
from multimedia.ai_analysis import AudioAnalyzer
from core import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ainflue Audio Processing Service",
    description="Professional audio processing with broadcast standards",
    version="2.1.0"
)

# Initialize audio processor
audio_processor = AudioProcessor()
audio_analyzer = AudioAnalyzer()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "audio_processing"}

@app.post("/process/audio")
async def process_audio(file: UploadFile = File(...)):
    """Process uploaded audio file."""
    try:
        # Save uploaded file
        file_path = f"/app/temp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process audio
        result = await audio_processor.process_file(file_path)
        
        # Clean up temp file
        os.remove(file_path)
        
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Audio processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/audio")
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze audio quality and characteristics."""
    try:
        file_path = f"/app/temp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        analysis = await audio_analyzer.analyze_file(file_path)
        os.remove(file_path)
        
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        logger.error(f"Audio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
EOF

# Set proper permissions
RUN chown ainflue:ainflue /app/audio_service.py

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM application AS production

# Switch to non-root user
USER ainflue

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health-check.sh

# Environment variables
ENV PYTHONPATH=/app
ENV SERVICE_NAME=audio_processing
ENV SERVICE_CATEGORY=audio_processing
ENV LOG_LEVEL=INFO

# Create volumes for data persistence
VOLUME ["/app/data", "/app/logs", "/app/output"]

# Set resource limits
LABEL memory="1g"
LABEL cpus="1.0"

# Entry point
CMD ["python3.11", "/app/audio_service.py"]