"""Content Processing Pipeline

Ultra-advanced content processing pipeline for multi-format content creators.
Handles audio, video, image, and text content with AI-powered optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Content Upload → Format Detection → Quality Analysis → AI Enhancement → Optimization → Validation
"""
import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import tempfile
import shutil

logger = logging.getLogger(__name__)


class ContentPipelineStage(Enum):
    """Content processing pipeline stages"""    UPLOAD_VALIDATION = "upload_validation"
    FORMAT_DETECTION = "format_detection"
    CONTENT_ANALYSIS = "content_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    AI_ENHANCEMENT = "ai_enhancement"
    FORMAT_CONVERSION = "format_conversion"
    OPTIMIZATION = "optimization"
    METADATA_EXTRACTION = "metadata_extraction"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    PREVIEW_GENERATION = "preview_generation"
    STORAGE_PREPARATION = "storage_preparation"
    FINAL_VALIDATION = "final_validation"


class ContentType(Enum):
    """Supported content types"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMODAL = "multimodal"


class ProcessingQuality(Enum):
    """Processing quality levels"""    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class ContentMetrics:
    """Content processing metrics"""    file_size: int = 0
    duration: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    bitrate: Optional[int] = None
    frame_rate: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    quality_score: float = 0.0
    compression_ratio: float = 0.0
    processing_time: float = 0.0


@dataclass
class ProcessingResult:
    """Content processing result"""    success: bool = False
    content_id: str = ""
    original_path: Optional[str] = None
    processed_path: Optional[str] = None
    content_type: Optional[ContentType] = None
    metrics: ContentMetrics = field(default_factory=ContentMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    thumbnails: List[str] = field(default_factory=list)
    previews: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_stages: List[str] = field(default_factory=list)
    quality_gates_passed: List[str] = field(default_factory=list)
    optimization_applied: Dict[str, Any] = field(default_factory=dict)
    ai_enhancements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGate:
    """Quality gate definition"""    name: str
    validator: Callable
    threshold: float = 0.8
    required: bool = True
    error_message: str = ""


@dataclass
class ValidationGate:
    """Validation gate definition"""    name: str
    validator: Callable
    required: bool = True
    error_message: str = ""


@dataclass
class OptimizationGate:
    """Optimization gate definition"""    name: str
    optimizer: Callable
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)


class ContentProcessor:
    """Individual content processor"""    
    def __init__(self, processor_type: str, config: Dict[str, Any]):
        self.processor_type = processor_type
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{processor_type}")
    
    async def process(self, content_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process content"""        self.logger.info(f"Processing {self.processor_type}: {content_path}")
        
        # Simulate processing based on type
        await asyncio.sleep(0.1)
        
        return {
            "processor": self.processor_type,
            "status": "completed",
            "output_path": content_path,
            "processing_time": 0.1,
            "quality_score": 0.9
        }


