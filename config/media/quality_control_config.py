"""
Quality Control Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Quality Control Configuration Module
import asyncio

==============================================

Enterprise-grade quality control configuration for the Ainflue platform.
Comprehensive media quality assessment, validation, automated testing,
and quality assurance for video, audio, and image content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

class QualityLevel(str, Enum):
    """Quality levels"""
    EXCELLENT = "excellent"     # 90-100%
    GOOD = "good"              # 75-89%
    ACCEPTABLE = "acceptable"   # 60-74%
    POOR = "poor"              # 40-59%
    UNACCEPTABLE = "unacceptable"  # 0-39%

class QualityMetricType(str, Enum):
    """Quality metric types"""
    # Video metrics
    PSNR = "psnr"                    # Peak Signal-to-Noise Ratio
    SSIM = "ssim"                    # Structural Similarity Index
    VMAF = "vmaf"                    # Video Multimethod Assessment Fusion
    LPIPS = "lpips"                  # Learned Perceptual Image Patch Similarity
    DSSIM = "dssim"                  # Structural Dissimilarity
    MSE = "mse"                      # Mean Squared Error
    BUTTERAUGLI = "butteraugli"      # Psychovisual similarity
    
    # Audio metrics
    SNR = "snr"                      # Signal-to-Noise Ratio
    THD = "thd"                      # Total Harmonic Distortion
    PESQ = "pesq"                    # Perceptual Evaluation of Speech Quality
    STOI = "stoi"                    # Short-Time Objective Intelligibility
    LOUDNESS = "loudness"            # Loudness measurement (LUFS)
    DYNAMIC_RANGE = "dynamic_range"   # Dynamic range measurement
    
    # Image metrics
    SHARPNESS = "sharpness"          # Image sharpness
    CONTRAST = "contrast"            # Image contrast
    BRIGHTNESS = "brightness"        # Image brightness
    COLOR_ACCURACY = "color_accuracy" # Color accuracy
    NOISE_LEVEL = "noise_level"      # Image noise level
    
    # Technical metrics
    BITRATE = "bitrate"              # Bitrate consistency
    FRAMERATE = "framerate"          # Frame rate stability
    RESOLUTION = "resolution"        # Resolution compliance
    CODEC_COMPLIANCE = "codec_compliance"  # Codec standard compliance
    FILE_SIZE = "file_size"          # File size optimization
    
    # Content metrics
    CONTENT_APPROPRIATENESS = "content_appropriateness"  # Content appropriateness
    SPEECH_CLARITY = "speech_clarity"                    # Speech clarity
    VISUAL_CLARITY = "visual_clarity"                    # Visual clarity
    AUDIO_CLARITY = "audio_clarity"                      # Audio clarity

class TestSeverity(str, Enum):
    """Test severity levels"""
    CRITICAL = "critical"       # Must pass for content to be acceptable
    HIGH = "high"              # Important quality factors
    MEDIUM = "medium"          # Standard quality checks
    LOW = "low"                # Nice-to-have quality factors
    INFO = "info"              # Informational only

class MediaType(str, Enum):
    """Media types for quality control"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    LIVE_STREAM = "live_stream"
    DOCUMENT = "document"
    SUBTITLE = "subtitle"
    METADATA = "metadata"

