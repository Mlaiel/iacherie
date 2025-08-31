"""
Vision Orchestrator - Enterprise Computer Vision Coordination System
================================================================

Advanced orchestration system managing all computer vision operations including
image processing, video analysis, object detection, and visual similarity matching
for content protection and AI-powered creative enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import base64

from ..base import BaseAgent, AgentStatus, AgentCapability
try:
    from core.exceptions import VisionProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    VisionProcessingError, ValidationError = globals().get('VisionProcessingError, ValidationError', Exception)
from ...utils.cache_manager import CacheManager
from ...security.content_validator import ContentValidator
from .image_processor import ImageProcessor
from .video_analyzer import VideoAnalyzer
from .object_detector import ObjectDetector
from .visual_similarity import VisualSimilarity
from .face_recognition import FaceRecognition
from .optical_character_reader import OpticalCharacterReader
from .scene_analyzer import SceneAnalyzer
from .metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)

@dataclass
class VisionProcessingRequest:
    """Comprehensive vision processing request structure"""
    content_id: str
    content_type: str  # image, video, frame
    file_path: Optional[str] = None
    file_data: Optional[bytes] = None
    processing_tasks: List[str] = None  # ['detection', 'similarity', 'ocr', 'faces']
    quality_requirements: Dict[str, Any] = None
    protection_level: str = 'standard'  # basic, standard, premium, enterprise
    metadata_extraction: bool = True
    fingerprint_generation: bool = True
    priority: str = 'normal'  # low, normal, high, critical

@dataclass
class VisionProcessingResult:
    """Comprehensive vision processing result structure"""
    content_id: str
    processing_status: str
    processing_time: float
    confidence_score: float
    detected_objects: List[Dict] = None
    recognized_faces: List[Dict] = None
    extracted_text: str = None
    scene_analysis: Dict = None
    visual_fingerprint: str = None
    similarity_matches: List[Dict] = None
    quality_metrics: Dict = None
    metadata: Dict = None
    errors: List[str] = None
    warnings: List[str] = None

class VisionOrchestrator(BaseAgent):
    """
    Enterprise-grade vision orchestration system providing comprehensive
    computer vision capabilities for content creators and influencers.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="vision_orchestrator",
            name="Vision Orchestrator",
            version="2.1.0",
            capabilities=[
                AgentCapability.IMAGE_PROCESSING,
                AgentCapability.VIDEO_ANALYSIS,
                AgentCapability.OBJECT_DETECTION,
                AgentCapability.FACE_RECOGNITION,
                AgentCapability.OPTICAL_CHARACTER_RECOGNITION,
                AgentCapability.VISUAL_SIMILARITY,
                AgentCapability.CONTENT_FINGERPRINTING,
                AgentCapability.METADATA_EXTRACTION,
                AgentCapability.QUALITY_ASSESSMENT
            ]
        )
        
        # Initialize specialized processors
        self.image_processor = ImageProcessor()
        self.video_analyzer = VideoAnalyzer()
        self.object_detector = ObjectDetector()
        self.visual_similarity = VisualSimilarity()
        self.face_recognition = FaceRecognition()
        self.ocr_reader = OpticalCharacterReader()
        self.scene_analyzer = SceneAnalyzer()
        self.metadata_extractor = MetadataExtractor()
        
        # Content validation and security
        self.content_validator = ContentValidator()
        self.cache_manager = CacheManager("vision_cache")
        
        # Processing configuration
        self.max_image_size = (4096, 4096)
        self.supported_formats = {
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'minimum_resolution': (640, 480),
            'maximum_file_size': 100 * 1024 * 1024,  # 100MB
            'minimum_confidence': 0.7,
            'blur_threshold': 100.0
        }

    async def initialize(self) -> bool:
        """Initialize all vision processing components"""



        try:
            logger.info("Initializing Vision Orchestrator...")
            
            # Initialize all processors
            await asyncio.gather(
                self.image_processor.initialize(),
                self.video_analyzer.initialize(),
                self.object_detector.initialize(),
                self.visual_similarity.initialize(),
                self.face_recognition.initialize(),
                self.ocr_reader.initialize(),
                self.scene_analyzer.initialize(),
                self.metadata_extractor.initialize()
            )
            
            self.status = AgentStatus.READY
            logger.info("Vision Orchestrator initialized successfully")
            # Initialize all vision components
            logger.info("Initializing vision processing components...")
            
            # Initialize device and GPU settings
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
            # Initialize core vision processors
            await self._initialize_processors()
            
            # Initialize ML models and transformations
            await self._initialize_models()
            
            # Initialize caching and performance monitoring
            self._initialize_infrastructure()
            
            # Warm up all models with sample data
            await self._warm_up_system()
            
            self.status = AgentStatus.READY
            logger.info("Vision Orchestrator successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Vision Orchestrator initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def _initialize_processors(self):
        """Initialize all vision processing components"""
        self.image_processor = ImageProcessor()
        self.video_analyzer = VideoAnalyzer()
        self.object_detector = ObjectDetector()
        self.visual_similarity = VisualSimilarity()
        self.face_recognition = FaceRecognition()
        self.ocr_reader = OpticalCharacterReader()
        self.scene_analyzer = SceneAnalyzer()
        self.metadata_extractor = MetadataExtractor()
        
        # Initialize all components
        await asyncio.gather(
            self.image_processor.initialize(),
            self.video_analyzer.initialize(),
            self.object_detector.initialize(),
            self.visual_similarity.initialize(),
            self.face_recognition.initialize(),
            self.ocr_reader.initialize(),
            self.scene_analyzer.initialize(),
            self.metadata_extractor.initialize()
        )

    async def _initialize_models(self):
        """Initialize ML models and transformations"""
        # Standard preprocessing transforms
        self.preprocess_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((224, 224)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Initialize model registry
        self.model_registry = {}
        
        # Load pre-trained models
        if self.device.type == 'cuda':
            logger.info(f"GPU acceleration enabled: {torch.cuda.get_device_name(0)}")
        
        logger.info("Vision models initialized")

    def _initialize_infrastructure(self):
        """Initialize caching and monitoring infrastructure"""
        self.cache_manager = CacheManager("vision_cache")
        self.performance_monitor = PerformanceMonitor("vision_orchestrator")
        
        # Processing queues for different priorities
        self.priority_queues = {
            'critical': asyncio.Queue(maxsize=10),
            'high': asyncio.Queue(maxsize=50),
            'normal': asyncio.Queue(maxsize=100),
            'low': asyncio.Queue(maxsize=200)
        }
        
        logger.info("Vision infrastructure initialized")

    async def _warm_up_system(self):
        """Warm up all models and systems"""



        try:
            # Create dummy image and video data
            dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Warm up image processing
            await self.image_processor.process_image(dummy_image)
            
            logger.info("System warm-up completed")
            
        except Exception as e:
            logger.warning(f"System warm-up failed: {e}")

    async def process_content(
        self, 
        request: VisionProcessingRequest
    ) -> VisionProcessingResult:
        """
        Process visual content through comprehensive vision pipeline
        
        Args:
            request: Vision processing request with all parameters
            
        Returns:
            Comprehensive processing results
        """
        start_time = datetime.now()
        content_id = request.content_id
        
        try:
            logger.info(f"Processing vision content {content_id}")
            
            # Validate request and content
            await self._validate_processing_request(request)
            
            # Check cache for existing results
            cached_result = await self._check_cache(request)
            if cached_result:
                logger.info(f"Returning cached result for {content_id}")
                return cached_result
            
            # Load and preprocess content
            content_data = await self._load_content(request)
            
            # Execute processing pipeline
            result = await self._execute_vision_pipeline(request, content_data)
            
            # Post-processing and optimization
            await self._optimize_results(result)
            
            # Cache results for future use
            await self._cache_processing_results(content_id, result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            # Record performance metrics
            await self.performance_monitor.record_metric(
                "vision_processing_time", processing_time
            )
            
            logger.info(
                f"Vision processing completed for {content_id} "
                f"in {processing_time:.2f}s with confidence {result.confidence_score:.3f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Vision processing failed for {content_id}: {e}")
            return VisionProcessingResult(
                content_id=content_id,
                processing_status="error",
                processing_time=(datetime.now() - start_time).total_seconds(),
                confidence_score=0.0,
                errors=[str(e)]
            )

    async def _validate_processing_request(
        self, 
        request: VisionProcessingRequest
    ) -> None:
        """Validate processing request parameters"""
        if not request.content_id:
            raise ValidationError("Content ID is required")
        
        if not request.content_type:
            raise ValidationError("Content type is required")
        
        if request.content_type not in ['image', 'video', 'frame']:
            raise ValidationError(f"Unsupported content type: {request.content_type}")
        
        if not request.file_path and not request.file_data:
            raise ValidationError("Either file_path or file_data must be provided")
        
        # Validate content security
        if request.file_data:
            await self.content_validator.validate_content_security(request.file_data)

    async def _load_content(
        self, 
        request: VisionProcessingRequest
    ) -> Union[np.ndarray, Any]:
        """Load and preprocess content for vision processing"""



        try:
            if request.file_data:
                # Load from binary data
                if request.content_type == 'image':
                    image = Image.open(io.BytesIO(request.file_data))
                    return np.array(image)
                elif request.content_type in ['video', 'frame']:
                    # Handle video/frame data
                    return cv2.imdecode(
                        np.frombuffer(request.file_data, np.uint8), 
                        cv2.IMREAD_COLOR
                    )
            
            elif request.file_path:
                # Load from file path
                if request.content_type == 'image':
                    return cv2.imread(request.file_path, cv2.IMREAD_COLOR)
                elif request.content_type in ['video', 'frame']:
                    return cv2.VideoCapture(request.file_path)
            
            raise VisionProcessingError("Failed to load content data")
            
        except Exception as e:
            raise VisionProcessingError(f"Content loading failed: {e}")

    async def _execute_vision_pipeline(
        self, 
        request: VisionProcessingRequest, 
        content_data: Any
    ) -> VisionProcessingResult:
        """Execute comprehensive vision processing pipeline"""
        result = VisionProcessingResult(
            content_id=request.content_id,
            processing_status="processing",
            confidence_score=0.0
        )
        
        processing_tasks = request.processing_tasks or [
            'detection', 'similarity', 'ocr', 'faces', 'scene', 'quality'
        ]
        
        try:
            # Parallel processing for efficiency
            tasks = []
            
            if 'detection' in processing_tasks:
                tasks.append(self._process_object_detection(content_data))
            
            if 'similarity' in processing_tasks and request.fingerprint_generation:
                tasks.append(self._generate_visual_fingerprint(content_data))
            
            if 'ocr' in processing_tasks:
                tasks.append(self._extract_text_content(content_data))
            
            if 'faces' in processing_tasks:
                tasks.append(self._recognize_faces(content_data))
            
            if 'scene' in processing_tasks:
                tasks.append(self._analyze_scene_content(content_data))
            
            if 'quality' in processing_tasks:
                tasks.append(self._assess_content_quality(content_data))
            
            if 'metadata' in processing_tasks:
                tasks.append(self._extract_comprehensive_metadata(content_data))
            
            # Execute all processing tasks concurrently
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results and handle exceptions
            await self._aggregate_processing_results(result, task_results, processing_tasks)
            
            # Calculate overall confidence score
            result.confidence_score = self._calculate_overall_confidence(result)
            
            # Validate and finalize results
            await self._finalize_processing_results(result, request)
            
            return result
            
        except Exception as e:
            logger.error(f"Vision pipeline execution failed: {e}")
            result.processing_status = "error"
            result.errors.append(str(e))
            return result

    async def _process_object_detection(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Process object detection on content"""



        try:
            detection_results = await self.object_detector.detect_objects(content_data)
            return {
                'task': 'detection',
                'success': True,
                'results': detection_results
            }
        except Exception as e:
            return {
                'task': 'detection',
                'success': False,
                'error': str(e)
            }

    async def _generate_visual_fingerprint(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Generate visual fingerprint for similarity matching"""



        try:
            fingerprint_data = await self.visual_similarity.generate_fingerprint(content_data)
            return {
                'task': 'similarity',
                'success': True,
                'results': fingerprint_data
            }
        except Exception as e:
            return {
                'task': 'similarity',
                'success': False,
                'error': str(e)
            }

    async def _extract_text_content(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Extract text content using OCR"""



        try:
            ocr_results = await self.ocr_reader.extract_text(content_data)
            return {
                'task': 'ocr',
                'success': True,
                'results': ocr_results
            }
        except Exception as e:
            return {
                'task': 'ocr',
                'success': False,
                'error': str(e)
            }

    async def _recognize_faces(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Recognize faces in content"""



        try:
            face_results = await self.face_recognition.recognize_faces(content_data)
            return {
                'task': 'faces',
                'success': True,
                'results': face_results
            }
        except Exception as e:
            return {
                'task': 'faces',
                'success': False,
                'error': str(e)
            }

    async def _analyze_scene_content(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Analyze scene and context"""



        try:
            scene_results = await self.scene_analyzer.analyze_scene(content_data)
            return {
                'task': 'scene',
                'success': True,
                'results': scene_results
            }
        except Exception as e:
            return {
                'task': 'scene',
                'success': False,
                'error': str(e)
            }

    async def _assess_content_quality(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Assess content quality metrics"""



        try:
            quality_results = await self.image_processor.assess_quality(content_data)
            return {
                'task': 'quality',
                'success': True,
                'results': quality_results
            }
        except Exception as e:
            return {
                'task': 'quality',
                'success': False,
                'error': str(e)
            }

    async def _extract_comprehensive_metadata(self, content_data: np.ndarray) -> Dict[str, Any]:
        """Extract comprehensive metadata"""



        try:
            metadata_results = await self.metadata_extractor.extract_metadata(content_data)
            return {
                'task': 'metadata',
                'success': True,
                'results': metadata_results
            }
        except Exception as e:
            return {
                'task': 'metadata',
                'success': False,
                'error': str(e)
            }

    async def _aggregate_processing_results(
        self,
        result: VisionProcessingResult,
        task_results: List[Any],
        processing_tasks: List[str]
    ) -> None:
        """Aggregate all processing task results"""
        result.detection_results = {}
        result.similarity_data = {}
        result.ocr_results = {}
        result.face_results = {}
        result.scene_analysis = {}
        result.quality_metrics = {}
        result.metadata = {}
        
        for i, task_result in enumerate(task_results):
            if isinstance(task_result, Exception):
                result.errors.append(f"Task {processing_tasks[i]} failed: {task_result}")
                continue
                
            if not isinstance(task_result, dict) or not task_result.get('success', False):
                error_msg = task_result.get('error', 'Unknown error') if isinstance(task_result, dict) else str(task_result)
                result.errors.append(f"Task {task_result.get('task', 'unknown')} failed: {error_msg}")
                continue
            
            task_name = task_result.get('task')
            task_data = task_result.get('results', {})
            
            # Map results to appropriate result fields
            if task_name == 'detection':
                result.detection_results = task_data
            elif task_name == 'similarity':
                result.similarity_data = task_data
            elif task_name == 'ocr':
                result.ocr_results = task_data
            elif task_name == 'faces':
                result.face_results = task_data
            elif task_name == 'scene':
                result.scene_analysis = task_data
            elif task_name == 'quality':
                result.quality_metrics = task_data
            elif task_name == 'metadata':
                result.metadata = task_data

    def _calculate_overall_confidence(self, result: VisionProcessingResult) -> float:
        """Calculate overall confidence score from all processing results"""
        confidence_scores = []
        
        # Extract confidence from each component
        if result.detection_results and 'confidence' in result.detection_results:
            confidence_scores.append(result.detection_results['confidence'])
        
        if result.similarity_data and 'confidence' in result.similarity_data:
            confidence_scores.append(result.similarity_data['confidence'])
        
        if result.ocr_results and 'confidence' in result.ocr_results:
            confidence_scores.append(result.ocr_results['confidence'])
        
        if result.face_results and 'confidence' in result.face_results:
            confidence_scores.append(result.face_results['confidence'])
        
        if result.scene_analysis and 'confidence' in result.scene_analysis:
            confidence_scores.append(result.scene_analysis['confidence'])
        
        if result.quality_metrics and 'overall_score' in result.quality_metrics:
            confidence_scores.append(result.quality_metrics['overall_score'])
        
        # Calculate weighted average
        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)
        
        return 0.0

    async def _finalize_processing_results(
        self,
        result: VisionProcessingResult,
        request: VisionProcessingRequest
    ) -> None:
        """Finalize and validate processing results"""
        # Set final processing status
        if result.errors:
            result.processing_status = "completed_with_errors"
        else:
            result.processing_status = "completed"
        
        # Add processing metadata
        result.processing_metadata = {
            'processing_tasks': request.processing_tasks,
            'fingerprint_generation': request.fingerprint_generation,
            'similarity_threshold': request.similarity_threshold,
            'processing_priority': request.processing_priority,
            'model_version': self.config.model_version,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Validate results based on minimum confidence threshold
        if result.confidence_score < self.config.min_confidence_threshold:
            result.errors.append(
                f"Processing confidence {result.confidence_score:.3f} below threshold "
                f"{self.config.min_confidence_threshold}"
            )

    async def _check_cache(self, request: VisionProcessingRequest) -> Optional[VisionProcessingResult]:
        """Check cache for existing processing results"""



        try:
            cache_key = self._generate_cache_key(request)
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result:
                # Validate cache freshness
                cache_age = (datetime.now() - cached_result.get('timestamp', datetime.min)).total_seconds()
                if cache_age < self.config.cache_ttl:
                    return VisionProcessingResult(**cached_result['result'])
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None

    def _generate_cache_key(self, request: VisionProcessingRequest) -> str:
        """Generate cache key from request parameters"""
        key_components = [
            request.content_id,
            str(sorted(request.processing_tasks or [])),
            str(request.fingerprint_generation),
            str(request.similarity_threshold),
            self.config.model_version
        ]
        
        return hashlib.md5('|'.join(key_components).encode()).hexdigest()

    async def _cache_processing_results(
        self,
        content_id: str,
        result: VisionProcessingResult
    ) -> None:
        """Cache processing results for future use"""



        try:
            cache_key = f"vision_result_{content_id}"
            cache_data = {
                'result': result.__dict__,
                'timestamp': datetime.now(),
                'content_id': content_id
            }
            
            await self.cache_manager.set(cache_key, cache_data, ttl=self.config.cache_ttl)
            
        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")

    async def _optimize_results(self, result: VisionProcessingResult) -> None:
        """Optimize and compress processing results"""



        try:
            # Compress large detection results
            if result.detection_results and len(str(result.detection_results)) > 10000:
                result.detection_results = await self._compress_detection_data(
                    result.detection_results
                )
            
            # Optimize similarity data
            if result.similarity_data and 'fingerprint' in result.similarity_data:
                result.similarity_data['fingerprint'] = await self._optimize_fingerprint(
                    result.similarity_data['fingerprint']
                )
            
        except Exception as e:
            logger.warning(f"Result optimization failed: {e}")

    async def _compress_detection_data(self, detection_data: Dict) -> Dict:
        """Compress detection data while preserving important information"""
        compressed = {
            'object_count': len(detection_data.get('objects', [])),
            'top_objects': detection_data.get('objects', [])[:10],  # Keep top 10
            'confidence': detection_data.get('confidence', 0.0),
            'processing_time': detection_data.get('processing_time', 0.0)
        }
        return compressed

    async def _optimize_fingerprint(self, fingerprint_data: Any) -> Any:
        """Optimize fingerprint data for storage and transmission"""
        if isinstance(fingerprint_data, np.ndarray):
            # Convert to more compact representation
            return {
                'shape': fingerprint_data.shape,
                'data': fingerprint_data.flatten().tolist()[:1000],  # Limit size
                'dtype': str(fingerprint_data.dtype)
            }
        return fingerprint_data

    async def search_similar_content(
        self, 
        query_fingerprint: str,
        similarity_threshold: float = 0.8,
        limit: int = 10
    ) -> List[Dict]:
        """Search for visually similar content"""



        try:
            return await self.visual_similarity.search_similar(
                query_fingerprint, 
                similarity_threshold, 
                limit
            )
        except Exception as e:
            logger.error(f"Similar content search failed: {e}")
            return []

    async def batch_process_content(
        self,
        requests: List[VisionProcessingRequest],
        max_concurrent: int = 5
    ) -> List[VisionProcessingResult]:
        """Process multiple content items in batches"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(request):
            async with semaphore:
                return await self.process_content(request)
        
        tasks = [process_with_semaphore(request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def process_video_content(
        self,
        request: VisionProcessingRequest
    ) -> VisionProcessingResult:
        """Specialized video content processing"""
        if request.content_type != 'video':
            raise ValueError("Request must be for video content")
        
        return await self.video_analyzer.analyze_video(
            request.file_path or request.file_data,
            processing_options={
                'extract_frames': True,
                'analyze_audio': True,
                'scene_detection': True,
                'motion_analysis': True
            }
        )

    async def get_processing_status(self, content_id: str) -> Optional[Dict]:
        """Get processing status for content"""



        try:
            cache_key = f"vision_status:{content_id}"
            status_data = await self.cache_manager.get(cache_key)
            
            if status_data:
                return {
                    'content_id': content_id,
                    'status': status_data.get('status', 'unknown'),
                    'progress': status_data.get('progress', 0),
                    'started_at': status_data.get('started_at'),
                    'estimated_completion': status_data.get('estimated_completion')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get processing status for {content_id}: {e}")
            return None

    async def update_processing_status(
        self,
        content_id: str,
        status: str,
        progress: float = 0.0
    ) -> None:
        """Update processing status"""



        try:
            cache_key = f"vision_status:{content_id}"
            status_data = {
                'status': status,
                'progress': progress,
                'updated_at': datetime.now().isoformat()
            }
            
            await self.cache_manager.set(cache_key, status_data, ttl=3600)
            
        except Exception as e:
            logger.warning(f"Failed to update status for {content_id}: {e}")

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats"""



        return {
            'image': ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp', 'gif'],
            'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg']
        }

    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive processing capabilities"""



        return {
            'max_image_size': self.config.max_image_size,
            'max_video_duration': self.config.max_video_duration,
            'supported_formats': self.get_supported_formats(),
            'quality_thresholds': {
                'minimum_confidence': self.config.min_confidence_threshold,
                'similarity_threshold': 0.8,
                'quality_threshold': 0.7
            },
            'available_tasks': [
                'object_detection',
                'face_recognition', 
                'optical_character_recognition',
                'visual_similarity',
                'scene_analysis',
                'quality_assessment',
                'metadata_extraction',
                'content_fingerprinting'
            ],
            'performance_metrics': {
                'avg_processing_time': self.performance_monitor.get_average('vision_processing_time'),
                'success_rate': self.performance_monitor.get_success_rate(),
                'cache_hit_rate': self.cache_manager.get_hit_rate()
            },
            'system_info': {
                'device': str(self.device),
                'gpu_available': torch.cuda.is_available(),
                'model_version': self.config.model_version,
                'status': self.status.value
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'overall_status': 'healthy',
            'components': {},
            'performance': {},
            'resources': {}
        }
        
        try:
            # Check component health
            components = [
                ('image_processor', self.image_processor),
                ('video_analyzer', self.video_analyzer),
                ('object_detector', self.object_detector),
                ('visual_similarity', self.visual_similarity),
                ('face_recognition', self.face_recognition),
                ('ocr_reader', self.ocr_reader),
                ('scene_analyzer', self.scene_analyzer),
                ('metadata_extractor', self.metadata_extractor)
            ]
            
            for name, component in components:
                try:
                    if hasattr(component, 'health_check'):
                        health_status['components'][name] = await component.health_check()
                    else:
                        health_status['components'][name] = 'available'
                except Exception as e:
                    health_status['components'][name] = f'error: {e}'
                    health_status['overall_status'] = 'degraded'
            
            # Check performance metrics
            health_status['performance'] = {
                'avg_processing_time': self.performance_monitor.get_average('vision_processing_time'),
                'cache_hit_rate': self.cache_manager.get_hit_rate(),
                'error_rate': self.performance_monitor.get_error_rate()
            }
            
            # Check system resources
            health_status['resources'] = {
                'gpu_available': torch.cuda.is_available(),
                'gpu_memory': torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else None,
                'cache_size': await self.cache_manager.get_size(),
                'queue_sizes': {k: v.qsize() for k, v in self.priority_queues.items()}
            }
            
        except Exception as e:
            health_status['overall_status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""



        return {
            'processing_times': self.performance_monitor.get_all_metrics(),
            'cache_statistics': await self.cache_manager.get_statistics(),
            'component_performance': {
                'image_processor': await self.image_processor.get_performance_metrics(),
                'video_analyzer': await self.video_analyzer.get_performance_metrics(),
                'object_detector': await self.object_detector.get_performance_metrics()
            }
        }

    async def cleanup(self) -> None:
        """Cleanup resources and connections"""



        try:
            logger.info("Starting Vision Orchestrator cleanup...")
            
            # Cleanup all components
            cleanup_tasks = []
            components = [
                self.image_processor,
                self.video_analyzer, 
                self.object_detector,
                self.visual_similarity,
                self.face_recognition,
                self.ocr_reader,
                self.scene_analyzer,
                self.metadata_extractor
            ]
            
            for component in components:
                if hasattr(component, 'cleanup'):
                    cleanup_tasks.append(component.cleanup())
            
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            # Cleanup infrastructure
            await self.cache_manager.close()
            await self.performance_monitor.close()
            
            # Clear queues
            for queue in self.priority_queues.values():
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
            
            self.status = AgentStatus.STOPPED
            logger.info("Vision Orchestrator cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Vision Orchestrator cleanup failed: {e}")
            self.status = AgentStatus.ERROR
