# SSL/TLS Deployment Module

**⚠️ PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED ⚠️**

**Author:** Fahed Mlaiel (mlaiel@live.de)

**Team Expertise:** Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + Microservices Architect + Audio Processing + DevOps + Prompt Engineering

---

## 🚨 INTELLECTUAL PROPERTY NOTICE

This code and all concepts contained within are the exclusive intellectual property of **Fahed Mlaiel**. Any unauthorized copying, distribution, modification, or use without explicit written permission is strictly prohibited and will result in legal action.

**Contact:** mlaiel@live.de for licensing inquiries.

---

## 📋 Overview

Enterprise-grade SSL/TLS certificate management and deployment system for the IA Influencer Agent platform. This module provides comprehensive certificate lifecycle management, automated provisioning, monitoring, and security compliance.

## 🎯 Core Features

### 🔐 Certificate Management
- **Certificate Generation**: RSA/ECDSA key generation with configurable sizes
- **CSR Creation**: Full Certificate Signing Request generation with SAN support
- **Format Conversion**: PEM/DER format conversion utilities
- **Validation**: Comprehensive certificate and key validation
- **Chain Verification**: Complete certificate chain validation

### 🤖 Let's Encrypt Integration
- **ACME v2 Protocol**: Full compliance with latest ACME specification
- **Challenge Support**: HTTP-01, DNS-01, and TLS-ALPN-01 challenges
- **DNS Provider APIs**: Cloudflare, Route53, and custom provider support
- **Automated Renewal**: Intelligent certificate renewal management
- **Staging Environment**: Safe testing with Let's Encrypt staging

### ⚙️ TLS Configuration
- **Security Profiles**: Modern, Intermediate, and Legacy configurations
- **Web Server Support**: Nginx and Apache configuration generation
- **Cipher Management**: Mozilla SSL Configuration guidelines compliance
- **Protocol Selection**: TLS 1.0 through TLS 1.3 support
- **Security Headers**: HSTS, CSP, and security header automation

### 📊 Certificate Monitoring
- **Real-time Monitoring**: Continuous certificate status monitoring
- **Expiry Alerts**: Configurable warning and critical thresholds
- **Multi-channel Alerts**: Email, Slack, Webhook, and PagerDuty integration
- **Performance Metrics**: SSL handshake and connection performance tracking
- **Health Reporting**: Comprehensive certificate health dashboards

### 🛠️ Utilities & Tools
- **SSL Scanner**: Remote SSL configuration analysis
- **Security Analysis**: SSLLABS-style security grading
- **CLI Tools**: Complete command-line interface for all operations
- **Test Server**: Built-in SSL test server for certificate validation
- **OpenSSL Integration**: Native OpenSSL command integration

## 🏗️ Architecture

```
ssl_tls/
├── __init__.py              # Module initialization and exports
├── cert_manager.py          # Core certificate management
├── letsencrypt_manager.py   # Let's Encrypt ACME integration
├── tls_config.py           # TLS configuration management
├── cert_monitor.py         # Certificate monitoring system
├── ssl_utils.py            # SSL utilities and validation
└── cli.py                  # Command-line interface
```

## 🚀 Quick Start

### Basic Certificate Validation
```python
from ssl_tls import SSLValidator, validate_ssl_configuration

# Validate certificate file
result = SSLValidator.validate_certificate_file(Path('/etc/ssl/cert.pem'))

# Validate complete SSL configuration
config_result = validate_ssl_configuration(
    cert_path=Path('/etc/ssl/cert.pem'),
    key_path=Path('/etc/ssl/private/key.pem')
)
```

### Let's Encrypt Certificate Request
```python
from ssl_tls import LetsEncryptManager, LetsEncryptConfig, CertificateRequest

config = LetsEncryptConfig(
    email="admin@example.com",
    staging=False,
    challenge_type=ChallengeType.HTTP_01,
    webroot_path="/var/www/html"
)

manager = LetsEncryptManager(config)
cert_request = CertificateRequest(
    domains=["example.com", "www.example.com"],
    email="admin@example.com",
    challenge_type=ChallengeType.HTTP_01
)

cert_pem, key_pem, chain_pem = manager.request_certificate(cert_request)
```

