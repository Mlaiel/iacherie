#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Remix System Integration Tests
================================================================================
Module: tests/ai_engine/remix_generation/test_professional_remix_integration.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Integration Tests (Level 4)
Created: 2025-01-20
================================================================================

Integration tests for the complete professional remix system.
"""

import pytest
import asyncio
import numpy as np
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, AsyncMock, patch

# Import the professional remix components
try:
    from ai_engine.remix_generation.professional_remix_coordinator import (
        ProfessionalRemixCoordinator,
        ProfessionalRemixRequest,
        ProfessionalRemixResult,
        RemixQuality,
        RemixStyle,
        ProcessingPipeline
    )
    from ai_engine.remix_generation.realtime_streaming_processor import (
        RealTimeStreamingProcessor,
        StreamingConfig,
        StreamingQuality,
        StreamingMode,
        AudioChunk
    )
except ImportError as e:
    pytest.skip(f"Professional remix modules not available: {e}", allow_module_level=True)


class TestProfessionalRemixIntegration:
    """Integration tests for professional remix system"""
    
    @pytest.fixture
    async def remix_coordinator(self):
        """Create a professional remix coordinator for testing"""
        coordinator = ProfessionalRemixCoordinator()
        
        # Mock the AI components to avoid dependencies
        coordinator._music_generation_engine = AsyncMock()
        coordinator._style_transfer_engine = AsyncMock()
        coordinator._mastering_engine = AsyncMock()
        coordinator._separation_service = AsyncMock()
        coordinator._collaboration_manager = AsyncMock()
        coordinator._quality_enhancer = AsyncMock()
        
        coordinator.is_initialized = True
        return coordinator
    
    @pytest.fixture
    def sample_audio_file(self):
        """Create a temporary audio file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            # Create mock audio data
            sample_rate = 44100
            duration = 1.0  # 1 second
            samples = int(sample_rate * duration)
            audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
            
            # Write to file (simplified - in real test would use actual audio format)
            f.write(audio_data.tobytes())
            return f.name
    
    @pytest.fixture
    def professional_remix_request(self, sample_audio_file):
        """Create a professional remix request for testing"""
        return ProfessionalRemixRequest(
            input_audio_path=sample_audio_file,
            target_style=RemixStyle.CLUB_MIX,
            quality_level=RemixQuality.PROFESSIONAL,
            pipeline=ProcessingPipeline.PROFESSIONAL_MASTERING,
            user_id="test_user_123",
            enable_stem_separation=True,
            enable_collaboration=False,
            generation_models=["wavenet", "musenet"],
            style_transfer_strength=0.8,
            creativity_level=0.7
        )
    
    @pytest.mark.asyncio
    async def test_professional_remix_coordinator_initialization(self):
        """Test professional remix coordinator initialization"""
        coordinator = ProfessionalRemixCoordinator()
        
        # Mock initialization methods
        with patch.object(coordinator, '_initialize_music_generation', new_callable=AsyncMock), \
             patch.object(coordinator, '_initialize_style_transfer', new_callable=AsyncMock), \
             patch.object(coordinator, '_initialize_mastering', new_callable=AsyncMock), \
             patch.object(coordinator, '_initialize_separation', new_callable=AsyncMock), \
             patch.object(coordinator, '_initialize_collaboration', new_callable=AsyncMock), \
             patch.object(coordinator, '_initialize_quality_enhancement', new_callable=AsyncMock):
            
            await coordinator.initialize()
            
            assert coordinator.is_initialized is True
            assert coordinator.config["professional_mastering_enabled"] is True
            assert coordinator.config["collaboration_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_professional_remix_creation(self, remix_coordinator, professional_remix_request):
        """Test complete professional remix creation process"""
        # Mock the processing methods
        remix_coordinator._perform_stem_separation = AsyncMock(return_value={
            "vocal": "/tmp/vocal.wav",
            "drums": "/tmp/drums.wav",
            "bass": "/tmp/bass.wav",
            "other": "/tmp/other.wav"
        })
        
        remix_coordinator._perform_music_generation = AsyncMock(return_value={
            "best_result": {"output_path": "/tmp/generated.wav", "quality_score": 0.92},
            "models_used": ["wavenet", "musenet"]
        })
        
        remix_coordinator._perform_style_transfer = AsyncMock(return_value={
            "output_path": "/tmp/styled.wav",
            "similarity_score": 0.89,
            "quality_score": 0.91
        })
        
        remix_coordinator._handle_collaboration = AsyncMock(return_value={
            "status": "disabled"
        })
        
        remix_coordinator._perform_professional_mastering = AsyncMock(return_value={
            "output_path": "/tmp/mastered.wav",
            "lufs": -16.0,
            "dynamic_range": 12.5,
            "quality_score": 0.95
        })
        
        remix_coordinator._perform_quality_enhancement = AsyncMock(return_value={
            "quality_score": 0.94,
            "technical_score": 0.93
        })
        
        # Execute professional remix
        result = await remix_coordinator.create_professional_remix(professional_remix_request)
        
        # Verify result
        assert result.success is True
        assert result.request_id is not None
        assert result.session_id is not None
        assert result.processing_time > 0
        assert result.main_remix_path == "/tmp/mastered.wav"
        assert len(result.models_used) == 2
        assert result.quality_score == 0.94
        assert result.mastering_lufs == -16.0
        assert result.style_similarity_score == 0.89
        
        # Verify all processing stages were called
        remix_coordinator._perform_stem_separation.assert_called_once()
        remix_coordinator._perform_music_generation.assert_called_once()
        remix_coordinator._perform_style_transfer.assert_called_once()
        remix_coordinator._perform_professional_mastering.assert_called_once()
        remix_coordinator._perform_quality_enhancement.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collaboration_workflow(self, remix_coordinator, professional_remix_request):
        """Test collaborative remix workflow"""
        # Enable collaboration
        professional_remix_request.enable_collaboration = True
        professional_remix_request.max_collaborators = 5
        
        # Mock collaboration setup
        remix_coordinator._handle_collaboration = AsyncMock(return_value={
            "session_id": "collab_session_123",
            "features": {
                "real_time_editing": True,
                "version_control": True,
                "conflict_resolution": "ai_mediated",
                "max_collaborators": 5
            },
            "status": "active"
        })
        
        # Mock other processing methods
        remix_coordinator._perform_stem_separation = AsyncMock(return_value={})
        remix_coordinator._perform_music_generation = AsyncMock(return_value={
            "best_result": {"output_path": "/tmp/generated.wav"},
            "models_used": ["wavenet"]
        })
        remix_coordinator._perform_style_transfer = AsyncMock(return_value={
            "output_path": "/tmp/styled.wav",
            "similarity_score": 0.85
        })
        remix_coordinator._perform_professional_mastering = AsyncMock(return_value={
            "output_path": "/tmp/mastered.wav",
            "lufs": -16.0
        })
        remix_coordinator._perform_quality_enhancement = AsyncMock(return_value={
            "quality_score": 0.90
        })
        
        # Execute remix with collaboration
        result = await remix_coordinator.create_professional_remix(professional_remix_request)
        
        # Verify collaboration was handled
        assert result.success is True
        assert "session_id" in result.collaboration_data
        remix_coordinator._handle_collaboration.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_session_management(self, remix_coordinator):
        """Test session management functionality"""
        # Create a mock session
        session_id = "test_session_123"
        session_data = {
            "request_id": "test_request_456",
            "session_id": session_id,
            "user_id": "test_user",
            "status": "processing",
            "progress": 50.0,
            "start_time": 1234567890
        }
        
        remix_coordinator.active_sessions[session_id] = session_data
        remix_coordinator.metrics["active_sessions"] = 1
        
        # Test session status retrieval
        status = await remix_coordinator.get_session_status(session_id)
        
        assert status["session_id"] == session_id
        assert status["status"] == "processing"
        assert status["progress"] == 50.0
        assert status["user_id"] == "test_user"
        
        # Test non-existent session
        status = await remix_coordinator.get_session_status("non_existent")
        assert status["status"] == "not_found"
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, remix_coordinator):
        """Test system metrics collection"""
        # Set up mock metrics
        remix_coordinator.metrics.update({
            "total_remixes": 10,
            "successful_remixes": 9,
            "average_processing_time": 45.5,
            "active_sessions": 2,
            "quality_scores": [0.85, 0.90, 0.88, 0.92, 0.87]
        })
        
        # Get system metrics
        metrics = await remix_coordinator.get_system_metrics()
        
        assert metrics["total_remixes"] == 10
        assert metrics["successful_remixes"] == 9
        assert metrics["success_rate_percent"] == 90.0
        assert metrics["average_processing_time_seconds"] == 45.5
        assert metrics["active_sessions"] == 2
        assert abs(metrics["average_quality_score"] - 0.884) < 0.01
        assert metrics["system_status"] == "operational"


