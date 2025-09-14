"""IA Influencer Agent - SSL/TLS Examples
Industrial-grade examples for SSL/TLS management operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Team Expertise:
    - Lead Dev IA + Backend Senior + ML Engineer
- DBA + Security Expert + Microservices Architect
- Audio Processing + DevOps + Prompt Engineering

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized copying, distribution, or use without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .cert_manager import CertificateManager, create_certificate_manager
from .letsencrypt_manager import LetsEncryptManager, LetsEncryptConfig, CertificateRequest, ChallengeType
from .tls_config import TLSConfigManager, TLSConfig, create_tls_config_manager
from .cert_monitor import CertificateMonitor, CertificateEndpoint, create_certificate_monitor
from .ssl_utils import (
    SSLScanner, SSLValidator, CertificateConverter, SSLTestServer,
    validate_ssl_configuration, generate_csr, create_self_signed_cert
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSLExamplesRunner:
    """Industrial-grade SSL/TLS examples runner"""
    
    def __init__(self) -> None:
        self.cert_manager = create_certificate_manager()
        self.tls_config_manager = create_tls_config_manager()
        self.cert_monitor = create_certificate_monitor()
        self.ssl_scanner = SSLScanner()
        self.ssl_validator = SSLValidator()
        self.cert_converter = CertificateConverter()
        self.test_server = SSLTestServer()


# Industrial-grade TLS Configuration Examples
PRODUCTION_TLS_CONFIG = {
    "min_version": "TLSv1.2",
    "max_version": "TLSv1.3",
    "cipher_suites": [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-RSA-AES128-GCM-SHA256"
    ],
    "certificate_path": "/etc/ssl/certs/ia-influencer.pem",
    "private_key_path": "/etc/ssl/private/ia-influencer.key",
    "ca_bundle_path": "/etc/ssl/certs/ca-bundle.pem",
    "enable_hsts": True,
    "hsts_max_age": 31536000,  # 1 year
    "hsts_include_subdomains": True,
    "hsts_preload": True,
    "enable_ocsp_stapling": True,
    "enable_session_resumption": True,
    "session_timeout": 300,
    "enable_compression": False,  # Prevent CRIME attacks
    "require_client_cert": False,
    "verify_client_cert": True,
    "dh_param_size": 2048,
    "session_cache_size": 10485760,  # 10MB
    "client_ca_path": "/etc/ssl/certs/client-ca.pem"
}

# Let's Encrypt Production Configuration
LETSENCRYPT_PRODUCTION_CONFIG = {
    "email": "ssl-admin@ia-influencer.com",
    "staging": False,
    "key_size": 2048,
    "challenge_type": "http-01",
    "webroot_path": "/var/www/html",
    "renewal_days": 30,
    "max_attempts": 3,
    "attempt_delay": 10,
    "dns_provider": None,
    "dns_credentials": {}
}

# Let's Encrypt DNS Configuration (Cloudflare)
LETSENCRYPT_DNS_CONFIG = {
    "email": "ssl-admin@ia-influencer.com",
    "staging": False,
    "key_size": 2048,
    "challenge_type": "dns-01",
    "dns_provider": "cloudflare",
    "dns_credentials": {
        "api_token": "your-cloudflare-api-token",
        "zone_id": "your-cloudflare-zone-id"
    },
    "renewal_days": 30,
    "max_attempts": 3,
    "attempt_delay": 10
}

# Production Monitoring Configuration
PRODUCTION_MONITORING_CONFIG = {
    "endpoints": [
        {
            "name": "main-api",
            "host": "api.ia-influencer.com",
            "port": 443,
            "check_interval": 3600,  # 1 hour
            "alert_days": 30,
            "critical_days": 7,
            "enabled": True,
            "verify_hostname": True,
            "verify_chain": True,
            "check_ocsp": True,
            "tags": ["production", "api", "critical"]
        },
        {
            "name": "web-frontend",
            "host": "ia-influencer.com",
            "port": 443,
            "check_interval": 3600,
            "alert_days": 30,
            "critical_days": 7,
            "enabled": True,
            "verify_hostname": True,
            "verify_chain": True,
            "check_ocsp": True,
            "tags": ["production", "web", "critical"]
        },
        {
            "name": "cdn-endpoint",
            "host": "cdn.ia-influencer.com",
            "port": 443,
            "check_interval": 7200,  # 2 hours
            "alert_days": 45,
            "critical_days": 14,
            "enabled": True,
            "verify_hostname": True,
            "verify_chain": True,
            "check_ocsp": False,
            "tags": ["production", "cdn"]
        }
    ],
    "notifications": {
        "email": {
            "enabled": True,
            "smtp_server": "smtp.ia-influencer.com",
            "smtp_port": 587,
            "username": "ssl-alerts@ia-influencer.com",
            "password": "your-smtp-password",
            "use_tls": True,
            "recipients": [
                "devops@ia-influencer.com",
                "security@ia-influencer.com",
                "fahed.mlaiel@ia-influencer.com"
            ]
        },
        "webhook": {
            "enabled": True,
            "url": "https://api.ia-influencer.com/webhooks/ssl-alerts",
            "headers": {
                "Authorization": "Bearer your-webhook-token",
                "Content-Type": "application/json"
            }
        },
        "slack": {
            "enabled": True,
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "channel": "#ssl-alerts"
        }
    },
    "logging": {
        "file_path": "/var/log/ssl-monitor.log",
        "level": "INFO",
        "rotate": True,
        "max_size": "100MB",
        "backup_count": 5
    }
}


def example_basic_certificate_management() -> None:
    """Example: Basic certificate management operations"""
    print("=== Basic Certificate Management Example ===")
    
    runner = SSLExamplesRunner()
    
    try:
        # Create a self-signed certificate for testing
        domain = "test.example.com"
        cert_data, key_data = create_self_signed_cert(
            domain=domain,
            key_size=2048,
            validity_days=365,
            country="US",
            state="CA",
            city="San Francisco",
            organization="IA Influencer Agent",
            organizational_unit="SSL Testing"
        )
        
        # Save certificate files
        cert_path = Path(f"{domain}_cert.pem")
        key_path = Path(f"{domain}_key.pem")
        
        with open(cert_path, 'wb') as f:
            f.write(cert_data)
        
        with open(key_path, 'wb') as f:
            f.write(key_data)
        
        print(f"# [EMOJI_REMOVED] Self-signed certificate created for {domain}")
        print(f"  Certificate: {cert_path.absolute()}")
        print(f"  Private key: {key_path.absolute()}")
        
        # Validate the certificate
        validation_result = runner.ssl_validator.validate_certificate(cert_data)
        print(f"# [EMOJI_REMOVED] Certificate validation: {'Valid' if validation_result.is_valid else 'Invalid'}")
        print(f"  Subject: {validation_result.subject}")
        print(f"  Issuer: {validation_result.issuer}")
        print(f"  Expiry: {validation_result.not_after}")
        
        # List managed certificates
        certificates = runner.cert_manager.list_certificates()
        print(f"# [EMOJI_REMOVED] Total managed certificates: {len(certificates)}")
        
    except Exception as e:
        print(f"# [EMOJI_REMOVED] Error in certificate management example: {e}")


def example_letsencrypt_certificate() -> None:
    """Example: Let's Encrypt certificate issuance"""
    print("\n=== Let's Encrypt Certificate Example ===")
    
    try:
        # Configure Let's Encrypt (staging environment for testing)
        config = LetsEncryptConfig(
            email="admin@example.com",
            staging=True,  # Use staging for testing
            key_size=2048,
            dns_provider="cloudflare",  # Example DNS provider
            dns_credentials={
                "api_token": "your_cloudflare_api_token"
            }
        )
        
        letsencrypt_manager = LetsEncryptManager(config)
        
        # Create certificate request
        cert_request = CertificateRequest(
            domains=["example.com", "www.example.com"],
            challenge_type=ChallengeType.DNS_01,
            key_size=2048,
            organization="IA Influencer Agent",
            organizational_unit="Web Services"
        )
        
        print(f"# [EMOJI_REMOVED] Certificate request created for domains: {cert_request.domains}")
        print(f"  Challenge type: {cert_request.challenge_type.value}")
        print(f"  Key size: {cert_request.key_size}")
        print("# [EMOJI_REMOVED]  Note: This example uses staging environment")
        print("   For production, set staging=False in LetsEncryptConfig")
        
        # In a real scenario, you would call:
        # result = letsencrypt_manager.issue_certificate(cert_request)
        
    except Exception as e:
        print(f"# [EMOJI_REMOVED] Error in Let's Encrypt example: {e}")
        check_interval=3600,
        warning_days=30,
        critical_days=7,
        enabled=True,
        verify_hostname=True,
        verify_chain=True,
        check_ocsp=True,
        tags=["production", "web", "high"]
    ),
    CertificateEndpoint(
        name="cdn-endpoint",
        hostname="cdn.ia-influencer.com",
        port=443,
        check_interval=7200,  # 2 hours
        warning_days=30,
        critical_days=7,
        enabled=True,
        verify_hostname=True,
        verify_chain=True,
        check_ocsp=True,
        tags=["production", "cdn", "medium"]
    ),
    CertificateEndpoint(
        name="admin-panel",
        hostname="admin.ia-influencer.com",
        port=443,
        check_interval=3600,
        warning_days=30,
        critical_days=7,
        enabled=True,
        verify_hostname=True,
        verify_chain=True,
        check_ocsp=True,
        tags=["production", "admin", "high"]
    )
]

