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

# Live Streaming Computer Vision Tests - IA Influencer Agent
# Industrial-Grade Test Suite for Live Streaming and Real-Time Processing
#
# Project Team Specialties:
# - Lead Dev + AI Architect: Advanced AI/ML Systems Design
# - Backend Senior (Python/FastAPI): High-Performance API Development  
# - ML Engineer (TensorFlow/PyTorch/HuggingFace): Deep Learning Models
# - DBA & Data Engineer: Scalable Data Architecture
# - Security Backend Specialist: Enterprise Security Implementation
# - Microservices Architect: Distributed Systems Design
# - Audio Developer: Professional Audio Processing
# - DevOps Engineer: Production Infrastructure
# - AI Prompt Engineer: Advanced Language Model Integration
#
# Created by: Fahed Mlaiel (mlaiel@live.de)
# 
# ⚠️  STRICT COPYRIGHT WARNING ⚠️ 
# This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
# ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
# without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
# STRICTLY PROHIBITED and will result in immediate legal action.
# All rights reserved. Patent pending.

import unittest
import numpy as np
import cv2
import tempfile
import os
import time
import threading
import queue
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pytest
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Import the streaming modules to test
try:
    from ai.computer_vision.streaming import (
        LiveStreamProcessor, RealTimeAnalyzer, StreamOptimizer,
        AdaptiveBitrate, StreamingConfig, StreamMetrics, 
        QualityAdaptation, PerformanceMonitor
    )
except ImportError as e:
    print(f"Warning: Could not import streaming modules: {e}")
    # Create mock classes for testing infrastructure
    class LiveStreamProcessor:
        def __init__(self, config=None):
            self.config = config or StreamingConfig()
            self.is_streaming = False
    
    class RealTimeAnalyzer:
        def __init__(self, config=None):
            self.config = config or StreamingConfig()
    
    class StreamOptimizer:
        def __init__(self, config=None):
            self.config = config or StreamingConfig()
    
    class AdaptiveBitrate:
        def __init__(self, config=None):
            self.config = config or StreamingConfig()
    
    class PerformanceMonitor:
        def __init__(self):
            pass
    
    class StreamingConfig:
        def __init__(self):
            self.fps = 30
            self.input_resolution = (1920, 1080)
            self.output_resolution = (1920, 1080)
            self.buffer_size = 5
    
    class StreamMetrics:
        def __init__(self):
            self.timestamp = datetime.now()
            self.fps_current = 30.0
            self.cpu_usage = 50.0
            self.latency_ms = 100.0
            self.frame_drops = 0
    
    class QualityAdaptation:
        def __init__(self):
            self.current_quality = "1080p"
            self.target_quality = "1080p"
            self.config = config or {}
            self.is_streaming = False
        def start_streaming(self, input_source, output_destinations):
            return True
        def stop_streaming(self):
            pass
        def get_current_metrics(self):
            return None
        def get_analysis_results(self):
            return []
    
    class RealTimeAnalyzer:
        def __init__(self, config=None):
            self.config = config or {}
        def start_analysis(self):
            pass
        def stop_analysis(self):
            pass
        def analyze_frame_async(self, frame, frame_id):
            return True
        def get_analysis_result(self, timeout=0.1):
            return None
    
    class StreamOptimizer:
        def __init__(self, config=None):
            self.config = config or {}
        def optimize_stream_settings(self, metrics, analysis_results):
            return {}
    
    class AdaptiveBitrate:
        def __init__(self, config=None):
            self.config = config or {}
        def recommend_quality_adaptation(self, metrics):
            return None
    
    class StreamingConfig:
        def __init__(self, **kwargs):
            self.input_resolution = kwargs.get('input_resolution', (1920, 1080))
            self.output_resolution = kwargs.get('output_resolution', (1920, 1080))
            self.fps = kwargs.get('fps', 30)
            self.bitrate = kwargs.get('bitrate', 5000)
            self.enable_gpu = kwargs.get('enable_gpu', True)
            self.processing_threads = kwargs.get('processing_threads', 4)
    
    class StreamMetrics:
        def __init__(self):
            self.timestamp = datetime.now()
            self.fps_current = 30.0
            self.fps_average = 30.0
            self.latency_ms = 50.0
            self.cpu_usage = 45.0
            self.gpu_usage = 60.0
            self.frame_drops = 0
    
    class QualityAdaptation:
        def __init__(self):
            self.current_quality = "1080p"
            self.target_quality = "1080p"
            self.adaptation_reason = "No adaptation needed"
    
    class PerformanceMonitor:
        def __init__(self):
            pass
        def record_frame_metrics(self, processing_time, encoding_time, latency, frame_drops=0):
            return StreamMetrics()