@dataclass
class QualityThreshold:
    """Quality threshold definition"""
    metric_type: QualityMetricType
    min_value: Optional[float] = None      # Minimum acceptable value
    max_value: Optional[float] = None      # Maximum acceptable value
    target_value: Optional[float] = None   # Target/ideal value
    tolerance: float = 0.0                 # Tolerance range around target
    
    # Scoring
    excellent_threshold: float = 90.0      # Score for excellent quality
    good_threshold: float = 75.0           # Score for good quality
    acceptable_threshold: float = 60.0     # Score for acceptable quality
    
    # Test configuration
    severity: TestSeverity = TestSeverity.MEDIUM
    enabled: bool = True
    weight: float = 1.0                    # Weight in overall score calculation
    
    def evaluate_score(self, measured_value: float) -> Tuple[float, QualityLevel]:
        """Evaluate quality score for measured value"""
        
        # Handle min/max bounds
        if self.min_value is not None and measured_value < self.min_value:
            return 0.0, QualityLevel.UNACCEPTABLE
        
        if self.max_value is not None and measured_value > self.max_value:
            return 0.0, QualityLevel.UNACCEPTABLE
        
        # Calculate score based on target value if available
        if self.target_value is not None:
            distance_from_target = abs(measured_value - self.target_value)
            
            # If within tolerance, score is excellent
            if distance_from_target <= self.tolerance:
                score = 100.0
            else:
                # Linear decrease from target
                max_distance = max(
                    abs(self.max_value - self.target_value) if self.max_value else 100,
                    abs(self.min_value - self.target_value) if self.min_value else 100
                )
                score = max(0.0, 100.0 - (distance_from_target / max_distance * 100))
        else:
            # Simple range-based scoring
            if self.min_value is not None and self.max_value is not None:
                range_size = self.max_value - self.min_value
                position = (measured_value - self.min_value) / range_size
                score = position * 100
            else:
                score = min(measured_value, 100.0)  # Assume 0-100 scale
        
        # Determine quality level
        if score >= self.excellent_threshold:
            level = QualityLevel.EXCELLENT
        elif score >= self.good_threshold:
            level = QualityLevel.GOOD
        elif score >= self.acceptable_threshold:
            level = QualityLevel.ACCEPTABLE
        elif score >= 40.0:
            level = QualityLevel.POOR
        else:
            level = QualityLevel.UNACCEPTABLE
        
        return score, level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_type": self.metric_type.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "target_value": self.target_value,
            "tolerance": self.tolerance,
            "excellent_threshold": self.excellent_threshold,
            "good_threshold": self.good_threshold,
            "acceptable_threshold": self.acceptable_threshold,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "weight": self.weight
        }

@dataclass
class QualityTestResult:
    """Quality test result"""
    test_id: str
    metric_type: QualityMetricType
    measured_value: float
    score: float
    quality_level: QualityLevel
    threshold: QualityThreshold
    
    # Test metadata
    timestamp: datetime = field(default_factory=datetime.now)
    test_duration_seconds: float = 0.0
    passed: bool = True
    
    # Additional data
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "test_id": self.test_id,
            "metric_type": self.metric_type.value,
            "measured_value": self.measured_value,
            "score": self.score,
            "quality_level": self.quality_level.value,
            "threshold": self.threshold.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "test_duration_seconds": self.test_duration_seconds,
            "passed": self.passed,
            "details": self.details,
            "error_message": self.error_message,
            "warnings": self.warnings
        }

