# Skill Mapper Service - Skill analysis and learning recommendations
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/skill-mapper.txt .
RUN pip install --no-cache-dir -r skill-mapper.txt

FROM base AS production
RUN groupadd -r skillmap && useradd -r -g skillmap skillmap
COPY src/creator_services/skill_mapper/ ./skill_mapper/
RUN mkdir -p /app/models /app/assessments && chown -R skillmap:skillmap /app
USER skillmap
EXPOSE 8306
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8306/health || exit 1
ENV PYTHONPATH=/app PORT=8306
CMD ["python", "-m", "uvicorn", "skill_mapper.main:app", "--host", "0.0.0.0", "--port", "8306"]