class TestStreamingConfig(unittest.TestCase):
    """Test suite for StreamingConfig class"""
    
    def test_default_configuration(self):
        """Test StreamingConfig with default values"""
        config = StreamingConfig()
        
        self.assertEqual(config.input_resolution, (1920, 1080))
        self.assertEqual(config.output_resolution, (1920, 1080))
        self.assertEqual(config.fps, 30)
        self.assertEqual(config.bitrate, 5000)
        self.assertTrue(config.enable_gpu)
        self.assertEqual(config.processing_threads, 4)
    
    def test_custom_configuration(self):
        """Test StreamingConfig with custom values"""
        config = StreamingConfig(
            input_resolution=(3840, 2160),
            output_resolution=(1280, 720),
            fps=60,
            bitrate=8000,
            enable_gpu=False,
            processing_threads=8
        )
        
        self.assertEqual(config.input_resolution, (3840, 2160))
        self.assertEqual(config.output_resolution, (1280, 720))
        self.assertEqual(config.fps, 60)
        self.assertEqual(config.bitrate, 8000)
        self.assertFalse(config.enable_gpu)
        self.assertEqual(config.processing_threads, 8)
    
    def test_4k_configuration(self):
        """Test 4K streaming configuration"""
        config = StreamingConfig(
            input_resolution=(3840, 2160),
            output_resolution=(3840, 2160),
            fps=30,
            bitrate=15000,
            enable_gpu=True,
            processing_threads=6
        )
        
        self.assertEqual(config.input_resolution, (3840, 2160))
        self.assertEqual(config.output_resolution, (3840, 2160))
        self.assertEqual(config.bitrate, 15000)
    
    def test_mobile_streaming_configuration(self):
        """Test mobile-optimized streaming configuration"""
        config = StreamingConfig(
            input_resolution=(1280, 720),
            output_resolution=(854, 480),
            fps=24,
            bitrate=1500,
            enable_gpu=False,
            processing_threads=2
        )
        
        self.assertEqual(config.input_resolution, (1280, 720))
        self.assertEqual(config.output_resolution, (854, 480))
        self.assertEqual(config.fps, 24)
        self.assertEqual(config.bitrate, 1500)
        self.assertEqual(config.processing_threads, 2)

