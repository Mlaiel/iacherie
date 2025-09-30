# =============================================================================
# AINFLUE PLAGIARISM CHECKER - SPECIALIZED DOCKERFILE
# =============================================================================
# Multi-stage Docker build for advanced plagiarism detection supporting
# text, audio, video, and image similarity detection with ML-based analysis.
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

ARG PYTHON_VERSION=3.11
ARG UBUNTU_VERSION=22.04
ARG BUILD_ENV=production

# =============================================================================
# STAGE 1: PLAGIARISM DETECTION BASE
# =============================================================================
FROM ubuntu:${UBUNTU_VERSION} AS plagiarism-base

LABEL stage=plagiarism-base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Advanced plagiarism detection engine"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install plagiarism detection dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        build-essential \
        pkg-config \
        ffmpeg \
        libopencv-dev \
        libtesseract-dev \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-fra \
        tesseract-ocr-deu \
        tesseract-ocr-ara \
        poppler-utils \
        libmagic-dev \
        curl \
        wget \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# STAGE 2: PYTHON DEPENDENCIES
# =============================================================================
FROM plagiarism-base AS plagiarism-deps

WORKDIR /tmp

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install plagiarism detection packages
RUN pip3 install --no-cache-dir \
        nltk>=3.8.0 \
        spacy>=3.7.0 \
        transformers>=4.35.0 \
        sentence-transformers>=2.2.0 \
        scikit-learn>=1.3.0 \
        fuzzywuzzy>=0.18.0 \
        python-Levenshtein>=0.21.0 \
        librosa>=0.10.0 \
        soundfile>=0.12.0 \
        opencv-python>=4.8.0 \
        pillow>=10.0.0 \
        pytesseract>=0.3.10 \
        PyPDF2>=3.0.0 \
        python-docx>=0.8.11 \
        beautifulsoup4>=4.12.0 \
        requests>=2.31.0 \
        aiohttp>=3.9.0 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pydantic>=2.5.0 \
        redis>=5.0.0 \
        prometheus-client>=0.19.0

# Download spaCy models
RUN python3 -m spacy download en_core_web_sm && \
    python3 -m spacy download fr_core_news_sm && \
    python3 -m spacy download de_core_news_sm

# =============================================================================
# STAGE 3: APPLICATION ENVIRONMENT
# =============================================================================
FROM plagiarism-deps AS plagiarism-app

WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./protection/plagiarism_checker/ /app/
COPY --chown=appuser:appuser ./core/ml_utils.py /app/core/
COPY --chown=appuser:appuser ./config/protection_config.py /app/config/

# Create directories for analysis data
RUN mkdir -p /app/models /app/datasets /app/cache /app/reports && \
    chown -R appuser:appuser /app/models /app/datasets /app/cache /app/reports

# Set up Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Environment variables
ENV SIMILARITY_THRESHOLD=0.85
ENV ENABLE_AUDIO_PLAGIARISM=true
ENV ENABLE_VIDEO_PLAGIARISM=true
ENV ENABLE_IMAGE_PLAGIARISM=true

# Expose port for API
EXPOSE 8041

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8041/health || exit 1

# Switch to non-root user
USER appuser

# Start plagiarism checker service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8041", "--workers", "2"]