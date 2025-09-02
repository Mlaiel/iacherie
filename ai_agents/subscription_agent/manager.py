"""Subscription Manager - Central Management System

Central management system for subscription operations with comprehensive
control and monitoring capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from .core.subscription_engine import SubscriptionEngine, SubscriptionStatus, SubscriptionTier

logger = logging.getLogger(__name__)

class SubscriptionSystemStatus(Enum):
    """
System status for subscription management"""

    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class SystemMetrics:
    """System metrics for subscription management"""
    total_subscriptions: int
    active_subscriptions: int
    processing_queue_size: int
    uptime: float
    last_updated: datetime

class SubscriptionManager:
    """
    Central Subscription Management System
    
    Provides comprehensive subscription management with:
    - Centralized subscription lifecycle control
    - Real-time monitoring and metrics
    - Automated billing and renewals
    - Subscription analytics and reporting
    - Integration with payment systems
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = SubscriptionSystemStatus.INITIALIZING
        self.subscription_engine = SubscriptionEngine(self.config.get('engine', {}))
        self.start_time = datetime.utcnow()
        self.metrics = SystemMetrics(
            total_subscriptions=0,
            active_subscriptions=0,
            processing_queue_size=0,
            uptime=0.0,
            last_updated=datetime.utcnow()
        )
        
    async def initialize(self) -> Dict[str, Any]:
        """
Initialize the subscription management system"""
        try:
            logger.info("Initializing Subscription Manager...")
            
            # Initialize subscription engine
            engine_result = await self.subscription_engine.initialize()
            
            # Update status
            self.status = SubscriptionSystemStatus.RUNNING
            
            # Update metrics
            await self._update_metrics()
            
            logger.info("Subscription Manager initialized successfully")
            
            return {
                "status": "initialized",
                "manager_status": self.status.value,
                "engine_result": engine_result,
                "metrics": self.metrics.__dict__
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize subscription manager: {e}")
            self.status = SubscriptionSystemStatus.ERROR
            raise
    
    async def shutdown(self):
        """Shutdown the subscription management system"""
        logger.info("Shutting down Subscription Manager...")
        
        self.status = SubscriptionSystemStatus.SHUTDOWN
        await self.subscription_engine.shutdown()
        
        logger.info("Subscription Manager shutdown complete")
    
    async def create_subscription(
        self,
        user_id: str,
        tier: str,
        billing_cycle: str = "monthly",
        trial_days: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new subscription"""
        try:
            # Convert string tier to enum
            tier_enum = SubscriptionTier(tier)
            
            result = await self.subscription_engine.create_subscription(
                user_id=user_id,
                tier=tier_enum,
                billing_cycle=billing_cycle,
                trial_days=trial_days,
                metadata=metadata
            )
            
            # Update metrics
            await self._update_metrics()
            
            return {
                "success": result.success,
                "subscription_id": result.subscription_id,
                "data": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        try:
            subscription = await self.subscription_engine.get_subscription(subscription_id)
            if subscription:
                return subscription.__dict__
            return True
            
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            return True
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a user"""
        try:
            subscriptions = await self.subscription_engine.get_user_subscriptions(user_id)
            return [sub.__dict__ for sub in subscriptions]
            
        except Exception as e:
            logger.error(f"Failed to get user subscriptions: {e}")
            return []
    
    async def update_subscription(
        self,
        subscription_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a subscription"""
        try:
            result = await self.subscription_engine.update_subscription(subscription_id, updates)
            
            return {
                "success": result.success,
                "subscription_id": result.subscription_id,
                "data": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Failed to update subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            result = await self.subscription_engine.cancel_subscription(subscription_id, immediate)
            
            # Update metrics
            await self._update_metrics()
            
            return {
                "success": result.success,
                "subscription_id": result.subscription_id,
                "data": result.data,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_billing(self, subscription_id: str) -> Dict[str, Any]:
        """Process billing for a subscription"""
        try:
            return await self.subscription_engine.process_billing(subscription_id)
            
        except Exception as e:
            logger.error(f"Failed to process billing: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get subscription analytics"""
        try:
            return await self.subscription_engine.get_subscription_analytics(user_id)
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and metrics"""
        await self._update_metrics()
        
        return {
            "status": self.status.value,
            "metrics": self.metrics.__dict__,
            "uptime_hours": (datetime.utcnow() - self.start_time).total_seconds() / 3600,
            "engine_running": self.subscription_engine.is_running
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            health_status = {
                "manager_status": self.status.value,
                "engine_running": self.subscription_engine.is_running,
                "total_subscriptions": len(self.subscription_engine.subscriptions),
                "active_jobs": len(self.subscription_engine.active_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if system is healthy
            is_healthy = (
                self.status == SubscriptionSystemStatus.RUNNING and
                self.subscription_engine.is_running
            )
            
            health_status["healthy"] = is_healthy
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Private helper methods
    async def _update_metrics(self):
        """Update system metrics"""
        try:
            self.metrics.total_subscriptions = len(self.subscription_engine.subscriptions)
            self.metrics.active_subscriptions = len([
                s for s in self.subscription_engine.subscriptions.values()
                if s.status == SubscriptionStatus.ACTIVE
            ])
            self.metrics.processing_queue_size = len(self.subscription_engine.active_jobs)
            self.metrics.uptime = (datetime.utcnow() - self.start_time).total_seconds()
            self.metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")