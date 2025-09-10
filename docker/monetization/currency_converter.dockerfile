# =============================================================================
# AINFLUE CURRENCY CONVERTER - ADVANCED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for real-time currency conversion supporting
# 180+ currencies, crypto currencies, and real-time exchange rates.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS currency-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced currency conversion service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget \
        libssl-dev libffi-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r currencyuser && \
    useradd -r -g currencyuser -d /app currencyuser && \
    mkdir -p /app && chown currencyuser:currencyuser /app

FROM currency-base AS currency-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements-currency.txt .
RUN pip3 install --no-cache-dir -r requirements-currency.txt

FROM currency-deps AS currency-app

WORKDIR /app

COPY --chown=currencyuser:currencyuser ./monetization/currency_converter/ .
COPY --chown=currencyuser:currencyuser ./core/security.py ./core/
COPY --chown=currencyuser:currencyuser ./config/currency_config.py ./config/

RUN mkdir -p /app/rates /app/cache /app/historical && \
    chown -R currencyuser:currencyuser /app/rates /app/cache /app/historical

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV RATE_UPDATE_INTERVAL=300
ENV ENABLE_CRYPTO_RATES=true
ENV CACHE_DURATION=600

EXPOSE 8031

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8031/health || exit 1

USER currencyuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8031", "--workers", "2"]