"""
🌐 Nginx Proxy Docker Configuration - IA-Influencer-Agent Platform
==================================================================
Expert: DevOps Engineer + Network Specialist + Load Balancing Expert
Creator: Fahed Mlaiel <mlaiel@live.de>
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Docker configuration for enterprise Nginx reverse proxy
supporting high-performance load balancing, SSL termination, and
advanced routing for IA-Influencer multi-service architecture.
"""

from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class NginxProxyDockerConfig:
    """Enterprise Nginx Proxy Docker Configuration"""
    
    # Image Configuration
    image_name: str = "nginx"
    image_tag: str = "alpine"
    
    # Container Configuration
    container_name: str = "ia-influencer-nginx"
    restart_policy: str = "unless-stopped"
    network_mode: str = "ia-influencer-network"
    
    # Port Configuration
    http_port: int = 80
    https_port: int = 443
    
    # SSL Configuration
    ssl_enabled: bool = True
    ssl_cert_path: str = "/etc/ssl/certs/ia-influencer.crt"
    ssl_key_path: str = "/etc/ssl/private/ia-influencer.key"
    ssl_dhparam_path: str = "/etc/ssl/certs/dhparam.pem"
    
    # Load Balancing Configuration
    enable_load_balancing: bool = True
    enable_sticky_sessions: bool = True
    enable_health_checks: bool = True
    
    # Security Configuration
    enable_rate_limiting: bool = True
    enable_ddos_protection: bool = True
    enable_security_headers: bool = True
    
    # Performance Configuration
    worker_processes: str = "auto"
    worker_connections: int = 4096
    keepalive_timeout: int = 65
    client_max_body_size: str = "100M"
    
    # Upstream Services
    upstream_services: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "api_gateway": {
            "servers": ["api-gateway:8000"],
            "health_check": "/health",
            "backup": False
        },
        "backend_services": {
            "servers": ["backend-services:8000"],
            "health_check": "/health",
            "backup": False
        },
        "ai_engines": {
            "servers": ["ai-engines:8000"],
            "health_check": "/health",
            "backup": False
        },
        "fingerprinting": {
            "servers": ["fingerprinting-engine:8000"],
            "health_check": "/health",
            "backup": False
        },
        "content_protection": {
            "servers": ["content-protection:8000"],
            "health_check": "/health",
            "backup": False
        },
        "monetization": {
            "servers": ["monetization-engine:8000"],
            "health_check": "/health",
            "backup": False
        },
        "flower_monitoring": {
            "servers": ["celery-flower:5555"],
            "health_check": "/api/workers",
            "backup": False
        }
    })
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for Nginx proxy"""
        return f"""
FROM {self.image_name}:{self.image_tag}

# Install additional packages
RUN apk add --no-cache \\
    curl \\
    openssl \\
    bash \\
    nano \\
    htop

# Create nginx user and directories
RUN addgroup -g 101 -S nginx && \\
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Create necessary directories
RUN mkdir -p /etc/nginx/conf.d \\
             /etc/nginx/sites-available \\
             /etc/nginx/sites-enabled \\
             /etc/nginx/ssl \\
             /var/log/nginx \\
             /var/cache/nginx \\
             /etc/ssl/certs \\
             /etc/ssl/private

# Copy configuration files
COPY config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY config/nginx/conf.d/ /etc/nginx/conf.d/
COPY config/nginx/sites-available/ /etc/nginx/sites-available/
COPY config/nginx/ssl/ /etc/nginx/ssl/

# Copy SSL certificates
COPY ssl/ /etc/ssl/

# Copy custom scripts
COPY scripts/nginx/ /usr/local/bin/

