"""
Nginx Load Balancer Manager for IA Influencer Agent

Provides enterprise-grade Nginx configuration and management for high-traffic
content protection, fingerprinting, and monetization services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import os
import subprocess
import tempfile
import asyncio
import aiofiles
import psutil
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import yaml
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import jinja2
from urllib.parse import urlparse
import ssl
import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
import redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import re
from ipaddress import IPv4Address, IPv6Address, AddressValueError

logger = logging.getLogger(__name__)

# Prometheus metrics
NGINX_REQUESTS_TOTAL = Counter('nginx_requests_total', 'Total requests processed by nginx', ['method', 'status', 'endpoint'])
NGINX_REQUEST_DURATION = Histogram('nginx_request_duration_seconds', 'Nginx request duration', ['endpoint'])
NGINX_ACTIVE_CONNECTIONS = Gauge('nginx_active_connections', 'Number of active connections')
NGINX_UPSTREAM_STATUS = Gauge('nginx_upstream_status', 'Upstream server status', ['upstream', 'server'])
NGINX_CACHE_HIT_RATIO = Gauge('nginx_cache_hit_ratio', 'Cache hit ratio')
NGINX_ERROR_RATE = Gauge('nginx_error_rate', 'Error rate per minute')

# Service discovery configuration
PLATFORM_SERVICES = {
    'fingerprinting': {
        'port_base': 8001,
        'health_endpoint': '/api/v1/health',
        'instances': 3,
        'paths': ['/api/v1/fingerprint', '/api/v1/audio', '/api/v1/video', '/api/v1/image']
    },
    'protection': {
        'port_base': 8002,
        'health_endpoint': '/api/v1/health',
        'instances': 2,
        'paths': ['/api/v1/protect', '/api/v1/monitor', '/api/v1/alerts']
    },
    'monetization': {
        'port_base': 8003,
        'health_endpoint': '/api/v1/health',
        'instances': 2,
        'paths': ['/api/v1/revenue', '/api/v1/payments', '/api/v1/analytics']
    },
    'ai_agent': {
        'port_base': 8004,
        'health_endpoint': '/api/v1/health',
        'instances': 2,
        'paths': ['/api/v1/agent', '/api/v1/recommendations', '/api/v1/spotify']
    },
    'crawlers': {
        'port_base': 8005,
        'health_endpoint': '/api/v1/health',
        'instances': 2,
        'paths': ['/api/v1/crawl', '/api/v1/youtube', '/api/v1/instagram']
    },
    'licensing': {
        'port_base': 8006,
        'health_endpoint': '/api/v1/health',
        'instances': 1,
        'paths': ['/api/v1/license', '/api/v1/contracts', '/api/v1/royalties']
    }
}


@dataclass
class UpstreamServer:
    """Upstream server configuration for load balancing"""
    host: str
    port: int
    weight: int = 1
    max_fails: int = 3
    fail_timeout: int = 30
    backup: bool = False
    down: bool = False
    health_check_path: str = "/health"
    max_conns: Optional[int] = None
    slow_start: Optional[int] = None


@dataclass
class NginxLocationConfig:
    """Nginx location block configuration"""
    path: str
    upstream_name: str
    proxy_read_timeout: int = 60
    proxy_connect_timeout: int = 60
    proxy_send_timeout: int = 60
    client_max_body_size: str = "100M"
    proxy_buffering: bool = True
    proxy_buffer_size: str = "16k"
    proxy_buffers: str = "8 16k"
    proxy_busy_buffers_size: str = "32k"
    add_headers: Dict[str, str] = None
    rate_limit: Optional[str] = None
    auth_required: bool = False
    websocket_support: bool = False


@dataclass
class SecurityConfig:
    """Security configuration for Nginx"""
    ssl_protocols: List[str] = None
    ssl_ciphers: str = "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
    ssl_prefer_server_ciphers: bool = True
    hsts_max_age: int = 31536000
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True
    content_type_options: bool = True
    frame_options: str = "DENY"
    xss_protection: bool = True
    referrer_policy: str = "strict-origin-when-cross-origin"
    
    def __post_init__(self):
        if self.ssl_protocols is None:
            self.ssl_protocols = ["TLSv1.2", "TLSv1.3"]


@dataclass
class CacheConfig:
    """Cache configuration for Nginx"""
    enabled: bool = True
    cache_path: str = "/var/cache/nginx/influencer_agent"
    keys_zone_name: str = "influencer_cache"
    keys_zone_size: str = "100m"
    max_size: str = "10g"
    inactive: str = "60m"
    use_temp_path: bool = False
    cache_valid_200: str = "1h"
    cache_valid_404: str = "1m"
    cache_bypass_patterns: List[str] = None
    
    def __post_init__(self):
        if self.cache_bypass_patterns is None:
            self.cache_bypass_patterns = ["/api/auth", "/api/upload", "/api/streaming"]


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    enabled: bool = True
    zone_name: str = "api_limit"
    zone_size: str = "10m"
    rate: str = "10r/s"
    burst: int = 20
    nodelay: bool = True
    dry_run: bool = False
    status_code: int = 429


class NginxManager:
    """
    Enterprise-grade Nginx Load Balancer Manager
    
    Handles configuration, deployment, and monitoring of Nginx load balancer
    for IA Influencer Agent platform with focus on:
    - High-traffic content protection services
    - AI fingerprinting workloads
    - Real-time monetization APIs
    - Multi-tenant isolation
    """
    
    def __init__(
        self,
        config_path: str = "/etc/nginx",
        sites_available: str = "/etc/nginx/sites-available", 
        sites_enabled: str = "/etc/nginx/sites-enabled",
        log_path: str = "/var/log/nginx",
        cache_path: str = "/var/cache/nginx"
    ):
        self.config_path = Path(config_path)
        self.sites_available = Path(sites_available)
        self.sites_enabled = Path(sites_enabled)
        self.log_path = Path(log_path)
        self.cache_path = Path(cache_path)
        
        self.upstream_servers: Dict[str, List[UpstreamServer]] = {}
        self.locations: Dict[str, List[NginxLocationConfig]] = {}
        self.virtual_hosts: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.metrics: Dict[str, Any] = {
            "requests_per_second": 0,
            "active_connections": 0,
            "upstream_response_times": {},
            "error_rates": {},
            "cache_hit_rates": {}
        }
        
        # Template environment for Nginx configs
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=False
        )
        
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._monitoring_active = False
        self._monitor_thread = None
        
        logger.info("Nginx Manager initialized for IA Influencer Agent platform")
    
    async def initialize_platform_configuration(self) -> bool:
        """
        Initialize Nginx configuration for IA Influencer Agent platform
        Configures load balancing for all critical services
        """



        try:
            # Create directory structure
            await self._create_directory_structure()
            
            # Configure upstream servers for platform services
            await self._configure_platform_upstreams()
            
            # Setup virtual hosts for different environments
            await self._configure_platform_virtual_hosts()
            
            # Configure security settings
            await self._configure_security_settings()
            
            # Setup caching for performance
            await self._configure_caching()
            
            # Configure rate limiting
            await self._configure_rate_limiting()
            
            # Generate main configuration
            await self._generate_main_configuration()
            
            logger.info("Platform Nginx configuration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize platform configuration: {e}")
            return False
    
    async def _configure_platform_upstreams(self) -> None:
        """Configure upstream servers for all platform services"""
        
        # API Gateway services
        api_servers = [
            UpstreamServer("api-gateway-1", 8000, weight=3),
            UpstreamServer("api-gateway-2", 8000, weight=3),
            UpstreamServer("api-gateway-3", 8000, weight=2)
        ]
        await self.add_upstream("api_gateway", api_servers)
        
        # AI Fingerprinting services
        fingerprint_servers = [
            UpstreamServer("fingerprint-service-1", 8001, weight=2),
            UpstreamServer("fingerprint-service-2", 8001, weight=2),
            UpstreamServer("fingerprint-service-3", 8001, weight=1)
        ]
        await self.add_upstream("fingerprint_engine", fingerprint_servers)
        
        # Content Protection services
        protection_servers = [
            UpstreamServer("protection-service-1", 8002, weight=2),
            UpstreamServer("protection-service-2", 8002, weight=2)
        ]
        await self.add_upstream("content_protection", protection_servers)
        
        # Monetization services
        monetization_servers = [
            UpstreamServer("monetization-service-1", 8003, weight=2),
            UpstreamServer("monetization-service-2", 8003, weight=2)
        ]
        await self.add_upstream("monetization_engine", monetization_servers)
        
        # AI Analytics services
        analytics_servers = [
            UpstreamServer("analytics-service-1", 8004, weight=3),
            UpstreamServer("analytics-service-2", 8004, weight=3),
            UpstreamServer("analytics-service-3", 8004, weight=2)
        ]
        await self.add_upstream("ai_analytics", analytics_servers)
        
        # Crawler services
        crawler_servers = [
            UpstreamServer("crawler-service-1", 8005, weight=2),
            UpstreamServer("crawler-service-2", 8005, weight=2)
        ]
        await self.add_upstream("web_crawlers", crawler_servers)
        
        # WebSocket services for real-time features
        websocket_servers = [
            UpstreamServer("websocket-service-1", 8006, weight=2),
            UpstreamServer("websocket-service-2", 8006, weight=2)
        ]
        await self.add_upstream("websocket_gateway", websocket_servers)
        
        logger.info("Platform upstream servers configured")
    
    async def _configure_platform_virtual_hosts(self) -> None:
        """Configure virtual hosts for different platform environments"""
        
        # Main API virtual host
        api_config = {
            "server_name": "api.influencer-agent.com",
            "ssl_enabled": True,
            "ssl_certificate": "/etc/ssl/certs/api.influencer-agent.com.crt",
            "ssl_certificate_key": "/etc/ssl/private/api.influencer-agent.com.key",
            "locations": [
                NginxLocationConfig(
                    path="/api/v1/",
                    upstream_name="api_gateway",
                    proxy_read_timeout=120,
                    client_max_body_size="500M",
                    rate_limit="api_limit",
                    websocket_support=False
                ),
                NginxLocationConfig(
                    path="/api/v1/fingerprint/",
                    upstream_name="fingerprint_engine",
                    proxy_read_timeout=300,
                    client_max_body_size="1G",
                    rate_limit="fingerprint_limit"
                ),
                NginxLocationConfig(
                    path="/api/v1/protection/",
                    upstream_name="content_protection",
                    proxy_read_timeout=180,
                    auth_required=True
                ),
                NginxLocationConfig(
                    path="/api/v1/monetization/",
                    upstream_name="monetization_engine",
                    proxy_read_timeout=120,
                    auth_required=True
                ),
                NginxLocationConfig(
                    path="/api/v1/analytics/",
                    upstream_name="ai_analytics",
                    proxy_read_timeout=180
                ),
                NginxLocationConfig(
                    path="/api/v1/crawlers/",
                    upstream_name="web_crawlers",
                    proxy_read_timeout=300
                )
            ]
        }
        await self.add_virtual_host("api_main", api_config)
        
        # WebSocket virtual host for real-time features
        ws_config = {
            "server_name": "ws.influencer-agent.com",
            "ssl_enabled": True,
            "ssl_certificate": "/etc/ssl/certs/ws.influencer-agent.com.crt",
            "ssl_certificate_key": "/etc/ssl/private/ws.influencer-agent.com.key",
            "locations": [
                NginxLocationConfig(
                    path="/ws/",
                    upstream_name="websocket_gateway",
                    websocket_support=True,
                    auth_required=True
                )
            ]
        }
        await self.add_virtual_host("websocket_main", ws_config)
        
        # Media serving virtual host
        media_config = {
            "server_name": "media.influencer-agent.com",
            "ssl_enabled": True,
            "ssl_certificate": "/etc/ssl/certs/media.influencer-agent.com.crt",
            "ssl_certificate_key": "/etc/ssl/private/media.influencer-agent.com.key",
            "static_files": True,
            "media_root": "/var/media/influencer-agent",
            "cache_enabled": True
        }
        await self.add_virtual_host("media_server", media_config)
        
        logger.info("Platform virtual hosts configured")
    
    async def add_upstream(self, name: str, servers: List[UpstreamServer]) -> bool:
        """Add or update upstream server group"""



        try:
            self.upstream_servers[name] = servers
            
            # Validate servers
            valid_servers = []
            for server in servers:
                if await self._validate_upstream_server(server):
                    valid_servers.append(server)
                else:
                    logger.warning(f"Server {server.host}:{server.port} validation failed")
            
            if not valid_servers:
                raise ValueError(f"No valid servers found for upstream {name}")
            
            self.upstream_servers[name] = valid_servers
            logger.info(f"Added upstream '{name}' with {len(valid_servers)} servers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add upstream '{name}': {e}")
            return False
    
    async def _validate_upstream_server(self, server: UpstreamServer) -> bool:
        """Validate upstream server connectivity"""



        try:
            # Test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server.host, server.port))
            sock.close()
            
            if result != 0:
                return False
            
            # Test health check endpoint if specified
            if server.health_check_path:
                import aiohttp
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    url = f"http://{server.host}:{server.port}{server.health_check_path}"
                    try:
                        async with session.get(url) as response:
                            return response.status == 200
                    except:
                        return False
            
            return True
            
        except Exception:
            return False
    
    async def add_virtual_host(self, name: str, config: Dict[str, Any]) -> bool:
        """Add virtual host configuration"""



        try:
            self.virtual_hosts[name] = config
            logger.info(f"Added virtual host '{name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to add virtual host '{name}': {e}")
            return False
    
    async def _configure_security_settings(self) -> None:
        """Configure security settings for the platform"""
        self.security_config = SecurityConfig()
        logger.info("Security settings configured")
    
    async def _configure_caching(self) -> None:
        """Configure caching for performance optimization"""
        self.cache_config = CacheConfig()
        
        # Create cache directories
        cache_dir = Path(self.cache_config.cache_path)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Caching configuration applied")
    
    async def _configure_rate_limiting(self) -> None:
        """Configure rate limiting for different endpoints"""
        self.rate_limit_configs = {
            "api_limit": RateLimitConfig(
                zone_name="api_limit",
                rate="100r/s",
                burst=200
            ),
            "fingerprint_limit": RateLimitConfig(
                zone_name="fingerprint_limit", 
                rate="10r/s",
                burst=20
            ),
            "upload_limit": RateLimitConfig(
                zone_name="upload_limit",
                rate="5r/s", 
                burst=10
            )
        }
        logger.info("Rate limiting configured")
    
    async def _generate_main_configuration(self) -> bool:
        """Generate main Nginx configuration file"""



        try:
            main_config = self._build_main_config()
            
            config_file = self.config_path / "nginx.conf"
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(main_config)
            
            # Generate upstream configurations
            await self._generate_upstream_configs()
            
            # Generate virtual host configurations
            await self._generate_virtual_host_configs()
            
            logger.info("Main Nginx configuration generated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate main configuration: {e}")
            return False
    
    def _build_main_config(self) -> str:
        """Build main nginx.conf content"""
        config = f"""