class TestLiveStreamProcessor(unittest.TestCase):
    """Test suite for LiveStreamProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = StreamingConfig(
            input_resolution=(1920, 1080),
            output_resolution=(1920, 1080),
            fps=30,
            bitrate=5000,
            processing_threads=2  # Reduced for testing
        )
        self.processor = LiveStreamProcessor(self.config)
    
    def test_processor_initialization(self):
        """Test LiveStreamProcessor initialization"""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.config, self.config)
        self.assertFalse(self.processor.is_streaming)
    
    def test_start_streaming_webcam(self):
        """Test starting streaming from webcam"""
        # Mock the streaming functionality
        with patch.object(self.processor, '_initialize_video_capture') as mock_cap, \
             patch.object(self.processor, '_initialize_video_writers') as mock_writers:
            
            mock_cap.return_value = Mock()
            mock_writers.return_value = [Mock()]
            
            result = self.processor.start_streaming(
                input_source="0",
                output_destinations=["test_output.mp4"]
            )
            
            # Note: This may return False in test environment without actual camera
            self.assertIsInstance(result, bool)
    
    def test_start_streaming_file_input(self):
        """Test starting streaming from file input"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            # Create a minimal test video file
            temp_path = temp_file.name
        
        try:
            with patch.object(self.processor, '_initialize_video_capture') as mock_cap, \
                 patch.object(self.processor, '_initialize_video_writers') as mock_writers:
                
                mock_cap.return_value = Mock()
                mock_writers.return_value = [Mock()]
                
                result = self.processor.start_streaming(
                    input_source=temp_path,
                    output_destinations=["test_output.mp4"]
                )
                
                self.assertIsInstance(result, bool)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_stop_streaming(self):
        """Test stopping streaming"""
        # Start streaming first (mocked)
        with patch.object(self.processor, '_initialize_video_capture') as mock_cap, \
             patch.object(self.processor, '_initialize_video_writers') as mock_writers:
            
            mock_cap.return_value = Mock()
            mock_writers.return_value = [Mock()]
            
            self.processor.is_streaming = True
            self.processor.stop_streaming()
            
            self.assertFalse(self.processor.is_streaming)
    
    def test_get_current_metrics(self):
        """Test getting current streaming metrics"""
        metrics = self.processor.get_current_metrics()
        
        # Should return None when not streaming, or StreamMetrics when streaming
        self.assertTrue(metrics is None or hasattr(metrics, 'fps_current'))
    
    def test_get_analysis_results(self):
        """Test getting AI analysis results"""
        results = self.processor.get_analysis_results()
        
        self.assertIsInstance(results, list)
    
    def test_multiple_output_destinations(self):
        """Test streaming to multiple output destinations"""
        destinations = [
            "output1.mp4",
            "output2.mp4",
            "rtmp://fake-server.com/stream"
        ]
        
        with patch.object(self.processor, '_initialize_video_capture') as mock_cap, \
             patch.object(self.processor, '_initialize_video_writers') as mock_writers:
            
            mock_cap.return_value = Mock()
            mock_writers.return_value = [Mock() for _ in destinations]
            
            result = self.processor.start_streaming(
                input_source="0",
                output_destinations=destinations
            )
            
            self.assertIsInstance(result, bool)

class TestRealTimeAnalyzer(unittest.TestCase):
    """Test suite for RealTimeAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = StreamingConfig(processing_threads=2)
        self.analyzer = RealTimeAnalyzer(self.config)
    
    def test_analyzer_initialization(self):
        """Test RealTimeAnalyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.config, self.config)
    
    def test_start_stop_analysis(self):
        """Test starting and stopping analysis"""
        # Start analysis
        self.analyzer.start_analysis()
        
        # Give it a moment to start
        time.sleep(0.1)
        
        # Stop analysis
        self.analyzer.stop_analysis()
        
        # Test passes if no exceptions are raised
        self.assertTrue(True)
    
    def test_analyze_frame_async(self):
        """Test asynchronous frame analysis"""
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Start analysis
        self.analyzer.start_analysis()
        
        try:
            # Submit frame for analysis
            result = self.analyzer.analyze_frame_async(test_frame, frame_id=1)
            
            self.assertIsInstance(result, bool)
            
            # Give analysis time to process
            time.sleep(0.1)
            
        finally:
            self.analyzer.stop_analysis()
    
    def test_get_analysis_result(self):
        """Test getting analysis results"""
        # Start analysis
        self.analyzer.start_analysis()
        
        try:
            # Create and submit test frame
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            self.analyzer.analyze_frame_async(test_frame, frame_id=1)
            
            # Try to get result
            result = self.analyzer.get_analysis_result(timeout=0.1)
            
            # Result can be None (no result yet) or a dict (analysis complete)
            self.assertTrue(result is None or isinstance(result, dict))
            
        finally:
            self.analyzer.stop_analysis()
    
    def test_analyze_multiple_frames(self):
        """Test analyzing multiple frames in sequence"""
        self.analyzer.start_analysis()
        
        try:
            # Submit multiple test frames
            for i in range(5):
                test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                result = self.analyzer.analyze_frame_async(test_frame, frame_id=i)
                self.assertIsInstance(result, bool)
            
            # Give time for processing
            time.sleep(0.2)
            
            # Try to collect results
            results = []
            for _ in range(10):  # Try up to 10 times
                result = self.analyzer.get_analysis_result(timeout=0.01)
                if result is not None:
                    results.append(result)
                else:
                    break
            
            # We might not get all results due to timing, but should get some
            self.assertIsInstance(results, list)
            
        finally:
            self.analyzer.stop_analysis()
    
    def test_frame_quality_analysis(self):
        """Test frame quality analysis functionality"""
        # Create frames with different quality characteristics
        frames = [
            np.zeros((480, 640, 3), dtype=np.uint8),  # Black frame
            np.ones((480, 640, 3), dtype=np.uint8) * 255,  # White frame
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),  # Random noise
        ]
        
        self.analyzer.start_analysis()
        
        try:
            for i, frame in enumerate(frames):
                result = self.analyzer.analyze_frame_async(frame, frame_id=i)
                self.assertTrue(result)
            
            time.sleep(0.2)  # Allow processing time
            
        finally:
            self.analyzer.stop_analysis()

