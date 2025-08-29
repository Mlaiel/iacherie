# 🛡️ Ainflue Platform Security Hardening Guide

## 📋 Executive Summary

This comprehensive security hardening guide provides detailed procedures for securing the Ainflue AI-powered content protection and monetization platform. These hardening measures ensure robust protection against cyber threats, maintain compliance with industry standards, and protect creator content and user data.

## 🎯 Security Hardening Objectives

### Primary Goals
1. **Minimize Attack Surface**: Reduce potential entry points for attackers
2. **Implement Defense in Depth**: Multi-layered security controls
3. **Ensure Compliance**: Meet regulatory and industry standards
4. **Protect Data**: Safeguard sensitive information at all levels
5. **Maintain Availability**: Ensure security measures don't impact performance

### Security Standards Compliance
- **OWASP Top 10**: Web application security risks
- **NIST Cybersecurity Framework**: Comprehensive security guidelines
- **CIS Controls**: Critical security controls implementation
- **ISO 27001**: Information security management standards
- **SOC 2**: Service organization control requirements

## 🏗️ Infrastructure Hardening

### Operating System Hardening

#### Ubuntu/Debian Server Hardening
```bash
#!/bin/bash
# ubuntu-hardening.sh - Ubuntu server security hardening

# Update system packages
apt update && apt upgrade -y
apt autoremove -y

# Install security packages
apt install -y fail2ban ufw aide lynis chkrootkit rkhunter

# Configure automatic security updates
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades
systemctl enable unattended-upgrades

# Disable unnecessary services
systemctl disable bluetooth
systemctl disable cups
systemctl disable avahi-daemon
systemctl stop bluetooth cups avahi-daemon

# Configure SSH hardening
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
echo "AllowUsers ainflue-admin" >> /etc/ssh/sshd_config
echo "Protocol 2" >> /etc/ssh/sshd_config
echo "MaxAuthTries 3" >> /etc/ssh/sshd_config
echo "ClientAliveInterval 300" >> /etc/ssh/sshd_config
echo "ClientAliveCountMax 2" >> /etc/ssh/sshd_config
systemctl restart sshd

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp  # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Set file permissions
chmod 700 /root
chmod 600 /etc/ssh/sshd_config
chmod 644 /etc/passwd
chmod 640 /etc/shadow
chmod 755 /etc
chmod 755 /bin /sbin /usr/bin /usr/sbin

# Configure kernel parameters
cat >> /etc/sysctl.conf << EOF
# IP Spoofing protection
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1

# Ignore ping requests
net.ipv4.icmp_echo_ignore_all = 1

# Ignore Directed pings
net.ipv4.icmp_echo_ignore_broadcasts = 1

# SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5
EOF

sysctl -p

# Configure file integrity monitoring
aide --init
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
echo "0 5 * * * /usr/bin/aide --check" >> /var/spool/cron/crontabs/root

echo "Ubuntu hardening completed successfully"
```

#### CentOS/RHEL Server Hardening
```bash
#!/bin/bash
# centos-hardening.sh - CentOS/RHEL server security hardening

# Update system
yum update -y
yum install -y epel-release

# Install security tools
yum install -y fail2ban firewalld aide lynis

# Configure firewall
systemctl enable firewalld
systemctl start firewalld
firewall-cmd --permanent --remove-service=ssh
firewall-cmd --permanent --add-port=2222/tcp
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# SELinux configuration
setsebool -P httpd_can_network_connect 1
setsebool -P httpd_execmem 1
semanage port -a -t ssh_port_t -p tcp 2222

# Disable unnecessary services
systemctl disable postfix
systemctl disable bluetooth
systemctl stop postfix bluetooth

echo "CentOS hardening completed successfully"
```

### Container Security Hardening

#### Docker Hardening Configuration
```yaml
# docker-daemon.json - Docker daemon security configuration
{
  "icc": false,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json",
  "apparmor-profile": "docker-default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "hard": 65536,
      "soft": 65536
    }
  },
  "cgroup-parent": "/system.slice/docker.service",
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
```

