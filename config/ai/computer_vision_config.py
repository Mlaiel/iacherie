"""Computer Vision Configuration for IA-Influencer Agent Platform
=============================================================

Professional Computer Vision and Image Processing configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class VisionTask(str, Enum):
    """
Supported computer vision tasks."""

    
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    IMAGE_SEGMENTATION = "image_segmentation"
    FACE_DETECTION = "face_detection"
    FACE_RECOGNITION = "face_recognition"
    IMAGE_SIMILARITY = "image_similarity"
    IMAGE_FINGERPRINTING = "image_fingerprinting"
    CONTENT_MODERATION = "content_moderation"
    BRAND_DETECTION = "brand_detection"
    TEXT_EXTRACTION = "text_extraction"  # OCR
    SCENE_CLASSIFICATION = "scene_classification"
    QUALITY_ASSESSMENT = "quality_assessment"
    IMAGE_ENHANCEMENT = "image_enhancement"
    DUPLICATE_DETECTION = "duplicate_detection"
    WATERMARK_DETECTION = "watermark_detection"
    VIDEO_ANALYSIS = "video_analysis"
    MOTION_DETECTION = "motion_detection"


class ImageFormat(str, Enum):
    """Supported image formats."""

    
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"
    GIF = "gif"
    SVG = "svg"


class VideoFormat(str, Enum):
    """Supported video formats."""

    
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    MKV = "mkv"


@dataclass
class VisionModelSpec:
    """Specification for computer vision model configuration."""
    
    task: VisionTask
    model_name: str
    model_path: str
    input_size: Tuple[int, int, int]  # (height, width, channels)
    output_classes: Optional[int] = None
    batch_size: int = 16
    requires_gpu: bool = True
    memory_requirement_mb: int = 1024
    inference_time_ms: int = 100
    accuracy_score: float = 0.85
    preprocessing_required: bool = True
    postprocessing_required: bool = False
    supports_streaming: bool = False
    custom_params: Optional[Dict[str, Any]] = None


class ComputerVisionConfig(BaseSettings):
    """
    Professional Computer Vision Configuration for IA-Influencer Agent Platform.
    
    Manages all computer vision models and configurations for image/video
    processing, analysis, protection, and content understanding.
    """
    
    # Core Vision Configuration
    DEFAULT_INPUT_SIZE: Tuple[int, int] = (224, 224)
    MAX_IMAGE_SIZE_MB: float = 50.0
    MAX_VIDEO_SIZE_MB: float = 500.0
    SUPPORTED_IMAGE_FORMATS: List[str] = ["jpeg", "png", "webp", "bmp"]
    SUPPORTED_VIDEO_FORMATS: List[str] = ["mp4", "avi", "mov", "webm"]
    
    # Model Configuration
    VISION_MODEL_CACHE_DIR: str = "/tmp/vision_models"
    GPU_ACCELERATION: bool = True
    BATCH_PROCESSING: bool = True
    MODEL_PARALLEL_PROCESSING: bool = False
    
    # Image Classification Models
    GENERAL_CLASSIFIER: str = "google/vit-base-patch16-224"
    CONTENT_CLASSIFIER: str = "google/vit-base-patch16-224-in21k"
    SCENE_CLASSIFIER: str = "microsoft/resnet-50"
    QUALITY_ASSESSOR: str = "google/vit-base-patch16-224"
    
    # Object Detection Models
    OBJECT_DETECTOR: str = "facebook/detr-resnet-50"
    FACE_DETECTOR: str = "opencv-haar-cascade"
    BRAND_DETECTOR: str = "ultralytics/yolov8n"
    LOGO_DETECTOR: str = "facebook/detr-resnet-50"
    
    # Image Similarity and Fingerprinting
    IMAGE_SIMILARITY_MODEL: str = "openai/clip-vit-base-patch32"
    IMAGE_EMBEDDING_MODEL: str = "sentence-transformers/clip-ViT-B-32"
    PERCEPTUAL_HASH_SIZE: int = 8
    FINGERPRINT_DIMENSION: int = 512
    
    # Video Analysis Models
    VIDEO_CLASSIFIER: str = "microsoft/videomae-base"
    MOTION_DETECTOR: str = "opencv-optical-flow"
    VIDEO_EMBEDDING_MODEL: str = "facebook/timesformer-base-finetuned-k400"
    
    # Content Moderation Models
    NSFW_DETECTOR: str = "Falconsai/nsfw_image_detection"
    VIOLENCE_DETECTOR: str = "facebook/detr-resnet-50"
    INAPPROPRIATE_CONTENT: str = "microsoft/resnet-50"
    
    # Text Extraction (OCR)
    OCR_MODEL: str = "microsoft/trocr-base-printed"
    TEXT_DETECTION_MODEL: str = "east-text-detector"
    HANDWRITING_RECOGNITION: str = "microsoft/trocr-base-handwritten"
    
    # Image Enhancement
    UPSCALING_MODEL: str = "Real-ESRGAN"
    DENOISING_MODEL: str = "DnCNN"
    COLOR_ENHANCEMENT: str = "adobe-enhance"
    
    # Processing Parameters
    IMAGE_RESIZE_QUALITY: int = 95
    VIDEO_FRAME_RATE: int = 30
    THUMBNAIL_SIZE: Tuple[int, int] = (150, 150)
    PREVIEW_SIZE: Tuple[int, int] = (512, 512)
    
    # Performance Thresholds
    SIMILARITY_THRESHOLD: float = 0.85
    CONFIDENCE_THRESHOLD: float = 0.8
    QUALITY_SCORE_MIN: float = 0.7
    DUPLICATE_THRESHOLD: float = 0.95
    
    # Video Processing
    VIDEO_CHUNK_DURATION: int = 10  # seconds
    KEYFRAME_EXTRACTION_INTERVAL: int = 1  # seconds
    MAX_VIDEO_DURATION: int = 600  # seconds
    VIDEO_RESOLUTION_LIMIT: Tuple[int, int] = (1920, 1080)
    
    # Batch Processing
    VISION_BATCH_SIZE: int = 16
    MAX_CONCURRENT_JOBS: int = 4
    PROCESSING_TIMEOUT: int = 300  # seconds
    
    class Config:
        env_prefix = "VISION_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("VISION_MODEL_CACHE_DIR")
    def create_cache_dir(cls, v):
        """Ensure vision model cache directory exists."""
        os.makedirs(v, exist_ok=True)
        os.makedirs(f"{v}/classification", exist_ok=True)
        os.makedirs(f"{v}/detection", exist_ok=True)
        os.makedirs(f"{v}/similarity", exist_ok=True)
        os.makedirs(f"{v}/video", exist_ok=True)
        return v
    
    def get_vision_model_spec(self, task: VisionTask) -> VisionModelSpec:
        """Get computer vision model specification by task."""
        specs = {
            VisionTask.IMAGE_CLASSIFICATION: VisionModelSpec(
                task=VisionTask.IMAGE_CLASSIFICATION,
                model_name="general_classifier",
                model_path=self.GENERAL_CLASSIFIER,
                input_size=(224, 224, 3),
                output_classes=1000,
                batch_size=32,
                requires_gpu=True,
                memory_requirement_mb=1024,
                inference_time_ms=50,
                accuracy_score=0.91,
                preprocessing_required=True,
                custom_params={
                    "normalize": True,
                    "resize_mode": "center_crop",
                    "interpolation": "bilinear"
                }
            ),
            
            VisionTask.OBJECT_DETECTION: VisionModelSpec(
                task=VisionTask.OBJECT_DETECTION,
                model_name="object_detector",
                model_path=self.OBJECT_DETECTOR,
                input_size=(800, 800, 3),
                output_classes=91,  # COCO classes
                batch_size=8,
                requires_gpu=True,
                memory_requirement_mb=2048,
                inference_time_ms=150,
                accuracy_score=0.88,
                preprocessing_required=True,
                postprocessing_required=True,
                custom_params={
                    "confidence_threshold": self.CONFIDENCE_THRESHOLD,
                    "nms_threshold": 0.5,
                    "max_detections": 100
                }
            ),
            
            VisionTask.FACE_DETECTION: VisionModelSpec(
                task=VisionTask.FACE_DETECTION,
                model_name="face_detector",
                model_path=self.FACE_DETECTOR,
                input_size=(640, 640, 3),
                batch_size=16,
                requires_gpu=False,
                memory_requirement_mb=512,
                inference_time_ms=80,
                accuracy_score=0.95,
                preprocessing_required=True,
                custom_params={
                    "min_face_size": 20,
                    "scale_factor": 1.1,
                    "min_neighbors": 3
                }
            ),
            
            VisionTask.IMAGE_SIMILARITY: VisionModelSpec(
                task=VisionTask.IMAGE_SIMILARITY,
                model_name="image_similarity",
                model_path=self.IMAGE_SIMILARITY_MODEL,
                input_size=(224, 224, 3),
                batch_size=64,
                requires_gpu=True,
                memory_requirement_mb=1536,
                inference_time_ms=60,
                accuracy_score=0.89,
                preprocessing_required=True,
                supports_streaming=True,
                custom_params={
                    "embedding_dim": self.FINGERPRINT_DIMENSION,
                    "normalize_embeddings": True,
                    "similarity_metric": "cosine"
                }
            ),
            
            VisionTask.CONTENT_MODERATION: VisionModelSpec(
                task=VisionTask.CONTENT_MODERATION,
                model_name="nsfw_detector",
                model_path=self.NSFW_DETECTOR,
                input_size=(224, 224, 3),
                output_classes=6,  # Safe, Suggestive, etc.
                batch_size=16,
                requires_gpu=True,
                memory_requirement_mb=768,
                inference_time_ms=70,
                accuracy_score=0.92,
                preprocessing_required=True,
                custom_params={
                    "categories": ["safe", "suggestive", "explicit", "violence", "disturbing"],
                    "threshold": 0.8
                }
            ),
            
            VisionTask.BRAND_DETECTION: VisionModelSpec(
                task=VisionTask.BRAND_DETECTION,
                model_name="brand_detector",
                model_path=self.BRAND_DETECTOR,
                input_size=(640, 640, 3),
                batch_size=8,
                requires_gpu=True,
                memory_requirement_mb=1536,
                inference_time_ms=200,
                accuracy_score=0.85,
                preprocessing_required=True,
                postprocessing_required=True,
                custom_params={
                    "known_brands": 1000,
                    "logo_database": "proprietary",
                    "confidence_threshold": 0.7
                }
            ),
            
            VisionTask.TEXT_EXTRACTION: VisionModelSpec(
                task=VisionTask.TEXT_EXTRACTION,
                model_name="ocr_model",
                model_path=self.OCR_MODEL,
                input_size=(224, 224, 3),
                batch_size=8,
                requires_gpu=True,
                memory_requirement_mb=1024,
                inference_time_ms=250,
                accuracy_score=0.87,
                preprocessing_required=True,
                postprocessing_required=True,
                custom_params={
                    "languages": ["en", "fr", "de", "es"],
                    "text_detection": True,
                    "confidence_threshold": 0.8
                }
            ),
            
            VisionTask.VIDEO_ANALYSIS: VisionModelSpec(
                task=VisionTask.VIDEO_ANALYSIS,
                model_name="video_classifier",
                model_path=self.VIDEO_CLASSIFIER,
                input_size=(224, 224, 3),
                output_classes=400,  # Kinetics-400
                batch_size=4,
                requires_gpu=True,
                memory_requirement_mb=4096,
                inference_time_ms=500,
                accuracy_score=0.83,
                preprocessing_required=True,
                custom_params={
                    "num_frames": 16,
                    "sampling_rate": 4,
                    "temporal_modeling": True
                }
            ),
            
            VisionTask.QUALITY_ASSESSMENT: VisionModelSpec(
                task=VisionTask.QUALITY_ASSESSMENT,
                model_name="quality_assessor",
                model_path=self.QUALITY_ASSESSOR,
                input_size=(224, 224, 3),
                batch_size=32,
                requires_gpu=False,
                memory_requirement_mb=512,
                inference_time_ms=40,
                accuracy_score=0.86,
                preprocessing_required=True,
                custom_params={
                    "metrics": ["sharpness", "brightness", "contrast", "noise"],
                    "overall_score": True,
                    "min_quality": self.QUALITY_SCORE_MIN
                }
            ),
        }
        
        return specs.get(task, self._get_default_vision_spec(task))
    
    def _get_default_vision_spec(self, task: VisionTask) -> VisionModelSpec:
        """Get default vision model specification."""
        return VisionModelSpec(
            task=task,
            model_name="default_vision",
            model_path=self.GENERAL_CLASSIFIER,
            input_size=(224, 224, 3),
            batch_size=self.VISION_BATCH_SIZE,
        )
    
    def get_image_processing_config(self) -> Dict[str, Any]:
        """Get image processing configuration."""
        return {
            "supported_formats": self.SUPPORTED_IMAGE_FORMATS,
            "max_size_mb": self.MAX_IMAGE_SIZE_MB,
            "default_input_size": self.DEFAULT_INPUT_SIZE,
            "resize_quality": self.IMAGE_RESIZE_QUALITY,
            "thumbnail_size": self.THUMBNAIL_SIZE,
            "preview_size": self.PREVIEW_SIZE,
            "preprocessing": {
                "normalize": True,
                "center_crop": True,
                "resize_mode": "bilinear",
                "color_space": "RGB"
            },
            "quality_assessment": {
                "enabled": True,
                "min_score": self.QUALITY_SCORE_MIN,
                "metrics": ["sharpness", "brightness", "contrast"]
            }
        }
    
    def get_video_processing_config(self) -> Dict[str, Any]:
        """Get video processing configuration."""
        return {
            "supported_formats": self.SUPPORTED_VIDEO_FORMATS,
            "max_size_mb": self.MAX_VIDEO_SIZE_MB,
            "max_duration": self.MAX_VIDEO_DURATION,
            "resolution_limit": self.VIDEO_RESOLUTION_LIMIT,
            "frame_rate": self.VIDEO_FRAME_RATE,
            "chunk_duration": self.VIDEO_CHUNK_DURATION,
            "keyframe_interval": self.KEYFRAME_EXTRACTION_INTERVAL,
            "processing": {
                "extract_frames": True,
                "motion_detection": True,
                "scene_detection": True,
                "audio_extraction": False
            }
        }
    
    def get_fingerprinting_config(self) -> Dict[str, Any]:
        """Get image fingerprinting configuration."""
        return {
            "similarity_threshold": self.SIMILARITY_THRESHOLD,
            "duplicate_threshold": self.DUPLICATE_THRESHOLD,
            "fingerprint_dimension": self.FINGERPRINT_DIMENSION,
            "perceptual_hash_size": self.PERCEPTUAL_HASH_SIZE,
            "algorithms": {
                "clip_embedding": {
                    "model": self.IMAGE_SIMILARITY_MODEL,
                    "dimension": self.FINGERPRINT_DIMENSION,
                    "normalize": True
                },
                "perceptual_hash": {
                    "hash_size": self.PERCEPTUAL_HASH_SIZE,
                    "highfreq_factor": 4
                },
                "difference_hash": {
                    "hash_size": self.PERCEPTUAL_HASH_SIZE
                }
            }
        }
    
    def get_content_moderation_config(self) -> Dict[str, Any]:
        """Get content moderation configuration."""
        return {
            "nsfw_detection": {
                "enabled": True,
                "model": self.NSFW_DETECTOR,
                "threshold": 0.8,
                "categories": ["safe", "suggestive", "explicit"]
            },
            "violence_detection": {
                "enabled": True,
                "model": self.VIOLENCE_DETECTOR,
                "threshold": 0.7
            },
            "inappropriate_content": {
                "enabled": True,
                "model": self.INAPPROPRIATE_CONTENT,
                "threshold": 0.75
            },
            "auto_blur": True,
            "auto_flag": True,
            "human_review_required": True
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get vision processing performance configuration."""
        return {
            "gpu_acceleration": self.GPU_ACCELERATION,
            "batch_processing": self.BATCH_PROCESSING,
            "batch_size": self.VISION_BATCH_SIZE,
            "max_concurrent_jobs": self.MAX_CONCURRENT_JOBS,
            "processing_timeout": self.PROCESSING_TIMEOUT,
            "model_parallel": self.MODEL_PARALLEL_PROCESSING,
            "memory_optimization": True,
            "inference_optimization": True,
            "cache_enabled": True
        }
    
    def get_supported_tasks(self) -> List[VisionTask]:
        """Get list of all supported vision tasks."""
        return [task for task in VisionTask]
    
    def get_models_by_gpu_requirement(self, gpu_available: bool) -> List[VisionModelSpec]:
        """
Get models based on GPU availability."""
        all_tasks = self.get_supported_tasks()
        models = []
        
        for task in all_tasks:
            spec = self.get_vision_model_spec(task)
            if gpu_available or not spec.requires_gpu:
                models.append(spec)
        
        return models
    
    def estimate_processing_time(self, task: VisionTask, num_items: int) -> float:
        """
Estimate processing time in seconds for a batch of items."""
        spec = self.get_vision_model_spec(task)
        batches = (num_items + spec.batch_size - 1) // spec.batch_size
        return batches * (spec.inference_time_ms / 1000.0)


# Global computer vision configuration instance
computer_vision_config = ComputerVisionConfig()
