# Influencer Tools Service - Social media and influencer marketing tools
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/influencer-tools.txt .
RUN pip install --no-cache-dir -r influencer-tools.txt

FROM base AS production
RUN groupadd -r influencer && useradd -r -g influencer influencer
COPY src/creator_services/influencer_tools/ ./influencer_tools/
RUN mkdir -p /app/models /app/partnerships /app/engagement && chown -R influencer:influencer /app
USER influencer
EXPOSE 8303
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8303/health || exit 1
ENV PYTHONPATH=/app PORT=8303
CMD ["python", "-m", "uvicorn", "influencer_tools.main:app", "--host", "0.0.0.0", "--port", "8303"]