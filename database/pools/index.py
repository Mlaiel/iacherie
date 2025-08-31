#!/usr/bin/env python3
"""Database Connection Pools Index - IA Influencer Agent + Content Protection Platform

Main entry point for the database connection pools module providing
enterprise-grade connection management, monitoring, and configuration.

This index file provides quick access to all pool components and
utilities for initialization and management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the backend path to Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from database.pools import (
    # Core managers
    DatabasePoolManager,
    get_pool_manager,
    initialize_all_pools,
    
    # Configuration
    PoolConfigurationManager,
    get_configuration_manager,
    
    # Monitoring
    PoolMonitoringManager,
    get_monitoring_manager,
    
    # Pool implementations
    PostgreSQLConnectionPool,
    RedisConnectionPool,
    ElasticsearchConnectionPool,
    MongoDBConnectionPool,
    VectorStoreConnectionPool,
    ObjectStorageConnectionPool,
    CacheConnectionPool,
    
    # Data models
    PoolConfig,
    DatabaseConnectionInfo,
    DatabaseType,
    ConnectionState,
    
    # Utilities
    get_pool_summary
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""    banner = """    ╔══════════════════════════════════════════════════════════════╗
    ║                Database Connection Pools                     ║
    ║            IA Influencer Agent + Content Protection         ║
    ║                                                              ║
    ║  Enterprise-grade multi-database connection pool management  ║
    ║  with real-time monitoring and automated scaling            ║
    ║                                                              ║
    ║  Author: Fahed Mlaiel <mlaiel@live.de>                      ║
    ║  © 2025 All Rights Reserved                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """    print(banner)

async def run_health_check():
    """Run comprehensive health check on all pools"""    print("🔍 Running comprehensive pool health check...")
    
    try:
        # Get pool summary
        summary = get_pool_summary()
        print(f"\n📊 Pool Summary:")
        print(f"   Version: {summary.get('version', 'N/A')}")
        print(f"   Components: {len(summary.get('components', {}))}")
        
        # Check component availability
        print(f"\n🔧 Component Status:")
        for component, status in summary.get('components', {}).items():
            print(f"   {component}: {status}")
        
        # Get pool manager
        pool_manager = get_pool_manager()
        if pool_manager:
            print(f"\n💾 Pool Manager:")
            print(f"   Active pools: {len(pool_manager.pools)}")
            print(f"   Registered configs: {len(pool_manager.pool_configs)}")
            
            # Health check all pools
            if pool_manager.pools:
                health_results = await pool_manager.health_check_all()
                print(f"\n🏥 Pool Health Status:")
                for pool_id, is_healthy in health_results.items():
                    status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                    print(f"   {pool_id}: {status}")
        
        # Check monitoring
        try:
            monitoring = get_monitoring_manager()
            if monitoring:
                print(f"\n📈 Monitoring System:")
                print(f"   Status: ✅ Available")
                print(f"   Metrics enabled: {monitoring.metrics_enabled}")
                print(f"   Alerts enabled: {monitoring.alerts_enabled}")
        except Exception as e:
            print(f"   Status: ❌ Error - {e}")
        
        # Check configuration manager
        try:
            config_manager = get_configuration_manager()
            if config_manager:
                print(f"\n⚙️  Configuration Manager:")
                print(f"   Status: ✅ Available")
                print(f"   Security level: {config_manager.security_level.value}")
        except Exception as e:
            print(f"   Status: ❌ Error - {e}")
        
        print(f"\n✅ Health check completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def initialize_demo_pools():
    """Initialize demo pools for testing"""    print("🚀 Initializing demo pools...")
    
    try:
        # Initialize with demo configuration
        success = await initialize_all_pools(
            config_dir="config/pools/demo",
            master_key="demo-key-not-for-production"
        )
        
        if success:
            print("✅ Demo pools initialized successfully")
            
            # Show pool status
            pool_manager = get_pool_manager()
            if pool_manager.pools:
                print(f"\n📊 Initialized Pools:")
                stats = pool_manager.get_all_stats()
                for pool_id, pool_stats in stats.items():
                    print(f"   {pool_id}:")
                    print(f"     State: {pool_stats.get('state', 'Unknown')}")
                    print(f"     Type: {pool_stats.get('database_type', 'Unknown')}")
                    
        else:
            print("❌ Failed to initialize demo pools")
            
        return success
        
    except Exception as e:
        print(f"❌ Demo initialization failed: {e}")
        return False

async def run_performance_test():
    """Run basic performance test"""    print("⚡ Running performance test...")
    
    try:
        pool_manager = get_pool_manager()
        
        if not pool_manager.pools:
            print("❌ No pools available for testing")
            return False
        
        # Test each pool
        for pool_id, pool in pool_manager.pools.items():
            print(f"\n🧪 Testing pool: {pool_id}")
            
            # Health check
            start_time = asyncio.get_event_loop().time()
            is_healthy = await pool.health_check()
            health_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            print(f"   Health check: {'✅ Pass' if is_healthy else '❌ Fail'} ({health_time:.2f}ms)")
            
            # Get statistics
            stats = pool.get_stats()
            print(f"   Statistics: {len(stats)} metrics available")
        
        print(f"\n✅ Performance test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def main():
    """Main application entry point"""    print_banner()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔧 Database Connection Pools Management System")
    print("   Choose an option:")
    print("   1. Run health check")
    print("   2. Initialize demo pools")
    print("   3. Run performance test")
    print("   4. Show pool summary")
    print("   5. Exit")
    
    while True:
        try:
            choice = input("\n➤ Enter your choice (1-5): ").strip()
            
            if choice == "1":
                await run_health_check()
            elif choice == "2":
                await initialize_demo_pools()
            elif choice == "3":
                await run_performance_test()
            elif choice == "4":
                summary = get_pool_summary()
                print(f"\n📊 Pool Summary:")
                for key, value in summary.items():
                    print(f"   {key}: {value}")
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    """Run the pools management system"""    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)