class ContentProcessingPipeline:
    """    Ultra-advanced content processing pipeline for multi-format content.
    
    Features:
    - Multi-format content support (audio, video, image, text)
    - AI-powered content enhancement
    - Quality gates and validation
    - Format conversion and optimization
    - Thumbnail and preview generation
    - Metadata extraction and enrichment
    - Performance monitoring and optimization
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Processing components
        self.content_processors: Dict[ContentType, List[ContentProcessor]] = {}
        self.stage_processors: Dict[ContentPipelineStage, Callable] = {}
        
        # Quality control
        self.quality_gates: List[QualityGate] = []
        self.validation_gates: List[ValidationGate] = []
        self.optimization_gates: List[OptimizationGate] = []
        
        # Processing state
        self.active_processes: Dict[str, ProcessingResult] = {}
        self.completed_processes: Dict[str, ProcessingResult] = {}
        
        # Performance monitoring
        self.processing_metrics: Dict[str, Any] = {}
        
        # Initialize components
        self._initialize_processors()
        self._initialize_stage_processors()
        self._initialize_quality_gates()
        self._initialize_validation_gates()
        self._initialize_optimization_gates()
        
        self.logger.info("Content Processing Pipeline initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""        return {
            "max_file_size": 500 * 1024 * 1024,  # 500MB
            "supported_formats": {
                "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
                "video": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
                "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
                "text": [".txt", ".md", ".doc", ".docx", ".pdf"]
            },
            "quality_thresholds": {
                "min_audio_quality": 0.7,
                "min_video_quality": 0.8,
                "min_image_quality": 0.85,
                "min_text_quality": 0.9
            },
            "optimization_settings": {
                "enable_ai_enhancement": True,
                "enable_format_conversion": True,
                "enable_compression": True,
                "target_quality": ProcessingQuality.HIGH
            },
            "output_settings": {
                "generate_thumbnails": True,
                "generate_previews": True,
                "extract_metadata": True,
                "create_variants": True
            },
            "processing_timeout": 300,
            "parallel_processing": True,
            "cache_enabled": True,
            "temp_directory": "/tmp/content_processing"
        }
    
    def _initialize_processors(self):
        """Initialize content processors"""        # Audio processors
        self.content_processors[ContentType.AUDIO] = [
            ContentProcessor("audio_analyzer", self.config),
            ContentProcessor("audio_enhancer", self.config),
            ContentProcessor("audio_normalizer", self.config),
            ContentProcessor("audio_compressor", self.config)
        ]
        
        # Video processors
        self.content_processors[ContentType.VIDEO] = [
            ContentProcessor("video_analyzer", self.config),
            ContentProcessor("video_enhancer", self.config),
            ContentProcessor("video_stabilizer", self.config),
            ContentProcessor("video_encoder", self.config)
        ]
        
        # Image processors
        self.content_processors[ContentType.IMAGE] = [
            ContentProcessor("image_analyzer", self.config),
            ContentProcessor("image_enhancer", self.config),
            ContentProcessor("image_optimizer", self.config),
            ContentProcessor("image_converter", self.config)
        ]
        
        # Text processors
        self.content_processors[ContentType.TEXT] = [
            ContentProcessor("text_analyzer", self.config),
            ContentProcessor("text_enhancer", self.config),
            ContentProcessor("text_formatter", self.config),
            ContentProcessor("text_optimizer", self.config)
        ]
    
    def _initialize_stage_processors(self):
        """Initialize stage processors"""        self.stage_processors = {
            ContentPipelineStage.UPLOAD_VALIDATION: self._process_upload_validation,
            ContentPipelineStage.FORMAT_DETECTION: self._process_format_detection,
            ContentPipelineStage.CONTENT_ANALYSIS: self._process_content_analysis,
            ContentPipelineStage.QUALITY_ASSESSMENT: self._process_quality_assessment,
            ContentPipelineStage.AI_ENHANCEMENT: self._process_ai_enhancement,
            ContentPipelineStage.FORMAT_CONVERSION: self._process_format_conversion,
            ContentPipelineStage.OPTIMIZATION: self._process_optimization,
            ContentPipelineStage.METADATA_EXTRACTION: self._process_metadata_extraction,
            ContentPipelineStage.THUMBNAIL_GENERATION: self._process_thumbnail_generation,
            ContentPipelineStage.PREVIEW_GENERATION: self._process_preview_generation,
            ContentPipelineStage.STORAGE_PREPARATION: self._process_storage_preparation,
            ContentPipelineStage.FINAL_VALIDATION: self._process_final_validation
        }
    
    def _initialize_quality_gates(self):
        """Initialize quality gates"""        self.quality_gates = [
            QualityGate(
                name="file_size_check",
                validator=self._validate_file_size,
                threshold=1.0,
                required=True,
                error_message="File size exceeds maximum allowed size"
            ),
            QualityGate(
                name="format_support_check",
                validator=self._validate_format_support,
                threshold=1.0,
                required=True,
                error_message="File format not supported"
            ),
            QualityGate(
                name="content_quality_check",
                validator=self._validate_content_quality,
                threshold=0.7,
                required=True,
                error_message="Content quality below minimum threshold"
            ),
            QualityGate(
                name="ai_enhancement_check",
                validator=self._validate_ai_enhancement,
                threshold=0.8,
                required=False,
                error_message="AI enhancement failed quality check"
            )
        ]
    
    def _initialize_validation_gates(self):
        """Initialize validation gates"""        self.validation_gates = [
            ValidationGate(
                name="virus_scan",
                validator=self._validate_virus_scan,
                required=True,
                error_message="Content failed virus scan"
            ),
            ValidationGate(
                name="copyright_check",
                validator=self._validate_copyright,
                required=True,
                error_message="Content failed copyright check"
            ),
            ValidationGate(
                name="content_policy_check",
                validator=self._validate_content_policy,
                required=True,
                error_message="Content violates content policy"
            )
        ]
    
    def _initialize_optimization_gates(self):
        """Initialize optimization gates"""        self.optimization_gates = [
            OptimizationGate(
                name="compression_optimization",
                optimizer=self._optimize_compression,
                enabled=True,
                parameters={"target_size_reduction": 0.3}
            ),
            OptimizationGate(
                name="quality_optimization",
                optimizer=self._optimize_quality,
                enabled=True,
                parameters={"target_quality": 0.9}
            ),
            OptimizationGate(
                name="performance_optimization",
                optimizer=self._optimize_performance,
                enabled=True,
                parameters={"target_load_time": 2.0}
            )
        ]
    
    async def process_content(
        self,
        content_path: str,
        content_type: Optional[ContentType] = None,
        processing_quality: ProcessingQuality = ProcessingQuality.HIGH,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """        Process content through the complete pipeline
        
        Args:
            content_path: Path to content file
            content_type: Type of content (auto-detected if None)
            processing_quality: Quality level for processing
            parameters: Additional processing parameters
            
        Returns:
            ProcessingResult with complete processing information
        """        start_time = time.time()
        content_id = hashlib.md5(f"{content_path}_{start_time}".encode()).hexdigest()
        
        # Initialize result
        result = ProcessingResult(
            content_id=content_id,
            original_path=content_path,
            content_type=content_type
        )
        
        try:
            self.logger.info(f"Starting content processing: {content_id}")
            self.active_processes[content_id] = result
            
            # Process through all stages
            stages = list(ContentPipelineStage)
            
            for stage in stages:
                stage_start_time = time.time()
                
                self.logger.info(f"Processing stage: {stage.value}")
                result.processing_stages.append(stage.value)
                
                # Execute stage
                stage_processor = self.stage_processors.get(stage)
                if stage_processor:
                    await stage_processor(result, parameters or {})
                
                # Record stage execution time
                stage_time = time.time() - stage_start_time
                self.logger.info(f"Stage {stage.value} completed in {stage_time:.2f}s")
                
                # Check if processing should continue
                if result.errors and any("critical" in error.lower() for error in result.errors):
                    break
            
            # Finalize processing
            result.success = len(result.errors) == 0
            result.metrics.processing_time = time.time() - start_time
            
            # Move to completed processes
            self.completed_processes[content_id] = result
            if content_id in self.active_processes:
                del self.active_processes[content_id]
            
            self.logger.info(f"Content processing completed: {content_id} (success: {result.success})")
            return result
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Processing failed: {str(e)}")
            result.metrics.processing_time = time.time() - start_time
            
            self.logger.error(f"Content processing failed: {content_id} - {e}")
            return result
    
    # Stage Processing Methods
    async def _process_upload_validation(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process upload validation stage"""        self.logger.info("Processing upload validation")
        
        # Run validation gates
        for gate in self.validation_gates:
            if gate.required:
                validation_result = await gate.validator(result.original_path, parameters)
                if not validation_result:
                    result.errors.append(gate.error_message)
                    return
        
        result.metadata["upload_validated"] = True
    
    async def _process_format_detection(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process format detection stage"""        self.logger.info("Processing format detection")
        
        if not result.content_type:
            # Auto-detect content type
            file_extension = Path(result.original_path).suffix.lower()
            
            for content_type, extensions in self.config["supported_formats"].items():
                if file_extension in extensions:
                    result.content_type = ContentType(content_type)
                    break
            
            if not result.content_type:
                result.errors.append(f"Unknown file format: {file_extension}")
                return
        
        result.metadata["detected_format"] = result.content_type.value
        result.metadata["file_extension"] = Path(result.original_path).suffix
    
    async def _process_content_analysis(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process content analysis stage"""        self.logger.info("Processing content analysis")
        
        # Get appropriate processors for content type
        processors = self.content_processors.get(result.content_type, [])
        
        # Run analysis processor
        if processors:
            analyzer = processors[0]  # First processor is typically the analyzer
            analysis_result = await analyzer.process(result.original_path, parameters)
            result.metadata["content_analysis"] = analysis_result
        
        # Update metrics with analysis results
        result.metrics.file_size = Path(result.original_path).stat().st_size
        result.metadata["analysis_completed"] = True
    
    async def _process_quality_assessment(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process quality assessment stage"""        self.logger.info("Processing quality assessment")
        
        # Run quality gates
        quality_scores = []
        
        for gate in self.quality_gates:
            quality_score = await gate.validator(result.original_path, parameters)
            quality_scores.append(quality_score)
            
            if gate.required and quality_score < gate.threshold:
                result.errors.append(gate.error_message)
            else:
                result.quality_gates_passed.append(gate.name)
        
        # Calculate overall quality score
        if quality_scores:
            result.metrics.quality_score = sum(quality_scores) / len(quality_scores)
        
        result.metadata["quality_assessment_completed"] = True
    
    async def _process_ai_enhancement(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process AI enhancement stage"""        self.logger.info("Processing AI enhancement")
        
        if not self.config["optimization_settings"]["enable_ai_enhancement"]:
            result.warnings.append("AI enhancement disabled")
            return
        
        # Get enhancement processor for content type
        processors = self.content_processors.get(result.content_type, [])
        enhancer = next((p for p in processors if "enhancer" in p.processor_type), None)
        
        if enhancer:
            enhancement_result = await enhancer.process(result.original_path, parameters)
            result.ai_enhancements = enhancement_result
            
            # Update quality score if enhancement improved it
            if enhancement_result.get("quality_improvement", 0) > 0:
                result.metrics.quality_score += enhancement_result["quality_improvement"]
                result.metrics.quality_score = min(result.metrics.quality_score, 1.0)
        
        result.metadata["ai_enhancement_completed"] = True
    
    async def _process_format_conversion(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process format conversion stage"""        self.logger.info("Processing format conversion")
        
        if not self.config["optimization_settings"]["enable_format_conversion"]:
            result.warnings.append("Format conversion disabled")
            return
        
        # Check if conversion is needed
        target_format = parameters.get("target_format")
        if target_format and target_format != result.metadata.get("file_extension"):
            # Simulate format conversion
            converted_path = result.original_path.replace(
                result.metadata["file_extension"], 
                target_format
            )
            result.processed_path = converted_path
            result.metadata["format_converted"] = True
            result.metadata["target_format"] = target_format
        else:
            result.processed_path = result.original_path
        
        result.metadata["format_conversion_completed"] = True
    
    async def _process_optimization(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process optimization stage"""        self.logger.info("Processing optimization")
        
        # Run optimization gates
        for gate in self.optimization_gates:
            if gate.enabled:
                optimization_result = await gate.optimizer(
                    result.processed_path or result.original_path, 
                    gate.parameters
                )
                result.optimization_applied[gate.name] = optimization_result
        
        result.metadata["optimization_completed"] = True
    
    async def _process_metadata_extraction(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process metadata extraction stage"""        self.logger.info("Processing metadata extraction")
        
        if not self.config["output_settings"]["extract_metadata"]:
            result.warnings.append("Metadata extraction disabled")
            return
        
        # Extract metadata based on content type
        metadata = {
            "extracted_at": datetime.now().isoformat(),
            "content_type": result.content_type.value,
            "file_size": result.metrics.file_size,
            "processing_quality": parameters.get("processing_quality", "high")
        }
        
        # Add content-specific metadata
        if result.content_type == ContentType.AUDIO:
            metadata.update({
                "duration": 180.0,  # Simulated
                "sample_rate": 44100,
                "channels": 2,
                "bitrate": 320
            })
        elif result.content_type == ContentType.VIDEO:
            metadata.update({
                "duration": 120.0,  # Simulated
                "resolution": [1920, 1080],
                "frame_rate": 30.0,
                "bitrate": 5000
            })
        elif result.content_type == ContentType.IMAGE:
            metadata.update({
                "resolution": [1920, 1080],
                "color_depth": 24,
                "dpi": 300
            })
        
        result.metadata.update(metadata)
        result.metadata["metadata_extraction_completed"] = True
    
    async def _process_thumbnail_generation(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process thumbnail generation stage"""        self.logger.info("Processing thumbnail generation")
        
        if not self.config["output_settings"]["generate_thumbnails"]:
            result.warnings.append("Thumbnail generation disabled")
            return
        
        # Generate thumbnails based on content type
        if result.content_type in [ContentType.VIDEO, ContentType.IMAGE]:
            # Simulate thumbnail generation
            thumbnail_path = f"{result.processed_path or result.original_path}_thumb.jpg"
            result.thumbnails.append(thumbnail_path)
            
            # Generate multiple sizes
            for size in ["small", "medium", "large"]:
                thumb_path = f"{result.processed_path or result.original_path}_thumb_{size}.jpg"
                result.thumbnails.append(thumb_path)
        
        result.metadata["thumbnail_generation_completed"] = True
    
    async def _process_preview_generation(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process preview generation stage"""        self.logger.info("Processing preview generation")
        
        if not self.config["output_settings"]["generate_previews"]:
            result.warnings.append("Preview generation disabled")
            return
        
        # Generate previews based on content type
        if result.content_type == ContentType.VIDEO:
            preview_path = f"{result.processed_path or result.original_path}_preview.mp4"
            result.previews.append(preview_path)
        elif result.content_type == ContentType.AUDIO:
            preview_path = f"{result.processed_path or result.original_path}_preview.mp3"
            result.previews.append(preview_path)
        
        result.metadata["preview_generation_completed"] = True
    
    async def _process_storage_preparation(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process storage preparation stage"""        self.logger.info("Processing storage preparation")
        
        # Prepare for storage (organize files, create manifest, etc.)
        storage_manifest = {
            "content_id": result.content_id,
            "original_file": result.original_path,
            "processed_file": result.processed_path,
            "thumbnails": result.thumbnails,
            "previews": result.previews,
            "metadata": result.metadata,
            "quality_score": result.metrics.quality_score
        }
        
        result.metadata["storage_manifest"] = storage_manifest
        result.metadata["storage_preparation_completed"] = True
    
    async def _process_final_validation(self, result: ProcessingResult, parameters: Dict[str, Any]):
        """Process final validation stage"""        self.logger.info("Processing final validation")
        
        # Validate final result
        validation_checks = [
            result.processed_path or result.original_path,
            result.content_type is not None,
            result.metrics.quality_score >= self.config["quality_thresholds"].get(
                f"min_{result.content_type.value}_quality", 0.7
            )
        ]
        
        if all(validation_checks):
            result.metadata["final_validation_passed"] = True
        else:
            result.errors.append("Final validation failed")
        
        result.metadata["final_validation_completed"] = True
    
    # Validation Methods
    async def _validate_file_size(self, file_path: str, parameters: Dict[str, Any]) -> float:
        """Validate file size"""        try:
            file_size = Path(file_path).stat().st_size
            max_size = self.config["max_file_size"]
            return 1.0 if file_size <= max_size else 0.0
        except Exception:
            return 0.0
    
    async def _validate_format_support(self, file_path: str, parameters: Dict[str, Any]) -> float:
        """Validate format support"""        try:
            file_extension = Path(file_path).suffix.lower()
            all_formats = []
            for formats in self.config["supported_formats"].values():
                all_formats.extend(formats)
            return 1.0 if file_extension in all_formats else 0.0
        except Exception:
            return 0.0
    
    async def _validate_content_quality(self, file_path: str, parameters: Dict[str, Any]) -> float:
        """Validate content quality"""        # Simulate quality validation
        return 0.85  # Would implement actual quality analysis
    
    async def _validate_ai_enhancement(self, file_path: str, parameters: Dict[str, Any]) -> float:
        """Validate AI enhancement quality"""        # Simulate AI enhancement validation
        return 0.90  # Would implement actual AI quality assessment
    
    async def _validate_virus_scan(self, file_path: str, parameters: Dict[str, Any]) -> bool:
        """Validate virus scan"""        # Simulate virus scan
        return True  # Would implement actual virus scanning
    
    async def _validate_copyright(self, file_path: str, parameters: Dict[str, Any]) -> bool:
        """Validate copyright"""        # Simulate copyright check
        return True  # Would implement actual copyright verification
    
    async def _validate_content_policy(self, file_path: str, parameters: Dict[str, Any]) -> bool:
        """Validate content policy"""        # Simulate content policy check
        return True  # Would implement actual policy validation
    
    # Optimization Methods
    async def _optimize_compression(self, file_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize compression"""        target_reduction = parameters.get("target_size_reduction", 0.3)
        
        return {
            "compression_applied": True,
            "size_reduction": target_reduction,
            "quality_retained": 0.95,
            "algorithm": "advanced_compression_v3"
        }
    
    async def _optimize_quality(self, file_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize quality"""        target_quality = parameters.get("target_quality", 0.9)
        
        return {
            "quality_optimization_applied": True,
            "target_quality": target_quality,
            "achieved_quality": target_quality * 0.98,
            "enhancement_method": "ai_quality_boost_v2"
        }
    
    async def _optimize_performance(self, file_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize performance"""        target_load_time = parameters.get("target_load_time", 2.0)
        
        return {
            "performance_optimization_applied": True,
            "target_load_time": target_load_time,
            "achieved_load_time": target_load_time * 0.8,
            "optimization_techniques": ["lazy_loading", "progressive_enhancement", "caching"]
        }
    
    # Public API Methods
    def get_processing_status(self, content_id: str) -> Optional[ProcessingResult]:
        """Get processing status"""        return self.active_processes.get(content_id) or self.completed_processes.get(content_id)
    
    def get_active_processes(self) -> Dict[str, ProcessingResult]:
        """Get all active processes"""        return self.active_processes.copy()
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""        completed_processes = list(self.completed_processes.values())
        
        return {
            "active_processes": len(self.active_processes),
            "completed_processes": len(completed_processes),
            "success_rate": len([p for p in completed_processes if p.success]) / max(len(completed_processes), 1),
            "average_processing_time": sum(p.metrics.processing_time for p in completed_processes) / max(len(completed_processes), 1),
            "average_quality_score": sum(p.metrics.quality_score for p in completed_processes) / max(len(completed_processes), 1)
        }
    
    async def cancel_processing(self, content_id: str) -> bool:
        """Cancel content processing"""        if content_id in self.active_processes:
            result = self.active_processes[content_id]
            result.success = False
            result.errors.append("Processing cancelled")
            
            # Move to completed
            self.completed_processes[content_id] = result
            del self.active_processes[content_id]
            
            self.logger.info(f"Content processing cancelled: {content_id}")
            return True
        
        return False
