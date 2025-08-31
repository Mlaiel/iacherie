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
"""Test script to verify that the application meets the requirements:
1. python main.py starts without error
2. API responds on /health
3. Tests pass without error configuration
"""import sys
import subprocess
import time
import requests
import signal
import os
from pathlib import Path

def test_main_py_starts():
    """Test that python main.py starts without error"""    print("🧪 Testing: python main.py starts without error")
    
    # Start main.py in background
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait a few seconds for startup
    time.sleep(8)
    
    # Check if process is still running (no immediate crash)
    if proc.poll() is None:
        print("✅ SUCCESS: main.py started and is running")
        
        # Terminate the process
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        
        return True
    else:
        print("❌ FAILED: main.py exited immediately")
        stdout, _ = proc.communicate()
        print(f"Output: {stdout}")
        return False

def test_health_endpoint():
    """Test that API responds on /health"""    print("🧪 Testing: API responds on /health")
    
    # Start main.py in background
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    try:
        # Wait for server to start
        time.sleep(8)
        
        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "message" in data:
                    print("✅ SUCCESS: /health endpoint responds correctly")
                    print(f"   Response: {data}")
                    return True
                else:
                    print("❌ FAILED: /health endpoint response missing required fields")
                    print(f"   Response: {data}")
                    return False
            else:
                print(f"❌ FAILED: /health endpoint returned status {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ FAILED: Could not connect to /health endpoint: {e}")
            return False
    
    finally:
        # Cleanup
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

def test_configuration():
    """Test that tests pass without error configuration"""    print("🧪 Testing: Configuration works without errors")
    
    try:
        # Test importing main modules
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test that we can at least import and run basic functionality
        from main import app, settings
        
        print("✅ SUCCESS: Basic imports work")
        print(f"   App title: {app.title}")
        print(f"   Environment: {settings.app.environment}")
        print(f"   Host: {settings.app.host}")
        print(f"   Port: {settings.app.port}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Configuration import failed: {e}")
        return False

def main():
    """Run all tests"""    print("🚀 Starting Application Startup Tests")
    print("=" * 50)
    
    tests = [
        ("Main.py Startup", test_main_py_starts),
        ("Health Endpoint", test_health_endpoint),
        ("Configuration", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    all_passed = True
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Application meets requirements:")
        print("   ✅ python main.py starts without error")
        print("   ✅ API responds on /health")
        print("   ✅ Tests pass without error configuration")
    else:
        print("💥 SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()