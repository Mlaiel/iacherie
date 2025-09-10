# Success Predictor Service - AI-powered success prediction and trend analysis
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/success-predictor.txt .
RUN pip install --no-cache-dir -r success-predictor.txt

FROM base AS production
RUN groupadd -r success && useradd -r -g success success
COPY src/creator_services/success_predictor/ ./success_predictor/
RUN mkdir -p /app/models /app/predictions && chown -R success:success /app
USER success
EXPOSE 8308
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8308/health || exit 1
ENV PYTHONPATH=/app PORT=8308
CMD ["python", "-m", "uvicorn", "success_predictor.main:app", "--host", "0.0.0.0", "--port", "8308"]