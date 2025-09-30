# =============================================================================
# AINFLUE REVENUE ANALYTICS - BUSINESS INSIGHTS DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS analytics-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced revenue analytics and business insights"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r analyticsuser && \
    useradd -r -g analyticsuser -d /app analyticsuser && \
    mkdir -p /app && chown -R analyticsuser:analyticsuser /app

FROM analytics-base AS analytics-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        numpy pandas matplotlib seaborn plotly \
        scikit-learn \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM analytics-deps AS production

WORKDIR /app
COPY ./revenue_analytics /app/revenue_analytics
COPY ./core /app/core

RUN mkdir -p /app/storage/analytics/{reports,dashboards} \
             /app/logs && \
    chown -R analyticsuser:analyticsuser /app

USER analyticsuser

ENV ANALYTICS_SERVICE_PORT=8047
ENV REPORT_GENERATION_SCHEDULE=daily
ENV DASHBOARD_REFRESH_INTERVAL=3600

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${ANALYTICS_SERVICE_PORT}/health || exit 1

EXPOSE ${ANALYTICS_SERVICE_PORT}
CMD ["python3.11", "-m", "revenue_analytics.main"]

LABEL org.opencontainers.image.title="Ainflue Revenue Analytics"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="revenue_analytics"
LABEL ainflue.service.port="8047"