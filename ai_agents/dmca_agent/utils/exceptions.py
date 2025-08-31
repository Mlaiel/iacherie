"""
DMCA Agent Exceptions - Enterprise Legal Protection System Error Handling
========================================================================

Comprehensive exception hierarchy for the DMCA Agent system providing detailed
error handling, logging, and recovery mechanisms for legal processing failures.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in immediate legal action.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels for DMCA operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categories of DMCA operation errors"""
    LEGAL_COMPLIANCE = "legal_compliance"
    TAKEDOWN_AUTOMATION = "takedown_automation"
    COPYRIGHT_VERIFICATION = "copyright_verification"
    DOCUMENT_GENERATION = "document_generation"
    PLATFORM_INTEGRATION = "platform_integration"
    DATABASE_ERROR = "database_error"
    SECURITY_VIOLATION = "security_violation"
    CONFIGURATION_ERROR = "configuration_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"

class DMCABaseException(Exception):
    """
    Base exception for all DMCA Agent operations
    
    Provides comprehensive error tracking, logging, and context information
    for legal processing operations.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC_ERROR,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        remediation_steps: Optional[List[str]] = None,
        legal_implications: Optional[str] = None
    ):
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.inner_exception = inner_exception
        self.remediation_steps = remediation_steps or []
        self.legal_implications = legal_implications
        self.timestamp = datetime.now()
        
        # Log the exception
        self._log_exception()
    
    def _log_exception(self):
        """Log the exception with appropriate level based on severity"""
        log_data = {
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "legal_implications": self.legal_implications
        }
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical("CRITICAL DMCA ERROR", extra=log_data)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error("HIGH SEVERITY DMCA ERROR", extra=log_data)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning("MEDIUM SEVERITY DMCA ERROR", extra=log_data)
        else:
            logger.info("LOW SEVERITY DMCA ERROR", extra=log_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""



        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "remediation_steps": self.remediation_steps,
            "legal_implications": self.legal_implications,
            "timestamp": self.timestamp.isoformat(),
            "inner_exception": str(self.inner_exception) if self.inner_exception else None
        }

# Legal Compliance Exceptions

class LegalComplianceException(DMCABaseException):
    """Base exception for legal compliance issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.LEGAL_COMPLIANCE)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class InvalidJurisdictionException(LegalComplianceException):
    """Exception for invalid or unsupported jurisdictions"""
    
    def __init__(self, jurisdiction: str, supported_jurisdictions: List[str], **kwargs):
        message = f"Jurisdiction '{jurisdiction}' is not supported. Supported: {', '.join(supported_jurisdictions)}"
        kwargs.setdefault('context', {}).update({
            'invalid_jurisdiction': jurisdiction,
            'supported_jurisdictions': supported_jurisdictions
        })
        kwargs.setdefault('remediation_steps', [
            f"Use one of the supported jurisdictions: {', '.join(supported_jurisdictions)}",
            "Contact system administrator to add new jurisdiction support",
            "Verify jurisdiction spelling and format"
        ])
        super().__init__(message, **kwargs)

class ComplianceScoreTooLowException(LegalComplianceException):
    """Exception when compliance score is below minimum threshold"""
    
    def __init__(self, score: float, minimum_required: float, missing_requirements: List[str], **kwargs):
        message = f"Compliance score {score:.2f} is below minimum required {minimum_required:.2f}"
        kwargs.setdefault('context', {}).update({
            'compliance_score': score,
            'minimum_required': minimum_required,
            'missing_requirements': missing_requirements
        })
        kwargs.setdefault('remediation_steps', [
            "Review and address missing compliance requirements",
            "Ensure all required legal documentation is provided",
            "Consider manual review for borderline cases"
        ])
        kwargs.setdefault('legal_implications', 
                         "Low compliance score may result in rejected takedown requests and legal exposure")
        super().__init__(message, **kwargs)

class MissingLegalRequirementsException(LegalComplianceException):
    """Exception for missing required legal documentation or information"""
    
    def __init__(self, missing_requirements: List[str], framework: str, **kwargs):
        message = f"Missing required legal requirements for {framework}: {', '.join(missing_requirements)}"
        kwargs.setdefault('context', {}).update({
            'missing_requirements': missing_requirements,
            'legal_framework': framework
        })
        kwargs.setdefault('remediation_steps', [
            f"Provide missing requirements: {', '.join(missing_requirements)}",
            "Review legal framework documentation for complete requirements",
            "Consult with legal counsel if requirements are unclear"
        ])
        super().__init__(message, **kwargs)

# Takedown Automation Exceptions

