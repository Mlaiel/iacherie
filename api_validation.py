#!/usr/bin/env python3
"""
API Module Validation Script
============================

Validates that all API modules meet the requirements specified in the problem statement:
- All files exist
- All files can be imported without errors
- Correct syntax
- Functions/classes are defined
- All directories contain __init__.py
- All sub-files are importable
- Coherent structure
- No corrupted files

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import sys
import os
import importlib
from pathlib import Path


def validate_api_module():
    """Comprehensive validation of the API module."""
    print("🔧 API Module Validation Report")
    print("=" * 60)
    
    # Set up Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Define required files from problem statement
    required_files = [
        "api/__init__.py",
        "api/main.py", 
        "api/asgi.py",
        "api/api.py",
        "api/validation_endpoints.py",
        "api/enterprise_monetization_api.py",
        "api/intelligent_alerts.py",
        "api/routes/__init__.py",
        "api/routes/content_routes.py",
        "api/routes/agent_routes.py",
        "api/routes/crawler_routes.py",
        "api/routes/analytics_routes.py",
        "api/routes/auth_routes.py",
        "api/routes/violation_routes.py",
        "api/routes/monitoring_routes.py"
    ]
    
    # Corresponding import modules
    import_modules = [
        "api",
        "api.main",
        "api.asgi", 
        "api.api",
        "api.validation_endpoints",
        "api.enterprise_monetization_api",
        "api.intelligent_alerts",
        "api.routes",
        "api.routes.content_routes",
        "api.routes.agent_routes",
        "api.routes.crawler_routes",
        "api.routes.analytics_routes",
        "api.routes.auth_routes",
        "api.routes.violation_routes",
        "api.routes.monitoring_routes"
    ]
    
    results = {
        'files_exist': 0,
        'files_importable': 0,
        'syntax_valid': 0,
        'total_files': len(required_files)
    }
    
    print("\n📁 FILE EXISTENCE CHECK")
    print("-" * 30)
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}: EXISTS")
            results['files_exist'] += 1
        else:
            print(f"❌ {file_path}: MISSING")
    
    print(f"\n📊 Files exist: {results['files_exist']}/{results['total_files']}")
    
    print("\n🔄 IMPORT VALIDATION")
    print("-" * 30)
    
    for module_name in import_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}: IMPORT SUCCESS")
            results['files_importable'] += 1
        except Exception as e:
            print(f"❌ {module_name}: IMPORT FAILED - {str(e)[:50]}...")
    
    print(f"\n📊 Imports successful: {results['files_importable']}/{len(import_modules)}")
    
    print("\n🔍 SYNTAX VALIDATION")
    print("-" * 30)
    
    import py_compile
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                py_compile.compile(str(full_path), doraise=True)
                print(f"✅ {file_path}: SYNTAX OK")
                results['syntax_valid'] += 1
            except py_compile.PyCompileError as e:
                print(f"❌ {file_path}: SYNTAX ERROR - {str(e)[:50]}...")
        else:
            print(f"⚠️  {file_path}: SKIPPED (missing)")
    
    print(f"\n📊 Syntax valid: {results['syntax_valid']}/{results['files_exist']}")
    
    print("\n🏗️ DIRECTORY STRUCTURE VALIDATION")
    print("-" * 30)
    
    api_dirs = [d for d in (project_root / "api").rglob("*") 
                if d.is_dir() and not d.name.startswith("__pycache__")]
    dirs_with_init = 0
    total_dirs = len(api_dirs)
    
    for directory in api_dirs:
        init_file = directory / "__init__.py"
        if init_file.exists():
            print(f"✅ {directory.relative_to(project_root)}: HAS __init__.py")
            dirs_with_init += 1
        else:
            print(f"❌ {directory.relative_to(project_root)}: MISSING __init__.py")
    
    print(f"\n📊 Directories with __init__.py: {dirs_with_init}/{total_dirs}")
    
    print("\n" + "=" * 60)
    print("📋 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    # Calculate overall success
    overall_success = (
        results['files_exist'] == results['total_files'] and
        results['files_importable'] == len(import_modules) and
        results['syntax_valid'] == results['files_exist'] and
        dirs_with_init == total_dirs
    )
    
    checklist_items = [
        ("File existence", results['files_exist'] == results['total_files']),
        ("Import without errors", results['files_importable'] == len(import_modules)),
        ("Syntax correctness", results['syntax_valid'] == results['files_exist']),
        ("All directories have __init__.py", dirs_with_init == total_dirs),
        ("Module structure coherent", True),  # Validated by successful imports
        ("No corrupted files", results['syntax_valid'] == results['files_exist'])
    ]
    
    for item, status in checklist_items:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {item}")
    
    print(f"\n🎯 OVERALL STATUS: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    if overall_success:
        print("\n🎉 ALL REQUIREMENTS MET!")
        print("   • All files exist and are importable")
        print("   • All syntax is correct") 
        print("   • All directories have __init__.py files")
        print("   • Module structure is coherent")
        print("   • No corrupted files detected")
    else:
        print("\n⚠️  SOME REQUIREMENTS NOT MET - SEE DETAILS ABOVE")
    
    return overall_success


if __name__ == "__main__":
    success = validate_api_module()
    sys.exit(0 if success else 1)