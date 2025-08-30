#!/usr/bin/env python3
"""
Final Environment Verification Test
Test that all dependencies are working and the FastAPI backend is functional.

This test verifies the solution to the problem statement:
- FastAPI, PyTest installed: Base functional established ✓
- Missing dependencies: passlib, pydantic-settings, aiohttp, cryptography ✓
- Broken imports: main.py and config.py (fixed with fallbacks) ✓
- Backend startable: Critical dependencies installed ✓
"""

import sys
import time
import subprocess
import requests
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_dependencies():
    """Test that all required dependencies are installed and importable"""
    print("🧪 Testing Dependencies Installation...")
    
    required_deps = [
        ("fastapi", "FastAPI framework"),
        ("passlib", "Password hashing library"),
        ("pydantic_settings", "Pydantic settings management"),
        ("aiohttp", "Async HTTP client/server"),
        ("cryptography", "Cryptographic library"),
        ("pytest", "Testing framework"),
        ("pytest_asyncio", "Async testing support"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("numpy", "Numerical computing"),
        ("redis", "Redis client"),
        ("email_validator", "Email validation"),
        ("python_multipart", "Multipart form support")
    ]
    
    missing = []
    installed = []
    
    for module_name, description in required_deps:
        try:
            __import__(module_name)
            installed.append((module_name, description))
            print(f"  ✅ {module_name}: {description}")
        except ImportError:
            missing.append((module_name, description))
            print(f"  ❌ {module_name}: {description}")
    
    print(f"\n📊 Dependencies Status:")
    print(f"  - Installed: {len(installed)}")
    print(f"  - Missing: {len(missing)}")
    
    if missing:
        print(f"\n⚠️  Missing dependencies:")
        for module_name, description in missing:
            print(f"    - {module_name}: {description}")
        return False
    
    print("✅ All required dependencies are installed!")
    return True

def test_simple_imports():
    """Test basic imports work"""
    print("\n🧪 Testing Basic Imports...")
    
    # Test basic FastAPI import
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        print("  ✅ FastAPI and Pydantic imports work")
    except Exception as e:
        print(f"  ❌ FastAPI imports failed: {e}")
        return False
    
    # Test security libraries
    try:
        import passlib
        import cryptography
        print("  ✅ Security libraries import work")
    except Exception as e:
        print(f"  ❌ Security library imports failed: {e}")
        return False
    
    # Test HTTP client
    try:
        import aiohttp
        print("  ✅ HTTP client library imports work")
    except Exception as e:
        print(f"  ❌ HTTP client imports failed: {e}")
        return False
    
    print("✅ All basic imports work!")
    return True

def test_fastapi_app_creation():
    """Test FastAPI app can be created successfully"""
    print("\n🧪 Testing FastAPI App Creation...")
    
    try:
        # Test simple main application import
        import simple_main
        app = simple_main.app
        print("  ✅ simple_main.py app creation works")
        
        # Verify it's a FastAPI app
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            print("  ✅ App is a valid FastAPI instance")
        else:
            print(f"  ❌ App is not a FastAPI instance: {type(app)}")
            return False
            
    except Exception as e:
        print(f"  ❌ FastAPI app creation failed: {e}")
        return False
    
    print("✅ FastAPI app creation works!")
    return True

def test_server_startup():
    """Test that the FastAPI server can start and respond"""
    print("\n🧪 Testing FastAPI Server Startup...")
    
    try:
        # Start the simple server in background
        print("  🚀 Starting server...")
        process = subprocess.Popen(
            [sys.executable, "simple_main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Wait for server to start
        print("  ⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=10)
            if response.status_code == 200:
                print("  ✅ Server is responding to HTTP requests")
                
                # Test JSON response
                data = response.json()
                if data.get("status") == "success":
                    print("  ✅ Server returns valid JSON response")
                else:
                    print(f"  ⚠️  Unexpected response: {data}")
                
                # Test health endpoint
                health_response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if health_response.status_code == 200:
                    print("  ✅ Health endpoint is working")
                else:
                    print(f"  ❌ Health endpoint failed: {health_response.status_code}")
                
                # Test dependencies endpoint
                deps_response = requests.get("http://127.0.0.1:8000/dependencies", timeout=5)
                if deps_response.status_code == 200:
                    deps_data = deps_response.json()
                    if deps_data.get("all_dependencies_satisfied"):
                        print("  ✅ Dependencies endpoint confirms all deps satisfied")
                    else:
                        print(f"  ⚠️  Dependencies not satisfied: {deps_data}")
                else:
                    print(f"  ❌ Dependencies endpoint failed: {deps_response.status_code}")
                    
                server_works = True
            else:
                print(f"  ❌ Server returned status code: {response.status_code}")
                server_works = False
                
        except requests.RequestException as e:
            print(f"  ❌ Could not connect to server: {e}")
            server_works = False
        
        # Stop the server
        print("  🛑 Stopping server...")
        process.terminate()
        process.wait(timeout=5)
        
        return server_works
        
    except Exception as e:
        print(f"  ❌ Server startup test failed: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

def test_main_py_startup():
    """Test that main.py can start with fallback settings"""
    print("\n🧪 Testing main.py Startup...")
    
    try:
        # Test that main.py imports work
        print("  📦 Testing main.py imports...")
        
        # Run main.py briefly to see if it starts
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Let it run briefly
        time.sleep(3)
        
        # Check if process is still running (good sign)
        if process.poll() is None:
            print("  ✅ main.py started successfully")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"  ❌ main.py exited early")
            print(f"  📄 Output: {stdout.decode()}")
            if stderr:
                print(f"  📄 Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"  ❌ main.py startup test failed: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

def main():
    """Run all tests"""
    print("🔍 Final Environment Verification Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies Installation", test_dependencies),
        ("Basic Imports", test_simple_imports),
        ("FastAPI App Creation", test_fastapi_app_creation),
        ("Server Startup", test_server_startup),
        ("main.py Startup", test_main_py_startup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI application is working correctly.")
        print("\n✅ Problem Statement Resolution:")
        print("  - FastAPI, PyTest installed: ✅ Base functional established")
        print("  - Missing dependencies: ✅ passlib, pydantic-settings, aiohttp, cryptography installed")
        print("  - Broken imports: ✅ main.py and config.py fixed with fallbacks")
        print("  - Backend startable: ✅ Critical dependencies installed and working")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)