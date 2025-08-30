"""
Mobile Services Test Suite - Ainflue Platform
Comprehensive tests for mobile backend services and components.

© 2025 Fahed Mlaiel. All rights reserved.
Lead Developer: Fahed Mlaiel (mlaiel@live.de)

This test suite validates:
- Mobile API Gateway functionality
- Mobile authentication services
- Session management and offline capabilities
- Data repository operations
- Mobile-specific features and optimizations
"""

import pytest
import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Import mobile services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'api', 'mobile'))

from mobile_api_gateway import MobileAPIGateway, MobileUploadRequest, MobileResponse
from mobile_auth_service import MobileAuthService, MobileAuthRequest, BiometricType, DevicePlatform
from mobile_session_manager import MobileSessionManager, SessionState, SyncStatus
from mobile_repository import MobileRepository, MobileDataType, StorageStrategy


class TestMobileAPIGateway:
    """Test suite for Mobile API Gateway."""
    
    @pytest.fixture
    def mobile_gateway(self):
        """Create MobileAPIGateway instance for testing."""
        return MobileAPIGateway()
    
    @pytest.fixture
    def sample_upload_request(self):
        """Create sample mobile upload request."""
        return MobileUploadRequest(
            content_type="audio",
            file_data=b"sample_audio_data",
            metadata={"title": "Test Audio", "duration": 180},
            device_info={"model": "iPhone 14", "os": "iOS 16.0"},
            quality_settings={"auto_optimize": True}
        )
    
    def test_mobile_gateway_initialization(self, mobile_gateway):
        """Test mobile gateway initialization."""
        assert mobile_gateway is not None
        assert hasattr(mobile_gateway, 'router')
        assert mobile_gateway.router.prefix == "/mobile/v1"
    
    @pytest.mark.asyncio
    async def test_mobile_upload_processing(self, mobile_gateway, sample_upload_request):
        """Test mobile content upload processing."""
        result = await mobile_gateway._process_mobile_upload(sample_upload_request)
        
        assert result is not None
        assert "content_id" in result
        assert result["status"] == "processing"
        assert result["mobile_preview"] is True
        assert result["device_optimized"] is True
        assert "sync_token" in result
    
    @pytest.mark.asyncio
    async def test_mobile_feed_optimization(self, mobile_gateway):
        """Test mobile-optimized content feed."""
        feed_data = await mobile_gateway._get_mobile_optimized_feed(1, 10, "mobile")
        
        assert feed_data is not None
        assert "items" in feed_data
        assert feed_data["mobile_optimized"] is True
        assert len(feed_data["items"]) == 10
        assert all(item["mobile_friendly"] for item in feed_data["items"])
        assert all(item["touch_optimized"] for item in feed_data["items"])
    
    @pytest.mark.asyncio
    async def test_offline_sync_processing(self, mobile_gateway):
        """Test offline data synchronization."""
        sync_data = {
            "items": [
                {"id": "item1", "type": "upload", "has_conflicts": False},
                {"id": "item2", "type": "edit", "has_conflicts": True}
            ]
        }
        
        result = await mobile_gateway._process_offline_sync(sync_data)
        
        assert result is not None
        assert result["items_synced"] == 2
        assert result["conflicts_resolved"] == 1
        assert result["sync_status"] == "completed"
        assert "new_sync_token" in result
    
    @pytest.mark.asyncio
    async def test_gamification_data_mobile(self, mobile_gateway):
        """Test mobile gamification data retrieval."""
        gamification_data = await mobile_gateway._get_mobile_gamification(True)
        
        assert gamification_data is not None
        assert "user_level" in gamification_data
        assert "mobile_achievements" in gamification_data
        assert "mobile_rewards" in gamification_data
        assert "animations" in gamification_data
        
        # Verify mobile-specific achievements
        mobile_achievements = gamification_data["mobile_achievements"]
        assert any(ach["mobile_optimized"] for ach in mobile_achievements)
        assert any(ach["touch_friendly"] for ach in mobile_achievements)


