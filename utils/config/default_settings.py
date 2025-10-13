"""
Default Configuration Settings
=============================

Enterprise default configuration settings with environment-specific defaults
and intelligent fallback strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, Optional, Union
import os
from pathlib import Path

class DefaultSettings:
    """
    Enterprise default configuration settings manager.
    
    Provides intelligent defaults for all configuration categories with
    environment-aware fallbacks and enterprise security standards.
    """
    
    @staticmethod
    def get_performance_defaults() -> Dict[str, Any]:
        """Get default performance configuration."""
        return {
            "performance_targets": {
                "cache_operations_p95": 1,
                "encryption_operations_p95": 5,
                "validation_operations_p95": 2,
                "database_operations_p95": 50,
                "file_operations_p95": 100,
                "utility_functions_p95": 10,
                "cache_operations_p99": 2,
                "encryption_operations_p99": 10,
                "validation_operations_p99": 5,
                "database_operations_p99": 100,
                "file_operations_p99": 200,
                "utility_functions_p99": 20,
                "cache_ops_per_second": 10000,
                "encryption_ops_per_second": 1000,
                "validation_ops_per_second": 5000
            },
            "memory": {
                "max_heap_size_mb": 512,
                "max_cache_size_mb": 100,
                "max_buffer_size_mb": 50,
                "gc_strategy": "generational",
                "gc_threshold": 0.8,
                "enable_memory_pools": True,
                "pool_sizes": {
                    "small_objects": 1024,
                    "medium_objects": 256,
                    "large_objects": 64
                }
            },
            "cpu": {
                "max_worker_threads": 8,
                "io_thread_pool_size": 16,
                "cpu_thread_pool_size": 4,
                "enable_cpu_affinity": True,
                "cpu_cores": [0, 1, 2, 3]
            },
            "io": {
                "max_concurrent_operations": 1000,
                "buffer_size_kb": 64,
                "enable_io_batching": True,
                "batch_size": 100,
                "database_pool_size": 20,
                "redis_pool_size": 15,
                "http_pool_size": 50
            }
        }
        
    @staticmethod
    def get_security_defaults() -> Dict[str, Any]:
        """Get default security configuration."""
        return {
            "encryption": {
                "symmetric_algorithm": "AES-256-GCM",
                "asymmetric_algorithm": "RSA-4096",
                "key_rotation_days": 90,
                "kdf_iterations": 100000
            },
            "authentication": {
                "jwt_algorithm": "HS256",
                "access_token_expire_minutes": 15,
                "refresh_token_expire_days": 30,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "password_min_length": 12,
                "require_mfa": True
            },
            "validation": {
                "max_input_size": 10485760,  # 10MB
                "scan_for_xss": True,
                "scan_for_sql_injection": True,
                "scan_for_nosql_injection": True,
                "check_file_headers": True
            }
        }
        
    @staticmethod
    def get_database_defaults() -> Dict[str, Any]:
        """Get default database configuration."""
        return {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "connection_validation": True,
            "idle_timeout_seconds": 300,
            "max_lifetime_seconds": 1800,
            "batch_size": 1000,
            "bulk_insert_size": 10000,
            "enable_query_cache": True,
            "query_cache_size_mb": 50,
            "statement_cache_size": 1000
        }
        
    @staticmethod
    def get_cache_defaults() -> Dict[str, Any]:
        """Get default cache configuration."""
        return {
            "l1_max_size": 1000,
            "l1_ttl_seconds": 300,
            "l2_ttl_seconds": 3600,
            "enable_compression": True,
            "l1_cache": {
                "algorithm": "lru",
                "max_entries": 2000,
                "ttl_seconds": 300
            },
            "l2_cache": {
                "algorithm": "lfu",
                "max_memory_mb": 100,
                "ttl_seconds": 3600
            },
            "enable_cache_warming": True,
            "warming_threads": 2,
            "eviction_policy": "adaptive",
            "eviction_threshold": 0.9
        }
        
    @staticmethod
    def get_monitoring_defaults() -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            "cpu_threshold": 80.0,
            "memory_threshold": 80.0,
            "disk_threshold": 90.0,
            "enable_prometheus": True,
            "metrics_retention_days": 30,
            "enable_alerts": True,
            "alert_channels": ["email", "slack"],
            "enable_profiling": True,
            "profiling_interval_seconds": 60,
            "metrics_buffer_size": 10000,
            "metrics_flush_interval_seconds": 10,
            "cpu_alert_threshold": 80,
            "memory_alert_threshold": 85,
            "latency_alert_threshold_ms": 100
        }
        
    @staticmethod
    def get_creator_economy_defaults() -> Dict[str, Any]:
        """Get default creator economy configuration."""
        return {
            "content_processing": {
                "max_file_size_mb": 100,
                "supported_formats": ["image", "video", "audio", "text"],
                "processing_timeout_seconds": 300,
                "quality_settings": {
                    "image_quality": 85,
                    "video_crf": 23,
                    "audio_bitrate": "192k"
                }
            },
            "collaboration": {
                "max_collaborators": 10,
                "invitation_timeout_hours": 24,
                "permission_levels": ["viewer", "editor", "admin"],
                "enable_real_time_sync": True
            },
            "monetization": {
                "commission_rate": 0.15,
                "minimum_payout": 10.0,
                "payout_frequency_days": 7,
                "supported_currencies": ["USD", "EUR", "GBP"]
            },
            "seo": {
                "auto_generate_meta": True,
                "optimize_images": True,
                "enable_sitemap": True,
                "canonical_urls": True
            }
        }
        
    @staticmethod
    def get_file_management_defaults() -> Dict[str, Any]:
        """Get default file management configuration."""
        return {
            "max_file_size_mb": 100,
            "allowed_extensions": [
                ".txt", ".pdf", ".doc", ".docx",
                ".jpg", ".jpeg", ".png", ".gif", ".webp",
                ".mp4", ".avi", ".mov", ".mkv",
                ".mp3", ".wav", ".flac", ".aac"
            ],
            "blocked_extensions": [
                ".exe", ".bat", ".sh", ".php", ".js", ".html"
            ],
            "scan_for_malware": True,
            "temp_directory": "/tmp/iacherie_uploads",
            "enable_optimization": True
        }
        
    @staticmethod
    def get_rate_limiting_defaults() -> Dict[str, Any]:
        """Get default rate limiting configuration."""
        return {
            "default_rpm": 60,  # requests per minute
            "burst_rpm": 120,
            "algorithm": "token_bucket",
            "enable_per_user_limits": True,
            "whitelist_ips": [],
            "blacklist_ips": []
        }
        
    @staticmethod
    def get_circuit_breaker_defaults() -> Dict[str, Any]:
        """Get default circuit breaker configuration."""
        return {
            "failure_threshold": 5,
            "timeout_seconds": 60,
            "half_open_max_calls": 3,
            "enable_monitoring": True
        }
        
    @staticmethod
    def get_logging_defaults() -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            "level": "INFO",
            "structured_logging": True,
            "log_encryption": True,
            "audit_logging": True,
            "retention_days": 365,
            "max_file_size_mb": 100,
            "backup_count": 5
        }
        
    @staticmethod
    def get_compliance_defaults() -> Dict[str, Any]:
        """Get default compliance configuration."""
        return {
            "gdpr_enabled": True,
            "sox_enabled": True,
            "iso27001_enabled": True,
            "owasp_enabled": True,
            "nist_enabled": True,
            "data_retention_days": 2555,  # 7 years
            "anonymization_enabled": True
        }
        
    @staticmethod
    def get_environment_defaults(environment: str = "development") -> Dict[str, Any]:
        """Get environment-specific default configuration."""
        base_defaults = {
            "environment": environment,
            "debug": environment in ["development", "testing"],
            "testing": environment == "testing",
            "production": environment == "production"
        }
        
        if environment == "development":
            base_defaults.update({
                "log_level": "DEBUG",
                "enable_profiling": True,
                "enable_hot_reload": True,
                "security_level": "medium"
            })
        elif environment == "staging":
            base_defaults.update({
                "log_level": "INFO",
                "enable_profiling": True,
                "enable_hot_reload": False,
                "security_level": "high"
            })
        elif environment == "production":
            base_defaults.update({
                "log_level": "WARNING",
                "enable_profiling": False,
                "enable_hot_reload": False,
                "security_level": "maximum"
            })
        elif environment == "testing":
            base_defaults.update({
                "log_level": "ERROR",
                "enable_profiling": False,
                "enable_hot_reload": False,
                "security_level": "medium"
            })
            
        return base_defaults
        
    @classmethod
    def get_all_defaults(cls, environment: str = "development") -> Dict[str, Any]:
        """Get complete default configuration for environment."""
        return {
            "environment": cls.get_environment_defaults(environment),
            "performance": cls.get_performance_defaults(),
            "security": cls.get_security_defaults(),
            "database": cls.get_database_defaults(),
            "cache": cls.get_cache_defaults(),
            "monitoring": cls.get_monitoring_defaults(),
            "creator_economy": cls.get_creator_economy_defaults(),
            "file_management": cls.get_file_management_defaults(),
            "rate_limiting": cls.get_rate_limiting_defaults(),
            "circuit_breaker": cls.get_circuit_breaker_defaults(),
            "logging": cls.get_logging_defaults(),
            "compliance": cls.get_compliance_defaults()
        }
        
    @staticmethod
    def get_override_for_environment(environment: str) -> Dict[str, Any]:
        """Get environment-specific configuration overrides."""
        overrides = {}
        
        if environment == "production":
            overrides.update({
                "security.authentication.require_mfa": True,
                "security.encryption.key_rotation_days": 30,
                "security.validation.max_input_size": 5242880,  # 5MB
                "performance.memory.max_heap_size_mb": 1024,
                "cache.l1_max_size": 2000,
                "cache.l2_ttl_seconds": 7200,
                "monitoring.cpu_threshold": 70.0,
                "monitoring.memory_threshold": 75.0,
                "rate_limiting.default_rpm": 30
            })
        elif environment == "staging":
            overrides.update({
                "security.authentication.require_mfa": False,
                "performance.memory.max_heap_size_mb": 768,
                "cache.l1_max_size": 1500,
                "monitoring.cpu_threshold": 75.0,
                "rate_limiting.default_rpm": 100
            })
        elif environment == "development":
            overrides.update({
                "security.authentication.require_mfa": False,
                "security.validation.scan_for_xss": False,
                "performance.memory.max_heap_size_mb": 256,
                "cache.l1_max_size": 500,
                "rate_limiting.default_rpm": 1000,
                "file_management.scan_for_malware": False
            })
            
        return overrides
        
    @staticmethod
    def validate_defaults() -> bool:
        """Validate that all default configurations are valid."""
        try:
            environments = ["development", "staging", "production", "testing"]
            
            for env in environments:
                defaults = DefaultSettings.get_all_defaults(env)
                overrides = DefaultSettings.get_override_for_environment(env)
                
                # Basic validation checks
                assert isinstance(defaults, dict), f"Invalid defaults for {env}"
                assert isinstance(overrides, dict), f"Invalid overrides for {env}"
                
                # Check required sections exist
                required_sections = [
                    "performance", "security", "database", "cache", 
                    "monitoring", "creator_economy"
                ]
                
                for section in required_sections:
                    assert section in defaults, f"Missing section {section} in {env}"
                    
            return True
        except Exception as e:
            import logging
            logging.error(f"Default configuration validation failed: {e}")
            return False