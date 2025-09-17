"""🔒 ML Security Module - Ainflue Enterprise
=======================================================================
Factory et registry pour composants sécurité ML avec orchestration enterprise.
Security services initialization + component registry + configuration management.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue ML Security
Version: 1.0 Production
=======================================================================
"""

import logging
from typing import Dict, List, Optional, Any, Type, Protocol
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityServiceType(Enum):
    """Types de services sécurité ML enterprise"""
    THREAT_DETECTION = "threat_detection"
    ADVERSARIAL_DEFENSE = "adversarial_defense"
    MODEL_INTEGRITY = "model_integrity"
    DATA_PRIVACY = "data_privacy"
    ACCESS_CONTROL = "access_control"
    ENCRYPTION = "encryption"
    AUDIT_TRAIL = "audit_trail"
    COMPLIANCE = "compliance"
    VULNERABILITY_SCAN = "vulnerability_scan"
    INTRUSION_DETECTION = "intrusion_detection"
    SECURE_SERVING = "secure_serving"
    FEDERATED_SECURITY = "federated_security"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    MONITORING = "monitoring"
    INCIDENT_RESPONSE = "incident_response"

@dataclass
class SecurityConfig:
    """Configuration sécurité ML enterprise"""
    service_type: SecurityServiceType
    security_level: str = "enterprise"
    encryption_enabled: bool = True
    audit_enabled: bool = True
    compliance_mode: str = "gdpr_ccpa"
    monitoring_enabled: bool = True
    threat_detection_enabled: bool = True
    adversarial_protection: bool = True
    model_integrity_checks: bool = True
    data_privacy_level: str = "high"
    access_control_mode: str = "rbac"
    incident_response_enabled: bool = True
    creator_ip_protection: bool = True
    ainflue_integration: bool = True

class SecurityService(Protocol):
    """Protocol pour services sécurité ML"""
    async def initialize(self, config: SecurityConfig) -> None:
        """Initialisation service sécurité"""
        ...
    
    async def execute_security_check(self, request: Any) -> Any:
        """Exécution check sécurité"""
        ...
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Statut service sécurité"""
        ...
    
    async def handle_security_incident(self, incident: Any) -> Any:
        """Gestion incident sécurité"""
        ...

class MLSecurityRegistry:
    """
    Registry services sécurité ML avec factory patterns.
    Orchestration services sécurité + lifecycle management + configuration.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._services: Dict[SecurityServiceType, SecurityService] = {}
        self._configurations: Dict[SecurityServiceType, SecurityConfig] = {}
        self._status_cache: Dict[str, Any] = {}
        self._initialized = False
        
    def register_security_service(
        self, 
        service_type: SecurityServiceType, 
        service: SecurityService, 
        config: SecurityConfig
    ) -> None:
        """Enregistrement service sécurité avec configuration."""
        self.logger.info(f"🔒 Registering security service: {service_type.value}")
        self._services[service_type] = service
        self._configurations[service_type] = config
        
    async def get_security_service(self, service_type: SecurityServiceType) -> Optional[SecurityService]:
        """Récupération service sécurité avec lazy loading."""
        if service_type not in self._services:
            self.logger.warning(f"🔒 Security service not found: {service_type.value}")
            return None
        return self._services[service_type]
        
    async def initialize_all_services(self) -> Dict[str, Any]:
        """Initialisation tous services sécurité avec orchestration."""
        self.logger.info("🔒 Initializing all ML security services...")
        
        initialization_results = {}
        
        for service_type, service in self._services.items():
            try:
                config = self._configurations.get(service_type)
                if config:
                    await service.initialize(config)
                    initialization_results[service_type.value] = "success"
                    self.logger.info(f"✅ {service_type.value} initialized successfully")
                else:
                    initialization_results[service_type.value] = "no_config"
                    self.logger.warning(f"⚠️ No configuration found for {service_type.value}")
            except Exception as e:
                initialization_results[service_type.value] = f"error: {str(e)}"
                self.logger.error(f"❌ Failed to initialize {service_type.value}: {e}")
        
        self._initialized = True
        self.logger.info(f"🔒 Security services initialization complete: {len(initialization_results)} services")
        
        return initialization_results
        
    async def execute_comprehensive_security_check(self, target: Any) -> Dict[str, Any]:
        """Exécution check sécurité comprehensive sur tous services."""
        if not self._initialized:
            await self.initialize_all_services()
            
        self.logger.info("🔒 Executing comprehensive security check...")
        
        security_results = {}
        
        for service_type, service in self._services.items():
            try:
                result = await service.execute_security_check(target)
                security_results[service_type.value] = result
                self.logger.debug(f"✅ Security check completed for {service_type.value}")
            except Exception as e:
                security_results[service_type.value] = {"error": str(e)}
                self.logger.error(f"❌ Security check failed for {service_type.value}: {e}")
        
        # Agrégation résultats
        overall_security_score = self._calculate_security_score(security_results)
        
        comprehensive_result = {
            "timestamp": asyncio.get_event_loop().time(),
            "overall_security_score": overall_security_score,
            "service_results": security_results,
            "threat_level": self._assess_threat_level(security_results),
            "recommendations": self._generate_security_recommendations(security_results)
        }
        
        self.logger.info(f"🔒 Comprehensive security check complete. Score: {overall_security_score}/100")
        
        return comprehensive_result
        
    def get_security_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble statut sécurité tous services."""
        return {
            "registered_services": len(self._services),
            "initialized": self._initialized,
            "service_types": [service_type.value for service_type in self._services.keys()],
            "security_level": "enterprise",
            "ip_owner": "Fahed Mlaiel (mlaiel@live.de)",
            "compliance_frameworks": ["GDPR", "CCPA", "SOC2"],
            "last_update": asyncio.get_event_loop().time()
        }
    
    def _calculate_security_score(self, results: Dict[str, Any]) -> float:
        """Calcul score sécurité global"""
        if not results:
            return 0.0
        
        scores = []
        for service_result in results.values():
            if isinstance(service_result, dict) and "score" in service_result:
                scores.append(service_result["score"])
            elif not isinstance(service_result, dict) or "error" not in service_result:
                scores.append(85.0)  # Score par défaut pour services fonctionnels
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _assess_threat_level(self, results: Dict[str, Any]) -> str:
        """Évaluation niveau menace global"""
        error_count = sum(1 for result in results.values() 
                         if isinstance(result, dict) and "error" in result)
        
        if error_count > len(results) * 0.5:
            return "HIGH"
        elif error_count > len(results) * 0.2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_security_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Génération recommandations sécurité"""
        recommendations = []
        
        for service_type, result in results.items():
            if isinstance(result, dict) and "error" in result:
                recommendations.append(f"Fix {service_type} service configuration")
        
        if not recommendations:
            recommendations.append("Security posture is good - maintain current practices")
        
        return recommendations

