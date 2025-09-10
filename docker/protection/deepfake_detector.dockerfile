# Deepfake Detector Service
# Advanced deepfake detection for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Deepfake Detector - Advanced deepfake detection"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for computer vision and ML
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        # Computer vision libraries
        libopencv-dev \
        python3-opencv \
        # Image processing
        libpng-dev \
        libjpeg-dev \
        libtiff-dev \
        # Video processing
        ffmpeg \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        # ML libraries system deps
        libhdf5-dev \
        libatlas-base-dev \
        libopenblas-dev \
        # GPU support (optional)
        nvidia-cuda-toolkit \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r deepfake && useradd -r -g deepfake deepfake

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-deepfake.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-deepfake.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./protection/deepfake_detector/ ./deepfake_detector/
COPY ./protection/common/ ./common/
COPY ./models/deepfake/ ./models/

# Create necessary directories
RUN mkdir -p /app/storage/deepfake/input \
             /app/storage/deepfake/analysis \
             /app/storage/deepfake/reports \
             /app/storage/deepfake/frames \
             /app/logs \
             /app/cache && \
    chown -R deepfake:deepfake /app

# Switch to non-root user
USER deepfake

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=deepfake_detector
ENV LOG_LEVEL=INFO
ENV DETECTION_CONFIDENCE=0.90
ENV FRAME_ANALYSIS_INTERVAL=30
ENV MAX_VIDEO_DURATION=3600
ENV SUPPORTED_FORMATS="mp4,avi,mov,jpg,png"

# Health check
HEALTHCHECK --interval=30s --timeout=20s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8041/health || exit 1

# Expose port
EXPOSE 8041

# Default command
CMD ["python", "-m", "deepfake_detector.main"]