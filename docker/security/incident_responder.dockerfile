# Incident Responder Service - Automated security incident response
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl git build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/incident-responder.txt .
RUN pip install --no-cache-dir -r incident-responder.txt

FROM base AS production
RUN groupadd -r incident && useradd -r -g incident incident
COPY src/security/incident_responder/ ./incident_responder/
COPY src/security/common/ ./common/
RUN mkdir -p /app/playbooks /app/reports && chown -R incident:incident /app
USER incident
EXPOSE 8110
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8110/health')" || exit 1
ENV PYTHONPATH=/app PORT=8110 RESPONSE_TIME_TARGET=300
CMD ["python", "-m", "uvicorn", "incident_responder.main:app", "--host", "0.0.0.0", "--port", "8110"]