# Brand Analyzer Service - Brand analysis and partnership optimization
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/brand-analyzer.txt .
RUN pip install --no-cache-dir -r brand-analyzer.txt

FROM base AS production
RUN groupadd -r brand && useradd -r -g brand brand
COPY src/creator_services/brand_analyzer/ ./brand_analyzer/
RUN mkdir -p /app/models /app/analytics /app/sentiment && chown -R brand:brand /app
USER brand
EXPOSE 8310
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8310/health || exit 1
ENV PYTHONPATH=/app PORT=8310
CMD ["python", "-m", "uvicorn", "brand_analyzer.main:app", "--host", "0.0.0.0", "--port", "8310"]