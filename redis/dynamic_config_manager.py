"""
Dynamic Configuration Manager for Redis Enterprise
Lead Dev IA Implementation - AI-Driven Configuration Optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from config.core.redis import RedisSettings

logger = logging.getLogger(__name__)

class ConfigChangeType(Enum):
    """Configuration change types"""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_UPDATE = "security_update"
    SCALING_ADJUSTMENT = "scaling_adjustment"
    MAINTENANCE_MODE = "maintenance_mode"
    FEATURE_TOGGLE = "feature_toggle"

@dataclass
class ConfigurationRule:
    """AI-driven configuration rule"""
    name: str
    condition: str
    action: Dict[str, Any]
    priority: int
    enabled: bool = True
    created_at: datetime = None
    last_applied: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ConfigurationChange:
    """Configuration change record"""
    change_id: str
    change_type: ConfigChangeType
    config_key: str
    old_value: Any
    new_value: Any
    reason: str
    applied_by: str
    applied_at: datetime
    success: bool
    rollback_available: bool = True

class DynamicConfigManager:
    """
    AI-powered dynamic configuration manager for Redis enterprise
    Lead Dev IA + ML Engineer implementation with intelligent optimization
    """
    
    def __init__(self, redis_settings: RedisSettings):
        self.redis_settings = redis_settings
        self.redis_client: Optional[redis.Redis] = None
        self.config_cache: Dict[str, Any] = {}
        self.rules: List[ConfigurationRule] = []
        self.change_history: List[ConfigurationChange] = []
        self.watchers: Dict[str, List[Callable]] = {}
        self.ai_optimizer_enabled = True
        self.config_key_prefix = "ainflue:config:"
        self.rules_key = "ainflue:config:rules"
        self.history_key = "ainflue:config:history"
        
        # AI optimization settings
        self.optimization_interval = 300  # 5 minutes
        self.performance_window = 3600   # 1 hour
        self.auto_rollback_threshold = 0.1  # 10% performance degradation
        
    async def initialize(self):
        """Initialize the dynamic configuration manager"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_settings.redis_dsn,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.redis_settings.redis_max_connections
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load existing configuration and rules
            await self._load_configuration()
            await self._load_rules()
            await self._load_change_history()
            
            # Start AI optimization task
            if self.ai_optimizer_enabled:
                asyncio.create_task(self._ai_optimization_loop())
                
            logger.info("Dynamic Configuration Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Dynamic Configuration Manager: {e}")
            raise
    
    async def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with cache support"""
        try:
            # Check cache first
            if key in self.config_cache:
                return self.config_cache[key]
                
            # Get from Redis
            redis_key = f"{self.config_key_prefix}{key}"
            value = await self.redis_client.get(redis_key)
            
            if value is not None:
                # Try to parse as JSON, fall back to string
                try:
                    parsed_value = json.loads(value)
                    self.config_cache[key] = parsed_value
                    return parsed_value
                except json.JSONDecodeError:
                    self.config_cache[key] = value
                    return value
            
            return default
            
        except Exception as e:
            logger.error(f"Error getting config key {key}: {e}")
            return default
    
    async def set_config(self, key: str, value: Any, change_type: ConfigChangeType = ConfigChangeType.FEATURE_TOGGLE, 
                        reason: str = "Manual update", applied_by: str = "system") -> bool:
        """Set configuration value with change tracking"""
        try:
            # Get old value for change tracking
            old_value = await self.get_config(key)
            
            # Store in Redis
            redis_key = f"{self.config_key_prefix}{key}"
            if isinstance(value, (dict, list)):
                redis_value = json.dumps(value)
            else:
                redis_value = str(value)
                
            await self.redis_client.set(redis_key, redis_value)
            
            # Update cache
            self.config_cache[key] = value
            
            # Record change
            change = ConfigurationChange(
                change_id=f"change_{datetime.utcnow().timestamp()}",
                change_type=change_type,
                config_key=key,
                old_value=old_value,
                new_value=value,
                reason=reason,
                applied_by=applied_by,
                applied_at=datetime.utcnow(),
                success=True
            )
            
            await self._record_change(change)
            
            # Notify watchers
            await self._notify_watchers(key, old_value, value)
            
            logger.info(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting config key {key}: {e}")
            
            # Record failed change
            change = ConfigurationChange(
                change_id=f"change_{datetime.utcnow().timestamp()}",
                change_type=change_type,
                config_key=key,
                old_value=old_value if 'old_value' in locals() else None,
                new_value=value,
                reason=reason,
                applied_by=applied_by,
                applied_at=datetime.utcnow(),
                success=False
            )
            await self._record_change(change)
            
            return False
    
    async def add_rule(self, rule: ConfigurationRule) -> bool:
        """Add AI-driven configuration rule"""
        try:
            self.rules.append(rule)
            
            # Store in Redis
            rules_data = [asdict(rule) for rule in self.rules]
            await self.redis_client.set(self.rules_key, json.dumps(rules_data, default=str))
            
            logger.info(f"Configuration rule added: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding configuration rule: {e}")
            return False
    
    async def watch_config(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Watch configuration changes"""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for AI optimization"""
        try:
            metrics = {}
            
            # Redis info
            info = await self.redis_client.info()
            metrics.update({
                'memory_used': info.get('used_memory', 0),
                'memory_peak': info.get('used_memory_peak', 0),
                'connected_clients': info.get('connected_clients', 0),
                'ops_per_second': info.get('instantaneous_ops_per_sec', 0),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)),
                'cpu_usage': info.get('used_cpu_sys', 0) + info.get('used_cpu_user', 0)
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def _ai_optimization_loop(self):
        """AI-driven optimization loop - ML Engineer implementation"""
        while True:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                # Get current performance metrics
                metrics = await self.get_performance_metrics()
                
                # Apply AI-driven rules
                for rule in self.rules:
                    if not rule.enabled:
                        continue
                        
                    try:
                        # Simple rule evaluation (can be enhanced with ML models)
                        if await self._evaluate_rule_condition(rule, metrics):
                            await self._apply_rule_action(rule)
                            rule.last_applied = datetime.utcnow()
                            rule.success_count += 1
                            
                    except Exception as e:
                        rule.failure_count += 1
                        logger.error(f"Error applying rule {rule.name}: {e}")
                
                # Performance-based auto-optimization
                await self._auto_optimize_performance(metrics)
                
            except Exception as e:
                logger.error(f"Error in AI optimization loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _evaluate_rule_condition(self, rule: ConfigurationRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate rule condition against current metrics"""
        try:
            # Simple condition evaluation - can be enhanced with ML
            condition = rule.condition.lower()
            
            if "memory_used >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get('memory_used', 0) > threshold
                
            elif "hit_rate <" in condition:
                threshold = float(condition.split("<")[1].strip())
                return metrics.get('hit_rate', 1.0) < threshold
                
            elif "ops_per_second >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return metrics.get('ops_per_second', 0) > threshold
                
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating rule condition: {e}")
            return False
    
    async def _apply_rule_action(self, rule: ConfigurationRule):
        """Apply rule action"""
        try:
            for config_key, config_value in rule.action.items():
                await self.set_config(
                    config_key, 
                    config_value, 
                    ConfigChangeType.PERFORMANCE_OPTIMIZATION,
                    f"AI rule: {rule.name}",
                    "ai_optimizer"
                )
                
        except Exception as e:
            logger.error(f"Error applying rule action: {e}")
    
    async def _auto_optimize_performance(self, metrics: Dict[str, Any]):
        """ML Engineer: Auto-optimize performance based on metrics"""
        try:
            # Memory optimization
            memory_usage_percent = metrics.get('memory_used', 0) / max(1, metrics.get('memory_peak', 1))
            
            if memory_usage_percent > 0.8:  # Over 80% memory usage
                # Increase eviction aggressiveness
                await self.set_config(
                    "redis_maxmemory_policy",
                    "allkeys-lru",
                    ConfigChangeType.PERFORMANCE_OPTIMIZATION,
                    "High memory usage detected",
                    "ai_optimizer"
                )
            
            # Connection optimization
            if metrics.get('connected_clients', 0) > 1000:
                # Increase connection timeout
                await self.set_config(
                    "redis_timeout",
                    300,
                    ConfigChangeType.PERFORMANCE_OPTIMIZATION,
                    "High client count detected",
                    "ai_optimizer"
                )
                
        except Exception as e:
            logger.error(f"Error in auto-optimization: {e}")
    
    async def _load_configuration(self):
        """Load existing configuration from Redis"""
        try:
            # Get all config keys
            pattern = f"{self.config_key_prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                config_key = key.replace(self.config_key_prefix, "")
                value = await self.redis_client.get(key)
                
                try:
                    self.config_cache[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    self.config_cache[config_key] = value
                    
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    async def _load_rules(self):
        """Load configuration rules from Redis"""
        try:
            rules_data = await self.redis_client.get(self.rules_key)
            if rules_data:
                rules_list = json.loads(rules_data)
                self.rules = [
                    ConfigurationRule(**rule_data) for rule_data in rules_list
                ]
                
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
    
    async def _load_change_history(self):
        """Load change history from Redis"""
        try:
            history_data = await self.redis_client.get(self.history_key)
            if history_data:
                history_list = json.loads(history_data)
                self.change_history = [
                    ConfigurationChange(**change_data) for change_data in history_list[-100:]  # Keep last 100
                ]
                
        except Exception as e:
            logger.error(f"Error loading change history: {e}")
    
    async def _record_change(self, change: ConfigurationChange):
        """Record configuration change"""
        try:
            self.change_history.append(change)
            
            # Keep only last 100 changes
            if len(self.change_history) > 100:
                self.change_history = self.change_history[-100:]
            
            # Store in Redis
            history_data = [asdict(change) for change in self.change_history]
            await self.redis_client.set(self.history_key, json.dumps(history_data, default=str))
            
        except Exception as e:
            logger.error(f"Error recording change: {e}")
    
    async def _notify_watchers(self, key: str, old_value: Any, new_value: Any):
        """Notify configuration watchers"""
        try:
            if key in self.watchers:
                for callback in self.watchers[key]:
                    try:
                        await callback(key, old_value, new_value)
                    except Exception as e:
                        logger.error(f"Error in watcher callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error notifying watchers: {e}")
    
    async def get_change_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get configuration change history"""
        try:
            return [asdict(change) for change in self.change_history[-limit:]]
        except Exception as e:
            logger.error(f"Error getting change history: {e}")
            return []
    
    async def rollback_change(self, change_id: str) -> bool:
        """Rollback a configuration change"""
        try:
            # Find the change
            change = next((c for c in self.change_history if c.change_id == change_id), None)
            if not change or not change.rollback_available:
                return False
            
            # Apply rollback
            return await self.set_config(
                change.config_key,
                change.old_value,
                ConfigChangeType.MAINTENANCE_MODE,
                f"Rollback of change {change_id}",
                "rollback_system"
            )
            
        except Exception as e:
            logger.error(f"Error rolling back change {change_id}: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the configuration manager"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Dynamic Configuration Manager shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_dynamic_config_manager(redis_settings: Optional[RedisSettings] = None) -> DynamicConfigManager:
    """Factory function to create and initialize DynamicConfigManager"""
    if redis_settings is None:
        redis_settings = RedisSettings()
    
    manager = DynamicConfigManager(redis_settings)
    await manager.initialize()
    return manager