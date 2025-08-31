"""IA Influencer Agent - Messaging Deployment Module
Enterprise messaging and queue deployment for high-performance content processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Core messaging managers
from .celery_manager import CeleryManager, CeleryClusterConfig, CeleryWorkerConfig
from .rabbitmq_manager import RabbitMQManager, RabbitMQClusterConfig, RabbitMQNodeConfig, ExchangeConfig, QueueConfig
from .kafka_manager import KafkaManager, KafkaClusterConfig, KafkaBrokerConfig, ZookeeperConfig, TopicConfig
from .message_router import (
    MessageRouter, Message, MessageType, MessagePriority, MessageProtocol,
    RoutingStrategy, RouteConfig, MessageHandler, MessageTransformer, MessageFilter
)

# Real-time communication and notifications
from .real_time_communication import (
    RealTimeCommunicationManager, WebSocketConnection, NotificationChannel, RealTimeMessage
)
from .notification_manager import (
    EmailNotificationManager, SMSNotificationManager, MultiChannelNotificationManager,
    EmailTemplate, SMSTemplate, NotificationPreferences
)

# Queue management and performance monitoring
from .queue_management import (
    QueueManager, QueueConfiguration, QueueStats, QueueTask, QueuePriority, QueueType, QueueStatus
)
from .performance_monitor import (
    MessagingPerformanceMonitor, PerformanceMetrics, AlertRule, PerformanceOptimizer
)

# Orchestration and deployment
from .index import (
    MessagingDeploymentOrchestrator,
    deploy_messaging_infrastructure,
    create_kafka_manager,
    create_rabbitmq_manager,
    create_celery_manager,
    create_message_router,
    create_messaging_orchestrator
)

__all__ = [
    # Core managers
    "CeleryManager",
    "CeleryClusterConfig", 
    "CeleryWorkerConfig",
    "RabbitMQManager",
    "RabbitMQClusterConfig",
    "RabbitMQNodeConfig",
    "ExchangeConfig",
    "QueueConfig",
    "KafkaManager",
    "KafkaClusterConfig",
    "KafkaBrokerConfig",
    "ZookeeperConfig",
    "TopicConfig",
    
    # Message routing
    "MessageRouter",
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageProtocol",
    "RoutingStrategy",
    "RouteConfig",
    "MessageHandler",
    "MessageTransformer",
    "MessageFilter",
    
    # Real-time communication
    "RealTimeCommunicationManager",
    "WebSocketConnection",
    "NotificationChannel",
    "RealTimeMessage",
    
    # Notification management
    "EmailNotificationManager",
    "SMSNotificationManager",
    "MultiChannelNotificationManager",
    "EmailTemplate",
    "SMSTemplate",
    "NotificationPreferences",
    
    # Queue management
    "QueueManager",
    "QueueConfiguration",
    "QueueStats",
    "QueueTask",
    "QueuePriority",
    "QueueType",
    "QueueStatus",
    
    # Performance monitoring
    "MessagingPerformanceMonitor",
    "PerformanceMetrics",
    "AlertRule",
    "PerformanceOptimizer",
    
    # Orchestration
    "MessagingDeploymentOrchestrator",
    "deploy_messaging_infrastructure",
    "create_kafka_manager",
    "create_rabbitmq_manager",
    "create_celery_manager",
    "create_message_router",
    "create_messaging_orchestrator"
]
