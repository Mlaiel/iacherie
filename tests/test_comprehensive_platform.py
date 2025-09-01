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
Comprehensive Testing Framework for Ainflue Platform

Integration tests, unit tests, and end-to-end testing for all platform components.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import aiohttp
import json
import tempfile
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Import our implementations
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from implementation.ai_task_processor import (
    AITaskProcessor, TaskType, TaskPriority, TaskContext, AITask
)
from implementation.platform_integration_manager import (
    PlatformIntegrationManager, PlatformType, APICredentials
)
from implementation.content_surveillance_implementation import (
    PlatformContentSurveillance, ContentType, DetectionResult
)


class TestAITaskProcessor:
    """
Test suite for AI Task Processor"""
    
    @pytest.fixture
    async def task_processor(self):
        """
Create AI task processor fixture"""
        config = {
            "max_concurrent_tasks": 5,
            "default_timeout": 30
        }
        processor = AITaskProcessor(config)
        yield processor
        # Cleanup any active tasks
        for task_id in list(processor.active_tasks.keys()):
            await processor.cancel_task(task_id)
    
    @pytest.mark.asyncio
    async def test_task_submission(self, task_processor):
        """Test task submission"""
        context = TaskContext(
            content_id="test_content_123",
            content_type="audio",
            parameters={"test_param": "test_value"}
        )
        
        task_id = await task_processor.submit_task(
            task_type=TaskType.CONTENT_ANALYSIS,
            context=context,
            priority=TaskPriority.HIGH
        )
        
        assert task_id is not None
        assert len(task_id) > 0
        
        # Wait for task completion
        result = await task_processor.get_task_result(task_id, wait=True, timeout=10)
        
        assert result is not None
        assert result.task_id == task_id
        assert result.task_type == TaskType.CONTENT_ANALYSIS
        assert result.status.value in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_content_analysis_task(self, task_processor):
        """Test content analysis task execution"""
        context = TaskContext(
            content_id="audio_123",
            content_type="audio",
            content_data={"duration": 180, "bitrate": 320}
        )
        
        task_id = await task_processor.submit_task(
            TaskType.CONTENT_ANALYSIS,
            context
        )
        
        result = await task_processor.get_task_result(task_id, wait=True)
        
        assert result.status.value == "completed"
        assert "content_type" in result.result_data
        assert "features" in result.result_data
        assert result.result_data["content_type"] == "audio"
    
    @pytest.mark.asyncio
    async def test_fingerprint_generation(self, task_processor):
        """Test fingerprint generation task"""
        context = TaskContext(
            content_id="test_content",
            content_data={"audio_data": "mock_audio_data"}
        )
        
        task_id = await task_processor.submit_task(
            TaskType.FINGERPRINT_GENERATION,
            context
        )
        
        result = await task_processor.get_task_result(task_id, wait=True)
        
        assert result.status.value == "completed"
        assert "fingerprint_hash" in result.result_data
        assert "confidence" in result.result_data
        assert result.result_data["confidence"] >= 0.0
    
    @pytest.mark.asyncio
    async def test_task_cancellation(self, task_processor):
        """Test task cancellation"""
        context = TaskContext(content_id="test")
        
        task_id = await task_processor.submit_task(
            TaskType.CONTENT_ANALYSIS,
            context
        )
        
        # Cancel immediately
        cancelled = await task_processor.cancel_task(task_id)
        assert cancelled
        
        result = await task_processor.get_task_result(task_id)
        if result:
            assert result.status.value == "cancelled"
    
    @pytest.mark.asyncio
    async def test_health_check(self, task_processor):
        """Test health check task"""
        context = TaskContext()
        
        task_id = await task_processor.submit_task(
            TaskType.HEALTH_CHECK,
            context
        )
        
        result = await task_processor.get_task_result(task_id, wait=True)
        
        assert result.status.value == "completed"
        assert result.result_data["status"] == "healthy"
        assert "active_tasks" in result.result_data
        assert "metrics" in result.result_data
    
    @pytest.mark.asyncio
    async def test_system_status(self, task_processor):
        """Test system status retrieval"""
        status = await task_processor.get_system_status()
        
        assert "processor_status" in status
        assert "active_tasks" in status
        assert "metrics" in status
        assert "capabilities" in status
        assert isinstance(status["capabilities"], list)


