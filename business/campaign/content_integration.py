"""Content Integration - Multi-Format Content Management and Processing
==================================================================

Advanced content integration system for managing multi-format content (audio, video, 
image, text) with AI processing, format conversion, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel is strictly
prohibited and may result in legal action.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO
from enum import Enum
from dataclasses import dataclass
import asyncio
import hashlib
import mimetypes
from pathlib import Path
import tempfile

from backend.core.logging import get_logger
from backend.ai.content.content_analyzer import ContentAnalyzer
from backend.ai.content.format_converter import FormatConverter
from backend.ai.content.content_optimizer import ContentOptimizer
from backend.ai.content.metadata_extractor import MetadataExtractor
from backend.business.protection.content_fingerprint import ContentFingerprint
from backend.utils.file_processor import FileProcessor
from backend.utils.cloud_storage import CloudStorageManager


class ContentType(str, Enum):
    """
Supported content types"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


class ContentFormat(str, Enum):
    """Supported content formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    MKV = "mkv"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    TIFF = "tiff"
    
    # Text formats
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ProcessingStatus(str, Enum):
    """Content processing status"""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    OPTIMIZED = "optimized"
    PROTECTED = "protected"
    READY = "ready"
    ERROR = "error"


@dataclass
class ContentMetadata:
    """Content metadata structure"""
    content_id: str
    original_filename: str
    content_type: ContentType
    content_format: ContentFormat
    file_size: int
    duration: Optional[float] = None
    dimensions: Optional[Dict[str, int]] = None
    quality_score: Optional[float] = None
    technical_metadata: Optional[Dict[str, Any]] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class ContentProcessingResult:
    """
Content processing result"""
    content_id: str
    status: ProcessingStatus
    processed_formats: List[ContentFormat]
    optimization_applied: bool
    protection_enabled: bool
    ai_analysis: Dict[str, Any]
    storage_urls: Dict[str, str]
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class ContentIntegrationConfig:
    """
