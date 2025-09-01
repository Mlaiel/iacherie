"""Content Protection Service - Unified Service Interface
=====================================================

Professional unified interface for IA Influencer Agent content protection system.
Provides comprehensive protection orchestration and service coordination.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, modification ou distribution sans autorisation 
écrite explicite de l'auteur est strictement interdite et constitue une violation 
du droit d'auteur. Les contrevenants s'exposent à des poursuites judiciaires.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

# Import all core managers
from .content_protection_manager import (
    ContentProtectionManager, ProtectionConfig, ProtectionLevel, 
    ViolationType, ProtectionStatus, ViolationAlert, ProtectionReport
)
from .rights_manager import (
    RightsManager, RightsType, LicenseStatus, RightsTransferType,
    RightsOwnership, LicenseAgreement, RightsVerification
)
from .violation_detector import (
    ViolationDetector, DetectionMethod, ViolationSeverity, DetectionConfig,
    ViolationEvidence, DetectionReport
)
from .takedown_manager import (
    TakedownManager, TakedownType, TakedownStatus, PlatformTakedownMethod,
    TakedownRequest, DMCANotice, TakedownResponse, TakedownResult
)
from .protection_analytics import (
    ProtectionAnalytics, AnalyticsMetric, TimeGranularity, ReportType,
    ProtectionMetrics, ViolationTrend, PlatformAnalytics, ThreatIntelligence,
    AnalyticsReport
)

# Import new modules
from .fingerprinting_engine import (
    FingerprintingEngine, ContentType, FingerprintMethod, FingerprintResult,
    SimilarityMatch, FingerprintConfig
)
from .platform_crawler import (
    PlatformCrawler, PlatformType, CrawlMethod, ContentStatus,
    CrawlTarget, CrawledContent, CrawlResult
)
from .revenue_tracker import (
    RevenueTracker, RevenueType, PlatformRevenue, CompensationMethod,
    RevenueRecord, ViolationImpact, CompensationClaim, RevenueAnalytics
)


@dataclass
class ServiceConfig:
    """
Unified service configuration"""
    db_session: AsyncSession
    redis_client: Redis
    api_keys: Dict[str, str]
    ml_models_path: str
    enable_realtime_monitoring: bool
    auto_takedown_enabled: bool
    notification_settings: Dict[str, Any]
    legal_templates_path: str


@dataclass
class ProtectionSummary:
    """
