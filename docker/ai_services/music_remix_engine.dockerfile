# Music Remix Engine Service
# AI-powered music remixing and audio manipulation service
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.12-slim AS base
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Ainflue Music Remix Engine - AI music processing service"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq5 libpq-dev pkg-config \
    ffmpeg libsndfile1 portaudio19-dev && rm -rf /var/lib/apt/lists/*
RUN groupadd -r remix && useradd -r -g remix remix

FROM base AS dependencies
COPY requirements.txt requirements-audio.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-audio.txt

FROM base AS production
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./ai_services/remix/ ./remix/
COPY ./ai_services/common/ ./common/
RUN mkdir -p /app/models /app/audio_processing /app/logs && chown -R remix:remix /app
USER remix
ENV PYTHONPATH=/app SERVICE_NAME=music_remix_engine
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "remix.main:app", "--host", "0.0.0.0", "--port", "8000"]