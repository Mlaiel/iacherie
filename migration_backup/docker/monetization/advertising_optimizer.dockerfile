# =============================================================================
# AINFLUE ADVERTISING OPTIMIZER - REVENUE DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS ad-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Revenue optimization for advertising campaigns"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r aduser && \
    useradd -r -g aduser -d /app aduser && \
    mkdir -p /app && chown -R aduser:aduser /app

FROM ad-base AS ad-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas scikit-learn \
        google-ads facebook-business \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM ad-deps AS production

WORKDIR /app
COPY ./advertising_optimizer /app/advertising_optimizer
COPY ./core /app/core

RUN mkdir -p /app/storage/advertising /app/logs && \
    chown -R aduser:aduser /app

USER aduser

ENV AD_SERVICE_PORT=8044
ENV OPTIMIZATION_INTERVAL=3600
ENV MIN_BUDGET_THRESHOLD=100

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${AD_SERVICE_PORT}/health || exit 1

EXPOSE ${AD_SERVICE_PORT}
CMD ["python3.11", "-m", "advertising_optimizer.main"]

LABEL org.opencontainers.image.title="Ainflue Advertising Optimizer"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="advertising_optimizer"
LABEL ainflue.service.port="8044"