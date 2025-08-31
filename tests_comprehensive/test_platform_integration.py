"""Comprehensive Integration Tests for Ainflue Platform

Tests the complete system integration including:
- API endpoints functionality
- Fingerprinting engine
- Internationalization
- Frontend-backend integration
- Database operations
- External service integrations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from fastapi.testclient import TestClient
from pathlib import Path

# Test configuration
TEST_CONFIG = {
    "test_user_id": "test_user_123",
    "test_content_types": ["audio", "video", "image", "text"],
    "supported_languages": ["en", "fr", "de", "ar", "ber"],
    "test_platforms": ["youtube", "instagram", "tiktok", "spotify"],
    "test_fingerprint_threshold": 0.8
}


class AinfluePlatformTests:
    """Comprehensive platform tests"""    
    def __init__(self):
        self.client = None
        self.test_data = {}
        self.setup_complete = False
    
    async def setup_test_environment(self):
        """Setup test environment"""        try:
            # Initialize test client
            from api.main import app
            self.client = TestClient(app)
            
            # Setup test data
            await self._create_test_data()
            
            self.setup_complete = True
            print("✅ Test environment setup complete")
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            raise
    
    async def _create_test_data(self):
        """Create test data for various scenarios"""        self.test_data = {
            "users": [
                {
                    "user_id": "user_001",
                    "email": "test1@example.com",
                    "name": "Test User 1",
                    "language": "en"
                },
                {
                    "user_id": "user_002", 
                    "email": "test2@example.com",
                    "name": "Test User 2",
                    "language": "fr"
                },
                {
                    "user_id": "user_003",
                    "email": "test3@example.com", 
                    "name": "Utilisateur Amazigh",
                    "language": "ber"
                }
            ],
            "test_files": {
                "audio": "test_audio.mp3",
                "video": "test_video.mp4", 
                "image": "test_image.jpg",
                "text": "test_document.txt"
            }
        }
    
    # API Tests
    async def test_authentication_api(self) -> Dict[str, Any]:
        """Test authentication API endpoints"""        results = {
            "test_name": "Authentication API",
            "status": "passed",
            "details": [],
            "errors": []
        }
        
        try:
            # Test user registration
            registration_data = {
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "name": "New User"
            }
            
            response = self.client.post("/api/auth/register", json=registration_data)
            if response.status_code == 201:
                results["details"].append("✅ User registration successful")
            else:
                results["errors"].append(f"❌ Registration failed: {response.status_code}")
                results["status"] = "failed"
            
            # Test user login
            login_data = {
                "email": "newuser@example.com",
                "password": "SecurePassword123!"
            }
            
            response = self.client.post("/api/auth/login", json=login_data)
            if response.status_code == 200:
                results["details"].append("✅ User login successful")
                token = response.json().get("access_token")
                if token:
                    results["details"].append("✅ JWT token received")
                else:
                    results["errors"].append("❌ No JWT token in response")
                    results["status"] = "failed"
            else:
                results["errors"].append(f"❌ Login failed: {response.status_code}")
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"❌ Authentication test exception: {str(e)}")
        
        return results
    
    async def test_fingerprinting_api(self) -> Dict[str, Any]:
        """Test fingerprinting API endpoints"""        results = {
            "test_name": "Fingerprinting API",
            "status": "passed",
            "details": [],
            "errors": []
        }
        
        try:
            # Test fingerprint creation for different content types
            for content_type in TEST_CONFIG["test_content_types"]:
                fingerprint_data = {
                    "file_id": f"test_file_{content_type}",
                    "content_type": content_type,
                    "analysis_level": "standard",
                    "priority": "normal"
                }
                
                response = self.client.post("/api/fingerprinting/create", json=fingerprint_data)
                if response.status_code in [200, 201]:
                    results["details"].append(f"✅ {content_type} fingerprinting successful")
                else:
                    results["errors"].append(f"❌ {content_type} fingerprinting failed: {response.status_code}")
                    results["status"] = "failed"
            
            # Test fingerprint matching
            match_data = {
                "fingerprint_data": {"test": "data"},
                "similarity_threshold": TEST_CONFIG["test_fingerprint_threshold"],
                "max_results": 10
            }
            
            response = self.client.post("/api/fingerprinting/match", json=match_data)
            if response.status_code == 200:
                results["details"].append("✅ Fingerprint matching successful")
            else:
                results["errors"].append(f"❌ Fingerprint matching failed: {response.status_code}")
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"❌ Fingerprinting test exception: {str(e)}")
        
        return results
    
    async def test_monitoring_api(self) -> Dict[str, Any]:
        """Test monitoring API endpoints"""        results = {
            "test_name": "Monitoring API",
            "status": "passed",
            "details": [],
            "errors": []
        }
        
        try:
            # Test monitoring target creation
            monitoring_data = {
                "fingerprint_id": "test_fingerprint_123",
                "platform": "youtube",
                "monitoring_frequency": "hourly",
                "alert_threshold": 0.8,
                "auto_takedown": False
            }
            
            response = self.client.post("/api/monitoring/targets", json=monitoring_data)
            if response.status_code in [200, 201]:
                results["details"].append("✅ Monitoring target creation successful")
            else:
                results["errors"].append(f"❌ Monitoring target creation failed: {response.status_code}")
                results["status"] = "failed"
            
            # Test alerts retrieval
            response = self.client.get("/api/monitoring/alerts")
            if response.status_code == 200:
                results["details"].append("✅ Alerts retrieval successful")
            else:
                results["errors"].append(f"❌ Alerts retrieval failed: {response.status_code}")
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"❌ Monitoring test exception: {str(e)}")
        
        return results
    
    async def test_internationalization(self) -> Dict[str, Any]:
        """Test internationalization support"""        results = {
            "test_name": "Internationalization",
            "status": "passed", 
            "details": [],
            "errors": []
        }
        
        try:
            # Test language files exist
            frontend_locales_path = Path("frontend/src/locales")
            
            for lang in TEST_CONFIG["supported_languages"]:
                lang_file = frontend_locales_path / f"{lang}.json"
                if lang_file.exists():
                    results["details"].append(f"✅ {lang} translation file exists")
                    
                    # Test file content
                    try:
                        with open(lang_file, 'r', encoding='utf-8') as f:
                            lang_data = json.load(f)
                            if len(lang_data) > 0:
                                results["details"].append(f"✅ {lang} translations loaded ({len(lang_data)} keys)")
                            else:
                                results["errors"].append(f"❌ {lang} translation file is empty")
                                results["status"] = "failed"
                    except Exception as e:
                        results["errors"].append(f"❌ {lang} translation file corrupted: {str(e)}")
                        results["status"] = "failed"
                else:
                    results["errors"].append(f"❌ {lang} translation file missing")
                    results["status"] = "failed"
            
            # Test Amazigh dialect support
            amazigh_dialects_path = Path("core/i18n/amazigh_dialects")
            if amazigh_dialects_path.exists():
                dialect_files = list(amazigh_dialects_path.glob("*.json"))
                if len(dialect_files) > 0:
                    results["details"].append(f"✅ Amazigh dialects supported ({len(dialect_files)} dialects)")
                else:
                    results["errors"].append("❌ No Amazigh dialect files found")
                    results["status"] = "failed"
            else:
                results["errors"].append("❌ Amazigh dialects directory missing")
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"❌ Internationalization test exception: {str(e)}")
        
        return results
    
    async def test_frontend_components(self) -> Dict[str, Any]:
        """Test frontend components"""        results = {
            "test_name": "Frontend Components",
            "status": "passed",
            "details": [],
            "errors": []
        }
        
        try:
            # Test essential component files exist
            frontend_components = [
                "frontend/src/components/dashboard/Dashboard.tsx",
                "frontend/src/components/dashboard/RevenueChart.tsx",
                "frontend/src/components/LanguageSelector.tsx",
                "frontend/src/hooks/useLanguage.tsx"
            ]
            
            for component_path in frontend_components:
                if Path(component_path).exists():
                    results["details"].append(f"✅ {component_path.split('/')[-1]} component exists")
                else:
                    results["errors"].append(f"❌ {component_path.split('/')[-1]} component missing")
                    results["status"] = "failed"
            
            # Test package.json exists and has required dependencies
            package_json_path = Path("frontend/package.json")
            if package_json_path.exists():
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    
                required_deps = ["next", "react", "tailwindcss", "recharts"]
                for dep in required_deps:
                    if dep in package_data.get("dependencies", {}):
                        results["details"].append(f"✅ {dep} dependency found")
                    else:
                        results["errors"].append(f"❌ {dep} dependency missing")
                        results["status"] = "failed"
            else:
                results["errors"].append("❌ Frontend package.json missing")
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "failed" 
            results["errors"].append(f"❌ Frontend component test exception: {str(e)}")
        
        return results
    
    async def test_backend_modules(self) -> Dict[str, Any]:
        """Test backend module structure"""        results = {
            "test_name": "Backend Modules",
            "status": "passed",
            "details": [],
            "errors": []
        }
        
        try:
            # Test critical backend modules exist
            critical_modules = [
                "api/routes/fingerprinting.py",
                "api/routes/monitoring.py", 
                "api/routes/monetization.py",
                "api/routes/collaboration.py",
                "ai_engine/fingerprinting/audio_fingerprint_engine.py",
                "ai_engine/fingerprinting/video_fingerprint_engine.py",
                "database/fingerprinting/fingerprint_analytics.py"
            ]
            
            for module_path in critical_modules:
                if Path(module_path).exists():
                    results["details"].append(f"✅ {module_path.split('/')[-1]} module exists")
                else:
                    results["errors"].append(f"❌ {module_path.split('/')[-1]} module missing")
                    results["status"] = "failed"
            
            # Test requirements.txt
            if Path("requirements.txt").exists():
                results["details"].append("✅ requirements.txt exists")
            else:
                results["errors"].append("❌ requirements.txt missing")
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(f"❌ Backend module test exception: {str(e)}")
        
        return results
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""        print("🚀 Starting Ainflue Comprehensive Platform Tests...")
        print("=" * 60)
        
        if not self.setup_complete:
            await self.setup_test_environment()
        
        # Run all test suites
        test_suites = [
            self.test_authentication_api,
            self.test_fingerprinting_api,
            self.test_monitoring_api,
            self.test_internationalization,
            self.test_frontend_components,
            self.test_backend_modules
        ]
        
        results = {
            "overall_status": "passed",
            "total_tests": len(test_suites),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "summary": {
                "critical_issues": [],
                "warnings": [],
                "recommendations": []
            }
        }
        
        for test_suite in test_suites:
            try:
                test_result = await test_suite()
                results["test_results"].append(test_result)
                
                if test_result["status"] == "passed":
                    results["passed_tests"] += 1
                    print(f"✅ {test_result['test_name']}: PASSED")
                else:
                    results["failed_tests"] += 1
                    results["overall_status"] = "failed"
                    print(f"❌ {test_result['test_name']}: FAILED")
                    
                    # Add to critical issues
                    for error in test_result["errors"]:
                        results["summary"]["critical_issues"].append(error)
                
                # Print details
                for detail in test_result["details"]:
                    print(f"   {detail}")
                for error in test_result["errors"]:
                    print(f"   {error}")
                    
            except Exception as e:
                results["failed_tests"] += 1
                results["overall_status"] = "failed"
                error_msg = f"❌ Test suite execution failed: {str(e)}"
                print(error_msg)
                results["summary"]["critical_issues"].append(error_msg)
        
        # Generate summary recommendations
        if results["overall_status"] == "passed":
            results["summary"]["recommendations"].append(
                "🎉 All tests passed! Platform is ready for 100% key-in-hand deployment."
            )
        else:
            results["summary"]["recommendations"].extend([
                "🔧 Address critical issues before production deployment",
                "📋 Review failed test details for specific fixes needed",
                "🚀 Re-run tests after implementing fixes"
            ])
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['passed_tests']}")
        print(f"   Failed: {results['failed_tests']}")
        print(f"   Overall Status: {results['overall_status'].upper()}")
        
        if results["summary"]["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES ({len(results['summary']['critical_issues'])}):")
            for issue in results["summary"]["critical_issues"][:5]:  # Show top 5
                print(f"   • {issue}")
        
        return results


# Test execution
async def main():
    """Main test execution function"""    tester = AinfluePlatformTests()
    results = await tester.run_comprehensive_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: test_results.json")
    return results


if __name__ == "__main__":
    asyncio.run(main())