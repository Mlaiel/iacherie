# =============================================================================
# AINFLUE FORENSIC ANALYZER - SPECIALIZED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for digital forensic analysis supporting
# metadata extraction, file analysis, and evidence collection for legal purposes.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: FORENSIC ANALYZER BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS forensic-base

LABEL stage=forensic-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced digital forensic analysis engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install forensic analysis dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        libexif-dev \
        exiftool \
        file \
        binutils \
        hexdump \
        strings \
        foremost \
        volatility3 \
        sleuthkit \
        libmagic-dev \
        libssl-dev \
        ffmpeg \
        imagemagick \
        curl \
        wget \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM forensic-base AS forensic-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install forensic analysis packages
RUN pip3 install --no-cache-dir \
        exifread>=3.0.0 \
        python-magic>=0.4.27 \
        pillow>=10.0.0 \
        opencv-python>=4.8.0 \
        librosa>=0.10.0 \
        soundfile>=0.12.0 \
        av>=10.0.0 \
        hashlib \
        cryptography>=41.0.0 \
        yara-python>=4.3.0 \
        pefile>=2023.2.7 \
        scapy>=2.5.0 \
        volatility3>=2.5.0 \
        pytsk3>=20230125 \
        sleuthkit>=4.12.0 \
        binwalk>=2.3.3 \
        numpy>=1.24.0 \
        pandas>=2.1.0 \
        matplotlib>=3.7.0 \
        seaborn>=0.12.0 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM forensic-deps AS forensic-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./protection/forensic_analyzer/ /app/
COPY --chown=appuser:appuser ./core/forensic_utils.py /app/core/
COPY --chown=appuser:appuser ./config/protection_config.py /app/config/

# Create directories for forensic data
RUN mkdir -p /app/evidence /app/reports /app/hashes /app/signatures && \
    chown -R appuser:appuser /app/evidence /app/reports /app/hashes /app/signatures

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Environment variables
ENV ANALYSIS_TIMEOUT=600
ENV ENABLE_DEEP_SCAN=true
ENV PRESERVE_METADATA=true
ENV EVIDENCE_CHAIN_VALIDATION=true

# Expose port for API
EXPOSE 8043

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8043/health || exit 1

# Switch to non-root user
USER appuser

# Start forensic analyzer service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8043", "--workers", "2"]