#### Secure Dockerfile Best Practices
```dockerfile
# Dockerfile.secure - Security-hardened container image
FROM node:18-alpine AS base

# Create non-root user
RUN addgroup -g 1001 -S nodejs \
    && adduser -S nextjs -u 1001

# Security updates
RUN apk update && apk upgrade && apk add --no-cache \
    curl \
    dumb-init \
    && rm -rf /var/cache/apk/*

# Set secure directory permissions
WORKDIR /app
RUN chown nextjs:nodejs /app

# Copy and install dependencies as non-root
USER nextjs
COPY --chown=nextjs:nodejs package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy application files
COPY --chown=nextjs:nodejs . .

# Remove unnecessary files
RUN rm -rf .git .gitignore README.md docs/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Security settings
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=1024"

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Non-root user execution
USER nextjs

# Secure port binding
EXPOSE 3000

CMD ["node", "server.js"]
```

#### Kubernetes Security Hardening
```yaml
# pod-security-policy.yaml - Kubernetes Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: ainflue-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  runAsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1000
        max: 65535
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
  seccompProfile:
    type: 'RuntimeDefault'

---
# network-policy.yaml - Kubernetes Network Policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ainflue-network-policy
spec:
  podSelector:
    matchLabels:
      app: ainflue
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to: []
    ports:
    - protocol: TCP
      port: 443
```

## 🔐 Application Security Hardening

### Web Application Security

#### NGINX Security Configuration
```nginx
# nginx-security.conf - NGINX security hardening
server {
    listen 80;
    server_name ainflue.com www.ainflue.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ainflue.com www.ainflue.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/ainflue.com.crt;
    ssl_certificate_key /etc/ssl/private/ainflue.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';" always;

    # Hide server information
    server_tokens off;

    # Request size limits
    client_max_body_size 10M;
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Timeout settings
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;

    # Disable unnecessary HTTP methods
    if ($request_method !~ ^(GET|HEAD|POST|PUT|DELETE)$ ) {
        return 405;
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Login endpoint rate limiting
    location /api/v1/auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://backend;
    }

    # Static file security
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options "nosniff";
    }

    # Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

#### Application Security Configuration
```python
# security_config.py - Application security configuration
import os
from datetime import timedelta

class SecurityConfig:
    # Authentication settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # Password policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_HISTORY_COUNT = 12
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = True
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379/0'
    RATELIMIT_DEFAULT = '100 per hour'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Input validation
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_ALLOWED_EXTENSIONS = {
        'image': ['png', 'jpg', 'jpeg', 'gif'],
        'audio': ['mp3', 'wav', 'flac'],
        'video': ['mp4', 'avi', 'mov']
    }
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Encryption settings
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    BCRYPT_LOG_ROUNDS = 14
    
    # Database security
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'sslcert': 'client-cert.pem',
            'sslkey': 'client-key.pem',
            'sslrootcert': 'ca-cert.pem'
        }
    }
```

#### Input Validation and Sanitization
```python
# validators.py - Input validation and sanitization
import re
import bleach
from marshmallow import Schema, fields, validate, ValidationError

class SecurityValidator:
    """Comprehensive input validation and sanitization"""
    
    @staticmethod
    def sanitize_html(content):
        """Sanitize HTML content to prevent XSS"""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        allowed_attributes = {}
        
        return bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def validate_sql_injection(query):
        """Check for SQL injection patterns"""
        dangerous_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(--|#|/\*|\*/)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\'\s*(OR|AND)\s+\'\w+\'\s*=\s*\'\w+)',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValidationError("Potential SQL injection detected")
        
        return True
    
    @staticmethod
    def validate_file_upload(file):
        """Validate uploaded files for security"""
        # Check file size
        max_size = 16 * 1024 * 1024  # 16MB
        if len(file.read()) > max_size:
            raise ValidationError("File too large")
        
        file.seek(0)  # Reset file pointer
        
        # Check file type by content, not just extension
        import magic
        file_type = magic.from_buffer(file.read(1024), mime=True)
        
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'audio/mpeg', 'audio/wav', 'audio/flac',
            'video/mp4', 'video/quicktime', 'video/x-msvideo'
        ]
        
        if file_type not in allowed_types:
            raise ValidationError("Invalid file type")
        
        file.seek(0)  # Reset file pointer
        
        return True

