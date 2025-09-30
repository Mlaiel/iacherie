# Multi-Stage Dockerfile for Ainflue Creator Economy Platform
# =============================================================
#
# 🎯 DEVOPS ENGINEER + CONTAINER EXPERT + SECURITY SPECIALIST
# Lead: Fahed Mlaiel (mlaiel@live.de)
#
# Production-ready container configuration for Creator Economy services:
# - Multi-stage build for optimal image size
# - Security-first approach with non-root user
# - Health checks and monitoring integration
# - Creator Economy specific optimizations
# - AI processing capabilities support
# - Content processing tools integration
#
# ⚠️ INTELLECTUAL PROPERTY PROTECTION:
# ==========================================
# © 2025 Fahed Mlaiel <mlaiel@live.de>
# TOUS DROITS RÉSERVÉS
#
# 🚨 PROTECTION INTELLECTUELLE:
# - Code propriétaire de Fahed Mlaiel
# - Utilisation commerciale INTERDITE sans autorisation écrite
# - Reverse engineering STRICTEMENT INTERDIT
# - Distribution INTERDITE sans licence explicite
# - Violation = Poursuites judiciaires automatiques
#
# Created: 2025-01-18
# Version: 1.0.0

# ==============================================================================
# BUILD STAGE - Dependencies and compilation
# ==============================================================================
FROM python:3.11-slim as builder

# Build arguments
ARG APP_NAME=ainflue-creator-platform
ARG APP_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF
ARG BUILD_ENV=production

# Metadata labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>" \
      org.label-schema.name="${APP_NAME}" \
      org.label-schema.version="${APP_VERSION}" \
      org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.vendor="Ainflue Creator Economy" \
      org.label-schema.description="Creator Economy Platform - Enterprise Container" \
      org.label-schema.url="https://ainflue.com" \
      org.label-schema.schema-version="1.0" \
      org.opencontainers.image.title="${APP_NAME}" \
      org.opencontainers.image.description="Ainflue Creator Economy Platform" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.authors="Fahed Mlaiel <mlaiel@live.de>" \
      org.opencontainers.image.vendor="Ainflue" \
      org.opencontainers.image.licenses="Proprietary" \
      intellectual.property.owner="Fahed Mlaiel" \
      business.unit="CreatorEconomy" \
      security.level="Enterprise"

# Set environment variables for build optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry/cache \
    POETRY_HOME="/opt/poetry" \
    VENV_PATH="/opt/venv"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    # Development headers
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    # Media processing libraries for Creator Economy
    ffmpeg \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    # Image processing
    libopencv-dev \
    python3-opencv \
    # Audio processing
    libsndfile1-dev \
    libasound2-dev \
    # Network tools
    curl \
    wget \
    git \
    # System utilities
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create Python virtual environment
RUN python -m venv $VENV_PATH

# Install Poetry
RUN pip install --upgrade pip setuptools wheel \
    && pip install poetry==1.6.1

# Create working directory
WORKDIR /build

# Copy dependency files first (for better caching)
COPY pyproject.toml poetry.lock* requirements*.txt ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project true \
    && poetry config cache-dir $POETRY_CACHE_DIR

# Install Python dependencies
RUN if [ -f pyproject.toml ]; then \
        poetry install --only=main --no-dev; \
    else \
        pip install -r requirements.txt && \
        if [ -f requirements-production.txt ]; then \
            pip install -r requirements-production.txt; \
        fi; \
    fi

# Install Creator Economy specific packages
RUN pip install \
    # AI/ML frameworks
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    tensorflow \
    transformers \
    # Media processing
    Pillow \
    opencv-python-headless \
    imageio \
    scikit-image \
    # Audio processing
    librosa \
    pydub \
    soundfile \
    # Video processing
    moviepy \
    # Content analysis
    nltk \
    spacy \
    # Performance optimization
    numba \
    cython

# Download NLTK and spaCy models
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')" \
    && python -m spacy download en_core_web_sm

# ==============================================================================
# RUNTIME STAGE - Minimal production image
# ==============================================================================
FROM python:3.11-slim as runtime

# Build arguments for runtime
ARG APP_NAME=ainflue-creator-platform
ARG APP_VERSION=1.0.0
ARG BUILD_ENV=production

