# Compliance Monitor Service - Regulatory compliance monitoring and reporting  
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl git build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements/compliance-monitor.txt .
RUN pip install --no-cache-dir -r compliance-monitor.txt

FROM base AS production
RUN groupadd -r compliance && useradd -r -g compliance compliance
COPY src/security/compliance_monitor/ ./compliance_monitor/
COPY src/security/common/ ./common/
RUN mkdir -p /app/reports /app/evidence && chown -R compliance:compliance /app
USER compliance
EXPOSE 8107
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8107/health')" || exit 1
ENV PYTHONPATH=/app PORT=8107 COMPLIANCE_STANDARDS=ISO27001,SOC2,GDPR
CMD ["python", "-m", "uvicorn", "compliance_monitor.main:app", "--host", "0.0.0.0", "--port", "8107"]