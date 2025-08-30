#!/usr/bin/env python3
"""
Test critical fixes for Ainflue platform core business requirements.
Tests the 4 critical areas mentioned in the problem statement.
"""

import asyncio
import pytest
from unittest.mock import patch
import requests
import time
import subprocess
import signal
import os
import importlib.util

def test_config_loads_without_errors():
    """Test that config.py loads without duplicate class errors"""
    try:
        import sys
        import importlib.util
        
        # Load config.py directly
        spec = importlib.util.spec_from_file_location("config_module", "config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        settings = config_module.settings
        assert settings is not None
        assert hasattr(settings, 'app')
        assert hasattr(settings, 'database')
        assert hasattr(settings, 'security')
        print("✅ Config loads successfully without duplicate class errors")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_business_logic_core_53_agents():
    """Test that business_logic_core.py has exactly 53 agents implemented"""
    try:
        from business_logic_core import BusinessLogicCore
        
        # Create instance and check agent initialization
        core = BusinessLogicCore()
        
        # Use asyncio to test the initialization
        async def test_agents():
            await core._initialize_core_agents()
            agent_count = len(core.agents)
            print(f"✅ Found {agent_count} agents in business_logic_core.py")
            return agent_count == 53
        
        result = asyncio.run(test_agents())
        assert result, "Expected exactly 53 agents"
        return True
    except Exception as e:
        print(f"❌ Business logic core test failed: {e}")
        return False

def test_main_application_starts():
    """Test that main.py can start the application"""
    try:
        # Start the server in background
        process = subprocess.Popen(
            ['python', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='/home/runner/work/Ainflue/Ainflue'
        )
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Application starts successfully")
            # Terminate the process
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Application failed to start. Stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Main application start test failed: {e}")
        return False

def test_api_endpoints_available():
    """Test that API endpoints are accessible"""
    try:
        # Start the server
        process = subprocess.Popen(
            ['python', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='/home/runner/work/Ainflue/Ainflue'
        )
        
        # Wait for startup
        time.sleep(8)
        
        try:
            # Test health endpoint
            response = requests.get('http://localhost:8000/health', timeout=5)
            health_ok = response.status_code == 200 and response.json().get('status') == 'healthy'
            
            # Test root endpoint  
            response = requests.get('http://localhost:8000/', timeout=5)
            root_ok = response.status_code == 200
            
            if health_ok and root_ok:
                print("✅ API endpoints are accessible and responding correctly")
                result = True
            else:
                print("❌ API endpoints not responding correctly")
                result = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to API endpoints: {e}")
            result = False
        finally:
            # Cleanup
            process.terminate()
            process.wait(timeout=5)
            
        return result
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def run_critical_tests():
    """Run all critical tests"""
    print("🔧 Running critical business fixes validation tests...\n")
    
    tests = [
        ("Config.py fixes", test_config_loads_without_errors),
        ("Business Logic Core 53 agents", test_business_logic_core_53_agents),
        ("Main.py application startup", test_main_application_starts),
        ("API endpoints validation", test_api_endpoints_available),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Testing: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"   Result: {'✅ PASSED' if result else '❌ FAILED'}\n")
        except Exception as e:
            print(f"   Result: ❌ FAILED - {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 60)
    print("🏁 CRITICAL FIXES VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<35} {status}")
    
    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CRITICAL FIXES VALIDATED SUCCESSFULLY!")
        return True
    else:
        print("⚠️  Some critical issues remain to be addressed.")
        return False

if __name__ == "__main__":
    run_critical_tests()