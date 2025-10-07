"""
IA Chérie - Healthcare Service Factory & Entry Point
====================================================

Central service factory for healthcare integration components with HIPAA compliance.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
© 2025 Fahed Mlaiel (mlaiel@live.de) - All Rights Reserved
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import hashlib
import json
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class HealthcareServiceType(Enum):
    """Enumeration of healthcare service types."""
    EHR_INTEGRATION = "ehr_integration"
    TELEMEDICINE = "telemedicine"
    MEDICAL_AI = "medical_ai"
    COMPLIANCE = "compliance"
    ENCRYPTION = "encryption"
    AUDIT = "audit"
    CONSENT = "consent"
    TERMINOLOGY = "terminology"
    CLINICAL_DECISION = "clinical_decision"
    IMAGING = "imaging"
    LABORATORY = "laboratory"
    PHARMACY = "pharmacy"
    INSURANCE = "insurance"
    ANALYTICS = "analytics"


class ComplianceLevel(Enum):
    """Healthcare compliance levels."""
    HIPAA_COMPLIANT = "hipaa_compliant"
    GDPR_COMPLIANT = "gdpr_compliant"
    FULL_COMPLIANCE = "full_compliance"
    BASIC = "basic"


@dataclass
class HealthcareConfig:
    """Configuration for healthcare services."""
    
    # Service Configuration
    service_name: str
    service_type: HealthcareServiceType
    compliance_level: ComplianceLevel = ComplianceLevel.FULL_COMPLIANCE
    
    # Security Configuration
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    mfa_required: bool = True
    
    # Audit Configuration
    audit_logging: bool = True
    audit_retention_years: int = 6  # HIPAA requirement
    
    # Integration Configuration
    integration_endpoints: Dict[str, str] = field(default_factory=dict)
    api_keys: Dict[str, str] = field(default_factory=dict)
    oauth_config: Dict[str, Any] = field(default_factory=dict)
    
    # Feature Flags
    phi_de_identification: bool = True
    breach_notification: bool = True
    consent_management: bool = True
    clinical_decision_support: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'service_name': self.service_name,
            'service_type': self.service_type.value,
            'compliance_level': self.compliance_level.value,
            'encryption_enabled': self.encryption_enabled,
            'encryption_algorithm': self.encryption_algorithm,
            'mfa_required': self.mfa_required,
            'audit_logging': self.audit_logging,
            'audit_retention_years': self.audit_retention_years,
            'integration_endpoints': self.integration_endpoints,
            'phi_de_identification': self.phi_de_identification,
            'breach_notification': self.breach_notification,
            'consent_management': self.consent_management,
            'clinical_decision_support': self.clinical_decision_support,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
        }


class HealthcareServiceFactory:
    """
    Factory for creating and managing healthcare services.
    
    Provides centralized service creation with:
    - HIPAA/GDPR compliance validation
    - Security configuration
    - Audit logging
    - Service lifecycle management
    
    Example:
        >>> factory = HealthcareServiceFactory()
        >>> config = HealthcareConfig(
        ...     service_name="Epic_EHR",
        ...     service_type=HealthcareServiceType.EHR_INTEGRATION
        ... )
        >>> ehr_service = await factory.create_service(config)
    """
    
    def __init__(self, global_config: Optional[Dict[str, Any]] = None):
        """
        Initialize healthcare service factory.
        
        Args:
            global_config: Optional global configuration for all services
        """
        self.global_config = global_config or {}
        self.services: Dict[str, Any] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        logger.info("Healthcare Service Factory initialized")
        self._log_audit_event('factory_initialized', {'timestamp': datetime.utcnow().isoformat()})
    
    async def create_service(
        self,
        config: HealthcareConfig
    ) -> Dict[str, Any]:
        """
        Create a healthcare service with specified configuration.
        
        Args:
            config: Service configuration
            
        Returns:
            Dict containing service instance and metadata
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If service creation fails
        """
        try:
            # Validate configuration
            await self._validate_config(config)
            
            # Check compliance requirements
            await self._validate_compliance(config)
            
            # Create service based on type
            service = await self._create_service_instance(config)
            
            # Register service
            service_id = self._generate_service_id(config)
            self.services[service_id] = {
                'service': service,
                'config': config,
                'created_at': datetime.utcnow(),
                'status': 'active'
            }
            
            # Log creation
            self._log_audit_event('service_created', {
                'service_id': service_id,
                'service_type': config.service_type.value,
                'compliance_level': config.compliance_level.value
            })
            
            logger.info(f"Healthcare service created: {service_id}")
            
            return {
                'service_id': service_id,
                'service': service,
                'config': config.to_dict(),
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Failed to create healthcare service: {str(e)}")
            self._log_audit_event('service_creation_failed', {
                'error': str(e),
                'service_name': config.service_name
            })
            raise RuntimeError(f"Service creation failed: {str(e)}")
    
    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an existing service by ID.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Service dict if found, None otherwise
        """
        service_data = self.services.get(service_id)
        if service_data:
            self._log_audit_event('service_accessed', {
                'service_id': service_id,
                'timestamp': datetime.utcnow().isoformat()
            })
        return service_data
    
    async def destroy_service(self, service_id: str) -> bool:
        """
        Destroy a healthcare service and cleanup resources.
        
        Args:
            service_id: Service identifier
            
        Returns:
            True if service was destroyed successfully
        """
        if service_id in self.services:
            service_data = self.services[service_id]
            
            # Perform cleanup
            await self._cleanup_service(service_data)
            
            # Remove service
            del self.services[service_id]
            
            # Log destruction
            self._log_audit_event('service_destroyed', {
                'service_id': service_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Healthcare service destroyed: {service_id}")
            return True
        
        return False
    
    async def list_services(
        self,
        service_type: Optional[HealthcareServiceType] = None
    ) -> List[Dict[str, Any]]:
        """
        List all active healthcare services.
        
        Args:
            service_type: Optional filter by service type
            
        Returns:
            List of service metadata dicts
        """
        services = []
        for service_id, service_data in self.services.items():
            if service_type is None or service_data['config'].service_type == service_type:
                services.append({
                    'service_id': service_id,
                    'service_type': service_data['config'].service_type.value,
                    'service_name': service_data['config'].service_name,
                    'created_at': service_data['created_at'].isoformat(),
                    'status': service_data['status']
                })
        
        return services
    
    async def validate_hipaa_compliance(self, service_id: str) -> Dict[str, Any]:
        """
        Validate HIPAA compliance for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Dict containing compliance validation results
        """
        service_data = self.services.get(service_id)
        if not service_data:
            raise ValueError(f"Service not found: {service_id}")
        
        config = service_data['config']
        
        validation_results = {
            'service_id': service_id,
            'compliance_checks': {
                'encryption_enabled': config.encryption_enabled,
                'encryption_algorithm': config.encryption_algorithm == 'AES-256-GCM',
                'mfa_required': config.mfa_required,
                'audit_logging': config.audit_logging,
                'audit_retention': config.audit_retention_years >= 6,
                'phi_de_identification': config.phi_de_identification,
                'breach_notification': config.breach_notification,
                'consent_management': config.consent_management,
            },
            'overall_compliant': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check if all requirements are met
        validation_results['overall_compliant'] = all(
            validation_results['compliance_checks'].values()
        )
        
        self._log_audit_event('compliance_validated', validation_results)
        
        return validation_results
    
    async def get_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit log entries.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            event_type: Optional event type filter
            
        Returns:
            List of audit log entries
        """
        filtered_log = self.audit_log
        
        if start_date:
            filtered_log = [
                entry for entry in filtered_log
                if datetime.fromisoformat(entry['timestamp']) >= start_date
            ]
        
        if end_date:
            filtered_log = [
                entry for entry in filtered_log
                if datetime.fromisoformat(entry['timestamp']) <= end_date
            ]
        
        if event_type:
            filtered_log = [
                entry for entry in filtered_log
                if entry['event_type'] == event_type
            ]
        
        return filtered_log
    
    # Private helper methods
    
    async def _validate_config(self, config: HealthcareConfig) -> None:
        """Validate service configuration."""
        if not config.service_name:
            raise ValueError("Service name is required")
        
        if config.compliance_level == ComplianceLevel.FULL_COMPLIANCE:
            if not config.encryption_enabled:
                raise ValueError("Encryption required for full compliance")
            if not config.audit_logging:
                raise ValueError("Audit logging required for full compliance")
            if config.audit_retention_years < 6:
                raise ValueError("HIPAA requires minimum 6 years audit retention")
    
    async def _validate_compliance(self, config: HealthcareConfig) -> None:
        """Validate compliance requirements."""
        if config.compliance_level in [ComplianceLevel.HIPAA_COMPLIANT, ComplianceLevel.FULL_COMPLIANCE]:
            # HIPAA specific validation
            if not config.mfa_required:
                logger.warning("MFA not required - may not meet HIPAA requirements")
            
            if config.encryption_algorithm != "AES-256-GCM":
                raise ValueError("AES-256-GCM encryption required for HIPAA compliance")
    
    async def _create_service_instance(self, config: HealthcareConfig) -> Any:
        """Create service instance based on type."""
        # Placeholder - actual service creation would happen here
        # Each service type would have its own implementation
        service_instance = {
            'type': config.service_type.value,
            'name': config.service_name,
            'config': config.to_dict(),
            'initialized': True
        }
        
        return service_instance
    
    async def _cleanup_service(self, service_data: Dict[str, Any]) -> None:
        """Cleanup service resources."""
        # Placeholder for service-specific cleanup
        pass
    
    def _generate_service_id(self, config: HealthcareConfig) -> str:
        """Generate unique service ID."""
        unique_string = f"{config.service_name}_{config.service_type.value}_{datetime.utcnow().isoformat()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _log_audit_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log audit event."""
        audit_entry = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': event_data
        }
        self.audit_log.append(audit_entry)


# Factory singleton instance
_factory_instance: Optional[HealthcareServiceFactory] = None


def get_healthcare_factory(
    global_config: Optional[Dict[str, Any]] = None
) -> HealthcareServiceFactory:
    """
    Get or create healthcare service factory singleton.
    
    Args:
        global_config: Optional global configuration
        
    Returns:
        HealthcareServiceFactory instance
    """
    global _factory_instance
    
    if _factory_instance is None:
        _factory_instance = HealthcareServiceFactory(global_config)
    
    return _factory_instance


# Convenience functions

async def create_ehr_connector(
    ehr_system: str,
    endpoint: str,
    credentials: Dict[str, str]
) -> Dict[str, Any]:
    """
    Convenience function to create EHR connector.
    
    Args:
        ehr_system: EHR system name (e.g., "Epic", "Cerner")
        endpoint: API endpoint URL
        credentials: Authentication credentials
        
    Returns:
        Service creation result dict
    """
    factory = get_healthcare_factory()
    config = HealthcareConfig(
        service_name=f"{ehr_system}_EHR_Connector",
        service_type=HealthcareServiceType.EHR_INTEGRATION,
        integration_endpoints={'ehr': endpoint},
        api_keys=credentials
    )
    return await factory.create_service(config)


async def create_telemedicine_service(
    platform: str,
    platform_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to create telemedicine service.
    
    Args:
        platform: Telemedicine platform (e.g., "Zoom Healthcare", "Doxy.me")
        platform_config: Platform-specific configuration
        
    Returns:
        Service creation result dict
    """
    factory = get_healthcare_factory()
    config = HealthcareConfig(
        service_name=f"{platform}_Telemedicine",
        service_type=HealthcareServiceType.TELEMEDICINE,
        integration_endpoints={'telemedicine': platform_config.get('endpoint', '')},
        oauth_config=platform_config.get('oauth', {})
    )
    return await factory.create_service(config)


if __name__ == "__main__":
    # Example usage
    async def main():
        factory = get_healthcare_factory()
        
        # Create EHR service
        config = HealthcareConfig(
            service_name="Epic_Production",
            service_type=HealthcareServiceType.EHR_INTEGRATION
        )
        service = await factory.create_service(config)
        print(f"Created service: {service['service_id']}")
        
        # Validate compliance
        compliance = await factory.validate_hipaa_compliance(service['service_id'])
        print(f"HIPAA Compliant: {compliance['overall_compliant']}")
        
        # List services
        services = await factory.list_services()
        print(f"Active services: {len(services)}")
    
    asyncio.run(main())
