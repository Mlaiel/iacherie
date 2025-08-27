"""
Legal Agent Module - Advanced Legal Operations & Intelligence System

Comprehensive legal automation, compliance monitoring, document generation, and legal intelligence
system for content creators. Handles legal research, contract analysis, IP protection, and regulatory adherence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .legal_agent import LegalAgent, LegalAgentConfig
from .legal_analyzer import LegalAnalyzer
from .document_generator import DocumentGenerator
from .regulatory_monitor import RegulatoryMonitor
from .legal_research import LegalResearcher
from .index import app as legal_service_app

__all__ = [
    "LegalAgent",
    "LegalAgentConfig", 
    "LegalAnalyzer",
    "DocumentGenerator",
    "RegulatoryMonitor",
    "LegalResearcher",
    "legal_service_app"
]

__version__ = '2.1.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
