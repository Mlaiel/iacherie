# Multitrack Mixer Service
# Professional multitrack mixing for Ainflue Platform
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim AS base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Multitrack Mixer - Professional multitrack audio mixing"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for audio mixing
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
        # Advanced audio tools
        ladspa-sdk \
        lv2-dev \
        # Audio plugins
        swh-plugins \
        tap-plugins \
        # Pro audio formats
        libflac-dev \
        libvorbis-dev \
        libopus-dev \
        libaac-dev \
        # Mixing console emulation
        ardour \
        mixxx \
        && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r mixer && useradd -r -g mixer mixer

# Install Python dependencies stage
FROM base AS dependencies
COPY requirements.txt requirements-mixer.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-mixer.txt

# Production stage
FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY ./audio/multitrack_mixer/ ./multitrack_mixer/
COPY ./audio/common/ ./common/
COPY ./config/mixer_presets/ ./presets/

# Create necessary directories
RUN mkdir -p /app/storage/mixer/input \
             /app/storage/mixer/output \
             /app/storage/mixer/tracks \
             /app/storage/mixer/projects \
             /app/storage/mixer/temp \
             /app/logs \
             /app/cache \
             /app/plugins && \
    chown -R mixer:mixer /app

# Copy mixing presets and templates
COPY ./templates/mixer/ ./templates/
COPY ./plugins/audio/ ./plugins/

# Switch to non-root user
USER mixer

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=multitrack_mixer
ENV LOG_LEVEL=INFO
ENV MAX_TRACKS=64
ENV MAX_PROJECT_SIZE=10GB
ENV MIXING_QUALITY=high
ENV AUTO_NORMALIZE=true
ENV DEFAULT_SAMPLE_RATE=48000
ENV DEFAULT_BIT_DEPTH=24

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8022/health || exit 1

# Expose port
EXPOSE 8022

# Default command
CMD ["python", "-m", "multitrack_mixer.main"]