# Nginx Configuration for IA Influencer Agent Platform
# Generated: {datetime.now().isoformat()}
# Author: Fahed Mlaiel <mlaiel@live.de>

user nginx;
worker_processes auto;
worker_cpu_affinity auto;
worker_rlimit_nofile 65535;

error_log {self.log_path}/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections 4096;
    use epoll;
    multi_accept on;
    accept_mutex off;
}}

http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for" '
                   'rt=$request_time uct="$upstream_connect_time" '
                   'uht="$upstream_header_time" urt="$upstream_response_time"';

    log_format json escape=json '{{
        "timestamp": "$time_iso8601",
        "remote_addr": "$remote_addr",
        "request": "$request",
        "status": $status,
        "body_bytes_sent": $body_bytes_sent,
        "request_time": $request_time,
        "upstream_response_time": "$upstream_response_time",
        "user_agent": "$http_user_agent",
        "x_forwarded_for": "$http_x_forwarded_for"
    }}';

    access_log {self.log_path}/access.log json;

    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;

    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 1G;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 32k;
    output_buffers 8 32k;
    postpone_output 1460;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;

    # Rate limiting zones
    {self._build_rate_limit_zones()}

    # Cache settings
    {self._build_cache_config()}

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers {self.security_config.ssl_ciphers};
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 5m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header X-Frame-Options {self.security_config.frame_options} always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy {self.security_config.referrer_policy} always;
    add_header Strict-Transport-Security "max-age={self.security_config.hsts_max_age}; includeSubDomains; preload" always;

    # Include upstream configurations
    include /etc/nginx/conf.d/upstreams/*.conf;

    # Include virtual host configurations
    include /etc/nginx/sites-enabled/*;
}}
"""
        return config
    
    def _build_rate_limit_zones(self) -> str:
        """Build rate limiting zones configuration"""
        zones = []
        for name, config in self.rate_limit_configs.items():
            zones.append(f"limit_req_zone $binary_remote_addr zone={config.zone_name}:{config.zone_size} rate={config.rate};")
        return "\n    ".join(zones)
    
    def _build_cache_config(self) -> str:
        """Build cache configuration"""
        if not self.cache_config.enabled:
            return ""
        
        return f"""
    proxy_cache_path {self.cache_config.cache_path} 
                     levels=1:2 
                     keys_zone={self.cache_config.keys_zone_name}:{self.cache_config.keys_zone_size}
                     max_size={self.cache_config.max_size}
                     inactive={self.cache_config.inactive}
                     use_temp_path={str(self.cache_config.use_temp_path).lower()};
    """
    
    async def _generate_upstream_configs(self) -> None:
        """Generate upstream configuration files"""
        upstream_dir = self.config_path / "conf.d" / "upstreams"
        upstream_dir.mkdir(parents=True, exist_ok=True)
        
        for name, servers in self.upstream_servers.items():
            config_content = self._build_upstream_config(name, servers)
            config_file = upstream_dir / f"{name}.conf"
            
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(config_content)
        
        logger.info(f"Generated {len(self.upstream_servers)} upstream configurations")
    
    def _build_upstream_config(self, name: str, servers: List[UpstreamServer]) -> str:
        """Build upstream configuration block"""
        config_lines = [f"upstream {name} {{"]
        
        # Add health check if available
        config_lines.append("    least_conn;")
        config_lines.append("    keepalive 32;")
        
        for server in servers:
            server_line = f"    server {server.host}:{server.port}"
            
            if server.weight != 1:
                server_line += f" weight={server.weight}"
            if server.max_fails != 3:
                server_line += f" max_fails={server.max_fails}"
            if server.fail_timeout != 30:
                server_line += f" fail_timeout={server.fail_timeout}s"
            if server.backup:
                server_line += " backup"
            if server.down:
                server_line += " down"
            if server.max_conns:
                server_line += f" max_conns={server.max_conns}"
            if server.slow_start:
                server_line += f" slow_start={server.slow_start}s"
            
            server_line += ";"
            config_lines.append(server_line)
        
        config_lines.append("}")
        return "\n".join(config_lines)
    
    async def _generate_virtual_host_configs(self) -> None:
        """Generate virtual host configuration files"""
        for name, config in self.virtual_hosts.items():
            vhost_content = self._build_virtual_host_config(name, config)
            config_file = self.sites_available / f"{name}.conf"
            
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(vhost_content)
            
            # Enable site by creating symlink
            enabled_file = self.sites_enabled / f"{name}.conf"
            if not enabled_file.exists():
                enabled_file.symlink_to(config_file)
        
        logger.info(f"Generated {len(self.virtual_hosts)} virtual host configurations")
    
    def _build_virtual_host_config(self, name: str, config: Dict[str, Any]) -> str:
        """Build virtual host configuration"""
        lines = []
        
        # Server block start
        lines.append("server {")
        lines.append(f"    server_name {config['server_name']};")
        
        # SSL configuration
        if config.get('ssl_enabled', False):
            lines.extend([
                "    listen 443 ssl http2;",
                "    listen [::]:443 ssl http2;",
                f"    ssl_certificate {config['ssl_certificate']};",
                f"    ssl_certificate_key {config['ssl_certificate_key']};",
            ])
        else:
            lines.extend([
                "    listen 80;",
                "    listen [::]:80;",
            ])
        
        # Location blocks
        locations = config.get('locations', [])
        for location in locations:
            lines.extend(self._build_location_block(location))
        
        # Static file serving for media server
        if config.get('static_files', False):
            media_root = config.get('media_root', '/var/media')
            lines.extend([
                "    location /media/ {",
                f"        alias {media_root}/;",
                "        expires 1y;",
                "        add_header Cache-Control 'public, immutable';",
                "    }"
            ])
        
        lines.append("}")
        
        # HTTP to HTTPS redirect
        if config.get('ssl_enabled', False):
            lines.extend([
                "",
                "server {",
                "    listen 80;",
                "    listen [::]:80;",
                f"    server_name {config['server_name']};",
                "    return 301 https://$server_name$request_uri;",
                "}"
            ])
        
        return "\n".join(lines)
    
    def _build_location_block(self, location: NginxLocationConfig) -> List[str]:
        """Build location block configuration"""
        lines = [f"    location {location.path} {{"]
        
        # Rate limiting
        if location.rate_limit:
            rate_config = self.rate_limit_configs.get(location.rate_limit)
            if rate_config:
                lines.append(f"        limit_req zone={rate_config.zone_name} burst={rate_config.burst}")
                if rate_config.nodelay:
                    lines[-1] += " nodelay"
                lines[-1] += ";"
        
        # Proxy settings
        lines.extend([
            f"        proxy_pass http://{location.upstream_name};",
            "        proxy_set_header Host $host;",
            "        proxy_set_header X-Real-IP $remote_addr;",
            "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            "        proxy_set_header X-Forwarded-Proto $scheme;",
            f"        proxy_read_timeout {location.proxy_read_timeout}s;",
            f"        proxy_connect_timeout {location.proxy_connect_timeout}s;",
            f"        proxy_send_timeout {location.proxy_send_timeout}s;",
            f"        client_max_body_size {location.client_max_body_size};"
        ])
        
        # WebSocket support
        if location.websocket_support:
            lines.extend([
                "        proxy_http_version 1.1;",
                "        proxy_set_header Upgrade $http_upgrade;",
                "        proxy_set_header Connection 'upgrade';",
                "        proxy_cache_bypass $http_upgrade;"
            ])
        
        # Buffering configuration
        if location.proxy_buffering:
            lines.extend([
                f"        proxy_buffer_size {location.proxy_buffer_size};",
                f"        proxy_buffers {location.proxy_buffers};",
                f"        proxy_busy_buffers_size {location.proxy_busy_buffers_size};"
            ])
        else:
            lines.append("        proxy_buffering off;")
        
        # Additional headers
        if location.add_headers:
            for header, value in location.add_headers.items():
                lines.append(f"        add_header {header} '{value}';")
        
        lines.append("    }")
        return lines
    
    async def _create_directory_structure(self) -> None:
        """Create necessary directory structure"""
        directories = [
            self.config_path,
            self.sites_available,
            self.sites_enabled,
            self.log_path,
            self.cache_path,
            self.config_path / "conf.d",
            self.config_path / "conf.d" / "upstreams"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Directory structure created")
    
    async def reload_configuration(self) -> bool:
        """Reload Nginx configuration"""



        try:
            # Test configuration first
            result = subprocess.run(
                ["nginx", "-t"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Nginx configuration test failed: {result.stderr}")
                return False
            
            # Reload configuration
            result = subprocess.run(
                ["nginx", "-s", "reload"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Nginx configuration reloaded successfully")
                return True
            else:
                logger.error(f"Failed to reload Nginx: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Nginx reload timed out")
            return False
        except Exception as e:
            logger.error(f"Error reloading Nginx configuration: {e}")
            return False
    
    async def start_monitoring(self) -> None:
        """Start monitoring Nginx performance and health"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Nginx monitoring started")
    
    def _monitoring_loop(self) -> None:
        """Monitoring loop for Nginx metrics"""
        while self._monitoring_active:
            try:
                # Collect basic metrics
                self._collect_connection_metrics()
                self._collect_log_metrics()
                self._check_upstream_health()
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_connection_metrics(self) -> None:
        """Collect connection metrics from Nginx"""



        try:
            # This would typically parse nginx status page or use nginx-prometheus-exporter
            # For now, we'll collect basic system metrics
            
            # Count nginx processes
            nginx_processes = len([p for p in psutil.process_iter(['name']) if p.info['name'] == 'nginx'])
            self.metrics['nginx_processes'] = nginx_processes
            
            # Get basic system metrics that affect nginx
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            self.metrics.update({
                'system_cpu_percent': cpu_percent,
                'system_memory_percent': memory.percent,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error collecting connection metrics: {e}")
    
    def _collect_log_metrics(self) -> None:
        """Collect metrics from Nginx logs"""



        try:
            access_log = self.log_path / "access.log"
            if not access_log.exists():
                return
            
            # Simple log parsing for recent entries
            # In production, this would use proper log parsing tools
            recent_time = datetime.now() - timedelta(minutes=5)
            
            # This is a simplified implementation
            # Real implementation would parse JSON logs and calculate proper metrics
            
        except Exception as e:
            logger.error(f"Error collecting log metrics: {e}")
    
    async def _check_upstream_health(self) -> None:
        """Check health of upstream servers"""
        health_results = {}
        
        for upstream_name, servers in self.upstream_servers.items():
            healthy_servers = 0
            total_servers = len(servers)
            
            for server in servers:
                if await self._validate_upstream_server(server):
                    healthy_servers += 1
            
            health_results[upstream_name] = {
                'healthy': healthy_servers,
                'total': total_servers,
                'health_percentage': (healthy_servers / total_servers) * 100 if total_servers > 0 else 0
            }
        
        self.metrics['upstream_health'] = health_results
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""



        return self.metrics.copy()
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self._monitoring_active = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=10)
        logger.info("Nginx monitoring stopped")
    
    async def emergency_maintenance_mode(self, enable: bool = True) -> bool:
        """Enable/disable emergency maintenance mode"""



        try:
            maintenance_config = f"""
server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    
    server_name _;
    
    ssl_certificate /etc/ssl/certs/maintenance.crt;
    ssl_certificate_key /etc/ssl/private/maintenance.key;
    
    location / {{
        return 503 'IA Influencer Agent Platform is temporarily under maintenance. Please try again later.';
        add_header Content-Type text/plain;
        add_header Retry-After 300;
    }}
}}
"""
            
            maintenance_file = self.sites_enabled / "maintenance.conf"
            
            if enable:
                # Create maintenance configuration
                async with aiofiles.open(maintenance_file, 'w') as f:
                    await f.write(maintenance_config)
                
                # Disable other sites
                for site_file in self.sites_enabled.glob("*.conf"):
                    if site_file.name != "maintenance.conf":
                        backup_file = site_file.with_suffix(".conf.disabled")
                        site_file.rename(backup_file)
                
                logger.info("Emergency maintenance mode enabled")
            else:
                # Remove maintenance configuration
                if maintenance_file.exists():
                    maintenance_file.unlink()
                
                # Re-enable other sites
                for backup_file in self.sites_enabled.glob("*.conf.disabled"):
                    site_file = backup_file.with_suffix(".conf")
                    backup_file.rename(site_file)
                
                logger.info("Emergency maintenance mode disabled")
            
            # Reload configuration
            return await self.reload_configuration()
            
        except Exception as e:
            logger.error(f"Failed to toggle maintenance mode: {e}")
            return False
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, '_monitoring_active') and self._monitoring_active:
            asyncio.create_task(self.stop_monitoring())
        
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
