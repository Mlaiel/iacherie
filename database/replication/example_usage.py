#!/usr/bin/env python3
"""Example Usage - Database Replication System
IA Influencer Agent + Content Protection Platform

This example demonstrates how to use the database replication system
for a content creator platform with multiple database backends.

WARNING: This example contains sensitive security configurations.
         DO NOT USE in production without proper security review.

Copyright (c) 2024 IA Influencer Agent Team. All rights reserved.

Unauthorized copying, modification, distribution, or use of this software
is strictly prohibited and may be subject to legal action.

Usage:
    python example_usage.py
"""
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add the backend directory to the path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from database.replication import (
    ReplicationMaster,
    ReplicationManager,
    ReplicationConfig,
    ReplicationCoordinator,
    ReplicationHealthMonitor,
    PostgreSQLReplicationHandler,
    RedisReplicationHandler,
    MongoDBReplicationHandler,
    ElasticsearchReplicationHandler,
    VectorStoreReplicationHandler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('replication_example.log')
    ]
)

logger = logging.getLogger(__name__)


class ReplicationExampleApp:
    """    Example application demonstrating database replication for content creators
    """    
    def __init__(self):
        self.config = None
        self.master = None
        self.manager = None
        self.coordinator = None
        self.health_monitor = None
        self.handlers: Dict[str, object] = {}
        self.running = False
        
    async def initialize(self):
        """Initialize the replication system"""        try:
            logger.info("Initializing replication system for content creator platform")
            
            # Load configuration
            config_path = Path(__file__).parent / "config.yml"
            self.config = ReplicationConfig.from_file(str(config_path))
            
            # Initialize handlers
            await self._initialize_handlers()
            
            # Initialize components
            await self._initialize_components()
            
            logger.info("Replication system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize replication system: {e}")
            raise
    
    async def _initialize_handlers(self):
        """Initialize database handlers"""        try:
            # PostgreSQL handler for user data and content metadata
            if self.config.databases.get('postgresql', {}).get('enabled', False):
                self.handlers['postgresql'] = PostgreSQLReplicationHandler(
                    config=self.config.databases['postgresql']
                )
                await self.handlers['postgresql'].initialize()
                logger.info("PostgreSQL handler initialized")
            
            # Redis handler for caching and sessions
            if self.config.databases.get('redis', {}).get('enabled', False):
                self.handlers['redis'] = RedisReplicationHandler(
                    config=self.config.databases['redis']
                )
                await self.handlers['redis'].initialize()
                logger.info("Redis handler initialized")
            
            # MongoDB handler for content files and analytics
            if self.config.databases.get('mongodb', {}).get('enabled', False):
                self.handlers['mongodb'] = MongoDBReplicationHandler(
                    config=self.config.databases['mongodb']
                )
                await self.handlers['mongodb'].initialize()
                logger.info("MongoDB handler initialized")
            
            # Elasticsearch handler for search and content discovery
            if self.config.databases.get('elasticsearch', {}).get('enabled', False):
                self.handlers['elasticsearch'] = ElasticsearchReplicationHandler(
                    config=self.config.databases['elasticsearch']
                )
                await self.handlers['elasticsearch'].initialize()
                logger.info("Elasticsearch handler initialized")
            
            # Vector store handler for AI/ML embeddings
            if self.config.databases.get('vector_store', {}).get('enabled', False):
                self.handlers['vector_store'] = VectorStoreReplicationHandler(
                    config=self.config.databases['vector_store']
                )
                await self.handlers['vector_store'].initialize()
                logger.info("Vector store handler initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize handlers: {e}")
            raise
    
    async def _initialize_components(self):
        """Initialize replication components"""        try:
            # Initialize replication manager
            self.manager = ReplicationManager(config=self.config)
            
            # Register handlers with manager
            for name, handler in self.handlers.items():
                await self.manager.register_handler(name, handler)
            
            # Initialize coordinator for cross-database sync
            self.coordinator = ReplicationCoordinator(
                config=self.config,
                handlers=self.handlers
            )
            
            # Initialize health monitor
            self.health_monitor = ReplicationHealthMonitor(
                config=self.config,
                handlers=self.handlers
            )
            
            # Initialize master orchestrator
            self.master = ReplicationMaster(
                config=self.config,
                manager=self.manager,
                coordinator=self.coordinator,
                health_monitor=self.health_monitor
            )
            
            await self.master.initialize()
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start_replication(self):
        """Start the replication system"""        try:
            logger.info("Starting replication system")
            
            # Start health monitoring
            await self.health_monitor.start_monitoring()
            
            # Start replication master
            await self.master.start()
            
            # Start coordinator
            await self.coordinator.start()
            
            self.running = True
            logger.info("Replication system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start replication system: {e}")
            raise
    
    async def stop_replication(self):
        """Stop the replication system gracefully"""        try:
            logger.info("Stopping replication system")
            self.running = False
            
            # Stop components in reverse order
            if self.coordinator:
                await self.coordinator.stop()
            
            if self.master:
                await self.master.stop()
            
            if self.health_monitor:
                await self.health_monitor.stop_monitoring()
            
            # Stop handlers
            for name, handler in self.handlers.items():
                if hasattr(handler, 'stop'):
                    await handler.stop()
            
            logger.info("Replication system stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping replication system: {e}")
    
    async def simulate_content_creator_workflow(self):
        """Simulate typical content creator platform operations"""        try:
            logger.info("Starting content creator workflow simulation")
            
            # Simulate user registration and profile creation
            await self._simulate_user_operations()
            
            # Simulate content upload and metadata storage
            await self._simulate_content_operations()
            
            # Simulate analytics and reporting
            await self._simulate_analytics_operations()
            
            # Simulate content protection and monitoring
            await self._simulate_protection_operations()
            
            logger.info("Content creator workflow simulation completed")
            
        except Exception as e:
            logger.error(f"Error in workflow simulation: {e}")
    
    async def _simulate_user_operations(self):
        """Simulate user-related database operations"""        # This would typically involve:
        # - User registration data in PostgreSQL
        # - Session data in Redis
        # - Profile documents in MongoDB
        # - User search indexing in Elasticsearch
        
        logger.info("Simulating user operations across databases")
        
        # Check replication lag after user operations
        lag_info = await self.coordinator.check_replication_lag()
        logger.info(f"Replication lag after user operations: {lag_info}")
    
    async def _simulate_content_operations(self):
        """Simulate content-related database operations"""        # This would typically involve:
        # - Content metadata in PostgreSQL
        # - Content files in MongoDB GridFS
        # - Content search in Elasticsearch
        # - Content embeddings in Vector store
        
        logger.info("Simulating content operations across databases")
        
        # Check sync status after content operations
        sync_status = await self.coordinator.get_sync_status()
        logger.info(f"Sync status after content operations: {sync_status}")
    
    async def _simulate_analytics_operations(self):
        """Simulate analytics and reporting operations"""        # This would typically involve:
        # - Analytics data in MongoDB
        # - Aggregated metrics in PostgreSQL
        # - Real-time counters in Redis
        # - Search analytics in Elasticsearch
        
        logger.info("Simulating analytics operations across databases")
    
    async def _simulate_protection_operations(self):
        """Simulate content protection operations"""        # This would typically involve:
        # - Fingerprint data in Vector store
        # - Protection alerts in PostgreSQL
        # - Real-time monitoring in Redis
        # - Violation logs in Elasticsearch
        
        logger.info("Simulating protection operations across databases")
    
    async def monitor_health(self):
        """Monitor system health and display metrics"""        try:
            while self.running:
                # Get health metrics
                health_status = await self.health_monitor.get_health_status()
                logger.info(f"System health: {health_status}")
                
                # Check for alerts
                alerts = await self.health_monitor.get_alerts()
                if alerts:
                    logger.warning(f"Active alerts: {len(alerts)}")
                    for alert in alerts:
                        logger.warning(f"Alert: {alert}")
                
                # Wait before next check
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"Error in health monitoring: {e}")
    
    async def demonstrate_failover(self):
        """Demonstrate failover capabilities"""        try:
            logger.info("Demonstrating failover capabilities")
            
            # Simulate primary failure
            logger.info("Simulating primary database failure...")
            
            # Trigger failover
            if self.master:
                await self.master.trigger_failover('postgresql')
                logger.info("Failover triggered for PostgreSQL")
            
            # Wait for failover to complete
            await asyncio.sleep(10)
            
            # Check system status after failover
            health_status = await self.health_monitor.get_health_status()
            logger.info(f"System status after failover: {health_status}")
            
        except Exception as e:
            logger.error(f"Error demonstrating failover: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""        try:
            await self.stop_replication()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main example execution"""    app = ReplicationExampleApp()
    
    def signal_handler(signum, frame):
        """Handle shutdown signals"""        logger.info(f"Received signal {signum}, initiating shutdown")
        asyncio.create_task(app.cleanup())
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the system
        await app.initialize()
        
        # Start replication
        await app.start_replication()
        
        # Create tasks for concurrent operations
        tasks = [
            # Monitor health continuously
            asyncio.create_task(app.monitor_health()),
            
            # Simulate content creator workflows
            asyncio.create_task(app.simulate_content_creator_workflow()),
        ]
        
        # Optionally demonstrate failover after some time
        async def delayed_failover():
            await asyncio.sleep(60)  # Wait 1 minute
            await app.demonstrate_failover()
        
        tasks.append(asyncio.create_task(delayed_failover()))
        
        # Run all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await app.cleanup()


if __name__ == "__main__":
    """    Example usage for IA Influencer Agent content creator platform
    
    This example demonstrates:
    1. Setting up multi-database replication
    2. Handling content creator workflows
    3. Monitoring system health
    4. Demonstrating failover capabilities
    5. Managing cross-database synchronization
    
    Requirements:
    - PostgreSQL with replication configured
    - Redis with Sentinel setup
    - MongoDB replica set
    - Elasticsearch cluster
    - Vector store (FAISS or Pinecone)
    
    Environment variables required:
    - DB_ENCRYPTION_KEY: Database encryption key
    - POSTGRESQL_PASSWORD: PostgreSQL password
    - REDIS_PASSWORD: Redis password
    - MONGODB_PASSWORD: MongoDB password
    - ELASTICSEARCH_PASSWORD: Elasticsearch password
    - VECTOR_STORE_API_KEY: Vector store API key
    """    
    # Check required environment variables
    required_env_vars = [
        'DB_ENCRYPTION_KEY',
        'POSTGRESQL_PASSWORD',
        'REDIS_PASSWORD',
        'MONGODB_PASSWORD',
        'ELASTICSEARCH_PASSWORD'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run the example
    asyncio.run(main())
