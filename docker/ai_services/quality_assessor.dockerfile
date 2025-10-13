# Quality Assessor Service
FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl libpq5 libpq-dev pkg-config && rm -rf /var/lib/apt/lists/*
RUN groupadd -r quality && useradd -r -g quality quality
FROM base AS dependencies
COPY requirements.txt requirements-quality.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-quality.txt
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./ai_services/quality/ ./quality/
COPY ./ai_services/common/ ./common/
RUN mkdir -p /app/models /app/quality_reports /app/logs && chown -R quality:quality /app
USER quality
ENV PYTHONPATH=/app SERVICE_NAME=quality_assessor
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "quality.main:app", "--host", "0.0.0.0", "--port", "8000"]