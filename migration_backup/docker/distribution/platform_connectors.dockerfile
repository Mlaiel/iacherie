# Platform Connectors Service - Multi-platform API integration
# Handles connections to YouTube, Instagram, TikTok, Spotify, etc.
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/platform-connectors.txt .
RUN pip install --no-cache-dir -r platform-connectors.txt

# Multi-stage build for production
FROM base AS production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY src/distribution/platform_connectors/ ./platform_connectors/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8000

# Run the application
CMD ["python", "-m", "uvicorn", "platform_connectors.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]