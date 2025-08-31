"""SSL/TLS Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional SSL certificate management and TLS configuration
for multi-format content protection and AI-powered creator monetization platform.

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
from datetime import datetime, timedelta
import ssl
import socket
import subprocess
from pathlib import Path


class CertificateType(Enum):
    """SSL certificate types"""
    SELF_SIGNED = "self_signed"
    LETS_ENCRYPT = "lets_encrypt"
    COMMERCIAL = "commercial"
    WILDCARD = "wildcard"
    EV = "extended_validation"
    MULTI_DOMAIN = "multi_domain"


class TLSVersion(Enum):
    """Supported TLS versions"""
    TLS_1_2 = "TLSv1.2"
    TLS_1_3 = "TLSv1.3"


@dataclass
class CertificateConfig:
    """SSL certificate configuration"""
    domain: str
    cert_type: CertificateType
    key_size: int = 4096
    validity_days: int = 365
    country: str = "DE"
    state: str = "Bavaria"
    city: str = "Munich"
    organization: str = "IA-Influencer Platform"
    organizational_unit: str = "Engineering"
    email: str = "mlaiel@live.de"
    subject_alt_names: List[str] = field(default_factory=list)
    key_usage: List[str] = field(default_factory=lambda: ["digitalSignature", "keyEncipherment"])
    extended_key_usage: List[str] = field(default_factory=lambda: ["serverAuth", "clientAuth"])


@dataclass
class NginxSSLConfig:
    """Nginx SSL configuration"""
    ssl_certificate: str
    ssl_certificate_key: str
    ssl_protocols: List[str] = field(default_factory=lambda: ["TLSv1.2", "TLSv1.3"])
    ssl_ciphers: str = "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
    ssl_prefer_server_ciphers: bool = True
    ssl_session_cache: str = "shared:SSL:50m"
    ssl_session_timeout: str = "1d"
    ssl_stapling: bool = True
    ssl_stapling_verify: bool = True
    add_header_hsts: bool = True
    hsts_max_age: int = 31536000


@dataclass
class LoadBalancerSSLConfig:
    """Load balancer SSL configuration"""
    ssl_policy: str
    certificate_arn: str
    backend_protocol: str = "HTTP"
    backend_port: int = 80
    health_check_path: str = "/health"
    ssl_redirect: bool = True


class SSLConfig:
    """
    Professional SSL/TLS configuration manager for IA-Influencer Agent Platform.
    
    Manages secure communications for:
    - API endpoints and web services
    - AI processing microservices communication
    - Content protection data transmission
    - Real-time WebSocket connections
    - Database connections (SSL/TLS)
    - Inter-service mesh security
    - CDN and load balancer termination
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.base_domain = self._get_base_domain()
        self.cert_directory = self._get_cert_directory()
        
    def _get_base_domain(self) -> str:
        """Get base domain based on environment"""
        domains = {
            "development": "dev.ia-influencer.com",
            "staging": "staging.ia-influencer.com",
            "production": "ia-influencer.com"
        }
        return domains.get(self.environment, "localhost")
    
    def _get_cert_directory(self) -> str:
        """Get certificate storage directory"""
        base_path = f"/etc/ssl/certs/{self.project_name}"
        return f"{base_path}/{self.environment}"
    
    def get_domains_config(self) -> Dict[str, CertificateConfig]:
        """Get SSL certificate configuration for all domains"""
        base_config = {
            "country": "DE",
            "state": "Bavaria", 
            "city": "Munich",
            "organization": "IA-Influencer Platform",
            "organizational_unit": "Engineering",
            "email": "mlaiel@live.de"
        }
        
        domains = {
            # Main API domain
            f"api.{self.base_domain}": CertificateConfig(
                domain=f"api.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"api.{self.base_domain}",
                    f"*.api.{self.base_domain}"
                ],
                **base_config
            ),
            
            # Web application domain
            f"app.{self.base_domain}": CertificateConfig(
                domain=f"app.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"app.{self.base_domain}",
                    f"www.app.{self.base_domain}"
                ],
                **base_config
            ),
            
            # AI services domain
            f"ai.{self.base_domain}": CertificateConfig(
                domain=f"ai.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"ai.{self.base_domain}",
                    f"ml.{self.base_domain}",
                    f"fingerprint.{self.base_domain}",
                    f"audio.{self.base_domain}",
                    f"video.{self.base_domain}",
                    f"image.{self.base_domain}",
                    f"text.{self.base_domain}"
                ],
                **base_config
            ),
            
            # Content protection domain  
            f"protection.{self.base_domain}": CertificateConfig(
                domain=f"protection.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"protection.{self.base_domain}",
                    f"crawlers.{self.base_domain}",
                    f"monitoring.{self.base_domain}",
                    f"alerts.{self.base_domain}"
                ],
                **base_config
            ),
            
            # Revenue and monetization domain
            f"revenue.{self.base_domain}": CertificateConfig(
                domain=f"revenue.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"revenue.{self.base_domain}",
                    f"payments.{self.base_domain}",
                    f"analytics.{self.base_domain}",
                    f"reports.{self.base_domain}"
                ],
                **base_config
            ),
            
            # Admin and management domain
            f"admin.{self.base_domain}": CertificateConfig(
                domain=f"admin.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"admin.{self.base_domain}",
                    f"dashboard.{self.base_domain}",
                    f"management.{self.base_domain}"
                ],
                **base_config
            ),
            
            # WebSocket domain
            f"ws.{self.base_domain}": CertificateConfig(
                domain=f"ws.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"ws.{self.base_domain}",
                    f"websocket.{self.base_domain}",
                    f"realtime.{self.base_domain}"
                ],
                **base_config
            ),
            
            # CDN domain
            f"cdn.{self.base_domain}": CertificateConfig(
                domain=f"cdn.{self.base_domain}",
                cert_type=CertificateType.LETS_ENCRYPT if self.environment == "production" else CertificateType.SELF_SIGNED,
                subject_alt_names=[
                    f"cdn.{self.base_domain}",
                    f"assets.{self.base_domain}",
                    f"media.{self.base_domain}",
                    f"uploads.{self.base_domain}"
                ],
                **base_config
            )
        }
        
        # Add wildcard certificate for production
        if self.environment == "production":
            domains[f"*.{self.base_domain}"] = CertificateConfig(
                domain=f"*.{self.base_domain}",
                cert_type=CertificateType.WILDCARD,
                subject_alt_names=[
                    f"*.{self.base_domain}",
                    self.base_domain
                ],
                **base_config
            )
        
        return domains
    
    def generate_openssl_config(self, cert_config: CertificateConfig) -> str:
        """Generate OpenSSL configuration for certificate"""
        config = f"""[req]
default_bits = {cert_config.key_size}
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C = {cert_config.country}
ST = {cert_config.state}
L = {cert_config.city}
O = {cert_config.organization}
OU = {cert_config.organizational_unit}
CN = {cert_config.domain}
emailAddress = {cert_config.email}

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
"""
        
        # Add subject alternative names
        for i, san in enumerate(cert_config.subject_alt_names, 1):
            if san.startswith("*.") or "." in san:
                config += f"DNS.{i} = {san}\n"
            else:
                config += f"IP.{i} = {san}\n"
        
        return config
    
    def generate_self_signed_certificate(self, cert_config: CertificateConfig) -> Dict[str, str]:
        """Generate self-signed certificate"""
        cert_dir = Path(f"{self.cert_directory}/{cert_config.domain}")
        cert_dir.mkdir(parents=True, exist_ok=True)
        
        key_file = cert_dir / "private.key"
        cert_file = cert_dir / "certificate.crt"
        config_file = cert_dir / "openssl.conf"
        
        # Write OpenSSL config
        with open(config_file, 'w') as f:
            f.write(self.generate_openssl_config(cert_config))
        
        # Generate private key
        key_cmd = [
            "openssl", "genrsa",
            "-out", str(key_file),
            str(cert_config.key_size)
        ]
        subprocess.run(key_cmd, check=True)
        
        # Generate certificate
        cert_cmd = [
            "openssl", "req",
            "-new", "-x509",
            "-key", str(key_file),
            "-out", str(cert_file),
            "-days", str(cert_config.validity_days),
            "-config", str(config_file),
            "-extensions", "v3_req"
        ]
        subprocess.run(cert_cmd, check=True)
        
        # Set proper permissions
        os.chmod(key_file, 0o600)
        os.chmod(cert_file, 0o644)
        
        return {
            "private_key": str(key_file),
            "certificate": str(cert_file),
            "config": str(config_file)
        }
    
    def get_lets_encrypt_config(self, domains: List[str]) -> Dict[str, Any]:
        """Get Let's Encrypt configuration"""
        return {
            "client": "certbot",
            "email": "mlaiel@live.de",
            "domains": domains,
            "webroot_path": "/var/www/certbot",
            "cert_name": f"{self.project_name}-{self.environment}",
            "deploy_hook": f"/etc/letsencrypt/renewal-hooks/deploy/{self.project_name}-reload.sh",
            "renew_hook": f"/etc/letsencrypt/renewal-hooks/renew/{self.project_name}-renew.sh",
            "pre_hook": f"/etc/letsencrypt/renewal-hooks/pre/{self.project_name}-pre.sh",
            "post_hook": f"/etc/letsencrypt/renewal-hooks/post/{self.project_name}-post.sh",
            "rsa_key_size": 4096,
            "elliptic_curve": "secp256r1",
            "must_staple": True,
            "auto_renew": True,
            "renew_before_expiry": 30,
            "test_cert": self.environment != "production"
        }
    
    def get_nginx_ssl_config(self, domain: str) -> NginxSSLConfig:
        """Generate Nginx SSL configuration"""
        cert_path = f"{self.cert_directory}/{domain}"
        
        return NginxSSLConfig(
            ssl_certificate=f"{cert_path}/certificate.crt",
            ssl_certificate_key=f"{cert_path}/private.key",
            ssl_protocols=["TLSv1.2", "TLSv1.3"],
            ssl_ciphers="ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384",
            ssl_prefer_server_ciphers=True,
            ssl_session_cache="shared:SSL:50m",
            ssl_session_timeout="1d",
            ssl_stapling=True,
            ssl_stapling_verify=True,
            add_header_hsts=True,
            hsts_max_age=31536000 if self.environment == "production" else 300
        )
    
    def generate_nginx_server_block(self, domain: str, upstream_name: str, upstream_port: int = 8000) -> str:
        """Generate Nginx server block with SSL configuration"""
        ssl_config = self.get_nginx_ssl_config(domain)
        
        return f"""# HTTP redirect to HTTPS
server {{
    listen 80;
    listen [::]:80;
    server_name {domain} www.{domain};
    
    location /.well-known/acme-challenge/ {{
        root /var/www/certbot;
    }}
    
    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}

# HTTPS server block
server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {domain} www.{domain};
    
    # SSL configuration
    ssl_certificate {ssl_config.ssl_certificate};
    ssl_certificate_key {ssl_config.ssl_certificate_key};
    ssl_protocols {' '.join(ssl_config.ssl_protocols)};
    ssl_ciphers {ssl_config.ssl_ciphers};
    ssl_prefer_server_ciphers {'on' if ssl_config.ssl_prefer_server_ciphers else 'off'};
    ssl_session_cache {ssl_config.ssl_session_cache};
    ssl_session_timeout {ssl_config.ssl_session_timeout};
    
    # OCSP Stapling
    ssl_stapling {'on' if ssl_config.ssl_stapling else 'off'};
    ssl_stapling_verify {'on' if ssl_config.ssl_stapling_verify else 'off'};
    
    # Security headers
    add_header Strict-Transport-Security "max-age={ssl_config.hsts_max_age}; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https: wss:; media-src 'self' https:; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'" always;
    
    # Logging
    access_log /var/log/nginx/{domain}_access.log;
    error_log /var/log/nginx/{domain}_error.log;
    
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
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone={upstream_name}_rate_limit:10m rate=10r/s;
    limit_req zone={upstream_name}_rate_limit burst=20 nodelay;
    
    # Client settings
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    keepalive_timeout 65s;
    
    # Proxy settings
    location / {{
        proxy_pass http://{upstream_name};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Health check
        proxy_intercept_errors on;
        error_page 502 503 504 /50x.html;
    }}
    
    # Health check endpoint
    location /health {{
        access_log off;
        proxy_pass http://{upstream_name}/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files
    location /static/ {{
        alias /var/www/{domain}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }}
    
    # Media files
    location /media/ {{
        alias /var/www/{domain}/media/;
        expires 30d;
        add_header Cache-Control "public";
    }}
    
    # Error pages
    location = /50x.html {{
        root /var/www/html;
    }}
    
    # Security
    location ~ /\\.ht {{
        deny all;
    }}
    
    location ~ /\\. {{
        deny all;
    }}
}}

# Upstream configuration
upstream {upstream_name} {{
    least_conn;
    server 127.0.0.1:{upstream_port} max_fails=3 fail_timeout=30s;
    server 127.0.0.1:{upstream_port + 1} max_fails=3 fail_timeout=30s backup;
    
    keepalive 32;
}}
"""
    
    def get_aws_alb_ssl_config(self) -> LoadBalancerSSLConfig:
        """Get AWS Application Load Balancer SSL configuration"""
        return LoadBalancerSSLConfig(
            ssl_policy="ELBSecurityPolicy-TLS-1-2-2019-07",
            certificate_arn=f"arn:aws:acm:eu-central-1:123456789012:certificate/{self.project_name}-{self.environment}",
            backend_protocol="HTTP",
            backend_port=8000,
            health_check_path="/health",
            ssl_redirect=True
        )
    
    def get_cloudflare_ssl_config(self) -> Dict[str, Any]:
        """Get Cloudflare SSL configuration"""
        return {
            "ssl_mode": "full_strict" if self.environment == "production" else "full",
            "min_tls_version": "1.2",
            "cipher_suites": [
                "ECDHE-ECDSA-AES128-GCM-SHA256",
                "ECDHE-ECDSA-AES256-GCM-SHA384",
                "ECDHE-RSA-AES128-GCM-SHA256",
                "ECDHE-RSA-AES256-GCM-SHA384"
            ],
            "hsts": {
                "enabled": True,
                "max_age": 31536000,
                "include_subdomains": True,
                "preload": True
            },
            "always_use_https": True,
            "automatic_https_rewrites": True,
            "security_headers": {
                "strict_transport_security": {
                    "enabled": True,
                    "max_age": 31536000,
                    "include_subdomains": True,
                    "preload": True
                }
            },
            "edge_certificates": {
                "universal_ssl": True,
                "dedicated_certificates": self.environment == "production"
            }
        }
    
    def check_certificate_expiry(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """Check SSL certificate expiry"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse certificate dates
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    # Calculate remaining days
                    now = datetime.now()
                    days_until_expiry = (not_after - now).days
                    
                    return {
                        "domain": domain,
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "subject": dict(x[0] for x in cert['subject']),
                        "serial_number": cert['serialNumber'],
                        "version": cert['version'],
                        "not_before": not_before,
                        "not_after": not_after,
                        "days_until_expiry": days_until_expiry,
                        "is_valid": now >= not_before and now <= not_after,
                        "expires_soon": days_until_expiry <= 30,
                        "subject_alt_names": cert.get('subjectAltName', [])
                    }
        except Exception as e:
            return {
                "domain": domain,
                "error": str(e),
                "is_valid": False,
                "expires_soon": True
            }
    
    def generate_cert_renewal_script(self) -> str:
        """Generate certificate renewal script"""
        script = f"""#!/bin/bash
# SSL Certificate Renewal Script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -euo pipefail

ENVIRONMENT="{self.environment}"
PROJECT_NAME="{self.project_name}"
BASE_DOMAIN="{self.base_domain}"
CERT_DIR="{self.cert_directory}"
LOG_FILE="/var/log/{self.project_name}/cert-renewal.log"

# Logging function
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log "ERROR: This script must be run as root"
    exit 1
fi

log "Starting SSL certificate renewal for $ENVIRONMENT environment"

# Renew Let's Encrypt certificates
if command -v certbot >/dev/null 2>&1; then
    log "Renewing Let's Encrypt certificates..."
    certbot renew --quiet --no-self-upgrade --deploy-hook "systemctl reload nginx"
    
    if [[ $? -eq 0 ]]; then
        log "Let's Encrypt certificates renewed successfully"
    else
        log "ERROR: Let's Encrypt renewal failed"
        exit 1
    fi
fi

# Check certificate expiry for all domains
DOMAINS=(
    "api.$BASE_DOMAIN"
    "app.$BASE_DOMAIN"
    "ai.$BASE_DOMAIN"
    "protection.$BASE_DOMAIN"
    "revenue.$BASE_DOMAIN"
    "admin.$BASE_DOMAIN"
    "ws.$BASE_DOMAIN"
    "cdn.$BASE_DOMAIN"
)

for domain in "${{DOMAINS[@]}}"; do
    log "Checking certificate expiry for $domain..."
    
    if openssl s_client -servername "$domain" -connect "$domain:443" </dev/null 2>/dev/null | \
       openssl x509 -noout -checkend $((30 * 24 * 3600)) >/dev/null 2>&1; then
        log "$domain certificate is valid for more than 30 days"
    else
        log "WARNING: $domain certificate expires within 30 days"
        # Send notification
        curl -X POST "https://api.slack.com/api/chat.postMessage" \
             -H "Authorization: Bearer $SLACK_TOKEN" \
             -H "Content-Type: application/json" \
             -d "{{
                 \"channel\": \"#alerts\",
                 \"text\": \"🚨 SSL Certificate Warning: $domain expires within 30 days\"
             }}" || true
    fi
