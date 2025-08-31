"""Storage Security Configuration for IA-Influencer Agent Platform
===============================================================

Professional storage security configuration for enterprise-grade content protection.

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
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import hashlib
import secrets
from datetime import datetime, timedelta

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    AES_128_GCM = "AES-128-GCM"

class AccessLevel(Enum):
    """Storage access levels."""
    PUBLIC_READ = "public_read"
    AUTHENTICATED_READ = "authenticated_read"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"

class SecurityThreat(Enum):
    """Types of security threats to monitor."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALWARE_UPLOAD = "malware_upload"
    DDoS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"
    DATA_CORRUPTION = "data_corruption"

@dataclass
class EncryptionConfig:
    """Encryption configuration for storage security."""
    
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_size_bits: int = 256
    key_rotation_days: int = 90
    
    # Key management
    master_key: Optional[str] = None
    key_derivation_rounds: int = 100000
    use_hardware_security_module: bool = False
    
    # Encryption settings
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    encrypt_metadata: bool = True
    
    # File-level encryption
    encrypt_file_names: bool = False
    encrypt_directory_structure: bool = False
    
    def __post_init__(self):
        if self.master_key is None:
            self.master_key = os.getenv('STORAGE_MASTER_KEY', '')

@dataclass
class AccessControl:
    """Access control configuration for storage resources."""
    
    # Permission settings
    default_access_level: AccessLevel = AccessLevel.PRIVATE
    require_authentication: bool = True
    enable_role_based_access: bool = True
    
    # User permissions
    user_permissions: Dict[str, List[str]] = None
    role_permissions: Dict[str, List[str]] = None
    
    # IP restrictions
    allowed_ip_ranges: List[str] = None
    blocked_ip_ranges: List[str] = None
    
    # Time-based access
    enable_time_restrictions: bool = False
    access_time_windows: Dict[str, Dict[str, str]] = None
    
    # Session management
    max_session_duration_hours: int = 8
    require_session_refresh: bool = True
    enable_concurrent_session_limits: bool = True
    max_concurrent_sessions: int = 5
    
    def __post_init__(self):
        if self.user_permissions is None:
            self.user_permissions = {}
        
        if self.role_permissions is None:
            self.role_permissions = {
                'admin': ['read', 'write', 'delete', 'manage'],
                'user': ['read', 'write'],
                'viewer': ['read'],
                'service': ['read', 'write', 'create']
            }
        
        if self.allowed_ip_ranges is None:
            self.allowed_ip_ranges = []
        
        if self.blocked_ip_ranges is None:
            self.blocked_ip_ranges = []
        
        if self.access_time_windows is None:
            self.access_time_windows = {}

@dataclass
class ContentScanningConfig:
    """Content scanning and malware detection configuration."""
    
    # Virus scanning
    enable_virus_scanning: bool = True
    virus_scanner_engine: str = 'clamav'  # clamav, windows_defender, custom
    quarantine_infected_files: bool = True
    
    # Content validation
    enable_content_validation: bool = True
    validate_file_headers: bool = True
    check_file_signatures: bool = True
    
    # Malware detection
    enable_malware_detection: bool = True
    behavioral_analysis: bool = True
    sandbox_analysis: bool = True
    
    # Content filtering
    block_executable_files: bool = True
    blocked_file_extensions: Set[str] = None
    allowed_file_extensions: Set[str] = None
    
    # Deep content inspection
    enable_deep_inspection: bool = True
    extract_embedded_files: bool = True
    analyze_compressed_files: bool = True
    
    def __post_init__(self):
        if self.blocked_file_extensions is None:
            self.blocked_file_extensions = {
                'exe', 'bat', 'cmd', 'com', 'scr', 'vbs', 'js', 'jar',
                'msi', 'dll', 'sys', 'pif', 'application', 'gadget'
            }
        
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = {
                # Audio
                'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma',
                # Video
                'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv',
                # Images
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
                # Documents
                'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
                # Data
                'json', 'xml', 'csv', 'xlsx'
            }

@dataclass
class AuditingConfig:
    """Security auditing and logging configuration."""
    
    # Audit logging
    enable_audit_logging: bool = True
    log_level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file_access: bool = True
    log_permission_changes: bool = True
    log_authentication_events: bool = True
    
    # Activity monitoring
    monitor_user_activity: bool = True
    monitor_file_changes: bool = True
    monitor_access_patterns: bool = True
    
    # Compliance logging
    enable_compliance_logging: bool = True
    gdpr_logging: bool = True
    hipaa_logging: bool = False
    sox_logging: bool = False
    
    # Log retention
    log_retention_days: int = 365
    compress_old_logs: bool = True
    encrypt_log_files: bool = True
    
    # Real-time monitoring
    enable_real_time_alerts: bool = True
    alert_on_suspicious_activity: bool = True
    alert_on_policy_violations: bool = True

