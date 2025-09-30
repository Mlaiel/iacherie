# Collaboration Matcher Service
# AI-powered creator matching and compatibility analysis
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Collaboration Matcher - AI-powered creator matching service"
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
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r collaboration && useradd -r -g collaboration collaboration

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-collaboration.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-collaboration.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./collaboration/matcher/ ./matcher/
COPY ./collaboration/common/ ./common/
COPY ./collaboration/models/ ./models/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/models && \
    chown -R collaboration:collaboration /app

# Switch to non-root user
USER collaboration

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=collaboration_matcher
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "matcher.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]