"""WSGI application entry point (e.g., for Gunicorn/uWSGI or AWS Lambda via Mangum).
English-only comments and professional naming.
"""
import os
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from backend.app.api import router as api_router
from backend.app.core import settings
from mangum import Mangum

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN", ""))

app = FastAPI(title="IA Influencer Agent Backend", version="1.0.0", docs_url="/docs", openapi_url="/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)
FastAPIInstrumentor.instrument_app(app)
root_prefix = settings.api_root_prefix.rstrip("/")
app.include_router(api_router, prefix=root_prefix)

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}

@app.get("/ready", tags=["System"])
def ready():
    return {"status": "ready"}

# WSGI handler for Gunicorn, uWSGI, AWS Lambda (via Mangum)
handler = Mangum(app)
