"""
ASGI Application Entry Point
---------------------------
- Startet die FastAPI-ASGI-App für Spotify AI Agent
- Integriert Security, CORS, Observability, Health, Multilingual, Sentry, OpenTelemetry

Autoren & Rollen:
- Lead Dev, Architecte IA, Backend Senior, ML Engineer, DBA/Data Engineer, Security Specialist, Microservices Architect
"""

import os
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from backend.app.api import router as api_router
from backend.app.core import configure_logging, settings

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN", ""))

configure_logging()

app = FastAPI(
    title="IA Influencer Agent Backend",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Security: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability: Prometheus
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# Observability: OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# API Routing with configured root prefix (e.g., /api)
root_prefix = settings.api_root_prefix.rstrip("/")
app.include_router(api_router, prefix=root_prefix)

# Health Endpoint
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}

# Readiness Endpoint
@app.get("/ready", tags=["System"])
def ready():
    return {"status": "ready"}
