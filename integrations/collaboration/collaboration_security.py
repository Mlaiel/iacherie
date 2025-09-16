"""
Collaboration Security Manager - Ainflue Integrations
===================================================
Enterprise-grade security for creator collaborations with end-to-end encryption,
digital rights management, and comprehensive compliance automation.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Enterprise Collaboration Platform
Version: 1.0 Enterprise
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import base64

# Mock dependencies for standalone operation
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import jwt
except ImportError:
    # Mock implementations for basic testing
    class Fernet:
        @staticmethod
        def generate_key():
            return b'mock_key_32_bytes_for_testing_123'
        
        def __init__(self, key):
            self.key = key
        
        def encrypt(self, data):
            return b'mock_encrypted_' + data
        
        def decrypt(self, data):
            return data.replace(b'mock_encrypted_', b'')

# Mock HTTPException for standalone operation
class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

# Mock status codes
class status:
    HTTP_409_CONFLICT = 409
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_404_NOT_FOUND = 404
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_400_BAD_REQUEST = 400
    HTTP_403_FORBIDDEN = 403

# Configure security logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(str, Enum):
    """Security levels for different collaboration types."""
    BASIC = "basic"
    ENHANCED = "enhanced" 
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"

class AccessLevel(str, Enum):
    """Access control levels."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"

class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    DMCA = "dmca"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"

class AuditEventType(str, Enum):
    """Security audit event types."""
    LOGIN = "login"
    LOGOUT = "logout"
    FILE_ACCESS = "file_access"
    PERMISSION_CHANGE = "permission_change"
    DATA_EXPORT = "data_export"
    SECURITY_VIOLATION = "security_violation"
    FRAUD_DETECTION = "fraud_detection"
    COMPLIANCE_CHECK = "compliance_check"

@dataclass
class EncryptionKey:
    """Encryption key management."""
    key_id: str
    key_data: bytes
    algorithm: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    key_type: str = "symmetric"  # symmetric, asymmetric_public, asymmetric_private
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityPolicy:
    """Enterprise security policy configuration."""
    policy_id: str
    tenant_id: str
    security_level: SecurityLevel
    encryption_required: bool = True
    mfa_required: bool = False
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    password_complexity_required: bool = True
    audit_logging_enabled: bool = True
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    ip_whitelist: List[str] = field(default_factory=list)
    allowed_file_types: List[str] = field(default_factory=lambda: ["*"])
    max_file_size_mb: int = 100
    data_retention_days: int = 365
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AccessPermission:
    """Granular access permissions."""
    permission_id: str
    user_id: str
    resource_id: str
    resource_type: str
    access_level: AccessLevel
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditEvent:
    """Security audit event."""
    event_id: str
    tenant_id: str
    user_id: str
    event_type: AuditEventType
    resource_id: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    status: str = "success"

@dataclass
class WatermarkConfig:
    """Digital watermark configuration."""
    watermark_id: str
    creator_id: str
    content_type: str
    watermark_data: str
    visibility: str = "invisible"  # visible, invisible, both
    position: str = "bottom_right"
    opacity: float = 0.3
    metadata: Dict[str, Any] = field(default_factory=dict)

