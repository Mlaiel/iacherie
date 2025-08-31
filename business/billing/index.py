"""Central Index for Billing Module - IA Influencer Agent
======================================================

Centralized access point for all billing system components with
industrial-grade configuration and initialization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import redis
import asyncpg
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

# Import all billing engines
from .billing_aggregator import BillingAggregatorEngine

logger = logging.getLogger(__name__)

class BillingSystemManager:
    """
    Central manager for the complete billing system providing
    unified initialization, configuration, and access to all components.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.billing_aggregator: Optional[BillingAggregatorEngine] = None
        self.is_initialized = False
    
    async def initialize(self, redis_config: Dict[str, Any], db_config: Dict[str, Any]) -> None:
        """Initialize the complete billing system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                password=redis_config.get('password'),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            
            # Test Redis connection
            await asyncio.to_thread(self.redis_client.ping)
            logger.info("Redis connection established")
            
            # Initialize database pool
            self.db_pool = await asyncpg.create_pool(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                min_size=db_config.get('min_connections', 5),
                max_size=db_config.get('max_connections', 20)
            )
            logger.info("Database pool created")
            
            # Initialize billing aggregator (which initializes all components)
            self.billing_aggregator = BillingAggregatorEngine(self.redis_client, self.db_pool)
            await self.billing_aggregator.initialize()
            
            self.is_initialized = True
            logger.info("Billing system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize billing system: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self) -> None:
        """Cleanup billing system resources"""
        try:
            if self.db_pool:
                await self.db_pool.close()
                logger.info("Database pool closed")
            
            if self.redis_client:
                await asyncio.to_thread(self.redis_client.close)
                logger.info("Redis connection closed")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_billing_aggregator(self) -> BillingAggregatorEngine:
        """Get the billing aggregator instance"""
        if not self.is_initialized or not self.billing_aggregator:
            raise RuntimeError("Billing system not initialized")
        
        return self.billing_aggregator
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get billing system status"""
        try:
            if not self.is_initialized:
                return {
                    'status': 'not_initialized',
                    'components': {}
                }
            
            # Get health status from aggregator
            health_status = await self.billing_aggregator.get_billing_health_status()
            
            return {
                'status': 'initialized',
                'health': health_status,
                'redis_connected': await asyncio.to_thread(self.redis_client.ping),
                'database_connected': bool(self.db_pool and not self.db_pool._closed)
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

# Global billing system manager instance
billing_system = BillingSystemManager()

@asynccontextmanager
async def billing_system_lifespan(app: FastAPI):
    """FastAPI lifespan context manager for billing system"""
    try:
        # Initialize billing system on startup
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
        
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'ia_influencer',
            'password': 'secure_password',
            'database': 'ia_influencer_db'
        }
        
        await billing_system.initialize(redis_config, db_config)
        
        yield
        
    finally:
        # Cleanup on shutdown
        await billing_system.cleanup()

# Convenience functions for accessing billing components
async def get_billing_aggregator() -> BillingAggregatorEngine:
    """Get billing aggregator instance"""
    return billing_system.get_billing_aggregator()

async def process_one_time_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process one-time payment"""
    aggregator = await get_billing_aggregator()
    return await aggregator.process_one_time_payment(payment_data)

async def process_subscription_billing(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process subscription billing"""
    aggregator = await get_billing_aggregator()
    return await aggregator.process_subscription_billing(subscription_data)

async def process_commission_payouts(payout_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process commission payouts"""
    aggregator = await get_billing_aggregator()
    return await aggregator.process_commission_payouts(payout_data)

async def process_royalty_distribution(distribution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process royalty distribution"""
    aggregator = await get_billing_aggregator()
    return await aggregator.process_royalty_distribution(distribution_data)

async def get_comprehensive_dashboard() -> Dict[str, Any]:
    """Get comprehensive billing dashboard"""
    aggregator = await get_billing_aggregator()
    return await aggregator.get_comprehensive_billing_dashboard()

async def get_billing_health_status() -> Dict[str, Any]:
    """Get billing system health status"""
    return await billing_system.get_system_status()

# Direct access to individual engines (for advanced use cases)
async def get_invoice_generator():
    """Get invoice generator engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.invoice_generator

async def get_payment_processor():
    """Get payment processor engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.payment_processor

async def get_commission_calculator():
    """Get commission calculator engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.commission_calculator

async def get_subscription_billing():
    """Get subscription billing engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.subscription_billing

async def get_royalty_distributor():
    """Get royalty distributor engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.royalty_distributor

async def get_tax_compliance():
    """Get tax compliance engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.tax_compliance

async def get_billing_analytics():
    """Get billing analytics engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.billing_analytics

async def get_payment_gateway():
    """Get payment gateway engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.payment_gateway

async def get_dispute_manager():
    """Get dispute manager engine"""
    aggregator = await get_billing_aggregator()
    return aggregator.dispute_manager

# Export everything for external use
__all__ = [
    'BillingSystemManager',
    'billing_system',
    'billing_system_lifespan',
    'get_billing_aggregator',
    'process_one_time_payment',
    'process_subscription_billing',
    'process_commission_payouts',
    'process_royalty_distribution',
    'get_comprehensive_dashboard',
    'get_billing_health_status',
    'get_invoice_generator',
    'get_payment_processor',
    'get_commission_calculator',
    'get_subscription_billing',
    'get_royalty_distributor',
    'get_tax_compliance',
    'get_billing_analytics',
    'get_payment_gateway',
    'get_dispute_manager'
]
