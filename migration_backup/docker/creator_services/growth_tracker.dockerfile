# Growth Tracker Service - Creator growth analytics and milestone tracking
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/growth-tracker.txt .
RUN pip install --no-cache-dir -r growth-tracker.txt

FROM base AS production
RUN groupadd -r growth && useradd -r -g growth growth
COPY src/creator_services/growth_tracker/ ./growth_tracker/
RUN mkdir -p /app/models /app/analytics /app/milestones && chown -R growth:growth /app
USER growth
EXPOSE 8307
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8307/health || exit 1
ENV PYTHONPATH=/app PORT=8307
CMD ["python", "-m", "uvicorn", "growth_tracker.main:app", "--host", "0.0.0.0", "--port", "8307"]