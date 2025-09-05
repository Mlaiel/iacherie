"""Regulatory Index - Centralized Compliance Orchestration

Central orchestration system for all regulatory compliance modules,
providing unified API for multi-jurisdiction compliance management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

from .dmca_handler import DMCAHandler
from .pipeda_compliance import PIPEDACompliance
from .lgpd_compliance import LGPDCompliance
from .pdpa_compliance import PDPACompliance
from .dpa_uk_compliance import DPAUKCompliance
from .coppa_handler import COPPAHandler
from .dsa_compliance import DSACompliance
from .netzg_compliance import NetzGCompliance
from .copyright_manager import CopyrightManager
from .international_laws import InternationalLawsManager
from .regulation_engine import RegulationEngine

logger = logging.getLogger(__name__)


class JurisdictionType(str, Enum):
    """Supported legal jurisdictions"""
    EU = "european_union"
    US = "united_states"
    CA = "canada"
    BR = "brazil"
    SG = "singapore"
    UK = "united_kingdom"
    DE = "germany"
    INTERNATIONAL = "international"


class ComplianceStatus(str, Enum):
    """Overall compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"
    EXEMPT = "exempt"


@dataclass
class ComplianceAssessment:
    """Comprehensive compliance assessment result"""
    jurisdiction: JurisdictionType
    regulation: str
    status: ComplianceStatus
    score: float  # 0-100
    violations: List[str]
    recommendations: List[str]
    assessed_at: datetime
    next_review: datetime


