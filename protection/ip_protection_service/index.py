"""🛡️ IP Protection Service - Main Orchestration Module
====================================================

Professional orchestration module for the IP Protection Service providing
unified access to all protection capabilities and streamlined workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY PROTECTION WARNING ⚠️
===============================================
Contact mlaiel@live.de for MANDATORY authorization before any interaction.
All access attempts are permanently logged and legally monitored.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import core service
from . import IPProtectionService

# Import individual components
from .plagiarism_detection_api import PlagiarismDetectionAPI, DetectionRequest, PlagiarismResult
from .unauthorized_usage_monitor import UnauthorizedUsageMonitor, MonitoringSession, UsageViolation
from .automated_dmca_system import AutomatedDMCASystem, DMCARequest, DMCAResult

# Import configuration and models
from .config import IPProtectionConfig
from .models import ContentType, ProtectionLevel, ViolationType, EnforcementType
from .exceptions import IPProtectionException

logger = logging.getLogger(__name__)

# Quick access functions for common operations
async def quick_content_protection(
    content_id: str,
    content_type: str,
    protection_level: str = "standard"
) -> Dict[str, Any]:
    """
    Quick content protection with default settings.
    
    Args:
        content_id: Unique identifier for the content
        content_type: Type of content (audio, video, image, text)
        protection_level: Level of protection (basic, standard, premium, enterprise, maximum)
        
    Returns:
        Comprehensive protection result
    """
    try:
        # Initialize service with default configuration
        service = IPProtectionService()
        await service.initialize()
        
        # Convert string parameters to enums
        content_type_enum = ContentType(content_type.lower())
        protection_level_enum = ProtectionLevel(protection_level.lower())
        
        # Execute comprehensive protection
        result = await service.protect_content_comprehensive(
            content_id=content_id,
            content_type=content_type_enum,
            protection_level=protection_level_enum
        )
        
        await service.shutdown()
        return result
        
    except Exception as e:
        logger.error(f"Quick content protection failed: {e}")
        raise IPProtectionException(f"Quick protection failed: {e}")

async def quick_plagiarism_detection(
    content_id: str,
    content_type: str,
    similarity_threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Quick plagiarism detection for content.
    
    Args:
        content_id: Unique identifier for the content
        content_type: Type of content (audio, video, image, text)
        similarity_threshold: Similarity threshold for detection
        
    Returns:
        Plagiarism detection result
    """
    try:
        # Initialize service with default configuration
        service = IPProtectionService()
        await service.initialize()
        
        # Convert string parameter to enum
        content_type_enum = ContentType(content_type.lower())
        
        # Execute plagiarism detection
        result = await service.detect_plagiarism(
            content_id=content_id,
            content_type=content_type_enum,
            detection_level=ProtectionLevel.STANDARD
        )
        
        await service.shutdown()
        
        return {
            "content_id": content_id,
            "violations_found": result.violations_found,
            "confidence_score": result.confidence_score,
            "similar_content": [
                {
                    "platform": match.platform,
                    "similarity_score": match.similarity_score,
                    "infringing_url": match.evidence_urls[0] if match.evidence_urls else None
                }
                for match in result.similar_content[:10]  # Top 10 matches
            ],
            "threat_assessment": result.threat_assessment.value,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Quick plagiarism detection failed: {e}")
        raise IPProtectionException(f"Plagiarism detection failed: {e}")

async def quick_monitoring_setup(
    content_id: str,
    platforms: Optional[List[str]] = None,
    monitoring_frequency: int = 300
) -> str:
    """
    Quick monitoring setup for content.
    
    Args:
        content_id: Unique identifier for the content to monitor
        platforms: Optional list of platforms to monitor
        monitoring_frequency: Frequency of monitoring checks in seconds
        
    Returns:
        Monitoring session ID
    """
    try:
        # Initialize service with default configuration
        service = IPProtectionService()
        await service.initialize()
        
        # Start monitoring
        session_id = await service.start_monitoring(
            content_id=content_id,
            platforms=platforms,
            monitoring_frequency=monitoring_frequency
        )
        
        # Note: Service should remain running for monitoring, so we don't shutdown here
        logger.info(f"Monitoring setup completed for content {content_id}, session: {session_id}")
        return session_id
        
    except Exception as e:
        logger.error(f"Quick monitoring setup failed: {e}")
        raise IPProtectionException(f"Monitoring setup failed: {e}")

async def quick_dmca_takedown(
    violation_id: str,
    escalation_level: str = "standard"
) -> Dict[str, Any]:
    """
    Quick DMCA takedown execution.
    
    Args:
        violation_id: Unique identifier for the violation
        escalation_level: Level of enforcement (standard, urgent, immediate)
        
    Returns:
        DMCA takedown result
    """
    try:
        # Initialize service with default configuration
        service = IPProtectionService()
        await service.initialize()
        
        # Convert string parameter to enum
        escalation_level_enum = EnforcementType(escalation_level.lower())
        
        # Execute DMCA takedown
        result = await service.execute_dmca_takedown(
            violation_id=violation_id,
            escalation_level=escalation_level_enum
        )
        
        await service.shutdown()
        
        return {
            "dmca_id": result.dmca_id,
            "violation_id": result.violation_id,
            "status": result.status.value,
            "platform": result.platform,
            "submission_timestamp": result.submission_timestamp.isoformat() if result.submission_timestamp else None,
            "compliance_score": result.compliance_score,
            "estimated_success_probability": result.estimated_success_probability,
            "reference_number": result.reference_number,
            "follow_up_required": result.follow_up_required,
            "recommendations": result.escalation_recommendations
        }
        
    except Exception as e:
        logger.error(f"Quick DMCA takedown failed: {e}")
        raise IPProtectionException(f"DMCA takedown failed: {e}")

async def get_protection_status(content_id: str) -> Dict[str, Any]:
    """
    Get comprehensive protection status for content.
    
    Args:
        content_id: Unique identifier for the content
        
    Returns:
        Protection status details
    """
    try:
        # Initialize service with default configuration
        service = IPProtectionService()
        await service.initialize()
        
        # Get protection status
        status = await service.get_protection_status(content_id)
        
        await service.shutdown()
        return status
        
    except Exception as e:
        logger.error(f"Get protection status failed: {e}")
        raise IPProtectionException(f"Status retrieval failed: {e}")

# Service factory functions
def create_ip_protection_service(config: Optional[Dict[str, Any]] = None) -> IPProtectionService:
    """
    Create and configure an IP Protection Service instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured IP Protection Service instance
    """
    return IPProtectionService(config)

def create_plagiarism_detection_api(config: Optional[Dict[str, Any]] = None) -> PlagiarismDetectionAPI:
    """
    Create and configure a Plagiarism Detection API instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Plagiarism Detection API instance
    """
    return PlagiarismDetectionAPI(config or {})

def create_usage_monitor(config: Optional[Dict[str, Any]] = None) -> UnauthorizedUsageMonitor:
    """
    Create and configure an Unauthorized Usage Monitor instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Unauthorized Usage Monitor instance
    """
    return UnauthorizedUsageMonitor(config or {})

def create_dmca_system(config: Optional[Dict[str, Any]] = None) -> AutomatedDMCASystem:
    """
    Create and configure an Automated DMCA System instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Automated DMCA System instance
    """
    return AutomatedDMCASystem(config or {})

# Configuration helpers
def load_default_config() -> IPProtectionConfig:
    """Load default IP Protection Service configuration."""
    return IPProtectionConfig()

def load_config_from_file(config_path: str) -> IPProtectionConfig:
    """Load IP Protection Service configuration from file."""
    return IPProtectionConfig.from_file(config_path)

# Health check and diagnostics
async def health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check of IP Protection Service.
    
    Returns:
        Health check results
    """
    try:
        # Initialize service
        service = IPProtectionService()
        await service.initialize()
        
        # Get system status
        status = await service.get_protection_status("health_check_content")
        
        await service.shutdown()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service_status": status,
            "version": "2.0.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "version": "2.0.0"
        }

# Export main functions and classes
__all__ = [
    # Main service
    "IPProtectionService",
    
    # Core APIs
    "PlagiarismDetectionAPI",
    "UnauthorizedUsageMonitor",
    "AutomatedDMCASystem",
    
    # Quick access functions
    "quick_content_protection",
    "quick_plagiarism_detection",
    "quick_monitoring_setup",
    "quick_dmca_takedown",
    "get_protection_status",
    
    # Factory functions
    "create_ip_protection_service",
    "create_plagiarism_detection_api",
    "create_usage_monitor",
    "create_dmca_system",
    
    # Configuration
    "load_default_config",
    "load_config_from_file",
    
    # Health and diagnostics
    "health_check",
    
    # Data models and types
    "DetectionRequest",
    "PlagiarismResult",
    "MonitoringSession",
    "UsageViolation",
    "DMCARequest",
    "DMCAResult",
    "IPProtectionConfig",
    "ContentType",
    "ProtectionLevel",
    "ViolationType",
    "EnforcementType",
    "IPProtectionException"
]

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All Rights Reserved"

# Usage examples in docstring
__doc__ += '''

Usage Examples:
==============

Basic Content Protection:
```python
import asyncio
from protection.ip_protection_service import quick_content_protection

async def protect_my_content():
    result = await quick_content_protection(
        content_id="my_song_123",
        content_type="audio",
        protection_level="premium"
    )
    print(f"Protection setup complete: {result['protection_score']}")

asyncio.run(protect_my_content())
```

Plagiarism Detection:
```python
from protection.ip_protection_service import quick_plagiarism_detection

async def check_plagiarism():
    result = await quick_plagiarism_detection(
        content_id="my_article_456", 
        content_type="text",
        similarity_threshold=0.90
    )
    print(f"Found {result['violations_found']} potential violations")

asyncio.run(check_plagiarism())
```

Advanced Service Usage:
```python
from protection.ip_protection_service import create_ip_protection_service

async def advanced_protection():
    service = create_ip_protection_service({
        "api": {"similarity_threshold": 0.95},
        "monitoring": {"default_monitoring_frequency": 180},
        "dmca": {"auto_submission_enabled": True}
    })
    
    await service.initialize()
    
    # Comprehensive protection workflow
    result = await service.protect_content_comprehensive(
        content_id="premium_content_789",
        content_type=ContentType.VIDEO,
        protection_level=ProtectionLevel.ENTERPRISE
    )
    
    await service.shutdown()
    return result

asyncio.run(advanced_protection())
```
'''