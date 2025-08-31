"""
Load Balancer Configuration Manager - IA Influencer Agent Platform

Centralized configuration management for all load balancing components,
providing dynamic configuration updates, validation, and template management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import json
import yaml
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import jsonschema
from jsonschema import validate, ValidationError
import hashlib
import shutil
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfiguration:
    """Service configuration for load balancing"""
    name: str
    port: int
    instances: int
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: int = 10
    max_retries: int = 3
    weight: int = 1
    backup: bool = False
    enabled: bool = True
    ssl_enabled: bool = False
    rate_limit: Optional[str] = None
    circuit_breaker_enabled: bool = True
    session_affinity: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadBalancerConfiguration:
    """Complete load balancer configuration"""
    version: str
    environment: str
    created_at: datetime
    updated_at: datetime
    services: Dict[str, ServiceConfiguration] = field(default_factory=dict)
    nginx_config: Dict[str, Any] = field(default_factory=dict)
    haproxy_config: Dict[str, Any] = field(default_factory=dict)
    envoy_config: Dict[str, Any] = field(default_factory=dict)
    ssl_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    global_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigurationManager:
    """
    Enterprise Configuration Manager for Load Balancer
    
    Provides centralized configuration management, validation,
    template rendering, and dynamic updates for all load balancing
    components in the IA Influencer Agent platform.
    """
    
    def __init__(self, config_dir: str = "/etc/ia-influencer/load-balancer"):
        self.config_dir = Path(config_dir)
        self.templates_dir = self.config_dir / "templates"
        self.schemas_dir = self.config_dir / "schemas"
        self.backups_dir = self.config_dir / "backups"
        
        # Configuration state
        self.current_config: Optional[LoadBalancerConfiguration] = None
        self.config_file = self.config_dir / "config.yaml"
        self.config_hash = ""
        
        # Template engine
        self.jinja_env = None
        
        # Validation schemas
        self.schemas: Dict[str, Dict] = {}
        
        # Change tracking
        self.config_watchers: List[callable] = []
        self.watch_task = None
        self.is_watching = False
        
        logger.info("Configuration Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize configuration manager"""



        try:
            logger.info("Initializing Configuration Manager...")
            
            # Create directories
            await self._create_directories()
            
            # Initialize template engine
            await self._initialize_templates()
            
            # Load validation schemas
            await self._load_schemas()
            
            # Load or create configuration
            await self._load_configuration()
            
            # Start configuration watching
            await self._start_config_watching()
            
            logger.info("Configuration Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Configuration Manager: {e}")
            raise
    
    async def _create_directories(self) -> None:
        """Create necessary directories"""
        directories = [
            self.config_dir,
            self.templates_dir,
            self.schemas_dir,
            self.backups_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory created/verified: {directory}")
    
    async def _initialize_templates(self) -> None:
        """Initialize Jinja2 template environment"""
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create default templates if they don't exist
        await self._create_default_templates()
        
        logger.info("Template engine initialized")
    
    async def _create_default_templates(self) -> None:
        """Create default configuration templates"""
        templates = {
            "nginx.conf.j2": self._get_nginx_template(),
            "haproxy.cfg.j2": self._get_haproxy_template(),
            "envoy.yaml.j2": self._get_envoy_template(),
            "ssl.conf.j2": self._get_ssl_template()
        }
        
        for template_name, template_content in templates.items():
            template_file = self.templates_dir / template_name
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write(template_content)
                logger.debug(f"Created template: {template_name}")
    
    def _get_nginx_template(self) -> str:
        """Get Nginx configuration template"""



        return """
# Nginx Configuration for IA Influencer Agent Platform
# Generated at {{ generated_at }}

user nginx;
worker_processes {{ nginx_config.worker_processes | default('auto') }};
worker_connections {{ nginx_config.worker_connections | default(4096) }};

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections {{ nginx_config.worker_connections | default(4096) }};
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size {{ nginx_config.max_body_size | default('100M') }};
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript 
               text/xml application/xml application/xml+rss text/javascript;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate={{ nginx_config.rate_limit | default('10r/s') }};
    limit_req_zone $binary_remote_addr zone=upload_limit:10m rate={{ nginx_config.upload_rate_limit | default('2r/s') }};
    
    {% if ssl_config.enabled %}
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    {% endif %}
    
    # Upstream definitions
    {% for service_name, service in services.items() %}
    {% if service.enabled %}
    upstream {{ service_name }}_backend {
        {% for i in range(service.instances) %}
        server {{ service_name }}_{{ i + 1 }}:{{ service.port }} weight={{ service.weight }};
        {% endfor %}
        
        # Health checks
        keepalive 32;
        keepalive_requests 100;
        keepalive_timeout 60s;
    }
    {% endif %}
    {% endfor %}
    
    # Main server block
    server {
        listen 80;
        server_name {{ nginx_config.server_name | default('api.ia-influencer.com') }};
        
        {% if ssl_config.enabled %}
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name {{ nginx_config.server_name | default('api.ia-influencer.com') }};
        
        # SSL certificates
        ssl_certificate {{ ssl_config.cert_path }}/{{ nginx_config.server_name | default('api.ia-influencer.com') }}.crt;
        ssl_certificate_key {{ ssl_config.key_path }}/{{ nginx_config.server_name | default('api.ia-influencer.com') }}.key;
        {% endif %}
        
        # Service routes
        {% for service_name, service in services.items() %}
        {% if service.enabled %}
        location /{{ service_name }}/ {
            proxy_pass http://{{ service_name }}_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout {{ service.health_check_timeout }}s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            {% if service.rate_limit %}
            limit_req zone=api_limit burst=20 nodelay;
            {% endif %}
            
            # Health check
            location {{ service.health_check_path }} {
                access_log off;
                return 200 "healthy\\n";
                add_header Content-Type text/plain;
            }
        }
        {% endif %}
        {% endfor %}
        
        # Default location
        location / {
            return 404;
        }
    }
}
"""
    
    def _get_haproxy_template(self) -> str:
        """Get HAProxy configuration template"""



        return """
# HAProxy Configuration for IA Influencer Agent Platform
# Generated at {{ generated_at }}

global
    log stdout local0
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon
    
    # SSL settings
    {% if ssl_config.enabled %}
    ssl-default-bind-ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    {% endif %}

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option http-server-close
    option forwardfor except 127.0.0.0/8
    option redispatch
    retries 3
    timeout connect {{ haproxy_config.connect_timeout | default('10s') }}
    timeout client {{ haproxy_config.client_timeout | default('60s') }}
    timeout server {{ haproxy_config.server_timeout | default('60s') }}
    timeout http-request 10s
    timeout http-keep-alive 2s
    timeout check 10s
    
    # Error pages
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

# Statistics page
frontend stats
    bind *:{{ haproxy_config.stats_port | default(8404) }}
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if LOCALHOST

# Main frontend
frontend main_frontend
    bind *:80
    {% if ssl_config.enabled %}
    bind *:443 ssl crt {{ ssl_config.cert_path }}/{{ haproxy_config.server_name | default('api.ia-influencer.com') }}.pem
    {% endif %}
    
    # Security headers
    http-response set-header X-Frame-Options DENY
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-XSS-Protection "1; mode=block"
    
    {% if ssl_config.enabled %}
    # Redirect HTTP to HTTPS
    redirect scheme https if !{ ssl_fc }
    {% endif %}
    
    # Service routing
    {% for service_name, service in services.items() %}
    {% if service.enabled %}
    use_backend {{ service_name }}_backend if { path_beg /{{ service_name }} }
    {% endif %}
    {% endfor %}
    
    default_backend api_backend

# Backend definitions
{% for service_name, service in services.items() %}
{% if service.enabled %}
backend {{ service_name }}_backend
    balance {{ haproxy_config.balance_algorithm | default('roundrobin') }}
    option httpchk GET {{ service.health_check_path }}
    
    {% for i in range(service.instances) %}
    server {{ service_name }}_{{ i + 1 }} {{ service_name }}_{{ i + 1 }}:{{ service.port }} check inter {{ service.health_check_interval }}s fall {{ service.max_retries }} rise 2{% if service.backup %} backup{% endif %}
    {% endfor %}
{% endif %}
{% endfor %}

# Default backend
backend api_backend
    http-request return status 404 content-type "application/json" string '{"error":"Not Found","code":404}'
"""
    
    def _get_envoy_template(self) -> str:
        """Get Envoy configuration template"""



        return """
# Envoy Configuration for IA Influencer Agent Platform
# Generated at {{ generated_at }}

admin:
  address:
    socket_address:
      protocol: TCP
      address: 0.0.0.0
      port_value: {{ envoy_config.admin_port | default(9901) }}

static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        protocol: TCP
        address: 0.0.0.0
        port_value: 80
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          access_log:
          - name: envoy.access_loggers.stdout
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.access_loggers.stream.v3.StdoutAccessLog
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
          route_config:
            name: local_route
            virtual_hosts:
            - name: local_service
              domains: ["*"]
              routes:
              {% for service_name, service in services.items() %}
              {% if service.enabled %}
              - match:
                  prefix: "/{{ service_name }}"
                route:
                  cluster: {{ service_name }}_service
                  timeout: 60s
              {% endif %}
              {% endfor %}
              - match:
                  prefix: "/"
                direct_response:
                  status: 404
                  body:
                    inline_string: "Not Found"
  
  clusters:
  {% for service_name, service in services.items() %}
  {% if service.enabled %}
  - name: {{ service_name }}_service
    connect_timeout: {{ service.health_check_timeout }}s
    type: LOGICAL_DNS
    dns_lookup_family: V4_ONLY
    load_assignment:
      cluster_name: {{ service_name }}_service
      endpoints:
      - lb_endpoints:
        {% for i in range(service.instances) %}
        - endpoint:
            address:
              socket_address:
                address: {{ service_name }}_{{ i + 1 }}
                port_value: {{ service.port }}
        {% endfor %}
    health_checks:
    - timeout: {{ service.health_check_timeout }}s
      interval: {{ service.health_check_interval }}s
      unhealthy_threshold: {{ service.max_retries }}
      healthy_threshold: 2
      http_health_check:
        path: "{{ service.health_check_path }}"
  {% endif %}
  {% endfor %}
"""
    
    def _get_ssl_template(self) -> str:
        """Get SSL configuration template"""



        return """
# SSL Configuration for IA Influencer Agent Platform
# Generated at {{ generated_at }}

{% if ssl_config.enabled %}
# Certificate paths
SSL_CERT_PATH="{{ ssl_config.cert_path }}"
SSL_KEY_PATH="{{ ssl_config.key_path }}"
SSL_CA_PATH="{{ ssl_config.ca_path | default('/etc/ssl/certs/ca-certificates.crt') }}"

# Certificate domains
DOMAINS="{{ ssl_config.domains | join(' ') }}"

# Auto-renewal settings
AUTO_RENEWAL={{ ssl_config.auto_renewal | default(true) | lower }}
RENEWAL_DAYS={{ ssl_config.renewal_days | default(30) }}

# ACME settings (for Let's Encrypt)
ACME_ENABLED={{ ssl_config.acme_enabled | default(true) | lower }}
ACME_EMAIL="{{ ssl_config.acme_email | default('admin@ia-influencer.com') }}"
ACME_STAGING={{ ssl_config.acme_staging | default(false) | lower }}

# OCSP stapling
OCSP_STAPLING={{ ssl_config.ocsp_stapling | default(true) | lower }}

# HSTS settings
HSTS_ENABLED={{ ssl_config.hsts_enabled | default(true) | lower }}
HSTS_MAX_AGE={{ ssl_config.hsts_max_age | default(31536000) }}
HSTS_INCLUDE_SUBDOMAINS={{ ssl_config.hsts_include_subdomains | default(true) | lower }}
{% endif %}
"""
    
    async def _load_schemas(self) -> None:
        """Load JSON schemas for validation"""
        # Create default schemas if they don't exist
        await self._create_default_schemas()
        
        # Load schemas
        schema_files = list(self.schemas_dir.glob("*.json"))
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema_name = schema_file.stem
                    self.schemas[schema_name] = json.load(f)
                logger.debug(f"Loaded schema: {schema_name}")
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")
        
        logger.info(f"Loaded {len(self.schemas)} validation schemas")
    
    async def _create_default_schemas(self) -> None:
        """Create default JSON schemas"""
        service_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                "instances": {"type": "integer", "minimum": 1},
                "health_check_path": {"type": "string"},
                "health_check_interval": {"type": "integer", "minimum": 5},
                "health_check_timeout": {"type": "integer", "minimum": 1},
                "max_retries": {"type": "integer", "minimum": 1},
                "weight": {"type": "integer", "minimum": 1},
                "backup": {"type": "boolean"},
                "enabled": {"type": "boolean"},
                "ssl_enabled": {"type": "boolean"},
                "rate_limit": {"type": ["string", "null"]},
                "circuit_breaker_enabled": {"type": "boolean"},
                "session_affinity": {"type": "boolean"},
                "metadata": {"type": "object"}
            },
            "required": ["name", "port", "instances"],
            "additionalProperties": False
        }
        
        config_schema = {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "environment": {"type": "string"},
                "services": {
                    "type": "object",
                    "additionalProperties": service_schema
                },
                "nginx_config": {"type": "object"},
                "haproxy_config": {"type": "object"},
                "envoy_config": {"type": "object"},
                "ssl_config": {"type": "object"},
                "monitoring_config": {"type": "object"},
                "global_settings": {"type": "object"}
            },
            "required": ["version", "environment"],
            "additionalProperties": False
        }
        
        schemas = {
            "service": service_schema,
            "config": config_schema
        }
        
        for schema_name, schema in schemas.items():
            schema_file = self.schemas_dir / f"{schema_name}.json"
            if not schema_file.exists():
                with open(schema_file, 'w') as f:
                    json.dump(schema, f, indent=2)
                logger.debug(f"Created schema: {schema_name}")
    
    async def _load_configuration(self) -> None:
        """Load or create configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Validate configuration
                if "config" in self.schemas:
                    validate(config_data, self.schemas["config"])
                
                # Convert to configuration object
                self.current_config = self._dict_to_config(config_data)
                
                # Calculate configuration hash
                self.config_hash = self._calculate_config_hash(config_data)
                
                logger.info("Configuration loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                await self._create_default_configuration()
        else:
            await self._create_default_configuration()
    
    async def _create_default_configuration(self) -> None:
        """Create default configuration"""
        logger.info("Creating default configuration...")
        
        config_data = {
            "version": "1.0.0",
            "environment": "production",
            "services": {
                "fingerprinting": {
                    "name": "fingerprinting",
                    "port": 8001,
                    "instances": 3,
                    "health_check_path": "/health",
                    "health_check_interval": 30,
                    "health_check_timeout": 10,
                    "max_retries": 3,
                    "weight": 1,
                    "backup": False,
                    "enabled": True,
                    "ssl_enabled": True,
                    "rate_limit": "50r/s",
                    "circuit_breaker_enabled": True,
                    "session_affinity": True
                },
                "protection": {
                    "name": "protection",
                    "port": 8002,
                    "instances": 2,
                    "health_check_path": "/health",
                    "health_check_interval": 30,
                    "health_check_timeout": 10,
                    "max_retries": 3,
                    "weight": 1,
                    "backup": False,
                    "enabled": True,
                    "ssl_enabled": True,
                    "rate_limit": "100r/s",
                    "circuit_breaker_enabled": True,
                    "session_affinity": False
                },
                "monetization": {
                    "name": "monetization",
                    "port": 8003,
                    "instances": 2,
                    "health_check_path": "/health",
                    "health_check_interval": 30,
                    "health_check_timeout": 10,
                    "max_retries": 3,
                    "weight": 1,
                    "backup": False,
                    "enabled": True,
                    "ssl_enabled": True,
                    "rate_limit": "100r/s",
                    "circuit_breaker_enabled": True,
                    "session_affinity": True
                },
                "ai_agent": {
                    "name": "ai_agent",
                    "port": 8004,
                    "instances": 2,
                    "health_check_path": "/health",
                    "health_check_interval": 30,
                    "health_check_timeout": 10,
                    "max_retries": 3,
                    "weight": 1,
                    "backup": False,
                    "enabled": True,
                    "ssl_enabled": True,
                    "rate_limit": "50r/s",
                    "circuit_breaker_enabled": True,
                    "session_affinity": True
                },
                "crawlers": {
                    "name": "crawlers",
                    "port": 8005,
                    "instances": 2,
                    "health_check_path": "/health",
                    "health_check_interval": 30,
                    "health_check_timeout": 10,
                    "max_retries": 3,
                    "weight": 1,
                    "backup": False,
                    "enabled": True,
                    "ssl_enabled": False,
                    "rate_limit": "20r/s",
                    "circuit_breaker_enabled": True,
                    "session_affinity": False
                }
            },
            "nginx_config": {
                "worker_processes": "auto",
                "worker_connections": 4096,
                "server_name": "api.ia-influencer.com",
                "max_body_size": "100M",
                "rate_limit": "100r/s",
                "upload_rate_limit": "5r/s"
            },
            "haproxy_config": {
                "stats_port": 8404,
                "connect_timeout": "10s",
                "client_timeout": "60s",
                "server_timeout": "60s",
                "balance_algorithm": "roundrobin",
                "server_name": "api.ia-influencer.com"
            },
            "envoy_config": {
                "admin_port": 9901
            },
            "ssl_config": {
                "enabled": True,
                "cert_path": "/etc/ssl/certs",
                "key_path": "/etc/ssl/private",
                "ca_path": "/etc/ssl/certs/ca-certificates.crt",
                "domains": ["api.ia-influencer.com", "*.ia-influencer.com"],
                "auto_renewal": True,
                "renewal_days": 30,
                "acme_enabled": True,
                "acme_email": "admin@ia-influencer.com",
                "acme_staging": False,
                "ocsp_stapling": True,
                "hsts_enabled": True,
                "hsts_max_age": 31536000,
                "hsts_include_subdomains": True
            },
            "monitoring_config": {
                "enabled": True,
                "prometheus_port": 9090,
                "collection_interval": 15,
                "health_check_enabled": True,
                "metrics_enabled": True,
                "alerting_enabled": True
            },
            "global_settings": {
                "max_connections": 10000,
                "default_timeout": 60,
                "log_level": "info",
                "debug_mode": False,
                "maintenance_mode": False
            }
        }
        
        # Convert to configuration object
        self.current_config = self._dict_to_config(config_data)
        
        # Save to file
        await self.save_configuration(self.current_config)
        
        logger.info("Default configuration created")
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> LoadBalancerConfiguration:
        """Convert dictionary to configuration object"""
        services = {}
        for service_name, service_data in config_data.get("services", {}).items():
            services[service_name] = ServiceConfiguration(**service_data)
        
        return LoadBalancerConfiguration(
            version=config_data["version"],
            environment=config_data["environment"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            services=services,
            nginx_config=config_data.get("nginx_config", {}),
            haproxy_config=config_data.get("haproxy_config", {}),
            envoy_config=config_data.get("envoy_config", {}),
            ssl_config=config_data.get("ssl_config", {}),
            monitoring_config=config_data.get("monitoring_config", {}),
            global_settings=config_data.get("global_settings", {})
        )
    
    def _config_to_dict(self, config: LoadBalancerConfiguration) -> Dict[str, Any]:
        """Convert configuration object to dictionary"""
        services = {}
        for service_name, service in config.services.items():
            services[service_name] = asdict(service)
        
        return {
            "version": config.version,
            "environment": config.environment,
            "services": services,
            "nginx_config": config.nginx_config,
            "haproxy_config": config.haproxy_config,
            "envoy_config": config.envoy_config,
            "ssl_config": config.ssl_config,
            "monitoring_config": config.monitoring_config,
            "global_settings": config.global_settings
        }
    
    def _calculate_config_hash(self, config_data: Dict[str, Any]) -> str:
        """Calculate hash of configuration data"""
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    async def save_configuration(self, config: LoadBalancerConfiguration) -> bool:
        """Save configuration to file"""



        try:
            # Create backup of current configuration
            await self._backup_configuration()
            
            # Update timestamps
            config.updated_at = datetime.now()
            
            # Convert to dictionary
            config_data = self._config_to_dict(config)
            
            # Validate configuration
            if "config" in self.schemas:
                validate(config_data, self.schemas["config"])
            
            # Write to temporary file first
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            # Atomic move
            temp_file.replace(self.config_file)
            
            # Update current config and hash
            self.current_config = config
            self.config_hash = self._calculate_config_hash(config_data)
            
            logger.info("Configuration saved successfully")
            
            # Notify watchers
            await self._notify_config_watchers()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    async def _backup_configuration(self) -> None:
        """Backup current configuration"""
        if self.config_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backups_dir / f"config_{timestamp}.yaml"
            shutil.copy2(self.config_file, backup_file)
            
            # Keep only last 10 backups
            backups = sorted(self.backups_dir.glob("config_*.yaml"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
    
    async def generate_configurations(self) -> Dict[str, str]:
        """Generate configuration files for all load balancers"""
        if not self.current_config:
            raise ValueError("No configuration loaded")
        
        generated_configs = {}
        
        try:
            # Prepare template context
            context = {
                "generated_at": datetime.now().isoformat(),
                "services": {name: asdict(service) for name, service in self.current_config.services.items()},
                "nginx_config": self.current_config.nginx_config,
                "haproxy_config": self.current_config.haproxy_config,
                "envoy_config": self.current_config.envoy_config,
                "ssl_config": self.current_config.ssl_config,
                "monitoring_config": self.current_config.monitoring_config,
                "global_settings": self.current_config.global_settings
            }
            
            # Generate configurations
            templates = ["nginx.conf.j2", "haproxy.cfg.j2", "envoy.yaml.j2", "ssl.conf.j2"]
            
            for template_name in templates:
                try:
                    template = self.jinja_env.get_template(template_name)
                    rendered = template.render(**context)
                    config_name = template_name.replace(".j2", "")
                    generated_configs[config_name] = rendered
                    logger.debug(f"Generated configuration: {config_name}")
                except Exception as e:
                    logger.error(f"Failed to generate {template_name}: {e}")
            
            logger.info(f"Generated {len(generated_configs)} configuration files")
            return generated_configs
            
        except Exception as e:
            logger.error(f"Failed to generate configurations: {e}")
            raise
    
    async def validate_configuration(self, config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration data"""
        errors = []
        
        try:
            # Schema validation
            if "config" in self.schemas:
                validate(config_data, self.schemas["config"])
            
            # Business logic validation
            services = config_data.get("services", {})
            
            # Check for port conflicts
            ports = {}
            for service_name, service in services.items():
                port = service.get("port")
                if port in ports:
                    errors.append(f"Port conflict: {port} used by both {ports[port]} and {service_name}")
                else:
                    ports[port] = service_name
            
            # Check for valid health check paths
            for service_name, service in services.items():
                health_check_path = service.get("health_check_path", "")
                if not health_check_path.startswith("/"):
                    errors.append(f"Invalid health check path for {service_name}: {health_check_path}")
            
            # Check SSL configuration
            ssl_config = config_data.get("ssl_config", {})
            if ssl_config.get("enabled") and not ssl_config.get("cert_path"):
                errors.append("SSL enabled but no certificate path specified")
            
            return len(errors) == 0, errors
            
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
    
    async def add_config_watcher(self, callback: callable) -> None:
        """Add configuration change watcher"""
        self.config_watchers.append(callback)
        logger.debug(f"Added configuration watcher: {callback.__name__}")
    
    async def remove_config_watcher(self, callback: callable) -> None:
        """Remove configuration change watcher"""
        if callback in self.config_watchers:
            self.config_watchers.remove(callback)
            logger.debug(f"Removed configuration watcher: {callback.__name__}")
    
    async def _notify_config_watchers(self) -> None:
        """Notify all configuration watchers"""
        for callback in self.config_watchers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_config)
                else:
                    callback(self.current_config)
            except Exception as e:
                logger.error(f"Error in config watcher {callback.__name__}: {e}")
    
    async def _start_config_watching(self) -> None:
        """Start watching configuration file for changes"""
        self.is_watching = True
        self.watch_task = asyncio.create_task(self._config_watch_loop())
        logger.info("Configuration file watching started")
    
    async def _config_watch_loop(self) -> None:
        """Configuration file watch loop"""
        while self.is_watching:
            try:
                if self.config_file.exists():
                    # Check if file has changed
                    with open(self.config_file, 'r') as f:
                        config_data = yaml.safe_load(f)
                    
                    new_hash = self._calculate_config_hash(config_data)
                    
                    if new_hash != self.config_hash:
                        logger.info("Configuration file changed, reloading...")
                        
                        # Validate new configuration
                        is_valid, errors = await self.validate_configuration(config_data)
                        
                        if is_valid:
                            self.current_config = self._dict_to_config(config_data)
                            self.config_hash = new_hash
                            await self._notify_config_watchers()
                            logger.info("Configuration reloaded successfully")
                        else:
                            logger.error(f"Invalid configuration detected: {errors}")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in config watch loop: {e}")
                await asyncio.sleep(10)
    
    async def get_configuration(self) -> Optional[LoadBalancerConfiguration]:
        """Get current configuration"""



        return self.current_config
    
    async def get_service_configuration(self, service_name: str) -> Optional[ServiceConfiguration]:
        """Get configuration for a specific service"""
        if self.current_config and service_name in self.current_config.services:
            return self.current_config.services[service_name]
        return None
    
    async def update_service_configuration(self, service_name: str, 
                                         service_config: ServiceConfiguration) -> bool:
        """Update configuration for a specific service"""
        if not self.current_config:
            return False
        
        self.current_config.services[service_name] = service_config
        return await self.save_configuration(self.current_config)
    
    async def shutdown(self) -> None:
        """Shutdown configuration manager"""



        try:
            logger.info("Shutting down Configuration Manager...")
            
            self.is_watching = False
            
            if self.watch_task:
                self.watch_task.cancel()
                try:
                    await self.watch_task
                except asyncio.CancelledError:
                    pass
            
            # Save current configuration
            if self.current_config:
                await self.save_configuration(self.current_config)
            
            logger.info("Configuration Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Configuration Manager shutdown: {e}")
