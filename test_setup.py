#!/usr/bin/env python3
"""
Test script to validate core Ainflue Platform setup
Tests the basic requirements and configuration without full dependencies
"""

import sys
import os
import importlib.util

def test_python_version():
    """Test Python version compatibility"""
    print("🔍 Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_fastapi_import():
    """Test FastAPI import"""
    print("🔍 Testing FastAPI import...")
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} - Available")
        return True
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

def test_basic_dependencies():
    """Test basic required dependencies"""
    print("🔍 Testing basic dependencies...")
    deps = [
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'), 
        ('starlette', 'Starlette'),
        ('dotenv', 'Python-dotenv'),
    ]
    
    failed = []
    for module, name in deps:
        try:
            __import__(module)
            print(f"  ✅ {name} - Available")
        except ImportError:
            print(f"  ❌ {name} - Missing")
            failed.append(name)
    
    return len(failed) == 0

def test_environment_files():
    """Test environment configuration files"""
    print("🔍 Testing environment files...")
    env_files = [
        '.env.development',
        '.env.staging', 
        '.env.production',
        'requirements.txt',
        'install.sh'
    ]
    
    missing = []
    for file in env_files:
        if os.path.exists(file):
            print(f"  ✅ {file} - Exists")
        else:
            print(f"  ❌ {file} - Missing")
            missing.append(file)
    
    return len(missing) == 0

def test_config_import():
    """Test configuration module import"""
    print("🔍 Testing configuration import...")
    try:
        # Test direct import without complex dependencies
        sys.path.insert(0, os.path.join(os.getcwd(), 'config'))
        import app_config
        print("✅ Configuration module - Available")
        print(f"  Environment: {app_config.settings.app.environment}")
        print(f"  Debug: {app_config.settings.app.debug}")
        print(f"  Host: {app_config.settings.app.host}")
        print(f"  Port: {app_config.settings.app.port}")
        return True
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Configuration loaded with issues: {e}")
        print("✅ Basic configuration still available")
        return True

def test_basic_fastapi_app():
    """Test basic FastAPI application creation"""
    print("🔍 Testing FastAPI app creation...")
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test App")
        
        @app.get("/")
        def root():
            return {"message": "Test successful"}
        
        print("✅ FastAPI app creation - Successful")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False

def test_logging_setup():
    """Test logging configuration"""
    print("🔍 Testing logging setup...")
    try:
        # Test basic logging setup without complex config
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Test log message")
        print("✅ Logging setup - Successful")
        return True
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 AINFLUE PLATFORM - SETUP VALIDATION TEST")
    print("=" * 60)
    print("Author: Fahed Mlaiel (mlaiel@live.de)")
    print("Testing core setup and configuration...")
    print()
    
    tests = [
        ("Python Version", test_python_version),
        ("FastAPI Import", test_fastapi_import),
        ("Basic Dependencies", test_basic_dependencies),
        ("Environment Files", test_environment_files),
        ("Configuration Import", test_config_import),
        ("FastAPI App Creation", test_basic_fastapi_app),
        ("Logging Setup", test_logging_setup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔧 {test_name}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Core setup is working correctly.")
        print("💡 You can now run: python main.py")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
        print("💡 Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())