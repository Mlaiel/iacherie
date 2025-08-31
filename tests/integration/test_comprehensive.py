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

"""Simple functional test for the FastAPI application
"""import asyncio
import subprocess
import time
import sys
import requests
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_dependencies():
    """Test that all required dependencies are available"""    print("🔍 Testing dependencies...")
    
    try:
        import passlib
        import pydantic_settings
        import aiohttp
        import cryptography
        import pytest_asyncio
        import fastapi
        import uvicorn
        print("✅ All core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_server_startup():
    """Test that the FastAPI server can start and respond"""    print("🚀 Testing FastAPI server startup...")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, "test_main_app.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test endpoints
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "Ainflue AI Platform is running!" in data.get("message", ""):
                print("✅ Root endpoint working")
            else:
                print("❌ Root endpoint response incorrect")
                return False
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "Platform is healthy" in data.get("message", ""):
                print("✅ Health endpoint working")
            else:
                print("❌ Health endpoint response incorrect")
                return False
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test docs endpoint
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200 and "swagger" in response.text.lower():
            print("✅ Documentation endpoint working")
        else:
            print("❌ Documentation endpoint failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False
    finally:
        # Clean up
        process.terminate()
        process.wait()

def test_async_functionality():
    """Test async functionality"""    print("⚡ Testing async functionality...")
    
    async def simple_async_test():
        await asyncio.sleep(0.01)
        return True
    
    try:
        result = asyncio.run(simple_async_test())
        if result:
            print("✅ Async functionality working")
            return True
        else:
            print("❌ Async test failed")
            return False
    except Exception as e:
        print(f"❌ Async test error: {e}")
        return False

def main():
    """Run all tests"""    print("🧪 Running Ainflue Platform Tests")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Async Functionality", test_async_functionality),
        ("Server Startup", test_server_startup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI application is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())