# Copy metadata from builder
COPY --from=builder /etc/os-release /etc/os-release

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Application settings
    APP_NAME=${APP_NAME} \
    APP_VERSION=${APP_VERSION} \
    APP_ENV=${BUILD_ENV} \
    # Server configuration
    HOST=0.0.0.0 \
    PORT=8000 \
    WORKERS=4 \
    # Creator Economy settings
    CONTENT_PROCESSING_ENABLED=true \
    AI_PROCESSING_ENABLED=true \
    COLLABORATION_ENABLED=true \
    MONETIZATION_ENABLED=true \
    SEO_OPTIMIZATION_ENABLED=true \
    # Security settings
    SECURE_SSL_REDIRECT=true \
    SECURE_HSTS_SECONDS=31536000 \
    SECURE_CONTENT_TYPE_NOSNIFF=true \
    SECURE_BROWSER_XSS_FILTER=true \
    # Performance settings
    MAX_WORKERS=16 \
    WORKER_TIMEOUT=120 \
    KEEPALIVE=5 \
    MAX_REQUESTS=1000 \
    MAX_REQUESTS_JITTER=100

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime libraries
    libpq5 \
    libffi8 \
    libssl3 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    # Media processing runtime libraries
    ffmpeg \
    libavformat59 \
    libavcodec59 \
    libavutil57 \
    libswscale6 \
    libswresample4 \
    # Image processing runtime
    libopencv-core4.5d \
    libopencv-imgproc4.5d \
    libopencv-imgcodecs4.5d \
    # Audio processing runtime
    libsndfile1 \
    libasound2 \
    # System utilities
    curl \
    ca-certificates \
    tzdata \
    # Process management
    dumb-init \
    # Monitoring tools
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r ainflue && \
    useradd -r -g ainflue -d /app -s /bin/bash ainflue && \
    mkdir -p /app /app/logs /app/tmp /app/uploads /app/cache && \
    chown -R ainflue:ainflue /app

# Copy virtual environment from builder
COPY --from=builder --chown=ainflue:ainflue /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=ainflue:ainflue . .

# Install application in development mode if setup.py exists
RUN if [ -f setup.py ]; then \
        pip install -e .; \
    fi

# Create required directories and set permissions
RUN mkdir -p \
    /app/static \
    /app/media \
    /app/reports \
    /app/backups \
    /app/content/video \
    /app/content/audio \
    /app/content/images \
    /app/content/documents \
    && chown -R ainflue:ainflue /app \
    && chmod -R 755 /app \
    && chmod -R 775 /app/logs /app/tmp /app/uploads /app/cache /app/media /app/content

# Copy and set up entrypoint script
COPY --chown=ainflue:ainflue docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch to non-root user
USER ainflue

# Expose application port
EXPOSE 8000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Add volume for persistent data
VOLUME ["/app/uploads", "/app/logs", "/app/content"]

# Set entrypoint
ENTRYPOINT ["dumb-init", "--", "/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ==============================================================================
# SPECIALIZED VARIANTS
# ==============================================================================

# AI Processing variant with GPU support
FROM runtime as ai-processing
USER root

# Install CUDA runtime for GPU processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-cuda-runtime \
    && rm -rf /var/lib/apt/lists/*

# Install GPU-accelerated packages
RUN pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 \
    tensorflow-gpu \
    cupy-cuda11x

USER ainflue

# Override environment for AI processing
ENV AI_PROCESSING_MODE=gpu \
    CUDA_VISIBLE_DEVICES=all \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

CMD ["python", "-m", "uvicorn", "ai_processor:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Development variant
FROM runtime as development
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    nano \
    tree \
    strace \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install \
    ipdb \
    ipython \
    jupyter \
    pytest \
    pytest-cov \
    black \
    isort \
    mypy \
    flake8

USER ainflue

# Override environment for development
ENV APP_ENV=development \
    DEBUG=true \
    RELOAD=true

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Creator Tools variant
FROM runtime as creator-tools
USER root

# Install additional creator economy tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Video editing tools
    handbrake-cli \
    mkvtoolnix \
    # Audio editing tools
    audacity \
    lame \
    # Image editing tools
    imagemagick \
    gimp \
    # Document processing
    pandoc \
    texlive-base \
    && rm -rf /var/lib/apt/lists/*

# Install creator-specific Python packages
RUN pip install \
    # Video processing
    vidgear \
    decord \
    # Audio processing
    librosa \
    essentia \
    # Image processing
    albumentations \
    imagehash \
    # Document processing
    pypdf2 \
    python-docx \
    # Social media integration
    tweepy \
    facebook-sdk \
    google-api-python-client

USER ainflue

# Override environment for creator tools
ENV CREATOR_TOOLS_ENABLED=true \
    VIDEO_PROCESSING_ENABLED=true \
    AUDIO_PROCESSING_ENABLED=true \
    IMAGE_PROCESSING_ENABLED=true \
    DOCUMENT_PROCESSING_ENABLED=true

CMD ["python", "-m", "uvicorn", "creator_tools:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]