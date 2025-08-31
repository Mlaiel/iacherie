"""Real-time Violation Detector
============================

Advanced real-time content violation detection system with AI-powered monitoring.
Implements continuous surveillance and instant alert mechanisms for content protection.

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
import hashlib
import json
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
import websockets
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import redis
import cv2
from PIL import Image
import io
import base64
import torch
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import faiss
import xxhash

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Violation type enumeration."""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    CONTENT_THEFT = "content_theft"
    DEEPFAKE_DETECTION = "deepfake_detection"
    PLAGIARISM = "plagiarism"
    BRAND_IMPERSONATION = "brand_impersonation"
    COUNTERFEIT_CONTENT = "counterfeit_content"

class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class DetectionStatus(Enum):
    """Detection status enumeration."""
    MONITORING = "monitoring"
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"

class MonitoringChannel(Enum):
    """Monitoring channel types."""
    WEB_CRAWLER = "web_crawler"
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    MARKETPLACE = "marketplace"
    SEARCH_ENGINE = "search_engine"
    API_WEBHOOK = "api_webhook"
    USER_REPORT = "user_report"

@dataclass
class ViolationAlert:
    """Real-time violation alert structure."""
    alert_id: str
    violation_type: ViolationType
    severity: AlertSeverity
    status: DetectionStatus
    original_content_id: str
    detected_url: str
    platform: str
    confidence_score: float
    similarity_score: float
    detection_method: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    detection_timestamp: datetime = field(default_factory=datetime.now)
    investigation_notes: List[str] = field(default_factory=list)
    false_positive_probability: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'violation_type': self.violation_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'original_content_id': self.original_content_id,
            'detected_url': self.detected_url,
            'platform': self.platform,
            'confidence_score': self.confidence_score,
            'similarity_score': self.similarity_score,
            'detection_method': self.detection_method,
            'evidence': self.evidence,
            'metadata': self.metadata,
            'detection_timestamp': self.detection_timestamp.isoformat(),
            'investigation_notes': self.investigation_notes,
            'false_positive_probability': self.false_positive_probability
        }

@dataclass
class MonitoringTarget:
    """Content monitoring target."""
    target_id: str
    content_id: str
    content_type: str
    fingerprints: Dict[str, Any]
    keywords: List[str]
    monitoring_channels: List[MonitoringChannel]
    owner_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_scan: Optional[datetime] = None
    scan_frequency: int = 3600  # seconds
    active: bool = True

@dataclass
class DetectionRule:
    """Violation detection rule."""
    rule_id: str
    name: str
    violation_type: ViolationType
    conditions: Dict[str, Any]
    threshold: float
    severity: AlertSeverity
    auto_action: Optional[str] = None
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

