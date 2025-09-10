# Publication Scheduler Service - Intelligent timing and scheduling
# Optimizes publication timing based on audience engagement patterns
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies for scheduling and time zones
RUN apt-get update && apt-get install -y \
    curl \
    tzdata \
    cron \
    supervisor \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/publication-scheduler.txt .
RUN pip install --no-cache-dir -r publication-scheduler.txt

# Multi-stage build for production
FROM base AS production

# Create non-root user
RUN groupadd -r scheduler && useradd -r -g scheduler scheduler

# Copy application code
COPY src/distribution/publication_scheduler/ ./publication_scheduler/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Copy supervisor configuration
COPY docker/distribution/configs/supervisor-scheduler.conf /etc/supervisor/conf.d/

# Create necessary directories
RUN mkdir -p /var/log/scheduler /var/run/scheduler
RUN chown -R scheduler:scheduler /app /var/log/scheduler /var/run/scheduler

# Switch to non-root user
USER scheduler

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8001
ENV SCHEDULER_TIMEZONE=UTC
ENV MAX_CONCURRENT_JOBS=10

# Run with supervisor to manage scheduler daemon and API
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisor-scheduler.conf", "-n"]