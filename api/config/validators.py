"""
Configuration Validators - IA Influencer Agent Platform
Comprehensive validation system for all configuration components

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import re
import ipaddress
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import dns.resolver
from pathlib import Path
import os
import socket
import ssl
import requests
from datetime import datetime, timedelta

from .app_config import AppConfig
from .database_config import DatabaseConfig, RedisConfig, MongoDBConfig, ElasticsearchConfig
from .security_config import SecurityConfig
from .blockchain_config import BlockchainConfig
from .monitoring_config import MonitoringConfig
from .logging_config import LoggingConfig


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    component: str
    
    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge with another validation result"""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            component=f"{self.component},{other.component}"
        )


class BaseValidator:
    """Base configuration validator"""
    
    @staticmethod
    def validate_url(url: str, schemes: List[str] = None) -> bool:
        """Validate URL format and scheme"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            if schemes and parsed.scheme not in schemes:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 1 <= port <= 65535
    
    @staticmethod
    def validate_directory_exists(path: str, create: bool = False) -> bool:
        """Validate directory exists or can be created"""
        try:
            path_obj = Path(path)
            if path_obj.exists():
                return path_obj.is_dir()
            elif create:
                path_obj.mkdir(parents=True, exist_ok=True)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def validate_file_permissions(path: str, required_permissions: int) -> bool:
        """Validate file permissions"""
        try:
            if not os.path.exists(path):
                return False
            
            current_permissions = oct(os.stat(path).st_mode)[-3:]
            return int(current_permissions, 8) >= required_permissions
        except Exception:
            return False
    
    @staticmethod
    def test_network_connectivity(host: str, port: int, timeout: int = 5) -> bool:
        """Test network connectivity to host:port"""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.error, socket.timeout):
            return False
    
    @staticmethod
    def validate_ssl_certificate(host: str, port: int = 443) -> bool:
        """Validate SSL certificate"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    return cert is not None
        except Exception:
            return False
    
    @staticmethod
    def validate_dns_resolution(hostname: str) -> bool:
        """Validate DNS resolution"""
        try:
            dns.resolver.resolve(hostname, 'A')
            return True
        except Exception:
            return False


class ConfigValidator(BaseValidator):
    """Main application configuration validator"""
    
    @classmethod
    def validate_app_config(cls, config: AppConfig) -> ValidationResult:
        """Validate main application configuration"""
        result = ValidationResult(True, [], [], "app_config")
        
        # Basic validation
        if not config.app_name:
            result.add_error("Application name is required")
        
        if not config.app_version:
            result.add_error("Application version is required")
        
        # Environment validation
        valid_environments = ["development", "testing", "staging", "production"]
        if config.environment not in valid_environments:
            result.add_error(f"Invalid environment: {config.environment}")
        
        # Host and port validation
        if not cls.validate_ip_address(config.host) and config.host not in ["localhost", "0.0.0.0"]:
            result.add_warning(f"Host {config.host} may not be a valid IP address")
        
        if not cls.validate_port(config.port):
            result.add_error(f"Invalid port: {config.port}")
        
        # Worker validation
        if config.workers < 1:
            result.add_error("Worker count must be at least 1")
        elif config.workers > 32:
            result.add_warning("High worker count may cause resource issues")
        
        # Security validation
        if len(config.secret_key) < 32:
            result.add_error("Secret key must be at least 32 characters")
        
        if len(config.jwt_secret) < 32:
            result.add_error("JWT secret must be at least 32 characters")
        
        # CORS validation
        for origin in config.cors_origins:
            if origin != "*" and not cls.validate_url(origin, ["http", "https"]):
                result.add_error(f"Invalid CORS origin: {origin}")
        
        # Database URL validation
        if not cls.validate_url(config.database_url, ["postgresql", "postgres"]):
            result.add_error("Invalid database URL")
        
        # Redis URL validation
        if not cls.validate_url(config.redis_url, ["redis", "rediss"]):
            result.add_error("Invalid Redis URL")
        
        # MongoDB URL validation
        if not cls.validate_url(config.mongodb_url, ["mongodb", "mongodb+srv"]):
            result.add_error("Invalid MongoDB URL")
        
        # Elasticsearch URL validation
        if not cls.validate_url(config.elasticsearch_url, ["http", "https"]):
            result.add_error("Invalid Elasticsearch URL")
        
        # Storage validation
        if config.storage_type == "s3":
            if not config.s3_access_key or not config.s3_secret_key:
                result.add_error("S3 credentials are required when using S3 storage")
            if not config.s3_bucket_name:
                result.add_error("S3 bucket name is required")
        elif config.storage_type == "local":
            if not cls.validate_directory_exists(config.local_storage_path, create=True):
                result.add_error(f"Cannot create local storage directory: {config.local_storage_path}")
        
        # Logging validation
        if not cls.validate_directory_exists(os.path.dirname(config.log_file_path), create=True):
            result.add_error(f"Cannot create log directory: {os.path.dirname(config.log_file_path)}")
        
        # Business validation
        total_commission = config.creator_commission_rate + config.platform_commission_rate
        if total_commission > 1.0:
            result.add_error("Total commission rates exceed 100%")
        elif total_commission > 0.5:
            result.add_warning("High total commission rates may reduce competitiveness")
        
        if config.minimum_payout_threshold <= 0:
            result.add_error("Minimum payout threshold must be positive")
        
        # Feature toggle validation
        feature_config = config.get_feature_config()
        critical_features = ["fingerprinting", "content_protection"]
        for feature in critical_features:
            if not feature_config.get(feature, True):
                result.add_warning(f"Critical feature '{feature}' is disabled")
        
        return result


