# Identity Verifier Service - Identity verification and KYC
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl git build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/identity-verifier.txt .
RUN pip install --no-cache-dir -r identity-verifier.txt

FROM base AS production
RUN groupadd -r identity && useradd -r -g identity identity
COPY src/security/identity_verifier/ ./identity_verifier/
COPY src/security/common/ ./common/
RUN mkdir -p /app/documents && chown -R identity:identity /app
USER identity
EXPOSE 8105
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8105/health || exit 1
ENV PYTHONPATH=/app PORT=8105
CMD ["python", "-m", "uvicorn", "identity_verifier.main:app", "--host", "0.0.0.0", "--port", "8105"]