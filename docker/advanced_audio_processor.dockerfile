# Advanced Real-Time Audio Processing Service
# High-performance audio processing with AI enhancement
# Author: Fahed Mlaiel (mlaiel@live.de) - Audio Processing Engineer Role

FROM ubuntu:22.04 AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Advanced Audio Processor - Real-time AI-enhanced audio processing"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install comprehensive audio processing dependencies
RUN apt-get update && apt-get install -y \
    # Core audio libraries
    ffmpeg \
    libsndfile1-dev \
    libportaudio2 \
    portaudio19-dev \
    libasound2-dev \
    libpulse-dev \
    libflac-dev \
    libvorbis-dev \
    libmp3lame-dev \
    libfaac-dev \
    libx264-dev \
    # Advanced audio processing
    sox \
    libsox-dev \
    aubio-tools \
    libaubio-dev \
    # Real-time audio
    jackd2 \
    qjackctl \
    # AI/ML audio libraries
    librubberband-dev \
    libfftw3-dev \
    libsamplerate0-dev \
    # Python and dependencies
    python3 \
    python3-pip \
    python3-dev \
    # System tools
    curl \
    wget \
    git \
    build-essential \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install specialized Python audio libraries
RUN pip3 install --no-cache-dir \
    # Core audio processing
    librosa \
    soundfile \
    audioread \
    pyaudio \
    pydub \
    # Advanced audio analysis
    essentia \
    madmom \
    aubio \
    # AI audio processing
    torch \
    torchaudio \
    tensorflow \
    # Real-time processing
    sounddevice \
    pyaudio \
    # Audio features
    python_speech_features \
    spectral-connectivity \
    # Streaming
    rtmp-python \
    websockets \
    # Performance
    numba \
    numpy \
    scipy

# Copy audio processing source code
COPY ./audio_processing/ ./processing/
COPY ./audio/common/ ./common/

# Security: Create audio processing user
RUN groupadd --gid 1000 audioprocessor && \
    useradd --uid 1000 --gid audioprocessor --shell /bin/bash --create-home audioprocessor && \
    usermod -aG audio audioprocessor

# Create audio processing directories
RUN mkdir -p \
    /app/input \
    /app/output \
    /app/temp \
    /app/models \
    /app/cache \
    /app/logs \
    /app/streaming \
    && chown -R audioprocessor:audioprocessor /app \
    && chmod 755 /app \
    && chmod 777 /app/input /app/output /app/temp

# Configure audio system
RUN echo "audioprocessor ALL=(ALL) NOPASSWD: /usr/bin/jackd" >> /etc/sudoers

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/* \
    && find /app -name "*.pyc" -delete

# Switch to audio processing user
USER audioprocessor

# Audio processing environment variables
ENV PYTHONPATH=/app \
    SERVICE_NAME=advanced_audio_processor \
    AUDIO_SAMPLE_RATE=48000 \
    AUDIO_CHANNELS=2 \
    BUFFER_SIZE=512 \
    JACK_NO_AUDIO_RESERVATION=1 \
    PULSE_PLAYBACK_CORK_FIX=1

# Health check for audio service
HEALTHCHECK --interval=30s --timeout=15s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/audio/health').raise_for_status()" || exit 1

EXPOSE 8000 8001 8002

# Start advanced audio processing service
CMD ["python3", "-m", "uvicorn", "processing.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info"]