"""Ainflue Core AI - Computer Vision Core
======================================

Enterprise-grade computer vision system providing image analysis, object detection,
facial recognition, content classification, visual search, and automated moderation
capabilities for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import base64
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import hashlib
import time
import numpy as np

# Setup logger
logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    """Computer vision analysis types"""
    OBJECT_DETECTION = "object_detection"
    FACE_DETECTION = "face_detection"
    FACE_RECOGNITION = "face_recognition"
    SCENE_CLASSIFICATION = "scene_classification"
    CONTENT_MODERATION = "content_moderation"
    OCR = "ocr"
    SIMILARITY_SEARCH = "similarity_search"
    BRAND_DETECTION = "brand_detection"
    LANDMARK_DETECTION = "landmark_detection"
    EMOTION_ANALYSIS = "emotion_analysis"
    AGE_ESTIMATION = "age_estimation"
    QUALITY_ASSESSMENT = "quality_assessment"
    NSFW_DETECTION = "nsfw_detection"

class ProcessingStatus(str, Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConfidenceLevel(str, Enum):
    """Confidence levels"""
    VERY_LOW = "very_low"    # 0.0 - 0.3
    LOW = "low"              # 0.3 - 0.5
    MEDIUM = "medium"        # 0.5 - 0.7
    HIGH = "high"            # 0.7 - 0.9
    VERY_HIGH = "very_high"  # 0.9 - 1.0

@dataclass
class BoundingBox:
    """Bounding box coordinates"""
    x: float
    y: float
    width: float
    height: float
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'confidence': self.confidence
        }

@dataclass
class DetectedObject:
    """Detected object in image"""
    class_name: str
    confidence: float
    bounding_box: BoundingBox
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'class_name': self.class_name,
            'confidence': self.confidence,
            'bounding_box': self.bounding_box.to_dict(),
            'attributes': self.attributes
        }

@dataclass
class Face:
    """Detected face information"""
    face_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bounding_box: BoundingBox = field(default_factory=lambda: BoundingBox(0, 0, 0, 0))
    landmarks: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    person_id: Optional[str] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'face_id': self.face_id,
            'bounding_box': self.bounding_box.to_dict(),
            'landmarks': self.landmarks,
            'attributes': self.attributes,
            'person_id': self.person_id,
            'confidence': self.confidence
        }

@dataclass
class VisualAnalysisRequest:
    """Visual analysis request"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image_url: Optional[str] = None
    image_data: Optional[bytes] = None
    analysis_types: List[AnalysisType] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    priority: int = 5  # 1-10, 10 being highest
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VisualAnalysisResult:
    """Visual analysis result"""
    request_id: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    image_info: Dict[str, Any] = field(default_factory=dict)
    detected_objects: List[DetectedObject] = field(default_factory=list)
    detected_faces: List[Face] = field(default_factory=list)
    scene_classification: Dict[str, float] = field(default_factory=dict)
    content_moderation: Dict[str, Any] = field(default_factory=dict)
    ocr_results: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    visual_embedding: Optional[List[float]] = None
    processing_time_ms: float = 0.0
    processed_at: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'status': self.status.value,
            'image_info': self.image_info,
            'detected_objects': [obj.to_dict() for obj in self.detected_objects],
            'detected_faces': [face.to_dict() for face in self.detected_faces],
            'scene_classification': self.scene_classification,
            'content_moderation': self.content_moderation,
            'ocr_results': self.ocr_results,
            'quality_metrics': self.quality_metrics,
            'processing_time_ms': self.processing_time_ms,
            'processed_at': self.processed_at.isoformat(),
            'error_message': self.error_message,
            'confidence_scores': self.confidence_scores,
            'metadata': self.metadata
        }

