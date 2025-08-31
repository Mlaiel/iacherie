"""🔐 Security Services Docker Configuration - IA-Influencer-Agent Platform
=========================================================================
Expert: Security Engineer + Compliance Specialist + DevOps Engineer
Creator: Fahed Mlaiel <mlaiel@live.de>
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Docker configuration for enterprise security services
supporting multi-layer security, threat detection, and compliance monitoring.
"""
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SecurityServicesDockerConfig:
    """Enterprise Security Services Docker Configuration"""
    
    # Image Configuration
    image_name: str = "ia-influencer/security-services"
    image_tag: str = "2.0.0"
    registry_url: str = "registry.ia-influencer.com"
    
    # Container Configuration
    container_name: str = "ia-influencer-security"
    restart_policy: str = "unless-stopped"
    network_mode: str = "ia-influencer-network"
    
    # Resource Limits
    cpu_limit: str = "2000m"
    memory_limit: str = "4Gi"
    cpu_reservation: str = "1000m"
    memory_reservation: str = "2Gi"
    
    # Security Configuration
    enable_waf: bool = True
    enable_ids: bool = True
    enable_vulnerability_scanner: bool = True
    enable_compliance_monitor: bool = True
    enable_audit_logger: bool = True
    
    # Ports Configuration
    main_port: int = 8080
    waf_port: int = 8081
    ids_port: int = 8082
    scanner_port: int = 8083
    
    # Environment Variables
    environment: Dict[str, str] = field(default_factory=lambda: {
        "SECURITY_MODE": "production",
        "LOG_LEVEL": "INFO",
        "COMPLIANCE_STANDARDS": "GDPR,CCPA,SOC2,ISO27001",
        "THREAT_DETECTION_ENABLED": "true",
        "AUDIT_RETENTION_DAYS": "365",
        "SCAN_INTERVAL_HOURS": "24"
    })
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for security services"""
        return f"""# Multi-stage build for Security Services
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    gcc \\
    g++ \\
    make \\
    libssl-dev \\
    libffi-dev \\
    python3-dev \\
    pkg-config \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements/security-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \\
    pip install --no-cache-dir -r security-requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    net-tools \\
    iptables \\
    fail2ban \\
    clamav \\
    clamav-daemon \\
    nmap \\
    tcpdump \\
    wireshark-common \\
    openssl \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create security user
RUN groupadd -r security && useradd -r -g security security

# Create directories
RUN mkdir -p /app/security/waf \\
             /app/security/ids \\
             /app/security/scanner \\
             /app/security/compliance \\
             /app/security/audit \\
             /app/logs/security \\
             /app/config/security \\
             /var/log/security \\
             /tmp/security/quarantine

# Copy application code
COPY backend/security/ /app/security/
COPY backend/deployment/docker/config/security/ /app/config/security/
COPY backend/deployment/docker/scripts/security/ /app/scripts/

