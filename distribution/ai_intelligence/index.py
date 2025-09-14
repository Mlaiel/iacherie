"""
Distribution AI Intelligence - Point d'entrée principal
Auteur: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Production Enterprise

Module d'intelligence artificielle pour la distribution globale Ainflue.
Orchestration de 53 agents IA spécialisés pour optimisation distribution multi-plateforme.
"""

from .ai_orchestrator import AIOrchestrator, DistributionAICoordinator
from .content_intelligence import ContentIntelligenceEngine, SemanticAnalyzer
from .platform_intelligence import PlatformIntelligenceEngine, AlgorithmPredictor
from .audience_intelligence import AudienceIntelligenceEngine, BehaviorPredictor
from .viral_intelligence import ViralIntelligenceEngine, TrendPredictor
from .performance_intelligence import PerformanceIntelligenceEngine, ROIOptimizer

# Import specialized engines from the combined module
from .specialized_intelligence_engines import (
    CrisisIntelligenceEngine, ThreatDetector,
    GeographicIntelligenceEngine,
    TemporalIntelligenceEngine, 
    CollaborationIntelligenceEngine,
    MonetizationIntelligenceEngine,
    ComplianceIntelligenceEngine,
    RealTimeIntelligenceEngine
)

# Exports publics du module
__all__ = [
    # Core AI Orchestration
    'AIOrchestrator',
    'DistributionAICoordinator',
    
    # Specialized Intelligence Engines
    'ContentIntelligenceEngine',
    'PlatformIntelligenceEngine', 
    'AudienceIntelligenceEngine',
    'ViralIntelligenceEngine',
    'PerformanceIntelligenceEngine',
    'CrisisIntelligenceEngine',
    'GeographicIntelligenceEngine',
    'TemporalIntelligenceEngine',
    'CollaborationIntelligenceEngine',
    'MonetizationIntelligenceEngine',
    'ComplianceIntelligenceEngine',
    'RealTimeIntelligenceEngine',
    
    # Specialized Predictors and Analyzers
    'SemanticAnalyzer',
    'AlgorithmPredictor',
    'BehaviorPredictor',
    'TrendPredictor',
    'ROIOptimizer',
    'ThreatDetector',
]

# Version et metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Distribution AI Intelligence - 53 Agents IA Spécialisés Enterprise"

# Configuration des 53 Agents IA Distribution
AI_AGENTS_CONFIG = {
    'content_adaptation_agents': 15,
    'audience_targeting_agents': 12,
    'viral_optimization_agents': 10,
    'performance_agents': 8,
    'crisis_management_agents': 8,
    'total_agents': 53
}

# Points d'entrée principaux pour l'orchestration IA
def get_ai_orchestrator():
    """Retourne l'orchestrateur principal des 53 agents IA."""
    return AIOrchestrator()

def get_distribution_coordinator():
    """Retourne le coordinateur distribution multi-plateforme."""
    return DistributionAICoordinator()

def initialize_all_agents():
    """Initialise tous les 53 agents IA spécialisés."""
    orchestrator = get_ai_orchestrator()
    return orchestrator.initialize_all_agents()