# =============================================================================
# AINFLUE INVOICE GENERATOR - AUTOMATED DOCKERFILE
# =============================================================================

FROM ubuntu:22.04 AS invoice-base

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL description="Automated invoice generation and management"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-dev python3-pip \
        build-essential curl \
        wkhtmltopdf \
        && rm -rf /var/lib/apt/lists/*

RUN groupadd -r invoiceuser && \
    useradd -r -g invoiceuser -d /app invoiceuser && \
    mkdir -p /app && chown -R invoiceuser:invoiceuser /app

FROM invoice-base AS invoice-deps

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir \
        jinja2 pdfkit reportlab \
        fastapi uvicorn pydantic celery redis \
        psycopg2-binary SQLAlchemy prometheus-client

FROM invoice-deps AS production

WORKDIR /app
COPY ./invoice_generator /app/invoice_generator
COPY ./core /app/core

RUN mkdir -p /app/storage/invoices/{generated,templates} \
             /app/logs && \
    chown -R invoiceuser:invoiceuser /app

USER invoiceuser

ENV INVOICE_SERVICE_PORT=8048
ENV INVOICE_SEQUENCE_START=10000
ENV AUTO_SEND_INVOICES=false

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${INVOICE_SERVICE_PORT}/health || exit 1

EXPOSE ${INVOICE_SERVICE_PORT}
CMD ["python3.11", "-m", "invoice_generator.main"]

LABEL org.opencontainers.image.title="Ainflue Invoice Generator"
LABEL ainflue.service.category="monetization"
LABEL ainflue.service.name="invoice_generator"
LABEL ainflue.service.port="8048"