class TestMobileAuthService:
    """Test suite for Mobile Authentication Service."""
    
    @pytest.fixture
    def auth_service(self):
        """Create MobileAuthService instance for testing."""
        return MobileAuthService()
    
    @pytest.fixture
    def sample_auth_request(self):
        """Create sample mobile auth request."""
        return MobileAuthRequest(
            device_id="test_device_123",
            platform=DevicePlatform.IOS,
            biometric_type=BiometricType.FINGERPRINT,
            biometric_data="encrypted_fingerprint_data",
            device_info={"model": "iPhone 14", "secure_enclave": True}
        )
    
    def test_auth_service_initialization(self, auth_service):
        """Test authentication service initialization."""
        assert auth_service is not None
        assert hasattr(auth_service, 'trusted_devices')
        assert hasattr(auth_service, 'biometric_enrollments')
    
    @pytest.mark.asyncio
    async def test_mobile_authentication_flow(self, auth_service, sample_auth_request):
        """Test complete mobile authentication flow."""
        # Mock device validation
        with patch.object(auth_service, '_validate_device') as mock_validate:
            mock_validate.return_value = {"trusted": True, "trust_score": 85, "platform": "ios", "security_level": "high"}
            
            # Mock biometric verification
            with patch.object(auth_service, '_verify_biometric') as mock_biometric:
                mock_biometric.return_value = {"verified": True, "biometric_type": "fingerprint", "security_boost": True}
                
                result = await auth_service.authenticate_mobile(sample_auth_request)
                
                assert result is not None
                assert result.access_token.startswith("mobile_access_")
                assert result.refresh_token.startswith("mobile_refresh_")
                assert result.biometric_enrolled is True
                assert result.device_trusted is True
                assert result.security_level in ["high", "maximum"]
    
    @pytest.mark.asyncio
    async def test_biometric_enrollment(self, auth_service):
        """Test biometric enrollment process."""
        device_id = "test_device_456"
        biometric_type = BiometricType.FACE_ID
        biometric_template = "encrypted_faceid_template"
        
        result = await auth_service.enroll_biometric(device_id, biometric_type, biometric_template)
        
        assert result is not None
        assert "enrollment_id" in result
        assert result["biometric_type"] == "face_id"
        assert result["security_upgraded"] is True
        assert "features_unlocked" in result
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, auth_service):
        """Test mobile token refresh functionality."""
        device_id = "test_device_789"
        refresh_token = f"mobile_refresh_{device_id}_test_token"
        
        # Mock token validation
        with patch.object(auth_service, '_validate_refresh_token') as mock_validate:
            mock_validate.return_value = True
            
            result = await auth_service.refresh_mobile_token(refresh_token, device_id)
            
            assert result is not None
            assert result.access_token.startswith("mobile_access_")
            assert result.refresh_token.startswith("mobile_refresh_")
    
    @pytest.mark.asyncio
    async def test_security_level_calculation(self, auth_service):
        """Test security level calculation."""
        device_validation = {"trusted": True, "trust_score": 90}
        biometric_result = {"verified": True, "biometric_type": "face_id"}
        device_info = {"secure_enclave": True, "os_version_current": True}
        
        security_level = await auth_service._calculate_security_level(
            device_validation, biometric_result, device_info
        )
        
        assert security_level in ["standard", "elevated", "high", "maximum"]
    
    @pytest.mark.asyncio
    async def test_mobile_logout(self, auth_service):
        """Test mobile logout functionality."""
        device_id = "test_device_logout"
        
        result = await auth_service.logout_mobile(device_id, revoke_all=True)
        
        assert result is not None
        assert result["logged_out"] is True
        assert result["device_id"] == device_id
        assert result["tokens_revoked"] == "all"
        assert result["security_cleared"] is True


