"""GDPR Service - Module RGPD
================================================================

Unified GDPR compliance service providing consent management, 
data export/deletion, and compliance audit functionality.

Features:
- Gestion consentements (Consent Management)
- Export/suppression données (Data Export/Deletion)
- Audit conformité (Compliance Audit)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import os
import importlib.util

# Import existing GDPR components
try:
    from backend.services.security.compliance.gdpr_manager import (
        GDPRComplianceManager, 
        GDPRRequestType, 
        ProcessingLawfulBasis,
        GDPRRequest,
        PersonalDataInventory,
        GDPRComplianceReport
    )
except ImportError as e:
    logging.warning(f"Could not import GDPRComplianceManager: {e}")
    GDPRComplianceManager = None

# Import consent management components with fallback
try:
    # Try importing directly from the module
    import sys
    consent_module_path = '/home/runner/work/Ainflue/Ainflue/business/legal/consent_management.py'
    if os.path.exists(consent_module_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("consent_management", consent_module_path)
        consent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(consent_module)
        
        ConsentManager = getattr(consent_module, 'ConsentManager', None)
        ConsentType = getattr(consent_module, 'ConsentType', None)
        ConsentStatus = getattr(consent_module, 'ConsentStatus', None)
        ProcessingPurpose = getattr(consent_module, 'ProcessingPurpose', None)
        ConsentRecord = getattr(consent_module, 'ConsentRecord', None)
    else:
        ConsentManager = None
        ConsentType = None
        ConsentStatus = None
        ProcessingPurpose = None
        ConsentRecord = None
except Exception as e:
    logging.warning(f"Could not import ConsentManager: {e}")
    ConsentManager = None
    ConsentType = None
    ConsentStatus = None
    ProcessingPurpose = None
    ConsentRecord = None

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."


class GDPRServiceError(Exception):
    """Base exception for GDPR service errors"""
    pass


class ConsentManagementError(GDPRServiceError):
    """Exception for consent management operations"""
    pass


class DataExportError(GDPRServiceError):
    """Exception for data export operations"""
    pass


class ComplianceAuditError(GDPRServiceError):
    """Exception for compliance audit operations"""
    pass


@dataclass
class GDPRServiceConfig:
    """Configuration for GDPR service"""
    encryption_enabled: bool = True
    data_retention_days: int = 2555  # 7 years default
    automated_erasure: bool = True
    audit_retention_days: int = 365
    consent_expiry_days: int = 730  # 2 years
    enable_compliance_monitoring: bool = True


@dataclass
class ConsentRequest:
    """Request for consent management"""
    user_id: str
    purposes: List[str]
    consent_values: Dict[str, bool]
    collection_context: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class DataExportRequest:
    """Request for data export"""
    user_id: str
    export_format: str = "json"  # json, csv, xml
    include_metadata: bool = True
    specific_data_types: Optional[List[str]] = None


@dataclass
class DataDeletionRequest:
    """Request for data deletion"""
    user_id: str
    deletion_reason: str
    specific_data_types: Optional[List[str]] = None
    retention_exceptions: Optional[List[str]] = None


@dataclass
class ComplianceAuditResult:
    """Result of compliance audit"""
    audit_id: str
    audit_date: datetime
    compliance_score: float
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    status: str


class GDPRService:
    """
    Unified GDPR Service providing comprehensive GDPR compliance functionality.
    
    This service consolidates consent management, data subject rights,
    and compliance auditing into a single interface.
    """
    
    def __init__(self, config: Optional[GDPRServiceConfig] = None):
        self.logger = logger
        self.config = config or GDPRServiceConfig()
        
        # Initialize underlying managers
        self._init_managers()
        
        # Service state
        self.service_id = str(uuid.uuid4())
        self.startup_time = datetime.now()
        
        self.logger.info(f"GDPR Service initialized with ID: {self.service_id}")
    
    def _init_managers(self):
        """Initialize underlying GDPR managers"""
        try:
            # Initialize GDPR compliance manager
            if GDPRComplianceManager:
                gdpr_config = {
                    'encryption_enabled': self.config.encryption_enabled,
                    'data_retention_days': self.config.data_retention_days,
                    'automated_erasure': self.config.automated_erasure
                }
                self.gdpr_manager = GDPRComplianceManager(gdpr_config)
            else:
                self.gdpr_manager = None
                self.logger.warning("GDPRComplianceManager not available")
            
            # Initialize consent manager
            if ConsentManager:
                consent_config = {
                    'default_consent_expiry': timedelta(days=self.config.consent_expiry_days),
                    'require_explicit_consent': True,
                    'enable_granular_consent': True
                }
                self.consent_manager = ConsentManager(consent_config)
            else:
                self.consent_manager = None
                self.logger.warning("ConsentManager not available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize GDPR managers: {e}")
            raise GDPRServiceError(f"Service initialization failed: {e}")
    
    # =================================================================
    # CONSENT MANAGEMENT (Gestion consentements)
    # =================================================================
    
    async def collect_consent(self, request: ConsentRequest) -> Dict[str, Any]:
        """
        Collect user consent for specified purposes.
        
        Args:
            request: ConsentRequest with user details and consent choices
            
        Returns:
            Dict containing consent records and status
            
        Raises:
            ConsentManagementError: If consent collection fails
        """
        try:
            if not self.consent_manager:
                raise ConsentManagementError("Consent manager not available")
            
            self.logger.info(f"Collecting consent for user {request.user_id}")
            
            # Convert purposes to enum if available
            purposes = []
            for purpose_str in request.purposes:
                try:
                    if hasattr(ProcessingPurpose, purpose_str.upper()):
                        purposes.append(getattr(ProcessingPurpose, purpose_str.upper()))
                    else:
                        # Fallback to string if enum not found
                        purposes.append(purpose_str)
                except:
                    purposes.append(purpose_str)
            
            # Collect consent through underlying manager
            consent_records = await self.consent_manager.collect_consent(
                user_id=request.user_id,
                purposes=purposes,
                consent_values=request.consent_values,
                collection_context=request.collection_context
            )
            
            # Format response
            result = {
                "status": "success",
                "user_id": request.user_id,
                "consent_records": [],
                "collection_timestamp": datetime.now().isoformat(),
                "service_id": self.service_id
            }
            
            # Process consent records
            for purpose, record in consent_records.items():
                result["consent_records"].append({
                    "purpose": str(purpose),
                    "consent_given": record.status == ConsentStatus.GIVEN,
                    "record_id": getattr(record, 'consent_id', getattr(record, 'id', 'unknown')),
                    "timestamp": record.given_at.isoformat() if record.given_at else None,
                    "expires_at": record.expires_at.isoformat() if record.expires_at else None
                })
            
            self.logger.info(f"Successfully collected consent for user {request.user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Consent collection failed: {e}")
            raise ConsentManagementError(f"Failed to collect consent: {e}")
    
    async def withdraw_consent(self, user_id: str, purposes: List[str], 
                             withdrawal_reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Withdraw user consent for specified purposes.
        
        Args:
            user_id: User identifier
            purposes: List of purposes to withdraw consent for
            withdrawal_reason: Optional reason for withdrawal
            
        Returns:
            Dict containing withdrawal confirmation and updated records
        """
        try:
            if not self.consent_manager:
                raise ConsentManagementError("Consent manager not available")
            
            self.logger.info(f"Withdrawing consent for user {user_id}")
            
            # Convert purposes to enum format
            purpose_enums = []
            for purpose_str in purposes:
                try:
                    if hasattr(ProcessingPurpose, purpose_str.upper()):
                        purpose_enums.append(getattr(ProcessingPurpose, purpose_str.upper()))
                    else:
                        purpose_enums.append(purpose_str)
                except:
                    purpose_enums.append(purpose_str)
            
            # Withdraw consent through underlying manager
            withdrawal_context = {
                "reason": withdrawal_reason,
                "withdrawal_method": "api",
                "service_id": self.service_id
            }
            
            withdrawal_records = await self.consent_manager.withdraw_consent(
                user_id=user_id,
                purposes=purpose_enums,
                withdrawal_method="api",
                withdrawal_context=withdrawal_context
            )
            
            # Format response
            result = {
                "status": "success",
                "user_id": user_id,
                "withdrawn_purposes": purposes,
                "withdrawal_records": [],
                "withdrawal_timestamp": datetime.now().isoformat(),
                "service_id": self.service_id
            }
            
            for record in withdrawal_records:
                result["withdrawal_records"].append({
                    "purpose": str(record.purpose),
                    "record_id": getattr(record, 'consent_id', getattr(record, 'id', 'unknown')),
                    "withdrawal_timestamp": record.withdrawn_at.isoformat() if hasattr(record, 'withdrawn_at') and record.withdrawn_at else None,
                    "status": record.status.value
                })
            
            self.logger.info(f"Successfully withdrew consent for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Consent withdrawal failed: {e}")
            raise ConsentManagementError(f"Failed to withdraw consent: {e}")
    
    async def check_consent_status(self, user_id: str, purpose: str) -> Dict[str, Any]:
        """
        Check current consent status for a user and purpose.
        
        Args:
            user_id: User identifier
            purpose: Processing purpose to check
            
        Returns:
            Dict containing consent status and details
        """
        try:
            if not self.consent_manager:
                raise ConsentManagementError("Consent manager not available")
            
            # Convert purpose to enum if available
            purpose_enum = purpose
            try:
                if hasattr(ProcessingPurpose, purpose.upper()):
                    purpose_enum = getattr(ProcessingPurpose, purpose.upper())
            except:
                pass
            
            # Check consent status
            consent_status = await self.consent_manager.check_consent(
                user_id=user_id,
                purpose=purpose_enum
            )
            
            return {
                "status": "success",
                "user_id": user_id,
                "purpose": purpose,
                "consent_given": consent_status,
                "check_timestamp": datetime.now().isoformat(),
                "service_id": self.service_id
            }
            
        except Exception as e:
            self.logger.error(f"Consent status check failed: {e}")
            raise ConsentManagementError(f"Failed to check consent status: {e}")
    
    # =================================================================
    # DATA EXPORT/DELETION (Export/suppression données)
    # =================================================================
    
    async def export_user_data(self, request: DataExportRequest) -> Dict[str, Any]:
        """
        Export all user data in specified format.
        
        Args:
            request: DataExportRequest with export specifications
            
        Returns:
            Dict containing exported data and metadata
        """
        try:
            if not self.gdpr_manager:
                raise DataExportError("GDPR manager not available")
            
            self.logger.info(f"Exporting data for user {request.user_id}")
            
            # Process data portability request through GDPR manager
            gdpr_request_details = {
                "export_format": request.export_format,
                "include_metadata": request.include_metadata,
                "specific_data_types": request.specific_data_types or []
            }
            
            request_id = await self.gdpr_manager.process_gdpr_request(
                user_id=int(request.user_id) if request.user_id.isdigit() else hash(request.user_id),
                request_type=GDPRRequestType.PORTABILITY,
                request_details=gdpr_request_details,
                requester_ip="127.0.0.1"  # Default for API requests
            )
            
            # Format response
            result = {
                "status": "success",
                "user_id": request.user_id,
                "export_format": request.export_format,
                "request_id": request_id,
                "export_timestamp": datetime.now().isoformat(),
                "estimated_completion": (datetime.now() + timedelta(hours=24)).isoformat(),
                "service_id": self.service_id,
                "download_instructions": "Data export will be available for download within 24 hours"
            }
            
            self.logger.info(f"Successfully initiated data export for user {request.user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Data export failed: {e}")
            raise DataExportError(f"Failed to export user data: {e}")
    
    async def delete_user_data(self, request: DataDeletionRequest) -> Dict[str, Any]:
        """
        Delete user data according to GDPR right to erasure.
        
        Args:
            request: DataDeletionRequest with deletion specifications
            
        Returns:
            Dict containing deletion confirmation and details
        """
        try:
            if not self.gdpr_manager:
                raise DataExportError("GDPR manager not available")
            
            self.logger.info(f"Deleting data for user {request.user_id}")
            
            # Process erasure request through GDPR manager
            gdpr_request_details = {
                "deletion_reason": request.deletion_reason,
                "specific_data_types": request.specific_data_types or [],
                "retention_exceptions": request.retention_exceptions or []
            }
            
            request_id = await self.gdpr_manager.process_gdpr_request(
                user_id=int(request.user_id) if request.user_id.isdigit() else hash(request.user_id),
                request_type=GDPRRequestType.ERASURE,
                request_details=gdpr_request_details,
                requester_ip="127.0.0.1"  # Default for API requests
            )
            
            # Format response
            result = {
                "status": "success",
                "user_id": request.user_id,
                "deletion_reason": request.deletion_reason,
                "request_id": request_id,
                "deletion_timestamp": datetime.now().isoformat(),
                "estimated_completion": (datetime.now() + timedelta(days=30)).isoformat(),
                "retention_exceptions": request.retention_exceptions or [],
                "service_id": self.service_id,
                "confirmation": "Data deletion request processed successfully"
            }
            
            self.logger.info(f"Successfully initiated data deletion for user {request.user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Data deletion failed: {e}")
            raise DataExportError(f"Failed to delete user data: {e}")
    
    async def get_gdpr_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get status of a GDPR request (export or deletion).
        
        Args:
            request_id: GDPR request identifier
            
        Returns:
            Dict containing request status and progress
        """
        try:
            if not self.gdpr_manager:
                raise DataExportError("GDPR manager not available")
            
            # Get request from GDPR manager
            gdpr_request = self.gdpr_manager.gdpr_requests.get(request_id)
            
            if not gdpr_request:
                return {
                    "status": "not_found",
                    "request_id": request_id,
                    "message": "Request not found",
                    "service_id": self.service_id
                }
            
            return {
                "status": "success",
                "request_id": request_id,
                "request_type": gdpr_request.request_type.value,
                "request_status": gdpr_request.status,
                "submitted_at": gdpr_request.submitted_at.isoformat(),
                "completed_at": gdpr_request.completed_at.isoformat() if gdpr_request.completed_at else None,
                "user_id": str(gdpr_request.user_id),
                "service_id": self.service_id
            }
            
        except Exception as e:
            self.logger.error(f"Request status check failed: {e}")
            raise DataExportError(f"Failed to get request status: {e}")
    
    # =================================================================
    # COMPLIANCE AUDIT (Audit conformité)
    # =================================================================
    
    async def run_compliance_audit(self) -> ComplianceAuditResult:
        """
        Run comprehensive GDPR compliance audit.
        
        Returns:
            ComplianceAuditResult with audit findings and recommendations
        """
        try:
            self.logger.info("Starting GDPR compliance audit")
            
            audit_id = str(uuid.uuid4())
            audit_date = datetime.now()
            findings = []
            recommendations = []
            
            # Check consent management compliance
            consent_audit = await self._audit_consent_management()
            findings.extend(consent_audit["findings"])
            recommendations.extend(consent_audit["recommendations"])
            
            # Check data retention compliance
            retention_audit = await self._audit_data_retention()
            findings.extend(retention_audit["findings"])
            recommendations.extend(retention_audit["recommendations"])
            
            # Check security compliance
            security_audit = await self._audit_security_compliance()
            findings.extend(security_audit["findings"])
            recommendations.extend(security_audit["recommendations"])
            
            # Calculate compliance score
            total_checks = len(findings)
            passed_checks = len([f for f in findings if f["status"] == "compliant"])
            compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 100
            
            # Determine overall status
            critical_issues = [f for f in findings if f["severity"] == "critical"]
            if critical_issues:
                status = "non_compliant"
            elif compliance_score >= 80:
                status = "compliant"
            else:
                status = "partially_compliant"
            
            result = ComplianceAuditResult(
                audit_id=audit_id,
                audit_date=audit_date,
                compliance_score=compliance_score,
                findings=findings,
                recommendations=recommendations,
                status=status
            )
            
            self.logger.info(f"Compliance audit completed with score: {compliance_score}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Compliance audit failed: {e}")
            raise ComplianceAuditError(f"Failed to run compliance audit: {e}")
    
    async def _audit_consent_management(self) -> Dict[str, Any]:
        """Audit consent management compliance"""
        findings = []
        recommendations = []
        
        # Check if consent manager is available
        if not self.consent_manager:
            findings.append({
                "category": "consent_management",
                "description": "Consent manager not available",
                "status": "non_compliant",
                "severity": "critical"
            })
            recommendations.append("Initialize and configure consent management system")
        else:
            findings.append({
                "category": "consent_management", 
                "description": "Consent management system operational",
                "status": "compliant",
                "severity": "info"
            })
        
        return {"findings": findings, "recommendations": recommendations}
    
    async def _audit_data_retention(self) -> Dict[str, Any]:
        """Audit data retention compliance"""
        findings = []
        recommendations = []
        
        # Check data retention configuration
        if self.config.data_retention_days > 0:
            findings.append({
                "category": "data_retention",
                "description": f"Data retention period configured: {self.config.data_retention_days} days",
                "status": "compliant",
                "severity": "info"
            })
        else:
            findings.append({
                "category": "data_retention",
                "description": "No data retention period configured",
                "status": "non_compliant", 
                "severity": "high"
            })
            recommendations.append("Configure appropriate data retention periods")
        
        # Check automated erasure
        if self.config.automated_erasure:
            findings.append({
                "category": "data_retention",
                "description": "Automated data erasure enabled",
                "status": "compliant",
                "severity": "info"
            })
        else:
            findings.append({
                "category": "data_retention",
                "description": "Automated data erasure not enabled",
                "status": "non_compliant",
                "severity": "medium"
            })
            recommendations.append("Enable automated data erasure for expired data")
        
        return {"findings": findings, "recommendations": recommendations}
    
    async def _audit_security_compliance(self) -> Dict[str, Any]:
        """Audit security compliance"""
        findings = []
        recommendations = []
        
        # Check encryption configuration
        if self.config.encryption_enabled:
            findings.append({
                "category": "security",
                "description": "Data encryption enabled",
                "status": "compliant",
                "severity": "info"
            })
        else:
            findings.append({
                "category": "security",
                "description": "Data encryption not enabled",
                "status": "non_compliant",
                "severity": "critical"
            })
            recommendations.append("Enable data encryption for personal data protection")
        
        return {"findings": findings, "recommendations": recommendations}
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """
        Get current compliance status report.
        
        Returns:
            Dict containing current compliance status and metrics
        """
        try:
            # Run fresh audit
            audit_result = await self.run_compliance_audit()
            
            # Compile comprehensive report
            report = {
                "service_info": {
                    "service_id": self.service_id,
                    "version": __version__,
                    "startup_time": self.startup_time.isoformat(),
                    "report_timestamp": datetime.now().isoformat()
                },
                "compliance_summary": {
                    "audit_id": audit_result.audit_id,
                    "compliance_score": audit_result.compliance_score,
                    "status": audit_result.status,
                    "total_findings": len(audit_result.findings),
                    "critical_issues": len([f for f in audit_result.findings if f["severity"] == "critical"]),
                    "recommendations_count": len(audit_result.recommendations)
                },
                "detailed_findings": audit_result.findings,
                "recommendations": audit_result.recommendations,
                "configuration": {
                    "encryption_enabled": self.config.encryption_enabled,
                    "data_retention_days": self.config.data_retention_days,
                    "automated_erasure": self.config.automated_erasure,
                    "consent_expiry_days": self.config.consent_expiry_days
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            raise ComplianceAuditError(f"Failed to generate compliance report: {e}")
    
    # =================================================================
    # SERVICE STATUS AND HEALTH
    # =================================================================
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and health information"""
        return {
            "service_id": self.service_id,
            "status": "operational",
            "version": __version__,
            "startup_time": self.startup_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.startup_time).total_seconds(),
            "components": {
                "gdpr_manager": "available" if self.gdpr_manager else "unavailable",
                "consent_manager": "available" if self.consent_manager else "unavailable"
            },
            "configuration": {
                "encryption_enabled": self.config.encryption_enabled,
                "automated_erasure": self.config.automated_erasure,
                "compliance_monitoring": self.config.enable_compliance_monitoring
            }
        }


# Convenience factory function
def create_gdpr_service(config: Optional[Dict[str, Any]] = None) -> GDPRService:
    """
    Factory function to create a GDPR service instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured GDPRService instance
    """
    service_config = GDPRServiceConfig()
    
    if config:
        for key, value in config.items():
            if hasattr(service_config, key):
                setattr(service_config, key, value)
    
    return GDPRService(service_config)


# Module exports
__all__ = [
    'GDPRService',
    'GDPRServiceConfig', 
    'ConsentRequest',
    'DataExportRequest',
    'DataDeletionRequest',
    'ComplianceAuditResult',
    'GDPRServiceError',
    'ConsentManagementError',
    'DataExportError',
    'ComplianceAuditError',
    'create_gdpr_service'
]