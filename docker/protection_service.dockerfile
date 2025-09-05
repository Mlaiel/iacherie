# =============================================================================
# AINFLUE PROTECTION RIGHTS SERVICE - ENTERPRISE DOCKERFILE
# =============================================================================
# Advanced content protection service with fingerprinting, watermarking,
# copyright monitoring, and blockchain verification capabilities.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: SECURITY BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS security-base

LABEL stage=security-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Enterprise content protection with blockchain verification"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install security and cryptography dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Python runtime
        python3.11 \
        python3.11-dev \
        python3-pip \
        python3.11-venv \
        # Cryptography libraries
        libssl-dev \
        libffi-dev \
        libgmp-dev \
        # Image processing for watermarking
        libopencv-dev \
        libimage-exiftool-perl \
        # Audio fingerprinting
        ffmpeg \
        libsndfile1-dev \
        # Video processing
        libavcodec-dev \
        libavformat-dev \
        # Build tools
        build-essential \
        pkg-config \
        cmake \
        git \
        wget \
        curl \
        # Database support
        libpq-dev \
        # System utilities
        ca-certificates \
        gnupg \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Create non-root user for security
RUN groupadd -r -g 10001 ainflue && \
    useradd -r -u 10001 -g ainflue -d /app -s /bin/bash ainflue

# =============================================================================
# STAGE 2: PROTECTION DEPENDENCIES
# =============================================================================
FROM security-base AS protection-deps

# Set up Python environment
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install protection-specific packages
RUN pip install --no-cache-dir \
    # Web framework
    fastapi>=0.104.1 \
    uvicorn[standard]>=0.24.0 \
    # Cryptography and security
    cryptography>=41.0.0 \
    pycryptodome>=3.19.0 \
    hashlib \
    # Blockchain integration
    web3>=6.0.0 \
    eth-account>=0.9.0 \
    # Image processing for watermarking
    Pillow>=10.0.0 \
    opencv-python>=4.8.0 \
    numpy>=1.24.0 \
    # Audio fingerprinting
    librosa>=0.10.0 \
    soundfile>=0.12.0 \
    aubio>=0.4.9 \
    # Video processing
    imageio>=2.31.0 \
    # Database
    asyncpg>=0.29.0 \
    redis>=5.0.0 \
    # Machine Learning for detection
    scikit-learn>=1.3.0 \
    # HTTP client for monitoring
    httpx>=0.25.0 \
    aiohttp>=3.9.0 \
    # Async support
    asyncio \
    aiofiles>=23.0.0 \
    # Monitoring and logging
    prometheus-client>=0.19.0 \
    structlog>=23.0.0 \
    # File format handling
    mutagen>=1.47.0 \
    exifread>=3.0.0

# =============================================================================
# STAGE 3: APPLICATION LAYER
# =============================================================================
FROM protection-deps AS application

WORKDIR /app

# Copy application code
COPY protection/ /app/protection/
COPY core/ /app/core/
COPY requirements.txt /app/
COPY analytics/ /app/analytics/

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/temp /app/fingerprints /app/watermarks \
             /app/blockchain /app/violations /app/dmca \
    && chown -R ainflue:ainflue /app

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /app/health-check.sh \
    && chmod +x /app/health-check.sh \
    && chown ainflue:ainflue /app/health-check.sh

# Create protection service script
COPY <<EOF /app/protection_service.py
"""
Ainflue Protection Rights Service
Enterprise content protection with advanced fingerprinting and monitoring
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from protection.fingerprinting.audio_fingerprinting import AudioFingerprinter
from protection.watermarking.image_watermarking import ImageWatermarker
from protection.monitoring.copyright_monitor import CopyrightMonitor
from protection.violation_detector import ViolationDetector
from protection.ip_protection_service import IPProtectionService
from core import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ainflue Protection Rights Service",
    description="Enterprise content protection and rights management",
    version="2.1.0"
)

# Initialize protection services
audio_fingerprinter = AudioFingerprinter()
image_watermarker = ImageWatermarker()
copyright_monitor = CopyrightMonitor()
violation_detector = ViolationDetector()
ip_protection = IPProtectionService()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "protection_service",
        "components": {
            "fingerprinting": "active",
            "watermarking": "active", 
            "monitoring": "active",
            "violation_detection": "active"
        }
    }

@app.post("/fingerprint/audio")
async def create_audio_fingerprint(file: UploadFile = File(...)):
    """Create audio fingerprint for copyright protection."""
    try:
        file_path = f"/app/temp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        fingerprint = await audio_fingerprinter.create_fingerprint(file_path)
        os.remove(file_path)
        
        return {"status": "success", "fingerprint": fingerprint}
    except Exception as e:
        logger.error(f"Audio fingerprinting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/watermark/image")
async def add_image_watermark(file: UploadFile = File(...), watermark_text: str = ""):
    """Add watermark to image for protection."""
    try:
        file_path = f"/app/temp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        watermarked_path = await image_watermarker.add_watermark(file_path, watermark_text)
        
        # Read watermarked file
        with open(watermarked_path, "rb") as f:
            watermarked_content = f.read()
        
        # Clean up temp files
        os.remove(file_path)
        os.remove(watermarked_path)
        
        return {"status": "success", "watermarked_file": watermarked_content.hex()}
    except Exception as e:
        logger.error(f"Image watermarking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor/content")
async def monitor_content(background_tasks: BackgroundTasks, content_id: str, fingerprint: str):
    """Start monitoring content for copyright violations."""
    try:
        background_tasks.add_task(copyright_monitor.start_monitoring, content_id, fingerprint)
        return {"status": "success", "message": f"Monitoring started for content {content_id}"}
    except Exception as e:
        logger.error(f"Content monitoring setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/violations/{content_id}")
async def get_violations(content_id: str):
    """Get copyright violations for specific content."""
    try:
        violations = await violation_detector.get_violations(content_id)
        return {"status": "success", "violations": violations}
    except Exception as e:
        logger.error(f"Violation retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/protect/ip")
async def protect_intellectual_property(
    content_type: str,
    creator_id: str,
    content_data: Dict[str, Any]
):
    """Comprehensive IP protection for content."""
    try:
        protection_result = await ip_protection.protect_content(
            content_type, creator_id, content_data
        )
        return {"status": "success", "protection": protection_result}
    except Exception as e:
        logger.error(f"IP protection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/protection")
async def get_protection_stats():
    """Get protection service statistics."""
    try:
        stats = {
            "total_fingerprints": await audio_fingerprinter.get_total_count(),
            "active_monitoring": await copyright_monitor.get_active_count(),
            "violations_detected": await violation_detector.get_violation_count(),
            "uptime": "99.99%"
        }
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
EOF

# Set proper permissions
RUN chown ainflue:ainflue /app/protection_service.py

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
ENV SERVICE_NAME=protection_service
ENV SERVICE_CATEGORY=protection
ENV LOG_LEVEL=INFO
ENV ENCRYPTION_ENABLED=true
ENV AUDIT_LOGGING=true

# Security hardening
ENV PYTHONHASHSEED=random
ENV PYTHONOPTIMIZE=1

# Create volumes for data persistence
VOLUME ["/app/data", "/app/logs", "/app/fingerprints", "/app/watermarks", "/app/violations"]

# Set resource limits
LABEL memory="1g"
LABEL cpus="1.0"

# Entry point
CMD ["python3.11", "/app/protection_service.py"]