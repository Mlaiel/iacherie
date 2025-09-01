"""CloudFlare DDoS Protection and Security Configuration
=====================================================

Production-ready CloudFlare security configuration for AI Influencer Agent platform.
Implements advanced DDoS protection, rate limiting, and security rules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SecurityLevel(Enum):
    """CloudFlare security levels"""
    OFF = "off"
    ESSENTIALLY_OFF = "essentially_off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNDER_ATTACK = "under_attack"


class ChallengeType(Enum):
    """Challenge types for suspicious traffic"""
    JAVASCRIPT = "js_challenge"
    CAPTCHA = "captcha"
    MANAGED = "managed_challenge"
    BLOCK = "block"


@dataclass
class CloudFlareConfig:
    """CloudFlare security configuration"""
    
    # Zone settings
    zone_id: str = os.getenv("CLOUDFLARE_ZONE_ID", "")
    api_token: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    email: str = os.getenv("CLOUDFLARE_EMAIL", "")
    api_key: str = os.getenv("CLOUDFLARE_API_KEY", "")
    
    # Security settings
    security_level: SecurityLevel = SecurityLevel.HIGH
    challenge_passage: int = 1800  # 30 minutes
    browser_integrity_check: bool = True
    always_use_https: bool = True
    automatic_https_rewrites: bool = True
    
    # DDoS Protection
    ddos_protection_enabled: bool = True
    under_attack_mode: bool = False
    
    # Rate Limiting Rules
    rate_limiting_rules: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "id": "api_rate_limit",
            "description": "API endpoint rate limiting",
            "match": {
                "request": {
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "schemes": ["HTTP", "HTTPS"],
                    "url": "*.ainflue.com/api/*"
                }
            },
            "threshold": 1000,  # requests per period
            "period": 60,  # seconds
            "action": {
                "mode": "challenge",
                "timeout": 300
            }
        },
        {
            "id": "login_rate_limit",
            "description": "Login endpoint rate limiting",
            "match": {
                "request": {
                    "methods": ["POST"],
                    "schemes": ["HTTPS"],
                    "url": "*.ainflue.com/auth/login"
                }
            },
            "threshold": 5,  # login attempts
            "period": 300,  # 5 minutes
            "action": {
                "mode": "block",
                "timeout": 3600  # 1 hour block
            }
        },
        {
            "id": "upload_rate_limit",
            "description": "Content upload rate limiting",
            "match": {
                "request": {
                    "methods": ["POST", "PUT"],
                    "schemes": ["HTTPS"],
                    "url": "*.ainflue.com/api/content/upload*"
                }
            },
            "threshold": 100,
            "period": 3600,  # per hour
            "action": {
                "mode": "challenge",
                "timeout": 300
            }
        }
    ])
    
    # Firewall Rules
    firewall_rules: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "id": "block_malicious_ips",
            "description": "Block known malicious IP addresses",
            "expression": "(ip.geoip.country in {\"CN\" \"RU\" \"KP\"} and cf.threat_score gt 10) or cf.threat_score gt 50",
            "action": "block",
            "priority": 1
        },
        {
            "id": "block_tor_exit_nodes",
            "description": "Block Tor exit nodes",
            "expression": "cf.threat_score gt 30 and http.user_agent contains \"Tor\"",
            "action": "challenge",
            "priority": 2
        },
        {
            "id": "admin_access_protection",
            "description": "Protect admin endpoints",
            "expression": "http.request.uri.path contains \"/admin\" and not ip.src in {\"1.2.3.4\" \"5.6.7.8\"}",
            "action": "challenge",
            "priority": 3
        },
        {
            "id": "api_abuse_protection",
            "description": "Protect against API abuse",
            "expression": "http.request.uri.path contains \"/api/\" and (http.user_agent eq \"\" or http.user_agent contains \"bot\" or http.user_agent contains \"crawler\")",
            "action": "challenge",
            "priority": 4
        },
        {
            "id": "sql_injection_protection",
            "description": "Block SQL injection attempts",
            "expression": "http.request.uri contains \"union\" or http.request.uri contains \"select\" or http.request.uri contains \"drop\" or http.request.uri contains \"insert\"",
            "action": "block",
            "priority": 5
        }
    ])
    
    # Page Rules
    page_rules: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": "*.ainflue.com/api/*"
                    }
                }
            ],
            "actions": [
                {
                    "id": "security_level",
                    "value": "high"
                },
                {
                    "id": "cache_level",
                    "value": "bypass"
                }
            ],
            "priority": 1,
            "status": "active"
        },
        {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": "*.ainflue.com/admin/*"
                    }
                }
            ],
            "actions": [
                {
                    "id": "security_level",
                    "value": "under_attack"
                },
                {
                    "id": "always_use_https",
                    "value": "on"
                }
            ],
            "priority": 2,
            "status": "active"
        }
    ])
    
    # Bot Management
    bot_management: Dict[str, Any] = field(default_factory=lambda: {
        "enable_js": True,
        "enable_ml": True,
        "fight_mode": True,
        "using_latest_model": True,
        "auto_update_model": True,
        "suppress_session_score": False,
        "optimize_wordpress": False
    })
    
    # Custom SSL settings
    ssl_settings: Dict[str, Any] = field(default_factory=lambda: {
        "value": "flexible",  # off, flexible, full, strict
        "min_tls_version": "1.2",
        "ciphers": [],
        "http2": "on",
        "http3": "on",
        "zero_rtt": "off",
        "tls_1_3": "on",
        "automatic_https_rewrites": "on",
        "certificate_transparency_monitoring": "on"
    })


class CloudFlareManager:
    """CloudFlare API management for security configuration"""
    
    def __init__(self, config: CloudFlareConfig):
        self.config = config
        
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for CloudFlare resources"""
        terraform_config = f'''
# CloudFlare Provider Configuration
terraform {{
  required_providers {{
    cloudflare = {{
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }}
  }}
}}

provider "cloudflare" {{
  api_token = var.cloudflare_api_token
}}

variable "cloudflare_api_token" {{
  description = "CloudFlare API Token"
  type        = string
  sensitive   = true
}}

variable "zone_id" {{
  description = "CloudFlare Zone ID"
  type        = string
  default     = "{self.config.zone_id}"
}}

# Zone Settings
resource "cloudflare_zone_settings_override" "security_settings" {{
  zone_id = var.zone_id
  
  settings {{
    security_level                = "{self.config.security_level.value}"
    challenge_ttl                 = {self.config.challenge_passage}
    browser_integrity_check       = {str(self.config.browser_integrity_check).lower()}
    always_use_https             = "{str(self.config.always_use_https).lower()}"
    automatic_https_rewrites     = "{str(self.config.automatic_https_rewrites).lower()}"
    ssl                          = "{self.config.ssl_settings['value']}"
    min_tls_version              = "{self.config.ssl_settings['min_tls_version']}"
    tls_1_3                      = "{self.config.ssl_settings['tls_1_3']}"
    http2                        = "{self.config.ssl_settings['http2']}"
    http3                        = "{self.config.ssl_settings['http3']}"
    zero_rtt                     = "{self.config.ssl_settings['zero_rtt']}"
  }}
}}

# Rate Limiting Rules
'''
        
        for i, rule in enumerate(self.config.rate_limiting_rules):
            terraform_config += f'''
resource "cloudflare_rate_limit" "rate_limit_{i}" {{
  zone_id   = var.zone_id
  threshold = {rule['threshold']}
  period    = {rule['period']}
  
  match {{
    request {{
      url_pattern = "{rule['match']['request']['url']}"
      schemes     = {json.dumps(rule['match']['request']['schemes'])}
      methods     = {json.dumps(rule['match']['request']['methods'])}
    }}
  }}
  
  action {{
    mode    = "{rule['action']['mode']}"
    timeout = {rule['action']['timeout']}
  }}
  
  description = "{rule['description']}"
}}
'''
        
        # Firewall Rules
        for i, rule in enumerate(self.config.firewall_rules):
            terraform_config += f'''
resource "cloudflare_filter" "filter_{i}" {{
  zone_id     = var.zone_id
  description = "{rule['description']}"
  expression  = "{rule['expression']}"
}}

resource "cloudflare_firewall_rule" "firewall_rule_{i}" {{
  zone_id     = var.zone_id
  description = "{rule['description']}"
  filter_id   = cloudflare_filter.filter_{i}.id
  action      = "{rule['action']}"
  priority    = {rule['priority']}
}}
'''
        
        # Page Rules
        for i, rule in enumerate(self.config.page_rules):
            terraform_config += f'''
resource "cloudflare_page_rule" "page_rule_{i}" {{
  zone_id  = var.zone_id
  target   = "{rule['targets'][0]['constraint']['value']}"
  priority = {rule['priority']}
  status   = "{rule['status']}"
  
  actions {{
'''
            for action in rule['actions']:
                terraform_config += f'    {action["id"]} = "{action["value"]}"\n'
            
            terraform_config += '  }\n}\n'
        
        return terraform_config
    
    def generate_ansible_playbook(self) -> str:
        """Generate Ansible playbook for CloudFlare configuration"""
        playbook = f'''---
- name: Configure CloudFlare Security Settings
  hosts: localhost
  gather_facts: false
  vars:
    cloudflare_api_token: "{{{{ cloudflare_api_token }}}}"
    zone_id: "{self.config.zone_id}"
  
  tasks:
    - name: Configure zone security settings
      uri:
        url: "https://api.cloudflare.com/client/v4/zones/{{{{ zone_id }}}}/settings/security_level"
        method: PATCH
        headers:
          Authorization: "Bearer {{{{ cloudflare_api_token }}}}"
          Content-Type: "application/json"
        body_format: json
        body:
          value: "{self.config.security_level.value}"
        status_code: 200
      register: security_level_result
    
    - name: Configure browser integrity check
      uri:
        url: "https://api.cloudflare.com/client/v4/zones/{{{{ zone_id }}}}/settings/browser_check"
        method: PATCH
        headers:
          Authorization: "Bearer {{{{ cloudflare_api_token }}}}"
          Content-Type: "application/json"
        body_format: json
        body:
          value: "{str(self.config.browser_integrity_check).lower()}"
        status_code: 200
    
    - name: Configure challenge passage
      uri:
        url: "https://api.cloudflare.com/client/v4/zones/{{{{ zone_id }}}}/settings/challenge_ttl"
        method: PATCH
        headers:
          Authorization: "Bearer {{{{ cloudflare_api_token }}}}"
          Content-Type: "application/json"
        body_format: json
        body:
          value: {self.config.challenge_passage}
        status_code: 200
'''
        
        return playbook
    
    def generate_docker_compose_override(self) -> str:
        """Generate Docker Compose override for CloudFlare tunnel"""
        return '''version: '3.8'

services:
  cloudflare-tunnel:
    image: cloudflare/cloudflared:latest
    container_name: ainflue-cloudflare-tunnel
    restart: unless-stopped
    command: tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
    networks:
      - ainflue-security
    depends_on:
      - api-gateway
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.1'
          memory: 64M

networks:
  ainflue-security:
    external: true
'''


