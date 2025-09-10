# Automation Orchestrator Service - Workflow automation for distribution
# Manages automated distribution workflows and pipelines
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/automation-orchestrator.txt .
RUN pip install --no-cache-dir -r automation-orchestrator.txt

FROM base AS production

# Create non-root user
RUN groupadd -r automation && useradd -r -g automation automation

# Copy application code
COPY src/distribution/automation_orchestrator/ ./automation_orchestrator/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Copy supervisor configuration
COPY docker/distribution/configs/supervisor-automation.conf /etc/supervisor/conf.d/

# Create directories
RUN mkdir -p /app/workflows /app/logs /var/log/automation
RUN chown -R automation:automation /app /var/log/automation

USER automation

EXPOSE 8009

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8009/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8009
ENV WORKFLOW_ENGINE=airflow
ENV MAX_PARALLEL_WORKFLOWS=50

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisor-automation.conf", "-n"]