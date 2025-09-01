"""Cache Configuration Usage Examples for IA-Influencer Agent Platform
===================================================================

Practical examples demonstrating how to use the cache configuration
system in different scenarios and deployment environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Import cache configurations
from . import (
    # Core configurations
    RedisCacheConfig,
    MemcachedConfig,
    CacheStrategiesConfig,
    
    # Management utilities
    CacheConfigurationFactory,
    CacheConfigurationManager,
    Environment,
    CacheType,
    config_manager,
    setup_cache_config,
    get_default_config,
    
    # Pre-configured bundles
    ENTERPRISE_PRODUCTION_BUNDLE,
    DEVELOPMENT_BUNDLE,
    TESTING_BUNDLE
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheUsageExamples:
    """
Collection of practical cache configuration usage examples"""
    
    @staticmethod
    def example_1_quick_setup():
        """
Example 1: Quick setup for development environment"""
        print("=== Example 1: Quick Development Setup ===")
        
        # Method 1: Auto-detection and setup
        bundle = setup_cache_config()
        print(f"Auto-configured for: {bundle.environment}")
        print(f"Cache type: {bundle.cache_type}")
        print(f"Bundle validated: {bundle.validate()}")
        
        # Method 2: Manual configuration
        dev_bundle = CacheConfigurationFactory.create_development_bundle(
            cache_type=CacheType.REDIS
        )
        print(f"\nDevelopment bundle summary:")
        summary = dev_bundle.get_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    @staticmethod
    def example_2_production_setup():
        """Example 2: Production environment with full monitoring"""
        print("\n=== Example 2: Production Setup ===")
        
        # Create enterprise production bundle
        bundle = CacheConfigurationFactory.create_production_bundle(
            cache_type=CacheType.HYBRID,
            multi_region=True
        )
        
        # Register and activate
        config_manager.register_bundle("enterprise_prod", bundle)
        config_manager.set_active_bundle("enterprise_prod")
        
        # Display configuration
        active = config_manager.get_active_bundle()
        if active:
            print("Production configuration activated:")
            print(f"  Environment: {active.environment}")
            print(f"  Cache Type: {active.cache_type}")
            print(f"  Redis Config: {'✓' if active.redis_config else '✗'}")
            print(f"  Memcached Config: {'✓' if active.memcached_config else '✗'}")
            print(f"  Distributed: {'✓' if active.distributed_config else '✗'}")
            print(f"  Monitoring: {'✓' if active.metrics_config else '✗'}")
            print(f"  Compression: {'✓' if active.compression_config else '✗'}")
    
    @staticmethod
    def example_3_redis_specific_config():
        """Example 3: Redis-specific configuration with clustering"""
        print("\n=== Example 3: Redis Clustering Configuration ===")
        
        # Get Redis configuration from bundle
        bundle = ENTERPRISE_PRODUCTION_BUNDLE
        redis_config = bundle.redis_config
        
        if redis_config:
            print("Redis Configuration Details:")
            print(f"  Host: {redis_config.host}")
            print(f"  Port: {redis_config.port}")
            print(f"  Database: {redis_config.database}")
            print(f"  SSL Enabled: {redis_config.ssl_config.enabled if redis_config.ssl_config else False}")
            print(f"  Cluster Mode: {redis_config.cluster_config.enabled if redis_config.cluster_config else False}")
            print(f"  Connection Pool Size: {redis_config.pool_config.max_connections if redis_config.pool_config else 'N/A'}")
            
            # Display cluster nodes if available
            if redis_config.cluster_config and redis_config.cluster_config.enabled:
                print("  Cluster Nodes:")
                for node in redis_config.cluster_config.nodes:
                    print(f"    - {node.host}:{node.port}")
    
    @staticmethod
    def example_4_memcached_configuration():
        """Example 4: Memcached distributed setup"""
        print("\n=== Example 4: Memcached Distributed Setup ===")
        
        bundle = ENTERPRISE_PRODUCTION_BUNDLE
        memcached_config = bundle.memcached_config
        
        if memcached_config:
            print("Memcached Configuration:")
            print(f"  Servers: {len(memcached_config.servers)}")
            for i, server in enumerate(memcached_config.servers, 1):
                print(f"    Server {i}: {server.host}:{server.port} (weight: {server.weight})")
            
            print(f"  Pool Size: {memcached_config.pool_config.pool_size}")
            print(f"  Failover: {memcached_config.failover_config.enabled}")
            print(f"  Hash Algorithm: {memcached_config.hash_config.algorithm}")
    
    @staticmethod
    def example_5_caching_strategies():
        """Example 5: Different caching strategies configuration"""
        print("\n=== Example 5: Caching Strategies ===")
        
        bundle = ENTERPRISE_PRODUCTION_BUNDLE
        strategies_config = bundle.strategies_config
        
        if strategies_config:
            print("Available Caching Strategies:")
            for strategy_name, strategy in strategies_config.strategies.items():
                print(f"  {strategy_name}:")
                print(f"    Type: {strategy.strategy_type}")
                print(f"    TTL: {strategy.ttl}s")
                print(f"    Max Size: {strategy.max_size}")
                print(f"    Async: {strategy.async_operations}")
    
    @staticmethod
    def example_6_cache_warming():
        """Example 6: Cache warming configuration"""
        print("\n=== Example 6: Cache Warming ===")
        
        bundle = ENTERPRISE_PRODUCTION_BUNDLE
        warming_config = bundle.warming_config
        
        if warming_config:
            print("Cache Warming Configuration:")
            print(f"  Enabled: {warming_config.enabled}")
            print(f"  Max Concurrent: {warming_config.max_concurrent_warmings}")
            print(f"  Batch Size: {warming_config.batch_size}")
            
            print("  Warming Rules:")
            for rule in warming_config.rules:
                print(f"    - {rule.name}: {rule.pattern}")
                print(f"      Priority: {rule.priority}, TTL: {rule.ttl}s")
    
    @staticmethod
    def example_7_metrics_monitoring():
        """Example 7: Metrics and monitoring setup"""
        print("\n=== Example 7: Metrics and Monitoring ===")
        
        bundle = ENTERPRISE_PRODUCTION_BUNDLE
        metrics_config = bundle.metrics_config
        
        if metrics_config:
            print("Metrics Configuration:")
            print(f"  Collection Interval: {metrics_config.collection_interval}s")
            print(f"  Retention Period: {metrics_config.retention_period}s")
            print(f"  Prometheus Export: {metrics_config.prometheus_config.enabled if metrics_config.prometheus_config else False}")
            
            print("  Standard Metrics:")
            for metric in metrics_config.metrics:
                print(f"    - {metric.name} ({metric.metric_type})")
            
            print("  Alert Rules:")
            for alert in metrics_config.alerts:
                print(f"    - {alert.name}: {alert.condition} (severity: {alert.severity})")
    
    @staticmethod
    def example_8_compression_setup():
        """Example 8: Compression configuration"""
        print("\n=== Example 8: Compression Setup ===")
        
        bundle = ENTERPRISE_PRODUCTION_BUNDLE
        compression_config = bundle.compression_config
        
        if compression_config:
            print("Compression Configuration:")
            print(f"  Enabled: {compression_config.enabled}")
            print(f"  Min Size Threshold: {compression_config.min_size_threshold} bytes")
            print(f"  Max Size Threshold: {compression_config.max_size_threshold} bytes")
            
            print("  Compression Profiles:")
            for profile_name, profile in compression_config.profiles.items():
                print(f"    {profile_name}:")
                print(f"      Algorithm: {profile.algorithm}")
                print(f"      Level: {profile.level}")
                print(f"      Content Types: {', '.join([ct.value for ct in profile.content_types])}")
    
    @staticmethod
    def example_9_custom_configuration():
        """Example 9: Creating custom configuration bundle"""
        print("\n=== Example 9: Custom Configuration ===")
        
        # Create custom Redis configuration
        from .redis_cache_config import RedisCacheConfig, RedisConnectionConfig
        
        custom_redis = RedisCacheConfig(
            connection_config=RedisConnectionConfig(
                host="custom-redis.example.com",
                port=6380,
                database=5,
                password="custom_password"
            )
        )
        
        # Create custom bundle
        custom_bundle = CacheConfigurationFactory.create_custom_bundle(
            environment=Environment.PRODUCTION,
            cache_type=CacheType.REDIS,
            redis_config=custom_redis
        )
        
        print("Custom Configuration Bundle:")
        print(f"  Environment: {custom_bundle.environment}")
        print(f"  Cache Type: {custom_bundle.cache_type}")
        print(f"  Custom Redis Host: {custom_bundle.redis_config.connection_config.host}")
        print(f"  Validated: {custom_bundle.validate()}")
    
    @staticmethod
    def example_10_environment_detection():
        """Example 10: Environment detection and auto-configuration"""
        print("\n=== Example 10: Environment Detection ===")
        
        # Show current environment detection
        import os
        
        print("Environment Detection:")
        print(f"  ENV var 'ENVIRONMENT': {os.getenv('ENVIRONMENT', 'not set')}")
        print(f"  Detected environment: {config_manager._detect_environment()}")
        
        # Show all registered bundles
        summary = config_manager.get_configuration_summary()
        print("\nConfiguration Manager Status:")
        print(f"  Detected Environment: {summary['detected_environment']}")
        print(f"  Registered Bundles: {summary['registered_bundles']}")
        print(f"  Active Bundle: {summary['active_bundle'] is not None}")
        print(f"  Total Bundles: {summary['total_bundles']}")
        
        # Validate all bundles
        validation_results = config_manager.validate_all_bundles()
        print("\nBundle Validation Results:")
        for bundle_name, is_valid in validation_results.items():
            print(f"  {bundle_name}: {'✓' if is_valid else '✗'}")


class AsyncCacheExamples:
    """Asynchronous cache operation examples"""
    
    @staticmethod
    async def example_async_operations():
        """