class TakedownException(DMCABaseException):
    """Base exception for takedown automation issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.TAKEDOWN_AUTOMATION)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class PlatformNotSupportedException(TakedownException):
    """Exception for unsupported platforms"""
    
    def __init__(self, platform: str, supported_platforms: List[str], **kwargs):
        message = f"Platform '{platform}' is not supported for automated takedowns"
        kwargs.setdefault('context', {}).update({
            'unsupported_platform': platform,
            'supported_platforms': supported_platforms
        })
        kwargs.setdefault('remediation_steps', [
            f"Use one of the supported platforms: {', '.join(supported_platforms)}",
            "Consider manual takedown process for unsupported platforms",
            "Contact development team to add platform support"
        ])
        super().__init__(message, **kwargs)

class TakedownFailedException(TakedownException):
    """Exception when takedown request fails"""
    
    def __init__(self, platform: str, reason: str, attempts: int, **kwargs):
        message = f"Takedown failed on {platform} after {attempts} attempts: {reason}"
        kwargs.setdefault('context', {}).update({
            'platform': platform,
            'failure_reason': reason,
            'attempts': attempts
        })
        kwargs.setdefault('remediation_steps', [
            "Review platform-specific requirements and retry",
            "Check API credentials and rate limits",
            "Consider manual takedown submission",
            "Escalate to legal team if automated methods fail"
        ])
        super().__init__(message, **kwargs)

class RateLimitExceededException(TakedownException):
    """Exception when platform rate limits are exceeded"""
    
    def __init__(self, platform: str, limit: int, reset_time: datetime, **kwargs):
        message = f"Rate limit exceeded for {platform}. Limit: {limit}, Reset: {reset_time}"
        kwargs.setdefault('context', {}).update({
            'platform': platform,
            'rate_limit': limit,
            'reset_time': reset_time.isoformat()
        })
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        kwargs.setdefault('remediation_steps', [
            f"Wait until rate limit resets at {reset_time}",
            "Implement request queuing and throttling",
            "Consider using multiple API keys if available",
            "Reduce request frequency for this platform"
        ])
        super().__init__(message, **kwargs)

class AuthenticationFailedException(TakedownException):
    """Exception when platform authentication fails"""
    
    def __init__(self, platform: str, auth_method: str, **kwargs):
        message = f"Authentication failed for {platform} using {auth_method}"
        kwargs.setdefault('context', {}).update({
            'platform': platform,
            'auth_method': auth_method
        })
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        kwargs.setdefault('remediation_steps', [
            "Verify API credentials are correct and active",
            "Check if API key or token has expired",
            "Ensure proper authentication method is configured",
            "Contact platform support if credentials are valid"
        ])
        super().__init__(message, **kwargs)

# Copyright Verification Exceptions

class CopyrightVerificationException(DMCABaseException):
    """Base exception for copyright verification issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.COPYRIGHT_VERIFICATION)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class InsufficientProofException(CopyrightVerificationException):
    """Exception when copyright proof is insufficient"""
    
    def __init__(self, verification_score: float, minimum_required: float, **kwargs):
        message = f"Copyright verification score {verification_score:.2f} is below required {minimum_required:.2f}"
        kwargs.setdefault('context', {}).update({
            'verification_score': verification_score,
            'minimum_required': minimum_required
        })
        kwargs.setdefault('remediation_steps', [
            "Provide additional proof of copyright ownership",
            "Include blockchain proof or digital signatures",
            "Submit official copyright registration documents",
            "Consider manual review by legal counsel"
        ])
        kwargs.setdefault('legal_implications',
                         "Insufficient proof may result in unsuccessful takedown requests and potential counter-claims")
        super().__init__(message, **kwargs)

class BlockchainVerificationFailedException(CopyrightVerificationException):
    """Exception when blockchain verification fails"""
    
    def __init__(self, blockchain_hash: str, network: str, **kwargs):
        message = f"Blockchain verification failed for hash {blockchain_hash} on {network}"
        kwargs.setdefault('context', {}).update({
            'blockchain_hash': blockchain_hash,
            'network': network
        })
        kwargs.setdefault('remediation_steps', [
            "Verify blockchain hash is correct and exists",
            "Check blockchain network connectivity",
            "Ensure sufficient confirmations have occurred",
            "Try alternative verification methods"
        ])
        super().__init__(message, **kwargs)

class ConflictingClaimsException(CopyrightVerificationException):
    """Exception when multiple conflicting copyright claims exist"""
    
    def __init__(self, content_id: str, conflicting_claims: List[Dict[str, Any]], **kwargs):
        message = f"Multiple conflicting copyright claims found for content {content_id}"
        kwargs.setdefault('context', {}).update({
            'content_id': content_id,
            'conflicting_claims': conflicting_claims,
            'claim_count': len(conflicting_claims)
        })
        kwargs.setdefault('severity', ErrorSeverity.CRITICAL)
        kwargs.setdefault('remediation_steps', [
            "Manual review required to resolve conflicting claims",
            "Contact all claimants to verify legitimate ownership",
            "Require additional proof from all parties",
            "Consider legal arbitration if conflicts cannot be resolved"
        ])
        kwargs.setdefault('legal_implications',
                         "Conflicting claims create significant legal risk and require careful resolution")
        super().__init__(message, **kwargs)