class DatabaseConfigValidator(BaseValidator):
    """Database configuration validator"""
    
    @classmethod
    def validate(cls, config: DatabaseConfig) -> ValidationResult:
        """Validate database configuration"""
        result = ValidationResult(True, [], [], "database_config")
        
        # Connection parameters validation
        if not config.host:
            result.add_error("Database host is required")
        elif not cls.validate_ip_address(config.host) and not cls.validate_dns_resolution(config.host):
            result.add_warning(f"Cannot resolve database host: {config.host}")
        
        if not cls.validate_port(config.port):
            result.add_error(f"Invalid database port: {config.port}")
        
        if not config.database:
            result.add_error("Database name is required")
        
        if not config.username:
            result.add_error("Database username is required")
        
        if not config.password:
            result.add_warning("Database password is not set")
        
        # Connection pool validation
        if config.max_connections < config.pool_size:
            result.add_error("Max connections must be >= pool size")
        
        if config.pool_size < 1:
            result.add_error("Pool size must be at least 1")
        
        if config.pool_overflow < 0:
            result.add_error("Pool overflow cannot be negative")
        
        # SSL validation
        valid_ssl_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if config.ssl_mode not in valid_ssl_modes:
            result.add_error(f"Invalid SSL mode: {config.ssl_mode}")
        
        # Performance validation
        if config.statement_timeout < 1000:
            result.add_warning("Very low statement timeout may cause query failures")
        
        if config.pool_recycle < 3600:
            result.add_warning("Low pool recycle time may cause unnecessary reconnections")
        
        # Network connectivity test (optional)
        if cls.test_network_connectivity(config.host, config.port):
            result.add_warning("Cannot connect to database server (may be expected in some environments)")
        
        return result
    
    @classmethod
    def validate_redis_config(cls, config: RedisConfig) -> ValidationResult:
        """Validate Redis configuration"""
        result = ValidationResult(True, [], [], "redis_config")
        
        if not config.host:
            result.add_error("Redis host is required")
        
        if not cls.validate_port(config.port):
            result.add_error(f"Invalid Redis port: {config.port}")
        
        if config.db < 0 or config.db > 15:
            result.add_error("Redis database must be between 0 and 15")
        
        if config.max_connections < 1:
            result.add_error("Redis max connections must be at least 1")
        
        if config.connection_timeout < 1:
            result.add_warning("Very low connection timeout may cause connection failures")
        
        # Test connectivity
        if not cls.test_network_connectivity(config.host, config.port):
            result.add_warning("Cannot connect to Redis server")
        
        return result


