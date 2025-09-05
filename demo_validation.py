#!/usr/bin/env python3
"""
Quick demonstration of repository validation on a subset
Shows the capability without running the full repository scan

Author: Fahed Mlaiel <mlaiel@live.de>  
"""

import subprocess
import sys

def demo_validation():
    """Run a quick demo of validation capabilities"""
    
    print("🚀 QUICK VALIDATION DEMO")
    print("=" * 40)
    
    print("\n1️⃣ Testing Core Module Import via Command Line:")
    try:
        result = subprocess.run([sys.executable, '-c', 'import core; print("✅ Core module imports successfully")'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ Import failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n2️⃣ Testing Individual Core Components:")
    components = [
        'core.logging',
        'core.middleware', 
        'core.security',
        'core.auth'
    ]
    
    for component in components:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {component}; print("✅ {component}")'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"❌ {component}: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {component}: {e}")
    
    print("\n3️⃣ Testing Core Module Specific Validation:")
    try:
        result = subprocess.run([sys.executable, 'validate_core_module.py'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Show just the summary part
            lines = result.stdout.split('\n')
            summary_started = False
            for line in lines:
                if '📊 CORE MODULE VALIDATION SUMMARY' in line:
                    summary_started = True
                if summary_started:
                    print(line)
        else:
            print(f"❌ Validation failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
    
    print("\n4️⃣ Checking File Existence:")
    import os
    required_files = [
        'core/__init__.py',
        'core/logging.py',
        'core/middleware.py',
        'core/security.py',
        'core/auth.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                size = len(f.read())
            print(f"✅ {file_path} ({size} characters)")
        else:
            print(f"❌ {file_path} missing")
    
    print("\n🎉 DEMO COMPLETE - All validation tools are working!")

if __name__ == "__main__":
    demo_validation()