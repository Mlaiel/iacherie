# Ainflue Platform - CI/Development Dockerfile
# Simplified version for CI builds and development

FROM python:3.12-slim

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Platform - CI/Development Build"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq5 \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r ainflue && useradd -r -g ainflue ainflue && \
    chown -R ainflue:ainflue /app
USER ainflue

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import main; print('OK')" || exit 1

# Default command
CMD ["python", "main.py"]