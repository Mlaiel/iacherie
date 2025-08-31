"""IA Influencer Agent - Business Licensing Module

This module handles comprehensive licensing management for multi-format content protection,
automated licensing workflows, revenue distribution, and intellectual property management.

Project: IA Influencer Agent & Content Protection Platform
Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING - COPYRIGHT PROTECTION:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
authorization from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited 
and will result in legal action under applicable copyright laws.
"""from .automated_licensing_engine import AutomatedLicensingEngine
from .copyright_enforcement import CopyrightEnforcementService
from .contract_management import ContractManagementService
from .distribution_rights_engine import DistributionRightsEngine
from .intellectual_property_service import IntellectualPropertyService
from .licensing_compliance import LicensingComplianceService
from .revenue_sharing_engine import RevenueSharingEngine
from .synchronization_rights import SynchronizationRightsService
from .territory_management import TerritoryManagementService
from .usage_analytics import UsageAnalyticsService
from .music_publishing_engine import MusicPublishingEngine
from .content_identification_service import ContentIdentificationService

__all__ = [
    "AutomatedLicensingEngine",
    "CopyrightEnforcementService", 
    "ContractManagementService",
    "DistributionRightsEngine",
    "IntellectualPropertyService",
    "LicensingComplianceService",
    "RevenueSharingEngine",
    "SynchronizationRightsService",
    "TerritoryManagementService",
    "UsageAnalyticsService",
    "MusicPublishingEngine",
    "ContentIdentificationService"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
