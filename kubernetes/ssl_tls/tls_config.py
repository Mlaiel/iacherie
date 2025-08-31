"""
IA Influencer Agent - TLS Configuration Manager
Advanced TLS/SSL configuration and security settings

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
import json
import logging
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

import yaml
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class TLSVersion(Enum):
    """TLS version enumeration"""
    TLSv1_0 = "TLSv1.0"
    TLSv1_1 = "TLSv1.1"
    TLSv1_2 = "TLSv1.2"
    TLSv1_3 = "TLSv1.3"


class SecurityLevel(Enum):
    """TLS security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class CipherSuite(Enum):
    """TLS cipher suite categories"""
    MODERN = "modern"
    INTERMEDIATE = "intermediate"
    OLD = "old"
    CUSTOM = "custom"


@dataclass
class TLSConfig:
    """TLS configuration structure"""
    # Basic TLS settings
    min_tls_version: TLSVersion = TLSVersion.TLSv1_2
    max_tls_version: TLSVersion = TLSVersion.TLSv1_3
    cipher_suite: CipherSuite = CipherSuite.MODERN
    security_level: SecurityLevel = SecurityLevel.HIGH
    
    # Certificate settings
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    ca_bundle_path: Optional[str] = None
    cert_chain_path: Optional[str] = None
    
    # Security features
    enable_hsts: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True
    
    enable_ocsp_stapling: bool = True
    enable_session_tickets: bool = False
    enable_compression: bool = False
    enable_renegotiation: bool = False
    
    # DHE parameters
    dh_param_size: int = 2048
    dh_param_path: Optional[str] = None
    
    # Client certificate settings
    verify_client_cert: bool = False
    client_ca_path: Optional[str] = None
    client_cert_optional: bool = False
    
    # Custom cipher list
    custom_ciphers: Optional[List[str]] = None
    
    # Session settings
    session_cache: bool = True
    session_cache_size: int = 1024
    session_timeout: int = 300
    
    # Logging and monitoring
    enable_access_log: bool = True
    enable_error_log: bool = True
    log_level: str = "info"


@dataclass
class NginxTLSConfig:
    """Nginx-specific TLS configuration"""
    server_name: str
    listen_port: int = 443
    http_redirect: bool = True
    http_port: int = 80
    
    # SSL certificate configuration
    ssl_certificate: str
    ssl_certificate_key: str
    ssl_trusted_certificate: Optional[str] = None
    
    # TLS protocols and ciphers
    ssl_protocols: List[str] = None
    ssl_ciphers: str = None
    ssl_prefer_server_ciphers: bool = True
    
    # Security headers
    add_header_hsts: bool = True
    add_header_csp: bool = True
    add_header_xframe: bool = True
    add_header_xcontent: bool = True
    
    # Additional configurations
    ssl_session_cache: str = "shared:SSL:10m"
    ssl_session_timeout: str = "10m"
    ssl_stapling: bool = True
    ssl_stapling_verify: bool = True
    
    # Custom directives
    custom_directives: Optional[List[str]] = None


@dataclass
class ApacheTLSConfig:
    """Apache-specific TLS configuration"""
    server_name: str
    document_root: str
    virtual_host_port: int = 443
    
    # SSL certificate configuration
    ssl_certificate_file: str
    ssl_certificate_key_file: str
    ssl_certificate_chain_file: Optional[str] = None
    ssl_ca_certificate_file: Optional[str] = None
    
    # TLS protocols and ciphers
    ssl_protocol: List[str] = None
    ssl_cipher_suite: str = None
    ssl_honor_cipher_order: bool = True
    
    # Security configurations
    ssl_compression: bool = False
    ssl_session_tickets: bool = False
    ssl_use_stapling: bool = True
    
    # Headers
    header_always_set: List[str] = None
    
    # Custom directives
    custom_directives: Optional[List[str]] = None


class TLSConfigError(Exception):
    """TLS configuration exception"""
    pass


