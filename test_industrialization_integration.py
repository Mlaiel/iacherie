#!/usr/bin/env python3
"""Simple Integration Test for Industrialization Metrics
======================================================

Simple test to validate the industrialization metrics system works.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import asyncio
import subprocess

def run_command(cmd, cwd=None):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

async def test_metrics_system():
    """Test the complete metrics system"""
    print("🧪 Testing Industrialization Metrics System")
    print("=" * 50)
    
    base_dir = "/home/runner/work/Ainflue/Ainflue"
    
    # Test 1: Core metrics module
    print("1. Testing core metrics module...")
    success, stdout, stderr = run_command(
        f"cd {base_dir} && python monitoring/industrialization_success_metrics.py",
        cwd=base_dir
    )
    if success:
        print("   ✅ Core metrics module works")
    else:
        print(f"   ❌ Core metrics module failed: {stderr}")
        return False
    
    # Test 2: Dashboard generation
    print("2. Testing dashboard generation...")
    success, stdout, stderr = run_command(
        f"cd {base_dir} && python monitoring/industrialization_dashboard.py",
        cwd=base_dir
    )
    if success:
        print("   ✅ Dashboard generation works")
    else:
        print(f"   ❌ Dashboard generation failed: {stderr}")
        return False
    
    # Test 3: Integration system
    print("3. Testing integration system...")
    success, stdout, stderr = run_command(
        f"cd {base_dir} && python monitoring/industrialization_metrics_integration.py",
        cwd=base_dir
    )
    if success:
        print("   ✅ Integration system works")
    else:
        print(f"   ❌ Integration system failed: {stderr}")
        return False
    
    # Test 4: Startup script
    print("4. Testing startup script...")
    success, stdout, stderr = run_command(
        f"cd {base_dir} && python start_industrialization_metrics.py report",
        cwd=base_dir
    )
    if success:
        print("   ✅ Startup script works")
        # Check if dashboard was generated
        dashboard_path = "/tmp/industrialization_dashboard.html"
        if os.path.exists(dashboard_path):
            print("   ✅ HTML dashboard generated successfully")
            print(f"   📊 Dashboard size: {os.path.getsize(dashboard_path)} bytes")
        else:
            print("   ⚠️ Dashboard file not found")
    else:
        print(f"   ❌ Startup script failed: {stderr}")
        return False
    
    # Test 5: Verify documentation format
    print("5. Testing documentation format...")
    checklist_path = f"{base_dir}/docs/checklists/CHECKLIST_INDUSTRIALISATION_COMPLETE.md"
    if os.path.exists(checklist_path):
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for required content from problem statement
        required_content = [
            "📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION",
            "🎯 KPIs TECHNIQUES",
            "💼 KPIs BUSINESS",
            "Uptime SLA\t99.9%\tMonitoring continu",
            "Response Time API\t<200ms P95\tAPM + alerting",
            "Error Rate\t<0.1%\tLogs + metrics",
            "Customer Satisfaction\t>4.5/5\tSurveys + NPS",
            "Revenue Growth\t+20% MoM\tBusiness intelligence"
        ]
        
        all_found = True
        for required in required_content:
            if required not in content:
                print(f"   ❌ Missing required content: {required}")
                all_found = False
        
        if all_found:
            print("   ✅ Documentation format matches problem statement")
        else:
            print("   ❌ Documentation format issues found")
            return False
    else:
        print(f"   ❌ Checklist file not found: {checklist_path}")
        return False
    
    print("=" * 50)
    print("🎉 All tests passed! The industrialization metrics system is working correctly.")
    
    # Show summary information
    print("\n📋 SYSTEM SUMMARY:")
    print(f"   • Core metrics system: ✅ Working")
    print(f"   • Dashboard generation: ✅ Working") 
    print(f"   • Integration layer: ✅ Working")
    print(f"   • Startup script: ✅ Working")
    print(f"   • Documentation format: ✅ Compliant")
    
    if os.path.exists("/tmp/industrialization_dashboard.html"):
        print(f"   • HTML Dashboard: ✅ Generated ({os.path.getsize('/tmp/industrialization_dashboard.html')} bytes)")
    
    return True

def main():
    """Main test function"""
    try:
        result = asyncio.run(test_metrics_system())
        if result:
            print("\n✅ Integration test PASSED")
            sys.exit(0)
        else:
            print("\n❌ Integration test FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()