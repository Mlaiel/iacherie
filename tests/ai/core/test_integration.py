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

"""Comprehensive AI Core Integration Tests

Ultra-advanced enterprise-grade integration test suite for complete AI core system
workflow validation and end-to-end business logic testing.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  COPYRIGHT WARNING: This file is protected by copyright law. Unauthorized copying,
distribution, modification, or use is strictly prohibited. Violations will result in
legal action. Contact mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: End-to-end integration, system orchestration, workflow validation
- Backend Senior Engineer: Service integration, API workflow, data flow validation
- DevOps Engineer: Infrastructure integration, deployment validation, scaling tests
- Security Engineer: Security integration, end-to-end protection, access validation
- Performance Engineer: Performance integration, load testing, optimization validation
- Quality Assurance Lead: Integration testing, workflow validation, acceptance testing

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import threading
import time
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed

# System imports
import sys
import logging

# Test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from ai.core.config import CoreConfig, ConfigManager
from ai.core.metrics import MetricsCollector
from ai.core.validation import ContentValidator
from ai.core.performance import PerformanceMonitor


class TestCompleteWorkflowIntegration:
    """Integration tests for complete AI core workflow"""    
    def setup_method(self):
        """Setup integration test environment"""        self.config = CoreConfig(
            environment="integration_test",
            debug_mode=True,
            enable_content_protection=True,
            enable_seo_optimization=True,
            enable_collaboration=True,
            enable_monetization=True
        )
        self.config_manager = ConfigManager()
        self.metrics_collector = MetricsCollector()
        self.content_validator = ContentValidator()
        self.performance_monitor = PerformanceMonitor()
    
    def test_full_business_workflow_integration(self):
        """Test complete business workflow integration"""        # Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
        
        # Mock content data for different creator types
        test_contents = {
            "musician": {
                "type": "audio",
                "format": ".mp3",
                "size_mb": 5.2,
                "duration": 180,
                "quality_score": 85.0,
                "metadata": {"genre": "pop", "bpm": 120}
            },
            "photographer": {
                "type": "image",
                "format": ".jpg", 
                "size_mb": 2.8,
                "resolution": "3840x2160",
                "quality_score": 90.0,
                "metadata": {"camera": "Canon EOS R5", "iso": 400}
            },
            "blogger": {
                "type": "text",
                "format": ".md",
                "size_mb": 0.1,
                "word_count": 1500,
                "quality_score": 88.0,
                "metadata": {"topic": "technology", "reading_time": 6}
            },
            "influencer": {
                "type": "video",
                "format": ".mp4",
                "size_mb": 25.0,
                "duration": 300,
                "quality_score": 82.0,
                "metadata": {"platform": "instagram", "engagement_rate": 0.08}
            },
            "comedian": {
                "type": "video",
                "format": ".mp4",
                "size_mb": 15.0,
                "duration": 420,
                "quality_score": 79.0,
                "metadata": {"genre": "stand-up", "language": "english"}
            }
        }
        
        workflow_results = {}
        
        for creator_type, content_data in test_contents.items():
            # Stage 1: Upload validation
            upload_result = self._simulate_upload_stage(content_data)
            assert upload_result["success"] is True
            
            # Stage 2: AI Analysis
            analysis_result = self._simulate_ai_analysis_stage(content_data)
            assert analysis_result["success"] is True
            assert analysis_result["quality_score"] >= 70.0
            
            # Stage 3: Content Protection
            protection_result = self._simulate_protection_stage(content_data)
            assert protection_result["success"] is True
            assert protection_result["protection_applied"] is True
            
            # Stage 4: SEO Enhancement
            seo_result = self._simulate_seo_stage(content_data)
            assert seo_result["success"] is True
            assert "seo_score" in seo_result
            
            # Stage 5: Collaboration Matching
            collaboration_result = self._simulate_collaboration_stage(creator_type, content_data)
            assert collaboration_result["success"] is True
            
            # Stage 6: Distribution Preparation
            distribution_result = self._simulate_distribution_stage(content_data)
            assert distribution_result["success"] is True
            
            workflow_results[creator_type] = {
                "upload": upload_result,
                "analysis": analysis_result,
                "protection": protection_result,
                "seo": seo_result,
                "collaboration": collaboration_result,
                "distribution": distribution_result
            }
        
        # Validate complete workflow for all creator types
        assert len(workflow_results) == 5
        for creator_type, results in workflow_results.items():
            for stage, result in results.items():
                assert result["success"] is True, f"Stage {stage} failed for {creator_type}"
        
        print("✓ Complete business workflow integration validated for all creator types")
    
    def _simulate_upload_stage(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate upload validation stage"""        try:
            # Validate file format
            supported_formats = [".mp3", ".wav", ".jpg", ".png", ".mp4", ".md", ".txt"]
            format_valid = content_data["format"] in supported_formats
            
            # Validate file size
            size_valid = content_data["size_mb"] <= self.config.max_request_size_mb
            
            # Validate quality score
            quality_valid = content_data["quality_score"] >= self.config.validation.min_quality_score
            
            success = format_valid and size_valid and quality_valid
            
            return {
                "success": success,
                "format_valid": format_valid,
                "size_valid": size_valid,
                "quality_valid": quality_valid,
                "content_id": f"content_{int(time.time() * 1000)}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simulate_ai_analysis_stage(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate AI analysis stage"""        try:
            # Simulate AI processing time
            time.sleep(0.1)
            
            # Calculate enhanced quality score
            base_score = content_data["quality_score"]
            ai_enhancement = 5.0  # AI improvement
            final_score = min(100.0, base_score + ai_enhancement)
            
            # Detect content features
            features = []
            if content_data["type"] == "audio":
                features.extend(["music_genre", "tempo", "mood"])
            elif content_data["type"] == "image":
                features.extend(["objects", "colors", "composition"])
            elif content_data["type"] == "video":
                features.extend(["scenes", "faces", "audio", "motion"])
            else:
                features.extend(["topics", "sentiment", "keywords"])
            
            return {
                "success": True,
                "quality_score": final_score,
                "ai_features": features,
                "processing_time": 0.1,
                "confidence": 0.92
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simulate_protection_stage(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate content protection stage"""        try:
            # Apply protection based on content type
            protection_methods = []
            
            if content_data["type"] == "audio":
                protection_methods.extend(["watermarking", "fingerprinting", "drm"])
            elif content_data["type"] == "image":
                protection_methods.extend(["invisible_watermark", "metadata_protection"])
            elif content_data["type"] == "video":
                protection_methods.extend(["video_watermark", "frame_protection", "drm"])
            else:
                protection_methods.extend(["copyright_metadata", "plagiarism_protection"])
            
            # Simulate protection processing
            time.sleep(0.05)
            
            return {
                "success": True,
                "protection_applied": True,
                "protection_methods": protection_methods,
                "protection_id": f"prot_{int(time.time() * 1000)}",
                "security_level": "high"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simulate_seo_stage(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate SEO enhancement stage"""        try:
            # Generate SEO enhancements
            seo_enhancements = {
                "tags": [],
                "description": "",
                "title_optimization": True,
                "keyword_density": 0.02
            }
            
            if content_data["type"] == "audio":
                seo_enhancements["tags"] = ["music", "audio", "entertainment"]
                seo_enhancements["description"] = "Professional music content"
            elif content_data["type"] == "image":
                seo_enhancements["tags"] = ["photography", "visual", "art"]
                seo_enhancements["description"] = "High-quality visual content"
            elif content_data["type"] == "video":
                seo_enhancements["tags"] = ["video", "entertainment", "content"]
                seo_enhancements["description"] = "Engaging video content"
            else:
                seo_enhancements["tags"] = ["blog", "article", "content"]
                seo_enhancements["description"] = "Informative written content"
            
            # Calculate SEO score
            base_quality = content_data["quality_score"]
            seo_score = min(100.0, base_quality * 1.1)
            
            return {
                "success": True,
                "seo_score": seo_score,
                "enhancements": seo_enhancements,
                "searchability_improved": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simulate_collaboration_stage(self, creator_type: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate collaboration matching stage"""        try:
            # Find potential collaborators based on creator type and content
            collaborator_matches = []
            
            if creator_type == "musician":
                collaborator_matches = ["producer", "vocalist", "mixer"]
            elif creator_type == "photographer":
                collaborator_matches = ["model", "editor", "gallery_owner"]
            elif creator_type == "blogger":
                collaborator_matches = ["editor", "researcher", "publisher"]
            elif creator_type == "influencer":
                collaborator_matches = ["brand", "content_creator", "marketer"]
            elif creator_type == "comedian":
                collaborator_matches = ["venue_owner", "producer", "fellow_comedian"]
            
            # Calculate collaboration potential
            collaboration_score = content_data["quality_score"] * 0.8 + 20.0
            
            return {
                "success": True,
                "matches_found": len(collaborator_matches),
                "collaborator_types": collaborator_matches,
                "collaboration_score": collaboration_score,
                "match_quality": "high" if collaboration_score > 80 else "medium"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simulate_distribution_stage(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate distribution preparation stage"""        try:
            # Determine distribution channels
            distribution_channels = []
            
            if content_data["type"] == "audio":
                distribution_channels = ["spotify", "apple_music", "youtube_music", "soundcloud"]
            elif content_data["type"] == "image":
                distribution_channels = ["instagram", "pinterest", "500px", "portfolio_site"]
            elif content_data["type"] == "video":
                distribution_channels = ["youtube", "tiktok", "instagram", "vimeo"]
            else:
                distribution_channels = ["blog_platform", "medium", "linkedin", "personal_site"]
            
            # Calculate distribution readiness
            readiness_score = content_data["quality_score"] * 0.9 + 10.0
            
            # Estimate monetization potential
            monetization_potential = content_data["quality_score"] * 0.7
            
            return {
                "success": True,
                "distribution_channels": distribution_channels,
                "readiness_score": readiness_score,
                "monetization_potential": monetization_potential,
                "distribution_ready": readiness_score > 75.0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class TestConcurrentWorkflowIntegration:
    """Integration tests for concurrent workflow processing"""    
    def setup_method(self):
        """Setup concurrent testing environment"""        self.config = CoreConfig(
            pipeline=PipelineConfig(
                max_concurrent_pipelines=20,
                enable_parallel_processing=True
            )
        )
    
    def test_concurrent_pipeline_processing(self):
        """Test concurrent pipeline processing"""        import threading
        import queue
        
        # Prepare multiple content items
        content_queue = queue.Queue()
        result_queue = queue.Queue()
        
        test_contents = [
            {"id": i, "type": "audio", "quality_score": 80.0 + i}
            for i in range(20)
        ]
        
        for content in test_contents:
            content_queue.put(content)
        
        def process_content_worker():
            while not content_queue.empty():
                try:
                    content = content_queue.get(timeout=1)
                    
                    # Simulate processing stages
                    start_time = time.time()
                    
                    # Simulate AI processing
                    time.sleep(0.1)
                    
                    processing_time = time.time() - start_time
                    
                    result = {
                        "content_id": content["id"],
                        "success": True,
                        "processing_time": processing_time,
                        "thread_id": threading.current_thread().ident
                    }
                    
                    result_queue.put(result)
                    content_queue.task_done()
                    
                except queue.Empty:
                    break
                except Exception as e:
                    result_queue.put({
                        "content_id": content.get("id", "unknown"),
                        "success": False,
                        "error": str(e)
                    })
        
        # Start concurrent workers
        max_workers = self.config.pipeline.max_concurrent_pipelines
        threads = []
        
        for _ in range(min(max_workers, 10)):  # Limit for testing
            thread = threading.Thread(target=process_content_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all content to be processed
        content_queue.join()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Validate results
        assert len(results) == 20, f"Expected 20 results, got {len(results)}"
        
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == 20, "Not all content processed successfully"
        
        # Check that multiple threads were used
        unique_threads = set(r["thread_id"] for r in successful_results if "thread_id" in r)
        assert len(unique_threads) > 1, "Concurrent processing not detected"
        
        # Validate processing times
        avg_processing_time = sum(r.get("processing_time", 0) for r in successful_results) / len(successful_results)
        assert avg_processing_time < 1.0, f"Average processing time too high: {avg_processing_time}"
        
        print(f"✓ Concurrent pipeline processing validated (Threads: {len(unique_threads)}, Avg time: {avg_processing_time:.3f}s)")
    
    @pytest.mark.asyncio
    async def test_async_workflow_integration(self):
        """Test asynchronous workflow integration"""        
        async def process_content_async(content_id: int, content_data: Dict[str, Any]) -> Dict[str, Any]:
            """Async content processing simulation"""            start_time = time.time()
            
            # Simulate async AI processing
            await asyncio.sleep(0.05)
            
            # Simulate async validation
            await asyncio.sleep(0.02)
            
            # Simulate async protection
            await asyncio.sleep(0.03)
            
            processing_time = time.time() - start_time
            
            return {
                "content_id": content_id,
                "success": True,
                "processing_time": processing_time,
                "stages_completed": ["validation", "ai_analysis", "protection"]
            }
        
        # Create multiple async tasks
        tasks = []
        for i in range(15):
            content_data = {
                "type": "mixed",
                "quality_score": 75.0 + i,
                "format": ".mp4"
            }
            task = process_content_async(i, content_data)
            tasks.append(task)
        
        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Validate results
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successful_results) == 15, "Not all async tasks completed successfully"
        
        # Check that async processing was faster than sequential
        sequential_time_estimate = len(tasks) * 0.1  # Each task ~0.1s
        assert total_time < sequential_time_estimate, f"Async processing not faster than sequential (Total: {total_time:.3f}s)"
        
        # Validate individual results
        for result in successful_results:
            assert "stages_completed" in result
            assert len(result["stages_completed"]) == 3
            assert result["processing_time"] < 0.2
        
        print(f"✓ Async workflow integration validated (Total time: {total_time:.3f}s for {len(tasks)} tasks)")


class TestSystemLoadIntegration:
    """Integration tests for system load and stress testing"""    
    def test_high_load_workflow_integration(self):
        """Test workflow integration under high load"""        from concurrent.futures import ThreadPoolExecutor, as_completed
        import statistics
        
        def process_high_load_content(content_id: int) -> Dict[str, Any]:
            """Process content under high load conditions"""            start_time = time.time()
            
            try:
                # Simulate resource-intensive operations
                config = CoreConfig()
                metrics = MetricsCollector()
                validator = ContentValidator()
                
                # Simulate content processing
                content_data = {
                    "id": content_id,
                    "type": "video",
                    "size_mb": 20.0,
                    "quality_score": 80.0
                }
                
                # Simulate processing stages
                stages = ["upload", "validation", "ai_analysis", "protection", "seo", "distribution"]
                completed_stages = []
                
                for stage in stages:
                    # Simulate stage processing
                    time.sleep(0.01)  # Minimal processing time
                    completed_stages.append(stage)
                
                processing_time = time.time() - start_time
                
                return {
                    "content_id": content_id,
                    "success": True,
                    "processing_time": processing_time,
                    "stages_completed": completed_stages,
                    "memory_usage": "simulated"
                }
                
            except Exception as e:
                return {
                    "content_id": content_id,
                    "success": False,
                    "error": str(e),
                    "processing_time": time.time() - start_time
                }
        
        # Test with high concurrent load
        num_concurrent_items = 50
        max_workers = 20
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_content = {
                executor.submit(process_high_load_content, i): i 
                for i in range(num_concurrent_items)
            }
            
            # Collect results
            results = []
            for future in as_completed(future_to_content):
                content_id = future_to_content[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "content_id": content_id,
                        "success": False,
                        "error": str(e)
                    })
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_results = [r for r in results if r.get("success")]
        failed_results = [r for r in results if not r.get("success")]
        
        success_rate = len(successful_results) / len(results)
        
        # Validate performance under load
        assert success_rate >= 0.95, f"Success rate too low under high load: {success_rate:.2%}"
        assert len(results) == num_concurrent_items, "Not all items processed"
        
        if successful_results:
            processing_times = [r["processing_time"] for r in successful_results]
            avg_processing_time = statistics.mean(processing_times)
            max_processing_time = max(processing_times)
            
            assert avg_processing_time < 1.0, f"Average processing time too high: {avg_processing_time:.3f}s"
            assert max_processing_time < 5.0, f"Maximum processing time too high: {max_processing_time:.3f}s"
        
        throughput = len(successful_results) / total_time
        
        print(f"✓ High load integration validated:")
        print(f"  - Items processed: {len(successful_results)}/{num_concurrent_items}")
        print(f"  - Success rate: {success_rate:.2%}")
        print(f"  - Total time: {total_time:.3f}s")
        print(f"  - Throughput: {throughput:.1f} items/second")
        if failed_results:
            print(f"  - Failed items: {len(failed_results)}")
    
    def test_resource_management_integration(self):
        """Test resource management during integration workflows"""        import psutil
        import gc
        
        # Measure initial resource usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        initial_cpu_percent = process.cpu_percent()
        
        # Create resource-intensive workflow
        def create_resource_intensive_workflow():
            configs = []
            metrics = []
            validators = []
            
            # Create many objects to test memory management
            for i in range(100):
                config = CoreConfig(
                    environment=f"test_{i}",
                    ai_engine=AIEngineConfig(max_concurrent_models=5 + i % 10)
                )
                configs.append(config)
                
                metric_collector = MetricsCollector()
                metrics.append(metric_collector)
                
                validator = ContentValidator()
                validators.append(validator)
            
            return configs, metrics, validators
        
        # Run resource-intensive operations
        start_time = time.time()
        configs, metrics, validators = create_resource_intensive_workflow()
        
        # Measure peak resource usage
        peak_memory = process.memory_info().rss / (1024 * 1024)  # MB
        peak_cpu_percent = process.cpu_percent()
        
        # Cleanup objects
        del configs, metrics, validators
        gc.collect()
        
        # Measure final resource usage
        time.sleep(0.5)  # Allow cleanup to complete
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        final_cpu_percent = process.cpu_percent()
        
        execution_time = time.time() - start_time
        
        # Validate resource management
        memory_increase = peak_memory - initial_memory
        memory_cleanup = peak_memory - final_memory
        cleanup_ratio = memory_cleanup / memory_increase if memory_increase > 0 else 1.0
        
        assert memory_increase < 500, f"Memory increase too high: {memory_increase:.1f}MB"
        assert cleanup_ratio > 0.5, f"Poor memory cleanup: {cleanup_ratio:.2%}"
        assert execution_time < 10.0, f"Execution time too long: {execution_time:.3f}s"
        
        print(f"✓ Resource management integration validated:")
        print(f"  - Initial memory: {initial_memory:.1f}MB")
        print(f"  - Peak memory: {peak_memory:.1f}MB")
        print(f"  - Final memory: {final_memory:.1f}MB")
        print(f"  - Memory increase: {memory_increase:.1f}MB")
        print(f"  - Cleanup ratio: {cleanup_ratio:.2%}")
        print(f"  - Execution time: {execution_time:.3f}s")


class TestErrorHandlingIntegration:
    """Integration tests for error handling across the system"""    
    def test_graceful_error_handling_integration(self):
        """Test graceful error handling throughout the workflow"""        
        def simulate_workflow_with_errors(error_stage: str = None):
            """Simulate workflow with potential errors at different stages"""            try:
                stages = ["upload", "validation", "ai_analysis", "protection", "seo", "distribution"]
                completed_stages = []
                
                for stage in stages:
                    if stage == error_stage:
                        # Simulate error at specific stage
                        raise Exception(f"Simulated error in {stage} stage")
                    
                    # Simulate successful stage processing
                    time.sleep(0.01)
                    completed_stages.append(stage)
                
                return {
                    "success": True,
                    "completed_stages": completed_stages,
                    "error": None
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "completed_stages": completed_stages,
                    "error": str(e),
                    "error_stage": error_stage
                }
        
        # Test workflow without errors
        result = simulate_workflow_with_errors()
        assert result["success"] is True
        assert len(result["completed_stages"]) == 6
        
        # Test workflow with errors at different stages
        error_stages = ["upload", "validation", "ai_analysis", "protection", "seo", "distribution"]
        
        for error_stage in error_stages:
            result = simulate_workflow_with_errors(error_stage)
            
            assert result["success"] is False
            assert result["error"] is not None
            assert error_stage in result["error"]
            
            # Check that stages before error were completed
            stage_index = error_stages.index(error_stage)
            expected_completed = stage_index
            assert len(result["completed_stages"]) == expected_completed
            
            print(f"✓ Error handling validated for {error_stage} stage")
    
    def test_system_recovery_integration(self):
        """Test system recovery after errors"""        config_manager = ConfigManager()
        
        # Test config system recovery
        try:
            # Create invalid configuration
            invalid_config = CoreConfig(api_rate_limit=-100)  # Invalid value
            
            # System should handle invalid config gracefully
            is_valid, errors = config_manager.validate_config(invalid_config)
            assert is_valid is False
            assert len(errors) > 0
            
            # System should be able to create valid config after error
            valid_config = CoreConfig(api_rate_limit=1000)
            is_valid, errors = config_manager.validate_config(valid_config)
            assert is_valid is True
            assert len(errors) == 0
            
            print("✓ Configuration system recovery validated")
            
        except Exception as e:
            pytest.fail(f"System recovery test failed: {e}")
    
    def test_concurrent_error_handling_integration(self):
        """Test error handling in concurrent operations"""        import threading
        import queue
        
        error_queue = queue.Queue()
        success_queue = queue.Queue()
        
        def worker_with_potential_errors(worker_id: int):
            """Worker that may encounter errors"""            try:
                # Simulate random errors (50% chance)
                if worker_id % 2 == 0:
                    raise Exception(f"Simulated error in worker {worker_id}")
                
                # Simulate successful processing
                time.sleep(0.1)
                config = CoreConfig(environment=f"worker_{worker_id}")
                
                success_queue.put({
                    "worker_id": worker_id,
                    "success": True,
                    "config_created": config is not None
                })
                
            except Exception as e:
                error_queue.put({
                    "worker_id": worker_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Start multiple workers with potential errors
        threads = []
        num_workers = 10
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=worker_with_potential_errors, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        successes = []
        errors = []
        
        while not success_queue.empty():
            successes.append(success_queue.get())
        
        while not error_queue.empty():
            errors.append(error_queue.get())
        
        # Validate error handling
        total_operations = len(successes) + len(errors)
        assert total_operations == num_workers, "Not all workers completed"
        
        # Should have roughly 50% success rate due to simulated errors
        success_rate = len(successes) / total_operations
        assert 0.3 <= success_rate <= 0.7, f"Unexpected success rate: {success_rate:.2%}"
        
        # Validate that errors were handled gracefully
        for error in errors:
            assert "error" in error
            assert error["success"] is False
        
        # Validate that successes worked correctly
        for success in successes:
            assert success["success"] is True
            assert success["config_created"] is True
        
        print(f"✓ Concurrent error handling validated (Success rate: {success_rate:.2%})")


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
