# Viral Predictor Service
FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl libpq5 libpq-dev pkg-config && rm -rf /var/lib/apt/lists/*
RUN groupadd -r viral && useradd -r -g viral viral
FROM base AS dependencies
COPY requirements.txt requirements-viral.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-viral.txt
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./seo/viral/ ./viral/
COPY ./seo/common/ ./common/
RUN mkdir -p /app/viral_analysis /app/logs && chown -R viral:viral /app
USER viral
ENV PYTHONPATH=/app SERVICE_NAME=viral_predictor
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "viral.main:app", "--host", "0.0.0.0", "--port", "8000"]