class SecurityConfigValidator(BaseValidator):
    """Security configuration validator"""
    
    @classmethod
    def validate(cls, config: SecurityConfig) -> ValidationResult:
        """Validate security configuration"""
        result = ValidationResult(True, [], [], "security_config")
        
        # Secret validation
        if len(config.secret_key) < 32:
            result.add_error("Secret key must be at least 32 characters")
        
        if len(config.jwt_secret_key) < 32:
            result.add_error("JWT secret key must be at least 32 characters")
        
        if len(config.encryption_key) < 32:
            result.add_error("Encryption key must be at least 32 characters")
        
        # Password policy validation
        if config.password_min_length < 8:
            result.add_error("Password minimum length should be at least 8")
        elif config.password_min_length < 12:
            result.add_warning("Consider increasing minimum password length to 12 or more")
        
        # JWT validation
        valid_jwt_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]
        if config.jwt_algorithm not in valid_jwt_algorithms:
            result.add_error(f"Invalid JWT algorithm: {config.jwt_algorithm}")
        
        if config.jwt_access_token_expire_minutes < 5:
            result.add_error("JWT access token expiry too short (minimum 5 minutes)")
        elif config.jwt_access_token_expire_minutes > 1440:  # 24 hours
            result.add_warning("JWT access token expiry very long (security risk)")
        
        if config.jwt_refresh_token_expire_days < 1:
            result.add_error("JWT refresh token expiry too short (minimum 1 day)")
        elif config.jwt_refresh_token_expire_days > 90:
            result.add_warning("JWT refresh token expiry very long (security risk)")
        
        # Session validation
        if config.session_timeout_minutes < 15:
            result.add_warning("Very short session timeout may affect user experience")
        elif config.session_timeout_minutes > 2880:  # 48 hours
            result.add_warning("Very long session timeout may be a security risk")
        
        # CORS validation
        if "*" in config.cors_allowed_origins:
            result.add_warning("Wildcard CORS origin is a security risk")
        
        for origin in config.cors_allowed_origins:
            if origin != "*" and not cls.validate_url(origin, ["http", "https"]):
                result.add_error(f"Invalid CORS origin: {origin}")
        
        # Authentication validation
        if config.max_login_attempts < 3:
            result.add_warning("Very low max login attempts may be too restrictive")
        elif config.max_login_attempts > 10:
            result.add_warning("High max login attempts may allow brute force attacks")
        
        if config.login_lockout_duration_minutes < 5:
            result.add_warning("Very short lockout duration may not deter attackers")
        
        # OAuth validation
        if config.oauth2_enabled:
            oauth_configs = [
                (config.google_oauth_client_id, config.google_oauth_client_secret, "Google"),
                (config.facebook_oauth_client_id, config.facebook_oauth_client_secret, "Facebook"),
                (config.github_oauth_client_id, config.github_oauth_client_secret, "GitHub")
            ]
            
            for client_id, client_secret, provider in oauth_configs:
                if client_id and not client_secret:
                    result.add_error(f"{provider} OAuth client secret is missing")
                elif client_secret and not client_id:
                    result.add_error(f"{provider} OAuth client ID is missing")
        
        # API security validation
        if config.api_key_length < 32:
            result.add_error("API key length should be at least 32 characters")
        
        if config.api_key_expire_days < 30:
            result.add_warning("Short API key expiry may cause frequent rotation issues")
        elif config.api_key_expire_days > 365:
            result.add_warning("Long API key expiry may be a security risk")
        
        # Rate limiting validation
        if config.rate_limit_enabled:
            if config.rate_limit_requests_per_minute < 10:
                result.add_warning("Very low rate limit may affect normal usage")
            elif config.rate_limit_requests_per_minute > 1000:
                result.add_warning("High rate limit may not prevent abuse")
        
        # File upload validation
        if config.max_file_size_mb <= 0:
            result.add_error("Max file size must be positive")
        elif config.max_file_size_mb > 1024:  # 1GB
            result.add_warning("Very large max file size may cause performance issues")
        
        # Content Security Policy validation
        if config.csp_enabled and not config.csp_default_src:
            result.add_error("CSP default-src directive is required when CSP is enabled")
        
        # Network security validation
        for ip_range in config.allowed_ip_ranges:
            try:
                ipaddress.ip_network(ip_range, strict=False)
            except ValueError:
                result.add_error(f"Invalid IP range: {ip_range}")
        
        return result


