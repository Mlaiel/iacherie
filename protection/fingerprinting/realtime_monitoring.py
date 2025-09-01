"""🚨 Real-Time Content Protection Monitoring System
================================================

Integrates 35+ platform crawlers with enhanced fingerprinting engines
for real-time copyright violation detection and automated enforcement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
# HTTP client
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    logging.warning("aiohttp not available - HTTP features limited")
from pathlib import Path

# Import enhanced fingerprinting engines
try:
    from enhanced_audio import ChromaprintMLEngine, EnhancedAudioFingerprint
    from enhanced_video import VideoDeepLearningEngine, EnhancedVideoFingerprint
    from enhanced_image import ImageProtectionEngine, EnhancedImageFingerprint
except ImportError:
    # Fallback for direct execution
    ChromaprintMLEngine = None
    EnhancedAudioFingerprint = None
    VideoDeepLearningEngine = None
    EnhancedVideoFingerprint = None
    ImageProtectionEngine = None
    EnhancedImageFingerprint = None

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Types of copyright violations."""
    AUDIO_MATCH = "audio_match"
    VIDEO_MATCH = "video_match"
    IMAGE_MATCH = "image_match"
    PARTIAL_MATCH = "partial_match"
    SUSPICIOUS_CONTENT = "suspicious_content"

