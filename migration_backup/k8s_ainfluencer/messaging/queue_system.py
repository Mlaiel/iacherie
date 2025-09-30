"""
IA Influencer Agent - Complete Message Queue System
Integrated message queue system with all enterprise features

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from .messaging_config import MessagingConfig, get_messaging_config
from .unified_messaging import UnifiedMessagingSystem, Message, MessagePriority
from .queue_monitor import QueueMonitor, AlertConfig, log_alert_handler, console_alert_handler
from .consumer_autoscaler import ConsumerAutoScaler, ScalingConfig

logger = logging.getLogger(__name__)


class EnterpriseMessageQueueSystem:
    """
    Complete enterprise message queue system with:
    - Multiple backend support (Redis, RabbitMQ, Kafka)
    - Dead letter queues
    - Message retry logic
    - Real-time monitoring
    - Consumer auto-scaling
    """
    
    def __init__(self, config: Optional[MessagingConfig] = None):
        self.config = config or get_messaging_config()
        
        # Core components
        self.messaging_system: Optional[UnifiedMessagingSystem] = None
        self.monitor: Optional[QueueMonitor] = None
        self.autoscaler: Optional[ConsumerAutoScaler] = None
        
        # State
        self.is_running = False
        self.initialized = False
        
        # Queue configurations
        self.queue_configs: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[str, Callable[[Message], None]] = {}
    
    async def initialize(self) -> None:
        """Initialize the complete message queue system"""
        try:
            logger.info("Initializing Enterprise Message Queue System...")
            
            # Initialize messaging system
            self.messaging_system = UnifiedMessagingSystem(self.config)
            await self.messaging_system.initialize()
            
            # Initialize monitoring
            self.monitor = QueueMonitor(self.messaging_system, self.config)
            
            # Add default alert handlers
            self.monitor.add_alert_handler(log_alert_handler)
            if self.config.monitoring_enabled:
                self.monitor.add_alert_handler(console_alert_handler)
            
            # Initialize auto-scaler
            self.autoscaler = ConsumerAutoScaler(
                self.messaging_system, 
                self.monitor, 
                self.config
            )
            
            self.initialized = True
            logger.info("Enterprise Message Queue System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize message queue system: {e}")
            raise
    
    async def start(self) -> None:
        """Start the message queue system"""
        if not self.initialized:
            await self.initialize()
        
        if self.is_running:
            logger.warning("Message queue system already running")
            return
        
        try:
            logger.info("Starting Enterprise Message Queue System...")
            
            # Start monitoring
            if self.config.monitoring_enabled:
                await self.monitor.start_monitoring()
            
            # Start auto-scaling
            if self.config.auto_scaling_enabled:
                await self.autoscaler.start_scaling()
            
            self.is_running = True
            logger.info("Enterprise Message Queue System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start message queue system: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the message queue system"""
        if not self.is_running:
            logger.warning("Message queue system not running")
            return
        
        try:
            logger.info("Shutting down Enterprise Message Queue System...")
            
            self.is_running = False
            
            # Stop auto-scaling
            if self.autoscaler:
                await self.autoscaler.stop_scaling()
            
            # Stop monitoring
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            # Shutdown messaging system
            if self.messaging_system:
                await self.messaging_system.shutdown()
            
            logger.info("Enterprise Message Queue System shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def configure_queue(self, 
                       queue_name: str,
                       handler: Callable[[Message], None],
                       scaling_config: Optional[ScalingConfig] = None,
                       alert_config: Optional[AlertConfig] = None) -> None:
        """Configure a queue with handler and policies"""
        
        # Default scaling configuration
        if scaling_config is None:
            scaling_config = ScalingConfig(
                queue_name=queue_name,
                min_consumers=self.config.min_consumers,
                max_consumers=self.config.max_consumers,
                target_queue_depth=50,
                scale_up_threshold=self.config.scale_up_threshold,
                scale_down_threshold=self.config.scale_down_threshold
            )
        
        # Default alert configuration
        if alert_config is None:
            alert_config = AlertConfig(
                queue_name=queue_name,
                max_queue_depth=1000,
                max_processing_time=30.0,
                max_error_rate=0.1
            )
        
        # Store configurations
        self.queue_configs[queue_name] = {
            "scaling_config": scaling_config,
            "alert_config": alert_config,
            "handler": handler
        }
        self.message_handlers[queue_name] = handler
        
        # Apply configurations if system is initialized
        if self.initialized:
            if self.autoscaler:
                self.autoscaler.add_scaling_config(scaling_config)
                self.autoscaler.register_message_handler(queue_name, handler)
            
            if self.monitor:
                self.monitor.add_alert_config(alert_config)
        
        logger.info(f"Configured queue {queue_name}")
    
    async def publish(self, 
                     queue_name: str, 
                     data: Dict[str, Any],
                     priority: MessagePriority = MessagePriority.NORMAL,
                     delay: Optional[float] = None,
                     correlation_id: Optional[str] = None,
                     reply_to: Optional[str] = None,
                     headers: Optional[Dict[str, str]] = None) -> str:
        """Publish a message to a queue"""
        if not self.messaging_system:
            raise RuntimeError("Message queue system not initialized")
        
        return await self.messaging_system.publish(
            queue_name=queue_name,
            data=data,
            priority=priority,
            delay=delay,
            correlation_id=correlation_id,
            reply_to=reply_to,
            headers=headers
        )
    
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get comprehensive queue statistics"""
        stats = {}
        
        # Basic queue stats
        if self.messaging_system:
            queue_stats = await self.messaging_system.get_queue_stats(queue_name)
            stats["queue"] = {
                "pending_messages": queue_stats.pending_messages,
                "processing_messages": queue_stats.processing_messages,
                "completed_messages": queue_stats.completed_messages,
                "failed_messages": queue_stats.failed_messages,
                "dead_letter_messages": queue_stats.dead_letter_messages,
                "consumer_count": queue_stats.consumer_count,
                "last_updated": queue_stats.last_updated.isoformat() if queue_stats.last_updated else None
            }
        
        # Monitoring metrics
        if self.monitor:
            metrics = self.monitor.get_queue_metrics(queue_name, hours=1)
            if metrics:
                latest_metrics = metrics[-1]
                stats["metrics"] = {
                    "messages_per_second": latest_metrics.messages_per_second,
                    "average_processing_time": latest_metrics.average_processing_time,
                    "error_rate": latest_metrics.error_rate,
                    "consumer_utilization": latest_metrics.consumer_utilization,
                    "queue_depth": latest_metrics.queue_depth,
                    "dlq_depth": latest_metrics.dlq_depth
                }
        
        # Consumer stats
        if self.autoscaler:
            consumer_stats = self.autoscaler.get_consumer_stats(queue_name)
            stats["consumers"] = consumer_stats
        
        # Scaling history
        if self.autoscaler:
            scaling_history = self.autoscaler.get_scaling_history(queue_name, hours=24)
            stats["scaling_history"] = [
                {
                    "timestamp": decision.timestamp.isoformat(),
                    "action": decision.action.value,
                    "current_consumers": decision.current_consumers,
                    "target_consumers": decision.target_consumers,
                    "reason": decision.reason,
                    "confidence": decision.confidence
                }
                for decision in scaling_history[-10:]  # Last 10 decisions
            ]
        
        return stats
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        health = {
            "status": "healthy" if self.is_running else "stopped",
            "initialized": self.initialized,
            "components": {
                "messaging_system": self.messaging_system is not None,
                "monitor": self.monitor is not None,
                "autoscaler": self.autoscaler is not None
            },
            "configuration": {
                "backend": self.config.primary_backend.value,
                "rabbitmq_enabled": self.config.enable_rabbitmq,
                "kafka_enabled": self.config.enable_kafka,
                "monitoring_enabled": self.config.monitoring_enabled,
                "auto_scaling_enabled": self.config.auto_scaling_enabled,
                "dead_letter_queue_enabled": self.config.dead_letter_queue_enabled,
                "retry_enabled": self.config.retry_enabled
            },
            "queues": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add queue health information
        if self.messaging_system:
            for queue_name in self.queue_configs.keys():
                try:
                    queue_stats = await self.get_queue_stats(queue_name)
                    health["queues"][queue_name] = {
                        "status": "healthy",
                        "pending_messages": queue_stats.get("queue", {}).get("pending_messages", 0),
                        "active_consumers": queue_stats.get("consumers", {}).get("active_consumers", 0),
                        "error_rate": queue_stats.get("metrics", {}).get("error_rate", 0.0)
                    }
                except Exception as e:
                    health["queues"][queue_name] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        return health
    
    def get_queue_list(self) -> List[str]:
        """Get list of configured queues"""
        return list(self.queue_configs.keys())
    
    async def purge_queue(self, queue_name: str) -> int:
        """Purge all messages from a queue"""
        if not self.messaging_system:
            raise RuntimeError("Message queue system not initialized")
        
        return await self.messaging_system.primary_backend.purge_queue(queue_name)
    
    async def replay_dead_letter_queue(self, queue_name: str, max_messages: int = 100) -> int:
        """Replay messages from dead letter queue back to main queue"""
        if not self.messaging_system:
            raise RuntimeError("Message queue system not initialized")
        
        dlq_name = f"{queue_name}.dlq"
        replayed = 0
        
        try:
            for _ in range(max_messages):
                # Get message from DLQ
                dlq_message = await self.messaging_system.consume(dlq_name, timeout=0.1)
                if not dlq_message:
                    break
                
                # Republish to main queue
                await self.messaging_system.publish(
                    queue_name=queue_name,
                    data=dlq_message.data,
                    priority=dlq_message.priority,
                    correlation_id=dlq_message.correlation_id,
                    reply_to=dlq_message.reply_to,
                    headers=dlq_message.headers
                )
                
                # Acknowledge DLQ message
                await self.messaging_system.ack(dlq_message, success=True)
                replayed += 1
            
            logger.info(f"Replayed {replayed} messages from {dlq_name} to {queue_name}")
            return replayed
            
        except Exception as e:
            logger.error(f"Failed to replay dead letter queue {dlq_name}: {e}")
            raise


# Convenience functions for quick setup
async def create_message_queue_system(config: Optional[MessagingConfig] = None) -> EnterpriseMessageQueueSystem:
    """Create and initialize a message queue system"""
    system = EnterpriseMessageQueueSystem(config)
    await system.initialize()
    return system


async def quick_setup_with_queues(queue_configs: Dict[str, Dict[str, Any]], 
                                config: Optional[MessagingConfig] = None) -> EnterpriseMessageQueueSystem:
    """Quick setup with multiple queue configurations"""
    system = await create_message_queue_system(config)
    
    for queue_name, queue_config in queue_configs.items():
        system.configure_queue(
            queue_name=queue_name,
            handler=queue_config["handler"],
            scaling_config=queue_config.get("scaling_config"),
            alert_config=queue_config.get("alert_config")
        )
    
    await system.start()
    return system


# Example usage demonstration
async def demo_setup():
    """Demonstration of the complete message queue system"""
    
    # Example message handlers
    async def content_processing_handler(message: Message):
        """Handle content processing messages"""
        print(f"Processing content: {message.data}")
        # Simulate processing time
        await asyncio.sleep(0.1)
    
    async def ai_analysis_handler(message: Message):
        """Handle AI analysis messages"""
        print(f"AI analyzing: {message.data}")
        # Simulate AI processing
        await asyncio.sleep(0.5)
    
    async def notification_handler(message: Message):
        """Handle notification messages"""
        print(f"Sending notification: {message.data}")
        await asyncio.sleep(0.05)
    
    # Queue configurations
    queue_configs = {
        "content_processing": {
            "handler": content_processing_handler,
            "scaling_config": ScalingConfig(
                queue_name="content_processing",
                min_consumers=2,
                max_consumers=8,
                target_queue_depth=20
            )
        },
        "ai_analysis": {
            "handler": ai_analysis_handler,
            "scaling_config": ScalingConfig(
                queue_name="ai_analysis",
                min_consumers=1,
                max_consumers=4,
                target_queue_depth=10
            )
        },
        "notifications": {
            "handler": notification_handler,
            "scaling_config": ScalingConfig(
                queue_name="notifications",
                min_consumers=1,
                max_consumers=3,
                target_queue_depth=50
            )
        }
    }
    
    # Create and start the system
    system = await quick_setup_with_queues(queue_configs)
    
    try:
        # Publish some test messages
        for i in range(10):
            await system.publish("content_processing", {"id": i, "type": "content"})
            await system.publish("ai_analysis", {"id": i, "type": "analysis"})
            await system.publish("notifications", {"id": i, "type": "notification"})
        
        # Let it run for a bit
        await asyncio.sleep(30)
        
        # Show system health
        health = await system.get_system_health()
        print("System Health:", health)
        
    finally:
        await system.shutdown()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_setup())