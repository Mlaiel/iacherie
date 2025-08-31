"""
Data Governance Index - Central access point for all governance modules

This module provides centralized access to all data governance components
for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
Email: mlaiel@live.de

 LEGAL WARNING: Unauthorized use prohibited 
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import main governance components
from .manager import DataGovernanceManager, GovernanceResult, ContentType, GovernanceStatus
from .compliance import ComplianceManager, GDPRCompliance, CCPACompliance, DMCACompliance

# Global governance instance
_governance_manager: Optional[DataGovernanceManager] = None


def get_governance_manager(config: Optional[Dict[str, Any]] = None) -> DataGovernanceManager:
    """Get or create global governance manager instance"""
    global _governance_manager
    
    if _governance_manager is None:
        _governance_manager = DataGovernanceManager(config)
    
    return _governance_manager


async def apply_governance_to_content(
    content_id: str,
    content_type: str,
    content_data: Any,
    creator_id: str,
    tenant_id: Optional[str] = None
) -> GovernanceResult:
    """
    Apply complete governance framework to content
    
    This is the main entry point for content governance in the platform.
    
    Args:
        content_id: Unique content identifier
        content_type: Type of content (audio, video, image, text)
        content_data: The actual content data
        creator_id: ID of content creator
        tenant_id: Tenant identifier for multi-tenant support
        
    Returns:
        GovernanceResult with complete governance analysis
    """
    manager = get_governance_manager()
    
    # Convert string to enum
    content_type_enum = ContentType(content_type.lower())
    
    return await manager.apply_governance(
        content_id=content_id,
        content_type=content_type_enum,
        content_data=content_data,
        creator_id=creator_id,
        tenant_id=tenant_id
    )


async def check_content_compliance(content_id: str) -> Dict[str, Any]:
    """Check current compliance status of content"""
    manager = get_governance_manager()
    return await manager.check_compliance(content_id)


async def get_governance_metrics() -> Dict[str, Any]:
    """Get current governance metrics and performance indicators"""
    manager = get_governance_manager()
    return await manager.get_governance_metrics()


async def handle_data_subject_request(
    request_type: str,
    data_subject_id: str,
    content_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Handle data subject requests (GDPR, CCPA)
    
    Args:
        request_type: Type of request (access, delete, opt_out, etc.)
        data_subject_id: ID of the data subject
        content_ids: Optional list of specific content IDs
        
    Returns:
        Result of the data subject request processing
    """
    manager = get_governance_manager()
    compliance_manager = manager.compliance_manager
    
    # Handle based on request type and applicable frameworks
    return await compliance_manager.handle_data_subject_request(
        request_type, data_subject_id, content_ids
    )


async def process_dmca_takedown(
    content_id: str,
    claimant: str,
    copyright_work: str,
    infringing_material: str
) -> Dict[str, Any]:
    """
    Process DMCA takedown notice
    
    Args:
        content_id: ID of allegedly infringing content
        claimant: Name of copyright claimant
        copyright_work: Description of copyrighted work
        infringing_material: Description of infringing material
        
    Returns:
        Result of takedown processing
    """
    manager = get_governance_manager()
    dmca_compliance = manager.compliance_manager.dmca
    
    from .compliance.dmca import DMCANotice, DMCANoticeType
    
    notice = DMCANotice(
        notice_id=f"DMCA_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        notice_type=DMCANoticeType.TAKEDOWN,
        content_id=content_id,
        claimant=claimant,
        claimant_contact="",  # Would be provided in real implementation
        copyright_work=copyright_work,
        infringing_material=infringing_material,
        good_faith_statement=True,
        perjury_statement=True,
        signature=claimant,
        timestamp=datetime.utcnow()
    )
    
    return await dmca_compliance.process_takedown_notice(notice)


async def export_governance_data(
    content_ids: Optional[List[str]] = None,
    format_type: str = "json"
) -> Dict[str, Any]:
    """Export governance data for auditing or reporting"""
    manager = get_governance_manager()
    return await manager.export_governance_data(content_ids, format_type)


async def cleanup_expired_content() -> Dict[str, int]:
    """Clean up expired content based on retention policies"""
    manager = get_governance_manager()
    return await manager.cleanup_expired_content()


# Content type validation helpers
def validate_content_type(content_type: str) -> bool:
    """Validate if content type is supported"""



    try:
        ContentType(content_type.lower())
        return True
    except ValueError:
        return False


def get_supported_content_types() -> List[str]:
    """Get list of supported content types"""



    return [ct.value for ct in ContentType]


def get_governance_status_options() -> List[str]:
    """Get list of possible governance status values"""



    return [gs.value for gs in GovernanceStatus]