class ViolationSeverity(Enum):
    """Severity levels for violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ContentViolation:
    """Represents a detected content violation."""
    violation_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    similarity_score: float
    platform: str
    platform_content_id: str
    platform_url: str
    original_content_id: str
    detected_at: datetime
    fingerprint_data: Dict[str, Any]
    platform_metadata: Dict[str, Any]
    confidence_score: float
    automated_actions: List[str] = None
    
    def __post_init__(self):
        if self.automated_actions is None:
            self.automated_actions = []

@dataclass
class MonitoringTarget:
    """Content to monitor across platforms."""
    content_id: str
    content_type: str  # audio, video, image
    file_path: str
    fingerprint: Any  # The actual fingerprint object
    owner_id: str
    monitoring_enabled: bool = True
    platforms_to_monitor: Set[str] = None
    similarity_threshold: float = 0.85
    created_at: datetime = None
    
    def __post_init__(self):
        if self.platforms_to_monitor is None:
            self.platforms_to_monitor = set()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class RealTimeMonitoringEngine:
    """Real-time monitoring engine integrating crawlers and fingerprinting."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize fingerprinting engines
        if ChromaprintMLEngine:
            self.audio_engine = ChromaprintMLEngine(self.config.get('audio', {}))
        else:
            self.audio_engine = None
            
        if VideoDeepLearningEngine:
            self.video_engine = VideoDeepLearningEngine(self.config.get('video', {}))
        else:
            self.video_engine = None
            
        if ImageProtectionEngine:
            self.image_engine = ImageProtectionEngine(self.config.get('image', {}))
        else:
            self.image_engine = None
        
        # Monitoring state
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        self.active_crawlers: Dict[str, bool] = {}
        self.violation_handlers: List[Callable] = []
        
        # Performance metrics
        self.metrics = {
            'total_content_scanned': 0,
            'violations_detected': 0,
            'false_positives': 0,
            'automated_actions_taken': 0,
            'platforms_monitored': 0,
            'last_scan_time': None
        }
        
        # Platform configuration
        self.platform_configs = self._load_platform_configs()
        
        logger.info("RealTimeMonitoringEngine initialized with 35+ platform support")
    
    def _load_platform_configs(self) -> Dict[str, Dict]:
        """Load configuration for all supported platforms."""
        platforms = {
            # Major video platforms
            'youtube': {'priority': 'high', 'scan_interval': 300, 'api_limit': 1000},
            'tiktok': {'priority': 'high', 'scan_interval': 600, 'api_limit': 500},
            'instagram': {'priority': 'high', 'scan_interval': 600, 'api_limit': 200},
            'facebook': {'priority': 'medium', 'scan_interval': 900, 'api_limit': 200},
            'twitter': {'priority': 'medium', 'scan_interval': 300, 'api_limit': 300},
            'linkedin': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'vimeo': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 150},
            'dailymotion': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'twitch': {'priority': 'medium', 'scan_interval': 600, 'api_limit': 300},
            'kick': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 50},
            
            # Audio platforms
            'spotify': {'priority': 'high', 'scan_interval': 900, 'api_limit': 100},
            'soundcloud': {'priority': 'high', 'scan_interval': 600, 'api_limit': 200},
            'apple_music': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 100},
            'youtube_music': {'priority': 'high', 'scan_interval': 600, 'api_limit': 300},
            'deezer': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 100},
            'amazon_music': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 100},
            'bandcamp': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 50},
            'mixcloud': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 50},
            
            # Image and social platforms
            'pinterest': {'priority': 'medium', 'scan_interval': 900, 'api_limit': 200},
            'reddit': {'priority': 'medium', 'scan_interval': 600, 'api_limit': 300},
            'discord': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'telegram': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'whatsapp': {'priority': 'low', 'scan_interval': 3600, 'api_limit': 50},
            'snapchat': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 100},
            'bereal': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 50},
            'mastodon': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'threads': {'priority': 'medium', 'scan_interval': 900, 'api_limit': 200},
            
            # Content and publishing platforms
            'medium': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'substack': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 50},
            'patreon': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 100},
            'onlyfans': {'priority': 'medium', 'scan_interval': 1200, 'api_limit': 100},
            'clubhouse': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 50},
            'rumble': {'priority': 'low', 'scan_interval': 1800, 'api_limit': 100},
            'twine': {'priority': 'low', 'scan_interval': 3600, 'api_limit': 50},
            
            # Additional platforms
            'generic_web': {'priority': 'low', 'scan_interval': 3600, 'api_limit': 200}
        }
        
        logger.info(f"Loaded configuration for {len(platforms)} platforms")
        return platforms
    
    async def add_monitoring_target(self, content_path: str, content_type: str, owner_id: str, 
                                  platforms: Optional[Set[str]] = None, 
                                  apply_watermark: bool = False) -> str:
        """Add content to monitoring targets."""
        try:
            # Generate fingerprint based on content type
            if content_type == 'audio':
                fingerprint = await self.audio_engine.generate_fingerprint(content_path)
            elif content_type == 'video':
                fingerprint = await self.video_engine.generate_fingerprint(content_path)
            elif content_type == 'image':
                fingerprint = await self.image_engine.generate_fingerprint(content_path, apply_watermark=apply_watermark)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Create monitoring target
            content_id = fingerprint.file_id
            monitoring_target = MonitoringTarget(
                content_id=content_id,
                content_type=content_type,
                file_path=content_path,
                fingerprint=fingerprint,
                owner_id=owner_id,
                platforms_to_monitor=platforms or set(self.platform_configs.keys())
            )
            
            self.monitoring_targets[content_id] = monitoring_target
            
            logger.info(f"Added monitoring target: {content_id} ({content_type}) for {len(monitoring_target.platforms_to_monitor)} platforms")
            return content_id
            
        except Exception as e:
            logger.error(f"Error adding monitoring target: {e}")
            raise
    
    async def start_monitoring(self):
        """Start real-time monitoring across all platforms."""
        logger.info("Starting real-time content monitoring...")
        
        # Start platform crawlers
        crawler_tasks = []
        for platform, config in self.platform_configs.items():
            if platform in self.monitoring_targets or any(platform in target.platforms_to_monitor for target in self.monitoring_targets.values()):
                task = asyncio.create_task(self._monitor_platform(platform, config))
                crawler_tasks.append(task)
        
        # Start violation processor
        violation_task = asyncio.create_task(self._process_violations())
        
        # Start metrics updater
        metrics_task = asyncio.create_task(self._update_metrics())
        
        # Run all tasks concurrently
        try:
            await asyncio.gather(*crawler_tasks, violation_task, metrics_task)
        except Exception as e:
            logger.error(f"Error in monitoring tasks: {e}")
    
    async def _monitor_platform(self, platform: str, config: Dict):
        """Monitor a specific platform for content violations."""
        logger.info(f"Starting monitoring for platform: {platform}")
        
        while True:
            try:
                # Get crawler for platform
                crawler = await self._get_platform_crawler(platform)
                
                if crawler:
                    # Scan platform for potential violations
                    content_items = await crawler.scan_recent_content()
                    
                    # Process each content item
                    for content_item in content_items:
                        await self._process_content_item(platform, content_item)
                    
                    self.metrics['total_content_scanned'] += len(content_items)
                    self.metrics['last_scan_time'] = datetime.utcnow()
                
                # Wait before next scan
                await asyncio.sleep(config['scan_interval'])
                
            except Exception as e:
                logger.error(f"Error monitoring platform {platform}: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _get_platform_crawler(self, platform: str):
        """Get or create a crawler for the specified platform."""
        # This would typically import and instantiate the appropriate crawler
        # For now, return a mock crawler
        
        class MockCrawler:
            def __init__(self, platform_name):
                self.platform_name = platform_name
            
            async def scan_recent_content(self):
                # Mock content scanning
                return [
                    {
                        'platform_id': f'{self.platform_name}_content_1',
                        'url': f'https://{self.platform_name}.com/content/1',
                        'content_type': 'video',
                        'file_url': 'https://example.com/video.mp4',
                        'metadata': {'title': 'Sample Video', 'duration': 180},
                        'timestamp': datetime.utcnow()
                    }
                ]
        
        return MockCrawler(platform)
    
    async def _process_content_item(self, platform: str, content_item: Dict):
        """Process a single content item for violation detection."""
        try:
            content_type = content_item.get('content_type', 'unknown')
            
            # Download and analyze content
            if content_type in ['audio', 'video', 'image']:
                temp_file = await self._download_content(content_item['file_url'])
                
                if temp_file:
                    # Generate fingerprint for the downloaded content
                    suspect_fingerprint = await self._generate_fingerprint(temp_file, content_type)
                    
                    if suspect_fingerprint:
                        # Check against monitoring targets
                        violations = await self._check_for_violations(platform, content_item, suspect_fingerprint, content_type)
                        
                        # Process any detected violations
                        for violation in violations:
                            await self._handle_violation(violation)
                    
                    # Clean up temp file
                    await self._cleanup_temp_file(temp_file)
        
        except Exception as e:
            logger.error(f"Error processing content item: {e}")
    
    async def _download_content(self, url: str) -> Optional[str]:
        """Download content for analysis."""
        try:
            # Mock download - in production, this would actually download the file
            # For now, return None to skip actual downloading
            return None
        except Exception as e:
            logger.error(f"Error downloading content from {url}: {e}")
            return None
    
    async def _generate_fingerprint(self, file_path: str, content_type: str):
        """Generate fingerprint for suspect content."""
        try:
            if content_type == 'audio':
                return await self.audio_engine.generate_fingerprint(file_path)
            elif content_type == 'video':
                return await self.video_engine.generate_fingerprint(file_path)
            elif content_type == 'image':
                return await self.image_engine.generate_fingerprint(file_path)
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating fingerprint: {e}")
            return None
    
    async def _check_for_violations(self, platform: str, content_item: Dict, suspect_fingerprint: Any, content_type: str) -> List[ContentViolation]:
        """Check suspect content against monitoring targets."""
        violations = []
        
        try:
            for target_id, target in self.monitoring_targets.items():
                if (target.content_type == content_type and 
                    platform in target.platforms_to_monitor and 
                    target.monitoring_enabled):
                    
                    # Calculate similarity
                    similarity_score = await self._calculate_similarity(target.fingerprint, suspect_fingerprint, content_type)
                    
                    if similarity_score >= target.similarity_threshold:
                        # Create violation record
                        violation = ContentViolation(
                            violation_id=f"violation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{target_id}",
                            violation_type=self._determine_violation_type(content_type, similarity_score),
                            severity=self._determine_severity(similarity_score),
                            similarity_score=similarity_score,
                            platform=platform,
                            platform_content_id=content_item['platform_id'],
                            platform_url=content_item['url'],
                            original_content_id=target_id,
                            detected_at=datetime.utcnow(),
                            fingerprint_data=asdict(suspect_fingerprint) if hasattr(suspect_fingerprint, '__dict__') else {},
                            platform_metadata=content_item.get('metadata', {}),
                            confidence_score=getattr(suspect_fingerprint, 'confidence_score', 0.8)
                        )
                        
                        violations.append(violation)
                        logger.warning(f"Content violation detected: {violation.violation_id} (similarity: {similarity_score:.3f})")
        
        except Exception as e:
            logger.error(f"Error checking for violations: {e}")
        
        return violations
    
    async def _calculate_similarity(self, original_fingerprint: Any, suspect_fingerprint: Any, content_type: str) -> float:
        """Calculate similarity between fingerprints."""
        try:
            if content_type == 'audio':
                return await self.audio_engine.calculate_similarity(original_fingerprint, suspect_fingerprint)
            elif content_type == 'video':
                return await self.video_engine.calculate_similarity(original_fingerprint, suspect_fingerprint)
            elif content_type == 'image':
                return await self.image_engine.calculate_similarity(original_fingerprint, suspect_fingerprint)
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _determine_violation_type(self, content_type: str, similarity_score: float) -> ViolationType:
        """Determine violation type based on content and similarity."""
        if similarity_score >= 0.95:
            if content_type == 'audio':
                return ViolationType.AUDIO_MATCH
            elif content_type == 'video':
                return ViolationType.VIDEO_MATCH
            elif content_type == 'image':
                return ViolationType.IMAGE_MATCH
        elif similarity_score >= 0.8:
            return ViolationType.PARTIAL_MATCH
        else:
            return ViolationType.SUSPICIOUS_CONTENT
    
    def _determine_severity(self, similarity_score: float) -> ViolationSeverity:
        """Determine violation severity based on similarity score."""
        if similarity_score >= 0.95:
            return ViolationSeverity.CRITICAL
        elif similarity_score >= 0.9:
            return ViolationSeverity.HIGH
        elif similarity_score >= 0.85:
            return ViolationSeverity.MEDIUM
        else:
            return ViolationSeverity.LOW
    
    async def _handle_violation(self, violation: ContentViolation):
        """Handle a detected violation."""
        try:
            logger.warning(f"Handling violation: {violation.violation_id}")
            
            # Automated actions based on severity
            if violation.severity == ViolationSeverity.CRITICAL:
                violation.automated_actions.extend([
                    'immediate_takedown_request',
                    'dmca_filing',
                    'owner_notification'
                ])
            elif violation.severity == ViolationSeverity.HIGH:
                violation.automated_actions.extend([
                    'takedown_request',
                    'owner_notification'
                ])
            elif violation.severity == ViolationSeverity.MEDIUM:
                violation.automated_actions.extend([
                    'warning_notice',
                    'owner_notification'
                ])
            else:
                violation.automated_actions.append('flagged_for_review')
            
            # Execute automated actions
            for action in violation.automated_actions:
                await self._execute_automated_action(violation, action)
            
            # Notify violation handlers
            for handler in self.violation_handlers:
                try:
                    await handler(violation)
                except Exception as e:
                    logger.error(f"Error in violation handler: {e}")
            
            self.metrics['violations_detected'] += 1
            self.metrics['automated_actions_taken'] += len(violation.automated_actions)
            
        except Exception as e:
            logger.error(f"Error handling violation: {e}")
    
    async def _execute_automated_action(self, violation: ContentViolation, action: str):
        """Execute an automated enforcement action."""
        try:
            logger.info(f"Executing automated action: {action} for violation {violation.violation_id}")
            
            if action == 'immediate_takedown_request':
                await self._send_takedown_request(violation, urgent=True)
            elif action == 'takedown_request':
                await self._send_takedown_request(violation, urgent=False)
            elif action == 'dmca_filing':
                await self._file_dmca_notice(violation)
            elif action == 'owner_notification':
                await self._notify_content_owner(violation)
            elif action == 'warning_notice':
                await self._send_warning_notice(violation)
            elif action == 'flagged_for_review':
                await self._flag_for_manual_review(violation)
            
        except Exception as e:
            logger.error(f"Error executing automated action {action}: {e}")
    
    async def _send_takedown_request(self, violation: ContentViolation, urgent: bool = False):
        """Send takedown request to platform."""
        # Mock implementation
        logger.info(f"{'URGENT ' if urgent else ''}Takedown request sent for {violation.platform_url}")
    
    async def _file_dmca_notice(self, violation: ContentViolation):
        """File DMCA takedown notice."""
        # Mock implementation
        logger.info(f"DMCA notice filed for {violation.platform_url}")
    
    async def _notify_content_owner(self, violation: ContentViolation):
        """Notify content owner of violation."""
        # Mock implementation
        logger.info(f"Content owner notified of violation: {violation.violation_id}")
    
    async def _send_warning_notice(self, violation: ContentViolation):
        """Send warning notice to platform."""
        # Mock implementation
        logger.info(f"Warning notice sent for {violation.platform_url}")
    
    async def _flag_for_manual_review(self, violation: ContentViolation):
        """Flag violation for manual review."""
        # Mock implementation
        logger.info(f"Violation flagged for manual review: {violation.violation_id}")
    
    async def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary files."""
        try:
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
        except Exception as e:
            logger.error(f"Error cleaning up temp file: {e}")
    
    async def _process_violations(self):
        """Background task to process violation queue."""
        while True:
            try:
                # Process any queued violations
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in violation processor: {e}")
    
    async def _update_metrics(self):
        """Background task to update performance metrics."""
        while True:
            try:
                # Update platform count
                self.metrics['platforms_monitored'] = len([p for p, active in self.active_crawlers.items() if active])
                
                # Log metrics periodically
                if self.metrics['total_content_scanned'] % 1000 == 0:
                    logger.info(f"Monitoring metrics: {self.metrics}")
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
    
    def add_violation_handler(self, handler: Callable):
        """Add a custom violation handler."""
        self.violation_handlers.append(handler)
    
    def get_monitoring_targets(self) -> Dict[str, MonitoringTarget]:
        """Get all monitoring targets."""
        return self.monitoring_targets.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics."""
        return self.metrics.copy()
    
    async def stop_monitoring(self):
        """Stop all monitoring activities."""
        logger.info("Stopping real-time content monitoring...")
        
        # Set all crawlers to inactive
        for platform in self.active_crawlers:
            self.active_crawlers[platform] = False
        
        # Additional cleanup would go here
        logger.info("Monitoring stopped")