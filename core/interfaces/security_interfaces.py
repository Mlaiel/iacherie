"""Security interfaces for IA Influencer Agent.

Defines interfaces for security management, authentication,
authorization, encryption and audit functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
(c) 2025 - All rights reserved. Unauthorized use prohibited.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum


class SecurityLevel(Enum):
    """
Security clearance levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class AuthMethod(Enum):
    """Authentication methods."""

    PASSWORD = "password"
    TWO_FACTOR = "two_factor"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"
    SSO = "sso"


class EncryptionAlgorithm(Enum):
    """Encryption algorithms."""

    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ELLIPTIC_CURVE = "elliptic_curve"
    CHACHA20 = "chacha20"


class SecurityManagerInterface(ABC):
    """Core interface for security management."""
    
    @abstractmethod
    async def assess_security_risk(
        self,
        resource_id: str,
        access_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess security risk for resource access.
        
        Args:
            resource_id: Resource being accessed
            access_request: Details of access request
            
        Returns:
            Security risk assessment and recommendations
        """
        pass
    
    @abstractmethod
    async def implement_security_policy(
        self,
        policy_definition: Dict[str, Any],
        scope: List[str]
    ) -> str:
        """
Implement security policy across specified scope."""
        pass
    
    @abstractmethod
    async def conduct_security_scan(
        self,
        scan_target: str,
        scan_type: str
    ) -> Dict[str, Any]:
        """
Conduct comprehensive security scan."""
        pass
    
    @abstractmethod
    async def handle_security_incident(
        self,
        incident_data: Dict[str, Any],
        severity_level: str
    ) -> str:
        """
Handle and respond to security incidents."""
        pass
    
    @abstractmethod
    async def generate_security_report(
        self,
        report_scope: List[str],
        report_period: str
    ) -> Dict[str, Any]:
        """
Generate comprehensive security status report."""
        pass
    
    @abstractmethod
    async def update_security_configurations(
        self,
        configuration_updates: Dict[str, Any]
    ) -> bool:
        """
Update system security configurations."""
        pass


class AuthenticationInterface(ABC):
    """
Interface for user authentication management."""
    
    @abstractmethod
    async def authenticate_user(
        self,
        credentials: Dict[str, Any],
        auth_method: AuthMethod
    ) -> Dict[str, Any]:
        """
        Authenticate user with provided credentials.
        
        Args:
            credentials: User authentication credentials
            auth_method: Authentication method being used
            
        Returns:
            Authentication result and session information
        """
        pass
    
    @abstractmethod
    async def validate_session_token(
        self,
        token: str,
        required_permissions: List[str]
    ) -> Dict[str, Any]:
        """
Validate session token and check permissions."""
        pass
    
    @abstractmethod
    async def refresh_authentication_token(
        self,
        refresh_token: str,
        user_id: str
    ) -> Dict[str, str]:
        """
Refresh expired authentication token."""
        pass
    
    @abstractmethod
    async def revoke_user_session(
        self,
        session_id: str,
        revocation_reason: str
    ) -> bool:
        """
Revoke active user session."""
        pass
    
    @abstractmethod
    async def setup_multi_factor_auth(
        self,
        user_id: str,
        mfa_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Setup multi-factor authentication for user."""
        pass
    
    @abstractmethod
    async def verify_biometric_data(
        self,
        user_id: str,
        biometric_data: bytes,
        biometric_type: str
    ) -> bool:
        """
Verify biometric authentication data."""
        pass


class AuthorizationInterface(ABC):
    """
Interface for access control and authorization."""
    
    @abstractmethod
    async def check_resource_permissions(
        self,
        user_id: str,
        resource_id: str,
        requested_actions: List[str]
    ) -> Dict[str, bool]:
        """
        Check user permissions for resource actions.
        
        Args:
            user_id: User requesting access
            resource_id: Resource being accessed
            requested_actions: List of actions user wants to perform
            
        Returns:
            Permission status for each requested action
        """
        pass
    
    @abstractmethod
    async def grant_resource_permission(
        self,
        user_id: str,
        resource_id: str,
        permissions: List[str],
        grantor_id: str
    ) -> bool:
        """
Grant resource permissions to user."""
        pass
    
    @abstractmethod
    async def revoke_resource_permission(
        self,
        user_id: str,
        resource_id: str,
        permissions: List[str],
        revoker_id: str
    ) -> bool:
        """
Revoke resource permissions from user."""
        pass
    
    @abstractmethod
    async def create_role_definition(
        self,
        role_name: str,
        role_permissions: List[str],
        role_description: str
    ) -> str:
        """
Create new role with specified permissions."""
        pass
    
    @abstractmethod
    async def assign_user_role(
        self,
        user_id: str,
        role_id: str,
        assignment_scope: Optional[str] = None
    ) -> bool:
        """
Assign role to user within specified scope."""
        pass
    
    @abstractmethod
    async def evaluate_conditional_access(
        self,
        user_id: str,
        resource_id: str,
        access_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Evaluate conditional access policies."""
        pass


class EncryptionInterface(ABC):
    """
Interface for encryption and cryptographic operations."""
    
    @abstractmethod
    async def encrypt_sensitive_data(
        self,
        plaintext_data: Union[str, bytes],
        encryption_key: str,
        algorithm: EncryptionAlgorithm
    ) -> Dict[str, Any]:
        """
        Encrypt sensitive data using specified algorithm.
        
        Args:
            plaintext_data: Data to encrypt
            encryption_key: Encryption key identifier
            algorithm: Encryption algorithm to use
            
        Returns:
            Encrypted data and metadata
        """
        pass
    
    @abstractmethod
    async def decrypt_sensitive_data(
        self,
        encrypted_data: Dict[str, Any],
        decryption_key: str
    ) -> Union[str, bytes]:
        """
Decrypt previously encrypted sensitive data."""
        pass
    
    @abstractmethod
    async def generate_encryption_key(
        self,
        key_type: str,
        key_strength: int,
        key_purpose: str
    ) -> str:
        """
Generate new encryption key for specified purpose."""
        pass
    
    @abstractmethod
    async def rotate_encryption_keys(
        self,
        key_identifiers: List[str],
        rotation_policy: Dict[str, Any]
    ) -> Dict[str, str]:
        """
Rotate encryption keys according to policy."""
        pass
    
    @abstractmethod
    async def create_digital_signature(
        self,
        data_to_sign: Union[str, bytes],
        signing_key: str
    ) -> str:
        """
Create digital signature for data integrity."""
        pass
    
    @abstractmethod
    async def verify_digital_signature(
        self,
        signed_data: Union[str, bytes],
        signature: str,
        verification_key: str
    ) -> bool:
        """
Verify digital signature authenticity."""
        pass


class AuditInterface(ABC):
    """
Interface for security auditing and compliance."""
    
    @abstractmethod
    async def log_security_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        severity_level: str
    ) -> str:
        """
        Log security event for audit trail.
        
        Args:
            event_type: Type of security event
            event_data: Event details and context
            severity_level: Event severity (low, medium, high, critical)
            
        Returns:
            Audit log entry ID
        """
        pass
    
    @abstractmethod
    async def generate_audit_report(
        self,
        audit_scope: List[str],
        report_period: Tuple[datetime, datetime],
        report_format: str
    ) -> Dict[str, Any]:
        """
Generate comprehensive audit report."""
        pass
    
    @abstractmethod
    async def track_data_access(
        self,
        user_id: str,
        resource_id: str,
        access_details: Dict[str, Any]
    ) -> bool:
        """
Track data access for compliance monitoring."""
        pass
    
    @abstractmethod
    async def monitor_privilege_escalation(
        self,
        user_id: str,
        privilege_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
Monitor and analyze privilege escalation attempts."""
        pass
    
    @abstractmethod
    async def conduct_compliance_check(
        self,
        compliance_framework: str,
        check_scope: List[str]
    ) -> Dict[str, Any]:
        """
Conduct compliance check against specified framework."""
        pass
    
    @abstractmethod
    async def archive_audit_logs(
        self,
        retention_policy: Dict[str, Any],
        archive_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Archive audit logs according to retention policy."""
        pass
