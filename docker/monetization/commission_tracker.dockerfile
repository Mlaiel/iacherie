# =============================================================================
# AINFLUE COMMISSION TRACKER - CALCULATION DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS commission-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Commission tracking and calculation service"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r commissionuser && \
    useradd -r -g commissionuser -d /app commissionuser && \
    mkdir -p /app && chown -R commissionuser:commissionuser /app

FROM commission-base AS commission-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas decimal \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM commission-deps AS production

WORKDIR /app
COPY ./commission_tracker /app/commission_tracker
COPY ./core /app/core

RUN mkdir -p /app/storage/commissions /app/logs && \
    chown -R commissionuser:commissionuser /app

USER commissionuser

ENV COMMISSION_SERVICE_PORT=8049
ENV DEFAULT_COMMISSION_RATE=0.10
ENV COMMISSION_CALCULATION_SCHEDULE=daily

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${COMMISSION_SERVICE_PORT}/health || exit 1

EXPOSE ${COMMISSION_SERVICE_PORT}
CMD ["python3.11", "-m", "commission_tracker.main"]

LABEL org.opencontainers.image.title="Ainflue Commission Tracker"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="commission_tracker"
LABEL ainflue.service.port="8049"