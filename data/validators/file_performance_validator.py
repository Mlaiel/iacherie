"""File Performance Validator - Consolidated File Integrity & Performance Validation
==================================================================================

Industrial-grade file validation and performance assessment system for the
IA Influencer Agent Platform, combining file integrity checks, performance
optimization analysis, and streaming capability validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Consolidated Validation Capabilities:
- File integrity verification and corruption detection
- Performance analysis for encoding/compression optimization
- Multi-platform format compatibility validation
- Streaming capability assessment
- Real-time performance metrics collection
- Auto-optimization recommendations
- Scalability assessment for enterprise deployment
"""

import asyncio
import logging
import hashlib
import mimetypes
import tempfile
import shutil
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import json
import time
import os
import subprocess

logger = logging.getLogger(__name__)

class FileValidationType(Enum):
    """Types of file validation."""
    INTEGRITY = "integrity"
    FORMAT = "format"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    STREAMING = "streaming"
    SECURITY = "security"
    COMPRESSION = "compression"
    ENCODING = "encoding"

class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class FileStatus(Enum):
    """File validation status."""
    VALID = "valid"
    CORRUPTED = "corrupted"
    INCOMPATIBLE = "incompatible"
    SUBOPTIMAL = "suboptimal"
    UNKNOWN = "unknown"

class PerformanceMetricType(Enum):
    """Types of performance metrics."""
    FILE_SIZE = "file_size"
    COMPRESSION_RATIO = "compression_ratio"
    BITRATE = "bitrate"
    RESOLUTION = "resolution"
    FRAME_RATE = "frame_rate"
    SAMPLE_RATE = "sample_rate"
    LOADING_TIME = "loading_time"
    PROCESSING_TIME = "processing_time"
    BANDWIDTH_USAGE = "bandwidth_usage"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"

class PerformanceLevel(Enum):
    """Performance quality levels."""
    POOR = "poor"
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    GOOD = "good"
    EXCELLENT = "excellent"
    OPTIMAL = "optimal"

class OptimizationType(Enum):
    """Types of optimization recommendations."""
    COMPRESSION = "compression"
    ENCODING = "encoding"
    RESOLUTION = "resolution"
    QUALITY = "quality"
    FORMAT_CONVERSION = "format_conversion"
    STREAMING_OPTIMIZATION = "streaming_optimization"
    CACHING = "caching"
    CDN = "cdn"

