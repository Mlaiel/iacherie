# AI Detection Service
# AI-powered content detection for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue AI Detection - AI-generated content detection"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for AI/ML
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        # ML libraries system deps
        libhdf5-dev \
        libatlas-base-dev \
        libopenblas-dev \
        # Image processing
        libpng-dev \
        libjpeg-dev \
        # Audio processing
        libsndfile1-dev \
        ffmpeg \
        # GPU support (optional)
        nvidia-cuda-toolkit \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r aidetection && useradd -r -g aidetection aidetection

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-ai-detection.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-ai-detection.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./protection/ai_detection/ ./ai_detection/
COPY ./protection/common/ ./common/
COPY ./models/detection/ ./models/

# Create necessary directories
RUN mkdir -p /app/storage/detection/input \
             /app/storage/detection/analysis \
             /app/storage/detection/reports \
             /app/logs \
             /app/cache && \
    chown -R aidetection:aidetection /app

# Switch to non-root user
USER aidetection

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=ai_detection
ENV LOG_LEVEL=INFO
ENV DETECTION_THRESHOLD=0.85
ENV SUPPORTED_FORMATS="mp3,wav,mp4,jpg,png,txt"
ENV AI_MODEL_PATH=/app/models

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8040/health || exit 1

# Expose port
EXPOSE 8040

# Default command
CMD ["python", "-m", "ai_detection.main"]