# Nginx Production Configuration
NGINX_PRODUCTION_CONFIG = NginxTLSConfig(
    server_name="api.ia-influencer.com",
    listen_port=443,
    http_redirect=True,
    http_port=80,
    ssl_certificate="/etc/ssl/certs/ia-influencer.pem",
    ssl_certificate_key="/etc/ssl/private/ia-influencer.key",
    ssl_trusted_certificate="/etc/ssl/certs/ca-bundle.pem",
    ssl_prefer_server_ciphers=True,
    add_header_hsts=True,
    add_header_csp=True,
    add_header_xframe=True,
    add_header_xcontent=True,
    ssl_session_cache="shared:SSL:50m",
    ssl_session_timeout="1d",
    ssl_stapling=True,
    ssl_stapling_verify=True,
    custom_directives=[
        "add_header X-Robots-Tag noindex",
        "add_header Referrer-Policy strict-origin-when-cross-origin",
        "add_header Permissions-Policy \"geolocation=(), microphone=(), camera=()\""
    ]
)

# Apache Production Configuration  
APACHE_PRODUCTION_CONFIG = ApacheTLSConfig(
    server_name="api.ia-influencer.com",
    document_root="/var/www/ia-influencer",
    virtual_host_port=443,
    ssl_certificate_file="/etc/ssl/certs/ia-influencer.pem",
    ssl_certificate_key_file="/etc/ssl/private/ia-influencer.key",
    ssl_certificate_chain_file="/etc/ssl/certs/ca-bundle.pem",
    ssl_honor_cipher_order=True,
    ssl_compression=False,
    ssl_session_tickets=False,
    ssl_use_stapling=True,
    header_always_set=[
        "Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\"",
        "Header always set X-Frame-Options \"SAMEORIGIN\"",
        "Header always set X-Content-Type-Options \"nosniff\"",
        "Header always set Referrer-Policy \"strict-origin-when-cross-origin\"",
        "Header always set Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'\""
    ],
    custom_directives=[
        "Header always set X-Robots-Tag \"noindex\"",
        "SSLOptions +StrictRequire",
        "SSLProtocol -all +TLSv1.2 +TLSv1.3"
    ]
)

