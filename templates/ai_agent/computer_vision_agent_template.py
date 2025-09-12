"""{{agent_name}} Computer Vision Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
import io
import base64

import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import torch
import torchvision.transforms as transforms
from transformers import pipeline, AutoModel, AutoTokenizer
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import CVModelManager
from cv.preprocessing import ImagePreprocessor, VideoPreprocessor
from cv.detection import ObjectDetector, FaceDetector
from cv.recognition import ImageClassifier, SceneAnalyzer
from cv.enhancement import ImageEnhancer, VideoStabilizer
from core.config import get_settings
from utils.exceptions import CVException
from monitoring.cv_metrics import CVMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class CVTaskType(Enum):
    """Computer vision task types"""
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    FACE_RECOGNITION = "face_recognition"
    SCENE_ANALYSIS = "scene_analysis"
    IMAGE_ENHANCEMENT = "image_enhancement"
    VIDEO_ANALYSIS = "video_analysis"
    CONTENT_MODERATION = "content_moderation"
    VISUAL_SEARCH = "visual_search"
    OCR_EXTRACTION = "ocr_extraction"
    STYLE_TRANSFER = "style_transfer"


class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"


class VideoFormat(Enum):
    """Supported video formats"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"
    MKV = "mkv"


class CVModelConfig(BaseModel):
    """Computer vision model configuration"""
    model_name: str = Field(..., description="Name of the CV model")
    model_type: str = Field(..., description="Type of CV model")
    confidence_threshold: float = Field(default=0.5, description="Confidence threshold for predictions")
    max_detections: int = Field(default=100, description="Maximum number of detections")
    input_resolution: Tuple[int, int] = Field(default=(224, 224), description="Input image resolution")
    batch_size: int = Field(default=1, description="Batch size for processing")
    use_gpu: bool = Field(default=True, description="Use GPU acceleration if available")
    preprocessing_config: Dict[str, Any] = Field(default_factory=dict, description="Preprocessing configuration")
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence threshold must be between 0 and 1')
        return v
    
    @validator('max_detections')
    def validate_max_detections(cls, v):
        if v <= 0:
            raise ValueError('Max detections must be positive')
        return v


