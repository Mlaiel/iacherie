"""Revenue Management System - Core Revenue Components

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVENUE MANAGEMENT SYSTEM - ENTERPRISE EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Developed by Expert Team:
🎯 Lead Dev IA: Fahed Mlaiel (Advanced AI/ML Architecture)
🛠️  Backend Senior: System Architecture & Performance Optimization  
🤖 ML Engineer: Revenue Forecasting & Optimization Algorithms
🗄️  DBA: Advanced Data Management & Analytics
🔒 Security Expert: Enterprise-Grade Security & Encryption
🚀 Microservices: Scalable Distributed Architecture
🎵 Audio Expert: Audio Revenue Stream Optimization
⚙️  DevOps: Production Infrastructure & Monitoring
🧠 IA Prompt Engineer: AI-Powered Decision Making
"""
# Import all revenue management modules
from .manager import RevenueManager
from .allocator import RevenueAllocator, create_revenue_allocator
from .analyzer import RevenueAnalyzer, create_revenue_analyzer
from .benchmarker import RevenueBenchmarker, create_revenue_benchmarker
from .calculator import RevenueCalculatorEngine, create_revenue_calculator
from .enhancer import RevenueEnhancer, create_revenue_enhancer
from .maximizer import RevenueMaximizer, create_revenue_maximizer
from .insights import RevenueInsightsEngine, create_insights_engine
from .simulator import RevenueSimulator, create_revenue_simulator
from .validator import RevenueValidator, create_revenue_validator
from .content_optimizer import ContentRevenueOptimizer, create_content_optimizer
from .intelligence import RevenueIntelligenceEngine, create_revenue_intelligence_engine
from .forecaster import RevenueForecastEngine, create_revenue_forecaster
from .optimizer import RevenueOptimizer, create_revenue_optimizer
from .tracker import RevenueTracker, create_revenue_tracker
from .stream_manager import RevenueStreamManager, create_stream_manager
from .platform_revenue_manager import PlatformRevenueManager, create_platform_revenue_manager
from .integration import RevenueIntegrationEngine, create_revenue_integration_engine

# Import new enterprise modules
from .distribution_manager import RevenueDistributionManager, create_distribution_manager
from .analytics_engine import RevenueAnalyticsEngine, create_revenue_analytics_engine
from .platform_integration_manager import PlatformIntegrationManager, create_platform_integration_manager
from .payment_processor import PaymentProcessingManager, create_payment_processing_manager

# Import central integration hub
from .index import RevenueManagementSystem, create_revenue_management_system, create_revenue_system_config

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "© 2025 Fahed Mlaiel"

# Export all public interfaces
__all__ = [
    # Core Revenue Management Classes
    'RevenueManager',
    'RevenueAllocator',
    'RevenueAnalyzer',
    'RevenueBenchmarker',
    'RevenueCalculatorEngine',
    'RevenueEnhancer',
    'RevenueMaximizer',
    'RevenueInsightsEngine',
    'RevenueSimulator',
    'RevenueValidator',
    'ContentRevenueOptimizer',
    'RevenueIntelligenceEngine',
    'RevenueForecastEngine',
    'RevenueOptimizer',
    'RevenueTracker',
    'RevenueStreamManager',
    'PlatformRevenueManager',
    'RevenueIntegrationEngine',
    
    # Enterprise Revenue Management Classes
    'RevenueDistributionManager',
    'RevenueAnalyticsEngine',
    'PlatformIntegrationManager',
    'PaymentProcessingManager',
    
    # Central Integration Hub
    'RevenueManagementSystem',
    
    # Factory Functions
    'create_revenue_allocator',
    'create_revenue_analyzer',
    'create_revenue_benchmarker',
    'create_revenue_calculator',
    'create_revenue_enhancer',
    'create_revenue_maximizer',
    'create_insights_engine',
    'create_revenue_simulator',
    'create_revenue_validator',
    'create_content_optimizer',
    'create_revenue_intelligence_engine',
    'create_revenue_forecaster',
    'create_revenue_optimizer',
    'create_revenue_tracker',
    'create_stream_manager',
    'create_platform_revenue_manager',
    'create_revenue_integration_engine',
    
    # Enterprise Factory Functions
    'create_distribution_manager',
    'create_revenue_analytics_engine',
    'create_platform_integration_manager',
    'create_payment_processing_manager',
    
    # System Factory Functions
    'create_revenue_management_system',
    'create_revenue_system_config',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__',
    '__copyright__'
]