class TestPlatformIntegrationManager:
    """Test suite for Platform Integration Manager"""
    
    @pytest.fixture
    def integration_manager(self):
        """
Create platform integration manager fixture"""
        return PlatformIntegrationManager()
    
    @pytest.fixture
    def mock_credentials(self):
        """
Mock API credentials"""
        return {
            "youtube": APICredentials(
                platform_id="youtube",
                api_key="test_youtube_key"
            ),
            "soundcloud": APICredentials(
                platform_id="soundcloud",
                client_id="test_soundcloud_id"
            )
        }
    
    def test_platform_initialization(self, integration_manager):
        """Test platform initialization"""
        platforms = integration_manager.get_supported_platforms()
        
        assert "youtube" in platforms
        assert "soundcloud" in platforms
        assert "instagram" in platforms
        assert "tiktok" in platforms
        assert "twitter" in platforms
        
        # Test platform info retrieval
        youtube_info = integration_manager.get_platform_info("youtube")
        assert youtube_info is not None
        assert youtube_info["name"] == "YouTube"
        assert youtube_info["platform_type"] == PlatformType.VIDEO_STREAMING.value
    
    def test_credentials_management(self, integration_manager, mock_credentials):
        """Test credentials management"""
        # Add credentials
        for platform_id, creds in mock_credentials.items():
            integration_manager.add_platform_credentials(platform_id, creds)
        
        # Verify credentials are stored
        assert "youtube" in integration_manager.credentials
        assert "soundcloud" in integration_manager.credentials
        
        youtube_creds = integration_manager.credentials["youtube"]
        assert youtube_creds.api_key == "test_youtube_key"
    
    @pytest.mark.asyncio
    async def test_session_management(self, integration_manager):
        """Test HTTP session management"""
        # Initialize session
        success = await integration_manager.initialize_session("youtube")
        assert success
        assert "youtube" in integration_manager.sessions
        
        # Close session
        await integration_manager.close_session("youtube")
        assert "youtube" not in integration_manager.sessions
    
    @pytest.mark.asyncio
    async def test_rate_limit_tracking(self, integration_manager):
        """Test rate limit tracking"""
        # Mock response headers
        headers = {
            "x-ratelimit-remaining": "999",
            "x-ratelimit-reset": str(int((datetime.utcnow() + timedelta(hours=1)).timestamp()))
        }
        
        integration_manager._update_rate_limit_tracking("youtube", headers)
        
        rate_limit_status = integration_manager.get_rate_limit_status("youtube")
        assert rate_limit_status["remaining"] == 999
        assert "reset_time" in rate_limit_status
    
    @pytest.mark.asyncio
    async def test_mock_api_request(self, integration_manager):
        """Test API request with mocked response"""
        # Add mock credentials
        integration_manager.add_platform_credentials(
            "youtube",
            APICredentials(platform_id="youtube", api_key="test_key")
        )
        
        # Mock aiohttp session
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"items": []})
            mock_response.headers = {}
            
            mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
            
            # Make request
            response = await integration_manager.make_api_request(
                platform_id="youtube",
                endpoint="/search",
                params={"q": "test"}
            )
            
            assert response.success
            assert response.platform_id == "youtube"