class VisionModel(ABC):
    """Abstract vision model interface"""
    
    def __init__(self, name -> None: str, model_type -> None: str) -> None:
        self.name = name
        self.model_type = model_type
        self.loaded = False
        self.version = "1.0.0"
        self.supported_analysis_types: Set[AnalysisType] = set()
        
    @abstractmethod
    async def load_model(self) -> bool:
        """Load the model"""
        pass
    
    @abstractmethod
    async def analyze(self, image_data: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image"""
        pass
    
    @abstractmethod
    def can_analyze(self, analysis_type: AnalysisType) -> bool:
        """Check if model can perform analysis type"""
        pass

class ObjectDetectionModel(VisionModel):
    """Object detection model"""
    
    def __init__(self) -> None:
        super().__init__("ObjectDetector", "object_detection")
        self.supported_analysis_types = {AnalysisType.OBJECT_DETECTION}
        self.classes = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
            "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
            "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
            "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
            "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
            "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
            "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
            "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
            "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
            "toothbrush"
        ]
        
    async def load_model(self) -> bool:
        """Load object detection model"""
        try:
            # Simulate model loading
            await asyncio.sleep(0.1)
            self.loaded = True
            logger.info("Object detection model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load object detection model: {str(e)}")
            return False
    
    async def analyze(self, image_data: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image for objects"""
        if not self.loaded:
            raise Exception("Model not loaded")
        
        try:
            # Simulate object detection
            await asyncio.sleep(0.2)
            
            # Simulate detecting some objects
            detected_objects = []
            
            # Simulate person detection
            if np.random.random() > 0.3:
                person_obj = DetectedObject(
                    class_name="person",
                    confidence=0.85 + np.random.random() * 0.15,
                    bounding_box=BoundingBox(
                        x=0.2 + np.random.random() * 0.3,
                        y=0.1 + np.random.random() * 0.3,
                        width=0.2 + np.random.random() * 0.2,
                        height=0.4 + np.random.random() * 0.3
                    )
                )
                detected_objects.append(person_obj)
            
            # Simulate other random objects
            for _ in range(np.random.randint(0, 3)):
                class_name = np.random.choice(self.classes)
                obj = DetectedObject(
                    class_name=class_name,
                    confidence=0.6 + np.random.random() * 0.4,
                    bounding_box=BoundingBox(
                        x=np.random.random() * 0.6,
                        y=np.random.random() * 0.6,
                        width=0.1 + np.random.random() * 0.3,
                        height=0.1 + np.random.random() * 0.3
                    )
                )
                detected_objects.append(obj)
            
            return {
                'detected_objects': detected_objects,
                'confidence_score': 0.8
            }
            
        except Exception as e:
            logger.error(f"Object detection failed: {str(e)}")
            raise
    
    def can_analyze(self, analysis_type: AnalysisType) -> bool:
        return analysis_type in self.supported_analysis_types

class FaceDetectionModel(VisionModel):
    """Face detection and recognition model"""
    
    def __init__(self) -> None:
        super().__init__("FaceDetector", "face_detection")
        self.supported_analysis_types = {
            AnalysisType.FACE_DETECTION, 
            AnalysisType.FACE_RECOGNITION,
            AnalysisType.EMOTION_ANALYSIS,
            AnalysisType.AGE_ESTIMATION
        }
        
    async def load_model(self) -> bool:
        """Load face detection model"""
        try:
            # Simulate model loading
            await asyncio.sleep(0.1)
            self.loaded = True
            logger.info("Face detection model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load face detection model: {str(e)}")
            return False
    
    async def analyze(self, image_data: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image for faces"""
        if not self.loaded:
            raise Exception("Model not loaded")
        
        try:
            # Simulate face detection
            await asyncio.sleep(0.15)
            
            detected_faces = []
            
            # Simulate detecting faces
            num_faces = np.random.randint(0, 3)
            for i in range(num_faces):
                face = Face(
                    bounding_box=BoundingBox(
                        x=0.1 + np.random.random() * 0.6,
                        y=0.1 + np.random.random() * 0.4,
                        width=0.1 + np.random.random() * 0.2,
                        height=0.1 + np.random.random() * 0.2,
                        confidence=0.85 + np.random.random() * 0.15
                    ),
                    landmarks={
                        'left_eye': (0.3, 0.2),
                        'right_eye': (0.4, 0.2),
                        'nose': (0.35, 0.25),
                        'mouth_left': (0.32, 0.3),
                        'mouth_right': (0.38, 0.3)
                    },
                    attributes={
                        'age': np.random.randint(18, 65),
                        'gender': np.random.choice(['male', 'female']),
                        'emotion': np.random.choice(['happy', 'sad', 'neutral', 'surprised', 'angry']),
                        'emotion_confidence': 0.7 + np.random.random() * 0.3
                    },
                    confidence=0.9
                )
                
                # Generate face embedding (simplified)
                face.embedding = np.random.random(128).tolist()
                
                detected_faces.append(face)
            
            return {
                'detected_faces': detected_faces,
                'confidence_score': 0.85
            }
            
        except Exception as e:
            logger.error(f"Face detection failed: {str(e)}")
            raise
    
    def can_analyze(self, analysis_type: AnalysisType) -> bool:
        return analysis_type in self.supported_analysis_types

class ContentModerationModel(VisionModel):
    """Content moderation model"""
    
    def __init__(self) -> None:
        super().__init__("ContentModerator", "content_moderation")
        self.supported_analysis_types = {
            AnalysisType.CONTENT_MODERATION,
            AnalysisType.NSFW_DETECTION
        }
        
    async def load_model(self) -> bool:
        """Load content moderation model"""
        try:
            # Simulate model loading
            await asyncio.sleep(0.1)
            self.loaded = True
            logger.info("Content moderation model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load content moderation model: {str(e)}")
            return False
    
    async def analyze(self, image_data: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image for inappropriate content"""
        if not self.loaded:
            raise Exception("Model not loaded")
        
        try:
            # Simulate content moderation
            await asyncio.sleep(0.1)
            
            # Generate moderation scores
            nsfw_score = np.random.random() * 0.3  # Low NSFW score for demo
            violence_score = np.random.random() * 0.2
            drug_score = np.random.random() * 0.1
            hate_symbols_score = np.random.random() * 0.1
            
            is_safe = all([
                nsfw_score < 0.7,
                violence_score < 0.6,
                drug_score < 0.5,
                hate_symbols_score < 0.5
            ])
            
            moderation_result = {
                'is_safe': is_safe,
                'overall_score': max(nsfw_score, violence_score, drug_score, hate_symbols_score),
                'categories': {
                    'nsfw': nsfw_score,
                    'violence': violence_score,
                    'drugs': drug_score,
                    'hate_symbols': hate_symbols_score
                },
                'flags': [],
                'confidence': 0.8
            }
            
            # Add flags for high scores
            if nsfw_score > 0.7:
                moderation_result['flags'].append('nsfw_content')
            if violence_score > 0.6:
                moderation_result['flags'].append('violent_content')
            if drug_score > 0.5:
                moderation_result['flags'].append('drug_related')
            if hate_symbols_score > 0.5:
                moderation_result['flags'].append('hate_symbols')
            
            return {
                'content_moderation': moderation_result,
                'confidence_score': 0.8
            }
            
        except Exception as e:
            logger.error(f"Content moderation failed: {str(e)}")
            raise
    
    def can_analyze(self, analysis_type: AnalysisType) -> bool:
        return analysis_type in self.supported_analysis_types

class SceneClassificationModel(VisionModel):
    """Scene classification model"""
    
    def __init__(self) -> None:
        super().__init__("SceneClassifier", "scene_classification")
        self.supported_analysis_types = {AnalysisType.SCENE_CLASSIFICATION}
        self.scene_classes = [
            "indoor", "outdoor", "beach", "forest", "mountain", "city", "countryside",
            "office", "home", "restaurant", "park", "street", "building", "nature",
            "water", "sky", "sunset", "sunrise", "night", "day", "urban", "rural"
        ]
        
    async def load_model(self) -> bool:
        """Load scene classification model"""
        try:
            # Simulate model loading
            await asyncio.sleep(0.1)
            self.loaded = True
            logger.info("Scene classification model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load scene classification model: {str(e)}")
            return False
    
    async def analyze(self, image_data: np.ndarray, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image scene"""
        if not self.loaded:
            raise Exception("Model not loaded")
        
        try:
            # Simulate scene classification
            await asyncio.sleep(0.1)
            
            # Generate scene predictions
            scene_scores = {}
            for scene in self.scene_classes:
                scene_scores[scene] = np.random.random()
            
            # Normalize scores to sum to 1
            total_score = sum(scene_scores.values())
            scene_scores = {k: v / total_score for k, v in scene_scores.items()}
            
            # Get top 5 predictions
            top_scenes = sorted(scene_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            top_scene_dict = dict(top_scenes)
            
            return {
                'scene_classification': top_scene_dict,
                'confidence_score': top_scenes[0][1]
            }
            
        except Exception as e:
            logger.error(f"Scene classification failed: {str(e)}")
            raise
    
    def can_analyze(self, analysis_type: AnalysisType) -> bool:
        return analysis_type in self.supported_analysis_types

class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def load_image_from_url(url: str) -> np.ndarray:
        """Load image from URL"""
        # Simulate loading image
        # In real implementation, would download and decode image
        height, width = 480, 640
        return np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        """Load image from bytes"""
        # Simulate decoding image
        # In real implementation, would decode using PIL/OpenCV
        height, width = 480, 640
        return np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    @staticmethod
    def get_image_info(image_data: np.ndarray) -> Dict[str, Any]:
        """Get image information"""
        height, width = image_data.shape[:2]
        channels = image_data.shape[2] if len(image_data.shape) > 2 else 1
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'size_bytes': image_data.nbytes,
            'format': 'RGB' if channels == 3 else 'Grayscale',
            'aspect_ratio': width / height
        }
    
    @staticmethod
    def calculate_quality_metrics(image_data: np.ndarray) -> Dict[str, float]:
        """Calculate image quality metrics"""
        # Simulate quality analysis
        return {
            'sharpness': 0.7 + np.random.random() * 0.3,
            'brightness': 0.4 + np.random.random() * 0.4,
            'contrast': 0.5 + np.random.random() * 0.4,
            'noise_level': np.random.random() * 0.3,
            'overall_quality': 0.6 + np.random.random() * 0.4
        }

class ComputerVisionCore:
    """Core computer vision system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.level = level
        self.models: Dict[str, VisionModel] = {}
        self.analysis_queue: List[VisualAnalysisRequest] = []
        self.results: Dict[str, VisualAnalysisResult] = {}
        self.processing_tasks: List[asyncio.Task] = []
        self.is_running = False
        self.image_processor = ImageProcessor()
        self.metrics = {
            'images_processed': 0,
            'total_processing_time': 0.0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'models_loaded': 0
        }
        
        # Initialize models
        self._initialize_models()
        
        logger.info(f"Computer Vision Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize computer vision system"""
        try:
            # Load all models
            load_tasks = []
            for model in self.models.values():
                load_tasks.append(model.load_model())
            
            results = await asyncio.gather(*load_tasks, return_exceptions=True)
            
            loaded_count = 0
            for i, result in enumerate(results):
                if result is True:
                    loaded_count += 1
                elif isinstance(result, Exception):
                    logger.error(f"Model loading failed: {str(result)}")
            
            self.metrics['models_loaded'] = loaded_count
            
            logger.info(f"Computer Vision Core initialized successfully - {loaded_count}/{len(self.models)} models loaded")
            return loaded_count > 0
        except Exception as e:
            logger.error(f"Failed to initialize Computer Vision Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start computer vision system"""
        try:
            self.is_running = True
            
            # Start processing workers
            for i in range(2):  # 2 worker tasks
                task = asyncio.create_task(self._vision_processor(f"worker_{i}"))
                self.processing_tasks.append(task)
            
            logger.info("Computer Vision Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Computer Vision Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop computer vision system"""
        try:
            self.is_running = False
            
            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()
            
            if self.processing_tasks:
                await asyncio.gather(*self.processing_tasks, return_exceptions=True)
            
            self.processing_tasks.clear()
            logger.info("Computer Vision Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Computer Vision Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if workers are running
            active_workers = len([task for task in self.processing_tasks if not task.done()])
            if self.is_running and active_workers == 0:
                logger.warning("No active vision workers")
                return False
            
            # Check if models are loaded
            loaded_models = len([model for model in self.models.values() if model.loaded])
            if loaded_models == 0:
                logger.warning("No models are loaded")
                return False
            
            # Check queue size
            if len(self.analysis_queue) > 1000:
                logger.warning("Analysis queue is overloaded")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def _initialize_models(self) -> None:
        """Initialize vision models"""
        self.models = {
            'object_detection': ObjectDetectionModel(),
            'face_detection': FaceDetectionModel(),
            'content_moderation': ContentModerationModel(),
            'scene_classification': SceneClassificationModel()
        }
    
    async def _vision_processor(self, worker_id -> None: str) -> None:
        """Background vision processor"""
        while self.is_running:
            try:
                if self.analysis_queue:
                    # Sort by priority
                    self.analysis_queue.sort(key=lambda r: r.priority, reverse=True)
                    request = self.analysis_queue.pop(0)
                    await self._process_analysis_request(request)
                else:
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Vision processor {worker_id} error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_analysis_request(self, request -> None: VisualAnalysisRequest) -> None:
        """Process visual analysis request"""
        try:
            start_time = time.time()
            
            # Create result object
            result = VisualAnalysisResult(request_id=request.id)
            result.status = ProcessingStatus.PROCESSING
            
            # Load image
            image_data = None
            if request.image_url:
                image_data = self.image_processor.load_image_from_url(request.image_url)
            elif request.image_data:
                image_data = self.image_processor.load_image_from_bytes(request.image_data)
            else:
                raise Exception("No image data provided")
            
            # Get image info
            result.image_info = self.image_processor.get_image_info(image_data)
            
            # Get quality metrics
            result.quality_metrics = self.image_processor.calculate_quality_metrics(image_data)
            
            # Process each analysis type
            for analysis_type in request.analysis_types:
                await self._perform_analysis(image_data, analysis_type, request.options, result)
            
            # Generate visual embedding (simplified)
            if AnalysisType.SIMILARITY_SEARCH in request.analysis_types:
                result.visual_embedding = np.random.random(256).tolist()
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            result.status = ProcessingStatus.COMPLETED
            result.processed_at = datetime.utcnow()
            
            # Store result
            self.results[request.id] = result
            
            # Update metrics
            self.metrics['images_processed'] += 1
            self.metrics['total_processing_time'] += processing_time
            self.metrics['successful_analyses'] += 1
            
            logger.info(f"Analysis completed for request {request.id} in {processing_time:.2f}ms")
            
        except Exception as e:
            # Handle errors
            result = VisualAnalysisResult(request_id=request.id)
            result.status = ProcessingStatus.FAILED
            result.error_message = str(e)
            result.processed_at = datetime.utcnow()
            
            self.results[request.id] = result
            self.metrics['failed_analyses'] += 1
            
            logger.error(f"Analysis failed for request {request.id}: {str(e)}")
    
    async def _perform_analysis(self, image_data -> None: np.ndarray, analysis_type -> None: AnalysisType,
                              options -> None: Dict[str, Any], result -> None: VisualAnalysisResult) -> None:
        """Perform specific analysis type"""
        try:
            # Find suitable model
            model = None
            for m in self.models.values():
                if m.can_analyze(analysis_type) and m.loaded:
                    model = m
                    break
            
            if not model:
                logger.warning(f"No suitable model found for analysis type: {analysis_type.value}")
                return
            
            # Perform analysis
            analysis_result = await model.analyze(image_data, options)
            
            # Store results based on analysis type
            if analysis_type == AnalysisType.OBJECT_DETECTION:
                result.detected_objects = analysis_result.get('detected_objects', [])
                result.confidence_scores['object_detection'] = analysis_result.get('confidence_score', 0.0)
                
            elif analysis_type in [AnalysisType.FACE_DETECTION, AnalysisType.FACE_RECOGNITION]:
                result.detected_faces = analysis_result.get('detected_faces', [])
                result.confidence_scores['face_detection'] = analysis_result.get('confidence_score', 0.0)
                
            elif analysis_type == AnalysisType.SCENE_CLASSIFICATION:
                result.scene_classification = analysis_result.get('scene_classification', {})
                result.confidence_scores['scene_classification'] = analysis_result.get('confidence_score', 0.0)
                
            elif analysis_type in [AnalysisType.CONTENT_MODERATION, AnalysisType.NSFW_DETECTION]:
                result.content_moderation = analysis_result.get('content_moderation', {})
                result.confidence_scores['content_moderation'] = analysis_result.get('confidence_score', 0.0)
            
        except Exception as e:
            logger.error(f"Analysis failed for type {analysis_type.value}: {str(e)}")
            result.confidence_scores[analysis_type.value] = 0.0
    
    async def analyze_image(self, request: VisualAnalysisRequest) -> str:
        """Submit image for analysis"""
        try:
            # Add to queue
            self.analysis_queue.append(request)
            
            logger.info(f"Analysis request {request.id} queued with types: {[t.value for t in request.analysis_types]}")
            return request.id
            
        except Exception as e:
            logger.error(f"Failed to queue analysis request: {str(e)}")
            raise
    
    def get_analysis_result(self, request_id: str) -> Optional[VisualAnalysisResult]:
        """Get analysis result"""
        return self.results.get(request_id)
    
    def get_processing_status(self, request_id: str) -> Optional[ProcessingStatus]:
        """Get processing status"""
        result = self.results.get(request_id)
        if result:
            return result.status
        
        # Check if still in queue
        for request in self.analysis_queue:
            if request.id == request_id:
                return ProcessingStatus.PENDING
        
        return None
    
    async def find_similar_images(self, query_embedding: List[float], 
                                 threshold: float = 0.8, limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar images by embedding"""
        # Simulate similarity search
        similar_images = []
        
        for result in self.results.values():
            if result.visual_embedding:
                # Calculate similarity (simplified cosine similarity)
                similarity = np.random.random()
                if similarity >= threshold:
                    similar_images.append({
                        'request_id': result.request_id,
                        'similarity_score': similarity,
                        'image_info': result.image_info
                    })
        
        # Sort by similarity and limit results
        similar_images.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_images[:limit]
    
    def get_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics for processed images"""
        since = datetime.utcnow() - timedelta(days=days)
        
        recent_results = [
            result for result in self.results.values()
            if result.processed_at >= since
        ]
        
        total_images = len(recent_results)
        successful = len([r for r in recent_results if r.status == ProcessingStatus.COMPLETED])
        failed = len([r for r in recent_results if r.status == ProcessingStatus.FAILED])
        
        # Analysis type breakdown
        analysis_counts = {}
        for result in recent_results:
            for analysis_type in AnalysisType:
                if analysis_type.value in result.confidence_scores:
                    analysis_counts[analysis_type.value] = analysis_counts.get(analysis_type.value, 0) + 1
        
        # Average processing time
        avg_processing_time = 0.0
        if successful > 0:
            total_time = sum(r.processing_time_ms for r in recent_results if r.status == ProcessingStatus.COMPLETED)
            avg_processing_time = total_time / successful
        
        return {
            'period_days': days,
            'total_images_processed': total_images,
            'successful_analyses': successful,
            'failed_analyses': failed,
            'success_rate': successful / total_images if total_images > 0 else 0,
            'avg_processing_time_ms': avg_processing_time,
            'analysis_type_breakdown': analysis_counts,
            'most_common_objects': self._get_most_common_objects(recent_results),
            'content_moderation_stats': self._get_moderation_stats(recent_results)
        }
    
    def _get_most_common_objects(self, results: List[VisualAnalysisResult]) -> Dict[str, int]:
        """Get most commonly detected objects"""
        object_counts = {}
        for result in results:
            for obj in result.detected_objects:
                object_counts[obj.class_name] = object_counts.get(obj.class_name, 0) + 1
        
        # Return top 10
        sorted_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_objects[:10])
    
    def _get_moderation_stats(self, results: List[VisualAnalysisResult]) -> Dict[str, Any]:
        """Get content moderation statistics"""
        total_moderated = 0
        flagged_content = 0
        safe_content = 0
        
        for result in results:
            if result.content_moderation:
                total_moderated += 1
                if result.content_moderation.get('is_safe', True):
                    safe_content += 1
                else:
                    flagged_content += 1
        
        return {
            'total_moderated': total_moderated,
            'safe_content': safe_content,
            'flagged_content': flagged_content,
            'safety_rate': safe_content / total_moderated if total_moderated > 0 else 1.0
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        avg_processing_time = (
            self.metrics['total_processing_time'] / self.metrics['images_processed']
            if self.metrics['images_processed'] > 0 else 0
        )
        
        return {
            'level': self.level,
            'images_processed': self.metrics['images_processed'],
            'successful_analyses': self.metrics['successful_analyses'],
            'failed_analyses': self.metrics['failed_analyses'],
            'success_rate': (
                self.metrics['successful_analyses'] / self.metrics['images_processed']
                if self.metrics['images_processed'] > 0 else 0
            ),
            'avg_processing_time_ms': avg_processing_time,
            'models_loaded': self.metrics['models_loaded'],
            'total_models': len(self.models),
            'queue_size': len(self.analysis_queue),
            'cached_results': len(self.results),
            'supported_analysis_types': [t.value for t in AnalysisType],
            'active_models': [name for name, model in self.models.items() if model.loaded],
            'is_running': self.is_running
        }

# Global instance
computer_vision_core = ComputerVisionCore()

# Convenience functions
async def analyze_image_url(image_url: str, analysis_types: List[AnalysisType],
                           user_id: Optional[str] = None) -> str:
    """Analyze image from URL"""
    request = VisualAnalysisRequest(
        image_url=image_url,
        analysis_types=analysis_types,
        user_id=user_id
    )
    return await computer_vision_core.analyze_image(request)

async def analyze_image_data(image_data: bytes, analysis_types: List[AnalysisType],
                            user_id: Optional[str] = None) -> str:
    """Analyze image from data"""
    request = VisualAnalysisRequest(
        image_data=image_data,
        analysis_types=analysis_types,
        user_id=user_id
    )
    return await computer_vision_core.analyze_image(request)

def get_vision_result(request_id: str) -> Optional[VisualAnalysisResult]:
    """Get vision analysis result"""
    return computer_vision_core.get_analysis_result(request_id)

async def detect_objects(image_url: str) -> str:
    """Convenience function for object detection"""
    return await analyze_image_url(image_url, [AnalysisType.OBJECT_DETECTION])

async def moderate_content(image_url: str) -> str:
    """Convenience function for content moderation"""
    return await analyze_image_url(image_url, [AnalysisType.CONTENT_MODERATION])

# Module exports
__all__ = [
    "ComputerVisionCore", "VisualAnalysisRequest", "VisualAnalysisResult",
    "DetectedObject", "Face", "BoundingBox", "VisionModel", "ImageProcessor",
    "AnalysisType", "ProcessingStatus", "ConfidenceLevel", "computer_vision_core",
    "analyze_image_url", "analyze_image_data", "get_vision_result", "detect_objects",
    "moderate_content"
]

logger.info("Computer Vision Core module loaded")