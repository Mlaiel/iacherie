# Workflow Manager Service
# Intelligent workflow automation and task distribution
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Workflow Manager - Intelligent workflow automation service"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq5 \
        libpq-dev \
        pkg-config \
        redis-tools \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r workflow && useradd -r -g workflow workflow

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-workflow.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-workflow.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./collaboration/workflow/ ./workflow/
COPY ./collaboration/common/ ./common/
COPY ./collaboration/workflows/ ./workflows/

# Create necessary directories
RUN mkdir -p /app/logs /app/temp /app/task_data && \
    chown -R workflow:workflow /app

# Switch to non-root user
USER workflow

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=workflow_manager
ENV LOG_LEVEL=INFO
ENV CELERY_BROKER_URL=${MESSAGE_QUEUE_URL}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "workflow.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]