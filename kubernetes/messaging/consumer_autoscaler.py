"""
IA Influencer Agent - Consumer Auto-Scaling System
Automatic scaling of message consumers based on queue metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from .unified_messaging import UnifiedMessagingSystem, Message
from .queue_monitor import QueueMonitor, QueueMetrics
from .messaging_config import MessagingConfig

logger = logging.getLogger(__name__)


class ScalingAction(str, Enum):
    """Scaling actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"


@dataclass
class ScalingConfig:
    """Configuration for consumer auto-scaling"""
    queue_name: str
    min_consumers: int = 1
    max_consumers: int = 10
    target_queue_depth: int = 10
    scale_up_threshold: float = 0.8  # Scale up when utilization > 80%
    scale_down_threshold: float = 0.3  # Scale down when utilization < 30%
    scale_up_cooldown: int = 60  # Don't scale up again for 1 minute
    scale_down_cooldown: int = 300  # Don't scale down again for 5 minutes
    messages_per_consumer_target: int = 20  # Target messages per consumer
    
    # Advanced scaling parameters
    aggressive_scaling: bool = False
    cpu_threshold: float = 0.8
    memory_threshold: float = 0.8
    error_rate_threshold: float = 0.1


@dataclass
class ConsumerInfo:
    """Information about a consumer"""
    consumer_id: str
    queue_name: str
    started_at: datetime
    messages_processed: int = 0
    last_activity: datetime = None
    status: str = "running"  # running, idle, stopping
    
    def __post_init__(self) -> None:
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()


