# Penetration Tester Service - Automated penetration testing and security assessment
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y curl git build-essential nmap masscan nikto && rm -rf /var/lib/apt/lists/*
COPY requirements/penetration-tester.txt .
RUN pip install --no-cache-dir -r penetration-tester.txt

FROM base AS production
RUN groupadd -r pentest && useradd -r -g pentest pentest
COPY src/security/penetration_tester/ ./penetration_tester/
COPY src/security/common/ ./common/
RUN mkdir -p /app/reports /app/tools && chown -R pentest:pentest /app
USER pentest
EXPOSE 8108
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8108/health || exit 1
ENV PYTHONPATH=/app PORT=8108 TEST_FREQUENCY=weekly
CMD ["python", "-m", "uvicorn", "penetration_tester.main:app", "--host", "0.0.0.0", "--port", "8108"]