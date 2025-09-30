"""🌐 API Gateway Docker Configuration - IA-Influencer-Agent Platform
===================================================================
Expert: DevOps Engineer + API Gateway Specialist + Load Balancer Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
===================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional API Gateway Docker configuration for high-performance
multi-format content processing and real-time AI protection services.
"""

from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
import yaml
import json

logger = logging.getLogger(__name__)

@dataclass
class APIGatewayDockerConfig:
    """
Enterprise API Gateway Docker configuration"""
    
    # Container Configuration
    image_name: str = "ia-influencer/api-gateway"
    image_tag: str = "2.0.0"
    container_name: str = "ia-influencer-api-gateway"
    
    # Network Configuration
    external_port: int = 80
    internal_port: int = 8000
    ssl_port: int = 443
    admin_port: int = 8001
    
    # Performance Configuration  
    worker_processes: int = 4
    worker_connections: int = 2048
    max_body_size: str = "100M"
    client_timeout: int = 60
    
    # Security Configuration
    enable_ssl: bool = True
    ssl_cert_path: str = "/etc/ssl/certs/ia-influencer.crt"
    ssl_key_path: str = "/etc/ssl/private/ia-influencer.key"
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: str = "1m"
    
    # Environment Configuration
    environment: str = "production"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Resource Limits
    cpu_limit: str = "2000m"
    memory_limit: str = "4Gi"
    cpu_request: str = "1000m"
    memory_request: str = "2Gi"
    
    # Health Check Configuration
    health_check_enabled: bool = True
    health_check_interval: str = "30s"
    health_check_timeout: str = "10s"
    health_check_retries: int = 3
    
    # Backend Services
    backend_services: Dict[str, str] = field(default_factory=lambda: {
        "ai_engines": "http://ai-engines:8000",
        "fingerprinting": "http://fingerprinting-engine:8000", 
        "content_protection": "http://content-protection:8000",
        "monetization": "http://monetization-engine:8000",
        "user_management": "http://user-management:8000",
        "analytics": "http://analytics-engine:8000"
    })
    
    def generate_dockerfile(self) -> str:
        """Generate production Dockerfile for API Gateway"""
        return f"""# IA-Influencer API Gateway - Production Docker Image
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Professional high-performance API Gateway with load balancing

# Multi-stage build for optimization
FROM node:18-alpine AS builder

LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL version="{self.image_tag}"
LABEL service="api-gateway"
LABEL platform="IA-Influencer-Agent"
LABEL environment="{self.environment}"

# Build environment
WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:18-alpine AS production

# Security hardening
RUN addgroup -g 1001 -S gateway && \\
    adduser -S gateway -u 1001 -G gateway

# Install system dependencies
RUN apk add --no-cache \\
    curl \\
    ca-certificates \\
    tzdata \\
    dumb-init

# Create directories
RUN mkdir -p /app/logs /app/config /app/ssl /app/temp && \\
    chown -R gateway:gateway /app

WORKDIR /app

# Copy application files
COPY --from=builder --chown=gateway:gateway /build/node_modules ./node_modules
COPY --chown=gateway:gateway . .

# Environment variables
ENV NODE_ENV={self.environment}
ENV PORT={self.internal_port}
ENV LOG_LEVEL={self.log_level}
ENV WORKER_PROCESSES={self.worker_processes}
ENV WORKER_CONNECTIONS={self.worker_connections}
ENV MAX_BODY_SIZE={self.max_body_size}
ENV CLIENT_TIMEOUT={self.client_timeout}
ENV RATE_LIMIT_REQUESTS={self.rate_limit_requests}
ENV RATE_LIMIT_WINDOW={self.rate_limit_window}

# Health check
HEALTHCHECK --interval={self.health_check_interval} \\
           --timeout={self.health_check_timeout} \\
           --start-period=60s \\
           --retries={self.health_check_retries} \\
    CMD curl -f http://localhost:{self.internal_port}/health || exit 1

# Switch to non-root user
USER gateway

# Expose ports
EXPOSE {self.internal_port}
EXPOSE {self.admin_port}
EXPOSE {self.ssl_port}

# Run with dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
"""
    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """
Generate docker-compose service configuration"""
        return {
            "image": f"{self.image_name}:{self.image_tag}",
            "container_name": self.container_name,
            "restart": "unless-stopped",
            "ports": [
                f"{self.external_port}:{self.internal_port}",
                f"{self.ssl_port}:{self.ssl_port}",
                f"{self.admin_port}:{self.admin_port}"
            ],
            "environment": {
                "NODE_ENV": self.environment,
                "LOG_LEVEL": self.log_level,
                "PORT": str(self.internal_port),
                "SSL_PORT": str(self.ssl_port),
                "ADMIN_PORT": str(self.admin_port),
                "WORKER_PROCESSES": str(self.worker_processes),
                "WORKER_CONNECTIONS": str(self.worker_connections),
                "MAX_BODY_SIZE": self.max_body_size,
                "CLIENT_TIMEOUT": str(self.client_timeout),
                "RATE_LIMIT_ENABLED": str(self.rate_limit_enabled).lower(),
                "RATE_LIMIT_REQUESTS": str(self.rate_limit_requests),
                "RATE_LIMIT_WINDOW": self.rate_limit_window,
                **{f"BACKEND_{k.upper()}": v for k, v in self.backend_services.items()}
            },
            "volumes": [
                "./config/gateway:/app/config:ro",
                "./ssl:/app/ssl:ro",
                "./logs/gateway:/app/logs",
                "/tmp:/app/temp"
            ],
            "networks": ["ia-influencer-network"],
            "depends_on": [
                "ai-engines",
                "fingerprinting-engine", 
                "content-protection",
                "monetization-engine"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": self.cpu_limit,
                        "memory": self.memory_limit
                    },
                    "reservations": {
                        "cpus": self.cpu_request,
                        "memory": self.memory_request
                    }
                }
            },
            "healthcheck": {
                "test": f"curl -f http://localhost:{self.internal_port}/health || exit 1",
                "interval": self.health_check_interval,
                "timeout": self.health_check_timeout,
                "retries": self.health_check_retries,
                "start_period": "60s"
            },
            "security_opt": [
                "no-new-privileges:true"
            ],
            "cap_drop": ["ALL"],
            "cap_add": ["NET_BIND_SERVICE"],
            "read_only": True,
            "tmpfs": [
                "/tmp:size=1G,mode=1777"
            ]
        }
    
    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration for API Gateway"""
        return f"""# IA-Influencer API Gateway - Nginx Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>
