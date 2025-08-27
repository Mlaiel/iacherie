"""
Scheduling Agent Module - Enterprise Content Scheduling & Timing Optimization System

Intelligent scheduling, timing optimization, and automated content distribution system.
Handles optimal posting times, audience timezone analysis, automated scheduling, and 
multi-creator collaboration coordination with enterprise-grade performance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .scheduling_agent import SchedulingAgent, SchedulingAgentManager
from .schedule_optimizer import ScheduleOptimizer, TimingAnalyzer
from .content_scheduler import ContentScheduler, AutoScheduler
from .timezone_manager import TimezoneManager, GlobalScheduler
from .calendar_integrator import CalendarIntegrator, EventSynchronizer
from .performance_monitor import RealTimePerformanceMonitor, create_performance_monitor
from .collaboration_scheduler import CollaborationScheduler, create_collaboration_scheduler
from .seo_integration import SEOIntegrationScheduler, create_seo_integration_scheduler
from .campaign_manager import CampaignManager, create_campaign_manager
from .index import (
    initialize_module,
    get_module_info,
    get_component,
    shutdown_module,
    is_initialized,
    health_check,
    __module_info__,
    __version__,
    __author__
)

__all__ = [
    # Core Components
    'SchedulingAgent',
    'SchedulingAgentManager', 
    'ScheduleOptimizer',
    'TimingAnalyzer',
    'ContentScheduler',
    'AutoScheduler',
    'TimezoneManager',
    'GlobalScheduler',
    'CalendarIntegrator',
    'EventSynchronizer',
    
    # Enterprise Performance Monitoring
    'RealTimePerformanceMonitor',
    'create_performance_monitor',
    
    # Collaboration System
    'CollaborationScheduler', 
    'create_collaboration_scheduler',
    
    # SEO Integration
    'SEOIntegrationScheduler',
    'create_seo_integration_scheduler',
    
    # Campaign Management
    'CampaignManager',
    'create_campaign_manager',
    
    # Module Management
    'initialize_module',
    'get_module_info',
    'get_component',
    'shutdown_module',
    'is_initialized',
    'health_check',
    
    # Module Info
    '__module_info__',
    '__version__',
    '__author__'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