@dataclass
class ScalingDecision:
    """Scaling decision with reasoning"""
    queue_name: str
    action: ScalingAction
    current_consumers: int
    target_consumers: int
    reason: str
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = None
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class ConsumerAutoScaler:
    """Automatic consumer scaling system"""
    
    def __init__(self, 
                 messaging_system -> None: UnifiedMessagingSystem, 
                 monitor -> None: QueueMonitor,
                 config -> None: Optional[MessagingConfig] = None) -> None:
        self.messaging_system = messaging_system
        self.monitor = monitor
        self.config = config or MessagingConfig.from_env()
        
        # Scaling configurations
        self.scaling_configs: Dict[str, ScalingConfig] = {}
        self.consumers: Dict[str, List[ConsumerInfo]] = {}
        self.scaling_history: Dict[str, List[ScalingDecision]] = {}
        self.last_scaling: Dict[str, datetime] = {}
        
        # Control
        self.is_running = False
        self.scaling_task: Optional[asyncio.Task] = None
        self.scaling_interval = 30  # Check every 30 seconds
        
        # Message handlers registry
        self.message_handlers: Dict[str, Callable[[Message], None]] = {}
        
        # Performance tracking
        self.consumer_performance: Dict[str, Dict[str, float]] = {}
    
    def add_scaling_config(self, scaling_config: ScalingConfig) -> None:
        """Add scaling configuration for a queue"""
        self.scaling_configs[scaling_config.queue_name] = scaling_config
        self.consumers[scaling_config.queue_name] = []
        self.scaling_history[scaling_config.queue_name] = []
        logger.info(f"Added scaling config for queue {scaling_config.queue_name}")
    
    def register_message_handler(self, queue_name: str, handler: Callable[[Message], None]) -> None:
        """Register message handler for a queue"""
        self.message_handlers[queue_name] = handler
        logger.info(f"Registered message handler for queue {queue_name}")
    
    async def start_scaling(self) -> None:
        """Start the auto-scaling system"""
        if self.is_running:
            logger.warning("Auto-scaling already running")
            return
        
        self.is_running = True
        self.scaling_task = asyncio.create_task(self._scaling_loop())
        
        # Start initial consumers
        for queue_name, config in self.scaling_configs.items():
            await self._ensure_min_consumers(queue_name, config)
        
        logger.info("Consumer auto-scaling started")
    
    async def stop_scaling(self) -> None:
        """Stop the auto-scaling system"""
        self.is_running = False
        
        if self.scaling_task:
            self.scaling_task.cancel()
            try:
                await self.scaling_task
            except asyncio.CancelledError:
                pass
        
        # Stop all consumers
        for queue_name in self.consumers:
            await self._stop_all_consumers(queue_name)
        
        logger.info("Consumer auto-scaling stopped")
    
    async def _scaling_loop(self) -> None:
        """Main scaling loop"""
        while self.is_running:
            try:
                await self._check_scaling_decisions()
                await asyncio.sleep(self.scaling_interval)
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                await asyncio.sleep(self.scaling_interval)
    
    async def _check_scaling_decisions(self) -> None:
        """Check if scaling is needed for any queue"""
        try:
            current_metrics = self.monitor.get_all_current_metrics()
            
            for queue_name, config in self.scaling_configs.items():
                if queue_name not in current_metrics:
                    continue
                
                metrics = current_metrics[queue_name]
                decision = await self._make_scaling_decision(queue_name, config, metrics)
                
                if decision.action != ScalingAction.NO_ACTION:
                    await self._execute_scaling_decision(decision)
                
        except Exception as e:
            logger.error(f"Failed to check scaling decisions: {e}")
    
    async def _make_scaling_decision(self, 
                                   queue_name: str, 
                                   config: ScalingConfig, 
                                   metrics: QueueMetrics) -> ScalingDecision:
        """Make scaling decision for a queue"""
        try:
            current_consumers = len(self.consumers.get(queue_name, []))
            
            # Check cooldowns
            now = datetime.utcnow()
            if queue_name in self.last_scaling:
                time_since_last = (now - self.last_scaling[queue_name]).total_seconds()
                
                # Get last decision to determine cooldown
                last_decision = self.scaling_history[queue_name][-1] if self.scaling_history[queue_name] else None
                if last_decision:
                    if last_decision.action == ScalingAction.SCALE_UP and time_since_last < config.scale_up_cooldown:
                        return ScalingDecision(
                            queue_name=queue_name,
                            action=ScalingAction.NO_ACTION,
                            current_consumers=current_consumers,
                            target_consumers=current_consumers,
                            reason=f"Scale up cooldown active ({time_since_last:.0f}s < {config.scale_up_cooldown}s)",
                            confidence=1.0
                        )
                    elif last_decision.action == ScalingAction.SCALE_DOWN and time_since_last < config.scale_down_cooldown:
                        return ScalingDecision(
                            queue_name=queue_name,
                            action=ScalingAction.NO_ACTION,
                            current_consumers=current_consumers,
                            target_consumers=current_consumers,
                            reason=f"Scale down cooldown active ({time_since_last:.0f}s < {config.scale_down_cooldown}s)",
                            confidence=1.0
                        )
            
            # Calculate target consumers based on queue depth
            if metrics.queue_depth == 0:
                target_consumers = config.min_consumers
                reason = "No messages in queue"
                confidence = 0.9
            else:
                # Calculate based on target messages per consumer
                target_by_depth = max(1, metrics.queue_depth // config.messages_per_consumer_target)
                
                # Calculate based on utilization
                utilization = metrics.consumer_utilization
                target_by_utilization = current_consumers
                
                if utilization > config.scale_up_threshold:
                    target_by_utilization = min(config.max_consumers, current_consumers + 1)
                    if config.aggressive_scaling:
                        target_by_utilization = min(config.max_consumers, int(current_consumers * 1.5))
                elif utilization < config.scale_down_threshold:
                    target_by_utilization = max(config.min_consumers, current_consumers - 1)
                
                # Use the more conservative target
                target_consumers = max(
                    config.min_consumers,
                    min(config.max_consumers, max(target_by_depth, target_by_utilization))
                )
                
                reason = f"Queue depth: {metrics.queue_depth}, utilization: {utilization:.2%}"
                confidence = 0.8
            
            # Check for error rate scaling down
            if metrics.error_rate > config.error_rate_threshold:
                if target_consumers > current_consumers:
                    target_consumers = current_consumers  # Don't scale up if high error rate
                    reason += f", high error rate: {metrics.error_rate:.2%}"
                    confidence = 0.6
            
            # Determine action
            if target_consumers > current_consumers:
                action = ScalingAction.SCALE_UP
            elif target_consumers < current_consumers:
                action = ScalingAction.SCALE_DOWN
            else:
                action = ScalingAction.NO_ACTION
            
            return ScalingDecision(
                queue_name=queue_name,
                action=action,
                current_consumers=current_consumers,
                target_consumers=target_consumers,
                reason=reason,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Failed to make scaling decision for {queue_name}: {e}")
            return ScalingDecision(
                queue_name=queue_name,
                action=ScalingAction.NO_ACTION,
                current_consumers=len(self.consumers.get(queue_name, [])),
                target_consumers=len(self.consumers.get(queue_name, [])),
                reason=f"Error: {e}",
                confidence=0.0
            )
    
    async def _execute_scaling_decision(self, decision: ScalingDecision) -> None:
        """Execute a scaling decision"""
        try:
            if decision.action == ScalingAction.SCALE_UP:
                consumers_to_add = decision.target_consumers - decision.current_consumers
                await self._scale_up(decision.queue_name, consumers_to_add)
            elif decision.action == ScalingAction.SCALE_DOWN:
                consumers_to_remove = decision.current_consumers - decision.target_consumers
                await self._scale_down(decision.queue_name, consumers_to_remove)
            
            # Record decision
            self.scaling_history[decision.queue_name].append(decision)
            self.last_scaling[decision.queue_name] = decision.timestamp
            
            # Keep only last 100 decisions
            if len(self.scaling_history[decision.queue_name]) > 100:
                self.scaling_history[decision.queue_name] = self.scaling_history[decision.queue_name][-100:]
            
            logger.info(f"Executed scaling decision for {decision.queue_name}: "
                       f"{decision.action.value} ({decision.current_consumers} -> {decision.target_consumers}). "
                       f"Reason: {decision.reason}")
            
        except Exception as e:
            logger.error(f"Failed to execute scaling decision: {e}")
    
    async def _scale_up(self, queue_name: str, count: int) -> None:
        """Scale up consumers for a queue"""
        try:
            handler = self.message_handlers.get(queue_name)
            if not handler:
                logger.error(f"No message handler registered for queue {queue_name}")
                return
            
            for i in range(count):
                consumer_id = f"{queue_name}-consumer-{int(time.time())}-{i}"
                consumer_info = ConsumerInfo(
                    consumer_id=consumer_id,
                    queue_name=queue_name,
                    started_at=datetime.utcnow()
                )
                
                # Start consumer
                task = asyncio.create_task(
                    self._consumer_worker(consumer_info, handler)
                )
                
                self.consumers[queue_name].append(consumer_info)
                logger.info(f"Started consumer {consumer_id} for queue {queue_name}")
            
        except Exception as e:
            logger.error(f"Failed to scale up consumers for {queue_name}: {e}")
    
    async def _scale_down(self, queue_name: str, count: int) -> None:
        """Scale down consumers for a queue"""
        try:
            consumers_list = self.consumers.get(queue_name, [])
            consumers_to_stop = consumers_list[-count:] if count <= len(consumers_list) else consumers_list
            
            for consumer_info in consumers_to_stop:
                consumer_info.status = "stopping"
                logger.info(f"Marked consumer {consumer_info.consumer_id} for stopping")
            
            # Remove from active list
            self.consumers[queue_name] = [
                c for c in consumers_list if c.status != "stopping"
            ]
            
        except Exception as e:
            logger.error(f"Failed to scale down consumers for {queue_name}: {e}")
    
    async def _consumer_worker(self, consumer_info: ConsumerInfo, handler: Callable[[Message], None]) -> None:
        """Consumer worker that processes messages"""
        logger.info(f"Consumer {consumer_info.consumer_id} started")
        
        try:
            while self.is_running and consumer_info.status == "running":
                try:
                    # Consume message
                    message = await self.messaging_system.consume(consumer_info.queue_name, timeout=1.0)
                    if not message:
                        continue
                    
                    # Update consumer activity
                    consumer_info.last_activity = datetime.utcnow()
                    
                    # Process message
                    try:
                        await handler(message)
                        await self.messaging_system.ack(message, success=True)
                        consumer_info.messages_processed += 1
                    except Exception as e:
                        logger.error(f"Message handler failed: {e}")
                        await self.messaging_system.ack(message, success=False, error=str(e))
                    
                except Exception as e:
                    logger.error(f"Consumer {consumer_info.consumer_id} error: {e}")
                    await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Consumer {consumer_info.consumer_id} crashed: {e}")
        
        finally:
            logger.info(f"Consumer {consumer_info.consumer_id} stopped. "
                       f"Processed {consumer_info.messages_processed} messages")
    
    async def _ensure_min_consumers(self, queue_name: str, config: ScalingConfig) -> None:
        """Ensure minimum number of consumers are running"""
        current_count = len(self.consumers.get(queue_name, []))
        if current_count < config.min_consumers:
            needed = config.min_consumers - current_count
            await self._scale_up(queue_name, needed)
    
    async def _stop_all_consumers(self, queue_name: str) -> None:
        """Stop all consumers for a queue"""
        consumers_list = self.consumers.get(queue_name, [])
        for consumer_info in consumers_list:
            consumer_info.status = "stopping"
        self.consumers[queue_name] = []
    
    def get_consumer_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get consumer statistics for a queue"""
        consumers_list = self.consumers.get(queue_name, [])
        
        total_processed = sum(c.messages_processed for c in consumers_list)
        active_consumers = len([c for c in consumers_list if c.status == "running"])
        
        return {
            "queue_name": queue_name,
            "active_consumers": active_consumers,
            "total_consumers": len(consumers_list),
            "total_messages_processed": total_processed,
            "consumers": [
                {
                    "consumer_id": c.consumer_id,
                    "status": c.status,
                    "started_at": c.started_at.isoformat(),
                    "messages_processed": c.messages_processed,
                    "last_activity": c.last_activity.isoformat() if c.last_activity else None
                }
                for c in consumers_list
            ]
        }
    
    def get_scaling_history(self, queue_name: str, hours: int = 24) -> List[ScalingDecision]:
        """Get scaling history for a queue"""
        if queue_name not in self.scaling_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            decision for decision in self.scaling_history[queue_name]
            if decision.timestamp >= cutoff_time
        ]