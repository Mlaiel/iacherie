"""
Advanced Surveillance Engine - Real-Time Content Monitoring & Alert System

Industrial surveillance system for automated content monitoring, threat detection,
and real-time alerting for content protection and intellectual property enforcement.

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

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from sqlalchemy.orm import Session
import redis
import websockets
from celery import Celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from twilio.rest import Client as TwilioClient

from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import SurveillanceError, AlertError
from ...models.surveillance import SurveillanceTarget, SurveillanceResult, AlertRule
from ...security.content_fingerprint import ContentFingerprint
from ...ml.anomaly_detection import AnomalyDetector
from .content_detector import ContentDetector, SimilarityResult
from .platform_crawler import PlatformCrawler, PlatformContent
from .web_crawler import WebCrawler

logger = logging.getLogger(__name__)

class SurveillanceStatus(Enum):
    """Surveillance operation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class ThreatLevel(Enum):
    """Content threat levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(Enum):
    """Alert notification types"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"

class MonitoringMode(Enum):
    """Content monitoring modes"""
    REAL_TIME = "real_time"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    CONTINUOUS = "continuous"
    BURST = "burst"

@dataclass
class SurveillanceConfig:
    """Comprehensive surveillance configuration"""
    target_id: str
    user_id: str
    
    # Content identification
    content_fingerprints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    semantic_signatures: List[str] = field(default_factory=list)
    
    # Monitoring parameters
    monitoring_mode: MonitoringMode = MonitoringMode.CONTINUOUS
    check_interval_minutes: int = 60
    platforms: List[str] = field(default_factory=list)
    similarity_threshold: float = 0.8
    
    # Alert configuration
    alert_types: List[AlertType] = field(default_factory=lambda: [AlertType.EMAIL])
    alert_threshold: float = 0.85
    escalation_threshold: float = 0.95
    cooldown_minutes: int = 30
    
    # Advanced settings
    enable_ai_analysis: bool = True
    enable_context_analysis: bool = True
    enable_threat_prediction: bool = True
    max_results_per_scan: int = 500
    geographic_filters: List[str] = field(default_factory=list)
    language_filters: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    active: bool = True

@dataclass
class ThreatDetection:
    """Threat detection result"""
    threat_id: str
    target_id: str
    content_id: str
    threat_level: ThreatLevel
    
    # Detection details
    similarity_score: float
    confidence_score: float
    detection_method: str
    matching_elements: List[str]
    
    # Content information
    platform: str
    content_url: str
    content_title: str
    content_author: str
    content_timestamp: datetime
    
    # Analysis
    threat_analysis: Dict[str, Any]
    recommended_actions: List[str]
    false_positive_probability: float
    
    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    investigated: bool = False
    resolved: bool = False

@dataclass
class AlertNotification:
    """Alert notification structure"""
    alert_id: str
    target_id: str
    threat_id: str
    alert_type: AlertType
    
    # Alert content
    title: str
    message: str
    severity: ThreatLevel
    recipient: str
    
    # Status tracking
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    status: str = "pending"
    
    # Retry logic
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None

