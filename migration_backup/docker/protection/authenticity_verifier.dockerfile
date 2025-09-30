# =============================================================================
# AINFLUE AUTHENTICITY VERIFIER - SPECIALIZED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for authenticity verification supporting
# digital signatures, blockchain verification, and AI-based authenticity detection.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: AUTHENTICITY VERIFICATION BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS authenticity-base

LABEL stage=authenticity-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced authenticity verification engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install authenticity verification dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        libssl-dev \
        libcrypto++-dev \
        libsodium-dev \
        libgmp-dev \
        curl \
        wget \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM authenticity-base AS authenticity-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install verification packages
RUN pip3 install --no-cache-dir \
        cryptography>=41.0.0 \
        pycryptodome>=3.19.0 \
        web3>=6.11.0 \
        eth-account>=0.9.0 \
        ecdsa>=0.18.0 \
        PyNaCl>=1.5.0 \
        hashlib \
        pillow>=10.0.0 \
        opencv-python>=4.8.0 \
        tensorflow>=2.13.0 \
        torch>=2.0.0 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM authenticity-deps AS authenticity-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./protection/authenticity_verifier/ /app/
COPY --chown=appuser:appuser ./core/security.py /app/core/
COPY --chown=appuser:appuser ./config/protection_config.py /app/config/

# Create directories for verification data
RUN mkdir -p /app/signatures /app/certificates /app/blockchain_data && \
    chown -R appuser:appuser /app/signatures /app/certificates /app/blockchain_data

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Environment variables
ENV VERIFICATION_TIMEOUT=30
ENV BLOCKCHAIN_NETWORK=mainnet
ENV ENABLE_AI_VERIFICATION=true

# Expose port for API
EXPOSE 8040

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8040/health || exit 1

# Switch to non-root user
USER appuser

# Start authenticity verifier service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8040", "--workers", "2"]