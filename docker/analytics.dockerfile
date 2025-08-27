# Analytics Service Dockerfile  
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONPATH=/app
ENV ANALYTICS_SERVICE=true
EXPOSE 8003

CMD ["python", "-m", "analytics.revenue_tracker"]