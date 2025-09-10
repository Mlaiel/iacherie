"""
Redis Configuration
Redis cache and session storage configuration
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    """Redis-specific settings"""
    
    # Redis Settings
    redis_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_username: Optional[str] = None
    
    # Redis Connection Pool Settings
    redis_max_connections: int = 50
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_health_check_interval: int = 30
    
    # Redis Cache Settings
    redis_default_ttl: int = 3600  # 1 hour
    redis_key_prefix: str = "ainflue:"
    redis_serializer: str = "json"
    redis_compression: bool = False
    
    # Redis SSL Settings
    redis_ssl_enabled: bool = False
    redis_ssl_cert_path: Optional[str] = None
    redis_ssl_key_path: Optional[str] = None
    redis_ssl_ca_path: Optional[str] = None
    
    @property
    def redis_dsn(self) -> str:
        """Get Redis connection string"""
        if self.redis_url:
            return self.redis_url
        
        # Build Redis URL
        auth = ""
        if self.redis_username or self.redis_password:
            username = self.redis_username or ""
            password = self.redis_password or ""
            auth = f"{username}:{password}@" if password else f"{username}@" if username else ""
        
        protocol = "rediss" if self.redis_ssl_enabled else "redis"
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        extra = "allow"


# Redis configuration functions
def get_redis_url() -> str:
    """Get the Redis URL for connections"""
    settings = RedisSettings()
    return settings.redis_dsn


def get_redis_config() -> dict:
    """Get Redis configuration as dictionary"""
    settings = RedisSettings()
    return {
        "url": settings.redis_dsn,
        "host": settings.redis_host,
        "port": settings.redis_port,
        "db": settings.redis_db,
        "password": settings.redis_password,
        "username": settings.redis_username,
        "max_connections": settings.redis_max_connections,
        "socket_timeout": settings.redis_socket_timeout,
        "socket_connect_timeout": settings.redis_socket_connect_timeout,
        "health_check_interval": settings.redis_health_check_interval,
        "default_ttl": settings.redis_default_ttl,
        "key_prefix": settings.redis_key_prefix,
        "ssl": settings.redis_ssl_enabled,
    }


# Redis settings instance
redis_settings = RedisSettings()

class RedisConfiguration:
    """Redis configuration manager for Ainflue platform"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.settings = redis_settings
        
    def get_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return get_redis_config()
    
    def get_url(self) -> str:
        """Get Redis URL"""
        return get_redis_url()

__all__ = [
    "RedisSettings", 
    "RedisConfiguration",
    "redis_settings", 
    "get_redis_url", 
    "get_redis_config"
]