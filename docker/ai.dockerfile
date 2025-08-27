# AI Service Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN mkdir -p /app/models /app/processed

ENV PYTHONPATH=/app
ENV AI_SERVICE=true
EXPOSE 8004

CMD ["python", "-m", "ai_engine.music_generator"]