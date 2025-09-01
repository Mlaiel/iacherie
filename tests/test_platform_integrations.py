# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Tests for Platform APIs Integration
===================================

Basic tests to validate the platform integration modules work correctly.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from integrations.platforms.api_rate_limiter import APIRateLimiter, RateLimitRule, RateLimitStatus
from integrations.platforms.platform_oauth_manager import PlatformOAuthManager, OAuthConfig, OAuthTokens
from integrations.platforms.platform_coordinator import PlatformCoordinator, PlatformStatus


class TestAPIRateLimiter:
    """
Test API Rate Limiter functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_check(self):
        """
Test basic rate limit checking"""
        async with APIRateLimiter() as limiter:
            # First request should be allowed
            status = await limiter.check_rate_limit("youtube", "search")
            assert not status.is_limited
            assert status.remaining_requests >= 0
            
            # Record the request
            await limiter.record_request("youtube", "search")
            
    @pytest.mark.asyncio 
    async def test_rate_limit_rules(self):
        """Test rate limit rule configuration"""
        async with APIRateLimiter() as limiter:
            # Test default YouTube limits
            assert "youtube" in limiter.platform_limits
            youtube_limits = limiter.platform_limits["youtube"]
            assert "*" in youtube_limits
            assert isinstance(youtube_limits["*"], RateLimitRule)
            
    @pytest.mark.asyncio
    async def test_platform_status(self):
        """Test platform status retrieval"""
        async with APIRateLimiter() as limiter:
            status = await limiter.get_platform_status("youtube")
            assert isinstance(status, dict)
            assert "*" in status


class TestPlatformOAuthManager:
    """Test Platform OAuth Manager functionality"""
    
    @pytest.mark.asyncio
    async def test_oauth_manager_initialization(self):
        """
Test OAuth manager initialization"""
        async with PlatformOAuthManager() as oauth_manager:
            supported_platforms = oauth_manager.get_supported_platforms()
            assert "youtube" in supported_platforms
            assert "instagram" in supported_platforms
            assert "tiktok" in supported_platforms
            assert "spotify" in supported_platforms
            assert "facebook" in supported_platforms
            assert "twitter" in supported_platforms
            
    @pytest.mark.asyncio
    async def test_platform_configuration(self):
        """Test platform OAuth configuration"""
        async with PlatformOAuthManager() as oauth_manager:
            oauth_manager.configure_platform(
                "youtube",
                "test_client_id",
                "test_client_secret", 
                "http://localhost:8000/callback"
            )
            
            config = oauth_manager.platform_configs["youtube"]
            assert config.client_id == "test_client_id"
            assert config.client_secret == "test_client_secret"
            assert config.redirect_uri == "http://localhost:8000/callback"
            
    @pytest.mark.asyncio
    async def test_authorization_url_generation(self):
        """Test OAuth authorization URL generation"""
        async with PlatformOAuthManager() as oauth_manager:
            oauth_manager.configure_platform(
                "youtube",
                "test_client_id",
                "test_client_secret",
                "http://localhost:8000/callback"
            )
            
            auth_url, state = oauth_manager.generate_authorization_url("youtube", "test_user")
            
            assert "accounts.google.com" in auth_url
            assert "test_client_id" in auth_url
            assert state in oauth_manager.oauth_states
            assert oauth_manager.oauth_states[state]["platform"] == "youtube"
            assert oauth_manager.oauth_states[state]["user_id"] == "test_user"
            
    @pytest.mark.asyncio
    async def test_token_encryption(self):
        """Test token encryption and decryption"""
        async with PlatformOAuthManager() as oauth_manager:
            # Create test tokens
            tokens = OAuthTokens(
                platform="youtube",
                user_id="test_user",
                access_token="test_access_token",
                refresh_token="test_refresh_token",
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
            # Encrypt tokens
            encrypted = oauth_manager.encrypt_tokens(tokens)
            assert isinstance(encrypted, str)
            assert encrypted != tokens.access_token
            
            # Decrypt tokens
            decrypted = oauth_manager.decrypt_tokens(encrypted)
            assert decrypted.platform == tokens.platform
            assert decrypted.user_id == tokens.user_id
            assert decrypted.access_token == tokens.access_token
            assert decrypted.refresh_token == tokens.refresh_token


class TestPlatformCoordinator:
    """Test Platform Coordinator functionality"""
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self):
        """
