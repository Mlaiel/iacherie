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
Standalone Test for Enhanced Performance Optimization

Test the performance optimization functionality without importing core modules
"""

import pytest
import sys
import os
from pathlib import Path
import sys
import os

# Add the current directory to Python path to import the module directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the module directly
import core.enhanced_performance_optimization as perf_opt


class TestEnhancedPerformanceOptimization:
    """
Test enhanced performance optimization features"""
    
    def test_performance_profiler_initialization(self):
        """
Test performance profiler initialization"""
        config = {
            "max_history_size": 500,
            "analysis_window": 600,
            "cpu_threshold": 75.0
        }
        
        profiler = perf_opt.EnhancedPerformanceProfiler(config)
        
        assert profiler.config == config
        assert profiler.max_history_size == 500
        assert profiler.analysis_window == 600
        assert profiler.profiling_active is False
        assert len(profiler.metrics_history) == 0
        assert len(profiler.bottlenecks) == 0
        assert len(profiler.optimization_recommendations) == 0
    
    def test_profiler_start_stop_cycle(self):
        """Test profiler start and stop cycle"""
        profiler = perf_opt.EnhancedPerformanceProfiler()
        
        # Test start profiling
        result = profiler.start_profiling()
        assert result is True
        assert profiler.profiling_active is True
        assert profiler.start_time is not None
        
        # Add some test metrics
        for i in range(5):
            metrics = perf_opt.PerformanceMetrics(
                cpu_usage=50.0 + i * 5,
                memory_usage=60.0 + i * 3,
                execution_time=1.0 + i * 0.2,
                throughput=100.0 - i * 2,
                error_rate=0.5 + i * 0.1
            )
            profiler.record_metrics(metrics)
        
        assert len(profiler.metrics_history) == 5
        
        # Test stop profiling
        results = profiler.stop_profiling()
        assert profiler.profiling_active is False
        assert "profiling_duration" in results
        assert "total_measurements" in results
        assert "analysis_results" in results
        assert results["total_measurements"] == 5
    
    def test_bottleneck_detection(self):
        """Test bottleneck detection"""
        config = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "execution_time_threshold": 5.0
        }
        
        profiler = perf_opt.EnhancedPerformanceProfiler(config)
        profiler.start_profiling()
        
        # Add metrics that should trigger bottleneck detection
        for i in range(10):
            metrics = perf_opt.PerformanceMetrics(
                cpu_usage=85.0,  # Above threshold
                memory_usage=90.0,  # Above threshold
                execution_time=6.0,  # Above threshold
                throughput=20.0,
                error_rate=1.0
            )
            profiler.record_metrics(metrics)
        
        # Analyze bottlenecks
        bottlenecks = profiler._analyze_bottlenecks()
        
        assert len(bottlenecks) > 0
        
        # Should detect CPU, memory, and execution time bottlenecks
        bottleneck_types = [b["type"] for b in bottlenecks]
        assert "cpu_bottleneck" in bottleneck_types
        assert "memory_bottleneck" in bottleneck_types
        assert "execution_time_bottleneck" in bottleneck_types
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations generation"""
        profiler = perf_opt.EnhancedPerformanceProfiler()
        profiler.start_profiling()
        
        # Add metrics that should generate optimization recommendations
        for i in range(10):
            metrics = perf_opt.PerformanceMetrics(
                cpu_usage=80.0,  # High CPU usage
                memory_usage=85.0,  # High memory usage
                execution_time=3.0,  # High execution time
                throughput=30.0,  # Low throughput
                error_rate=0.5
            )
            profiler.record_metrics(metrics)
        
        # Generate recommendations
        recommendations = profiler._identify_optimizations()
        
        assert len(recommendations) > 0
        
        # Check recommendation structure
        for rec in recommendations:
            assert hasattr(rec, 'priority')
            assert hasattr(rec, 'category')
            assert hasattr(rec, 'title')
            assert hasattr(rec, 'description')
            assert hasattr(rec, 'recommendations')
            assert len(rec.recommendations) > 0
        
        # Should have CPU and memory optimization recommendations
        categories = [rec.category for rec in recommendations]
        assert "cpu_optimization" in categories
        assert "memory_optimization" in categories
    
    def test_performance_score_calculation(self):
        """Test performance score calculation"""
        profiler = perf_opt.EnhancedPerformanceProfiler()
        profiler.start_profiling()
        
        # Add metrics for good performance
        for i in range(5):
            metrics = perf_opt.PerformanceMetrics(
                cpu_usage=40.0,  # Good CPU usage
                memory_usage=50.0,  # Good memory usage
                execution_time=0.8,  # Good execution time
                throughput=150.0,  # Good throughput
                error_rate=0.1  # Low error rate
            )
            profiler.record_metrics(metrics)
        
        score_data = profiler._calculate_performance_score()
        
        assert "overall_score" in score_data
        assert "grade" in score_data
        assert "status" in score_data
        assert "component_scores" in score_data
        
        # Should have good performance score
        assert score_data["overall_score"] >= 80.0
        assert score_data["grade"] in ["A", "B"]
        assert score_data["status"] in ["excellent", "good"]


