# Collaboration Analytics Service
# Real-time analytics and performance tracking
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Collaboration Analytics - Real-time analytics service"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential curl libpq5 libpq-dev pkg-config \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r analytics && useradd -r -g analytics analytics

FROM base AS dependencies
COPY requirements.txt requirements-analytics.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-analytics.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./collaboration/analytics/ ./analytics/
COPY ./collaboration/common/ ./common/

RUN mkdir -p /app/analytics_data /app/logs && \
    chown -R analytics:analytics /app

USER analytics
ENV PYTHONPATH=/app SERVICE_NAME=collaboration_analytics

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "analytics.main:app", "--host", "0.0.0.0", "--port", "8000"]