Content integration configuration"""
    auto_optimization: bool = True
    auto_protection: bool = True
    generate_previews: bool = True
    extract_metadata: bool = True
    ai_analysis: bool = True
    format_conversion: bool = True
    quality_enhancement: bool = True
    watermark_protection: bool = False


class ContentIntegration:
    """
    Advanced Multi-Format Content Integration System
    
    Handles comprehensive content management including upload processing,
    format conversion, AI analysis, optimization, and protection for all
    supported content types.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.content_analyzer = ContentAnalyzer()
        self.format_converter = FormatConverter()
        self.content_optimizer = ContentOptimizer()
        self.metadata_extractor = MetadataExtractor()
        self.content_fingerprint = ContentFingerprint()
        self.file_processor = FileProcessor()
        self.cloud_storage = CloudStorageManager()
        
        self._processing_queue: Dict[str, Dict] = {}
        self._content_cache: Dict[str, Dict] = {}
        
        # Start background processing
        asyncio.create_task(self._content_processing_worker())
    
    async def upload_content(
        self,
        campaign_id: str,
        creator_id: str,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        content_type: Optional[ContentType] = None,
        config: Optional[ContentIntegrationConfig] = None
    ) -> Dict[str, Any]:
        """
        Upload and process content for campaign integration
        
        Args:
            campaign_id: Campaign unique identifier
            creator_id: Creator unique identifier
            file_data: File data (bytes or file-like object)
            filename: Original filename
            content_type: Optional content type override
            config: Processing configuration
            
        Returns:
            Upload and processing status
        """
        try:
            config = config or ContentIntegrationConfig()
            content_id = await self._generate_content_id(filename, creator_id)
            
            # Detect content type and format
            detected_type, detected_format = await self._detect_content_type_and_format(
                file_data, filename
            )
            final_content_type = content_type or detected_type
            
            # Validate content
            validation_result = await self._validate_content(
                file_data, final_content_type, detected_format
            )
            if not validation_result["valid"]:
                raise ValueError(f"Content validation failed: {validation_result['errors']}")
            
            # Store original content
            original_url = await self.cloud_storage.upload_file(
                file_data, 
                f"campaigns/{campaign_id}/content/original/{content_id}.{detected_format.value}",
                content_type=f"{final_content_type.value}/{detected_format.value}"
            )
            
            # Extract basic metadata
            metadata = await self._extract_content_metadata(
                file_data, content_id, filename, final_content_type, detected_format
            )
            
            # Create processing task
            processing_task = {
                "content_id": content_id,
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "metadata": metadata,
                "config": config,
                "original_url": original_url,
                "status": ProcessingStatus.UPLOADED,
                "created_at": datetime.utcnow()
            }
            
            # Add to processing queue
            self._processing_queue[content_id] = processing_task
            
            # Start async processing
            asyncio.create_task(self._process_content_async(content_id))
            
            self.logger.info(f"Content uploaded successfully: {content_id}")
            
            return {
                "content_id": content_id,
                "status": ProcessingStatus.UPLOADED.value,
                "original_url": original_url,
                "metadata": metadata.__dict__,
                "processing_started": True,
                "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Content upload failed: {str(e)}")
            raise
    
    async def get_content_status(
        self,
        content_id: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get content processing status and details
        
        Args:
            content_id: Content unique identifier
            include_details: Whether to include detailed processing information
            
        Returns:
            Content status and processing details
        """
        try:
            # Check processing queue
            if content_id in self._processing_queue:
                task = self._processing_queue[content_id]
                status_data = {
                    "content_id": content_id,
                    "status": task["status"].value if hasattr(task["status"], 'value') else task["status"],
                    "progress_percentage": await self._calculate_processing_progress(content_id),
                    "created_at": task["created_at"].isoformat(),
                    "estimated_completion": await self._estimate_completion_time(content_id)
                }
                
                if include_details:
                    status_data.update({
                        "metadata": task["metadata"].__dict__ if hasattr(task["metadata"], '__dict__') else task["metadata"],
                        "processing_steps": await self._get_processing_steps_status(content_id),
                        "error_details": task.get("error_message")
                    })
                
                return status_data
            
            # Check content cache for completed content
            if content_id in self._content_cache:
                cached_content = self._content_cache[content_id]
                return {
                    "content_id": content_id,
                    "status": ProcessingStatus.READY.value,
                    "progress_percentage": 100,
                    "processing_completed": True,
                    "result": cached_content if include_details else {"available": True}
                }
            
            # Content not found
            return {
                "content_id": content_id,
                "status": "not_found",
                "error": "Content not found in processing queue or cache"
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Content status retrieval failed: {str(e)}")
            raise
    
    async def get_processed_content(
        self,
        content_id: str,
        requested_format: Optional[ContentFormat] = None,
        quality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve processed content in requested format
        
        Args:
            content_id: Content unique identifier
            requested_format: Desired content format
            quality: Desired quality level
            
        Returns:
            Processed content data and URLs
        """
        try:
            # Check if content is ready
            if content_id not in self._content_cache:
                status = await self.get_content_status(content_id, include_details=False)
                if status["status"] != ProcessingStatus.READY.value:
                    raise ValueError(f"Content not ready: {status['status']}")
            
            content_data = self._content_cache[content_id]
            
            # Determine best format
            if requested_format and requested_format in content_data["processed_formats"]:
                selected_format = requested_format
            else:
                selected_format = await self._select_optimal_format(
                    content_data, requested_format
                )
            
            # Get quality variant
            quality_key = quality or "standard"
            
            # Build response
            response = {
                "content_id": content_id,
                "format": selected_format.value,
                "quality": quality_key,
                "metadata": content_data["metadata"],
                "urls": {
                    "original": content_data["storage_urls"].get("original"),
                    "optimized": content_data["storage_urls"].get(f"{selected_format.value}_{quality_key}"),
                    "preview": content_data["storage_urls"].get("preview")
                },
                "ai_analysis": content_data.get("ai_analysis", {}),
                "protection_status": content_data.get("protection_status", {})
            }
            
            # Add format-specific data
            if content_data["metadata"]["content_type"] == ContentType.AUDIO:
                response["audio_analysis"] = content_data.get("audio_analysis", {})
            elif content_data["metadata"]["content_type"] == ContentType.VIDEO:
                response["video_analysis"] = content_data.get("video_analysis", {})
            elif content_data["metadata"]["content_type"] == ContentType.IMAGE:
                response["image_analysis"] = content_data.get("image_analysis", {})
            
            return response
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Processed content retrieval failed: {str(e)}")
            raise
    
    async def optimize_content_for_platform(
        self,
        content_id: str,
        target_platform: str,
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize content for specific platform requirements
        
        Args:
            content_id: Content unique identifier
            target_platform: Target platform (youtube, instagram, tiktok, etc.)
            optimization_goals: Optimization objectives
            
        Returns:
            Platform-optimized content variants
        """
        try:
            if content_id not in self._content_cache:
                raise ValueError(f"Content not found: {content_id}")
            
            content_data = self._content_cache[content_id]
            
            # Get platform requirements
            platform_specs = await self._get_platform_specifications(target_platform)
            
            # Analyze current content against platform requirements
            compatibility_analysis = await self._analyze_platform_compatibility(
                content_data, platform_specs
            )
            
            # Generate optimization plan
            optimization_plan = await self.content_optimizer.create_platform_optimization_plan(
                content_data,
                platform_specs,
                optimization_goals,
                compatibility_analysis
            )
            
            # Execute optimizations
            optimized_variants = {}
            for optimization_type, optimization_params in optimization_plan.items():
                optimized_content = await self._execute_platform_optimization(
                    content_data,
                    optimization_type,
                    optimization_params,
                    target_platform
                )
                optimized_variants[optimization_type] = optimized_content
            
            # Store optimized variants
            storage_urls = {}
            for variant_type, variant_data in optimized_variants.items():
                url = await self.cloud_storage.upload_file(
                    variant_data["data"],
                    f"campaigns/{content_data['campaign_id']}/content/optimized/{target_platform}/{content_id}_{variant_type}.{variant_data['format']}",
                    content_type=variant_data["mime_type"]
                )
                storage_urls[variant_type] = url
            
            # Update content cache
            if "platform_optimizations" not in self._content_cache[content_id]:
                self._content_cache[content_id]["platform_optimizations"] = {}
            
            self._content_cache[content_id]["platform_optimizations"][target_platform] = {
                "variants": optimized_variants,
                "storage_urls": storage_urls,
                "optimization_plan": optimization_plan,
                "created_at": datetime.utcnow()
            }
            
            return {
                "content_id": content_id,
                "target_platform": target_platform,
                "optimization_completed": True,
                "variants": list(optimized_variants.keys()),
                "storage_urls": storage_urls,
                "compatibility_score": compatibility_analysis["score"],
                "optimization_improvements": compatibility_analysis["improvements"]
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Platform optimization failed: {str(e)}")
            raise
    
    async def batch_process_content(
        self,
        campaign_id: str,
        creator_id: str,
        file_list: List[Dict[str, Any]],
        config: Optional[ContentIntegrationConfig] = None
    ) -> Dict[str, Any]:
        """
        Process multiple content files in batch
        
        Args:
            campaign_id: Campaign unique identifier
            creator_id: Creator unique identifier
            file_list: List of files to process
            config: Processing configuration
            
        Returns:
            Batch processing results
        """
        try:
            config = config or ContentIntegrationConfig()
            batch_id = f"batch_{campaign_id}_{int(datetime.utcnow().timestamp())}"
            
            batch_results = {
                "batch_id": batch_id,
                "total_files": len(file_list),
                "processed_files": [],
                "failed_files": [],
                "status": "processing",
                "started_at": datetime.utcnow().isoformat()
            }
            
            # Process files concurrently
            processing_tasks = []
            for file_info in file_list:
                task = asyncio.create_task(
                    self._process_single_file_in_batch(
                        campaign_id, creator_id, file_info, config, batch_id
                    )
                )
                processing_tasks.append(task)
            
            # Wait for all processing to complete
            results = await asyncio.gather(*processing_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    batch_results["failed_files"].append({
                        "filename": file_list[i].get("filename", f"file_{i}"),
                        "error": str(result)
                    })
                else:
                    batch_results["processed_files"].append(result)
            
            batch_results["status"] = "completed"
            batch_results["success_count"] = len(batch_results["processed_files"])
            batch_results["failure_count"] = len(batch_results["failed_files"])
            batch_results["completed_at"] = datetime.utcnow().isoformat()
            
            return batch_results
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Batch content processing failed: {str(e)}")
            raise
    
    async def analyze_content_performance(
        self,
        content_id: str,
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze content performance and generate insights
        
        Args:
            content_id: Content unique identifier
            performance_metrics: Performance data from platforms
            
        Returns:
            Content performance analysis and recommendations
        """
        try:
            if content_id not in self._content_cache:
                raise ValueError(f"Content not found: {content_id}")
            
            content_data = self._content_cache[content_id]
            
            # Perform AI-powered performance analysis
            performance_analysis = await self.content_analyzer.analyze_performance(
                content_data, performance_metrics
            )
            
            # Generate content insights
            content_insights = await self._generate_content_insights(
                content_data, performance_metrics, performance_analysis
            )
            
            # Identify improvement opportunities
            improvement_opportunities = await self._identify_content_improvements(
                content_data, performance_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_content_recommendations(
                content_data, performance_analysis, improvement_opportunities
            )
            
            return {
                "content_id": content_id,
                "performance_analysis": performance_analysis,
                "content_insights": content_insights,
                "improvement_opportunities": improvement_opportunities,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            self.logger.error(f"Content performance analysis failed: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _content_processing_worker(self) -> None:
        """Background worker for processing content"""
        while True:
            try:
                # Process queued content
                content_ids = list(self._processing_queue.keys())
                
                for content_id in content_ids:
                    task = self._processing_queue[content_id]
                    if task["status"] == ProcessingStatus.UPLOADED:
                        asyncio.create_task(self._process_content_async(content_id))
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:

                
                logger.error(f"Error: {e}")

                
                raise
                self.logger.error(f"Content processing worker error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _process_content_async(self, content_id: str) -> None:
        """Asynchronous content processing"""
        try:
            if content_id not in self._processing_queue:
                return
            
            task = self._processing_queue[content_id]
            config = task["config"]
            
            # Update status
            task["status"] = ProcessingStatus.PROCESSING
            
            # Extract detailed metadata
            if config.extract_metadata:
                detailed_metadata = await self._extract_detailed_metadata(
                    task["original_url"], task["metadata"]
                )
                task["metadata"] = detailed_metadata
            
            # AI analysis
            ai_analysis = {}
            if config.ai_analysis:
                ai_analysis = await self.content_analyzer.analyze_content(
                    task["original_url"], task["metadata"]
                )
            
            task["status"] = ProcessingStatus.ANALYZED
            
            # Content optimization
            optimization_result = {}
            if config.auto_optimization:
                optimization_result = await self.content_optimizer.optimize_content(
                    task["original_url"], 
                    task["metadata"], 
                    ai_analysis
                )
            
            task["status"] = ProcessingStatus.OPTIMIZED
            
            # Content protection
            protection_result = {}
            if config.auto_protection:
                protection_result = await self.content_fingerprint.protect_content(
                    content_id,
                    task["original_url"],
                    task["metadata"]
                )
            
            task["status"] = ProcessingStatus.PROTECTED
            
            # Generate previews and variants
            storage_urls = {"original": task["original_url"]}
            if config.generate_previews:
                preview_urls = await self._generate_content_previews(
                    task["original_url"], task["metadata"]
                )
                storage_urls.update(preview_urls)
            
            # Format conversion
            if config.format_conversion:
                converted_formats = await self._convert_content_formats(
                    task["original_url"], task["metadata"]
                )
                storage_urls.update(converted_formats)
            
            # Create final result
            processing_result = ContentProcessingResult(
                content_id=content_id,
                status=ProcessingStatus.READY,
                processed_formats=[task["metadata"].content_format],
                optimization_applied=bool(optimization_result),
                protection_enabled=bool(protection_result),
                ai_analysis=ai_analysis,
                storage_urls=storage_urls,
                processing_time=(datetime.utcnow() - task["created_at"]).total_seconds()
            )
            
            # Cache completed content
            self._content_cache[content_id] = {
                "metadata": task["metadata"],
                "ai_analysis": ai_analysis,
                "optimization_result": optimization_result,
                "protection_result": protection_result,
                "storage_urls": storage_urls,
                "processed_formats": [task["metadata"].content_format],
                "campaign_id": task["campaign_id"],
                "creator_id": task["creator_id"],
                "processing_result": processing_result
            }
            
            # Remove from processing queue
            del self._processing_queue[content_id]
            
            self.logger.info(f"Content processing completed: {content_id}")
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            # Handle processing error
            if content_id in self._processing_queue:
                self._processing_queue[content_id]["status"] = ProcessingStatus.ERROR
                self._processing_queue[content_id]["error_message"] = str(e)
            
            self.logger.error(f"Content processing failed for {content_id}: {str(e)}")
    
    async def _generate_content_id(self, filename: str, creator_id: str) -> str:
        """Generate unique content ID"""
        timestamp = datetime.utcnow().isoformat()
        content_string = f"{filename}_{creator_id}_{timestamp}"
        return hashlib.sha256(content_string.encode()).hexdigest()[:16]
    
    async def _detect_content_type_and_format(
        self, 
        file_data: Union[bytes, BinaryIO], 
        filename: str
    ) -> Tuple[ContentType, ContentFormat]:
        """Detect content type and format from file"""
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        file_extension = Path(filename).suffix.lower().lstrip('.')
        
        # Map to our enums
        format_mapping = {
            'mp3': (ContentType.AUDIO, ContentFormat.MP3),
            'wav': (ContentType.AUDIO, ContentFormat.WAV),
            'flac': (ContentType.AUDIO, ContentFormat.FLAC),
            'mp4': (ContentType.VIDEO, ContentFormat.MP4),
            'avi': (ContentType.VIDEO, ContentFormat.AVI),
            'mov': (ContentType.VIDEO, ContentFormat.MOV),
            'jpg': (ContentType.IMAGE, ContentFormat.JPEG),
            'jpeg': (ContentType.IMAGE, ContentFormat.JPEG),
            'png': (ContentType.IMAGE, ContentFormat.PNG),
            'gif': (ContentType.IMAGE, ContentFormat.GIF),
            'txt': (ContentType.TEXT, ContentFormat.TXT),
            'md': (ContentType.TEXT, ContentFormat.MD),
            'pdf': (ContentType.DOCUMENT, ContentFormat.PDF)
        }
        
        return format_mapping.get(file_extension, (ContentType.DOCUMENT, ContentFormat.TXT))
    
    async def _validate_content(
        self, 
        file_data: Union[bytes, BinaryIO], 
        content_type: ContentType, 
        content_format: ContentFormat
    ) -> Dict[str, Any]:
        """
Validate uploaded content"""
        return {"valid": True, "errors": []}
    
    async def _extract_content_metadata(
        self,
        file_data: Union[bytes, BinaryIO],
        content_id: str,
        filename: str,
        content_type: ContentType,
        content_format: ContentFormat
    ) -> ContentMetadata:
        """Extract basic content metadata"""
        file_size = len(file_data) if isinstance(file_data, bytes) else 0
        
        return ContentMetadata(
            content_id=content_id,
            original_filename=filename,
            content_type=content_type,
            content_format=content_format,
            file_size=file_size,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