# Set permissions
RUN chmod +x /usr/local/bin/*.sh && \\
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx && \\
    chmod 644 /etc/ssl/certs/* && \\
    chmod 600 /etc/ssl/private/* && \\
    chmod 755 /etc/ssl/certs /etc/ssl/private

# Generate DH parameters if not provided
RUN if [ ! -f {self.ssl_dhparam_path} ]; then \\
        openssl dhparam -out {self.ssl_dhparam_path} 2048; \\
    fi

# Test nginx configuration
RUN nginx -t

# Expose ports
EXPOSE {self.http_port} {self.https_port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate Docker Compose service configuration"""
        return {
            "build": {
                "context": ".",
                "dockerfile": "Dockerfile"
            },
            "image": f"ia-influencer/nginx-proxy:2.0.0",
            "container_name": self.container_name,
            "restart": self.restart_policy,
            "ports": [
                f"{self.http_port}:80",
                f"{self.https_port}:443"
            ],
            "volumes": [
                "./config/nginx:/etc/nginx:ro",
                "./ssl:/etc/ssl:ro",
                "./logs/nginx:/var/log/nginx",
                "./static:/usr/share/nginx/html/static:ro"
            ],
            "networks": [self.network_mode],
            "depends_on": [
                "api-gateway",
                "backend-services",
                "ai-engines",
                "fingerprinting-engine",
                "content-protection",
                "monetization-engine"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "2000m",
                        "memory": "1Gi"
                    },
                    "reservations": {
                        "cpus": "500m",
                        "memory": "256Mi"
                    }
                }
            },
            "healthcheck": {
                "test": "curl -f http://localhost/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "10s"
            }
        }
    
    def generate_nginx_config(self) -> str:
        """Generate main nginx.conf"""
        return f"""
# IA-Influencer Nginx Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>
# High-performance reverse proxy and load balancer

user nginx;
worker_processes {self.worker_processes};
worker_rlimit_nofile 65535;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections {self.worker_connections};
    use epoll;
    multi_accept on;
}}

http {{
    # Basic Settings
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Performance Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout {self.keepalive_timeout};
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Buffer Settings
    client_body_buffer_size 128k;
    client_max_body_size {self.client_max_body_size};
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Timeout Settings
    client_body_timeout 30s;
    client_header_timeout 30s;
    send_timeout 30s;
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
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
    
    # Brotli Compression
    brotli on;
    brotli_comp_level 6;
    brotli_types
        text/plain
        text/css
        application/json
        application/javascript
        text/xml
        application/xml
        application/xml+rss
        text/javascript;
    
    # Logging Format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    log_format detailed '$remote_addr - $remote_user [$time_local] "$request" '
                       '$status $body_bytes_sent "$http_referer" '
                       '"$http_user_agent" "$http_x_forwarded_for" '
                       'rt=$request_time uct="$upstream_connect_time" '
                       'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log detailed;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    # Real IP Configuration
    set_real_ip_from 10.0.0.0/8;
    set_real_ip_from 172.16.0.0/12;
    set_real_ip_from 192.168.0.0/16;
    real_ip_header X-Forwarded-For;
    real_ip_recursive on;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_dhparam {self.ssl_dhparam_path};
    
    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:; media-src 'self' https:; object-src 'none'; frame-ancestors 'none';" always;
    
    # Hide Nginx version
    server_tokens off;
    
    # Include upstream configurations
    include /etc/nginx/conf.d/upstreams.conf;
    
    # Include server configurations
    include /etc/nginx/sites-enabled/*.conf;
}}
"""

    def generate_upstream_config(self) -> str:
        """Generate upstream configuration"""
        upstream_blocks = []
        
        for service_name, config in self.upstream_services.items():
            servers = "\n        ".join([f"server {server};" for server in config["servers"]])
            
            upstream_block = f"""
upstream {service_name} {{
    # Load balancing method
    least_conn;
    
    # Server definitions
    {servers}
    
    # Health check
    # health_check uri={config.get('health_check', '/health')} interval=30s;
    
    # Keepalive connections
    keepalive 32;
    keepalive_requests 100;
    keepalive_timeout 60s;
}}"""
            upstream_blocks.append(upstream_block)
        
        return f"""
# IA-Influencer Upstream Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

{"".join(upstream_blocks)}
"""

    def generate_server_config(self) -> str:
        """Generate main server configuration"""
        return f"""
# IA-Influencer Main Server Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Redirect HTTP to HTTPS
server {{
    listen {self.http_port};
    server_name _;
    
    # Health check endpoint
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
    
    # Redirect all HTTP traffic to HTTPS
    location / {{
        return 301 https://$host$request_uri;
    }}
}}

# HTTPS Server
server {{
    listen {self.https_port} ssl http2;
    server_name ia-influencer.com www.ia-influencer.com api.ia-influencer.com;
    
    # SSL Configuration
    ssl_certificate {self.ssl_cert_path};
    ssl_certificate_key {self.ssl_key_path};
    
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
    limit_conn addr 10;
    
    # Main API routes
    location /api/v1/ {{
        proxy_pass http://api_gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }}
    
    # Backend services
    location /backend/ {{
        proxy_pass http://backend_services/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # AI processing endpoints
    location /ai/ {{
        proxy_pass http://ai_engines/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }}
    
    # Fingerprinting endpoints
    location /fingerprint/ {{
        proxy_pass http://fingerprinting/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }}
    
    # Content protection endpoints
    location /protection/ {{
        proxy_pass http://content_protection/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Monetization endpoints
    location /monetization/ {{
        proxy_pass http://monetization/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # File uploads (with rate limiting)
    location /upload/ {{
        limit_req zone=upload burst=5 nodelay;
        client_max_body_size 500M;
        proxy_pass http://backend_services/upload/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_request_buffering off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }}
    
    # Authentication endpoints
    location /auth/ {{
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://api_gateway/auth/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # WebSocket connections
    location /ws/ {{
        proxy_pass http://api_gateway/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }}
    
    # Static files
    location /static/ {{
        alias /usr/share/nginx/html/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }}
    
    # Health check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
    
    # Monitoring (Flower)
    location /monitoring/ {{
        auth_basic "IA-Influencer Monitoring";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://flower_monitoring/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {{
        root /usr/share/nginx/html;
    }}
    
    # Security headers for all responses
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}}

# Admin subdomain
server {{
    listen {self.https_port} ssl http2;
    server_name admin.ia-influencer.com;
    
    # SSL Configuration
    ssl_certificate {self.ssl_cert_path};
    ssl_certificate_key {self.ssl_key_path};
    
    # Admin authentication
    auth_basic "IA-Influencer Admin";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Admin API
    location / {{
        proxy_pass http://api_gateway/admin/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""

    def generate_security_config(self) -> str:
        """Generate security configuration"""
        return """
# IA-Influencer Nginx Security Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Map for blocking malicious requests
map $request_method $limit {
    default         "";
    POST            $binary_remote_addr;
    PUT             $binary_remote_addr;
    DELETE          $binary_remote_addr;
}

# Geographic blocking (example)
geo $blocked_country {
    default 0;
    # Add specific country blocks here if needed
    # CN 1;  # Block China (example)
    # RU 1;  # Block Russia (example)
}

# Block common attack patterns
map $http_user_agent $blocked_agent {
    default 0;
    ~*bot 1;
    ~*crawl 1;
    ~*spider 1;
    ~*scan 1;
    ~*hack 1;
    ~*test 1;
    ~*benchmark 1;
    ~*exploit 1;
    ~*attack 1;
    "~*python-requests" 1;
    "~*curl" 1;
    "~*wget" 1;
    "" 1;  # Empty user agent
}

# Block malicious referers
map $http_referer $blocked_referer {
    default 0;
    ~*spam 1;
    ~*casino 1;
    ~*poker 1;
    ~*porn 1;
    ~*adult 1;
    ~*malware 1;
    ~*phishing 1;
}

# Block based on request URI
map $request_uri $blocked_uri {
    default 0;
    ~*/\.well-known/security\.txt$ 0;
    ~*/\.well-known/(.*)$ 1;
    ~*/\.git 1;
    ~*/\.svn 1;
    ~*/\.env 1;
    ~*/wp-admin 1;
    ~*/wp-login 1;
    ~*/admin 1;
    ~*/phpmyadmin 1;
    ~*/config 1;
    ~*/backup 1;
    ~*/tmp 1;
    ~*/temp 1;
    ~*\.(sql|bak|backup|old|orig|save)$ 1;
    ~*\.(php|asp|aspx|jsp|cgi)$ 1;
}