class BlockchainConfigValidator(BaseValidator):
    """Blockchain configuration validator"""
    
    @classmethod
    def validate(cls, config: BlockchainConfig) -> ValidationResult:
        """Validate blockchain configuration"""
        result = ValidationResult(True, [], [], "blockchain_config")
        
        # Network configuration validation
        for network, network_config in config.networks.items():
            if not cls.validate_url(network_config.rpc_url, ["http", "https", "ws", "wss"]):
                result.add_error(f"Invalid RPC URL for {network.value}: {network_config.rpc_url}")
            
            if network_config.chain_id <= 0:
                result.add_error(f"Invalid chain ID for {network.value}: {network_config.chain_id}")
            
            if not cls.validate_url(network_config.block_explorer_url, ["http", "https"]):
                result.add_error(f"Invalid block explorer URL for {network.value}")
        
        # Wallet configuration validation
        wallet_methods = [config.private_key, config.mnemonic, config.keystore_path]
        if not any(wallet_methods) and not config.development_mode:
            result.add_error("At least one wallet method (private key, mnemonic, or keystore) is required")
        
        if config.private_key:
            if len(config.private_key) != 64 and not config.private_key.startswith('0x'):
                result.add_error("Invalid private key format")
        
        if config.keystore_path and not os.path.exists(config.keystore_path):
            result.add_error(f"Keystore file not found: {config.keystore_path}")
        
        # Gas configuration validation
        if config.default_gas_limit <= 0:
            result.add_error("Gas limit must be positive")
        elif config.default_gas_limit < 21000:
            result.add_warning("Gas limit is very low and may cause transaction failures")
        
        if config.default_gas_price_gwei <= 0:
            result.add_error("Gas price must be positive")
        
        if config.max_gas_price_gwei <= config.default_gas_price_gwei:
            result.add_error("Max gas price must be greater than default gas price")
        
        # Transaction configuration validation
        if config.transaction_timeout_seconds < 30:
            result.add_warning("Very short transaction timeout may cause failures")
        elif config.transaction_timeout_seconds > 3600:
            result.add_warning("Very long transaction timeout may hang processes")
        
        if config.confirmation_blocks < 1:
            result.add_error("Confirmation blocks must be at least 1")
        elif config.confirmation_blocks > 100:
            result.add_warning("High confirmation blocks may cause long delays")
        
        # Smart contract validation
        for contract_type, networks in config.contract_addresses.items():
            for network, address in networks.items():
                if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
                    result.add_error(f"Invalid contract address for {contract_type.value} on {network.value}")
        
        # IPFS validation
        if config.ipfs_enabled:
            if not cls.validate_url(config.ipfs_gateway, ["http", "https"]):
                result.add_error("Invalid IPFS gateway URL")
            
            if not cls.validate_url(config.ipfs_api_url, ["http", "https"]):
                result.add_error("Invalid IPFS API URL")
        
        # Multi-signature validation
        if config.multi_sig_enabled:
            if config.multi_sig_threshold <= 0:
                result.add_error("Multi-sig threshold must be positive")
            
            if config.multi_sig_threshold > len(config.multi_sig_owners):
                result.add_error("Multi-sig threshold cannot exceed number of owners")
            
            for owner in config.multi_sig_owners:
                if not re.match(r'^0x[a-fA-F0-9]{40}$', owner):
                    result.add_error(f"Invalid multi-sig owner address: {owner}")
        
        # Token configuration validation
        if config.platform_token_enabled:
            if not config.platform_token_symbol:
                result.add_error("Platform token symbol is required")
            
            if not config.platform_token_name:
                result.add_error("Platform token name is required")
            
            if config.platform_token_decimals < 0 or config.platform_token_decimals > 18:
                result.add_error("Platform token decimals must be between 0 and 18")
        
        # Staking validation
        if config.staking_enabled:
            if config.staking_rewards_apr <= 0:
                result.add_error("Staking rewards APR must be positive")
            elif config.staking_rewards_apr > 100:
                result.add_warning("Very high staking rewards may not be sustainable")
            
            if config.minimum_stake_amount <= 0:
                result.add_error("Minimum stake amount must be positive")
        
        # Governance validation
        if config.governance_enabled:
            if config.voting_period_blocks <= 0:
                result.add_error("Voting period must be positive")
            
            if config.proposal_threshold <= 0:
                result.add_error("Proposal threshold must be positive")
        
        return result


