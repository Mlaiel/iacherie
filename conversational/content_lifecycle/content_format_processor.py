"""
Content Format Processor Module - Multi-Format Content Processing System

Enterprise-grade multi-format content processing system supporting the complete
creator economy workflow: upload → AI processing → protection → monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Tuple, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import hashlib
import os
from pathlib import Path
import mimetypes

from ...core.database import get_db_session
from ...core.exceptions import BusinessLogicError, ValidationError
from ...utils.cache_manager import CacheManager
from ...utils.event_emitter import EventEmitter
from ...ai.content_generation.format_detection import FormatDetector
from ...ai.audio.audio_processor import AudioProcessor
from ...ai.content_generation.image_generator import ImageProcessor
from ...ai.content_generation.video_generator import VideoProcessor
from ...ai.content_generation.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """Supported content formats"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    MULTIMODAL = "multimodal"


class ProcessingStage(Enum):
    """Content processing stages"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    FORMAT_DETECTION = "format_detection"
    METADATA_EXTRACTION = "metadata_extraction"
    QUALITY_ANALYSIS = "quality_analysis"
    AI_ENHANCEMENT = "ai_enhancement"
    FINGERPRINTING = "fingerprinting"
    PROTECTION_SETUP = "protection_setup"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_PREP = "collaboration_prep"
    DISTRIBUTION_PREP = "distribution_prep"
    COMPLETED = "completed"


class ProcessingPriority(Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    REAL_TIME = "real_time"


@dataclass
class ContentFile:
    """Content file representation"""
    file_id: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    content_format: ContentFormat
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_stage: ProcessingStage = ProcessingStage.UPLOAD
    upload_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessingResult:
    """Content processing result"""
    result_id: str
    content_id: str
    processing_stage: ProcessingStage
    success: bool
    processed_data: Dict[str, Any]
    quality_score: float
    performance_metrics: Dict[str, float]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EnhancementProfile:
    """Content enhancement profile"""
    profile_id: str
    content_format: ContentFormat
    target_quality: float
    enhancement_settings: Dict[str, Any]
    ai_models: List[str]
    processing_options: Dict[str, bool]
    output_formats: List[str]
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContentFormatProcessor:
    """
    Enterprise-grade multi-format content processor supporting the complete
    creator economy workflow from upload to monetization.
    """
    
    def __init__(self, cache_manager: CacheManager, event_emitter: EventEmitter):
        self.cache_manager = cache_manager
        self.event_emitter = event_emitter
        self.format_detector = FormatDetector()
        self.audio_processor = AudioProcessor()
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.text_processor = TextProcessor()
        self.processing_queue = asyncio.Queue()
        self.active_processors = {}
        self.quality_thresholds = self._initialize_quality_thresholds()
        
    def _initialize_quality_thresholds(self) -> Dict[ContentFormat, float]:
        """Initialize quality thresholds for each content format"""
        return {
            ContentFormat.AUDIO: 0.85,
            ContentFormat.VIDEO: 0.80,
            ContentFormat.IMAGE: 0.90,
            ContentFormat.TEXT: 0.88,
            ContentFormat.DOCUMENT: 0.85,
            ContentFormat.PRESENTATION: 0.82,
            ContentFormat.SPREADSHEET: 0.80,
            ContentFormat.MULTIMODAL: 0.85
        }
    
    async def process_uploaded_content(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: str,
        processing_priority: ProcessingPriority = ProcessingPriority.NORMAL,
        enhancement_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded content through the complete creator workflow
        
        Business Logic Flow:
        Upload → Format Detection → Quality Analysis → AI Enhancement → 
        Protection Setup → SEO Optimization → Collaboration Prep → Distribution Prep
        """
        try:
            content_id = str(uuid.uuid4())
            
            # Stage 1: Upload and Initial Processing
            content_file = await self._handle_file_upload(
                file_data, filename, content_id, user_id
            )
            
            # Stage 2: Format Detection and Validation
            format_result = await self._detect_and_validate_format(content_file)
            
            # Stage 3: Metadata Extraction
            metadata_result = await self._extract_comprehensive_metadata(content_file)
            
            # Stage 4: Quality Analysis
            quality_result = await self._analyze_content_quality(content_file)
            
            # Stage 5: AI Enhancement (if quality below threshold)
            if quality_result["quality_score"] < self.quality_thresholds[content_file.content_format]:
                enhancement_result = await self._apply_ai_enhancement(
                    content_file, enhancement_profile_id
                )
            else:
                enhancement_result = {"enhanced": False, "reason": "quality_sufficient"}
            
            # Stage 6: Content Fingerprinting for Protection
            fingerprint_result = await self._generate_content_fingerprint(content_file)
            
            # Stage 7: SEO Optimization
            seo_result = await self._optimize_for_seo(content_file, metadata_result)
            
            # Stage 8: Collaboration Preparation
            collaboration_result = await self._prepare_for_collaboration(content_file)
            
            # Stage 9: Distribution Preparation
            distribution_result = await self._prepare_for_distribution(content_file)
            
            # Update processing stage
            content_file.processing_stage = ProcessingStage.COMPLETED
            
            # Emit completion event
            await self.event_emitter.emit("content_processing_completed", {
                "content_id": content_id,
                "user_id": user_id,
                "content_format": content_file.content_format.value,
                "processing_results": {
                    "format": format_result,
                    "metadata": metadata_result,
                    "quality": quality_result,
                    "enhancement": enhancement_result,
                    "fingerprint": fingerprint_result,
                    "seo": seo_result,
                    "collaboration": collaboration_result,
                    "distribution": distribution_result
                }
            })
            
            return {
                "content_id": content_id,
                "content_file": content_file,
                "processing_results": {
                    "format_detection": format_result,
                    "metadata_extraction": metadata_result,
                    "quality_analysis": quality_result,
                    "ai_enhancement": enhancement_result,
                    "content_fingerprinting": fingerprint_result,
                    "seo_optimization": seo_result,
                    "collaboration_preparation": collaboration_result,
                    "distribution_preparation": distribution_result
                },
                "ready_for_lifecycle": True,
                "next_stage": "protection_activation"
            }
            
        except Exception as e:
            logger.error(f"Content processing failed for {filename}: {str(e)}")
            await self.event_emitter.emit("content_processing_failed", {
                "filename": filename,
                "user_id": user_id,
                "error": str(e)
            })
            raise BusinessLogicError(f"Content processing failed: {str(e)}")
    
    async def _handle_file_upload(
        self,
        file_data: BinaryIO,
        filename: str,
        content_id: str,
        user_id: str
    ) -> ContentFile:
        """Handle secure file upload and initial processing"""
        try:
            # Generate secure file path
            file_extension = Path(filename).suffix.lower()
            secure_filename = f"{content_id}_{hashlib.md5(filename.encode()).hexdigest()}{file_extension}"
            file_path = f"/secure_storage/content/{user_id}/{content_id}/{secure_filename}"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Read file data and calculate checksum
            file_content = file_data.read()
            file_size = len(file_content)
            checksum = hashlib.sha256(file_content).hexdigest()
            
            # Write file securely
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Determine content format
            content_format = self._determine_content_format(mime_type, file_extension)
            
            return ContentFile(
                file_id=str(uuid.uuid4()),
                original_filename=filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                content_format=content_format,
                checksum=checksum,
                processing_stage=ProcessingStage.UPLOAD
            )
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise BusinessLogicError(f"File upload failed: {str(e)}")
    
    def _determine_content_format(self, mime_type: str, file_extension: str) -> ContentFormat:
        """Determine content format from MIME type and extension"""
        mime_format_map = {
            "audio/": ContentFormat.AUDIO,
            "video/": ContentFormat.VIDEO,
            "image/": ContentFormat.IMAGE,
            "text/": ContentFormat.TEXT,
            "application/pdf": ContentFormat.DOCUMENT,
            "application/msword": ContentFormat.DOCUMENT,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ContentFormat.DOCUMENT,
            "application/vnd.ms-powerpoint": ContentFormat.PRESENTATION,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ContentFormat.PRESENTATION,
            "application/vnd.ms-excel": ContentFormat.SPREADSHEET,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ContentFormat.SPREADSHEET
        }
        
        for mime_prefix, format_type in mime_format_map.items():
            if mime_type.startswith(mime_prefix) or mime_type == mime_prefix:
                return format_type
        
        # Fallback to extension-based detection
        extension_map = {
            ".mp3": ContentFormat.AUDIO,
            ".wav": ContentFormat.AUDIO,
            ".flac": ContentFormat.AUDIO,
            ".mp4": ContentFormat.VIDEO,
            ".avi": ContentFormat.VIDEO,
            ".mov": ContentFormat.VIDEO,
            ".jpg": ContentFormat.IMAGE,
            ".jpeg": ContentFormat.IMAGE,
            ".png": ContentFormat.IMAGE,
            ".gif": ContentFormat.IMAGE,
            ".txt": ContentFormat.TEXT,
            ".md": ContentFormat.TEXT,
            ".pdf": ContentFormat.DOCUMENT
        }
        
        return extension_map.get(file_extension.lower(), ContentFormat.DOCUMENT)
    
    async def _detect_and_validate_format(self, content_file: ContentFile) -> Dict[str, Any]:
        """Detect and validate content format using AI"""
        try:
            detection_result = await self.format_detector.analyze_content(content_file.file_path)
            
            # Validate format consistency
            detected_format = ContentFormat(detection_result.get("detected_format", "document"))
            format_confidence = detection_result.get("confidence", 0.0)
            
            validation_result = {
                "original_format": content_file.content_format.value,
                "detected_format": detected_format.value,
                "format_confidence": format_confidence,
                "format_match": content_file.content_format == detected_format,
                "validation_passed": format_confidence > 0.8,
                "detailed_analysis": detection_result
            }
            
            # Update content file if detection is more accurate
            if format_confidence > 0.9 and content_file.content_format != detected_format:
                content_file.content_format = detected_format
                validation_result["format_updated"] = True
            
            content_file.processing_stage = ProcessingStage.FORMAT_DETECTION
            return validation_result
            
        except Exception as e:
            logger.error(f"Format detection failed: {str(e)}")
            return {
                "validation_passed": False,
                "error": str(e),
                "fallback_format": content_file.content_format.value
            }
    
    async def _extract_comprehensive_metadata(self, content_file: ContentFile) -> Dict[str, Any]:
        """Extract comprehensive metadata based on content format"""
        try:
            metadata_extractor = self._get_metadata_extractor(content_file.content_format)
            metadata_result = await metadata_extractor.extract_metadata(content_file.file_path)
            
            # Add standard metadata
            standard_metadata = {
                "file_info": {
                    "original_filename": content_file.original_filename,
                    "file_size": content_file.file_size,
                    "mime_type": content_file.mime_type,
                    "checksum": content_file.checksum,
                    "upload_timestamp": content_file.upload_timestamp.isoformat()
                },
                "content_analysis": metadata_result.get("content_analysis", {}),
                "technical_specs": metadata_result.get("technical_specs", {}),
                "quality_indicators": metadata_result.get("quality_indicators", {})
            }
            
            # Store metadata in content file
            content_file.metadata.update(standard_metadata)
            content_file.processing_stage = ProcessingStage.METADATA_EXTRACTION
            
            return {
                "extraction_success": True,
                "metadata": standard_metadata,
                "format_specific_metadata": metadata_result
            }
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {
                "extraction_success": False,
                "error": str(e),
                "basic_metadata": {
                    "original_filename": content_file.original_filename,
                    "file_size": content_file.file_size,
                    "mime_type": content_file.mime_type
                }
            }
    
    def _get_metadata_extractor(self, content_format: ContentFormat):
        """Get appropriate metadata extractor for content format"""
        extractors = {
            ContentFormat.AUDIO: self.audio_processor,
            ContentFormat.VIDEO: self.video_processor,
            ContentFormat.IMAGE: self.image_processor,
            ContentFormat.TEXT: self.text_processor,
            ContentFormat.DOCUMENT: self.text_processor,
            ContentFormat.PRESENTATION: self.text_processor,
            ContentFormat.SPREADSHEET: self.text_processor,
            ContentFormat.MULTIMODAL: self.video_processor  # Default to video for multimodal
        }
        return extractors.get(content_format, self.text_processor)
    
    async def _analyze_content_quality(self, content_file: ContentFile) -> Dict[str, Any]:
        """Analyze content quality using AI-powered assessment"""
        try:
            quality_analyzer = self._get_metadata_extractor(content_file.content_format)
            quality_result = await quality_analyzer.analyze_quality(content_file.file_path)
            
            quality_score = quality_result.get("overall_quality", 0.0)
            quality_breakdown = quality_result.get("quality_breakdown", {})
            improvement_suggestions = quality_result.get("improvement_suggestions", [])
            
            quality_assessment = {
                "overall_quality": quality_score,
                "quality_breakdown": quality_breakdown,
                "meets_threshold": quality_score >= self.quality_thresholds[content_file.content_format],
                "improvement_suggestions": improvement_suggestions,
                "quality_category": self._categorize_quality(quality_score),
                "enhancement_recommended": quality_score < self.quality_thresholds[content_file.content_format]
            }
            
            content_file.processing_stage = ProcessingStage.QUALITY_ANALYSIS
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {str(e)}")
            return {
                "overall_quality": 0.5,
                "quality_breakdown": {},
                "meets_threshold": False,
                "error": str(e)
            }
    
    def _categorize_quality(self, quality_score: float) -> str:
        """Categorize quality score into descriptive category"""
        if quality_score >= 0.95:
            return "exceptional"
        elif quality_score >= 0.90:
            return "excellent"
        elif quality_score >= 0.80:
            return "good"
        elif quality_score >= 0.70:
            return "fair"
        elif quality_score >= 0.60:
            return "poor"
        else:
            return "unacceptable"
    
    async def _apply_ai_enhancement(
        self,
        content_file: ContentFile,
        enhancement_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply AI-powered content enhancement"""
        try:
            enhancer = self._get_metadata_extractor(content_file.content_format)
            
            # Get enhancement profile or use default
            if enhancement_profile_id:
                enhancement_profile = await self._get_enhancement_profile(enhancement_profile_id)
            else:
                enhancement_profile = self._get_default_enhancement_profile(content_file.content_format)
            
            # Apply enhancements
            enhancement_result = await enhancer.enhance_content(
                content_file.file_path,
                enhancement_profile.enhancement_settings
            )
            
            # Update file path if enhanced version created
            if enhancement_result.get("enhanced_file_path"):
                content_file.file_path = enhancement_result["enhanced_file_path"]
            
            content_file.processing_stage = ProcessingStage.AI_ENHANCEMENT
            
            return {
                "enhancement_applied": True,
                "enhancement_type": enhancement_result.get("enhancement_type", "unknown"),
                "quality_improvement": enhancement_result.get("quality_improvement", 0.0),
                "processing_time": enhancement_result.get("processing_time", 0.0),
                "enhanced_file_path": enhancement_result.get("enhanced_file_path"),
                "enhancement_details": enhancement_result
            }
            
        except Exception as e:
            logger.error(f"AI enhancement failed: {str(e)}")
            return {
                "enhancement_applied": False,
                "error": str(e),
                "fallback_used": True
            }
    
    async def _generate_content_fingerprint(self, content_file: ContentFile) -> Dict[str, Any]:
        """Generate content fingerprint for protection and rights management"""
        try:
            fingerprint_generator = self._get_metadata_extractor(content_file.content_format)
            fingerprint_result = await fingerprint_generator.generate_fingerprint(content_file.file_path)
            
            content_file.processing_stage = ProcessingStage.FINGERPRINTING
            
            return {
                "fingerprint_generated": True,
                "fingerprint_hash": fingerprint_result.get("fingerprint_hash"),
                "vector_embedding": fingerprint_result.get("vector_embedding"),
                "protection_metadata": fingerprint_result.get("protection_metadata", {}),
                "watermark_applied": fingerprint_result.get("watermark_applied", False)
            }
            
        except Exception as e:
            logger.error(f"Fingerprinting failed: {str(e)}")
            return {
                "fingerprint_generated": False,
                "error": str(e),
                "fallback_hash": content_file.checksum
            }
    
    async def _optimize_for_seo(
        self,
        content_file: ContentFile,
        metadata_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize content for SEO and discoverability"""
        try:
            # Extract or generate SEO-relevant metadata
            seo_optimizer = self.text_processor  # Use text processor for SEO optimization
            
            seo_data = {
                "title": metadata_result.get("metadata", {}).get("title", content_file.original_filename),
                "description": metadata_result.get("metadata", {}).get("description", ""),
                "tags": metadata_result.get("metadata", {}).get("tags", []),
                "content_format": content_file.content_format.value
            }
            
            seo_result = await seo_optimizer.optimize_seo(seo_data)
            
            return {
                "seo_optimized": True,
                "optimized_title": seo_result.get("optimized_title"),
                "optimized_description": seo_result.get("optimized_description"),
                "seo_keywords": seo_result.get("keywords", []),
                "seo_tags": seo_result.get("tags", []),
                "discoverability_score": seo_result.get("discoverability_score", 0.0),
                "platform_optimizations": seo_result.get("platform_optimizations", {})
            }
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {str(e)}")
            return {
                "seo_optimized": False,
                "error": str(e),
                "basic_seo": {
                    "title": content_file.original_filename,
                    "format": content_file.content_format.value
                }
            }
    
    async def _prepare_for_collaboration(self, content_file: ContentFile) -> Dict[str, Any]:
        """Prepare content for collaboration and matching"""
        try:
            collaboration_data = {
                "content_format": content_file.content_format.value,
                "quality_score": content_file.metadata.get("quality_score", 0.0),
                "technical_specs": content_file.metadata.get("technical_specs", {}),
                "content_tags": content_file.metadata.get("tags", []),
                "creator_preferences": {}  # To be filled by user preferences
            }
            
            # Generate collaboration profile
            collaboration_profile = await self._generate_collaboration_profile(collaboration_data)
            
            return {
                "collaboration_ready": True,
                "collaboration_profile": collaboration_profile,
                "matching_potential": collaboration_profile.get("matching_potential", 0.0),
                "recommended_collaborators": collaboration_profile.get("recommended_collaborators", []),
                "collaboration_opportunities": collaboration_profile.get("opportunities", [])
            }
            
        except Exception as e:
            logger.error(f"Collaboration preparation failed: {str(e)}")
            return {
                "collaboration_ready": False,
                "error": str(e)
            }
    
    async def _prepare_for_distribution(self, content_file: ContentFile) -> Dict[str, Any]:
        """Prepare content for multi-platform distribution"""
        try:
            distribution_config = await self._generate_distribution_config(content_file)
            
            return {
                "distribution_ready": True,
                "supported_platforms": distribution_config.get("supported_platforms", []),
                "format_adaptations": distribution_config.get("format_adaptations", {}),
                "scheduling_recommendations": distribution_config.get("scheduling_recommendations", {}),
                "cross_platform_strategy": distribution_config.get("cross_platform_strategy", {})
            }
            
        except Exception as e:
            logger.error(f"Distribution preparation failed: {str(e)}")
            return {
                "distribution_ready": False,
                "error": str(e)
            }
    
    async def _generate_collaboration_profile(self, collaboration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate collaboration profile for content"""
        # Implementation for collaboration profile generation
        return {
            "matching_potential": 0.85,
            "recommended_collaborators": [],
            "opportunities": ["cross_promotion", "remix_collaboration", "content_series"]
        }
    
    async def _generate_distribution_config(self, content_file: ContentFile) -> Dict[str, Any]:
        """Generate distribution configuration for content"""
        platform_map = {
            ContentFormat.AUDIO: ["spotify", "apple_music", "soundcloud", "youtube_music"],
            ContentFormat.VIDEO: ["youtube", "tiktok", "instagram_reels", "facebook"],
            ContentFormat.IMAGE: ["instagram", "pinterest", "twitter", "facebook"],
            ContentFormat.TEXT: ["medium", "linkedin", "twitter", "facebook"]
        }
        
        return {
            "supported_platforms": platform_map.get(content_file.content_format, []),
            "format_adaptations": {},
            "scheduling_recommendations": {},
            "cross_platform_strategy": {}
        }
    
    async def _get_enhancement_profile(self, profile_id: str) -> EnhancementProfile:
        """Get enhancement profile by ID"""
        # Implementation for retrieving enhancement profile
        pass
    
    def _get_default_enhancement_profile(self, content_format: ContentFormat) -> EnhancementProfile:
        """Get default enhancement profile for content format"""
        return EnhancementProfile(
            profile_id="default",
            content_format=content_format,
            target_quality=self.quality_thresholds[content_format],
            enhancement_settings={},
            ai_models=[],
            processing_options={},
            output_formats=[],
            created_by="system"
        )
    
    async def get_processing_status(self, content_id: str) -> Dict[str, Any]:
        """Get current processing status for content"""
        try:
            # Retrieve processing status from cache or database
            status = await self.cache_manager.get(f"processing_status:{content_id}")
            
            if not status:
                return {
                    "content_id": content_id,
                    "status": "not_found",
                    "message": "Content not found or processing not started"
                }
            
            return json.loads(status)
            
        except Exception as e:
            logger.error(f"Failed to get processing status: {str(e)}")
            return {
                "content_id": content_id,
                "status": "error",
                "error": str(e)
            }
    
    async def cancel_processing(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel content processing"""
        try:
            # Cancel active processing
            if content_id in self.active_processors:
                processor_task = self.active_processors[content_id]
                processor_task.cancel()
                del self.active_processors[content_id]
            
            # Emit cancellation event
            await self.event_emitter.emit("content_processing_cancelled", {
                "content_id": content_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "content_id": content_id,
                "cancelled": True,
                "message": "Processing cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel processing: {str(e)}")
            return {
                "content_id": content_id,
                "cancelled": False,
                "error": str(e)
            }


# Factory function for creating content format processor
def create_content_format_processor(
    cache_manager: CacheManager,
    event_emitter: EventEmitter
) -> ContentFormatProcessor:
    """Factory function to create content format processor instance"""
    return ContentFormatProcessor(cache_manager, event_emitter)