Test coordinator initialization"""
        async with PlatformCoordinator() as coordinator:
            assert coordinator.oauth_manager is not None
            assert coordinator.rate_limiter is not None
            assert coordinator.youtube_api is not None
            assert coordinator.instagram_api is not None
            assert coordinator.tiktok_api is not None
            assert coordinator.spotify_api is not None
            assert coordinator.facebook_api is not None
            assert coordinator.twitter_api is not None
            assert coordinator.dmca_api is not None
            
    @pytest.mark.asyncio
    async def test_platform_oauth_configuration(self):
        """
Test platform OAuth configuration through coordinator"""
        async with PlatformCoordinator() as coordinator:
            coordinator.configure_platform_oauth(
                "youtube",
                "test_client_id",
                "test_client_secret",
                "http://localhost:8000/callback"
            )
            
            config = coordinator.oauth_manager.platform_configs["youtube"]
            assert config.client_id == "test_client_id"
            
    @pytest.mark.asyncio
    async def test_platform_health_check(self):
        """Test platform health checking"""
        async with PlatformCoordinator() as coordinator:
            # Test with no tokens (should be disconnected)
            status = await coordinator.check_platform_health("test_user", "youtube")
            assert isinstance(status, PlatformStatus)
            assert status.platform == "youtube"
            assert not status.is_connected
            assert not status.is_authenticated
            
    @pytest.mark.asyncio
    async def test_token_storage(self):
        """Test token storage and retrieval"""
        async with PlatformCoordinator() as coordinator:
            # Store test tokens
            tokens = OAuthTokens(
                platform="youtube",
                user_id="test_user",
                access_token="test_access_token",
                refresh_token="test_refresh_token",
                expires_at=datetime.now() + timedelta(hours=1)
            )
            
            coordinator.tokens_storage["test_user"] = {"youtube": tokens}
            
            # Retrieve tokens
            retrieved_tokens = await coordinator.get_user_tokens("test_user", "youtube")
            assert retrieved_tokens is not None
            assert retrieved_tokens.access_token == "test_access_token"
            
    @pytest.mark.asyncio
    async def test_all_platform_status(self):
        """Test getting status for all platforms"""
        async with PlatformCoordinator() as coordinator:
            status_dict = await coordinator.get_all_platform_status("test_user")
            
            assert isinstance(status_dict, dict)
            assert "youtube" in status_dict
            assert "instagram" in status_dict
            assert "tiktok" in status_dict
            assert "spotify" in status_dict
            assert "facebook" in status_dict
            assert "twitter" in status_dict
            
            for platform, status in status_dict.items():
                assert isinstance(status, PlatformStatus)
                assert status.platform == platform


@pytest.mark.asyncio
async def test_integration_basic_workflow():
    """Test basic integration workflow"""
    async with PlatformCoordinator() as coordinator:
        # Configure OAuth
        coordinator.configure_platform_oauth(
            "youtube",
            "test_client_id", 
            "test_client_secret",
            "http://localhost:8000/callback"
        )
        
        # Generate auth URL
        auth_url = await coordinator.initiate_platform_auth("youtube", "test_user")
        assert "accounts.google.com" in auth_url
        
        # Check initial health status
        status = await coordinator.check_platform_health("test_user", "youtube")
        assert not status.is_connected
        
        # Test rate limiting
        rate_status = await coordinator.rate_limiter.check_rate_limit("youtube", "search")
        assert not rate_status.is_limited


def test_module_imports():
    """Test that all modules can be imported successfully"""
    from integrations.platforms import (
        PlatformCoordinator,
        PlatformOAuthManager,
        APIRateLimiter,
        YouTubeContentIDAPI,
        InstagramBusinessAPI,
        TikTokCreatorAPI,
        SpotifyArtistsAPI,
        FacebookRightsAPI,
        TwitterAPIv2,
        DMCAServicesAPI
    )
    
    # Test that classes can be instantiated
    rate_limiter = APIRateLimiter()
    oauth_manager = PlatformOAuthManager()
    coordinator = PlatformCoordinator()
    
    assert rate_limiter is not None
    assert oauth_manager is not None
    assert coordinator is not None


if __name__ == "__main__":
    # Run basic tests
    asyncio.run(test_integration_basic_workflow())
    test_module_imports()
    print("✅ All basic tests passed!")