### Certificate Monitoring
```python
from ssl_tls import CertificateMonitor, CertificateEndpoint

monitor = CertificateMonitor()

# Add endpoint for monitoring
endpoint = CertificateEndpoint(
    name="production-api",
    hostname="api.example.com",
    port=443,
    warning_days=30,
    critical_days=7
)

monitor.add_endpoint(endpoint)

# Start monitoring
import asyncio
asyncio.run(monitor.start_monitoring())
```

### TLS Configuration Generation
```python
from ssl_tls import TLSConfigManager, TLSConfig, NginxTLSConfig

tls_manager = TLSConfigManager()

# Create TLS configuration
tls_config = TLSConfig(
    min_tls_version=TLSVersion.TLSv1_2,
    cipher_suite=CipherSuite.MODERN,
    enable_hsts=True,
    enable_ocsp_stapling=True
)

# Generate Nginx configuration
nginx_config = NginxTLSConfig(
    server_name="example.com",
    ssl_certificate="/etc/ssl/cert.pem",
    ssl_certificate_key="/etc/ssl/private/key.pem"
)

config_content = tls_manager.generate_nginx_config(tls_config, nginx_config)
```

## 🖥️ CLI Usage

### Certificate Validation
```bash
# Validate certificate file
python -m ssl_tls.cli validate-cert /etc/ssl/cert.pem

# Validate SSL configuration
python -m ssl_tls.cli validate-config /etc/ssl/cert.pem /etc/ssl/private/key.pem

# Scan remote host
python -m ssl_tls.cli scan example.com --port 443
```

### Certificate Generation
```bash
# Generate CSR
python -m ssl_tls.cli generate-csr example.com "Example Org" US \
    --state "California" --city "San Francisco" \
    --email admin@example.com --key-size 2048

# Request Let's Encrypt certificate
python -m ssl_tls.cli letsencrypt example.com,www.example.com admin@example.com \
    --challenge-type http-01 --webroot-path /var/www/html
```

### Certificate Monitoring
```bash
# Add monitoring endpoint
python -m ssl_tls.cli monitor --add-endpoint \
    --endpoint-name "prod-api" --hostname api.example.com \
    --port 443 --warning-days 30 --critical-days 7

# Check all endpoints
python -m ssl_tls.cli monitor --check-now

# Start continuous monitoring
python -m ssl_tls.cli monitor --start-monitoring
```

### Configuration Generation
```bash
# Generate Nginx configuration
python -m ssl_tls.cli generate-config nginx example.com \
    /etc/ssl/cert.pem /etc/ssl/private/key.pem \
    /etc/nginx/sites-available/example.com.conf \
    --cipher-suite modern --enable-hsts

# Generate Apache configuration
python -m ssl_tls.cli generate-config apache example.com \
    /etc/ssl/cert.pem /etc/ssl/private/key.pem \
    /etc/apache2/sites-available/example.com.conf \
    --document-root /var/www/html
```

## 📋 Configuration Examples

### Let's Encrypt Configuration
```python
config = LetsEncryptConfig(
    email="admin@example.com",
    staging=False,  # Use production environment
    key_size=2048,
    challenge_type=ChallengeType.DNS_01,  # DNS challenge
    dns_provider="cloudflare",
    dns_credentials={
        "api_token": "your-cloudflare-token",
        "zone_id": "your-zone-id"
    },
    renewal_days=30
)
```