class SurveillanceEngine:
    """
    Advanced Surveillance Engine for Content Monitoring
    
    Real-time content surveillance system with AI-powered threat detection,
    multi-platform monitoring, and intelligent alerting capabilities.
    """
    
    def __init__(self):
        # Core components
        self.content_detector = ContentDetector()
        self.platform_crawler = PlatformCrawler()
        self.web_crawler = WebCrawler()
        self.content_fingerprint = ContentFingerprint()
        self.anomaly_detector = AnomalyDetector()
        
        # State management
        self.surveillance_targets: Dict[str, SurveillanceConfig] = {}
        self.active_monitors: Dict[str, asyncio.Task] = {}
        self.threat_detections: Dict[str, ThreatDetection] = {}
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        
        # Infrastructure
        self.redis_client: Optional[redis.Redis] = None
        self.celery_app: Optional[Celery] = None
        self.websocket_connections: Set[websockets.WebSocketServerProtocol] = set()
        
        # Statistics
        self.surveillance_stats = {
            'active_targets': 0,
            'total_scans': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'alerts_sent': 0,
            'uptime_seconds': 0,
            'avg_scan_time_ms': 0.0
        }
        
        self.start_time = time.time()
        logger.info("Surveillance Engine initialized")

    async def initialize(self) -> None:
        """Initialize surveillance engine components"""
        try:
            # Initialize content detection components
            await self.content_detector.initialize()
            await self.platform_crawler.initialize()
            await self.web_crawler.initialize()
            
            # Initialize Redis for caching and pub/sub
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            
            # Initialize Celery for background tasks
            self.celery_app = Celery(
                'surveillance_engine',
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND
            )
            
            # Load existing surveillance targets
            await self._load_surveillance_targets()
            
            # Start background services
            asyncio.create_task(self._alert_processor())
            asyncio.create_task(self._statistics_updater())
            asyncio.create_task(self._health_monitor())
            
            logger.info("Surveillance Engine initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Surveillance Engine: {str(e)}")
            raise SurveillanceError(f"Initialization failed: {str(e)}")

    async def create_surveillance_target(self, config: SurveillanceConfig) -> str:
        """Create new surveillance target"""
        try:
            # Validate configuration
            await self._validate_surveillance_config(config)
            
            # Store configuration
            self.surveillance_targets[config.target_id] = config
            
            # Persist to database
            await self._save_surveillance_target(config)
            
            # Start monitoring if active
            if config.active:
                await self._start_target_monitoring(config.target_id)
            
            self.surveillance_stats['active_targets'] += 1
            
            logger.info(f"Created surveillance target: {config.target_id}")
            return config.target_id
            
        except Exception as e:
            logger.error(f"Failed to create surveillance target: {str(e)}")
            raise SurveillanceError(f"Target creation failed: {str(e)}")

    async def _validate_surveillance_config(self, config: SurveillanceConfig) -> None:
        """Validate surveillance configuration"""
        if not config.target_id:
            raise ValidationError("Target ID is required")
        
        if not config.user_id:
            raise ValidationError("User ID is required")
        
        if not config.content_fingerprints and not config.keywords:
            raise ValidationError("Either content fingerprints or keywords must be provided")
        
        if not config.platforms:
            raise ValidationError("At least one platform must be specified")
        
        if config.similarity_threshold < 0 or config.similarity_threshold > 1:
            raise ValidationError("Similarity threshold must be between 0 and 1")

    async def _start_target_monitoring(self, target_id: str) -> None:
        """Start monitoring for specific target"""
        if target_id in self.active_monitors:
            return  # Already monitoring
        
        config = self.surveillance_targets.get(target_id)
        if not config:
            return
        
        # Create monitoring task
        if config.monitoring_mode == MonitoringMode.REAL_TIME:
            monitor_task = asyncio.create_task(self._real_time_monitoring(target_id))
        elif config.monitoring_mode == MonitoringMode.CONTINUOUS:
            monitor_task = asyncio.create_task(self._continuous_monitoring(target_id))
        elif config.monitoring_mode == MonitoringMode.SCHEDULED:
            monitor_task = asyncio.create_task(self._scheduled_monitoring(target_id))
        else:
            monitor_task = asyncio.create_task(self._continuous_monitoring(target_id))
        
        self.active_monitors[target_id] = monitor_task
        logger.info(f"Started monitoring for target: {target_id}")

    async def _real_time_monitoring(self, target_id: str) -> None:
        """Real-time monitoring with immediate detection"""
        config = self.surveillance_targets.get(target_id)
        if not config:
            return
        
        logger.info(f"Starting real-time monitoring for {target_id}")
        
        while config.active:
            try:
                # Perform real-time scan
                await self._perform_surveillance_scan(target_id)
                
                # Short interval for real-time monitoring
                await asyncio.sleep(30)  # 30 seconds
                
            except Exception as e:
                logger.error(f"Real-time monitoring error for {target_id}: {str(e)}")
                await asyncio.sleep(60)  # Longer wait on error

    async def _continuous_monitoring(self, target_id: str) -> None:
        """Continuous monitoring with configurable intervals"""
        config = self.surveillance_targets.get(target_id)
        if not config:
            return
        
        logger.info(f"Starting continuous monitoring for {target_id}")
        
        while config.active:
            try:
                # Perform surveillance scan
                await self._perform_surveillance_scan(target_id)
                
                # Wait for configured interval
                await asyncio.sleep(config.check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Continuous monitoring error for {target_id}: {str(e)}")
                await asyncio.sleep(300)  # 5 minutes on error

    async def _scheduled_monitoring(self, target_id: str) -> None:
        """Scheduled monitoring at specific times"""
        config = self.surveillance_targets.get(target_id)
        if not config:
            return
        
        # Implementation for scheduled monitoring based on cron-like schedule
        # This is a simplified version
        
        while config.active:
            try:
                current_hour = datetime.now().hour
                
                # Example: Run every 6 hours (0, 6, 12, 18)
                if current_hour % 6 == 0:
                    await self._perform_surveillance_scan(target_id)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Scheduled monitoring error for {target_id}: {str(e)}")
                await asyncio.sleep(3600)

    async def _perform_surveillance_scan(self, target_id: str) -> None:
        """Perform comprehensive surveillance scan"""
        scan_start = time.time()
        config = self.surveillance_targets.get(target_id)
        
        if not config:
            return
        
        try:
            logger.debug(f"Performing surveillance scan for {target_id}")
            
            # Scan each configured platform
            all_threats = []
            
            for platform in config.platforms:
                try:
                    platform_threats = await self._scan_platform_for_threats(
                        target_id, platform, config
                    )
                    all_threats.extend(platform_threats)
                    
                except Exception as e:
                    logger.error(f"Platform scan failed for {platform}: {str(e)}")
            
            # Process detected threats
            for threat in all_threats:
                await self._process_threat_detection(threat)
            
            # Update statistics
            scan_time = (time.time() - scan_start) * 1000
            self.surveillance_stats['total_scans'] += 1
            self._update_average_scan_time(scan_time)
            
            if all_threats:
                logger.info(f"Surveillance scan for {target_id} found {len(all_threats)} threats")
            
        except Exception as e:
            logger.error(f"Surveillance scan failed for {target_id}: {str(e)}")

    async def _scan_platform_for_threats(self, target_id: str, platform: str,
                                       config: SurveillanceConfig) -> List[ThreatDetection]:
        """Scan specific platform for content threats"""
        threats = []
        
        try:
            # Build search queries
            search_queries = []
            
            # Keyword-based queries
            for keyword in config.keywords:
                search_queries.append({'query': keyword})
            
            # Perform platform crawling
            platform_type = self._get_platform_type(platform)
            if not platform_type:
                return threats
            
            for query in search_queries[:5]:  # Limit queries per scan
                try:
                    content_results = await self.platform_crawler.crawl_platform(
                        platform_type, query, config.max_results_per_scan
                    )
                    
                    # Analyze content for threats
                    for content in content_results:
                        threat = await self._analyze_content_for_threat(target_id, content, config)
                        if threat:
                            threats.append(threat)
                            
                except Exception as e:
                    logger.error(f"Platform crawling failed for {platform}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Platform threat scan failed: {str(e)}")
        
        return threats

    async def _analyze_content_for_threat(self, target_id: str, content: PlatformContent,
                                        config: SurveillanceConfig) -> Optional[ThreatDetection]:
        """Analyze content for potential threats"""
        try:
            # Create content signature
            content_signature = await self.content_detector.create_content_signature(
                content.content, content.content_type
            )
            
            max_similarity = 0.0
            best_match_fingerprint = ""
            
            # Compare against protected content fingerprints
            for fingerprint in config.content_fingerprints:
                similarity_result = await self.content_detector.calculate_similarity(
                    content_signature.content_id, fingerprint
                )
                
                if similarity_result and similarity_result.similarity_score > max_similarity:
                    max_similarity = similarity_result.similarity_score
                    best_match_fingerprint = fingerprint
            
            # Check if similarity exceeds threshold
            if max_similarity >= config.similarity_threshold:
                threat_level = self._calculate_threat_level(max_similarity, config)
                
                # Create threat detection
                threat = ThreatDetection(
                    threat_id=str(uuid.uuid4()),
                    target_id=target_id,
                    content_id=content.content_id,
                    threat_level=threat_level,
                    similarity_score=max_similarity,
                    confidence_score=similarity_result.confidence_score if similarity_result else 0.8,
                    detection_method="similarity_analysis",
                    matching_elements=[best_match_fingerprint],
                    platform=content.platform.value,
                    content_url=content.url,
                    content_title=content.title,
                    content_author=content.author_name,
                    content_timestamp=content.created_at or datetime.now(),
                    threat_analysis={
                        'similarity_breakdown': {
                            'text_similarity': similarity_result.text_similarity if similarity_result else 0,
                            'semantic_similarity': similarity_result.semantic_similarity if similarity_result else 0,
                            'structural_similarity': similarity_result.structural_similarity if similarity_result else 0
                        },
                        'content_analysis': {
                            'word_count': len(content.content.split()),
                            'language': content.language,
                            'engagement_metrics': {
                                'likes': content.likes,
                                'shares': content.shares,
                                'comments': content.comments,
                                'views': content.views
                            }
                        }
                    },
                    recommended_actions=self._get_recommended_actions(threat_level, max_similarity),
                    false_positive_probability=self._estimate_false_positive_probability(
                        max_similarity, content, similarity_result
                    )
                )
                
                return threat
            
        except Exception as e:
            logger.error(f"Content threat analysis failed: {str(e)}")
        
        return None

    def _calculate_threat_level(self, similarity_score: float, config: SurveillanceConfig) -> ThreatLevel:
        """Calculate threat level based on similarity score"""
        if similarity_score >= 0.98:
            return ThreatLevel.EMERGENCY
        elif similarity_score >= config.escalation_threshold:
            return ThreatLevel.CRITICAL
        elif similarity_score >= config.alert_threshold:
            return ThreatLevel.HIGH
        elif similarity_score >= 0.75:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _get_recommended_actions(self, threat_level: ThreatLevel, similarity_score: float) -> List[str]:
        """Get recommended actions based on threat level"""
        actions = []
        
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY]:
            actions.extend([
                "Immediate legal review required",
                "Consider DMCA takedown notice",
                "Document evidence for legal proceedings",
                "Contact platform abuse team"
            ])
        elif threat_level == ThreatLevel.HIGH:
            actions.extend([
                "Investigate content authenticity",
                "Prepare takedown request",
                "Monitor for additional violations",
                "Consider contacting content creator"
            ])
        elif threat_level == ThreatLevel.MEDIUM:
            actions.extend([
                "Manual review recommended",
                "Monitor content development",
                "Assess commercial impact"
            ])
        else:
            actions.append("Continue monitoring")
        
        return actions

    def _estimate_false_positive_probability(self, similarity_score: float, 
                                           content: PlatformContent,
                                           similarity_result: Optional[SimilarityResult]) -> float:
        """Estimate probability of false positive detection"""
        false_positive_prob = 0.0
        
        # Base probability based on similarity score
        if similarity_score < 0.8:
            false_positive_prob += 0.4
        elif similarity_score < 0.9:
            false_positive_prob += 0.2
        elif similarity_score < 0.95:
            false_positive_prob += 0.1
        
        # Adjust based on content characteristics
        if len(content.content) < 100:  # Short content more likely to be coincidental
            false_positive_prob += 0.2
        
        if content.content_type.value == "text" and similarity_result:
            # High structural but low semantic similarity might indicate common phrases
            if (similarity_result.structural_similarity > 0.8 and 
                similarity_result.semantic_similarity < 0.6):
                false_positive_prob += 0.3
        
        return min(false_positive_prob, 0.9)

    async def _process_threat_detection(self, threat: ThreatDetection) -> None:
        """Process detected threat and trigger appropriate actions"""
        try:
            # Store threat detection
            self.threat_detections[threat.threat_id] = threat
            
            # Save to database
            await self._save_threat_detection(threat)
            
            # Update statistics
            self.surveillance_stats['threats_detected'] += 1
            
            # Trigger alerts if threshold exceeded
            config = self.surveillance_targets.get(threat.target_id)
            if config and threat.similarity_score >= config.alert_threshold:
                await self._trigger_threat_alert(threat, config)
            
            # Send real-time notifications
            await self._send_realtime_notification(threat)
            
            # Log threat detection
            logger.warning(
                f"Threat detected: {threat.threat_level.value} - "
                f"Similarity: {threat.similarity_score:.2%} - "
                f"Platform: {threat.platform} - "
                f"URL: {threat.content_url}"
            )
            
        except Exception as e:
            logger.error(f"Failed to process threat detection: {str(e)}")

    async def _trigger_threat_alert(self, threat: ThreatDetection, config: SurveillanceConfig) -> None:
        """Trigger alert notifications for threat detection"""
        try:
            for alert_type in config.alert_types:
                alert = AlertNotification(
                    alert_id=str(uuid.uuid4()),
                    target_id=threat.target_id,
                    threat_id=threat.threat_id,
                    alert_type=alert_type,
                    title=f"Content Threat Detected - {threat.threat_level.value.upper()}",
                    message=self._generate_alert_message(threat),
                    severity=threat.threat_level,
                    recipient=await self._get_alert_recipient(config.user_id, alert_type)
                )
                
                await self.alert_queue.put(alert)
                
        except Exception as e:
            logger.error(f"Failed to trigger threat alert: {str(e)}")

    def _generate_alert_message(self, threat: ThreatDetection) -> str:
        """Generate alert message for threat detection"""
        return f"""
CONTENT THREAT ALERT

Threat Level: {threat.threat_level.value.upper()}
Similarity Score: {threat.similarity_score:.2%}
Platform: {threat.platform}
Content URL: {threat.content_url}
Author: {threat.content_author}
Detected: {threat.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Recommended Actions:
{chr(10).join(f'• {action}' for action in threat.recommended_actions)}

Confidence: {threat.confidence_score:.2%}
False Positive Probability: {threat.false_positive_probability:.2%}
"""

    async def _get_alert_recipient(self, user_id: str, alert_type: AlertType) -> str:
        """Get alert recipient based on user preferences"""
        # This would typically query user preferences from database
        # For now, return placeholder
        if alert_type == AlertType.EMAIL:
            return f"user_{user_id}@example.com"
        elif alert_type == AlertType.SMS:
            return f"+1234567890"  # Would be retrieved from user profile
        else:
            return f"user_{user_id}"

    async def _send_realtime_notification(self, threat: ThreatDetection) -> None:
        """Send real-time notifications via WebSocket"""
        if not self.websocket_connections:
            return
        
        notification = {
            'type': 'threat_detection',
            'threat_id': threat.threat_id,
            'target_id': threat.target_id,
            'threat_level': threat.threat_level.value,
            'similarity_score': threat.similarity_score,
            'platform': threat.platform,
            'timestamp': threat.detected_at.isoformat()
        }
        
        # Send to all connected WebSocket clients
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send(json.dumps(notification))
            except:
                disconnected.add(ws)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected

    def _get_platform_type(self, platform_name: str) -> Optional[Any]:
        """Convert platform name to platform type enum"""
        platform_mapping = {
            'twitter': 'TWITTER',
            'instagram': 'INSTAGRAM',
            'youtube': 'YOUTUBE',
            'facebook': 'FACEBOOK',
            'tiktok': 'TIKTOK',
            'linkedin': 'LINKEDIN',
            'reddit': 'REDDIT'
        }
        
        platform_enum_name = platform_mapping.get(platform_name.lower())
        if platform_enum_name:
            # Return the actual enum from platform_crawler module
            # This is a placeholder - would need proper import
            return platform_enum_name
        
        return None

    def _update_average_scan_time(self, scan_time_ms: float) -> None:
        """Update average scan time statistics"""
        total_scans = self.surveillance_stats['total_scans']
        current_avg = self.surveillance_stats['avg_scan_time_ms']
        
        self.surveillance_stats['avg_scan_time_ms'] = (
            (current_avg * (total_scans - 1) + scan_time_ms) / total_scans
        )

    async def _alert_processor(self) -> None:
        """Background alert processing service"""
        logger.info("Alert processor started")
        
        while True:
            try:
                # Get alert from queue
                alert = await self.alert_queue.get()
                
                # Process alert based on type
                success = await self._send_alert(alert)
                
                if success:
                    alert.status = "sent"
                    alert.sent_at = datetime.now()
                    self.surveillance_stats['alerts_sent'] += 1
                else:
                    alert.retry_count += 1
                    if alert.retry_count < alert.max_retries:
                        alert.next_retry_at = datetime.now() + timedelta(minutes=5 ** alert.retry_count)
                        await self.alert_queue.put(alert)  # Re-queue for retry
                    else:
                        alert.status = "failed"
                        logger.error(f"Alert failed after {alert.max_retries} attempts: {alert.alert_id}")
                
            except Exception as e:
                logger.error(f"Alert processor error: {str(e)}")
                await asyncio.sleep(10)

    async def _send_alert(self, alert: AlertNotification) -> bool:
        """Send alert notification"""
        try:
            if alert.alert_type == AlertType.EMAIL:
                return await self._send_email_alert(alert)
            elif alert.alert_type == AlertType.SMS:
                return await self._send_sms_alert(alert)
            elif alert.alert_type == AlertType.WEBHOOK:
                return await self._send_webhook_alert(alert)
            elif alert.alert_type == AlertType.SLACK:
                return await self._send_slack_alert(alert)
            else:
                logger.warning(f"Unsupported alert type: {alert.alert_type}")
                return False
                
        except Exception as e:
            logger.error(f"Alert sending failed: {str(e)}")
            return False

    async def _send_email_alert(self, alert: AlertNotification) -> bool:
        """Send email alert"""
        try:
            smtp_server = settings.SMTP_SERVER
            smtp_port = settings.SMTP_PORT
            username = settings.SMTP_USERNAME
            password = settings.SMTP_PASSWORD
            
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = alert.recipient
            msg['Subject'] = alert.title
            
            msg.attach(MIMEText(alert.message, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            text = msg.as_string()
            server.sendmail(username, alert.recipient, text)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Email alert failed: {str(e)}")
            return False

    async def _send_sms_alert(self, alert: AlertNotification) -> bool:
        """Send SMS alert using Twilio"""
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=f"{alert.title}\n\n{alert.message}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=alert.recipient
            )
            
            return message.sid is not None
            
        except Exception as e:
            logger.error(f"SMS alert failed: {str(e)}")
            return False

    async def _send_webhook_alert(self, alert: AlertNotification) -> bool:
        """Send webhook alert"""
        try:
            webhook_payload = {
                'alert_id': alert.alert_id,
                'target_id': alert.target_id,
                'threat_id': alert.threat_id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity.value,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                alert.recipient,  # Webhook URL
                json=webhook_payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Webhook alert failed: {str(e)}")
            return False

    async def _send_slack_alert(self, alert: AlertNotification) -> bool:
        """Send Slack alert"""
        try:
            slack_webhook_url = alert.recipient
            
            slack_payload = {
                'text': alert.title,
                'attachments': [
                    {
                        'color': self._get_slack_color(alert.severity),
                        'text': alert.message,
                        'ts': int(time.time())
                    }
                ]
            }
            
            response = requests.post(
                slack_webhook_url,
                json=slack_payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Slack alert failed: {str(e)}")
            return False

    def _get_slack_color(self, severity: ThreatLevel) -> str:
        """Get Slack message color based on severity"""
        colors = {
            ThreatLevel.EMERGENCY: '#ff0000',
            ThreatLevel.CRITICAL: '#ff4500',
            ThreatLevel.HIGH: '#ffa500',
            ThreatLevel.MEDIUM: '#ffff00',
            ThreatLevel.LOW: '#90ee90',
            ThreatLevel.NONE: '#d3d3d3'
        }
        return colors.get(severity, '#d3d3d3')

    async def _statistics_updater(self) -> None:
        """Update surveillance statistics periodically"""
        while True:
            try:
                # Update uptime
                self.surveillance_stats['uptime_seconds'] = int(time.time() - self.start_time)
                
                # Update active targets count
                self.surveillance_stats['active_targets'] = len([
                    t for t in self.surveillance_targets.values() if t.active
                ])
                
                # Persist statistics to Redis
                if self.redis_client:
                    await self._save_statistics_to_redis()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Statistics update failed: {str(e)}")
                await asyncio.sleep(60)

    async def _health_monitor(self) -> None:
        """Monitor surveillance engine health"""
        while True:
            try:
                # Check component health
                health_status = await self._check_component_health()
                
                # Log health issues
                for component, status in health_status.items():
                    if not status['healthy']:
                        logger.warning(f"Component unhealthy: {component} - {status['message']}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(300)

    async def _check_component_health(self) -> Dict[str, Dict]:
        """Check health of surveillance engine components"""
        health_status = {}
        
        # Check Redis connection
        try:
            if self.redis_client:
                self.redis_client.ping()
                health_status['redis'] = {'healthy': True, 'message': 'OK'}
            else:
                health_status['redis'] = {'healthy': False, 'message': 'Not connected'}
        except:
            health_status['redis'] = {'healthy': False, 'message': 'Connection failed'}
        
        # Check active monitors
        active_monitors = len(self.active_monitors)
        expected_monitors = len([t for t in self.surveillance_targets.values() if t.active])
        
        health_status['monitors'] = {
            'healthy': active_monitors == expected_monitors,
            'message': f'{active_monitors}/{expected_monitors} monitors active'
        }
        
        # Check alert queue
        queue_size = self.alert_queue.qsize()
        health_status['alert_queue'] = {
            'healthy': queue_size < 1000,  # Threshold for healthy queue size
            'message': f'{queue_size} alerts in queue'
        }
        
        return health_status

    async def _load_surveillance_targets(self) -> None:
        """Load surveillance targets from database"""
        try:
            # This would load from database
            # Placeholder implementation
            logger.info("Loading surveillance targets from database")
            
        except Exception as e:
            logger.error(f"Failed to load surveillance targets: {str(e)}")

    async def _save_surveillance_target(self, config: SurveillanceConfig) -> None:
        """Save surveillance target to database"""
        try:
            # This would save to database
            # Placeholder implementation
            logger.debug(f"Saving surveillance target: {config.target_id}")
            
        except Exception as e:
            logger.error(f"Failed to save surveillance target: {str(e)}")

    async def _save_threat_detection(self, threat: ThreatDetection) -> None:
        """Save threat detection to database"""
        try:
            # This would save to database
            # Placeholder implementation
            logger.debug(f"Saving threat detection: {threat.threat_id}")
            
        except Exception as e:
            logger.error(f"Failed to save threat detection: {str(e)}")

    async def _save_statistics_to_redis(self) -> None:
        """Save statistics to Redis"""
        try:
            if self.redis_client:
                stats_key = "surveillance_engine:stats"
                self.redis_client.hmset(stats_key, self.surveillance_stats)
                self.redis_client.expire(stats_key, 86400)  # 24 hours
                
        except Exception as e:
            logger.error(f"Failed to save statistics to Redis: {str(e)}")

    async def stop_surveillance_target(self, target_id: str) -> bool:
        """Stop surveillance for specific target"""
        try:
            if target_id in self.surveillance_targets:
                self.surveillance_targets[target_id].active = False
                
                if target_id in self.active_monitors:
                    self.active_monitors[target_id].cancel()
                    del self.active_monitors[target_id]
                
                await self._save_surveillance_target(self.surveillance_targets[target_id])
                logger.info(f"Stopped surveillance for target: {target_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop surveillance target: {str(e)}")
        
        return False

    async def pause_surveillance_target(self, target_id: str, duration_minutes: int = 60) -> bool:
        """Temporarily pause surveillance for target"""
        try:
            if target_id in self.active_monitors:
                # Store resume time
                resume_time = datetime.now() + timedelta(minutes=duration_minutes)
                
                # Schedule resume task
                asyncio.create_task(self._resume_surveillance_after_delay(target_id, duration_minutes * 60))
                
                # Pause monitoring
                self.active_monitors[target_id].cancel()
                del self.active_monitors[target_id]
                
                logger.info(f"Paused surveillance for {target_id} until {resume_time}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to pause surveillance target: {str(e)}")
        
        return False

    async def _resume_surveillance_after_delay(self, target_id: str, delay_seconds: int) -> None:
        """Resume surveillance after delay"""
        await asyncio.sleep(delay_seconds)
        
        if target_id in self.surveillance_targets and self.surveillance_targets[target_id].active:
            await self._start_target_monitoring(target_id)
            logger.info(f"Resumed surveillance for target: {target_id}")

    def get_surveillance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive surveillance statistics"""
        return {
            **self.surveillance_stats,
            'targets_configured': len(self.surveillance_targets),
            'active_monitors': len(self.active_monitors),
            'threat_detections_total': len(self.threat_detections),
            'pending_alerts': self.alert_queue.qsize()
        }

    def get_target_status(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific surveillance target"""
        config = self.surveillance_targets.get(target_id)
        if not config:
            return None
        
        return {
            'target_id': target_id,
            'active': config.active,
            'monitoring_mode': config.monitoring_mode.value,
            'platforms': config.platforms,
            'last_scan': None,  # Would be retrieved from database
            'threats_detected': len([
                t for t in self.threat_detections.values() 
                if t.target_id == target_id
            ]),
            'is_monitoring': target_id in self.active_monitors
        }

    async def cleanup(self) -> None:
        """Cleanup surveillance engine resources"""
        logger.info("Shutting down Surveillance Engine...")
        
        # Stop all monitoring tasks
        for task in self.active_monitors.values():
            task.cancel()
        
        # Close WebSocket connections
        for ws in self.websocket_connections:
            await ws.close()
        
        # Cleanup components
        await self.content_detector.cleanup()
        await self.platform_crawler.cleanup()
        await self.web_crawler.cleanup()
        
        logger.info("Surveillance Engine shutdown complete")


class AlertSystem:
    """
    Advanced Alert System for Content Protection
    
    Manages alert rules, notification channels, and escalation procedures
    for content protection and threat response.
    """
    
    def __init__(self, surveillance_engine: SurveillanceEngine):
        self.surveillance_engine = surveillance_engine
        self.alert_rules: Dict[str, Dict] = {}
        self.notification_channels: Dict[str, Dict] = {}
        self.escalation_policies: Dict[str, Dict] = {}
        
    async def create_alert_rule(self, rule_config: Dict[str, Any]) -> str:
        """Create custom alert rule"""
        rule_id = str(uuid.uuid4())
        self.alert_rules[rule_id] = {
            **rule_config,
            'created_at': datetime.now(),
            'active': True
        }
        return rule_id
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send alert through configured channels"""
        try:
            alert = AlertNotification(
                alert_id=str(uuid.uuid4()),
                target_id=alert_data.get('target_id', ''),
                threat_id=alert_data.get('threat_id', ''),
                alert_type=AlertType(alert_data.get('type', 'email')),
                title=alert_data.get('title', 'Alert'),
                message=alert_data.get('message', ''),
                severity=ThreatLevel(alert_data.get('severity', 'medium')),
                recipient=alert_data.get('recipient', '')
            )
            
            await self.surveillance_engine.alert_queue.put(alert)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            return False
    
    def configure_notification_channel(self, channel_id: str, channel_config: Dict[str, Any]) -> None:
        """Configure notification channel"""
        self.notification_channels[channel_id] = {
            **channel_config,
            'configured_at': datetime.now(),
            'active': True
        }
    
    def create_escalation_policy(self, policy_id: str, policy_config: Dict[str, Any]) -> None:
        """Create escalation policy for alerts"""
        self.escalation_policies[policy_id] = {
            **policy_config,
            'created_at': datetime.now(),
            'active': True
        }
