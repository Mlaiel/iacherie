# Monetization Service Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONPATH=/app
ENV MONETIZATION_SERVICE=true
EXPOSE 8002

CMD ["python", "-m", "monetization.payment_processor"]