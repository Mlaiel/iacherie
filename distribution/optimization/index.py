"""
Distribution Optimization Module - Point d'entrée principal
Auteur: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise

Module d'optimisation avancée pour distribution multi-plateforme avec IA.
Includes 53 AI agents for comprehensive optimization.
"""

# Import core optimization engines
try:
    from .ai_optimization_engine import AIOptimizationEngine, OptimizationType, OptimizationPriority
except ImportError:
    AIOptimizationEngine = None

try:
    from .performance_optimizer import PerformanceOptimizer, PerformanceMetric
except ImportError:
    PerformanceOptimizer = None

try:
    from .cost_optimizer import CostOptimizer, CostCategory
except ImportError:
    CostOptimizer = None

try:
    from .conversion_optimizer import ConversionOptimizer, ConversionStage
except ImportError:
    ConversionOptimizer = None

# Import existing optimization components
try:
    from .ai_timing_optimizer import AITimingOptimizer
except ImportError:
    AITimingOptimizer = None

try:
    from .distribution_intelligence import DistributionIntelligence
except ImportError:
    DistributionIntelligence = None

try:
    from .hashtag_optimizer import HashtagOptimizer
except ImportError:
    HashtagOptimizer = None

try:
    from .queue_intelligence import QueueIntelligence
except ImportError:
    QueueIntelligence = None

# Exports publics du module
__all__ = [
    # Core Enterprise Optimizers
    'AIOptimizationEngine',
    'PerformanceOptimizer', 
    'CostOptimizer',
    'ConversionOptimizer',
    
    # Existing Components
    'AITimingOptimizer',
    'DistributionIntelligence',
    'HashtagOptimizer',
    'QueueIntelligence',
]

# Version et metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Optimization Module - 53 AI Agents + Advanced Optimizers"

# Configuration des optimiseurs enterprise
OPTIMIZATION_CONFIG = {
    'ai_optimization_enabled': True,
    'performance_monitoring': True,
    'cost_optimization': True,
    'conversion_tracking': True,
    'real_time_optimization': True,
    'multi_platform_support': True,
    'enterprise_features': True
}

# Points d'entrée principaux pour l'optimisation
def get_ai_optimization_engine():
    """Retourne le moteur d'optimisation IA principal."""
    if AIOptimizationEngine:
        return AIOptimizationEngine()
    return None

def get_performance_optimizer():
    """Retourne l'optimiseur de performance."""
    if PerformanceOptimizer:
        return PerformanceOptimizer()
    return None

def get_cost_optimizer():
    """Retourne l'optimiseur de coûts."""
    if CostOptimizer:
        return CostOptimizer()
    return None

def get_conversion_optimizer():
    """Retourne l'optimiseur de conversion."""
    if ConversionOptimizer:
        return ConversionOptimizer()
    return None

def initialize_all_optimizers():
    """Initialise tous les optimiseurs enterprise."""
    optimizers = {}
    
    if AIOptimizationEngine:
        optimizers['ai_optimization'] = get_ai_optimization_engine()
    if PerformanceOptimizer:
        optimizers['performance'] = get_performance_optimizer()
    if CostOptimizer:
        optimizers['cost'] = get_cost_optimizer() 
    if ConversionOptimizer:
        optimizers['conversion'] = get_conversion_optimizer()
    
    optimizers['status'] = f'{len(optimizers)} optimizers initialized'
    return optimizers