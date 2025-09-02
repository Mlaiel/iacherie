"""Caching Agent Examples and Tests

Example usage patterns and basic tests for the caching agent system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

ATTENTION: Ce code fait partie de la propriété intellectuelle de Fahed Mlaiel.
Toute reproduction, distribution, ou utilisation non autorisée est strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import json
from typing import Dict, Any

from .manager import CachingManager, CacheConfig, CachePriority
from .config import DEVELOPMENT_CONFIG, get_config_for_environment
from .utils import CacheKey, PerformanceTimer
from .exceptions import CachingAgentError


async def basic_cache_example():
    """
Demonstrate basic cache operations."""
    print("=== Basic Cache Operations Example ===")
    
    # Initialize cache manager with development config
    cache_manager = CachingManager(DEVELOPMENT_CONFIG)
    await cache_manager.initialize()
    
    try:
        # Basic set and get operations
        await cache_manager.set("user:1001", {"name": "Alice", "role": "admin"})
        user_data = await cache_manager.get("user:1001")
        print(f"Retrieved user data: {user_data}")
        
        # Cache with TTL
        await cache_manager.set(
            "session:abc123", 
            {"user_id": 1001, "expires": "2025-01-15"},
            ttl=3600  # 1 hour
        )
        
        # Cache with priority
        await cache_manager.set(
            "critical:data",
            {"important": "information"},
            priority=CachePriority.CRITICAL
        )
        
        # Bulk operations
        bulk_data = {
            "config:theme": {"dark_mode": True, "language": "en"},
            "config:notifications": {"email": True, "push": False}
        }
        await cache_manager.set_bulk(bulk_data)
        
        # Check cache statistics
        stats = await cache_manager.get_statistics()
        print(f"Cache statistics: {stats}")
        
    finally:
        await cache_manager.shutdown()


async def advanced_cache_example():
    """Demonstrate advanced cache features."""
    print("\n=== Advanced Cache Features Example ===")
    
    # Use production configuration for advanced features
    prod_config = get_config_for_environment("production")
    cache_manager = CachingManager(prod_config)
    await cache_manager.initialize()
    
    try:
        # Using structured cache keys
        audio_key = CacheKey(
            namespace="audio",
            identifier="fingerprint_123",
            content_type="audio_fingerprint",
            tenant_id="company_a"
        )
        
        audio_data = {
            "fingerprint": "af123456789...",
            "duration": 180.5,
            "artist": "John Doe",
            "title": "Sample Song"
        }
        
        with PerformanceTimer("Cache Set Operation") as timer:
            await cache_manager.set(
                audio_key.to_string(),
                audio_data,
                ttl=86400,  # 24 hours
                priority=CachePriority.CRITICAL
            )
        
        print(f"Set operation took {timer.get_duration_ms():.2f}ms")
        
        # Cache invalidation by tags
        await cache_manager.set("user:profile:1001", {"name": "Alice"}, tags=["user:1001", "profiles"])
        await cache_manager.set("user:settings:1001", {"theme": "dark"}, tags=["user:1001", "settings"])
        
        # Invalidate all data for user 1001
        await cache_manager.invalidate_by_tag("user:1001")
        
        # Performance analytics
        metrics = await cache_manager.analytics.get_performance_metrics()
        print(f"Hit rate: {metrics.hit_rate:.2%}")
        print(f"Average response time: {metrics.avg_response_time:.2f}ms")
        
    finally:
        await cache_manager.shutdown()


async def caching_strategies_example():
    """Demonstrate different caching strategies."""
    print("\n=== Caching Strategies Example ===")
    
    cache_manager = CachingManager(DEVELOPMENT_CONFIG)
    await cache_manager.initialize()
    
    try:
        # Geographic caching - cache data closer to user's location
        user_location = {"country": "Germany", "region": "Europe"}
        geographic_key = f"geo:content:{user_location['country']}"
        
        await cache_manager.set(
            geographic_key,
            {"localized_content": "German content here", "currency": "EUR"},
            content_type="geographic",
            metadata=user_location
        )
        
        # Content-aware caching - different strategies for different content types
        content_types = [
            ("audio_fingerprint", {"fingerprint_data": "audio123"}, 86400),  # 24h
            ("user_session", {"session_id": "sess123", "user_id": 1001}, 3600),  # 1h
            ("analytics_data", {"page_views": 1500, "unique_visitors": 800}, 43200),  # 12h
            ("temporary_upload", {"file_id": "temp123", "size": 1024}, 1800),  # 30m
        ]
        
        for content_type, data, ttl in content_types:
            key = f"{content_type}:example"
            await cache_manager.set(key, data, ttl=ttl, content_type=content_type)
            print(f"Cached {content_type} with {ttl}s TTL")
        
        # Adaptive caching - cache adjusts based on access patterns
        popular_key = "trending:video:123"
        for i in range(10):  # Simulate multiple accesses
            await cache_manager.get(popular_key)  # This will increase access frequency
        
        # The adaptive strategy will automatically increase TTL for popular content
        
    finally:
        await cache_manager.shutdown()


async def distributed_cache_example():
    """Demonstrate distributed cache coordination."""
    print("\n=== Distributed Cache Example ===")
    
    # This would typically be used in a multi-node environment
    config = get_config_for_environment("production")
    config.enable_distributed_coordination = True
    
    cache_manager = CachingManager(config)
    await cache_manager.initialize()
    
    try:
        # In a real scenario, multiple nodes would coordinate cache operations
        node_data = {
            "node_id": "node_001",
            "status": "active",
            "load": 0.45,
            "memory_usage": "2.1GB"
        }
        
        # This data would be automatically synchronized across nodes
        await cache_manager.set("cluster:node:001", node_data, ttl=300)
        
        # Consistency checks - ensure data is consistent across cache levels
        await cache_manager.ensure_consistency("important:data:key")
        
        print("Distributed cache operations completed")
        
    finally:
        await cache_manager.shutdown()


async def error_handling_example():
    """Demonstrate error handling and recovery."""
    print("\n=== Error Handling Example ===")
    
    cache_manager = CachingManager(DEVELOPMENT_CONFIG)
    await cache_manager.initialize()
    
    try:
        # Invalid key example
        try:
            await cache_manager.set("", {"data": "value"})  # Empty key
        except CachingAgentError as e:
            print(f"Caught expected error: {e}")
        
        # Large data example (exceeding cache limits)
        try:
            large_data = {"data": "x" * (10 * 1024 * 1024)}  # 10MB of data
            await cache_manager.set("large:data", large_data)
        except CachingAgentError as e:
            print(f"Caught capacity error: {e}")
        
        # Graceful degradation - cache failures don't break the application
        await cache_manager.set("fallback:test", {"fallback": True})
        
        # Simulate cache miss
        missing_data = await cache_manager.get("non:existent:key")
        print(f"Missing data result: {missing_data}")
        
    finally:
        await cache_manager.shutdown()


async def performance_monitoring_example():
    """Demonstrate performance monitoring and optimization."""
    print("\n=== Performance Monitoring Example ===")
    
    config = get_config_for_environment("production")
    cache_manager = CachingManager(config)
    await cache_manager.initialize()
    
    try:
        # Generate some cache activity
        for i in range(100):
            key = f"perf:test:{i % 10}"  # Create some repeated keys
            data = {"iteration": i, "timestamp": asyncio.get_event_loop().time()}
            await cache_manager.set(key, data)
            
            if i % 3 == 0:  # Get every third item
                await cache_manager.get(key)
        
        # Get performance report
        report = await cache_manager.analytics.generate_report()
        print(f"Total operations: {report.total_operations}")
        print(f"Hit rate: {report.hit_rate:.2%}")
        print(f"Cache efficiency: {report.cache_efficiency:.2%}")
        print(f"Memory usage: {report.memory_usage}")
        print(f"Top accessed keys: {report.top_keys[:5]}")
        
        # Get optimization recommendations
        recommendations = await cache_manager.optimizer.get_recommendations()
        for rec in recommendations[:3]:
            print(f"Recommendation: {rec.recommendation_type} - {rec.description}")
        
    finally:
        await cache_manager.shutdown()


async def main():
    """Run all examples."""
    examples = [
        basic_cache_example,
        advanced_cache_example,
        caching_strategies_example,
        distributed_cache_example,
        error_handling_example,
        performance_monitoring_example
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
        finally:
            print("-" * 50)


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())


# Unit test examples
class CacheTestSuite:
    """Basic test suite for cache functionality."""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def setup(self):
        """
