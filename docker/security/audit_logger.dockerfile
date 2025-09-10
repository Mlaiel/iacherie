# Audit Logger Service - Comprehensive security audit and compliance logging
# Manages security event logging, audit trails, and compliance reporting
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    rsyslog \
    logrotate \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/audit-logger.txt .
RUN pip install --no-cache-dir -r audit-logger.txt

FROM base AS production

# Create non-root user
RUN groupadd -r audit && useradd -r -g audit audit

# Copy application code
COPY src/security/audit_logger/ ./audit_logger/
COPY src/security/common/ ./common/
COPY src/security/config/ ./config/

# Create directories and set permissions
RUN mkdir -p /var/log/audit /app/compliance /app/reports
RUN chown -R audit:audit /app /var/log/audit

USER audit

EXPOSE 8103

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8103/health')" || exit 1

ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8103
ENV LOG_RETENTION_DAYS=2555
ENV SIEM_INTEGRATION=enabled

CMD ["python", "-m", "uvicorn", "audit_logger.main:app", "--host", "0.0.0.0", "--port", "8103", "--workers", "2"]