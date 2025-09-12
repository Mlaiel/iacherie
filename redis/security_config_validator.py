"""
Security Configuration Validator for Redis Enterprise
Sécurité Expert Implementation - Comprehensive Security Validation and Compliance

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import re
import ssl
import hashlib
import secrets
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import ipaddress
import redis.asyncio as redis
from config.core.redis import RedisSettings

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for different environments"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    """Compliance standards supported"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO27001 = "iso27001"
    NIST = "nist"

class SecurityThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityIssue:
    """Security validation issue"""
    severity: SecurityThreatLevel
    category: str
    description: str
    recommendation: str
    compliance_impact: List[ComplianceStandard] = field(default_factory=list)
    auto_fixable: bool = False
    fix_command: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    name: str
    description: str
    required_level: SecurityLevel
    compliance_standards: List[ComplianceStandard]
    validation_rules: List[str]
    auto_enforce: bool = False
    
@dataclass
class SecurityValidationResult:
    """Security validation result"""
    valid: bool
    security_level: SecurityLevel
    issues: List[SecurityIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compliance_status: Dict[ComplianceStandard, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    auto_fixes_available: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)

class SecurityConfigValidator:
    """
    Enterprise security configuration validator for Redis
    Sécurité Expert implementation with compliance and threat detection
    """
    
    def __init__(self, redis_settings: RedisSettings, security_level: SecurityLevel = SecurityLevel.STANDARD):
        self.redis_settings = redis_settings
        self.security_level = security_level
        self.redis_client: Optional[redis.Redis] = None
        
        # Security policies
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.compliance_requirements: Dict[ComplianceStandard, Dict[str, Any]] = {}
        
        # Validation caches
        self.validation_cache: Dict[str, SecurityValidationResult] = {}
        self.threat_intelligence: Dict[str, Any] = {}
        
        # Security configuration keys
        self.security_config_key = "ainflue:security:config"
        self.threat_log_key = "ainflue:security:threats"
        self.compliance_log_key = "ainflue:security:compliance"
        
        # Initialize security policies and compliance requirements
        self._initialize_security_policies()
        self._initialize_compliance_requirements()
    
    def _initialize_security_policies(self):
        """Initialize security policies for different categories"""
        try:
            # Authentication policies
            self.security_policies["auth_strong_passwords"] = SecurityPolicy(
                name="Strong Password Policy",
                description="Enforce strong password requirements",
                required_level=SecurityLevel.STANDARD,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.PCI_DSS],
                validation_rules=[
                    "password_min_length_12",
                    "password_complexity_high",
                    "password_no_dictionary_words"
                ]
            )
            
            self.security_policies["auth_mfa_required"] = SecurityPolicy(
                name="Multi-Factor Authentication",
                description="Require MFA for administrative access",
                required_level=SecurityLevel.HIGH,
                compliance_standards=[ComplianceStandard.PCI_DSS, ComplianceStandard.SOX],
                validation_rules=["mfa_enabled", "mfa_backup_codes"]
            )
            
            # Encryption policies
            self.security_policies["encryption_at_rest"] = SecurityPolicy(
                name="Encryption at Rest",
                description="Encrypt all data stored in Redis",
                required_level=SecurityLevel.HIGH,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
                validation_rules=["encryption_algorithm_aes256", "key_rotation_enabled"]
            )
            
            self.security_policies["encryption_in_transit"] = SecurityPolicy(
                name="Encryption in Transit",
                description="Encrypt all data in transit to/from Redis",
                required_level=SecurityLevel.STANDARD,
                compliance_standards=[ComplianceStandard.PCI_DSS, ComplianceStandard.GDPR],
                validation_rules=["tls_version_min_1_2", "certificate_validation"]
            )
            
            # Access control policies
            self.security_policies["access_control_acl"] = SecurityPolicy(
                name="Access Control Lists",
                description="Implement granular access control",
                required_level=SecurityLevel.STANDARD,
                compliance_standards=[ComplianceStandard.SOX, ComplianceStandard.ISO27001],
                validation_rules=["acl_enabled", "principle_of_least_privilege"]
            )
            
            # Network security policies
            self.security_policies["network_security"] = SecurityPolicy(
                name="Network Security",
                description="Secure network configuration",
                required_level=SecurityLevel.STANDARD,
                compliance_standards=[ComplianceStandard.NIST, ComplianceStandard.ISO27001],
                validation_rules=["firewall_configured", "ip_whitelist", "port_security"]
            )
            
            # Audit and monitoring policies
            self.security_policies["audit_logging"] = SecurityPolicy(
                name="Audit Logging",
                description="Comprehensive audit logging",
                required_level=SecurityLevel.STANDARD,
                compliance_standards=[ComplianceStandard.SOX, ComplianceStandard.GDPR],
                validation_rules=["audit_log_enabled", "log_retention_policy", "log_integrity"]
            )
            
        except Exception as e:
            logger.error(f"Error initializing security policies: {e}")
    
    def _initialize_compliance_requirements(self):
        """Initialize compliance requirements"""
        try:
            # GDPR requirements
            self.compliance_requirements[ComplianceStandard.GDPR] = {
                "data_encryption": True,
                "access_control": True,
                "audit_logging": True,
                "data_retention_policy": True,
                "right_to_be_forgotten": True,
                "data_portability": True,
                "privacy_by_design": True
            }
            
            # PCI DSS requirements
            self.compliance_requirements[ComplianceStandard.PCI_DSS] = {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_control": True,
                "multi_factor_auth": True,
                "security_monitoring": True,
                "vulnerability_management": True,
                "secure_network": True
            }
            
            # HIPAA requirements
            self.compliance_requirements[ComplianceStandard.HIPAA] = {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_control": True,
                "audit_logging": True,
                "minimum_necessary_access": True,
                "breach_notification": True,
                "risk_assessment": True
            }
            
            # SOX requirements
            self.compliance_requirements[ComplianceStandard.SOX] = {
                "access_control": True,
                "audit_logging": True,
                "change_management": True,
                "data_integrity": True,
                "segregation_of_duties": True
            }
            
            # ISO27001 requirements
            self.compliance_requirements[ComplianceStandard.ISO27001] = {
                "information_security_policy": True,
                "risk_management": True,
                "access_control": True,
                "cryptography": True,
                "security_monitoring": True,
                "incident_management": True,
                "business_continuity": True
            }
            
            # NIST requirements
            self.compliance_requirements[ComplianceStandard.NIST] = {
                "identify": True,
                "protect": True,
                "detect": True,
                "respond": True,
                "recover": True,
                "continuous_monitoring": True
            }
            
        except Exception as e:
            logger.error(f"Error initializing compliance requirements: {e}")
    
    async def initialize(self):
        """Initialize the security configuration validator"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_settings.redis_dsn,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.redis_settings.redis_max_connections
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load existing security configuration
            await self._load_security_configuration()
            
            logger.info(f"Security Configuration Validator initialized with level: {self.security_level.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Security Configuration Validator: {e}")
            raise
    
    async def validate_configuration(self, config: Dict[str, Any], 
                                   compliance_standards: Optional[List[ComplianceStandard]] = None) -> SecurityValidationResult:
        """Comprehensive security configuration validation"""
        try:
            result = SecurityValidationResult(
                valid=True,
                security_level=self.security_level
            )
            
            # Validate authentication configuration
            auth_issues = await self._validate_authentication(config)
            result.issues.extend(auth_issues)
            
            # Validate encryption configuration
            encryption_issues = await self._validate_encryption(config)
            result.issues.extend(encryption_issues)
            
            # Validate access control
            access_issues = await self._validate_access_control(config)
            result.issues.extend(access_issues)
            
            # Validate network security
            network_issues = await self._validate_network_security(config)
            result.issues.extend(network_issues)
            
            # Validate audit and monitoring
            audit_issues = await self._validate_audit_monitoring(config)
            result.issues.extend(audit_issues)
            
            # Check compliance requirements
            if compliance_standards:
                compliance_status = await self._check_compliance(config, compliance_standards)
                result.compliance_status.update(compliance_status)
            
            # Determine overall validity
            critical_issues = [issue for issue in result.issues if issue.severity == SecurityThreatLevel.CRITICAL]
            high_issues = [issue for issue in result.issues if issue.severity == SecurityThreatLevel.HIGH]
            
            result.valid = len(critical_issues) == 0 and len(high_issues) == 0
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(result.issues)
            result.auto_fixes_available = [issue.fix_command for issue in result.issues if issue.auto_fixable and issue.fix_command]
            
            # Cache result
            cache_key = hashlib.md5(str(config).encode()).hexdigest()
            self.validation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating security configuration: {e}")
            return SecurityValidationResult(
                valid=False,
                security_level=self.security_level,
                issues=[SecurityIssue(
                    severity=SecurityThreatLevel.CRITICAL,
                    category="validation_error",
                    description=f"Security validation failed: {str(e)}",
                    recommendation="Fix the validation error and retry"
                )]
            )
    
    async def _validate_authentication(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate authentication configuration"""
        issues = []
        
        try:
            # Check if authentication is enabled
            auth_enabled = config.get('security_settings', {}).get('auth_enabled', False)
            if not auth_enabled and self.security_level != SecurityLevel.BASIC:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="authentication",
                    description="Redis authentication is disabled",
                    recommendation="Enable Redis authentication with AUTH command",
                    compliance_impact=[ComplianceStandard.PCI_DSS, ComplianceStandard.GDPR],
                    auto_fixable=True,
                    fix_command="SET auth_enabled true"
                ))
            
            # Check password strength
            password = config.get('redis_config', {}).get('password')
            if password:
                password_issues = self._validate_password_strength(password)
                issues.extend(password_issues)
            elif auth_enabled:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.CRITICAL,
                    category="authentication",
                    description="Authentication enabled but no password configured",
                    recommendation="Configure a strong password for Redis authentication",
                    compliance_impact=[ComplianceStandard.PCI_DSS, ComplianceStandard.GDPR]
                ))
            
            # Check ACL configuration
            acl_enabled = config.get('security_settings', {}).get('acl_enabled', False)
            if not acl_enabled and self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="authorization",
                    description="Redis ACL is not enabled",
                    recommendation="Enable Redis ACL for granular access control",
                    compliance_impact=[ComplianceStandard.SOX, ComplianceStandard.ISO27001],
                    auto_fixable=True,
                    fix_command="SET acl_enabled true"
                ))
            
        except Exception as e:
            logger.error(f"Error validating authentication: {e}")
            issues.append(SecurityIssue(
                severity=SecurityThreatLevel.MEDIUM,
                category="validation_error",
                description=f"Authentication validation error: {str(e)}",
                recommendation="Review authentication configuration"
            ))
        
        return issues
    
    def _validate_password_strength(self, password: str) -> List[SecurityIssue]:
        """Validate password strength"""
        issues = []
        
        # Check minimum length
        if len(password) < 12:
            issues.append(SecurityIssue(
                severity=SecurityThreatLevel.HIGH,
                category="password_policy",
                description="Password is too short (minimum 12 characters)",
                recommendation="Use a password with at least 12 characters",
                compliance_impact=[ComplianceStandard.PCI_DSS]
            ))
        
        # Check complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if complexity_score < 3:
            issues.append(SecurityIssue(
                severity=SecurityThreatLevel.MEDIUM,
                category="password_policy",
                description="Password lacks complexity (missing uppercase, lowercase, digits, or special characters)",
                recommendation="Use a password with uppercase, lowercase, digits, and special characters",
                compliance_impact=[ComplianceStandard.PCI_DSS]
            ))
        
        # Check for common patterns
        common_patterns = [
            r'123456',
            r'password',
            r'admin',
            r'qwerty',
            r'abc123'
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="password_policy",
                    description="Password contains common patterns or dictionary words",
                    recommendation="Use a unique password without common patterns",
                    compliance_impact=[ComplianceStandard.PCI_DSS, ComplianceStandard.NIST]
                ))
                break
        
        return issues
    
    async def _validate_encryption(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate encryption configuration"""
        issues = []
        
        try:
            security_settings = config.get('security_settings', {})
            
            # Check encryption at rest
            encryption_at_rest = security_settings.get('encryption_at_rest', False)
            if not encryption_at_rest and self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="encryption",
                    description="Encryption at rest is not enabled",
                    recommendation="Enable encryption at rest for sensitive data protection",
                    compliance_impact=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA, ComplianceStandard.PCI_DSS],
                    auto_fixable=True,
                    fix_command="SET encryption_at_rest true"
                ))
            
            # Check SSL/TLS configuration
            ssl_enabled = config.get('redis_config', {}).get('ssl_enabled', False)
            if not ssl_enabled and self.security_level != SecurityLevel.BASIC:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="encryption",
                    description="SSL/TLS encryption in transit is not enabled",
                    recommendation="Enable SSL/TLS for secure communication",
                    compliance_impact=[ComplianceStandard.PCI_DSS, ComplianceStandard.GDPR],
                    auto_fixable=True,
                    fix_command="SET ssl_enabled true"
                ))
            
            # Validate SSL certificate configuration
            if ssl_enabled:
                ssl_issues = await self._validate_ssl_configuration(config)
                issues.extend(ssl_issues)
            
            # Check key rotation
            key_rotation = security_settings.get('key_rotation_enabled', False)
            if encryption_at_rest and not key_rotation:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="key_management",
                    description="Automatic key rotation is not enabled",
                    recommendation="Enable automatic key rotation for better security",
                    compliance_impact=[ComplianceStandard.PCI_DSS, ComplianceStandard.NIST]
                ))
            
        except Exception as e:
            logger.error(f"Error validating encryption: {e}")
            issues.append(SecurityIssue(
                severity=SecurityThreatLevel.MEDIUM,
                category="validation_error",
                description=f"Encryption validation error: {str(e)}",
                recommendation="Review encryption configuration"
            ))
        
        return issues
    
    async def _validate_ssl_configuration(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate SSL/TLS configuration"""
        issues = []
        
        try:
            redis_config = config.get('redis_config', {})
            
            # Check certificate paths
            cert_path = redis_config.get('ssl_cert_path')
            key_path = redis_config.get('ssl_key_path')
            ca_path = redis_config.get('ssl_ca_path')
            
            if not cert_path:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="ssl_configuration",
                    description="SSL certificate path not configured",
                    recommendation="Configure SSL certificate path"
                ))
            
            if not key_path:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="ssl_configuration", 
                    description="SSL private key path not configured",
                    recommendation="Configure SSL private key path"
                ))
            
            # Validate TLS version (if available in config)
            tls_version = redis_config.get('tls_version')
            if tls_version and float(tls_version) < 1.2:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="ssl_configuration",
                    description="TLS version is below recommended minimum (1.2)",
                    recommendation="Use TLS version 1.2 or higher",
                    compliance_impact=[ComplianceStandard.PCI_DSS]
                ))
            
        except Exception as e:
            logger.error(f"Error validating SSL configuration: {e}")
        
        return issues
    
    async def _validate_access_control(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate access control configuration"""
        issues = []
        
        try:
            security_settings = config.get('security_settings', {})
            
            # Check for default/weak configurations
            if config.get('redis_config', {}).get('port') == 6379:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.LOW,
                    category="access_control",
                    description="Using default Redis port (6379)",
                    recommendation="Consider using a non-standard port for better security",
                    auto_fixable=True,
                    fix_command="SET port 6380"
                ))
            
            # Check bind configuration
            bind_address = config.get('redis_config', {}).get('bind_address', '127.0.0.1')
            if bind_address == '0.0.0.0':
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="access_control",
                    description="Redis bound to all interfaces (0.0.0.0)",
                    recommendation="Bind Redis to specific interfaces only",
                    compliance_impact=[ComplianceStandard.NIST, ComplianceStandard.ISO27001]
                ))
            
            # Check rate limiting
            rate_limiting = security_settings.get('rate_limiting', False)
            if not rate_limiting and self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="access_control",
                    description="Rate limiting is not enabled",
                    recommendation="Enable rate limiting to prevent abuse",
                    auto_fixable=True,
                    fix_command="SET rate_limiting true"
                ))
            
        except Exception as e:
            logger.error(f"Error validating access control: {e}")
        
        return issues
    
    async def _validate_network_security(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate network security configuration"""
        issues = []
        
        try:
            # Check for IP whitelist
            allowed_ips = config.get('security_settings', {}).get('allowed_ips', [])
            if not allowed_ips and self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="network_security",
                    description="No IP whitelist configured",
                    recommendation="Configure IP whitelist for restricted access"
                ))
            
            # Validate IP addresses in whitelist
            for ip in allowed_ips:
                try:
                    ipaddress.ip_address(ip)
                except ValueError:
                    try:
                        ipaddress.ip_network(ip)
                    except ValueError:
                        issues.append(SecurityIssue(
                            severity=SecurityThreatLevel.LOW,
                            category="network_security",
                            description=f"Invalid IP address in whitelist: {ip}",
                            recommendation="Fix or remove invalid IP address from whitelist"
                        ))
            
            # Check for dangerous network configurations
            protected_mode = config.get('redis_config', {}).get('protected_mode', True)
            if not protected_mode:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.HIGH,
                    category="network_security",
                    description="Redis protected mode is disabled",
                    recommendation="Enable protected mode for additional security",
                    compliance_impact=[ComplianceStandard.NIST],
                    auto_fixable=True,
                    fix_command="SET protected_mode true"
                ))
            
        except Exception as e:
            logger.error(f"Error validating network security: {e}")
        
        return issues
    
    async def _validate_audit_monitoring(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate audit and monitoring configuration"""
        issues = []
        
        try:
            security_settings = config.get('security_settings', {})
            
            # Check audit logging
            audit_logging = security_settings.get('audit_logging', False)
            if not audit_logging and self.security_level in [SecurityLevel.STANDARD, SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="audit_monitoring",
                    description="Audit logging is not enabled",
                    recommendation="Enable audit logging for compliance and security monitoring",
                    compliance_impact=[ComplianceStandard.SOX, ComplianceStandard.GDPR],
                    auto_fixable=True,
                    fix_command="SET audit_logging true"
                ))
            
            # Check security monitoring
            security_monitoring = security_settings.get('security_monitoring', False)
            if not security_monitoring and self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.MEDIUM,
                    category="audit_monitoring",
                    description="Security monitoring is not enabled",
                    recommendation="Enable security monitoring for threat detection"
                ))
            
            # Check log retention policy
            log_retention_days = security_settings.get('log_retention_days', 0)
            if audit_logging and log_retention_days < 90:
                issues.append(SecurityIssue(
                    severity=SecurityThreatLevel.LOW,
                    category="audit_monitoring",
                    description="Log retention period is too short (recommended: 90+ days)",
                    recommendation="Set log retention to at least 90 days for compliance",
                    compliance_impact=[ComplianceStandard.SOX, ComplianceStandard.PCI_DSS]
                ))
            
        except Exception as e:
            logger.error(f"Error validating audit monitoring: {e}")
        
        return issues
    
    async def _check_compliance(self, config: Dict[str, Any], 
                              compliance_standards: List[ComplianceStandard]) -> Dict[ComplianceStandard, bool]:
        """Check compliance with specified standards"""
        compliance_status = {}
        
        try:
            for standard in compliance_standards:
                requirements = self.compliance_requirements.get(standard, {})
                compliance_status[standard] = True
                
                for requirement, required in requirements.items():
                    if required:
                        is_compliant = await self._check_compliance_requirement(config, requirement)
                        if not is_compliant:
                            compliance_status[standard] = False
                            break
                            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            # Default to non-compliant on error
            for standard in compliance_standards:
                compliance_status[standard] = False
        
        return compliance_status
    
    async def _check_compliance_requirement(self, config: Dict[str, Any], requirement: str) -> bool:
        """Check specific compliance requirement"""
        try:
            security_settings = config.get('security_settings', {})
            
            if requirement == "data_encryption":
                return security_settings.get('encryption_at_rest', False)
            elif requirement == "access_control":
                return security_settings.get('auth_enabled', False) or security_settings.get('acl_enabled', False)
            elif requirement == "audit_logging":
                return security_settings.get('audit_logging', False)
            elif requirement == "encryption_at_rest":
                return security_settings.get('encryption_at_rest', False)
            elif requirement == "encryption_in_transit":
                return config.get('redis_config', {}).get('ssl_enabled', False)
            elif requirement == "multi_factor_auth":
                return security_settings.get('mfa_enabled', False)
            elif requirement == "security_monitoring":
                return security_settings.get('security_monitoring', False)
            # Add more requirement checks as needed
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking compliance requirement {requirement}: {e}")
            return False
    
    async def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate security recommendations based on issues"""
        recommendations = []
        
        try:
            # Group issues by category
            issues_by_category = {}
            for issue in issues:
                if issue.category not in issues_by_category:
                    issues_by_category[issue.category] = []
                issues_by_category[issue.category].append(issue)
            
            # Generate category-specific recommendations
            for category, category_issues in issues_by_category.items():
                critical_count = len([i for i in category_issues if i.severity == SecurityThreatLevel.CRITICAL])
                high_count = len([i for i in category_issues if i.severity == SecurityThreatLevel.HIGH])
                
                if critical_count > 0:
                    recommendations.append(f"URGENT: Address {critical_count} critical {category} issues immediately")
                elif high_count > 0:
                    recommendations.append(f"HIGH PRIORITY: Address {high_count} high-severity {category} issues")
            
            # Add general recommendations based on security level
            if self.security_level == SecurityLevel.CRITICAL:
                recommendations.extend([
                    "Implement comprehensive security monitoring and alerting",
                    "Enable all available encryption options",
                    "Conduct regular security audits and penetration testing",
                    "Implement zero-trust network architecture"
                ])
            elif self.security_level == SecurityLevel.HIGH:
                recommendations.extend([
                    "Enable advanced authentication and authorization",
                    "Implement security monitoring and threat detection",
                    "Regular security assessments recommended"
                ])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Review security configuration and address identified issues")
        
        return recommendations
    
    async def auto_fix_issues(self, issues: List[SecurityIssue]) -> Dict[str, bool]:
        """Automatically fix security issues where possible"""
        fix_results = {}
        
        try:
            for issue in issues:
                if issue.auto_fixable and issue.fix_command:
                    try:
                        # Parse and execute fix command
                        if issue.fix_command.startswith("SET "):
                            key_value = issue.fix_command[4:].split(" ", 1)
                            if len(key_value) == 2:
                                key, value = key_value
                                # Convert string values to appropriate types
                                if value.lower() == 'true':
                                    value = True
                                elif value.lower() == 'false':
                                    value = False
                                elif value.isdigit():
                                    value = int(value)
                                
                                # Store the fix
                                await self.redis_client.hset(self.security_config_key, key, str(value))
                                fix_results[issue.description] = True
                                logger.info(f"Auto-fixed security issue: {issue.description}")
                            else:
                                fix_results[issue.description] = False
                        else:
                            fix_results[issue.description] = False
                    except Exception as e:
                        logger.error(f"Error auto-fixing issue '{issue.description}': {e}")
                        fix_results[issue.description] = False
                        
        except Exception as e:
            logger.error(f"Error in auto-fix process: {e}")
        
        return fix_results
    
    async def _load_security_configuration(self):
        """Load existing security configuration from Redis"""
        try:
            config_data = await self.redis_client.hgetall(self.security_config_key)
            if config_data:
                logger.info("Loaded existing security configuration from Redis")
                
        except Exception as e:
            logger.error(f"Error loading security configuration: {e}")
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get overall security status"""
        try:
            # Get recent validation results
            recent_validations = list(self.validation_cache.values())[-10:]  # Last 10 validations
            
            if not recent_validations:
                return {"status": "unknown", "message": "No recent validations"}
            
            # Calculate security metrics
            latest_validation = recent_validations[-1]
            total_issues = len(latest_validation.issues)
            critical_issues = len([i for i in latest_validation.issues if i.severity == SecurityThreatLevel.CRITICAL])
            high_issues = len([i for i in latest_validation.issues if i.severity == SecurityThreatLevel.HIGH])
            
            # Determine overall status
            if critical_issues > 0:
                status = "critical"
            elif high_issues > 0:
                status = "high_risk"
            elif total_issues > 0:
                status = "medium_risk"
            else:
                status = "secure"
            
            return {
                "status": status,
                "security_level": self.security_level.value,
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "last_validation": latest_validation.validation_timestamp.isoformat(),
                "compliance_status": latest_validation.compliance_status,
                "auto_fixes_available": len(latest_validation.auto_fixes_available)
            }
            
        except Exception as e:
            logger.error(f"Error getting security status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def shutdown(self):
        """Shutdown the security configuration validator"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Security Configuration Validator shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_security_config_validator(redis_settings: Optional[RedisSettings] = None, 
                                         security_level: SecurityLevel = SecurityLevel.STANDARD) -> SecurityConfigValidator:
    """Factory function to create and initialize SecurityConfigValidator"""
    if redis_settings is None:
        redis_settings = RedisSettings()
    
    validator = SecurityConfigValidator(redis_settings, security_level)
    await validator.initialize()
    return validator