Set up test environment."""
        config = DEVELOPMENT_CONFIG
        self.cache_manager = CachingManager(config)
        await self.cache_manager.initialize()
    
    async def teardown(self):
        try:
            logger.info(f"Executing test_basic_operations")
            
            # Implementation for test_basic_operations
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_basic_operations completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing test_bulk_operations")
            
            # Implementation for test_bulk_operations
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_bulk_operations completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_bulk_operations failed: {e}")
            raise
    async def test_bulk_operations(self):
        """Test bulk cache operations."""
        bulk_data = {
            "bulk:1": {"value": 1},
        try:
            logger.info(f"Executing test_invalidation")
            
            # Implementation for test_invalidation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_invalidation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_invalidation failed: {e}")
            raise
        await self.cache_manager.set("tagged:3", {"data": 3}, tags=["group:b"])
        
        # Invalidate by tag
        await self.cache_manager.invalidate_by_tag("group:a")
        
        # Check results
        result1 = await self.cache_manager.get("tagged:1")
        result2 = await self.cache_manager.get("tagged:2")
        result3 = await self.cache_manager.get("tagged:3")
        
        assert result1 is None
        assert result2 is None
        assert result3 == {"data": 3}
        
        print("✓ Invalidation test passed")
    
    async def run_all_tests(self):
        """Run all tests."""
        await self.setup()
        try:
            await self.test_basic_operations()
            await self.test_bulk_operations()
            await self.test_invalidation()
            print("✅ All tests passed!")
        finally:
            await self.teardown()


# Run tests if executed directly
async def run_tests():
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    """Run test suite."""
    test_suite = CacheTestSuite()
    await test_suite.run_all_tests()


# Example of integrating with the IA-Influencer-Agent platform
class IAInfluencerCacheIntegration:
    """
