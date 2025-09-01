"""Surveillance Database Module Index
=================================

Main entry point and factory functions for the surveillance system.
Provides easy access to all surveillance components and utilities.

Author: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All Rights Reserved.

WARNING: This code and concept are protected intellectual property.
Any unauthorized use, copying, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from . import (
    ContentMonitoringEngine, AlertManager, SurveillanceAnalytics,
    YouTubeConnector, InstagramConnector, TikTokConnector, TwitterConnector,
    EvidenceCollector, ViolationReportGenerator, AudioDetectionEngine,
    VideoDetectionEngine, ImageDetectionEngine, TextDetectionEngine
)

logger = logging.getLogger(__name__)


class SurveillanceSystemFactory:
    """
    Factory class for creating and managing surveillance system components.
    
    Provides centralized configuration and initialization of all surveillance
    modules with proper dependency management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.components: Dict[str, Any] = {}
        self.initialized = False
        
        # Detection engines
        self.detection_engines: Dict[str, Any] = {}
        
        # Platform connectors
        self.platform_connectors: Dict[str, Any] = {}
        
        # Alert and monitoring systems
        self.alert_manager: Optional[AlertManager] = None
        self.monitoring_engine: Optional[ContentMonitoringEngine] = None
        self.analytics: Optional[SurveillanceAnalytics] = None
        self.evidence_collector: Optional[EvidenceCollector] = None
        
        logger.info("SurveillanceSystemFactory initialized")
    
    async def initialize(self) -> bool:
        """Initialize all surveillance components with proper dependency management."""
        try:
            if self.initialized:
                logger.warning("Surveillance system already initialized")
                return True
            
            logger.info("Initializing surveillance system components...")
            
            # Step 1: Initialize detection engines
            await self._initialize_detection_engines()
            
            # Step 2: Initialize platform connectors
            await self._initialize_platform_connectors()
            
            # Step 3: Initialize core monitoring systems
            await self._initialize_core_systems()
            
            # Step 4: Initialize alert and reporting systems
            await self._initialize_alert_systems()
            
            # Step 5: Start monitoring processes
            await self._start_monitoring()
            
            self.initialized = True
            logger.info("Surveillance system successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize surveillance system: {str(e)}")
            await self.cleanup()
            return False
    
    async def _initialize_detection_engines(self):
        """Initialize all content detection engines."""
        engines_config = self.config.get('detection_engines', {})
        
        # Audio detection engine
        if engines_config.get('audio', {}).get('enabled', True):
            audio_config = engines_config.get('audio', {})
            self.detection_engines['audio'] = AudioDetectionEngine(audio_config)
            await self.detection_engines['audio'].initialize()
            logger.info("Audio detection engine initialized")
        
        # Video detection engine
        if engines_config.get('video', {}).get('enabled', True):
            video_config = engines_config.get('video', {})
            self.detection_engines['video'] = VideoDetectionEngine(video_config)
            await self.detection_engines['video'].initialize()
            logger.info("Video detection engine initialized")
        
        # Image detection engine
        if engines_config.get('image', {}).get('enabled', True):
            image_config = engines_config.get('image', {})
            self.detection_engines['image'] = ImageDetectionEngine(image_config)
            await self.detection_engines['image'].initialize()
            logger.info("Image detection engine initialized")
        
        # Text detection engine
        if engines_config.get('text', {}).get('enabled', True):
            text_config = engines_config.get('text', {})
            self.detection_engines['text'] = TextDetectionEngine(text_config)
            await self.detection_engines['text'].initialize()
            logger.info("Text detection engine initialized")
    
    async def _initialize_platform_connectors(self):
        """Initialize platform-specific connectors."""
        connectors_config = self.config.get('platform_connectors', {})
        
        # YouTube connector
        if connectors_config.get('youtube', {}).get('enabled', False):
            youtube_config = connectors_config.get('youtube', {})
            self.platform_connectors['youtube'] = YouTubeConnector(youtube_config)
            await self.platform_connectors['youtube'].initialize()
            logger.info("YouTube connector initialized")
        
        # Instagram connector
        if connectors_config.get('instagram', {}).get('enabled', False):
            instagram_config = connectors_config.get('instagram', {})
            self.platform_connectors['instagram'] = InstagramConnector(instagram_config)
            await self.platform_connectors['instagram'].initialize()
            logger.info("Instagram connector initialized")
        
        # TikTok connector
        if connectors_config.get('tiktok', {}).get('enabled', False):
            tiktok_config = connectors_config.get('tiktok', {})
            self.platform_connectors['tiktok'] = TikTokConnector(tiktok_config)
            await self.platform_connectors['tiktok'].initialize()
            logger.info("TikTok connector initialized")
        
        # Twitter connector
        if connectors_config.get('twitter', {}).get('enabled', False):
            twitter_config = connectors_config.get('twitter', {})
            self.platform_connectors['twitter'] = TwitterConnector(twitter_config)
            await self.platform_connectors['twitter'].initialize()
            logger.info("Twitter connector initialized")
    
    async def _initialize_core_systems(self):
        """Initialize core monitoring and analytics systems."""
        core_config = self.config.get('core_systems', {})
        
        # Content monitoring engine
        monitoring_config = core_config.get('monitoring', {})
        self.monitoring_engine = ContentMonitoringEngine(
            monitoring_config, 
            self.detection_engines,
            self.platform_connectors
        )
        await self.monitoring_engine.initialize()
        logger.info("Content monitoring engine initialized")
        
        # Analytics system
        analytics_config = core_config.get('analytics', {})
        self.analytics = SurveillanceAnalytics(analytics_config)
        await self.analytics.initialize()
        logger.info("Surveillance analytics initialized")
        
        # Evidence collector
        evidence_config = core_config.get('evidence', {})
        self.evidence_collector = EvidenceCollector(evidence_config)
        await self.evidence_collector.initialize()
        logger.info("Evidence collector initialized")
    
    async def _initialize_alert_systems(self):
        """Initialize alert and notification systems."""
        alert_config = self.config.get('alert_systems', {})
        
        self.alert_manager = AlertManager(
            alert_config,
            analytics=self.analytics,
            evidence_collector=self.evidence_collector
        )
        await self.alert_manager.initialize()
        logger.info("Alert manager initialized")
    
    async def _start_monitoring(self):
        """Start active monitoring processes."""
        if self.monitoring_engine:
            await self.monitoring_engine.start_monitoring()
            logger.info("Active monitoring started")
    
    async def cleanup(self):
        """Cleanup all surveillance components."""
        logger.info("Cleaning up surveillance system...")
        
        # Stop monitoring
        if self.monitoring_engine:
            await self.monitoring_engine.stop_monitoring()
        
        # Cleanup detection engines
        for engine_name, engine in self.detection_engines.items():
            try:
                await engine.cleanup()
                logger.info(f"Cleaned up {engine_name} detection engine")
            except Exception as e:
                logger.error(f"Error cleaning up {engine_name} engine: {str(e)}")
        
        # Cleanup platform connectors
        for platform_name, connector in self.platform_connectors.items():
            try:
                await connector.cleanup()
                logger.info(f"Cleaned up {platform_name} connector")
            except Exception as e:
                logger.error(f"Error cleaning up {platform_name} connector: {str(e)}")
        
        # Cleanup core systems
        for system_name, system in [
            ('alert_manager', self.alert_manager),
            ('analytics', self.analytics),
            ('evidence_collector', self.evidence_collector),
            ('monitoring_engine', self.monitoring_engine)
        ]:
            if system:
                try:
                    await system.cleanup()
                    logger.info(f"Cleaned up {system_name}")
                except Exception as e:
                    logger.error(f"Error cleaning up {system_name}: {str(e)}")
        
        self.initialized = False
        logger.info("Surveillance system cleanup completed")
    
    def get_component(self, component_type: str, name: Optional[str] = None) -> Any:
        """Get a specific surveillance component."""
        if component_type == "detection_engines":
            if name:
                return self.detection_engines.get(name)
            return self.detection_engines
        
        elif component_type == "platform_connectors":
            if name:
                return self.platform_connectors.get(name)
            return self.platform_connectors
        
        elif component_type == "alert_manager":
            return self.alert_manager
        
        elif component_type == "monitoring_engine":
            return self.monitoring_engine
        
        elif component_type == "analytics":
            return self.analytics
        
        elif component_type == "evidence_collector":
            return self.evidence_collector
        
        else:
            logger.warning(f"Unknown component type: {component_type}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            'initialized': self.initialized,
            'timestamp': datetime.utcnow().isoformat(),
            'detection_engines': {},
            'platform_connectors': {},
            'core_systems': {}
        }
        
        # Detection engines status
        for name, engine in self.detection_engines.items():
            try:
                status['detection_engines'][name] = {
                    'active': hasattr(engine, 'is_active') and engine.is_active,
                    'last_check': getattr(engine, 'last_check', None)
                }
            except Exception as e:
                status['detection_engines'][name] = {'error': str(e)}
        
        # Platform connectors status
        for name, connector in self.platform_connectors.items():
            try:
                status['platform_connectors'][name] = {
                    'connected': hasattr(connector, 'is_connected') and connector.is_connected,
                    'last_sync': getattr(connector, 'last_sync', None)
                }
            except Exception as e:
                status['platform_connectors'][name] = {'error': str(e)}
        
        # Core systems status
        core_systems = {
            'alert_manager': self.alert_manager,
            'monitoring_engine': self.monitoring_engine,
            'analytics': self.analytics,
            'evidence_collector': self.evidence_collector
        }
        
        for name, system in core_systems.items():
            if system:
                try:
                    status['core_systems'][name] = {
                        'active': hasattr(system, 'is_active') and system.is_active,
                        'last_activity': getattr(system, 'last_activity', None)
                    }
                except Exception as e:
                    status['core_systems'][name] = {'error': str(e)}
            else:
                status['core_systems'][name] = {'status': 'not_initialized'}
        
        return status


