# Noise Reducer Service
# Advanced noise reduction for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Noise Reducer - Advanced audio noise reduction"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        # Audio processing libraries
        ffmpeg \
        sox \
        libsox-fmt-all \
        libsndfile1-dev \
        libsamplerate0-dev \
        # Advanced audio processing tools
        audacity \
        ladspa-sdk \
        # Spectral analysis tools
        fftw3-dev \
        libfftw3-dev \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r noisereducer && useradd -r -g noisereducer noisereducer

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-noise.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-noise.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./audio/noise_reducer/ ./noise_reducer/
COPY ./audio/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/storage/noise/input \
             /app/storage/noise/output \
             /app/storage/noise/profiles \
             /app/logs \
             /app/cache && \
    chown -R noisereducer:noisereducer /app

# Switch to non-root user
USER noisereducer

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=noise_reducer
ENV LOG_LEVEL=INFO
ENV NOISE_REDUCTION_STRENGTH=medium
ENV PRESERVE_SPEECH=true
ENV SPECTRAL_GATE_THRESHOLD=-20

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8024/health || exit 1

# Expose port
EXPOSE 8024

# Default command
CMD ["python", "-m", "noise_reducer.main"]