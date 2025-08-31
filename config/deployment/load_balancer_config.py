"""Load Balancer Configuration Module for IA-Influencer Agent Platform
=================================================================

Professional load balancing and traffic distribution configuration
for multi-format content protection and AI-powered creator monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml


class LoadBalancerType(Enum):
    """Load balancer types"""    NGINX = "nginx"
    HAPROXY = "haproxy"
    AWS_ALB = "aws_alb"
    AWS_NLB = "aws_nlb"
    GOOGLE_LB = "google_lb"
    AZURE_LB = "azure_lb"
    CLOUDFLARE = "cloudflare"
    KUBERNETES_INGRESS = "k8s_ingress"


class RoutingStrategy(Enum):
    """Load balancing algorithms"""    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_conn"
    IP_HASH = "ip_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_time"
    CONSISTENT_HASH = "consistent_hash"


class HealthCheckType(Enum):
    """Health check types"""    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    GRPC = "grpc"


@dataclass
class BackendServer:
    """Backend server configuration"""    host: str
    port: int
    weight: int = 1
    max_fails: int = 3
    fail_timeout: int = 30
    backup: bool = False
    down: bool = False
    slow_start: int = 0
    resolve: bool = False


@dataclass
class HealthCheck:
    """Health check configuration"""    type: HealthCheckType
    path: str = "/health"
    port: Optional[int] = None
    interval: int = 30
    timeout: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    expected_codes: str = "200-299"
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class UpstreamConfig:
    """Upstream server configuration"""    name: str
    servers: List[BackendServer]
    strategy: RoutingStrategy = RoutingStrategy.LEAST_CONNECTIONS
    health_check: Optional[HealthCheck] = None
    keepalive: int = 32
    keepalive_requests: int = 100
    keepalive_timeout: int = 60
    max_conns: Optional[int] = None
    queue: Optional[int] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""    zone_name: str
    zone_size: str = "10m"
    rate: str = "10r/s"
    burst: int = 20
    nodelay: bool = True
    key: str = "$binary_remote_addr"


class LoadBalancerConfig:
    """    Professional load balancer configuration manager for IA-Influencer Agent Platform.
    
    Manages traffic distribution for:
    - API services with intelligent routing
    - AI processing microservices load balancing
    - Content protection service scaling
    - Real-time WebSocket connection distribution
    - Revenue tracking and analytics services
    - Database connection pooling and failover
    - CDN integration and edge caching
    """    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.base_domain = self._get_base_domain()
        self.load_balancer_type = self._get_load_balancer_type()
        
    def _get_base_domain(self) -> str:
        """Get base domain based on environment"""        domains = {
            "development": "dev.ia-influencer.com",
            "staging": "staging.ia-influencer.com",
            "production": "ia-influencer.com"
        }
        return domains.get(self.environment, "localhost")
    
    def _get_load_balancer_type(self) -> LoadBalancerType:
        """Get load balancer type based on environment"""        lb_types = {
            "development": LoadBalancerType.NGINX,
            "staging": LoadBalancerType.NGINX,
            "production": LoadBalancerType.AWS_ALB
        }
        return lb_types.get(self.environment, LoadBalancerType.NGINX)
    
    def get_upstream_configs(self) -> Dict[str, UpstreamConfig]:
        """Get upstream configurations for all services"""        base_port = 8000
        
        upstreams = {
            # Main API service
            "api_backend": UpstreamConfig(
                name="api_backend",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port),
                    BackendServer(host="127.0.0.1", port=base_port + 1),
                    BackendServer(host="127.0.0.1", port=base_port + 2, backup=True)
                ],
                strategy=RoutingStrategy.LEAST_CONNECTIONS,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/api/v1/health",
                    interval=30,
                    timeout=5,
                    healthy_threshold=2,
                    unhealthy_threshold=3
                ),
                keepalive=64,
                max_conns=100
            ),
            
            # AI processing services
            "ai_fingerprinting": UpstreamConfig(
                name="ai_fingerprinting",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 10, weight=2),
                    BackendServer(host="127.0.0.1", port=base_port + 11, weight=2),
                    BackendServer(host="127.0.0.1", port=base_port + 12, weight=1)
                ],
                strategy=RoutingStrategy.CONSISTENT_HASH,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/fingerprint/health",
                    interval=15,
                    timeout=10,
                    expected_codes="200"
                ),
                keepalive=32,
                max_conns=50
            ),
            
            # Audio processing services
            "ai_audio": UpstreamConfig(
                name="ai_audio",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 20),
                    BackendServer(host="127.0.0.1", port=base_port + 21),
                    BackendServer(host="127.0.0.1", port=base_port + 22, backup=True)
                ],
                strategy=RoutingStrategy.LEAST_RESPONSE_TIME,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/audio/health",
                    interval=30,
                    timeout=15
                ),
                keepalive=16
            ),
            
            # Video processing services
            "ai_video": UpstreamConfig(
                name="ai_video", 
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 30),
                    BackendServer(host="127.0.0.1", port=base_port + 31)
                ],
                strategy=RoutingStrategy.LEAST_CONNECTIONS,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/video/health",
                    interval=30,
                    timeout=20
                ),
                keepalive=8
            ),
            
            # Image processing services
            "ai_image": UpstreamConfig(
                name="ai_image",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 40),
                    BackendServer(host="127.0.0.1", port=base_port + 41),
                    BackendServer(host="127.0.0.1", port=base_port + 42)
                ],
                strategy=RoutingStrategy.ROUND_ROBIN,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/image/health",
                    interval=30,
                    timeout=10
                ),
                keepalive=24
            ),
            
            # Text analysis services
            "ai_text": UpstreamConfig(
                name="ai_text",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 50),
                    BackendServer(host="127.0.0.1", port=base_port + 51)
                ],
                strategy=RoutingStrategy.IP_HASH,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/text/health",
                    interval=30,
                    timeout=5
                ),
                keepalive=16
            ),
            
            # Content protection services
            "protection_crawlers": UpstreamConfig(
                name="protection_crawlers",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 60),
                    BackendServer(host="127.0.0.1", port=base_port + 61),
                    BackendServer(host="127.0.0.1", port=base_port + 62)
                ],
                strategy=RoutingStrategy.WEIGHTED_ROUND_ROBIN,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/crawlers/health",
                    interval=60,
                    timeout=10
                ),
                keepalive=32
            ),
            
            # Monitoring and alerting
            "protection_monitoring": UpstreamConfig(
                name="protection_monitoring",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 70),
                    BackendServer(host="127.0.0.1", port=base_port + 71, backup=True)
                ],
                strategy=RoutingStrategy.LEAST_CONNECTIONS,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/monitoring/health",
                    interval=30,
                    timeout=5
                ),
                keepalive=16
            ),
            
            # Revenue tracking services
            "revenue_analytics": UpstreamConfig(
                name="revenue_analytics",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 80),
                    BackendServer(host="127.0.0.1", port=base_port + 81),
                    BackendServer(host="127.0.0.1", port=base_port + 82, backup=True)
                ],
                strategy=RoutingStrategy.LEAST_CONNECTIONS,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/revenue/health",
                    interval=30,
                    timeout=5
                ),
                keepalive=32
            ),
            
            # Payment processing
            "revenue_payments": UpstreamConfig(
                name="revenue_payments",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 90),
                    BackendServer(host="127.0.0.1", port=base_port + 91)
                ],
                strategy=RoutingStrategy.IP_HASH,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTPS,
                    path="/payments/health",
                    interval=30,
                    timeout=10,
                    headers={"Authorization": "Bearer health-check-token"}
                ),
                keepalive=16
            ),
            
            # WebSocket services
            "websocket_realtime": UpstreamConfig(
                name="websocket_realtime",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 100),
                    BackendServer(host="127.0.0.1", port=base_port + 101),
                    BackendServer(host="127.0.0.1", port=base_port + 102)
                ],
                strategy=RoutingStrategy.IP_HASH,  # Sticky sessions for WebSockets
                health_check=HealthCheck(
                    type=HealthCheckType.TCP,
                    port=base_port + 100,
                    interval=30,
                    timeout=5
                ),
                keepalive=64
            ),
            
            # Admin dashboard
            "admin_dashboard": UpstreamConfig(
                name="admin_dashboard",
                servers=[
                    BackendServer(host="127.0.0.1", port=base_port + 110),
                    BackendServer(host="127.0.0.1", port=base_port + 111, backup=True)
                ],
                strategy=RoutingStrategy.ROUND_ROBIN,
                health_check=HealthCheck(
                    type=HealthCheckType.HTTP,
                    path="/admin/health",
                    interval=60,
                    timeout=10
                ),
                keepalive=16
            )
        }
        
        # Add Kubernetes service endpoints for production
        if self.environment == "production":
            for upstream_name, upstream in upstreams.items():
                # Replace localhost with Kubernetes service names
                for server in upstream.servers:
                    if server.host == "127.0.0.1":
                        server.host = f"{upstream_name.replace('_', '-')}-service.{self.environment}.svc.cluster.local"
                        server.resolve = True
        
        return upstreams
    
    def get_rate_limit_configs(self) -> Dict[str, RateLimitConfig]:
        """Get rate limiting configurations"""        return {
            "api_general": RateLimitConfig(
                zone_name="api_general",
                zone_size="10m",
                rate="100r/s",
                burst=200,
                key="$binary_remote_addr"
            ),
            "api_auth": RateLimitConfig(
                zone_name="api_auth",
                zone_size="5m",
                rate="10r/s",
                burst=20,
                key="$binary_remote_addr"
            ),
            "ai_processing": RateLimitConfig(
                zone_name="ai_processing",
                zone_size="20m",
                rate="5r/s",
                burst=10,
                key="$binary_remote_addr"
            ),
            "file_upload": RateLimitConfig(
                zone_name="file_upload",
                zone_size="10m",
                rate="2r/s",
                burst=5,
                key="$binary_remote_addr"
            ),
            "payment_processing": RateLimitConfig(
                zone_name="payment_processing",
                zone_size="5m",
                rate="1r/s",
                burst=3,
                key="$binary_remote_addr"
            )
        }
    
    def generate_nginx_config(self) -> str:
        """Generate complete Nginx load balancer configuration"""        upstreams = self.get_upstream_configs()
        rate_limits = self.get_rate_limit_configs()
        
        config = f"""# Nginx Load Balancer Configuration for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>
