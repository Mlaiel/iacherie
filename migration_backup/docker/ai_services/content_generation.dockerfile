# Content Generation Service
# AI-powered content creation and generation service
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Content Generation - AI content creation service"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r contentgen && useradd -r -g contentgen contentgen

FROM base AS dependencies
COPY requirements.txt requirements-content.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-content.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./ai_services/content/ ./content/
COPY ./ai_services/common/ ./common/
RUN mkdir -p /app/models /app/generated_content /app/logs && chown -R contentgen:contentgen /app
USER contentgen
ENV PYTHONPATH=/app SERVICE_NAME=content_generation
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "content.main:app", "--host", "0.0.0.0", "--port", "8000"]