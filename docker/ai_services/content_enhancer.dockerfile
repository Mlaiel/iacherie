# Content Enhancer Service
FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl libpq5 libpq-dev pkg-config && rm -rf /var/lib/apt/lists/*
RUN groupadd -r enhancer && useradd -r -g enhancer enhancer
FROM base AS dependencies
COPY requirements.txt requirements-enhancement.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-enhancement.txt
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./ai_services/enhancer/ ./enhancer/
COPY ./ai_services/common/ ./common/
RUN mkdir -p /app/models /app/enhanced_content /app/logs && chown -R enhancer:enhancer /app
USER enhancer
ENV PYTHONPATH=/app SERVICE_NAME=content_enhancer
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "enhancer.main:app", "--host", "0.0.0.0", "--port", "8000"]