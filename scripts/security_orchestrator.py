#!/usr/bin/env python3
"""
Security Orchestrator - Enterprise Security Automation
Author: Fahed Mlaiel (mlaiel@live.de) 
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced security automation for Ainflue Platform:
- Vulnerability scanning and assessment
- Threat detection and response
- Security policy enforcement
- Compliance monitoring and reporting
- Incident response automation
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import requests
import hashlib
import socket
from dataclasses import dataclass, asdict
from enum import Enum

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(Enum):
    VULNERABILITY = "vulnerability"
    INTRUSION = "intrusion"
    MALWARE = "malware"
    DATA_BREACH = "data_breach"
    POLICY_VIOLATION = "policy_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source: str
    description: str
    affected_systems: List[str]
    evidence: Dict[str, Any]
    status: str = "detected"
    response_actions: List[str] = None

@dataclass
class VulnerabilityReport:
    """Vulnerability assessment report"""
    scan_id: str
    timestamp: datetime
    target: str
    vulnerabilities: List[Dict[str, Any]]
    risk_score: float
    recommendations: List[str]

class SecurityOrchestrator:
    """
    Enterprise security automation orchestrator
    
    Features:
    - Automated vulnerability scanning
    - Real-time threat detection
    - Incident response automation
    - Compliance monitoring
    - Security policy enforcement
    - Audit trail maintenance
    """
    
    def __init__(self, config_path: str = "/etc/ainflue/security.yaml"):
        self.config_path = config_path
        self.security_events: List[SecurityEvent] = []
        self.active_incidents: Dict[str, SecurityEvent] = {}
        self.vulnerability_reports: List[VulnerabilityReport] = []
        self.blocked_ips: set = set()
        self.security_policies = {}
        
    async def load_security_configuration(self) -> Dict[str, Any]:
        """Load security configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.security_policies = config.get('policies', {})
            logger.info("Security configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load security configuration: {e}")
            # Use default configuration
            return {
                'policies': {
                    'max_failed_logins': 5,
                    'session_timeout': 3600,
                    'password_complexity': True,
                    'rate_limit_per_minute': 100
                },
                'scanning': {
                    'vulnerability_scan_interval': 86400,
                    'port_scan_detection': True,
                    'malware_scan_enabled': True
                },
                'alerts': {
                    'email_notifications': True,
                    'slack_webhook': None,
                    'sms_alerts': False
                }
            }
    
    async def run_vulnerability_scan(self, target: str = "localhost") -> VulnerabilityReport:
        """Execute comprehensive vulnerability scan"""
        try:
            scan_id = hashlib.md5(f"{target}_{datetime.now()}".encode()).hexdigest()
            logger.info(f"Starting vulnerability scan {scan_id} for target: {target}")
            
            vulnerabilities = []
            
            # Network port scan
            open_ports = await self._scan_ports(target)
            for port in open_ports:
                vulnerabilities.append({
                    'type': 'open_port',
                    'severity': 'medium',
                    'port': port,
                    'description': f'Open port {port} detected',
                    'recommendation': f'Review necessity of port {port}'
                })
            
            # SSL/TLS security check
            ssl_issues = await self._check_ssl_security(target)
            vulnerabilities.extend(ssl_issues)
            
            # Web application security scan
            if target in ['localhost', '127.0.0.1'] or target.startswith('http'):
                web_vulns = await self._scan_web_vulnerabilities(target)
                vulnerabilities.extend(web_vulns)
            
            # System configuration check
            config_issues = await self._check_system_configuration()
            vulnerabilities.extend(config_issues)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(vulnerabilities)
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(vulnerabilities)
            
            report = VulnerabilityReport(
                scan_id=scan_id,
                timestamp=datetime.now(),
                target=target,
                vulnerabilities=vulnerabilities,
                risk_score=risk_score,
                recommendations=recommendations
            )
            
            self.vulnerability_reports.append(report)
            
            logger.info(f"Vulnerability scan completed. Risk score: {risk_score:.2f}")
            
            # Generate alert for high-risk findings
            if risk_score >= 7.0:
                await self._create_security_event(
                    SecurityEventType.VULNERABILITY,
                    ThreatLevel.HIGH,
                    f"High-risk vulnerabilities detected (score: {risk_score:.2f})",
                    [target],
                    {'scan_id': scan_id, 'vulnerability_count': len(vulnerabilities)}
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Vulnerability scan failed: {e}")
            raise
    
    async def _scan_ports(self, target: str, ports: List[int] = None) -> List[int]:
        """Scan for open ports"""
        if ports is None:
            ports = [22, 80, 443, 3306, 5432, 6379, 27017, 9200, 5601]
        
        open_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    
            except Exception:
                continue
        
        return open_ports
    
    async def _check_ssl_security(self, target: str) -> List[Dict[str, Any]]:
        """Check SSL/TLS security configuration"""
        vulnerabilities = []
        
        try:
            # Use openssl to check certificate
            result = subprocess.run([
                'openssl', 's_client', '-connect', f'{target}:443',
                '-servername', target, '-brief'
            ], capture_output=True, text=True, timeout=10, input='')
            
            if result.returncode == 0:
                output = result.stdout + result.stderr
                
                # Check for weak protocols
                if 'TLSv1.0' in output or 'TLSv1.1' in output:
                    vulnerabilities.append({
                        'type': 'weak_tls',
                        'severity': 'high',
                        'description': 'Weak TLS protocol versions detected',
                        'recommendation': 'Disable TLSv1.0 and TLSv1.1, use TLSv1.2+'
                    })
                
                # Check certificate expiration
                if 'Certificate will expire' in output:
                    vulnerabilities.append({
                        'type': 'cert_expiring',
                        'severity': 'medium',
                        'description': 'SSL certificate expiring soon',
                        'recommendation': 'Renew SSL certificate before expiration'
                    })
            
        except Exception as e:
            logger.warning(f"SSL check failed for {target}: {e}")
        
        return vulnerabilities
    
    async def _scan_web_vulnerabilities(self, target: str) -> List[Dict[str, Any]]:
        """Scan for common web vulnerabilities"""
        vulnerabilities = []
        
        try:
            base_url = target if target.startswith('http') else f'http://{target}'
            
            # Check for common security headers
            response = requests.get(base_url, timeout=10)
            headers = response.headers
            
            # Missing security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000',
                'Content-Security-Policy': 'default-src \'self\''
            }
            
            for header, expected in security_headers.items():
                if header not in headers:
                    vulnerabilities.append({
                        'type': 'missing_security_header',
                        'severity': 'medium',
                        'header': header,
                        'description': f'Missing security header: {header}',
                        'recommendation': f'Add {header}: {expected}'
                    })
            
            # Check for information disclosure
            server_header = headers.get('Server', '')
            if server_header and not server_header.lower().startswith('ainflue'):
                vulnerabilities.append({
                    'type': 'information_disclosure',
                    'severity': 'low',
                    'description': f'Server version disclosed: {server_header}',
                    'recommendation': 'Remove or customize Server header'
                })
            
            # Test for SQL injection (basic)
            test_urls = [
                f"{base_url}/?id=1'",
                f"{base_url}/search?q=test'"
            ]
            
            for test_url in test_urls:
                try:
                    response = requests.get(test_url, timeout=5)
                    if any(error in response.text.lower() for error in 
                          ['sql syntax', 'mysql error', 'postgresql error', 'sqlite error']):
                        vulnerabilities.append({
                            'type': 'sql_injection',
                            'severity': 'critical',
                            'url': test_url,
                            'description': 'Potential SQL injection vulnerability',
                            'recommendation': 'Implement parameterized queries and input validation'
                        })
                except:
                    continue
            
        except Exception as e:
            logger.warning(f"Web vulnerability scan failed: {e}")
        
        return vulnerabilities
    
    async def _check_system_configuration(self) -> List[Dict[str, Any]]:
        """Check system security configuration"""
        vulnerabilities = []
        
        try:
            # Check for weak file permissions
            sensitive_files = [
                '/etc/passwd',
                '/etc/shadow',
                '/etc/ssh/sshd_config',
                '/etc/ainflue/config.yaml'
            ]
            
            for file_path in sensitive_files:
                if os.path.exists(file_path):
                    stat_info = os.stat(file_path)
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    if file_path == '/etc/shadow' and permissions != '640':
                        vulnerabilities.append({
                            'type': 'weak_file_permissions',
                            'severity': 'high',
                            'file': file_path,
                            'permissions': permissions,
                            'description': f'Weak permissions on {file_path}',
                            'recommendation': 'Set appropriate permissions (640 for shadow file)'
                        })
            
            # Check SSH configuration
            if os.path.exists('/etc/ssh/sshd_config'):
                with open('/etc/ssh/sshd_config', 'r') as f:
                    ssh_config = f.read()
                
                if 'PermitRootLogin yes' in ssh_config:
                    vulnerabilities.append({
                        'type': 'ssh_root_login',
                        'severity': 'high',
                        'description': 'SSH root login enabled',
                        'recommendation': 'Disable root SSH login'
                    })
                
                if 'PasswordAuthentication yes' in ssh_config:
                    vulnerabilities.append({
                        'type': 'ssh_password_auth',
                        'severity': 'medium',
                        'description': 'SSH password authentication enabled',
                        'recommendation': 'Use key-based authentication only'
                    })
            
        except Exception as e:
            logger.warning(f"System configuration check failed: {e}")
        
        return vulnerabilities
    
    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score"""
        severity_weights = {
            'critical': 10.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5
        }
        
        total_score = 0.0
        max_possible = 0.0
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            weight = severity_weights.get(severity, 2.5)
            total_score += weight
            max_possible += 10.0
        
        if max_possible == 0:
            return 0.0
        
        return min(10.0, (total_score / len(vulnerabilities)) if vulnerabilities else 0.0)
    
    def _generate_security_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            rec = vuln.get('recommendation')
            if rec:
                recommendations.add(rec)
        
        # Add general recommendations
        recommendations.add('Implement regular security scanning')
        recommendations.add('Keep all systems and dependencies updated')
        recommendations.add('Enable comprehensive logging and monitoring')
        recommendations.add('Implement proper backup and disaster recovery')
        
        return list(recommendations)
    
    async def monitor_security_events(self, duration: int = 3600) -> List[SecurityEvent]:
        """Monitor for security events"""
        logger.info(f"Starting security event monitoring for {duration} seconds")
        
        events = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Check for suspicious network activity
                network_events = await self._detect_network_anomalies()
                events.extend(network_events)
                
                # Check for file system anomalies
                fs_events = await self._detect_filesystem_anomalies()
                events.extend(fs_events)
                
                # Check for authentication anomalies
                auth_events = await self._detect_authentication_anomalies()
                events.extend(auth_events)
                
                # Process and respond to events
                for event in events[-10:]:  # Process last 10 events
                    await self._process_security_event(event)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(60)
        
        logger.info(f"Security monitoring completed. {len(events)} events detected")
        return events
    
    async def _detect_network_anomalies(self) -> List[SecurityEvent]:
        """Detect network-based security anomalies"""
        events = []
        
        try:
            # Check for port scanning attempts
            netstat_result = subprocess.run(
                ['netstat', '-an'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if netstat_result.returncode == 0:
                connections = netstat_result.stdout.split('\n')
                connection_counts = {}
                
                for conn in connections:
                    if 'ESTABLISHED' in conn:
                        parts = conn.split()
                        if len(parts) >= 5:
                            remote_addr = parts[4].split(':')[0]
                            connection_counts[remote_addr] = connection_counts.get(remote_addr, 0) + 1
                
                # Flag IPs with unusually high connection counts
                for ip, count in connection_counts.items():
                    if count > 50 and ip not in ['127.0.0.1', '::1']:
                        event = SecurityEvent(
                            event_id=hashlib.md5(f"network_{ip}_{datetime.now()}".encode()).hexdigest(),
                            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                            threat_level=ThreatLevel.MEDIUM,
                            timestamp=datetime.now(),
                            source=ip,
                            description=f"High connection count from IP: {ip} ({count} connections)",
                            affected_systems=['network'],
                            evidence={'connection_count': count, 'ip_address': ip}
                        )
                        events.append(event)
            
        except Exception as e:
            logger.warning(f"Network anomaly detection failed: {e}")
        
        return events
    
    async def _detect_filesystem_anomalies(self) -> List[SecurityEvent]:
        """Detect filesystem-based security anomalies"""
        events = []
        
        try:
            # Check for unauthorized file modifications
            sensitive_paths = [
                '/etc/passwd',
                '/etc/shadow',
                '/etc/hosts',
                '/etc/crontab'
            ]
            
            for path in sensitive_paths:
                if os.path.exists(path):
                    stat_info = os.stat(path)
                    current_time = time.time()
                    
                    # Flag files modified in the last 5 minutes
                    if current_time - stat_info.st_mtime < 300:
                        event = SecurityEvent(
                            event_id=hashlib.md5(f"fs_{path}_{datetime.now()}".encode()).hexdigest(),
                            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                            threat_level=ThreatLevel.HIGH,
                            timestamp=datetime.now(),
                            source='filesystem',
                            description=f"Recent modification to sensitive file: {path}",
                            affected_systems=['filesystem'],
                            evidence={'file_path': path, 'modification_time': stat_info.st_mtime}
                        )
                        events.append(event)
            
        except Exception as e:
            logger.warning(f"Filesystem anomaly detection failed: {e}")
        
        return events
    
    async def _detect_authentication_anomalies(self) -> List[SecurityEvent]:
        """Detect authentication-based security anomalies"""
        events = []
        
        try:
            # Check system logs for failed authentication attempts
            if os.path.exists('/var/log/auth.log'):
                result = subprocess.run(
                    ['tail', '-n', '100', '/var/log/auth.log'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    auth_logs = result.stdout.split('\n')
                    failed_attempts = {}
                    
                    for line in auth_logs:
                        if 'Failed password' in line or 'authentication failure' in line:
                            # Extract IP address if present
                            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                            if ip_match:
                                ip = ip_match.group(1)
                                failed_attempts[ip] = failed_attempts.get(ip, 0) + 1
                    
                    # Flag IPs with multiple failed attempts
                    for ip, count in failed_attempts.items():
                        if count >= 3:
                            event = SecurityEvent(
                                event_id=hashlib.md5(f"auth_{ip}_{datetime.now()}".encode()).hexdigest(),
                                event_type=SecurityEventType.INTRUSION,
                                threat_level=ThreatLevel.HIGH,
                                timestamp=datetime.now(),
                                source=ip,
                                description=f"Multiple failed authentication attempts from {ip} ({count} attempts)",
                                affected_systems=['authentication'],
                                evidence={'failed_attempts': count, 'ip_address': ip}
                            )
                            events.append(event)
            
        except Exception as e:
            logger.warning(f"Authentication anomaly detection failed: {e}")
        
        return events
    
    async def _process_security_event(self, event: SecurityEvent):
        """Process and respond to security events"""
        try:
            logger.warning(f"Processing security event: {event.event_id}")
            
            # Add to security events list
            self.security_events.append(event)
            
            # Determine response actions
            response_actions = []
            
            if event.threat_level == ThreatLevel.CRITICAL:
                response_actions.extend([
                    'immediate_escalation',
                    'block_source_ip',
                    'emergency_notification'
                ])
            elif event.threat_level == ThreatLevel.HIGH:
                response_actions.extend([
                    'escalate_to_admin',
                    'increase_monitoring',
                    'collect_evidence'
                ])
            
            # Execute automated responses
            await self._execute_response_actions(event, response_actions)
            
            # Send notifications
            await self._send_security_notification(event)
            
            # Update incident tracking
            if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self.active_incidents[event.event_id] = event
            
        except Exception as e:
            logger.error(f"Failed to process security event: {e}")
    
    async def _execute_response_actions(self, event: SecurityEvent, actions: List[str]):
        """Execute automated response actions"""
        for action in actions:
            try:
                if action == 'block_source_ip' and event.source:
                    await self._block_ip_address(event.source)
                elif action == 'increase_monitoring':
                    await self._increase_monitoring_level()
                elif action == 'collect_evidence':
                    await self._collect_security_evidence(event)
                
                logger.info(f"Executed response action: {action}")
                
            except Exception as e:
                logger.error(f"Failed to execute response action {action}: {e}")
    
    async def _block_ip_address(self, ip_address: str):
        """Block IP address using iptables"""
        try:
            if ip_address not in self.blocked_ips:
                result = subprocess.run([
                    'iptables', '-A', 'INPUT', 
                    '-s', ip_address, 
                    '-j', 'DROP'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.blocked_ips.add(ip_address)
                    logger.info(f"Blocked IP address: {ip_address}")
                else:
                    logger.error(f"Failed to block IP {ip_address}: {result.stderr}")
        
        except Exception as e:
            logger.error(f"IP blocking failed: {e}")
    
    async def _increase_monitoring_level(self):
        """Increase monitoring sensitivity"""
        # Implementation would adjust monitoring thresholds
        logger.info("Increased monitoring sensitivity")
    
    async def _collect_security_evidence(self, event: SecurityEvent):
        """Collect evidence for security incident"""
        try:
            evidence_dir = f"/var/log/ainflue/evidence/{event.event_id}"
            os.makedirs(evidence_dir, exist_ok=True)
            
            # Collect system information
            with open(f"{evidence_dir}/system_info.txt", 'w') as f:
                f.write(f"Event ID: {event.event_id}\n")
                f.write(f"Timestamp: {event.timestamp}\n")
                f.write(f"Description: {event.description}\n")
                f.write(f"Evidence: {json.dumps(event.evidence, indent=2)}\n")
            
            logger.info(f"Evidence collected for event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Evidence collection failed: {e}")
    
    async def _send_security_notification(self, event: SecurityEvent):
        """Send security notification"""
        try:
            # Log notification (implementation would include email/Slack/SMS)
            logger.warning(
                f"SECURITY ALERT: {event.description} "
                f"(Level: {event.threat_level.value}, Source: {event.source})"
            )
            
        except Exception as e:
            logger.error(f"Security notification failed: {e}")
    
    async def _create_security_event(self, event_type: SecurityEventType, 
                                   threat_level: ThreatLevel, description: str,
                                   affected_systems: List[str], evidence: Dict[str, Any]):
        """Create and process a new security event"""
        event = SecurityEvent(
            event_id=hashlib.md5(f"{event_type.value}_{datetime.now()}".encode()).hexdigest(),
            event_type=event_type,
            threat_level=threat_level,
            timestamp=datetime.now(),
            source='system',
            description=description,
            affected_systems=affected_systems,
            evidence=evidence
        )
        
        await self._process_security_event(event)
        return event
    
    async def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            report = {
                'report_id': hashlib.md5(f"security_report_{datetime.now()}".encode()).hexdigest(),
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_events': len(self.security_events),
                    'active_incidents': len(self.active_incidents),
                    'vulnerability_scans': len(self.vulnerability_reports),
                    'blocked_ips': len(self.blocked_ips)
                },
                'threat_levels': {
                    'critical': len([e for e in self.security_events if e.threat_level == ThreatLevel.CRITICAL]),
                    'high': len([e for e in self.security_events if e.threat_level == ThreatLevel.HIGH]),
                    'medium': len([e for e in self.security_events if e.threat_level == ThreatLevel.MEDIUM]),
                    'low': len([e for e in self.security_events if e.threat_level == ThreatLevel.LOW])
                },
                'latest_vulnerabilities': [
                    asdict(report) for report in self.vulnerability_reports[-5:]
                ],
                'recent_events': [
                    asdict(event) for event in self.security_events[-10:]
                ]
            }
            
            logger.info("Security report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Security report generation failed: {e}")
            raise

async def main():
    """CLI entry point for security orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue Security Orchestrator')
    parser.add_argument('--scan', action='store_true', help='Run vulnerability scan')
    parser.add_argument('--monitor', type=int, metavar='DURATION', help='Monitor for security events (seconds)')
    parser.add_argument('--report', action='store_true', help='Generate security report')
    parser.add_argument('--target', default='localhost', help='Scan target')
    parser.add_argument('--config', default='/etc/ainflue/security.yaml', help='Configuration file')
    
    args = parser.parse_args()
    
    orchestrator = SecurityOrchestrator(args.config)
    await orchestrator.load_security_configuration()
    
    try:
        if args.scan:
            report = await orchestrator.run_vulnerability_scan(args.target)
            print(json.dumps(asdict(report), indent=2, default=str))
        
        if args.monitor:
            events = await orchestrator.monitor_security_events(args.monitor)
            print(f"Monitoring completed. {len(events)} events detected.")
        
        if args.report:
            report = await orchestrator.generate_security_report()
            print(json.dumps(report, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"Security orchestrator failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())