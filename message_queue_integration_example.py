"""
Complete Message Queue System Integration Example
Demonstrates how to use the Enterprise Message Queue System in production

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Complete example showing all enterprise message queue features
    """
    
    # Import the system components
    try:
        from kubernetes.messaging.enterprise_queue_system import EnterpriseMessageQueueSystem
        from kubernetes.messaging.messaging_config import MessagingConfig, MessagingBackend
        from kubernetes.messaging.unified_messaging import MessagePriority
        from kubernetes.messaging.consumer_autoscaler import ScalingConfig
        from kubernetes.messaging.queue_monitor import AlertConfig
    except ImportError as e:
        logger.error(f"Failed to import messaging components: {e}")
        logger.info("This example requires the complete message queue system implementation")
        return
    
    # Configuration for production-like setup
    config = MessagingConfig(
        primary_backend=MessagingBackend.REDIS,
        redis_host="localhost",
        redis_port=6379,
        
        # Enable enterprise features
        monitoring_enabled=True,
        auto_scaling_enabled=True,
        dead_letter_queue_enabled=True,
        retry_enabled=True,
        
        # Performance settings
        max_retries=3,
        retry_backoff_factor=2.0,
        min_consumers=1,
        max_consumers=8,
        scale_up_threshold=0.7,
        scale_down_threshold=0.3
    )
    
    # Create the enterprise message queue system
    system = EnterpriseMessageQueueSystem(config)
    
    try:
        logger.info("🚀 Initializing Enterprise Message Queue System...")
        await system.initialize()
        
        # Define message handlers for different types of work
        
        async def content_processing_handler(message):
            """Handle content processing tasks"""
            content_id = message.data.get("content_id")
            action = message.data.get("action", "process")
            
            logger.info(f"📄 Processing content {content_id}: {action}")
            
            # Simulate processing time based on action
            if action == "fingerprint":
                await asyncio.sleep(0.5)  # Fingerprinting takes longer
            elif action == "analyze":
                await asyncio.sleep(0.3)  # AI analysis
            else:
                await asyncio.sleep(0.1)  # Basic processing
            
            # Simulate occasional failures for demonstration
            import random
            if random.random() < 0.1:  # 10% failure rate
                raise Exception(f"Simulated processing error for content {content_id}")
            
            logger.info(f"✅ Completed processing content {content_id}")
        
        async def notification_handler(message):
            """Handle notification sending"""
            recipient = message.data.get("recipient")
            message_text = message.data.get("message")
            
            logger.info(f"📧 Sending notification to {recipient}: {message_text}")
            await asyncio.sleep(0.05)  # Quick notification sending
            logger.info(f"✅ Notification sent to {recipient}")
        
        async def ai_analysis_handler(message):
            """Handle AI analysis tasks"""
            task_type = message.data.get("task_type")
            data_size = message.data.get("data_size", 1)
            
            logger.info(f"🤖 Running AI analysis: {task_type} (size: {data_size})")
            
            # Simulate variable processing time based on data size
            processing_time = 0.2 + (data_size * 0.1)
            await asyncio.sleep(processing_time)
            
            logger.info(f"✅ Completed AI analysis: {task_type}")
        
        # Configure queues with different scaling and alert policies
        
        # High-volume content processing queue
        system.configure_queue(
            queue_name="content_processing",
            handler=content_processing_handler,
            scaling_config=ScalingConfig(
                queue_name="content_processing",
                min_consumers=2,
                max_consumers=6,
                target_queue_depth=20,
                scale_up_threshold=0.8,
                scale_down_threshold=0.2,
                scale_up_cooldown=30,
                scale_down_cooldown=120
            ),
            alert_config=AlertConfig(
                queue_name="content_processing",
                max_queue_depth=100,
                max_processing_time=2.0,
                max_error_rate=0.15
            )
        )
        
        # Fast notification queue
        system.configure_queue(
            queue_name="notifications",
            handler=notification_handler,
            scaling_config=ScalingConfig(
                queue_name="notifications",
                min_consumers=1,
                max_consumers=3,
                target_queue_depth=50,
                scale_up_threshold=0.7,
                scale_down_threshold=0.3
            ),
            alert_config=AlertConfig(
                queue_name="notifications",
                max_queue_depth=200,
                max_processing_time=1.0,
                max_error_rate=0.05
            )
        )
        
        # Resource-intensive AI analysis queue
        system.configure_queue(
            queue_name="ai_analysis",
            handler=ai_analysis_handler,
            scaling_config=ScalingConfig(
                queue_name="ai_analysis",
                min_consumers=1,
                max_consumers=4,
                target_queue_depth=5,  # Keep queue small due to resource intensity
                scale_up_threshold=0.6,
                scale_down_threshold=0.2,
                aggressive_scaling=False
            ),
            alert_config=AlertConfig(
                queue_name="ai_analysis",
                max_queue_depth=20,
                max_processing_time=5.0,
                max_error_rate=0.1
            )
        )
        
        # Start the system
        logger.info("🔥 Starting Enterprise Message Queue System...")
        await system.start()
        
        # Publish various types of messages to demonstrate the system
        logger.info("📤 Publishing test messages...")
        
        # Content processing messages
        for i in range(15):
            action = ["process", "fingerprint", "analyze"][i % 3]
            await system.publish(
                queue_name="content_processing",
                data={
                    "content_id": f"content_{i}",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                },
                priority=MessagePriority.HIGH if action == "fingerprint" else MessagePriority.NORMAL
            )
        
        # Notification messages
        for i in range(10):
            await system.publish(
                queue_name="notifications",
                data={
                    "recipient": f"user_{i}@example.com",
                    "message": f"Your content processing is complete #{i}",
                    "type": "email"
                },
                priority=MessagePriority.NORMAL
            )
        
        # AI analysis messages with varying complexity
        for i in range(8):
            await system.publish(
                queue_name="ai_analysis",
                data={
                    "task_type": f"analysis_type_{i % 3}",
                    "data_size": (i % 5) + 1,  # 1-5 size units
                    "priority": "high" if i < 3 else "normal"
                },
                priority=MessagePriority.HIGH if i < 3 else MessagePriority.NORMAL
            )
        
        # Delayed message (scheduled processing)
        await system.publish(
            queue_name="content_processing",
            data={
                "content_id": "delayed_content",
                "action": "scheduled_process",
                "scheduled_for": datetime.utcnow().isoformat()
            },
            delay=10  # Process in 10 seconds
        )
        
        logger.info("✅ All messages published successfully")
        
        # Let the system run and process messages
        logger.info("⏳ Processing messages for 60 seconds...")
        
        for i in range(12):  # Check every 5 seconds for 1 minute
            await asyncio.sleep(5)
            
            # Show system health and stats
            health = await system.get_system_health()
            logger.info(f"🏥 System Health: {health['status']}")
            
            # Show queue statistics
            for queue_name in ["content_processing", "notifications", "ai_analysis"]:
                try:
                    stats = await system.get_queue_stats(queue_name)
                    queue_info = stats.get("queue", {})
                    consumer_info = stats.get("consumers", {})
                    metrics_info = stats.get("metrics", {})
                    
                    logger.info(
                        f"📊 {queue_name}: "
                        f"pending={queue_info.get('pending_messages', 0)}, "
                        f"processing={queue_info.get('processing_messages', 0)}, "
                        f"consumers={consumer_info.get('active_consumers', 0)}, "
                        f"error_rate={metrics_info.get('error_rate', 0):.1%}"
                    )
                except Exception as e:
                    logger.warning(f"Could not get stats for {queue_name}: {e}")
        
        # Demonstrate dead letter queue functionality
        logger.info("🔍 Checking dead letter queues...")
        for queue_name in ["content_processing", "notifications", "ai_analysis"]:
            try:
                dlq_stats = await system.get_queue_stats(f"{queue_name}.dlq")
                dlq_count = dlq_stats.get("queue", {}).get("pending_messages", 0)
                if dlq_count > 0:
                    logger.info(f"💀 Found {dlq_count} messages in {queue_name} DLQ")
                    
                    # Demonstrate DLQ replay
                    replayed = await system.replay_dead_letter_queue(queue_name, max_messages=5)
                    logger.info(f"🔄 Replayed {replayed} messages from {queue_name} DLQ")
            except Exception as e:
                logger.debug(f"No DLQ stats for {queue_name}: {e}")
        
        # Final system health report
        final_health = await system.get_system_health()
        logger.info("📋 Final System Health Report:")
        logger.info(f"   Status: {final_health['status']}")
        logger.info(f"   Components: {final_health['components']}")
        logger.info(f"   Queues configured: {len(final_health['queues'])}")
        
        for queue_name, queue_health in final_health['queues'].items():
            if queue_health['status'] == 'healthy':
                logger.info(f"   ✅ {queue_name}: {queue_health['pending_messages']} pending, "
                           f"{queue_health['active_consumers']} consumers")
            else:
                logger.warning(f"   ❌ {queue_name}: {queue_health.get('error', 'Unknown error')}")
        
        logger.info("🎉 Enterprise Message Queue System demonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Graceful shutdown
        logger.info("🛑 Shutting down Enterprise Message Queue System...")
        await system.shutdown()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    print("🚀 Enterprise Message Queue System - Complete Integration Example")
    print("=" * 70)
    print("This example demonstrates:")
    print("- Multi-queue setup with different scaling policies")
    print("- Message publishing with priorities and delays")
    print("- Real-time monitoring and health checks")
    print("- Dead letter queue handling and replay")
    print("- Automatic consumer scaling")
    print("- Graceful error handling and recovery")
    print("=" * 70)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)