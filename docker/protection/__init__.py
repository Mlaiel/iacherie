"""
  Init   module
Enterprise implementation for Ainflue platform
"""

# =============================================================================
# AINFLUE PROTECTION RIGHTS DOCKER MODULE
# =============================================================================
# Content protection and rights management Docker containers
#
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# =============================================================================

"""
from typing import Dict, List, Optional, Union, Tuple

Protection Rights Docker Module

This module provides Docker containers for comprehensive content protection
and rights management including fingerprinting, watermarking, copyright
monitoring, and blockchain verification.

Services:
- Protection Service: Main protection and rights management
- Fingerprinting Engine: Multi-format digital fingerprinting  
- Watermarking Service: Advanced invisible/visible watermarking
- Copyright Monitor: Real-time copyright violation monitoring
- DMCA Automation: Automated DMCA takedown processing
- Blockchain Verifier: Blockchain-based content verification
- Violation Detector: AI-powered violation detection
- Rights Manager: Comprehensive rights management
- Enforcement Engine: Rights enforcement automation
- DRM Controller: Digital Rights Management
- Content Scanner: Automated content scanning
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Protection services registry
PROTECTION_SERVICES = {
    "protection_service": {
        "name": "Protection Service",
        "dockerfile": "protection_service.dockerfile",
        "port": 8020,
        "description": "Main content protection and rights management service"
    },
    "fingerprinting_engine": {
        "name": "Fingerprinting Engine",
        "dockerfile": "fingerprinting_engine.dockerfile",
        "port": 8021,
        "description": "Multi-format digital fingerprinting service"
    },
    "watermarking_service": {
        "name": "Watermarking Service", 
        "dockerfile": "watermarking_service.dockerfile",
        "port": 8022,
        "description": "Advanced invisible/visible watermarking service"
    },
    "copyright_monitor": {
        "name": "Copyright Monitor",
        "dockerfile": "copyright_monitor.dockerfile",
        "port": 8023,
        "description": "Real-time copyright violation monitoring"
    },
    "dmca_automation": {
        "name": "DMCA Automation",
        "dockerfile": "dmca_automation.dockerfile",
        "port": 8024,
        "description": "Automated DMCA takedown processing"
    },
    "blockchain_verifier": {
        "name": "Blockchain Verifier",
        "dockerfile": "blockchain_verifier.dockerfile",
        "port": 8025,
        "description": "Blockchain-based content verification"
    },
    "violation_detector": {
        "name": "Violation Detector",
        "dockerfile": "violation_detector.dockerfile",
        "port": 8026,
        "description": "AI-powered violation detection service"
    },
    "rights_manager": {
        "name": "Rights Manager",
        "dockerfile": "rights_manager.dockerfile",
        "port": 8027,
        "description": "Comprehensive rights management service"
    },
    "enforcement_engine": {
        "name": "Enforcement Engine",
        "dockerfile": "enforcement_engine.dockerfile",
        "port": 8028,
        "description": "Rights enforcement automation service"
    },
    "drm_controller": {
        "name": "DRM Controller",
        "dockerfile": "drm_controller.dockerfile",
        "port": 8029,
        "description": "Digital Rights Management controller"
    },
    "content_scanner": {
        "name": "Content Scanner",
        "dockerfile": "content_scanner.dockerfile",
        "port": 8030,
        "description": "Automated content scanning service"
    }
}

def get_protection_service_info(service_name: str) -> dict:
    """Get information about a specific protection service."""
    return PROTECTION_SERVICES.get(service_name, {})

def list_protection_services() -> list:
    """List all available protection services."""
    return list(PROTECTION_SERVICES.keys())

def get_services_by_category() -> dict:
    """Get protection services organized by category."""
    return {
        "content_identification": [
            "fingerprinting_engine", 
            "watermarking_service",
            "content_scanner"
        ],
        "monitoring": [
            "copyright_monitor",
            "violation_detector"
        ],
        "enforcement": [
            "dmca_automation",
            "enforcement_engine",
            "rights_manager"
        ],
        "verification": [
            "blockchain_verifier",
            "drm_controller"
        ],
        "core": [
            "protection_service"
        ]
    }