# Factory Functions
def create_threat_detection_engine(config: SecurityConfig) -> 'ThreatDetectionEngine':
    """Factory création moteur détection menaces."""
    try:
        from .threat_detection_engine import ThreatDetectionEngine
        return ThreatDetectionEngine(config)
    except ImportError:
        logger.error("ThreatDetectionEngine not available")
        return None

def create_adversarial_defense_system(config: SecurityConfig) -> 'AdversarialDefenseSystem':
    """Factory création système défense adversariale."""
    try:
        from .adversarial_defense_system import AdversarialDefenseSystem
        return AdversarialDefenseSystem(config)
    except ImportError:
        logger.error("AdversarialDefenseSystem not available")
        return None

def create_model_integrity_validator(config: SecurityConfig) -> 'ModelIntegrityValidator':
    """Factory création validateur intégrité modèles."""
    try:
        from .model_integrity_validator import ModelIntegrityValidator
        return ModelIntegrityValidator(config)
    except ImportError:
        logger.error("ModelIntegrityValidator not available")
        return None

def create_data_privacy_protector(config: SecurityConfig) -> 'DataPrivacyProtector':
    """Factory création protecteur confidentialité données."""
    try:
        from .data_privacy_protector import DataPrivacyProtector
        return DataPrivacyProtector(config)
    except ImportError:
        logger.error("DataPrivacyProtector not available")
        return None

def create_access_control_manager(config: SecurityConfig) -> 'AccessControlManager':
    """Factory création gestionnaire contrôle accès."""
    try:
        from .access_control_manager import AccessControlManager
        return AccessControlManager(config)
    except ImportError:
        logger.error("AccessControlManager not available")
        return None

def create_encryption_service(config: SecurityConfig) -> 'EncryptionService':
    """Factory création service chiffrement."""
    try:
        from .encryption_service import EncryptionService
        return EncryptionService(config)
    except ImportError:
        logger.error("EncryptionService not available")
        return None

# Security Services Registry Global
_security_registry = MLSecurityRegistry()

def get_security_registry() -> MLSecurityRegistry:
    """Accès au registry global sécurité ML"""
    return _security_registry

# Export API
__all__ = [
    'MLSecurityRegistry',
    'SecurityConfig', 
    'SecurityServiceType',
    'SecurityService',
    'create_threat_detection_engine',
    'create_adversarial_defense_system',
    'create_model_integrity_validator',
    'create_data_privacy_protector',
    'create_access_control_manager',
    'create_encryption_service',
    'get_security_registry',
    '_security_registry'
]

# Version et informations
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - Fahed Mlaiel"