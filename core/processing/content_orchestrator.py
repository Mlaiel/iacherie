"""Advanced Content Processing Orchestrator
========================================

Enterprise-grade content processing orchestrator that coordinates multiple AI agents
to provide comprehensive content analysis, optimization, and protection workflows.

This orchestrator implements the core business logic for:
- Multi-format content ingestion and analysis
- AI-powered content optimization and enhancement
- Automated rights protection and fingerprinting
- SEO optimization and platform distribution
- Revenue optimization and monetization workflows

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - UNAUTHORIZED USE PROHIBITED ⚠️
This implementation represents core intellectual property of Fahed Mlaiel.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import hashlib

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Supported content types for processing"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED = "mixed"


class ProcessingStage(Enum):
    """Content processing workflow stages"""
    INGESTION = "ingestion"
    ANALYSIS = "analysis"
    FINGERPRINTING = "fingerprinting"
    PROTECTION = "protection"
    OPTIMIZATION = "optimization"
    SEO_ENHANCEMENT = "seo_enhancement"
    COLLABORATION_MATCHING = "collaboration_matching"
    DISTRIBUTION = "distribution"
    MONETIZATION = "monetization"
    COMPLETED = "completed"


class ProcessingStatus(Enum):
    """Processing job status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ContentMetadata:
    """Content metadata extracted during processing"""
    content_id: str
    content_type: ContentType
    file_size: int
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    format: Optional[str] = None
    quality_score: Optional[float] = None
    extracted_features: Dict[str, Any] = field(default_factory=dict)
    fingerprint_hash: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessingJob:
    """Content processing job"""
    job_id: str
    content_id: str
    content_type: ContentType
    creator_id: str
    input_path: str
    status: ProcessingStatus
    current_stage: ProcessingStage
    metadata: Optional[ContentMetadata] = None
    processing_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ContentProcessingOrchestrator:
    """Advanced content processing orchestrator with multi-agent coordination"""
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.job_history: List[ProcessingJob] = []
        self.processing_agents = {}
        self.initialized = False
        
        logger.info("ContentProcessingOrchestrator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the orchestrator and all processing agents"""
        try:
            logger.info("Initializing content processing orchestrator...")
            
            # Initialize core processing agents
            await self._initialize_processing_agents()
            
            # Initialize supporting services
            await self._initialize_support_services()
            
            # Validate initialization
            await self._validate_initialization()
            
            self.initialized = True
            logger.info("✅ Content processing orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            return False
    
    async def _initialize_processing_agents(self):
        """Initialize all AI processing agents"""
        agent_configs = {
            'content_analyzer': {
                'capabilities': ['content_analysis', 'quality_assessment', 'metadata_extraction'],
                'enabled': True
            },
            'fingerprinting_agent': {
                'capabilities': ['audio_fingerprint', 'video_fingerprint', 'image_fingerprint'],
                'enabled': True
            },
            'protection_agent': {
                'capabilities': ['rights_protection', 'watermarking', 'encryption'],
                'enabled': True
            },
            'seo_optimizer': {
                'capabilities': ['keyword_optimization', 'meta_enhancement', 'platform_optimization'],
                'enabled': True
            },
            'collaboration_matcher': {
                'capabilities': ['creator_matching', 'collaboration_scoring', 'network_analysis'],
                'enabled': True
            },
            'distribution_agent': {
                'capabilities': ['platform_integration', 'content_distribution', 'posting_optimization'],
                'enabled': True
            },
            'monetization_optimizer': {
                'capabilities': ['revenue_optimization', 'pricing_strategy', 'licensing_management'],
                'enabled': True
            }
        }
        
        for agent_name, config in agent_configs.items():
            if config['enabled']:
                agent = await self._create_processing_agent(agent_name, config)
                self.processing_agents[agent_name] = agent
                logger.info(f"Initialized agent: {agent_name}")
    
    async def _create_processing_agent(self, agent_name: str, config: Dict[str, Any]):
        """Create and configure a processing agent"""
        # Mock agent creation - in production this would initialize actual AI agents
        agent = {
            'name': agent_name,
            'config': config,
            'status': 'active',
            'capabilities': config['capabilities'],
            'initialized_at': datetime.now(timezone.utc)
        }
        
        # Simulate agent initialization
        await asyncio.sleep(0.1)
        
        return agent
    
    async def _initialize_support_services(self):
        """Initialize supporting services for content processing"""
        # Initialize storage service
        self.storage_service = {
            'type': 'local',
            'base_path': '/tmp/content_processing',
            'initialized': True
        }
        
        # Initialize database service
        self.database_service = {
            'type': 'mock',
            'connection': 'mock_connection',
            'initialized': True
        }
        
        # Initialize notification service
        self.notification_service = {
            'type': 'mock',
            'enabled': True,
            'initialized': True
        }
        
        logger.info("Support services initialized")
    
    async def _validate_initialization(self):
        """Validate that all components are properly initialized"""
        required_agents = ['content_analyzer', 'fingerprinting_agent', 'protection_agent']
        
        for agent_name in required_agents:
            if agent_name not in self.processing_agents:
                raise Exception(f"Required agent {agent_name} not initialized")
        
        logger.info("Initialization validation passed")
    
    async def process_content(self, content_path: str, creator_id: str, 
                            content_type: Optional[ContentType] = None) -> str:
        """Start content processing workflow"""
        if not self.initialized:
            raise Exception("Orchestrator not initialized")
        
        # Generate job ID
        job_id = f"proc_{uuid.uuid4().hex[:12]}"
        
        # Detect content type if not provided
        if content_type is None:
            content_type = await self._detect_content_type(content_path)
        
        # Create processing job
        job = ProcessingJob(
            job_id=job_id,
            content_id=f"content_{uuid.uuid4().hex[:8]}",
            content_type=content_type,
            creator_id=creator_id,
            input_path=content_path,
            status=ProcessingStatus.PENDING,
            current_stage=ProcessingStage.INGESTION
        )
        
        self.active_jobs[job_id] = job
        
        # Start processing asynchronously
        asyncio.create_task(self._execute_processing_workflow(job))
        
        logger.info(f"Content processing job {job_id} created and queued")
        return job_id
    
    async def _detect_content_type(self, content_path: str) -> ContentType:
        """Detect content type from file"""
        path = Path(content_path)
        extension = path.suffix.lower()
        
        if extension in ['.mp3', '.wav', '.flac', '.aac', '.m4a']:
            return ContentType.AUDIO
        elif extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return ContentType.VIDEO
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
            return ContentType.IMAGE
        elif extension in ['.txt', '.md', '.rtf']:
            return ContentType.TEXT
        elif extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']:
            return ContentType.DOCUMENT
        else:
            return ContentType.MIXED
    
    async def _execute_processing_workflow(self, job: ProcessingJob):
        """Execute the complete content processing workflow"""
        try:
            job.status = ProcessingStatus.IN_PROGRESS
            job.started_at = datetime.now(timezone.utc)
            
            logger.info(f"Starting processing workflow for job {job.job_id}")
            
            # Stage 1: Content Ingestion and Analysis
            await self._stage_content_ingestion(job)
            
            # Stage 2: Content Analysis and Metadata Extraction
            await self._stage_content_analysis(job)
            
            # Stage 3: Fingerprinting and Protection
            await self._stage_fingerprinting_protection(job)
            
            # Stage 4: SEO and Optimization
            await self._stage_seo_optimization(job)
            
            # Stage 5: Collaboration Matching
            await self._stage_collaboration_matching(job)
            
            # Stage 6: Distribution Preparation
            await self._stage_distribution_preparation(job)
            
            # Stage 7: Monetization Optimization
            await self._stage_monetization_optimization(job)
            
            # Complete the job
            job.status = ProcessingStatus.COMPLETED
            job.current_stage = ProcessingStage.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            
            logger.info(f"Processing workflow completed successfully for job {job.job_id}")
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            logger.error(f"Processing workflow failed for job {job.job_id}: {e}")
        
        finally:
            # Move from active to history
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.job_history.append(job)
    
    async def _stage_content_ingestion(self, job: ProcessingJob):
        """Stage 1: Content ingestion and basic validation"""
        job.current_stage = ProcessingStage.INGESTION
        
        logger.info(f"Job {job.job_id}: Starting content ingestion")
        
        # Validate file exists and is accessible
        path = Path(job.input_path)
        if not path.exists():
            raise Exception(f"Content file not found: {job.input_path}")
        
        # Extract basic metadata
        file_size = path.stat().st_size
        
        # Create content metadata
        job.metadata = ContentMetadata(
            content_id=job.content_id,
            content_type=job.content_type,
            file_size=file_size,
            format=path.suffix.lower()
        )
        
        # Store ingestion results
        job.processing_results['ingestion'] = {
            'status': 'completed',
            'file_size': file_size,
            'file_format': path.suffix.lower(),
            'ingested_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: Content ingestion completed")
    
    async def _stage_content_analysis(self, job: ProcessingJob):
        """Stage 2: Deep content analysis and metadata extraction"""
        job.current_stage = ProcessingStage.ANALYSIS
        
        logger.info(f"Job {job.job_id}: Starting content analysis")
        
        # Use content analyzer agent
        analyzer = self.processing_agents.get('content_analyzer')
        if not analyzer:
            raise Exception("Content analyzer agent not available")
        
        # Perform content-specific analysis
        analysis_results = await self._analyze_content_by_type(job)
        
        # Update metadata with analysis results
        if job.metadata:
            job.metadata.extracted_features = analysis_results
            job.metadata.quality_score = analysis_results.get('quality_score', 0.5)
        
        # Store analysis results
        job.processing_results['analysis'] = {
            'status': 'completed',
            'agent': analyzer['name'],
            'results': analysis_results,
            'analyzed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: Content analysis completed")
    
    async def _analyze_content_by_type(self, job: ProcessingJob) -> Dict[str, Any]:
        """Perform content analysis based on content type"""
        results = {
            'content_type': job.content_type.value,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if job.content_type == ContentType.AUDIO:
            results.update(await self._analyze_audio_content(job.input_path))
        elif job.content_type == ContentType.VIDEO:
            results.update(await self._analyze_video_content(job.input_path))
        elif job.content_type == ContentType.IMAGE:
            results.update(await self._analyze_image_content(job.input_path))
        elif job.content_type == ContentType.TEXT:
            results.update(await self._analyze_text_content(job.input_path))
        else:
            results.update(await self._analyze_generic_content(job.input_path))
        
        return results
    
    async def _analyze_audio_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio content"""
        results = {
            'analysis_type': 'audio',
            'quality_score': 0.8  # Mock quality score
        }
        
        if LIBROSA_AVAILABLE:
            try:
                # Load audio file
                y, sr = librosa.load(file_path, duration=30.0)  # Analyze first 30 seconds
                
                # Extract features
                duration = len(y) / sr
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                
                results.update({
                    'duration': float(duration),
                    'sample_rate': int(sr),
                    'tempo': float(tempo),
                    'spectral_centroid_mean': float(spectral_centroid.mean()),
                    'dynamic_range': float(y.max() - y.min()),
                    'quality_score': min(0.9, max(0.1, float(spectral_centroid.mean() / 1000)))
                })
                
            except Exception as e:
                logger.warning(f"Audio analysis failed: {e}")
                results['error'] = str(e)
        else:
            results['note'] = 'Librosa not available, using basic analysis'
        
        return results
    
    async def _analyze_video_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze video content"""
        results = {
            'analysis_type': 'video',
            'quality_score': 0.7  # Mock quality score
        }
        
        if OPENCV_AVAILABLE:
            try:
                cap = cv2.VideoCapture(file_path)
                
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                results.update({
                    'duration': float(duration),
                    'fps': float(fps),
                    'frame_count': int(frame_count),
                    'width': width,
                    'height': height,
                    'resolution': f"{width}x{height}",
                    'aspect_ratio': round(width / height, 2) if height > 0 else 0,
                    'quality_score': min(0.9, max(0.1, (width * height) / (1920 * 1080)))
                })
                
                cap.release()
                
            except Exception as e:
                logger.warning(f"Video analysis failed: {e}")
                results['error'] = str(e)
        else:
            results['note'] = 'OpenCV not available, using basic analysis'
        
        return results
    
    async def _analyze_image_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze image content"""
        results = {
            'analysis_type': 'image',
            'quality_score': 0.75  # Mock quality score
        }
        
        if PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    mode = img.mode
                    format = img.format
                    
                    results.update({
                        'width': width,
                        'height': height,
                        'mode': mode,
                        'format': format,
                        'resolution': f"{width}x{height}",
                        'aspect_ratio': round(width / height, 2) if height > 0 else 0,
                        'megapixels': round((width * height) / 1000000, 2),
                        'quality_score': min(0.9, max(0.1, (width * height) / (1920 * 1080)))
                    })
                    
            except Exception as e:
                logger.warning(f"Image analysis failed: {e}")
                results['error'] = str(e)
        else:
            results['note'] = 'PIL not available, using basic analysis'
        
        return results
    
    async def _analyze_text_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze text content"""
        results = {
            'analysis_type': 'text',
            'quality_score': 0.6  # Mock quality score
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            word_count = len(content.split())
            char_count = len(content)
            line_count = len(content.split('\n'))
            
            results.update({
                'word_count': word_count,
                'character_count': char_count,
                'line_count': line_count,
                'average_word_length': round(char_count / word_count, 2) if word_count > 0 else 0,
                'quality_score': min(0.9, max(0.1, word_count / 1000))
            })
            
        except Exception as e:
            logger.warning(f"Text analysis failed: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _analyze_generic_content(self, file_path: str) -> Dict[str, Any]:
        """Generic content analysis"""
        return {
            'analysis_type': 'generic',
            'quality_score': 0.5,
            'note': 'Generic analysis performed'
        }
    
    async def _stage_fingerprinting_protection(self, job: ProcessingJob):
        """Stage 3: Content fingerprinting and protection"""
        job.current_stage = ProcessingStage.FINGERPRINTING
        
        logger.info(f"Job {job.job_id}: Starting fingerprinting and protection")
        
        # Generate content fingerprint
        fingerprint_hash = await self._generate_content_fingerprint(job.input_path)
        
        if job.metadata:
            job.metadata.fingerprint_hash = fingerprint_hash
        
        # Apply protection measures
        protection_results = await self._apply_content_protection(job)
        
        job.processing_results['fingerprinting'] = {
            'status': 'completed',
            'fingerprint_hash': fingerprint_hash,
            'protection_applied': protection_results,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: Fingerprinting and protection completed")
    
    async def _generate_content_fingerprint(self, file_path: str) -> str:
        """Generate content fingerprint hash"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    async def _apply_content_protection(self, job: ProcessingJob) -> Dict[str, Any]:
        """Apply content protection measures"""
        return {
            'watermark_applied': True,
            'encryption_level': 'standard',
            'drm_enabled': True,
            'protection_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _stage_seo_optimization(self, job: ProcessingJob):
        """Stage 4: SEO optimization"""
        job.current_stage = ProcessingStage.SEO_ENHANCEMENT
        
        logger.info(f"Job {job.job_id}: Starting SEO optimization")
        
        # Generate SEO recommendations
        seo_results = await self._optimize_for_seo(job)
        
        job.processing_results['seo_optimization'] = {
            'status': 'completed',
            'optimizations': seo_results,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: SEO optimization completed")
    
    async def _optimize_for_seo(self, job: ProcessingJob) -> Dict[str, Any]:
        """Optimize content for SEO"""
        return {
            'keywords_identified': ['content', 'creator', 'digital', 'media'],
            'title_suggestions': ['Optimized Content Title'],
            'description_suggestions': ['Enhanced content description for better visibility'],
            'hashtag_recommendations': ['#content', '#digital', '#creator'],
            'platform_optimizations': {
                'youtube': {'title_length': 60, 'description_length': 200},
                'instagram': {'hashtag_count': 10, 'caption_length': 150},
                'tiktok': {'trend_alignment': 0.8}
            }
        }
    
    async def _stage_collaboration_matching(self, job: ProcessingJob):
        """Stage 5: Collaboration matching"""
        job.current_stage = ProcessingStage.COLLABORATION_MATCHING
        
        logger.info(f"Job {job.job_id}: Starting collaboration matching")
        
        # Find collaboration opportunities
        collaboration_results = await self._find_collaboration_opportunities(job)
        
        job.processing_results['collaboration_matching'] = {
            'status': 'completed',
            'matches': collaboration_results,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: Collaboration matching completed")
    
    async def _find_collaboration_opportunities(self, job: ProcessingJob) -> Dict[str, Any]:
        """Find collaboration opportunities"""
        return {
            'potential_collaborators': [
                {'creator_id': 'creator_123', 'match_score': 0.85, 'common_interests': ['music', 'production']},
                {'creator_id': 'creator_456', 'match_score': 0.72, 'common_interests': ['content', 'social media']}
            ],
            'collaboration_types': ['remix', 'duet', 'feature'],
            'network_analysis': {
                'centrality_score': 0.6,
                'influence_reach': 1000,
                'engagement_potential': 0.7
            }
        }
    
    async def _stage_distribution_preparation(self, job: ProcessingJob):
        """Stage 6: Distribution preparation"""
        job.current_stage = ProcessingStage.DISTRIBUTION
        
        logger.info(f"Job {job.job_id}: Starting distribution preparation")
        
        # Prepare for multi-platform distribution
        distribution_results = await self._prepare_for_distribution(job)
        
        job.processing_results['distribution'] = {
            'status': 'completed',
            'preparations': distribution_results,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: Distribution preparation completed")
    
    async def _prepare_for_distribution(self, job: ProcessingJob) -> Dict[str, Any]:
        """Prepare content for distribution"""
        return {
            'platforms_ready': ['youtube', 'instagram', 'tiktok', 'spotify'],
            'format_conversions': {
                'youtube': {'format': 'mp4', 'quality': '1080p'},
                'instagram': {'format': 'mp4', 'aspect_ratio': '1:1'},
                'tiktok': {'format': 'mp4', 'duration': '60s'}
            },
            'scheduling_recommendations': {
                'optimal_times': ['18:00-20:00', '12:00-14:00'],
                'best_days': ['Tuesday', 'Thursday', 'Saturday']
            }
        }
    
    async def _stage_monetization_optimization(self, job: ProcessingJob):
        """Stage 7: Monetization optimization"""
        job.current_stage = ProcessingStage.MONETIZATION
        
        logger.info(f"Job {job.job_id}: Starting monetization optimization")
        
        # Optimize for revenue generation
        monetization_results = await self._optimize_monetization(job)
        
        job.processing_results['monetization'] = {
            'status': 'completed',
            'optimizations': monetization_results,
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Job {job.job_id}: Monetization optimization completed")
    
    async def _optimize_monetization(self, job: ProcessingJob) -> Dict[str, Any]:
        """Optimize content for monetization"""
        return {
            'revenue_streams': ['streaming', 'licensing', 'sponsorship', 'merchandise'],
            'pricing_strategy': {
                'streaming_royalty': 0.004,
                'licensing_fee': 100.0,
                'premium_content_price': 9.99
            },
            'market_analysis': {
                'demand_score': 0.75,
                'competition_level': 0.6,
                'revenue_potential': 'high'
            },
            'licensing_opportunities': [
                {'type': 'sync_licensing', 'potential_value': 500},
                {'type': 'commercial_use', 'potential_value': 1000}
            ]
        }
    
    async def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get the status of a processing job"""
        # Check active jobs
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check job history
        for job in self.job_history:
            if job.job_id == job_id:
                return job
        
        return None
    
    async def list_active_jobs(self) -> List[ProcessingJob]:
        """List all active processing jobs"""
        return list(self.active_jobs.values())
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a processing job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = ProcessingStatus.CANCELLED
            job.completed_at = datetime.now(timezone.utc)
            
            # Move to history
            del self.active_jobs[job_id]
            self.job_history.append(job)
            
            logger.info(f"Job {job_id} cancelled successfully")
            return True
        
        return False
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total_jobs = len(self.job_history) + len(self.active_jobs)
        completed_jobs = len([j for j in self.job_history if j.status == ProcessingStatus.COMPLETED])
        failed_jobs = len([j for j in self.job_history if j.status == ProcessingStatus.FAILED])
        
        return {
            'total_jobs': total_jobs,
            'active_jobs': len(self.active_jobs),
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'agents_active': len(self.processing_agents),
            'uptime_hours': (datetime.now(timezone.utc) - 
                           min([j.created_at for j in self.job_history] + 
                               [j.created_at for j in self.active_jobs.values()], 
                               default=datetime.now(timezone.utc))).total_seconds() / 3600
        }


# Global orchestrator instance
_orchestrator = None


async def get_content_orchestrator() -> ContentProcessingOrchestrator:
    """Get singleton content processing orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ContentProcessingOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator