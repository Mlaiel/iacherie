"""Partnership Business Module for IA Influencer Agent
Strategic partnership management and business relationship system

 STRICT COPYRIGHT WARNING 
Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
All rights reserved. Unauthorized use, copying, or reproduction 
of this code, concept, or intellectual property without explicit 
written permission from Fahed Mlaiel is strictly prohibited 
and will result in legal action.

Development Team Specialties:
- Lead Developer + AI Architect: Fahed Mlaiel
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architecture Expert  
- Audio Processing Developer
- DevOps Engineer
- AI Prompt Engineering Specialist
Contact: mlaiel@live.de

This module manages strategic partnerships, business relationships,
contract management, and partnership monetization for creators.
"""
from .partnership_manager import PartnershipManager
from .contract_engine import ContractEngine
from .negotiation_engine import NegotiationEngine
from .revenue_distribution import RevenueDistributionService
from .partner_analytics import PartnerAnalyticsService
from .partnership_models import (
    Partnership, PartnershipType, PartnershipStatus,
    Contract, ContractTerm, NegotiationStage,
    PartnershipRevenue, PartnershipMetrics
)
from .business_intelligence import BusinessIntelligenceEngine
from .opportunity_finder import OpportunityFinderService
from .partnership_lifecycle import PartnershipLifecycleManager

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    'PartnershipManager',
    'ContractEngine', 
    'NegotiationEngine',
    'RevenueDistributionService',
    'PartnerAnalyticsService',
    'BusinessIntelligenceEngine',
    'OpportunityFinderService',
    'PartnershipLifecycleManager',
    'Partnership',
    'PartnershipType',
    'PartnershipStatus', 
    'Contract',
    'ContractTerm',
    'NegotiationStage',
    'PartnershipRevenue',
    'PartnershipMetrics'
]