class TLSConfigManager:
    """
    Advanced TLS/SSL configuration management
    Supports multiple web servers and security standards
    """
    
    # Mozilla TLS configurations
    MOZILLA_MODERN_CIPHERS = [
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "DHE-RSA-AES128-GCM-SHA256",
        "DHE-RSA-AES256-GCM-SHA384"
    ]
    
    MOZILLA_INTERMEDIATE_CIPHERS = MOZILLA_MODERN_CIPHERS + [
        "ECDHE-ECDSA-AES128-SHA256",
        "ECDHE-RSA-AES128-SHA256",
        "ECDHE-ECDSA-AES128-SHA",
        "ECDHE-RSA-AES256-SHA384",
        "ECDHE-RSA-AES128-SHA",
        "ECDHE-ECDSA-AES256-SHA384",
        "ECDHE-ECDSA-AES256-SHA",
        "ECDHE-RSA-AES256-SHA",
        "DHE-RSA-AES128-SHA256",
        "DHE-RSA-AES128-SHA",
        "DHE-RSA-AES256-SHA256",
        "DHE-RSA-AES256-SHA"
    ]
    
    MOZILLA_OLD_CIPHERS = MOZILLA_INTERMEDIATE_CIPHERS + [
        "ECDHE-ECDSA-DES-CBC3-SHA",
        "ECDHE-RSA-DES-CBC3-SHA",
        "EDH-RSA-DES-CBC3-SHA",
        "AES128-GCM-SHA256",
        "AES256-GCM-SHA384",
        "AES128-SHA256",
        "AES256-SHA256",
        "AES128-SHA",
        "AES256-SHA",
        "DES-CBC3-SHA"
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize TLS configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.base_config = TLSConfig()
        
        # Load configuration if provided
        if config_path and config_path.exists():
            self.load_config(config_path)
        
        self.logger.info("TLS configuration manager initialized")
    
    def load_config(self, config_path: Path) -> TLSConfig:
        """
        Load TLS configuration from file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded TLS configuration
        """



        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Convert to TLSConfig object
            self.base_config = TLSConfig(**config_data)
            
            self.logger.info(f"Loaded TLS configuration from {config_path}")
            return self.base_config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise TLSConfigError(f"Configuration load failed: {e}")
    
    def save_config(self, config: TLSConfig, output_path: Path, format_type: str = "yaml") -> None:
        """
        Save TLS configuration to file
        
        Args:
            config: TLS configuration to save
            output_path: Output file path
            format_type: Output format (yaml/json)
        """



        try:
            config_dict = asdict(config)
            
            # Convert enum values to strings
            for key, value in config_dict.items():
                if isinstance(value, Enum):
                    config_dict[key] = value.value
            
            with open(output_path, 'w') as f:
                if format_type.lower() == "yaml":
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, default=str)
            
            self.logger.info(f"Saved TLS configuration to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {output_path}: {e}")
            raise TLSConfigError(f"Configuration save failed: {e}")
    
    def get_cipher_list(self, cipher_suite: CipherSuite, custom_ciphers: List[str] = None) -> str:
        """
        Get cipher list based on security level
        
        Args:
            cipher_suite: Cipher suite category
            custom_ciphers: Custom cipher list
            
        Returns:
            Formatted cipher string
        """
        if cipher_suite == CipherSuite.CUSTOM and custom_ciphers:
            return ":".join(custom_ciphers)
        elif cipher_suite == CipherSuite.MODERN:
            return ":".join(self.MOZILLA_MODERN_CIPHERS)
        elif cipher_suite == CipherSuite.INTERMEDIATE:
            return ":".join(self.MOZILLA_INTERMEDIATE_CIPHERS)
        elif cipher_suite == CipherSuite.OLD:
            return ":".join(self.MOZILLA_OLD_CIPHERS)
        else:
            return ":".join(self.MOZILLA_INTERMEDIATE_CIPHERS)
    
    def get_tls_protocols(self, config: TLSConfig) -> List[str]:
        """
        Get enabled TLS protocols based on configuration
        
        Args:
            config: TLS configuration
            
        Returns:
            List of enabled protocols
        """
        all_protocols = {
            TLSVersion.TLSv1_0: "TLSv1",
            TLSVersion.TLSv1_1: "TLSv1.1",
            TLSVersion.TLSv1_2: "TLSv1.2",
            TLSVersion.TLSv1_3: "TLSv1.3"
        }
        
        enabled_protocols = []
        protocol_order = [TLSVersion.TLSv1_0, TLSVersion.TLSv1_1, TLSVersion.TLSv1_2, TLSVersion.TLSv1_3]
        
        min_index = protocol_order.index(config.min_tls_version)
        max_index = protocol_order.index(config.max_tls_version)
        
        for i in range(min_index, max_index + 1):
            protocol_version = protocol_order[i]
            enabled_protocols.append(all_protocols[protocol_version])
        
        return enabled_protocols
    
    def generate_nginx_config(self, tls_config: TLSConfig, server_config: NginxTLSConfig) -> str:
        """
        Generate Nginx SSL/TLS configuration
        
        Args:
            tls_config: Base TLS configuration
            server_config: Nginx-specific configuration
            
        Returns:
            Nginx configuration string
        """



        try:
            # Get protocols and ciphers
            protocols = server_config.ssl_protocols or self.get_tls_protocols(tls_config)
            cipher_list = server_config.ssl_ciphers or self.get_cipher_list(
                tls_config.cipher_suite, 
                tls_config.custom_ciphers
            )
            
            config_lines = []
            
            # HTTP to HTTPS redirect
            if server_config.http_redirect:
                config_lines.extend([
                    f"server {{",
                    f"    listen {server_config.http_port};",
                    f"    server_name {server_config.server_name};",
                    f"    return 301 https://$server_name$request_uri;",
                    f"}}",
                    f""
                ])
            
            # HTTPS server block
            config_lines.extend([
                f"server {{",
                f"    listen {server_config.listen_port} ssl http2;",
                f"    server_name {server_config.server_name};",
                f"",
                f"    # SSL Certificate Configuration",
                f"    ssl_certificate {server_config.ssl_certificate};",
                f"    ssl_certificate_key {server_config.ssl_certificate_key};",
            ])
            
            if server_config.ssl_trusted_certificate:
                config_lines.append(f"    ssl_trusted_certificate {server_config.ssl_trusted_certificate};")
            
            config_lines.extend([
                f"",
                f"    # SSL/TLS Configuration",
                f"    ssl_protocols {' '.join(protocols)};",
                f"    ssl_ciphers '{cipher_list}';",
                f"    ssl_prefer_server_ciphers {'on' if server_config.ssl_prefer_server_ciphers else 'off'};",
                f"",
                f"    # SSL Session Configuration",
                f"    ssl_session_cache {server_config.ssl_session_cache};",
                f"    ssl_session_timeout {server_config.ssl_session_timeout};",
            ])
            
            # OCSP Stapling
            if server_config.ssl_stapling:
                config_lines.extend([
                    f"",
                    f"    # OCSP Stapling",
                    f"    ssl_stapling on;",
                    f"    ssl_stapling_verify {'on' if server_config.ssl_stapling_verify else 'off'};",
                ])
            
            # Security Headers
            if server_config.add_header_hsts and tls_config.enable_hsts:
                hsts_value = f"max-age={tls_config.hsts_max_age}"
                if tls_config.hsts_include_subdomains:
                    hsts_value += "; includeSubDomains"
                if tls_config.hsts_preload:
                    hsts_value += "; preload"
                
                config_lines.extend([
                    f"",
                    f"    # Security Headers",
                    f"    add_header Strict-Transport-Security \"{hsts_value}\" always;",
                ])
            
            if server_config.add_header_csp:
                config_lines.append(f"    add_header Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';\" always;")
            
            if server_config.add_header_xframe:
                config_lines.append(f"    add_header X-Frame-Options \"SAMEORIGIN\" always;")
            
            if server_config.add_header_xcontent:
                config_lines.append(f"    add_header X-Content-Type-Options \"nosniff\" always;")
            
            # Custom directives
            if server_config.custom_directives:
                config_lines.extend([f"", f"    # Custom Directives"])
                for directive in server_config.custom_directives:
                    config_lines.append(f"    {directive};")
            
            # Close server block
            config_lines.extend([
                f"",
                f"    # Application configuration goes here",
                f"    location / {{",
                f"        # Proxy pass or static content",
                f"    }}",
                f"}}"
            ])
            
            return "\n".join(config_lines)
            
        except Exception as e:
            self.logger.error(f"Failed to generate Nginx configuration: {e}")
            raise TLSConfigError(f"Nginx config generation failed: {e}")
    
    def generate_apache_config(self, tls_config: TLSConfig, server_config: ApacheTLSConfig) -> str:
        """
        Generate Apache SSL/TLS configuration
        
        Args:
            tls_config: Base TLS configuration
            server_config: Apache-specific configuration
            
        Returns:
            Apache configuration string
        """



        try:
            # Get protocols and ciphers
            protocols = server_config.ssl_protocol or self.get_tls_protocols(tls_config)
            cipher_list = server_config.ssl_cipher_suite or self.get_cipher_list(
                tls_config.cipher_suite,
                tls_config.custom_ciphers
            )
            
            config_lines = [
                f"<VirtualHost *:{server_config.virtual_host_port}>",
                f"    ServerName {server_config.server_name}",
                f"    DocumentRoot {server_config.document_root}",
                f"",
                f"    # SSL Engine",
                f"    SSLEngine on",
                f"",
                f"    # SSL Certificate Configuration",
                f"    SSLCertificateFile {server_config.ssl_certificate_file}",
                f"    SSLCertificateKeyFile {server_config.ssl_certificate_key_file}",
            ]
            
            if server_config.ssl_certificate_chain_file:
                config_lines.append(f"    SSLCertificateChainFile {server_config.ssl_certificate_chain_file}")
            
            if server_config.ssl_ca_certificate_file:
                config_lines.append(f"    SSLCACertificateFile {server_config.ssl_ca_certificate_file}")
            
            config_lines.extend([
                f"",
                f"    # SSL/TLS Configuration",
                f"    SSLProtocol {' '.join(protocols)}",
                f"    SSLCipherSuite {cipher_list}",
                f"    SSLHonorCipherOrder {'On' if server_config.ssl_honor_cipher_order else 'Off'}",
                f"",
                f"    # Security Configuration",
                f"    SSLCompression {'On' if server_config.ssl_compression else 'Off'}",
                f"    SSLSessionTickets {'On' if server_config.ssl_session_tickets else 'Off'}",
            ])
            
            # OCSP Stapling
            if server_config.ssl_use_stapling:
                config_lines.extend([
                    f"",
                    f"    # OCSP Stapling",
                    f"    SSLUseStapling On",
                    f"    SSLStaplingCache shmcb:/var/run/ocsp(128000)",
                ])
            
            # Security Headers
            headers = server_config.header_always_set or []
            
            if tls_config.enable_hsts:
                hsts_value = f"max-age={tls_config.hsts_max_age}"
                if tls_config.hsts_include_subdomains:
                    hsts_value += "; includeSubDomains"
                if tls_config.hsts_preload:
                    hsts_value += "; preload"
                headers.append(f"Header always set Strict-Transport-Security \"{hsts_value}\"")
            
            if headers:
                config_lines.extend([f"", f"    # Security Headers"])
                for header in headers:
                    config_lines.append(f"    {header}")
            
            # Custom directives
            if server_config.custom_directives:
                config_lines.extend([f"", f"    # Custom Directives"])
                for directive in server_config.custom_directives:
                    config_lines.append(f"    {directive}")
            
            config_lines.extend([
                f"",
                f"    # Application configuration goes here",
                f"</VirtualHost>"
            ])
            
            return "\n".join(config_lines)
            
        except Exception as e:
            self.logger.error(f"Failed to generate Apache configuration: {e}")
            raise TLSConfigError(f"Apache config generation failed: {e}")
    
    def validate_certificate_files(self, config: TLSConfig) -> Dict[str, bool]:
        """
        Validate certificate files exist and are readable
        
        Args:
            config: TLS configuration
            
        Returns:
            Dictionary of validation results
        """
        validation_results = {}
        
        files_to_check = {
            'certificate': config.certificate_path,
            'private_key': config.private_key_path,
            'ca_bundle': config.ca_bundle_path,
            'cert_chain': config.cert_chain_path,
            'dh_params': config.dh_param_path,
            'client_ca': config.client_ca_path
        }
        
        for file_type, file_path in files_to_check.items():
            if file_path:
                try:
                    path = Path(file_path)
                    validation_results[file_type] = path.exists() and path.is_file()
                    
                    if validation_results[file_type] and file_type in ['certificate', 'ca_bundle', 'cert_chain']:
                        # Validate certificate format
                        try:
                            with open(path, 'rb') as f:
                                cert_data = f.read()
                            x509.load_pem_x509_certificate(cert_data, default_backend())
                        except Exception:
                            validation_results[file_type] = False
                            self.logger.warning(f"Invalid certificate format: {file_path}")
                    
                except Exception as e:
                    validation_results[file_type] = False
                    self.logger.warning(f"Failed to validate {file_type} file {file_path}: {e}")
            else:
                validation_results[file_type] = None
        
        return validation_results
    
    def test_ssl_connection(self, hostname: str, port: int = 443, timeout: int = 10) -> Dict[str, Any]:
        """
        Test SSL/TLS connection to server
        
        Args:
            hostname: Server hostname
            port: Server port
            timeout: Connection timeout
            
        Returns:
            Connection test results
        """



        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate info
            with ssl.create_connection((hostname, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    protocol = ssock.version()
                    cipher = ssock.cipher()
                    
                    return {
                        'success': True,
                        'protocol': protocol,
                        'cipher_suite': cipher[0] if cipher else None,
                        'cipher_strength': cipher[2] if cipher else None,
                        'certificate': {
                            'subject': dict(x[0] for x in cert['subject']),
                            'issuer': dict(x[0] for x in cert['issuer']),
                            'version': cert['version'],
                            'serial_number': cert['serialNumber'],
                            'not_before': cert['notBefore'],
                            'not_after': cert['notAfter'],
                            'subject_alt_names': cert.get('subjectAltName', [])
                        }
                    }
        
        except Exception as e:
            self.logger.error(f"SSL connection test failed for {hostname}:{port}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_security_recommendations(self, config: TLSConfig) -> List[str]:
        """
        Get security recommendations for TLS configuration
        
        Args:
            config: TLS configuration to analyze
            
        Returns:
            List of security recommendations
        """
        recommendations = []
        
        # Check TLS version
        if config.min_tls_version in [TLSVersion.TLSv1_0, TLSVersion.TLSv1_1]:
            recommendations.append("Consider using TLS 1.2 or higher as minimum version")
        
        # Check cipher suite
        if config.cipher_suite == CipherSuite.OLD:
            recommendations.append("Consider upgrading to intermediate or modern cipher suite")
        
        # Check HSTS
        if not config.enable_hsts:
            recommendations.append("Enable HTTP Strict Transport Security (HSTS)")
        elif config.hsts_max_age < 31536000:
            recommendations.append("Consider increasing HSTS max-age to at least 1 year")
        
        # Check OCSP stapling
        if not config.enable_ocsp_stapling:
            recommendations.append("Enable OCSP stapling for better certificate validation")
        
        # Check session tickets
        if config.enable_session_tickets:
            recommendations.append("Consider disabling SSL session tickets for better security")
        
        # Check compression
        if config.enable_compression:
            recommendations.append("Disable SSL/TLS compression to prevent CRIME attacks")
        
        # Check DH parameters
        if config.dh_param_size < 2048:
            recommendations.append("Use at least 2048-bit DH parameters")
        
        return recommendations
    
    def generate_security_report(self, config: TLSConfig) -> Dict[str, Any]:
        """
        Generate comprehensive security report
        
        Args:
            config: TLS configuration to analyze
            
        Returns:
            Security analysis report
        """
        # Calculate security score
        score = 100
        issues = []
        
        # TLS version check
        if config.min_tls_version == TLSVersion.TLSv1_0:
            score -= 30
            issues.append("TLS 1.0 is deprecated and insecure")
        elif config.min_tls_version == TLSVersion.TLSv1_1:
            score -= 20
            issues.append("TLS 1.1 is deprecated")
        
        # Cipher suite check
        if config.cipher_suite == CipherSuite.OLD:
            score -= 15
            issues.append("Using old cipher suite with weak ciphers")
        elif config.cipher_suite == CipherSuite.INTERMEDIATE:
            score -= 5
            issues.append("Consider upgrading to modern cipher suite")
        
        # Security features
        if not config.enable_hsts:
            score -= 10
            issues.append("HSTS not enabled")
        
        if not config.enable_ocsp_stapling:
            score -= 5
            issues.append("OCSP stapling not enabled")
        
        if config.enable_session_tickets:
            score -= 5
            issues.append("Session tickets enabled (potential security risk)")
        
        if config.enable_compression:
            score -= 10
            issues.append("Compression enabled (CRIME vulnerability)")
        
        if config.dh_param_size < 2048:
            score -= 10
            issues.append("Weak DH parameters")
        
        # Determine security level
        if score >= 90:
            security_level = "Excellent"
        elif score >= 80:
            security_level = "Good"
        elif score >= 70:
            security_level = "Acceptable"
        elif score >= 60:
            security_level = "Needs Improvement"
        else:
            security_level = "Poor"
        
        return {
            'security_score': max(0, score),
            'security_level': security_level,
            'issues': issues,
            'recommendations': self.get_security_recommendations(config),
            'analysis_date': datetime.utcnow().isoformat(),
            'configuration_summary': {
                'min_tls_version': config.min_tls_version.value,
                'max_tls_version': config.max_tls_version.value,
                'cipher_suite': config.cipher_suite.value,
                'hsts_enabled': config.enable_hsts,
                'ocsp_stapling': config.enable_ocsp_stapling,
                'session_tickets': config.enable_session_tickets,
                'compression': config.enable_compression
            }
        }


def create_tls_config_manager(config_path: Optional[Path] = None) -> TLSConfigManager:
    """
    Factory function to create TLS configuration manager
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured TLS manager
    """



    return TLSConfigManager(config_path)