# Development/Staging Configuration
STAGING_TLS_CONFIG = TLSConfig(
    min_tls_version=TLSVersion.TLSv1_2,
    max_tls_version=TLSVersion.TLSv1_3,
    cipher_suite=CipherSuite.INTERMEDIATE,
    security_level=SecurityLevel.MEDIUM,
    certificate_path="/etc/ssl/certs/staging-ia-influencer.pem",
    private_key_path="/etc/ssl/private/staging-ia-influencer.key",
    enable_hsts=True,
    hsts_max_age=86400,  # 1 day for staging
    hsts_include_subdomains=False,
    hsts_preload=False,
    enable_ocsp_stapling=True,
    enable_session_tickets=False,
    enable_compression=False
)

# Staging Let's Encrypt Configuration
LETSENCRYPT_STAGING_CONFIG = LetsEncryptConfig(
    email="ssl-staging@ia-influencer.com",
    staging=True,  # Use staging environment
    key_size=2048,
    challenge_type=ChallengeType.HTTP_01,
    webroot_path="/var/www/staging",
    renewal_days=7  # More frequent renewal for testing
)

# High Security Configuration (for sensitive endpoints)
HIGH_SECURITY_TLS_CONFIG = TLSConfig(
    min_tls_version=TLSVersion.TLSv1_3,  # TLS 1.3 only
    max_tls_version=TLSVersion.TLSv1_3,
    cipher_suite=CipherSuite.MODERN,
    security_level=SecurityLevel.MAXIMUM,
    certificate_path="/etc/ssl/certs/secure-ia-influencer.pem",
    private_key_path="/etc/ssl/private/secure-ia-influencer.key",
    enable_hsts=True,
    hsts_max_age=63072000,  # 2 years
    hsts_include_subdomains=True,
    hsts_preload=True,
    enable_ocsp_stapling=True,
    enable_session_tickets=False,
    enable_compression=False,
    enable_renegotiation=False,
    verify_client_cert=True,  # Require client certificates
    client_ca_path="/etc/ssl/certs/client-ca.pem",
    client_cert_optional=False,
    dh_param_size=4096,  # Stronger DH parameters
    session_cache=False   # Disable session cache for maximum security
)

