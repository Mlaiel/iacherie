# =============================================================================
# AINFLUE PAYMENT PROCESSOR - ADVANCED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced payment processing supporting
# Stripe, PayPal, crypto payments, and multi-currency processing.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS payment-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced payment processing service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential pkg-config curl wget \
        libssl-dev libffi-dev \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r paymentuser && \
    useradd -r -g paymentuser -d /app paymentuser && \
    mkdir -p /app && chown -R paymentuser:paymentuser /app

FROM payment-base AS payment-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas \
        stripe paypalrestsdk \
        cryptography pycryptodome \
        web3 bitcoin-python \
        requests aiohttp \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        python-jose passlib bcrypt

FROM payment-deps AS payment-app

WORKDIR /app
COPY ./payment_processor /app/payment_processor
COPY ./core /app/core

RUN mkdir -p /app/storage/payments/{transactions,receipts,refunds} \
             /app/logs /app/cache /app/keys && \
    chmod 700 /app/keys && \
    chown -R paymentuser:paymentuser /app

FROM payment-app AS production

USER paymentuser

ENV PAYMENT_SERVICE_PORT=8041
ENV SUPPORTED_CURRENCIES=USD,EUR,GBP,JPY,BTC,ETH
ENV PAYMENT_PROVIDERS=stripe,paypal,crypto
ENV PCI_COMPLIANCE=true
ENV FRAUD_DETECTION=true

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PAYMENT_SERVICE_PORT}/health || exit 1

EXPOSE ${PAYMENT_SERVICE_PORT}
VOLUME ["/app/storage", "/app/logs", "/app/keys"]

CMD ["python3.11", "-m", "payment_processor.main"]

LABEL org.opencontainers.image.title="Ainflue Payment Processor"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="payment_processor"
LABEL ainflue.service.port="8041"