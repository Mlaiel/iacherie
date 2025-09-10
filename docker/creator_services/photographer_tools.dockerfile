# Photographer Tools Service - Image processing and photography tools
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y libopencv-dev python3-opencv imagemagick curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/photographer-tools.txt .
RUN pip install --no-cache-dir -r photographer-tools.txt

FROM base AS production
RUN groupadd -r photographer && useradd -r -g photographer photographer
COPY src/creator_services/photographer_tools/ ./photographer_tools/
RUN mkdir -p /app/models /app/images /app/gallery && chown -R photographer:photographer /app
USER photographer
EXPOSE 8301
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8301/health || exit 1
ENV PYTHONPATH=/app PORT=8301 IMAGE_ENGINE=opencv
CMD ["python", "-m", "uvicorn", "photographer_tools.main:app", "--host", "0.0.0.0", "--port", "8301"]