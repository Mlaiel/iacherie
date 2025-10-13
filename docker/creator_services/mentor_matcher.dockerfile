# Mentor Matcher Service - AI-powered mentor matching and mentorship management
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/mentor-matcher.txt .
RUN pip install --no-cache-dir -r mentor-matcher.txt

FROM base AS production
RUN groupadd -r mentor && useradd -r -g mentor mentor
COPY src/creator_services/mentor_matcher/ ./mentor_matcher/
RUN mkdir -p /app/models /app/mentors /app/mentorships && chown -R mentor:mentor /app
USER mentor
EXPOSE 8309
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8309/health || exit 1
ENV PYTHONPATH=/app PORT=8309
CMD ["python", "-m", "uvicorn", "mentor_matcher.main:app", "--host", "0.0.0.0", "--port", "8309"]