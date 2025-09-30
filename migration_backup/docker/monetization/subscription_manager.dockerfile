# =============================================================================
# AINFLUE SUBSCRIPTION MANAGER - LIFECYCLE DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS subscription-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Comprehensive subscription lifecycle management"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r subuser && \
    useradd -r -g subuser -d /app subuser && \
    mkdir -p /app && chown -R subuser:subuser /app

FROM subscription-base AS subscription-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas stripe \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client \
        schedule apscheduler

FROM subscription-deps AS production

WORKDIR /app
COPY ./subscription_manager /app/subscription_manager
COPY ./core /app/core

RUN mkdir -p /app/storage/subscriptions /app/logs && \
    chown -R subuser:subuser /app

USER subuser

ENV SUBSCRIPTION_SERVICE_PORT=8042
ENV BILLING_CYCLE_CHECK_HOUR=6
ENV TRIAL_PERIOD_DAYS=14

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${SUBSCRIPTION_SERVICE_PORT}/health || exit 1

EXPOSE ${SUBSCRIPTION_SERVICE_PORT}
CMD ["python3.11", "-m", "subscription_manager.main"]

LABEL org.opencontainers.image.title="Ainflue Subscription Manager"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="subscription_manager"
LABEL ainflue.service.port="8042"