class MonitoringConfigValidator(BaseValidator):
    """Monitoring configuration validator"""
    
    @classmethod
    def validate(cls, config: MonitoringConfig) -> ValidationResult:
        """Validate monitoring configuration"""
        result = ValidationResult(True, [], [], "monitoring_config")
        
        if not config.enabled:
            result.add_warning("Monitoring is disabled")
            return result
        
        # Prometheus validation
        if config.prometheus.enabled:
            if not cls.validate_ip_address(config.prometheus.host) and not cls.validate_dns_resolution(config.prometheus.host):
                result.add_warning(f"Cannot resolve Prometheus host: {config.prometheus.host}")
            
            if not cls.validate_port(config.prometheus.port):
                result.add_error(f"Invalid Prometheus port: {config.prometheus.port}")
            
            if not config.prometheus.metrics_path.startswith('/'):
                result.add_error("Prometheus metrics path must start with '/'")
        
        # Grafana validation
        if config.grafana.enabled:
            if not cls.validate_ip_address(config.grafana.host) and not cls.validate_dns_resolution(config.grafana.host):
                result.add_warning(f"Cannot resolve Grafana host: {config.grafana.host}")
            
            if not cls.validate_port(config.grafana.port):
                result.add_error(f"Invalid Grafana port: {config.grafana.port}")
            
            if not config.grafana.admin_username:
                result.add_error("Grafana admin username is required")
            
            if not config.grafana.admin_password or config.grafana.admin_password == "admin":
                result.add_warning("Default Grafana admin password should be changed")
        
        # Jaeger validation
        if config.jaeger.enabled:
            if not cls.validate_ip_address(config.jaeger.agent_host) and not cls.validate_dns_resolution(config.jaeger.agent_host):
                result.add_warning(f"Cannot resolve Jaeger agent host: {config.jaeger.agent_host}")
            
            if not cls.validate_port(config.jaeger.agent_port):
                result.add_error(f"Invalid Jaeger agent port: {config.jaeger.agent_port}")
            
            if not cls.validate_url(config.jaeger.collector_endpoint, ["http", "https"]):
                result.add_error("Invalid Jaeger collector endpoint")
            
            if config.jaeger.sampler_param < 0 or config.jaeger.sampler_param > 1:
                result.add_error("Jaeger sampler param must be between 0 and 1")
        
        # Elasticsearch validation
        if config.elasticsearch.enabled:
            for host in config.elasticsearch.hosts:
                if ':' in host:
                    hostname, port = host.split(':')
                    if not cls.validate_ip_address(hostname) and not cls.validate_dns_resolution(hostname):
                        result.add_warning(f"Cannot resolve Elasticsearch host: {hostname}")
                    if not cls.validate_port(int(port)):
                        result.add_error(f"Invalid Elasticsearch port: {port}")
        
        # Alert validation
        if config.alerts.enabled:
            alert_channels = [
                config.alerts.email_enabled,
                config.alerts.slack_enabled,
                config.alerts.discord_enabled,
                config.alerts.webhook_enabled
            ]
            
            if not any(alert_channels):
                result.add_error("At least one alert channel must be enabled")
            
            if config.alerts.email_enabled:
                if not config.alerts.smtp_host:
                    result.add_error("SMTP host is required for email alerts")
                if not config.alerts.from_email or not cls.validate_email(config.alerts.from_email):
                    result.add_error("Valid from email is required")
                if not config.alerts.to_emails:
                    result.add_error("At least one recipient email is required")
                for email in config.alerts.to_emails:
                    if not cls.validate_email(email):
                        result.add_error(f"Invalid recipient email: {email}")
            
            if config.alerts.slack_enabled and not config.alerts.slack_webhook_url:
                result.add_error("Slack webhook URL is required for Slack alerts")
            
            if config.alerts.discord_enabled and not config.alerts.discord_webhook_url:
                result.add_error("Discord webhook URL is required for Discord alerts")
            
            if config.alerts.webhook_enabled and not config.alerts.webhook_url:
                result.add_error("Webhook URL is required for webhook alerts")
            
            # Threshold validation
            if config.alerts.cpu_threshold <= 0 or config.alerts.cpu_threshold > 100:
                result.add_error("CPU threshold must be between 0 and 100")
            
            if config.alerts.memory_threshold <= 0 or config.alerts.memory_threshold > 100:
                result.add_error("Memory threshold must be between 0 and 100")
            
            if config.alerts.disk_threshold <= 0 or config.alerts.disk_threshold > 100:
                result.add_error("Disk threshold must be between 0 and 100")
        
        # Metrics validation
        if config.system_metrics_interval < 5:
            result.add_warning("Very short system metrics interval may cause performance issues")
        
        if config.application_metrics_interval < 10:
            result.add_warning("Very short application metrics interval may cause performance issues")
        
        # Health check validation
        if config.health_check_enabled:
            if config.health_check_interval < 10:
                result.add_warning("Very frequent health checks may cause performance issues")
            
            if config.health_check_timeout >= config.health_check_interval:
                result.add_error("Health check timeout must be less than interval")
        
        # Retention validation
        if config.metrics_retention_days < 1:
            result.add_error("Metrics retention must be at least 1 day")
        elif config.metrics_retention_days > 365:
            result.add_warning("Very long metrics retention may consume significant storage")
        
        return result