# DDoS protection
limit_req_zone $binary_remote_addr zone=ddos:50m rate=20r/s;
limit_conn_zone $binary_remote_addr zone=perip:10m;
limit_conn_zone $server_name zone=perserver:10m;

# Security server block
server {
    # Block requests
    if ($blocked_country) { return 444; }
    if ($blocked_agent) { return 444; }
    if ($blocked_referer) { return 444; }
    if ($blocked_uri) { return 444; }
    
    # DDoS protection
    limit_req zone=ddos burst=50 nodelay;
    limit_conn perip 20;
    limit_conn perserver 1000;
    
    # Hide server signature
    server_tokens off;
    
    # Prevent access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Prevent access to backup files
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Block access to sensitive files
    location ~* \.(htaccess|htpasswd|ini|log|sh|sql|conf)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
"""

    def generate_monitoring_config(self) -> str:
        """Generate monitoring configuration"""
        return """
# IA-Influencer Nginx Monitoring Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Nginx status for monitoring
server {
    listen 8080;
    server_name localhost;
    
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        allow 172.16.0.0/12;
        allow 10.0.0.0/8;
        allow 192.168.0.0/16;
        deny all;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /metrics {
        access_log off;
        # Prometheus metrics endpoint
        # This would require nginx-prometheus-exporter
        return 200 "metrics endpoint\n";
        add_header Content-Type text/plain;
    }
}
"""

    def generate_scripts(self) -> Dict[str, str]:
        """Generate Nginx scripts"""
        scripts = {}
        
        # SSL certificate generator
        scripts["generate-ssl.sh"] = """#!/bin/bash
# SSL Certificate Generator for IA-Influencer
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

DOMAIN=${1:-ia-influencer.com}
SSL_DIR="/etc/ssl"
CERT_DIR="$SSL_DIR/certs"
KEY_DIR="$SSL_DIR/private"

echo "🔐 Generating SSL certificates for $DOMAIN..."

# Create directories
mkdir -p "$CERT_DIR" "$KEY_DIR"

# Generate private key
openssl genrsa -out "$KEY_DIR/ia-influencer.key" 4096

# Generate certificate signing request
openssl req -new -key "$KEY_DIR/ia-influencer.key" -out "$CERT_DIR/ia-influencer.csr" -subj "/C=DE/ST=Bavaria/L=Munich/O=IA-Influencer/OU=IT/CN=$DOMAIN/emailAddress=mlaiel@live.de"

# Generate self-signed certificate (for development)
openssl x509 -req -days 365 -in "$CERT_DIR/ia-influencer.csr" -signkey "$KEY_DIR/ia-influencer.key" -out "$CERT_DIR/ia-influencer.crt"

# Generate DH parameters
openssl dhparam -out "$CERT_DIR/dhparam.pem" 2048

# Set proper permissions
chmod 644 "$CERT_DIR"/*
chmod 600 "$KEY_DIR"/*

echo "✅ SSL certificates generated successfully!"
echo "Certificate: $CERT_DIR/ia-influencer.crt"
echo "Private key: $KEY_DIR/ia-influencer.key"
echo "DH params: $CERT_DIR/dhparam.pem"
"""

        # Configuration validator
        scripts["validate-config.sh"] = """#!/bin/bash
# Nginx Configuration Validator
# Creator: Fahed Mlaiel <mlaiel@live.de>

echo "🔍 Validating Nginx configuration..."

# Test nginx configuration
if nginx -t -c /etc/nginx/nginx.conf; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

# Check SSL certificates
if [ -f "/etc/ssl/certs/ia-influencer.crt" ] && [ -f "/etc/ssl/private/ia-influencer.key" ]; then
    echo "✅ SSL certificates found"
    
    # Verify certificate
    if openssl x509 -in /etc/ssl/certs/ia-influencer.crt -text -noout > /dev/null 2>&1; then
        echo "✅ SSL certificate is valid"
    else
        echo "❌ SSL certificate is invalid"
        exit 1
    fi
else
    echo "⚠️  SSL certificates not found"
fi

# Check upstream services
echo "🔍 Checking upstream services..."
for service in api-gateway backend-services ai-engines fingerprinting-engine content-protection monetization-engine; do
    if curl -f --connect-timeout 5 "http://$service:8000/health" > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "⚠️  $service is not responding"
    fi
done

echo "🏁 Configuration validation completed"
"""

        # Log analyzer
        scripts["analyze-logs.sh"] = """#!/bin/bash
# Nginx Log Analyzer
# Creator: Fahed Mlaiel <mlaiel@live.de>

LOG_FILE=${1:-/var/log/nginx/access.log}
LINES=${2:-1000}

echo "📊 Analyzing Nginx logs: $LOG_FILE (last $LINES lines)"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

echo ""
echo "🔝 Top 10 IP addresses:"
tail -n "$LINES" "$LOG_FILE" | awk '{print $1}' | sort | uniq -c | sort -nr | head -10

echo ""
echo "🔝 Top 10 requested URLs:"
tail -n "$LINES" "$LOG_FILE" | awk '{print $7}' | sort | uniq -c | sort -nr | head -10

echo ""
echo "📈 Status code distribution:"
tail -n "$LINES" "$LOG_FILE" | awk '{print $9}' | sort | uniq -c | sort -nr

echo ""
echo "🕐 Requests by hour:"
tail -n "$LINES" "$LOG_FILE" | awk '{print $4}' | cut -d: -f2 | sort | uniq -c

echo ""
echo "🌍 Top 10 User Agents:"
tail -n "$LINES" "$LOG_FILE" | awk -F'"' '{print $6}' | sort | uniq -c | sort -nr | head -10

echo ""
echo "⚡ Response time statistics:"
tail -n "$LINES" "$LOG_FILE" | awk '{print $NF}' | grep -E '^[0-9]+\.[0-9]+$' | awk '
{
    sum += $1
    count++
    if ($1 > max) max = $1
    if (min == "" || $1 < min) min = $1
}
END {
    if (count > 0) {
        print "Average: " sum/count "s"
        print "Min: " min "s"
        print "Max: " max "s"
    }
}'

echo ""
echo "🚨 4xx and 5xx errors:"
tail -n "$LINES" "$LOG_FILE" | awk '$9 >= 400 {print $0}' | tail -20
"""

        return scripts
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all Nginx configuration files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Dockerfile
        dockerfile_path = output_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(self.generate_dockerfile())
        files_created.append(str(dockerfile_path))
        
        # Save main configuration files
        config_dir = output_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Main nginx.conf
        nginx_conf_path = config_dir / "nginx.conf"
        with open(nginx_conf_path, 'w') as f:
            f.write(self.generate_nginx_config())
        files_created.append(str(nginx_conf_path))
        
        # conf.d directory
        conf_d_dir = config_dir / "conf.d"
        conf_d_dir.mkdir(exist_ok=True)
        
        upstreams_path = conf_d_dir / "upstreams.conf"
        with open(upstreams_path, 'w') as f:
            f.write(self.generate_upstream_config())
        files_created.append(str(upstreams_path))
        
        security_path = conf_d_dir / "security.conf"
        with open(security_path, 'w') as f:
            f.write(self.generate_security_config())
        files_created.append(str(security_path))
        
        monitoring_path = conf_d_dir / "monitoring.conf"
        with open(monitoring_path, 'w') as f:
            f.write(self.generate_monitoring_config())
        files_created.append(str(monitoring_path))
        
        # sites-available directory
        sites_dir = config_dir / "sites-available"
        sites_dir.mkdir(exist_ok=True)
        
        default_site_path = sites_dir / "default.conf"
        with open(default_site_path, 'w') as f:
            f.write(self.generate_server_config())
        files_created.append(str(default_site_path))
        
        # Save scripts
        scripts_dir = output_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script_name, script_content in self.generate_scripts().items():
            script_path = scripts_dir / script_name
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)
            files_created.append(str(script_path))
        
        logger.info(f"✅ Nginx proxy configuration saved: {len(files_created)} files")
        return files_created
