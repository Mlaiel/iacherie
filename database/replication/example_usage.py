"""
Example Usage module
Enterprise implementation for Ainflue platform
"""

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
    ReplicationManager,
    ReplicationConfig,
    FailoverManager,
    ReplicationMonitor,
    PostgreSQLReplicationHandler,
    RedisReplicationHandler,
    MongoDBReplicationHandler,
    ElasticsearchReplicationHandler,
    FAISSReplicationHandler,
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
    """
    Example application demonstrating database replication for content creators
    """
    
    def __init__(self) -> None:
        self.config = None
        self.failover_manager = None
        self.manager = None
        self.monitor = None
        self.handlers: Dict[str, object] = {}
        self.running = False
        
    async def initialize(self) -> None:
        """Initialize the replication system"""
        try:
            logger.info("Initializing replication system for content creator platform")
            
            # Initialize basic configuration
            self.config = {
                'databases': {
                    'postgresql': {'enabled': True},
                    'redis': {'enabled': True},
                    'mongodb': {'enabled': True},
                    'elasticsearch': {'enabled': True},
                    'vector_store': {'enabled': True}
                }
            }
            
            # Initialize handlers
            await self._initialize_handlers()
            
            # Initialize components
            await self._initialize_components()
            
            logger.info("Replication system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize replication system: {e}")
            raise
    
    async def _initialize_handlers(self) -> None:
        """Initialize database handlers"""
        try:
            # PostgreSQL handler for user data and content metadata
            if self.config['databases'].get('postgresql', {}).get('enabled', False):
                self.handlers['postgresql'] = PostgreSQLReplicationHandler()
                logger.info("PostgreSQL handler initialized")
            
            # Redis handler for caching and sessions
            if self.config['databases'].get('redis', {}).get('enabled', False):
                self.handlers['redis'] = RedisReplicationHandler()
                logger.info("Redis handler initialized")
            
            # MongoDB handler for content files and analytics
            if self.config['databases'].get('mongodb', {}).get('enabled', False):
                self.handlers['mongodb'] = MongoDBReplicationHandler()
                logger.info("MongoDB handler initialized")
            
            # Elasticsearch handler for search and content discovery
            if self.config['databases'].get('elasticsearch', {}).get('enabled', False):
                self.handlers['elasticsearch'] = ElasticsearchReplicationHandler()
                logger.info("Elasticsearch handler initialized")
            
            # Vector store handler for AI/ML embeddings
            if self.config['databases'].get('vector_store', {}).get('enabled', False):
                self.handlers['vector_store'] = FAISSReplicationHandler()
                logger.info("Vector store handler initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize handlers: {e}")
            raise
    
    async def _initialize_components(self) -> None:
        """Initialize replication components"""
        try:
            # Initialize replication manager
            self.manager = ReplicationManager()
            
            # Initialize monitor for health tracking
            self.monitor = ReplicationMonitor()
            
            # Initialize failover manager
            self.failover_manager = FailoverManager(self.config)
            await self.failover_manager.initialize()
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start_replication(self) -> None:
        """Start the replication system"""
        try:
            logger.info("Starting replication system")
            
            # Start health monitoring
            if self.failover_manager:
                await self.failover_manager.start_monitoring()
            
            self.running = True
            logger.info("Replication system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start replication system: {e}")
            raise
    
    async def stop_replication(self) -> None:
        """Stop the replication system gracefully"""
        try:
            logger.info("Stopping replication system")
            self.running = False
            
            # Stop failover manager
            if self.failover_manager:
                await self.failover_manager.stop_monitoring()
            
            logger.info("Replication system stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping replication system: {e}")
    
    async def simulate_content_creator_workflow(self) -> None:
        """Simulate typical content creator platform operations"""
        try:
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
    
    async def _simulate_user_operations(self) -> None:
        """Simulate user-related database operations"""
        logger.info("Simulating user operations across databases")
        
        # Simulate some operations
        await asyncio.sleep(1)
        logger.info("User operations simulation completed")
    
    async def _simulate_content_operations(self) -> None:
        """Simulate content-related database operations"""
        logger.info("Simulating content operations across databases")
        
        # Simulate some operations
        await asyncio.sleep(1)
        logger.info("Content operations simulation completed")
    
    async def _simulate_analytics_operations(self) -> None:
        """Simulate analytics and reporting operations"""
        # This would typically involve:
        # - Analytics data in MongoDB
        # - Aggregated metrics in PostgreSQL
        # - Real-time counters in Redis
        # - Search analytics in Elasticsearch
        
        logger.info("Simulating analytics operations across databases")
    
    async def _simulate_protection_operations(self) -> None:
        """Simulate content protection operations"""
        # This would typically involve:
        # - Fingerprint data in Vector store
        # - Protection alerts in PostgreSQL
        # - Real-time monitoring in Redis
        # - Violation logs in Elasticsearch
        
        logger.info("Simulating protection operations across databases")
    
    async def monitor_health(self) -> None:
        """Monitor system health and display metrics"""
        try:
            while self.running:
                # Get health metrics
                if self.failover_manager:
                    health_status = await self.failover_manager.get_failover_status()
                    logger.info(f"System health: {health_status}")
                
                # Wait before next check
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"Error in health monitoring: {e}")
    
    async def demonstrate_failover(self) -> None:
        """Demonstrate failover capabilities"""
        try:
            logger.info("Demonstrating failover capabilities")
            
            # Simulate primary failure
            logger.info("Simulating primary database failure...")
            
            # Trigger manual failover
            if self.failover_manager:
                success = await self.failover_manager.manual_failover('postgresql', 'postgresql_replica_1')
                logger.info(f"Manual failover result: {success}")
            
            # Wait for failover to complete
            await asyncio.sleep(10)
            
            # Check system status after failover
            if self.failover_manager:
                health_status = await self.failover_manager.get_failover_status()
                logger.info(f"System status after failover: {health_status}")
            
        except Exception as e:
            logger.error(f"Error demonstrating failover: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.stop_replication()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main() -> None:
    """Main example execution"""
    app = ReplicationExampleApp()
    
    def signal_handler(signum, frame) -> None:
        """
Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown")
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
        async def delayed_failover() -> None:
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
    """
    Example usage for IA Influencer Agent content creator platform
    
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
