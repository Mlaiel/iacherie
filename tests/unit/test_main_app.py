# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""Simplified main.py to test core FastAPI startup functionality
This bypasses complex imports to focus on basic dependency testing
"""import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Test that we can import from config
try:
    from config import settings
    print("✓ Successfully imported config.py")
    print(f"✓ Environment: {settings.app.environment}")
    print(f"✓ Debug mode: {settings.app.debug}")
    print(f"✓ Host: {settings.app.host}")
    print(f"✓ Port: {settings.app.port}")
except Exception as e:
    print(f"❌ Failed to import config: {e}")
    # Create minimal fallback settings
    class MockSettings:
        class App:
            environment = "development"
            debug = True
            host = "127.0.0.1"
            port = 8000
        app = App()
    settings = MockSettings()
    print("⚠️  Using fallback settings")

# Try to import the main app or create a minimal one
try:
    from api.main import app
    print("✓ Successfully imported main FastAPI app")
except Exception as e:
    print(f"⚠️  Could not import api.main app: {e}")
    print("📦 Creating minimal FastAPI app for testing")
    
    # Create minimal FastAPI app
    app = FastAPI(
        title="Ainflue AI Platform",
        description="AI-Powered Content Protection & Monetization Platform",
        version="1.0.0"
    )
    
    class StatusResponse(BaseModel):
        message: str
        status: str
        environment: str
    
    @app.get("/", response_model=StatusResponse)
    async def root():
        return StatusResponse(
            message="Ainflue AI Platform is running!",
            status="success",
            environment=settings.app.environment
        )
    
    @app.get("/health", response_model=StatusResponse)
    async def health_check():
        return StatusResponse(
            message="Platform is healthy",
            status="operational",
            environment=settings.app.environment
        )

async def initialize_platform():
    """Initialize the platform on first run"""    try:
        print("📋 Initializing Ainflue platform...")
        
        # Try to create database tables (simplified)
        try:
            from database.schema import create_tables
            await create_tables()
            print("✓ Database tables created")
        except Exception as e:
            print(f"⚠️  Database initialization skipped: {e}")
        
        print("✅ Platform initialization completed")
        
    except Exception as e:
        print(f"❌ Platform initialization failed: {str(e)}")
        raise

def main():
    """Main entry point"""    print("🚀 Starting Ainflue AI Platform")
    print(f"📍 Environment: {settings.app.environment}")
    print(f"🔧 Debug mode: {settings.app.debug}")
    
    try:
        # Initialize platform if needed
        if settings.app.environment in ["development", "staging"]:
            print("🔄 Running platform initialization...")
            try:
                asyncio.run(initialize_platform())
            except Exception as e:
                print(f"⚠️  Initialization failed but continuing: {e}")
        
        # Start the server
        print(f"🌐 Starting server on {settings.app.host}:{settings.app.port}")
        uvicorn.run(
            app,
            host=settings.app.host,
            port=settings.app.port,
            reload=False,  # Disable reload for testing
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("🛑 Platform stopped by user")
    except Exception as e:
        print(f"💥 Platform startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()