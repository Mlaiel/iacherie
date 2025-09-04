#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration Tests for Remix IA Professionnel
================================================================================
Module: tests/test_remix_ia_professionnel_integration.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Integration Test Suite for Professional Remix AI System
Created: 2025-01-26
================================================================================

Tests for the core Remix IA Professionnel requirements:
- Modèles génératifs WaveNet/MuseNet
- Style transfer musical neuronal
- Séparation stems temps réel
- Mastering IA professionnel
- Collaboration temps réel multi-users
"""
import asyncio
import unittest
import numpy as np
import logging
import os
import sys
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRemixIAProfessionnelIntegration(unittest.TestCase):
    """Integration tests for Remix IA Professionnel system"""
    
    def setUp(self):
        """Set up test environment"""
        self.sample_rate = 44100
        self.test_audio_mono = np.random.normal(0, 0.1, self.sample_rate)  # 1 second of audio
        self.test_audio_stereo = np.random.normal(0, 0.1, (2, self.sample_rate))  # Stereo
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
    
    def test_wavenet_model_integration(self):
        """Test WaveNet model integration with real data"""
        logger.info("🧪 Testing WaveNet model integration...")
        
        try:
            from ai_engine.remix_generation.music_generation_models import (
                WaveNetGenerator, GenerationRequest, GenerationQuality
            )
            
            # Create WaveNet generator
            generator = WaveNetGenerator()
            
            # Create test request
            request = GenerationRequest(
                input_audio_path="test_input.wav",
                target_style="electronic",
                quality=GenerationQuality.HIGH,
                duration_seconds=5,
                sample_rate=self.sample_rate
            )
            
            # Test model creation
            model = generator._create_model()
            self.assertIsNotNone(model)
            logger.info("✅ WaveNet model created successfully")
            
            # Test async generation (using asyncio.run for compatibility)
            async def test_generation():
                result = await generator.generate_music(request)
                return result
            
            result = asyncio.run(test_generation())
            
            self.assertTrue(result.success)
            self.assertEqual(result.model_used.value, "wavenet")
            self.assertGreater(result.quality_score, 0.9)
            self.assertGreater(result.generation_time, 0.0)
            
            logger.info(f"✅ WaveNet generation: {result.quality_score:.2f} quality in {result.generation_time:.2f}s")
            
        except Exception as e:
            self.fail(f"WaveNet integration test failed: {e}")
    
    def test_real_time_stem_separation(self):
        """Test real-time stem separation capabilities"""
        logger.info("🧪 Testing real-time stem separation...")
        
        try:
            from ai_engine.remix_generation.instrument_separator import (
                RealTimeStreamingSeparator, InstrumentType
            )
            
            # Create streaming separator
            separator = RealTimeStreamingSeparator(
                chunk_size=1024,
                sample_rate=self.sample_rate,
                max_latency_ms=50.0
            )
            
            async def test_streaming():
                # Start streaming
                started = await separator.start_streaming()
                self.assertTrue(started)
                
                # Process audio chunks
                chunk_size = 1024
                total_chunks = len(self.test_audio_mono) // chunk_size
                
                processed_chunks = []
                for i in range(min(5, total_chunks)):  # Test first 5 chunks
                    start_idx = i * chunk_size
                    end_idx = start_idx + chunk_size
                    chunk = self.test_audio_mono[start_idx:end_idx]
                    
                    separated_sources = await separator.process_audio_chunk(chunk)
                    
                    # Verify separation results
                    self.assertIn(InstrumentType.VOCALS, separated_sources)
                    self.assertIn(InstrumentType.DRUMS, separated_sources)
                    self.assertIn(InstrumentType.BASS, separated_sources)
                    self.assertIn(InstrumentType.OTHER, separated_sources)
                    
                    # Check output dimensions
                    for source_type, audio_data in separated_sources.items():
                        self.assertEqual(len(audio_data), chunk_size)
                    
                    processed_chunks.append(separated_sources)
                
                # Stop streaming
                await separator.stop_streaming()
                
                return processed_chunks
            
            chunks = asyncio.run(test_streaming())
            self.assertGreater(len(chunks), 0)
            
            logger.info(f"✅ Processed {len(chunks)} audio chunks with real-time separation")
            
        except Exception as e:
            self.fail(f"Real-time stem separation test failed: {e}")
    
    def test_professional_mastering_pipeline(self):
        """Test professional mastering pipeline"""
        logger.info("🧪 Testing professional mastering pipeline...")
        
        try:
            from ai_engine.remix_generation.ai_mastering_engine import (
                ProfessionalMasteringPipeline, MasteringTarget
            )
            
            # Create mastering pipeline
            pipeline = ProfessionalMasteringPipeline(
                sample_rate=self.sample_rate,
                bit_depth=24
            )
            
            async def test_mastering():
                # Test streaming target
                result_streaming = await pipeline.master_audio(
                    self.test_audio_mono,
                    MasteringTarget.STREAMING
                )
                
                self.assertTrue(result_streaming.success)
                self.assertIsNotNone(result_streaming.mastered_audio)
                self.assertGreater(result_streaming.quality_score, 0.8)
                
                # Verify LUFS target compliance
                target_lufs = -14.0
                lufs_diff = abs(result_streaming.mastered_lufs - target_lufs)
                self.assertLess(lufs_diff, 1.0)  # Within 1 dB of target
                
                # Test audiophile target
                result_audiophile = await pipeline.master_audio(
                    self.test_audio_mono,
                    MasteringTarget.AUDIOPHILE
                )
                
                self.assertTrue(result_audiophile.success)
                self.assertGreater(result_audiophile.quality_score, 0.8)
                
                # Audiophile should preserve more dynamic range
                self.assertLess(result_audiophile.mastered_lufs, result_streaming.mastered_lufs)
                
                return result_streaming, result_audiophile
            
            streaming_result, audiophile_result = asyncio.run(test_mastering())
            
            logger.info(f"✅ Streaming master: {streaming_result.mastered_lufs:.1f} LUFS, Quality: {streaming_result.quality_score:.2f}")
            logger.info(f"✅ Audiophile master: {audiophile_result.mastered_lufs:.1f} LUFS, Quality: {audiophile_result.quality_score:.2f}")
            
        except Exception as e:
            self.fail(f"Professional mastering test failed: {e}")
    
    def test_websocket_collaboration_server(self):
        """Test WebSocket collaboration server"""
        logger.info("🧪 Testing WebSocket collaboration server...")
        
        try:
            from ai_engine.remix_generation.collaborative_remix_ai import (
                WebSocketCollaborationServer
            )
            
            # Create collaboration server
            server = WebSocketCollaborationServer(
                host="localhost",
                port=8766,  # Different port to avoid conflicts
                redis_url="redis://localhost:6379"
            )
            
            async def test_server():
                # Test server initialization
                self.assertFalse(server.is_running)
                
                # Test server start (would normally start actual WebSocket server)
                # For testing, we'll just verify the configuration
                self.assertEqual(server.host, "localhost")
                self.assertEqual(server.port, 8766)
                self.assertIsNotNone(server.active_connections)
                self.assertIsNotNone(server.session_connections)
                
                # Test session management structures
                session_id = "test_session_123"
                client_id = "test_client_456"
                
                # Simulate adding client to session
                server.session_connections[session_id].add(client_id)
                server.user_sessions[client_id] = session_id
                
                self.assertIn(client_id, server.session_connections[session_id])
                self.assertEqual(server.user_sessions[client_id], session_id)
                
                # Test session state structure
                session_state = await server._get_session_state(session_id)
                self.assertIn("session_id", session_state)
                self.assertIn("users", session_state)
                self.assertIn("user_count", session_state)
                
                return True
            
            result = asyncio.run(test_server())
            self.assertTrue(result)
            
            logger.info("✅ WebSocket collaboration server structure validated")
            
        except Exception as e:
            self.fail(f"WebSocket collaboration test failed: {e}")
    
    def test_style_transfer_integration(self):
        """Test neural style transfer integration"""
        logger.info("🧪 Testing neural style transfer...")
        
        try:
            from ai_engine.remix_generation.style_transfer_engine import (
                StyleAnalyzer, StyleTransferRequest, StyleTransferMode
            )
            
            # Create style analyzer
            analyzer = StyleAnalyzer()
            
            async def test_style_transfer():
                # Test spectral analysis
                spectral_data = await analyzer.analyze_spectral_content(
                    self.test_audio_mono, self.sample_rate
                )
                
                self.assertIn("stft_magnitude", spectral_data)
                self.assertIn("spectral_centroid", spectral_data)
                self.assertIn("harmonic_component", spectral_data)
                
                # Test instrument identification
                instruments = await analyzer.identify_instruments(spectral_data)
                
                # Should return probabilities for different instruments
                self.assertIsInstance(instruments, dict)
                
                # Probabilities should sum to approximately 1.0
                if instruments:
                    total_prob = sum(instruments.values())
                    self.assertAlmostEqual(total_prob, 1.0, places=1)
                
                return spectral_data, instruments
            
            spectral_data, instruments = asyncio.run(test_style_transfer())
            
            logger.info(f"✅ Style analysis completed: {len(spectral_data)} features extracted")
            if instruments:
                logger.info(f"✅ Identified {len(instruments)} instrument types")
            
        except Exception as e:
            self.fail(f"Style transfer test failed: {e}")
    
    def test_complete_remix_workflow(self):
        """Test complete remix workflow integration"""
        logger.info("🧪 Testing complete remix workflow...")
        
        try:
            # This test verifies that all components can work together
            from ai_engine.remix_generation.music_generation_models import (
                WaveNetGenerator, GenerationRequest, GenerationQuality
            )
            from ai_engine.remix_generation.style_transfer_engine import StyleAnalyzer
            from ai_engine.remix_generation.instrument_separator import RealTimeStreamingSeparator
            from ai_engine.remix_generation.ai_mastering_engine import ProfessionalMasteringPipeline, MasteringTarget
            
            async def test_workflow():
                workflow_results = {}
                
                # Step 1: Style Analysis
                analyzer = StyleAnalyzer()
                spectral_data = await analyzer.analyze_spectral_content(
                    self.test_audio_mono, self.sample_rate
                )
                workflow_results["style_analysis"] = len(spectral_data) > 0
                
                # Step 2: Stem Separation
                separator = RealTimeStreamingSeparator(chunk_size=1024, sample_rate=self.sample_rate)
                await separator.start_streaming()
                
                chunk = self.test_audio_mono[:1024]
                separated = await separator.process_audio_chunk(chunk)
                workflow_results["stem_separation"] = len(separated) > 0
                
                await separator.stop_streaming()
                
                # Step 3: AI Generation
                generator = WaveNetGenerator()
                request = GenerationRequest(
                    input_audio_path="test.wav",
                    target_style="electronic",
                    quality=GenerationQuality.HIGH,
                    duration_seconds=2,
                    sample_rate=self.sample_rate
                )
                
                generation_result = await generator.generate_music(request)
                workflow_results["ai_generation"] = generation_result.success
                
                # Step 4: Professional Mastering
                mastering_pipeline = ProfessionalMasteringPipeline(sample_rate=self.sample_rate)
                mastering_result = await mastering_pipeline.master_audio(
                    self.test_audio_mono, MasteringTarget.STREAMING
                )
                workflow_results["professional_mastering"] = mastering_result.success
                
                return workflow_results
            
            results = asyncio.run(test_workflow())
            
            # Verify all workflow steps completed successfully
            for step, success in results.items():
                self.assertTrue(success, f"Workflow step {step} failed")
                logger.info(f"✅ {step}: {'SUCCESS' if success else 'FAILED'}")
            
            logger.info("✅ Complete remix workflow integration test passed")
            
        except Exception as e:
            self.fail(f"Complete workflow test failed: {e}")
    
    def test_performance_benchmarks(self):
        """Test performance requirements compliance"""
        logger.info("🧪 Testing performance benchmarks...")
        
        try:
            import time
            
            # Test concurrent processing capability
            from ai_engine.remix_generation.ai_mastering_engine import ProfessionalMasteringPipeline, MasteringTarget
            
            async def test_concurrent_mastering():
                pipeline = ProfessionalMasteringPipeline(sample_rate=self.sample_rate)
                
                # Measure processing time
                start_time = time.time()
                
                # Process multiple tracks concurrently (simulated)
                tasks = []
                for i in range(3):  # Test 3 concurrent processes
                    audio_sample = np.random.normal(0, 0.1, self.sample_rate // 2)  # 0.5 second samples
                    task = pipeline.master_audio(audio_sample, MasteringTarget.STREAMING)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                
                processing_time = time.time() - start_time
                
                # Verify all processed successfully
                for result in results:
                    self.assertTrue(result.success)
                
                # Performance requirements
                self.assertLess(processing_time, 10.0)  # Should complete within 10 seconds
                avg_time_per_track = processing_time / len(results)
                self.assertLess(avg_time_per_track, 5.0)  # Average < 5 seconds per track
                
                return processing_time, len(results)
            
            processing_time, track_count = asyncio.run(test_concurrent_mastering())
            
            logger.info(f"✅ Processed {track_count} tracks in {processing_time:.2f}s")
            logger.info(f"✅ Average: {processing_time/track_count:.2f}s per track")
            
        except Exception as e:
            self.fail(f"Performance benchmark test failed: {e}")


def run_integration_test_suite():
    """Run the complete integration test suite"""
    logger.info("🚀 Starting Remix IA Professionnel Integration Test Suite")
    logger.info("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestRemixIAProfessionnelIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = (total_tests - failures - errors) / total_tests if total_tests > 0 else 0
    
    logger.info("=" * 80)
    logger.info("🎯 INTEGRATION TEST SUMMARY")
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {total_tests - failures - errors}")
    logger.info(f"Failed: {failures}")
    logger.info(f"Errors: {errors}")
    logger.info(f"Success Rate: {success_rate:.1%}")
    
    if success_rate >= 0.9:
        logger.info("✅ INTEGRATION TESTS PASSED - Remix IA Professionnel ready for production")
    else:
        logger.warning("⚠️ INTEGRATION TESTS INCOMPLETE - Review failures and errors")
    
    return {
        "total_tests": total_tests,
        "passed": total_tests - failures - errors,
        "failed": failures,
        "errors": errors,
        "success_rate": success_rate,
        "status": "PASSED" if success_rate >= 0.9 else "FAILED"
    }


if __name__ == "__main__":
    # Run the integration test suite
    results = run_integration_test_suite()
    
    # Exit with appropriate code
    exit_code = 0 if results["status"] == "PASSED" else 1
    sys.exit(exit_code)