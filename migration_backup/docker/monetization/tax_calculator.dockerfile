# =============================================================================
# AINFLUE TAX CALCULATOR - ADVANCED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced tax calculation supporting
# international tax laws, VAT, GST, and automated tax reporting.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS tax-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced tax calculation service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget \
        libssl-dev libffi-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r taxuser && \
    useradd -r -g taxuser -d /app taxuser && \
    mkdir -p /app && chown taxuser:taxuser /app

FROM tax-base AS tax-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements-tax.txt .
RUN pip3 install --no-cache-dir -r requirements-tax.txt

FROM tax-deps AS tax-app

WORKDIR /app

COPY --chown=taxuser:taxuser ./monetization/tax_calculator/ .
COPY --chown=taxuser:taxuser ./core/security.py ./core/
COPY --chown=taxuser:taxuser ./config/tax_config.py ./config/

RUN mkdir -p /app/reports /app/cache /app/tax_rules && \
    chown -R taxuser:taxuser /app/reports /app/cache /app/tax_rules

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV TAX_CACHE_TTL=3600
ENV ENABLE_CRYPTO_TAX=true
ENV ENABLE_INTERNATIONAL_TAX=true

EXPOSE 8030

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8030/health || exit 1

USER taxuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8030", "--workers", "2"]