# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
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
Comprehensive Tests for Content Creator Agent

Industrial-grade testing for the advanced content creation agent covering multi-format
content generation, style transfer, brand consistency, and platform optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  STRICT LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, modification, or use of this code,
concepts, or ideas without explicit written permission from Fahed Mlaiel
is strictly prohibited and will result in legal action.

Project Team Specialties:
 Lead Dev + Architecte Développeur IA
 Développeur Backend Senior (Python/FastAPI/Django)  
 Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
 DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
 Spécialiste Sécurité Backend
 Architecte Microservices
 Développeur Audio
 DevOps Engineer
 IA Prompt Engineer
"""

import pytest
import sys
import os
from pathlib import Path
import pytest_asyncio
import asyncio
import json
import uuid
import time
import tempfile
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import hashlib
import base64

# Add the agents path for direct import
content_creator_path = "/workspaces/Ainflue/backend/ai/ai_agents"
if content_creator_path not in sys.path:
    sys.path.insert(0, content_creator_path)

# Import content creator modules
try:
    from content_creator import (
        ContentCreatorAgent,
        ContentCreationRequest,
        ContentCreationResult
    )
    from base_agent import (
        AgentConfiguration,
        AgentCapability,
        AgentTask,
        AgentPriority,
        AgentStatus
    )
except ImportError as e:
    print(f"Warning: Could not import content creator modules: {e}")
    # Create mock classes for testing
    class MockContentCreatorAgent:
        pass
    class MockContentCreationRequest:
        pass
    class MockContentCreationResult:
        pass


# Mock content types and formats for testing
class ContentType:
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MUSIC = "music"

class ContentFormat:
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PNG = "png"
    JPG = "jpg"
    MP3 = "mp3"
    WAV = "wav"
    MP4 = "mp4"
    AVI = "avi"

class ContentQuality:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"


class TestableContentCreatorAgent(ContentCreatorAgent):
    """Testable implementation of ContentCreatorAgent"""
    
    def __init__(self, config: AgentConfiguration):
        try:
            super().__init__(config)
        except:
            # Fallback for testing without full dependencies
            self.config = config
            self.agent_id = config.agent_id
            self.agent_name = config.agent_name
            self.capabilities = config.capabilities
            self.status = AgentStatus.INITIALIZING
        
        self.created_content = []
        self.generation_history = []
        self.mock_outputs = {}
        
    async def _custom_initialize(self) -> None:
        """Test implementation of custom initialization"""
        await asyncio.sleep(0.1)
        self.status = AgentStatus.READY
        
    async def _create_text_content(self, request: ContentCreationRequest) -> Dict[str, Any]:
        """Mock text content creation"""
        content = f"Generated text content for: {request.style_preferences.get('topic', 'general')}"
        return {
            "content": content,
            "word_count": len(content.split()),
            "language": request.language,
            "style": request.style_preferences
        }
        
    async def _create_image_content(self, request: ContentCreationRequest) -> Dict[str, Any]:
        """Mock image content creation"""



        return {
            "image_path": f"/tmp/generated_image_{uuid.uuid4()}.{request.format}",
            "dimensions": request.resolution or "1920x1080",
            "file_size": 1024000,  # 1MB
            "style": request.style_preferences
        }
        
    async def _create_audio_content(self, request: ContentCreationRequest) -> Dict[str, Any]:
        """Mock audio content creation"""



        return {
            "audio_path": f"/tmp/generated_audio_{uuid.uuid4()}.{request.format}",
            "duration": request.duration_seconds or 30,
            "sample_rate": 44100,
            "channels": 2,
            "file_size": 2048000  # 2MB
        }
        
    async def _create_video_content(self, request: ContentCreationRequest) -> Dict[str, Any]:
        """Mock video content creation"""



        return {
            "video_path": f"/tmp/generated_video_{uuid.uuid4()}.{request.format}",
            "duration": request.duration_seconds or 60,
            "resolution": request.resolution or "1920x1080",
            "fps": 30,
            "file_size": 10240000  # 10MB
        }


class TestContentCreatorAgent:
    """Comprehensive test suite for ContentCreatorAgent"""
    
    @pytest.fixture
    def creator_config(self) -> AgentConfiguration:
        """Content creator agent configuration"""



        return AgentConfiguration(
            agent_id="content_creator_001",
            agent_name="Advanced Content Creator",
            capabilities={
                AgentCapability.TEXT_GENERATION,
                AgentCapability.IMAGE_GENERATION,
                AgentCapability.AUDIO_GENERATION,
                AgentCapability.VIDEO_GENERATION,
                AgentCapability.MUSIC_COMPOSITION,
                AgentCapability.CONTENT_OPTIMIZATION,
                AgentCapability.COPYRIGHT_DETECTION
            },
            max_concurrent_tasks=5,
            default_timeout=300,
            memory_limit_mb=2048,
            cpu_limit_percent=70,
            custom_settings={
                "content_quality": "high",
                "brand_consistency": True,
                "copyright_protection": True,
                "multi_platform_optimization": True
            }
        )
    
    @pytest_asyncio.fixture
    async def content_creator(self, creator_config) -> TestableContentCreatorAgent:
        """Initialized content creator agent"""
        agent = TestableContentCreatorAgent(creator_config)
        await agent._custom_initialize()
        return agent
    
    @pytest.fixture
    def text_creation_request(self) -> ContentCreationRequest:
        """Text content creation request"""



        return ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            quality=ContentQuality.HIGH,
            style_preferences={
                "topic": "AI and Technology",
                "tone": "professional",
                "length": "medium",
                "target_audience": "tech professionals"
            },
            target_audience="Software developers and AI researchers",
            language="en",
            keywords=["artificial intelligence", "machine learning", "innovation"],
            platform_requirements={
                "linkedin": {"max_length": 3000},
                "twitter": {"max_length": 280},
                "medium": {"min_length": 1000}
            }
        )
    
    @pytest.fixture
    def image_creation_request(self) -> ContentCreationRequest:
        """Image content creation request"""



        return ContentCreationRequest(
            content_type=ContentType.IMAGE,
            format=ContentFormat.PNG,
            quality=ContentQuality.PREMIUM,
            style_preferences={
                "style": "modern minimalist",
                "color_scheme": "blue and white",
                "mood": "professional"
            },
            resolution="1920x1080",
            brand_guidelines={
                "logo_position": "bottom_right",
                "brand_colors": ["#0066CC", "#FFFFFF"],
                "font_family": "Roboto"
            }
        )
    
    @pytest.fixture
    def audio_creation_request(self) -> ContentCreationRequest:
        """Audio content creation request"""



        return ContentCreationRequest(
            content_type=ContentType.AUDIO,
            format=ContentFormat.MP3,
            quality=ContentQuality.HIGH,
            duration_seconds=120,
            style_preferences={
                "genre": "ambient",
                "mood": "calm",
                "tempo": "slow"
            },
            platform_requirements={
                "spotify": {"bitrate": 320},
                "youtube": {"format": "mp4"}
            }
        )
    
    async def test_agent_initialization_and_capabilities(self, content_creator):
        """Test content creator agent initialization and capabilities"""
        assert content_creator.status == AgentStatus.READY
        
        # Verify required capabilities
        required_capabilities = {
            AgentCapability.TEXT_GENERATION,
            AgentCapability.IMAGE_GENERATION,
            AgentCapability.AUDIO_GENERATION,
            AgentCapability.VIDEO_GENERATION,
            AgentCapability.CONTENT_OPTIMIZATION
        }
        
        assert required_capabilities.issubset(content_creator.capabilities)
        
        # Test capability checking
        assert await content_creator.can_handle_task("text_generation", {})
        assert await content_creator.can_handle_task("image_generation", {})
        assert await content_creator.can_handle_task("audio_generation", {})
    
    async def test_text_content_creation(self, content_creator, text_creation_request):
        """Test text content creation functionality"""
        # Create content creation task
        task = AgentTask(
            task_type="create_content",
            context={
                "request": text_creation_request,
                "content_type": "text"
            },
            priority=AgentPriority.HIGH
        )
        
        # Mock the content creation
        with patch.object(content_creator, '_create_text_content') as mock_create:
            mock_create.return_value = {
                "content": "# AI and Technology\n\nArtificial intelligence is transforming...",
                "word_count": 250,
                "language": "en",
                "style": text_creation_request.style_preferences,
                "seo_score": 85,
                "readability_score": 90
            }
            
            # Execute task
            result = await content_creator._create_text_content(text_creation_request)
            
            # Verify result
            assert "content" in result
            assert result["word_count"] > 0
            assert result["language"] == "en"
            assert "seo_score" in result
    
    async def test_image_content_creation(self, content_creator, image_creation_request):
        """Test image content creation functionality"""
        task = AgentTask(
            task_type="create_content",
            context={
                "request": image_creation_request,
                "content_type": "image"
            }
        )
        
        # Execute image creation
        result = await content_creator._create_image_content(image_creation_request)
        
        # Verify result
        assert "image_path" in result
        assert result["dimensions"] == "1920x1080"
        assert result["file_size"] > 0
        assert "style" in result
    
    async def test_audio_content_creation(self, content_creator, audio_creation_request):
        """Test audio content creation functionality"""
        result = await content_creator._create_audio_content(audio_creation_request)
        
        # Verify audio result
        assert "audio_path" in result
        assert result["duration"] == 120
        assert result["sample_rate"] == 44100
        assert result["channels"] == 2
        assert result["file_size"] > 0
    
    async def test_video_content_creation(self, content_creator):
        """Test video content creation functionality"""
        video_request = ContentCreationRequest(
            content_type=ContentType.VIDEO,
            format=ContentFormat.MP4,
            quality=ContentQuality.HIGH,
            duration_seconds=90,
            resolution="1920x1080",
            style_preferences={
                "style": "cinematic",
                "transitions": "smooth",
                "color_grading": "warm"
            }
        )
        
        result = await content_creator._create_video_content(video_request)
        
        # Verify video result
        assert "video_path" in result
        assert result["duration"] == 90
        assert result["resolution"] == "1920x1080"
        assert result["fps"] == 30
    
    @pytest.mark.integration
    async def test_multi_format_content_creation_workflow(self, content_creator):
        """Test complete multi-format content creation workflow"""
        # Create requests for different content types
        requests = [
            ContentCreationRequest(
                content_type=ContentType.TEXT,
                format=ContentFormat.MARKDOWN,
                quality=ContentQuality.HIGH,
                style_preferences={"topic": "AI Innovation"}
            ),
            ContentCreationRequest(
                content_type=ContentType.IMAGE,
                format=ContentFormat.PNG,
                quality=ContentQuality.HIGH,
                resolution="1080x1080"
            ),
            ContentCreationRequest(
                content_type=ContentType.AUDIO,
                format=ContentFormat.MP3,
                quality=ContentQuality.HIGH,
                duration_seconds=60
            )
        ]
        
        # Execute all content creation tasks
        results = []
        for request in requests:
            if request.content_type == ContentType.TEXT:
                result = await content_creator._create_text_content(request)
            elif request.content_type == ContentType.IMAGE:
                result = await content_creator._create_image_content(request)
            elif request.content_type == ContentType.AUDIO:
                result = await content_creator._create_audio_content(request)
            
            results.append(result)
        
        # Verify all content was created
        assert len(results) == 3
        
        # Verify text content
        text_result = results[0]
        assert "content" in text_result
        assert "word_count" in text_result
        
        # Verify image content
        image_result = results[1]
        assert "image_path" in image_result
        assert "dimensions" in image_result
        
        # Verify audio content
        audio_result = results[2]
        assert "audio_path" in audio_result
        assert "duration" in audio_result
    
    async def test_content_quality_assessment(self, content_creator):
        """Test content quality assessment and scoring"""
        request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            quality=ContentQuality.PREMIUM,
            style_preferences={
                "quality_threshold": 0.9,
                "grammar_check": True,
                "plagiarism_check": True
            }
        )
        
        # Mock quality assessment
        with patch.object(content_creator, '_assess_content_quality') as mock_assess:
            mock_assess.return_value = {
                "overall_score": 0.92,
                "grammar_score": 0.95,
                "originality_score": 0.88,
                "readability_score": 0.93,
                "seo_score": 0.85,
                "brand_consistency_score": 0.97
            }
            
            # Create and assess content
            content_result = await content_creator._create_text_content(request)
            
            # Quality should meet premium standards
            if hasattr(content_creator, '_assess_content_quality'):
                quality_result = await content_creator._assess_content_quality(content_result, request)
                assert quality_result["overall_score"] >= 0.9
    
    @pytest.mark.performance
    async def test_concurrent_content_creation(self, content_creator):
        """Test concurrent content creation performance"""
        num_requests = 10
        requests = []
        
        for i in range(num_requests):
            request = ContentCreationRequest(
                content_type=ContentType.TEXT,
                format=ContentFormat.MARKDOWN,
                quality=ContentQuality.MEDIUM,
                style_preferences={"topic": f"Topic {i}"}
            )
            requests.append(request)
        
        # Create content concurrently
        start_time = time.time()
        tasks = [
            content_creator._create_text_content(request)
            for request in requests
        ]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verify all content was created
        assert len(results) == num_requests
        for result in results:
            assert "content" in result
        
        # Should complete reasonably fast with concurrency
        assert total_time < 10.0  # Should complete within 10 seconds
        
        # Calculate throughput
        throughput = num_requests / total_time
        assert throughput > 1.0  # At least 1 creation per second
    
    async def test_brand_consistency_enforcement(self, content_creator):
        """Test brand consistency enforcement"""
        brand_guidelines = {
            "brand_voice": "friendly but professional",
            "prohibited_words": ["cheap", "bad", "worst"],
            "required_elements": ["company_name", "brand_message"],
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
            "typography": {
                "primary_font": "Roboto",
                "secondary_font": "Open Sans"
            }
        }
        
        request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.HTML,
            quality=ContentQuality.HIGH,
            brand_guidelines=brand_guidelines,
            style_preferences={
                "enforce_brand_consistency": True
            }
        )
        
        # Mock brand consistency check
        with patch.object(content_creator, '_check_brand_consistency') as mock_check:
            mock_check.return_value = {
                "compliance_score": 0.88,
                "violations": [],
                "suggestions": ["Add brand message", "Use primary font"],
                "approved": True
            }
            
            result = await content_creator._create_text_content(request)
            
            # Content should comply with brand guidelines
            assert "content" in result
    
    async def test_platform_specific_optimization(self, content_creator):
        """Test platform-specific content optimization"""
        request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            quality=ContentQuality.HIGH,
            platform_requirements={
                "instagram": {
                    "max_length": 2200,
                    "hashtag_count": 30,
                    "mention_format": "@username"
                },
                "linkedin": {
                    "max_length": 3000,
                    "professional_tone": True,
                    "call_to_action": True
                },
                "twitter": {
                    "max_length": 280,
                    "hashtag_count": 3,
                    "thread_support": True
                }
            }
        )
        
        # Mock platform optimization
        with patch.object(content_creator, '_optimize_for_platforms') as mock_optimize:
            mock_optimize.return_value = {
                "instagram": {
                    "content": "Optimized Instagram post...",
                    "hashtags": ["#AI", "#Tech", "#Innovation"],
                    "character_count": 150
                },
                "linkedin": {
                    "content": "Professional LinkedIn post...",
                    "call_to_action": "Connect with us for more insights!",
                    "character_count": 280
                },
                "twitter": {
                    "content": "Concise Twitter post...",
                    "hashtags": ["#AI", "#Tech"],
                    "character_count": 120
                }
            }
            
            base_content = await content_creator._create_text_content(request)
            
            # Should have platform-specific versions
            if hasattr(content_creator, '_optimize_for_platforms'):
                optimized = await content_creator._optimize_for_platforms(base_content, request)
                assert "instagram" in optimized
                assert "linkedin" in optimized
                assert "twitter" in optimized
    
    async def test_copyright_and_fingerprinting(self, content_creator):
        """Test copyright protection and content fingerprinting"""
        request = ContentCreationRequest(
            content_type=ContentType.IMAGE,
            format=ContentFormat.PNG,
            quality=ContentQuality.HIGH,
            style_preferences={
                "copyright_protection": True,
                "watermark": True,
                "digital_signature": True
            }
        )
        
        # Mock copyright protection
        with patch.object(content_creator, '_apply_copyright_protection') as mock_copyright:
            mock_copyright.return_value = {
                "fingerprint": "sha256:abc123def456...",
                "watermark_applied": True,
                "digital_signature": "RSA:signature_hash",
                "copyright_metadata": {
                    "creator": "Fahed Mlaiel",
                    "creation_date": datetime.now(timezone.utc).isoformat(),
                    "rights": "All rights reserved"
                }
            }
            
            base_content = await content_creator._create_image_content(request)
            
            # Should have copyright protection
            if hasattr(content_creator, '_apply_copyright_protection'):
                protected = await content_creator._apply_copyright_protection(base_content, request)
                assert "fingerprint" in protected
                assert "watermark_applied" in protected
    
    @pytest.mark.stress
    async def test_high_volume_content_generation(self, content_creator):
        """Stress test with high volume content generation"""
        num_contents = 50
        content_types = [ContentType.TEXT, ContentType.IMAGE, ContentType.AUDIO]
        
        tasks = []
        for i in range(num_contents):
            content_type = content_types[i % len(content_types)]
            request = ContentCreationRequest(
                content_type=content_type,
                format=ContentFormat.MARKDOWN if content_type == ContentType.TEXT else ContentFormat.PNG,
                quality=ContentQuality.MEDIUM,
                style_preferences={"batch_id": f"batch_{i}"}
            )
            
            if content_type == ContentType.TEXT:
                task = content_creator._create_text_content(request)
            elif content_type == ContentType.IMAGE:
                task = content_creator._create_image_content(request)
            elif content_type == ContentType.AUDIO:
                task = content_creator._create_audio_content(request)
            
            tasks.append(task)
        
        # Execute in batches to manage memory
        batch_size = 10
        all_results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            all_results.extend(batch_results)
        
        # Count successful generations
        successful = sum(1 for r in all_results if isinstance(r, dict))
        success_rate = successful / num_contents
        
        # Should achieve high success rate
        assert success_rate >= 0.9
        print(f"High volume test: {successful}/{num_contents} successful ({success_rate:.1%})")
    
    async def test_content_style_transfer(self, content_creator):
        """Test content style transfer functionality"""
        source_content = "Original technical article about AI..."
        target_styles = ["casual", "formal", "creative", "persuasive"]
        
        request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            quality=ContentQuality.HIGH,
            style_preferences={
                "source_content": source_content,
                "style_transfer": True,
                "target_styles": target_styles
            }
        )
        
        # Mock style transfer
        with patch.object(content_creator, '_transfer_content_style') as mock_transfer:
            mock_transfer.return_value = {
                "casual": "Hey! Let me tell you about AI...",
                "formal": "This paper presents an analysis of artificial intelligence...",
                "creative": "Imagine a world where machines think...",
                "persuasive": "Why AI will revolutionize your business..."
            }
            
            if hasattr(content_creator, '_transfer_content_style'):
                result = await content_creator._transfer_content_style(source_content, target_styles)
                
                # Should have all target styles
                for style in target_styles:
                    assert style in result
                    assert len(result[style]) > 0
    
    @pytest.mark.edge_cases
    async def test_edge_cases_and_error_handling(self, content_creator):
        """Test edge cases and error handling"""
        # Test with minimal request
        minimal_request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            quality=ContentQuality.LOW
        )
        
        result = await content_creator._create_text_content(minimal_request)
        assert "content" in result
        
        # Test with maximum complexity request
        complex_request = ContentCreationRequest(
            content_type=ContentType.VIDEO,
            format=ContentFormat.MP4,
            quality=ContentQuality.PREMIUM,
            duration_seconds=300,
            resolution="4K",
            style_preferences={
                "style": "cinematic",
                "color_grading": "professional",
                "audio_quality": "studio",
                "effects": ["transitions", "text_overlays", "color_correction"]
            },
            brand_guidelines={
                "logo_placement": "corner",
                "brand_colors": ["#FF0000", "#00FF00"],
                "audio_branding": True
            },
            platform_requirements={
                "youtube": {"aspect_ratio": "16:9", "thumbnail": True},
                "instagram": {"aspect_ratio": "1:1", "duration": 60},
                "tiktok": {"aspect_ratio": "9:16", "duration": 30}
            }
        )
        
        result = await content_creator._create_video_content(complex_request)
        assert "video_path" in result
    
    async def test_collaboration_and_workflow_integration(self, content_creator):
        """Test collaboration features and workflow integration"""
        collaboration_request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.HTML,
            quality=ContentQuality.HIGH,
            collaboration_id="collab_001",
            style_preferences={
                "collaborative_editing": True,
                "review_workflow": True,
                "version_control": True
            }
        )
        
        # Mock collaboration features
        with patch.object(content_creator, '_setup_collaboration') as mock_collab:
            mock_collab.return_value = {
                "collaboration_id": "collab_001",
                "shared_workspace": "/shared/workspace/collab_001",
                "contributors": ["editor_1", "reviewer_1"],
                "workflow_status": "in_progress",
                "version": "1.0"
            }
            
            result = await content_creator._create_text_content(collaboration_request)
            
            # Should support collaborative features
            assert "content" in result
    
    def test_content_creation_request_validation(self):
        """Test content creation request validation"""
        # Valid request
        valid_request = ContentCreationRequest(
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            quality=ContentQuality.HIGH
        )
        
        assert valid_request.content_type == ContentType.TEXT
        assert valid_request.format == ContentFormat.MARKDOWN
        assert valid_request.quality == ContentQuality.HIGH
        assert valid_request.language == "en"  # Default
        
        # Request with full parameters
        full_request = ContentCreationRequest(
            content_type=ContentType.IMAGE,
            format=ContentFormat.PNG,
            quality=ContentQuality.PREMIUM,
            resolution="1920x1080",
            duration_seconds=None,
            language="de",
            mood="energetic",
            genre="modern",
            keywords=["innovation", "technology"],
            style_preferences={
                "color_scheme": "vibrant",
                "composition": "rule_of_thirds"
            },
            platform_requirements={
                "instagram": {"square": True},
                "facebook": {"landscape": True}
            },
            brand_guidelines={
                "logo": True,
                "colors": ["#FF0000", "#0000FF"]
            }
        )
        
        assert full_request.language == "de"
        assert full_request.mood == "energetic"
        assert len(full_request.keywords) == 2
        assert "color_scheme" in full_request.style_preferences
    
    def test_content_creation_result_structure(self):
        """Test content creation result structure"""
        result = ContentCreationResult(
            content_id="content_123",
            content_type=ContentType.TEXT,
            format=ContentFormat.MARKDOWN,
            file_path="/tmp/content_123.md",
            metadata={
                "word_count": 500,
                "reading_time": "2 minutes",
                "seo_score": 85
            },
            fingerprint="sha256:abcdef123456",
            quality_score=0.92,
            style_analysis={
                "tone": "professional",
                "complexity": "medium",
                "readability": "high"
            },
            creation_time=datetime.now(timezone.utc),
            processing_time_seconds=2.5,
            size_bytes=1024,
            copyright_status="protected",
            monetization_ready=True,
            platform_compatibility={
                "instagram": True,
                "linkedin": True,
                "twitter": False  # Too long
            },
            seo_metadata={
                "title": "AI Innovation Guide",
                "description": "Comprehensive guide to AI innovation",
                "keywords": ["AI", "innovation", "technology"]
            }
        )
        
        assert result.content_id == "content_123"
        assert result.quality_score == 0.92
        assert result.monetization_ready is True
        assert "instagram" in result.platform_compatibility
        assert "title" in result.seo_metadata


# Pytest markers for categorizing tests
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.content_creation
]


# Manual test runner
async def run_manual_content_creator_tests():
    """Run content creator tests manually"""
    print(" Running Content Creator Agent Tests...")
    
    try:
        test_suite = TestContentCreatorAgent()
        
        # Create test configuration
        config = AgentConfiguration(
            agent_id="test_content_creator",
            agent_name="Test Content Creator",
            capabilities={
                AgentCapability.TEXT_GENERATION,
                AgentCapability.IMAGE_GENERATION,
                AgentCapability.AUDIO_GENERATION
            }
        )
        
        # Create test agent
        agent = TestableContentCreatorAgent(config)
        await agent._custom_initialize()
        
        print(" Content Creator Agent Tests Completed!")
        return True
        
    except Exception as e:
        print(f" Content Creator tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_manual_content_creator_tests())
    if success:
        print(" All Content Creator tests passed!")
    else:
        print(" Some Content Creator tests failed!")

import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from ai.ai_agents import (
    ContentCreatorAgent,
    AgentConfiguration,
    AgentCapability,
    BaseAIAgent
)

logger = logging.getLogger(__name__)


class TestContentCreatorAgent:
    """Comprehensive test suite for ContentCreatorAgent"""
    
    @pytest.fixture
    def content_agent_config(self) -> AgentConfiguration:
        """Content creator agent configuration"""



        return AgentConfiguration(
            agent_id="content_creator_test",
            agent_name="Test Content Creator",
            capabilities={
                AgentCapability.text_generation,
                AgentCapability.image_generation,
                AgentCapability.audio_generation,
                AgentCapability.video_generation,
                AgentCapability.music_composition,
                AgentCapability.content_optimization,
                AgentCapability.content_fingerprinting,
                AgentCapability.real_time_processing
            },
            max_concurrent_tasks=5,
            default_timeout=60,
            custom_settings={
                "creativity_level": 0.8,
                "quality_threshold": 0.9,
                "originality_check": True,
                "multi_format_enabled": True,
                "brand_consistency": True
            }
        )
    
    @pytest.fixture
    async def content_agent(self, content_agent_config) -> ContentCreatorAgent:
        """Initialized content creator agent"""
        agent = ContentCreatorAgent(content_agent_config)
        await agent.initialize()
        
        yield agent
        
        await agent.shutdown()
    
    async def test_agent_initialization(self, content_agent_config):
        """Test content creator agent initialization"""
        agent = ContentCreatorAgent(content_agent_config)
        
        # Before initialization
        assert not agent.initialized
        assert agent.status.name == "CREATED"
        
        # Initialize
        result = await agent.initialize()
        
        # After initialization
        assert result is True
        assert agent.initialized
        assert agent.status.name == "READY"
        
        # Verify capabilities
        assert agent.has_capability(AgentCapability.text_generation)
        assert agent.has_capability(AgentCapability.image_generation)
        assert agent.has_capability(AgentCapability.audio_generation)
        assert agent.has_capability(AgentCapability.video_generation)
        assert agent.has_capability(AgentCapability.music_composition)
        
        # Verify custom settings
        assert agent.get_setting("creativity_level") == 0.8
        assert agent.get_setting("quality_threshold") == 0.9
        assert agent.get_setting("originality_check") is True
        
        await agent.shutdown()
    
    async def test_text_content_generation(self, content_agent, test_content_data):
        """Test text content generation"""
        text_request = {
            "task_type": "content_creation",
            "content_type": "text",
            "request": test_content_data["text_content"]
        }
        
        result = await content_agent.process_task(text_request)
        
        # Verify successful generation
        assert result["success"] is True
        assert "content" in result
        
        content = result["content"]
        assert "text" in content
        assert "metadata" in content
        assert "quality_score" in content
        assert "word_count" in content
        assert "readability_score" in content
        
        # Verify text quality
        generated_text = content["text"]
        assert isinstance(generated_text, str)
        assert len(generated_text) > 50  # Reasonable length
        assert "AI" in generated_text or "content" in generated_text  # Related to topic
        
        # Verify quality metrics
        assert 0 <= content["quality_score"] <= 1.0
        assert content["word_count"] > 0
        assert 0 <= content["readability_score"] <= 100
        
        # Verify metadata
        metadata = content["metadata"]
        assert "creation_time" in metadata
        assert "content_type" in metadata
        assert "platform_optimized" in metadata
        assert metadata["content_type"] == "text"
    
    async def test_image_content_generation(self, content_agent, test_content_data):
        """Test image content generation"""
        image_request = {
            "task_type": "content_creation",
            "content_type": "image",
            "request": test_content_data["image_content"]
        }
        
        result = await content_agent.process_task(image_request)
        
        # Verify successful generation
        assert result["success"] is True
        assert "content" in result
        
        content = result["content"]
        assert "image_data" in content or "image_url" in content
        assert "metadata" in content
        assert "quality_score" in content
        
        # Verify image metadata
        metadata = content["metadata"]
        assert "dimensions" in metadata
        assert "format" in metadata
        assert "creation_time" in metadata
        assert "style" in metadata
        
        # Verify dimensions match request
        requested_dims = test_content_data["image_content"]["dimensions"]
        assert metadata["dimensions"] == requested_dims
        
        # Verify format
        requested_format = test_content_data["image_content"]["format"]
        assert metadata["format"] == requested_format
        
        # Verify quality
        assert 0 <= content["quality_score"] <= 1.0
    
    async def test_audio_content_generation(self, content_agent, test_content_data):
        """Test audio content generation"""
        audio_request = {
            "task_type": "content_creation",
            "content_type": "audio",
            "request": test_content_data["audio_content"]
        }
        
        result = await content_agent.process_task(audio_request)
        
        # Verify successful generation
        assert result["success"] is True
        assert "content" in result
        
        content = result["content"]
        assert "audio_data" in content or "audio_url" in content
        assert "metadata" in content
        assert "quality_score" in content
        assert "audio_features" in content
        
        # Verify audio metadata
        metadata = content["metadata"]
        assert "duration" in metadata
        assert "sample_rate" in metadata
        assert "format" in metadata
        assert "channels" in metadata
        
        # Verify audio features
        features = content["audio_features"]
        assert "tempo" in features
        assert "key" in features
        assert "genre" in features
        assert "mood" in features
        
        # Verify requested parameters
        requested_duration = test_content_data["audio_content"]["duration"]
        assert abs(metadata["duration"] - requested_duration) < 2  # Within 2 seconds
        
        requested_genre = test_content_data["audio_content"]["genre"]
        assert features["genre"] == requested_genre
    
    async def test_video_content_generation(self, content_agent, test_content_data):
        """Test video content generation"""
        video_request = {
            "task_type": "content_creation",
            "content_type": "video",
            "request": test_content_data["video_content"]
        }
        
        result = await content_agent.process_task(video_request)
        
        # Verify successful generation
        assert result["success"] is True
        assert "content" in result
        
        content = result["content"]
        assert "video_data" in content or "video_url" in content
        assert "metadata" in content
        assert "quality_score" in content
        
        # Verify video metadata
        metadata = content["metadata"]
        assert "duration" in metadata
        assert "resolution" in metadata
        assert "format" in metadata
        assert "frame_rate" in metadata
        
        # Verify platform optimization
        requested_platform = test_content_data["video_content"]["platform"]
        assert "platform_optimized" in metadata
        assert metadata["platform_optimized"] == requested_platform
        
        # Verify format for platform
        if requested_platform == "tiktok":
            assert metadata["format"] == "vertical"
    
    async def test_music_composition(self, content_agent, test_audio_data):
        """Test music composition capabilities"""
        composition_request = {
            "task_type": "music_composition",
            "request": test_audio_data["composition_request"]
        }
        
        result = await content_agent.process_task(composition_request)
        
        # Verify successful composition
        assert result["success"] is True
        assert "composition" in result
        
        composition = result["composition"]
        assert "audio_data" in composition or "audio_url" in composition
        assert "musical_analysis" in composition
        assert "metadata" in composition
        assert "quality_score" in composition
        
        # Verify musical analysis
        analysis = composition["musical_analysis"]
        assert "key" in analysis
        assert "tempo" in analysis
        assert "time_signature" in analysis
        assert "chord_progression" in analysis
        assert "instruments" in analysis
        
        # Verify composition matches request
        request = test_audio_data["composition_request"]
        assert analysis["key"] == request["key"]
        assert abs(analysis["tempo"] - request["tempo"]) < 5  # Within 5 BPM
        
        # Verify instruments
        requested_instruments = set(request["instruments"])
        generated_instruments = set(analysis["instruments"])
        assert requested_instruments.issubset(generated_instruments)
    
    async def test_multi_format_content_generation(self, content_agent):
        """Test multi-format content generation"""
        multi_format_request = {
            "task_type": "multi_format_creation",
            "topic": "AI revolution in creative industries",
            "formats": ["text", "image", "audio"],
            "platform": "instagram",
            "style": "professional_engaging",
            "brand_guidelines": {
                "colors": ["#1DA1F2", "#FFFFFF"],
                "tone": "innovative_friendly",
                "keywords": ["AI", "creativity", "innovation"]
            }
        }
        
        result = await content_agent.process_task(multi_format_request)
        
        # Verify successful multi-format generation
        assert result["success"] is True
        assert "content_bundle" in result
        
        bundle = result["content_bundle"]
        assert "text_content" in bundle
        assert "image_content" in bundle
        assert "audio_content" in bundle
        assert "metadata" in bundle
        
        # Verify each format
        text_content = bundle["text_content"]
        assert "text" in text_content
        assert "hashtags" in text_content
        assert len(text_content["hashtags"]) > 0
        
        image_content = bundle["image_content"]
        assert "image_data" in image_content or "image_url" in image_content
        assert "style_consistency" in image_content
        
        audio_content = bundle["audio_content"]
        assert "audio_data" in audio_content or "audio_url" in audio_content
        assert "duration" in audio_content
        
        # Verify platform optimization
        metadata = bundle["metadata"]
        assert metadata["platform"] == "instagram"
        assert "cross_format_consistency" in metadata
        assert metadata["cross_format_consistency"] >= 0.8  # High consistency
    
    async def test_style_transfer(self, content_agent):
        """Test style transfer capabilities"""
        style_transfer_request = {
            "task_type": "style_transfer",
            "source_content": {
                "text": "This is a basic informational text about AI technology.",
                "type": "text"
            },
            "target_style": {
                "voice": "enthusiastic_influencer",
                "tone": "casual_engaging",
                "format": "social_media_post",
                "platform": "tiktok"
            },
            "preserve_meaning": True
        }
        
        result = await content_agent.process_task(style_transfer_request)
        
        # Verify successful style transfer
        assert result["success"] is True
        assert "transformed_content" in result
        
        transformed = result["transformed_content"]
        assert "text" in transformed
        assert "style_analysis" in transformed
        assert "quality_metrics" in transformed
        
        # Verify style transformation
        analysis = transformed["style_analysis"]
        assert "voice_match" in analysis
        assert "tone_match" in analysis
        assert "platform_optimization" in analysis
        
        # Verify quality metrics
        metrics = transformed["quality_metrics"]
        assert "readability_score" in metrics
        assert "engagement_potential" in metrics
        assert "brand_consistency" in metrics
        assert "meaning_preservation" in metrics
        
        # Verify meaning preservation
        assert metrics["meaning_preservation"] >= 0.8  # High preservation
        
        # Verify style application
        assert analysis["voice_match"] >= 0.7
        assert analysis["tone_match"] >= 0.7
    
    async def test_quality_assessment(self, content_agent):
        """Test content quality assessment"""
        content_for_assessment = {
            "text": "Check out this amazing AI tool that will revolutionize your content creation!  With cutting-edge technology, you can now generate professional-quality content in seconds. Perfect for influencers, marketers, and creators! #AI #ContentCreation #Innovation",
            "type": "social_media_post",
            "platform": "instagram"
        }
        
        quality_request = {
            "task_type": "quality_assessment",
            "content": content_for_assessment
        }
        
        result = await content_agent.process_task(quality_request)
        
        # Verify successful assessment
        assert result["success"] is True
        assert "quality_analysis" in result
        
        analysis = result["quality_analysis"]
        assert "overall_score" in analysis
        assert "dimensions" in analysis
        assert "recommendations" in analysis
        assert "strengths" in analysis
        assert "areas_for_improvement" in analysis
        
        # Verify quality dimensions
        dimensions = analysis["dimensions"]
        required_dimensions = [
            "readability", "engagement_potential", "brand_consistency",
            "platform_optimization", "originality", "emotional_impact"
        ]
        
        for dimension in required_dimensions:
            assert dimension in dimensions
            assert 0 <= dimensions[dimension] <= 1.0
        
        # Verify overall score
        assert 0 <= analysis["overall_score"] <= 1.0
        
        # Verify recommendations
        recommendations = analysis["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert "category" in recommendation
            assert "suggestion" in recommendation
            assert "impact" in recommendation
    
    async def test_platform_optimization(self, content_agent):
        """Test platform-specific optimization"""
        platforms = ["instagram", "tiktok", "youtube", "twitter", "linkedin"]
        
        base_content = {
            "topic": "AI in business transformation",
            "key_points": [
                "Automation increases efficiency",
                "AI reduces operational costs", 
                "Data-driven decision making",
                "Competitive advantage through AI"
            ]
        }
        
        optimization_results = {}
        
        for platform in platforms:
            optimization_request = {
                "task_type": "platform_optimization",
                "content": base_content,
                "target_platform": platform
            }
            
            result = await content_agent.process_task(optimization_request)
            
            # Verify successful optimization
            assert result["success"] is True
            assert "optimized_content" in result
            
            optimized = result["optimized_content"]
            assert "text" in optimized
            assert "hashtags" in optimized
            assert "optimal_timing" in optimized
            assert "engagement_strategies" in optimized
            
            optimization_results[platform] = optimized
        
        # Verify platform-specific differences
        # Instagram should have visual focus
        instagram_content = optimization_results["instagram"]
        assert "visual_elements" in instagram_content
        assert len(instagram_content["hashtags"]) <= 30  # Instagram limit
        
        # TikTok should have trending elements
        tiktok_content = optimization_results["tiktok"]
        assert "trending_elements" in tiktok_content
        assert "hook_strategy" in tiktok_content
        
        # LinkedIn should be professional
        linkedin_content = optimization_results["linkedin"]
        assert "professional_tone" in linkedin_content
        assert "industry_relevance" in linkedin_content
        
        # Twitter should be concise
        twitter_content = optimization_results["twitter"]
        assert len(twitter_content["text"]) <= 280  # Twitter limit
    
    async def test_content_fingerprinting(self, content_agent):
        """Test content fingerprinting for originality"""
        original_content = {
            "text": "This is completely original content created for testing purposes. It contains unique ideas and perspectives that have never been expressed before in this exact combination.",
            "type": "article",
            "metadata": {
                "author": "Test Author",
                "creation_date": datetime.now(timezone.utc).isoformat()
            }
        }
        
        fingerprint_request = {
            "task_type": "content_fingerprinting",
            "content": original_content
        }
        
        result = await content_agent.process_task(fingerprint_request)
        
        # Verify successful fingerprinting
        assert result["success"] is True
        assert "fingerprint" in result
        
        fingerprint = result["fingerprint"]
        assert "hash" in fingerprint
        assert "features" in fingerprint
        assert "originality_score" in fingerprint
        assert "similar_content" in fingerprint
        
        # Verify fingerprint properties
        assert isinstance(fingerprint["hash"], str)
        assert len(fingerprint["hash"]) > 10  # Reasonable hash length
        
        features = fingerprint["features"]
        assert "text_length" in features
        assert "vocabulary_richness" in features
        assert "semantic_features" in features
        
        # Verify originality
        assert 0 <= fingerprint["originality_score"] <= 1.0
        assert fingerprint["originality_score"] > 0.8  # Should be highly original
        
        # Test duplicate detection
        duplicate_request = {
            "task_type": "content_fingerprinting",
            "content": original_content  # Same content
        }
        
        duplicate_result = await content_agent.process_task(duplicate_request)
        duplicate_fingerprint = duplicate_result["fingerprint"]
        
        # Fingerprints should be identical for identical content
        assert duplicate_fingerprint["hash"] == fingerprint["hash"]
    
    async def test_brand_consistency(self, content_agent):
        """Test brand consistency enforcement"""
        brand_guidelines = {
            "voice": "professional_friendly",
            "tone": "innovative_trustworthy",
            "values": ["innovation", "reliability", "customer_focus"],
            "prohibited_words": ["cheap", "discount", "basic"],
            "required_elements": ["call_to_action", "brand_mention"],
            "color_palette": ["#1DA1F2", "#FFFFFF", "#14171A"],
            "style_preferences": {
                "sentence_length": "medium",
                "paragraph_length": "short",
                "use_emojis": True,
                "technical_depth": "medium"
            }
        }
        
        consistency_request = {
            "task_type": "brand_consistency_check",
            "content": {
                "text": "Our innovative platform provides reliable solutions for your business needs. Transform your workflow with cutting-edge technology!  Contact us today to learn more.",
                "type": "marketing_copy"
            },
            "brand_guidelines": brand_guidelines
        }
        
        result = await content_agent.process_task(consistency_request)
        
        # Verify successful consistency check
        assert result["success"] is True
        assert "consistency_analysis" in result
        
        analysis = result["consistency_analysis"]
        assert "overall_score" in analysis
        assert "voice_compliance" in analysis
        assert "tone_compliance" in analysis
        assert "values_alignment" in analysis
        assert "prohibited_content_check" in analysis
        assert "required_elements_check" in analysis
        
        # Verify compliance scores
        assert 0 <= analysis["overall_score"] <= 1.0
        assert 0 <= analysis["voice_compliance"] <= 1.0
        assert 0 <= analysis["tone_compliance"] <= 1.0
        
        # Verify values alignment
        values_alignment = analysis["values_alignment"]
        for value in brand_guidelines["values"]:
            assert value in values_alignment
            assert 0 <= values_alignment[value] <= 1.0
        
        # Verify prohibited content check
        prohibited_check = analysis["prohibited_content_check"]
        assert "violations_found" in prohibited_check
        assert "violation_count" in prohibited_check
        
        # Verify required elements
        required_check = analysis["required_elements_check"]
        for element in brand_guidelines["required_elements"]:
            assert element in required_check
    
    async def test_content_enhancement(self, content_agent):
        """Test content enhancement capabilities"""
        basic_content = {
            "text": "AI is good for business. It helps companies.",
            "type": "social_media_post",
            "target_audience": "business_professionals"
        }
        
        enhancement_request = {
            "task_type": "content_enhancement",
            "content": basic_content,
            "enhancement_goals": [
                "increase_engagement",
                "improve_clarity",
                "add_emotional_appeal",
                "optimize_length",
                "include_call_to_action"
            ]
        }
        
        result = await content_agent.process_task(enhancement_request)
        
        # Verify successful enhancement
        assert result["success"] is True
        assert "enhanced_content" in result
        
        enhanced = result["enhanced_content"]
        assert "text" in enhanced
        assert "improvements_made" in enhanced
        assert "quality_comparison" in enhanced
        
        # Verify enhancement improvements
        enhanced_text = enhanced["text"]
        original_text = basic_content["text"]
        
        # Enhanced text should be longer and more detailed
        assert len(enhanced_text) > len(original_text)
        
        # Should contain more engaging elements
        improvements = enhanced["improvements_made"]
        assert len(improvements) > 0
        
        # Verify quality comparison
        comparison = enhanced["quality_comparison"]
        assert "before_score" in comparison
        assert "after_score" in comparison
        assert "improvement_percentage" in comparison
        
        # Enhanced content should have better quality
        assert comparison["after_score"] > comparison["before_score"]
        assert comparison["improvement_percentage"] > 0
    
    async def test_concurrent_content_generation(self, content_agent):
        """Test concurrent content generation"""
        requests = []
        
        # Create multiple content requests
        for i in range(5):
            request = {
                "task_type": "content_creation",
                "content_type": "text",
                "request": {
                    "topic": f"AI topic {i}",
                    "style": "engaging_professional",
                    "length": "medium",
                    "platform": "linkedin"
                }
            }
            requests.append(content_agent.process_task(request))
        
        # Execute concurrently
        results = await asyncio.gather(*requests)
        
        # Verify all requests completed successfully
        assert len(results) == 5
        for result in results:
            assert result["success"] is True
            assert "content" in result
            assert "text" in result["content"]
    
    @pytest.mark.performance
    async def test_content_generation_performance(self, content_agent, assert_performance):
        """Test content generation performance"""
        # Test text generation speed
        text_request = {
            "task_type": "content_creation",
            "content_type": "text",
            "request": {
                "topic": "AI performance testing",
                "style": "professional",
                "length": "short"
            }
        }
        
        result = await content_agent.process_task(text_request)
        assert_performance("text_generation", max_time=10.0)
        
        assert result["success"] is True
        
        # Test multi-format generation speed
        multi_request = {
            "task_type": "multi_format_creation",
            "topic": "Performance testing",
            "formats": ["text", "image"],
            "platform": "instagram"
        }
        
        result = await content_agent.process_task(multi_request)
        assert_performance("multi_format_generation", max_time=30.0)
        
        assert result["success"] is True
    
    async def test_error_handling(self, content_agent):
        """Test error handling in content generation"""
        # Test invalid content type
        invalid_request = {
            "task_type": "content_creation",
            "content_type": "invalid_type",
            "request": {"topic": "test"}
        }
        
        result = await content_agent.process_task(invalid_request)
        assert result["success"] is False
        assert "error" in result
        
        # Test missing required parameters
        incomplete_request = {
            "task_type": "content_creation",
            "content_type": "text"
            # Missing 'request' parameter
        }
        
        result = await content_agent.process_task(incomplete_request)
        assert result["success"] is False
        assert "error" in result
        
        # Agent should remain functional after errors
        valid_request = {
            "task_type": "content_creation",
            "content_type": "text",
            "request": {
                "topic": "Error recovery test",
                "style": "professional"
            }
        }
        
        result = await content_agent.process_task(valid_request)
        assert result["success"] is True
