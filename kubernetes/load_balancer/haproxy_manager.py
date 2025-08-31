"""HAProxy Load Balancer Manager

Enterprise-grade HAProxy configuration and management for the IA Influencer
Agent platform, providing high-performance Layer 4/7 load balancing,
health checking, and advanced traffic management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""
import os
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


@dataclass
class HAProxyServer:
    """HAProxy server configuration"""    name: str
    address: str
    port: int
    weight: int = 1
    maxconn: int = 1000
    check: bool = True
    check_interval: str = "5s"
    rise: int = 2
    fall: int = 3
    backup: bool = False
    disabled: bool = False


@dataclass
class HAProxyBackend:
    """HAProxy backend configuration"""    name: str
    balance_algorithm: str = "roundrobin"
    mode: str = "http"
    servers: List[HAProxyServer] = None
    health_check: Optional[str] = None
    timeout_connect: str = "5s"
    timeout_server: str = "30s"
    cookie_persistence: bool = False
    ssl_check: bool = False


@dataclass
class HAProxyFrontend:
    """HAProxy frontend configuration"""    name: str
    bind_address: str
    bind_port: int
    mode: str = "http"
    default_backend: str = None
    ssl_certificate: Optional[str] = None
    redirect_scheme: Optional[str] = None
    acl_rules: List[Dict[str, str]] = None
    use_backend_rules: List[Dict[str, str]] = None


class HAProxyConfigGenerator:
    """Generate HAProxy configurations"""    
    def __init__(self):
        self.global_config = {
            'daemon': True,
            'maxconn': 4096,
            'log': 'stdout local0',
            'chroot': '/var/lib/haproxy',
            'stats_socket': '/run/haproxy/admin.sock',
            'stats_timeout': '30s',
            'user': 'haproxy',
            'group': 'haproxy',
            'ssl_default_bind_ciphers': 'ECDHE+RSA+AES256:ECDHE+RSA+AES128:!aNULL:!MD5:!DSS',
            'ssl_default_bind_options': 'ssl-min-ver TLSv1.2'
        }
        
        self.defaults_config = {
            'mode': 'http',
            'timeout_connect': '5s',
            'timeout_client': '30s',
            'timeout_server': '30s',
            'timeout_http_request': '10s',
            'timeout_queue': '1m',
            'timeout_tunnel': '1h',
            'retries': 3,
            'option_httplog': True,
            'option_dontlognull': True,
            'option_http_server_close': True,
            'option_forwardfor': True,
            'option_redispatch': True
        }
    
    def generate_global_section(self) -> str:
        """Generate global configuration section"""        lines = ["global"]
        
        for key, value in self.global_config.items():
            if isinstance(value, bool):
                if value:
                    lines.append(f"    {key.replace('_', '-')}")
            else:
                lines.append(f"    {key.replace('_', '-')} {value}")
        
        return "\n".join(lines)
    
    def generate_defaults_section(self) -> str:
        """Generate defaults configuration section"""        lines = ["defaults"]
        
        for key, value in self.defaults_config.items():
            if isinstance(value, bool):
                if value:
                    lines.append(f"    {key.replace('_', ' ')}")
            else:
                lines.append(f"    {key.replace('_', ' ')} {value}")
        
        return "\n".join(lines)
    
    def generate_frontend_section(self, frontend: HAProxyFrontend) -> str:
        """Generate frontend configuration section"""        lines = [f"frontend {frontend.name}"]
        
        # Bind configuration
        bind_line = f"    bind {frontend.bind_address}:{frontend.bind_port}"
        if frontend.ssl_certificate:
            bind_line += f" ssl crt {frontend.ssl_certificate}"
        lines.append(bind_line)
        
        # Mode
        lines.append(f"    mode {frontend.mode}")
        
        # Redirect scheme
        if frontend.redirect_scheme:
            lines.append(f"    redirect scheme {frontend.redirect_scheme} if !{{ ssl_fc }}")
        
        # ACL rules
        if frontend.acl_rules:
            for acl in frontend.acl_rules:
                lines.append(f"    acl {acl['name']} {acl['condition']}")
        
        # Use backend rules
        if frontend.use_backend_rules:
            for rule in frontend.use_backend_rules:
                lines.append(f"    use_backend {rule['backend']} if {rule['condition']}")
        
        # Default backend
        if frontend.default_backend:
            lines.append(f"    default_backend {frontend.default_backend}")
        
        # Security headers
        if frontend.mode == "http":
            lines.extend([
                "    http-response set-header X-Frame-Options DENY",
                "    http-response set-header X-Content-Type-Options nosniff",
                "    http-response set-header X-XSS-Protection \"1; mode=block\"",
                "    http-response set-header Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\"",
                "    http-response set-header Referrer-Policy \"strict-origin-when-cross-origin\""
            ])
        
        return "\n".join(lines)
    
    def generate_backend_section(self, backend: HAProxyBackend) -> str:
        """Generate backend configuration section"""        lines = [f"backend {backend.name}"]
        
        # Mode and balance
        lines.append(f"    mode {backend.mode}")
        lines.append(f"    balance {backend.balance_algorithm}")
        
        # Timeouts
        lines.append(f"    timeout connect {backend.timeout_connect}")
        lines.append(f"    timeout server {backend.timeout_server}")
        
        # Health check
        if backend.health_check:
            lines.append(f"    option httpchk {backend.health_check}")
        
        # Cookie persistence
        if backend.cookie_persistence:
            lines.append(f"    cookie SERVERID insert indirect nocache")
        
        # SSL check
        if backend.ssl_check:
            lines.append("    option ssl-hello-chk")
        
        # HTTP options for HTTP mode
        if backend.mode == "http":
            lines.extend([
                "    option httplog",
                "    option http-server-close",
                "    option forwardfor",
                "    http-request set-header X-Forwarded-Proto https if { ssl_fc }",
                "    http-request set-header X-Forwarded-Proto http if !{ ssl_fc }"
            ])
        
        # Servers
        if backend.servers:
            for server in backend.servers:
                server_line = f"    server {server.name} {server.address}:{server.port}"
                
                if server.weight != 1:
                    server_line += f" weight {server.weight}"
                if server.maxconn != 1000:
                    server_line += f" maxconn {server.maxconn}"
                if server.check:
                    server_line += f" check inter {server.check_interval} rise {server.rise} fall {server.fall}"
                if server.backup:
                    server_line += " backup"
                if server.disabled:
                    server_line += " disabled"
                if backend.cookie_persistence:
                    server_line += f" cookie {server.name}"
                
                lines.append(server_line)
        
        return "\n".join(lines)
    
    def generate_stats_section(self, 
                             bind_address: str = "127.0.0.1",
                             bind_port: int = 8404,
                             username: str = "admin",
                             password: str = "admin") -> str:
        """Generate statistics section"""        lines = [
            "listen stats",
            f"    bind {bind_address}:{bind_port}",
            "    mode http",
            "    stats enable",
            "    stats uri /stats",
            "    stats refresh 30s",
            "    stats show-node",
            "    stats show-legends",
            f"    stats auth {username}:{password}",
            "    stats admin if TRUE"
        ]
        
        return "\n".join(lines)


class HAProxyManager:
    """Enterprise HAProxy Load Balancer Manager"""    
    def __init__(self, config_file: str = "/etc/haproxy/haproxy.cfg"):
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        self.config_generator = HAProxyConfigGenerator()
        self.frontends: List[HAProxyFrontend] = []
        self.backends: List[HAProxyBackend] = []
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def add_frontend(self, frontend: HAProxyFrontend) -> bool:
        """Add frontend configuration"""        try:
            # Check if frontend already exists
            existing = next((f for f in self.frontends if f.name == frontend.name), None)
            if existing:
                self.frontends.remove(existing)
            
            self.frontends.append(frontend)
            logger.info(f"Frontend {frontend.name} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add frontend {frontend.name}: {e}")
            return False
    
    def add_backend(self, backend: HAProxyBackend) -> bool:
        """Add backend configuration"""        try:
            # Check if backend already exists
            existing = next((b for b in self.backends if b.name == backend.name), None)
            if existing:
                self.backends.remove(existing)
            
            self.backends.append(backend)
            logger.info(f"Backend {backend.name} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add backend {backend.name}: {e}")
            return False
    
    def configure_platform_services(self) -> bool:
        """Configure HAProxy for platform services"""        try:
            # Configure backends for different services
            backends = [
                HAProxyBackend(
                    name="fingerprinting_servers",
                    balance_algorithm="leastconn",
                    health_check="GET /health",
                    servers=[
                        HAProxyServer("fingerprint-1", "10.0.1.10", 8001, weight=2),
                        HAProxyServer("fingerprint-2", "10.0.1.11", 8001, weight=2),
                        HAProxyServer("fingerprint-3", "10.0.1.12", 8001, weight=1, backup=True)
                    ],
                    timeout_server="300s"  # Extended for fingerprinting processing
                ),
                HAProxyBackend(
                    name="protection_servers",
                    balance_algorithm="roundrobin",
                    health_check="GET /health",
                    servers=[
                        HAProxyServer("protection-1", "10.0.2.10", 8002, weight=3),
                        HAProxyServer("protection-2", "10.0.2.11", 8002, weight=2)
                    ]
                ),
                HAProxyBackend(
                    name="monetization_servers",
                    balance_algorithm="source",  # Session persistence for payments
                    health_check="GET /health",
                    cookie_persistence=True,
                    servers=[
                        HAProxyServer("monetization-1", "10.0.3.10", 8003, weight=2),
                        HAProxyServer("monetization-2", "10.0.3.11", 8003, weight=2)
                    ]
                ),
                HAProxyBackend(
                    name="ai_agent_servers",
                    balance_algorithm="leastconn",
                    health_check="GET /health",
                    servers=[
                        HAProxyServer("ai-agent-1", "10.0.4.10", 8004, weight=3),
                        HAProxyServer("ai-agent-2", "10.0.4.11", 8004, weight=2)
                    ],
                    timeout_server="120s"  # Extended for AI processing
                ),
                HAProxyBackend(
                    name="crawler_servers",
                    balance_algorithm="roundrobin",
                    health_check="GET /health",
                    servers=[
                        HAProxyServer("crawler-1", "10.0.5.10", 8005, weight=1),
                        HAProxyServer("crawler-2", "10.0.5.11", 8005, weight=1)
                    ]
                ),
                HAProxyBackend(
                    name="dashboard_servers",
                    balance_algorithm="roundrobin",
                    health_check="GET /health",
                    servers=[
                        HAProxyServer("dashboard-1", "10.0.6.10", 3000, weight=1),
                        HAProxyServer("dashboard-2", "10.0.6.11", 3000, weight=1)
                    ]
                )
            ]
            
            # Add all backends
            for backend in backends:
                self.add_backend(backend)
            
            # Configure main API frontend
            api_frontend = HAProxyFrontend(
                name="ia_influencer_api",
                bind_address="0.0.0.0",
                bind_port=443,
                ssl_certificate="/etc/ssl/certs/ia-influencer.com.pem",
                redirect_scheme="https",
                acl_rules=[
                    {"name": "is_fingerprinting", "condition": "path_beg /api/v1/fingerprinting/"},
                    {"name": "is_protection", "condition": "path_beg /api/v1/protection/"},
                    {"name": "is_monetization", "condition": "path_beg /api/v1/monetization/"},
                    {"name": "is_ai_agent", "condition": "path_beg /api/v1/ai-agent/"},
                    {"name": "is_crawler", "condition": "path_beg /api/v1/crawlers/"},
                    {"name": "is_dashboard", "condition": "path_beg /dashboard/"}
                ],
                use_backend_rules=[
                    {"backend": "fingerprinting_servers", "condition": "is_fingerprinting"},
                    {"backend": "protection_servers", "condition": "is_protection"},
                    {"backend": "monetization_servers", "condition": "is_monetization"},
                    {"backend": "ai_agent_servers", "condition": "is_ai_agent"},
                    {"backend": "crawler_servers", "condition": "is_crawler"},
                    {"backend": "dashboard_servers", "condition": "is_dashboard"}
                ],
                default_backend="ai_agent_servers"
            )
            
            # Configure HTTP redirect frontend
            http_frontend = HAProxyFrontend(
                name="ia_influencer_http_redirect",
                bind_address="0.0.0.0",
                bind_port=80,
                redirect_scheme="https"
            )
            
            # Add frontends
            self.add_frontend(api_frontend)
            self.add_frontend(http_frontend)
            
            logger.info("Platform services configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform services: {e}")
            return False
    
    def generate_configuration(self) -> str:
        """Generate complete HAProxy configuration"""        try:
            config_sections = []
            
            # Global section
            config_sections.append(self.config_generator.generate_global_section())
            config_sections.append("")
            
            # Defaults section
            config_sections.append(self.config_generator.generate_defaults_section())
            config_sections.append("")
            
            # Stats section
            config_sections.append(self.config_generator.generate_stats_section())
            config_sections.append("")
            
            # Frontend sections
            for frontend in self.frontends:
                config_sections.append(self.config_generator.generate_frontend_section(frontend))
                config_sections.append("")
            
            # Backend sections
            for backend in self.backends:
                config_sections.append(self.config_generator.generate_backend_section(backend))
                config_sections.append("")
            
            return "\n".join(config_sections)
            
        except Exception as e:
            logger.error(f"Failed to generate configuration: {e}")
            return ""
    
    def write_configuration(self) -> bool:
        """Write configuration to file"""        try:
            config_content = self.generate_configuration()
            if not config_content:
                logger.error("Failed to generate configuration content")
                return False
            
            # Backup existing configuration
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                self.config_file.rename(backup_file)
                logger.info(f"Existing configuration backed up to {backup_file}")
            
            # Write new configuration
            with open(self.config_file, 'w') as f:
                f.write(config_content)
            
            logger.info(f"Configuration written to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write configuration: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test HAProxy configuration validity"""        try:
            result = subprocess.run(
                ['haproxy', '-c', '-f', str(self.config_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("HAProxy configuration test passed")
                return True
            else:
                logger.error(f"HAProxy configuration test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to test configuration: {e}")
            return False
    
    def reload_configuration(self) -> bool:
        """Reload HAProxy configuration"""        try:
            if not self.test_configuration():
                logger.error("Configuration test failed, not reloading")
                return False
            
            # Get master process PID
            pid_result = subprocess.run(['pgrep', '-f', 'haproxy'], capture_output=True, text=True)
            if pid_result.returncode != 0:
                logger.error("HAProxy is not running")
                return False
            
            master_pid = pid_result.stdout.strip().split('\n')[0]
            
            # Send USR2 signal for graceful reload
            reload_result = subprocess.run(['kill', '-USR2', master_pid], capture_output=True, text=True)
            
            if reload_result.returncode == 0:
                logger.info("HAProxy configuration reloaded successfully")
                return True
            else:
                logger.error(f"Failed to reload HAProxy: {reload_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HAProxy statistics via stats socket"""        try:
            # Connect to stats socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect('/run/haproxy/admin.sock')
            
            # Get general info
            sock.send(b'show info\n')
            info_data = sock.recv(4096).decode('utf-8')
            
            # Get stats
            sock.send(b'show stat\n')
            stats_data = sock.recv(8192).decode('utf-8')
            
            sock.close()
            
            # Parse stats
            stats = {
                'info': {},
                'backends': {},
                'frontends': {},
                'servers': {}
            }
            
            # Parse info data
            for line in info_data.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    stats['info'][key.strip()] = value.strip()
            
            # Parse stats data
            lines = stats_data.strip().split('\n')
            if lines:
                headers = lines[0].split(',')
                for line in lines[1:]:
                    values = line.split(',')
                    if len(values) >= len(headers):
                        stat_dict = dict(zip(headers, values))
                        pxname = stat_dict.get('# pxname', '')
                        svname = stat_dict.get('svname', '')
                        
                        if svname == 'BACKEND':
                            stats['backends'][pxname] = stat_dict
                        elif svname == 'FRONTEND':
                            stats['frontends'][pxname] = stat_dict
                        else:
                            if pxname not in stats['servers']:
                                stats['servers'][pxname] = {}
                            stats['servers'][pxname][svname] = stat_dict
            
            stats['timestamp'] = datetime.now().isoformat()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get HAProxy stats: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict[str, Any]:
        """Get HAProxy status and health"""        try:
            # Check if HAProxy is running
            ps_result = subprocess.run(['pgrep', 'haproxy'], capture_output=True, text=True)
            is_running = ps_result.returncode == 0
            
            status = {
                'is_running': is_running,
                'config_test_passed': self.test_configuration(),
                'frontends_count': len(self.frontends),
                'backends_count': len(self.backends),
                'config_file': str(self.config_file),
                'timestamp': datetime.now().isoformat()
            }
            
            if is_running:
                # Get process info
                ps_info = subprocess.run(
                    ['ps', '-p', ps_result.stdout.strip(), '-o', 'pid,ppid,cmd'],
                    capture_output=True,
                    text=True
                )
                status['process_info'] = ps_info.stdout if ps_info.returncode == 0 else None
                
                # Get stats if available
                try:
                    stats = self.get_stats()
                    status['stats_available'] = 'error' not in stats
                    if 'info' in stats:
                        status['version'] = stats['info'].get('Version', 'Unknown')
                        status['uptime'] = stats['info'].get('Uptime_sec', 'Unknown')
                except:
                    status['stats_available'] = False
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get HAProxy status: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
