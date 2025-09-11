# Neural Enhancement Service
# AI-powered neural audio enhancement for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Neural Enhancement - AI-powered audio neural enhancement"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies and AI libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libsndfile1-dev \
        libsamplerate0-dev \
        ffmpeg \
        sox \
        libsox-fmt-all \
        # GPU support (optional)
        nvidia-cuda-toolkit \
        # Audio processing
        portaudio19-dev \
        libasound2-dev \
        # ML libraries system deps
        libhdf5-dev \
        pkg-config \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r neuralaudio && useradd -r -g neuralaudio neuralaudio

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-neural.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-neural.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./audio/neural_enhancement/ ./neural_enhancement/
COPY ./audio/common/ ./common/
COPY ./models/audio/ ./models/

# Create necessary directories
RUN mkdir -p /app/storage/neural/input \
             /app/storage/neural/output \
             /app/storage/neural/temp \
             /app/storage/neural/models \
             /app/logs \
             /app/cache && \
    chown -R neuralaudio:neuralaudio /app

# Download pre-trained models
RUN python -c "import torch;  import torchaudio;  from transformers import AutoModel;  # Download pre-trained models;  print('Downloading neural enhancement models...')" || echo "Models will be downloaded at runtime"

# Switch to non-root user
USER neuralaudio

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=neural_enhancement
ENV LOG_LEVEL=INFO
ENV NEURAL_MODEL_PATH=/app/models
ENV ENHANCEMENT_QUALITY=high
ENV BATCH_SIZE=4
ENV MAX_DURATION=300

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

# Expose port
EXPOSE 8020

# Default command
CMD ["python", "-m", "neural_enhancement.main"]