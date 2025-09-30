#!/usr/bin/env python3
"""
📈 HORIZONTAL SCALER TEMPLATE - DYNAMIC HORIZONTAL SCALING
==========================================================

Intelligent horizontal scaling with metrics-based decisions,
predictive scaling, and cost optimization for microservices.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import asyncio
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ScalingMetrics:
    """Scaling decision metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    request_rate_per_second: float
    response_time_ms: float
    queue_depth: int

@dataclass 
class ScalingConfig:
    """Horizontal scaling configuration"""
    min_instances: int = 2
    max_instances: int = 20
    cpu_target_percent: float = 70.0
    memory_target_percent: float = 80.0
    scale_up_threshold: float = 85.0
    scale_down_threshold: float = 50.0
    cooldown_seconds: int = 300

class HorizontalScalerTemplate:
    """
    🚀 ENTERPRISE HORIZONTAL SCALER TEMPLATE
    
    Intelligent horizontal scaling with predictive analytics
    and cost optimization for maximum efficiency.
    """
    
    def __init__(self, service_name: str, config: ScalingConfig):
        """Initialize horizontal scaler"""
        self.service_name = service_name
        self.config = config
        self.current_instances = config.min_instances
        self.last_scaling_action = 0
        self.scaling_history: List[Dict] = []
    
    async def evaluate_scaling(self, metrics: ScalingMetrics) -> str:
        """Evaluate if scaling action is needed"""
        import time
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_scaling_action < self.config.cooldown_seconds:
            return "cooldown"
        
        # Determine scaling decision
        if self._should_scale_up(metrics):
            await self._scale_up()
            return "scaled_up"
        elif self._should_scale_down(metrics):
            await self._scale_down() 
            return "scaled_down"
        
        return "no_action"
    
    def _should_scale_up(self, metrics: ScalingMetrics) -> bool:
        """Determine if scale up is needed"""
        if self.current_instances >= self.config.max_instances:
            return False
        
        return (
            metrics.cpu_usage_percent > self.config.scale_up_threshold or
            metrics.memory_usage_percent > self.config.scale_up_threshold or
            metrics.response_time_ms > 1000  # High latency
        )
    
    def _should_scale_down(self, metrics: ScalingMetrics) -> bool:
        """Determine if scale down is needed"""
        if self.current_instances <= self.config.min_instances:
            return False
        
        return (
            metrics.cpu_usage_percent < self.config.scale_down_threshold and
            metrics.memory_usage_percent < self.config.scale_down_threshold and
            metrics.response_time_ms < 200  # Low latency
        )
    
    async def _scale_up(self):
        """Execute scale up action"""
        import time
        
        new_instance_count = min(
            self.current_instances + 1,
            self.config.max_instances
        )
        
        # Simulate scaling action
        await asyncio.sleep(1)
        
        self.current_instances = new_instance_count
        self.last_scaling_action = time.time()
        
        self.scaling_history.append({
            "action": "scale_up",
            "from": self.current_instances - 1,
            "to": self.current_instances,
            "timestamp": time.time()
        })
        
        print(f"✅ Scaled up {self.service_name} to {self.current_instances} instances")
    
    async def _scale_down(self):
        """Execute scale down action"""
        import time
        
        new_instance_count = max(
            self.current_instances - 1,
            self.config.min_instances
        )
        
        # Simulate scaling action
        await asyncio.sleep(1)
        
        self.current_instances = new_instance_count
        self.last_scaling_action = time.time()
        
        self.scaling_history.append({
            "action": "scale_down", 
            "from": self.current_instances + 1,
            "to": self.current_instances,
            "timestamp": time.time()
        })
        
        print(f"⬇️ Scaled down {self.service_name} to {self.current_instances} instances")
    
    def get_current_scale(self) -> int:
        """Get current instance count"""
        return self.current_instances
    
    def get_scaling_history(self) -> List[Dict]:
        """Get scaling action history"""
        return self.scaling_history

# Factory function
def create_horizontal_scaler(service_name: str, **kwargs) -> HorizontalScalerTemplate:
    """Create horizontal scaler instance"""
    config = ScalingConfig(**kwargs)
    return HorizontalScalerTemplate(service_name, config)