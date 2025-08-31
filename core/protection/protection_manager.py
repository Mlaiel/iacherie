"""
Protection Manager - Central Orchestrator for Content Protection System

This module serves as the main coordinator for all content protection activities:
- Manages fingerprinting, monitoring, and violation detection workflows
- Coordinates between different protection components
- Provides unified API for protection operations
- Handles protection policies and configurations
- Manages protection lifecycle for content

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path
import uuid
from concurrent.futures import ThreadPoolExecutor

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ContentType, ProtectionStatus
from ...config.settings import get_settings
from .fingerprint_engine import FingerprintEngine, FingerprintResult
from .content_monitor import ContentMonitor, MonitoringConfig, MonitoringPlatform, MonitoringResult
from .violation_detector import ViolationDetector, DetectionConfig, ViolationEvidence
from .verification_service import VerificationService
from .alert_manager import AlertManager
from .dmca_handler import DMCAHandler
from .evidence_collector import EvidenceCollector

logger = get_logger(__name__)
settings = get_settings()


class ProtectionLevel(Enum):
    """Protection levels for content"""
    BASIC = "basic"           # Fingerprinting only
    STANDARD = "standard"     # Fingerprinting + basic monitoring
    PREMIUM = "premium"       # Full monitoring + violation detection
    ENTERPRISE = "enterprise" # Full protection + legal automation


class ProtectionPolicy(Enum):
    """Protection policies for different content types"""
    STRICT = "strict"         # Zero tolerance for any similarity
    BALANCED = "balanced"     # Standard thresholds with false positive filtering
    PERMISSIVE = "permissive" # High thresholds, educational use allowed
    CUSTOM = "custom"         # User-defined thresholds


@dataclass
class ProtectionConfiguration:
    """Comprehensive protection configuration"""
    protection_level: ProtectionLevel
    protection_policy: ProtectionPolicy
    
    # Monitoring settings
    monitoring_platforms: List[MonitoringPlatform] = field(default_factory=list)
    monitoring_interval_minutes: int = 60
    deep_monitoring: bool = False
    
    # Detection settings
    similarity_threshold: float = 0.75
    false_positive_threshold: float = 0.30
    auto_dmca_enabled: bool = False
    
    # Alert settings
    email_alerts: bool = True
    webhook_alerts: bool = False
    real_time_alerts: bool = True
    
    # Custom thresholds by content type
    custom_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Whitelist and blacklist
    whitelisted_domains: Set[str] = field(default_factory=set)
    blacklisted_domains: Set[str] = field(default_factory=set)


@dataclass
class ProtectedContent:
    """Represents content under protection"""
    content_id: str
    content_type: ContentType
    file_path: Optional[Path] = None
    text_content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Protection status
    protection_status: ProtectionStatus = ProtectionStatus.PENDING
    fingerprints: List[FingerprintResult] = field(default_factory=list)
    monitor_ids: List[str] = field(default_factory=list)
    
    # Statistics
    violations_detected: int = 0
    violations_resolved: int = 0
    last_scan: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProtectionJob:
    """Represents a protection job/task"""
    job_id: str
    content_id: str
    job_type: str  # fingerprint, monitor, detect, etc.
    status: str = "pending"
    progress: float = 0.0
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ProtectionManager:
    """Central manager for all content protection operations"""
    
    def __init__(self):
        # Core components
        self.fingerprint_engine = FingerprintEngine()
        self.content_monitor = ContentMonitor()
        self.violation_detector = ViolationDetector()
        self.verification_service = VerificationService()
        self.alert_manager = AlertManager()
        self.dmca_handler = DMCAHandler()
        self.evidence_collector = EvidenceCollector()
        
        # State management
        self.protected_content: Dict[str, ProtectedContent] = {}
        self.protection_configs: Dict[str, ProtectionConfiguration] = {}
        self.active_jobs: Dict[str, ProtectionJob] = {}
        self.job_queue = asyncio.Queue()
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default protection configurations"""
        # Basic protection config
        self.protection_configs['basic'] = ProtectionConfiguration(
            protection_level=ProtectionLevel.BASIC,
            protection_policy=ProtectionPolicy.BALANCED,
            monitoring_platforms=[],
            email_alerts=False
        )
        
        # Standard protection config
        self.protection_configs['standard'] = ProtectionConfiguration(
            protection_level=ProtectionLevel.STANDARD,
            protection_policy=ProtectionPolicy.BALANCED,
            monitoring_platforms=[MonitoringPlatform.YOUTUBE, MonitoringPlatform.INSTAGRAM],
            monitoring_interval_minutes=120
        )
        
        # Premium protection config
        self.protection_configs['premium'] = ProtectionConfiguration(
            protection_level=ProtectionLevel.PREMIUM,
            protection_policy=ProtectionPolicy.STRICT,
            monitoring_platforms=[
                MonitoringPlatform.YOUTUBE, MonitoringPlatform.INSTAGRAM,
                MonitoringPlatform.TIKTOK, MonitoringPlatform.TWITTER
            ],
            monitoring_interval_minutes=60,
            deep_monitoring=True,
            similarity_threshold=0.70
        )
        
        # Enterprise protection config
        self.protection_configs['enterprise'] = ProtectionConfiguration(
            protection_level=ProtectionLevel.ENTERPRISE,
            protection_policy=ProtectionPolicy.STRICT,
            monitoring_platforms=list(MonitoringPlatform),
            monitoring_interval_minutes=30,
            deep_monitoring=True,
            similarity_threshold=0.65,
            auto_dmca_enabled=True,
            real_time_alerts=True
        )
    
    async def start_protection_service(self):
        """Start the protection service background tasks"""



        try:
            # Start job processor
            job_processor_task = asyncio.create_task(self._process_job_queue())
            self.background_tasks.add(job_processor_task)
            
            # Start periodic violation detection
            violation_detector_task = asyncio.create_task(self._periodic_violation_detection())
            self.background_tasks.add(violation_detector_task)
            
            # Start monitoring results processor
            monitoring_processor_task = asyncio.create_task(self._process_monitoring_results())
            self.background_tasks.add(monitoring_processor_task)
            
            logger.info("Protection service started successfully")
            
        except Exception as e:
            logger.error(f"Error starting protection service: {e}")
            raise
    
    async def stop_protection_service(self):
        """Stop the protection service and cleanup"""



        try:
            # Cancel all background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Stop all monitors
            for content in self.protected_content.values():
                for monitor_id in content.monitor_ids:
                    await self.content_monitor.stop_monitoring(monitor_id)
            
            # Cleanup resources
            self.executor.shutdown(wait=True)
            
            logger.info("Protection service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping protection service: {e}")
    
    async def protect_content(self, 
                            content_path: Optional[Path] = None,
                            content_type: ContentType = None,
                            text_content: Optional[str] = None,
                            protection_config: str = 'standard',
                            search_terms: Optional[List[str]] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start protection for new content"""



        try:
            # Generate content ID
            content_id = str(uuid.uuid4())
            
            # Validate input
            if not content_path and not text_content:
                raise ValueError("Either content_path or text_content must be provided")
            
            if not content_type:
                content_type = self._detect_content_type(content_path) if content_path else ContentType.TEXT
            
            # Create protected content record
            protected = ProtectedContent(
                content_id=content_id,
                content_type=content_type,
                file_path=content_path,
                text_content=text_content,
                metadata=metadata or {}
            )
            
            self.protected_content[content_id] = protected
            
            # Get protection configuration
            config = self.protection_configs.get(protection_config, self.protection_configs['standard'])
            
            # Step 1: Generate fingerprints
            fingerprint_job_id = await self._create_fingerprint_job(content_id)
            
            # Step 2: Setup monitoring (if configured)
            if config.monitoring_platforms:
                monitor_job_id = await self._create_monitoring_job(content_id, config, search_terms)
            
            logger.info(f"Started protection for content {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Error protecting content: {e}")
            raise
    
    async def _create_fingerprint_job(self, content_id: str) -> str:
        """Create fingerprinting job"""
        job_id = str(uuid.uuid4())
        job = ProtectionJob(
            job_id=job_id,
            content_id=content_id,
            job_type="fingerprint"
        )
        
        self.active_jobs[job_id] = job
        await self.job_queue.put(job)
        
        return job_id
    
    async def _create_monitoring_job(self, 
                                   content_id: str, 
                                   config: ProtectionConfiguration,
                                   search_terms: Optional[List[str]]) -> str:
        """Create monitoring job"""
        job_id = str(uuid.uuid4())
        job = ProtectionJob(
            job_id=job_id,
            content_id=content_id,
            job_type="monitor",
            result={
                'config': config,
                'search_terms': search_terms or []
            }
        )
        
        self.active_jobs[job_id] = job
        await self.job_queue.put(job)
        
        return job_id
    
    async def _process_job_queue(self):
        """Process protection jobs from queue"""
        while True:
            try:
                # Get job from queue
                job = await self.job_queue.get()
                
                # Process job based on type
                if job.job_type == "fingerprint":
                    await self._process_fingerprint_job(job)
                elif job.job_type == "monitor":
                    await self._process_monitoring_job(job)
                elif job.job_type == "detect":
                    await self._process_detection_job(job)
                
                # Mark job as completed
                job.completed_at = datetime.utcnow()
                job.status = "completed" if not job.error_message else "failed"
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                if 'job' in locals():
                    job.status = "failed"
                    job.error_message = str(e)
    
    async def _process_fingerprint_job(self, job: ProtectionJob):
        """Process fingerprinting job"""



        try:
            job.status = "running"
            job.progress = 0.1
            
            content = self.protected_content[job.content_id]
            
            # Generate fingerprints
            fingerprints = await self.fingerprint_engine.generate_fingerprint(
                content.file_path,
                content.content_type,
                content.text_content
            )
            
            job.progress = 0.8
            
            # Store fingerprints
            content.fingerprints = fingerprints
            content.protection_status = ProtectionStatus.ACTIVE
            
            # Add to search index
            for fingerprint in fingerprints:
                await self.fingerprint_engine.add_to_index(fingerprint, job.content_id)
            
            job.progress = 1.0
            job.result = {'fingerprints_count': len(fingerprints)}
            
            logger.info(f"Generated {len(fingerprints)} fingerprints for content {job.content_id}")
            
        except Exception as e:
            job.error_message = str(e)
            logger.error(f"Error in fingerprinting job: {e}")
    
    async def _process_monitoring_job(self, job: ProtectionJob):
        """Process monitoring setup job"""



        try:
            job.status = "running"
            job.progress = 0.1
            
            content = self.protected_content[job.content_id]
            config = job.result['config']
            search_terms = job.result['search_terms']
            
            # If no search terms provided, generate from metadata
            if not search_terms:
                search_terms = self._generate_search_terms(content)
            
            job.progress = 0.3
            
            # Create monitors for each platform
            monitor_ids = []
            for platform in config.monitoring_platforms:
                monitor_config = MonitoringConfig(
                    platform=platform,
                    search_terms=search_terms,
                    interval_minutes=config.monitoring_interval_minutes,
                    deep_scan=config.deep_monitoring,
                    rate_limit_delay=2.0
                )
                
                monitor_id = self.content_monitor.create_monitor(monitor_config)
                await self.content_monitor.start_monitoring(monitor_id)
                monitor_ids.append(monitor_id)
                
                job.progress += 0.6 / len(config.monitoring_platforms)
            
            # Store monitor IDs
            content.monitor_ids = monitor_ids
            
            job.progress = 1.0
            job.result = {'monitor_ids': monitor_ids, 'search_terms': search_terms}
            
            logger.info(f"Started {len(monitor_ids)} monitors for content {job.content_id}")
            
        except Exception as e:
            job.error_message = str(e)
            logger.error(f"Error in monitoring job: {e}")
    
    async def _process_detection_job(self, job: ProtectionJob):
        """Process violation detection job"""



        try:
            job.status = "running"
            job.progress = 0.1
            
            content = self.protected_content[job.content_id]
            monitoring_results = job.result.get('monitoring_results', [])
            
            # Configure detection
            detection_config = DetectionConfig(
                similarity_threshold=0.75,
                false_positive_threshold=0.30
            )
            
            job.progress = 0.3
            
            # Detect violations
            violations = await self.violation_detector.detect_violations(
                job.content_id,
                monitoring_results,
                detection_config
            )
            
            job.progress = 0.8
            
            # Process violations
            for violation in violations:
                # Collect evidence
                evidence = await self.evidence_collector.collect_evidence(violation)
                
                # Send alerts
                await self.alert_manager.send_violation_alert(violation, evidence)
                
                # Auto-DMCA if configured
                protection_config = self._get_protection_config_for_content(job.content_id)
                if protection_config.auto_dmca_enabled and violation.severity.value in ['critical', 'high']:
                    await self.dmca_handler.submit_takedown_request(violation, evidence)
            
            # Update content statistics
            content.violations_detected += len(violations)
            content.last_scan = datetime.utcnow()
            
            job.progress = 1.0
            job.result = {'violations_found': len(violations)}
            
            logger.info(f"Detected {len(violations)} violations for content {job.content_id}")
            
        except Exception as e:
            job.error_message = str(e)
            logger.error(f"Error in detection job: {e}")
    
    async def _periodic_violation_detection(self):
        """Periodic violation detection for all protected content"""
        while True:
            try:
                # Run detection every 30 minutes
                await asyncio.sleep(1800)
                
                for content_id, content in self.protected_content.items():
                    if content.protection_status == ProtectionStatus.ACTIVE and content.monitor_ids:
                        # Get recent monitoring results
                        monitoring_results = []
                        for monitor_id in content.monitor_ids:
                            results = self.content_monitor.get_monitor_results(monitor_id, limit=50)
                            monitoring_results.extend(results)
                        
                        if monitoring_results:
                            # Create detection job
                            job_id = str(uuid.uuid4())
                            job = ProtectionJob(
                                job_id=job_id,
                                content_id=content_id,
                                job_type="detect",
                                result={'monitoring_results': monitoring_results}
                            )
                            
                            self.active_jobs[job_id] = job
                            await self.job_queue.put(job)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic violation detection: {e}")
    
    async def _process_monitoring_results(self):
        """Process new monitoring results as they come in"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Get new URLs detected in last hour
                new_urls = self.content_monitor.get_all_detected_urls(hours=1)
                
                if new_urls:
                    logger.info(f"Processing {len(new_urls)} new detected URLs")
                    
                    # For each protected content, check if new URLs are violations
                    for content_id, content in self.protected_content.items():
                        if content.protection_status == ProtectionStatus.ACTIVE:
                            # Quick similarity check for real-time alerts
                            await self._quick_violation_check(content_id, new_urls)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing monitoring results: {e}")
    
    async def _quick_violation_check(self, content_id: str, urls: List[str]):
        """Perform quick violation check for real-time alerts"""



        try:
            content = self.protected_content[content_id]
            
            # Only check first few URLs to avoid overload
            for url in urls[:5]:
                # Quick similarity analysis
                similarity_scores = await self.violation_detector.similarity_analyzer.analyze_similarity(
                    content.fingerprints,
                    url,
                    DetectionConfig(similarity_threshold=0.80)
                )
                
                if similarity_scores:
                    max_similarity = max(s.similarity_score for s in similarity_scores)
                    
                    if max_similarity > 0.90:  # High confidence violation
                        # Send real-time alert
                        await self.alert_manager.send_realtime_alert(
                            content_id, url, max_similarity
                        )
        
        except Exception as e:
            logger.warning(f"Error in quick violation check: {e}")
    
    def _generate_search_terms(self, content: ProtectedContent) -> List[str]:
        """Generate search terms from content metadata"""
        search_terms = []
        
        # Extract from metadata
        metadata = content.metadata
        if 'title' in metadata:
            search_terms.append(metadata['title'])
        if 'artist' in metadata:
            search_terms.append(metadata['artist'])
        if 'keywords' in metadata:
            search_terms.extend(metadata['keywords'])
        
        # Generate from filename if available
        if content.file_path:
            filename = content.file_path.stem
            search_terms.append(filename.replace('_', ' ').replace('-', ' '))
        
        # Clean and deduplicate
        search_terms = list(set(term.strip() for term in search_terms if term.strip()))
        
        return search_terms[:10]  # Limit to 10 terms
    
    def _detect_content_type(self, file_path: Path) -> ContentType:
        """Detect content type from file extension"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
            return ContentType.AUDIO
        elif suffix in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return ContentType.VIDEO
        elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return ContentType.IMAGE
        else:
            return ContentType.TEXT
    
    def _get_protection_config_for_content(self, content_id: str) -> ProtectionConfiguration:
        """Get protection configuration for specific content"""
        # This would typically be stored per content
        # For now, return standard config
        return self.protection_configs['standard']
    
    # Public API methods
    
    async def get_protection_status(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get protection status for content"""
        if content_id not in self.protected_content:
            return None
        
        content = self.protected_content[content_id]
        
        return {
            'content_id': content_id,
            'content_type': content.content_type.value,
            'protection_status': content.protection_status.value,
            'fingerprints_count': len(content.fingerprints),
            'monitors_active': len(content.monitor_ids),
            'violations_detected': content.violations_detected,
            'violations_resolved': content.violations_resolved,
            'last_scan': content.last_scan.isoformat() if content.last_scan else None,
            'created_at': content.created_at.isoformat()
        }
    
    async def stop_protection(self, content_id: str) -> bool:
        """Stop protection for specific content"""



        try:
            if content_id not in self.protected_content:
                return False
            
            content = self.protected_content[content_id]
            
            # Stop all monitors
            for monitor_id in content.monitor_ids:
                await self.content_monitor.stop_monitoring(monitor_id)
            
            # Update status
            content.protection_status = ProtectionStatus.STOPPED
            content.monitor_ids = []
            
            logger.info(f"Stopped protection for content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping protection: {e}")
            return False
    
    async def update_protection_config(self, 
                                     content_id: str, 
                                     config_name: str) -> bool:
        """Update protection configuration for content"""



        try:
            if content_id not in self.protected_content:
                return False
            
            if config_name not in self.protection_configs:
                return False
            
            # Stop current protection
            await self.stop_protection(content_id)
            
            # Restart with new config
            content = self.protected_content[content_id]
            search_terms = self._generate_search_terms(content)
            
            monitor_job_id = await self._create_monitoring_job(
                content_id, 
                self.protection_configs[config_name],
                search_terms
            )
            
            logger.info(f"Updated protection config for content {content_id} to {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating protection config: {e}")
            return False
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        total_violations = sum(content.violations_detected for content in self.protected_content.values())
        total_resolved = sum(content.violations_resolved for content in self.protected_content.values())
        
        active_content = sum(1 for content in self.protected_content.values() 
                           if content.protection_status == ProtectionStatus.ACTIVE)
        
        return {
            'protected_content_count': len(self.protected_content),
            'active_content_count': active_content,
            'total_violations_detected': total_violations,
            'total_violations_resolved': total_resolved,
            'active_monitors': sum(len(content.monitor_ids) for content in self.protected_content.values()),
            'active_jobs': len([job for job in self.active_jobs.values() if job.status == "running"]),
            'fingerprint_engine_stats': self.fingerprint_engine.get_statistics(),
            'monitoring_stats': self.content_monitor.get_monitoring_statistics(),
            'detection_stats': self.violation_detector.get_detection_statistics()
        }