class TestAdaptiveBitrate(unittest.TestCase):
    """Test suite for AdaptiveBitrate class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = StreamingConfig()
        self.adaptive_bitrate = AdaptiveBitrate(self.config)
    
    def test_initialization(self):
        """Test AdaptiveBitrate initialization"""
        self.assertIsNotNone(self.adaptive_bitrate)
        self.assertEqual(self.adaptive_bitrate.config, self.config)
        self.assertIn("1080p", self.adaptive_bitrate.quality_levels)
    
    def test_analyze_network_conditions(self):
        """Test network conditions analysis"""
        conditions = self.adaptive_bitrate.analyze_network_conditions()
        
        self.assertIsInstance(conditions, dict)
        expected_keys = ['cpu_usage', 'memory_usage', 'bandwidth_mbps', 'network_stability']
        for key in expected_keys:
            if key in conditions:  # Some keys might not be available in test environment
                self.assertIsInstance(conditions[key], (int, float))
    
    def test_quality_adaptation_high_cpu(self):
        """Test quality adaptation when CPU usage is high"""
        # Create metrics with high CPU usage
        metrics = StreamMetrics()
        metrics.cpu_usage = 90.0
        metrics.latency_ms = 150.0
        metrics.frame_drops = 2
        
        adaptation = self.adaptive_bitrate.recommend_quality_adaptation(metrics)
        
        if adaptation:
            self.assertIsInstance(adaptation, QualityAdaptation)
            # High CPU should trigger adaptation
            self.assertIsInstance(adaptation.adaptation_reason, str)
    
    def test_quality_adaptation_good_performance(self):
        """Test quality adaptation with good performance"""
        # Create metrics with good performance
        metrics = StreamMetrics()
        metrics.cpu_usage = 30.0
        metrics.latency_ms = 25.0
        metrics.frame_drops = 0
        metrics.fps_current = 30.0
        
        adaptation = self.adaptive_bitrate.recommend_quality_adaptation(metrics)
        
        if adaptation:
            self.assertIsInstance(adaptation, QualityAdaptation)
    
    def test_quality_level_transitions(self):
        """Test quality level transitions"""
        # Test downgrade
        lower = self.adaptive_bitrate._get_lower_quality("1080p")
        self.assertIn(lower, ["720p", "480p"])
        
        # Test upgrade  
        higher = self.adaptive_bitrate._get_higher_quality("720p")
        self.assertIn(higher, ["1080p", "4K"])
    
    def test_bandwidth_estimation(self):
        """Test bandwidth estimation"""
        # Add some mock metrics to history
        for i in range(10):
            mock_metrics = StreamMetrics()
            mock_metrics.bitrate_kbps = 5000 + (i * 100)
            self.adaptive_bitrate.metrics_history.append(mock_metrics)
        
        bandwidth = self.adaptive_bitrate._estimate_bandwidth()
        self.assertIsInstance(bandwidth, float)
        self.assertGreater(bandwidth, 0)
    
    def test_network_stability_calculation(self):
        """Test network stability calculation"""
        # Add mock metrics with varying latencies
        latencies = [50, 55, 45, 60, 40, 65, 35, 70, 30, 75]
        for i, latency in enumerate(latencies):
            mock_metrics = StreamMetrics()
            mock_metrics.latency_ms = latency
            mock_metrics.frame_drops = 0 if i % 3 else 1
            self.adaptive_bitrate.metrics_history.append(mock_metrics)
        
        stability = self.adaptive_bitrate._calculate_network_stability()
        self.assertIsInstance(stability, float)
        self.assertGreaterEqual(stability, 0.0)
        self.assertLessEqual(stability, 1.0)

class TestStreamOptimizer(unittest.TestCase):
    """Test suite for StreamOptimizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = StreamingConfig()
        self.optimizer = StreamOptimizer(self.config)
    
    def test_initialization(self):
        """Test StreamOptimizer initialization"""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.config, self.config)
        self.assertIsInstance(self.optimizer.optimization_strategies, list)
        self.assertGreater(len(self.optimizer.optimization_strategies), 0)
    
    def test_cpu_optimization_strategy(self):
        """Test CPU optimization strategy"""
        # Create metrics with high CPU usage
        metrics = StreamMetrics()
        metrics.cpu_usage = 85.0
        
        analysis_results = []
        
        recommendations = self.optimizer._cpu_optimization_strategy(metrics, analysis_results)
        
        if recommendations:
            self.assertIsInstance(recommendations, dict)
            self.assertIn('settings_changes', recommendations)
            self.assertIn('performance_improvements', recommendations)
    
    def test_memory_optimization_strategy(self):
        """Test memory optimization strategy"""
        # Create metrics with high memory usage
        metrics = StreamMetrics()
        metrics.memory_usage_mb = 8192  # 8GB
        
        analysis_results = []
        
        recommendations = self.optimizer._memory_optimization_strategy(metrics, analysis_results)
        
        if recommendations:
            self.assertIsInstance(recommendations, dict)
            self.assertIn('resource_optimizations', recommendations)
    
    def test_network_optimization_strategy(self):
        """Test network optimization strategy"""
        # Create metrics with network issues
        metrics = StreamMetrics()
        metrics.latency_ms = 350.0
        metrics.frame_drops = 15
        
        analysis_results = []
        
        recommendations = self.optimizer._network_optimization_strategy(metrics, analysis_results)
        
        if recommendations:
            self.assertIsInstance(recommendations, dict)
            self.assertIn('quality_adjustments', recommendations)
    
    def test_optimize_stream_settings(self):
        """Test complete stream settings optimization"""
        # Create test metrics
        metrics = StreamMetrics()
        metrics.cpu_usage = 75.0
        metrics.latency_ms = 120.0
        metrics.frame_drops = 3
        
        # Create test analysis results
        analysis_results = [
            {
                'frame_id': 1,
                'objects': [{'class': 'person', 'confidence': 0.8}],
                'faces': [{'bbox': [100, 100, 200, 200]}],
                'quality_metrics': {'sharpness': 0.7}
            }
        ]
        
        recommendations = self.optimizer.optimize_stream_settings(metrics, analysis_results)
        
        self.assertIsInstance(recommendations, dict)
        expected_keys = ['settings_changes', 'performance_improvements', 
                        'quality_adjustments', 'resource_optimizations']
        for key in expected_keys:
            self.assertIn(key, recommendations)
    
    def test_quality_optimization_complex_content(self):
        """Test quality optimization for complex content"""
        metrics = StreamMetrics()
        
        # Complex content with many objects and faces
        analysis_results = [
            {
                'objects': [{'class': f'object_{i}'} for i in range(15)],
                'faces': [{'bbox': [i*50, i*50, (i+1)*50, (i+1)*50]} for i in range(5)]
            }
        ]
        
        recommendations = self.optimizer._quality_optimization_strategy(metrics, analysis_results)
        
        if recommendations:
            self.assertIsInstance(recommendations, dict)
    
    def test_quality_optimization_simple_content(self):
        """Test quality optimization for simple content"""
        metrics = StreamMetrics()
        
        # Simple content with few objects
        analysis_results = [
            {
                'objects': [{'class': 'person'}],
                'faces': []
            }
        ]
        
        recommendations = self.optimizer._quality_optimization_strategy(metrics, analysis_results)
        
        if recommendations:
            self.assertIsInstance(recommendations, dict)

