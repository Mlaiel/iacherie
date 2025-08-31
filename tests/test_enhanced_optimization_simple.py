# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test Enhanced Performance Optimization

Simple test for the enhanced performance optimization features
"""import pytest
import sys
import os
from pathlib import Path
import time
from datetime import datetime, timedelta
from core.enhanced_performance_optimization import (
    EnhancedPerformanceProfiler,
    PerformanceMetrics,
    AdvancedCacheStrategy,
    DatabaseIndexingOptimizer,
    OptimizationLevel,
    PerformanceStatus
)


class TestEnhancedPerformanceOptimization:
    """Test enhanced performance optimization features"""    
    def test_performance_profiler_initialization(self):
        """Test performance profiler initialization"""        config = {
            "max_history_size": 500,
            "analysis_window": 600,
            "cpu_threshold": 75.0
        }
        
        profiler = EnhancedPerformanceProfiler(config)
        
        assert profiler.config == config
        assert profiler.max_history_size == 500
        assert profiler.analysis_window == 600
        assert profiler.profiling_active is False
        assert len(profiler.metrics_history) == 0
        assert len(profiler.bottlenecks) == 0
        assert len(profiler.optimization_recommendations) == 0
    
    def test_profiler_start_stop_cycle(self):
        """Test profiler start and stop cycle"""        profiler = EnhancedPerformanceProfiler()
        
        # Test start profiling
        result = profiler.start_profiling()
        assert result is True
        assert profiler.profiling_active is True
        assert profiler.start_time is not None
        
        # Add some test metrics
        for i in range(5):
            metrics = PerformanceMetrics(
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
    
    def test_performance_metrics_recording(self):
        """Test performance metrics recording"""        profiler = EnhancedPerformanceProfiler()
        profiler.start_profiling()
        
        # Record metrics with high resource usage
        high_usage_metrics = PerformanceMetrics(
            cpu_usage=90.0,
            memory_usage=95.0,
            execution_time=8.0,
            throughput=15.0,
            error_rate=8.0
        )
        
        result = profiler.record_metrics(high_usage_metrics)
        assert result is True
        assert len(profiler.metrics_history) == 1
        
        latest_metrics = profiler.metrics_history[-1]
        assert latest_metrics.cpu_usage == 90.0
        assert latest_metrics.memory_usage == 95.0
        assert latest_metrics.execution_time == 8.0
    
    def test_bottleneck_detection(self):
        """Test bottleneck detection"""        config = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "execution_time_threshold": 5.0
        }
        
        profiler = EnhancedPerformanceProfiler(config)
        profiler.start_profiling()
        
        # Add metrics that should trigger bottleneck detection
        for i in range(10):
            metrics = PerformanceMetrics(
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
        """Test optimization recommendations generation"""        profiler = EnhancedPerformanceProfiler()
        profiler.start_profiling()
        
        # Add metrics that should generate optimization recommendations
        for i in range(10):
            metrics = PerformanceMetrics(
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
        """Test performance score calculation"""        profiler = EnhancedPerformanceProfiler()
        profiler.start_profiling()
        
        # Add metrics for good performance
        for i in range(5):
            metrics = PerformanceMetrics(
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
    
    def test_trend_analysis(self):
        """Test performance trend analysis"""        profiler = EnhancedPerformanceProfiler()
        profiler.start_profiling()
        
        # Add metrics showing increasing trend
        for i in range(10):
            metrics = PerformanceMetrics(
                cpu_usage=50.0 + i * 2,  # Increasing trend
                memory_usage=60.0 + i * 1.5,  # Increasing trend
                execution_time=1.0 + i * 0.1,  # Increasing trend
                throughput=100.0 - i * 1,  # Decreasing trend
                error_rate=0.5
            )
            profiler.record_metrics(metrics)
        
        trends = profiler._analyze_trends()
        
        assert "cpu_usage" in trends
        assert "memory_usage" in trends
        assert "execution_time" in trends
        assert "throughput" in trends
        
        # CPU, memory, and execution time should show increasing trends
        assert trends["cpu_usage"]["direction"] == "increasing"
        assert trends["memory_usage"]["direction"] == "increasing"
        assert trends["execution_time"]["direction"] == "increasing"
        
        # Throughput should show decreasing trend
        assert trends["throughput"]["direction"] == "decreasing"


class TestAdvancedCacheStrategy:
    """Test advanced cache strategy"""    
    def test_cache_strategy_initialization(self):
        """Test cache strategy initialization"""        config = {"advanced_features": True}
        cache_strategy = AdvancedCacheStrategy(config)
        
        assert cache_strategy.config == config
        assert "L1_memory" in cache_strategy.cache_layers
        assert "L2_redis" in cache_strategy.cache_layers
        assert "L3_distributed" in cache_strategy.cache_layers
        assert "L4_persistent" in cache_strategy.cache_layers
        
        # Check initial metrics
        assert cache_strategy.cache_metrics["hits"] == 0
        assert cache_strategy.cache_metrics["misses"] == 0
    
    def test_cache_strategy_recommendation(self):
        """Test cache strategy recommendation logic"""        cache_strategy = AdvancedCacheStrategy()
        
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
    
    def test_cache_performance_analysis(self):
        """Test cache performance analysis"""        cache_strategy = AdvancedCacheStrategy()
        
        # Simulate cache operations
        cache_strategy.cache_metrics = {
            "hits": 700,
            "misses": 300,
            "evictions": 50,
            "promotions": 20,
            "demotions": 10
        }
        
        analysis = cache_strategy.analyze_cache_performance()
        
        assert "performance_metrics" in analysis
        assert "optimization_recommendations" in analysis
        
        # Check performance metrics
        metrics = analysis["performance_metrics"]
        assert metrics["hit_ratio"] == 70.0  # 700/(700+300)*100
        assert metrics["total_operations"] == 1000
        assert metrics["cache_efficiency"] == "poor"  # <70% hit ratio
        
        # Should have recommendations for poor performance
        assert len(analysis["optimization_recommendations"]) > 0


class TestDatabaseIndexingOptimizer:
    """Test database indexing optimizer"""    
    def test_indexing_optimizer_initialization(self):
        """Test indexing optimizer initialization"""        config = {"auto_optimization": True}
        optimizer = DatabaseIndexingOptimizer(config)
        
        assert optimizer.config == config
        assert "btree" in optimizer.index_types
        assert "hash" in optimizer.index_types
        assert "gin" in optimizer.index_types
        assert "gist" in optimizer.index_types
    
    def test_query_performance_analysis(self):
        """Test query performance analysis"""        optimizer = DatabaseIndexingOptimizer()
        
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
    
    def test_index_optimization_recommendations(self):
        """Test index optimization recommendations"""        optimizer = DatabaseIndexingOptimizer()
        
        # Mock existing index statistics
        index_stats = [
            {
                "name": "unused_large_index",
                "usage_count": 5,
                "size_mb": 500,
                "fragmentation_percent": 15
            },
            {
                "name": "fragmented_index",
                "usage_count": 1000,
                "size_mb": 200,
                "fragmentation_percent": 45
            },
            {
                "name": "heavily_used_large_index",
                "usage_count": 5000,
                "size_mb": 2000,
                "fragmentation_percent": 20
            }
        ]
        
        optimization_plan = optimizer.optimize_existing_indexes(index_stats)
        
        assert "indexes_to_drop" in optimization_plan
        assert "indexes_to_rebuild" in optimization_plan
        assert "indexes_to_modify" in optimization_plan
        assert "maintenance_recommendations" in optimization_plan
        
        # Should recommend dropping unused large index
        assert len(optimization_plan["indexes_to_drop"]) > 0
        assert optimization_plan["indexes_to_drop"][0]["index_name"] == "unused_large_index"
        
        # Should recommend rebuilding fragmented index
        assert len(optimization_plan["indexes_to_rebuild"]) > 0
        assert optimization_plan["indexes_to_rebuild"][0]["index_name"] == "fragmented_index"
        
        # Should recommend modifying heavily used large index
        assert len(optimization_plan["indexes_to_modify"]) > 0
        assert optimization_plan["indexes_to_modify"][0]["index_name"] == "heavily_used_large_index"


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple optimization features"""    
    def test_comprehensive_performance_optimization_workflow(self):
        """Test complete performance optimization workflow"""        # Step 1: Initialize profiler
        profiler = EnhancedPerformanceProfiler({
            "max_history_size": 100,
            "cpu_threshold": 75.0,
            "memory_threshold": 80.0
        })
        
        # Step 2: Start profiling and collect data
        profiler.start_profiling()
        
        # Simulate performance degradation over time
        for i in range(20):
            metrics = PerformanceMetrics(
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
    
    def test_cache_and_database_optimization_integration(self):
        """Test integration between cache strategy and database optimization"""        # Initialize components
        cache_strategy = AdvancedCacheStrategy()
        db_optimizer = DatabaseIndexingOptimizer()
        
        # Simulate cache performance issue
        cache_strategy.cache_metrics = {
            "hits": 400,
            "misses": 600,  # Poor hit ratio
            "evictions": 200,  # High eviction rate
            "promotions": 50,
            "demotions": 30
        }
        
        # Analyze cache performance
        cache_analysis = cache_strategy.analyze_cache_performance()
        cache_hit_ratio = cache_analysis["performance_metrics"]["hit_ratio"]
        
        # If cache performance is poor, should recommend database optimization
        if cache_hit_ratio < 70:
            # Simulate database query analysis
            query_stats = {
                "avg_execution_time": 1200,  # Slow due to cache misses
                "index_usage_ratio": 0.6,
                "query_patterns": [
                    {
                        "type": "equality",
                        "columns": ["cache_key"],
                        "frequency": 200
                    }
                ]
            }
            
            db_analysis = db_optimizer.analyze_query_performance(query_stats)
            
            # Should recommend database optimizations to compensate for poor cache performance
            assert len(db_analysis["index_recommendations"]) > 0
            assert db_analysis["optimization_priority"] in ["medium", "high"]
        
        # Verify integrated recommendations
        integrated_recommendations = {
            "cache_optimization": cache_analysis["optimization_recommendations"],
            "database_optimization": db_analysis["index_recommendations"] if cache_hit_ratio < 70 else []
        }
        
        # Should have recommendations for both cache and database
        assert len(integrated_recommendations["cache_optimization"]) > 0
        if cache_hit_ratio < 70:
            assert len(integrated_recommendations["database_optimization"]) > 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])