@dataclass
class QualityAssessment:
    """Complete quality assessment"""
    assessment_id: str
    file_path: str
    media_type: MediaType
    user_id: str
    
    # Test results
    test_results: List[QualityTestResult] = field(default_factory=list)
    
    # Overall scores
    overall_score: float = 0.0
    overall_quality_level: QualityLevel = QualityLevel.UNACCEPTABLE
    
    # Assessment metadata
    assessment_started: datetime = field(default_factory=datetime.now)
    assessment_completed: Optional[datetime] = None
    assessment_duration_seconds: float = 0.0
    
    # File information
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    resolution: str = ""
    codec: str = ""
    bitrate_kbps: int = 0
    
    # Status
    status: str = "pending"         # pending, running, completed, failed
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    critical_failures: int = 0
    
    # Issues and recommendations
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Processing information
    processor_id: str = ""
    error_message: str = ""
    
    def calculate_overall_score(self) -> None:
        """Calculate overall quality score"""
        
        if not self.test_results:
            self.overall_score = 0.0
            self.overall_quality_level = QualityLevel.UNACCEPTABLE
            return
        
        # Calculate weighted average
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for result in self.test_results:
            weight = result.threshold.weight
            total_weighted_score += result.score * weight
            total_weight += weight
        
        if total_weight > 0:
            self.overall_score = total_weighted_score / total_weight
        else:
            self.overall_score = 0.0
        
        # Determine overall quality level
        if self.overall_score >= 90.0:
            self.overall_quality_level = QualityLevel.EXCELLENT
        elif self.overall_score >= 75.0:
            self.overall_quality_level = QualityLevel.GOOD
        elif self.overall_score >= 60.0:
            self.overall_quality_level = QualityLevel.ACCEPTABLE
        elif self.overall_score >= 40.0:
            self.overall_quality_level = QualityLevel.POOR
        else:
            self.overall_quality_level = QualityLevel.UNACCEPTABLE
    
    def update_test_counts(self) -> None:
        """Update test count statistics"""
        self.total_tests = len(self.test_results)
        self.passed_tests = sum(1 for r in self.test_results if r.passed)
        self.failed_tests = self.total_tests - self.passed_tests
        self.critical_failures = sum(
            1 for r in self.test_results 
            if not r.passed and r.threshold.severity == TestSeverity.CRITICAL
        )
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality assessment summary"""
        
        # Group results by metric type
        results_by_type = {}
        for result in self.test_results:
            metric_type = result.metric_type.value
            if metric_type not in results_by_type:
                results_by_type[metric_type] = []
            results_by_type[metric_type].append(result)
        
        # Calculate category scores
        category_scores = {}
        for metric_type, results in results_by_type.items():
            if results:
                avg_score = sum(r.score for r in results) / len(results)
                category_scores[metric_type] = {
                    "average_score": avg_score,
                    "test_count": len(results),
                    "passed_count": sum(1 for r in results if r.passed)
                }
        
        return {
            "assessment_id": self.assessment_id,
            "overall_score": self.overall_score,
            "overall_quality_level": self.overall_quality_level.value,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "critical_failures": self.critical_failures,
            "category_scores": category_scores,
            "issues_count": len(self.issues),
            "recommendations_count": len(self.recommendations),
            "assessment_duration_seconds": self.assessment_duration_seconds,
            "status": self.status
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "assessment_id": self.assessment_id,
            "file_path": self.file_path,
            "media_type": self.media_type.value,
            "user_id": self.user_id,
            "test_results": [r.to_dict() for r in self.test_results],
            "overall_score": self.overall_score,
            "overall_quality_level": self.overall_quality_level.value,
            "assessment_started": self.assessment_started.isoformat(),
            "assessment_completed": self.assessment_completed.isoformat() if self.assessment_completed else None,
            "assessment_duration_seconds": self.assessment_duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "codec": self.codec,
            "bitrate_kbps": self.bitrate_kbps,
            "status": self.status,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "critical_failures": self.critical_failures,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "processor_id": self.processor_id,
            "error_message": self.error_message,
            "quality_summary": self.get_quality_summary()
        }

@dataclass
class QualityProfile:
    """Quality control profile"""
    profile_id: str
    name: str
    description: str
    media_type: MediaType
    
    # Quality thresholds
    thresholds: List[QualityThreshold] = field(default_factory=list)
    
    # Profile settings
    auto_reject_on_critical_failure: bool = True
    auto_approve_on_excellent: bool = False
    require_manual_review: bool = False
    
    # Processing settings
    parallel_testing: bool = True
    timeout_seconds: int = 300
    
    # Notification settings
    notify_on_failure: bool = True
    notify_on_completion: bool = False
    
    # Metadata
    enabled: bool = True
    priority: int = 5
    created_date: datetime = field(default_factory=datetime.now)
    
    def get_threshold_by_metric(self, metric_type: QualityMetricType) -> Optional[QualityThreshold]:
        """Get threshold for specific metric type"""
        for threshold in self.thresholds:
            if threshold.metric_type == metric_type and threshold.enabled:
                return threshold
        return None
    
    def get_critical_thresholds(self) -> List[QualityThreshold]:
        """Get critical thresholds"""
        return [t for t in self.thresholds if t.severity == TestSeverity.CRITICAL and t.enabled]
    
    def calculate_complexity_score(self) -> int:
        """Calculate profile complexity score (1-10)"""
        complexity = len(self.thresholds)
        
        # Add complexity for advanced metrics
        advanced_metrics = [
            QualityMetricType.VMAF, QualityMetricType.LPIPS, 
            QualityMetricType.BUTTERAUGLI, QualityMetricType.PESQ
        ]
        
        for threshold in self.thresholds:
            if threshold.metric_type in advanced_metrics:
                complexity += 2
        
        return min(complexity, 10)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "media_type": self.media_type.value,
            "thresholds": [t.to_dict() for t in self.thresholds],
            "auto_reject_on_critical_failure": self.auto_reject_on_critical_failure,
            "auto_approve_on_excellent": self.auto_approve_on_excellent,
            "require_manual_review": self.require_manual_review,
            "parallel_testing": self.parallel_testing,
            "timeout_seconds": self.timeout_seconds,
            "notify_on_failure": self.notify_on_failure,
            "notify_on_completion": self.notify_on_completion,
            "enabled": self.enabled,
            "priority": self.priority,
            "complexity_score": self.calculate_complexity_score(),
            "critical_thresholds_count": len(self.get_critical_thresholds()),
            "total_thresholds_count": len(self.thresholds),
            "created_date": self.created_date.isoformat()
        }

class QualityControlConfiguration:
    """Main quality control configuration manager"""
    
    def __init__(self) -> None:
        """Initialize quality control configuration"""
        # Data storage
        self.profiles: Dict[str, QualityProfile] = {}
        self.assessments: Dict[str, QualityAssessment] = {}
        self.test_results: List[QualityTestResult] = []
        
        # Global settings
        self.quality_control_enabled = True
        self.auto_quality_assessment = True
        self.real_time_monitoring = True
        self.batch_processing = True
        
        # Performance settings
        self.performance_settings = {
            "max_concurrent_assessments": 5,
            "max_assessment_duration_hours": 2,
            "cleanup_old_results_days": 30,
            "enable_caching": True,
            "cache_duration_hours": 24,
            "parallel_metric_calculation": True,
            "use_gpu_acceleration": True
        }
        
        # Quality settings
        self.quality_settings = {
            "default_quality_threshold": 75.0,
            "critical_failure_threshold": 40.0,
            "auto_retry_failed_tests": True,
            "max_retry_attempts": 3,
            "quality_trend_analysis": True,
            "predictive_quality_scoring": True,
            "adaptive_thresholds": False
        }
        
        # Monitoring settings
        self.monitoring_settings = {
            "real_time_alerts": True,
            "quality_degradation_detection": True,
            "trending_quality_analysis": True,
            "anomaly_detection": True,
            "performance_impact_monitoring": True,
            "quality_dashboard": True,
            "automated_reporting": True
        }
        
        # Notification settings
        self.notification_settings = {
            "webhook_notifications": True,
            "email_notifications": True,
            "slack_notifications": False,
            "critical_failure_immediate_alert": True,
            "quality_degradation_alerts": True,
            "daily_quality_reports": True,
            "weekly_quality_summaries": True
        }
        
        # Integration settings
        self.integration_settings = {
            "ffmpeg_integration": True,
            "opencv_integration": True,
            "machine_learning_quality_prediction": True,
            "cloud_processing": False,
            "external_quality_apis": False,
            "custom_metric_plugins": True
        }
        
        # Initialize default profiles
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self) -> None:
        """Initialize default quality control profiles"""
        
        # Video quality profile
        video_profile = QualityProfile(
            profile_id="standard_video_quality",
            name="Standard Video Quality",
            description="Standard quality control for video content",
            media_type=MediaType.VIDEO,
            thresholds=[
                # Video technical quality
                QualityThreshold(
                    metric_type=QualityMetricType.SSIM,
                    min_value=0.8,
                    target_value=0.95,
                    tolerance=0.05,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.VMAF,
                    min_value=70.0,
                    target_value=85.0,
                    tolerance=5.0,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.PSNR,
                    min_value=25.0,
                    target_value=35.0,
                    tolerance=2.0,
                    severity=TestSeverity.MEDIUM,
                    weight=1.5
                ),
                
                # Technical compliance
                QualityThreshold(
                    metric_type=QualityMetricType.FRAMERATE,
                    min_value=24.0,
                    max_value=60.0,
                    target_value=30.0,
                    tolerance=2.0,
                    severity=TestSeverity.CRITICAL,
                    weight=1.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.RESOLUTION,
                    min_value=480.0,  # Minimum height
                    severity=TestSeverity.CRITICAL,
                    weight=1.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.BITRATE,
                    min_value=500.0,   # kbps
                    max_value=10000.0, # kbps
                    severity=TestSeverity.MEDIUM,
                    weight=1.0
                ),
                
                # Content quality
                QualityThreshold(
                    metric_type=QualityMetricType.VISUAL_CLARITY,
                    min_value=70.0,
                    target_value=85.0,
                    severity=TestSeverity.HIGH,
                    weight=1.5
                )
            ],
            auto_reject_on_critical_failure=True,
            parallel_testing=True,
            timeout_seconds=600
        )
        
        self.profiles[video_profile.profile_id] = video_profile
        
        # Audio quality profile
        audio_profile = QualityProfile(
            profile_id="standard_audio_quality",
            name="Standard Audio Quality",
            description="Standard quality control for audio content",
            media_type=MediaType.AUDIO,
            thresholds=[
                # Audio technical quality
                QualityThreshold(
                    metric_type=QualityMetricType.SNR,
                    min_value=40.0,
                    target_value=60.0,
                    tolerance=5.0,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.THD,
                    max_value=1.0,    # Maximum 1% THD
                    target_value=0.1, # Target 0.1% THD
                    tolerance=0.1,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.LOUDNESS,
                    min_value=-30.0,  # LUFS
                    max_value=-14.0,  # LUFS
                    target_value=-23.0, # Standard for streaming
                    tolerance=2.0,
                    severity=TestSeverity.MEDIUM,
                    weight=1.5
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.DYNAMIC_RANGE,
                    min_value=6.0,    # LU
                    target_value=12.0,
                    severity=TestSeverity.MEDIUM,
                    weight=1.0
                ),
                
                # Content quality
                QualityThreshold(
                    metric_type=QualityMetricType.AUDIO_CLARITY,
                    min_value=70.0,
                    target_value=85.0,
                    severity=TestSeverity.HIGH,
                    weight=1.5
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.SPEECH_CLARITY,
                    min_value=75.0,
                    target_value=90.0,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                )
            ],
            auto_reject_on_critical_failure=True,
            parallel_testing=True,
            timeout_seconds=300
        )
        
        self.profiles[audio_profile.profile_id] = audio_profile
        
        # Image quality profile
        image_profile = QualityProfile(
            profile_id="standard_image_quality",
            name="Standard Image Quality",
            description="Standard quality control for image content",
            media_type=MediaType.IMAGE,
            thresholds=[
                # Image technical quality
                QualityThreshold(
                    metric_type=QualityMetricType.SHARPNESS,
                    min_value=70.0,
                    target_value=85.0,
                    tolerance=5.0,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.CONTRAST,
                    min_value=60.0,
                    target_value=80.0,
                    tolerance=10.0,
                    severity=TestSeverity.MEDIUM,
                    weight=1.5
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.BRIGHTNESS,
                    min_value=40.0,
                    max_value=90.0,
                    target_value=65.0,
                    tolerance=15.0,
                    severity=TestSeverity.MEDIUM,
                    weight=1.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.COLOR_ACCURACY,
                    min_value=75.0,
                    target_value=90.0,
                    tolerance=5.0,
                    severity=TestSeverity.HIGH,
                    weight=1.5
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.NOISE_LEVEL,
                    max_value=20.0,   # Maximum noise level
                    target_value=5.0,
                    tolerance=3.0,
                    severity=TestSeverity.MEDIUM,
                    weight=1.5
                ),
                
                # Technical requirements
                QualityThreshold(
                    metric_type=QualityMetricType.RESOLUTION,
                    min_value=720.0,  # Minimum width
                    severity=TestSeverity.CRITICAL,
                    weight=1.0
                )
            ],
            auto_reject_on_critical_failure=True,
            parallel_testing=True,
            timeout_seconds=120
        )
        
        self.profiles[image_profile.profile_id] = image_profile
        
        # Live stream quality profile
        live_stream_profile = QualityProfile(
            profile_id="live_stream_quality",
            name="Live Stream Quality",
            description="Real-time quality control for live streaming",
            media_type=MediaType.LIVE_STREAM,
            thresholds=[
                # Stream stability
                QualityThreshold(
                    metric_type=QualityMetricType.FRAMERATE,
                    min_value=25.0,
                    target_value=30.0,
                    tolerance=2.0,
                    severity=TestSeverity.CRITICAL,
                    weight=2.0
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.BITRATE,
                    min_value=1000.0,  # kbps
                    max_value=8000.0,  # kbps
                    target_value=2500.0,
                    tolerance=500.0,
                    severity=TestSeverity.HIGH,
                    weight=2.0
                ),
                
                # Audio/video sync and quality
                QualityThreshold(
                    metric_type=QualityMetricType.VISUAL_CLARITY,
                    min_value=60.0,
                    target_value=75.0,
                    severity=TestSeverity.HIGH,
                    weight=1.5
                ),
                QualityThreshold(
                    metric_type=QualityMetricType.AUDIO_CLARITY,
                    min_value=65.0,
                    target_value=80.0,
                    severity=TestSeverity.HIGH,
                    weight=1.5
                )
            ],
            auto_reject_on_critical_failure=False,  # Don't auto-reject live streams
            require_manual_review=True,
            parallel_testing=True,
            timeout_seconds=60,
            notify_on_failure=True
        )
        
        self.profiles[live_stream_profile.profile_id] = live_stream_profile
    
    def create_quality_assessment(self, assessment_data: Dict[str, Any]) -> QualityAssessment:
        """Create quality assessment"""
        
        assessment = QualityAssessment(
            assessment_id=assessment_data.get("assessment_id", f"qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            file_path=assessment_data["file_path"],
            media_type=MediaType(assessment_data["media_type"]),
            user_id=assessment_data["user_id"],
            file_size_bytes=assessment_data.get("file_size_bytes", 0),
            duration_seconds=assessment_data.get("duration_seconds", 0.0),
            resolution=assessment_data.get("resolution", ""),
            codec=assessment_data.get("codec", ""),
            bitrate_kbps=assessment_data.get("bitrate_kbps", 0),
            processor_id=assessment_data.get("processor_id", "")
        )
        
        self.assessments[assessment.assessment_id] = assessment
        return assessment
    
    async def run_quality_assessment(self, assessment_id: str, profile_id: str) -> Dict[str, Any]:
        """Run quality assessment"""
        
        result = {
            "success": False,
            "assessment_id": assessment_id,
            "overall_score": 0.0,
            "quality_level": QualityLevel.UNACCEPTABLE.value,
            "error": None
        }
        
        try:
            if assessment_id not in self.assessments:
                result["error"] = f"Assessment {assessment_id} not found"
                return result
            
            if profile_id not in self.profiles:
                result["error"] = f"Profile {profile_id} not found"
                return result
            
            assessment = self.assessments[assessment_id]
            profile = self.profiles[profile_id]
            
            # Update assessment status
            assessment.status = "running"
            assessment.assessment_started = datetime.now()
            
            # Run quality tests
            test_results = await self._run_quality_tests(assessment, profile)
            
            # Update assessment with results
            assessment.test_results = test_results
            assessment.calculate_overall_score()
            assessment.update_test_counts()
            assessment.assessment_completed = datetime.now()
            assessment.assessment_duration_seconds = (
                assessment.assessment_completed - assessment.assessment_started
            ).total_seconds()
            assessment.status = "completed"
            
            # Generate recommendations
            assessment.recommendations = self._generate_recommendations(assessment, profile)
            
            # Check for auto actions
            auto_action = self._check_auto_actions(assessment, profile)
            
            result.update({
                "success": True,
                "overall_score": assessment.overall_score,
                "quality_level": assessment.overall_quality_level.value,
                "total_tests": assessment.total_tests,
                "passed_tests": assessment.passed_tests,
                "failed_tests": assessment.failed_tests,
                "critical_failures": assessment.critical_failures,
                "auto_action": auto_action,
                "recommendations_count": len(assessment.recommendations)
            })
        
        except Exception as e:
            if assessment_id in self.assessments:
                self.assessments[assessment_id].status = "failed"
                self.assessments[assessment_id].error_message = str(e)
            result["error"] = str(e)
        
        return result
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality control statistics"""
        
        stats = {
            "total_assessments": len(self.assessments),
            "total_profiles": len(self.profiles),
            "total_test_results": len(self.test_results),
            "assessments_by_status": {},
            "assessments_by_media_type": {},
            "quality_level_distribution": {},
            "average_overall_score": 0.0,
            "average_assessment_duration": 0.0,
            "critical_failure_rate": 0.0
        }
        
        # Calculate statistics
        total_scores = []
        total_durations = []
        total_critical_failures = 0
        
        for assessment in self.assessments.values():
            # Count by status
            status = assessment.status
            stats["assessments_by_status"][status] = stats["assessments_by_status"].get(status, 0) + 1
            
            # Count by media type
            media_type = assessment.media_type.value
            stats["assessments_by_media_type"][media_type] = stats["assessments_by_media_type"].get(media_type, 0) + 1
            
            # Quality level distribution
            if assessment.status == "completed":
                quality_level = assessment.overall_quality_level.value
                stats["quality_level_distribution"][quality_level] = stats["quality_level_distribution"].get(quality_level, 0) + 1
                
                total_scores.append(assessment.overall_score)
                total_durations.append(assessment.assessment_duration_seconds)
                total_critical_failures += assessment.critical_failures
        
        # Calculate averages
        if total_scores:
            stats["average_overall_score"] = sum(total_scores) / len(total_scores)
        
        if total_durations:
            stats["average_assessment_duration"] = sum(total_durations) / len(total_durations)
        
        if self.assessments:
            stats["critical_failure_rate"] = (total_critical_failures / len(self.assessments)) * 100
        
        return stats
    
    def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get quality trends"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent assessments
        recent_assessments = [
            a for a in self.assessments.values()
            if a.assessment_started > cutoff_date and a.status == "completed"
        ]
        
        if not recent_assessments:
            return {
                "period_days": days,
                "assessments_count": 0,
                "trends": {}
            }
        
        # Group by date
        daily_scores = {}
        for assessment in recent_assessments:
            date_key = assessment.assessment_started.date().isoformat()
            if date_key not in daily_scores:
                daily_scores[date_key] = []
            daily_scores[date_key].append(assessment.overall_score)
        
        # Calculate daily averages
        daily_averages = {}
        for date_key, scores in daily_scores.items():
            daily_averages[date_key] = sum(scores) / len(scores)
        
        # Calculate trend
        dates = sorted(daily_averages.keys())
        if len(dates) >= 2:
            first_avg = daily_averages[dates[0]]
            last_avg = daily_averages[dates[-1]]
            trend_direction = "improving" if last_avg > first_avg else "declining" if last_avg < first_avg else "stable"
            trend_change = last_avg - first_avg
        else:
            trend_direction = "insufficient_data"
            trend_change = 0.0
        
        return {
            "period_days": days,
            "assessments_count": len(recent_assessments),
            "daily_averages": daily_averages,
            "trend_direction": trend_direction,
            "trend_change": trend_change,
            "current_average": statistics.mean([a.overall_score for a in recent_assessments]),
            "quality_consistency": statistics.stdev([a.overall_score for a in recent_assessments]) if len(recent_assessments) > 1 else 0.0
        }
    
    def search_assessments(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search quality assessments"""
        
        matching_assessments = []
        
        for assessment in self.assessments.values():
            if self._matches_assessment_criteria(assessment, search_criteria):
                matching_assessments.append(assessment.to_dict())
        
        # Sort by assessment date (descending)
        matching_assessments.sort(key=lambda x: x["assessment_started"], reverse=True)
        
        return matching_assessments
    
    # Helper methods
    async def _run_quality_tests(self, assessment: QualityAssessment, 
                                profile: QualityProfile) -> List[QualityTestResult]:
        """Run quality tests for assessment"""
        
        test_results = []
        
        for threshold in profile.thresholds:
            if not threshold.enabled:
                continue
            
            # Simulate quality test execution
            measured_value = await self._execute_quality_test(assessment, threshold)
            
            # Evaluate score
            score, quality_level = threshold.evaluate_score(measured_value)
            
            # Create test result
            test_result = QualityTestResult(
                test_id=f"test_{threshold.metric_type.value}_{datetime.now().strftime('%H%M%S')}",
                metric_type=threshold.metric_type,
                measured_value=measured_value,
                score=score,
                quality_level=quality_level,
                threshold=threshold,
                passed=score >= threshold.acceptable_threshold,
                test_duration_seconds=1.0  # Simulated duration
            )
            
            test_results.append(test_result)
            self.test_results.append(test_result)
        
        return test_results
    
    async def _execute_quality_test(self, assessment: QualityAssessment, 
                                  threshold: QualityThreshold) -> float:
        """Execute individual quality test"""
        
        # Simulate quality measurement
        import random
        
        if threshold.target_value is not None:
            # Generate value around target with some randomness
            base_value = threshold.target_value
            variation = random.uniform(-10, 10)
            measured_value = base_value + variation
        elif threshold.min_value is not None and threshold.max_value is not None:
            # Generate value within range
            measured_value = random.uniform(threshold.min_value, threshold.max_value)
        else:
            # Default to 0-100 scale
            measured_value = random.uniform(50, 95)
        
        # Ensure bounds
        if threshold.min_value is not None:
            measured_value = max(measured_value, threshold.min_value)
        if threshold.max_value is not None:
            measured_value = min(measured_value, threshold.max_value)
        
        return measured_value
    
    def _generate_recommendations(self, assessment: QualityAssessment, 
                                 profile: QualityProfile) -> List[str]:
        """Generate quality improvement recommendations"""
        
        recommendations = []
        
        # Analyze failed tests
        failed_tests = [r for r in assessment.test_results if not r.passed]
        
        for test in failed_tests:
            metric_type = test.metric_type
            
            if metric_type == QualityMetricType.SSIM and test.measured_value < 0.8:
                recommendations.append("Consider using higher quality encoding settings to improve structural similarity")
            
            elif metric_type == QualityMetricType.VMAF and test.measured_value < 70:
                recommendations.append("Increase bitrate or use slower encoding preset to improve perceptual quality")
            
            elif metric_type == QualityMetricType.BITRATE and test.measured_value < test.threshold.min_value:
                recommendations.append("Increase encoding bitrate to meet minimum quality requirements")
            
            elif metric_type == QualityMetricType.FRAMERATE:
                recommendations.append("Ensure consistent frame rate throughout the video")
            
            elif metric_type == QualityMetricType.RESOLUTION:
                recommendations.append("Use higher resolution source material or upscaling techniques")
            
            elif metric_type == QualityMetricType.SNR and test.measured_value < 40:
                recommendations.append("Reduce background noise in audio recording or use noise reduction")
            
            elif metric_type == QualityMetricType.LOUDNESS:
                recommendations.append("Adjust audio levels to meet broadcast/streaming standards")
            
            elif metric_type == QualityMetricType.SHARPNESS:
                recommendations.append("Use higher quality capture equipment or post-processing sharpening")
        
        # General recommendations based on overall score
        if assessment.overall_score < 60:
            recommendations.append("Consider reviewing entire production workflow for quality improvements")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _check_auto_actions(self, assessment: QualityAssessment, 
                           profile: QualityProfile) -> str:
        """Check for automatic actions based on assessment results"""
        
        if assessment.critical_failures > 0 and profile.auto_reject_on_critical_failure:
            return "auto_rejected"
        
        elif assessment.overall_quality_level == QualityLevel.EXCELLENT and profile.auto_approve_on_excellent:
            return "auto_approved"
        
        elif profile.require_manual_review:
            return "manual_review_required"
        
        elif assessment.overall_quality_level in [QualityLevel.GOOD, QualityLevel.ACCEPTABLE]:
            return "auto_approved"
        
        else:
            return "manual_review_recommended"
    
    def _matches_assessment_criteria(self, assessment: QualityAssessment, 
                                   criteria: Dict[str, Any]) -> bool:
        """Check if assessment matches search criteria"""
        
        # Check user ID
        if "user_id" in criteria and criteria["user_id"] != assessment.user_id:
            return False
        
        # Check media type
        if "media_type" in criteria and criteria["media_type"] != assessment.media_type.value:
            return False
        
        # Check status
        if "status" in criteria and criteria["status"] != assessment.status:
            return False
        
        # Check quality level
        if "quality_level" in criteria and criteria["quality_level"] != assessment.overall_quality_level.value:
            return False
        
        # Check score range
        if "min_score" in criteria and assessment.overall_score < criteria["min_score"]:
            return False
        
        if "max_score" in criteria and assessment.overall_score > criteria["max_score"]:
            return False
        
        # Check date range
        if "start_date" in criteria:
            start_date = datetime.fromisoformat(criteria["start_date"])
            if assessment.assessment_started < start_date:
                return False
        
        if "end_date" in criteria:
            end_date = datetime.fromisoformat(criteria["end_date"])
            if assessment.assessment_started > end_date:
                return False
        
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete quality control configuration"""
        return {
            "quality_statistics": self.get_quality_statistics(),
            "quality_trends": self.get_quality_trends(),
            "profiles_count": len(self.profiles),
            "assessments_count": len(self.assessments),
            "test_results_count": len(self.test_results),
            "global_settings": {
                "quality_control_enabled": self.quality_control_enabled,
                "auto_quality_assessment": self.auto_quality_assessment,
                "real_time_monitoring": self.real_time_monitoring,
                "batch_processing": self.batch_processing
            },
            "performance_settings": self.performance_settings,
            "quality_settings": self.quality_settings,
            "monitoring_settings": self.monitoring_settings,
            "notification_settings": self.notification_settings,
            "integration_settings": self.integration_settings
        }

# Global quality control configuration instance
quality_control_config = QualityControlConfiguration()

# Export main classes
__all__ = [
    "QualityControlConfiguration",
    "QualityLevel",
    "QualityMetricType",
    "TestSeverity",
    "MediaType",
    "QualityThreshold",
    "QualityTestResult",
    "QualityAssessment",
    "QualityProfile",
    "quality_control_config"
]
