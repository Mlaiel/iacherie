# IA Influencer Agent - Logging Service Dockerfile
# Enterprise-grade logging infrastructure container
# Author: Fahed Mlaiel <mlaiel@live.de>

FROM python:3.11-slim

# Set labels for image metadata
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="IA Influencer Agent - Enterprise Logging Infrastructure"
LABEL version="1.0.0"
LABEL vendor="IA Influencer Agent"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r iaapp && useradd -r -g iaapp iaapp

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/ia-influencer \
    && mkdir -p /app/data \
    && mkdir -p /app/config

# Set proper permissions
RUN chown -R iaapp:iaapp /app \
    && chown -R iaapp:iaapp /var/log/ia-influencer

# Switch to non-root user
USER iaapp

# Expose ports
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import asyncio; from index import get_logging_system; \
                   asyncio.run(get_logging_system().health_check())" || exit 1

# Environment variables with defaults
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production
ENV SERVICE_NAME=ia-logging-service

# Default command
CMD ["python", "index.py", "start"]
