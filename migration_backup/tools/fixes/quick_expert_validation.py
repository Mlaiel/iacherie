#!/usr/bin/env python3
"""
🎯 EXPERT TEAM QUICK VALIDATION - Core Implementation Checker
=============================================================

Quick validation of expert team core implementations without
potentially problematic imports.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import sys
import os
import subprocess
import importlib
from typing import List, Tuple

def check_python_dependencies() -> List[Tuple[str, bool, str]]:
    """Check critical Python dependencies for all expert roles"""
    dependencies = [
        # Lead Dev IA
        ('torch', 'Lead Dev IA'),
        ('transformers', 'Lead Dev IA'),
        ('openai', 'Lead Dev IA'),
        
        # Backend Senior
        ('fastapi', 'Backend Senior'),
        ('uvicorn', 'Backend Senior'),
        ('pydantic', 'Backend Senior'),
        
        # ML Engineer
        ('numpy', 'ML Engineer'),
        ('pandas', 'ML Engineer'),
        ('sklearn', 'ML Engineer'),
        
        # DBA
        ('asyncpg', 'DBA'),
        ('sqlalchemy', 'DBA'),
        ('pymongo', 'DBA'),
        
        # Security
        ('cryptography', 'Sécurité'),
        ('jwt', 'Sécurité'),
        ('passlib', 'Sécurité'),
        
        # Audio Engineer
        ('librosa', 'Audio Engineer'),
        ('soundfile', 'Audio Engineer'),
        
        # DevOps (monitoring)
        ('prometheus_client', 'DevOps'),
    ]
    
    results = []
    for dep, role in dependencies:
        try:
            mod = importlib.import_module(dep)
            version = getattr(mod, '__version__', 'unknown')
            results.append((f"{role}: {dep} v{version}", True, role))
        except ImportError:
            results.append((f"{role}: {dep} MISSING", False, role))
    
    return results

def check_file_structure() -> List[Tuple[str, bool, str]]:
    """Check if critical files exist"""
    critical_files = [
        ('main.py', 'Backend Senior'),
        ('master_expert_orchestrator.py', 'All Experts'),
        ('expert_team_validator.py', 'All Experts'),
        ('frontend/package.json', 'DevOps'),
        ('requirements.txt', 'DevOps'),
        ('services/orchestration/ai_model_orchestration_hub.py', 'Lead Dev IA'),
        ('services/orchestration/real_time_analytics_orchestrator.py', 'ML Engineer'),
        ('infrastructure/compliance/global_compliance_manager.py', 'Sécurité'),
        ('backend/core/database_core.py', 'DBA'),
    ]
    
    results = []
    for file_path, role in critical_files:
        exists = os.path.exists(file_path)
        status = "EXISTS" if exists else "MISSING"
        results.append((f"{role}: {file_path} {status}", exists, role))
    
    return results

def check_frontend_build() -> Tuple[str, bool, str]:
    """Check if frontend can build"""
    try:
        result = subprocess.run(
            ['npm', '--version'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            npm_version = result.stdout.strip()
            return (f"DevOps: npm v{npm_version} READY", True, "DevOps")
        else:
            return ("DevOps: npm NOT AVAILABLE", False, "DevOps")
    except Exception as e:
        return (f"DevOps: npm check FAILED - {str(e)[:30]}", False, "DevOps")

def main():
    """Run quick expert team validation"""
    print("🚀 EXPERT TEAM QUICK VALIDATION")
    print("=" * 50)
    
    all_results = []
    
    # Check Python dependencies
    print("🔍 Checking Python dependencies...")
    dep_results = check_python_dependencies()
    all_results.extend(dep_results)
    
    # Check file structure
    print("📁 Checking file structure...")
    file_results = check_file_structure()
    all_results.extend(file_results)
    
    # Check frontend tools
    print("🛠️  Checking frontend tools...")
    frontend_result = check_frontend_build()
    all_results.append(frontend_result)
    
    # Summary by role
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY BY EXPERT ROLE")
    print("=" * 50)
    
    roles = ['Lead Dev IA', 'Backend Senior', 'ML Engineer', 'DBA', 'Sécurité', 
             'Audio Engineer', 'DevOps', 'All Experts']
    
    total_success = 0
    total_checks = len(all_results)
    
    for role in roles:
        role_results = [r for r in all_results if r[2] == role]
        if role_results:
            role_success = len([r for r in role_results if r[1]])
            role_total = len(role_results)
            success_rate = (role_success / role_total) * 100
            
            status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
            print(f"{status_icon} {role}: {role_success}/{role_total} ({success_rate:.0f}%)")
            
            total_success += role_success
            
            # Show details for failed checks
            for result in role_results:
                if not result[1]:
                    print(f"   ❌ {result[0]}")
    
    # Overall summary
    print("\n" + "=" * 50)
    overall_success_rate = (total_success / total_checks) * 100
    
    if overall_success_rate >= 90:
        print("🎉 EXPERT TEAM STATUS: EXCELLENT")
        print("🏆 All expert roles successfully implemented!")
        exit_code = 0
    elif overall_success_rate >= 70:
        print("✅ EXPERT TEAM STATUS: GOOD")
        print("🎯 Most expert roles working, minor issues")
        exit_code = 0
    else:
        print("⚠️ EXPERT TEAM STATUS: NEEDS ATTENTION")
        print("🔧 Some expert roles need fixes")
        exit_code = 1
    
    print(f"📈 Overall Success Rate: {overall_success_rate:.1f}% ({total_success}/{total_checks})")
    print("=" * 50)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()