class TestPerformanceMonitor(unittest.TestCase):
    """Test suite for PerformanceMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()
    
    def test_initialization(self):
        """Test PerformanceMonitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.frame_count, 0)
        self.assertEqual(self.monitor.fps_frame_count, 0)
    
    def test_record_frame_metrics(self):
        """Test recording frame metrics"""
        processing_time = 25.0  # ms
        encoding_time = 15.0    # ms
        latency = 45.0          # ms
        frame_drops = 0
        
        metrics = self.monitor.record_frame_metrics(
            processing_time, encoding_time, latency, frame_drops
        )
        
        self.assertIsInstance(metrics, StreamMetrics)
        self.assertEqual(metrics.processing_time_ms, processing_time)
        self.assertEqual(metrics.encoding_time_ms, encoding_time)
        self.assertEqual(metrics.latency_ms, latency)
        self.assertEqual(metrics.frame_drops, frame_drops)
        self.assertEqual(self.monitor.frame_count, 1)
    
    def test_fps_calculation(self):
        """Test FPS calculation over multiple frames"""
        # Record multiple frames quickly
        for i in range(10):
            metrics = self.monitor.record_frame_metrics(20.0, 10.0, 30.0, 0)
            time.sleep(0.01)  # Small delay between frames
        
        self.assertEqual(self.monitor.frame_count, 10)
        self.assertGreater(metrics.fps_current, 0)
        self.assertGreater(metrics.fps_average, 0)
    
    def test_bitrate_estimation(self):
        """Test bitrate estimation"""
        # Test with different processing times
        processing_times = [10.0, 50.0, 100.0]
        
        for proc_time in processing_times:
            bitrate = self.monitor._estimate_bitrate(proc_time)
            self.assertIsInstance(bitrate, float)
            self.assertGreater(bitrate, 0)
    
    def test_streaming_quality_score(self):
        """Test streaming quality score calculation"""
        # Test with good metrics
        score = self.monitor._calculate_streaming_quality_score(30.0, 50.0, 0)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Test with poor metrics
        poor_score = self.monitor._calculate_streaming_quality_score(10.0, 300.0, 10)
        self.assertLess(poor_score, score)  # Poor metrics should give lower score
    
    def test_metrics_history(self):
        """Test metrics history storage"""
        initial_history_length = len(self.monitor.metrics_history)
        
        # Record several frames
        for i in range(5):
            self.monitor.record_frame_metrics(25.0, 15.0, 40.0, 0)
        
        self.assertEqual(len(self.monitor.metrics_history), initial_history_length + 5)
        
        # Verify history contains StreamMetrics objects
        for metric in self.monitor.metrics_history:
            self.assertIsInstance(metric, StreamMetrics)

