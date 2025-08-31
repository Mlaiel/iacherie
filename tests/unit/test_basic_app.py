# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys

import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Basic FastAPI application test to verify dependencies and startup
"""

import sys

from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI

from pydantic import BaseModel

import uvicorn

# Test basic imports that should work with installed dependencies
try:
    import passlib
    import pydantic_settings
    import aiohttp
    import cryptography
    import pytest_asyncio
    print("✓ All required dependencies are installed:")
    print(f"  - passlib: {passlib.__version__}")
    print(f"  - pydantic-settings: Available")
    print(f"  - aiohttp: {aiohttp.__version__}")
    print(f"  - cryptography: {cryptography.__version__}")
    print(f"  - pytest-asyncio: Available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)

# Create basic FastAPI app
app = FastAPI(
    title="Ainflue Platform Test",
    description="Basic test to verify FastAPI startup",
    version="1.0.0"
)

class TestResponse(BaseModel):
    message: str
    status: str

@app.get("/", response_model=TestResponse)
async def root():
    return TestResponse(
        message="Ainflue Platform is running!",
        status="success"
    )

@app.get("/health", response_model=TestResponse)
async def health_check():
    return TestResponse(
        message="All systems operational",
        status="healthy"
    )

if __name__ == "__main__":
    print("🚀 Starting basic Ainflue FastAPI test server...")
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)