class UserRegistrationSchema(Schema):
    """User registration validation schema"""
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(required=True, validate=[
        validate.Length(min=12, max=128),
        validate.Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            error="Password must contain uppercase, lowercase, digit, and special character"
        )
    ])
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=30),
        validate.Regexp(r'^[a-zA-Z0-9_-]+$', error="Username contains invalid characters")
    ])
    
    def validate_password_strength(self, value):
        """Additional password strength validation"""
        common_passwords = ['password', '123456', 'qwerty', 'admin']
        if value.lower() in common_passwords:
            raise ValidationError("Password is too common")
        
        return value
```

## 🗄️ Database Security Hardening

### PostgreSQL Security Configuration

#### PostgreSQL Hardening
```sql
-- postgresql-security.sql - PostgreSQL security hardening

-- Create restricted users
CREATE ROLE ainflue_app_user WITH LOGIN PASSWORD 'strong_random_password';
CREATE ROLE ainflue_readonly WITH LOGIN PASSWORD 'strong_random_password';

-- Grant minimal privileges
GRANT CONNECT ON DATABASE ainflue TO ainflue_app_user;
GRANT USAGE ON SCHEMA public TO ainflue_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ainflue_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ainflue_app_user;

-- Read-only access for analytics
GRANT CONNECT ON DATABASE ainflue TO ainflue_readonly;
GRANT USAGE ON SCHEMA public TO ainflue_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ainflue_readonly;

-- Revoke public access
REVOKE ALL ON DATABASE ainflue FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Enable row level security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE content ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY user_isolation ON users
    FOR ALL TO ainflue_app_user
    USING (id = current_setting('app.current_user_id')::uuid);

CREATE POLICY content_isolation ON content
    FOR ALL TO ainflue_app_user
    USING (user_id = current_setting('app.current_user_id')::uuid);

-- Enable logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';
ALTER SYSTEM SET log_checkpoints = 'on';
ALTER SYSTEM SET log_lock_waits = 'on';
SELECT pg_reload_conf();
```

#### PostgreSQL Configuration (postgresql.conf)
```ini
# postgresql.conf - Security hardening configuration

# Connection settings
listen_addresses = 'localhost'
port = 5432
max_connections = 100
superuser_reserved_connections = 3

# SSL settings
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'ca.crt'
ssl_crl_file = 'root.crl'
ssl_min_protocol_version = 'TLSv1.2'
ssl_ciphers = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256'
ssl_prefer_server_ciphers = on

# Authentication
password_encryption = scram-sha-256
krb_server_keyfile = '/etc/postgresql/krb5.keytab'

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'ddl'
log_connections = on
log_disconnections = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Security
shared_preload_libraries = 'pg_stat_statements'
track_activities = on
track_counts = on
track_functions = 'all'
```

#### PostgreSQL Host-Based Authentication (pg_hba.conf)
```conf
# pg_hba.conf - Host-based authentication configuration

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     scram-sha-256

# IPv4 local connections
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# Application connections
hostssl ainflue         ainflue_app_user 10.0.0.0/16           scram-sha-256
hostssl ainflue         ainflue_readonly 10.0.0.0/16           scram-sha-256

# Deny all other connections
host    all             all             0.0.0.0/0               reject
host    all             all             ::/0                    reject
```

### MongoDB Security Configuration

#### MongoDB Hardening
```javascript
// mongodb-security.js - MongoDB security configuration

// Enable authentication
use admin
db.createUser({
  user: "mongoAdmin",
  pwd: "strong_random_password",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
})

// Create application user
use ainflue
db.createUser({
  user: "ainflue_app",
  pwd: "strong_app_password",
  roles: [
    { role: "readWrite", db: "ainflue" }
  ]
})

