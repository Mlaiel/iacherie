"""Connection Pool Manager - IA Influencer Agent Platform

Manages connection pooling across all database systems:
- Dynamic pool sizing based on load
- Connection lifecycle management
- Load balancing and distribution
- Pool health monitoring and optimization
- Resource allocation and cleanup
- Performance tuning and metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics

from .metrics import ConnectionMetrics


class PoolType(Enum):
    """Connection pool types"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"
    OBJECT_STORAGE = "object_storage"


@dataclass
class PoolConfig:
    """Connection pool configuration"""
    min_size: int = 5
    max_size: int = 50
    idle_timeout: int = 300  # seconds
    max_lifetime: int = 3600  # seconds
    health_check_interval: int = 30  # seconds
    auto_scaling: bool = True
    scale_up_threshold: float = 0.8  # 80% usage
    scale_down_threshold: float = 0.3  # 30% usage
    scale_increment: int = 5


class ConnectionPoolManager:
    """
    Central connection pool manager for all database systems.
    
    Provides:
    - Dynamic pool sizing based on load patterns
    - Connection health monitoring and cleanup
    - Load balancing across multiple connections
    - Performance optimization and tuning
    - Resource utilization tracking
    - Automatic failover support
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pool configurations
        self.pool_configs: Dict[str, PoolConfig] = {}
        self.handlers: Dict[str, Any] = {}
        
        # Pool metrics
        self.metrics = ConnectionMetrics()
        self.pool_stats: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Load tracking
        self.load_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.history_window = timedelta(minutes=15)
    
    async def initialize(self, handlers: Dict[str, Any]) -> None:
        """Initialize pool manager with database handlers"""
        self.handlers = handlers
        
        # Initialize default configurations
        for db_type in handlers.keys():
            self.pool_configs[db_type] = PoolConfig()
            self.pool_stats[db_type] = {
                "current_size": 0,
                "active_connections": 0,
                "idle_connections": 0,
                "total_created": 0,
                "total_destroyed": 0,
                "average_usage": 0.0,
                "peak_usage": 0.0,
                "last_scaled": None
            }
            self.load_history[db_type] = []
        
        # Start monitoring
        await self.start_monitoring()
        
        self.logger.info("Connection pool manager initialized")
    
    async def start_monitoring(self) -> None:
        """Start pool monitoring and auto-scaling"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started connection pool monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop pool monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped connection pool monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for pool management"""
        while self.monitoring_active:
            try:
                # Update pool statistics
                await self._update_pool_stats()
                
                # Perform auto-scaling if enabled
                await self._auto_scale_pools()
                
                # Clean up idle connections
                await self._cleanup_idle_connections()
                
                # Update load history
                await self._update_load_history()
                
                # Wait for next iteration
                await asyncio.sleep(30)  # 30 second monitoring interval
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Pool monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _update_pool_stats(self) -> None:
        """Update statistics for all connection pools"""
        for db_type, handler in self.handlers.items():
            try:
                # Get pool metrics from handler
                if hasattr(handler, 'get_pool_stats'):
                    stats = await handler.get_pool_stats()
                    self.pool_stats[db_type].update(stats)
                elif hasattr(handler, 'pool'):
                    # Extract stats from connection pool directly
                    pool = handler.pool
                    if pool:
                        self.pool_stats[db_type].update({
                            "current_size": pool.get_size() if hasattr(pool, 'get_size') else 0,
                            "idle_connections": pool.get_idle_size() if hasattr(pool, 'get_idle_size') else 0
                        })
                
                # Calculate derived metrics
                stats = self.pool_stats[db_type]
                current_size = stats.get("current_size", 0)
                idle = stats.get("idle_connections", 0)
                
                if current_size > 0:
                    stats["active_connections"] = current_size - idle
                    usage_ratio = (current_size - idle) / current_size
                    stats["average_usage"] = usage_ratio
                    
                    if usage_ratio > stats.get("peak_usage", 0):
                        stats["peak_usage"] = usage_ratio
                
            except Exception as e:
                self.logger.error(f"Failed to update pool stats for {db_type}: {e}")
    
    async def _auto_scale_pools(self) -> None:
        """Automatically scale connection pools based on usage"""
        for db_type, config in self.pool_configs.items():
            if not config.auto_scaling:
                continue
            
            try:
                stats = self.pool_stats[db_type]
                current_size = stats.get("current_size", 0)
                usage_ratio = stats.get("average_usage", 0.0)
                
                # Check if scaling is needed
                should_scale_up = (usage_ratio > config.scale_up_threshold and 
                                 current_size < config.max_size)
                should_scale_down = (usage_ratio < config.scale_down_threshold and 
                                   current_size > config.min_size)
                
                if should_scale_up:
                    await self._scale_pool_up(db_type, config)
                elif should_scale_down:
                    await self._scale_pool_down(db_type, config)
                
            except Exception as e:
                self.logger.error(f"Auto-scaling failed for {db_type}: {e}")
    
    async def _scale_pool_up(self, db_type: str, config: PoolConfig) -> None:
        """Scale up connection pool"""
        try:
            handler = self.handlers[db_type]
            stats = self.pool_stats[db_type]
            
            current_size = stats.get("current_size", 0)
            new_size = min(current_size + config.scale_increment, config.max_size)
            
            # Scale up the pool if handler supports it
            if hasattr(handler, 'scale_pool'):
                await handler.scale_pool(new_size)
                stats["current_size"] = new_size
                stats["last_scaled"] = datetime.utcnow()
                
                self.logger.info(f"Scaled up {db_type} pool from {current_size} to {new_size}")
            
        except Exception as e:
            self.logger.error(f"Failed to scale up {db_type} pool: {e}")
    
    async def _scale_pool_down(self, db_type: str, config: PoolConfig) -> None:
        """Scale down connection pool"""
        try:
            handler = self.handlers[db_type]
            stats = self.pool_stats[db_type]
            
            current_size = stats.get("current_size", 0)
            new_size = max(current_size - config.scale_increment, config.min_size)
            
            # Scale down the pool if handler supports it
            if hasattr(handler, 'scale_pool'):
                await handler.scale_pool(new_size)
                stats["current_size"] = new_size
                stats["last_scaled"] = datetime.utcnow()
                
                self.logger.info(f"Scaled down {db_type} pool from {current_size} to {new_size}")
            
        except Exception as e:
            self.logger.error(f"Failed to scale down {db_type} pool: {e}")
    
    async def _cleanup_idle_connections(self) -> None:
        """Clean up idle connections that exceed timeout"""
        for db_type, config in self.pool_configs.items():
            try:
                handler = self.handlers[db_type]
                
                # Cleanup idle connections if handler supports it
                if hasattr(handler, 'cleanup_idle_connections'):
                    cleaned = await handler.cleanup_idle_connections(config.idle_timeout)
                    if cleaned > 0:
                        self.logger.info(f"Cleaned up {cleaned} idle connections for {db_type}")
                
            except Exception as e:
                self.logger.error(f"Failed to cleanup idle connections for {db_type}: {e}")
    
    async def _update_load_history(self) -> None:
        """Update load history for trend analysis"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - self.history_window
        
        for db_type, stats in self.pool_stats.items():
            # Record current load
            usage_ratio = stats.get("average_usage", 0.0)
            self.load_history[db_type].append((current_time, usage_ratio))
            
            # Trim old history
            self.load_history[db_type] = [
                (timestamp, load) for timestamp, load in self.load_history[db_type]
                if timestamp > cutoff_time
            ]
    
    def get_pool_config(self, db_type: str) -> Optional[PoolConfig]:
        """Get pool configuration for database type"""
        return self.pool_configs.get(db_type)
    
    def set_pool_config(self, db_type: str, config: PoolConfig) -> None:
        """Set pool configuration for database type"""
        self.pool_configs[db_type] = config
        self.logger.info(f"Updated pool configuration for {db_type}")
    
    def get_pool_stats(self, db_type: Optional[str] = None) -> Dict[str, Any]:
        """Get pool statistics"""
        if db_type:
            return self.pool_stats.get(db_type, {})
        return self.pool_stats.copy()
    
    def get_load_trends(self, db_type: str, hours: int = 1) -> Dict[str, Any]:
        """Get load trends for a database type"""
        if db_type not in self.load_history:
            return {}
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        history = [
            (timestamp, load) for timestamp, load in self.load_history[db_type]
            if timestamp > cutoff_time
        ]
        
        if not history:
            return {}
        
        loads = [load for _, load in history]
        
        return {
            "average_load": statistics.mean(loads),
            "peak_load": max(loads),
            "min_load": min(loads),
            "median_load": statistics.median(loads),
            "data_points": len(loads),
            "time_range": {
                "start": history[0][0].isoformat(),
                "end": history[-1][0].isoformat()
            }
        }
    
    async def optimize_pool_sizes(self) -> Dict[str, Dict[str, Any]]:
        """Analyze and recommend optimal pool sizes"""
        recommendations = {}
        
        for db_type in self.pool_stats.keys():
            try:
                # Analyze load patterns
                trends = self.get_load_trends(db_type, hours=24)
                
                if not trends:
                    continue
                
                config = self.pool_configs[db_type]
                stats = self.pool_stats[db_type]
                
                # Calculate recommendations
                avg_load = trends.get("average_load", 0.0)
                peak_load = trends.get("peak_load", 0.0)
                
                # Recommended pool size based on load patterns
                current_size = stats.get("current_size", config.min_size)
                
                # Calculate optimal size (with buffer for peak loads)
                optimal_min = max(int(current_size * avg_load * 1.2), config.min_size)
                optimal_max = max(int(current_size * peak_load * 1.5), optimal_min + 10)
                
                recommendations[db_type] = {
                    "current_config": {
                        "min_size": config.min_size,
                        "max_size": config.max_size,
                        "current_size": current_size
                    },
                    "recommended_config": {
                        "min_size": optimal_min,
                        "max_size": optimal_max
                    },
                    "load_analysis": trends,
                    "efficiency_score": self._calculate_efficiency_score(stats, trends)
                }
                
            except Exception as e:
                self.logger.error(f"Failed to optimize pool size for {db_type}: {e}")
        
        return recommendations
    
    def _calculate_efficiency_score(self, stats: Dict[str, Any], trends: Dict[str, Any]) -> float:
        """Calculate pool efficiency score (0-100)"""
        try:
            avg_usage = trends.get("average_load", 0.0)
            peak_usage = trends.get("peak_load", 0.0)
            
            # Ideal usage is around 60-80%
            usage_score = 100 - abs(avg_usage - 0.7) * 100
            
            # Penalty for too much variation (inefficient sizing)
            variation = peak_usage - avg_usage
            variation_penalty = min(variation * 50, 30)
            
            score = max(usage_score - variation_penalty, 0)
            return min(score, 100)
            
        except Exception:
            return 0.0
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pool manager metrics"""
        total_connections = sum(
            stats.get("current_size", 0) 
            for stats in self.pool_stats.values()
        )
        
        total_active = sum(
            stats.get("active_connections", 0) 
            for stats in self.pool_stats.values()
        )
        
        return {
            "monitoring_active": self.monitoring_active,
            "total_pools": len(self.pool_stats),
            "total_connections": total_connections,
            "total_active_connections": total_active,
            "overall_utilization": (total_active / total_connections * 100) if total_connections > 0 else 0,
            "pool_stats": self.pool_stats,
            "pool_configs": {
                db_type: {
                    "min_size": config.min_size,
                    "max_size": config.max_size,
                    "auto_scaling": config.auto_scaling,
                    "scale_up_threshold": config.scale_up_threshold,
                    "scale_down_threshold": config.scale_down_threshold
                }
                for db_type, config in self.pool_configs.items()
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown connection pool manager"""
        self.logger.info("Shutting down connection pool manager...")
        
        await self.stop_monitoring()
        
        # Clear all data
        self.pool_configs.clear()
        self.handlers.clear()
        self.pool_stats.clear()
        self.load_history.clear()
        
        self.logger.info("Connection pool manager shutdown completed")
