"""IA Influencer Agent - Certificate Monitoring System
Real-time SSL/TLS certificate monitoring and alerting

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
import os
import ssl
import time
import json
import logging
import asyncio
import smtplib
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import requests
import schedule
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import psutil


class AlertLevel(Enum):
    """Alert severity levels"""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringStatus(Enum):
    """Certificate monitoring status"""    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    INVALID = "invalid"
    UNREACHABLE = "unreachable"
    REVOKED = "revoked"


@dataclass
class CertificateEndpoint:
    """Certificate endpoint configuration"""    name: str
    hostname: str
    port: int = 443
    check_interval: int = 3600  # seconds
    warning_days: int = 30
    critical_days: int = 7
    enabled: bool = True
    verify_hostname: bool = True
    verify_chain: bool = True
    check_ocsp: bool = True
    custom_ca_path: Optional[str] = None
    tags: List[str] = None


@dataclass
class CertificateStatus:
    """Certificate status information"""    endpoint: str
    hostname: str
    port: int
    status: MonitoringStatus
    certificate_info: Dict[str, Any]
    last_check: datetime
    next_check: datetime
    alert_level: AlertLevel
    days_until_expiry: int
    issues: List[str]
    performance_metrics: Dict[str, float]


@dataclass
class AlertConfig:
    """Alert configuration"""    email_enabled: bool = True
    email_recipients: List[str] = None
    email_smtp_server: str = "localhost"
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_use_tls: bool = True
    
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None
    webhook_headers: Dict[str, str] = None
    
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None
    
    pagerduty_enabled: bool = False
    pagerduty_integration_key: Optional[str] = None
    
    log_file_path: Optional[str] = None
    log_level: str = "INFO"


class CertificateMonitoringError(Exception):
    """Certificate monitoring exception"""    pass


class CertificateMonitor:
    """    Enterprise SSL/TLS certificate monitoring system
    Real-time monitoring, alerting, and reporting
    """    
    def __init__(self, config_path: Optional[Path] = None):
        """        Initialize certificate monitor
        
        Args:
            config_path: Path to monitoring configuration
        """        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.endpoints: List[CertificateEndpoint] = []
        self.alert_config = AlertConfig()
        
        # Monitoring state
        self.certificate_statuses: Dict[str, CertificateStatus] = {}
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Performance tracking
        self.performance_metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'alerts_sent': 0,
            'last_check_duration': 0.0
        }
        
        # Alert rate limiting
        self.last_alerts: Dict[str, datetime] = {}
        self.alert_cooldown = 3600  # 1 hour
        
        # Load configuration
        if config_path and config_path.exists():
            self.load_config(config_path)
        
        self.logger.info("Certificate monitor initialized")
    
    def load_config(self, config_path: Path) -> None:
        """        Load monitoring configuration from file
        
        Args:
            config_path: Path to configuration file
        """        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Load endpoints
            self.endpoints = []
            for endpoint_data in config_data.get('endpoints', []):
                endpoint = CertificateEndpoint(**endpoint_data)
                self.endpoints.append(endpoint)
            
            # Load alert configuration
            alert_data = config_data.get('alerts', {})
            self.alert_config = AlertConfig(**alert_data)
            
            # Load monitoring settings
            monitoring_data = config_data.get('monitoring', {})
            self.alert_cooldown = monitoring_data.get('alert_cooldown', 3600)
            
            self.logger.info(f"Loaded configuration for {len(self.endpoints)} endpoints")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise CertificateMonitoringError(f"Configuration load failed: {e}")
    
    def save_config(self, config_path: Path) -> None:
        """        Save monitoring configuration to file
        
        Args:
            config_path: Path to save configuration
        """        try:
            config_data = {
                'endpoints': [asdict(endpoint) for endpoint in self.endpoints],
                'alerts': asdict(self.alert_config),
                'monitoring': {
                    'alert_cooldown': self.alert_cooldown
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def add_endpoint(self, endpoint: CertificateEndpoint) -> None:
        """        Add certificate endpoint for monitoring
        
        Args:
            endpoint: Endpoint configuration
        """        self.endpoints.append(endpoint)
        self.logger.info(f"Added endpoint: {endpoint.name} ({endpoint.hostname}:{endpoint.port})")
    
    def remove_endpoint(self, endpoint_name: str) -> bool:
        """        Remove certificate endpoint from monitoring
        
        Args:
            endpoint_name: Name of endpoint to remove
            
        Returns:
            True if endpoint was removed
        """        for i, endpoint in enumerate(self.endpoints):
            if endpoint.name == endpoint_name:
                del self.endpoints[i]
                # Remove from status tracking
                if endpoint_name in self.certificate_statuses:
                    del self.certificate_statuses[endpoint_name]
                self.logger.info(f"Removed endpoint: {endpoint_name}")
                return True
        return False
    
    def check_certificate(self, endpoint: CertificateEndpoint) -> CertificateStatus:
        """        Check certificate for single endpoint
        
        Args:
            endpoint: Endpoint to check
            
        Returns:
            Certificate status
        """        start_time = time.time()
        issues = []
        certificate_info = {}
        status = MonitoringStatus.VALID
        alert_level = AlertLevel.INFO
        days_until_expiry = 0
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            if endpoint.custom_ca_path:
                context.load_verify_locations(endpoint.custom_ca_path)
            
            if not endpoint.verify_hostname:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate
            with ssl.create_connection((endpoint.hostname, endpoint.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=endpoint.hostname) as ssock:
                    # Get peer certificate
                    der_cert = ssock.getpeercert_raw()
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    
                    # Extract certificate information
                    certificate_info = self._extract_certificate_info(cert, ssock)
                    
                    # Check expiry
                    now = datetime.utcnow()
                    not_after = cert.not_valid_after
                    days_until_expiry = (not_after - now).days
                    
                    # Determine status and alert level
                    if days_until_expiry < 0:
                        status = MonitoringStatus.EXPIRED
                        alert_level = AlertLevel.CRITICAL
                        issues.append("Certificate has expired")
                    elif days_until_expiry <= endpoint.critical_days:
                        status = MonitoringStatus.EXPIRING_SOON
                        alert_level = AlertLevel.CRITICAL
                        issues.append(f"Certificate expires in {days_until_expiry} days")
                    elif days_until_expiry <= endpoint.warning_days:
                        status = MonitoringStatus.EXPIRING_SOON
                        alert_level = AlertLevel.WARNING
                        issues.append(f"Certificate expires in {days_until_expiry} days")
                    
                    # Verify hostname if enabled
                    if endpoint.verify_hostname:
                        if not self._verify_hostname_match(cert, endpoint.hostname):
                            issues.append("Hostname verification failed")
                            if status == MonitoringStatus.VALID:
                                status = MonitoringStatus.INVALID
                                alert_level = AlertLevel.WARNING
                    
                    # Check certificate chain if enabled
                    if endpoint.verify_chain:
                        chain_issues = self._verify_certificate_chain(cert, ssock)
                        if chain_issues:
                            issues.extend(chain_issues)
                            if status == MonitoringStatus.VALID:
                                status = MonitoringStatus.INVALID
                                alert_level = AlertLevel.WARNING
                    
                    # Check OCSP if enabled
                    if endpoint.check_ocsp:
                        ocsp_issues = self._check_ocsp_status(cert)
                        if ocsp_issues:
                            issues.extend(ocsp_issues)
                            if "revoked" in " ".join(ocsp_issues).lower():
                                status = MonitoringStatus.REVOKED
                                alert_level = AlertLevel.CRITICAL
        
        except ssl.SSLError as e:
            issues.append(f"SSL error: {e}")
            status = MonitoringStatus.INVALID
            alert_level = AlertLevel.CRITICAL
        except ConnectionError as e:
            issues.append(f"Connection error: {e}")
            status = MonitoringStatus.UNREACHABLE
            alert_level = AlertLevel.WARNING
        except Exception as e:
            issues.append(f"Check failed: {e}")
            status = MonitoringStatus.INVALID
            alert_level = AlertLevel.WARNING
        
        # Calculate performance metrics
        check_duration = time.time() - start_time
        performance_metrics = {
            'check_duration': check_duration,
            'response_time': check_duration * 1000,  # ms
            'ssl_handshake_time': check_duration * 0.3  # estimated
        }
        
        # Create status object
        now = datetime.utcnow()
        next_check = now + timedelta(seconds=endpoint.check_interval)
        
        cert_status = CertificateStatus(
            endpoint=endpoint.name,
            hostname=endpoint.hostname,
            port=endpoint.port,
            status=status,
            certificate_info=certificate_info,
            last_check=now,
            next_check=next_check,
            alert_level=alert_level,
            days_until_expiry=days_until_expiry,
            issues=issues,
            performance_metrics=performance_metrics
        )
        
        # Update performance tracking
        self.performance_metrics['total_checks'] += 1
        if status in [MonitoringStatus.VALID, MonitoringStatus.EXPIRING_SOON]:
            self.performance_metrics['successful_checks'] += 1
        else:
            self.performance_metrics['failed_checks'] += 1
        self.performance_metrics['last_check_duration'] = check_duration
        
        self.logger.debug(f"Certificate check completed for {endpoint.name}: {status.value}")
        return cert_status
    
    def _extract_certificate_info(
        self, 
        cert: x509.Certificate, 
        ssl_socket: ssl.SSLSocket
    ) -> Dict[str, Any]:
        """Extract detailed certificate information"""        # Basic certificate info
        subject = cert.subject
        issuer = cert.issuer
        
        # Get common name
        common_name = None
        for attribute in subject:
            if attribute.oid == x509.NameOID.COMMON_NAME:
                common_name = attribute.value
                break
        
        # Get Subject Alternative Names
        san_list = []
        try:
            san_extension = cert.extensions.get_extension_for_oid(
                x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            for name in san_extension.value:
                if isinstance(name, x509.DNSName):
                    san_list.append(name.value)
        except x509.ExtensionNotFound:
            pass
        
        # Get SSL/TLS protocol and cipher info
        protocol = ssl_socket.version()
        cipher = ssl_socket.cipher()
        
        # Calculate fingerprints
        cert_der = cert.public_bytes(x509.Encoding.DER)
        sha1_fingerprint = hashlib.sha1(cert_der).hexdigest()
        sha256_fingerprint = hashlib.sha256(cert_der).hexdigest()
        
        return {
            'common_name': common_name,
            'subject': subject.rfc4514_string(),
            'issuer': issuer.rfc4514_string(),
            'serial_number': str(cert.serial_number),
            'not_before': cert.not_valid_before.isoformat(),
            'not_after': cert.not_valid_after.isoformat(),
            'subject_alt_names': san_list,
            'signature_algorithm': cert.signature_algorithm_oid._name,
            'key_size': cert.public_key().key_size if hasattr(cert.public_key(), 'key_size') else None,
            'sha1_fingerprint': sha1_fingerprint,
            'sha256_fingerprint': sha256_fingerprint,
            'protocol': protocol,
            'cipher_suite': cipher[0] if cipher else None,
            'cipher_strength': cipher[2] if cipher else None
        }
    
    def _verify_hostname_match(self, cert: x509.Certificate, hostname: str) -> bool:
        """Verify certificate matches hostname"""        try:
            # Check common name
            subject = cert.subject
            for attribute in subject:
                if attribute.oid == x509.NameOID.COMMON_NAME:
                    if self._match_hostname(attribute.value, hostname):
                        return True
            
            # Check Subject Alternative Names
            try:
                san_extension = cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                for name in san_extension.value:
                    if isinstance(name, x509.DNSName):
                        if self._match_hostname(name.value, hostname):
                            return True
            except x509.ExtensionNotFound:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _match_hostname(self, cert_hostname: str, request_hostname: str) -> bool:
        """Match hostname with wildcard support"""        if cert_hostname == request_hostname:
            return True
        
        # Wildcard matching
        if cert_hostname.startswith('*.'):
            cert_domain = cert_hostname[2:]
            if '.' in request_hostname:
                request_domain = request_hostname.split('.', 1)[1]
                return cert_domain == request_domain
        
        return False
    
    def _verify_certificate_chain(self, cert: x509.Certificate, ssl_socket: ssl.SSLSocket) -> List[str]:
        """Verify certificate chain"""        issues = []
        try:
            # Get certificate chain
            cert_chain = ssl_socket.getpeercert_chain()
            if not cert_chain or len(cert_chain) < 2:
                issues.append("Incomplete certificate chain")
            
            # Additional chain validation can be implemented here
            
        except Exception as e:
            issues.append(f"Chain verification failed: {e}")
        
        return issues
    
    def _check_ocsp_status(self, cert: x509.Certificate) -> List[str]:
        """Check OCSP status"""        issues = []
        try:
            # Extract OCSP URL from certificate
            ocsp_url = None
            try:
                aia_extension = cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS
                )
                for access_description in aia_extension.value:
                    if access_description.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                        ocsp_url = access_description.access_location.value
                        break
            except x509.ExtensionNotFound:
                return issues  # No OCSP URL found
            
            if ocsp_url:
                # Simple OCSP check (production would need full OCSP implementation)
                try:
                    response = requests.head(ocsp_url, timeout=5)
                    if response.status_code not in [200, 405]:  # 405 is common for HEAD requests
                        issues.append("OCSP responder unreachable")
                except requests.RequestException:
                    issues.append("OCSP check failed")
            
        except Exception as e:
            issues.append(f"OCSP status check failed: {e}")
        
        return issues
    
    async def start_monitoring(self) -> None:
        """Start continuous certificate monitoring"""        if self.monitoring_active:
            self.logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.logger.info("Starting certificate monitoring")
        
        # Schedule initial checks
        for endpoint in self.endpoints:
            if endpoint.enabled:
                schedule.every(endpoint.check_interval).seconds.do(
                    self._scheduled_check, endpoint
                )
        
        # Run monitoring loop
        while self.monitoring_active:
            try:
                schedule.run_pending()
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)
        
        self.logger.info("Certificate monitoring stopped")
    
    def stop_monitoring(self) -> None:
        """Stop certificate monitoring"""        self.monitoring_active = False
        schedule.clear()
        self.logger.info("Stopping certificate monitoring")
    
    def _scheduled_check(self, endpoint: CertificateEndpoint) -> None:
        """Perform scheduled certificate check"""        try:
            cert_status = self.check_certificate(endpoint)
            self.certificate_statuses[endpoint.name] = cert_status
            
            # Send alerts if needed
            if cert_status.alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
                self._send_alert(cert_status)
            
        except Exception as e:
            self.logger.error(f"Scheduled check failed for {endpoint.name}: {e}")
    
    def _send_alert(self, cert_status: CertificateStatus) -> None:
        """Send certificate alert"""        try:
            # Check alert rate limiting
            alert_key = f"{cert_status.endpoint}:{cert_status.alert_level.value}"
            now = datetime.utcnow()
            
            if alert_key in self.last_alerts:
                time_since_last = (now - self.last_alerts[alert_key]).total_seconds()
                if time_since_last < self.alert_cooldown:
                    self.logger.debug(f"Alert rate limited for {alert_key}")
                    return
            
            self.last_alerts[alert_key] = now
            
            # Prepare alert message
            alert_message = self._format_alert_message(cert_status)
            
            # Send email alert
            if self.alert_config.email_enabled:
                self._send_email_alert(cert_status, alert_message)
            
            # Send webhook alert
            if self.alert_config.webhook_enabled:
                self._send_webhook_alert(cert_status, alert_message)
            
            # Send Slack alert
            if self.alert_config.slack_enabled:
                self._send_slack_alert(cert_status, alert_message)
            
            # Send PagerDuty alert
            if self.alert_config.pagerduty_enabled:
                self._send_pagerduty_alert(cert_status, alert_message)
            
            self.performance_metrics['alerts_sent'] += 1
            self.logger.info(f"Alert sent for {cert_status.endpoint}: {cert_status.alert_level.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    def _format_alert_message(self, cert_status: CertificateStatus) -> str:
        """Format alert message"""        message_lines = [
            f"Certificate Alert - {cert_status.alert_level.value.upper()}",
            f"",
            f"Endpoint: {cert_status.endpoint}",
            f"Hostname: {cert_status.hostname}:{cert_status.port}",
            f"Status: {cert_status.status.value}",
            f"Days until expiry: {cert_status.days_until_expiry}",
            f"Last check: {cert_status.last_check.isoformat()}",
        ]
        
        if cert_status.certificate_info.get('common_name'):
            message_lines.append(f"Certificate CN: {cert_status.certificate_info['common_name']}")
        
        if cert_status.certificate_info.get('not_after'):
            message_lines.append(f"Expires: {cert_status.certificate_info['not_after']}")
        
        if cert_status.issues:
            message_lines.extend([
                f"",
                f"Issues:",
                *[f"- {issue}" for issue in cert_status.issues]
            ])
        
        return "\n".join(message_lines)
    
    def _send_email_alert(self, cert_status: CertificateStatus, message: str) -> None:
        """Send email alert"""        try:
            if not self.alert_config.email_recipients:
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.alert_config.email_username or "certificate-monitor@localhost"
            msg['To'] = ", ".join(self.alert_config.email_recipients)
            msg['Subject'] = f"Certificate Alert: {cert_status.endpoint} - {cert_status.alert_level.value.upper()}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server
            with smtplib.SMTP(self.alert_config.email_smtp_server, self.alert_config.email_smtp_port) as server:
                if self.alert_config.email_use_tls:
                    server.starttls()
                
                if self.alert_config.email_username and self.alert_config.email_password:
                    server.login(self.alert_config.email_username, self.alert_config.email_password)
                
                server.send_message(msg)
            
            self.logger.debug(f"Email alert sent for {cert_status.endpoint}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _send_webhook_alert(self, cert_status: CertificateStatus, message: str) -> None:
        """Send webhook alert"""        try:
            if not self.alert_config.webhook_url:
                return
            
            payload = {
                'endpoint': cert_status.endpoint,
                'hostname': cert_status.hostname,
                'port': cert_status.port,
                'status': cert_status.status.value,
                'alert_level': cert_status.alert_level.value,
                'days_until_expiry': cert_status.days_until_expiry,
                'issues': cert_status.issues,
                'certificate_info': cert_status.certificate_info,
                'timestamp': cert_status.last_check.isoformat(),
                'message': message
            }
            
            headers = self.alert_config.webhook_headers or {'Content-Type': 'application/json'}
            
            response = requests.post(
                self.alert_config.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Webhook alert sent for {cert_status.endpoint}")
            else:
                self.logger.warning(f"Webhook alert failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")
    
    def _send_slack_alert(self, cert_status: CertificateStatus, message: str) -> None:
        """Send Slack alert"""        try:
            if not self.alert_config.slack_webhook_url:
                return
            
            color = {
                AlertLevel.INFO: "good",
                AlertLevel.WARNING: "warning",
                AlertLevel.CRITICAL: "danger",
                AlertLevel.EMERGENCY: "danger"
            }.get(cert_status.alert_level, "warning")
            
            payload = {
                "channel": self.alert_config.slack_channel,
                "username": "Certificate Monitor",
                "icon_emoji": ":warning:",
                "attachments": [{
                    "color": color,
                    "title": f"Certificate Alert: {cert_status.endpoint}",
                    "text": message,
                    "fields": [
                        {
                            "title": "Status",
                            "value": cert_status.status.value,
                            "short": True
                        },
                        {
                            "title": "Days until expiry",
                            "value": str(cert_status.days_until_expiry),
                            "short": True
                        }
                    ],
                    "ts": int(cert_status.last_check.timestamp())
                }]
            }
            
            response = requests.post(
                self.alert_config.slack_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Slack alert sent for {cert_status.endpoint}")
            else:
                self.logger.warning(f"Slack alert failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_pagerduty_alert(self, cert_status: CertificateStatus, message: str) -> None:
        """Send PagerDuty alert"""        try:
            if not self.alert_config.pagerduty_integration_key:
                return
            
            payload = {
                "routing_key": self.alert_config.pagerduty_integration_key,
                "event_action": "trigger",
                "dedup_key": f"cert-{cert_status.endpoint}",
                "payload": {
                    "summary": f"Certificate Alert: {cert_status.endpoint} - {cert_status.status.value}",
                    "source": cert_status.hostname,
                    "severity": "critical" if cert_status.alert_level == AlertLevel.CRITICAL else "warning",
                    "component": "ssl-certificate",
                    "group": "certificate-monitoring",
                    "class": "certificate",
                    "custom_details": {
                        "endpoint": cert_status.endpoint,
                        "hostname": cert_status.hostname,
                        "port": cert_status.port,
                        "days_until_expiry": cert_status.days_until_expiry,
                        "issues": cert_status.issues,
                        "message": message
                    }
                }
            }
            
            response = requests.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 202:
                self.logger.debug(f"PagerDuty alert sent for {cert_status.endpoint}")
            else:
                self.logger.warning(f"PagerDuty alert failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to send PagerDuty alert: {e}")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get monitoring status summary"""        total_endpoints = len(self.endpoints)
        active_endpoints = len([e for e in self.endpoints if e.enabled])
        
        status_counts = {}
        for status in MonitoringStatus:
            status_counts[status.value] = 0
        
        alert_counts = {}
        for level in AlertLevel:
            alert_counts[level.value] = 0
        
        for cert_status in self.certificate_statuses.values():
            status_counts[cert_status.status.value] += 1
            alert_counts[cert_status.alert_level.value] += 1
        
        return {
            'monitoring_active': self.monitoring_active,
            'total_endpoints': total_endpoints,
            'active_endpoints': active_endpoints,
            'status_distribution': status_counts,
            'alert_distribution': alert_counts,
            'performance_metrics': self.performance_metrics,
            'last_update': datetime.utcnow().isoformat()
        }
    
    def get_detailed_status(self) -> List[Dict[str, Any]]:
        """Get detailed status for all endpoints"""        return [asdict(status) for status in self.certificate_statuses.values()]
    
    def generate_report(self, output_path: Path, format_type: str = "json") -> None:
        """        Generate monitoring report
        
        Args:
            output_path: Report output path
            format_type: Report format (json/html/csv)
        """        try:
            report_data = {
                'summary': self.get_status_summary(),
                'endpoints': self.get_detailed_status(),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            if format_type.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
            elif format_type.lower() == "html":
                self._generate_html_report(report_data, output_path)
            elif format_type.lower() == "csv":
                self._generate_csv_report(report_data, output_path)
            else:
                raise ValueError(f"Unsupported report format: {format_type}")
            
            self.logger.info(f"Report generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise
    
    def _generate_html_report(self, report_data: Dict[str, Any], output_path: Path) -> None:
        """Generate HTML report"""        html_content = f"""        <!DOCTYPE html>
        <html>
        <head>
            <title>Certificate Monitoring Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .critical {{ background-color: #ffebee; }}
                .warning {{ background-color: #fff3e0; }}
                .valid {{ background-color: #e8f5e8; }}
            </style>
        </head>
        <body>
            <h1>Certificate Monitoring Report</h1>
            <p>Generated: {report_data['generated_at']}</p>
            
            <h2>Summary</h2>
            <p>Total Endpoints: {report_data['summary']['total_endpoints']}</p>
            <p>Active Endpoints: {report_data['summary']['active_endpoints']}</p>
            <p>Monitoring Status: {'Active' if report_data['summary']['monitoring_active'] else 'Inactive'}</p>
            
            <h2>Certificate Status</h2>
            <table>
                <tr>
                    <th>Endpoint</th>
                    <th>Hostname</th>
                    <th>Status</th>
                    <th>Days Until Expiry</th>
                    <th>Last Check</th>
                    <th>Issues</th>
                </tr>
        """        
        for endpoint in report_data['endpoints']:
            status_class = {
                'valid': 'valid',
                'expiring_soon': 'warning',
                'expired': 'critical',
                'invalid': 'critical',
                'unreachable': 'warning'
            }.get(endpoint['status'], '')
            
            issues_text = ', '.join(endpoint['issues']) if endpoint['issues'] else 'None'
            
            html_content += f"""                <tr class="{status_class}">
                    <td>{endpoint['endpoint']}</td>
                    <td>{endpoint['hostname']}:{endpoint['port']}</td>
                    <td>{endpoint['status']}</td>
                    <td>{endpoint['days_until_expiry']}</td>
                    <td>{endpoint['last_check']}</td>
                    <td>{issues_text}</td>
                </tr>
            """        
        html_content += """            </table>
        </body>
        </html>
        """        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _generate_csv_report(self, report_data: Dict[str, Any], output_path: Path) -> None:
        """Generate CSV report"""        import csv
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'endpoint', 'hostname', 'port', 'status', 'alert_level',
                'days_until_expiry', 'last_check', 'issues', 'common_name'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for endpoint in report_data['endpoints']:
                writer.writerow({
                    'endpoint': endpoint['endpoint'],
                    'hostname': endpoint['hostname'],
                    'port': endpoint['port'],
                    'status': endpoint['status'],
                    'alert_level': endpoint['alert_level'],
                    'days_until_expiry': endpoint['days_until_expiry'],
                    'last_check': endpoint['last_check'],
                    'issues': '; '.join(endpoint['issues']),
                    'common_name': endpoint['certificate_info'].get('common_name', '')
                })


def create_certificate_monitor(config_path: Optional[Path] = None) -> CertificateMonitor:
    """    Factory function to create certificate monitor
    
    Args:
        config_path: Path to monitoring configuration
        
    Returns:
        Configured certificate monitor
    """    return CertificateMonitor(config_path)