// Create read-only user
db.createUser({
  user: "ainflue_readonly",
  pwd: "strong_readonly_password",
  roles: [
    { role: "read", db: "ainflue" }
  ]
})
```

#### MongoDB Configuration (mongod.conf)
```yaml
# mongod.conf - MongoDB security configuration
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  component:
    accessControl:
      verbosity: 2

storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      journalCompressor: snappy
    collectionConfig:
      blockCompressor: snappy

net:
  port: 27017
  bindIp: 127.0.0.1
  ssl:
    mode: requireSSL
    PEMKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/ca.pem

security:
  authorization: enabled
  clusterAuthMode: x509
  javascriptEnabled: false

operationProfiling:
  slowOpThresholdMs: 100
  mode: slowOp

replication:
  replSetName: "rs0"
```

## 🔐 Encryption and Key Management

### Data Encryption Configuration

#### Application-Level Encryption
```python
# encryption.py - Application encryption utilities
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class EncryptionManager:
    """Centralized encryption management"""
    
    def __init__(self):
        self.encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        
        self.fernet = Fernet(self.encryption_key.encode())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like PII"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_file(self, file_path: str, output_path: str):
        """Encrypt file contents"""
        with open(file_path, 'rb') as infile:
            file_data = infile.read()
        
        encrypted_data = self.fernet.encrypt(file_data)
        
        with open(output_path, 'wb') as outfile:
            outfile.write(encrypted_data)
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def verify_password(self, password: str, hashed_password: str, salt: bytes) -> bool:
        """Verify password against hash"""
        key, _ = self.hash_password(password, salt)
        return key.decode() == hashed_password

# Database field encryption
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    
    # Encrypted fields
    phone = db.Column(EncryptedType(db.String, secret_key, AesEngine, 'pkcs5'))
    ssn = db.Column(EncryptedType(db.String, secret_key, AesEngine, 'pkcs5'))
    credit_card = db.Column(EncryptedType(db.String, secret_key, AesEngine, 'pkcs5'))
```

### SSL/TLS Certificate Management

#### Certificate Generation and Management
```bash
#!/bin/bash
# ssl-cert-management.sh - SSL certificate management

# Generate CA private key
openssl genrsa -out ca-key.pem 4096

# Generate CA certificate
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem -subj "/C=US/ST=CA/L=San Francisco/O=Ainflue/CN=Ainflue CA"

# Generate server private key
openssl genrsa -out server-key.pem 4096

# Generate server certificate signing request
openssl req -subj "/C=US/ST=CA/L=San Francisco/O=Ainflue/CN=ainflue.com" -sha256 -new -key server-key.pem -out server.csr

# Create extensions file for server certificate
cat > server-extfile.cnf <<EOF
subjectAltName = DNS:ainflue.com,DNS:www.ainflue.com,DNS:api.ainflue.com
extendedKeyUsage = serverAuth
EOF

# Generate server certificate
openssl x509 -req -days 365 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem -out server-cert.pem -extfile server-extfile.cnf -CAcreateserial

# Generate client private key
openssl genrsa -out client-key.pem 4096

# Generate client certificate signing request
openssl req -subj "/C=US/ST=CA/L=San Francisco/O=Ainflue/CN=client" -new -key client-key.pem -out client.csr

# Create extensions file for client certificate
echo extendedKeyUsage = clientAuth > client-extfile.cnf

# Generate client certificate
openssl x509 -req -days 365 -sha256 -in client.csr -CA ca.pem -CAkey ca-key.pem -out client-cert.pem -extfile client-extfile.cnf -CAcreateserial

# Set appropriate permissions
chmod 400 *-key.pem
chmod 444 *-cert.pem ca.pem

# Clean up
rm server.csr client.csr server-extfile.cnf client-extfile.cnf

echo "SSL certificates generated successfully"
```

## 🔍 Security Monitoring and Alerting

### Security Information and Event Management (SIEM)

#### ELK Stack Security Configuration
```yaml
# elasticsearch.yml - Elasticsearch security configuration
cluster.name: ainflue-security
node.name: security-node-1

network.host: 0.0.0.0
http.port: 9200

xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: elastic-certificates.p12
xpack.security.transport.ssl.truststore.path: elastic-certificates.p12

xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: elastic-certificates.p12

xpack.monitoring.collection.enabled: true
```

#### Logstash Security Pipeline
```ruby
# logstash-security.conf - Security event processing pipeline
input {
  beats {
    port => 5044
    ssl => true
    ssl_certificate_authorities => ["/etc/pki/ca.crt"]
    ssl_certificate => "/etc/pki/logstash.crt"
    ssl_key => "/etc/pki/logstash.key"
  }
}

filter {
  if [fields][type] == "security" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
    
    if [response] >= 400 {
      mutate {
        add_tag => ["error"]
        add_field => { "severity" => "warning" }
      }
    }
    
    if [response] >= 500 {
      mutate {
        add_field => { "severity" => "critical" }
      }
    }
    
    # Detect security patterns
    if [request] =~ /(?i)(union|select|insert|delete|drop|script|alert|eval)/ {
      mutate {
        add_tag => ["potential_injection"]
        add_field => { "security_alert" => "SQL_Injection_Attempt" }
      }
    }
    
    if [clientip] {
      geoip {
        source => "clientip"
        target => "geoip"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["https://elasticsearch:9200"]
    ssl => true
    cacert => "/etc/pki/ca.crt"
    user => "logstash_writer"
    password => "${LOGSTASH_PASSWORD}"
    index => "security-logs-%{+YYYY.MM.dd}"
  }
}
```

#### Security Alerting Rules
```yaml
# security-alerts.yml - Watcher alerting configuration
trigger:
  schedule:
    interval: 1m

input:
  search:
    request:
      search_type: query_then_fetch
      indices: ["security-logs-*"]
      body:
        query:
          bool:
            must:
              - range:
                  "@timestamp":
                    gte: "now-5m"
              - terms:
                  tags: ["potential_injection", "brute_force", "anomaly"]

condition:
  compare:
    ctx.payload.hits.total: 
      gt: 0

actions:
  send_email:
    email:
      to: ["security@ainflue.com"]
      subject: "Security Alert: Potential Attack Detected"
      body: |
        Security alert triggered at {{ctx.execution_time}}.
        
        Number of security events: {{ctx.payload.hits.total}}
        
        Please investigate immediately.

  send_slack:
    webhook:
      scheme: https
      host: hooks.slack.com
      port: 443
      method: post
      path: /services/YOUR/SLACK/WEBHOOK
      body: |
        {
          "text": "🚨 Security Alert: {{ctx.payload.hits.total}} potential security events detected",
          "channel": "#security-alerts",
          "username": "Security Bot"
        }
```

## 📋 Security Compliance and Auditing

### Compliance Framework Implementation

#### GDPR Compliance Configuration
```python
# gdpr_compliance.py - GDPR compliance implementation
from datetime import datetime, timedelta
from sqlalchemy import event
from flask import request, g

class GDPRCompliance:
    """GDPR compliance utilities"""
    
    @staticmethod
    def log_data_access(user_id, data_type, purpose):
        """Log data access for audit trail"""
        audit_log = DataAccessLog(
            user_id=user_id,
            data_type=data_type,
            purpose=purpose,
            accessed_at=datetime.utcnow(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
    
    @staticmethod
    def anonymize_user_data(user_id):
        """Anonymize user data for GDPR compliance"""
        user = User.query.get(user_id)
        if user:
            user.email = f"anonymized_{user_id}@deleted.com"
            user.phone = None
            user.name = "Anonymized User"
            user.address = None
            user.is_anonymized = True
            user.anonymized_at = datetime.utcnow()
            db.session.commit()
    
    @staticmethod
    def export_user_data(user_id):
        """Export all user data for GDPR data portability"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        user_data = {
            'personal_info': {
                'email': user.email,
                'name': user.name,
                'phone': user.phone,
                'created_at': user.created_at.isoformat()
            },
            'content': [
                {
                    'id': content.id,
                    'title': content.title,
                    'created_at': content.created_at.isoformat(),
                    'file_path': content.file_path
                }
                for content in user.content
            ],
            'analytics': user.analytics_data
        }
        
        return user_data

# Audit logging decorator
def audit_log(data_type, purpose):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if hasattr(g, 'current_user_id'):
                GDPRCompliance.log_data_access(
                    g.current_user_id, 
                    data_type, 
                    purpose
                )
            return result
        return wrapper
    return decorator

# Database model with audit trail
class AuditMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class DataAccessLog(db.Model, AuditMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_type = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    accessed_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
```

## 🔧 Security Automation and Orchestration

### Automated Security Response

#### Security Orchestration Platform (SOAR)
```python
# security_automation.py - Automated security response
import requests
import json
from datetime import datetime
from celery import Celery

class SecurityOrchestrator:
    """Automated security response orchestration"""
    
    def __init__(self):
        self.celery = Celery('security_tasks')
        self.threat_intel_api = "https://api.threatintel.com"
        self.siem_api = "https://siem.ainflue.com/api"
    
    def analyze_security_event(self, event):
        """Analyze security event and determine response"""
        severity = self.calculate_severity(event)
        
        if severity >= 8:  # Critical
            self.trigger_incident_response(event)
        elif severity >= 6:  # High
            self.automated_containment(event)
        elif severity >= 4:  # Medium
            self.enhanced_monitoring(event)
        else:  # Low
            self.log_for_analysis(event)
    
    def calculate_severity(self, event):
        """Calculate event severity score"""
        base_score = 0
        
        # IP reputation check
        ip_reputation = self.check_ip_reputation(event.get('source_ip'))
        base_score += ip_reputation * 2
        
        # Attack pattern matching
        attack_patterns = self.detect_attack_patterns(event.get('payload'))
        base_score += len(attack_patterns) * 3
        
        # Asset criticality
        asset_criticality = self.get_asset_criticality(event.get('target'))
        base_score += asset_criticality * 2
        
        # User behavior analysis
        user_anomaly = self.analyze_user_behavior(event.get('user_id'))
        base_score += user_anomaly * 1.5
        
        return min(base_score, 10)  # Cap at 10
    
    @celery.task
    def automated_containment(self, event):
        """Automated threat containment"""
        source_ip = event.get('source_ip')
        
        # Block IP at firewall
        self.block_ip_address(source_ip)
        
        # Disable user account if applicable
        user_id = event.get('user_id')
        if user_id and self.is_account_compromised(user_id):
            self.disable_user_account(user_id)
        
        # Isolate affected systems
        affected_systems = event.get('affected_systems', [])
        for system in affected_systems:
            self.isolate_system(system)
        
        # Notify security team
        self.send_security_alert(event, "automated_containment")
    
    def block_ip_address(self, ip_address):
        """Block IP address at network level"""
        # AWS Security Group update
        import boto3
        ec2 = boto3.client('ec2')
        
        ec2.authorize_security_group_ingress(
            GroupId='sg-security-group-id',
            IpPermissions=[
                {
                    'IpProtocol': '-1',
                    'IpRanges': [{'CidrIp': f'{ip_address}/32', 'Description': 'Blocked by security automation'}]
                }
            ]
        )
        
        # Update WAF rules
        import boto3
        waf = boto3.client('wafv2')
        
        waf.update_ip_set(
            Scope='CLOUDFRONT',
            Id='blocked-ips',
            Addresses=[ip_address]
        )
```

---

**Document Information**
- **Version**: 1.0.0
- **Last Updated**: {{current_date}}
- **Next Review**: {{next_review_date}}
- **Owner**: Chief Security Officer
- **Approved By**: Executive Leadership Team

---

**Implementation Checklist**
- [ ] Operating system hardening applied
- [ ] Container security configured
- [ ] Application security implemented
- [ ] Database security hardened
- [ ] Encryption and key management deployed
- [ ] Security monitoring activated
- [ ] Compliance measures implemented
- [ ] Automation and orchestration configured
- [ ] Security testing completed
- [ ] Documentation updated

---

> **Classification**: Confidential - Security Implementation Guide  
> **Access Level**: Security Team and Authorized Personnel Only  
> **Review Frequency**: Quarterly