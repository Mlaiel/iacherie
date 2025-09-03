"""
IA Influencer Agent - Unified Messaging Configuration
Enterprise messaging system configuration and setup

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MessagingBackend(str, Enum):
    """Supported messaging backends"""
    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"

@dataclass
class MessagingConfig:
    """Unified messaging system configuration"""
    
    # Backend selection
    primary_backend: MessagingBackend = MessagingBackend.REDIS
    enable_rabbitmq: bool = True
    enable_kafka: bool = True
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # RabbitMQ configuration
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    
    # Kafka configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "ia-influencer-agent"
    
    # Queue configuration
    default_queue_maxsize: int = 10000
    dead_letter_queue_enabled: bool = True
    retry_enabled: bool = True
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    
    # Monitoring configuration
    monitoring_enabled: bool = True
    metrics_export_interval: int = 30
    health_check_interval: int = 60
    
    # Scaling configuration
    auto_scaling_enabled: bool = True
    min_consumers: int = 1
    max_consumers: int = 10
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.2
    
    @classmethod
    def from_env(cls) -> 'MessagingConfig':
        """Create configuration from environment variables"""
        return cls(
            primary_backend=MessagingBackend(os.getenv('MESSAGING_BACKEND', 'redis')),
            enable_rabbitmq=os.getenv('ENABLE_RABBITMQ', 'true').lower() == 'true',
            enable_kafka=os.getenv('ENABLE_KAFKA', 'true').lower() == 'true',
            
            redis_host=os.getenv('REDIS_HOST', 'localhost'),
            redis_port=int(os.getenv('REDIS_PORT', 6379)),
            redis_db=int(os.getenv('REDIS_DB', 0)),
            redis_password=os.getenv('REDIS_PASSWORD'),
            
            rabbitmq_host=os.getenv('RABBITMQ_HOST', 'localhost'),
            rabbitmq_port=int(os.getenv('RABBITMQ_PORT', 5672)),
            rabbitmq_user=os.getenv('RABBITMQ_USER', 'guest'),
            rabbitmq_password=os.getenv('RABBITMQ_PASSWORD', 'guest'),
            rabbitmq_vhost=os.getenv('RABBITMQ_VHOST', '/'),
            
            kafka_bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            kafka_client_id=os.getenv('KAFKA_CLIENT_ID', 'ia-influencer-agent'),
            
            dead_letter_queue_enabled=os.getenv('DLQ_ENABLED', 'true').lower() == 'true',
            retry_enabled=os.getenv('RETRY_ENABLED', 'true').lower() == 'true',
            max_retries=int(os.getenv('MAX_RETRIES', 3)),
            retry_backoff_factor=float(os.getenv('RETRY_BACKOFF_FACTOR', 2.0)),
            
            monitoring_enabled=os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
            auto_scaling_enabled=os.getenv('AUTO_SCALING_ENABLED', 'true').lower() == 'true',
            min_consumers=int(os.getenv('MIN_CONSUMERS', 1)),
            max_consumers=int(os.getenv('MAX_CONSUMERS', 10)),
        )


def get_messaging_config() -> MessagingConfig:
    """Get the global messaging configuration"""
    return MessagingConfig.from_env()