# Format Converter Service
FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl libpq5 libpq-dev pkg-config ffmpeg && rm -rf /var/lib/apt/lists/*
RUN groupadd -r converter && useradd -r -g converter converter
FROM base AS dependencies
COPY requirements.txt requirements-converter.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-converter.txt
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./ai_services/converter/ ./converter/
COPY ./ai_services/common/ ./common/
RUN mkdir -p /app/models /app/conversions /app/logs && chown -R converter:converter /app
USER converter
ENV PYTHONPATH=/app SERVICE_NAME=format_converter
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "converter.main:app", "--host", "0.0.0.0", "--port", "8000"]