@dataclass
class FileValidationIssue:
    """File validation issue details."""
    validation_type: FileValidationType
    severity: ValidationSeverity
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    impact: str = "medium"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class FileValidationResult:
    """File validation result."""
    is_valid: bool
    file_status: FileStatus
    file_size: int
    mime_type: Optional[str]
    format_info: Dict[str, Any] = field(default_factory=dict)
    integrity_check: Dict[str, Any] = field(default_factory=dict)
    issues: List[FileValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_duration_ms: int = 0
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class PerformanceMetric:
    """Performance metric measurement."""
    metric_type: PerformanceMetricType
    value: Union[int, float, str]
    unit: str
    benchmark_score: float  # 0.0 to 1.0
    optimal_range: Optional[Tuple[Union[int, float], Union[int, float]]] = None
    measured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class PerformanceIssue:
    """Performance optimization issue."""
    metric_type: PerformanceMetricType
    severity: ValidationSeverity
    description: str
    current_value: Union[int, float, str]
    recommended_value: Optional[Union[int, float, str]] = None
    optimization_type: OptimizationType = OptimizationType.QUALITY
    potential_improvement: float = 0.0  # Percentage improvement

@dataclass
class PerformanceValidationResult:
    """Performance validation result."""
    overall_performance: PerformanceLevel
    performance_score: float
    metrics: List[PerformanceMetric] = field(default_factory=list)
    issues: List[PerformanceIssue] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    streaming_assessment: Dict[str, Any] = field(default_factory=dict)
    platform_compatibility: Dict[str, bool] = field(default_factory=dict)
    estimated_improvements: Dict[str, float] = field(default_factory=dict)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_duration_ms: int = 0

class FilePerformanceValidator:
    """Consolidated file integrity and performance validation system."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the file performance validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.format_specifications = self._load_format_specifications()
        self.performance_benchmarks = self._load_performance_benchmarks()
        self.platform_requirements = self._load_platform_requirements()
        
        # Validation settings
        self.enable_deep_scan = self.config.get('enable_deep_scan', True)
        self.enable_performance_analysis = self.config.get('enable_performance_analysis', True)
        self.enable_auto_optimization = self.config.get('enable_auto_optimization', False)
        self.max_file_size = self.config.get('max_file_size', 1024 * 1024 * 1024)  # 1GB default
        
        logger.info("FilePerformanceValidator initialized")
    
    def _load_format_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Load file format specifications.
        
        Returns:
            Dictionary of format specifications
        """
        specs = {
            'video': {
                'mp4': {
                    'mime_types': ['video/mp4'],
                    'max_size': 8 * 1024 * 1024 * 1024,  # 8GB
                    'recommended_codecs': ['h264', 'h265'],
                    'optimal_bitrate': {'1080p': 8000, '720p': 5000, '480p': 2500},
                    'streaming_compatible': True
                },
                'webm': {
                    'mime_types': ['video/webm'],
                    'max_size': 4 * 1024 * 1024 * 1024,  # 4GB
                    'recommended_codecs': ['vp8', 'vp9'],
                    'optimal_bitrate': {'1080p': 6000, '720p': 4000, '480p': 2000},
                    'streaming_compatible': True
                },
                'mov': {
                    'mime_types': ['video/quicktime'],
                    'max_size': 10 * 1024 * 1024 * 1024,  # 10GB
                    'recommended_codecs': ['h264', 'prores'],
                    'optimal_bitrate': {'1080p': 12000, '720p': 8000, '480p': 4000},
                    'streaming_compatible': False
                }
            },
            'audio': {
                'mp3': {
                    'mime_types': ['audio/mpeg'],
                    'max_size': 500 * 1024 * 1024,  # 500MB
                    'optimal_bitrate': 320,
                    'sample_rates': [44100, 48000],
                    'streaming_compatible': True
                },
                'wav': {
                    'mime_types': ['audio/wav'],
                    'max_size': 2 * 1024 * 1024 * 1024,  # 2GB
                    'optimal_bitrate': 1411,  # 44.1kHz 16-bit stereo
                    'sample_rates': [44100, 48000, 96000],
                    'streaming_compatible': False
                },
                'flac': {
                    'mime_types': ['audio/flac'],
                    'max_size': 1 * 1024 * 1024 * 1024,  # 1GB
                    'compression_ratio': 0.6,
                    'sample_rates': [44100, 48000, 96000, 192000],
                    'streaming_compatible': True
                }
            },
            'image': {
                'jpeg': {
                    'mime_types': ['image/jpeg'],
                    'max_size': 100 * 1024 * 1024,  # 100MB
                    'optimal_quality': 85,
                    'max_dimensions': (8192, 8192),
                    'compression_type': 'lossy'
                },
                'png': {
                    'mime_types': ['image/png'],
                    'max_size': 200 * 1024 * 1024,  # 200MB
                    'max_dimensions': (8192, 8192),
                    'compression_type': 'lossless',
                    'supports_transparency': True
                },
                'webp': {
                    'mime_types': ['image/webp'],
                    'max_size': 50 * 1024 * 1024,  # 50MB
                    'optimal_quality': 80,
                    'max_dimensions': (16383, 16383),
                    'compression_type': 'both',
                    'supports_transparency': True
                }
            }
        }
        return specs
    
    def _load_performance_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Load performance benchmarks for different content types.
        
        Returns:
            Dictionary of performance benchmarks
        """
        benchmarks = {
            'video': {
                'file_size': {
                    '1080p_1min': 100 * 1024 * 1024,  # 100MB per minute
                    '720p_1min': 50 * 1024 * 1024,   # 50MB per minute
                    '480p_1min': 25 * 1024 * 1024    # 25MB per minute
                },
                'loading_time': {
                    'excellent': 2.0,  # seconds
                    'good': 5.0,
                    'acceptable': 10.0
                },
                'compression_efficiency': {
                    'optimal': 0.8,  # Size ratio compared to uncompressed
                    'good': 0.6,
                    'acceptable': 0.4
                }
            },
            'audio': {
                'file_size': {
                    'mp3_320_1min': 2.4 * 1024 * 1024,  # 2.4MB per minute
                    'mp3_128_1min': 1.0 * 1024 * 1024,  # 1MB per minute
                    'flac_1min': 25 * 1024 * 1024       # 25MB per minute
                },
                'loading_time': {
                    'excellent': 1.0,
                    'good': 3.0,
                    'acceptable': 5.0
                },
                'quality_score': {
                    'optimal': 0.95,
                    'good': 0.85,
                    'acceptable': 0.7
                }
            },
            'image': {
                'file_size': {
                    'high_res': 5 * 1024 * 1024,   # 5MB
                    'medium_res': 1 * 1024 * 1024, # 1MB
                    'web_optimized': 500 * 1024    # 500KB
                },
                'loading_time': {
                    'excellent': 0.5,
                    'good': 1.0,
                    'acceptable': 2.0
                },
                'compression_ratio': {
                    'optimal': 0.1,  # 10% of original
                    'good': 0.2,     # 20% of original
                    'acceptable': 0.5 # 50% of original
                }
            }
        }
        return benchmarks
    
    def _load_platform_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific requirements.
        
        Returns:
            Dictionary of platform requirements
        """
        requirements = {
            'youtube': {
                'video': {
                    'max_size': 128 * 1024 * 1024 * 1024,  # 128GB
                    'max_duration': 12 * 3600,  # 12 hours
                    'supported_formats': ['mp4', 'webm', 'mov', 'avi'],
                    'recommended_resolution': ['1080p', '720p', '4K'],
                    'min_bitrate': 1000,
                    'max_bitrate': 68000
                },
                'audio': {
                    'sample_rate': [44100, 48000],
                    'bitrate': [128, 384],
                    'channels': [1, 2]  # Mono or stereo
                }
            },
            'instagram': {
                'video': {
                    'max_size': 4 * 1024 * 1024 * 1024,  # 4GB
                    'max_duration': 3600,  # 60 minutes for IGTV
                    'supported_formats': ['mp4', 'mov'],
                    'aspect_ratios': ['1:1', '4:5', '16:9', '9:16'],
                    'min_resolution': (600, 315),
                    'max_resolution': (1920, 1920)
                },
                'image': {
                    'max_size': 30 * 1024 * 1024,  # 30MB
                    'supported_formats': ['jpeg', 'png', 'gif'],
                    'min_resolution': (320, 320),
                    'max_resolution': (1440, 1440)
                }
            },
            'tiktok': {
                'video': {
                    'max_size': 4 * 1024 * 1024 * 1024,  # 4GB
                    'max_duration': 600,  # 10 minutes
                    'supported_formats': ['mp4', 'mov', 'webm'],
                    'aspect_ratios': ['9:16', '1:1', '16:9'],
                    'min_resolution': (540, 960),
                    'max_resolution': (1080, 1920)
                }
            },
            'spotify': {
                'audio': {
                    'max_size': 200 * 1024 * 1024,  # 200MB
                    'supported_formats': ['mp3', 'wav', 'flac', 'm4a'],
                    'sample_rate': [44100, 48000],
                    'min_bitrate': 96,
                    'recommended_bitrate': 320
                }
            }
        }
        return requirements
    
    async def validate_file(self, file_path: Union[str, Path],
                          validation_types: Optional[List[FileValidationType]] = None) -> FileValidationResult:
        """Validate file integrity and format compliance.
        
        Args:
            file_path: Path to file to validate
            validation_types: Specific validation types to perform
            
        Returns:
            FileValidationResult with validation details
        """
        start_time = datetime.now()
        file_path = Path(file_path)
        issues = []
        recommendations = []
        
        try:
            # Basic file checks
            if not file_path.exists():
                return FileValidationResult(
                    is_valid=False,
                    file_status=FileStatus.UNKNOWN,
                    file_size=0,
                    mime_type=None,
                    issues=[FileValidationIssue(
                        validation_type=FileValidationType.INTEGRITY,
                        severity=ValidationSeverity.CRITICAL,
                        description=f"File not found: {file_path}",
                        remediation="Ensure file exists and path is correct"
                    )],
                    validation_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
            
            # Get file information
            file_size = file_path.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Determine validation types
            if validation_types is None:
                validation_types = [
                    FileValidationType.INTEGRITY,
                    FileValidationType.FORMAT,
                    FileValidationType.PERFORMANCE
                ]
            
            # Perform validations
            format_info = {}
            integrity_check = {}
            
            if FileValidationType.INTEGRITY in validation_types:
                integrity_result = await self._validate_file_integrity(file_path)
                integrity_check = integrity_result
                if not integrity_result['is_valid']:
                    issues.append(FileValidationIssue(
                        validation_type=FileValidationType.INTEGRITY,
                        severity=ValidationSeverity.CRITICAL,
                        description="File integrity check failed",
                        details=integrity_result,
                        remediation="Re-upload or repair the file"
                    ))
            
            if FileValidationType.FORMAT in validation_types:
                format_result = await self._validate_file_format(file_path, mime_type)
                format_info = format_result
                issues.extend(format_result.get('issues', []))
            
            if FileValidationType.PERFORMANCE in validation_types and self.enable_performance_analysis:
                performance_issues = await self._check_performance_issues(file_path, file_size, mime_type)
                issues.extend(performance_issues)
            
            if FileValidationType.SECURITY in validation_types:
                security_issues = await self._check_security_issues(file_path)
                issues.extend(security_issues)
            
            # Generate recommendations
            recommendations = self._generate_file_recommendations(file_path, file_size, mime_type, issues)
            
            # Determine file status
            file_status = self._determine_file_status(issues)
            is_valid = file_status in [FileStatus.VALID, FileStatus.SUBOPTIMAL]
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return FileValidationResult(
                is_valid=is_valid,
                file_status=file_status,
                file_size=file_size,
                mime_type=mime_type,
                format_info=format_info,
                integrity_check=integrity_check,
                issues=issues,
                recommendations=recommendations,
                validation_duration_ms=duration_ms,
                validated_at=start_time
            )
            
        except Exception as e:
            logger.error(f"File validation failed: {e}")
            return FileValidationResult(
                is_valid=False,
                file_status=FileStatus.UNKNOWN,
                file_size=0,
                mime_type=None,
                issues=[FileValidationIssue(
                    validation_type=FileValidationType.INTEGRITY,
                    severity=ValidationSeverity.CRITICAL,
                    description=f"File validation error: {str(e)}",
                    remediation="Check file accessibility and try again"
                )],
                validation_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def assess_performance(self, file_path: Union[str, Path],
                               platforms: Optional[List[str]] = None) -> PerformanceValidationResult:
        """Assess file performance and optimization opportunities.
        
        Args:
            file_path: Path to file to assess
            platforms: Target platforms for compatibility check
            
        Returns:
            PerformanceValidationResult with performance analysis
        """
        start_time = datetime.now()
        file_path = Path(file_path)
        
        try:
            # Basic file information
            file_size = file_path.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Collect performance metrics
            metrics = await self._collect_performance_metrics(file_path, file_size, mime_type)
            
            # Analyze performance issues
            issues = await self._analyze_performance_issues(metrics, file_path)
            
            # Check platform compatibility
            platform_compatibility = {}
            if platforms:
                for platform in platforms:
                    platform_compatibility[platform] = await self._check_platform_compatibility(
                        file_path, platform, metrics
                    )
            
            # Assess streaming capabilities
            streaming_assessment = await self._assess_streaming_capability(file_path, metrics)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                metrics, issues, platform_compatibility
            )
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(metrics, issues)
            overall_performance = self._determine_performance_level(performance_score)
            
            # Estimate potential improvements
            estimated_improvements = self._estimate_improvements(issues, optimization_suggestions)
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return PerformanceValidationResult(
                overall_performance=overall_performance,
                performance_score=performance_score,
                metrics=metrics,
                issues=issues,
                optimization_suggestions=optimization_suggestions,
                streaming_assessment=streaming_assessment,
                platform_compatibility=platform_compatibility,
                estimated_improvements=estimated_improvements,
                assessed_at=start_time,
                assessment_duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error(f"Performance assessment failed: {e}")
            return PerformanceValidationResult(
                overall_performance=PerformanceLevel.POOR,
                performance_score=0.0,
                issues=[PerformanceIssue(
                    metric_type=PerformanceMetricType.PROCESSING_TIME,
                    severity=ValidationSeverity.ERROR,
                    description=f"Performance assessment failed: {str(e)}",
                    current_value="error"
                )],
                assessed_at=start_time,
                assessment_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def _validate_file_integrity(self, file_path: Path) -> Dict[str, Any]:
        """Validate file integrity using checksums and format verification.
        
        Args:
            file_path: Path to file
            
        Returns:
            Integrity validation result
        """
        try:
            # Calculate file hash
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            file_hash = hash_sha256.hexdigest()
            
            # Basic corruption checks
            is_valid = True
            corruption_indicators = []
            
            # Check file size consistency
            stated_size = file_path.stat().st_size
            if stated_size == 0:
                is_valid = False
                corruption_indicators.append("File is empty")
            
            # Check file header consistency (simplified)
            with open(file_path, 'rb') as f:
                header = f.read(16)
                if len(header) < 16:
                    is_valid = False
                    corruption_indicators.append("File header incomplete")
            
            return {
                'is_valid': is_valid,
                'file_hash': file_hash,
                'file_size': stated_size,
                'corruption_indicators': corruption_indicators,
                'integrity_score': 1.0 if is_valid else 0.0
            }
            
        except Exception as e:
            logger.error(f"Integrity validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'integrity_score': 0.0
            }
    
    async def _validate_file_format(self, file_path: Path, mime_type: Optional[str]) -> Dict[str, Any]:
        """Validate file format compliance and specifications.
        
        Args:
            file_path: Path to file
            mime_type: MIME type of file
            
        Returns:
            Format validation result
        """
        issues = []
        format_info = {
            'file_extension': file_path.suffix.lower(),
            'mime_type': mime_type,
            'is_supported': False,
            'format_category': None
        }
        
        try:
            # Determine format category
            if mime_type:
                if mime_type.startswith('video/'):
                    format_info['format_category'] = 'video'
                elif mime_type.startswith('audio/'):
                    format_info['format_category'] = 'audio'
                elif mime_type.startswith('image/'):
                    format_info['format_category'] = 'image'
            
            # Check against specifications
            category = format_info['format_category']
            if category and category in self.format_specifications:
                format_specs = self.format_specifications[category]
                file_ext = file_path.suffix.lower().lstrip('.')
                
                if file_ext in format_specs:
                    format_info['is_supported'] = True
                    spec = format_specs[file_ext]
                    
                    # Check file size limits
                    file_size = file_path.stat().st_size
                    max_size = spec.get('max_size', float('inf'))
                    
                    if file_size > max_size:
                        issues.append(FileValidationIssue(
                            validation_type=FileValidationType.FORMAT,
                            severity=ValidationSeverity.ERROR,
                            description=f"File size {file_size} exceeds maximum {max_size} for {file_ext}",
                            remediation=f"Compress file to under {max_size} bytes"
                        ))
                    
                    # Store specification compliance
                    format_info['specification_compliance'] = {
                        'max_size_compliant': file_size <= max_size,
                        'mime_type_compliant': mime_type in spec.get('mime_types', []),
                        'streaming_compatible': spec.get('streaming_compatible', False)
                    }
                else:
                    issues.append(FileValidationIssue(
                        validation_type=FileValidationType.FORMAT,
                        severity=ValidationSeverity.WARNING,
                        description=f"Unsupported format: {file_ext}",
                        remediation=f"Convert to supported format for {category}"
                    ))
        
        except Exception as e:
            logger.error(f"Format validation failed: {e}")
            issues.append(FileValidationIssue(
                validation_type=FileValidationType.FORMAT,
                severity=ValidationSeverity.ERROR,
                description=f"Format validation error: {str(e)}"
            ))
        
        format_info['issues'] = issues
        return format_info
    
    async def _check_performance_issues(self, file_path: Path, file_size: int,
                                      mime_type: Optional[str]) -> List[FileValidationIssue]:
        """Check for performance-related issues.
        
        Args:
            file_path: Path to file
            file_size: File size in bytes
            mime_type: MIME type
            
        Returns:
            List of performance issues
        """
        issues = []
        
        try:
            # File size performance check
            if file_size > self.max_file_size:
                issues.append(FileValidationIssue(
                    validation_type=FileValidationType.PERFORMANCE,
                    severity=ValidationSeverity.WARNING,
                    description=f"Large file size: {file_size / (1024*1024):.1f}MB",
                    remediation="Consider compression or format optimization",
                    impact="high"
                ))
            
            # Loading time estimation
            estimated_loading_time = file_size / (1024 * 1024)  # Rough estimate: 1MB/s
            if estimated_loading_time > 10:
                issues.append(FileValidationIssue(
                    validation_type=FileValidationType.PERFORMANCE,
                    severity=ValidationSeverity.WARNING,
                    description=f"Slow loading time estimated: {estimated_loading_time:.1f}s",
                    remediation="Optimize file size for faster loading",
                    impact="medium"
                ))
            
            # Format-specific performance checks
            if mime_type and mime_type.startswith('video/'):
                # Video-specific performance issues
                if file_size > 100 * 1024 * 1024:  # 100MB
                    issues.append(FileValidationIssue(
                        validation_type=FileValidationType.PERFORMANCE,
                        severity=ValidationSeverity.INFO,
                        description="Consider video compression for web delivery",
                        remediation="Use more efficient video codecs",
                        impact="low"
                    ))
            
            elif mime_type and mime_type.startswith('image/'):
                # Image-specific performance issues
                if file_size > 5 * 1024 * 1024:  # 5MB
                    issues.append(FileValidationIssue(
                        validation_type=FileValidationType.PERFORMANCE,
                        severity=ValidationSeverity.WARNING,
                        description="Large image file size affects page load speed",
                        remediation="Compress image or use WebP format",
                        impact="medium"
                    ))
        
        except Exception as e:
            logger.error(f"Performance check failed: {e}")
            issues.append(FileValidationIssue(
                validation_type=FileValidationType.PERFORMANCE,
                severity=ValidationSeverity.ERROR,
                description=f"Performance check error: {str(e)}"
            ))
        
        return issues
    
    async def _check_security_issues(self, file_path: Path) -> List[FileValidationIssue]:
        """Check for security-related issues in file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of security issues
        """
        issues = []
        
        try:
            # Check for executable files
            if file_path.suffix.lower() in ['.exe', '.bat', '.sh', '.scr', '.com']:
                issues.append(FileValidationIssue(
                    validation_type=FileValidationType.SECURITY,
                    severity=ValidationSeverity.CRITICAL,
                    description="Executable file detected - security risk",
                    remediation="Remove executable files or scan for malware",
                    impact="critical"
                ))
            
            # Check for suspicious file sizes (very small files that claim to be media)
            file_size = file_path.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            if mime_type and mime_type.startswith(('video/', 'audio/')) and file_size < 1024:
                issues.append(FileValidationIssue(
                    validation_type=FileValidationType.SECURITY,
                    severity=ValidationSeverity.WARNING,
                    description="Suspiciously small media file",
                    remediation="Verify file authenticity",
                    impact="medium"
                ))
            
            # Check file permissions
            if file_path.stat().st_mode & 0o111:  # Executable bit set
                issues.append(FileValidationIssue(
                    validation_type=FileValidationType.SECURITY,
                    severity=ValidationSeverity.WARNING,
                    description="File has executable permissions",
                    remediation="Remove executable permissions if not needed",
                    impact="low"
                ))
        
        except Exception as e:
            logger.error(f"Security check failed: {e}")
            issues.append(FileValidationIssue(
                validation_type=FileValidationType.SECURITY,
                severity=ValidationSeverity.ERROR,
                description=f"Security check error: {str(e)}"
            ))
        
        return issues
    
    async def _collect_performance_metrics(self, file_path: Path, file_size: int,
                                         mime_type: Optional[str]) -> List[PerformanceMetric]:
        """Collect performance metrics for file.
        
        Args:
            file_path: Path to file
            file_size: File size in bytes
            mime_type: MIME type
            
        Returns:
            List of performance metrics
        """
        metrics = []
        
        try:
            # File size metric
            size_mb = file_size / (1024 * 1024)
            size_score = min(1.0, max(0.0, 1.0 - (size_mb / 100)))  # Score based on 100MB threshold
            
            metrics.append(PerformanceMetric(
                metric_type=PerformanceMetricType.FILE_SIZE,
                value=file_size,
                unit="bytes",
                benchmark_score=size_score
            ))
            
            # Loading time estimate
            loading_time = size_mb / 10  # Assume 10MB/s download speed
            loading_score = min(1.0, max(0.0, 1.0 - (loading_time / 10)))  # 10s threshold
            
            metrics.append(PerformanceMetric(
                metric_type=PerformanceMetricType.LOADING_TIME,
                value=loading_time,
                unit="seconds",
                benchmark_score=loading_score,
                optimal_range=(0.0, 5.0)
            ))
            
            # Compression ratio estimate (simplified)
            if mime_type:
                if 'jpeg' in mime_type or 'mp3' in mime_type or 'mp4' in mime_type:
                    compression_ratio = 0.1  # Assume 10:1 compression for lossy formats
                elif 'png' in mime_type or 'flac' in mime_type:
                    compression_ratio = 0.3  # Assume 3:1 compression for lossless formats
                else:
                    compression_ratio = 1.0  # No compression assumed
                
                compression_score = min(1.0, 1.0 - compression_ratio)
                
                metrics.append(PerformanceMetric(
                    metric_type=PerformanceMetricType.COMPRESSION_RATIO,
                    value=compression_ratio,
                    unit="ratio",
                    benchmark_score=compression_score,
                    optimal_range=(0.05, 0.3)
                ))
        
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
        
        return metrics
    
    async def _analyze_performance_issues(self, metrics: List[PerformanceMetric],
                                        file_path: Path) -> List[PerformanceIssue]:
        """Analyze performance metrics to identify issues.
        
        Args:
            metrics: Performance metrics
            file_path: Path to file
            
        Returns:
            List of performance issues
        """
        issues = []
        
        for metric in metrics:
            if metric.benchmark_score < 0.5:  # Below average performance
                severity = ValidationSeverity.WARNING if metric.benchmark_score > 0.2 else ValidationSeverity.ERROR
                
                if metric.metric_type == PerformanceMetricType.FILE_SIZE:
                    issues.append(PerformanceIssue(
                        metric_type=metric.metric_type,
                        severity=severity,
                        description=f"Large file size: {metric.value / (1024*1024):.1f}MB",
                        current_value=f"{metric.value / (1024*1024):.1f}MB",
                        recommended_value="<50MB",
                        optimization_type=OptimizationType.COMPRESSION,
                        potential_improvement=50.0
                    ))
                
                elif metric.metric_type == PerformanceMetricType.LOADING_TIME:
                    issues.append(PerformanceIssue(
                        metric_type=metric.metric_type,
                        severity=severity,
                        description=f"Slow loading time: {metric.value:.1f}s",
                        current_value=f"{metric.value:.1f}s",
                        recommended_value="<5s",
                        optimization_type=OptimizationType.COMPRESSION,
                        potential_improvement=60.0
                    ))
                
                elif metric.metric_type == PerformanceMetricType.COMPRESSION_RATIO:
                    if metric.value > 0.5:  # Poor compression
                        issues.append(PerformanceIssue(
                            metric_type=metric.metric_type,
                            severity=ValidationSeverity.INFO,
                            description=f"Poor compression efficiency: {metric.value:.2f}",
                            current_value=f"{metric.value:.2f}",
                            recommended_value="<0.3",
                            optimization_type=OptimizationType.ENCODING,
                            potential_improvement=40.0
                        ))
        
        return issues
    
    async def _check_platform_compatibility(self, file_path: Path, platform: str,
                                          metrics: List[PerformanceMetric]) -> bool:
        """Check file compatibility with specific platform.
        
        Args:
            file_path: Path to file
            platform: Platform name
            metrics: Performance metrics
            
        Returns:
            True if compatible with platform
        """
        if platform not in self.platform_requirements:
            return False
        
        requirements = self.platform_requirements[platform]
        file_size = file_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        try:
            # Determine content type
            if mime_type and mime_type.startswith('video/'):
                content_type = 'video'
            elif mime_type and mime_type.startswith('audio/'):
                content_type = 'audio'
            elif mime_type and mime_type.startswith('image/'):
                content_type = 'image'
            else:
                return False
            
            if content_type not in requirements:
                return False
            
            req = requirements[content_type]
            
            # Check file size
            if 'max_size' in req and file_size > req['max_size']:
                return False
            
            # Check format support
            file_ext = file_path.suffix.lower().lstrip('.')
            if 'supported_formats' in req and file_ext not in req['supported_formats']:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Platform compatibility check failed: {e}")
            return False
    
    async def _assess_streaming_capability(self, file_path: Path,
                                         metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Assess file's streaming capability.
        
        Args:
            file_path: Path to file
            metrics: Performance metrics
            
        Returns:
            Streaming assessment result
        """
        assessment = {
            'is_streamable': False,
            'streaming_quality': 'poor',
            'buffering_risk': 'high',
            'recommendations': []
        }
        
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            file_size = file_path.stat().st_size
            
            # Get format specifications
            if mime_type:
                category = None
                if mime_type.startswith('video/'):
                    category = 'video'
                elif mime_type.startswith('audio/'):
                    category = 'audio'
                
                if category:
                    file_ext = file_path.suffix.lower().lstrip('.')
                    specs = self.format_specifications.get(category, {}).get(file_ext, {})
                    
                    if specs.get('streaming_compatible', False):
                        assessment['is_streamable'] = True
                        
                        # Assess streaming quality based on file size and bitrate
                        size_mb = file_size / (1024 * 1024)
                        
                        if size_mb < 50:
                            assessment['streaming_quality'] = 'excellent'
                            assessment['buffering_risk'] = 'low'
                        elif size_mb < 200:
                            assessment['streaming_quality'] = 'good'
                            assessment['buffering_risk'] = 'medium'
                        else:
                            assessment['streaming_quality'] = 'fair'
                            assessment['buffering_risk'] = 'high'
                            assessment['recommendations'].append("Consider reducing file size for better streaming")
                    else:
                        assessment['recommendations'].append(f"Convert to streaming-compatible format")
            
            if not assessment['is_streamable']:
                assessment['recommendations'].append("Use streaming-optimized formats like MP4 or WebM")
        
        except Exception as e:
            logger.error(f"Streaming assessment failed: {e}")
            assessment['recommendations'].append("Unable to assess streaming capability")
        
        return assessment
    
    async def _generate_optimization_suggestions(self, metrics: List[PerformanceMetric],
                                               issues: List[PerformanceIssue],
                                               platform_compatibility: Dict[str, bool]) -> List[str]:
        """Generate optimization suggestions based on analysis.
        
        Args:
            metrics: Performance metrics
            issues: Performance issues
            platform_compatibility: Platform compatibility results
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # File size optimization
        size_issues = [i for i in issues if i.metric_type == PerformanceMetricType.FILE_SIZE]
        if size_issues:
            suggestions.append("Compress file to reduce size and improve loading times")
            suggestions.append("Consider using more efficient encoding formats")
        
        # Loading time optimization
        loading_issues = [i for i in issues if i.metric_type == PerformanceMetricType.LOADING_TIME]
        if loading_issues:
            suggestions.append("Optimize for faster loading by reducing file size")
            suggestions.append("Consider progressive loading or adaptive streaming")
        
        # Platform-specific suggestions
        incompatible_platforms = [p for p, compatible in platform_compatibility.items() if not compatible]
        if incompatible_platforms:
            suggestions.append(f"Convert format for compatibility with: {', '.join(incompatible_platforms)}")
        
        # Format-specific optimizations
        compression_issues = [i for i in issues if i.optimization_type == OptimizationType.COMPRESSION]
        if compression_issues:
            suggestions.append("Apply better compression algorithms")
            suggestions.append("Use lossless compression where quality is critical")
        
        encoding_issues = [i for i in issues if i.optimization_type == OptimizationType.ENCODING]
        if encoding_issues:
            suggestions.append("Use modern encoding standards (H.265, VP9, AV1)")
            suggestions.append("Optimize encoding settings for target platforms")
        
        # CDN and caching suggestions
        if any(m.metric_type == PerformanceMetricType.FILE_SIZE and m.value > 10*1024*1024 for m in metrics):
            suggestions.append("Consider using CDN for global content delivery")
            suggestions.append("Implement caching strategies for frequently accessed content")
        
        return suggestions[:6]  # Limit to top 6 suggestions
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetric],
                                   issues: List[PerformanceIssue]) -> float:
        """Calculate overall performance score.
        
        Args:
            metrics: Performance metrics
            issues: Performance issues
            
        Returns:
            Performance score (0.0 to 1.0)
        """
        if not metrics:
            return 0.0
        
        # Calculate average benchmark score
        avg_benchmark_score = sum(m.benchmark_score for m in metrics) / len(metrics)
        
        # Apply penalty for issues
        issue_penalty = 0.0
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                issue_penalty += 0.3
            elif issue.severity == ValidationSeverity.ERROR:
                issue_penalty += 0.2
            elif issue.severity == ValidationSeverity.WARNING:
                issue_penalty += 0.1
        
        # Calculate final score
        final_score = max(0.0, avg_benchmark_score - issue_penalty)
        return min(1.0, final_score)
    
    def _determine_performance_level(self, performance_score: float) -> PerformanceLevel:
        """Determine performance level based on score.
        
        Args:
            performance_score: Performance score (0.0 to 1.0)
            
        Returns:
            Performance level
        """
        if performance_score >= 0.95:
            return PerformanceLevel.OPTIMAL
        elif performance_score >= 0.85:
            return PerformanceLevel.EXCELLENT
        elif performance_score >= 0.7:
            return PerformanceLevel.GOOD
        elif performance_score >= 0.5:
            return PerformanceLevel.AVERAGE
        elif performance_score >= 0.3:
            return PerformanceLevel.BELOW_AVERAGE
        else:
            return PerformanceLevel.POOR
    
    def _estimate_improvements(self, issues: List[PerformanceIssue],
                             suggestions: List[str]) -> Dict[str, float]:
        """Estimate potential improvements from optimization.
        
        Args:
            issues: Performance issues
            suggestions: Optimization suggestions
            
        Returns:
            Dictionary of estimated improvements
        """
        improvements = {
            'file_size_reduction': 0.0,
            'loading_time_improvement': 0.0,
            'streaming_quality_improvement': 0.0,
            'platform_compatibility_improvement': 0.0
        }
        
        # Calculate potential improvements based on issues
        for issue in issues:
            if issue.metric_type == PerformanceMetricType.FILE_SIZE:
                improvements['file_size_reduction'] = max(
                    improvements['file_size_reduction'],
                    issue.potential_improvement
                )
            elif issue.metric_type == PerformanceMetricType.LOADING_TIME:
                improvements['loading_time_improvement'] = max(
                    improvements['loading_time_improvement'],
                    issue.potential_improvement
                )
        
        # Estimate streaming and compatibility improvements
        if any('streaming' in s.lower() for s in suggestions):
            improvements['streaming_quality_improvement'] = 40.0
        
        if any('compatibility' in s.lower() or 'convert' in s.lower() for s in suggestions):
            improvements['platform_compatibility_improvement'] = 70.0
        
        return improvements
    
    def _generate_file_recommendations(self, file_path: Path, file_size: int,
                                     mime_type: Optional[str],
                                     issues: List[FileValidationIssue]) -> List[str]:
        """Generate general file recommendations.
        
        Args:
            file_path: Path to file
            file_size: File size in bytes
            mime_type: MIME type
            issues: Validation issues
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Critical issue recommendations
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            recommendations.append("Address critical issues before proceeding")
        
        # Format recommendations
        if mime_type and mime_type.startswith('video/'):
            recommendations.append("Ensure video format is web-compatible (MP4, WebM)")
            if file_size > 100 * 1024 * 1024:  # 100MB
                recommendations.append("Consider video compression for web delivery")
        
        elif mime_type and mime_type.startswith('image/'):
            recommendations.append("Use WebP format for better compression")
            if file_size > 1024 * 1024:  # 1MB
                recommendations.append("Optimize image compression for web use")
        
        # Security recommendations
        security_issues = [i for i in issues if i.validation_type == FileValidationType.SECURITY]
        if security_issues:
            recommendations.append("Review file for security concerns")
        
        # Performance recommendations
        performance_issues = [i for i in issues if i.validation_type == FileValidationType.PERFORMANCE]
        if performance_issues:
            recommendations.append("Optimize file for better performance")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _determine_file_status(self, issues: List[FileValidationIssue]) -> FileStatus:
        """Determine overall file status based on issues.
        
        Args:
            issues: List of validation issues
            
        Returns:
            File status
        """
        if not issues:
            return FileStatus.VALID
        
        # Check for critical issues
        if any(i.severity == ValidationSeverity.CRITICAL for i in issues):
            return FileStatus.CORRUPTED
        
        # Check for incompatibility issues
        format_issues = [i for i in issues if i.validation_type == FileValidationType.FORMAT]
        if any(i.severity == ValidationSeverity.ERROR for i in format_issues):
            return FileStatus.INCOMPATIBLE
        
        # Check for performance issues
        performance_issues = [i for i in issues if i.validation_type == FileValidationType.PERFORMANCE]
        if performance_issues:
            return FileStatus.SUBOPTIMAL
        
        return FileStatus.VALID

# Convenience functions for direct validation
async def validate_file(file_path: Union[str, Path],
                      validation_types: Optional[List[FileValidationType]] = None,
                      config: Optional[Dict[str, Any]] = None) -> FileValidationResult:
    """Validate file (convenience function).
    
    Args:
        file_path: Path to file
        validation_types: Types of validation to perform
        config: Optional validator configuration
        
    Returns:
        FileValidationResult
    """
    validator = FilePerformanceValidator(config)
    return await validator.validate_file(file_path, validation_types)

async def assess_performance(file_path: Union[str, Path],
                           platforms: Optional[List[str]] = None,
                           config: Optional[Dict[str, Any]] = None) -> PerformanceValidationResult:
    """Assess file performance (convenience function).
    
    Args:
        file_path: Path to file
        platforms: Target platforms
        config: Optional validator configuration
        
    Returns:
        PerformanceValidationResult
    """
    validator = FilePerformanceValidator(config)
    return await validator.assess_performance(file_path, platforms)

# Export all classes and functions
__all__ = [
    'FilePerformanceValidator',
    'FileValidationType',
    'ValidationSeverity',
    'FileStatus',
    'PerformanceMetricType',
    'PerformanceLevel',
    'OptimizationType',
    'FileValidationIssue',
    'FileValidationResult',
    'PerformanceMetric',
    'PerformanceIssue',
    'PerformanceValidationResult',
    'validate_file',
    'assess_performance'
]