# Environment: {self.environment}

# Worker processes
worker_processes auto;
worker_rlimit_nofile 65535;

# Events block
events {{
    worker_connections 4096;
    use epoll;
    multi_accept on;
}}

# HTTP block
http {{
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_header_buffer_size 32k;
    client_max_body_size 100m;
    large_client_header_buffers 4 32k;
    
    # Timeouts
    client_body_timeout 30s;
    client_header_timeout 30s;
    send_timeout 30s;
    
    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for" '
                   'rt=$request_time uct="$upstream_connect_time" '
                   'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip compression
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
    
    # Rate limiting zones
"""        
        # Add rate limiting zones
        for rate_limit in rate_limits.values():
            config += f"    limit_req_zone {rate_limit.key} zone={rate_limit.zone_name}:{rate_limit.zone_size} rate={rate_limit.rate};\n"
        
        config += "\n    # Connection limiting\n"
        config += "    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;\n"
        config += "    limit_conn conn_limit_per_ip 20;\n\n"
        
        # Add upstream configurations
        config += "    # Upstream configurations\n"
        for upstream in upstreams.values():
            config += f"    upstream {upstream.name} {{\n"
            
            # Load balancing method
            if upstream.strategy == RoutingStrategy.LEAST_CONNECTIONS:
                config += "        least_conn;\n"
            elif upstream.strategy == RoutingStrategy.IP_HASH:
                config += "        ip_hash;\n"
            elif upstream.strategy == RoutingStrategy.CONSISTENT_HASH:
                config += "        hash $request_uri consistent;\n"
            
            # Servers
            for server in upstream.servers:
                server_line = f"        server {server.host}:{server.port}"
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
                if server.slow_start > 0:
                    server_line += f" slow_start={server.slow_start}s"
                if server.resolve:
                    server_line += " resolve"
                server_line += ";\n"
                config += server_line
            
            # Keepalive
            config += f"        keepalive {upstream.keepalive};\n"
            if upstream.keepalive_requests != 100:
                config += f"        keepalive_requests {upstream.keepalive_requests};\n"
            if upstream.keepalive_timeout != 60:
                config += f"        keepalive_timeout {upstream.keepalive_timeout}s;\n"
            
            config += "    }\n\n"
        
        # Server blocks
        config += f"""    # Main server block
    server {{
        listen 80;
        listen [::]:80;
        server_name {self.base_domain} www.{self.base_domain};
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }}
    
    # HTTPS server block
    server {{
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name {self.base_domain} www.{self.base_domain};
        
        # SSL configuration (managed by ssl_config.py)
        include /etc/nginx/ssl-params.conf;
        
        # Security headers
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # API routes
        location /api/v1/ {{
            limit_req zone=api_general burst=200 nodelay;
            proxy_pass http://api_backend;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Authentication endpoints
        location ~ ^/api/v1/(auth|login|register|logout) {{
            limit_req zone=api_auth burst=20 nodelay;
            proxy_pass http://api_backend;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # AI fingerprinting endpoints
        location /api/v1/fingerprint/ {{
            limit_req zone=ai_processing burst=10 nodelay;
            client_max_body_size 500m;
            proxy_pass http://ai_fingerprinting;
            proxy_read_timeout 300s;
            proxy_send_timeout 300s;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Audio processing
        location /api/v1/audio/ {{
            limit_req zone=ai_processing burst=10 nodelay;
            client_max_body_size 200m;
            proxy_pass http://ai_audio;
            proxy_read_timeout 180s;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Video processing
        location /api/v1/video/ {{
            limit_req zone=ai_processing burst=5 nodelay;
            client_max_body_size 1g;
            proxy_pass http://ai_video;
            proxy_read_timeout 600s;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Image processing
        location /api/v1/image/ {{
            limit_req zone=ai_processing burst=10 nodelay;
            client_max_body_size 100m;
            proxy_pass http://ai_image;
            proxy_read_timeout 120s;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Text analysis
        location /api/v1/text/ {{
            limit_req zone=ai_processing burst=20 nodelay;
            proxy_pass http://ai_text;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Content protection
        location /api/v1/protection/ {{
            limit_req zone=api_general burst=100 nodelay;
            proxy_pass http://protection_crawlers;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Monitoring endpoints
        location /api/v1/monitoring/ {{
            limit_req zone=api_general burst=50 nodelay;
            proxy_pass http://protection_monitoring;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Revenue analytics
        location /api/v1/revenue/ {{
            limit_req zone=api_general burst=100 nodelay;
            proxy_pass http://revenue_analytics;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Payment processing
        location /api/v1/payments/ {{
            limit_req zone=payment_processing burst=3 nodelay;
            proxy_pass http://revenue_payments;
            proxy_ssl_verify on;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # WebSocket connections
        location /ws/ {{
            proxy_pass http://websocket_realtime;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }}
        
        # Admin dashboard
        location /admin/ {{
            auth_basic "Admin Access";
            auth_basic_user_file /etc/nginx/.htpasswd;
            proxy_pass http://admin_dashboard;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # File uploads
        location /upload/ {{
            limit_req zone=file_upload burst=5 nodelay;
            client_max_body_size 1g;
            proxy_pass http://api_backend;
            proxy_request_buffering off;
            include /etc/nginx/proxy-params.conf;
        }}
        
        # Static files
        location /static/ {{
            alias /var/www/static/;
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
        
        # Nginx status (for monitoring)
        location /nginx_status {{
            stub_status on;
            access_log off;
            allow 127.0.0.1;
            allow 10.0.0.0/8;
            deny all;
        }}
    }}
    
    # Include additional server blocks
    include /etc/nginx/sites-enabled/*;
}}
"""        
        return config
    
    def generate_haproxy_config(self) -> str:
        """Generate HAProxy load balancer configuration"""        upstreams = self.get_upstream_configs()
        
        config = f"""# HAProxy Load Balancer Configuration for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>
# Environment: {self.environment}

global
    log stdout local0
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon
    
    # SSL settings
    ssl-default-bind-ciphers ECDHE+AESGCM:ECDHE+CHACHA20:RSA+AESGCM:RSA+AES:!aNULL:!MD5:!DSS
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    
    # Tuning
    maxconn 4096
    nbthread 2

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option log-health-checks
    option forwardfor except 127.0.0.0/8
    option redispatch
    retries 3
    timeout http-request 10s
    timeout queue 1m
    timeout connect 10s
    timeout client 1m
    timeout server 1m
    timeout http-keep-alive 10s
    timeout check 10s
    maxconn 3000

# Statistics page
frontend stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats hide-version
    stats auth admin:secure-password-{self.environment}

# HTTP frontend (redirect to HTTPS)
frontend http_frontend
    bind *:80
    redirect scheme https code 301 if !{{ ssl_fc }}

# HTTPS frontend
frontend https_frontend
    bind *:443 ssl crt /etc/ssl/certs/haproxy/
    
    # Security headers
    http-response set-header X-Frame-Options DENY
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-XSS-Protection "1; mode=block"
    
    # Rate limiting (using stick tables)
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request reject if {{ sc_http_req_rate(0) gt 20 }}
    
    # ACL definitions
    acl api_path path_beg /api/v1/
    acl auth_path path_beg /api/v1/auth /api/v1/login /api/v1/register /api/v1/logout
    acl fingerprint_path path_beg /api/v1/fingerprint/
    acl audio_path path_beg /api/v1/audio/
    acl video_path path_beg /api/v1/video/
    acl image_path path_beg /api/v1/image/
    acl text_path path_beg /api/v1/text/
    acl protection_path path_beg /api/v1/protection/
    acl monitoring_path path_beg /api/v1/monitoring/
    acl revenue_path path_beg /api/v1/revenue/
    acl payments_path path_beg /api/v1/payments/
    acl websocket_path path_beg /ws/
    acl admin_path path_beg /admin/
    acl upload_path path_beg /upload/
    acl health_path path /health
    
    # Backend selection
    use_backend api_backend if api_path !auth_path !fingerprint_path !audio_path !video_path !image_path !text_path !protection_path !monitoring_path !revenue_path !payments_path !upload_path
    use_backend api_backend if auth_path
    use_backend ai_fingerprinting if fingerprint_path
    use_backend ai_audio if audio_path
    use_backend ai_video if video_path
    use_backend ai_image if image_path
    use_backend ai_text if text_path
    use_backend protection_crawlers if protection_path
    use_backend protection_monitoring if monitoring_path
    use_backend revenue_analytics if revenue_path
    use_backend revenue_payments if payments_path
    use_backend websocket_realtime if websocket_path
    use_backend admin_dashboard if admin_path
    use_backend api_backend if upload_path
    use_backend health_backend if health_path
    
    default_backend api_backend

"""        
        # Add backend configurations
        for upstream in upstreams.values():
            config += f"""# Backend: {upstream.name}
backend {upstream.name}
    balance {'roundrobin' if upstream.strategy == RoutingStrategy.ROUND_ROBIN else 'leastconn'}
    option httpchk GET {upstream.health_check.path if upstream.health_check else '/health'}
    http-check expect status {upstream.health_check.expected_codes if upstream.health_check else '200'}
    
"""            for i, server in enumerate(upstream.servers):
                server_options = []
                if server.weight != 1:
                    server_options.append(f"weight {server.weight}")
                if server.max_fails != 3:
                    server_options.append(f"maxconn {server.max_fails * 10}")
                if server.backup:
                    server_options.append("backup")
                if server.down:
                    server_options.append("disabled")
                
                check_options = ""
                if upstream.health_check:
                    check_options = f"check inter {upstream.health_check.interval}s fall {upstream.health_check.unhealthy_threshold} rise {upstream.health_check.healthy_threshold}"
                
                options_str = " ".join(server_options)
                config += f"    server {upstream.name}-{i+1} {server.host}:{server.port} {options_str} {check_options}\n"
        
        # Add health check backend
        config += """# Health check backend
backend health_backend
    http-request return status 200 content-type "text/plain" string "healthy"
"""        
        return config
    
    def get_aws_alb_config(self) -> Dict[str, Any]:
        """Get AWS Application Load Balancer configuration"""        return {
            "load_balancer": {
                "name": f"{self.project_name}-{self.environment}-alb",
                "scheme": "internet-facing",
                "type": "application",
                "ip_address_type": "ipv4",
                "security_groups": [
                    f"{self.project_name}-{self.environment}-alb-sg"
                ],
                "subnets": [
                    "subnet-12345678",
                    "subnet-87654321"
                ],
                "enable_deletion_protection": self.environment == "production",
                "enable_cross_zone_load_balancing": True,
                "enable_http2": True,
                "idle_timeout": 60
            },
            "target_groups": [
                {
                    "name": f"{self.project_name}-api-{self.environment}",
                    "protocol": "HTTP",
                    "port": 8000,
                    "vpc_id": "vpc-12345678",
                    "health_check": {
                        "enabled": True,
                        "healthy_threshold_count": 2,
                        "interval_seconds": 30,
                        "matcher": "200",
                        "path": "/api/v1/health",
                        "port": "traffic-port",
                        "protocol": "HTTP",
                        "timeout_seconds": 5,
                        "unhealthy_threshold_count": 3
                    },
                    "target_type": "instance",
                    "deregistration_delay": 300
                },
                {
                    "name": f"{self.project_name}-ai-{self.environment}",
                    "protocol": "HTTP",
                    "port": 8010,
                    "vpc_id": "vpc-12345678",
                    "health_check": {
                        "enabled": True,
                        "healthy_threshold_count": 2,
                        "interval_seconds": 30,
                        "matcher": "200",
                        "path": "/fingerprint/health",
                        "timeout_seconds": 10
                    }
                }
            ],
            "listeners": [
                {
                    "port": 80,
                    "protocol": "HTTP",
                    "default_actions": [
                        {
                            "type": "redirect",
                            "redirect": {
                                "protocol": "HTTPS",
                                "port": "443",
                                "status_code": "HTTP_301"
                            }
                        }
                    ]
                },
                {
                    "port": 443,
                    "protocol": "HTTPS",
                    "ssl_policy": "ELBSecurityPolicy-TLS-1-2-2019-07",
                    "certificate_arn": f"arn:aws:acm:eu-central-1:123456789012:certificate/{self.project_name}-{self.environment}",
                    "default_actions": [
                        {
                            "type": "forward",
                            "target_group_arn": f"arn:aws:elasticloadbalancing:eu-central-1:123456789012:targetgroup/{self.project_name}-api-{self.environment}"
                        }
                    ],
                    "rules": [
                        {
                            "priority": 100,
                            "conditions": [
                                {
                                    "field": "path-pattern",
                                    "values": ["/api/v1/fingerprint/*", "/api/v1/audio/*", "/api/v1/video/*", "/api/v1/image/*"]
                                }
                            ],
                            "actions": [
                                {
                                    "type": "forward",
                                    "target_group_arn": f"arn:aws:elasticloadbalancing:eu-central-1:123456789012:targetgroup/{self.project_name}-ai-{self.environment}"
                                }
                            ]
                        }
                    ]
                }
            ],
            "access_logs": {
                "enabled": True,
                "bucket": f"{self.project_name}-{self.environment}-access-logs",
                "prefix": "alb-logs"
            }
        }
    
    def get_kubernetes_ingress_config(self) -> Dict[str, Any]:
        """Get Kubernetes Ingress configuration"""        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.project_name}-ingress",
                "namespace": self.environment,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod" if self.environment == "production" else "letsencrypt-staging",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/use-regex": "true",
                    "nginx.ingress.kubernetes.io/proxy-body-size": "1g",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                    "nginx.ingress.kubernetes.io/enable-cors": "true",
                    "nginx.ingress.kubernetes.io/cors-allow-origin": "*",
                    "nginx.ingress.kubernetes.io/cors-allow-methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "nginx.ingress.kubernetes.io/cors-allow-headers": "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [self.base_domain, f"api.{self.base_domain}", f"ws.{self.base_domain}"],
                        "secretName": f"{self.project_name}-tls"
                    }
                ],
                "rules": [
                    {
                        "host": f"api.{self.base_domain}",
                        "http": {
                            "paths": [
                                {
                                    "path": "/api/v1/fingerprint",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "ai-fingerprinting-service",
                                            "port": {
                                                "number": 8010
                                            }
                                        }
                                    }
                                },
                                {
                                    "path": "/api/v1/audio",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "ai-audio-service",
                                            "port": {
                                                "number": 8020
                                            }
                                        }
                                    }
                                },
                                {
                                    "path": "/api/v1/video",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "ai-video-service",
                                            "port": {
                                                "number": 8030
                                            }
                                        }
                                    }
                                },
                                {
                                    "path": "/api/v1/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "api-backend-service",
                                            "port": {
                                                "number": 8000
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "host": f"ws.{self.base_domain}",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "websocket-realtime-service",
                                            "port": {
                                                "number": 8100
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def export_configurations(self, output_dir: str = "./loadbalancer-configs") -> Dict[str, str]:
        """Export all load balancer configurations to files"""        import os
        os.makedirs(output_dir, exist_ok=True)
        
        configs = {}
        
        # Nginx configuration
        nginx_config = self.generate_nginx_config()
        nginx_path = os.path.join(output_dir, f"nginx-{self.environment}.conf")
        with open(nginx_path, 'w') as f:
            f.write(nginx_config)
        configs['nginx'] = nginx_path
        
        # HAProxy configuration
        haproxy_config = self.generate_haproxy_config()
        haproxy_path = os.path.join(output_dir, f"haproxy-{self.environment}.cfg")
        with open(haproxy_path, 'w') as f:
            f.write(haproxy_config)
        configs['haproxy'] = haproxy_path
        
        # AWS ALB configuration
        aws_alb_config = self.get_aws_alb_config()
        aws_path = os.path.join(output_dir, f"aws-alb-{self.environment}.json")
        with open(aws_path, 'w') as f:
            json.dump(aws_alb_config, f, indent=2)
        configs['aws_alb'] = aws_path
        
        # Kubernetes Ingress configuration
        k8s_ingress_config = self.get_kubernetes_ingress_config()
        k8s_path = os.path.join(output_dir, f"k8s-ingress-{self.environment}.yaml")
        with open(k8s_path, 'w') as f:
            yaml.dump(k8s_ingress_config, f, default_flow_style=False)
        configs['k8s_ingress'] = k8s_path
        
        return configs
