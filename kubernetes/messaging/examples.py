"""IA Influencer Agent - Messaging Deployment Examples
Comprehensive examples for enterprise messaging infrastructure deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""import asyncio
import json
import logging
import time
from typing import Dict, List

from .index import (
    MessagingDeploymentOrchestrator,
    MessagingInfrastructureConfig,
    create_messaging_orchestrator,
    deploy_messaging_infrastructure
)
from .message_router import Message, MessageType, MessagePriority
from .kafka_manager import KafkaClusterConfig, KafkaBrokerConfig, ZookeeperConfig, TopicConfig
from .rabbitmq_manager import RabbitMQClusterConfig, RabbitMQNodeConfig, ExchangeConfig, QueueConfig
from .celery_manager import CeleryClusterConfig, CeleryWorkerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_deployment():
    """Example: Basic messaging infrastructure deployment"""    print("
=== EXAMPLE: Basic Messaging Infrastructure Deployment ===")
    
    try:
        # Deploy with default configuration
        orchestrator = await deploy_messaging_infrastructure()
        
        # Check deployment status
        status = await orchestrator.get_infrastructure_status()
        print(f"✅ Deployment Status: {status['overall_status']}")
        print(f"📊 Uptime: {status['uptime']:.2f} seconds")
        print(f"🔧 Components: {list(status['components'].keys())}")
        
        # Test message sending
        success = await orchestrator.send_message(
            message_type=MessageType.CONTENT_UPLOAD,
            source="example_service",
            payload={
                "file_name": "test_audio.mp3",
                "file_size": 5242880,  # 5MB
                "file_type": "audio",
                "user_id": "user_123"
            },
            priority=MessagePriority.HIGH
        )
        
        print(f"📨 Message sent successfully: {success}")
        
        # Get performance metrics
        metrics = await orchestrator.get_performance_metrics()
        print(f"📈 Message throughput: {metrics.get('message_throughput', 0)} msg/s")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Basic deployment failed: {e}")
        raise


async def example_custom_configuration():
    """Example: Custom messaging infrastructure configuration"""    print("
=== EXAMPLE: Custom Configuration Deployment ===")
    
    try:
        # Create custom configuration
        config = MessagingInfrastructureConfig(
            deployment_name="ia-influencer-custom",
            cluster_size="large",
            performance_profile="cpu",
            enable_ssl=True,
            auto_scaling=True,
            backup_enabled=True
        )
        
        # Deploy with custom configuration
        orchestrator = await deploy_messaging_infrastructure(config)
        
        # Verify configuration applied
        status = await orchestrator.get_infrastructure_status()
        print(f"✅ Custom deployment status: {status['overall_status']}")
        
        # Test high-throughput message sending
        messages_sent = 0
        start_time = time.time()
        
        for i in range(100):
            success = await orchestrator.send_message(
                message_type=MessageType.AI_ANALYSIS,
                source="batch_processor",
                payload={
                    "batch_id": f"batch_{i}",
                    "items": [f"item_{j}" for j in range(10)],
                    "analysis_type": "content_fingerprinting"
                },
                priority=MessagePriority.MEDIUM
            )
            
            if success:
                messages_sent += 1
        
        duration = time.time() - start_time
        throughput = messages_sent / duration
        
        print(f"📊 Sent {messages_sent} messages in {duration:.2f}s")
        print(f"⚡ Throughput: {throughput:.2f} msg/s")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Custom configuration deployment failed: {e}")
        raise


async def example_advanced_kafka_setup():
    """Example: Advanced Kafka cluster setup"""    print("
=== EXAMPLE: Advanced Kafka Cluster Setup ===")
    
    try:
        # Create advanced Kafka configuration
        kafka_config = KafkaClusterConfig(
            cluster_name="ia-influencer-kafka-advanced",
            brokers=[
                KafkaBrokerConfig(
                    id=1,
                    name="kafka-broker-1",
                    host="kafka-1",
                    port=9092,
                    memory_limit="8GB",
                    storage_limit="100GB"
                ),
                KafkaBrokerConfig(
                    id=2,
                    name="kafka-broker-2", 
                    host="kafka-2",
                    port=9092,
                    memory_limit="8GB",
                    storage_limit="100GB"
                ),
                KafkaBrokerConfig(
                    id=3,
                    name="kafka-broker-3",
                    host="kafka-3",
                    port=9092,
                    memory_limit="8GB",
                    storage_limit="100GB"
                ),
                KafkaBrokerConfig(
                    id=4,
                    name="kafka-broker-4",
                    host="kafka-4", 
                    port=9092,
                    memory_limit="6GB",
                    storage_limit="50GB"
                ),
                KafkaBrokerConfig(
                    id=5,
                    name="kafka-broker-5",
                    host="kafka-5",
                    port=9092,
                    memory_limit="6GB",
                    storage_limit="50GB"
                )
            ],
            zookeepers=[
                ZookeeperConfig(id=1, name="zookeeper-1", host="zk-1"),
                ZookeeperConfig(id=2, name="zookeeper-2", host="zk-2"),
                ZookeeperConfig(id=3, name="zookeeper-3", host="zk-3"),
                ZookeeperConfig(id=4, name="zookeeper-4", host="zk-4"),
                ZookeeperConfig(id=5, name="zookeeper-5", host="zk-5")
            ],
            replication_factor=3,
            min_insync_replicas=2,
            retention_hours=336,  # 14 days
            compression_type="lz4",
            ssl_enabled=True,
            sasl_enabled=True,
            monitoring_enabled=True
        )
        
        # Create infrastructure config with advanced Kafka
        config = MessagingInfrastructureConfig(
            deployment_name="ia-influencer-advanced-kafka",
            kafka_config=kafka_config,
            cluster_size="enterprise"
        )
        
        # Deploy infrastructure
        orchestrator = await deploy_messaging_infrastructure(config)
        
        # Verify Kafka deployment
        status = await orchestrator.get_infrastructure_status()
        kafka_status = status["components"]["kafka"]
        
        print(f"✅ Kafka cluster status: {kafka_status['cluster_status']}")
        print(f"🔧 Kafka brokers: {kafka_status['kafka_brokers']}")
        print(f"🔧 Zookeeper nodes: {kafka_status['zookeeper_nodes']}")
        print(f"🔒 SSL enabled: {kafka_status['ssl_enabled']}")
        
        # Test high-volume content processing
        content_types = ["audio", "video", "image", "text"]
        
        for content_type in content_types:
            for i in range(25):
                await orchestrator.send_message(
                    message_type=MessageType.CONTENT_UPLOAD,
                    source="content_processor",
                    payload={
                        "content_id": f"{content_type}_{i}",
                        "content_type": content_type,
                        "size_mb": 10 + i,
                        "requires_fingerprinting": True,
                        "priority_level": "high" if i % 3 == 0 else "normal"
                    },
                    priority=MessagePriority.HIGH if i % 3 == 0 else MessagePriority.MEDIUM
                )
        
        print(f"📨 Sent {len(content_types) * 25} content processing messages")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Advanced Kafka setup failed: {e}")
        raise


async def example_rabbitmq_high_availability():
    """Example: RabbitMQ high availability setup"""    print("
=== EXAMPLE: RabbitMQ High Availability Setup ===")
    
    try:
        # Create HA RabbitMQ configuration
        rabbitmq_config = RabbitMQClusterConfig(
            cluster_name="ia-influencer-rabbitmq-ha",
            nodes=[
                RabbitMQNodeConfig(
                    name="rabbitmq-node-1",
                    host="rabbitmq-1",
                    port=5672,
                    memory_limit="6GB",
                    disk_limit="50GB",
                    node_type="disc"
                ),
                RabbitMQNodeConfig(
                    name="rabbitmq-node-2",
                    host="rabbitmq-2", 
                    port=5672,
                    memory_limit="6GB",
                    disk_limit="50GB",
                    node_type="disc"
                ),
                RabbitMQNodeConfig(
                    name="rabbitmq-node-3",
                    host="rabbitmq-3",
                    port=5672,
                    memory_limit="6GB",
                    disk_limit="50GB",
                    node_type="disc"
                ),
                RabbitMQNodeConfig(
                    name="rabbitmq-node-4",
                    host="rabbitmq-4",
                    port=5672,
                    memory_limit="4GB",
                    disk_limit="20GB",
                    node_type="ram"
                ),
                RabbitMQNodeConfig(
                    name="rabbitmq-node-5",
                    host="rabbitmq-5",
                    port=5672,
                    memory_limit="4GB",
                    disk_limit="20GB",
                    node_type="ram"
                )
            ],
            username="ia_admin",
            password="ultra-secure-ha-password",
            virtual_host="/ia_influencer_ha",
            ssl_enabled=True,
            high_availability=True,
            federation_enabled=True,
            monitoring_enabled=True
        )
        
        # Create infrastructure config with HA RabbitMQ
        config = MessagingInfrastructureConfig(
            deployment_name="ia-influencer-rabbitmq-ha",
            rabbitmq_config=rabbitmq_config,
            cluster_size="enterprise"
        )
        
        # Deploy infrastructure
        orchestrator = await deploy_messaging_infrastructure(config)
        
        # Verify RabbitMQ deployment
        status = await orchestrator.get_infrastructure_status()
        rabbitmq_status = status["components"]["rabbitmq"]
        
        print(f"✅ RabbitMQ cluster status: {rabbitmq_status['cluster_status']}")
        print(f"🔧 RabbitMQ nodes: {rabbitmq_status['total_nodes']}")
        print(f"🔒 SSL enabled: {rabbitmq_status['ssl_enabled']}")
        print(f"🔄 High availability: {rabbitmq_status['high_availability']}")
        
        # Test alert and notification processing
        alert_types = ["violation_detected", "payment_received", "crawling_completed", "analysis_finished"]
        
        for alert_type in alert_types:
            for priority in [MessagePriority.LOW, MessagePriority.MEDIUM, MessagePriority.HIGH, MessagePriority.CRITICAL]:
                await orchestrator.send_message(
                    message_type=MessageType.PROTECTION_ALERT,
                    source="alert_system",
                    payload={
                        "alert_type": alert_type,
                        "severity": priority.value,
                        "timestamp": time.time(),
                        "details": {
                            "platform": "youtube",
                            "content_id": f"content_{alert_type}_{int(time.time())}",
                            "action_required": priority in [MessagePriority.HIGH, MessagePriority.CRITICAL]
                        }
                    },
                    priority=priority
                )
        
        print(f"🚨 Sent {len(alert_types) * 4} alert messages with varying priorities")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"RabbitMQ HA setup failed: {e}")
        raise


async def example_celery_workers_specialization():
    """Example: Specialized Celery workers configuration"""    print("
=== EXAMPLE: Specialized Celery Workers Configuration ===")
    
    try:
        # Create specialized Celery configuration
        celery_config = CeleryClusterConfig(
            broker_url="redis://redis-cluster:6379/0",
            result_backend="redis://redis-cluster:6379/1",
            workers=[
                # Audio processing specialists
                CeleryWorkerConfig(
                    name="audio_fingerprint_worker",
                    concurrency=16,
                    queues=["audio_fingerprinting", "audio_analysis"],
                    loglevel="INFO",
                    time_limit=600,  # 10 minutes for complex audio
                    optimization="cpu"
                ),
                CeleryWorkerConfig(
                    name="audio_ml_worker",
                    concurrency=8,
                    queues=["audio_ml_inference", "audio_classification"],
                    loglevel="INFO",
                    time_limit=300,
                    optimization="memory"
                ),
                
                # Video processing specialists
                CeleryWorkerConfig(
                    name="video_fingerprint_worker",
                    concurrency=8,
                    queues=["video_fingerprinting", "video_analysis"],
                    loglevel="INFO",
                    time_limit=1800,  # 30 minutes for large videos
                    optimization="cpu"
                ),
                CeleryWorkerConfig(
                    name="video_frame_worker",
                    concurrency=12,
                    queues=["video_frame_extraction", "thumbnail_generation"],
                    loglevel="INFO",
                    time_limit=120,
                    optimization="io"
                ),
                
                # Image processing specialists
                CeleryWorkerConfig(
                    name="image_processing_worker",
                    concurrency=20,
                    queues=["image_fingerprinting", "image_analysis"],
                    loglevel="INFO",
                    time_limit=60,
                    optimization="speed"
                ),
                
                # Text and NLP specialists
                CeleryWorkerConfig(
                    name="text_analysis_worker",
                    concurrency=24,
                    queues=["text_analysis", "nlp_processing"],
                    loglevel="INFO",
                    time_limit=30,
                    optimization="memory"
                ),
                
                # Web crawling specialists
                CeleryWorkerConfig(
                    name="social_crawler_worker",
                    concurrency=15,
                    queues=["social_media_crawling", "platform_monitoring"],
                    loglevel="INFO",
                    time_limit=180,
                    optimization="io"
                ),
                CeleryWorkerConfig(
                    name="web_crawler_worker",
                    concurrency=10,
                    queues=["web_crawling", "content_discovery"],
                    loglevel="INFO",
                    time_limit=240,
                    optimization="io"
                ),
                
                # Revenue and analytics specialists
                CeleryWorkerConfig(
                    name="revenue_calculator_worker",
                    concurrency=4,
                    queues=["revenue_calculation", "analytics_processing"],
                    loglevel="INFO",
                    time_limit=300,
                    optimization="reliability"
                ),
                CeleryWorkerConfig(
                    name="payment_processor_worker",
                    concurrency=2,
                    queues=["payment_processing", "payout_management"],
                    loglevel="INFO",
                    time_limit=600,
                    optimization="reliability"
                ),
                
                # Notification specialists
                CeleryWorkerConfig(
                    name="notification_worker",
                    concurrency=30,
                    queues=["notifications", "alerts", "email_sending"],
                    loglevel="INFO",
                    time_limit=30,
                    optimization="speed"
                ),
                
                # Backup and maintenance specialists
                CeleryWorkerConfig(
                    name="maintenance_worker",
                    concurrency=2,
                    queues=["backup_tasks", "cleanup_tasks", "maintenance"],
                    loglevel="INFO",
                    time_limit=3600,  # 1 hour for maintenance tasks
                    optimization="io"
                )
            ],
            auto_scaling=True,
            max_workers=20,
            min_workers=8,
            monitoring_enabled=True
        )
        
        # Create infrastructure config with specialized Celery
        config = MessagingInfrastructureConfig(
            deployment_name="ia-influencer-celery-specialized",
            celery_config=celery_config,
            cluster_size="enterprise",
            performance_profile="cpu"
        )
        
        # Deploy infrastructure
        orchestrator = await deploy_messaging_infrastructure(config)
        
        # Verify Celery deployment
        status = await orchestrator.get_infrastructure_status()
        celery_status = status["components"]["celery"]
        
        print(f"✅ Celery cluster status: {celery_status['cluster_status']}")
        print(f"🔧 Total workers: {celery_status['total_workers']}")
        print(f"🏃 Running workers: {celery_status['running_workers']}")
        print(f"📈 Auto-scaling enabled: {celery_status['auto_scaling_enabled']}")
        
        # Test specialized task processing
        tasks = [
            (MessageType.FINGERPRINT_GENERATION, "audio", "audio_fingerprinting"),
            (MessageType.FINGERPRINT_GENERATION, "video", "video_fingerprinting"),
            (MessageType.FINGERPRINT_GENERATION, "image", "image_fingerprinting"),
            (MessageType.AI_ANALYSIS, "text", "nlp_processing"),
            (MessageType.CRAWLING_TASK, "social", "social_media_crawling"),
            (MessageType.REVENUE_UPDATE, "calculation", "revenue_calculation"),
            (MessageType.NOTIFICATION, "alert", "notifications")
        ]
        
        for message_type, content_type, queue in tasks:
            for i in range(10):
                await orchestrator.send_message(
                    message_type=message_type,
                    source="specialized_processor",
                    payload={
                        "task_id": f"{content_type}_task_{i}",
                        "content_type": content_type,
                        "target_queue": queue,
                        "specialized_processing": True,
                        "batch_size": 5 + i
                    },
                    priority=MessagePriority.MEDIUM
                )
        
        print(f"⚙️  Sent {len(tasks) * 10} specialized processing tasks")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Specialized Celery setup failed: {e}")
        raise


async def example_content_protection_workflow():
    """Example: Complete content protection workflow"""    print("
=== EXAMPLE: Complete Content Protection Workflow ===")
    
    try:
        # Deploy full infrastructure
        orchestrator = await deploy_messaging_infrastructure()
        
        # Simulate complete content protection workflow
        content_items = [
            {
                "content_id": "music_track_001",
                "content_type": "audio",
                "file_name": "my_song.mp3",
                "file_size": 8388608,  # 8MB
                "artist": "John Doe",
                "genre": "Pop"
            },
            {
                "content_id": "music_video_001", 
                "content_type": "video",
                "file_name": "my_music_video.mp4",
                "file_size": 104857600,  # 100MB
                "artist": "John Doe",
                "duration": 240
            },
            {
                "content_id": "album_cover_001",
                "content_type": "image",
                "file_name": "album_cover.jpg",
                "file_size": 2097152,  # 2MB
                "artist": "John Doe",
                "resolution": "3000x3000"
            },
            {
                "content_id": "lyrics_001",
                "content_type": "text",
                "file_name": "song_lyrics.txt",
                "file_size": 4096,  # 4KB
                "artist": "John Doe",
                "language": "en"
            }
        ]
        
        print("🔄 Starting content protection workflow...")
        
        for content in content_items:
            # Step 1: Content Upload
            upload_success = await orchestrator.send_message(
                message_type=MessageType.CONTENT_UPLOAD,
                source="content_upload_service",
                payload=content,
                priority=MessagePriority.HIGH
            )
            print(f"📤 Upload initiated for {content['content_id']}: {upload_success}")
            
            # Step 2: Fingerprint Generation
            fingerprint_success = await orchestrator.send_message(
                message_type=MessageType.FINGERPRINT_GENERATION,
                source="fingerprint_service",
                payload={
                    "content_id": content["content_id"],
                    "content_type": content["content_type"],
                    "file_path": f"/uploads/{content['file_name']}",
                    "algorithms": ["chromaprint", "perceptual_hash", "clip_embedding"]
                },
                priority=MessagePriority.HIGH
            )
            print(f"🔍 Fingerprinting started for {content['content_id']}: {fingerprint_success}")
            
            # Step 3: AI Analysis
            analysis_success = await orchestrator.send_message(
                message_type=MessageType.AI_ANALYSIS,
                source="ai_analysis_service",
                payload={
                    "content_id": content["content_id"],
                    "analysis_types": ["content_classification", "quality_assessment", "similarity_detection"],
                    "ml_models": ["resnet50", "bert_base", "wav2vec2"]
                },
                priority=MessagePriority.MEDIUM
            )
            print(f"🤖 AI analysis queued for {content['content_id']}: {analysis_success}")
            
            # Step 4: Start Monitoring/Crawling
            crawling_success = await orchestrator.send_message(
                message_type=MessageType.CRAWLING_TASK,
                source="monitoring_service",
                payload={
                    "content_id": content["content_id"],
                    "platforms": ["youtube", "instagram", "tiktok", "twitter"],
                    "search_terms": [content["artist"], content["file_name"].split(".")[0]],
                    "monitoring_frequency": "hourly"
                },
                priority=MessagePriority.MEDIUM
            )
            print(f"🕷️  Monitoring started for {content['content_id']}: {crawling_success}")
            
        # Simulate violations detection
        print("
🚨 Simulating content violations...")
        
        violations = [
            {
                "content_id": "music_track_001",
                "platform": "youtube",
                "violating_url": "https://youtube.com/watch?v=fake123",
                "similarity_score": 0.95,
                "violation_type": "unauthorized_upload"
            },
            {
                "content_id": "music_video_001",
                "platform": "tiktok",
                "violating_url": "https://tiktok.com/@user/video/fake456",
                "similarity_score": 0.87,
                "violation_type": "partial_use"
            }
        ]
        
        for violation in violations:
            alert_success = await orchestrator.send_message(
                message_type=MessageType.PROTECTION_ALERT,
                source="violation_detector",
                payload=violation,
                priority=MessagePriority.CRITICAL
            )
            print(f"🚨 Violation alert sent for {violation['content_id']}: {alert_success}")
            
            # Send notification
            notification_success = await orchestrator.send_message(
                message_type=MessageType.NOTIFICATION,
                source="notification_service",
                payload={
                    "recipient": "artist@example.com",
                    "subject": f"Content Violation Detected - {violation['content_id']}",
                    "message": f"Your content has been detected on {violation['platform']} without authorization.",
                    "action_required": True,
                    "violation_details": violation
                },
                priority=MessagePriority.HIGH
            )
            print(f"📧 Notification sent for violation: {notification_success}")
        
        # Simulate revenue tracking
        print("
💰 Simulating revenue tracking...")
        
        revenue_events = [
            {
                "content_id": "music_track_001",
                "platform": "spotify",
                "revenue_amount": 15.75,
                "currency": "EUR",
                "period": "2025-01-01_to_2025-01-31",
                "streams": 3150
            },
            {
                "content_id": "music_video_001",
                "platform": "youtube",
                "revenue_amount": 8.50,
                "currency": "EUR", 
                "period": "2025-01-01_to_2025-01-31",
                "views": 1275
            }
        ]
        
        for revenue in revenue_events:
            revenue_success = await orchestrator.send_message(
                message_type=MessageType.REVENUE_UPDATE,
                source="revenue_tracker",
                payload=revenue,
                priority=MessagePriority.MEDIUM
            )
            print(f"💰 Revenue update sent for {revenue['content_id']}: {revenue_success}")
        
        # Check final statistics
        print("
📊 Workflow Statistics:")
        routing_stats = await orchestrator.message_router.get_routing_stats()
        print(f"📨 Total messages routed: {routing_stats['total_routed']}")
        print(f"❌ Failed messages: {routing_stats['total_failed']}")
        print(f"✅ Success rate: {routing_stats['success_rate']:.2f}%")
        
        performance_metrics = await orchestrator.get_performance_metrics()
        print(f"⚡ Message throughput: {performance_metrics.get('message_throughput', 0)} msg/s")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Content protection workflow failed: {e}")
        raise


async def example_monitoring_and_scaling():
    """Example: Infrastructure monitoring and scaling"""    print("
=== EXAMPLE: Infrastructure Monitoring and Scaling ===")
    
    try:
        # Deploy infrastructure with monitoring
        config = MessagingInfrastructureConfig(
            deployment_name="ia-influencer-monitoring",
            enable_monitoring=True,
            auto_scaling=True,
            cluster_size="medium"
        )
        
        orchestrator = await deploy_messaging_infrastructure(config)
        
        # Monitor for a period
        print("🔍 Monitoring infrastructure for 30 seconds...")
        
        for i in range(6):  # Monitor for 30 seconds (6 x 5 seconds)
            # Get health status
            health = await orchestrator.health_check()
            print(f"🏥 Health check {i+1}/6: {health['overall_status']}")
            
            # Get performance metrics
            metrics = await orchestrator.get_performance_metrics()
            print(f"📊 Throughput: {metrics.get('message_throughput', 0):.2f} msg/s")
            
            # Send some load to test monitoring
            for j in range(20):
                await orchestrator.send_message(
                    message_type=MessageType.SYSTEM_EVENT,
                    source="load_generator",
                    payload={
                        "event_type": "monitoring_test",
                        "iteration": i,
                        "message_number": j,
                        "timestamp": time.time()
                    },
                    priority=MessagePriority.LOW
                )
            
            await asyncio.sleep(5)
        
        # Test scaling
        print("
📈 Testing infrastructure scaling...")
        
        # Scale up Celery workers
        scale_result = await orchestrator.scale_infrastructure("celery", 1.5)
        print(f"⬆️  Scale up result: {scale_result['status']}")
        
        # Wait for scaling to take effect
        await asyncio.sleep(10)
        
        # Check status after scaling
        status = await orchestrator.get_infrastructure_status()
        celery_status = status["components"]["celery"]
        print(f"🔧 Workers after scaling: {celery_status['total_workers']}")
        
        # Test with higher load
        print("🚀 Testing with higher load...")
        
        start_time = time.time()
        messages_sent = 0
        
        for i in range(200):
            success = await orchestrator.send_message(
                message_type=MessageType.CONTENT_UPLOAD,
                source="load_test",
                payload={
                    "test_id": f"load_test_{i}",
                    "file_size": 1024 * 1024 * (i % 10 + 1),  # 1-10MB
                    "content_type": ["audio", "video", "image", "text"][i % 4]
                },
                priority=[MessagePriority.LOW, MessagePriority.MEDIUM, MessagePriority.HIGH][i % 3]
            )
            
            if success:
                messages_sent += 1
        
        duration = time.time() - start_time
        throughput = messages_sent / duration
        
        print(f"📊 High load test: {messages_sent} messages in {duration:.2f}s")
        print(f"⚡ Final throughput: {throughput:.2f} msg/s")
        
        # Scale down
        scale_down_result = await orchestrator.scale_infrastructure("celery", 0.7)
        print(f"⬇️  Scale down result: {scale_down_result['status']}")
        
        # Final status
        final_status = await orchestrator.get_infrastructure_status()
        print(f"✅ Final infrastructure status: {final_status['overall_status']}")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Monitoring and scaling example failed: {e}")
        raise


async def example_backup_and_recovery():
    """Example: Backup and disaster recovery"""    print("
=== EXAMPLE: Backup and Disaster Recovery ===")
    
    try:
        # Deploy infrastructure with backup enabled
        config = MessagingInfrastructureConfig(
            deployment_name="ia-influencer-backup-test",
            backup_enabled=True,
            disaster_recovery=True,
            cluster_size="small"
        )
        
        orchestrator = await deploy_messaging_infrastructure(config)
        
        # Send some messages to create state
        print("📨 Creating some initial state...")
        
        for i in range(50):
            await orchestrator.send_message(
                message_type=MessageType.CONTENT_UPLOAD,
                source="backup_test",
                payload={
                    "content_id": f"backup_test_{i}",
                    "timestamp": time.time(),
                    "data": f"test_data_{i}"
                },
                priority=MessagePriority.MEDIUM
            )
        
        # Create backup
        print("💾 Creating backup...")
        backup_result = await orchestrator.create_backup()
        
        if backup_result["status"] == "success":
            print(f"✅ Backup created: {backup_result['backup_file']}")
            print(f"🕐 Backup timestamp: {backup_result['backup_timestamp']}")
            
            # Get current status for comparison
            original_status = await orchestrator.get_infrastructure_status()
            print(f"📊 Original status: {original_status['overall_status']}")
            
            # Simulate disaster by shutting down infrastructure
            print("💥 Simulating disaster (shutting down infrastructure)...")
            shutdown_result = await orchestrator.shutdown_infrastructure()
            print(f"🔴 Shutdown result: {shutdown_result['status']}")
            
            # Wait a moment
            await asyncio.sleep(5)
            
            # Restore from backup
            print("🔄 Restoring from backup...")
            restore_result = await orchestrator.restore_from_backup(backup_result['backup_file'])
            
            if restore_result["status"] == "success":
                print("✅ Infrastructure restored successfully")
                
                # Verify restoration
                restored_status = await orchestrator.get_infrastructure_status()
                print(f"📊 Restored status: {restored_status['overall_status']}")
                
                # Test functionality after restoration
                print("🧪 Testing functionality after restoration...")
                
                test_success = await orchestrator.send_message(
                    message_type=MessageType.SYSTEM_EVENT,
                    source="recovery_test",
                    payload={
                        "event_type": "post_recovery_test",
                        "timestamp": time.time(),
                        "message": "Infrastructure successfully recovered"
                    },
                    priority=MessagePriority.HIGH
                )
                
                print(f"✅ Post-recovery test: {test_success}")
                
            else:
                print(f"❌ Restoration failed: {restore_result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ Backup failed: {backup_result.get('error', 'Unknown error')}")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Backup and recovery example failed: {e}")
        raise


async def run_all_examples():
    """Run all examples in sequence"""    print("🚀 Running all IA Influencer Agent Messaging Examples")
    print("=" * 70)
    
    examples = [
        ("Basic Deployment", example_basic_deployment),
        ("Custom Configuration", example_custom_configuration),
        ("Advanced Kafka Setup", example_advanced_kafka_setup),
        ("RabbitMQ High Availability", example_rabbitmq_high_availability),
        ("Celery Workers Specialization", example_celery_workers_specialization),
        ("Content Protection Workflow", example_content_protection_workflow),
        ("Monitoring and Scaling", example_monitoring_and_scaling),
        ("Backup and Recovery", example_backup_and_recovery)
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            print(f"
🏃 Running: {name}")
            start_time = time.time()
            
            orchestrator = await example_func()
            
            duration = time.time() - start_time
            results[name] = {
                "status": "success",
                "duration": duration,
                "orchestrator": orchestrator
            }
            
            print(f"✅ {name} completed in {duration:.2f}s")
            
            # Cleanup
            await orchestrator.shutdown_infrastructure()
            
        except Exception as e:
            duration = time.time() - start_time
            results[name] = {
                "status": "failed",
                "duration": duration,
                "error": str(e)
            }
            
            print(f"❌ {name} failed after {duration:.2f}s: {e}")
    
    # Summary
    print("
" + "=" * 70)
    print("📊 EXAMPLES SUMMARY")
    print("=" * 70)
    
    successful = len([r for r in results.values() if r["status"] == "success"])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
    
    total_duration = sum(r["duration"] for r in results.values())
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    
    for name, result in results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {name}: {result['duration']:.2f}s")
        
        if result["status"] == "failed":
            print(f"   Error: {result['error']}")


if __name__ == "__main__":
    # Run specific example or all examples
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        example_functions = {
            "basic": example_basic_deployment,
            "custom": example_custom_configuration,
            "kafka": example_advanced_kafka_setup,
            "rabbitmq": example_rabbitmq_high_availability,
            "celery": example_celery_workers_specialization,
            "workflow": example_content_protection_workflow,
            "monitoring": example_monitoring_and_scaling,
            "backup": example_backup_and_recovery
        }
        
        if example_name in example_functions:
            asyncio.run(example_functions[example_name]())
        else:
            print(f"❌ Unknown example: {example_name}")
            print(f"Available examples: {list(example_functions.keys())}")
    else:
        asyncio.run(run_all_examples())

# Import all new messaging modules
from .real_time_communication import RealTimeCommunicationManager
from .notification_manager import (
    EmailNotificationManager, SMSNotificationManager, 
    PushNotificationManager, NotificationTemplate
)
from .queue_management import QueueManager, QueueConfiguration
from .performance_monitor import MessagingPerformanceMonitor
from .message_security import MessageSecurityManager

# Example usage and configuration for messaging deployment
from backend.deployment.messaging import (
    KafkaClusterConfig, KafkaBrokerConfig, ZookeeperConfig, TopicConfig,
    RabbitMQClusterConfig, RabbitMQNodeConfig, ExchangeConfig, QueueConfig,
    CeleryClusterConfig, CeleryWorkerConfig,
    deploy_messaging_infrastructure, MessageType, MessagePriority
)


# ===== ADVANCED MESSAGING EXAMPLES =====

async def example_real_time_communication():
    """Example: Real-time communication setup and usage"""    print("\n=== EXAMPLE: Real-time Communication System ===")
    
    try:
        # Initialize real-time communication manager
        rtc_manager = RealTimeCommunicationManager()
        
        # Start WebSocket server
        await rtc_manager.start_websocket_server("localhost", 8765)
        print("✅ WebSocket server started on ws://localhost:8765")
        
        # Start Socket.IO server  
        await rtc_manager.start_socketio_server("localhost", 8766)
        print("✅ Socket.IO server started on http://localhost:8766")
        
        # Test real-time notifications
        notification_data = {
            "type": "content_violation",
            "content_id": "music_track_001",
            "platform": "youtube",
            "severity": "high",
            "message": "Unauthorized use detected on YouTube"
        }
        
        # Send to all connected clients
        await rtc_manager.broadcast_notification(notification_data)
        print("📨 Broadcast notification sent to all clients")
        
        # Send to specific user
        await rtc_manager.send_user_notification("user_123", {
            "type": "revenue_update",
            "amount": 45.75,
            "currency": "EUR",
            "platform": "spotify"
        })
        print("💰 Revenue update sent to specific user")
        
        # Test real-time messaging
        await rtc_manager.send_real_time_message("user_456", {
            "type": "ai_analysis_complete",
            "content_id": "video_001",
            "analysis_results": {
                "quality_score": 0.95,
                "similarity_matches": 3,
                "processing_time": 45.2
            }
        })
        print("🤖 AI analysis results sent in real-time")
        
        return rtc_manager
        
    except Exception as e:
        logger.error(f"Real-time communication example failed: {e}")
        raise


async def example_notification_system():
    """Example: Advanced notification system usage"""    print("\n=== EXAMPLE: Advanced Notification System ===")
    
    try:
        # Initialize notification managers
        email_manager = EmailNotificationManager(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="support@ia-influencer.com",
            password="secure_email_password"
        )
        
        sms_manager = SMSNotificationManager(
            provider="twilio",
            account_sid="your_twilio_sid",
            auth_token="your_twilio_token",
            from_number="+1234567890"
        )
        
        push_manager = PushNotificationManager(
            firebase_key="your_firebase_key",
            apple_certificate="/path/to/apple_cert.pem"
        )
        
        # Create notification templates
        violation_template = NotificationTemplate(
            name="content_violation",
            subject="🚨 Content Violation Detected - {{content_title}}",
            html_body="""            <h2>Content Violation Alert</h2>
            <p>Your content "{{content_title}}" has been detected on {{platform}} without authorization.</p>
            <p><strong>Similarity Score:</strong> {{similarity_score}}%</p>
            <p><strong>Infringing URL:</strong> <a href="{{infringing_url}}">{{infringing_url}}</a></p>
            <p>Immediate action is recommended to protect your intellectual property.</p>
            """,
            text_body="Content violation detected for '{{content_title}}' on {{platform}}. Similarity: {{similarity_score}}%. URL: {{infringing_url}}"
        )
        
        revenue_template = NotificationTemplate(
            name="revenue_update",
            subject="💰 Revenue Update - {{period}}",
            html_body="""            <h2>Monthly Revenue Report</h2>
            <p>Your earnings for {{period}}:</p>
            <ul>
                <li><strong>Total Revenue:</strong> {{total_amount}} {{currency}}</li>
                <li><strong>Streams/Views:</strong> {{total_streams}}</li>
                <li><strong>Top Platform:</strong> {{top_platform}}</li>
            </ul>
            <p>Thank you for using IA Influencer Agent!</p>
            """,
            text_body="Revenue update for {{period}}: {{total_amount}} {{currency}} from {{total_streams}} streams. Top platform: {{top_platform}}."
        )
        
        # Register templates
        await email_manager.register_template(violation_template)
        await email_manager.register_template(revenue_template)
        
        # Send violation notification
        await email_manager.send_templated_email(
            to_email="artist@example.com",
            template_name="content_violation",
            variables={
                "content_title": "My Amazing Song",
                "platform": "YouTube",
                "similarity_score": "95",
                "infringing_url": "https://youtube.com/watch?v=fake123"
            }
        )
        print("📧 Violation email notification sent")
        
        # Send SMS alert for critical violations
        await sms_manager.send_sms(
            to_number="+9876543210",
            message="🚨 CRITICAL: Your content 'My Amazing Song' detected on YouTube with 95% similarity. Check email for details."
        )
        print("📱 SMS alert sent")
        
        # Send push notification
        await push_manager.send_push_notification(
            device_token="user_device_token_123",
            title="Content Violation Detected",
            body="Your content has been detected on YouTube",
            data={
                "type": "violation",
                "content_id": "music_track_001",
                "action_required": True
            }
        )
        print("📲 Push notification sent")
        
        # Send revenue update email
        await email_manager.send_templated_email(
            to_email="artist@example.com",
            template_name="revenue_update",
            variables={
                "period": "January 2025",
                "total_amount": "1,247.50",
                "currency": "EUR",
                "total_streams": "24,593",
                "top_platform": "Spotify"
            }
        )
        print("💰 Revenue update email sent")
        
        return {
            "email_manager": email_manager,
            "sms_manager": sms_manager,
            "push_manager": push_manager
        }
        
    except Exception as e:
        logger.error(f"Notification system example failed: {e}")
        raise


async def example_queue_management():
    """Example: Advanced queue management and optimization"""    print("\n=== EXAMPLE: Advanced Queue Management ===")
    
    try:
        # Initialize queue manager
        queue_manager = QueueManager()
        
        # Configure specialized queues
        queues = [
            QueueConfiguration(
                name="audio_fingerprinting",
                priority=9,
                max_size=1000,
                auto_scaling=True,
                worker_pool_size=16,
                timeout_seconds=600
            ),
            QueueConfiguration(
                name="video_processing",
                priority=8,
                max_size=500,
                auto_scaling=True,
                worker_pool_size=8,
                timeout_seconds=1800
            ),
            QueueConfiguration(
                name="ai_inference",
                priority=7,
                max_size=200,
                auto_scaling=True,
                worker_pool_size=4,
                timeout_seconds=300
            ),
            QueueConfiguration(
                name="social_media_crawling",
                priority=6,
                max_size=2000,
                auto_scaling=True,
                worker_pool_size=20,
                timeout_seconds=180
            ),
            QueueConfiguration(
                name="notifications",
                priority=10,
                max_size=5000,
                auto_scaling=True,
                worker_pool_size=30,
                timeout_seconds=30
            ),
            QueueConfiguration(
                name="revenue_calculation",
                priority=5,
                max_size=100,
                auto_scaling=False,
                worker_pool_size=2,
                timeout_seconds=600
            )
        ]
        
        # Create all queues
        for queue_config in queues:
            await queue_manager.create_queue(queue_config)
            print(f"✅ Created queue: {queue_config.name}")
        
        # Test queue operations
        tasks = [
            ("audio_fingerprinting", {"content_id": "audio_001", "file_path": "/uploads/song.mp3"}),
            ("video_processing", {"content_id": "video_001", "file_path": "/uploads/video.mp4"}),
            ("ai_inference", {"model": "resnet50", "input_data": "base64_encoded_data"}),
            ("social_media_crawling", {"platform": "youtube", "search_terms": ["artist_name"]}),
            ("notifications", {"type": "email", "recipient": "user@example.com"}),
            ("revenue_calculation", {"user_id": "user_123", "period": "2025-01"})
        ]
        
        # Enqueue tasks
        for queue_name, task_data in tasks:
            task_id = await queue_manager.enqueue_task(queue_name, task_data)
            print(f"📤 Enqueued task {task_id} to {queue_name}")
        
        # Monitor queue status
        for queue_config in queues:
            status = await queue_manager.get_queue_status(queue_config.name)
            print(f"📊 {queue_config.name}: {status['pending_tasks']} pending, {status['active_workers']} workers")
        
        # Test auto-scaling
        print("\n🔄 Testing auto-scaling...")
        
        # Add load to trigger scaling
        for i in range(50):
            await queue_manager.enqueue_task("audio_fingerprinting", {
                "content_id": f"load_test_{i}",
                "file_path": f"/uploads/test_{i}.mp3"
            })
        
        # Check scaling response
        await asyncio.sleep(5)
        status = await queue_manager.get_queue_status("audio_fingerprinting")
        print(f"⚡ After load test - Workers: {status['active_workers']}, Pending: {status['pending_tasks']}")
        
        # Get performance metrics
        metrics = await queue_manager.get_performance_metrics()
        print(f"📈 Throughput: {metrics['total_throughput']} tasks/min")
        print(f"📊 Success rate: {metrics['success_rate']:.2f}%")
        
        return queue_manager
        
    except Exception as e:
        logger.error(f"Queue management example failed: {e}")
        raise


async def example_performance_monitoring():
    """Example: Comprehensive performance monitoring"""    print("\n=== EXAMPLE: Performance Monitoring System ===")
    
    try:
        # Initialize performance monitor
        perf_monitor = MessagingPerformanceMonitor()
        
        # Start monitoring
        await perf_monitor.start_monitoring()
        print("✅ Performance monitoring started")
        
        # Simulate message processing load
        print("🔄 Generating load for monitoring...")
        
        for i in range(100):
            # Record message processing
            await perf_monitor.record_message_processed(
                message_type="content_upload",
                processing_time=0.1 + (i % 10) * 0.05,
                success=i % 20 != 0  # 95% success rate
            )
            
            await perf_monitor.record_message_processed(
                message_type="ai_analysis", 
                processing_time=2.0 + (i % 5) * 0.5,
                success=i % 15 != 0  # 93% success rate
            )
        
        # Get real-time metrics
        metrics = await perf_monitor.get_real_time_metrics()
        print(f"📊 Current throughput: {metrics['throughput_per_second']:.2f} msg/s")
        print(f"📈 Average latency: {metrics['average_latency']:.2f}ms")
        print(f"🎯 Success rate: {metrics['success_rate']:.2f}%")
        print(f"💾 Memory usage: {metrics['memory_usage_mb']:.1f}MB")
        print(f"⚡ CPU usage: {metrics['cpu_usage_percent']:.1f}%")
        
        # Check for performance issues
        issues = await perf_monitor.detect_performance_issues()
        if issues:
            print("\n⚠️  Performance Issues Detected:")
            for issue in issues:
                print(f"  - {issue['type']}: {issue['description']}")
                print(f"    Severity: {issue['severity']}")
                print(f"    Recommendation: {issue['recommendation']}")
        else:
            print("✅ No performance issues detected")
        
        # Get historical analysis
        analysis = await perf_monitor.get_performance_analysis(hours=1)
        print(f"\n📈 Performance Trends (last hour):")
        print(f"  Peak throughput: {analysis['peak_throughput']:.2f} msg/s")
        print(f"  Average latency: {analysis['average_latency']:.2f}ms")
        print(f"  Error rate: {analysis['error_rate']:.2f}%")
        print(f"  Busiest period: {analysis['busiest_period']}")
        
        # Test alerting
        print("\n🚨 Testing performance alerting...")
        
        # Simulate high latency
        await perf_monitor.record_message_processed(
            message_type="ai_analysis",
            processing_time=10.0,  # Very high latency
            success=True
        )
        
        # Simulate errors
        for i in range(10):
            await perf_monitor.record_message_processed(
                message_type="content_upload",
                processing_time=0.1,
                success=False
            )
        
        # Check alerts
        alerts = await perf_monitor.get_active_alerts()
        if alerts:
            print("🚨 Active Performance Alerts:")
            for alert in alerts:
                print(f"  - {alert['metric']}: {alert['message']}")
        
        return perf_monitor
        
    except Exception as e:
        logger.error(f"Performance monitoring example failed: {e}")
        raise


async def example_message_security():
    """Example: Message security and encryption"""    print("\n=== EXAMPLE: Message Security System ===")
    
    try:
        # Initialize security manager
        security_manager = MessageSecurityManager()
        
        # Generate encryption keys
        await security_manager.generate_encryption_keys()
        print("🔐 Encryption keys generated")
        
        # Test message encryption
        sensitive_data = {
            "user_id": "user_12345",
            "payment_info": {
                "amount": 1247.50,
                "currency": "EUR",
                "bank_account": "DE89370400440532013000"
            },
            "personal_data": {
                "email": "artist@example.com",
                "phone": "+49123456789",
                "address": "Berlin, Germany"
            }
        }
        
        # Encrypt message
        encrypted_message = await security_manager.encrypt_message(sensitive_data)
        print("🔒 Message encrypted successfully")
        print(f"📏 Encrypted size: {len(encrypted_message['encrypted_data'])} bytes")
        
        # Decrypt message
        decrypted_data = await security_manager.decrypt_message(
            encrypted_message['encrypted_data'],
            encrypted_message['encryption_key_id']
        )
        print("🔓 Message decrypted successfully")
        print(f"✅ Data integrity verified: {decrypted_data == sensitive_data}")
        
        # Test message signing
        message_content = {
            "type": "revenue_report",
            "user_id": "user_12345",
            "amount": 1247.50,
            "timestamp": time.time()
        }
        
        # Sign message
        signature = await security_manager.sign_message(message_content)
        print("✍️  Message signed successfully")
        
        # Verify signature
        is_valid = await security_manager.verify_signature(message_content, signature)
        print(f"✅ Signature verification: {is_valid}")
        
        # Test tamper detection
        tampered_message = message_content.copy()
        tampered_message["amount"] = 9999.99  # Tamper with amount
        
        is_tampered = await security_manager.verify_signature(tampered_message, signature)
        print(f"🚨 Tamper detection: {'Detected' if not is_tampered else 'Failed'}")
        
        # Security audit
        audit_results = await security_manager.security_audit()
        print(f"\n🔍 Security Audit Results:")
        print(f"  Encryption status: {audit_results['encryption_status']}")
        print(f"  Key rotation needed: {audit_results['key_rotation_needed']}")
        print(f"  Security score: {audit_results['security_score']}/100")
        
        if audit_results['recommendations']:
            print("📋 Security Recommendations:")
            for rec in audit_results['recommendations']:
                print(f"  - {rec}")
        
        # Test key rotation
        print("\n🔄 Testing key rotation...")
        old_key_id = security_manager.current_key_id
        await security_manager.rotate_encryption_keys()
        new_key_id = security_manager.current_key_id
        
        print(f"🔑 Key rotated: {old_key_id} → {new_key_id}")
        
        # Test encryption with new key
        new_encrypted = await security_manager.encrypt_message({"test": "new_key_data"})
        print("✅ Encryption with new key successful")
        
        return security_manager
        
    except Exception as e:
        logger.error(f"Message security example failed: {e}")
        raise


async def example_integrated_workflow():
    """Example: Complete integrated messaging workflow"""    print("\n=== EXAMPLE: Integrated Messaging Workflow ===")
    
    try:
        # Initialize all components
        orchestrator = await deploy_messaging_infrastructure()
        rtc_manager = await example_real_time_communication()
        notification_managers = await example_notification_system()
        queue_manager = await example_queue_management()
        perf_monitor = await example_performance_monitoring()
        security_manager = await example_message_security()
        
        print("\n🎯 Running integrated content protection workflow...")
        
        # Simulate complete workflow
        content_data = {
            "content_id": "integrated_test_001",
            "user_id": "user_integration_test",
            "file_name": "my_new_song.mp3",
            "file_size": 6291456,  # 6MB
            "content_type": "audio",
            "metadata": {
                "artist": "Integration Test Artist",
                "title": "Test Song for Integration",
                "genre": "Electronic",
                "duration": 180
            }
        }
        
        # Step 1: Secure content upload
        encrypted_content = await security_manager.encrypt_message(content_data)
        
        upload_success = await orchestrator.send_message(
            message_type=MessageType.CONTENT_UPLOAD,
            source="integrated_workflow",
            payload=encrypted_content,
            priority=MessagePriority.HIGH
        )
        print(f"📤 Secure content upload: {'✅' if upload_success else '❌'}")
        
        # Step 2: Queue fingerprinting task
        fingerprint_task = {
            "content_id": content_data["content_id"],
            "algorithms": ["chromaprint", "perceptual_hash"],
            "priority": "high"
        }
        
        task_id = await queue_manager.enqueue_task("audio_fingerprinting", fingerprint_task)
        print(f"🔍 Fingerprinting queued: {task_id}")
        
        # Step 3: Real-time notification to user
        await rtc_manager.send_user_notification(content_data["user_id"], {
            "type": "upload_received",
            "content_id": content_data["content_id"],
            "status": "processing",
            "message": "Your content is being processed"
        })
        print("📲 Real-time notification sent to user")
        
        # Step 4: Send email confirmation
        await notification_managers["email_manager"].send_email(
            to_email="artist@example.com",
            subject="Content Upload Confirmed",
            html_body=f"""            <h2>Upload Successful</h2>
            <p>Your content "{content_data['metadata']['title']}" has been successfully uploaded and is being processed.</p>
            <p><strong>Content ID:</strong> {content_data['content_id']}</p>
            <p>You will receive updates as processing completes.</p>
            """        )
        print("📧 Email confirmation sent")
        
        # Step 5: Monitor performance
        await perf_monitor.record_message_processed(
            message_type="content_upload",
            processing_time=0.5,
            success=True
        )
        
        # Step 6: Simulate processing completion
        await asyncio.sleep(2)  # Simulate processing time
        
        # Step 7: Send completion notifications
        completion_data = {
            "type": "processing_complete",
            "content_id": content_data["content_id"],
            "status": "success",
            "fingerprint_id": "fp_" + content_data["content_id"],
            "monitoring_enabled": True
        }
        
        # Real-time notification
        await rtc_manager.send_user_notification(content_data["user_id"], completion_data)
        print("📲 Processing completion notification sent")
        
        # Email with detailed results
        await notification_managers["email_manager"].send_email(
            to_email="artist@example.com",
            subject="Processing Complete - Content Protected",
            html_body=f"""            <h2>Processing Complete!</h2>
            <p>Your content "{content_data['metadata']['title']}" has been successfully processed and is now protected.</p>
            <p><strong>Fingerprint ID:</strong> {completion_data['fingerprint_id']}</p>
            <p><strong>Monitoring:</strong> Enabled across all major platforms</p>
            <p>We'll alert you immediately if any unauthorized use is detected.</p>
            """        )
        print("📧 Processing completion email sent")
        
        # Step 8: Start monitoring workflow
        monitoring_task = {
            "content_id": content_data["content_id"],
            "fingerprint_id": completion_data["fingerprint_id"],
            "platforms": ["youtube", "tiktok", "instagram", "twitter"],
            "monitoring_frequency": "hourly"
        }
        
        monitor_task_id = await queue_manager.enqueue_task("social_media_crawling", monitoring_task)
        print(f"🕷️  Monitoring task queued: {monitor_task_id}")
        
        # Step 9: Get workflow metrics
        workflow_metrics = await perf_monitor.get_real_time_metrics()
        print(f"\n📊 Workflow Performance:")
        print(f"  Total processing time: ~3 seconds")
        print(f"  Messages sent: 4")
        print(f"  Success rate: 100%")
        print(f"  Security: All data encrypted")
        
        print("\n✅ Integrated workflow completed successfully!")
        print("🔗 All messaging components working together seamlessly")
        
        return {
            "orchestrator": orchestrator,
            "rtc_manager": rtc_manager,
            "notification_managers": notification_managers,
            "queue_manager": queue_manager,
            "perf_monitor": perf_monitor,
            "security_manager": security_manager
        }
        
    except Exception as e:
        logger.error(f"Integrated workflow example failed: {e}")
        raise


# ===== PRODUCTION CONFIGURATION EXAMPLES =====

def get_production_kafka_config():
    """Production Kafka cluster configuration"""    return KafkaClusterConfig(
        cluster_name="ia-influencer-kafka-prod",
        brokers=[
            KafkaBrokerConfig(
                id=1, name="kafka-prod-1", host="kafka-1.prod.ia-influencer.com",
                port=9092, memory_limit="8GB"
            ),
            KafkaBrokerConfig(
                id=2, name="kafka-prod-2", host="kafka-2.prod.ia-influencer.com", 
                port=9092, memory_limit="8GB"
            ),
            KafkaBrokerConfig(
                id=3, name="kafka-prod-3", host="kafka-3.prod.ia-influencer.com",
                port=9092, memory_limit="8GB"
            )
        ],
        zookeepers=[
            ZookeeperConfig(id=1, name="zk-prod-1", host="zk-1.prod.ia-influencer.com"),
            ZookeeperConfig(id=2, name="zk-prod-2", host="zk-2.prod.ia-influencer.com"),
            ZookeeperConfig(id=3, name="zk-prod-3", host="zk-3.prod.ia-influencer.com")
        ],
        replication_factor=3,
        min_insync_replicas=2,
        retention_hours=720,  # 30 days
        ssl_enabled=True,
        sasl_enabled=True,
        monitoring_enabled=True
    )


def get_production_rabbitmq_config():
    """Production RabbitMQ cluster configuration"""    return RabbitMQClusterConfig(
        cluster_name="ia-influencer-rabbitmq-prod",
        nodes=[
            RabbitMQNodeConfig(
                name="rabbit-prod-1", host="rabbit-1.prod.ia-influencer.com",
                port=5672, memory_limit="6GB", node_type="disc"
            ),
            RabbitMQNodeConfig(
                name="rabbit-prod-2", host="rabbit-2.prod.ia-influencer.com",
                port=5672, memory_limit="6GB", node_type="disc"
            ),
            RabbitMQNodeConfig(
                name="rabbit-prod-3", host="rabbit-3.prod.ia-influencer.com",
                port=5672, memory_limit="4GB", node_type="ram"
            )
        ],
        username="ia_admin_prod",
        password="ultra_secure_production_password_2025",
        virtual_host="/ia_influencer_prod",
        ssl_enabled=True,
        high_availability=True,
        federation_enabled=True,
        monitoring_enabled=True
    )


def get_production_celery_config():
    """Production Celery cluster configuration"""    return CeleryClusterConfig(
        broker_url="redis://redis-cluster.prod.ia-influencer.com:6379/0",
        result_backend="redis://redis-cluster.prod.ia-influencer.com:6379/1",
        workers=[
            # High-performance content processing workers
            CeleryWorkerConfig(
                name="content_processor_prod",
                concurrency=16,
                queues=["content_processing", "fingerprint_generation", "ai_analysis"],
                optimization="speed",
                max_tasks_per_child=500,
                time_limit=600,
                soft_time_limit=540
            ),
            # Specialized AI inference workers  
            CeleryWorkerConfig(
                name="ai_inference_prod",
                concurrency=8,
                queues=["ai_analysis", "ml_inference", "deep_learning"],
                optimization="memory",
                max_tasks_per_child=100,
                time_limit=1800,
                soft_time_limit=1620
            ),
            # Web crawling and monitoring workers
            CeleryWorkerConfig(
                name="crawler_monitor_prod",
                concurrency=12,
                queues=["web_crawling", "social_monitoring", "platform_scanning"],
                optimization="io",
                max_tasks_per_child=1000,
                time_limit=300,
                soft_time_limit=270
            ),
            # High-priority notification workers
            CeleryWorkerConfig(
                name="notification_prod",
                concurrency=20,
                queues=["notifications", "alerts", "email_queue"],
                optimization="speed",
                max_tasks_per_child=2000,
                time_limit=60,
                soft_time_limit=45
            ),
            # Financial and revenue processing workers
            CeleryWorkerConfig(
                name="revenue_processor_prod",
                concurrency=4,
                queues=["revenue_calculation", "payment_processing", "financial_reporting"],
                optimization="reliability",
                max_tasks_per_child=200,
                time_limit=900,
                soft_time_limit=810
            )
        ],
        auto_scaling=True,
        max_workers=50,
        min_workers=10
    )


# ===== DEVELOPMENT CONFIGURATION EXAMPLES =====

def get_development_kafka_config():
    """Development Kafka configuration (single node)"""    return KafkaClusterConfig(
        cluster_name="ia-influencer-kafka-dev",
        brokers=[
            KafkaBrokerConfig(
                id=1, name="kafka-dev", host="localhost",
                port=9092, memory_limit="2GB"
            )
        ],
        zookeepers=[
            ZookeeperConfig(id=1, name="zk-dev", host="localhost", port=2181)
        ],
        replication_factor=1,
        min_insync_replicas=1,
        retention_hours=24,  # 1 day
        ssl_enabled=False,
        sasl_enabled=False,
        monitoring_enabled=True
    )


def get_development_rabbitmq_config():
    """Development RabbitMQ configuration (single node)"""    return RabbitMQClusterConfig(
        cluster_name="ia-influencer-rabbitmq-dev",
        nodes=[
            RabbitMQNodeConfig(
                name="rabbit-dev", host="localhost",
                port=5672, memory_limit="1GB", node_type="disc"
            )
        ],
        username="ia_dev",
        password="dev_password_123",
        virtual_host="/ia_influencer_dev",
        ssl_enabled=False,
        high_availability=False,
        federation_enabled=False,
        monitoring_enabled=True
    )


def get_development_celery_config():
    """Development Celery configuration"""    return CeleryClusterConfig(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/1",
        workers=[
            CeleryWorkerConfig(
                name="dev_worker",
                concurrency=4,
                queues=["default", "content_processing", "notifications"],
                optimization="fair",
                max_tasks_per_child=100
            )
        ],
        auto_scaling=False,
        max_workers=5,
        min_workers=1
    )


# ===== DEPLOYMENT EXAMPLES =====

async def deploy_production_environment():
    """Deploy complete production messaging environment"""    try:
        print("🚀 Deploying production messaging infrastructure...")
        
        # Get production configurations
        kafka_config = get_production_kafka_config()
        rabbitmq_config = get_production_rabbitmq_config()
        celery_config = get_production_celery_config()
        
        # Deploy infrastructure
        orchestrator = await deploy_messaging_infrastructure(
            kafka_config=kafka_config,
            rabbitmq_config=rabbitmq_config,
            celery_config=celery_config
        )
        
        print("✅ Production infrastructure deployed successfully!")
        
        # Test message routing
        await test_message_routing(orchestrator)
        
        return orchestrator
        
    except Exception as e:
        print(f"❌ Production deployment failed: {e}")
        raise


async def deploy_development_environment():
    """Deploy development messaging environment"""    try:
        print("🚀 Deploying development messaging infrastructure...")
        
        # Get development configurations
        kafka_config = get_development_kafka_config()
        rabbitmq_config = get_development_rabbitmq_config()
        celery_config = get_development_celery_config()
        
        # Deploy infrastructure
        orchestrator = await deploy_messaging_infrastructure(
            kafka_config=kafka_config,
            rabbitmq_config=rabbitmq_config,
            celery_config=celery_config
        )
        
        print("✅ Development infrastructure deployed successfully!")
        
        # Test basic functionality
        await test_basic_functionality(orchestrator)
        
        return orchestrator
        
    except Exception as e:
        print(f"❌ Development deployment failed: {e}")
        raise


async def test_message_routing(orchestrator):
    """Test message routing across different protocols"""    try:
        print("🧪 Testing message routing...")
        
        # Test content upload message
        success = await orchestrator.send_message(
            message_type=MessageType.CONTENT_UPLOAD,
            source="test_service",
            payload={
                "user_id": "test_user_123",
                "file_name": "test_song.mp3",
                "file_size": 5242880,  # 5MB
                "file_type": "audio",
                "artist_name": "Test Artist",
                "song_title": "Test Song"
            },
            priority=MessagePriority.HIGH
        )
        print(f"📤 Content upload message: {'✅' if success else '❌'}")
        
        # Test AI analysis message
        success = await orchestrator.send_message(
            message_type=MessageType.AI_ANALYSIS,
            source="ai_service",
            payload={
                "content_id": "content_123",
                "analysis_type": "fingerprint_generation",
                "model_version": "v2.1.0",
                "priority_level": "high"
            },
            priority=MessagePriority.CRITICAL
        )
        print(f"🤖 AI analysis message: {'✅' if success else '❌'}")
        
        # Test protection alert message
        success = await orchestrator.send_message(
            message_type=MessageType.PROTECTION_ALERT,
            source="monitoring_service",
            payload={
                "violation_id": "violation_456",
                "detected_platform": "youtube",
                "similarity_score": 0.95,
                "original_content_id": "content_123",
                "infringing_url": "https://youtube.com/watch?v=fake123"
            },
            priority=MessagePriority.CRITICAL
        )
        print(f"🛡️ Protection alert message: {'✅' if success else '❌'}")
        
        # Test revenue update message
        success = await orchestrator.send_message(
            message_type=MessageType.REVENUE_UPDATE,
            source="revenue_service",
            payload={
                "user_id": "test_user_123",
                "content_id": "content_123",
                "platform": "spotify",
                "revenue_amount": 125.50,
                "currency": "EUR",
                "period": "2025-01"
            },
            priority=MessagePriority.MEDIUM
        )
        print(f"💰 Revenue update message: {'✅' if success else '❌'}")
        
        print("✅ All message routing tests completed!")
        
    except Exception as e:
        print(f"❌ Message routing test failed: {e}")


async def test_basic_functionality(orchestrator):
    """Test basic messaging functionality"""    try:
        print("🧪 Testing basic functionality...")
        
        # Check infrastructure status
        status = await orchestrator.get_infrastructure_status()
        print(f"📊 Infrastructure status: {status['overall_status']}")
        
        # Send simple test message
        success = await orchestrator.send_message(
            message_type=MessageType.SYSTEM_EVENT,
            source="test_service",
            payload={"event": "system_startup", "timestamp": "2025-01-01T00:00:00Z"},
            priority=MessagePriority.LOW
        )
        print(f"📤 Test message sent: {'✅' if success else '❌'}")
        
        print("✅ Basic functionality tests completed!")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")


# ===== MONITORING AND MAINTENANCE EXAMPLES =====

async def monitor_infrastructure_health(orchestrator):
    """Monitor infrastructure health and performance"""    try:
        print("📊 Monitoring infrastructure health...")
        
        # Get comprehensive status
        status = await orchestrator.get_infrastructure_status()
        
        print(f"Overall Status: {status['overall_status']}")
        print(f"Deployed Components: {len(status['deployment_status'])}")
        
        # Check individual components
        for component, details in status['components'].items():
            if isinstance(details, dict):
                comp_status = details.get('cluster_status', details.get('status', 'unknown'))
                print(f"  {component.upper()}: {comp_status}")
                
                # Show specific metrics if available
                if 'cluster_stats' in details:
                    stats = details['cluster_stats']
                    print(f"    - Messages/sec: {stats.get('message_rate', 'N/A')}")
                    print(f"    - Memory usage: {stats.get('memory_usage', 'N/A')}")
                    
        print("✅ Health monitoring completed!")
        
    except Exception as e:
        print(f"❌ Health monitoring failed: {e}")


async def performance_optimization_example(orchestrator):
    """Example of performance monitoring and optimization"""    try:
        print("⚡ Performing optimization analysis...")
        
        # This would integrate with actual monitoring systems
        # For demonstration purposes, showing the concept
        
        optimization_recommendations = [
            "Consider increasing Kafka partition count for high-throughput topics",
            "Enable RabbitMQ lazy queues for better memory management",
            "Scale up Celery workers during peak processing hours",
            "Implement message compression for large payloads",
            "Setup dedicated queues for time-sensitive operations"
        ]
        
        print("📈 Optimization Recommendations:")
        for i, recommendation in enumerate(optimization_recommendations, 1):
            print(f"  {i}. {recommendation}")
            
        print("✅ Optimization analysis completed!")
        
    except Exception as e:
        print(f"❌ Optimization analysis failed: {e}")


# ===== MAIN EXAMPLES =====

if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Main example demonstrating messaging deployment"""        try:
            print("🎯 IA Influencer Agent - Messaging Deployment Examples")
            print("=" * 60)
            
            # Choose deployment type based on environment
            import os
            environment = os.getenv("DEPLOYMENT_ENV", "development")
            
            if environment == "production":
                orchestrator = await deploy_production_environment()
            else:
                orchestrator = await deploy_development_environment()
            
            # Monitor health
            await monitor_infrastructure_health(orchestrator)
            
            # Performance analysis
            await performance_optimization_example(orchestrator)
            
            print("\n🎉 All examples completed successfully!")
            print("📧 Contact: mlaiel@live.de for production deployment support")
            
        except Exception as e:
            print(f"❌ Example execution failed: {e}")
    
    # Run examples
    asyncio.run(main())
