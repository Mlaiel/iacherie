"""
Content Matching Engine - Moteur Matching Contenu
=================================================

 PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

© 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Advanced content matching engine for copyright protection and similarity detection.
Provides sophisticated content analysis, fingerprinting, and matching capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import re
import hashlib
import base64
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    WEBPAGE = "webpage"


class MatchType(Enum):
    """Content match type."""
    EXACT = "exact"
    SIMILARITY = "similarity"
    DERIVATIVE = "derivative"
    PARTIAL = "partial"
    TRANSFORMED = "transformed"


@dataclass
class ContentFingerprint:
    """Content fingerprint data."""
    fingerprint_id: str
    content_id: str
    content_type: ContentType
    hash_value: str
    perceptual_hash: Optional[str] = None
    feature_vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    duration_seconds: Optional[float] = None


@dataclass
class ProtectedContent:
    """Protected content entry."""
    content_id: str
    owner_id: str
    owner_name: str
    title: str
    description: str
    content_type: ContentType
    fingerprints: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    protection_level: str = "standard"  # basic, standard, strict, maximum
    auto_takedown: bool = False
    notification_emails: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    active: bool = True


@dataclass
class ContentMatch:
    """Content match result."""
    match_id: str
    original_content_id: str
    matched_content_id: str
    match_type: MatchType
    similarity_score: float
    confidence_score: float
    fingerprint_matches: List[str] = field(default_factory=list)
    matched_segments: List[Dict[str, Any]] = field(default_factory=list)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)
    platform: str = ""
    url: str = ""
    user_id: str = ""
    username: str = ""
    verified: bool = False
    false_positive: bool = False


@dataclass
class MatchingTask:
    """Content matching task."""
    task_id: str
    content_id: str
    content_type: ContentType
    priority: int = 1  # 1=highest, 5=lowest
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    matches_found: int = 0
    processing_time_seconds: float = 0.0


@dataclass
class MatchingMetrics:
    """Content matching engine metrics."""
    total_protected_content: int = 0
    total_fingerprints: int = 0
    total_matches_found: int = 0
    total_tasks_processed: int = 0
    tasks_pending: int = 0
    tasks_running: int = 0
    average_processing_time_seconds: float = 0.0
    accuracy_rate: float = 0.0
    false_positive_rate: float = 0.0
    content_types_processed: Dict[str, int] = field(default_factory=dict)
    last_match: Optional[datetime] = None
    system_uptime_seconds: float = 0.0


class ContentMatchingEngine:
    """
    Advanced content matching engine for copyright protection.
    
    Features:
    - Multi-modal content fingerprinting (text, image, video, audio)
    - Perceptual hashing for media content
    - Semantic similarity analysis
    - Real-time content matching
    - Copyright protection management
    - Automated takedown capabilities
    - Advanced analytics and reporting
    - Scalable processing architecture
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content matching engine."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 20)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.8)
        self.enable_ml_analysis = self.config.get('enable_ml_analysis', True)
        self.enable_perceptual_hashing = self.config.get('enable_perceptual_hashing', True)
        self.enable_semantic_analysis = self.config.get('enable_semantic_analysis', True)
        
        # Engine state
        self.metrics = MatchingMetrics()
        self._matching_active = False
        self._processing_task: Optional[asyncio.Task] = None
        self._start_time = datetime.now()
        
        # Content storage
        self.protected_content: Dict[str, ProtectedContent] = {}
        self.content_fingerprints: Dict[str, ContentFingerprint] = {}
        self.content_matches: Dict[str, ContentMatch] = {}
        
        # Task management
        self.matching_tasks: Dict[str, MatchingTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Set[str] = set()
        
        # Fingerprinting algorithms
        self.text_fingerprinters = {}
        self.image_fingerprinters = {}
        self.video_fingerprinters = {}
        self.audio_fingerprinters = {}
        
        # ML models
        self.similarity_models = {}
        self.feature_extractors = {}
        
        self._logger.info("Content Matching Engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the content matching engine."""



        try:
            self._logger.info("Initializing content matching engine...")
            
            # Initialize fingerprinting algorithms
            await self._initialize_fingerprinting()
            
            # Initialize ML models
            if self.enable_ml_analysis:
                await self._initialize_ml_models()
            
            # Setup content analysis pipelines
            await self._setup_analysis_pipelines()
            
            self._logger.info("Content matching engine initialization complete")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize content matching engine: {e}")
            raise
    
    async def _initialize_fingerprinting(self) -> None:
        """Initialize fingerprinting algorithms."""



        try:
            # This would initialize actual fingerprinting algorithms
            # For now, implement placeholders
            self.text_fingerprinters['hash'] = self._compute_text_hash
            self.text_fingerprinters['shingle'] = self._compute_text_shingles
            
            self.image_fingerprinters['phash'] = self._compute_image_perceptual_hash
            self.image_fingerprinters['dhash'] = self._compute_image_difference_hash
            
            self.video_fingerprinters['temporal'] = self._compute_video_temporal_hash
            self.video_fingerprinters['frame'] = self._compute_video_frame_hash
            
            self.audio_fingerprinters['chromaprint'] = self._compute_audio_chromaprint
            self.audio_fingerprinters['mfcc'] = self._compute_audio_mfcc
            
            self._logger.debug("Fingerprinting algorithms initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize fingerprinting: {e}")
            raise
    
    async def _initialize_ml_models(self) -> None:
        """Initialize ML models for content analysis."""



        try:
            # This would load actual ML models
            # For now, implement placeholders
            self.similarity_models['text'] = "text_similarity_model"
            self.similarity_models['image'] = "image_similarity_model"
            self.similarity_models['video'] = "video_similarity_model"
            self.similarity_models['audio'] = "audio_similarity_model"
            
            self.feature_extractors['text'] = "text_feature_extractor"
            self.feature_extractors['image'] = "image_feature_extractor"
            self.feature_extractors['video'] = "video_feature_extractor"
            self.feature_extractors['audio'] = "audio_feature_extractor"
            
            self._logger.debug("ML models initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize ML models: {e}")
            raise
    
    async def _setup_analysis_pipelines(self) -> None:
        """Setup content analysis pipelines."""



        try:
            # This would setup actual analysis pipelines
            # For now, implement placeholder
            self._logger.debug("Analysis pipelines setup complete")
            
        except Exception as e:
            self._logger.error(f"Failed to setup analysis pipelines: {e}")
            raise
    
    async def start_matching_engine(self) -> None:
        """Start the content matching engine."""



        try:
            if self._matching_active:
                self._logger.warning("Content matching engine is already active")
                return
            
            self._logger.info("Starting content matching engine...")
            
            self._matching_active = True
            self._processing_task = asyncio.create_task(self._process_matching_tasks())
            
            self._logger.info("Content matching engine started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start content matching engine: {e}")
            self._matching_active = False
            raise
    
    async def stop_matching_engine(self) -> None:
        """Stop the content matching engine."""



        try:
            if not self._matching_active:
                self._logger.warning("Content matching engine is not active")
                return
            
            self._logger.info("Stopping content matching engine...")
            
            self._matching_active = False
            
            if self._processing_task and not self._processing_task.done():
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            
            self._logger.info("Content matching engine stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping content matching engine: {e}")
            raise
    
    async def register_protected_content(
        self,
        owner_id: str,
        owner_name: str,
        title: str,
        content_data: bytes,
        content_type: ContentType,
        protection_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register content for protection."""



        try:
            content_id = f"content_{datetime.now().timestamp()}_{hash(title) % 10000}"
            
            config = protection_config or {}
            
            protected_content = ProtectedContent(
                content_id=content_id,
                owner_id=owner_id,
                owner_name=owner_name,
                title=title,
                description=config.get('description', ''),
                content_type=content_type,
                tags=config.get('tags', []),
                copyright_info=config.get('copyright_info', {}),
                protection_level=config.get('protection_level', 'standard'),
                auto_takedown=config.get('auto_takedown', False),
                notification_emails=config.get('notification_emails', []),
                expires_at=config.get('expires_at')
            )
            
            self.protected_content[content_id] = protected_content
            
            # Generate fingerprints
            fingerprints = await self._generate_content_fingerprints(content_id, content_data, content_type)
            protected_content.fingerprints = [fp.fingerprint_id for fp in fingerprints]
            
            self.metrics.total_protected_content += 1
            self.metrics.total_fingerprints += len(fingerprints)
            
            self._logger.info(f"Registered protected content: {content_id} ({content_type.value})")
            return content_id
            
        except Exception as e:
            self._logger.error(f"Failed to register protected content: {e}")
            raise
    
    async def submit_content_for_matching(
        self,
        content_data: bytes,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit content for matching against protected content."""



        try:
            task_id = f"task_{datetime.now().timestamp()}_{hash(str(content_data[:100])) % 10000}"
            
            content_id = f"candidate_{task_id}"
            
            task = MatchingTask(
                task_id=task_id,
                content_id=content_id,
                content_type=content_type
            )
            
            self.matching_tasks[task_id] = task
            
            # Store content for processing
            await self._store_candidate_content(content_id, content_data, content_type, metadata or {})
            
            # Add to processing queue
            await self.task_queue.put(task_id)
            
            self._logger.info(f"Submitted content for matching: {task_id} ({content_type.value})")
            return task_id
            
        except Exception as e:
            self._logger.error(f"Failed to submit content for matching: {e}")
            raise
    
    async def get_matching_results(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get matching results for a task."""



        try:
            if task_id not in self.matching_tasks:
                return None
            
            task = self.matching_tasks[task_id]
            
            # Get matches for this content
            matches = [
                match for match in self.content_matches.values()
                if match.matched_content_id == task.content_id
            ]
            
            return {
                'task_id': task_id,
                'status': task.status,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'processing_time_seconds': task.processing_time_seconds,
                'matches_found': len(matches),
                'matches': [
                    {
                        'match_id': m.match_id,
                        'original_content_id': m.original_content_id,
                        'match_type': m.match_type.value,
                        'similarity_score': m.similarity_score,
                        'confidence_score': m.confidence_score,
                        'detected_at': m.detected_at.isoformat()
                    }
                    for m in matches
                ]
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get matching results for {task_id}: {e}")
            return None
    
    async def _process_matching_tasks(self) -> None:
        """Process matching tasks from the queue."""
        self._logger.info("Content matching task processing started")
        
        try:
            while self._matching_active:
                try:
                    # Limit concurrent tasks
                    if len(self.active_tasks) >= self.max_concurrent_tasks:
                        await asyncio.sleep(1)
                        continue
                    
                    # Get next task
                    try:
                        task_id = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    except asyncio.TimeoutError:
                        continue
                    
                    if task_id in self.matching_tasks:
                        asyncio.create_task(self._execute_matching_task(task_id))
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._logger.error(f"Error processing matching tasks: {e}")
                    await asyncio.sleep(5)
        
        except asyncio.CancelledError:
            pass
        
        self._logger.info("Content matching task processing stopped")
    
    async def _execute_matching_task(self, task_id: str) -> None:
        """Execute a content matching task."""



        try:
            task = self.matching_tasks[task_id]
            self.active_tasks.add(task_id)
            
            task.status = "running"
            task.started_at = datetime.now()
            
            self._logger.debug(f"Executing matching task: {task_id}")
            
            # Generate fingerprints for candidate content
            candidate_fingerprints = await self._get_candidate_fingerprints(task.content_id, task.content_type)
            
            # Compare against all protected content
            matches = []
            
            for protected_id, protected_content in self.protected_content.items():
                if not protected_content.active:
                    continue
                
                if protected_content.content_type != task.content_type:
                    continue
                
                # Compare fingerprints
                content_matches = await self._compare_content_fingerprints(
                    protected_id,
                    task.content_id,
                    protected_content.fingerprints,
                    candidate_fingerprints
                )
                
                matches.extend(content_matches)
            
            # Store matches
            for match in matches:
                self.content_matches[match.match_id] = match
            
            task.matches_found = len(matches)
            task.status = "completed"
            task.completed_at = datetime.now()
            task.processing_time_seconds = (task.completed_at - task.started_at).total_seconds()
            
            # Update metrics
            self.metrics.total_matches_found += len(matches)
            self.metrics.total_tasks_processed += 1
            
            if matches:
                self.metrics.last_match = datetime.now()
                
                # Update content type metrics
                content_type_key = task.content_type.value
                if content_type_key not in self.metrics.content_types_processed:
                    self.metrics.content_types_processed[content_type_key] = 0
                self.metrics.content_types_processed[content_type_key] += 1
            
            # Update average processing time
            if self.metrics.average_processing_time_seconds == 0:
                self.metrics.average_processing_time_seconds = task.processing_time_seconds
            else:
                self.metrics.average_processing_time_seconds = (
                    self.metrics.average_processing_time_seconds * 0.9 + 
                    task.processing_time_seconds * 0.1
                )
            
            self._logger.info(f"Completed matching task: {task_id} - {len(matches)} matches found")
            
        except Exception as e:
            self._logger.error(f"Error executing matching task {task_id}: {e}")
            
            task = self.matching_tasks[task_id]
            task.status = "failed"
            task.completed_at = datetime.now()
            task.error_message = str(e)
        
        finally:
            self.active_tasks.discard(task_id)
    
    async def _generate_content_fingerprints(
        self,
        content_id: str,
        content_data: bytes,
        content_type: ContentType
    ) -> List[ContentFingerprint]:
        """Generate fingerprints for content."""
        fingerprints = []
        
        try:
            if content_type == ContentType.TEXT:
                fingerprints.extend(await self._generate_text_fingerprints(content_id, content_data))
            elif content_type == ContentType.IMAGE:
                fingerprints.extend(await self._generate_image_fingerprints(content_id, content_data))
            elif content_type == ContentType.VIDEO:
                fingerprints.extend(await self._generate_video_fingerprints(content_id, content_data))
            elif content_type == ContentType.AUDIO:
                fingerprints.extend(await self._generate_audio_fingerprints(content_id, content_data))
            
            # Store fingerprints
            for fingerprint in fingerprints:
                self.content_fingerprints[fingerprint.fingerprint_id] = fingerprint
            
        except Exception as e:
            self._logger.error(f"Error generating fingerprints for {content_id}: {e}")
        
        return fingerprints
    
    async def _generate_text_fingerprints(
        self,
        content_id: str,
        content_data: bytes
    ) -> List[ContentFingerprint]:
        """Generate text content fingerprints."""
        fingerprints = []
        
        try:
            text_content = content_data.decode('utf-8', errors='ignore')
            
            # Hash-based fingerprint
            hash_value = hashlib.sha256(text_content.encode()).hexdigest()
            
            fingerprint = ContentFingerprint(
                fingerprint_id=f"text_hash_{content_id}",
                content_id=content_id,
                content_type=ContentType.TEXT,
                hash_value=hash_value,
                size_bytes=len(content_data)
            )
            fingerprints.append(fingerprint)
            
            # Shingle-based fingerprint (for similarity detection)
            shingles = await self._compute_text_shingles(text_content)
            shingle_hash = hashlib.sha256(json.dumps(sorted(shingles)).encode()).hexdigest()
            
            shingle_fingerprint = ContentFingerprint(
                fingerprint_id=f"text_shingle_{content_id}",
                content_id=content_id,
                content_type=ContentType.TEXT,
                hash_value=shingle_hash,
                metadata={'shingles': shingles},
                size_bytes=len(content_data)
            )
            fingerprints.append(shingle_fingerprint)
            
        except Exception as e:
            self._logger.error(f"Error generating text fingerprints: {e}")
        
        return fingerprints
    
    async def _generate_image_fingerprints(
        self,
        content_id: str,
        content_data: bytes
    ) -> List[ContentFingerprint]:
        """Generate image content fingerprints."""
        fingerprints = []
        
        try:
            # Hash-based fingerprint
            hash_value = hashlib.sha256(content_data).hexdigest()
            
            fingerprint = ContentFingerprint(
                fingerprint_id=f"image_hash_{content_id}",
                content_id=content_id,
                content_type=ContentType.IMAGE,
                hash_value=hash_value,
                size_bytes=len(content_data)
            )
            fingerprints.append(fingerprint)
            
            if self.enable_perceptual_hashing:
                # Perceptual hash fingerprint
                perceptual_hash = await self._compute_image_perceptual_hash(content_data)
                
                perceptual_fingerprint = ContentFingerprint(
                    fingerprint_id=f"image_phash_{content_id}",
                    content_id=content_id,
                    content_type=ContentType.IMAGE,
                    hash_value=hash_value,
                    perceptual_hash=perceptual_hash,
                    size_bytes=len(content_data)
                )
                fingerprints.append(perceptual_fingerprint)
            
        except Exception as e:
            self._logger.error(f"Error generating image fingerprints: {e}")
        
        return fingerprints
    
    async def _generate_video_fingerprints(
        self,
        content_id: str,
        content_data: bytes
    ) -> List[ContentFingerprint]:
        """Generate video content fingerprints."""
        fingerprints = []
        
        try:
            # Hash-based fingerprint
            hash_value = hashlib.sha256(content_data).hexdigest()
            
            fingerprint = ContentFingerprint(
                fingerprint_id=f"video_hash_{content_id}",
                content_id=content_id,
                content_type=ContentType.VIDEO,
                hash_value=hash_value,
                size_bytes=len(content_data)
            )
            fingerprints.append(fingerprint)
            
            # Temporal fingerprint (frame-based)
            temporal_hash = await self._compute_video_temporal_hash(content_data)
            
            temporal_fingerprint = ContentFingerprint(
                fingerprint_id=f"video_temporal_{content_id}",
                content_id=content_id,
                content_type=ContentType.VIDEO,
                hash_value=hash_value,
                perceptual_hash=temporal_hash,
                size_bytes=len(content_data)
            )
            fingerprints.append(temporal_fingerprint)
            
        except Exception as e:
            self._logger.error(f"Error generating video fingerprints: {e}")
        
        return fingerprints
    
    async def _generate_audio_fingerprints(
        self,
        content_id: str,
        content_data: bytes
    ) -> List[ContentFingerprint]:
        """Generate audio content fingerprints."""
        fingerprints = []
        
        try:
            # Hash-based fingerprint
            hash_value = hashlib.sha256(content_data).hexdigest()
            
            fingerprint = ContentFingerprint(
                fingerprint_id=f"audio_hash_{content_id}",
                content_id=content_id,
                content_type=ContentType.AUDIO,
                hash_value=hash_value,
                size_bytes=len(content_data)
            )
            fingerprints.append(fingerprint)
            
            # Audio fingerprint (chromaprint-style)
            audio_hash = await self._compute_audio_chromaprint(content_data)
            
            audio_fingerprint = ContentFingerprint(
                fingerprint_id=f"audio_chromaprint_{content_id}",
                content_id=content_id,
                content_type=ContentType.AUDIO,
                hash_value=hash_value,
                perceptual_hash=audio_hash,
                size_bytes=len(content_data)
            )
            fingerprints.append(audio_fingerprint)
            
        except Exception as e:
            self._logger.error(f"Error generating audio fingerprints: {e}")
        
        return fingerprints
    
    async def _store_candidate_content(
        self,
        content_id: str,
        content_data: bytes,
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> None:
        """Store candidate content for matching."""



        try:
            # Generate fingerprints for candidate content
            fingerprints = await self._generate_content_fingerprints(content_id, content_data, content_type)
            
            # Store metadata for later use
            # In a real implementation, this would be stored in a database
            
        except Exception as e:
            self._logger.error(f"Error storing candidate content {content_id}: {e}")
    
    async def _get_candidate_fingerprints(
        self,
        content_id: str,
        content_type: ContentType
    ) -> List[str]:
        """Get fingerprint IDs for candidate content."""



        try:
            # Return fingerprint IDs for this content
            fingerprint_ids = [
                fp_id for fp_id, fp in self.content_fingerprints.items()
                if fp.content_id == content_id and fp.content_type == content_type
            ]
            
            return fingerprint_ids
            
        except Exception as e:
            self._logger.error(f"Error getting candidate fingerprints for {content_id}: {e}")
            return []
    
    async def _compare_content_fingerprints(
        self,
        protected_content_id: str,
        candidate_content_id: str,
        protected_fingerprints: List[str],
        candidate_fingerprints: List[str]
    ) -> List[ContentMatch]:
        """Compare fingerprints between protected and candidate content."""
        matches = []
        
        try:
            for protected_fp_id in protected_fingerprints:
                if protected_fp_id not in self.content_fingerprints:
                    continue
                
                protected_fp = self.content_fingerprints[protected_fp_id]
                
                for candidate_fp_id in candidate_fingerprints:
                    if candidate_fp_id not in self.content_fingerprints:
                        continue
                    
                    candidate_fp = self.content_fingerprints[candidate_fp_id]
                    
                    # Only compare same fingerprint types
                    if not self._are_fingerprints_comparable(protected_fp, candidate_fp):
                        continue
                    
                    # Calculate similarity
                    similarity_score = await self._calculate_fingerprint_similarity(
                        protected_fp, candidate_fp
                    )
                    
                    if similarity_score >= self.similarity_threshold:
                        match_type = self._determine_match_type(similarity_score)
                        confidence_score = self._calculate_confidence_score(
                            similarity_score, protected_fp, candidate_fp
                        )
                        
                        match = ContentMatch(
                            match_id=f"match_{protected_content_id}_{candidate_content_id}_{datetime.now().timestamp()}",
                            original_content_id=protected_content_id,
                            matched_content_id=candidate_content_id,
                            match_type=match_type,
                            similarity_score=similarity_score,
                            confidence_score=confidence_score,
                            fingerprint_matches=[protected_fp_id, candidate_fp_id],
                            analysis_results={
                                'fingerprint_type': protected_fp.fingerprint_id.split('_')[1],
                                'content_type': protected_fp.content_type.value
                            }
                        )
                        
                        matches.append(match)
            
        except Exception as e:
            self._logger.error(f"Error comparing fingerprints: {e}")
        
        return matches
    
    def _are_fingerprints_comparable(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> bool:
        """Check if two fingerprints can be compared."""
        # Same content type
        if fp1.content_type != fp2.content_type:
            return False
        
        # Same fingerprint algorithm type
        fp1_type = fp1.fingerprint_id.split('_')[1] if '_' in fp1.fingerprint_id else ''
        fp2_type = fp2.fingerprint_id.split('_')[1] if '_' in fp2.fingerprint_id else ''
        
        return fp1_type == fp2_type
    
    async def _calculate_fingerprint_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calculate similarity between two fingerprints."""



        try:
            # Exact hash match
            if fp1.hash_value == fp2.hash_value:
                return 1.0
            
            # Perceptual hash similarity
            if fp1.perceptual_hash and fp2.perceptual_hash:
                return await self._calculate_perceptual_similarity(fp1.perceptual_hash, fp2.perceptual_hash)
            
            # Feature vector similarity
            if fp1.feature_vector and fp2.feature_vector:
                return await self._calculate_vector_similarity(fp1.feature_vector, fp2.feature_vector)
            
            # Metadata-based similarity
            if fp1.metadata and fp2.metadata:
                return await self._calculate_metadata_similarity(fp1.metadata, fp2.metadata)
            
            return 0.0
            
        except Exception as e:
            self._logger.error(f"Error calculating fingerprint similarity: {e}")
            return 0.0
    
    async def _calculate_perceptual_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between perceptual hashes."""



        try:
            # Hamming distance for perceptual hashes
            if len(hash1) != len(hash2):
                return 0.0
            
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            max_distance = len(hash1)
            
            similarity = 1.0 - (hamming_distance / max_distance)
            return max(0.0, similarity)
            
        except Exception as e:
            self._logger.error(f"Error calculating perceptual similarity: {e}")
            return 0.0
    
    async def _calculate_vector_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between feature vectors."""



        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, similarity)
            
        except Exception as e:
            self._logger.error(f"Error calculating vector similarity: {e}")
            return 0.0
    
    async def _calculate_metadata_similarity(self, meta1: Dict[str, Any], meta2: Dict[str, Any]) -> float:
        """Calculate similarity based on metadata."""



        try:
            # For text shingles
            if 'shingles' in meta1 and 'shingles' in meta2:
                shingles1 = set(meta1['shingles'])
                shingles2 = set(meta2['shingles'])
                
                intersection = len(shingles1.intersection(shingles2))
                union = len(shingles1.union(shingles2))
                
                if union == 0:
                    return 0.0
                
                return intersection / union
            
            return 0.0
            
        except Exception as e:
            self._logger.error(f"Error calculating metadata similarity: {e}")
            return 0.0
    
    def _determine_match_type(self, similarity_score: float) -> MatchType:
        """Determine match type based on similarity score."""
        if similarity_score >= 0.99:
            return MatchType.EXACT
        elif similarity_score >= 0.90:
            return MatchType.SIMILARITY
        elif similarity_score >= 0.80:
            return MatchType.DERIVATIVE
        else:
            return MatchType.PARTIAL
    
    def _calculate_confidence_score(
        self,
        similarity_score: float,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calculate confidence score for the match."""
        # Base confidence on similarity score
        confidence = similarity_score
        
        # Adjust based on fingerprint quality
        if fp1.perceptual_hash and fp2.perceptual_hash:
            confidence *= 0.95  # Perceptual hashes are slightly less certain
        
        # Adjust based on content size
        if fp1.size_bytes > 0 and fp2.size_bytes > 0:
            size_ratio = min(fp1.size_bytes, fp2.size_bytes) / max(fp1.size_bytes, fp2.size_bytes)
            confidence *= (0.8 + 0.2 * size_ratio)  # Penalize very different sizes
        
        return min(1.0, confidence)
    
    # Fingerprinting algorithm implementations (placeholders)
    async def _compute_text_hash(self, text: str) -> str:
        """Compute text hash."""



        return hashlib.sha256(text.encode()).hexdigest()
    
    async def _compute_text_shingles(self, text: str, k: int = 3) -> List[str]:
        """Compute text shingles."""
        words = text.lower().split()
        shingles = []
        
        for i in range(len(words) - k + 1):
            shingle = ' '.join(words[i:i+k])
            shingles.append(shingle)
        
        return shingles
    
    async def _compute_image_perceptual_hash(self, image_data: bytes) -> str:
        """Compute image perceptual hash."""
        # Placeholder implementation
        hash_value = hashlib.md5(image_data).hexdigest()[:16]
        return hash_value
    
    async def _compute_image_difference_hash(self, image_data: bytes) -> str:
        """Compute image difference hash."""
        # Placeholder implementation
        hash_value = hashlib.md5(image_data).hexdigest()[16:]
        return hash_value
    
    async def _compute_video_temporal_hash(self, video_data: bytes) -> str:
        """Compute video temporal hash."""
        # Placeholder implementation
        hash_value = hashlib.sha1(video_data).hexdigest()[:20]
        return hash_value
    
    async def _compute_video_frame_hash(self, video_data: bytes) -> str:
        """Compute video frame hash."""
        # Placeholder implementation
        hash_value = hashlib.sha1(video_data).hexdigest()[20:]
        return hash_value
    
    async def _compute_audio_chromaprint(self, audio_data: bytes) -> str:
        """Compute audio chromaprint."""
        # Placeholder implementation
        hash_value = hashlib.sha1(audio_data).hexdigest()[:24]
        return hash_value
    
    async def _compute_audio_mfcc(self, audio_data: bytes) -> List[float]:
        """Compute audio MFCC features."""
        # Placeholder implementation
        return [0.1 * i for i in range(13)]
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get engine status."""
        uptime_seconds = (datetime.now() - self._start_time).total_seconds()
        self.metrics.system_uptime_seconds = uptime_seconds
        
        # Update task counts
        self.metrics.tasks_pending = len([t for t in self.matching_tasks.values() if t.status == 'pending'])
        self.metrics.tasks_running = len(self.active_tasks)
        
        return {
            'engine_active': self._matching_active,
            'active_tasks': len(self.active_tasks),
            'total_protected_content': len(self.protected_content),
            'total_fingerprints': len(self.content_fingerprints),
            'total_matches': len(self.content_matches),
            'metrics': {
                'total_protected_content': self.metrics.total_protected_content,
                'total_fingerprints': self.metrics.total_fingerprints,
                'total_matches_found': self.metrics.total_matches_found,
                'total_tasks_processed': self.metrics.total_tasks_processed,
                'tasks_pending': self.metrics.tasks_pending,
                'tasks_running': self.metrics.tasks_running,
                'average_processing_time_seconds': self.metrics.average_processing_time_seconds,
                'accuracy_rate': self.metrics.accuracy_rate,
                'false_positive_rate': self.metrics.false_positive_rate,
                'content_types_processed': self.metrics.content_types_processed,
                'last_match': self.metrics.last_match.isoformat() if self.metrics.last_match else None,
                'system_uptime_seconds': self.metrics.system_uptime_seconds
            }
        }
    
    def get_recent_matches(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent content matches."""
        recent_matches = sorted(
            self.content_matches.values(),
            key=lambda m: m.detected_at,
            reverse=True
        )[:limit]
        
        return [
            {
                'match_id': m.match_id,
                'original_content_id': m.original_content_id,
                'matched_content_id': m.matched_content_id,
                'match_type': m.match_type.value,
                'similarity_score': m.similarity_score,
                'confidence_score': m.confidence_score,
                'detected_at': m.detected_at.isoformat(),
                'platform': m.platform,
                'url': m.url,
                'username': m.username,
                'verified': m.verified,
                'false_positive': m.false_positive
            }
            for m in recent_matches
        ]
    
    async def shutdown(self) -> None:
        """Shutdown the content matching engine."""



        try:
            self._logger.info("Shutting down content matching engine...")
            
            await self.stop_matching_engine()
            
            # Clear data
            self.protected_content.clear()
            self.content_fingerprints.clear()
            self.content_matches.clear()
            self.matching_tasks.clear()
            
            self._logger.info("Content matching engine shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during content matching engine shutdown: {e}")
            raise


# Export main class
__all__ = [
    'ContentMatchingEngine', 'ContentFingerprint', 'ProtectedContent', 'ContentMatch',
    'MatchingTask', 'MatchingMetrics', 'ContentType', 'MatchType'
]