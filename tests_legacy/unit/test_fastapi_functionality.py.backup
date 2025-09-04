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

"""Basic test for FastAPI application startup and functionality
"""
import pytest
import sys
import os
from pathlib import Path
import pytest_asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import our test app
from test_main_app import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ainflue AI Platform is running!"
    assert data["status"] == "success"
    assert data["environment"] == "development"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Platform is healthy"
    assert data["status"] == "operational"
    assert data["environment"] == "development"

def test_docs_endpoint():
    """Test that docs endpoint is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()

def test_openapi_endpoint():
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "Ainflue AI Platform"

@pytest_asyncio.async_test
async def test_async_functionality():
    """Test that async functionality works"""
    import asyncio
    await asyncio.sleep(0.01)  # Simple async operation
    assert True

if __name__ == "__main__":
    print("Running basic FastAPI tests...")
    
    # Run tests manually for immediate feedback
    try:
        test_root_endpoint()
        print("✓ Root endpoint test passed")
        
        test_health_endpoint()
        print("✓ Health endpoint test passed")
        
        test_docs_endpoint()
        print("✓ Docs endpoint test passed")
        
        test_openapi_endpoint()
        print("✓ OpenAPI endpoint test passed")
        
        print("✅ All FastAPI tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)