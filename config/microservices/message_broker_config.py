"""Message Broker Configuration for IA-Influencer Agent Platform
============================================================

Professional message broker configuration for microservices communication.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator
import json


class MessageBrokerType(str, Enum):
    """Message broker types."""
    RABBITMQ = "rabbitmq"
    APACHE_KAFKA = "kafka"
    REDIS = "redis"
    NATS = "nats"
    PULSAR = "pulsar"
    AWS_SQS = "aws_sqs"
    AZURE_SERVICE_BUS = "azure_service_bus"


class ExchangeType(str, Enum):
    """RabbitMQ exchange types."""
    DIRECT = "direct"
    TOPIC = "topic"
    FANOUT = "fanout"
    HEADERS = "headers"


class DeliveryMode(int, Enum):
    """Message delivery modes."""
    NON_PERSISTENT = 1
    PERSISTENT = 2


@dataclass
class QueueConfig:
    """Queue configuration."""
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Dict[str, Any] = field(default_factory=dict)
    max_length: Optional[int] = None
    max_length_bytes: Optional[int] = None
    message_ttl: Optional[int] = None
    expires: Optional[int] = None
    max_priority: Optional[int] = None
    dead_letter_exchange: Optional[str] = None
    dead_letter_routing_key: Optional[str] = None


@dataclass
class ExchangeConfig:
    """Exchange configuration."""
    name: str
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BindingConfig:
    """Binding configuration."""
    queue: str
    exchange: str
    routing_key: str = ""
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageConfig:
    """Message configuration."""
    body: Union[str, bytes, dict]
    routing_key: str
    exchange: str = ""
    delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    priority: int = 0
    headers: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    expiration: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[float] = None
    type: Optional[str] = None
    user_id: Optional[str] = None
    app_id: Optional[str] = None


class MessageBrokerConfig(BaseSettings):
    """
    Centralized message broker configuration for microservices communication.
    Supports RabbitMQ, Apache Kafka, Redis, NATS, and cloud message brokers.
    """
    
    # Broker type selection
    broker_type: MessageBrokerType = Field(
        MessageBrokerType.RABBITMQ, 
        env="MESSAGE_BROKER_TYPE"
    )
    
    # RabbitMQ configuration
    rabbitmq_host: str = Field("localhost", env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, env="RABBITMQ_PORT")
    rabbitmq_username: str = Field("guest", env="RABBITMQ_USERNAME")
    rabbitmq_password: str = Field("guest", env="RABBITMQ_PASSWORD")
    rabbitmq_virtual_host: str = Field("/", env="RABBITMQ_VIRTUAL_HOST")
    rabbitmq_ssl_enabled: bool = Field(False, env="RABBITMQ_SSL_ENABLED")
    rabbitmq_ssl_cert_path: Optional[str] = Field(None, env="RABBITMQ_SSL_CERT_PATH")
    rabbitmq_ssl_key_path: Optional[str] = Field(None, env="RABBITMQ_SSL_KEY_PATH")
    rabbitmq_ssl_ca_path: Optional[str] = Field(None, env="RABBITMQ_SSL_CA_PATH")
    
    # Apache Kafka configuration
    kafka_bootstrap_servers: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_security_protocol: str = Field("PLAINTEXT", env="KAFKA_SECURITY_PROTOCOL")
    kafka_sasl_mechanism: Optional[str] = Field(None, env="KAFKA_SASL_MECHANISM")
    kafka_sasl_username: Optional[str] = Field(None, env="KAFKA_SASL_USERNAME")
    kafka_sasl_password: Optional[str] = Field(None, env="KAFKA_SASL_PASSWORD")
    kafka_ssl_cert_path: Optional[str] = Field(None, env="KAFKA_SSL_CERT_PATH")
    kafka_ssl_key_path: Optional[str] = Field(None, env="KAFKA_SSL_KEY_PATH")
    kafka_ssl_ca_path: Optional[str] = Field(None, env="KAFKA_SSL_CA_PATH")
    
    # Redis configuration
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(0, env="REDIS_DB")
    redis_ssl: bool = Field(False, env="REDIS_SSL")
    
    # NATS configuration
    nats_servers: str = Field("nats://localhost:4222", env="NATS_SERVERS")
    nats_user: Optional[str] = Field(None, env="NATS_USER")
    nats_password: Optional[str] = Field(None, env="NATS_PASSWORD")
    nats_token: Optional[str] = Field(None, env="NATS_TOKEN")
    nats_tls_cert_path: Optional[str] = Field(None, env="NATS_TLS_CERT_PATH")
    nats_tls_key_path: Optional[str] = Field(None, env="NATS_TLS_KEY_PATH")
    nats_tls_ca_path: Optional[str] = Field(None, env="NATS_TLS_CA_PATH")
    
    # AWS SQS configuration
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field("us-east-1", env="AWS_REGION")
    aws_sqs_endpoint_url: Optional[str] = Field(None, env="AWS_SQS_ENDPOINT_URL")
    
    # Azure Service Bus configuration
    azure_service_bus_connection_string: Optional[str] = Field(
        None, 
        env="AZURE_SERVICE_BUS_CONNECTION_STRING"
    )
    
    # Connection settings
    connection_timeout: int = Field(30, env="MESSAGE_BROKER_CONNECTION_TIMEOUT")
    heartbeat: int = Field(60, env="MESSAGE_BROKER_HEARTBEAT")
    blocked_connection_timeout: int = Field(300, env="MESSAGE_BROKER_BLOCKED_CONNECTION_TIMEOUT")
    socket_timeout: int = Field(10, env="MESSAGE_BROKER_SOCKET_TIMEOUT")
    
    # Pool settings
    connection_pool_size: int = Field(10, env="MESSAGE_BROKER_POOL_SIZE")
    max_connections: int = Field(100, env="MESSAGE_BROKER_MAX_CONNECTIONS")
    
    # Consumer settings
    prefetch_count: int = Field(10, env="MESSAGE_BROKER_PREFETCH_COUNT")
    consumer_timeout: int = Field(1000, env="MESSAGE_BROKER_CONSUMER_TIMEOUT")
    auto_ack: bool = Field(False, env="MESSAGE_BROKER_AUTO_ACK")
    
    # Producer settings
    confirm_delivery: bool = Field(True, env="MESSAGE_BROKER_CONFIRM_DELIVERY")
    mandatory: bool = Field(False, env="MESSAGE_BROKER_MANDATORY")
    immediate: bool = Field(False, env="MESSAGE_BROKER_IMMEDIATE")
    
    # Retry settings
    retry_enabled: bool = Field(True, env="MESSAGE_BROKER_RETRY_ENABLED")
    max_retries: int = Field(3, env="MESSAGE_BROKER_MAX_RETRIES")
    retry_delay: int = Field(5, env="MESSAGE_BROKER_RETRY_DELAY")
    retry_backoff_multiplier: float = Field(2.0, env="MESSAGE_BROKER_RETRY_BACKOFF_MULTIPLIER")
    
    # Dead letter settings
    dead_letter_enabled: bool = Field(True, env="MESSAGE_BROKER_DEAD_LETTER_ENABLED")
    dead_letter_exchange: str = Field("dlx", env="MESSAGE_BROKER_DEAD_LETTER_EXCHANGE")
    dead_letter_queue: str = Field("dlq", env="MESSAGE_BROKER_DEAD_LETTER_QUEUE")
    
    # Monitoring settings
    metrics_enabled: bool = Field(True, env="MESSAGE_BROKER_METRICS_ENABLED")
    health_check_enabled: bool = Field(True, env="MESSAGE_BROKER_HEALTH_CHECK_ENABLED")
    health_check_interval: int = Field(30, env="MESSAGE_BROKER_HEALTH_CHECK_INTERVAL")
    
    # Serialization
    default_serializer: str = Field("json", env="MESSAGE_BROKER_DEFAULT_SERIALIZER")
    compression_enabled: bool = Field(True, env="MESSAGE_BROKER_COMPRESSION_ENABLED")
    compression_type: str = Field("gzip", env="MESSAGE_BROKER_COMPRESSION_TYPE")
    
    class Config:
        env_prefix = "MESSAGE_BROKER_"
        case_sensitive = False
    
    @validator("broker_type")
    def validate_broker_type(cls, v):
        if v not in MessageBrokerType:
            raise ValueError(f"Invalid broker type: {v}")
        return v
    
    def get_connection_url(self) -> str:
        """Get connection URL based on broker type."""
        if self.broker_type == MessageBrokerType.RABBITMQ:
            protocol = "amqps" if self.rabbitmq_ssl_enabled else "amqp"
            return (
                f"{protocol}://{self.rabbitmq_username}:{self.rabbitmq_password}@"
                f"{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_virtual_host}"
            )
        elif self.broker_type == MessageBrokerType.REDIS:
            protocol = "rediss" if self.redis_ssl else "redis"
            auth = f":{self.redis_password}@" if self.redis_password else ""
            return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
        elif self.broker_type == MessageBrokerType.APACHE_KAFKA:
            return self.kafka_bootstrap_servers
        elif self.broker_type == MessageBrokerType.NATS:
            return self.nats_servers
        else:
            raise ValueError(f"Unsupported broker type: {self.broker_type}")
    
    def get_broker_config(self) -> Dict[str, Any]:
        """Get complete broker configuration."""
        return {
            "broker_type": self.broker_type,
            "connection_url": self.get_connection_url(),
            "connection": {
                "timeout": self.connection_timeout,
                "heartbeat": self.heartbeat,
                "blocked_timeout": self.blocked_connection_timeout,
                "socket_timeout": self.socket_timeout,
            },
            "pool": {
                "size": self.connection_pool_size,
                "max_connections": self.max_connections,
            },
            "consumer": {
                "prefetch_count": self.prefetch_count,
                "timeout": self.consumer_timeout,
                "auto_ack": self.auto_ack,
            },
            "producer": {
                "confirm_delivery": self.confirm_delivery,
                "mandatory": self.mandatory,
                "immediate": self.immediate,
            },
            "retry": {
                "enabled": self.retry_enabled,
                "max_retries": self.max_retries,
                "delay": self.retry_delay,
                "backoff_multiplier": self.retry_backoff_multiplier,
            },
            "dead_letter": {
                "enabled": self.dead_letter_enabled,
                "exchange": self.dead_letter_exchange,
                "queue": self.dead_letter_queue,
            },
            "monitoring": {
                "metrics_enabled": self.metrics_enabled,
                "health_check_enabled": self.health_check_enabled,
                "health_check_interval": self.health_check_interval,
            },
            "serialization": {
                "default_serializer": self.default_serializer,
                "compression_enabled": self.compression_enabled,
                "compression_type": self.compression_type,
            }
        }


# Pre-configured exchanges for IA-Influencer Agent microservices
MICROSERVICE_EXCHANGES = {
    "ia.platform": ExchangeConfig(
        name="ia.platform",
        type=ExchangeType.TOPIC,
        durable=True
    ),
    "ia.spotify": ExchangeConfig(
        name="ia.spotify",
        type=ExchangeType.TOPIC,
        durable=True
    ),
    "ia.content.protection": ExchangeConfig(
        name="ia.content.protection",
        type=ExchangeType.TOPIC,
        durable=True
    ),
    "ia.fingerprinting": ExchangeConfig(
        name="ia.fingerprinting",
        type=ExchangeType.DIRECT,
        durable=True
    ),
    "ia.crawler": ExchangeConfig(
        name="ia.crawler",
        type=ExchangeType.TOPIC,
        durable=True
    ),
    "ia.monetization": ExchangeConfig(
        name="ia.monetization",
        type=ExchangeType.DIRECT,
        durable=True
    ),
    "ia.notifications": ExchangeConfig(
        name="ia.notifications",
        type=ExchangeType.FANOUT,
        durable=True
    ),
    "ia.analytics": ExchangeConfig(
        name="ia.analytics",
        type=ExchangeType.TOPIC,
        durable=True
    ),
    "ia.dlx": ExchangeConfig(
        name="ia.dlx",
        type=ExchangeType.DIRECT,
        durable=True
    )
}

# Pre-configured queues for IA-Influencer Agent microservices
MICROSERVICE_QUEUES = {
    # API Gateway queues
    "api.gateway.auth": QueueConfig(
        name="api.gateway.auth",
        durable=True,
        max_length=10000,
        message_ttl=300000,  # 5 minutes
        dead_letter_exchange="ia.dlx",
        dead_letter_routing_key="api.gateway.auth.failed"
    ),
    "api.gateway.rate.limit": QueueConfig(
        name="api.gateway.rate.limit",
        durable=True,
        max_length=50000,
        message_ttl=60000,  # 1 minute
    ),
    
    # Spotify Agent queues
    "spotify.analytics.process": QueueConfig(
        name="spotify.analytics.process",
        durable=True,
        max_length=5000,
        message_ttl=1800000,  # 30 minutes
        dead_letter_exchange="ia.dlx",
        dead_letter_routing_key="spotify.analytics.failed"
    ),
    "spotify.recommendations.generate": QueueConfig(
        name="spotify.recommendations.generate",
        durable=True,
        max_length=3000,
        message_ttl=900000,  # 15 minutes
    ),
    "spotify.content.sync": QueueConfig(
        name="spotify.content.sync",
        durable=True,
        max_length=10000,
        message_ttl=3600000,  # 1 hour
    ),
    
    # Content Protection queues
    "protection.content.scan": QueueConfig(
        name="protection.content.scan",
        durable=True,
        max_length=20000,
        message_ttl=7200000,  # 2 hours
        dead_letter_exchange="ia.dlx",
        dead_letter_routing_key="protection.scan.failed"
    ),
    "protection.violation.detected": QueueConfig(
        name="protection.violation.detected",
        durable=True,
        max_length=5000,
        message_ttl=604800000,  # 1 week
    ),
    "protection.takedown.request": QueueConfig(
        name="protection.takedown.request",
        durable=True,
        max_length=2000,
        message_ttl=2592000000,  # 30 days
    ),
    
    # Fingerprinting queues
    "fingerprint.audio.process": QueueConfig(
        name="fingerprint.audio.process",
        durable=True,
        max_length=10000,
        message_ttl=1800000,  # 30 minutes
        dead_letter_exchange="ia.dlx",
        dead_letter_routing_key="fingerprint.audio.failed"
    ),
    "fingerprint.video.process": QueueConfig(
        name="fingerprint.video.process",
        durable=True,
        max_length=5000,
        message_ttl=3600000,  # 1 hour
    ),
    "fingerprint.image.process": QueueConfig(
        name="fingerprint.image.process",
        durable=True,
        max_length=15000,
        message_ttl=900000,  # 15 minutes
    ),
    "fingerprint.text.process": QueueConfig(
        name="fingerprint.text.process",
        durable=True,
        max_length=20000,
        message_ttl=600000,  # 10 minutes
    ),
    
    # Web Crawler queues
    "crawler.youtube.scan": QueueConfig(
        name="crawler.youtube.scan",
        durable=True,
        max_length=50000,
        message_ttl=3600000,  # 1 hour
    ),
    "crawler.instagram.scan": QueueConfig(
        name="crawler.instagram.scan",
        durable=True,
        max_length=30000,
        message_ttl=3600000,  # 1 hour
    ),
    "crawler.tiktok.scan": QueueConfig(
        name="crawler.tiktok.scan",
        durable=True,
        max_length=40000,
        message_ttl=3600000,  # 1 hour
    ),
    "crawler.generic.scan": QueueConfig(
        name="crawler.generic.scan",
        durable=True,
        max_length=10000,
        message_ttl=7200000,  # 2 hours
    ),
    
    # Monetization queues
    "monetization.revenue.calculate": QueueConfig(
        name="monetization.revenue.calculate",
        durable=True,
        max_length=5000,
        message_ttl=86400000,  # 24 hours
        dead_letter_exchange="ia.dlx",
        dead_letter_routing_key="monetization.revenue.failed"
    ),
    "monetization.payment.process": QueueConfig(
        name="monetization.payment.process",
        durable=True,
        max_length=2000,
        message_ttl=604800000,  # 1 week
    ),
    "monetization.licensing.request": QueueConfig(
        name="monetization.licensing.request",
        durable=True,
        max_length=1000,
        message_ttl=2592000000,  # 30 days
    ),
    
    # Notification queues
    "notifications.email.send": QueueConfig(
        name="notifications.email.send",
        durable=True,
        max_length=20000,
        message_ttl=3600000,  # 1 hour
    ),
    "notifications.websocket.broadcast": QueueConfig(
        name="notifications.websocket.broadcast",
        durable=False,
        max_length=50000,
        message_ttl=300000,  # 5 minutes
    ),
    "notifications.push.send": QueueConfig(
        name="notifications.push.send",
        durable=True,
        max_length=10000,
        message_ttl=1800000,  # 30 minutes
    ),
    
    # Analytics queues
    "analytics.events.process": QueueConfig(
        name="analytics.events.process",
        durable=True,
        max_length=100000,
        message_ttl=86400000,  # 24 hours
    ),
    "analytics.reports.generate": QueueConfig(
        name="analytics.reports.generate",
        durable=True,
        max_length=1000,
        message_ttl=3600000,  # 1 hour
    ),
    "analytics.metrics.aggregate": QueueConfig(
        name="analytics.metrics.aggregate",
        durable=True,
        max_length=5000,
        message_ttl=7200000,  # 2 hours
    ),
    
    # Dead letter queues
    "dlq.general": QueueConfig(
        name="dlq.general",
        durable=True,
        message_ttl=2592000000,  # 30 days
    )
}

# Pre-configured bindings for IA-Influencer Agent microservices
MICROSERVICE_BINDINGS = [
    # API Gateway bindings
    BindingConfig(
        queue="api.gateway.auth",
        exchange="ia.platform",
        routing_key="auth.*"
    ),
    BindingConfig(
        queue="api.gateway.rate.limit",
        exchange="ia.platform",
        routing_key="rate.limit.*"
    ),
    
    # Spotify Agent bindings
    BindingConfig(
        queue="spotify.analytics.process",
        exchange="ia.spotify",
        routing_key="analytics.*"
    ),
    BindingConfig(
        queue="spotify.recommendations.generate",
        exchange="ia.spotify",
        routing_key="recommendations.*"
    ),
    BindingConfig(
        queue="spotify.content.sync",
        exchange="ia.spotify",
        routing_key="content.sync"
    ),
    
    # Content Protection bindings
    BindingConfig(
        queue="protection.content.scan",
        exchange="ia.content.protection",
        routing_key="scan.*"
    ),
    BindingConfig(
        queue="protection.violation.detected",
        exchange="ia.content.protection",
        routing_key="violation.detected"
    ),
    BindingConfig(
        queue="protection.takedown.request",
        exchange="ia.content.protection",
        routing_key="takedown.request"
    ),
    
    # Fingerprinting bindings
    BindingConfig(
        queue="fingerprint.audio.process",
        exchange="ia.fingerprinting",
        routing_key="audio"
    ),
    BindingConfig(
        queue="fingerprint.video.process",
        exchange="ia.fingerprinting",
        routing_key="video"
    ),
    BindingConfig(
        queue="fingerprint.image.process",
        exchange="ia.fingerprinting",
        routing_key="image"
    ),
    BindingConfig(
        queue="fingerprint.text.process",
        exchange="ia.fingerprinting",
        routing_key="text"
    ),
    
    # Web Crawler bindings
    BindingConfig(
        queue="crawler.youtube.scan",
        exchange="ia.crawler",
        routing_key="youtube.*"
    ),
    BindingConfig(
        queue="crawler.instagram.scan",
        exchange="ia.crawler",
        routing_key="instagram.*"
    ),
    BindingConfig(
        queue="crawler.tiktok.scan",
        exchange="ia.crawler",
        routing_key="tiktok.*"
    ),
    BindingConfig(
        queue="crawler.generic.scan",
        exchange="ia.crawler",
        routing_key="generic.*"
    ),
    
    # Monetization bindings
    BindingConfig(
        queue="monetization.revenue.calculate",
        exchange="ia.monetization",
        routing_key="revenue"
    ),
    BindingConfig(
        queue="monetization.payment.process",
        exchange="ia.monetization",
        routing_key="payment"
    ),
    BindingConfig(
        queue="monetization.licensing.request",
        exchange="ia.monetization",
        routing_key="licensing"
    ),
    
    # Notification bindings (fanout - all queues receive all messages)
    BindingConfig(
        queue="notifications.email.send",
        exchange="ia.notifications",
        routing_key=""
    ),
    BindingConfig(
        queue="notifications.websocket.broadcast",
        exchange="ia.notifications",
        routing_key=""
    ),
    BindingConfig(
        queue="notifications.push.send",
        exchange="ia.notifications",
        routing_key=""
    ),
    
    # Analytics bindings
    BindingConfig(
        queue="analytics.events.process",
        exchange="ia.analytics",
        routing_key="events.*"
    ),
    BindingConfig(
        queue="analytics.reports.generate",
        exchange="ia.analytics",
        routing_key="reports.*"
    ),
    BindingConfig(
        queue="analytics.metrics.aggregate",
        exchange="ia.analytics",
        routing_key="metrics.*"
    ),
    
    # Dead letter bindings
    BindingConfig(
        queue="dlq.general",
        exchange="ia.dlx",
        routing_key="#"
    )
]


# Export configuration instance
message_broker_config = MessageBrokerConfig()