Example of asynchronous cache operations"""
        print("\n=== Async Cache Operations Example ===")
        
        # Get configuration
        bundle = get_default_config()
        
        # Simulate async cache operations
        async def simulate_cache_operation(operation: str, key: str, delay: float = 0.1):
            await asyncio.sleep(delay)  # Simulate network delay
            return f"{operation}({key}) completed"
        
        # Parallel cache operations
        tasks = [
            simulate_cache_operation("GET", "user:123"),
            simulate_cache_operation("SET", "user:123", 0.05),
            simulate_cache_operation("DEL", "user:old"),
            simulate_cache_operation("INCR", "counter:views")
        ]
        
        results = await asyncio.gather(*tasks)
        
        print("Async Operations Results:")
        for result in results:
            print(f"  - {result}")
        
        # Simulate cache warming
        print("\nCache Warming Simulation:")
        warming_tasks = []
        for i in range(5):
            task = simulate_cache_operation("WARM", f"popular_content:{i}", 0.2)
            warming_tasks.append(task)
        
        warming_results = await asyncio.gather(*warming_tasks)
        for result in warming_results:
            print(f"  - {result}")


def run_all_examples():
    """Run all configuration examples"""
    print("IA-Influencer Agent Cache Configuration Examples")
    print("=" * 60)
    
    # Synchronous examples
    examples = CacheUsageExamples()
    
    examples.example_1_quick_setup()
    examples.example_2_production_setup()
    examples.example_3_redis_specific_config()
    examples.example_4_memcached_configuration()
    examples.example_5_caching_strategies()
    examples.example_6_cache_warming()
    examples.example_7_metrics_monitoring()
    examples.example_8_compression_setup()
    examples.example_9_custom_configuration()
    examples.example_10_environment_detection()
    
    # Asynchronous examples
    async def run_async_examples():
        async_examples = AsyncCacheExamples()
        await async_examples.example_async_operations()
    
    # Run async examples
    asyncio.run(run_async_examples())
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")


if __name__ == "__main__":
    run_all_examples()