done

# Reload web server
if systemctl is-active --quiet nginx; then
    log "Reloading Nginx configuration..."
    nginx -t && systemctl reload nginx
    log "Nginx reloaded successfully"
fi

# Update Kubernetes secrets if running in K8s
if command -v kubectl >/dev/null 2>&1; then
    log "Updating Kubernetes TLS secrets..."
    
    for domain in "${{DOMAINS[@]}}"; do
        CERT_FILE="$CERT_DIR/$domain/certificate.crt"
        KEY_FILE="$CERT_DIR/$domain/private.key"
        
        if [[ -f "$CERT_FILE" && -f "$KEY_FILE" ]]; then
            kubectl create secret tls "$domain-tls" \
                --cert="$CERT_FILE" \
                --key="$KEY_FILE" \
                --namespace="$ENVIRONMENT" \
                --dry-run=client -o yaml | kubectl apply -f -
            log "Updated TLS secret for $domain"
        fi
    done
fi

log "SSL certificate renewal completed successfully"
"""
        return script
    
    def export_configurations(self, output_dir: str = "./ssl-configs") -> Dict[str, str]:
        """Export all SSL configurations to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        configs = {}
        domains_config = self.get_domains_config()
        
        # Export domain configurations
        for domain, cert_config in domains_config.items():
            domain_dir = os.path.join(output_dir, domain.replace("*.", "wildcard."))
            os.makedirs(domain_dir, exist_ok=True)
            
            # OpenSSL config
            openssl_config = self.generate_openssl_config(cert_config)
            openssl_path = os.path.join(domain_dir, "openssl.conf")
            with open(openssl_path, 'w') as f:
                f.write(openssl_config)
            
            # Nginx server block
            nginx_config = self.generate_nginx_server_block(
                domain.replace("*.", ""),
                f"{domain.replace('.', '_').replace('*', 'wildcard')}_upstream"
            )
            nginx_path = os.path.join(domain_dir, "nginx.conf")
            with open(nginx_path, 'w') as f:
                f.write(nginx_config)
            
            configs[domain] = {
                "openssl_config": openssl_path,
                "nginx_config": nginx_path
            }
        
        # Export renewal script
        renewal_script = self.generate_cert_renewal_script()
        renewal_path = os.path.join(output_dir, f"renew-certs-{self.environment}.sh")
        with open(renewal_path, 'w') as f:
            f.write(renewal_script)
        os.chmod(renewal_path, 0o755)
        configs['renewal_script'] = renewal_path
        
        # Export Let's Encrypt config
        lets_encrypt_config = self.get_lets_encrypt_config(list(domains_config.keys()))
        lets_encrypt_path = os.path.join(output_dir, f"letsencrypt-{self.environment}.json")
        with open(lets_encrypt_path, 'w') as f:
            import json
            json.dump(lets_encrypt_config, f, indent=2)
        configs['lets_encrypt'] = lets_encrypt_path
        
        return configs