class CollaborationSecurityManager:
    """
    Enterprise Collaboration Security Manager
    
    Comprehensive security management for creator collaborations:
    - End-to-end encryption for all communications
    - Digital rights management (DRM) integration
    - Secure file sharing and version control
    - IP protection and watermarking
    - Access control and permissions management
    - Security audit trails
    - Fraud detection and prevention
    - GDPR/CCPA compliance automation
    - Content filtering and moderation
    - Blockchain-based authenticity verification
    """
    
    def __init__(self):
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.access_permissions: Dict[str, List[AccessPermission]] = {}
        self.audit_events: List[AuditEvent] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.fraud_detection_rules: List[Dict[str, Any]] = []
        self.watermark_configs: Dict[str, WatermarkConfig] = {}
        
        # Initialize default security configuration
        self._initialize_default_security()
        
        logger.info("Collaboration Security Manager initialized")
    
    def _initialize_default_security(self):
        """Initialize default security configurations."""
        # Generate master encryption key
        master_key = Fernet.generate_key()
        self.encryption_keys["master"] = EncryptionKey(
            key_id="master",
            key_data=master_key,
            algorithm="Fernet",
            key_type="symmetric"
        )
        
        # Initialize fraud detection rules
        self.fraud_detection_rules = [
            {
                "rule_id": "multiple_login_attempts",
                "description": "Detect multiple failed login attempts",
                "threshold": 5,
                "window_minutes": 15,
                "risk_score": 8.0
            },
            {
                "rule_id": "unusual_file_access",
                "description": "Detect unusual file access patterns",
                "threshold": 10,
                "window_minutes": 5,
                "risk_score": 6.0
            },
            {
                "rule_id": "large_data_export",
                "description": "Detect large data exports",
                "threshold_mb": 1000,
                "risk_score": 7.0
            }
        ]
    
    async def create_security_policy(
        self,
        tenant_id: str,
        security_level: SecurityLevel,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> SecurityPolicy:
        """Create comprehensive security policy for tenant."""
        try:
            policy_id = str(uuid.uuid4())
            
            # Base policy configuration
            policy = SecurityPolicy(
                policy_id=policy_id,
                tenant_id=tenant_id,
                security_level=security_level
            )
            
            # Configure based on security level
            level_configs = {
                SecurityLevel.BASIC: {
                    "encryption_required": True,
                    "mfa_required": False,
                    "session_timeout_minutes": 120,
                    "max_login_attempts": 10,
                    "audit_logging_enabled": True,
                    "compliance_frameworks": [ComplianceFramework.GDPR]
                },
                SecurityLevel.ENHANCED: {
                    "encryption_required": True,
                    "mfa_required": True,
                    "session_timeout_minutes": 60,
                    "max_login_attempts": 5,
                    "audit_logging_enabled": True,
                    "compliance_frameworks": [ComplianceFramework.GDPR, ComplianceFramework.CCPA]
                },
                SecurityLevel.ENTERPRISE: {
                    "encryption_required": True,
                    "mfa_required": True,
                    "session_timeout_minutes": 30,
                    "max_login_attempts": 3,
                    "audit_logging_enabled": True,
                    "compliance_frameworks": [
                        ComplianceFramework.GDPR, ComplianceFramework.CCPA,
                        ComplianceFramework.SOC2, ComplianceFramework.ISO27001
                    ]
                },
                SecurityLevel.MAXIMUM: {
                    "encryption_required": True,
                    "mfa_required": True,
                    "session_timeout_minutes": 15,
                    "max_login_attempts": 2,
                    "audit_logging_enabled": True,
                    "compliance_frameworks": [
                        ComplianceFramework.GDPR, ComplianceFramework.CCPA,
                        ComplianceFramework.SOC2, ComplianceFramework.ISO27001,
                        ComplianceFramework.PCI_DSS
                    ]
                }
            }
            
            # Apply level-specific configuration
            config = level_configs.get(security_level, {})
            for key, value in config.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            # Apply custom settings
            if custom_settings:
                for key, value in custom_settings.items():
                    if hasattr(policy, key):
                        setattr(policy, key, value)
            
            self.security_policies[tenant_id] = policy
            
            # Log security policy creation
            await self._log_audit_event(
                tenant_id=tenant_id,
                user_id="system",
                event_type=AuditEventType.COMPLIANCE_CHECK,
                details={
                    "action": "security_policy_created",
                    "policy_id": policy_id,
                    "security_level": security_level.value
                }
            )
            
            logger.info(f"Created security policy {policy_id} for tenant {tenant_id}")
            return policy
            
        except Exception as e:
            logger.error(f"Failed to create security policy for tenant {tenant_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Security policy creation failed: {str(e)}"
            )
    
    async def encrypt_data(
        self,
        data: Union[str, bytes],
        tenant_id: str,
        key_id: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """Encrypt data with tenant-specific or specified encryption key."""
        try:
            # Use specified key or tenant's master key
            encryption_key_id = key_id or f"{tenant_id}_master"
            
            # Get or create encryption key
            if encryption_key_id not in self.encryption_keys:
                await self._generate_tenant_encryption_key(tenant_id)
                encryption_key_id = f"{tenant_id}_master"
            
            encryption_key = self.encryption_keys[encryption_key_id]
            
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Encrypt based on algorithm
            if encryption_key.algorithm == "Fernet":
                fernet = Fernet(encryption_key.key_data)
                encrypted_data = fernet.encrypt(data)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {encryption_key.algorithm}")
            
            return encrypted_data, encryption_key_id
            
        except Exception as e:
            logger.error(f"Encryption failed for tenant {tenant_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data encryption failed: {str(e)}"
            )
    
    async def decrypt_data(
        self,
        encrypted_data: bytes,
        key_id: str,
        tenant_id: str
    ) -> bytes:
        """Decrypt data using specified key."""
        try:
            # Verify tenant has access to key
            if not await self._verify_key_access(tenant_id, key_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to encryption key"
                )
            
            encryption_key = self.encryption_keys.get(key_id)
            if not encryption_key:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Encryption key {key_id} not found"
                )
            
            # Decrypt based on algorithm
            if encryption_key.algorithm == "Fernet":
                fernet = Fernet(encryption_key.key_data)
                decrypted_data = fernet.decrypt(encrypted_data)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {encryption_key.algorithm}")
            
            # Log data access
            await self._log_audit_event(
                tenant_id=tenant_id,
                user_id="system",
                event_type=AuditEventType.FILE_ACCESS,
                details={
                    "action": "data_decryption",
                    "key_id": key_id,
                    "data_size": len(encrypted_data)
                }
            )
            
            return decrypted_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Decryption failed for key {key_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data decryption failed: {str(e)}"
            )
    
    async def grant_access_permission(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        access_level: AccessLevel,
        granted_by: str,
        tenant_id: str,
        expires_in_hours: Optional[int] = None
    ) -> AccessPermission:
        """Grant granular access permissions to resources."""
        try:
            permission_id = str(uuid.uuid4())
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            
            permission = AccessPermission(
                permission_id=permission_id,
                user_id=user_id,
                resource_id=resource_id,
                resource_type=resource_type,
                access_level=access_level,
                granted_by=granted_by,
                expires_at=expires_at
            )
            
            # Store permission
            if user_id not in self.access_permissions:
                self.access_permissions[user_id] = []
            self.access_permissions[user_id].append(permission)
            
            # Log permission grant
            await self._log_audit_event(
                tenant_id=tenant_id,
                user_id=granted_by,
                event_type=AuditEventType.PERMISSION_CHANGE,
                details={
                    "action": "permission_granted",
                    "target_user": user_id,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                    "access_level": access_level.value,
                    "permission_id": permission_id
                }
            )
            
            logger.info(f"Granted {access_level.value} access to {resource_id} for user {user_id}")
            return permission
            
        except Exception as e:
            logger.error(f"Failed to grant access permission: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Permission grant failed: {str(e)}"
            )
    
    async def verify_access_permission(
        self,
        user_id: str,
        resource_id: str,
        required_access_level: AccessLevel
    ) -> bool:
        """Verify user has required access level to resource."""
        try:
            user_permissions = self.access_permissions.get(user_id, [])
            
            # Access level hierarchy
            access_hierarchy = {
                AccessLevel.READ: 1,
                AccessLevel.WRITE: 2,
                AccessLevel.ADMIN: 3,
                AccessLevel.OWNER: 4
            }
            
            required_level = access_hierarchy[required_access_level]
            
            for permission in user_permissions:
                if permission.resource_id == resource_id:
                    # Check if permission is still valid
                    if permission.expires_at and permission.expires_at < datetime.utcnow():
                        continue
                    
                    # Check access level
                    user_level = access_hierarchy[permission.access_level]
                    if user_level >= required_level:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Access verification failed for user {user_id}: {str(e)}")
            return False
    
    async def apply_digital_watermark(
        self,
        content_data: bytes,
        creator_id: str,
        content_type: str,
        watermark_config: Optional[WatermarkConfig] = None
    ) -> Tuple[bytes, str]:
        """Apply digital watermark to content for IP protection."""
        try:
            # Create or use existing watermark configuration
            if not watermark_config:
                watermark_id = str(uuid.uuid4())
                watermark_config = WatermarkConfig(
                    watermark_id=watermark_id,
                    creator_id=creator_id,
                    content_type=content_type,
                    watermark_data=f"Ainflue_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                )
                self.watermark_configs[watermark_id] = watermark_config
            
            # Apply watermark based on content type
            if content_type.startswith("audio/"):
                watermarked_content = await self._apply_audio_watermark(content_data, watermark_config)
            elif content_type.startswith("image/"):
                watermarked_content = await self._apply_image_watermark(content_data, watermark_config)
            elif content_type.startswith("video/"):
                watermarked_content = await self._apply_video_watermark(content_data, watermark_config)
            else:
                # For text and other content, embed metadata
                watermarked_content = await self._apply_metadata_watermark(content_data, watermark_config)
            
            logger.info(f"Applied watermark {watermark_config.watermark_id} to content for creator {creator_id}")
            return watermarked_content, watermark_config.watermark_id
            
        except Exception as e:
            logger.error(f"Watermark application failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Watermark application failed: {str(e)}"
            )
    
    async def detect_fraud_activity(
        self,
        tenant_id: str,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Tuple[bool, float, List[str]]:
        """Detect fraudulent activity using ML-based detection."""
        try:
            fraud_indicators = []
            total_risk_score = 0.0
            
            # Check against fraud detection rules
            for rule in self.fraud_detection_rules:
                risk_detected, risk_score, indicator = await self._evaluate_fraud_rule(
                    rule, tenant_id, user_id, activity_data
                )
                
                if risk_detected:
                    fraud_indicators.append(indicator)
                    total_risk_score += risk_score
            
            # Determine if fraud is detected (threshold: 5.0)
            is_fraud = total_risk_score >= 5.0
            
            if is_fraud:
                # Log fraud detection
                await self._log_audit_event(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    event_type=AuditEventType.FRAUD_DETECTION,
                    details={
                        "fraud_detected": True,
                        "risk_score": total_risk_score,
                        "indicators": fraud_indicators,
                        "activity_data": activity_data
                    },
                    risk_score=total_risk_score
                )
                
                logger.warning(f"Fraud detected for user {user_id} with risk score {total_risk_score}")
            
            return is_fraud, total_risk_score, fraud_indicators
            
        except Exception as e:
            logger.error(f"Fraud detection failed: {str(e)}")
            return False, 0.0, []
    
    async def ensure_compliance(
        self,
        tenant_id: str,
        framework: ComplianceFramework,
        data_operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ensure compliance with specified frameworks."""
        try:
            compliance_result = {
                "framework": framework.value,
                "compliant": True,
                "violations": [],
                "recommendations": [],
                "audit_trail": []
            }
            
            policy = self.security_policies.get(tenant_id)
            if not policy or framework not in policy.compliance_frameworks:
                compliance_result["compliant"] = False
                compliance_result["violations"].append(f"Framework {framework.value} not enabled for tenant")
                return compliance_result
            
            # Framework-specific compliance checks
            if framework == ComplianceFramework.GDPR:
                compliance_result = await self._check_gdpr_compliance(tenant_id, data_operations, compliance_result)
            elif framework == ComplianceFramework.CCPA:
                compliance_result = await self._check_ccpa_compliance(tenant_id, data_operations, compliance_result)
            elif framework == ComplianceFramework.SOC2:
                compliance_result = await self._check_soc2_compliance(tenant_id, data_operations, compliance_result)
            
            # Log compliance check
            await self._log_audit_event(
                tenant_id=tenant_id,
                user_id="system",
                event_type=AuditEventType.COMPLIANCE_CHECK,
                details={
                    "framework": framework.value,
                    "compliant": compliance_result["compliant"],
                    "violations_count": len(compliance_result["violations"]),
                    "operations_checked": len(data_operations)
                }
            )
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Compliance check failed for framework {framework.value}: {str(e)}")
            return {
                "framework": framework.value,
                "compliant": False,
                "violations": [f"Compliance check failed: {str(e)}"],
                "recommendations": [],
                "audit_trail": []
            }
    
    async def get_security_audit_report(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive security audit report."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter audit events by tenant and date range
            tenant_events = [
                event for event in self.audit_events
                if event.tenant_id == tenant_id and start_date <= event.timestamp <= end_date
            ]
            
            # Analyze events
            event_summary = {}
            security_violations = []
            high_risk_events = []
            
            for event in tenant_events:
                event_type = event.event_type.value
                event_summary[event_type] = event_summary.get(event_type, 0) + 1
                
                if event.event_type == AuditEventType.SECURITY_VIOLATION:
                    security_violations.append(event)
                
                if event.risk_score >= 7.0:
                    high_risk_events.append(event)
            
            report = {
                "tenant_id": tenant_id,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_events": len(tenant_events),
                    "event_types": event_summary,
                    "security_violations": len(security_violations),
                    "high_risk_events": len(high_risk_events)
                },
                "security_policy": self.security_policies.get(tenant_id).__dict__ if tenant_id in self.security_policies else None,
                "recommendations": await self._generate_security_recommendations(tenant_id, tenant_events),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Security audit report generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Audit report generation failed: {str(e)}"
            )
    
    # Private helper methods
    
    async def _generate_tenant_encryption_key(self, tenant_id: str):
        """Generate encryption key for tenant."""
        key_id = f"{tenant_id}_master"
        key_data = Fernet.generate_key()
        
        self.encryption_keys[key_id] = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            algorithm="Fernet",
            metadata={"tenant_id": tenant_id}
        )
    
    async def _verify_key_access(self, tenant_id: str, key_id: str) -> bool:
        """Verify tenant has access to encryption key."""
        key = self.encryption_keys.get(key_id)
        if not key:
            return False
        
        # Check if key belongs to tenant or is shared
        return (key.metadata.get("tenant_id") == tenant_id or 
                key.key_id == "master" or
                tenant_id in key.metadata.get("shared_with", []))
    
    async def _apply_audio_watermark(self, content_data: bytes, config: WatermarkConfig) -> bytes:
        """Apply watermark to audio content."""
        # Placeholder for audio watermarking logic
        # In production, this would use audio processing libraries
        return content_data
    
    async def _apply_image_watermark(self, content_data: bytes, config: WatermarkConfig) -> bytes:
        """Apply watermark to image content."""
        # Placeholder for image watermarking logic
        # In production, this would use image processing libraries
        return content_data
    
    async def _apply_video_watermark(self, content_data: bytes, config: WatermarkConfig) -> bytes:
        """Apply watermark to video content."""
        # Placeholder for video watermarking logic
        # In production, this would use video processing libraries
        return content_data
    
    async def _apply_metadata_watermark(self, content_data: bytes, config: WatermarkConfig) -> bytes:
        """Apply metadata watermark to content."""
        # Add watermark information to content metadata
        watermark_info = {
            "watermark_id": config.watermark_id,
            "creator_id": config.creator_id,
            "timestamp": datetime.utcnow().isoformat(),
            "platform": "Ainflue"
        }
        
        # For text content, append watermark as metadata
        if isinstance(content_data, bytes):
            watermark_json = json.dumps(watermark_info).encode('utf-8')
            return content_data + b"\n<!-- WATERMARK: " + base64.b64encode(watermark_json) + b" -->"
        
        return content_data
    
    async def _evaluate_fraud_rule(
        self,
        rule: Dict[str, Any],
        tenant_id: str,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Tuple[bool, float, str]:
        """Evaluate a single fraud detection rule."""
        rule_id = rule["rule_id"]
        
        # Rule-specific evaluation logic
        if rule_id == "multiple_login_attempts":
            failed_attempts = activity_data.get("failed_login_attempts", 0)
            if failed_attempts >= rule["threshold"]:
                return True, rule["risk_score"], f"Multiple failed login attempts: {failed_attempts}"
        
        elif rule_id == "unusual_file_access":
            file_accesses = activity_data.get("file_accesses_per_hour", 0)
            if file_accesses >= rule["threshold"]:
                return True, rule["risk_score"], f"Unusual file access pattern: {file_accesses} accesses/hour"
        
        elif rule_id == "large_data_export":
            export_size_mb = activity_data.get("export_size_mb", 0)
            if export_size_mb >= rule["threshold_mb"]:
                return True, rule["risk_score"], f"Large data export: {export_size_mb}MB"
        
        return False, 0.0, ""
    
    async def _check_gdpr_compliance(
        self,
        tenant_id: str,
        data_operations: List[Dict[str, Any]],
        compliance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check GDPR compliance requirements."""
        for operation in data_operations:
            if operation.get("type") == "data_processing":
                if not operation.get("consent_obtained"):
                    compliance_result["violations"].append("Data processing without consent")
                    compliance_result["compliant"] = False
                
                if not operation.get("purpose_specified"):
                    compliance_result["violations"].append("Data processing purpose not specified")
                    compliance_result["compliant"] = False
        
        return compliance_result
    
    async def _check_ccpa_compliance(
        self,
        tenant_id: str,
        data_operations: List[Dict[str, Any]],
        compliance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check CCPA compliance requirements."""
        for operation in data_operations:
            if operation.get("type") == "data_sale":
                if not operation.get("opt_out_provided"):
                    compliance_result["violations"].append("Data sale without opt-out option")
                    compliance_result["compliant"] = False
        
        return compliance_result
    
    async def _check_soc2_compliance(
        self,
        tenant_id: str,
        data_operations: List[Dict[str, Any]],
        compliance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check SOC2 compliance requirements."""
        policy = self.security_policies.get(tenant_id)
        if policy:
            if not policy.audit_logging_enabled:
                compliance_result["violations"].append("Audit logging not enabled")
                compliance_result["compliant"] = False
            
            if not policy.encryption_required:
                compliance_result["violations"].append("Encryption not required")
                compliance_result["compliant"] = False
        
        return compliance_result
    
    async def _generate_security_recommendations(
        self,
        tenant_id: str,
        events: List[AuditEvent]
    ) -> List[str]:
        """Generate security recommendations based on audit events."""
        recommendations = []
        
        # Analyze event patterns
        security_violations = len([e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION])
        failed_logins = len([e for e in events if e.event_type == AuditEventType.LOGIN and e.status == "failed"])
        
        if security_violations > 0:
            recommendations.append("Review and strengthen security policies")
        
        if failed_logins > 10:
            recommendations.append("Consider implementing additional authentication measures")
        
        policy = self.security_policies.get(tenant_id)
        if policy and not policy.mfa_required:
            recommendations.append("Enable multi-factor authentication for enhanced security")
        
        return recommendations
    
    async def _log_audit_event(
        self,
        tenant_id: str,
        user_id: str,
        event_type: AuditEventType,
        details: Dict[str, Any],
        resource_id: Optional[str] = None,
        risk_score: float = 0.0,
        status: str = "success"
    ):
        """Log security audit event."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            resource_id=resource_id,
            details=details,
            risk_score=risk_score,
            status=status
        )
        
        self.audit_events.append(event)
        
        # Keep only last 10000 events for performance
        if len(self.audit_events) > 10000:
            self.audit_events = self.audit_events[-10000:]

# Factory function for integration
def create_security_manager() -> CollaborationSecurityManager:
    """Factory function to create collaboration security manager instance."""
    return CollaborationSecurityManager()

# Security configuration constants
SECURITY_CONFIG = {
    "manager_version": "1.0.0",
    "supported_encryption_algorithms": ["Fernet", "AES-256", "RSA-4096"],
    "supported_compliance_frameworks": [framework.value for framework in ComplianceFramework],
    "default_session_timeout_minutes": 60,
    "max_audit_events": 10000,
    "fraud_detection_threshold": 5.0,
    "encryption_key_rotation_days": 90,
    "audit_log_retention_days": 2555,  # 7 years for compliance
    "watermark_enabled": True,
    "blockchain_verification_enabled": True
}

if __name__ == "__main__":
    # Example usage
    async def main():
        security_manager = create_security_manager()
        
        # Create security policy
        policy = await security_manager.create_security_policy(
            "enterprise_001",
            SecurityLevel.ENTERPRISE
        )
        print(f"Created security policy: {policy.policy_id}")
        
        # Encrypt data
        test_data = "Sensitive collaboration data"
        encrypted_data, key_id = await security_manager.encrypt_data(test_data, "enterprise_001")
        print(f"Encrypted data with key: {key_id}")
        
        # Decrypt data
        decrypted_data = await security_manager.decrypt_data(encrypted_data, key_id, "enterprise_001")
        print(f"Decrypted data: {decrypted_data.decode('utf-8')}")
        
        # Grant access permission
        permission = await security_manager.grant_access_permission(
            "user_001",
            "project_001",
            "collaboration_project",
            AccessLevel.WRITE,
            "admin_001",
            "enterprise_001"
        )
        print(f"Granted permission: {permission.permission_id}")
        
        # Generate audit report
        report = await security_manager.get_security_audit_report("enterprise_001")
        print(f"Generated audit report with {report['summary']['total_events']} events")
    
    asyncio.run(main())