# Global factory instance
_surveillance_factory: Optional[SurveillanceSystemFactory] = None


def create_surveillance_system(config: Dict[str, Any]) -> SurveillanceSystemFactory:
    """
    Create a new surveillance system factory with the given configuration.
    
    Args:
        config: Configuration dictionary for the surveillance system
        
    Returns:
        SurveillanceSystemFactory instance
    """
    global _surveillance_factory
    _surveillance_factory = SurveillanceSystemFactory(config)
    return _surveillance_factory


def get_surveillance_system() -> Optional[SurveillanceSystemFactory]:
    """
    Get the current surveillance system factory instance.
    
    Returns:
        Current SurveillanceSystemFactory instance or None if not created
    """
    return _surveillance_factory


async def initialize_surveillance_system(config: Dict[str, Any]) -> bool:
    """
    Create and initialize the surveillance system with the given configuration.
    
    Args:
        config: Configuration dictionary for the surveillance system
        
    Returns:
        True if initialization successful, False otherwise
    """
    factory = create_surveillance_system(config)
    return await factory.initialize()


async def shutdown_surveillance_system():
    """
Shutdown and cleanup the surveillance system."""
    global _surveillance_factory
    if _surveillance_factory:
        await _surveillance_factory.cleanup()
        _surveillance_factory = None
        try:
            # Initialize monitoring engine
            self.monitoring_engine = ContentMonitoringEngine(self.config.get("monitoring", {}))
            await self.monitoring_engine.initialize()
            
            # Initialize alert manager
            self.alert_manager = AlertManager(self.config.get("alerts", {}))
            await self.alert_manager.initialize()
            
            # Initialize analytics
            self.analytics = SurveillanceAnalytics(self.config.get("analytics", {}))
            await self.analytics.initialize()
            
            # Initialize evidence collector
            self.evidence_collector = EvidenceCollector(self.config.get("evidence", {}))
            await self.evidence_collector.initialize()
            
            # Initialize platform connectors
            await self._initialize_platform_connectors()
            
            # Initialize reporting systems
            await self._initialize_reporting_systems()
            
            self.initialized = True
            logger.info("All surveillance components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize surveillance components: {e}")
            return False
    
    async def _initialize_platform_connectors(self) -> None:
        """Initialize platform-specific connectors."""
        connectors_config = self.config.get("platform_connectors", {})
        
        # YouTube connector
        if connectors_config.get("youtube", {}).get("enabled", False):
            self.platform_connectors["youtube"] = YouTubeConnector(
                connectors_config["youtube"]
            )
            await self.platform_connectors["youtube"].initialize()
        
        # Instagram connector
        if connectors_config.get("instagram", {}).get("enabled", False):
            self.platform_connectors["instagram"] = InstagramConnector(
                connectors_config["instagram"]
            )
            await self.platform_connectors["instagram"].initialize()
        
        # TikTok connector
        if connectors_config.get("tiktok", {}).get("enabled", False):
            self.platform_connectors["tiktok"] = TikTokConnector(
                connectors_config["tiktok"]
            )
            await self.platform_connectors["tiktok"].initialize()
        
        # Twitter connector
        if connectors_config.get("twitter", {}).get("enabled", False):
            self.platform_connectors["twitter"] = TwitterConnector(
                connectors_config["twitter"]
            )
            await self.platform_connectors["twitter"].initialize()
        
        # Generic web connector
        if connectors_config.get("generic_web", {}).get("enabled", False):
            self.platform_connectors["generic_web"] = GenericWebConnector(
                connectors_config["generic_web"]
            )
            await self.platform_connectors["generic_web"].initialize()
        
        logger.info(f"Initialized {len(self.platform_connectors)} platform connectors")
    
    async def _initialize_reporting_systems(self) -> None:
        """Initialize reporting systems."""
        reporting_config = self.config.get("reporting", {})
        
        # Compliance reporter
        if reporting_config.get("compliance", {}).get("enabled", False):
            self.reporting_systems["compliance"] = ComplianceReporter(
                reporting_config["compliance"]
            )
            await self.reporting_systems["compliance"].initialize()
        
        # Violation reporter
        if reporting_config.get("violations", {}).get("enabled", False):
            self.reporting_systems["violations"] = ViolationReporter(
                reporting_config["violations"]
            )
            await self.reporting_systems["violations"].initialize()
        
        logger.info(f"Initialized {len(self.reporting_systems)} reporting systems")
    
    async def start_monitoring(self, user_id: str, content_fingerprints: List[Dict[str, Any]]) -> bool:
        """Start surveillance monitoring for user content."""
        if not self.initialized:
            logger.error("Surveillance system not initialized")
            return False
        
        try:
            # Start content monitoring
            monitoring_result = await self.monitoring_engine.start_monitoring(
                user_id, content_fingerprints
            )
            
            if monitoring_result:
                logger.info(f"Started monitoring for user {user_id} with {len(content_fingerprints)} fingerprints")
                return True
            else:
                logger.error(f"Failed to start monitoring for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting monitoring for user {user_id}: {e}")
            return False
    
    async def stop_monitoring(self, user_id: str) -> bool:
        """Stop surveillance monitoring for user."""
        if not self.initialized:
            logger.error("Surveillance system not initialized")
            return False
        
        try:
            result = await self.monitoring_engine.stop_monitoring(user_id)
            logger.info(f"Stopped monitoring for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error stopping monitoring for user {user_id}: {e}")
            return False
    
    async def get_surveillance_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current surveillance status."""
        if not self.initialized:
            return {"error": "Surveillance system not initialized"}
        
        try:
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "initialized": self.initialized,
                "monitoring_active": await self.monitoring_engine.is_active(),
                "platform_connectors": len(self.platform_connectors),
                "reporting_systems": len(self.reporting_systems)
            }
            
            if user_id:
                status["user_monitoring"] = await self.monitoring_engine.get_user_status(user_id)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting surveillance status: {e}")
            return {"error": str(e)}
    
    async def generate_surveillance_report(self, 
                                         user_id: str, 
                                         report_type: str = "summary",
                                         date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate surveillance report for user."""
        if not self.initialized:
            return {"error": "Surveillance system not initialized"}
        
        try:
            # Get analytics data
            analytics_data = await self.analytics.get_user_analytics(user_id, date_range)
            
            # Generate report based on type
            if report_type == "compliance" and "compliance" in self.reporting_systems:
                report = await self.reporting_systems["compliance"].generate_report(
                    user_id, analytics_data
                )
            elif report_type == "violations" and "violations" in self.reporting_systems:
                report = await self.reporting_systems["violations"].generate_report(
                    user_id, analytics_data
                )
            else:
                # Default summary report
                report = {
                    "user_id": user_id,
                    "report_type": report_type,
                    "generated_at": datetime.utcnow().isoformat(),
                    "analytics": analytics_data,
                    "summary": await self._generate_summary_report(user_id, analytics_data)
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating surveillance report for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def _generate_summary_report(self, user_id: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary report from analytics data."""
        return {
            "total_violations_detected": analytics_data.get("violations_count", 0),
            "platforms_monitored": analytics_data.get("platforms_count", 0),
            "evidence_collected": analytics_data.get("evidence_count", 0),
            "average_detection_time": analytics_data.get("avg_detection_time", 0),
            "monitoring_effectiveness": analytics_data.get("effectiveness_score", 0)
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown surveillance system."""
        logger.info("Shutting down surveillance database system...")
        
        try:
            # Shutdown monitoring engine
            if self.monitoring_engine:
                await self.monitoring_engine.shutdown()
            
            # Shutdown alert manager
            if self.alert_manager:
                await self.alert_manager.shutdown()
            
            # Shutdown analytics
            if self.analytics:
                await self.analytics.shutdown()
            
            # Shutdown platform connectors
            for connector in self.platform_connectors.values():
                await connector.shutdown()
            
            # Shutdown reporting systems
            for reporter in self.reporting_systems.values():
                await reporter.shutdown()
            
            self.initialized = False
            logger.info("Surveillance database system shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during surveillance system shutdown: {e}")


# Global surveillance index instance
_surveillance_index: Optional[SurveillanceDatabaseIndex] = None


def get_surveillance_index() -> Optional[SurveillanceDatabaseIndex]:
    """Get global surveillance database index instance."""
    return _surveillance_index


def initialize_surveillance_index(config: Dict[str, Any]) -> SurveillanceDatabaseIndex:
    """
Initialize global surveillance database index."""
    global _surveillance_index
    _surveillance_index = SurveillanceDatabaseIndex(config)
    return _surveillance_index