def create_cloudflare_config() -> CloudFlareConfig:
    """Create default CloudFlare configuration"""
    return CloudFlareConfig()


def export_config_to_file(config: CloudFlareConfig, output_dir: str = "./cloudflare_configs"):
    """Export CloudFlare configuration to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    manager = CloudFlareManager(config)
    
    # Generate Terraform configuration
    with open(f"{output_dir}/main.tf", "w") as f:
        f.write(manager.generate_terraform_config())
    
    # Generate Ansible playbook
    with open(f"{output_dir}/cloudflare-security.yml", "w") as f:
        f.write(manager.generate_ansible_playbook())
    
    # Generate Docker Compose override
    with open(f"{output_dir}/docker-compose.cloudflare.yml", "w") as f:
        f.write(manager.generate_docker_compose_override())
    
    # Generate environment variables template
    with open(f"{output_dir}/.env.cloudflare.example", "w") as f:
        f.write(f'''# CloudFlare Configuration
CLOUDFLARE_ZONE_ID={config.zone_id}
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_EMAIL=your_email@example.com
CLOUDFLARE_API_KEY=your_global_api_key_here
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here

# Security Settings
CLOUDFLARE_SECURITY_LEVEL={config.security_level.value}
CLOUDFLARE_UNDER_ATTACK_MODE={str(config.under_attack_mode).lower()}
CLOUDFLARE_CHALLENGE_PASSAGE={config.challenge_passage}
''')


if __name__ == "__main__":
    # Create and export configuration
    config = create_cloudflare_config()
    export_config_to_file(config)
    print("CloudFlare security configuration exported successfully!")