class CVImageTask(BaseModel):
    """Computer vision image processing task"""
    id: str = Field(..., description="Unique task identifier")
    image_data: Union[str, bytes] = Field(..., description="Image data (base64 or bytes)")
    image_format: ImageFormat = Field(default=ImageFormat.JPEG, description="Image format")
    task_type: CVTaskType = Field(..., description="Type of CV task")
    model_config: CVModelConfig = Field(..., description="Model configuration")
    roi_coordinates: Optional[Tuple[int, int, int, int]] = Field(default=None, description="Region of interest (x, y, w, h)")
    enhancement_options: Optional[Dict[str, Any]] = Field(default=None, description="Image enhancement options")
    metadata_extraction: bool = Field(default=True, description="Extract image metadata")
    priority: int = Field(default=1, description="Task priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CVVideoTask(BaseModel):
    """Computer vision video processing task"""
    id: str = Field(..., description="Unique task identifier")
    video_path: str = Field(..., description="Path to video file")
    video_format: VideoFormat = Field(default=VideoFormat.MP4, description="Video format")
    task_type: CVTaskType = Field(..., description="Type of CV task")
    model_config: CVModelConfig = Field(..., description="Model configuration")
    frame_sampling_rate: int = Field(default=1, description="Process every Nth frame")
    start_time: Optional[float] = Field(default=None, description="Start time in seconds")
    end_time: Optional[float] = Field(default=None, description="End time in seconds")
    output_format: Optional[str] = Field(default=None, description="Output video format")
    priority: int = Field(default=1, description="Task priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CVDetection(BaseModel):
    """Computer vision detection result"""
    class_name: str = Field(..., description="Detected object class")
    confidence: float = Field(..., description="Detection confidence")
    bounding_box: Tuple[int, int, int, int] = Field(..., description="Bounding box (x, y, w, h)")
    additional_attributes: Optional[Dict[str, Any]] = Field(default=None, description="Additional attributes")


class CVResult(BaseModel):
    """Computer vision operation result"""
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether the operation succeeded")
    task_type: CVTaskType = Field(..., description="Type of CV task")
    detections: Optional[List[CVDetection]] = Field(default=None, description="Detection results")
    classifications: Optional[Dict[str, float]] = Field(default=None, description="Classification results")
    enhanced_image: Optional[str] = Field(default=None, description="Enhanced image (base64)")
    extracted_text: Optional[str] = Field(default=None, description="Extracted text (OCR)")
    scene_description: Optional[str] = Field(default=None, description="Scene description")
    content_moderation: Optional[Dict[str, Any]] = Field(default=None, description="Content moderation results")
    processing_time: float = Field(..., description="Processing time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{agent_name}}Agent(BaseAIAgent):
    """{{agent_description}} with comprehensive computer vision capabilities"""
    
    def __init__(
        self,
        agent_id: str,
        model_configs: Dict[str, CVModelConfig],
        enable_gpu: bool = True,
        cache_size: int = 1000,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, **kwargs)
        self.model_configs = model_configs
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.cache_size = cache_size
        self.device = torch.device("cuda" if self.enable_gpu else "cpu")
        
        # Initialize components
        self.model_manager = CVModelManager()
        self.image_preprocessor = ImagePreprocessor()
        self.video_preprocessor = VideoPreprocessor()
        self.object_detector = ObjectDetector()
        self.face_detector = FaceDetector()
        self.image_classifier = ImageClassifier()
        self.scene_analyzer = SceneAnalyzer()
        self.image_enhancer = ImageEnhancer()
        self.video_stabilizer = VideoStabilizer()
        self.metrics_collector = CVMetricsCollector()
        
        # Load models
        self._load_models()
        
        logger.info(f"ComputerVisionAgent {agent_id} initialized with {len(model_configs)} models")
    
    def _load_models(self):
        """Load computer vision models"""
        try:
            for model_name, config in self.model_configs.items():
                self.model_manager.load_model(
                    model_name=model_name,
                    model_type=config.model_type,
                    device=self.device,
                    config=config.dict()
                )
            logger.info("All CV models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CV models: {e}")
            raise CVException(f"Model loading failed: {e}")
    
    async def process_image_task(self, task: CVImageTask) -> CVResult:
        """Process image analysis task"""
        start_time = datetime.utcnow()
        
        try:
            # Decode image data
            if isinstance(task.image_data, str):
                image_bytes = base64.b64decode(task.image_data)
            else:
                image_bytes = task.image_data
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # Apply ROI if specified
            if task.roi_coordinates:
                x, y, w, h = task.roi_coordinates
                image = image.crop((x, y, x + w, y + h))
            
            # Preprocess image
            processed_image = await self.image_preprocessor.preprocess(
                image=image,
                target_size=task.model_config.input_resolution,
                config=task.model_config.preprocessing_config
            )
            
            # Perform task-specific processing
            result_data = await self._execute_image_task(processed_image, task)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = CVResult(
                task_id=task.id,
                success=True,
                task_type=task.task_type,
                processing_time=processing_time,
                **result_data
            )
            
            # Collect metrics
            await self.metrics_collector.record_task_completion(
                task_type=task.task_type.value,
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Image task {task.id} failed: {e}")
            
            # Collect error metrics
            await self.metrics_collector.record_task_completion(
                task_type=task.task_type.value,
                processing_time=processing_time,
                success=False
            )
            
            return CVResult(
                task_id=task.id,
                success=False,
                task_type=task.task_type,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def process_video_task(self, task: CVVideoTask) -> CVResult:
        """Process video analysis task"""
        start_time = datetime.utcnow()
        
        try:
            # Load video
            video_data = await self.video_preprocessor.load_video(
                video_path=task.video_path,
                start_time=task.start_time,
                end_time=task.end_time
            )
            
            # Extract frames for processing
            frames = await self.video_preprocessor.extract_frames(
                video_data=video_data,
                sampling_rate=task.frame_sampling_rate,
                target_size=task.model_config.input_resolution
            )
            
            # Process frames
            frame_results = []
            for frame_idx, frame in enumerate(frames):
                frame_result = await self._execute_image_task_on_frame(frame, task, frame_idx)
                frame_results.append(frame_result)
            
            # Aggregate results
            aggregated_result = await self._aggregate_video_results(frame_results, task)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = CVResult(
                task_id=task.id,
                success=True,
                task_type=task.task_type,
                processing_time=processing_time,
                **aggregated_result
            )
            
            # Collect metrics
            await self.metrics_collector.record_task_completion(
                task_type=task.task_type.value,
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Video task {task.id} failed: {e}")
            
            return CVResult(
                task_id=task.id,
                success=False,
                task_type=task.task_type,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _execute_image_task(self, image: np.ndarray, task: CVImageTask) -> Dict[str, Any]:
        """Execute specific image processing task"""
        result_data = {}
        
        if task.task_type == CVTaskType.IMAGE_CLASSIFICATION:
            classifications = await self.image_classifier.classify(
                image=image,
                model_config=task.model_config
            )
            result_data["classifications"] = classifications
            
        elif task.task_type == CVTaskType.OBJECT_DETECTION:
            detections = await self.object_detector.detect(
                image=image,
                model_config=task.model_config
            )
            result_data["detections"] = [
                CVDetection(
                    class_name=det["class_name"],
                    confidence=det["confidence"],
                    bounding_box=det["bounding_box"]
                ) for det in detections
            ]
            
        elif task.task_type == CVTaskType.FACE_RECOGNITION:
            faces = await self.face_detector.detect_faces(
                image=image,
                model_config=task.model_config
            )
            result_data["detections"] = [
                CVDetection(
                    class_name="face",
                    confidence=face["confidence"],
                    bounding_box=face["bounding_box"],
                    additional_attributes=face.get("attributes", {})
                ) for face in faces
            ]
            
        elif task.task_type == CVTaskType.SCENE_ANALYSIS:
            scene_description = await self.scene_analyzer.analyze_scene(
                image=image,
                model_config=task.model_config
            )
            result_data["scene_description"] = scene_description
            
        elif task.task_type == CVTaskType.IMAGE_ENHANCEMENT:
            enhanced_image = await self.image_enhancer.enhance(
                image=image,
                enhancement_options=task.enhancement_options or {}
            )
            # Convert to base64
            enhanced_base64 = await self._image_to_base64(enhanced_image)
            result_data["enhanced_image"] = enhanced_base64
            
        elif task.task_type == CVTaskType.CONTENT_MODERATION:
            moderation_result = await self._moderate_content(image, task.model_config)
            result_data["content_moderation"] = moderation_result
            
        elif task.task_type == CVTaskType.OCR_EXTRACTION:
            extracted_text = await self._extract_text_ocr(image)
            result_data["extracted_text"] = extracted_text
            
        return result_data
    
    async def _execute_image_task_on_frame(
        self, 
        frame: np.ndarray, 
        task: CVVideoTask, 
        frame_idx: int
    ) -> Dict[str, Any]:
        """Execute image task on video frame"""
        # Create temporary image task
        temp_task = CVImageTask(
            id=f"{task.id}_frame_{frame_idx}",
            image_data=await self._frame_to_base64(frame),
            task_type=task.task_type,
            model_config=task.model_config
        )
        
        return await self._execute_image_task(frame, temp_task)
    
    async def _aggregate_video_results(
        self, 
        frame_results: List[Dict[str, Any]], 
        task: CVVideoTask
    ) -> Dict[str, Any]:
        """Aggregate results from video frames"""
        aggregated = {}
        
        if task.task_type == CVTaskType.OBJECT_DETECTION:
            # Aggregate detections across frames
            all_detections = []
            for frame_result in frame_results:
                if "detections" in frame_result:
                    all_detections.extend(frame_result["detections"])
            aggregated["detections"] = all_detections
            
        elif task.task_type == CVTaskType.IMAGE_CLASSIFICATION:
            # Average classification scores
            classification_sums = {}
            classification_counts = {}
            
            for frame_result in frame_results:
                if "classifications" in frame_result:
                    for class_name, score in frame_result["classifications"].items():
                        classification_sums[class_name] = classification_sums.get(class_name, 0) + score
                        classification_counts[class_name] = classification_counts.get(class_name, 0) + 1
            
            aggregated["classifications"] = {
                class_name: classification_sums[class_name] / classification_counts[class_name]
                for class_name in classification_sums
            }
        
        return aggregated
    
    async def _moderate_content(self, image: np.ndarray, model_config: CVModelConfig) -> Dict[str, Any]:
        """Perform content moderation on image"""
        # Implementation for content moderation
        # This could include NSFW detection, violence detection, etc.
        moderation_result = {
            "is_safe": True,
            "flags": [],
            "confidence": 0.95
        }
        return moderation_result
    
    async def _extract_text_ocr(self, image: np.ndarray) -> str:
        """Extract text from image using OCR"""
        # Implementation for OCR text extraction
        # Could use Tesseract, EasyOCR, or cloud APIs
        extracted_text = "Sample extracted text"
        return extracted_text
    
    async def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert image to base64 string"""
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(image)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return image_base64
    
    async def _frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert video frame to base64 string"""
        return await self._image_to_base64(frame)
    
    async def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported image and video formats"""
        return {
            "image_formats": [fmt.value for fmt in ImageFormat],
            "video_formats": [fmt.value for fmt in VideoFormat]
        }
    
    async def get_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about loaded models"""
        model_info = {}
        for model_name, config in self.model_configs.items():
            model_info[model_name] = {
                "model_type": config.model_type,
                "confidence_threshold": config.confidence_threshold,
                "input_resolution": config.input_resolution,
                "batch_size": config.batch_size,
                "use_gpu": config.use_gpu
            }
        return model_info
    
    async def update_model_config(self, model_name: str, new_config: CVModelConfig):
        """Update model configuration"""
        if model_name in self.model_configs:
            self.model_configs[model_name] = new_config
            # Reload model with new configuration
            await self.model_manager.reload_model(model_name, new_config.dict())
            logger.info(f"Updated configuration for model {model_name}")
        else:
            raise CVException(f"Model {model_name} not found")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the CV agent"""
        return await self.metrics_collector.get_metrics_summary()


# Template usage example
def create_computer_vision_agent_example():
    """Example of how to create and use a computer vision agent"""
    
    # Define model configurations
    model_configs = {
        "yolo_detector": CVModelConfig(
            model_name="yolo_v5",
            model_type="object_detection",
            confidence_threshold=0.5,
            max_detections=100,
            input_resolution=(640, 640)
        ),
        "resnet_classifier": CVModelConfig(
            model_name="resnet50",
            model_type="image_classification",
            confidence_threshold=0.3,
            input_resolution=(224, 224)
        ),
        "face_detector": CVModelConfig(
            model_name="mtcnn",
            model_type="face_detection",
            confidence_threshold=0.7,
            input_resolution=(224, 224)
        )
    }
    
    # Create agent
    cv_agent = ComputerVisionAgent(
        agent_id="cv_agent_001",
        model_configs=model_configs,
        enable_gpu=True
    )
    
    return cv_agent


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "computer_vision_agent_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive computer vision agent template for image and video analysis",
    "required_parameters": [
        "agent_name",
        "agent_description", 
        "author_name",
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_model_configs",
        "additional_task_types",
        "custom_preprocessing_options"
    ],
    "dependencies": [
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "transformers>=4.35.0",
        "numpy>=1.24.0"
    ],
    "features": [
        "Multi-format image/video support",
        "Object detection and classification",
        "Face recognition and analysis",
        "Scene understanding",
        "Image enhancement",
        "Content moderation",
        "OCR text extraction",
        "Performance monitoring",
        "GPU acceleration",
        "Batch processing"
    ]
}