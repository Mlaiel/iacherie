# Stem Separator Service
# AI-powered stem separation for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Stem Separator - AI-powered audio stem separation"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing and ML
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        # Audio libraries
        ffmpeg \
        sox \
        libsox-fmt-all \
        libsndfile1-dev \
        libsamplerate0-dev \
        # ML dependencies
        libhdf5-dev \
        libatlas-base-dev \
        libopenblas-dev \
        # GPU support (optional)
        nvidia-cuda-toolkit \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r stemsep && useradd -r -g stemsep stemsep

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-stems.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-stems.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./audio/stem_separator/ ./stem_separator/
COPY ./audio/common/ ./common/
COPY ./models/separation/ ./models/

# Create necessary directories
RUN mkdir -p /app/storage/stems/input \
             /app/storage/stems/output \
             /app/storage/stems/vocals \
             /app/storage/stems/drums \
             /app/storage/stems/bass \
             /app/storage/stems/other \
             /app/logs \
             /app/cache && \
    chown -R stemsep:stemsep /app

# Switch to non-root user
USER stemsep

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=stem_separator
ENV LOG_LEVEL=INFO
ENV SEPARATION_MODEL=spleeter
ENV OUTPUT_STEMS=4
ENV MAX_DURATION=600

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8023/health || exit 1

# Expose port
EXPOSE 8023

# Default command
CMD ["python", "-m", "stem_separator.main"]