class LoggingConfigValidator(BaseValidator):
    """Logging configuration validator"""
    
    @classmethod
    def validate(cls, config: LoggingConfig) -> ValidationResult:
        """Validate logging configuration"""
        result = ValidationResult(True, [], [], "logging_config")
        
        if not config.enabled:
            result.add_warning("Logging is disabled")
            return result
        
        # Log level validation
        valid_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
        if config.root_level.value not in valid_levels:
            result.add_error(f"Invalid log level: {config.root_level.value}")
        
        # Handler validation
        enabled_handlers = [
            config.console_enabled,
            config.file_enabled,
            config.syslog_handler.enabled,
            config.elasticsearch_handler.enabled,
            config.webhook_handler.enabled
        ]
        
        if not any(enabled_handlers):
            result.add_error("At least one log handler must be enabled")
        
        # File handler validation
        if config.file_enabled:
            log_dir = os.path.dirname(config.file_handler.filename)
            if not cls.validate_directory_exists(log_dir, create=True):
                result.add_error(f"Cannot create log directory: {log_dir}")
            
            if config.file_handler.max_bytes <= 0:
                result.add_error("File max bytes must be positive")
            elif config.file_handler.max_bytes < 1048576:  # 1MB
                result.add_warning("Very small log file size may cause frequent rotation")
            
            if config.file_handler.backup_count < 1:
                result.add_warning("Consider keeping at least 1 backup log file")
            elif config.file_handler.backup_count > 50:
                result.add_warning("High backup count may consume significant storage")
        
        # Syslog handler validation
        if config.syslog_handler.enabled:
            if not cls.validate_ip_address(config.syslog_handler.host) and not cls.validate_dns_resolution(config.syslog_handler.host):
                result.add_warning(f"Cannot resolve syslog host: {config.syslog_handler.host}")
            
            if not cls.validate_port(config.syslog_handler.port):
                result.add_error(f"Invalid syslog port: {config.syslog_handler.port}")
        
        # Elasticsearch handler validation
        if config.elasticsearch_handler.enabled:
            for host in config.elasticsearch_handler.hosts:
                if ':' in host:
                    hostname, port = host.split(':')
                    if not cls.validate_ip_address(hostname) and not cls.validate_dns_resolution(hostname):
                        result.add_warning(f"Cannot resolve Elasticsearch host: {hostname}")
        
        # Webhook handler validation
        if config.webhook_handler.enabled:
            if not config.webhook_handler.url:
                result.add_error("Webhook URL is required when webhook logging is enabled")
            elif not cls.validate_url(config.webhook_handler.url, ["http", "https"]):
                result.add_error("Invalid webhook URL")
            
            if config.webhook_handler.timeout <= 0:
                result.add_error("Webhook timeout must be positive")
            elif config.webhook_handler.timeout > 60:
                result.add_warning("Very long webhook timeout may cause delays")
        
        # Structured logging validation
        if config.structured.enabled:
            if config.structured.mask_sensitive_data and not config.structured.sensitive_fields:
                result.add_warning("Sensitive data masking enabled but no sensitive fields defined")
        
        # Logger configuration validation
        for logger_name, logger_config in config.logger_configs.items():
            level = logger_config.get("level")
            if level and level not in valid_levels:
                result.add_error(f"Invalid log level for logger {logger_name}: {level}")
            
            handlers = logger_config.get("handlers", [])
            if not handlers:
                result.add_warning(f"Logger {logger_name} has no handlers configured")
        
        # Sampling validation
        if config.enable_sampling:
            if config.sampling_rate <= 0 or config.sampling_rate > 1:
                result.add_error("Sampling rate must be between 0 and 1")
            elif config.sampling_rate < 0.01:
                result.add_warning("Very low sampling rate may miss important logs")
        
        return result


def validate_all_configurations(config: AppConfig) -> ValidationResult:
    """Validate all configuration components"""
    results = []
    
    # Validate main app config
    results.append(ConfigValidator.validate_app_config(config))
    
    # Validate database config
    db_config = DatabaseConfig()
    results.append(DatabaseConfigValidator.validate(db_config))
    
    # Validate security config
    security_config = SecurityConfig()
    results.append(SecurityConfigValidator.validate(security_config))
    
    # Validate monitoring config
    monitoring_config = MonitoringConfig()
    results.append(MonitoringConfigValidator.validate(monitoring_config))
    
    # Validate logging config
    logging_config = LoggingConfig()
    results.append(LoggingConfigValidator.validate(logging_config))
    
    # Merge all results
    final_result = ValidationResult(True, [], [], "all_configurations")
    for result in results:
        final_result = final_result.merge(result)
    
    return final_result