### TLS Security Configuration
```python
# High security configuration
tls_config = TLSConfig(
    min_tls_version=TLSVersion.TLSv1_2,
    max_tls_version=TLSVersion.TLSv1_3,
    cipher_suite=CipherSuite.MODERN,
    security_level=SecurityLevel.HIGH,
    enable_hsts=True,
    hsts_max_age=31536000,  # 1 year
    hsts_include_subdomains=True,
    hsts_preload=True,
    enable_ocsp_stapling=True,
    enable_session_tickets=False,  # Disabled for security
    enable_compression=False,      # Disabled to prevent CRIME
    dh_param_size=2048
)
```

### Monitoring Configuration
```python
# Email alerts configuration
alert_config = AlertConfig(
    email_enabled=True,
    email_recipients=["admin@example.com", "security@example.com"],
    email_smtp_server="smtp.example.com",
    email_smtp_port=587,
    email_username="alerts@example.com",
    email_password="smtp-password",
    email_use_tls=True,
    
    # Slack integration
    slack_enabled=True,
    slack_webhook_url="https://hooks.slack.com/...",
    slack_channel="#ssl-alerts",
    
    # PagerDuty integration
    pagerduty_enabled=True,
    pagerduty_integration_key="your-pagerduty-key"
)
```

## 🔧 Dependencies

### Core Dependencies
- `cryptography` - Certificate and cryptographic operations
- `requests` - HTTP operations and API calls
- `schedule` - Task scheduling for monitoring
- `psutil` - System performance monitoring

### Optional Dependencies
- `acme` - Let's Encrypt ACME protocol (install with: `pip install acme`)
- `dnspython` - DNS operations for DNS challenges
- `boto3` - AWS Route53 integration
- `PyYAML` - YAML configuration support

### System Dependencies
- `openssl` - OpenSSL command-line tools
- Web server (Nginx/Apache) for generated configurations

## 🛡️ Security Considerations

### Certificate Security
- Private keys are stored with restricted permissions (0o600)
- Support for password-protected private keys
- Secure key generation with proper entropy
- Certificate chain validation against trusted CAs

### TLS Security
- Modern cipher suite preferences (Mozilla guidelines)
- Deprecated protocol detection and warnings
- HSTS header generation with preload support
- OCSP stapling for revocation checking

### Monitoring Security
- Encrypted connections for remote monitoring
- Rate limiting for alert notifications
- Secure credential storage for DNS providers
- Audit logging for all certificate operations

## 📊 Performance & Scalability

### Monitoring Performance
- Asynchronous certificate checking
- Configurable check intervals per endpoint
- Efficient certificate parsing and validation
- Minimal memory footprint for large-scale monitoring

### Let's Encrypt Integration
- Intelligent retry mechanisms
- Challenge timeout handling
- Concurrent domain validation
- Automatic cleanup of challenge files

## 🚨 Error Handling

### Comprehensive Exception Handling
- Custom exception classes for different error types
- Detailed error messages with actionable information
- Graceful degradation for non-critical failures
- Extensive logging for troubleshooting

### Validation Errors
- Certificate format validation
- Key-certificate matching verification
- Hostname validation against certificate
- Expiry date checking with warnings

## 📈 Monitoring & Metrics

### Certificate Health Metrics
- Days until expiry tracking
- Certificate chain depth analysis
- Cipher strength evaluation
- Protocol support assessment

### Performance Metrics
- SSL handshake timing
- Certificate validation duration
- Monitoring check frequencies
- Alert delivery statistics

## 🔄 Integration Points

### IA Influencer Agent Platform
- Integrated with deployment automation
- Supports multi-tenant certificate management
- Provides SSL metrics for analytics platform
- Interfaces with notification systems

### External Services
- Let's Encrypt ACME v2 API
- DNS provider APIs (Cloudflare, Route53)
- Monitoring services (PagerDuty, Slack)
- Email systems (SMTP)

---

## 📞 Support & Contact

**Technical Lead:** Fahed Mlaiel  
**Email:** mlaiel@live.de  
**Project:** IA Influencer Agent Platform

For technical support, feature requests, or licensing inquiries, please contact the development team.

---

**© 2025 Fahed Mlaiel. All Rights Reserved.**
