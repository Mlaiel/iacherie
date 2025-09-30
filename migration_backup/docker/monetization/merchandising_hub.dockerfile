# =============================================================================
# AINFLUE MERCHANDISING HUB - COMMERCE DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS merch-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Merchandising and product monetization platform"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        imagemagick \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r merchuser && \
    useradd -r -g merchuser -d /app merchuser && \
    mkdir -p /app && chown -R merchuser:merchuser /app

FROM merch-base AS merch-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        pillow requests stripe \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM merch-deps AS production

WORKDIR /app
COPY ./merchandising_hub /app/merchandising_hub
COPY ./core /app/core

RUN mkdir -p /app/storage/merchandising/{products,designs,orders} \
             /app/logs && \
    chown -R merchuser:merchuser /app

USER merchuser

ENV MERCH_SERVICE_PORT=8050
ENV PRODUCT_IMAGE_MAX_SIZE=5MB
ENV ORDER_FULFILLMENT_TIMEOUT=72

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${MERCH_SERVICE_PORT}/health || exit 1

EXPOSE ${MERCH_SERVICE_PORT}
CMD ["python3.11", "-m", "merchandising_hub.main"]

LABEL org.opencontainers.image.title="Ainflue Merchandising Hub"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="merchandising_hub"
LABEL ainflue.service.port="8050"