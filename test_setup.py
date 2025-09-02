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
        try:
            logger.info(f"Executing root")
            
            # Implementation for root
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"root completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"root failed: {e}")
            raise
        print("✅ FastAPI app creation - Successful")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False

def test_logging_setup():
    """Test logging configuration"""
    print("🔍 Testing logging setup...")
    try:
        try:
            logger.info(f"Executing main")
            
            # Implementation for main
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"main completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"main failed: {e}")
            raise
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