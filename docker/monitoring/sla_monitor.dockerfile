# SLA Monitor Service - Service level agreement monitoring
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements/sla-monitor.txt .
RUN pip install --no-cache-dir -r sla-monitor.txt

FROM base AS production
RUN groupadd -r sla && useradd -r -g sla sla
COPY src/monitoring/sla_monitor/ ./sla_monitor/
RUN mkdir -p /app/reports && chown -R sla:sla /app
USER sla
EXPOSE 8204
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8204/health')" || exit 1
ENV PYTHONPATH=/app PORT=8204
CMD ["python", "-m", "uvicorn", "sla_monitor.main:app", "--host", "0.0.0.0", "--port", "8204"]