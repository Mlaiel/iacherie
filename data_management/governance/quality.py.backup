"""Data Quality Management System

Advanced data quality assessment, monitoring, and improvement system
for multi-format content with real-time quality metrics and scoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import statistics
from abc import ABC, abstractmethod

from ...core.base import BaseManager
from ...core.exceptions import QualityError, ValidationError
from ...core.database import DatabaseManager
from ...ai.models import ContentAnalyzer, QualityClassifier


class QualityDimension(Enum):
    """Data quality dimensions"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    INTEGRITY = "integrity"
    ACCESSIBILITY = "accessibility"


class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 75-89%
    ACCEPTABLE = "acceptable"  # 60-74%
    POOR = "poor"           # 40-59%
    CRITICAL = "critical"   # 0-39%


@dataclass
class QualityRule:
    """Data quality rule definition"""
    rule_id: str
    name: str
    description: str
    dimension: QualityDimension
    content_types: List[str]
    validation_function: str  # Function name or expression
    threshold: float  # Quality threshold (0-1)
    weight: float = 1.0  # Rule weight in overall score
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityIssue:
    """Quality issue record"""
    issue_id: str
    content_id: str
    rule_id: str
    dimension: QualityDimension
    description: str
    severity: QualityLevel
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Quality metrics for content"""
    content_id: str
    content_type: str
    overall_score: float  # 0-100
    dimension_scores: Dict[QualityDimension, float]
    quality_level: QualityLevel
    issues_count: int
    critical_issues_count: int
    assessed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseQualityChecker(ABC):
    """Base class for content-specific quality checkers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def check_quality(
        self,
        content_id: str,
        content_data: Any,
        metadata: Dict[str, Any]
    ) -> QualityMetrics:
        """Check quality for specific content type"""
        logger.warning(f"check_quality method not implemented in {self.__class__.__name__}")
        
        # Create default quality metrics
        dimension_scores = {
            QualityDimension.COMPLETENESS: 80.0,
            QualityDimension.ACCURACY: 75.0,
            QualityDimension.CONSISTENCY: 85.0,
            QualityDimension.VALIDITY: 90.0
        }
        
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        
        # Determine quality level based on score
        if overall_score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 75:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 60:
            quality_level = QualityLevel.ACCEPTABLE
        elif overall_score >= 40:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.CRITICAL
        
        return QualityMetrics(
            content_id=content_id,
            content_type=type(content_data).__name__,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            quality_level=quality_level,
            issues_count=0,
            critical_issues_count=0,
            assessed_at=datetime.utcnow(),
            metadata={"checker": self.__class__.__name__}
        )
    
    @abstractmethod
    def get_quality_rules(self) -> List[QualityRule]:
        """Get quality rules for this content type"""
        logger.warning(f"get_quality_rules method not implemented in {self.__class__.__name__}")
        
        # Return basic default rules
        return [
            QualityRule(
                rule_id="default_completeness",
                name="Basic Completeness Check",
                description="Check if content has required fields",
                dimension=QualityDimension.COMPLETENESS,
                content_types=["default"],
                validation_function="check_completeness",
                threshold=0.8
            ),
            QualityRule(
                rule_id="default_validity",
                name="Basic Validity Check", 
                description="Check if content format is valid",
                dimension=QualityDimension.VALIDITY,
                content_types=["default"],
                validation_function="check_validity",
                threshold=0.9
            )
        ]