class TestContentSurveillance:
    """Test suite for Content Surveillance"""
    
    @pytest.fixture
    async def surveillance_engine(self):
        """
Create content surveillance engine fixture"""
        config = {
            "youtube_api_key": "test_key",
            "soundcloud_client_id": "test_id"
        }
        async with PlatformContentSurveillance(config) as engine:
            yield engine
    
    @pytest.mark.asyncio
    async def test_platform_detection(self, surveillance_engine):
        """Test platform detection from URLs"""
        test_urls = [
            ("https://www.youtube.com/watch?v=123", "youtube"),
            ("https://soundcloud.com/artist/track", "soundcloud"),
            ("https://www.instagram.com/p/123", "instagram"),
            ("https://www.tiktok.com/@user/video/123", "tiktok"),
            ("https://example.com/content", "generic")
        ]
        
        for url, expected_platform in test_urls:
            detected = surveillance_engine._detect_platform_from_url(url)
            assert detected == expected_platform
    
    @pytest.mark.asyncio
    async def test_mock_content_search(self, surveillance_engine):
        """Test content search with mocked responses"""
        with patch.object(surveillance_engine, '_search_platform') as mock_search:
            mock_search.return_value = [
                DetectionResult(
                    content_id="test_123",
                    platform="youtube",
                    url="https://youtube.com/watch?v=123",
                    content_type=ContentType.VIDEO,
                    confidence=0.85,
                    metadata={"title": "Test Video"},
                    detected_at=datetime.utcnow()
                )
            ]
            
            results = await surveillance_engine.search_content(
                query="test content",
                platforms=["youtube"]
            )
            
            assert len(results) == 1
            assert results[0].platform == "youtube"
            assert results[0].confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_screenshot_functionality(self, surveillance_engine):
        """Test screenshot functionality"""
        screenshot_path = await surveillance_engine.take_screenshot(
            "https://example.com/test"
        )
        
        assert screenshot_path is not None
        assert "screenshot_" in screenshot_path
        assert screenshot_path.endswith(".png")
    
    @pytest.mark.asyncio
    async def test_content_extraction(self, surveillance_engine):
        """Test content information extraction"""
        # Test generic extraction
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {"content-type": "text/html"}
            mock_response.read = AsyncMock(return_value=b"<html>Test content</html>")
            
            mock_get.return_value.__aenter__.return_value = mock_response
            
            info = await surveillance_engine.extract_content_info("https://example.com/test")
            
            assert info["platform"] == "generic"
            assert info["url"] == "https://example.com/test"
            assert info["status_code"] == 200