class TestAdvancedCacheStrategy:
    """Test advanced cache strategy"""
    
    def test_cache_strategy_initialization(self):
        """
Test cache strategy initialization"""
        config = {"advanced_features": True}
        cache_strategy = perf_opt.AdvancedCacheStrategy(config)
        
        assert cache_strategy.config == config
        assert "L1_memory" in cache_strategy.cache_layers
        assert "L2_redis" in cache_strategy.cache_layers
        assert "L3_distributed" in cache_strategy.cache_layers
        assert "L4_persistent" in cache_strategy.cache_layers
        
        # Check initial metrics
        assert cache_strategy.cache_metrics["hits"] == 0
        assert cache_strategy.cache_metrics["misses"] == 0
    
    def test_cache_strategy_recommendation(self):
        """Test cache strategy recommendation logic"""
        cache_strategy = perf_opt.AdvancedCacheStrategy()
        
        # Test small, high-frequency data (should go to L1)
        strategy1 = cache_strategy.get_cache_strategy("small_hot_data", 512*1024, 150)
        assert strategy1["recommended_layer"] == "L1_memory"
        assert strategy1["priority"] == "high"
        assert strategy1["should_preload"] is True
        
        # Test medium, medium-frequency data (should go to L2)
        strategy2 = cache_strategy.get_cache_strategy("medium_data", 50*1024*1024, 25)
        assert strategy2["recommended_layer"] == "L2_redis"
        assert strategy2["priority"] == "normal"
        
        # Test large data (should go to L3 or L4)
        strategy3 = cache_strategy.get_cache_strategy("large_data", 500*1024*1024, 5)
        assert strategy3["recommended_layer"] in ["L3_distributed", "L4_persistent"]
        assert strategy3["compression"] is True


class TestDatabaseIndexingOptimizer:
    """Test database indexing optimizer"""
    
    def test_indexing_optimizer_initialization(self):
        """
Test indexing optimizer initialization"""
        config = {"auto_optimization": True}
        optimizer = perf_opt.DatabaseIndexingOptimizer(config)
        
        assert optimizer.config == config
        assert "btree" in optimizer.index_types
        assert "hash" in optimizer.index_types
        assert "gin" in optimizer.index_types
        assert "gist" in optimizer.index_types
    
    def test_query_performance_analysis(self):
        """Test query performance analysis"""
        optimizer = perf_opt.DatabaseIndexingOptimizer()
        
        # Mock slow query performance
        query_stats = {
            "avg_execution_time": 2500,  # 2.5 seconds - slow
            "index_usage_ratio": 0.3,    # Low index usage
            "query_patterns": [
                {
                    "type": "equality",
                    "columns": ["user_id", "status"],
                    "frequency": 150
                },
                {
                    "type": "range",
                    "columns": ["created_date"],
                    "frequency": 80
                }
            ]
        }
        
        analysis = optimizer.analyze_query_performance(query_stats)
        
        assert "current_performance" in analysis
        assert "bottlenecks" in analysis
        assert "index_recommendations" in analysis
        assert "optimization_priority" in analysis
        
        # Should detect bottlenecks
        assert len(analysis["bottlenecks"]) > 0
        bottleneck_types = [b["type"] for b in analysis["bottlenecks"]]
        assert "slow_execution" in bottleneck_types
        assert "low_index_usage" in bottleneck_types
        
        # Should have high priority due to slow execution
        assert analysis["optimization_priority"] == "high"
        
        # Should have index recommendations
        assert len(analysis["index_recommendations"]) > 0


def test_comprehensive_workflow():
    """Test comprehensive performance optimization workflow"""
    # Step 1: Initialize profiler
    profiler = perf_opt.EnhancedPerformanceProfiler({
        "max_history_size": 100,
        "cpu_threshold": 75.0,
        "memory_threshold": 80.0
    })
    
    # Step 2: Start profiling and collect data
    profiler.start_profiling()
    
    # Simulate performance degradation over time
    for i in range(20):
        metrics = perf_opt.PerformanceMetrics(
            cpu_usage=60.0 + i * 2,  # Increasing CPU usage
            memory_usage=70.0 + i * 1.5,  # Increasing memory usage
            execution_time=1.5 + i * 0.1,  # Increasing execution time
            throughput=120.0 - i * 2,  # Decreasing throughput
            error_rate=0.2 + i * 0.05  # Increasing error rate
        )
        profiler.record_metrics(metrics)
    
    # Step 3: Analyze results
    results = profiler.stop_profiling()
    
    assert results["total_measurements"] == 20
    
    analysis = results["analysis_results"]
    assert analysis["status"] == "completed"
    
    # Should detect performance degradation trends
    trends = analysis["performance_trends"]
    assert trends["cpu_usage"]["direction"] == "increasing"
    assert trends["memory_usage"]["direction"] == "increasing"
    
    # Should identify bottlenecks
    bottlenecks = analysis["bottleneck_analysis"]
    assert len(bottlenecks) > 0
    
    # Should provide optimization recommendations
    recommendations = analysis["optimization_opportunities"]
    assert len(recommendations) > 0
    
    # Performance score should reflect degraded performance
    performance_score = analysis["performance_score"]
    assert performance_score["overall_score"] < 80.0  # Should be degraded


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])