@dataclass
class StorageSecurityConfig:
    """
    Comprehensive storage security configuration for IA-Influencer Agent platform.
    Provides enterprise-grade security for content storage and access control.
    """
    
    # Security components
    encryption_config: EncryptionConfig = None
    access_control: AccessControl = None
    content_scanning: ContentScanningConfig = None
    auditing_config: AuditingConfig = None
    
    # Global security settings
    security_level: str = 'high'  # low, medium, high, maximum
    enable_zero_trust: bool = True
    require_multi_factor_auth: bool = True
    
    # Threat detection
    enable_threat_detection: bool = True
    monitored_threats: List[SecurityThreat] = None
    threat_response_automation: bool = True
    
    # Data protection
    enable_data_loss_prevention: bool = True
    classify_sensitive_data: bool = True
    redact_pii_data: bool = True
    
    # Compliance settings
    enable_compliance_mode: bool = True
    compliance_standards: List[str] = None
    
    # Incident response
    enable_incident_response: bool = True
    auto_quarantine_threats: bool = True
    notify_security_team: bool = True
    
    # Performance vs security balance
    security_performance_mode: str = 'balanced'  # fast, balanced, secure
    cache_security_decisions: bool = True
    security_cache_ttl_seconds: int = 300
    
    def __post_init__(self):
        """Initialize security configurations if not provided."""
        if self.encryption_config is None:
            self.encryption_config = EncryptionConfig()
        
        if self.access_control is None:
            self.access_control = AccessControl()
        
        if self.content_scanning is None:
            self.content_scanning = ContentScanningConfig()
        
        if self.auditing_config is None:
            self.auditing_config = AuditingConfig()
        
        if self.monitored_threats is None:
            self.monitored_threats = [
                SecurityThreat.UNAUTHORIZED_ACCESS,
                SecurityThreat.DATA_BREACH,
                SecurityThreat.MALWARE_UPLOAD,
                SecurityThreat.DDoS_ATTACK
            ]
        
        if self.compliance_standards is None:
            self.compliance_standards = ['GDPR', 'SOC2', 'ISO27001']
    
    def generate_encryption_key(self, key_type: str = 'file') -> str:
        """Generate a new encryption key for specified purpose."""
        key_lengths = {
            'file': 32,      # 256 bits for file encryption
            'database': 32,  # 256 bits for database encryption
            'session': 16,   # 128 bits for session keys
            'api': 32        # 256 bits for API keys
        }
        
        key_length = key_lengths.get(key_type, 32)
        return secrets.token_hex(key_length)
    
    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """Hash sensitive data with salt for secure storage."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            self.encryption_config.key_derivation_rounds
        )
        
        return f"{salt}${hash_value.hex()}"
    
    def validate_file_permissions(self, user_id: str, file_path: str, 
                                 operation: str) -> bool:
        """Validate user permissions for file operation."""
        # Check user-specific permissions
        user_perms = self.access_control.user_permissions.get(user_id, [])
        if operation in user_perms:
            return True
        
        # Check role-based permissions (would need user role lookup)
        # This is a simplified version
        return operation in ['read']  # Default to read-only
    
    def scan_file_for_threats(self, file_path: str) -> Dict[str, Any]:
        """Scan file for security threats (simulated)."""
        results = {
            'clean': True,
            'threats_found': [],
            'scan_time': datetime.now().isoformat(),
            'scanner_version': '1.0.0'
        }
        
        if not self.content_scanning.enable_virus_scanning:
            results['skipped'] = 'Virus scanning disabled'
            return results
        
        # File extension check
        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        
        if file_ext in self.content_scanning.blocked_file_extensions:
            results['clean'] = False
            results['threats_found'].append({
                'type': 'blocked_extension',
                'description': f'File extension {file_ext} is blocked',
                'severity': 'high'
            })
        
        # File size check (basic)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                results['threats_found'].append({
                    'type': 'suspicious_size',
                    'description': f'File size {file_size} bytes exceeds safe limits',
                    'severity': 'medium'
                })
        
        if results['threats_found']:
            results['clean'] = False
        
        return results
    
    def generate_access_token(self, user_id: str, permissions: List[str], 
                            duration_hours: int = 24) -> Dict[str, Any]:
        """Generate secure access token for storage operations."""
        token_data = {
            'user_id': user_id,
            'permissions': permissions,
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            'token_id': secrets.token_urlsafe(32)
        }
        
        # In production, this would be a signed JWT
        token = secrets.token_urlsafe(64)
        
        return {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': duration_hours * 3600,
            'permissions': permissions,
            'metadata': token_data
        }
    
    def validate_ip_access(self, client_ip: str) -> bool:
        """Validate IP address against allow/block lists."""
        # Check blocked IPs first
        for blocked_range in self.access_control.blocked_ip_ranges:
            if self._ip_in_range(client_ip, blocked_range):
                return False
        
        # If allow list is empty, allow all (except blocked)
        if not self.access_control.allowed_ip_ranges:
            return True
        
        # Check allowed IPs
        for allowed_range in self.access_control.allowed_ip_ranges:
            if self._ip_in_range(client_ip, allowed_range):
                return True
        
        return False
    
    def _ip_in_range(self, ip: str, ip_range: str) -> bool:
        """Check if IP is in specified range (simplified implementation)."""
        # This is a simplified implementation
        # In production, use proper IP address libraries
        if '/' in ip_range:
            # CIDR notation
            return ip.startswith(ip_range.split('/')[0][:-1])
        else:
            # Exact match
            return ip == ip_range
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event for auditing."""
        if not self.auditing_config.enable_audit_logging:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'security_level': self.security_level,
            'source': 'storage_security'
        }
        
        # In production, this would write to secure audit log
        print(f"SECURITY EVENT: {log_entry}")
    
    def get_security_policy_for_content(self, content_type: str) -> Dict[str, Any]:
        """Get security policy for specific content type."""
        policies = {
            'audio': {
                'access_level': AccessLevel.AUTHENTICATED_READ,
                'encryption_required': True,
                'virus_scan_required': True,
                'content_validation': True
            },
            'video': {
                'access_level': AccessLevel.AUTHENTICATED_READ,
                'encryption_required': True,
                'virus_scan_required': True,
                'content_validation': True
            },
            'image': {
                'access_level': AccessLevel.PUBLIC_READ,
                'encryption_required': False,
                'virus_scan_required': True,
                'content_validation': True
            },
            'document': {
                'access_level': AccessLevel.PRIVATE,
                'encryption_required': True,
                'virus_scan_required': True,
                'content_validation': True
            },
            'model': {
                'access_level': AccessLevel.RESTRICTED,
                'encryption_required': True,
                'virus_scan_required': True,
                'content_validation': True
            },
            'fingerprint': {
                'access_level': AccessLevel.CONFIDENTIAL,
                'encryption_required': True,
                'virus_scan_required': False,
                'content_validation': False
            }
        }
        
        return policies.get(content_type, policies['document'])  # Default to document policy
    
    def validate_configuration(self) -> bool:
        """Validate storage security configuration."""
        try:
            # Check encryption configuration
            if self.encryption_config.encrypt_at_rest and not self.encryption_config.master_key:
                print("Encryption at rest enabled but no master key provided")
                return False
            
            # Check access control
            if self.access_control.require_authentication and not self.access_control.enable_role_based_access:
                print("Authentication required but no role-based access configured")
                return False
            
            # Check content scanning
            if self.content_scanning.enable_virus_scanning and not self.content_scanning.virus_scanner_engine:
                print("Virus scanning enabled but no scanner engine configured")
                return False
            
            return True
        except Exception as e:
            print(f"Storage security configuration validation failed: {e}")
            return False
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export security configuration to JSON-serializable format."""
        return {
            'security_level': self.security_level,
            'enable_zero_trust': self.enable_zero_trust,
            'require_multi_factor_auth': self.require_multi_factor_auth,
            'enable_threat_detection': self.enable_threat_detection,
            'enable_data_loss_prevention': self.enable_data_loss_prevention,
            'enable_compliance_mode': self.enable_compliance_mode,
            'compliance_standards': self.compliance_standards,
            'encryption': {
                'algorithm': self.encryption_config.algorithm.value,
                'encrypt_at_rest': self.encryption_config.encrypt_at_rest,
                'encrypt_in_transit': self.encryption_config.encrypt_in_transit,
                'key_rotation_days': self.encryption_config.key_rotation_days
            },
            'access_control': {
                'default_access_level': self.access_control.default_access_level.value,
                'require_authentication': self.access_control.require_authentication,
                'enable_role_based_access': self.access_control.enable_role_based_access,
                'max_session_duration_hours': self.access_control.max_session_duration_hours
            },
            'content_scanning': {
                'enable_virus_scanning': self.content_scanning.enable_virus_scanning,
                'enable_content_validation': self.content_scanning.enable_content_validation,
                'enable_malware_detection': self.content_scanning.enable_malware_detection,
                'block_executable_files': self.content_scanning.block_executable_files
            },
            'auditing': {
                'enable_audit_logging': self.auditing_config.enable_audit_logging,
                'log_retention_days': self.auditing_config.log_retention_days,
                'enable_real_time_alerts': self.auditing_config.enable_real_time_alerts
            }
        }

# Global storage security configuration instance
storage_security_config = StorageSecurityConfig()
