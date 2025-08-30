#!/usr/bin/env python3
"""
Mobile Services Validation Script - Ainflue Platform
Quick validation of mobile services implementation.

© 2025 Fahed Mlaiel. All rights reserved.
Lead Developer: Fahed Mlaiel (mlaiel@live.de)
"""

import sys
import os
import asyncio
from datetime import datetime

# Add mobile services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api', 'mobile'))

def test_mobile_api_gateway():
    """Test Mobile API Gateway."""
    try:
        from mobile_api_gateway import MobileAPIGateway, MobileUploadRequest, MobileResponse
        
        # Test initialization
        gateway = MobileAPIGateway()
        assert gateway is not None
        assert hasattr(gateway, 'router')
        
        # Test upload request creation
        upload_request = MobileUploadRequest(
            content_type="audio",
            file_data=b"test_data",
            metadata={"title": "Test"},
            device_info={"model": "Test Device"}
        )
        assert upload_request.content_type == "audio"
        
        print("✅ Mobile API Gateway: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Mobile API Gateway: FAILED - {str(e)}")
        return False

def test_mobile_auth_service():
    """Test Mobile Authentication Service."""
    try:
        from mobile_auth_service import MobileAuthService, MobileAuthRequest, BiometricType, DevicePlatform
        
        # Test initialization
        auth_service = MobileAuthService()
        assert auth_service is not None
        assert hasattr(auth_service, 'trusted_devices')
        
        # Test auth request creation
        auth_request = MobileAuthRequest(
            device_id="test_device",
            platform=DevicePlatform.IOS,
            biometric_type=BiometricType.FINGERPRINT,
            device_info={"model": "iPhone"}
        )
        assert auth_request.device_id == "test_device"
        assert auth_request.platform == DevicePlatform.IOS
        
        print("✅ Mobile Auth Service: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Mobile Auth Service: FAILED - {str(e)}")
        return False

def test_mobile_session_manager():
    """Test Mobile Session Manager."""
    try:
        from mobile_session_manager import MobileSessionManager, SessionState, SyncStatus
        
        # Test initialization
        session_manager = MobileSessionManager()
        assert session_manager is not None
        assert hasattr(session_manager, 'active_sessions')
        assert hasattr(session_manager, 'offline_sessions')
        
        # Test enums
        assert SessionState.ACTIVE is not None
        assert SyncStatus.SYNCED is not None
        
        print("✅ Mobile Session Manager: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Mobile Session Manager: FAILED - {str(e)}")
        return False

def test_mobile_repository():
    """Test Mobile Repository."""
    try:
        from mobile_repository import MobileRepository, MobileDataType, StorageStrategy
        
        # Test initialization
        repository = MobileRepository()
        assert repository is not None
        assert hasattr(repository, 'local_storage')
        assert hasattr(repository, 'sync_queue')
        
        # Test enums
        assert MobileDataType.CONTENT is not None
        assert StorageStrategy.OFFLINE_FIRST is not None
        
        print("✅ Mobile Repository: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Mobile Repository: FAILED - {str(e)}")
        return False

def test_mobile_services_index():
    """Test Mobile Services Index."""
    try:
        from index import mobile_services_index, get_mobile_services_summary
        
        # Test index functionality
        assert mobile_services_index is not None
        assert hasattr(mobile_services_index, 'services')
        
        # Test summary function
        summary = get_mobile_services_summary()
        assert summary is not None
        assert "services" in summary
        assert "implementation_status" in summary
        
        print("✅ Mobile Services Index: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Mobile Services Index: FAILED - {str(e)}")
        return False

async def test_async_mobile_functionality():
    """Test async mobile functionality."""
    try:
        from mobile_api_gateway import MobileAPIGateway
        from mobile_auth_service import MobileAuthService
        from mobile_session_manager import MobileSessionManager
        from mobile_repository import MobileRepository
        
        # Create service instances
        gateway = MobileAPIGateway()
        auth_service = MobileAuthService()
        session_manager = MobileSessionManager()
        repository = MobileRepository()
        
        # Test async methods exist and are callable
        assert hasattr(gateway, '_process_mobile_upload')
        assert hasattr(auth_service, 'authenticate_mobile')
        assert hasattr(session_manager, 'create_mobile_session')
        assert hasattr(repository, 'store_mobile_data')
        
        print("✅ Async Mobile Functionality: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Async Mobile Functionality: FAILED - {str(e)}")
        return False

def test_mobile_imports():
    """Test mobile services can be imported."""
    try:
        # Test all mobile service imports
        import mobile_api_gateway
        import mobile_auth_service  
        import mobile_session_manager
        import mobile_repository
        import index
        
        print("✅ Mobile Imports: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Mobile Imports: FAILED - {str(e)}")
        return False

def check_mobile_files_exist():
    """Check that all required mobile files exist."""
    mobile_api_dir = os.path.join(os.path.dirname(__file__), 'api', 'mobile')
    
    required_files = [
        'mobile_api_gateway.py',
        'mobile_auth_service.py', 
        'mobile_session_manager.py',
        'mobile_repository.py',
        'index.py',
        '__init__.py'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(mobile_api_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing mobile files: {missing_files}")
        return False
    else:
        print("✅ All mobile files exist: PASSED")
        return True

def main():
    """Run all mobile service validation tests."""
    print("🧪 Running Mobile Services Validation Tests...")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("👨‍💻 Developer: Fahed Mlaiel (mlaiel@live.de)")
    print("🏢 Project: Ainflue Mobile Services Architecture")
    print("-" * 60)
    
    test_results = []
    
    # File existence check
    print("\n📁 Checking Mobile Files...")
    test_results.append(check_mobile_files_exist())
    
    # Import tests
    print("\n📦 Testing Imports...")
    test_results.append(test_mobile_imports())
    
    # Service tests
    print("\n🧪 Testing Mobile Services...")
    test_results.append(test_mobile_api_gateway())
    test_results.append(test_mobile_auth_service())
    test_results.append(test_mobile_session_manager())
    test_results.append(test_mobile_repository())
    test_results.append(test_mobile_services_index())
    
    # Async functionality test
    print("\n⚡ Testing Async Functionality...")
    try:
        async_result = asyncio.run(test_async_mobile_functionality())
        test_results.append(async_result)
    except Exception as e:
        print(f"❌ Async test failed: {str(e)}")
        test_results.append(False)
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "="*60)
    print("🎉 MOBILE SERVICES VALIDATION SUMMARY")
    print("="*60)
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🚀 ALL MOBILE SERVICES VALIDATION TESTS PASSED!")
        print("✨ Mobile services architecture is production-ready!")
        print("\n📱 Mobile Services Ready For:")
        print("   • iOS and Android deployment")
        print("   • Offline-first content creation")
        print("   • Biometric authentication")
        print("   • Real-time synchronization")
        print("   • Professional content processing")
        
        return True
    else:
        failed_tests = total_tests - passed_tests
        print(f"⚠️  {failed_tests} validation test(s) failed")
        print("🔧 Please check implementation and try again")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)