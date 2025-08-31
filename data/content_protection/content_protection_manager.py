"""Content Protection Manager
=========================

Advanced content protection and rights management system for multi-format content.
Handles detection, enforcement, and automated protection workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis
import json

from ..models.content_model import ContentModel
from ..models.protection_model import ProtectionModel
from ..fingerprinting.vector_matcher import VectorMatcher
from ..crawlers.platform_crawler import PlatformCrawler


class ProtectionLevel(Enum):
    """Content protection levels"""    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ViolationType(Enum):
    """Types of content violations"""    DIRECT_COPY = "direct_copy"
    PARTIAL_COPY = "partial_copy"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_USE = "unauthorized_use"
    REMIX_VIOLATION = "remix_violation"


class ProtectionStatus(Enum):
    """Protection status enumeration"""    ACTIVE = "active"
    PENDING = "pending"
    VIOLATED = "violated"
    RESOLVED = "resolved"
    DISABLED = "disabled"


@dataclass
class ProtectionConfig:
    """Content protection configuration"""    content_id: str
    protection_level: ProtectionLevel
    enable_automated_takedown: bool
    similarity_threshold: float
    platforms_to_monitor: List[str]
    notification_settings: Dict[str, bool]
    watermark_enabled: bool
    encryption_enabled: bool


@dataclass
class ViolationAlert:
    """Content violation alert"""    violation_id: str
    content_id: str
    detected_url: str
    platform: str
    violation_type: ViolationType
    similarity_score: float
    evidence_urls: List[str]
    detected_at: datetime
    status: str
    severity: str


@dataclass
class ProtectionReport:
    """Protection effectiveness report"""    content_id: str
    protection_period: int
    total_scans: int
    violations_detected: int
    violations_resolved: int
    protection_effectiveness: float
    platforms_monitored: List[str]
    last_scan: datetime


class ContentProtectionManager:
    """    Professional content protection manager for IA Influencer Agent platform.
    
    Provides comprehensive protection for audio, video, image, and text content
    across multiple platforms with AI-powered detection and automated enforcement.
    """    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 vector_matcher: VectorMatcher, platform_crawler: PlatformCrawler):
        """        Initialize ContentProtectionManager.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            vector_matcher: Vector matching service for similarity detection
            platform_crawler: Platform crawler for content monitoring
        """        self.db_session = db_session
        self.redis = redis_client
        self.vector_matcher = vector_matcher
        self.platform_crawler = platform_crawler
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.scan_interval = 3600  # 1 hour
        self.cache_ttl = 1800  # 30 minutes
        self.batch_size = 100
        
        # Protection thresholds
        self.similarity_thresholds = {
            ProtectionLevel.BASIC: 0.85,
            ProtectionLevel.STANDARD: 0.80,
            ProtectionLevel.PREMIUM: 0.75,
            ProtectionLevel.ENTERPRISE: 0.70
        }
    
    async def enable_content_protection(self, content_id: str, 
                                      config: ProtectionConfig) -> bool:
        """        Enable protection for specific content.
        
        Args:
            content_id: Content identifier
            config: Protection configuration
            
        Returns:
            Success status
        """        try:
            # Validate content exists
            content = await self._get_content_by_id(content_id)
            if not content:
                self.logger.warning(f"Content not found: {content_id}")
                return False
            
            # Create protection record
            protection = ProtectionModel(
                id=str(uuid.uuid4()),
                content_id=content_id,
                user_id=content.user_id,
                protection_level=config.protection_level.value,
                similarity_threshold=config.similarity_threshold,
                platforms_to_monitor=json.dumps(config.platforms_to_monitor),
                notification_settings=json.dumps(config.notification_settings),
                watermark_enabled=config.watermark_enabled,
                encryption_enabled=config.encryption_enabled,
                automated_takedown=config.enable_automated_takedown,
                status=ProtectionStatus.ACTIVE.value,
                created_at=datetime.utcnow()
            )
            
            self.db_session.add(protection)
            await self.db_session.commit()
            
            # Initialize fingerprinting
            await self._initialize_fingerprinting(content_id, config)
            
            # Schedule monitoring
            await self._schedule_monitoring(content_id, config)
            
            # Cache protection status
            await self._cache_protection_status(content_id, True)
            
            self.logger.info(f"Protection enabled for content {content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling protection for {content_id}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def scan_for_violations(self, content_id: str) -> List[ViolationAlert]:
        """        Scan for content violations across monitored platforms.
        
        Args:
            content_id: Content identifier to scan for
            
        Returns:
            List of detected violations
        """        try:
            # Get protection config
            protection = await self._get_protection_config(content_id)
            if not protection:
                self.logger.warning(f"No protection config found for {content_id}")
                return []
            
            # Get content fingerprints
            fingerprints = await self._get_content_fingerprints(content_id)
            if not fingerprints:
                self.logger.warning(f"No fingerprints found for {content_id}")
                return []
            
            violations = []
            platforms = json.loads(protection.platforms_to_monitor)
            
            # Scan each platform
            for platform in platforms:
                platform_violations = await self._scan_platform_violations(
                    content_id, platform, fingerprints, protection.similarity_threshold
                )
                violations.extend(platform_violations)
            
            # Process and store violations
            for violation in violations:
                await self._store_violation(violation)
                
                # Trigger automated response if enabled
                if protection.automated_takedown:
                    await self._trigger_automated_response(violation)
            
            # Update scan timestamp
            await self._update_last_scan(content_id)
            
            self.logger.info(f"Scan completed for {content_id}, found {len(violations)} violations")
            return violations
            
        except Exception as e:
            self.logger.error(f"Error scanning violations for {content_id}: {str(e)}")
            return []
    
    async def get_protection_status(self, content_id: str) -> Dict[str, Any]:
        """        Get comprehensive protection status for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Protection status information
        """        try:
            # Check cache first
            cache_key = f"protection_status:{content_id}"
            cached_status = await self._get_from_cache(cache_key)
            
            if cached_status:
                return cached_status
            
            # Get protection record
            protection = await self._get_protection_config(content_id)
            if not protection:
                return {'protected': False, 'status': 'not_protected'}
            
            # Get violation statistics
            violations_stats = await self._get_violation_statistics(content_id)
            
            # Get latest scan info
            latest_scan = await self._get_latest_scan_info(content_id)
            
            # Calculate protection effectiveness
            effectiveness = await self._calculate_protection_effectiveness(content_id)
            
            status = {
                'protected': True,
                'protection_level': protection.protection_level,
                'status': protection.status,
                'similarity_threshold': protection.similarity_threshold,
                'platforms_monitored': json.loads(protection.platforms_to_monitor),
                'automated_takedown': protection.automated_takedown,
                'violations_detected': violations_stats.get('total_violations', 0),
                'violations_resolved': violations_stats.get('resolved_violations', 0),
                'protection_effectiveness': effectiveness,
                'last_scan': latest_scan.get('timestamp') if latest_scan else None,
                'next_scan': latest_scan.get('next_scheduled') if latest_scan else None,
                'active_alerts': violations_stats.get('active_alerts', 0)
            }
            
            # Cache status
            await self._save_to_cache(cache_key, status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting protection status for {content_id}: {str(e)}")
            return {'protected': False, 'error': str(e)}
    
    async def generate_protection_report(self, content_id: str, 
                                       period_days: int = 30) -> ProtectionReport:
        """        Generate comprehensive protection report.
        
        Args:
            content_id: Content identifier
            period_days: Report period in days
            
        Returns:
            Protection report
        """        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get protection data
            protection = await self._get_protection_config(content_id)
            if not protection:
                raise ValueError(f"No protection found for content {content_id}")
            
            # Get scan statistics
            scan_stats = await self._get_scan_statistics(content_id, start_date, end_date)
            
            # Get violation statistics
            violation_stats = await self._get_violation_statistics_period(
                content_id, start_date, end_date
            )
            
            # Calculate effectiveness
            effectiveness = await self._calculate_protection_effectiveness_period(
                content_id, start_date, end_date
            )
            
            # Get latest scan
            latest_scan = await self._get_latest_scan_info(content_id)
            
            report = ProtectionReport(
                content_id=content_id,
                protection_period=period_days,
                total_scans=scan_stats.get('total_scans', 0),
                violations_detected=violation_stats.get('total_violations', 0),
                violations_resolved=violation_stats.get('resolved_violations', 0),
                protection_effectiveness=effectiveness,
                platforms_monitored=json.loads(protection.platforms_to_monitor),
                last_scan=latest_scan.get('timestamp') if latest_scan else None
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating protection report for {content_id}: {str(e)}")
            raise
    
    async def disable_protection(self, content_id: str) -> bool:
        """        Disable protection for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Success status
        """        try:
            # Update protection status
            query = select(ProtectionModel).where(ProtectionModel.content_id == content_id)
            result = await self.db_session.execute(query)
            protection = result.scalar_one_or_none()
            
            if not protection:
                return False
            
            protection.status = ProtectionStatus.DISABLED.value
            protection.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            # Remove from monitoring schedule
            await self._remove_from_monitoring(content_id)
            
            # Clear cache
            await self._clear_protection_cache(content_id)
            
            self.logger.info(f"Protection disabled for content {content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling protection for {content_id}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def bulk_enable_protection(self, content_configs: List[Tuple[str, ProtectionConfig]]) -> Dict[str, bool]:
        """        Enable protection for multiple content items.
        
        Args:
            content_configs: List of (content_id, config) tuples
            
        Returns:
            Dictionary mapping content_id to success status
        """        results = {}
        
        for content_id, config in content_configs:
            try:
                success = await self.enable_content_protection(content_id, config)
                results[content_id] = success
            except Exception as e:
                self.logger.error(f"Error enabling protection for {content_id}: {str(e)}")
                results[content_id] = False
        
        return results
    
    async def get_violation_alerts(self, user_id: str, limit: int = 50) -> List[ViolationAlert]:
        """        Get recent violation alerts for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of alerts to return
            
        Returns:
            List of violation alerts
        """        try:
            # Query violations for user's content
            query = """                SELECT v.* FROM violations v
                JOIN content c ON v.content_id = c.id
                WHERE c.user_id = :user_id
                ORDER BY v.detected_at DESC
                LIMIT :limit
            """            
            result = await self.db_session.execute(
                query, {'user_id': user_id, 'limit': limit}
            )
            
            violations = result.fetchall()
            
            alerts = []
            for violation in violations:
                alert = ViolationAlert(
                    violation_id=violation.id,
                    content_id=violation.content_id,
                    detected_url=violation.detected_url,
                    platform=violation.platform,
                    violation_type=ViolationType(violation.violation_type),
                    similarity_score=violation.similarity_score,
                    evidence_urls=json.loads(violation.evidence_data or '[]'),
                    detected_at=violation.detected_at,
                    status=violation.status,
                    severity=violation.severity
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting violation alerts for user {user_id}: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _get_content_by_id(self, content_id: str) -> Optional[ContentModel]:
        """Get content by ID"""        query = select(ContentModel).where(ContentModel.id == content_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_protection_config(self, content_id: str) -> Optional[ProtectionModel]:
        """Get protection configuration"""        query = select(ProtectionModel).where(
            and_(
                ProtectionModel.content_id == content_id,
                ProtectionModel.status != ProtectionStatus.DISABLED.value
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def _initialize_fingerprinting(self, content_id: str, config: ProtectionConfig):
        """Initialize fingerprinting for content"""        # This would integrate with the fingerprinting module
        # to create initial fingerprints for the content
        pass
    
    async def _schedule_monitoring(self, content_id: str, config: ProtectionConfig):
        """Schedule regular monitoring for content"""        # Add to monitoring queue
        monitoring_data = {
            'content_id': content_id,
            'platforms': config.platforms_to_monitor,
            'interval': self.scan_interval,
            'next_scan': datetime.utcnow() + timedelta(seconds=self.scan_interval)
        }
        
        monitoring_key = f"monitoring_schedule:{content_id}"
        await self.redis.setex(
            monitoring_key, 
            self.scan_interval * 2, 
            json.dumps(monitoring_data, default=str)
        )
    
    async def _scan_platform_violations(self, content_id: str, platform: str, 
                                      fingerprints: Dict, threshold: float) -> List[ViolationAlert]:
        """Scan specific platform for violations"""        violations = []
        
        try:
            # Use platform crawler to search for similar content
            search_results = await self.platform_crawler.search_similar_content(
                platform, fingerprints, threshold
            )
            
            for result in search_results:
                if result['similarity_score'] >= threshold:
                    violation = ViolationAlert(
                        violation_id=str(uuid.uuid4()),
                        content_id=content_id,
                        detected_url=result['url'],
                        platform=platform,
                        violation_type=self._classify_violation_type(result),
                        similarity_score=result['similarity_score'],
                        evidence_urls=result.get('evidence_urls', []),
                        detected_at=datetime.utcnow(),
                        status='new',
                        severity=self._calculate_severity(result['similarity_score'])
                    )
                    violations.append(violation)
        
        except Exception as e:
            self.logger.error(f"Error scanning {platform} for violations: {str(e)}")
        
        return violations
    
    async def _get_content_fingerprints(self, content_id: str) -> Dict[str, Any]:
        """Get content fingerprints from database"""        # This would query the fingerprinting database
        # Placeholder implementation
        return {
            'audio_fingerprint': 'audio_hash_placeholder',
            'video_fingerprint': 'video_hash_placeholder',
            'image_fingerprint': 'image_hash_placeholder',
            'text_fingerprint': 'text_hash_placeholder'
        }
    
    async def _store_violation(self, violation: ViolationAlert):
        """Store violation in database"""        # Implementation to store violation record
        pass
    
    async def _trigger_automated_response(self, violation: ViolationAlert):
        """Trigger automated takedown response"""        # Implementation for automated DMCA takedown
        pass
    
    async def _classify_violation_type(self, result: Dict) -> ViolationType:
        """Classify the type of violation"""        similarity = result['similarity_score']
        
        if similarity >= 0.95:
            return ViolationType.DIRECT_COPY
        elif similarity >= 0.85:
            return ViolationType.PARTIAL_COPY
        elif similarity >= 0.75:
            return ViolationType.DERIVATIVE_WORK
        else:
            return ViolationType.UNAUTHORIZED_USE
    
    async def _calculate_severity(self, similarity_score: float) -> str:
        """Calculate violation severity"""        if similarity_score >= 0.95:
            return 'critical'
        elif similarity_score >= 0.85:
            return 'high'
        elif similarity_score >= 0.75:
            return 'medium'
        else:
            return 'low'
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """Save data to cache"""        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    async def _cache_protection_status(self, content_id: str, protected: bool):
        """Cache protection status"""        cache_key = f"protection_enabled:{content_id}"
        await self.redis.setex(cache_key, self.cache_ttl, str(protected))
    
    async def _get_violation_statistics(self, content_id: str) -> Dict[str, int]:
        """Get violation statistics for content"""        # Implementation would query violation database
        return {
            'total_violations': 5,
            'resolved_violations': 3,
            'active_alerts': 2
        }
    
    async def _get_latest_scan_info(self, content_id: str) -> Dict[str, Any]:
        """Get latest scan information"""        # Implementation would get scan timestamps
        return {
            'timestamp': datetime.utcnow() - timedelta(hours=1),
            'next_scheduled': datetime.utcnow() + timedelta(hours=1)
        }
    
    async def _calculate_protection_effectiveness(self, content_id: str) -> float:
        """Calculate protection effectiveness percentage"""        # Implementation would calculate based on violations detected vs resolved
        return 0.94  # 94% effectiveness placeholder
    
    async def _update_last_scan(self, content_id: str):
        """Update last scan timestamp"""        scan_key = f"last_scan:{content_id}"
        await self.redis.setex(scan_key, 86400, datetime.utcnow().isoformat())
    
    async def _remove_from_monitoring(self, content_id: str):
        """Remove content from monitoring schedule"""        monitoring_key = f"monitoring_schedule:{content_id}"
        await self.redis.delete(monitoring_key)
    
    async def _clear_protection_cache(self, content_id: str):
        """Clear all cached protection data"""        cache_keys = [
            f"protection_status:{content_id}",
            f"protection_enabled:{content_id}",
            f"last_scan:{content_id}"
        ]
        
        for key in cache_keys:
            await self.redis.delete(key)
    
    async def _get_scan_statistics(self, content_id: str, start_date: datetime, 
                                 end_date: datetime) -> Dict[str, int]:
        """Get scan statistics for period"""        # Implementation would query scan logs
        return {'total_scans': 24}  # Placeholder
    
    async def _get_violation_statistics_period(self, content_id: str, start_date: datetime,
                                             end_date: datetime) -> Dict[str, int]:
        """Get violation statistics for period"""        # Implementation would query violations in period
        return {
            'total_violations': 8,
            'resolved_violations': 6
        }
    
    async def _calculate_protection_effectiveness_period(self, content_id: str, 
                                                       start_date: datetime,
                                                       end_date: datetime) -> float:
        """Calculate protection effectiveness for period"""        # Implementation would calculate effectiveness for specific period
        return 0.92  # 92% effectiveness placeholder
