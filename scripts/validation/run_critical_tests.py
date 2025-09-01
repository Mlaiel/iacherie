#!/usr/bin/env python3
"""Direct Test Runner for Critical Unit Tests.

==========================================

Run critical unit tests directly without conftest dependencies.
This addresses the immediate testing gap while bypassing configuration issues.

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Validate critical unit tests implementation
"""

import sys
import asyncio
import traceback
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def run_fingerprinting_tests():
    """
Run fingerprinting agent tests."""
    print("🚀 Running Critical Unit Tests for Ainflue Platform")
    print("=" * 60)
    
    results = []
    
    # Run all test suites
    results.append(await run_fingerprinting_tests())
    results.append(await run_monetization_tests())
    results.append(await run_crawler_tests())
    results.append(await run_api_tests())
    results.append(await run_integration_tests())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    test_names = [
        "Fingerprinting Agent",
        "Monetization Agent", 
        "Critical Crawlers",
        "API Endpoints",
        "Integration Workflows"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:20}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL CRITICAL TESTS PASSED!")
        print("\n✅ Problem Resolved: 'Tests Manquants: Pas de tests unitaires centralisés'")
        print("✅ Quality validation now available for production deployment")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} test suite(s) failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)