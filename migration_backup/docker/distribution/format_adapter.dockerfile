# Format Adapter Service - Multi-platform content format optimization
# Converts and optimizes content for different platform requirements
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies for media processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    curl \
    git \
    build-essential \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libavutil-dev \
    libmagickwand-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/format-adapter.txt .
RUN pip install --no-cache-dir -r format-adapter.txt

# Multi-stage build for production
FROM base AS production

# Create non-root user
RUN groupadd -r processor && useradd -r -g processor processor

# Copy application code
COPY src/distribution/format_adapter/ ./format_adapter/
COPY src/distribution/common/ ./common/
COPY src/distribution/config/ ./config/

# Create directories for media processing
RUN mkdir -p /app/media /app/cache /app/temp /app/output
RUN chown -R processor:processor /app

# Copy ImageMagick policy for security
COPY docker/distribution/configs/imagemagick-policy.xml /etc/ImageMagick-6/policy.xml

# Switch to non-root user
USER processor

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')" || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHON_ENV=production
ENV PORT=8002
ENV FFMPEG_QUALITY=high
ENV MAX_FILE_SIZE=500MB
ENV ENABLE_GPU_ACCELERATION=false

# Run the application with higher worker timeout for media processing
CMD ["python", "-m", "uvicorn", "format_adapter.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2", "--timeout-keep-alive", "300"]