# High-performance reverse proxy with load balancing

user nginx;
worker_processes {self.worker_processes};
worker_rlimit_nofile 65535;

error_log /var/log/nginx/error.log {self.log_level.lower()};
pid /var/run/nginx.pid;

events {{
    worker_connections {self.worker_connections};
    use epoll;
    multi_accept on;
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
    
    access_log /var/log/nginx/access.log main;
    
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size {self.max_body_size};
    client_body_timeout {self.client_timeout};
    client_header_timeout {self.client_timeout};
    send_timeout {self.client_timeout};
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:{self.rate_limit_requests}m rate={self.rate_limit_requests}r/{self.rate_limit_window};
    limit_req_status 429;
    
    # Upstream backend services
    {self._generate_upstream_configs()}
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Main server block
    server {{
        listen {self.internal_port};
        listen {self.ssl_port} ssl http2;
        server_name _;
        
        # SSL certificates
        ssl_certificate {self.ssl_cert_path};
        ssl_certificate_key {self.ssl_key_path};
        
        # Health check endpoint
        location /health {{
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }}
        
        # API routing
        {self._generate_location_blocks()}
        
        # Error pages
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {{
            root /usr/share/nginx/html;
        }}
    }}
    
    # Admin interface
    server {{
        listen {self.admin_port};
        server_name _;
        
        location /admin {{
            allow 127.0.0.1;
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
            
            proxy_pass http://admin_backend;
            include /etc/nginx/proxy_params;
        }}
    }}
}}
"""
    
    def _generate_upstream_configs(self) -> str:
        """
Generate upstream server configurations"""
        upstreams = []
        for service, url in self.backend_services.items():
            upstreams.append(f"""
    upstream {service}_backend {{
        least_conn;
        server {url.replace('http://', '')} max_fails=3 fail_timeout=30s;
        keepalive 32;
    }}""")
        return "\n".join(upstreams)
    
    def _generate_location_blocks(self) -> str:
        """Generate location blocks for API routing"""
        locations = []
        
        # API routes mapping
        route_mapping = {
            "/api/v1/ai": "ai_engines_backend",
            "/api/v1/fingerprint": "fingerprinting_backend",
            "/api/v1/protection": "content_protection_backend", 
            "/api/v1/monetization": "monetization_backend",
            "/api/v1/users": "user_management_backend",
            "/api/v1/analytics": "analytics_backend"
        }
        
        for route, upstream in route_mapping.items():
            locations.append(f"""
        location {route} {{
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://{upstream};
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }}""")
        
        return "\n".join(locations)
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all configuration files to output directory"""
        import os
        from pathlib import Path
        
        config_dir = Path(output_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Dockerfile
        dockerfile_path = config_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(self.generate_dockerfile())
        files_created.append(str(dockerfile_path))
        
        # Save Nginx config
        nginx_config_path = config_dir / "nginx.conf"
        with open(nginx_config_path, 'w') as f:
            f.write(self.generate_nginx_config())
        files_created.append(str(nginx_config_path))
        
        # Save docker-compose service config
        compose_config_path = config_dir / "docker-compose.api-gateway.yml"
        service_config = {
            "version": "3.8",
            "services": {
                "api-gateway": self.generate_docker_compose_service()
            }
        }
        with open(compose_config_path, 'w') as f:
            yaml.dump(service_config, f, default_flow_style=False)
        files_created.append(str(compose_config_path))
        
        logger.info(f"✅ API Gateway configuration files saved: {files_created}")
        return files_created
