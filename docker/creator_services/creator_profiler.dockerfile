# Creator Profiler Service - AI-powered creator analysis and profiling
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/creator-profiler.txt .
RUN pip install --no-cache-dir -r creator-profiler.txt

FROM base AS production
RUN groupadd -r profiler && useradd -r -g profiler profiler
COPY src/creator_services/creator_profiler/ ./creator_profiler/
RUN mkdir -p /app/models /app/profiles && chown -R profiler:profiler /app
USER profiler
EXPOSE 8305
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8305/health || exit 1
ENV PYTHONPATH=/app PORT=8305
CMD ["python", "-m", "uvicorn", "creator_profiler.main:app", "--host", "0.0.0.0", "--port", "8305"]