Integration example for IA-Influencer-Agent platform."""
    
    def __init__(self):
        self.cache_manager = None
    
    async def initialize(self):
        """
Initialize cache for IA-Influencer platform."""
        # Use audio processing configuration for this platform
        config = get_config_for_environment("audio_processing")
        self.cache_manager = CachingManager(config)
        await self.cache_manager.initialize()
    
    async def cache_audio_fingerprint(self, track_id: str, fingerprint_data: Dict[str, Any]):
        """Cache audio fingerprint for content protection."""
        key = CacheKey(
            namespace="audio",
            identifier=f"fingerprint_{track_id}",
            content_type="audio_fingerprint"
        )
        
        await self.cache_manager.set(
            key.to_string(),
            fingerprint_data,
            ttl=86400,  # 24 hours
            priority=CachePriority.CRITICAL,
            tags=[f"track:{track_id}", "audio_protection"]
        )
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any]):
        """Cache user session data."""
        key = f"user:session:{user_id}"
        
        await self.cache_manager.set(
            key,
            session_data,
            ttl=3600,  # 1 hour
            priority=CachePriority.HIGH,
            tags=[f"user:{user_id}", "sessions"]
        )
    
    async def cache_collaboration_data(self, project_id: str, collaboration_data: Dict[str, Any]):
        """Cache collaboration project data."""
        key = f"collaboration:project:{project_id}"
        
        await self.cache_manager.set(
            key,
            collaboration_data,
            ttl=7200,  # 2 hours
            priority=CachePriority.HIGH,
            tags=[f"project:{project_id}", "collaboration"]
        )
    
    async def invalidate_user_data(self, user_id: str):
        """Invalidate all cached data for a user."""
        await self.cache_manager.invalidate_by_tag(f"user:{user_id}")
    
    async def get_cache_health_report(self):
        """Get cache health and performance report."""
        return await self.cache_manager.analytics.generate_report()
