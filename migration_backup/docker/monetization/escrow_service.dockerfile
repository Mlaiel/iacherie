# =============================================================================
# AINFLUE ESCROW SERVICE - ADVANCED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for secure escrow service supporting
# multi-party transactions, smart contracts, and automated dispute resolution.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS escrow-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced escrow service for secure transactions"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget \
        libssl-dev libffi-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r escrowuser && \
    useradd -r -g escrowuser -d /app escrowuser && \
    mkdir -p /app && chown escrowuser:escrowuser /app

FROM escrow-base AS escrow-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements-escrow.txt .
RUN pip3 install --no-cache-dir -r requirements-escrow.txt

FROM escrow-deps AS escrow-app

WORKDIR /app

COPY --chown=escrowuser:escrowuser ./monetization/escrow_service/ .
COPY --chown=escrowuser:escrowuser ./core/security.py ./core/
COPY --chown=escrowuser:escrowuser ./config/escrow_config.py ./config/

RUN mkdir -p /app/transactions /app/disputes /app/contracts && \
    chown -R escrowuser:escrowuser /app/transactions /app/disputes /app/contracts

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV ESCROW_TIMEOUT=86400
ENV ENABLE_SMART_CONTRACTS=true
ENV AUTO_DISPUTE_RESOLUTION=true

EXPOSE 8032

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8032/health || exit 1

USER escrowuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8032", "--workers", "2"]