class TestIntegrationWorkflows:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    async def full_system(self):
        """
Create full system fixture with all components"""
        task_processor = AITaskProcessor()
        integration_manager = PlatformIntegrationManager()
        
        # Add test credentials
        integration_manager.add_platform_credentials(
            "youtube",
            APICredentials(platform_id="youtube", api_key="test_key")
        )
        
        async with PlatformContentSurveillance() as surveillance:
            yield {
                "task_processor": task_processor,
                "integration_manager": integration_manager,
                "surveillance": surveillance
            }
    
    @pytest.mark.asyncio
    async def test_content_upload_workflow(self, full_system):
        """Test complete content upload and processing workflow"""
        task_processor = full_system["task_processor"]
        
        # Step 1: Submit content for analysis
        context = TaskContext(
            content_id="upload_test_123",
            content_type="audio",
            content_data={
                "filename": "test_audio.mp3",
                "duration": 240,
                "bitrate": 320
            }
        )
        
        analysis_task_id = await task_processor.submit_task(
            TaskType.CONTENT_ANALYSIS,
            context
        )
        
        # Step 2: Generate fingerprint
        fingerprint_task_id = await task_processor.submit_task(
            TaskType.FINGERPRINT_GENERATION,
            context
        )
        
        # Step 3: Wait for both tasks to complete
        analysis_result = await task_processor.get_task_result(
            analysis_task_id, wait=True
        )
        fingerprint_result = await task_processor.get_task_result(
            fingerprint_task_id, wait=True
        )
        
        # Verify workflow completion
        assert analysis_result.status.value == "completed"
        assert fingerprint_result.status.value == "completed"
        
        # Verify results contain expected data
        assert "features" in analysis_result.result_data
        assert "fingerprint_hash" in fingerprint_result.result_data
    
    @pytest.mark.asyncio
    async def test_content_protection_workflow(self, full_system):
        """Test content protection and monitoring workflow"""
        task_processor = full_system["task_processor"]
        surveillance = full_system["surveillance"]
        
        # Step 1: Generate content fingerprint
        context = TaskContext(
            content_id="protect_test_456",
            content_data={"protected_content": "sample_data"}
        )
        
        fingerprint_task_id = await task_processor.submit_task(
            TaskType.FINGERPRINT_GENERATION,
            context
        )
        
        fingerprint_result = await task_processor.get_task_result(
            fingerprint_task_id, wait=True
        )
        
        assert fingerprint_result.status.value == "completed"
        
        # Step 2: Search for potential violations
        with patch.object(surveillance, 'search_content') as mock_search:
            mock_search.return_value = []
            
            search_results = await surveillance.search_content(
                query="test_content_search",
                platforms=["youtube"]
            )
            
            assert isinstance(search_results, list)
    
    @pytest.mark.asyncio
    async def test_platform_monitoring_workflow(self, full_system):
        """Test platform monitoring workflow"""
        integration_manager = full_system["integration_manager"]
        
        # Test multiple platform connections
        platforms = ["youtube", "soundcloud"]
        
        connection_results = {}
        for platform in platforms:
            # Mock the connection test
            with patch.object(integration_manager, 'make_api_request') as mock_request:
                mock_request.return_value.success = True
                
                result = await integration_manager.test_platform_connection(platform)
                connection_results[platform] = result
        
        # Verify all connections succeeded (mocked)
        for platform, success in connection_results.items():
            assert success, f"Connection failed for {platform}"


# Utility functions for testing

def create_mock_content_data(content_type: str = "audio") -> Dict[str, Any]:
    """Create mock content data for testing"""
    base_data = {
        "id": "test_content_123",
        "type": content_type,
        "created_at": datetime.utcnow().isoformat(),
        "size": 1024000
    }
    
    if content_type == "audio":
        base_data.update({
            "duration": 180,
            "bitrate": 320,
            "sample_rate": 44100,
            "format": "mp3"
        })
    elif content_type == "video":
        base_data.update({
            "duration": 300,
            "resolution": "1920x1080",
            "fps": 30,
            "codec": "h264"
        })
    elif content_type == "image":
        base_data.update({
            "width": 1920,
            "height": 1080,
            "format": "jpg",
            "color_space": "rgb"
        })
    
    return base_data


def create_test_config() -> Dict[str, Any]:
    """Create test configuration"""
    return {
        "max_concurrent_tasks": 3,
        "default_timeout": 10,
        "youtube_api_key": "test_youtube_key",
        "soundcloud_client_id": "test_soundcloud_id",
        "test_mode": True
    }


# Performance and load testing

@pytest.mark.asyncio
async def test_concurrent_task_processing():
    """Test concurrent task processing under load"""
    processor = AITaskProcessor({"max_concurrent_tasks": 5})
    
    # Submit multiple tasks concurrently
    task_ids = []
    for i in range(10):
        context = TaskContext(content_id=f"load_test_{i}")
        task_id = await processor.submit_task(TaskType.HEALTH_CHECK, context)
        task_ids.append(task_id)
    
    # Wait for all tasks to complete
    results = []
    for task_id in task_ids:
        result = await processor.get_task_result(task_id, wait=True, timeout=30)
        results.append(result)
    
    # Verify all tasks completed successfully
    successful_tasks = [r for r in results if r and r.status.value == "completed"]
    assert len(successful_tasks) == len(task_ids)
    
    # Verify system metrics
    status = await processor.get_system_status()
    assert status["metrics"]["tasks_processed"] >= len(task_ids)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([str(Path(__file__)), "-v", "--asyncio-mode=auto"])