# Document Generation Exceptions

class DocumentGenerationException(DMCABaseException):
    """Base exception for document generation issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.DOCUMENT_GENERATION)
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)

class TemplateNotFoundException(DocumentGenerationException):
    """Exception when required template is not found"""
    
    def __init__(self, template_name: str, template_path: str, **kwargs):
        message = f"Template '{template_name}' not found at path: {template_path}"
        kwargs.setdefault('context', {}).update({
            'template_name': template_name,
            'template_path': template_path
        })
        kwargs.setdefault('remediation_steps', [
            f"Create template file at {template_path}",
            "Verify template directory configuration",
            "Check template naming conventions",
            "Use default template if available"
        ])
        super().__init__(message, **kwargs)

class InvalidTemplateException(DocumentGenerationException):
    """Exception when template contains errors or invalid syntax"""
    
    def __init__(self, template_name: str, validation_errors: List[str], **kwargs):
        message = f"Template '{template_name}' contains validation errors: {', '.join(validation_errors)}"
        kwargs.setdefault('context', {}).update({
            'template_name': template_name,
            'validation_errors': validation_errors
        })
        kwargs.setdefault('remediation_steps', [
            "Fix template syntax errors",
            "Validate template against schema",
            "Test template with sample data",
            "Review template documentation"
        ])
        super().__init__(message, **kwargs)

class DocumentValidationException(DocumentGenerationException):
    """Exception when generated document fails validation"""
    
    def __init__(self, document_type: str, validation_errors: List[str], **kwargs):
        message = f"Generated {document_type} document failed validation: {', '.join(validation_errors)}"
        kwargs.setdefault('context', {}).update({
            'document_type': document_type,
            'validation_errors': validation_errors
        })
        kwargs.setdefault('remediation_steps', [
            "Review document content and fix errors",
            "Verify all required fields are populated",
            "Check legal compliance requirements",
            "Regenerate document with corrected data"
        ])
        super().__init__(message, **kwargs)

# Platform Integration Exceptions

class PlatformIntegrationException(DMCABaseException):
    """Base exception for platform integration issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.PLATFORM_INTEGRATION)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class APIException(PlatformIntegrationException):
    """Exception for platform API errors"""
    
    def __init__(self, platform: str, endpoint: str, status_code: int, response: str, **kwargs):
        message = f"API error from {platform} at {endpoint}: {status_code} - {response}"
        kwargs.setdefault('context', {}).update({
            'platform': platform,
            'endpoint': endpoint,
            'status_code': status_code,
            'response': response
        })
        kwargs.setdefault('remediation_steps', [
            f"Check {platform} API documentation for error code {status_code}",
            "Verify API credentials and permissions",
            "Review request parameters and format",
            "Implement retry logic for transient errors"
        ])
        super().__init__(message, **kwargs)

class NetworkTimeoutException(PlatformIntegrationException):
    """Exception for network timeouts"""
    
    def __init__(self, platform: str, timeout_seconds: int, **kwargs):
        message = f"Network timeout connecting to {platform} after {timeout_seconds} seconds"
        kwargs.setdefault('context', {}).update({
            'platform': platform,
            'timeout_seconds': timeout_seconds
        })
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        kwargs.setdefault('remediation_steps', [
            "Increase timeout duration",
            "Check network connectivity to platform",
            "Implement retry with exponential backoff",
            "Verify platform service status"
        ])
        super().__init__(message, **kwargs)

# Security Exceptions