def export_monitoring_config(output_path: Path) -> None:
    """Export complete monitoring configuration to file"""
    monitoring_config = {
        "endpoints": [
            {
                "name": endpoint.name,
                "hostname": endpoint.hostname,
                "port": endpoint.port,
                "check_interval": endpoint.check_interval,
                "warning_days": endpoint.warning_days,
                "critical_days": endpoint.critical_days,
                "enabled": endpoint.enabled,
                "verify_hostname": endpoint.verify_hostname,
                "verify_chain": endpoint.verify_chain,
                "check_ocsp": endpoint.check_ocsp,
                "tags": endpoint.tags or []
            }
            for endpoint in PRODUCTION_ENDPOINTS
        ],
        "alerts": {
            "email_enabled": PRODUCTION_ALERT_CONFIG.email_enabled,
            "email_recipients": PRODUCTION_ALERT_CONFIG.email_recipients,
            "email_smtp_server": PRODUCTION_ALERT_CONFIG.email_smtp_server,
            "email_smtp_port": PRODUCTION_ALERT_CONFIG.email_smtp_port,
            "email_username": PRODUCTION_ALERT_CONFIG.email_username,
            "email_use_tls": PRODUCTION_ALERT_CONFIG.email_use_tls,
            "slack_enabled": PRODUCTION_ALERT_CONFIG.slack_enabled,
            "slack_channel": PRODUCTION_ALERT_CONFIG.slack_channel,
            "pagerduty_enabled": PRODUCTION_ALERT_CONFIG.pagerduty_enabled,
            "webhook_enabled": PRODUCTION_ALERT_CONFIG.webhook_enabled,
            "webhook_url": PRODUCTION_ALERT_CONFIG.webhook_url,
            "log_file_path": PRODUCTION_ALERT_CONFIG.log_file_path,
            "log_level": PRODUCTION_ALERT_CONFIG.log_level
        },
        "monitoring": {
            "alert_cooldown": 3600  # 1 hour cooldown between same alerts
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(monitoring_config, f, indent=2)

def generate_docker_compose_ssl() -> str:
    """Generate Docker Compose SSL configuration"""
    return """version: '3.8'

services:
  ssl-monitor:
    build: .
    container_name: ia-influencer-ssl-monitor
    restart: unless-stopped
    volumes:
      - /etc/ssl:/etc/ssl:ro
      - /var/log:/var/log
      - ./ssl-monitor-config.json:/app/config/monitor.json:ro
    environment:
      - SSL_MONITOR_CONFIG=/app/config/monitor.json
      - LOG_LEVEL=INFO
    networks:
      - ia-influencer-network
    healthcheck:
      test: ["CMD", "python", "-c", "import ssl_tls; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx-ssl:
    image: nginx:alpine
    container_name: ia-influencer-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/ssl:/etc/ssl:ro
      - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
      - /var/www/html:/var/www/html:ro
    depends_on:
      - ssl-monitor
    networks:
      - ia-influencer-network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  ia-influencer-network:
    driver: bridge
    
volumes:
  ssl-certs:
    driver: local
"""def generate_systemd_service() -> str:
    """Generate systemd service configuration"""
    return """[Unit]
Description=IA Influencer Agent SSL Certificate Monitor
After=network.target
Wants=network.target

[Service]
Type=exec
User=ssl-monitor
Group=ssl-monitor
WorkingDirectory=/opt/ia-influencer/ssl-monitor
ExecStart=/opt/ia-influencer/ssl-monitor/venv/bin/python -m ssl_tls.cli monitor --start-monitoring --config /etc/ia-influencer/ssl-monitor.json
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ia-ssl-monitor

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log /etc/ssl/private
ReadOnlyPaths=/etc/ssl/certs

# Resource limits
LimitNOFILE=65536
MemoryMax=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
"""def generate_logrotate_config() -> str:
    """Generate logrotate configuration"""
    return """/var/log/ssl-monitor.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 ssl-monitor ssl-monitor
    postrotate
        /bin/systemctl reload ia-ssl-monitor
    endscript
}

/var/log/ssl_manager.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 ssl-monitor ssl-monitor
}
"""if __name__ == "__main__":
    # Export example configurations
    output_dir = Path("examples/configs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export monitoring configuration
    export_monitoring_config(output_dir / "ssl-monitor-production.json")
    
    # Export Docker Compose
    with open(output_dir / "docker-compose.yml", "w") as f:
        f.write(generate_docker_compose_ssl())
    
    # Export systemd service
    with open(output_dir / "ia-ssl-monitor.service", "w") as f:
        f.write(generate_systemd_service())
    
    # Export logrotate config
    with open(output_dir / "ssl-monitor-logrotate", "w") as f:
        f.write(generate_logrotate_config())
    
    print("# [EMOJI_REMOVED] SSL/TLS example configurations exported to examples/configs/")

# File has syntax issues - needs manual review