# Set permissions
RUN chown -R security:security /app/ /var/log/security /tmp/security
RUN chmod +x /app/scripts/*.sh

# Copy ClamAV configuration
COPY config/security/clamav/ /etc/clamav/

# Update ClamAV database
RUN freshclam --quiet

# Configure fail2ban
COPY config/security/fail2ban/ /etc/fail2ban/

# Security configurations
COPY config/security/iptables.rules /etc/iptables.rules
COPY config/security/modsecurity.conf /etc/modsecurity/
COPY config/security/suricata.yaml /etc/suricata/

# Install security tools
COPY scripts/security/install-security-tools.sh /tmp/
RUN chmod +x /tmp/install-security-tools.sh && /tmp/install-security-tools.sh

# Expose ports
EXPOSE {self.main_port} {self.waf_port} {self.ids_port} {self.scanner_port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:{self.main_port}/health || exit 1

# Switch to security user
USER security

# Working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \\
    PYTHONUNBUFFERED=1 \\
    SECURITY_CONFIG_PATH=/app/config/security \\
    LOG_PATH=/app/logs/security

# Entry point
COPY scripts/security/entrypoint.sh /app/scripts/
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["python", "-m", "security.main"]
"""
    def generate_docker_compose_service(self) -> Dict[str, Any]:
        """Generate Docker Compose service configuration"""
        return {
            "image": f"{self.registry_url}/{self.image_name}:{self.image_tag}",
            "container_name": self.container_name,
            "restart": self.restart_policy,
            "ports": [
                f"{self.main_port}:{self.main_port}",
                f"{self.waf_port}:{self.waf_port}",
                f"{self.ids_port}:{self.ids_port}",
                f"{self.scanner_port}:{self.scanner_port}"
            ],
            "environment": self.environment,
            "volumes": [
                "./config/security:/app/config/security:ro",
                "./logs/security:/app/logs/security",
                "security_quarantine:/tmp/security/quarantine",
                "security_rules:/app/security/rules",
                "audit_logs:/var/log/security",
                "/var/run/docker.sock:/var/run/docker.sock:ro"
            ],
            "networks": [self.network_mode],
            "depends_on": [
                "postgres-master",
                "redis",
                "elasticsearch"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": self.cpu_limit,
                        "memory": self.memory_limit
                    },
                    "reservations": {
                        "cpus": self.cpu_reservation,
                        "memory": self.memory_reservation
                    }
                }
            },
            "cap_add": [
                "NET_ADMIN",
                "NET_RAW",
                "SYS_ADMIN"
            ],
            "privileged": True,
            "security_opt": [
                "seccomp:unconfined"
            ],
            "healthcheck": {
                "test": f"curl -f http://localhost:{self.main_port}/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            }
        }
    
    def generate_waf_service(self) -> Dict[str, Any]:
        """Generate WAF (Web Application Firewall) service"""
        return {
            "image": "owasp/modsecurity:apache",
            "container_name": f"{self.container_name}-waf",
            "restart": self.restart_policy,
            "ports": ["80:80", "443:443"],
            "environment": {
                "MODSEC_RULE_ENGINE": "On",
                "MODSEC_REQ_BODY_ACCESS": "On",
                "MODSEC_REQ_BODY_LIMIT": "13107200",
                "MODSEC_RESP_BODY_ACCESS": "On",
                "MODSEC_AUDIT_ENGINE": "RelevantOnly",
                "MODSEC_AUDIT_LOG": "/var/log/modsec_audit.log",
                "BACKEND": "http://api-gateway:8000"
            },
            "volumes": [
                "./config/security/modsecurity:/etc/modsecurity.d:ro",
                "./config/security/apache:/etc/apache2/sites-available:ro",
                "./logs/security/waf:/var/log:rw"
            ],
            "networks": [self.network_mode],
            "depends_on": ["api-gateway"],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "1000m",
                        "memory": "2Gi"
                    }
                }
            }
        }
    
    def generate_ids_service(self) -> Dict[str, Any]:
        """Generate IDS (Intrusion Detection System) service"""
        return {
            "image": "jasonish/suricata:latest",
            "container_name": f"{self.container_name}-ids",
            "restart": self.restart_policy,
            "network_mode": "host",
            "cap_add": [
                "NET_ADMIN",
                "SYS_NICE"
            ],
            "environment": {
                "SURICATA_OPTIONS": "-i eth0"
            },
            "volumes": [
                "./config/security/suricata:/etc/suricata:ro",
                "./logs/security/ids:/var/log/suricata:rw",
                "ids_rules:/var/lib/suricata/rules"
            ],
            "command": [
                "/usr/bin/suricata",
                "-c", "/etc/suricata/suricata.yaml",
                "-i", "eth0",
                "-v"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "2000m",
                        "memory": "4Gi"
                    }
                }
            }
        }
    
    def generate_vulnerability_scanner_service(self) -> Dict[str, Any]:
        """Generate vulnerability scanner service"""
        return {
            "image": "owasp/zap2docker-stable",
            "container_name": f"{self.container_name}-scanner",
            "restart": self.restart_policy,
            "ports": ["8090:8090"],
            "environment": {
                "ZAP_PORT": "8090"
            },
            "volumes": [
                "./config/security/zap:/zap/wrk:rw",
                "./logs/security/scanner:/zap/logs:rw"
            ],
            "networks": [self.network_mode],
            "command": [
                "zap.sh",
                "-daemon",
                "-host", "0.0.0.0",
                "-port", "8090",
                "-config", "api.addrs.addr.name=.*",
                "-config", "api.addrs.addr.regex=true"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "2000m",
                        "memory": "4Gi"
                    }
                }
            }
        }
    
    def generate_compliance_monitor_service(self) -> Dict[str, Any]:
        """Generate compliance monitoring service"""
        return {
            "image": f"{self.registry_url}/compliance-monitor:latest",
            "container_name": f"{self.container_name}-compliance",
            "restart": self.restart_policy,
            "ports": ["8094:8094"],
            "environment": {
                "COMPLIANCE_STANDARDS": "GDPR,CCPA,SOC2,ISO27001",
                "SCAN_INTERVAL": "3600",
                "REPORT_RETENTION_DAYS": "2555",
                "ALERT_WEBHOOK_URL": "${COMPLIANCE_WEBHOOK_URL}"
            },
            "volumes": [
                "./config/security/compliance:/app/config:ro",
                "./logs/security/compliance:/app/logs:rw",
                "compliance_reports:/app/reports"
            ],
            "networks": [self.network_mode],
            "depends_on": [
                "postgres-master",
                "elasticsearch"
            ],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "1000m",
                        "memory": "2Gi"
                    }
                }
            }
        }
    
    def generate_security_requirements(self) -> str:
        """Generate security requirements.txt"""
        return """# Security Services Requirements
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Core security framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Cryptography and security
cryptography==41.0.8
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6

# Web security
python-decouple==3.8
httpx==0.25.2
requests==2.31.0
aiofiles==23.2.1

# Security monitoring
psutil==5.9.6
python-dateutil==2.8.2
schedule==1.2.0

# Vulnerability scanning
python-nmap==0.7.1
scapy==2.5.0
yara-python==4.3.1

# WAF and IDS integration
mod-wsgi==4.9.4
apache-libcloud==3.8.0

# Compliance and audit
audit-python==1.2.0
gdpr-tools==1.1.0
sox-compliance==2.0.1

# Database security
sqlalchemy-utils==0.41.1
alembic==1.13.1
psycopg2-binary==2.9.9

# Logging and monitoring
structlog==23.2.0
python-json-logger==2.0.7
prometheus-client==0.19.0

# Async and messaging
celery==5.3.4
redis==5.0.1
kombu==5.3.4

# File and content security
python-magic==0.4.27
clamd==1.0.2
hashlib-compat==1.0.1

# Network security
netaddr==0.9.0
ipaddress==1.0.23
dns==1.16.0

# Machine learning for threat detection
scikit-learn==1.3.2
numpy==1.24.4
pandas==2.1.4

# Configuration and utilities
pyyaml==6.0.1
click==8.1.7
rich==13.7.0
typer==0.9.0

# Testing (for security testing)
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
"""
    def generate_security_config_files(self) -> Dict[str, str]:
        """Generate security configuration files"""
        configs = {}
        
        # ModSecurity configuration
        configs["modsecurity.conf"] = """# ModSecurity Configuration for IA-Influencer
# Creator: Fahed Mlaiel <mlaiel@live.de>

# Basic configuration
SecRuleEngine On
SecRequestBodyAccess On
SecRequestBodyLimit 13107200
SecRequestBodyNoFilesLimit 131072
SecRequestBodyInMemoryLimit 131072
SecRequestBodyLimitAction Reject
SecPcreMatchLimit 1000
SecPcreMatchLimitRecursion 1000

# Response body handling
SecResponseBodyAccess On
SecResponseBodyMimeType text/plain text/html text/xml
SecResponseBodyLimit 524288
SecResponseBodyLimitAction ProcessPartial

# Temporary directory
SecTmpDir /tmp/modsec/
SecDataDir /tmp/modsec/

# Audit logging
SecAuditEngine RelevantOnly
SecAuditLogRelevantStatus "^(?:5|4(?!04))"
SecAuditLogParts ABDEFHIJZ
SecAuditLogType Serial
SecAuditLog /var/log/modsec_audit.log

# Debug logging
SecDebugLog /var/log/modsec_debug.log
SecDebugLogLevel 3

# OWASP Core Rule Set
Include /etc/modsecurity.d/owasp-crs/*.conf
Include /etc/modsecurity.d/custom-rules/*.conf

# Custom rules for IA-Influencer
SecRule ARGS "@detectSQLi" \\
    "id:1001,\\
    phase:2,\\
    block,\\
    msg:'SQL Injection Attack Detected',\\
    logdata:'Matched Data: %{MATCHED_VAR} found within %{MATCHED_VAR_NAME}',\\
    tag:'application-multi',\\
    tag:'language-multi',\\
    tag:'platform-multi',\\
    tag:'attack-sqli'"

SecRule ARGS "@detectXSS" \\
    "id:1002,\\
    phase:2,\\
    block,\\
    msg:'XSS Attack Detected',\\
    logdata:'Matched Data: %{MATCHED_VAR} found within %{MATCHED_VAR_NAME}',\\
    tag:'application-multi',\\
    tag:'language-multi',\\
    tag:'platform-multi',\\
    tag:'attack-xss'"
"""
        # Suricata configuration
        configs["suricata.yaml"] = """# Suricata IDS Configuration for IA-Influencer
# Creator: Fahed Mlaiel <mlaiel@live.de>

vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "$HOME_NET"
    SMTP_SERVERS: "$HOME_NET"
    SQL_SERVERS: "$HOME_NET"
    DNS_SERVERS: "$HOME_NET"
    TELNET_SERVERS: "$HOME_NET"
    AIM_SERVERS: "$EXTERNAL_NET"
    DC_SERVERS: "$HOME_NET"
    DNP3_SERVER: "$HOME_NET"
    DNP3_CLIENT: "$HOME_NET"
    MODBUS_CLIENT: "$HOME_NET"
    MODBUS_SERVER: "$HOME_NET"
    ENIP_CLIENT: "$HOME_NET"
    ENIP_SERVER: "$HOME_NET"

  port-groups:
    HTTP_PORTS: "80,81,311,383,591,593,901,1220,1414,1741,1830,2301,2381,2809,3037,3128,3702,4343,4848,5250,6988,7000,7001,7144,7145,7510,7777,7779,8000,8008,8014,8028,8080,8085,8088,8090,8118,8123,8180,8181,8243,8280,8300,8800,8888,8899,9000,9060,9080,9090,9091,9443,9999,11371,34443,34444,41080,50002,55555"
    SHELLCODE_PORTS: "!80"
    ORACLE_PORTS: 1521
    SSH_PORTS: 22
    DNP3_PORTS: 20000
    MODBUS_PORTS: 502
    FILE_DATA_PORTS: "[$HTTP_PORTS,110,143]"
    FTP_PORTS: 21
    GENEVE_PORTS: 6081
    VXLAN_PORTS: 4789
    TEREDO_PORTS: 3544

default-log-dir: /var/log/suricata/

stats:
  enabled: yes
  interval: 8

outputs:
  - fast:
      enabled: yes
      filename: fast.log
      append: yes
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      community-id: true
      types:
        - alert
        - http
        - dns
        - tls
        - files
        - smtp
        - ssh
        - stats
        - flow

logging:
  default-log-level: notice
  outputs:
    - console:
        enabled: yes
    - file:
        enabled: yes
        level: info
        filename: /var/log/suricata/suricata.log

af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes

detect-engine:
  - profile: medium
  - custom-values:
      toclient-groups: 3
      toserver-groups: 25
  - sgh-mpm-context: auto
  - inspection-recursion-limit: 3000

threading:
  set-cpu-affinity: no
  cpu-affinity:
    - management-cpu-set:
        cpu: [ 0 ]
    - receive-cpu-set:
        cpu: [ 0 ]
    - worker-cpu-set:
        cpu: [ "all" ]
        mode: "exclusive"
        prio:
          low: [ 0 ]
          medium: [ "1-2" ]
          high: [ 3 ]
          default: "medium"

rule-files:
  - suricata.rules
  - /var/lib/suricata/rules/botcc.rules
  - /var/lib/suricata/rules/ciarmy.rules
  - /var/lib/suricata/rules/compromised.rules
  - /var/lib/suricata/rules/drop.rules
  - /var/lib/suricata/rules/dshield.rules
  - /var/lib/suricata/rules/emerging-activex.rules
  - /var/lib/suricata/rules/emerging-attack_response.rules
  - /var/lib/suricata/rules/emerging-chat.rules
  - /var/lib/suricata/rules/emerging-current_events.rules
  - /var/lib/suricata/rules/emerging-dns.rules
  - /var/lib/suricata/rules/emerging-dos.rules
  - /var/lib/suricata/rules/emerging-exploit.rules
  - /var/lib/suricata/rules/emerging-ftp.rules
  - /var/lib/suricata/rules/emerging-imap.rules
  - /var/lib/suricata/rules/emerging-malware.rules
  - /var/lib/suricata/rules/emerging-misc.rules
  - /var/lib/suricata/rules/emerging-mobile_malware.rules
  - /var/lib/suricata/rules/emerging-netbios.rules
  - /var/lib/suricata/rules/emerging-p2p.rules
  - /var/lib/suricata/rules/emerging-policy.rules
  - /var/lib/suricata/rules/emerging-pop3.rules
  - /var/lib/suricata/rules/emerging-rpc.rules
  - /var/lib/suricata/rules/emerging-scan.rules
  - /var/lib/suricata/rules/emerging-shellcode.rules
  - /var/lib/suricata/rules/emerging-smtp.rules
  - /var/lib/suricata/rules/emerging-snmp.rules
  - /var/lib/suricata/rules/emerging-sql.rules
  - /var/lib/suricata/rules/emerging-telnet.rules
  - /var/lib/suricata/rules/emerging-tftp.rules
  - /var/lib/suricata/rules/emerging-trojan.rules
  - /var/lib/suricata/rules/emerging-user_agents.rules
  - /var/lib/suricata/rules/emerging-voip.rules
  - /var/lib/suricata/rules/emerging-web_client.rules
  - /var/lib/suricata/rules/emerging-web_server.rules
  - /var/lib/suricata/rules/emerging-worm.rules
  - /var/lib/suricata/rules/tor.rules
  - /var/lib/suricata/rules/http-events.rules
  - /var/lib/suricata/rules/smtp-events.rules
  - /var/lib/suricata/rules/dns-events.rules
  - /var/lib/suricata/rules/tls-events.rules

classification-file: /etc/suricata/classification.config
reference-config-file: /etc/suricata/reference.config
"""
        # Fail2ban configuration
        configs["fail2ban_jail.conf"] = """# Fail2ban configuration for IA-Influencer
# Creator: Fahed Mlaiel <mlaiel@live.de>

[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = auto
usedns = warn
logencoding = auto
enabled = false
mode = normal
filter = %(__name__)s[mode=%(mode)s]

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
backend = %(sshd_backend)s

[apache-auth]
enabled = true
port = http,https
logpath = /var/log/apache*/*error.log