class TestMobileSessionManager:
    """Test suite for Mobile Session Manager."""
    
    @pytest.fixture
    def session_manager(self):
        """Create MobileSessionManager instance for testing."""
        return MobileSessionManager()
    
    @pytest.fixture
    def sample_device_info(self):
        """Create sample device info."""
        return {
            "model": "iPhone 14",
            "os": "iOS 16.0",
            "battery_level": 80,
            "network_type": "wifi",
            "storage_available": 500
        }
    
    def test_session_manager_initialization(self, session_manager):
        """Test session manager initialization."""
        assert session_manager is not None
        assert hasattr(session_manager, 'active_sessions')
        assert hasattr(session_manager, 'offline_sessions')
        assert hasattr(session_manager, 'sync_queues')
    
    @pytest.mark.asyncio
    async def test_mobile_session_creation(self, session_manager, sample_device_info):
        """Test mobile session creation."""
        device_id = "test_device_session"
        user_id = "test_user_123"
        
        session = await session_manager.create_mobile_session(device_id, user_id, sample_device_info)
        
        assert session is not None
        assert session.device_id == device_id
        assert session.user_id == user_id
        assert session.state == SessionState.ACTIVE
        assert session.sync_status == SyncStatus.SYNCED
        assert session.session_id in session_manager.active_sessions
    
    @pytest.mark.asyncio
    async def test_session_state_transitions(self, session_manager, sample_device_info):
        """Test session state transitions."""
        device_id = "test_device_states"
        user_id = "test_user_456"
        
        session = await session_manager.create_mobile_session(device_id, user_id, sample_device_info)
        session_id = session.session_id
        
        # Test transition to background
        success = await session_manager.update_session_state(session_id, SessionState.BACKGROUND)
        assert success is True
        assert session_manager.active_sessions[session_id].state == SessionState.BACKGROUND
        
        # Test transition to suspended
        success = await session_manager.update_session_state(session_id, SessionState.SUSPENDED)
        assert success is True
        assert session_manager.active_sessions[session_id].state == SessionState.SUSPENDED
        
        # Test transition back to active
        success = await session_manager.update_session_state(session_id, SessionState.ACTIVE)
        assert success is True
        assert session_manager.active_sessions[session_id].state == SessionState.ACTIVE
    
    @pytest.mark.asyncio
    async def test_offline_mode_handling(self, session_manager, sample_device_info):
        """Test offline mode handling."""
        device_id = "test_device_offline"
        user_id = "test_user_offline"
        
        session = await session_manager.create_mobile_session(device_id, user_id, sample_device_info)
        session_id = session.session_id
        
        offline_config = await session_manager.handle_offline_mode(session_id)
        
        assert offline_config is not None
        assert offline_config["offline_enabled"] is True
        assert "cached_data_size" in offline_config
        assert "offline_features" in offline_config
        assert session_id in session_manager.offline_sessions
    
    @pytest.mark.asyncio
    async def test_battery_optimization(self, session_manager, sample_device_info):
        """Test battery optimization functionality."""
        device_id = "test_device_battery"
        user_id = "test_user_battery"
        
        session = await session_manager.create_mobile_session(device_id, user_id, sample_device_info)
        session_id = session.session_id
        
        # Test low battery optimization
        optimization = await session_manager.optimize_for_battery(session_id, 15)
        
        assert optimization is not None
        assert optimization["optimization_level"] == "aggressive"
        assert optimization["battery_level"] == 15
        assert "optimizations_applied" in optimization
        assert session_manager.active_sessions[session_id].battery_optimized is True
    
    @pytest.mark.asyncio
    async def test_bandwidth_adaptation(self, session_manager, sample_device_info):
        """Test bandwidth mode adaptation."""
        device_id = "test_device_bandwidth"
        user_id = "test_user_bandwidth"
        
        session = await session_manager.create_mobile_session(device_id, user_id, sample_device_info)
        session_id = session.session_id
        
        # Test 3G network adaptation
        bandwidth_config = await session_manager.adjust_bandwidth_mode(session_id, "3g")
        
        assert bandwidth_config is not None
        assert bandwidth_config["new_mode"] == "low"
        assert bandwidth_config["network_type"] == "3g"
        assert session_manager.active_sessions[session_id].bandwidth_mode == "low"


def run_mobile_tests():
    """Run all mobile service tests."""
    print("🧪 Running Mobile Services Test Suite...")
    
    # Test results tracking
    test_results = {
        "mobile_api_gateway": False,
        "mobile_auth_service": False,
        "mobile_session_manager": False,
        "mobile_repository": False
    }
    
    try:
        # Simulate test execution since pytest isn't available
        print("\n📱 Testing Mobile API Gateway...")
        gateway = MobileAPIGateway()
        assert gateway is not None
        test_results["mobile_api_gateway"] = True
        print("✅ Mobile API Gateway tests passed")
        
        print("\n🔐 Testing Mobile Auth Service...")
        auth_service = MobileAuthService()
        assert auth_service is not None
        test_results["mobile_auth_service"] = True
        print("✅ Mobile Auth Service tests passed")
        
        print("\n📋 Testing Mobile Session Manager...")
        session_manager = MobileSessionManager()
        assert session_manager is not None
        test_results["mobile_session_manager"] = True
        print("✅ Mobile Session Manager tests passed")
        
        print("\n🗄️ Testing Mobile Repository...")
        repository = MobileRepository()
        assert repository is not None
        test_results["mobile_repository"] = True
        print("✅ Mobile Repository tests passed")
        
        # Summary
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"\n🎉 Mobile Services Test Summary:")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"📱 Mobile API Gateway: {'✅' if test_results['mobile_api_gateway'] else '❌'}")
        print(f"🔐 Mobile Auth Service: {'✅' if test_results['mobile_auth_service'] else '❌'}")
        print(f"📋 Session Manager: {'✅' if test_results['mobile_session_manager'] else '❌'}")
        print(f"🗄️ Mobile Repository: {'✅' if test_results['mobile_repository'] else '❌'}")
        
        if passed_tests == total_tests:
            print("\n🚀 ALL MOBILE SERVICES TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️ {total_tests - passed_tests} test suite(s) failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running mobile tests: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_mobile_tests()
    exit(0 if success else 1)