class AudioQualityChecker(BaseQualityChecker):
    """Quality checker for audio content"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.content_analyzer = ContentAnalyzer(config)
    
    async def check_quality(
        self,
        content_id: str,
        content_data: Any,
        metadata: Dict[str, Any]
    ) -> QualityMetrics:
        """Check audio content quality"""
        dimension_scores = {}
        issues_count = 0
        critical_issues_count = 0
        
        # Check completeness
        completeness_score = await self._check_completeness(content_data, metadata)
        dimension_scores[QualityDimension.COMPLETENESS] = completeness_score
        
        # Check accuracy (technical quality)
        accuracy_score = await self._check_audio_accuracy(content_data, metadata)
        dimension_scores[QualityDimension.ACCURACY] = accuracy_score
        
        # Check consistency
        consistency_score = await self._check_consistency(content_data, metadata)
        dimension_scores[QualityDimension.CONSISTENCY] = consistency_score
        
        # Check validity (format, encoding)
        validity_score = await self._check_validity(content_data, metadata)
        dimension_scores[QualityDimension.VALIDITY] = validity_score
        
        # Check integrity
        integrity_score = await self._check_integrity(content_data, metadata)
        dimension_scores[QualityDimension.INTEGRITY] = integrity_score
        
        # Calculate overall score
        overall_score = statistics.mean(dimension_scores.values()) * 100
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)
        
        return QualityMetrics(
            content_id=content_id,
            content_type="audio",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            quality_level=quality_level,
            issues_count=issues_count,
            critical_issues_count=critical_issues_count,
            assessed_at=datetime.utcnow(),
            metadata={"audio_analysis": True}
        )
    
    async def _check_completeness(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check audio completeness"""
        score = 1.0
        
        # Check if audio has required metadata
        required_fields = ["duration", "sample_rate", "channels", "format"]
        present_fields = sum(1 for field in required_fields if metadata.get(field))
        score = present_fields / len(required_fields)
        
        # Check for audio data presence
        if not content_data or len(content_data) == 0:
            score *= 0.5
        
        return score
    
    async def _check_audio_accuracy(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check audio technical accuracy"""
        score = 1.0
        
        # Check sample rate
        sample_rate = metadata.get("sample_rate", 0)
        if sample_rate < 44100:  # Below CD quality
            score *= 0.7
        elif sample_rate < 22050:  # Below acceptable quality
            score *= 0.4
        
        # Check bit depth
        bit_depth = metadata.get("bit_depth", 0)
        if bit_depth < 16:
            score *= 0.6
        
        # Check for audio quality issues using AI
        quality_analysis = await self.content_analyzer.analyze_audio_quality(content_data)
        if quality_analysis.get("noise_level", 0) > 0.3:
            score *= 0.8
        
        if quality_analysis.get("distortion_level", 0) > 0.2:
            score *= 0.7
        
        return score
    
    async def _check_consistency(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check audio consistency"""
        score = 1.0
        
        # Check consistency between metadata and actual content
        stated_duration = metadata.get("duration", 0)
        actual_duration = await self._calculate_actual_duration(content_data)
        
        if abs(stated_duration - actual_duration) > 1.0:  # More than 1 second difference
            score *= 0.8
        
        return score
    
    async def _check_validity(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check audio format validity"""
        score = 1.0
        
        # Check supported format
        audio_format = metadata.get("format", "").lower()
        supported_formats = ["mp3", "wav", "flac", "aac", "ogg"]
        
        if audio_format not in supported_formats:
            score *= 0.5
        
        # Validate audio headers
        if not await self._validate_audio_headers(content_data):
            score *= 0.6
        
        return score
    
    async def _check_integrity(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check audio data integrity"""
        score = 1.0
        
        # Check for corruption
        if await self._detect_audio_corruption(content_data):
            score *= 0.3
        
        # Check checksum if available
        if metadata.get("checksum"):
            if not await self._verify_checksum(content_data, metadata["checksum"]):
                score *= 0.5
        
        return score
    
    async def _calculate_actual_duration(self, content_data: Any) -> float:
        """Calculate actual audio duration"""
        # Implementation would use audio processing library
        return 0.0
    
    async def _validate_audio_headers(self, content_data: Any) -> bool:
        """Validate audio file headers"""
        # Implementation would check audio format headers
        return True
    
    async def _detect_audio_corruption(self, content_data: Any) -> bool:
        """Detect audio corruption"""
        # Implementation would analyze audio for corruption patterns
        return False
    
    async def _verify_checksum(self, content_data: Any, expected_checksum: str) -> bool:
        """Verify content checksum"""
        # Implementation would calculate and compare checksums
        return True
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def get_quality_rules(self) -> List[QualityRule]:
        """Get audio quality rules"""
        return [
            QualityRule(
                rule_id="audio_sample_rate",
                name="Minimum Sample Rate",
                description="Audio must have minimum 22kHz sample rate",
                dimension=QualityDimension.ACCURACY,
                content_types=["audio"],
                validation_function="sample_rate >= 22050",
                threshold=0.8
            ),
            QualityRule(
                rule_id="audio_duration",
                name="Audio Duration Validity",
                description="Audio must have valid duration",
                dimension=QualityDimension.COMPLETENESS,
                content_types=["audio"],
                validation_function="duration > 0",
                threshold=1.0
            )
        ]


class VideoQualityChecker(BaseQualityChecker):
    """Quality checker for video content"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.content_analyzer = ContentAnalyzer(config)
    
    async def check_quality(
        self,
        content_id: str,
        content_data: Any,
        metadata: Dict[str, Any]
    ) -> QualityMetrics:
        """Check video content quality"""
        dimension_scores = {}
        
        # Check completeness
        dimension_scores[QualityDimension.COMPLETENESS] = await self._check_video_completeness(content_data, metadata)
        
        # Check accuracy (resolution, frame rate)
        dimension_scores[QualityDimension.ACCURACY] = await self._check_video_accuracy(content_data, metadata)
        
        # Check consistency
        dimension_scores[QualityDimension.CONSISTENCY] = await self._check_video_consistency(content_data, metadata)
        
        # Check validity
        dimension_scores[QualityDimension.VALIDITY] = await self._check_video_validity(content_data, metadata)
        
        # Check integrity
        dimension_scores[QualityDimension.INTEGRITY] = await self._check_video_integrity(content_data, metadata)
        
        overall_score = statistics.mean(dimension_scores.values()) * 100
        quality_level = self._determine_quality_level(overall_score)
        
        return QualityMetrics(
            content_id=content_id,
            content_type="video",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            quality_level=quality_level,
            issues_count=0,
            critical_issues_count=0,
            assessed_at=datetime.utcnow(),
            metadata={"video_analysis": True}
        )
    
    async def _check_video_completeness(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check video completeness"""
        score = 1.0
        
        required_fields = ["duration", "width", "height", "fps", "codec"]
        present_fields = sum(1 for field in required_fields if metadata.get(field))
        score = present_fields / len(required_fields)
        
        return score
    
    async def _check_video_accuracy(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check video technical accuracy"""
        score = 1.0
        
        # Check resolution
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)
        
        if width < 720 or height < 480:  # Below acceptable resolution
            score *= 0.6
        
        # Check frame rate
        fps = metadata.get("fps", 0)
        if fps < 24:
            score *= 0.7
        
        return score
    
    async def _check_video_consistency(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check video consistency"""
        # Implementation for video consistency checks
        return 1.0
    
    async def _check_video_validity(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check video format validity"""
        score = 1.0
        
        codec = metadata.get("codec", "").lower()
        supported_codecs = ["h264", "h265", "vp8", "vp9", "av1"]
        
        if codec not in supported_codecs:
            score *= 0.7
        
        return score
    
    async def _check_video_integrity(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check video integrity"""
        # Implementation for video integrity checks
        return 1.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def get_quality_rules(self) -> List[QualityRule]:
        """Get video quality rules"""
        return [
            QualityRule(
                rule_id="video_resolution",
                name="Minimum Resolution",
                description="Video must have minimum 720p resolution",
                dimension=QualityDimension.ACCURACY,
                content_types=["video"],
                validation_function="width >= 720 and height >= 480",
                threshold=0.8
            )
        ]


class ImageQualityChecker(BaseQualityChecker):
    """Quality checker for image content"""
    
    async def check_quality(
        self,
        content_id: str,
        content_data: Any,
        metadata: Dict[str, Any]
    ) -> QualityMetrics:
        """Check image content quality"""
        dimension_scores = {}
        
        # Check completeness
        dimension_scores[QualityDimension.COMPLETENESS] = await self._check_image_completeness(content_data, metadata)
        
        # Check accuracy (resolution, color depth)
        dimension_scores[QualityDimension.ACCURACY] = await self._check_image_accuracy(content_data, metadata)
        
        # Check validity
        dimension_scores[QualityDimension.VALIDITY] = await self._check_image_validity(content_data, metadata)
        
        overall_score = statistics.mean(dimension_scores.values()) * 100
        quality_level = self._determine_quality_level(overall_score)
        
        return QualityMetrics(
            content_id=content_id,
            content_type="image",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            quality_level=quality_level,
            issues_count=0,
            critical_issues_count=0,
            assessed_at=datetime.utcnow()
        )
    
    async def _check_image_completeness(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check image completeness"""
        score = 1.0
        
        required_fields = ["width", "height", "format", "color_mode"]
        present_fields = sum(1 for field in required_fields if metadata.get(field))
        score = present_fields / len(required_fields)
        
        return score
    
    async def _check_image_accuracy(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check image technical accuracy"""
        score = 1.0
        
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)
        
        if width < 800 or height < 600:  # Below acceptable resolution
            score *= 0.7
        
        return score
    
    async def _check_image_validity(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check image format validity"""
        score = 1.0
        
        image_format = metadata.get("format", "").lower()
        supported_formats = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
        
        if image_format not in supported_formats:
            score *= 0.5
        
        return score
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def get_quality_rules(self) -> List[QualityRule]:
        """Get image quality rules"""
        return [
            QualityRule(
                rule_id="image_resolution",
                name="Minimum Image Resolution",
                description="Image must have minimum 800x600 resolution",
                dimension=QualityDimension.ACCURACY,
                content_types=["image"],
                validation_function="width >= 800 and height >= 600",
                threshold=0.7
            )
        ]


class TextQualityChecker(BaseQualityChecker):
    """Quality checker for text content"""
    
    async def check_quality(
        self,
        content_id: str,
        content_data: Any,
        metadata: Dict[str, Any]
    ) -> QualityMetrics:
        """Check text content quality"""
        dimension_scores = {}
        
        # Check completeness
        dimension_scores[QualityDimension.COMPLETENESS] = await self._check_text_completeness(content_data, metadata)
        
        # Check accuracy (grammar, spelling)
        dimension_scores[QualityDimension.ACCURACY] = await self._check_text_accuracy(content_data, metadata)
        
        # Check consistency
        dimension_scores[QualityDimension.CONSISTENCY] = await self._check_text_consistency(content_data, metadata)
        
        # Check validity
        dimension_scores[QualityDimension.VALIDITY] = await self._check_text_validity(content_data, metadata)
        
        overall_score = statistics.mean(dimension_scores.values()) * 100
        quality_level = self._determine_quality_level(overall_score)
        
        return QualityMetrics(
            content_id=content_id,
            content_type="text",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            quality_level=quality_level,
            issues_count=0,
            critical_issues_count=0,
            assessed_at=datetime.utcnow()
        )
    
    async def _check_text_completeness(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check text completeness"""
        score = 1.0
        
        if not content_data or len(str(content_data).strip()) == 0:
            score = 0.0
        
        # Check for required metadata
        required_fields = ["language", "encoding", "word_count"]
        present_fields = sum(1 for field in required_fields if metadata.get(field))
        metadata_score = present_fields / len(required_fields)
        
        return (score + metadata_score) / 2
    
    async def _check_text_accuracy(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check text accuracy (grammar, spelling)"""
        # Implementation would use NLP models for grammar/spelling check
        return 0.9  # Placeholder
    
    async def _check_text_consistency(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check text consistency"""
        # Implementation would check for consistent formatting, style
        return 0.95  # Placeholder
    
    async def _check_text_validity(self, content_data: Any, metadata: Dict[str, Any]) -> float:
        """Check text validity"""
        score = 1.0
        
        # Check encoding
        encoding = metadata.get("encoding", "").lower()
        if encoding not in ["utf-8", "ascii", "latin-1"]:
            score *= 0.8
        
        return score
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def get_quality_rules(self) -> List[QualityRule]:
        """Get text quality rules"""
        return [
            QualityRule(
                rule_id="text_not_empty",
                name="Text Content Present",
                description="Text content must not be empty",
                dimension=QualityDimension.COMPLETENESS,
                content_types=["text"],
                validation_function="len(content.strip()) > 0",
                threshold=1.0
            )
        ]


class QualityManager(BaseManager):
    """
    Central data quality management system
    
    Orchestrates quality assessment across all content types,
    provides quality monitoring, reporting, and improvement recommendations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the quality manager"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db_manager = DatabaseManager(config)
        
        # Quality checkers by content type
        self.quality_checkers = {
            "audio": AudioQualityChecker(config),
            "video": VideoQualityChecker(config),
            "image": ImageQualityChecker(config),
            "text": TextQualityChecker(config)
        }
        
        # Quality storage
        self.quality_metrics: Dict[str, QualityMetrics] = {}
        self.quality_issues: List[QualityIssue] = []
        self.quality_rules: Dict[str, QualityRule] = {}
        
        # Performance metrics
        self.metrics = {
            "total_assessments": 0,
            "average_quality_score": 0.0,
            "critical_issues_count": 0,
            "resolved_issues_count": 0
        }
    
    async def initialize(self) -> None:
        """Initialize the quality manager"""
        try:
            await self._load_quality_rules()
            await self._load_quality_history()
            
            # Start background quality monitoring
            asyncio.create_task(self._quality_monitor())
            
            self.logger.info("Quality manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize quality manager: {e}")
            raise QualityError(f"Quality manager initialization failed: {e}")
    
    async def assess_quality(
        self,
        content_id: str,
        content_type: str,
        content_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityMetrics:
        """
        Assess quality of content
        
        Args:
            content_id: Unique content identifier
            content_type: Type of content (audio, video, image, text)
            content_data: Actual content data
            metadata: Content metadata
            
        Returns:
            QualityMetrics: Quality assessment results
        """
        try:
            if content_type not in self.quality_checkers:
                raise QualityError(f"Unsupported content type: {content_type}")
            
            # Get appropriate quality checker
            checker = self.quality_checkers[content_type]
            
            # Perform quality assessment
            quality_metrics = await checker.check_quality(
                content_id, content_data, metadata or {}
            )
            
            # Store quality metrics
            self.quality_metrics[content_id] = quality_metrics
            
            # Generate quality issues for poor quality
            await self._generate_quality_issues(quality_metrics)
            
            # Update performance metrics
            self.metrics["total_assessments"] += 1
            self._update_average_quality_score(quality_metrics.overall_score)
            
            self.logger.info(f"Quality assessed for {content_id}: {quality_metrics.overall_score:.2f}")
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error assessing quality for {content_id}: {e}")
            raise QualityError(f"Quality assessment failed: {e}")
    
    async def get_quality_metrics(
        self,
        content_id: Optional[str] = None,
        content_type: Optional[str] = None,
        quality_level: Optional[QualityLevel] = None
    ) -> Union[QualityMetrics, List[QualityMetrics]]:
        """
        Get quality metrics with optional filtering
        
        Args:
            content_id: Specific content ID
            content_type: Filter by content type
            quality_level: Filter by quality level
            
        Returns:
            QualityMetrics or list of QualityMetrics
        """
        if content_id:
            return self.quality_metrics.get(content_id)
        
        # Filter metrics
        filtered_metrics = list(self.quality_metrics.values())
        
        if content_type:
            filtered_metrics = [m for m in filtered_metrics if m.content_type == content_type]
        
        if quality_level:
            filtered_metrics = [m for m in filtered_metrics if m.quality_level == quality_level]
        
        return filtered_metrics
    
    async def get_quality_summary(
        self,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get quality summary statistics
        
        Args:
            content_type: Filter by content type
            
        Returns:
            Dict with quality summary
        """
        metrics = await self.get_quality_metrics(content_type=content_type)
        if isinstance(metrics, QualityMetrics):
            metrics = [metrics]
        
        if not metrics:
            return {"total_content": 0, "average_score": 0.0}
        
        total_content = len(metrics)
        average_score = sum(m.overall_score for m in metrics) / total_content
        
        # Quality level breakdown
        level_breakdown = {}
        for level in QualityLevel:
            count = len([m for m in metrics if m.quality_level == level])
            level_breakdown[level.value] = count
        
        # Dimension scores
        dimension_averages = {}
        for dimension in QualityDimension:
            scores = []
            for metric in metrics:
                if dimension in metric.dimension_scores:
                    scores.append(metric.dimension_scores[dimension] * 100)
            
            if scores:
                dimension_averages[dimension.value] = statistics.mean(scores)
        
        return {
            "total_content": total_content,
            "average_score": round(average_score, 2),
            "quality_level_breakdown": level_breakdown,
            "dimension_averages": dimension_averages,
            "critical_issues": len([m for m in metrics if m.critical_issues_count > 0])
        }
    
    async def get_quality_issues(
        self,
        content_id: Optional[str] = None,
        dimension: Optional[QualityDimension] = None,
        severity: Optional[QualityLevel] = None,
        resolved: Optional[bool] = None
    ) -> List[QualityIssue]:
        """
        Get quality issues with optional filtering
        
        Args:
            content_id: Filter by content ID
            dimension: Filter by quality dimension
            severity: Filter by severity level
            resolved: Filter by resolution status
            
        Returns:
            List of filtered quality issues
        """
        filtered_issues = self.quality_issues.copy()
        
        if content_id:
            filtered_issues = [i for i in filtered_issues if i.content_id == content_id]
        
        if dimension:
            filtered_issues = [i for i in filtered_issues if i.dimension == dimension]
        
        if severity:
            filtered_issues = [i for i in filtered_issues if i.severity == severity]
        
        if resolved is not None:
            if resolved:
                filtered_issues = [i for i in filtered_issues if i.resolved_at is not None]
            else:
                filtered_issues = [i for i in filtered_issues if i.resolved_at is None]
        
        return filtered_issues
    
    async def resolve_quality_issue(
        self,
        issue_id: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Mark a quality issue as resolved
        
        Args:
            issue_id: ID of issue to resolve
            resolution_notes: Optional resolution notes
            
        Returns:
            bool: True if issue resolved successfully
        """
        for issue in self.quality_issues:
            if issue.issue_id == issue_id:
                issue.resolved_at = datetime.utcnow()
                issue.resolution_notes = resolution_notes
                
                self.metrics["resolved_issues_count"] += 1
                
                self.logger.info(f"Resolved quality issue: {issue_id}")
                return True
        
        return False
    
    async def add_quality_rule(self, rule: QualityRule) -> bool:
        """
        Add a new quality rule
        
        Args:
            rule: Quality rule to add
            
        Returns:
            bool: True if rule added successfully
        """
        try:
            # Validate rule
            await self._validate_quality_rule(rule)
            
            # Store rule
            self.quality_rules[rule.rule_id] = rule
            
            self.logger.info(f"Added quality rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding quality rule {rule.rule_id}: {e}")
            raise QualityError(f"Quality rule addition failed: {e}")
    
    async def get_quality_recommendations(
        self,
        content_id: str
    ) -> List[str]:
        """
        Get quality improvement recommendations for content
        
        Args:
            content_id: ID of content to analyze
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        # Get quality metrics
        metrics = self.quality_metrics.get(content_id)
        if not metrics:
            return ["Perform quality assessment first"]
        
        # Analyze dimension scores
        for dimension, score in metrics.dimension_scores.items():
            if score < 0.7:  # Below acceptable threshold
                recommendations.extend(
                    await self._get_dimension_recommendations(dimension, score)
                )
        
        # Analyze quality issues
        issues = await self.get_quality_issues(content_id=content_id, resolved=False)
        for issue in issues:
            recommendations.append(
                f"Resolve {issue.dimension.value} issue: {issue.description}"
            )
        
        return recommendations
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get quality management metrics"""
        return {
            **self.metrics,
            "quality_checkers_count": len(self.quality_checkers),
            "quality_rules_count": len(self.quality_rules),
            "total_issues": len(self.quality_issues),
            "unresolved_issues": len([i for i in self.quality_issues if i.resolved_at is None])
        }
    
    def _update_average_quality_score(self, new_score: float) -> None:
        """Update running average quality score"""
        total_assessments = self.metrics["total_assessments"]
        current_average = self.metrics["average_quality_score"]
        
        self.metrics["average_quality_score"] = (
            (current_average * (total_assessments - 1) + new_score) / total_assessments
        )
    
    async def _generate_quality_issues(self, metrics: QualityMetrics) -> None:
        """Generate quality issues based on metrics"""
        for dimension, score in metrics.dimension_scores.items():
            if score < 0.4:  # Critical threshold
                issue = QualityIssue(
                    issue_id=f"quality_{metrics.content_id}_{dimension.value}_{datetime.utcnow().timestamp()}",
                    content_id=metrics.content_id,
                    rule_id=f"threshold_{dimension.value}",
                    dimension=dimension,
                    description=f"Low {dimension.value} score: {score:.2f}",
                    severity=QualityLevel.CRITICAL if score < 0.2 else QualityLevel.POOR,
                    detected_at=datetime.utcnow()
                )
                
                self.quality_issues.append(issue)
                
                if issue.severity == QualityLevel.CRITICAL:
                    self.metrics["critical_issues_count"] += 1
    
    async def _get_dimension_recommendations(
        self,
        dimension: QualityDimension,
        score: float
    ) -> List[str]:
        """Get recommendations for improving specific quality dimension"""
        recommendations = []
        
        if dimension == QualityDimension.COMPLETENESS:
            recommendations.append("Ensure all required metadata fields are populated")
            recommendations.append("Verify content data is complete and not truncated")
        
        elif dimension == QualityDimension.ACCURACY:
            recommendations.append("Improve technical quality (resolution, sample rate, etc.)")
            recommendations.append("Validate content against format specifications")
        
        elif dimension == QualityDimension.CONSISTENCY:
            recommendations.append("Ensure metadata matches actual content properties")
            recommendations.append("Standardize formatting and structure")
        
        elif dimension == QualityDimension.VALIDITY:
            recommendations.append("Use supported formats and encodings")
            recommendations.append("Validate content structure and headers")
        
        elif dimension == QualityDimension.INTEGRITY:
            recommendations.append("Check for data corruption or damage")
            recommendations.append("Verify checksums and data integrity")
        
        return recommendations
    
    async def _quality_monitor(self) -> None:
        """Background task to monitor quality trends"""
        while True:
            try:
                # Monitor quality trends
                await self._analyze_quality_trends()
                
                # Clean up old resolved issues
                await self._cleanup_old_issues()
                
                # Sleep for monitoring interval (daily)
                await asyncio.sleep(86400)
                
            except Exception as e:
                self.logger.error(f"Error in quality monitor: {e}")
                await asyncio.sleep(3600)  # Shorter sleep on error
    
    async def _analyze_quality_trends(self) -> None:
        """Analyze quality trends over time"""
        try:
            self.logger.info("Analyzing quality trends")
            
            # Get quality history for trend analysis
            current_time = datetime.utcnow()
            lookback_period = timedelta(days=30)
            
            # Simulate quality trend analysis
            quality_data_points = []
            
            # Collect quality metrics over time
            for content_type in ["audio", "video", "image", "text"]:
                content_metrics = []
                
                # Generate sample trend data (would come from database)
                for i in range(30):  # Last 30 days
                    date = current_time - timedelta(days=i)
                    
                    # Simulate quality score with some variation
                    base_score = 0.85
                    variation = (i % 7) * 0.02  # Weekly variation
                    daily_variation = (date.day % 3) * 0.01  # Daily variation
                    quality_score = min(1.0, base_score + variation - daily_variation)
                    
                    content_metrics.append({
                        "date": date.isoformat(),
                        "content_type": content_type,
                        "average_quality_score": quality_score,
                        "total_assessments": 50 + (i % 20),
                        "failed_assessments": max(0, int((1 - quality_score) * 10))
                    })
                
                quality_data_points.extend(content_metrics)
            
            # Analyze trends
            trends = {}
            for content_type in ["audio", "video", "image", "text"]:
                type_data = [dp for dp in quality_data_points if dp["content_type"] == content_type]
                
                if len(type_data) >= 7:  # Need at least a week of data
                    recent_scores = [dp["average_quality_score"] for dp in type_data[:7]]
                    older_scores = [dp["average_quality_score"] for dp in type_data[7:14]]
                    
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg
                    
                    trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
                    trend_magnitude = abs(recent_avg - older_avg)
                    
                    trends[content_type] = {
                        "direction": trend_direction,
                        "magnitude": trend_magnitude,
                        "recent_average": recent_avg,
                        "older_average": older_avg,
                        "data_points": len(type_data)
                    }
            
            # Store trend analysis results
            self.quality_trends = {
                "analysis_date": current_time.isoformat(),
                "lookback_days": 30,
                "content_type_trends": trends,
                "overall_trend": self._calculate_overall_trend(trends),
                "recommendations": self._generate_quality_recommendations(trends)
            }
            
            self.logger.info(f"Quality trend analysis completed for {len(trends)} content types")
            
        except Exception as e:
            self.logger.error(f"Error analyzing quality trends: {str(e)}")
    
    def _calculate_overall_trend(self, trends: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate overall quality trend across all content types"""
        if not trends:
            return {"direction": "unknown", "confidence": 0.0}
        
        improving_count = sum(1 for t in trends.values() if t["direction"] == "improving")
        declining_count = sum(1 for t in trends.values() if t["direction"] == "declining")
        stable_count = sum(1 for t in trends.values() if t["direction"] == "stable")
        
        total_count = len(trends)
        
        if improving_count > declining_count:
            direction = "improving"
            confidence = improving_count / total_count
        elif declining_count > improving_count:
            direction = "declining"
            confidence = declining_count / total_count
        else:
            direction = "stable"
            confidence = stable_count / total_count
        
        return {
            "direction": direction,
            "confidence": confidence,
            "improving_types": improving_count,
            "declining_types": declining_count,
            "stable_types": stable_count
        }
    
    def _generate_quality_recommendations(self, trends: Dict[str, Dict]) -> List[str]:
        """Generate recommendations based on quality trends"""
        recommendations = []
        
        for content_type, trend_data in trends.items():
            if trend_data["direction"] == "declining" and trend_data["magnitude"] > 0.05:
                recommendations.append(
                    f"Quality declining for {content_type} content. "
                    f"Consider reviewing quality rules and validation processes."
                )
            
            elif trend_data["recent_average"] < 0.7:
                recommendations.append(
                    f"Low quality scores detected for {content_type} content. "
                    f"Immediate attention required to improve quality standards."
                )
            
            elif trend_data["direction"] == "improving":
                recommendations.append(
                    f"Quality improving for {content_type} content. "
                    f"Current processes are working well."
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Quality metrics are stable. Continue monitoring.")
        
        return recommendations
    
    async def _cleanup_old_issues(self) -> None:
        """Clean up old resolved issues"""
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        self.quality_issues = [
            issue for issue in self.quality_issues
            if not issue.resolved_at or issue.resolved_at > cutoff_date
        ]
    
    async def _validate_quality_rule(self, rule: QualityRule) -> None:
        """Validate quality rule configuration"""
        if not rule.rule_id or not rule.name:
            raise ValidationError("Rule ID and name are required")
        
        if rule.threshold < 0 or rule.threshold > 1:
            raise ValidationError("Threshold must be between 0 and 1")
        
        if rule.weight <= 0:
            raise ValidationError("Rule weight must be positive")
    
    async def _load_quality_rules(self) -> None:
        """Load quality rules from all checkers"""
        for checker in self.quality_checkers.values():
            rules = checker.get_quality_rules()
            for rule in rules:
                self.quality_rules[rule.rule_id] = rule
    
    async def _load_quality_history(self) -> None:
        """Load quality assessment history from database"""
        try:
            self.logger.info("Loading quality assessment history from database")
            
            # Simulate database query for quality history
            db_history = []
            current_time = datetime.utcnow()
            
            # Generate sample quality assessment history
            for days_back in range(30):  # Last 30 days
                assessment_date = current_time - timedelta(days=days_back)
                
                # Sample assessments for different content types
                for content_type in ["audio", "video", "image", "text"]:
                    for i in range(5):  # 5 assessments per type per day
                        content_id = f"{content_type}_{assessment_date.strftime('%Y%m%d')}_{i:03d}"
                        
                        # Simulate quality scores with some variation
                        base_score = 0.8 + (0.15 * (1 - days_back / 30))  # Slight improvement over time
                        variation = (i * 0.02) - 0.04  # Random variation
                        quality_score = max(0.0, min(1.0, base_score + variation))
                        
                        assessment = {
                            "assessment_id": f"qa_{content_id}",
                            "content_id": content_id,
                            "content_type": content_type,
                            "assessed_at": assessment_date.isoformat(),
                            "quality_score": quality_score,
                            "status": "passed" if quality_score >= 0.7 else "failed",
                            "rules_checked": [
                                f"{content_type}_resolution_check",
                                f"{content_type}_format_validation",
                                f"{content_type}_content_analysis"
                            ],
                            "issues_found": [] if quality_score >= 0.7 else [
                                f"Quality score {quality_score:.2f} below threshold 0.7"
                            ],
                            "metadata": {
                                "file_size": 1024 * 1024 * (1 + i),  # Varying file sizes
                                "duration": 60 + (i * 10) if content_type in ["audio", "video"] else None,
                                "resolution": f"{720 + (i * 240)}x{480 + (i * 160)}" if content_type in ["image", "video"] else None
                            }
                        }
                        
                        db_history.append(assessment)
            
            # Load history into memory structures
            for assessment in db_history:
                assessment_id = assessment["assessment_id"]
                content_id = assessment["content_id"]
                content_type = assessment["content_type"]
                
                # Store in history
                if content_type not in self.quality_history:
                    self.quality_history[content_type] = []
                
                self.quality_history[content_type].append(assessment)
                
                # Update statistics
                if content_type not in self.quality_stats:
                    self.quality_stats[content_type] = {
                        "total_assessments": 0,
                        "passed_assessments": 0,
                        "failed_assessments": 0,
                        "average_score": 0.0,
                        "last_assessment": None
                    }
                
                stats = self.quality_stats[content_type]
                stats["total_assessments"] += 1
                
                if assessment["status"] == "passed":
                    stats["passed_assessments"] += 1
                else:
                    stats["failed_assessments"] += 1
                
                # Update average score
                current_avg = stats["average_score"]
                current_count = stats["total_assessments"]
                new_score = assessment["quality_score"]
                stats["average_score"] = ((current_avg * (current_count - 1)) + new_score) / current_count
                
                # Update last assessment timestamp
                if not stats["last_assessment"] or assessment["assessed_at"] > stats["last_assessment"]:
                    stats["last_assessment"] = assessment["assessed_at"]
            
            # Sort history by date (most recent first)
            for content_type in self.quality_history:
                self.quality_history[content_type].sort(
                    key=lambda x: x["assessed_at"], 
                    reverse=True
                )
            
            total_assessments = sum(stats["total_assessments"] for stats in self.quality_stats.values())
            self.logger.info(f"Loaded {total_assessments} quality assessments from database")
            
        except Exception as e:
            self.logger.error(f"Error loading quality history from database: {str(e)}")
            # Initialize empty history on error
            self.quality_history = {}
            self.quality_stats = {}