[apache-badbots]
enabled = true
port = http,https
logpath = /var/log/apache*/*access.log
bantime = 86400
maxretry = 1

[apache-noscript]
enabled = true
port = http,https
logpath = /var/log/apache*/*access.log
maxretry = 6

[apache-overflows]
enabled = true
port = http,https
logpath = /var/log/apache*/*error.log
maxretry = 2

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[ia-influencer-api]
enabled = true
port = 8000,8080
logpath = /app/logs/security/api-security.log
maxretry = 10
findtime = 300
bantime = 7200
"""
        return configs
    
    def generate_entrypoint_script(self) -> str:
        """Generate entrypoint script for security services"""
        return """#!/bin/bash
# Security Services Entrypoint Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "🔐 Starting IA-Influencer Security Services..."

# Initialize directories
mkdir -p /app/logs/security/{waf,ids,scanner,compliance,audit}
mkdir -p /tmp/security/quarantine
mkdir -p /var/log/security

# Set proper permissions
chown -R security:security /app/logs/security /tmp/security /var/log/security

# Start ClamAV daemon
echo "🦠 Starting ClamAV daemon..."
clamd &

# Update virus definitions
echo "🔄 Updating virus definitions..."
freshclam --quiet &

# Start fail2ban
echo "🚫 Starting Fail2ban..."
fail2ban-server -b

# Initialize iptables rules
if [ -f /etc/iptables.rules ]; then
    echo "🔥 Loading iptables rules..."
    iptables-restore < /etc/iptables.rules
fi

# Start Suricata IDS
echo "🔍 Starting Suricata IDS..."
suricata -c /etc/suricata/suricata.yaml -i eth0 -D

# Wait for dependencies
echo "⏳ Waiting for dependencies..."
wait-for-it postgres-master:5432 --timeout=60
wait-for-it redis:6379 --timeout=60
wait-for-it elasticsearch:9200 --timeout=60

# Start security monitoring
echo "🛡️ Starting security monitoring..."
python -m security.monitor &

# Start vulnerability scanner
echo "🔍 Starting vulnerability scanner..."
python -m security.scanner &

# Start compliance monitor
echo "📋 Starting compliance monitor..."
python -m security.compliance &

# Start audit logger
echo "📝 Starting audit logger..."
python -m security.audit &

# Start main security service
echo "🚀 Starting main security service..."
exec "$@"
"""
    
    def save_config_files(self, output_dir: str) -> List[str]:
        """Save all security configuration files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save Dockerfile
        dockerfile_path = output_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(self.generate_dockerfile())
        files_created.append(str(dockerfile_path))
        
        # Save requirements
        requirements_path = output_path / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(self.generate_security_requirements())
        files_created.append(str(requirements_path))
        
        # Save configuration files
        config_dir = output_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        for filename, content in self.generate_security_config_files().items():
            config_path = config_dir / filename
            with open(config_path, 'w') as f:
                f.write(content)
            files_created.append(str(config_path))
        
        # Save entrypoint script
        scripts_dir = output_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        entrypoint_path = scripts_dir / "entrypoint.sh"
        with open(entrypoint_path, 'w') as f:
            f.write(self.generate_entrypoint_script())
        entrypoint_path.chmod(0o755)
        files_created.append(str(entrypoint_path))
        
        logger.info(f"✅ Security services configuration saved: {len(files_created)} files")
        return files_created