class RealTimeViolationDetector:
    """
    Professional real-time violation detection system.
    
    Features:
    - Real-time content monitoring across multiple platforms
    - AI-powered similarity detection and matching
    - Automated alert generation and escalation
    - Multi-modal content analysis (text, image, video, audio)
    - False positive reduction with ML models
    - Configurable detection rules and thresholds
    - Real-time notification and webhook systems
    - Evidence collection and preservation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the real-time violation detector."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self._init_storage()
        self._init_ai_models()
        self._init_monitoring_system()
        
        # Configuration parameters
        self.detection_threshold = self.config.get('detection_threshold', 0.85)
        self.false_positive_threshold = self.config.get('false_positive_threshold', 0.3)
        self.max_concurrent_detections = self.config.get('max_concurrent_detections', 100)
        self.alert_cooldown = self.config.get('alert_cooldown', 300)  # 5 minutes
        
        # State management
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        self.detection_rules: Dict[str, DetectionRule] = {}
        self.active_alerts: Dict[str, ViolationAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.recent_alerts: Dict[str, datetime] = {}  # URL -> last alert time
        
        # Event handlers
        self.alert_handlers: List[Callable[[ViolationAlert], None]] = []
        self.webhook_urls: List[str] = []
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.monitoring_active = False
        self.monitoring_thread = None
        
        self.logger.info("RealTimeViolationDetector initialized successfully")
    
    def _init_storage(self) -> None:
        """Initialize storage systems."""
        try:
            # Redis for real-time data
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage: {e}")
            # Use fallback in-memory storage
            self.redis_client = None
    
    def _init_ai_models(self) -> None:
        """Initialize AI models for detection."""
        try:
            # CLIP model for visual similarity
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Sentence transformer for text similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize FAISS indices for fast similarity search
            self.vector_dimension = 512
            self.text_index = faiss.IndexFlatIP(self.vector_dimension)
            self.image_index = faiss.IndexFlatIP(self.vector_dimension)
            
            # Content ID mappings
            self.text_content_ids = []
            self.image_content_ids = []
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def _init_monitoring_system(self) -> None:
        """Initialize monitoring system components."""
        try:
            # Initialize monitoring channels
            self.monitoring_channels = {
                MonitoringChannel.WEB_CRAWLER: self._init_web_crawler,
                MonitoringChannel.SOCIAL_MEDIA: self._init_social_media_monitor,
                MonitoringChannel.VIDEO_PLATFORM: self._init_video_platform_monitor,
                MonitoringChannel.API_WEBHOOK: self._init_webhook_monitor
            }
            
            # Load default detection rules
            self._load_default_detection_rules()
            
            self.logger.info("Monitoring system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring system: {e}")
            raise
    
    def _load_default_detection_rules(self) -> None:
        """Load default detection rules."""
        default_rules = [
            DetectionRule(
                rule_id="copyright_high_similarity",
                name="High Similarity Copyright Detection",
                violation_type=ViolationType.COPYRIGHT_INFRINGEMENT,
                conditions={'similarity_threshold': 0.90},
                threshold=0.90,
                severity=AlertSeverity.HIGH,
                auto_action="flag_and_notify"
            ),
            DetectionRule(
                rule_id="exact_duplicate_detection",
                name="Exact Duplicate Content Detection",
                violation_type=ViolationType.CONTENT_THEFT,
                conditions={'similarity_threshold': 0.98},
                threshold=0.98,
                severity=AlertSeverity.CRITICAL,
                auto_action="immediate_takedown_request"
            ),
            DetectionRule(
                rule_id="trademark_keyword_detection",
                name="Trademark Keyword Detection",
                violation_type=ViolationType.TRADEMARK_VIOLATION,
                conditions={'keyword_match': True},
                threshold=0.80,
                severity=AlertSeverity.MEDIUM,
                auto_action="flag_for_review"
            )
        ]
        
        for rule in default_rules:
            self.detection_rules[rule.rule_id] = rule
    
    async def add_monitoring_target(self, target: MonitoringTarget) -> bool:
        """Add content for monitoring."""
        try:
            # Store target
            self.monitoring_targets[target.target_id] = target
            
            # Add fingerprints to indices if available
            if 'text_embedding' in target.fingerprints:
                embedding = np.array(target.fingerprints['text_embedding']).astype(np.float32)
                if embedding.shape[0] == self.vector_dimension:
                    self.text_index.add(embedding.reshape(1, -1))
                    self.text_content_ids.append(target.content_id)
            
            if 'image_embedding' in target.fingerprints:
                embedding = np.array(target.fingerprints['image_embedding']).astype(np.float32)
                if embedding.shape[0] == self.vector_dimension:
                    self.image_index.add(embedding.reshape(1, -1))
                    self.image_content_ids.append(target.content_id)
            
            # Store in Redis if available
            if self.redis_client:
                target_data = {
                    'target_id': target.target_id,
                    'content_id': target.content_id,
                    'content_type': target.content_type,
                    'keywords': json.dumps(target.keywords),
                    'owner_id': target.owner_id,
                    'active': target.active
                }
                self.redis_client.hset(f"target:{target.target_id}", mapping=target_data)
            
            self.logger.info(f"Added monitoring target: {target.target_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add monitoring target: {e}")
            return False
    
    async def start_monitoring(self) -> None:
        """Start real-time monitoring."""
        if self.monitoring_active:
            self.logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Real-time monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in separate thread."""
        while self.monitoring_active:
            try:
                # Check each monitoring target
                for target in list(self.monitoring_targets.values()):
                    if not target.active:
                        continue
                    
                    # Check if it's time to scan
                    if self._should_scan_target(target):
                        asyncio.run(self._scan_target(target))
                
                # Sleep before next iteration
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _should_scan_target(self, target: MonitoringTarget) -> bool:
        """Check if target should be scanned."""
        if target.last_scan is None:
            return True
        
        time_since_scan = (datetime.now() - target.last_scan).total_seconds()
        return time_since_scan >= target.scan_frequency
    
    async def _scan_target(self, target: MonitoringTarget) -> None:
        """Scan a specific monitoring target."""
        try:
            target.last_scan = datetime.now()
            
            # Scan across different channels
            for channel in target.monitoring_channels:
                if channel in self.monitoring_channels:
                    await self.monitoring_channels[channel](target)
            
        except Exception as e:
            self.logger.error(f"Failed to scan target {target.target_id}: {e}")
    
    async def _init_web_crawler(self, target: MonitoringTarget) -> None:
        """Initialize web crawler monitoring."""
        # Implementation for web crawler
        await self._perform_web_search(target)
    
    async def _init_social_media_monitor(self, target: MonitoringTarget) -> None:
        """Initialize social media monitoring."""
        # Implementation for social media monitoring
        await self._perform_social_media_search(target)
    
    async def _init_video_platform_monitor(self, target: MonitoringTarget) -> None:
        """Initialize video platform monitoring."""
        # Implementation for video platform monitoring
        await self._perform_video_platform_search(target)
    
    async def _init_webhook_monitor(self, target: MonitoringTarget) -> None:
        """Initialize webhook monitoring."""
        # Webhook monitoring is passive - handled by receive_webhook
        pass
    
    async def _perform_web_search(self, target: MonitoringTarget) -> None:
        """Perform web search for potential violations."""
        try:
            # Search using keywords
            for keyword in target.keywords:
                search_results = await self._search_web(keyword, target.content_type)
                
                for result in search_results:
                    await self._analyze_search_result(target, result, "web_search")
        
        except Exception as e:
            self.logger.error(f"Web search failed for target {target.target_id}: {e}")
    
    async def _perform_social_media_search(self, target: MonitoringTarget) -> None:
        """Perform social media search."""
        # Implementation depends on available APIs
        platforms = ['twitter', 'instagram', 'facebook', 'tiktok']
        
        for platform in platforms:
            try:
                results = await self._search_social_platform(platform, target.keywords)
                
                for result in results:
                    await self._analyze_search_result(target, result, f"social_{platform}")
            
            except Exception as e:
                self.logger.error(f"Social media search failed for {platform}: {e}")
    
    async def _perform_video_platform_search(self, target: MonitoringTarget) -> None:
        """Perform video platform search."""
        platforms = ['youtube', 'vimeo', 'dailymotion']
        
        for platform in platforms:
            try:
                results = await self._search_video_platform(platform, target.keywords)
                
                for result in results:
                    await self._analyze_search_result(target, result, f"video_{platform}")
            
            except Exception as e:
                self.logger.error(f"Video platform search failed for {platform}: {e}")
    
    async def _search_web(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search the web for content."""
        # Implement web search using search engines or custom crawlers
        # This is a simplified version
        search_results = []
        
        try:
            # Example using a search API (would need real implementation)
            async with aiohttp.ClientSession() as session:
                # Placeholder for actual search implementation
                pass
            
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
        
        return search_results
    
    async def _search_social_platform(self, platform: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search social media platform."""
        # Implement platform-specific search
        # This would use platform APIs or web scraping
        results = []
        
        try:
            # Platform-specific implementation needed
            pass
            
        except Exception as e:
            self.logger.error(f"Social platform search error for {platform}: {e}")
        
        return results
    
    async def _search_video_platform(self, platform: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search video platform."""
        # Implement video platform search
        results = []
        
        try:
            # Platform-specific implementation needed
            pass
            
        except Exception as e:
            self.logger.error(f"Video platform search error for {platform}: {e}")
        
        return results
    
    async def _analyze_search_result(
        self,
        target: MonitoringTarget,
        result: Dict[str, Any],
        detection_method: str
    ) -> None:
        """Analyze search result for potential violations."""
        try:
            result_url = result.get('url', '')
            
            # Check cooldown period
            if self._is_in_cooldown(result_url):
                return
            
            # Extract content from result
            content_data = await self._extract_content_from_result(result)
            
            if not content_data:
                return
            
            # Perform similarity analysis
            similarity_scores = await self._calculate_similarity_scores(target, content_data)
            
            # Check against detection rules
            violations = await self._check_detection_rules(target, result, similarity_scores)
            
            # Generate alerts for detected violations
            for violation in violations:
                await self._generate_violation_alert(
                    target, result, violation, detection_method, similarity_scores
                )
        
        except Exception as e:
            self.logger.error(f"Failed to analyze search result: {e}")
    
    def _is_in_cooldown(self, url: str) -> bool:
        """Check if URL is in alert cooldown period."""
        if url not in self.recent_alerts:
            return False
        
        time_since_alert = (datetime.now() - self.recent_alerts[url]).total_seconds()
        return time_since_alert < self.alert_cooldown
    
    async def _extract_content_from_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract content from search result."""
        content_data = {}
        
        try:
            # Extract text content
            if 'text' in result:
                content_data['text'] = result['text']
            elif 'description' in result:
                content_data['text'] = result['description']
            
            # Extract image content
            if 'image_url' in result:
                image_data = await self._download_image(result['image_url'])
                if image_data:
                    content_data['image'] = image_data
            
            # Extract video content (thumbnail or keyframes)
            if 'video_url' in result:
                video_data = await self._extract_video_frames(result['video_url'])
                if video_data:
                    content_data['video_frames'] = video_data
            
            return content_data if content_data else None
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from result: {e}")
            return None
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=10) as response:
                    if response.status == 200:
                        return await response.read()
            
        except Exception as e:
            self.logger.error(f"Failed to download image: {e}")
        
        return None
    
    async def _extract_video_frames(self, video_url: str) -> Optional[List[bytes]]:
        """Extract key frames from video."""
        # Implementation would extract key frames from video
        # This is a simplified placeholder
        return None
    
    async def _calculate_similarity_scores(
        self,
        target: MonitoringTarget,
        content_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate similarity scores between target and found content."""
        similarity_scores = {}
        
        try:
            # Text similarity
            if 'text' in content_data and 'text_embedding' in target.fingerprints:
                text_similarity = await self._calculate_text_similarity(
                    target.fingerprints['text_embedding'],
                    content_data['text']
                )
                similarity_scores['text'] = text_similarity
            
            # Image similarity
            if 'image' in content_data and 'image_embedding' in target.fingerprints:
                image_similarity = await self._calculate_image_similarity(
                    target.fingerprints['image_embedding'],
                    content_data['image']
                )
                similarity_scores['image'] = image_similarity
            
            # Keyword matching
            if 'text' in content_data:
                keyword_score = self._calculate_keyword_similarity(
                    target.keywords,
                    content_data['text']
                )
                similarity_scores['keywords'] = keyword_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity scores: {e}")
        
        return similarity_scores
    
    async def _calculate_text_similarity(
        self,
        target_embedding: List[float],
        found_text: str
    ) -> float:
        """Calculate text similarity using embeddings."""
        try:
            # Generate embedding for found text
            found_embedding = self.sentence_model.encode([found_text])[0]
            
            # Calculate cosine similarity
            target_array = np.array(target_embedding)
            found_array = np.array(found_embedding)
            
            # Ensure same dimensions
            min_dim = min(len(target_array), len(found_array))
            target_array = target_array[:min_dim]
            found_array = found_array[:min_dim]
            
            # Normalize vectors
            target_norm = target_array / np.linalg.norm(target_array)
            found_norm = found_array / np.linalg.norm(found_array)
            
            # Calculate similarity
            similarity = np.dot(target_norm, found_norm)
            
            return float(max(0, similarity))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate text similarity: {e}")
            return 0.0
    
    async def _calculate_image_similarity(
        self,
        target_embedding: List[float],
        found_image: bytes
    ) -> float:
        """Calculate image similarity using CLIP embeddings."""
        try:
            # Load image
            image = Image.open(io.BytesIO(found_image))
            
            # Generate CLIP embedding
            inputs = self.clip_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            found_embedding = image_features.numpy().flatten()
            
            # Calculate similarity
            target_array = np.array(target_embedding)
            found_array = np.array(found_embedding)
            
            # Ensure same dimensions
            min_dim = min(len(target_array), len(found_array))
            target_array = target_array[:min_dim]
            found_array = found_array[:min_dim]
            
            # Normalize vectors
            target_norm = target_array / np.linalg.norm(target_array)
            found_norm = found_array / np.linalg.norm(found_array)
            
            # Calculate similarity
            similarity = np.dot(target_norm, found_norm)
            
            return float(max(0, similarity))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate image similarity: {e}")
            return 0.0
    
    def _calculate_keyword_similarity(self, target_keywords: List[str], found_text: str) -> float:
        """Calculate keyword-based similarity."""
        if not target_keywords or not found_text:
            return 0.0
        
        found_text_lower = found_text.lower()
        matches = 0
        
        for keyword in target_keywords:
            if keyword.lower() in found_text_lower:
                matches += 1
        
        return matches / len(target_keywords)
    
    async def _check_detection_rules(
        self,
        target: MonitoringTarget,
        result: Dict[str, Any],
        similarity_scores: Dict[str, float]
    ) -> List[DetectionRule]:
        """Check similarity scores against detection rules."""
        violations = []
        
        for rule in self.detection_rules.values():
            if not rule.active:
                continue
            
            if await self._rule_matches(rule, target, result, similarity_scores):
                violations.append(rule)
        
        return violations
    
    async def _rule_matches(
        self,
        rule: DetectionRule,
        target: MonitoringTarget,
        result: Dict[str, Any],
        similarity_scores: Dict[str, float]
    ) -> bool:
        """Check if a detection rule matches."""
        try:
            conditions = rule.conditions
            
            # Check similarity threshold
            if 'similarity_threshold' in conditions:
                threshold = conditions['similarity_threshold']
                max_similarity = max(similarity_scores.values()) if similarity_scores else 0
                
                if max_similarity < threshold:
                    return False
            
            # Check keyword matching
            if 'keyword_match' in conditions and conditions['keyword_match']:
                if 'keywords' not in similarity_scores or similarity_scores['keywords'] < 0.5:
                    return False
            
            # Additional rule conditions can be added here
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check rule match: {e}")
            return False
    
    async def _generate_violation_alert(
        self,
        target: MonitoringTarget,
        result: Dict[str, Any],
        rule: DetectionRule,
        detection_method: str,
        similarity_scores: Dict[str, float]
    ) -> None:
        """Generate violation alert."""
        try:
            alert_id = self._generate_alert_id()
            detected_url = result.get('url', '')
            platform = result.get('platform', 'unknown')
            
            # Calculate overall confidence
            confidence_score = await self._calculate_confidence_score(similarity_scores, rule)
            
            # Get maximum similarity score
            max_similarity = max(similarity_scores.values()) if similarity_scores else 0
            
            # Calculate false positive probability
            false_positive_prob = await self._calculate_false_positive_probability(
                target, result, similarity_scores
            )
            
            # Create alert
            alert = ViolationAlert(
                alert_id=alert_id,
                violation_type=rule.violation_type,
                severity=rule.severity,
                status=DetectionStatus.DETECTED,
                original_content_id=target.content_id,
                detected_url=detected_url,
                platform=platform,
                confidence_score=confidence_score,
                similarity_score=max_similarity,
                detection_method=detection_method,
                evidence={
                    'similarity_scores': similarity_scores,
                    'detection_rule': rule.rule_id,
                    'search_result': result
                },
                metadata={
                    'target_id': target.target_id,
                    'owner_id': target.owner_id,
                    'keywords_matched': target.keywords
                },
                false_positive_probability=false_positive_prob
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            self.recent_alerts[detected_url] = datetime.now()
            
            # Store in Redis if available
            if self.redis_client:
                self.redis_client.set(
                    f"alert:{alert_id}",
                    json.dumps(alert.to_dict()),
                    ex=86400 * 30  # 30 days
                )
            
            # Trigger alert handlers
            await self._trigger_alert_handlers(alert)
            
            self.logger.info(f"Generated violation alert: {alert_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate violation alert: {e}")
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        timestamp = str(int(time.time() * 1000))
        random_suffix = xxhash.xxh32(timestamp).hexdigest()[:8]
        return f"alert_{timestamp}_{random_suffix}"
    
    async def _calculate_confidence_score(
        self,
        similarity_scores: Dict[str, float],
        rule: DetectionRule
    ) -> float:
        """Calculate overall confidence score for detection."""
        if not similarity_scores:
            return 0.0
        
        # Weight different similarity types
        weights = {
            'text': 0.3,
            'image': 0.4,
            'keywords': 0.2,
            'audio': 0.3,
            'video': 0.4
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for score_type, score in similarity_scores.items():
            if score_type in weights:
                weight = weights[score_type]
                weighted_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        base_confidence = weighted_score / total_weight
        
        # Adjust based on rule severity
        severity_multiplier = {
            AlertSeverity.LOW: 0.8,
            AlertSeverity.MEDIUM: 0.9,
            AlertSeverity.HIGH: 1.0,
            AlertSeverity.CRITICAL: 1.1,
            AlertSeverity.EMERGENCY: 1.2
        }
        
        multiplier = severity_multiplier.get(rule.severity, 1.0)
        adjusted_confidence = min(1.0, base_confidence * multiplier)
        
        return adjusted_confidence
    
    async def _calculate_false_positive_probability(
        self,
        target: MonitoringTarget,
        result: Dict[str, Any],
        similarity_scores: Dict[str, float]
    ) -> float:
        """Calculate probability of false positive."""
        # This would use ML models trained on historical data
        # For now, use heuristic approach
        
        factors = []
        
        # Low similarity across multiple modalities reduces false positive risk
        num_high_similarities = sum(1 for score in similarity_scores.values() if score > 0.8)
        if num_high_similarities >= 2:
            factors.append(0.1)  # Low false positive risk
        elif num_high_similarities == 1:
            factors.append(0.3)  # Medium risk
        else:
            factors.append(0.7)  # High risk
        
        # Check for common false positive patterns
        result_url = result.get('url', '').lower()
        if any(domain in result_url for domain in ['wikipedia', 'dictionary', 'news']):
            factors.append(0.6)  # Higher false positive risk for reference sites
        
        # Calculate average
        return sum(factors) / len(factors) if factors else 0.5
    
    async def _trigger_alert_handlers(self, alert: ViolationAlert) -> None:
        """Trigger all registered alert handlers."""
        try:
            # Call registered handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    self.logger.error(f"Alert handler error: {e}")
            
            # Send webhook notifications
            await self._send_webhook_notifications(alert)
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert handlers: {e}")
    
    async def _send_webhook_notifications(self, alert: ViolationAlert) -> None:
        """Send webhook notifications for alert."""
        if not self.webhook_urls:
            return
        
        webhook_data = alert.to_dict()
        
        for webhook_url in self.webhook_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook_url,
                        json=webhook_data,
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            self.logger.info(f"Webhook notification sent to {webhook_url}")
                        else:
                            self.logger.warning(f"Webhook failed: {response.status}")
            
            except Exception as e:
                self.logger.error(f"Webhook notification error: {e}")
    
    def add_alert_handler(self, handler: Callable[[ViolationAlert], None]) -> None:
        """Add alert handler function."""
        self.alert_handlers.append(handler)
    
    def add_webhook_url(self, url: str) -> None:
        """Add webhook URL for notifications."""
        self.webhook_urls.append(url)
    
    async def receive_webhook(self, webhook_data: Dict[str, Any]) -> None:
        """Receive webhook data for processing."""
        try:
            # Process webhook data for potential violations
            # This would be called by webhook endpoints
            
            # Extract relevant information
            content_url = webhook_data.get('url')
            content_type = webhook_data.get('type')
            content_data = webhook_data.get('content')
            
            if not content_url or not content_data:
                return
            
            # Check against all monitoring targets
            for target in self.monitoring_targets.values():
                if not target.active:
                    continue
                
                # Calculate similarities
                similarity_scores = await self._calculate_similarity_scores(target, content_data)
                
                # Check detection rules
                violations = await self._check_detection_rules(target, webhook_data, similarity_scores)
                
                # Generate alerts
                for violation in violations:
                    await self._generate_violation_alert(
                        target, webhook_data, violation, "webhook", similarity_scores
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to process webhook: {e}")
    
    async def get_active_alerts(
        self,
        severity_filter: Optional[AlertSeverity] = None,
        status_filter: Optional[DetectionStatus] = None
    ) -> List[ViolationAlert]:
        """Get active alerts with optional filtering."""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [alert for alert in alerts if alert.severity == severity_filter]
        
        if status_filter:
            alerts = [alert for alert in alerts if alert.status == status_filter]
        
        return sorted(alerts, key=lambda x: x.detection_timestamp, reverse=True)
    
    async def update_alert_status(self, alert_id: str, new_status: DetectionStatus) -> bool:
        """Update alert status."""
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].status = new_status
                
                # Update in Redis if available
                if self.redis_client:
                    alert_data = self.active_alerts[alert_id].to_dict()
                    self.redis_client.set(f"alert:{alert_id}", json.dumps(alert_data), ex=86400 * 30)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update alert status: {e}")
            return False
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection system statistics."""
        try:
            total_alerts = len(self.alert_history)
            active_alerts = len(self.active_alerts)
            monitoring_targets = len([t for t in self.monitoring_targets.values() if t.active])
            
            # Calculate alert distribution by severity
            severity_distribution = defaultdict(int)
            for alert in self.alert_history:
                severity_distribution[alert.severity.name] += 1
            
            # Calculate false positive rate
            false_positives = len([
                alert for alert in self.alert_history
                if alert.status == DetectionStatus.FALSE_POSITIVE
            ])
            false_positive_rate = false_positives / total_alerts if total_alerts > 0 else 0
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'monitoring_targets': monitoring_targets,
                'false_positive_rate': false_positive_rate,
                'severity_distribution': dict(severity_distribution),
                'monitoring_active': self.monitoring_active,
                'system_uptime': self._get_system_uptime()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get detection statistics: {e}")
            return {}
    
    def _get_system_uptime(self) -> str:
        """Get system uptime."""
        # This would track actual uptime
        return "N/A"
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if self.monitoring_active:
                self.monitoring_active = False
            
            if self.executor:
                self.executor.shutdown(wait=False)
            
        except Exception:
            pass

# Export main classes
__all__ = [
    'RealTimeViolationDetector',
    'ViolationAlert',
    'MonitoringTarget',
    'DetectionRule',
    'ViolationType',
    'AlertSeverity',
    'DetectionStatus',
    'MonitoringChannel'
]