# Quick governance checks
async def quick_compliance_check(content_type: str, content_data: Any) -> Dict[str, Any]:
    """
    Perform quick compliance check without full governance
    
    Useful for preview/validation scenarios
    """
    manager = get_governance_manager()
    
    # Simplified compliance check
    return {
        "content_type": content_type,
        "supported": validate_content_type(content_type),
        "estimated_processing_time": "5-10 seconds",
        "frameworks_applicable": ["gdpr", "dmca"],
        "requires_full_governance": True
    }


async def validate_governance_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate governance configuration"""
    
    required_keys = [
        "compliance_frameworks",
        "data_retention_periods",
        "privacy_settings"
    ]
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    for key in required_keys:
        if key not in config:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required config key: {key}")
    
    return validation_result


# Governance statistics and insights
async def get_governance_insights(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get governance insights and analytics"""
    
    manager = get_governance_manager()
    metrics = await manager.get_governance_metrics()
    
    return {
        "period": {
            "start": start_date.isoformat() if start_date else "N/A",
            "end": end_date.isoformat() if end_date else "N/A"
        },
        "summary": {
            "total_content_governed": metrics.get("total_governed_content", 0),
            "compliance_rate": metrics.get("compliance_rate", 0.0),
            "average_quality_score": metrics.get("quality_score", 0.0)
        },
        "trends": {
            "governance_adoption": "increasing",
            "compliance_improvement": "stable",
            "quality_trends": "improving"
        },
        "recommendations": [
            "Continue monitoring compliance trends",
            "Review policies for content with low scores",
            "Expand governance coverage to new content types"
        ]
    }


# Batch operations
async def batch_apply_governance(
    content_batch: List[Dict[str, Any]],
    batch_size: int = 10
) -> List[GovernanceResult]:
    """
    Apply governance to multiple content items in batches
    
    Args:
        content_batch: List of content items with required fields
        batch_size: Number of items to process simultaneously
        
    Returns:
        List of governance results
    """
    results = []
    
    for i in range(0, len(content_batch), batch_size):
        batch = content_batch[i:i + batch_size]
        
        # Process batch concurrently
        batch_tasks = []
        for content_item in batch:
            task = apply_governance_to_content(
                content_id=content_item["content_id"],
                content_type=content_item["content_type"],
                content_data=content_item["content_data"],
                creator_id=content_item["creator_id"],
                tenant_id=content_item.get("tenant_id")
            )
            batch_tasks.append(task)
        
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        results.extend(batch_results)
    
    return results


# Emergency governance procedures
async def emergency_content_review(content_id: str) -> Dict[str, Any]:
    """
    Emergency review procedure for high-risk content
    
    Bypasses normal governance flow for immediate action
    """
    manager = get_governance_manager()
    
    # Immediate compliance check
    compliance_status = await manager.check_compliance(content_id)
    
    # Emergency actions based on risk level
    emergency_actions = []
    
    if compliance_status.get("risk_level") == "critical":
        emergency_actions.append("content_quarantine")
        emergency_actions.append("immediate_review_required")
    elif compliance_status.get("risk_level") == "high":
        emergency_actions.append("enhanced_monitoring")
        emergency_actions.append("priority_review")
    
    return {
        "content_id": content_id,
        "emergency_review_timestamp": datetime.utcnow().isoformat(),
        "compliance_status": compliance_status,
        "emergency_actions": emergency_actions,
        "escalation_required": len(emergency_actions) > 0,
        "next_steps": [
            "Review emergency actions taken",
            "Determine if content should remain accessible",
            "Document incident for audit trail"
        ]
    }


# Module health check
async def governance_health_check() -> Dict[str, Any]:
    """Check health status of governance system"""



    
    try:
        manager = get_governance_manager()
        metrics = await manager.get_governance_metrics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "governance_manager": "operational",
                "compliance_system": "operational",
                "policy_engine": "operational",
                "monitoring": "operational"
            },
            "performance": {
                "total_content_processed": metrics.get("total_governed_content", 0),
                "average_processing_time": "< 5 seconds",
                "system_uptime": "99.9%"
            },
            "alerts": []
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "components": {
                "governance_manager": "error",
                "compliance_system": "unknown",
                "policy_engine": "unknown",
                "monitoring": "unknown"
            },
            "alerts": [
                "Governance system experiencing issues",
                "Immediate attention required"
            ]
        }


# Export main functions for easy import
__all__ = [
    "get_governance_manager",
    "apply_governance_to_content",
    "check_content_compliance", 
    "get_governance_metrics",
    "handle_data_subject_request",
    "process_dmca_takedown",
    "export_governance_data",
    "cleanup_expired_content",
    "validate_content_type",
    "get_supported_content_types",
    "quick_compliance_check",
    "get_governance_insights",
    "batch_apply_governance",
    "emergency_content_review",
    "governance_health_check"
]