class TestRealTimeStreamingIntegration:
    """Integration tests for real-time streaming processor"""
    
    @pytest.fixture
    async def streaming_processor(self):
        """Create a real-time streaming processor for testing"""
        processor = RealTimeStreamingProcessor()
        
        # Mock audio processor
        mock_audio_processor = Mock()
        mock_audio_processor.initialize = AsyncMock()
        mock_audio_processor.process_chunk = AsyncMock()
        
        processor.audio_processor = mock_audio_processor
        return processor
    
    @pytest.fixture
    def streaming_config(self):
        """Create streaming configuration for testing"""
        return StreamingConfig(
            sample_rate=44100,
            buffer_size=1024,
            channels=2,
            quality=StreamingQuality.BALANCED,
            mode=StreamingMode.ENHANCEMENT,
            enable_ai_processing=True,
            max_latency_ms=100.0
        )
    
    @pytest.mark.asyncio
    async def test_streaming_session_creation(self, streaming_processor, streaming_config):
        """Test creation of streaming session"""
        with patch.object(streaming_processor, '_start_session_processing', new_callable=AsyncMock):
            session_id = await streaming_processor.create_streaming_session("test_user", streaming_config)
            
            assert session_id.startswith("stream_test_user_")
            assert session_id in streaming_processor.active_sessions
            
            session = streaming_processor.active_sessions[session_id]
            assert session.user_id == "test_user"
            assert session.config == streaming_config
            assert session.is_active is True
    
    @pytest.mark.asyncio
    async def test_audio_chunk_processing(self, streaming_processor, streaming_config):
        """Test audio chunk processing in streaming"""
        # Create session
        with patch.object(streaming_processor, '_start_session_processing', new_callable=AsyncMock):
            session_id = await streaming_processor.create_streaming_session("test_user", streaming_config)
        
        # Create test audio data
        audio_data = np.random.random((1024, 2)).astype(np.float32)
        
        # Mock the audio processor to return processed chunk
        processed_chunk = AudioChunk(
            data=audio_data * 1.1,
            timestamp=1234567890.0,
            sample_rate=44100,
            channels=2,
            chunk_id=0,
            metadata={"processing_time_ms": 15.5}
        )
        streaming_processor.audio_processor.process_chunk.return_value = processed_chunk
        
        # Add audio chunk
        await streaming_processor.add_audio_chunk(session_id, audio_data)
        
        # Verify chunk was added to input buffer
        session = streaming_processor.active_sessions[session_id]
        assert not session.input_buffer.empty()
    
    @pytest.mark.asyncio
    async def test_session_status_and_metrics(self, streaming_processor, streaming_config):
        """Test session status retrieval and metrics"""
        # Create session
        with patch.object(streaming_processor, '_start_session_processing', new_callable=AsyncMock):
            session_id = await streaming_processor.create_streaming_session("test_user", streaming_config)
        
        # Update session metrics
        session = streaming_processor.active_sessions[session_id]
        session.chunks_processed = 100
        session.average_latency_ms = 25.5
        session.quality_score = 0.85
        
        # Get session status
        status = await streaming_processor.get_session_status(session_id)
        
        assert status["session_id"] == session_id
        assert status["user_id"] == "test_user"
        assert status["is_active"] is True
        assert status["chunks_processed"] == 100
        assert status["average_latency_ms"] == 25.5
        assert status["quality_score"] == 0.85
        assert "uptime_seconds" in status
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self, streaming_processor, streaming_config):
        """Test proper session cleanup"""
        # Create session
        with patch.object(streaming_processor, '_start_session_processing', new_callable=AsyncMock):
            session_id = await streaming_processor.create_streaming_session("test_user", streaming_config)
        
        assert session_id in streaming_processor.active_sessions
        
        # Stop session
        await streaming_processor.stop_session(session_id)
        
        assert session_id not in streaming_processor.active_sessions


class TestProfessionalRemixAPIIntegration:
    """Integration tests for the professional remix API"""
    
    @pytest.mark.asyncio
    async def test_api_health_check(self):
        """Test API health check endpoint"""
        try:
            from ai_engine.remix_generation.professional_remix_api import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "Professional AI Remix API"
            assert "timestamp" in data
            
        except ImportError:
            pytest.skip("FastAPI or API module not available")
    
    @pytest.mark.asyncio
    async def test_api_models_endpoint(self):
        """Test API models information endpoint"""
        try:
            from ai_engine.remix_generation.professional_remix_api import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/models")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "music_generation_models" in data
            assert "style_transfer_engines" in data
            assert "audio_processors" in data
            assert "collaboration_features" in data
            
            # Check WaveNet model is available
            models = data["music_generation_models"]
            wavenet_model = next((m for m in models if m["name"] == "WaveNet"), None)
            assert wavenet_model is not None
            assert wavenet_model["status"] == "available"
            assert wavenet_model["quality"] == "ultra_high"
            
        except ImportError:
            pytest.skip("FastAPI or API module not available")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])