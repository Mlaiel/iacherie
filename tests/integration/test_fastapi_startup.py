# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Integration Test: Complete FastAPI Application Startup
=====================================================

Tests the complete startup process of the Ainflue FastAPI application including:
- Basic application initialization
- Health endpoints validation  
- API documentation generation
- Core middleware functionality

Author: Integration Test Suite
"""

import asyncio
import subprocess
import time
import sys
import requests
import pytest
import sys
import os
from pathlib import Path
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFastAPIApplicationStartup:
    """Integration tests for FastAPI application startup"""
    
    @pytest.fixture(scope="class")
    def app_process(self):
        """Start the FastAPI application for testing"""
        print(" Starting FastAPI application...")
        
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "test_main_app.py"
        ], 
        cwd=str(Path(__file__).parent.parent.parent),
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Verify server is running
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
                    print(" FastAPI server started successfully")
                    break
            except:
                if i < max_retries - 1:
                    time.sleep(2)
                else:
                    process.terminate()
                    raise Exception("Failed to start FastAPI server")
        
        yield process
        
        # Cleanup
        print(" Stopping FastAPI application...")
        process.terminate()
        process.wait()
    
    def test_application_startup_successful(self, app_process):
        """Test that the FastAPI application starts successfully"""
        assert app_process.poll() is None, "Application process should be running"
        print(" Application startup successful")
    
    def test_root_endpoint_accessible(self, app_process):
        """Test that the root endpoint is accessible and returns correct response"""
        response = requests.get("http://127.0.0.1:8000/", timeout=10)
        
        assert response.status_code == 200, f"Root endpoint failed with status {response.status_code}"
        
        data = response.json()
        assert "message" in data, "Response should contain message field"
        assert "Ainflue AI Platform is running!" in data["message"], "Message should indicate platform is running"
        assert data["status"] == "success", "Status should be success"
        
        print(" Root endpoint accessible and returning correct response")
    
    def test_health_endpoint_functional(self, app_process):
        """Test that the health endpoint is functional"""
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        
        assert response.status_code == 200, f"Health endpoint failed with status {response.status_code}"
        
        data = response.json()
        assert "message" in data, "Health response should contain message field"
        assert "Platform is healthy" in data["message"], "Health message should indicate platform health"
        assert data["status"] == "operational", "Health status should be operational"
        
        print(" Health endpoint functional")
    
    def test_api_documentation_accessible(self, app_process):
        """Test that API documentation is accessible"""
        response = requests.get("http://127.0.0.1:8000/docs", timeout=10)
        
        assert response.status_code == 200, f"Documentation endpoint failed with status {response.status_code}"
        assert "swagger" in response.text.lower(), "Documentation should contain Swagger UI"
        
        print(" API documentation accessible")
    
    def test_openapi_schema_generation(self, app_process):
        """Test that OpenAPI schema is properly generated"""
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=10)
        
        assert response.status_code == 200, f"OpenAPI schema endpoint failed with status {response.status_code}"
        
        schema = response.json()
        assert "openapi" in schema, "Schema should contain openapi version"
        assert "info" in schema, "Schema should contain info section"
        assert "paths" in schema, "Schema should contain paths"
        
        # Verify application info
        info = schema["info"]
        assert "title" in info, "Schema info should contain title"
        assert "Ainflue" in info["title"], "Title should reference Ainflue platform"
        
        print(" OpenAPI schema properly generated")
    
    def test_cors_configuration(self, app_process):
        """Test CORS configuration if enabled"""
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET'
        }
        
        response = requests.options("http://127.0.0.1:8000/", headers=headers, timeout=10)
        
        # CORS might not be configured in minimal app, so we just test it doesn't crash
        assert response.status_code in [200, 405], "CORS preflight should not crash the application"
        
        print(" CORS configuration stable")
    
    def test_application_metadata(self, app_process):
        """Test that application metadata is correctly configured"""
        response = requests.get("http://127.0.0.1:8000/", timeout=10)
        data = response.json()
        
        # Test environment is correctly set
        assert "environment" in data, "Response should contain environment information"
        assert data["environment"] in ["development", "testing", "staging", "production"], \
            "Environment should be a valid environment type"
        
        print(" Application metadata correctly configured")


if __name__ == "__main__":
    # Run the integration tests
    print("🧪 Running FastAPI Startup Integration Tests")
    print("=" * 60)
    
    # Run with pytest
    exit_code = pytest.main([str(Path(__file__)), "-v", "--tb=short"])
    sys.exit(exit_code)