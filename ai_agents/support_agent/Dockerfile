# Multi-stage Dockerfile for Support Agent - Production Ready
# Ultra-Advanced AI Customer Support & Assistance System
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  CRITICAL LEGAL NOTICE:
# This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
# Unauthorized use, copying, distribution, or commercialization is strictly prohibited.

# Stage 1: Base image with Python and system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system support && \
    useradd --system --group support --home /app support

# Stage 2: Dependencies installation
FROM base as dependencies

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Development image
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy

# Copy source code
COPY . .

# Change ownership to support user
RUN chown -R support:support /app

USER support

# Expose development port
EXPOSE 8080

# Development command
CMD ["python", "-m", "uvicorn", "support_agent.server:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# Stage 4: Production image
FROM dependencies as production

# Copy only necessary files for production
COPY --chown=support:support ./support_agent ./support_agent
COPY --chown=support:support ./config ./config
COPY --chown=support:support ./__init__.py ./__init__.py

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/models && \
    chown -R support:support /app

# Switch to non-root user
USER support

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose production port
EXPOSE 8080

# Production command
CMD ["python", "-m", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "support_agent.server:app"]

# Stage 5: Testing image
FROM development as testing

# Run tests
RUN python -m pytest tests/ -v --cov=support_agent --cov-report=term-missing

# Stage 6: Security scanning (optional)
FROM production as security

USER root

# Install security scanning tools
RUN pip install --no-cache-dir safety bandit

# Run security checks
RUN safety check && \
    bandit -r support_agent/

USER support

# Labels for metadata
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \
      version="2.1.0" \
      description="Support Agent - Ultra-Advanced AI Customer Support System" \
      copyright="© 2025 Fahed Mlaiel. All rights reserved." \
      license="Proprietary"

# Default to production stage
FROM production
