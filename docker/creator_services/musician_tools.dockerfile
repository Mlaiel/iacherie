# Musician Tools Service - Audio processing and music creation tools
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/musician-tools.txt .
RUN pip install --no-cache-dir -r musician-tools.txt

FROM base AS production
RUN groupadd -r musician && useradd -r -g musician musician
COPY src/creator_services/musician_tools/ ./musician_tools/
RUN mkdir -p /app/models /app/audio /app/library && chown -R musician:musician /app
USER musician
EXPOSE 8300
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8300/health || exit 1
ENV PYTHONPATH=/app PORT=8300 AUDIO_ENGINE=ffmpeg
CMD ["python", "-m", "uvicorn", "musician_tools.main:app", "--host", "0.0.0.0", "--port", "8300"]