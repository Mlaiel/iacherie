# Real Time Processing Service
# Real-time audio processing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Real Time Processing - Low-latency audio processing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for real-time audio
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        # Real-time audio libraries
        libjack-jackd2-dev \
        jackd2 \
        portaudio19-dev \
        libasound2-dev \
        libpulse-dev \
        # Low-latency kernel optimizations
        rtirq-init \
        # Audio processing
        ffmpeg \
        sox \
        libsox-fmt-all \
        libsndfile1-dev \
        libsamplerate0-dev \
        # Performance monitoring
        htop \
        iotop \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security with audio group
RUN groupadd -r realtimeaudio && useradd -r -g realtimeaudio realtimeaudio
RUN usermod -a -G audio realtimeaudio

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-realtime.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-realtime.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./audio/real_time_processing/ ./real_time_processing/
COPY ./audio/common/ ./common/

# Create necessary directories
RUN mkdir -p /app/storage/realtime/input \
             /app/storage/realtime/output \
             /app/storage/realtime/buffer \
             /app/logs \
             /app/cache && \
    chown -R realtimeaudio:realtimeaudio /app

# Copy real-time configuration
COPY ./config/realtime_audio.conf /etc/security/limits.d/
COPY ./config/jack_settings.conf /app/config/

# Switch to non-root user
USER realtimeaudio

# Set environment variables for real-time performance
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=real_time_processing
ENV LOG_LEVEL=INFO
ENV RT_BUFFER_SIZE=256
ENV RT_SAMPLE_RATE=48000
ENV RT_LATENCY_TARGET=5
ENV MAX_CONCURRENT_STREAMS=16
ENV JACK_AUTO_START=true

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8021/health || exit 1

# Expose port
EXPOSE 8021

# Default command
CMD ["python", "-m", "real_time_processing.main"]