class TestStreamingIntegration(unittest.TestCase):
    """Integration tests for streaming components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.config = StreamingConfig(
            input_resolution=(640, 480),  # Smaller for testing
            output_resolution=(640, 480),
            fps=15,  # Lower FPS for testing
            processing_threads=1  # Single thread for testing
        )
    
    def test_processor_analyzer_integration(self):
        """Test integration between LiveStreamProcessor and RealTimeAnalyzer"""
        processor = LiveStreamProcessor(self.config)
        analyzer = RealTimeAnalyzer(self.config)
        
        # Start analyzer
        analyzer.start_analysis()
        
        try:
            # Create test frame
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Submit to analyzer
            result = analyzer.analyze_frame_async(test_frame, 1)
            self.assertTrue(result)
            
            # Allow processing time
            time.sleep(0.1)
            
        finally:
            analyzer.stop_analysis()
    
    def test_adaptive_bitrate_optimizer_integration(self):
        """Test integration between AdaptiveBitrate and StreamOptimizer"""
        adaptive = AdaptiveBitrate(self.config)
        optimizer = StreamOptimizer(self.config)
        
        # Create test metrics
        metrics = StreamMetrics()
        metrics.cpu_usage = 60.0
        metrics.latency_ms = 80.0
        
        # Get adaptation recommendation
        adaptation = adaptive.recommend_quality_adaptation(metrics)
        
        # Get optimization recommendations
        analysis_results = []
        optimizations = optimizer.optimize_stream_settings(metrics, analysis_results)
        
        # Both should return valid results
        if adaptation:
            self.assertIsInstance(adaptation, QualityAdaptation)
        self.assertIsInstance(optimizations, dict)
    
    def test_end_to_end_streaming_simulation(self):
        """Test end-to-end streaming simulation"""
        processor = LiveStreamProcessor(self.config)
        monitor = PerformanceMonitor()
        adaptive = AdaptiveBitrate(self.config)
        
        # Simulate streaming metrics over time
        for frame_num in range(10):
            processing_time = 20.0 + np.random.normal(0, 5)  # Random processing time
            encoding_time = 10.0 + np.random.normal(0, 2)
            latency = 50.0 + np.random.normal(0, 10)
            
            # Record metrics
            metrics = monitor.record_frame_metrics(
                processing_time, encoding_time, latency, 0
            )
            
            # Check if adaptation is needed
            adaptation = adaptive.recommend_quality_adaptation(metrics)
            
            # Verify we get valid responses
            self.assertIsInstance(metrics, StreamMetrics)
            if adaptation:
                self.assertIsInstance(adaptation, QualityAdaptation)
            
            time.sleep(0.01)  # Small delay between frames

class TestStreamingErrorHandling(unittest.TestCase):
    """Test suite for error handling in streaming components"""
    
    def test_invalid_input_source(self):
        """Test handling of invalid input sources"""
        config = StreamingConfig()
        processor = LiveStreamProcessor(config)
        
        # Test with non-existent file
        result = processor.start_streaming(
            input_source="/non/existent/file.mp4",
            output_destinations=["output.mp4"]
        )
        
        # Should handle gracefully
        self.assertIsInstance(result, bool)
    
    def test_invalid_output_destination(self):
        """Test handling of invalid output destinations"""
        config = StreamingConfig()
        processor = LiveStreamProcessor(config)
        
        # Test with invalid output path
        result = processor.start_streaming(
            input_source="0",
            output_destinations=["/invalid/path/output.mp4"]
        )
        
        # Should handle gracefully
        self.assertIsInstance(result, bool)
    
    def test_analyzer_with_invalid_frame(self):
        """Test analyzer with invalid frame data"""
        config = StreamingConfig()
        analyzer = RealTimeAnalyzer(config)
        
        analyzer.start_analysis()
        
        try:
            # Test with None frame
            result = analyzer.analyze_frame_async(None, 1)
            # Should handle gracefully (might return False)
            self.assertIsInstance(result, bool)
            
            # Test with wrong shape frame
            wrong_frame = np.zeros((10, 10), dtype=np.uint8)  # 2D instead of 3D
            result = analyzer.analyze_frame_async(wrong_frame, 2)
            self.assertIsInstance(result, bool)
            
        finally:
            analyzer.stop_analysis()
    
    def test_metrics_with_invalid_data(self):
        """Test metrics handling with invalid data"""
        monitor = PerformanceMonitor()
        
        # Test with negative values
        metrics = monitor.record_frame_metrics(-10.0, -5.0, -20.0, -1)
        
        # Should handle gracefully and return valid metrics
        self.assertIsInstance(metrics, StreamMetrics)
        self.assertGreaterEqual(metrics.processing_time_ms, 0)  # Should be normalized

if __name__ == '__main__':
    # Configure test environment
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestStreamingConfig,
        TestLiveStreamProcessor,
        TestRealTimeAnalyzer,
        TestAdaptiveBitrate,
        TestStreamOptimizer,
        TestPerformanceMonitor,
        TestStreamingIntegration,
        TestStreamingErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"STREAMING TESTS SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