Comprehensive protection status summary"""
    user_id: str
    total_content_protected: int
    active_violations: int
    resolved_violations: int
    pending_takedowns: int
    revenue_recovered: float
    protection_effectiveness: float
    last_scan: datetime
    next_scan: datetime


class ContentProtectionService:
    """
    Unified Content Protection Service.
    
    Orchestrates all content protection components for comprehensive
    multi-format content protection across platforms.
    """
    
    def __init__(self, config: ServiceConfig):
        """
        Initialize ContentProtectionService.
        
        Args:
            config: Service configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core managers
        self.protection_manager = ContentProtectionManager(
            config.db_session, config.redis_client, 
            None, None  # Will be injected
        )
        
        self.rights_manager = RightsManager(
            config.db_session, config.redis_client
        )
        
        self.violation_detector = ViolationDetector(
            config.db_session, config.redis_client
        )
        
        self.takedown_manager = TakedownManager(
            config.db_session, config.redis_client
        )
        
        self.protection_analytics = ProtectionAnalytics(
            config.db_session, config.redis_client
        )
        
        # Initialize new components
        self.fingerprinting_engine = FingerprintingEngine(
            config.db_session, config.redis_client, config.ml_models_path
        )
        
        self.platform_crawler = PlatformCrawler(
            config.db_session, config.redis_client, config.api_keys
        )
        
        self.revenue_tracker = RevenueTracker(
            config.db_session, config.redis_client, config.api_keys
        )
        
        # Service state
        self.is_initialized = False
        self.monitoring_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> bool:
        """
        Initialize the content protection service.
        
        Returns:
            Initialization success status
        """
        try:
            self.logger.info("Initializing Content Protection Service...")
            
            # Initialize fingerprinting engine
            # (Model initialization happens in constructor)
            
            # Start platform crawler session
            await self.platform_crawler.start_crawler_session()
            
            # Start real-time monitoring if enabled
            if self.config.enable_realtime_monitoring:
                await self._start_realtime_monitoring()
            
            self.is_initialized = True
            self.logger.info("Content Protection Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing service: {str(e)}")
            return False
    
    async def shutdown(self):
        """Shutdown the content protection service"""
        try:
            self.logger.info("Shutting down Content Protection Service...")
            
            # Stop monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Close platform crawler session
            await self.platform_crawler.close_crawler_session()
            
            self.is_initialized = False
            self.logger.info("Content Protection Service shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    async def protect_content(self, user_id: str, content_data: Dict[str, Any],
                            protection_config: Optional[ProtectionConfig] = None) -> Dict[str, Any]:
        """
        Comprehensive content protection setup.
        
        Args:
            user_id: User identifier
            content_data: Content data and metadata
            protection_config: Protection configuration (optional)
            
        Returns:
            Protection setup result
        """
        try:
            content_id = content_data.get('content_id', str(uuid.uuid4()))
            content_type = ContentType(content_data.get('content_type', 'audio'))
            
            # Step 1: Extract fingerprints
            fingerprints = await self.fingerprinting_engine.extract_fingerprint(
                content_data['file_data'],
                content_type
            )
            
            if not fingerprints:
                return {'success': False, 'error': 'Failed to extract fingerprints'}
            
            # Step 2: Register ownership rights
            ownership_id = await self.rights_manager.register_ownership(
                content_id, user_id, content_data.get('rights_data', {})
            )
            
            # Step 3: Enable content protection
            if protection_config is None:
                protection_config = self._get_default_protection_config(content_id, content_type)
            
            protection_enabled = await self.protection_manager.enable_content_protection(
                content_id, protection_config
            )
            
            if not protection_enabled:
                return {'success': False, 'error': 'Failed to enable protection'}
            
            # Step 4: Configure violation detection
            detection_config = DetectionConfig(
                content_id=content_id,
                detection_methods=[DetectionMethod.AUDIO_FINGERPRINT, DetectionMethod.METADATA_ANALYSIS],
                similarity_threshold=protection_config.similarity_threshold,
                scan_frequency=24,
                platforms_to_scan=protection_config.platforms_to_monitor,
                enable_realtime=self.config.enable_realtime_monitoring,
                alert_threshold=protection_config.similarity_threshold,
                auto_evidence_collection=True
            )
            
            detection_configured = await self.violation_detector.configure_detection(detection_config)
            
            # Step 5: Setup revenue tracking
            await self.revenue_tracker.sync_platform_revenue(
                user_id, 
                [PlatformRevenue.YOUTUBE, PlatformRevenue.SPOTIFY],
                (datetime.utcnow() - timedelta(days=30), datetime.utcnow())
            )
            
            return {
                'success': True,
                'content_id': content_id,
                'ownership_id': ownership_id,
                'fingerprints_extracted': len(fingerprints),
                'protection_enabled': protection_enabled,
                'detection_configured': detection_configured,
                'monitoring_active': self.config.enable_realtime_monitoring
            }
            
        except Exception as e:
            self.logger.error(f"Error protecting content: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def scan_and_respond(self, content_id: str) -> Dict[str, Any]:
        """
        Comprehensive violation scan and automated response.
        
        Args:
            content_id: Content identifier to scan for
            
        Returns:
            Scan and response results
        """
        try:
            # Step 1: Scan for violations
            violations = await self.violation_detector.scan_for_violations(content_id)
            
            if not violations:
                return {
                    'violations_found': 0,
                    'takedowns_initiated': 0,
                    'evidence_collected': 0
                }
            
            takedowns_initiated = 0
            evidence_collected = 0
            
            # Step 2: Process each violation
            for violation in violations:
                # Collect evidence
                evidence = await self.violation_detector.collect_violation_evidence(violation)
                evidence_collected += len(evidence)
                
                # Calculate revenue impact
                impact = await self.revenue_tracker.calculate_violation_impact(
                    violation.alert_id,
                    content_id,
                    {
                        'views': 10000,  # Would be extracted from platform data
                        'engagement': 500
                    }
                )
                
                # Initiate takedown if auto-takedown is enabled
                if (self.config.auto_takedown_enabled and 
                    violation.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]):
                    
                    takedown_data = {
                        'content_id': content_id,
                        'violation_id': violation.alert_id,
                        'platform': violation.platform,
                        'infringing_url': violation.detected_url,
                        'violation_type': violation.violation_type.value,
                        'evidence': evidence
                    }
                    
                    takedown_id = await self.takedown_manager.submit_takedown_request(takedown_data)
                    if takedown_id:
                        takedowns_initiated += 1
            
            return {
                'violations_found': len(violations),
                'takedowns_initiated': takedowns_initiated,
                'evidence_collected': evidence_collected,
                'violations': [
                    {
                        'alert_id': v.alert_id,
                        'platform': v.platform,
                        'similarity_score': v.similarity_score,
                        'severity': v.severity.value
                    }
                    for v in violations
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error in scan and respond: {str(e)}")
            return {'error': str(e)}
    
    async def get_comprehensive_status(self, user_id: str) -> ProtectionSummary:
        """
        Get comprehensive protection status for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Protection status summary
        """
        try:
            # Get protected content count
            protected_content = await self._get_protected_content_count(user_id)
            
            # Get violation statistics
            violation_stats = await self._get_user_violation_statistics(user_id)
            
            # Get takedown statistics
            takedown_stats = await self._get_user_takedown_statistics(user_id)
            
            # Get revenue data
            revenue_analytics = await self.revenue_tracker.generate_revenue_analytics(user_id)
            
            # Get scan schedule
            scan_schedule = await self._get_next_scan_schedule(user_id)
            
            summary = ProtectionSummary(
                user_id=user_id,
                total_content_protected=protected_content,
                active_violations=violation_stats.get('active_violations', 0),
                resolved_violations=violation_stats.get('resolved_violations', 0),
                pending_takedowns=takedown_stats.get('pending_takedowns', 0),
                revenue_recovered=float(revenue_analytics.loss_from_violations),
                protection_effectiveness=violation_stats.get('effectiveness', 0.0),
                last_scan=scan_schedule.get('last_scan', datetime.utcnow()),
                next_scan=scan_schedule.get('next_scan', datetime.utcnow())
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive status: {str(e)}")
            raise
    
    async def generate_protection_report(self, user_id: str, 
                                       report_type: str = "comprehensive",
                                       period_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive protection report.
        
        Args:
            user_id: User identifier
            report_type: Type of report to generate
            period_days: Report period in days
            
        Returns:
            Generated report data
        """
        try:
            # Generate analytics report
            analytics_report = await self.protection_analytics.generate_comprehensive_report(
                user_id, ReportType.EXECUTIVE_SUMMARY, period_days
            )
            
            # Generate revenue analytics
            revenue_analytics = await self.revenue_tracker.generate_revenue_analytics(
                user_id, period_days
            )
            
            # Get crawl statistics
            crawl_stats = await self.platform_crawler.get_crawl_statistics(
                None, period_days
            )
            
            # Compile comprehensive report
            report = {
                'report_id': str(uuid.uuid4()),
                'user_id': user_id,
                'report_type': report_type,
                'period_days': period_days,
                'generated_at': datetime.utcnow().isoformat(),
                
                # Protection metrics
                'protection_summary': analytics_report.executive_summary,
                'violation_trends': analytics_report.violation_trends,
                'platform_performance': analytics_report.platform_analytics,
                
                # Revenue metrics
                'revenue_summary': {
                    'total_revenue': float(revenue_analytics.total_revenue),
                    'revenue_by_platform': {k: float(v) for k, v in revenue_analytics.revenue_by_platform.items()},
                    'growth_rate': revenue_analytics.growth_rate,
                    'losses_from_violations': float(revenue_analytics.loss_from_violations),
                    'protection_roi': revenue_analytics.protection_roi
                },
                
                # Monitoring metrics
                'monitoring_summary': crawl_stats,
                
                # Recommendations
                'recommendations': await self._generate_recommendations(user_id, analytics_report, revenue_analytics)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating protection report: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _start_realtime_monitoring(self):
        """Start real-time monitoring tasks"""
        try:
            # Start violation monitoring task
            violation_task = asyncio.create_task(self._realtime_violation_monitor())
            self.monitoring_tasks.append(violation_task)
            
            # Start revenue monitoring task
            revenue_task = asyncio.create_task(self._realtime_revenue_monitor())
            self.monitoring_tasks.append(revenue_task)
            
            self.logger.info("Real-time monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting real-time monitoring: {str(e)}")
    
    async def _realtime_violation_monitor(self):
        """Real-time violation monitoring loop"""
        while True:
            try:
                # Get active protected content
                protected_content = await self._get_all_protected_content()
                
                # Scan for violations in batches
                for content_batch in self._batch_content(protected_content, 5):
                    scan_tasks = []
                    for content_id in content_batch:
                        task = self.violation_detector.scan_for_violations(content_id)
                        scan_tasks.append(task)
                    
                    # Execute scans
                    results = await asyncio.gather(*scan_tasks, return_exceptions=True)
                    
                    # Process results
                    for content_id, violations in zip(content_batch, results):
                        if isinstance(violations, list) and violations:
                            await self._handle_realtime_violations(content_id, violations)
                
                # Wait before next scan cycle
                await asyncio.sleep(3600)  # 1 hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in real-time violation monitoring: {str(e)}")
                await asyncio.sleep(300)  # 5 minutes before retry
    
    async def _realtime_revenue_monitor(self):
        """Real-time revenue monitoring loop"""
        while True:
            try:
                # Get active users
                active_users = await self._get_active_users()
                
                # Sync revenue data for active users
                for user_id in active_users:
                    platforms = [PlatformRevenue.YOUTUBE, PlatformRevenue.SPOTIFY, 
                               PlatformRevenue.INSTAGRAM, PlatformRevenue.TIKTOK]
                    
                    date_range = (
                        datetime.utcnow() - timedelta(hours=24),
                        datetime.utcnow()
                    )
                    
                    await self.revenue_tracker.sync_platform_revenue(
                        user_id, platforms, date_range
                    )
                
                # Wait before next sync cycle
                await asyncio.sleep(21600)  # 6 hours
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in real-time revenue monitoring: {str(e)}")
                await asyncio.sleep(1800)  # 30 minutes before retry
    
    def _get_default_protection_config(self, content_id: str, content_type: ContentType) -> ProtectionConfig:
        """Get default protection configuration"""
        return ProtectionConfig(
            content_id=content_id,
            protection_level=ProtectionLevel.STANDARD,
            enable_automated_takedown=self.config.auto_takedown_enabled,
            similarity_threshold=0.80,
            platforms_to_monitor=['youtube', 'instagram', 'tiktok'],
            notification_settings={'email': True, 'webhook': True},
            watermark_enabled=True,
            encryption_enabled=True
        )
    
    def _batch_content(self, content_list: List[str], batch_size: int) -> List[List[str]]:
        """
Batch content list into smaller chunks"""
        for i in range(0, len(content_list), batch_size):
            yield content_list[i:i + batch_size]
    
    async def _handle_realtime_violations(self, content_id: str, violations: List[ViolationAlert]):
        """
Handle violations detected in real-time"""
        for violation in violations:
            if violation.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]:
                # Immediate response for critical violations
                await self.scan_and_respond(content_id)
    
    async def _get_protected_content_count(self, user_id: str) -> int:
        """
Get count of protected content for user"""
        # Implementation would query database
        return 15  # Placeholder
    
    async def _get_user_violation_statistics(self, user_id: str) -> Dict[str, Any]:
        """
Get violation statistics for user"""
        # Implementation would query database
        return {
            'active_violations': 3,
            'resolved_violations': 12,
            'effectiveness': 0.94
        }
    
    async def _get_user_takedown_statistics(self, user_id: str) -> Dict[str, Any]:
        """
Get takedown statistics for user"""
        # Implementation would query database
        return {'pending_takedowns': 2}
    
    async def _get_next_scan_schedule(self, user_id: str) -> Dict[str, datetime]:
        """
Get next scan schedule for user"""
        # Implementation would query scheduled scans
        return {
            'last_scan': datetime.utcnow() - timedelta(hours=2),
            'next_scan': datetime.utcnow() + timedelta(hours=22)
        }
    
    async def _generate_recommendations(self, user_id: str, analytics_report: Any, 
                                      revenue_analytics: RevenueAnalytics) -> List[Dict[str, str]]:
        """
Generate protection recommendations"""
        recommendations = []
        
        # Analyze protection effectiveness
        if revenue_analytics.protection_roi < 2.0:
            recommendations.append({
                'type': 'optimization',
                'title': 'Improve Protection ROI',
                'description': 'Consider adjusting protection settings or platforms monitored to improve return on investment.',
                'priority': 'medium'
            })
        
        # Analyze violation trends
        if analytics_report.violation_trends:
            recommendations.append({
                'type': 'monitoring',
                'title': 'Increase Monitoring Frequency',
                'description': 'Recent violation trends suggest more frequent monitoring may be beneficial.',
                'priority': 'high'
            })
        
        # Revenue optimization
        if revenue_analytics.growth_rate < 0.1:
            recommendations.append({
                'type': 'revenue',
                'title': 'Revenue Growth Opportunity',
                'description': 'Consider expanding to additional platforms to increase revenue potential.',
                'priority': 'low'
            })
        
        return recommendations
    
    async def _get_all_protected_content(self) -> List[str]:
        """
Get all protected content IDs"""
        # Implementation would query database
        return ['content_1', 'content_2', 'content_3']
    
    async def _get_active_users(self) -> List[str]:
        """
Get active user IDs"""
        # Implementation would query database
        return ['user_1', 'user_2', 'user_3']


# Convenience functions for easy service setup

async def initialize_protection_service(config: ServiceConfig) -> ContentProtectionService:
    """
    Initialize and configure content protection service.
    
    Args:
        config: Service configuration
        
    Returns:
        Initialized content protection service
    """
    service = ContentProtectionService(config)
    success = await service.initialize()
    
    if not success:
        raise RuntimeError("Failed to initialize content protection service")
    
    return service


async def quick_protection_setup(user_id: str, content_data: Dict[str, Any],
                               service: ContentProtectionService) -> Dict[str, Any]:
    """
    Quick setup for content protection.
    
    Args:
        user_id: User identifier
        content_data: Content data and metadata
        service: Initialized protection service
        
    Returns:
        Protection setup result
    """
    return await service.protect_content(user_id, content_data)

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

# Import all main components
from .content_protection_manager import (
    ContentProtectionManager,
    ProtectionConfig,
    ProtectionLevel,
    ViolationType,
    ProtectionStatus,
    ViolationAlert,
    ProtectionReport
)

from .rights_manager import (
    RightsManager,
    RightsType,
    LicenseStatus,
    RightsTransferType,
    RightsOwnership,
    LicenseAgreement,
    RightsVerification
)

from .violation_detector import (
    ViolationDetector,
    DetectionMethod,
    ViolationSeverity,
    DetectionConfig,
    ViolationEvidence,
    DetectionReport
)

from .takedown_manager import (
    TakedownManager,
    TakedownType,
    TakedownStatus,
    PlatformTakedownMethod,
    TakedownRequest,
    DMCANotice,
    TakedownResponse,
    TakedownResult
)

from .protection_analytics import (
    ProtectionAnalytics,
    AnalyticsMetric,
    TimeGranularity,
    ReportType,
    ProtectionMetrics,
    ViolationTrend,
    PlatformAnalytics,
    ThreatIntelligence,
    AnalyticsReport
)


class ContentProtectionService:
    """
    Unified Content Protection Service.
    
    Orchestrates all content protection components and provides
    a simplified interface for comprehensive content protection.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize ContentProtectionService.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.protection_manager = ContentProtectionManager(db_session, redis_client)
        self.rights_manager = RightsManager(db_session, redis_client)
        self.violation_detector = ViolationDetector(db_session, redis_client)
        self.takedown_manager = TakedownManager(db_session, redis_client)
        self.analytics = ProtectionAnalytics(db_session, redis_client)
        
        self.logger.info("Content Protection Service initialized")
    
    async def setup_complete_protection(self, content_id: str, user_id: str,
                                      protection_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up complete content protection workflow.
        
        Args:
            content_id: Content identifier
            user_id: User identifier
            protection_config: Complete protection configuration
            
        Returns:
            Setup results and status
        """
        try:
            results = {
                'content_id': content_id,
                'user_id': user_id,
                'setup_started': datetime.utcnow().isoformat(),
                'components': {}
            }
            
            # 1. Register content ownership
            if protection_config.get('register_ownership', True):
                ownership_id = await self.rights_manager.register_ownership(
                    content_id=content_id,
                    owner_id=user_id,
                    rights_data=protection_config.get('ownership_data', {
                        'rights_type': 'exclusive',
                        'percentage': 100.0,
                        'territory': ['WORLDWIDE'],
                        'media_types': ['ALL']
                    })
                )
                results['components']['ownership'] = {
                    'status': 'registered',
                    'ownership_id': ownership_id
                }
            
            # 2. Configure content protection
            if protection_config.get('enable_protection', True):
                config = ProtectionConfig(
                    content_id=content_id,
                    protection_level=ProtectionLevel(protection_config.get('protection_level', 'premium')),
                    enable_automated_takedown=protection_config.get('automated_takedown', True),
                    similarity_threshold=protection_config.get('similarity_threshold', 0.80),
                    platforms_to_monitor=protection_config.get('platforms', ['youtube', 'instagram', 'tiktok']),
                    notification_settings=protection_config.get('notifications', {'email': True}),
                    watermark_enabled=protection_config.get('watermark', True),
                    encryption_enabled=protection_config.get('encryption', True)
                )
                
                protection_enabled = await self.protection_manager.enable_content_protection(
                    content_id, config
                )
                results['components']['protection'] = {
                    'status': 'enabled' if protection_enabled else 'failed',
                    'config': config.__dict__
                }
            
            # 3. Configure violation detection
            if protection_config.get('enable_detection', True):
                detection_config = DetectionConfig(
                    content_id=content_id,
                    detection_methods=[
                        DetectionMethod.AUDIO_FINGERPRINT,
                        DetectionMethod.VIDEO_FINGERPRINT,
                        DetectionMethod.IMAGE_FINGERPRINT,
                        DetectionMethod.TEXT_SIMILARITY
                    ],
                    similarity_threshold=protection_config.get('detection_threshold', 0.75),
                    scan_frequency=protection_config.get('scan_frequency', 24),
                    platforms_to_scan=protection_config.get('platforms', ['youtube', 'instagram']),
                    enable_realtime=protection_config.get('realtime', True),
                    alert_threshold=protection_config.get('alert_threshold', 0.80),
                    auto_evidence_collection=True
                )
                
                detection_configured = await self.violation_detector.configure_detection(detection_config)
                results['components']['detection'] = {
                    'status': 'configured' if detection_configured else 'failed',
                    'config': detection_config.__dict__
                }
            
            # 4. Schedule initial protection scan
            if results['components'].get('detection', {}).get('status') == 'configured':
                initial_scan = await self.violation_detector.scan_for_violations(content_id)
                results['components']['initial_scan'] = {
                    'status': 'completed',
                    'violations_found': len(initial_scan),
                    'violations': [v.__dict__ for v in initial_scan[:5]]  # First 5 violations
                }
            
            results['setup_completed'] = datetime.utcnow().isoformat()
            results['overall_status'] = 'success'
            
            self.logger.info(f"Complete protection setup successful for content {content_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in complete protection setup: {str(e)}")
            results['setup_completed'] = datetime.utcnow().isoformat()
            results['overall_status'] = 'failed'
            results['error'] = str(e)
            return results
    
    async def get_protection_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive protection dashboard for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Complete protection dashboard data
        """
        try:
            dashboard = {
                'user_id': user_id,
                'generated_at': datetime.utcnow().isoformat(),
                'real_time_metrics': {},
                'recent_activity': {},
                'protection_summary': {},
                'alerts': {}
            }
            
            # Get real-time metrics
            dashboard['real_time_metrics'] = await self.analytics.get_real_time_metrics(user_id)
            
            # Get recent violation alerts
            recent_alerts = await self.protection_manager.get_violation_alerts(user_id, limit=10)
            dashboard['alerts']['recent_violations'] = [alert.__dict__ for alert in recent_alerts]
            
            # Get protection status for user's content
            # This would require querying user's content first
            dashboard['protection_summary'] = {
                'total_protected_content': 0,  # Would be calculated
                'active_monitoring': 0,        # Would be calculated
                'protection_effectiveness': 0.0  # Would be calculated
            }
            
            # Get recent takedown activity
            takedown_report = await self.takedown_manager.generate_takedown_report(user_id, 7)
            dashboard['recent_activity']['takedowns'] = takedown_report
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error generating protection dashboard: {str(e)}")
            return {'error': str(e), 'user_id': user_id}
    
    async def handle_violation_workflow(self, violation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complete violation detection and response workflow.
        
        Args:
            violation_data: Violation detection data
            
        Returns:
            Workflow execution results
        """
        try:
            workflow_results = {
                'violation_id': violation_data.get('violation_id'),
                'content_id': violation_data.get('content_id'),
                'workflow_started': datetime.utcnow().isoformat(),
                'steps': {}
            }
            
            # Step 1: Verify rights
            rights_verification = await self.rights_manager.verify_rights(
                violation_data['content_id'],
                violation_data['requester_id'],
                'usage'
            )
            
            workflow_results['steps']['rights_verification'] = {
                'result': rights_verification.result,
                'confidence': rights_verification.confidence_score,
                'verification_id': rights_verification.verification_id
            }
            
            # Step 2: Collect evidence if rights verified
            if rights_verification.result:
                # Create violation alert object for evidence collection
                violation_alert = ViolationAlert(
                    alert_id=violation_data['violation_id'],
                    content_id=violation_data['content_id'],
                    detected_url=violation_data['detected_url'],
                    platform=violation_data['platform'],
                    violation_type=ViolationType(violation_data.get('violation_type', 'unauthorized_use')),
                    severity=ViolationSeverity(violation_data.get('severity', 'medium')),
                    similarity_score=violation_data.get('similarity_score', 0.0),
                    confidence_score=violation_data.get('confidence_score', 0.0),
                    evidence=[],
                    detected_at=datetime.utcnow(),
                    status='processing',
                    location_data=violation_data.get('location_data', {})
                )
                
                evidence = await self.violation_detector.collect_violation_evidence(violation_alert)
                workflow_results['steps']['evidence_collection'] = {
                    'evidence_count': len(evidence),
                    'evidence_types': [e.evidence_type for e in evidence]
                }
                
                # Step 3: Submit takedown if evidence sufficient
                if len(evidence) > 0 and violation_data.get('auto_takedown', True):
                    takedown_data = {
                        'content_id': violation_data['content_id'],
                        'violation_id': violation_data['violation_id'],
                        'requester_id': violation_data['requester_id'],
                        'platform': violation_data['platform'],
                        'infringing_url': violation_data['detected_url'],
                        'original_content_url': violation_data.get('original_url', ''),
                        'description': f"Unauthorized use detected with {violation_data.get('similarity_score', 0):.1%} similarity",
                        'evidence_urls': [e.url for e in evidence if e.url],
                        'auto_generated': True
                    }
                    
                    takedown_id = await self.takedown_manager.submit_takedown_request(takedown_data)
                    workflow_results['steps']['takedown_submission'] = {
                        'submitted': True,
                        'takedown_id': takedown_id
                    }
            
            workflow_results['workflow_completed'] = datetime.utcnow().isoformat()
            workflow_results['overall_status'] = 'completed'
            
            return workflow_results
            
        except Exception as e:
            self.logger.error(f"Error in violation workflow: {str(e)}")
            workflow_results['workflow_completed'] = datetime.utcnow().isoformat()
            workflow_results['overall_status'] = 'failed'
            workflow_results['error'] = str(e)
            return workflow_results
    
    async def generate_comprehensive_report(self, user_id: str, 
                                          report_type: str = "monthly") -> Dict[str, Any]:
        """
        Generate comprehensive protection report across all components.
        
        Args:
            user_id: User identifier
            report_type: Type of report (daily, weekly, monthly, quarterly)
            
        Returns:
            Comprehensive protection report
        """
        try:
            period_days = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30,
                'quarterly': 90
            }.get(report_type, 30)
            
            # Generate analytics report
            analytics_report = await self.analytics.generate_comprehensive_report(
                user_id=user_id,
                report_type=ReportType.EXECUTIVE_SUMMARY,
                period_days=period_days
            )
            
            # Generate takedown report
            takedown_report = await self.takedown_manager.generate_takedown_report(
                user_id=user_id,
                period_days=period_days
            )
            
            # Calculate ROI metrics
            roi_metrics = await self.analytics.calculate_roi_metrics(
                user_id=user_id,
                period_days=period_days
            )
            
            # Compile comprehensive report
            comprehensive_report = {
                'report_id': analytics_report.report_id,
                'user_id': user_id,
                'report_type': report_type,
                'period_days': period_days,
                'generated_at': datetime.utcnow().isoformat(),
                'analytics': analytics_report.__dict__,
                'takedowns': takedown_report,
                'roi_metrics': roi_metrics,
                'summary': {
                    'total_violations_detected': analytics_report.executive_summary.get('violations_detected', 0),
                    'total_takedowns_submitted': takedown_report.get('statistics', {}).get('total_requests', 0),
                    'protection_effectiveness': analytics_report.executive_summary.get('effectiveness', 0.0),
                    'roi_percentage': roi_metrics.get('roi_percentage', 0.0)
                }
            }
            
            return comprehensive_report
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {str(e)}")
            return {'error': str(e), 'user_id': user_id}


# Convenience functions for easy access

async def initialize_protection_service(db_session: AsyncSession, 
                                       redis_client: Redis) -> ContentProtectionService:
    """
    Initialize and return a ContentProtectionService instance.
    
    Args:
        db_session: Async database session
        redis_client: Redis client
        
    Returns:
        Initialized ContentProtectionService
    """
    return ContentProtectionService(db_session, redis_client)


async def quick_protection_setup(service: ContentProtectionService,
                                content_id: str, user_id: str,
                                protection_level: str = "premium") -> Dict[str, Any]:
    """
    Quick setup for standard content protection.
    
    Args:
        service: ContentProtectionService instance
        content_id: Content identifier
        user_id: User identifier
        protection_level: Protection level (basic, standard, premium, enterprise)
        
    Returns:
        Setup results
    """
    config = {
        'protection_level': protection_level,
        'enable_protection': True,
        'enable_detection': True,
        'automated_takedown': True,
        'platforms': ['youtube', 'instagram', 'tiktok', 'twitter'],
        'similarity_threshold': 0.80,
        'detection_threshold': 0.75,
        'realtime': True
    }
    
    return await service.setup_complete_protection(content_id, user_id, config)


# Export all components for external use
__all__ = [
    # Main service
    'ContentProtectionService',
    'initialize_protection_service',
    'quick_protection_setup',
    
    # Core managers
    'ContentProtectionManager',
    'RightsManager', 
    'ViolationDetector',
    'TakedownManager',
    'ProtectionAnalytics',
    
    # Configuration classes
    'ProtectionConfig',
    'DetectionConfig',
    
    # Enums
    'ProtectionLevel',
    'ViolationType',
    'ProtectionStatus',
    'RightsType',
    'LicenseStatus',
    'DetectionMethod',
    'ViolationSeverity',
    'TakedownType',
    'TakedownStatus',
    'AnalyticsMetric',
    'TimeGranularity',
    'ReportType',
    
    # Data classes
    'ViolationAlert',
    'ProtectionReport',
    'RightsOwnership',
    'LicenseAgreement',
    'ViolationEvidence',
    'TakedownRequest',
    'DMCANotice',
    'ProtectionMetrics',
    'AnalyticsReport'
]