class SecurityException(DMCABaseException):
    """Base exception for security-related issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.SECURITY_VIOLATION)
        kwargs.setdefault('severity', ErrorSeverity.CRITICAL)
        super().__init__(message, **kwargs)

class InvalidSignatureException(SecurityException):
    """Exception for invalid digital signatures"""
    
    def __init__(self, signature_info: str, **kwargs):
        message = f"Invalid digital signature: {signature_info}"
        kwargs.setdefault('context', {}).update({
            'signature_info': signature_info
        })
        kwargs.setdefault('remediation_steps', [
            "Verify signature algorithm and parameters",
            "Check certificate validity and trust chain",
            "Regenerate signature with correct keys",
            "Validate signing process and integrity"
        ])
        kwargs.setdefault('legal_implications',
                         "Invalid signatures may compromise legal validity of documents")
        super().__init__(message, **kwargs)

class EncryptionException(SecurityException):
    """Exception for encryption/decryption failures"""
    
    def __init__(self, operation: str, algorithm: str, **kwargs):
        message = f"Encryption {operation} failed using {algorithm}"
        kwargs.setdefault('context', {}).update({
            'operation': operation,
            'algorithm': algorithm
        })
        kwargs.setdefault('remediation_steps', [
            "Verify encryption keys are valid and accessible",
            "Check algorithm configuration and parameters",
            "Ensure proper key management practices",
            "Review encryption implementation"
        ])
        super().__init__(message, **kwargs)

# Database Exceptions

class DatabaseException(DMCABaseException):
    """Base exception for database-related issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.DATABASE_ERROR)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class CaseNotFoundException(DatabaseException):
    """Exception when a case is not found in the database"""
    
    def __init__(self, case_id: str, **kwargs):
        message = f"Case not found: {case_id}"
        kwargs.setdefault('context', {}).update({
            'case_id': case_id
        })
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        kwargs.setdefault('remediation_steps', [
            "Verify case ID is correct",
            "Check if case was deleted or archived",
            "Ensure database connectivity",
            "Review case creation logs"
        ])
        super().__init__(message, **kwargs)

class DatabaseConnectionException(DatabaseException):
    """Exception for database connectivity issues"""
    
    def __init__(self, database_type: str, connection_string: str, **kwargs):
        # Don't log sensitive connection details
        safe_connection = connection_string.split('@')[-1] if '@' in connection_string else connection_string
        message = f"Failed to connect to {database_type} database: {safe_connection}"
        kwargs.setdefault('context', {}).update({
            'database_type': database_type,
            'connection_endpoint': safe_connection
        })
        kwargs.setdefault('severity', ErrorSeverity.CRITICAL)
        kwargs.setdefault('remediation_steps', [
            "Verify database server is running",
            "Check network connectivity to database",
            "Validate connection credentials",
            "Review firewall and security group settings"
        ])
        super().__init__(message, **kwargs)

# Configuration Exceptions

class ConfigurationException(DMCABaseException):
    """Base exception for configuration issues"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('category', ErrorCategory.CONFIGURATION_ERROR)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class MissingConfigurationException(ConfigurationException):
    """Exception for missing required configuration"""
    
    def __init__(self, config_key: str, config_section: str, **kwargs):
        message = f"Missing required configuration: {config_key} in section {config_section}"
        kwargs.setdefault('context', {}).update({
            'config_key': config_key,
            'config_section': config_section
        })
        kwargs.setdefault('remediation_steps', [
            f"Set configuration value for {config_key}",
            f"Review {config_section} configuration section",
            "Check environment variables and config files",
            "Consult configuration documentation"
        ])
        super().__init__(message, **kwargs)

class InvalidConfigurationException(ConfigurationException):
    """Exception for invalid configuration values"""
    
    def __init__(self, config_key: str, invalid_value: Any, expected_type: str, **kwargs):
        message = f"Invalid configuration for {config_key}: {invalid_value} (expected {expected_type})"
        kwargs.setdefault('context', {}).update({
            'config_key': config_key,
            'invalid_value': str(invalid_value),
            'expected_type': expected_type
        })
        kwargs.setdefault('remediation_steps', [
            f"Set {config_key} to a valid {expected_type} value",
            "Review configuration documentation",
            "Validate configuration against schema",
            "Check for typos in configuration values"
        ])
        super().__init__(message, **kwargs)

# Utility Functions

def handle_exception(
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = True
) -> DMCABaseException:
    """
    Convert generic exceptions to DMCA-specific exceptions
    
    Args:
        exc: Original exception
        context: Additional context information
        reraise: Whether to reraise the converted exception
        
    Returns:
        DMCABaseException: Converted exception
    """
    if isinstance(exc, DMCABaseException):
        dmca_exc = exc
    else:
        # Convert generic exception to DMCA exception
        dmca_exc = DMCABaseException(
            message=str(exc),
            context=context,
            inner_exception=exc,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.BUSINESS_LOGIC_ERROR
        )
    
    if reraise:
        raise dmca_exc
    
    return dmca_exc

def create_error_response(exc: Exception) -> Dict[str, Any]:
    """
    Create standardized error response from exception
    
    Args:
        exc: Exception to convert
        
    Returns:
        Dict containing error response
    """
    if isinstance(exc, DMCABaseException):
        return exc.to_dict()
    else:
        return {
            "error": True,
            "error_code": exc.__class__.__name__,
            "message": str(exc),
            "severity": ErrorSeverity.MEDIUM.value,
            "category": ErrorCategory.BUSINESS_LOGIC_ERROR.value,
            "timestamp": datetime.now().isoformat()
        }
