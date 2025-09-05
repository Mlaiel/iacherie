# =============================================================================
# AINFLUE BLOCKCHAIN VERIFIER - DISTRIBUTED DOCKERFILE  
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION} AS blockchain-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Blockchain-based content verification service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl wget \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r blockchainuser && \
    useradd -r -g blockchainuser -d /app blockchainuser && \
    mkdir -p /app && chown -R blockchainuser:blockchainuser /app

FROM blockchain-base AS blockchain-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        web3 eth-hash eth-account \
        cryptography hashlib xxhash \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM blockchain-deps AS production

WORKDIR /app
COPY ./blockchain_verifier /app/blockchain_verifier
COPY ./core /app/core

RUN mkdir -p /app/storage/blockchain/{records,keys} \
             /app/logs && \
    chown -R blockchainuser:blockchainuser /app

USER blockchainuser

ENV BLOCKCHAIN_SERVICE_PORT=8025
ENV BLOCKCHAIN_NETWORK=ethereum
ENV VERIFICATION_CONTRACT_ADDRESS=""
ENV GAS_LIMIT=200000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${BLOCKCHAIN_SERVICE_PORT}/health || exit 1

EXPOSE ${BLOCKCHAIN_SERVICE_PORT}
CMD ["python3.11", "-m", "blockchain_verifier.main"]

LABEL org.opencontainers.image.title="Ainflue Blockchain Verifier"
LABEL ainflue.service.category="protection"
LABEL ainflue.service.name="blockchain_verifier" 
LABEL ainflue.service.port="8025"