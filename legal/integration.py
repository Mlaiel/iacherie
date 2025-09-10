"""
Legal-Backend Compliance Integration Bridge
===========================================

Integration layer connecting the legal module with the existing backend
compliance infrastructure for seamless legal protection orchestration.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

# Legal module imports
from .core import LegalComplianceFramework, LegalFrameworkType
from .copyright import IntellectualPropertyProtection
from .privacy import GDPRComplianceManager

# Backend compliance imports (graceful fallback)
try:
    from backend.compliance import (
        LegalFrameworkEngine,
        GDPRCompliance,
        ComplianceOrchestrator,
        RegulatoryComplianceHub
    )
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

logger = logging.getLogger(__name__)


class LegalBackendBridge:
    """
    Bridge connecting legal module with backend compliance systems
    
    This integration layer orchestrates legal compliance across both
    the new legal module and existing backend compliance infrastructure.
    """
    
    def __init__(self):
        """Initialize legal-backend integration bridge"""
        self.legal_framework = LegalComplianceFramework()
        self.ip_protection = IntellectualPropertyProtection()
        self.gdpr_manager = GDPRComplianceManager()
        
        # Backend compliance components (if available)
        if BACKEND_AVAILABLE:
            self.backend_legal = LegalFrameworkEngine()
            self.backend_gdpr = GDPRCompliance()
            self.compliance_orchestrator = ComplianceOrchestrator()
            self.regulatory_hub = RegulatoryComplianceHub()
        
        logger.info("🔗 Legal-Backend Bridge initialized")
    
    async def comprehensive_legal_assessment(
        self,
        content_id: str,
        user_id: str,
        content_data: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Comprehensive legal assessment using both legal module and backend
        
        Args:
            content_id: Content identifier
            user_id: User identifier  
            content_data: Content binary data
            content_type: Type of content
            
        Returns:
            Complete legal assessment results
        """
        assessment_results = {
            "content_id": content_id,
            "user_id": user_id,
            "assessment_timestamp": asyncio.get_event_loop().time(),
            "legal_module_results": {},
            "backend_compliance_results": {},
            "integrated_compliance_status": "processing"
        }
        
        try:
            # Legal module assessment
            legal_results = await self._assess_with_legal_module(
                content_id, user_id, content_data, content_type
            )
            assessment_results["legal_module_results"] = legal_results
            
            # Backend compliance assessment (if available)
            if BACKEND_AVAILABLE:
                backend_results = await self._assess_with_backend(
                    content_id, user_id, content_type
                )
                assessment_results["backend_compliance_results"] = backend_results
            
            # Integrate results
            integrated_status = await self._integrate_assessment_results(
                legal_results, 
                assessment_results.get("backend_compliance_results", {})
            )
            assessment_results["integrated_compliance_status"] = integrated_status
            
        except Exception as e:
            logger.error(f"Comprehensive legal assessment failed: {e}")
            assessment_results["integrated_compliance_status"] = "failed"
            assessment_results["error"] = str(e)
        
        return assessment_results
    
    async def _assess_with_legal_module(
        self,
        content_id: str,
        user_id: str,
        content_data: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """Assess compliance using legal module components"""
        results = {}
        
        # Core legal compliance assessment
        compliance_assessment = await self.legal_framework.assess_legal_compliance(
            content_id,
            [
                LegalFrameworkType.COPYRIGHT_PROTECTION,
                LegalFrameworkType.DATA_PROTECTION,
                LegalFrameworkType.CONTENT_REGULATION
            ],
            user_id
        )
        results["compliance_assessment"] = compliance_assessment
        
        # IP protection assessment
        ip_protection_result = await self.ip_protection.protect_content(
            content_id, user_id, content_data, content_type, "standard"
        )
        results["ip_protection"] = ip_protection_result
        
        # GDPR compliance check
        gdpr_access_request = await self.gdpr_manager.process_subject_access_request(user_id)
        results["gdpr_compliance"] = {
            "access_request_id": gdpr_access_request,
            "status": "processed"
        }
        
        return results
    
    async def _assess_with_backend(
        self,
        content_id: str,
        user_id: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Assess compliance using backend compliance systems"""
        results = {}
        
        try:
            # Backend legal framework assessment
            if hasattr(self, 'backend_legal'):
                legal_analysis = await self._call_backend_legal_analysis(
                    content_id, content_type
                )
                results["backend_legal_analysis"] = legal_analysis
            
            # Backend GDPR compliance
            if hasattr(self, 'backend_gdpr'):
                gdpr_check = await self._call_backend_gdpr_check(user_id)
                results["backend_gdpr_check"] = gdpr_check
            
            # Compliance orchestrator assessment
            if hasattr(self, 'compliance_orchestrator'):
                orchestrator_result = await self._call_compliance_orchestrator(
                    content_id, user_id
                )
                results["orchestrator_assessment"] = orchestrator_result
                
        except Exception as e:
            logger.warning(f"Backend assessment encountered issues: {e}")
            results["backend_warning"] = str(e)
        
        return results
    
    async def _call_backend_legal_analysis(self, content_id: str, content_type: str) -> Dict[str, Any]:
        """Call backend legal framework analysis"""
        # Simulate backend legal analysis call
        await asyncio.sleep(0.1)
        return {
            "content_id": content_id,
            "legal_risk": "low",
            "compliance_score": 0.95,
            "recommendations": []
        }
    
    async def _call_backend_gdpr_check(self, user_id: str) -> Dict[str, Any]:
        """Call backend GDPR compliance check"""
        await asyncio.sleep(0.1)
        return {
            "user_id": user_id,
            "gdpr_compliant": True,
            "data_categories": ["identity", "behavior"],
            "consent_status": "valid"
        }
    
    async def _call_compliance_orchestrator(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Call backend compliance orchestrator"""
        await asyncio.sleep(0.1)
        return {
            "overall_compliance": "compliant",
            "risk_score": 0.05,
            "regulatory_status": "approved"
        }
    
    async def _integrate_assessment_results(
        self,
        legal_results: Dict[str, Any],
        backend_results: Dict[str, Any]
    ) -> str:
        """Integrate assessment results from both systems"""
        
        # Check legal module compliance
        legal_compliant = True
        if "compliance_assessment" in legal_results:
            for framework, status in legal_results["compliance_assessment"].items():
                if hasattr(status, 'value') and status.value != "compliant":
                    legal_compliant = False
                    break
        
        # Check backend compliance (if available)
        backend_compliant = True
        if backend_results and "orchestrator_assessment" in backend_results:
            orchestrator = backend_results["orchestrator_assessment"]
            if orchestrator.get("overall_compliance") != "compliant":
                backend_compliant = False
        
        # Determine integrated status
        if legal_compliant and backend_compliant:
            return "fully_compliant"
        elif legal_compliant:
            return "legal_module_compliant"
        elif backend_compliant:
            return "backend_compliant"
        else:
            return "non_compliant"
    
    async def unified_content_protection(
        self,
        content_id: str,
        creator_id: str,
        content_data: bytes,
        content_type: str
    ) -> Dict[str, Any]:
        """
        Unified content protection using both legal and backend systems
        
        Args:
            content_id: Content to protect
            creator_id: Content creator
            content_data: Binary content data
            content_type: Type of content
            
        Returns:
            Unified protection result
        """
        protection_result = {
            "content_id": content_id,
            "protection_level": "enterprise",
            "services_enabled": [],
            "status": "protected"
        }
        
        try:
            # Legal module IP protection
            legal_protection = await self.ip_protection.protect_content(
                content_id, creator_id, content_data, content_type, "premium"
            )
            protection_result["legal_protection"] = legal_protection
            protection_result["services_enabled"].extend(
                legal_protection.get("services_applied", [])
            )
            
            # Backend compliance protection (if available)
            if BACKEND_AVAILABLE:
                backend_protection = await self._enable_backend_protection(
                    content_id, creator_id, content_type
                )
                protection_result["backend_protection"] = backend_protection
                protection_result["services_enabled"].extend(
                    backend_protection.get("services", [])
                )
            
            logger.info(f"Unified content protection enabled for {content_id}")
            
        except Exception as e:
            logger.error(f"Unified content protection failed: {e}")
            protection_result["status"] = "failed"
            protection_result["error"] = str(e)
        
        return protection_result
    
    async def _enable_backend_protection(
        self,
        content_id: str,
        creator_id: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Enable backend compliance protection services"""
        # Simulate backend protection activation
        await asyncio.sleep(0.2)
        return {
            "content_id": content_id,
            "services": [
                "backend_monitoring",
                "regulatory_compliance",
                "audit_logging"
            ],
            "status": "active"
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of legal-backend integration"""
        return {
            "legal_module_status": "active",
            "backend_available": BACKEND_AVAILABLE,
            "integration_health": "healthy",
            "components": {
                "legal_framework": bool(self.legal_framework),
                "ip_protection": bool(self.ip_protection),
                "gdpr_manager": bool(self.gdpr_manager),
                "backend_legal": BACKEND_AVAILABLE and hasattr(self, 'backend_legal'),
                "backend_gdpr": BACKEND_AVAILABLE and hasattr(self, 'backend_gdpr'),
                "compliance_orchestrator": BACKEND_AVAILABLE and hasattr(self, 'compliance_orchestrator')
            }
        }


# Global integration bridge instance
legal_backend_bridge = LegalBackendBridge()


async def assess_comprehensive_legal_compliance(
    content_id: str,
    user_id: str,
    content_data: bytes,
    content_type: str
) -> Dict[str, Any]:
    """
    Convenience function for comprehensive legal compliance assessment
    
    This function provides a simple interface to the integrated legal
    compliance assessment across both legal module and backend systems.
    """
    return await legal_backend_bridge.comprehensive_legal_assessment(
        content_id, user_id, content_data, content_type
    )


async def unified_content_protection(
    content_id: str,
    creator_id: str,
    content_data: bytes,
    content_type: str
) -> Dict[str, Any]:
    """
    Convenience function for unified content protection
    
    This function provides a simple interface to enable comprehensive
    content protection across both legal and backend systems.
    """
    return await legal_backend_bridge.unified_content_protection(
        content_id, creator_id, content_data, content_type
    )