"""Crawlers Module - Main Coordinator
==================================

Professional crawler coordination system for IA-Influencer-Agent platform.
Implements comprehensive multi-platform content monitoring and protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path

# Import platform crawlers
from .platforms import (
    YouTubeCrawler, InstagramCrawler, TikTokCrawler,
    TwitterCrawler, FacebookCrawler, SpotifyCrawler,
    GenericCrawler
)

# Import utility modules
from .utils import (
    RateLimiter, ProxyManager, UserAgentRotator,
    ContentExtractor, SessionManager
)

# Import surveillance and analysis
from .surveillance import SurveillanceEngine, SurveillanceTarget, SurveillancePriority

# Import intelligence engines
from .content_intelligence import (
    ContentIntelligenceEngine, ContentType, ContentCategory,
    ContentFeatures, ContentInsights, create_content_intelligence_engine
)
from .trend_detection import (
    TrendDetectionEngine, TrendType, TrendScope, TrendCategory,
    TrendPattern, MarketOpportunity, ViralPrediction, create_trend_detection_engine
)
from .collaboration_matching import (
    CollaborationMatchingEngine, CollaborationType, CompatibilityLevel,
    CollaborationOpportunity, CollaborationMatch, create_collaboration_matching_engine
)
from .orchestration_engine import OrchestrationEngine, create_orchestration_engine
from .revenue_intelligence import RevenueIntelligenceEngine, create_revenue_intelligence_engine
from .analysis import ContentAnalyzer, ViolationType, AnalysisResult

logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """
Crawler system configuration."""
    max_concurrent_crawlers: int = 50
    default_rate_limit: float = 1.0
    enable_proxy_rotation: bool = True
    enable_user_agent_rotation: bool = True
    enable_content_analysis: bool = True
    enable_violation_detection: bool = True
    data_persistence_enabled: bool = True
    data_directory: str = "./data/crawlers"
    log_level: str = "INFO"

class CrawlerOrchestrator:
    """
    Main crawler orchestration system.
    
    This class coordinates all crawler activities including:
    - Platform-specific crawling
    - Content analysis and violation detection
    - Surveillance management
    - Resource optimization
    - Performance monitoring
    - Data persistence
    - Alert management
    """
    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
Initialize crawler orchestrator."""
        self.config = config or CrawlerConfig()
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        # Create data directory
        self.data_dir = Path(self.config.data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize core systems
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager() if self.config.enable_proxy_rotation else None
        self.user_agent_rotator = UserAgentRotator() if self.config.enable_user_agent_rotation else None
        self.content_extractor = ContentExtractor()
        self.session_manager = SessionManager(
            self.proxy_manager,
            self.user_agent_rotator,
            self.rate_limiter
        )
        
        # Initialize analysis system
        self.content_analyzer = ContentAnalyzer() if self.config.enable_content_analysis else None
        
        # Initialize surveillance system
        self.surveillance_engine = SurveillanceEngine()
        
        # Initialize platform crawlers
        self.crawlers = {
            'youtube': YouTubeCrawler(),
            'instagram': InstagramCrawler(),
            'tiktok': TikTokCrawler(),
            'twitter': TwitterCrawler(),
            'facebook': FacebookCrawler(),
            'spotify': SpotifyCrawler(),
            'generic': GenericCrawler()
        }
        
        # Configure crawlers with shared resources
        for crawler in self.crawlers.values():
            if hasattr(crawler, 'set_rate_limiter'):
                crawler.set_rate_limiter(self.rate_limiter)
            if hasattr(crawler, 'set_session_manager'):
                crawler.set_session_manager(self.session_manager)
        
        # Event callbacks
        self.violation_callbacks: List[Callable] = []
        self.analysis_callbacks: List[Callable] = []
        self.monitoring_callbacks: List[Callable] = []
        
        # Setup surveillance callbacks
        if self.surveillance_engine:
            self.surveillance_engine.add_violation_callback(self._handle_surveillance_violation)
            self.surveillance_engine.add_completion_callback(self._handle_surveillance_completion)
            self.surveillance_engine.add_error_callback(self._handle_surveillance_error)
        
        logger.info("Crawler orchestrator initialized successfully")
    
    async def start_monitoring(
        self,
        targets: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Start comprehensive monitoring for specified targets."""
        target_ids = {}
        
        for target_config in targets:
            try:
                platform = target_config['platform']
                target_type = target_config['type']
                identifier = target_config['identifier']
                priority = SurveillancePriority(target_config.get('priority', 2))
                frequency = target_config.get('frequency', 3600)
                metadata = target_config.get('metadata', {})
                
                target_id = await self.surveillance_engine.add_target(
                    platform=platform,
                    target_type=target_type,
                    identifier=identifier,
                    priority=priority,
                    frequency=frequency,
                    metadata=metadata
                )
                
                target_key = f"{platform}_{target_type}_{identifier}"
                target_ids[target_key] = target_id
                
                logger.info(f"Started monitoring: {target_key}")
                
            except Exception as e:
                logger.error(f"Failed to start monitoring for {target_config}: {e}")
        
        return target_ids
    
    async def analyze_content(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: str,
        content_type: str = "post"
    ) -> Optional[AnalysisResult]:
        """Analyze content for violations and similarities."""
        if not self.content_analyzer:
            logger.warning("Content analysis disabled")
            return True
        
        try:
            result = await self.content_analyzer.analyze_content(
                content_id=content_id,
                content_data=content_data,
                platform=platform,
                content_type=content_type
            )
            
            # Call analysis callbacks
            for callback in self.analysis_callbacks:
                try:
                    await callback(result)
                except Exception as e:
                    logger.error(f"Analysis callback error: {e}")
            
            # Handle violations if detected
            if result.is_violation and self.config.enable_violation_detection:
                await self._handle_content_violation(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Content analysis failed for {content_id}: {e}")
            return True
    
    async def _handle_surveillance_violation(
        self,
        target: SurveillanceTarget,
        violations: List[Dict[str, Any]]
    ) -> None:
        """Handle violations detected by surveillance system."""
        try:
            logger.warning(
                f"Surveillance violations detected for {target.platform}/{target.identifier}: "
                f"{len(violations)} violations"
            )
            
            # Call violation callbacks
            for callback in self.violation_callbacks:
                try:
                    await callback(target, violations)
                except Exception as e:
                    logger.error(f"Violation callback error: {e}")
            
            # Persist violation data if enabled
            if self.config.data_persistence_enabled:
                await self._persist_violation_data(target, violations)
                
        except Exception as e:
            logger.error(f"Surveillance violation handling failed: {e}")
    
    async def _handle_surveillance_completion(self, task) -> None:
        """Handle surveillance task completion."""
        logger.debug(f"Surveillance task completed: {task.task_id}")
    
    async def _handle_surveillance_error(self, task, error) -> None:
        """Handle surveillance task errors."""
        logger.error(f"Surveillance task failed: {task.task_id} - {error}")
    
    async def _handle_content_violation(self, analysis_result: AnalysisResult) -> None:
        """Handle content violations detected by analysis."""
        try:
            logger.warning(
                f"Content violation detected for {analysis_result.content_id}: "
                f"risk={analysis_result.risk_score:.2f}, "
                f"violations={len(analysis_result.violations_detected)}"
            )
            
            # Create violation record
            violation_data = {
                'content_id': analysis_result.content_id,
                'risk_score': analysis_result.risk_score,
                'violations': [
                    {
                        'type': v.violation_type.value,
                        'similarity_score': v.similarity_score,
                        'confidence': v.confidence,
                        'original_id': v.original_id,
                        'details': v.details
                    }
                    for v in analysis_result.violations_detected
                ],
                'recommendations': analysis_result.recommendations,
                'detected_at': analysis_result.processed_at.isoformat()
            }
            
            # Call violation callbacks
            for callback in self.violation_callbacks:
                try:
                    await callback(None, [violation_data])
                except Exception as e:
                    logger.error(f"Violation callback error: {e}")
                    
        except Exception as e:
            logger.error(f"Content violation handling failed: {e}")
    
    async def _persist_violation_data(
        self,
        target: SurveillanceTarget,
        violations: List[Dict[str, Any]]
    ) -> None:
        """Persist violation data to disk."""
        try:
            violations_dir = self.data_dir / "violations"
            violations_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{target.platform}_{target.target_id}_{timestamp}.json"
            filepath = violations_dir / filename
            
            data = {
                'target': {
                    'target_id': target.target_id,
                    'platform': target.platform,
                    'target_type': target.target_type,
                    'identifier': target.identifier,
                    'priority': target.priority.name
                },
                'violations': violations,
                'detected_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Persisted violation data to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to persist violation data: {e}")
    
    def add_violation_callback(self, callback: Callable) -> None:
        """Add callback for violation events."""
        self.violation_callbacks.append(callback)
    
    def add_analysis_callback(self, callback: Callable) -> None:
        """
Add callback for analysis events."""
        self.analysis_callbacks.append(callback)
    
    def add_monitoring_callback(self, callback: Callable) -> None:
        """
Add callback for monitoring events."""
        self.monitoring_callbacks.append(callback)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
Get comprehensive system status."""
        status = {
            'timestamp': datetime.now().isoformat(),
            'orchestrator': {
                'config': {
                    'max_concurrent_crawlers': self.config.max_concurrent_crawlers,
                    'proxy_rotation_enabled': self.config.enable_proxy_rotation,
                    'user_agent_rotation_enabled': self.config.enable_user_agent_rotation,
                    'content_analysis_enabled': self.config.enable_content_analysis,
                    'violation_detection_enabled': self.config.enable_violation_detection
                }
            },
            'crawlers': {
                platform: 'available' for platform in self.crawlers.keys()
            }
        }
        
        # Add subsystem status
        if self.surveillance_engine:
            status['surveillance'] = self.surveillance_engine.get_metrics().__dict__
        
        if self.content_analyzer:
            status['content_analysis'] = self.content_analyzer.get_analysis_statistics()
        
        if self.session_manager:
            status['session_manager'] = await self.session_manager.get_session_statistics()
        
        return status
    
    async def shutdown(self) -> None:
        """
Shutdown orchestrator gracefully."""
        logger.info("Shutting down crawler orchestrator...")
        
        if self.surveillance_engine:
            await self.surveillance_engine.shutdown()
        
        if self.session_manager:
            await self.session_manager.close_all_sessions()
        
        logger.info("Crawler orchestrator shutdown complete")


# Export main classes and functions
__all__ = [
    'CrawlerOrchestrator',
    'CrawlerConfig',
    'ViolationType',
    'SurveillancePriority',
    'YouTubeCrawler',
    'InstagramCrawler',
    'TikTokCrawler',
    'TwitterCrawler',
    'FacebookCrawler',
    'SpotifyCrawler',
    'GenericCrawler',
    'RateLimiter',
    'ProxyManager',
    'UserAgentRotator',
    'ContentExtractor',
    'SessionManager'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