class RegulatoryIndex:
    """Central regulatory compliance orchestrator"""
    
    def __init__(self):
        self.dmca_handler = DMCAHandler()
        self.pipeda_compliance = PIPEDACompliance()
        self.lgpd_compliance = LGPDCompliance()
        self.pdpa_compliance = PDPACompliance()
        self.dpa_uk_compliance = DPAUKCompliance()
        self.coppa_handler = COPPAHandler()
        self.dsa_compliance = DSACompliance()
        self.netzg_compliance = NetzGCompliance()
        self.copyright_manager = CopyrightManager()
        self.international_laws = InternationalLawsManager()
        self.regulation_engine = RegulationEngine()
        
        # Compliance orchestration mapping
        self.jurisdiction_handlers = {
            JurisdictionType.US: [self.dmca_handler, self.coppa_handler],
            JurisdictionType.CA: [self.pipeda_compliance],
            JurisdictionType.BR: [self.lgpd_compliance],
            JurisdictionType.SG: [self.pdpa_compliance],
            JurisdictionType.UK: [self.dpa_uk_compliance],
            JurisdictionType.EU: [self.dsa_compliance],
            JurisdictionType.DE: [self.netzg_compliance],
            JurisdictionType.INTERNATIONAL: [self.copyright_manager, self.international_laws]
        }
    
    async def assess_comprehensive_compliance(
        self, 
        user_data: Dict[str, Any],
        content_data: Optional[Dict[str, Any]] = None,
        jurisdictions: Optional[List[JurisdictionType]] = None
    ) -> List[ComplianceAssessment]:
        """Perform comprehensive multi-jurisdiction compliance assessment"""
        try:
            logger.info("Starting comprehensive compliance assessment")
            
            if jurisdictions is None:
                jurisdictions = list(JurisdictionType)
            
            assessments = []
            
            # Parallel compliance checking across jurisdictions
            assessment_tasks = []
            for jurisdiction in jurisdictions:
                task = self._assess_jurisdiction_compliance(jurisdiction, user_data, content_data)
                assessment_tasks.append(task)
            
            jurisdiction_results = await asyncio.gather(*assessment_tasks, return_exceptions=True)
            
            for jurisdiction, results in zip(jurisdictions, jurisdiction_results):
                if isinstance(results, Exception):
                    logger.error(f"Compliance assessment failed for {jurisdiction}: {results}")
                    continue
                
                assessments.extend(results)
            
            logger.info(f"Completed compliance assessment for {len(assessments)} regulations")
            return assessments
            
        except Exception as e:
            logger.error(f"Comprehensive compliance assessment failed: {e}")
            raise
    
    async def _assess_jurisdiction_compliance(
        self, 
        jurisdiction: JurisdictionType,
        user_data: Dict[str, Any],
        content_data: Optional[Dict[str, Any]]
    ) -> List[ComplianceAssessment]:
        """Assess compliance for specific jurisdiction"""
        assessments = []
        handlers = self.jurisdiction_handlers.get(jurisdiction, [])
        
        for handler in handlers:
            try:
                # Call appropriate assessment method based on handler type
                if hasattr(handler, 'assess_compliance'):
                    result = await handler.assess_compliance(user_data, content_data)
                    assessment = self._create_assessment(jurisdiction, handler.__class__.__name__, result)
                    assessments.append(assessment)
                
            except Exception as e:
                logger.error(f"Assessment failed for {handler.__class__.__name__}: {e}")
                # Create failed assessment
                assessment = ComplianceAssessment(
                    jurisdiction=jurisdiction,
                    regulation=handler.__class__.__name__,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    violations=[f"Assessment error: {str(e)}"],
                    recommendations=["Review compliance implementation"],
                    assessed_at=datetime.utcnow(),
                    next_review=datetime.utcnow()
                )
                assessments.append(assessment)
        
        return assessments
    
    def _create_assessment(
        self, 
        jurisdiction: JurisdictionType, 
        regulation: str, 
        result: Dict[str, Any]
    ) -> ComplianceAssessment:
        """Create standardized compliance assessment"""
        return ComplianceAssessment(
            jurisdiction=jurisdiction,
            regulation=regulation,
            status=ComplianceStatus(result.get('status', 'under_review')),
            score=result.get('score', 0.0),
            violations=result.get('violations', []),
            recommendations=result.get('recommendations', []),
            assessed_at=datetime.utcnow(),
            next_review=result.get('next_review', datetime.utcnow())
        )
    
    async def get_compliance_summary(self, assessments: List[ComplianceAssessment]) -> Dict[str, Any]:
        """Generate executive compliance summary"""
        try:
            total_assessments = len(assessments)
            if total_assessments == 0:
                return {"status": "no_assessments", "message": "No compliance assessments available"}
            
            compliant_count = sum(1 for a in assessments if a.status == ComplianceStatus.COMPLIANT)
            average_score = sum(a.score for a in assessments) / total_assessments
            
            violations = []
            for assessment in assessments:
                violations.extend(assessment.violations)
            
            summary = {
                "overall_status": "compliant" if compliant_count == total_assessments else "non_compliant",
                "compliance_rate": (compliant_count / total_assessments) * 100,
                "average_score": round(average_score, 2),
                "total_assessments": total_assessments,
                "compliant_assessments": compliant_count,
                "total_violations": len(violations),
                "jurisdictions_covered": len(set(a.jurisdiction for a in assessments)),
                "assessment_timestamp": datetime.utcnow().isoformat(),
                "priority_actions": self._get_priority_actions(assessments)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Compliance summary generation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_priority_actions(self, assessments: List[ComplianceAssessment]) -> List[str]:
        """Identify priority compliance actions"""
        actions = []
        
        # Find critical non-compliance issues
        critical_assessments = [a for a in assessments if a.status == ComplianceStatus.NON_COMPLIANT and a.score < 50]
        
        for assessment in critical_assessments:
            actions.append(f"Address {assessment.regulation} violations in {assessment.jurisdiction}")
        
        # Add general recommendations
        if len(critical_assessments) > 0:
            actions.append("Implement immediate remediation plan")
            actions.append("Schedule compliance review meeting")
        
        return actions[:5]  # Top 5 priority actions
    
    async def trigger_compliance_monitoring(self) -> Dict[str, Any]:
        """Trigger automated compliance monitoring across all jurisdictions"""
        try:
            logger.info("Starting automated compliance monitoring")
            
            monitoring_results = {
                "monitoring_started": datetime.utcnow().isoformat(),
                "active_monitors": [],
                "status": "active"
            }
            
            # Start monitoring for each jurisdiction
            for jurisdiction, handlers in self.jurisdiction_handlers.items():
                for handler in handlers:
                    if hasattr(handler, 'start_monitoring'):
                        await handler.start_monitoring()
                        monitoring_results["active_monitors"].append({
                            "jurisdiction": jurisdiction,
                            "handler": handler.__class__.__name__,
                            "status": "monitoring"
                        })
            
            logger.info(f"Started monitoring for {len(monitoring_results['active_monitors'])} compliance modules")
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Compliance monitoring startup failed: {e}")
            return {"status": "error", "message": str(e)}


# Singleton instance for global access
regulatory_index = RegulatoryIndex()