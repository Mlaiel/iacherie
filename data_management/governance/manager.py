"""Data Governance Manager - Central orchestrator for all governance operations

This manager coordinates all governance activities including compliance checking,
policy enforcement, lifecycle management, and quality assurance.

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from dataclasses import dataclass

from ..core.base import BaseManager
from ..core.exceptions import GovernanceError, ComplianceError
from .policies import PolicyEngine, DataPolicy
from .compliance import ComplianceManager
from .lifecycle import LifecycleManager
from .quality import QualityManager
from .lineage import LineageTracker
from .access import AccessController
from .privacy import PrivacyManager
from .monitoring import GovernanceMonitor
from .metadata import MetadataManager
from .classification import DataClassifier


class ContentType(Enum):
    """Content types supported by the platform"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class GovernanceStatus(Enum):
    """Governance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class GovernanceResult:
    """Result of governance operations"""
    content_id: str
    status: GovernanceStatus
    policies_applied: List[str]
    compliance_score: float
    quality_score: float
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


class DataGovernanceManager(BaseManager):
    """
    Central manager for all data governance operations
    
    Coordinates compliance checking, policy enforcement, quality assurance,
    and lifecycle management for all content types in the platform.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data governance manager"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize sub-managers
        self.policy_engine = PolicyEngine(config)
        self.compliance_manager = ComplianceManager(config)
        self.lifecycle_manager = LifecycleManager(config)
        self.quality_manager = QualityManager(config)
        self.lineage_tracker = LineageTracker(config)
        self.access_controller = AccessController(config)
        self.privacy_manager = PrivacyManager(config)
        self.governance_monitor = GovernanceMonitor(config)
        self.metadata_manager = MetadataManager(config)
        self.data_classifier = DataClassifier(config)
        
        # Governance metrics
        self.metrics = {
            "total_governed_content": 0,
            "compliance_rate": 0.0,
            "quality_score": 0.0,
            "policy_violations": 0,
            "privacy_incidents": 0
        }
    
    async def apply_governance(
        self,
        content_id: str,
        content_type: ContentType,
        content_data: Any,
        creator_id: str,
        tenant_id: Optional[str] = None,
        policies: Optional[List[str]] = None
    ) -> GovernanceResult:
        """
        Apply complete governance framework to content
        
        Args:
            content_id: Unique content identifier
            content_type: Type of content (audio, video, image, text)
            content_data: The actual content data
            creator_id: ID of content creator
            tenant_id: Tenant identifier for multi-tenant support
            policies: Specific policies to apply (optional)
            
        Returns:
            GovernanceResult with complete governance analysis
        """
        try:
            self.logger.info(f"Applying governance to content {content_id}")
            
            # Initialize result
            result = GovernanceResult(
                content_id=content_id,
                status=GovernanceStatus.PROCESSING,
                policies_applied=[],
                compliance_score=0.0,
                quality_score=0.0,
                issues=[],
                recommendations=[],
                metadata={},
                timestamp=datetime.utcnow()
            )
            
            # 1. Content Classification
            classification = await self.data_classifier.classify_content(
                content_data, content_type
            )
            result.metadata["classification"] = classification
            
            # 2. Privacy Analysis
            privacy_analysis = await self.privacy_manager.analyze_privacy(
                content_data, content_type
            )
            result.metadata["privacy"] = privacy_analysis
            
            # 3. Apply Data Policies
            if policies is None:
                policies = await self.policy_engine.get_applicable_policies(
                    content_type, classification, creator_id, tenant_id
                )
            
            policy_results = []
            for policy_id in policies:
                policy_result = await self.policy_engine.apply_policy(
                    policy_id, content_id, content_data
                )
                policy_results.append(policy_result)
                result.policies_applied.append(policy_id)
            
            result.metadata["policy_results"] = policy_results
            
            # 4. Compliance Checking
            compliance_result = await self.compliance_manager.check_compliance(
                content_id, content_type, content_data, classification
            )
            result.compliance_score = compliance_result.overall_score
            result.issues.extend(compliance_result.violations)
            result.metadata["compliance"] = compliance_result
            
            # 5. Quality Assessment
            quality_result = await self.quality_manager.assess_quality(
                content_id, content_type, content_data
            )
            result.quality_score = quality_result.overall_score
            result.metadata["quality"] = quality_result
            
            # 6. Access Control Setup
            access_result = await self.access_controller.setup_access(
                content_id, creator_id, tenant_id, classification
            )
            result.metadata["access"] = access_result
            
            # 7. Lifecycle Management
            lifecycle_result = await self.lifecycle_manager.initialize_lifecycle(
                content_id, content_type, classification
            )
            result.metadata["lifecycle"] = lifecycle_result
            
            # 8. Data Lineage Tracking
            await self.lineage_tracker.track_creation(
                content_id, creator_id, content_type, classification
            )
            
            # 9. Metadata Management
            await self.metadata_manager.store_metadata(
                content_id, result.metadata
            )
            
            # 10. Determine Final Status
            if result.compliance_score >= 0.9 and result.quality_score >= 0.8:
                result.status = GovernanceStatus.COMPLIANT
            elif result.compliance_score >= 0.7:
                result.status = GovernanceStatus.PENDING_REVIEW
            else:
                result.status = GovernanceStatus.NON_COMPLIANT
            
            # 11. Generate Recommendations
            result.recommendations = await self._generate_recommendations(result)
            
            # 12. Update Metrics
            await self._update_metrics(result)
            
            # 13. Monitor and Alert
            await self.governance_monitor.process_result(result)
            
            self.logger.info(f"Governance applied successfully for {content_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Governance failed for {content_id}: {str(e)}")
            result.status = GovernanceStatus.ERROR
            result.issues.append(f"Governance error: {str(e)}")
            raise GovernanceError(f"Failed to apply governance: {str(e)}")
    
    async def check_compliance(self, content_id: str) -> Dict[str, Any]:
        """Check current compliance status of content"""
        try:
            return await self.compliance_manager.get_compliance_status(content_id)
        except Exception as e:
            raise ComplianceError(f"Failed to check compliance: {str(e)}")
    
    async def update_policies(
        self,
        content_id: str,
        new_policies: List[str]
    ) -> GovernanceResult:
        """Update governance policies for existing content"""
        try:
            # Get existing content metadata
            metadata = await self.metadata_manager.get_metadata(content_id)
            if not metadata:
                raise GovernanceError(f"Content {content_id} not found")
            
            # Re-apply governance with new policies
            return await self.apply_governance(
                content_id=content_id,
                content_type=ContentType(metadata["content_type"]),
                content_data=metadata["content_data"],
                creator_id=metadata["creator_id"],
                tenant_id=metadata.get("tenant_id"),
                policies=new_policies
            )
        except Exception as e:
            raise GovernanceError(f"Failed to update policies: {str(e)}")
    
    async def get_governance_status(self, content_id: str) -> Optional[GovernanceResult]:
        """Get current governance status for content"""
        try:
            metadata = await self.metadata_manager.get_metadata(content_id)
            if not metadata:
                return None
            
            return GovernanceResult(
                content_id=content_id,
                status=GovernanceStatus(metadata.get("status", "unknown")),
                policies_applied=metadata.get("policies_applied", []),
                compliance_score=metadata.get("compliance_score", 0.0),
                quality_score=metadata.get("quality_score", 0.0),
                issues=metadata.get("issues", []),
                recommendations=metadata.get("recommendations", []),
                metadata=metadata,
                timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.utcnow().isoformat()))
            )
        except Exception as e:
            self.logger.error(f"Failed to get governance status: {str(e)}")
            return None
    
    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Get current governance metrics"""
        return {
            **self.metrics,
            "compliance_details": await self.compliance_manager.get_metrics(),
            "quality_details": await self.quality_manager.get_metrics(),
            "policy_details": await self.policy_engine.get_metrics(),
            "privacy_details": await self.privacy_manager.get_metrics()
        }
    
    async def _generate_recommendations(self, result: GovernanceResult) -> List[str]:
        """Generate governance recommendations based on analysis"""
        recommendations = []
        
        # Compliance recommendations
        if result.compliance_score < 0.9:
            recommendations.append("Review and address compliance violations")
            if result.compliance_score < 0.7:
                recommendations.append("Consider content review before publication")
        
        # Quality recommendations
        if result.quality_score < 0.8:
            recommendations.append("Improve content quality metrics")
            recommendations.append("Consider content enhancement or re-processing")
        
        # Privacy recommendations
        privacy_data = result.metadata.get("privacy", {})
        if privacy_data.get("pii_detected"):
            recommendations.append("Remove or anonymize detected PII")
        
        # Security recommendations
        classification = result.metadata.get("classification", {})
        if classification.get("risk_level", "low") == "high":
            recommendations.append("Apply additional security measures")
            recommendations.append("Enable enhanced monitoring")
        
        return recommendations
    
    async def _update_metrics(self, result: GovernanceResult) -> None:
        """Update governance metrics based on result"""
        self.metrics["total_governed_content"] += 1
        
        # Update compliance rate
        if result.status == GovernanceStatus.COMPLIANT:
            compliant_content = self.metrics["total_governed_content"] * self.metrics["compliance_rate"]
            self.metrics["compliance_rate"] = (compliant_content + 1) / self.metrics["total_governed_content"]
        else:
            compliant_content = self.metrics["total_governed_content"] * self.metrics["compliance_rate"]
            self.metrics["compliance_rate"] = compliant_content / self.metrics["total_governed_content"]
        
        # Update quality score (rolling average)
        current_avg = self.metrics["quality_score"]
        total_content = self.metrics["total_governed_content"]
        self.metrics["quality_score"] = ((current_avg * (total_content - 1)) + result.quality_score) / total_content
        
        # Update violation count
        if result.issues:
            self.metrics["policy_violations"] += len(result.issues)
    
    async def cleanup_expired_content(self) -> Dict[str, int]:
        """Clean up expired content based on retention policies"""
        return await self.lifecycle_manager.cleanup_expired_content()
    
    async def export_governance_data(
        self,
        content_ids: Optional[List[str]] = None,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export governance data for auditing or reporting"""
        try:
            return await self.metadata_manager.export_data(content_ids, format_type)
        except Exception as e:
            raise GovernanceError(f"Failed to export governance data: {str(e)}")
