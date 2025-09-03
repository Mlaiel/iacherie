"""Quality Analyzer

Comprehensive media quality analysis system for audio, video, and image content.
Provides detailed quality metrics, issue detection, and improvement recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import json

from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
from .image_optimizer import ImageOptimizer

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality levels"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class AnalysisMode(Enum):
    """Analysis modes"""
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    PROFESSIONAL = "professional"


@dataclass
class QualityScore:
    """Quality score breakdown"""
    overall: float
    technical: float
    perceptual: float
    compression: float
    noise: float
    clarity: float


@dataclass
class QualityIssue:
    """Identified quality issue"""
    issue_id: str
    severity: str
    category: str
    description: str
    recommendation: str
    confidence: float


@dataclass
class QualityReport:
    """Comprehensive quality analysis report"""
    content_id: str
    media_type: str
    analysis_mode: AnalysisMode
    quality_score: QualityScore
    quality_level: QualityLevel
    issues_detected: List[QualityIssue]
    technical_metrics: Dict[str, Any]
    recommendations: List[str]
    analysis_timestamp: str
    processing_time: float


class QualityAnalyzer:
    """Comprehensive media quality analysis system"""
    
    def __init__(self):
        """Initialize quality analyzer"""
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.image_optimizer = ImageOptimizer()
        
        # Quality thresholds
        self._quality_thresholds = self._initialize_quality_thresholds()
        
        # Issue detection rules
        self._detection_rules = self._initialize_detection_rules()
    
    async def analyze_media_quality(self,
                                  media_data: Union[bytes, BinaryIO],
                                  media_type: str,
                                  analysis_mode: AnalysisMode = AnalysisMode.COMPREHENSIVE,
                                  custom_params: Optional[Dict[str, Any]] = None) -> QualityReport:
        """
        Comprehensive media quality analysis
        
        Args:
            media_data: Media content to analyze
            media_type: Type of media (audio, video, image)
            analysis_mode: Depth of analysis
            custom_params: Additional analysis parameters
            
        Returns:
            Detailed quality analysis report
        """
        try:
            start_time = asyncio.get_event_loop().time()
            content_id = str(uuid.uuid4())
            
            # Get input data
            if isinstance(media_data, bytes):
                input_bytes = media_data
            else:
                input_bytes = media_data.read()
                media_data.seek(0)
            
            # Perform analysis based on media type
            if media_type.lower() == 'audio':
                analysis_result = await self._analyze_audio_quality(
                    input_bytes, analysis_mode, custom_params
                )
            elif media_type.lower() == 'video':
                analysis_result = await self._analyze_video_quality(
                    input_bytes, analysis_mode, custom_params
                )
            elif media_type.lower() == 'image':
                analysis_result = await self._analyze_image_quality(
                    input_bytes, analysis_mode, custom_params
                )
            else:
                raise ValueError(f"Unsupported media type: {media_type}")
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                analysis_result['metrics'], media_type
            )
            
            # Determine quality level
            quality_level = self._determine_quality_level(quality_score.overall)
            
            # Detect issues
            issues = await self._detect_quality_issues(
                analysis_result['metrics'], media_type, analysis_mode
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                quality_score, issues, media_type
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return QualityReport(
                content_id=content_id,
                media_type=media_type,
                analysis_mode=analysis_mode,
                quality_score=quality_score,
                quality_level=quality_level,
                issues_detected=issues,
                technical_metrics=analysis_result['metrics'],
                recommendations=recommendations,
                analysis_timestamp=str(start_time),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return QualityReport(
                content_id=str(uuid.uuid4()),
                media_type=media_type,
                analysis_mode=analysis_mode,
                quality_score=QualityScore(0, 0, 0, 0, 0, 0),
                quality_level=QualityLevel.POOR,
                issues_detected=[QualityIssue(
                    str(uuid.uuid4()), "critical", "analysis", f"Analysis failed: {str(e)}", 
                    "Check input format and try again", 0.9
                )],
                technical_metrics={},
                recommendations=["Fix analysis errors before proceeding"],
                analysis_timestamp=str(asyncio.get_event_loop().time()),
                processing_time=0
            )
    
    async def batch_analyze_quality(self,
                                  media_files: List[Dict[str, Any]],
                                  analysis_mode: AnalysisMode = AnalysisMode.BASIC) -> List[QualityReport]:
        """
        Analyze quality of multiple media files
        
        Args:
            media_files: List of media files with metadata
            analysis_mode: Analysis mode to use
            
        Returns:
            List of quality analysis reports
        """
        tasks = []
        
        for media_file in media_files:
            task = self.analyze_media_quality(
                media_file['data'],
                media_file['media_type'],
                analysis_mode,
                media_file.get('custom_params')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = QualityReport(
                    content_id=str(uuid.uuid4()),
                    media_type=media_files[i].get('media_type', 'unknown'),
                    analysis_mode=analysis_mode,
                    quality_score=QualityScore(0, 0, 0, 0, 0, 0),
                    quality_level=QualityLevel.POOR,
                    issues_detected=[],
                    technical_metrics={},
                    recommendations=[],
                    analysis_timestamp=str(asyncio.get_event_loop().time()),
                    processing_time=0
                )
        
        return results
    
    async def compare_quality(self,
                            original_media: Union[bytes, BinaryIO],
                            processed_media: Union[bytes, BinaryIO],
                            media_type: str) -> Dict[str, Any]:
        """
        Compare quality between original and processed media
        
        Args:
            original_media: Original media content
            processed_media: Processed media content
            media_type: Type of media
            
        Returns:
            Quality comparison report
        """
        try:
            # Analyze both versions
            original_report = await self.analyze_media_quality(
                original_media, media_type, AnalysisMode.COMPREHENSIVE
            )
            
            processed_report = await self.analyze_media_quality(
                processed_media, media_type, AnalysisMode.COMPREHENSIVE
            )
            
            # Calculate quality differences
            quality_diff = {
                'overall': processed_report.quality_score.overall - original_report.quality_score.overall,
                'technical': processed_report.quality_score.technical - original_report.quality_score.technical,
                'perceptual': processed_report.quality_score.perceptual - original_report.quality_score.perceptual,
                'compression': processed_report.quality_score.compression - original_report.quality_score.compression,
                'noise': processed_report.quality_score.noise - original_report.quality_score.noise,
                'clarity': processed_report.quality_score.clarity - original_report.quality_score.clarity
            }
            
            # Determine if processing improved or degraded quality
            overall_improvement = quality_diff['overall'] > 0
            
            # Identify specific improvements and degradations
            improvements = []
            degradations = []
            
            for metric, diff in quality_diff.items():
                if diff > 5:  # Significant improvement
                    improvements.append(f"{metric}: +{diff:.1f}")
                elif diff < -5:  # Significant degradation
                    degradations.append(f"{metric}: {diff:.1f}")
            
            return {
                'original_quality': original_report.quality_score.__dict__,
                'processed_quality': processed_report.quality_score.__dict__,
                'quality_differences': quality_diff,
                'overall_improvement': overall_improvement,
                'improvements': improvements,
                'degradations': degradations,
                'recommendation': self._get_comparison_recommendation(
                    overall_improvement, improvements, degradations
                )
            }
            
        except Exception as e:
            logger.error(f"Quality comparison failed: {e}")
            return {
                'error': str(e),
                'comparison_failed': True
            }
    
    async def _analyze_audio_quality(self,
                                   audio_data: bytes,
                                   analysis_mode: AnalysisMode,
                                   custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audio quality"""
        try:
            # Use audio processor for analysis
            analysis_result = await self.audio_processor.analyze_audio_quality(audio_data)
            
            if 'error' in analysis_result:
                raise Exception(analysis_result['error'])
            
            metrics = analysis_result['metrics']
            
            # Add additional analysis for comprehensive mode
            if analysis_mode in [AnalysisMode.COMPREHENSIVE, AnalysisMode.PROFESSIONAL]:
                # Extract audio features for advanced analysis
                features_result = await self.audio_processor.extract_audio_features(audio_data)
                
                if 'features' in features_result:
                    metrics.update({
                        'advanced_features': features_result['features']
                    })
            
            return {
                'metrics': metrics,
                'analysis_mode': analysis_mode.value
            }
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}")
            return {
                'metrics': {},
                'error': str(e)
            }
    
    async def _analyze_video_quality(self,
                                   video_data: bytes,
                                   analysis_mode: AnalysisMode,
                                   custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze video quality"""
        try:
            # Use video processor for analysis
            analysis_result = await self.video_processor.analyze_video_quality(video_data)
            
            if 'error' in analysis_result:
                raise Exception(analysis_result['error'])
            
            metrics = analysis_result['metrics']
            
            # Add additional analysis for comprehensive mode
            if analysis_mode in [AnalysisMode.COMPREHENSIVE, AnalysisMode.PROFESSIONAL]:
                # Extract frames for detailed analysis
                frames_result = await self.video_processor.extract_frames(
                    video_data, frame_interval=5.0, max_frames=20
                )
                
                if frames_result.get('success'):
                    metrics.update({
                        'frame_analysis': {
                            'frames_extracted': frames_result['frames_extracted'],
                            'frame_consistency': self._analyze_frame_consistency(frames_result['frames'])
                        }
                    })
            
            return {
                'metrics': metrics,
                'analysis_mode': analysis_mode.value
            }
            
        except Exception as e:
            logger.error(f"Video quality analysis failed: {e}")
            return {
                'metrics': {},
                'error': str(e)
            }
    
    async def _analyze_image_quality(self,
                                   image_data: bytes,
                                   analysis_mode: AnalysisMode,
                                   custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze image quality"""
        try:
            # Use image optimizer for basic analysis
            from .image_optimizer import OptimizationMode
            
            # Perform a dummy optimization to get metrics
            result = await self.image_optimizer.optimize_image(
                image_data,
                OptimizationMode.QUALITY,
                custom_params=custom_params
            )
            
            if result.error:
                raise Exception(result.error)
            
            metrics = result.quality_metrics.__dict__
            
            # Add additional analysis for comprehensive mode
            if analysis_mode in [AnalysisMode.COMPREHENSIVE, AnalysisMode.PROFESSIONAL]:
                # Add advanced image analysis metrics
                metrics.update({
                    'compression_artifacts': self._detect_compression_artifacts(metrics),
                    'noise_level': self._estimate_noise_level(metrics),
                    'detail_preservation': self._assess_detail_preservation(metrics)
                })
            
            return {
                'metrics': metrics,
                'analysis_mode': analysis_mode.value
            }
            
        except Exception as e:
            logger.error(f"Image quality analysis failed: {e}")
            return {
                'metrics': {},
                'error': str(e)
            }
    
    def _calculate_quality_score(self, metrics: Dict[str, Any], media_type: str) -> QualityScore:
        """Calculate comprehensive quality score"""
        try:
            thresholds = self._quality_thresholds.get(media_type, {})
            
            if media_type == 'audio':
                return self._calculate_audio_quality_score(metrics, thresholds)
            elif media_type == 'video':
                return self._calculate_video_quality_score(metrics, thresholds)
            elif media_type == 'image':
                return self._calculate_image_quality_score(metrics, thresholds)
            else:
                return QualityScore(50, 50, 50, 50, 50, 50)
                
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return QualityScore(0, 0, 0, 0, 0, 0)
    
    def _calculate_audio_quality_score(self, metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> QualityScore:
        """Calculate audio quality score"""
        # Technical score based on sample rate, bit depth, etc.
        technical = 50
        if metrics.get('sample_rate', 0) >= thresholds.get('good_sample_rate', 44100):
            technical += 25
        if metrics.get('snr_estimate', 0) >= thresholds.get('good_snr', 20):
            technical += 25
        
        # Perceptual score based on dynamic range and frequency response
        perceptual = 50
        if metrics.get('dynamic_range', 0) >= thresholds.get('good_dynamic_range', 20):
            perceptual += 25
        
        # Noise score (inverted - lower noise is better)
        noise = max(0, 100 - (metrics.get('noise_level', 50)))
        
        # Clarity score based on frequency response
        clarity = 50
        freq_response = metrics.get('frequency_response', {})
        if freq_response:
            balance = abs(freq_response.get('bass', 0) - freq_response.get('treble', 0))
            if balance < 10:  # Good frequency balance
                clarity += 25
        
        compression = 75  # Default for audio
        overall = (technical + perceptual + noise + clarity) / 4
        
        return QualityScore(overall, technical, perceptual, compression, noise, clarity)
    
    def _calculate_video_quality_score(self, metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> QualityScore:
        """Calculate video quality score"""
        # Technical score based on resolution, fps, bitrate
        technical = 50
        width = metrics.get('width', 0)
        height = metrics.get('height', 0)
        
        if width >= 1920 and height >= 1080:
            technical += 20
        elif width >= 1280 and height >= 720:
            technical += 15
        
        if metrics.get('fps', 0) >= 30:
            technical += 15
        
        if metrics.get('bitrate', 0) >= thresholds.get('good_bitrate', 2000000):
            technical += 15
        
        # Perceptual score based on motion and scene complexity
        perceptual = 50 + min(25, metrics.get('quality_score', 50) - 50)
        
        # Compression score based on bitrate vs resolution
        pixel_count = width * height
        if pixel_count > 0 and metrics.get('bitrate', 0) > 0:
            bits_per_pixel = metrics.get('bitrate', 0) / (pixel_count * metrics.get('fps', 30))
            if bits_per_pixel > 0.1:
                compression = 85
            elif bits_per_pixel > 0.05:
                compression = 70
            else:
                compression = 50
        else:
            compression = 50
        
        noise = 75  # Default noise score for video
        clarity = 50 + min(25, metrics.get('scene_complexity', 0) / 2)
        
        overall = (technical + perceptual + compression + noise + clarity) / 5
        
        return QualityScore(overall, technical, perceptual, compression, noise, clarity)
    
    def _calculate_image_quality_score(self, metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> QualityScore:
        """Calculate image quality score"""
        # Technical score based on resolution and bit depth
        technical = 50
        megapixels = (metrics.get('width', 0) * metrics.get('height', 0)) / 1000000
        
        if megapixels >= 24:  # 6K+
            technical += 25
        elif megapixels >= 8:  # 4K
            technical += 20
        elif megapixels >= 2:  # 1080p
            technical += 15
        
        # Perceptual score based on sharpness and contrast
        perceptual = 50
        if metrics.get('sharpness', 0) > thresholds.get('good_sharpness', 500):
            perceptual += 25
        if metrics.get('contrast', 0) > thresholds.get('good_contrast', 0.3):
            perceptual += 25
        
        # Compression score based on file size vs quality
        compression = 75  # Default
        
        # Noise score (lower is better)
        noise = 75  # Default
        
        # Clarity score based on sharpness
        clarity = min(100, 50 + (metrics.get('sharpness', 0) / 20))
        
        overall = (technical + perceptual + compression + noise + clarity) / 5
        
        return QualityScore(overall, technical, perceptual, compression, noise, clarity)
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level from overall score"""
        if overall_score >= 85:
            return QualityLevel.EXCELLENT
        elif overall_score >= 70:
            return QualityLevel.GOOD
        elif overall_score >= 50:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    async def _detect_quality_issues(self,
                                   metrics: Dict[str, Any],
                                   media_type: str,
                                   analysis_mode: AnalysisMode) -> List[QualityIssue]:
        """Detect quality issues based on metrics"""
        issues = []
        rules = self._detection_rules.get(media_type, [])
        
        for rule in rules:
            if self._evaluate_rule(rule, metrics):
                issue = QualityIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=rule['severity'],
                    category=rule['category'],
                    description=rule['description'],
                    recommendation=rule['recommendation'],
                    confidence=rule.get('confidence', 0.8)
                )
                issues.append(issue)
        
        return issues
    
    def _evaluate_rule(self, rule: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """Evaluate a detection rule against metrics"""
        try:
            condition = rule['condition']
            metric_path = condition['metric']
            operator = condition['operator']
            threshold = condition['threshold']
            
            # Get metric value (support nested paths)
            metric_value = metrics
            for key in metric_path.split('.'):
                metric_value = metric_value.get(key, 0)
            
            # Evaluate condition
            if operator == 'lt':
                return metric_value < threshold
            elif operator == 'gt':
                return metric_value > threshold
            elif operator == 'eq':
                return metric_value == threshold
            elif operator == 'lte':
                return metric_value <= threshold
            elif operator == 'gte':
                return metric_value >= threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Rule evaluation failed: {e}")
            return False
    
    async def _generate_recommendations(self,
                                      quality_score: QualityScore,
                                      issues: List[QualityIssue],
                                      media_type: str) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # General recommendations based on quality score
        if quality_score.overall < 50:
            recommendations.append("Overall quality is poor - consider re-recording or using higher quality settings")
        
        if quality_score.technical < 60:
            if media_type == 'audio':
                recommendations.append("Use higher sample rate (48kHz or higher) and bit depth")
            elif media_type == 'video':
                recommendations.append("Increase resolution and frame rate for better quality")
            elif media_type == 'image':
                recommendations.append("Use higher resolution camera or scanning settings")
        
        if quality_score.noise > 70:  # High noise
            recommendations.append("Apply noise reduction to improve clarity")
        
        if quality_score.clarity < 60:
            recommendations.append("Apply sharpening or clarity enhancement")
        
        # Issue-specific recommendations
        for issue in issues:
            if issue.severity in ['high', 'critical']:
                recommendations.append(issue.recommendation)
        
        return list(set(recommendations))  # Remove duplicates
    
    def _initialize_quality_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality thresholds for different media types"""
        return {
            'audio': {
                'good_sample_rate': 44100,
                'excellent_sample_rate': 48000,
                'good_snr': 20,
                'excellent_snr': 40,
                'good_dynamic_range': 20,
                'excellent_dynamic_range': 40
            },
            'video': {
                'good_bitrate': 2000000,  # 2 Mbps
                'excellent_bitrate': 8000000,  # 8 Mbps
                'good_fps': 30,
                'excellent_fps': 60
            },
            'image': {
                'good_sharpness': 500,
                'excellent_sharpness': 1000,
                'good_contrast': 0.3,
                'excellent_contrast': 0.5
            }
        }
    
    def _initialize_detection_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize quality issue detection rules"""
        return {
            'audio': [
                {
                    'condition': {'metric': 'sample_rate', 'operator': 'lt', 'threshold': 22050},
                    'severity': 'high',
                    'category': 'technical',
                    'description': 'Low sample rate detected',
                    'recommendation': 'Use sample rate of 44.1kHz or higher',
                    'confidence': 0.9
                },
                {
                    'condition': {'metric': 'snr_estimate', 'operator': 'lt', 'threshold': 10},
                    'severity': 'medium',
                    'category': 'noise',
                    'description': 'High noise levels detected',
                    'recommendation': 'Apply noise reduction or record in quieter environment',
                    'confidence': 0.8
                }
            ],
            'video': [
                {
                    'condition': {'metric': 'fps', 'operator': 'lt', 'threshold': 24},
                    'severity': 'medium',
                    'category': 'technical',
                    'description': 'Low frame rate detected',
                    'recommendation': 'Use frame rate of 24fps or higher for smooth playback',
                    'confidence': 0.9
                },
                {
                    'condition': {'metric': 'bitrate', 'operator': 'lt', 'threshold': 1000000},
                    'severity': 'high',
                    'category': 'compression',
                    'description': 'Very low bitrate may cause quality issues',
                    'recommendation': 'Increase bitrate for better quality',
                    'confidence': 0.8
                }
            ],
            'image': [
                {
                    'condition': {'metric': 'sharpness', 'operator': 'lt', 'threshold': 100},
                    'severity': 'medium',
                    'category': 'clarity',
                    'description': 'Image appears soft or blurry',
                    'recommendation': 'Apply sharpening or use better focus when capturing',
                    'confidence': 0.7
                }
            ]
        }
    
    def _analyze_frame_consistency(self, frames: List[Dict[str, Any]]) -> float:
        """Analyze consistency between video frames"""
        # Placeholder for frame consistency analysis
        return 0.8  # Default good consistency
    
    def _detect_compression_artifacts(self, metrics: Dict[str, Any]) -> float:
        """Detect compression artifacts in image"""
        # Placeholder for compression artifact detection
        return 0.2  # Default low artifacts
    
    def _estimate_noise_level(self, metrics: Dict[str, Any]) -> float:
        """Estimate noise level in image"""
        # Placeholder for noise level estimation
        return 0.3  # Default moderate noise
    
    def _assess_detail_preservation(self, metrics: Dict[str, Any]) -> float:
        """Assess detail preservation in image"""
        # Based on sharpness and other factors
        sharpness = metrics.get('sharpness', 0)
        return min(1.0, sharpness / 1000)  # Normalize to 0-1
    
    def _get_comparison_recommendation(self,
                                     overall_improvement: bool,
                                     improvements: List[str],
                                     degradations: List[str]) -> str:
        """Get recommendation based on quality comparison"""
        if overall_improvement and not degradations:
            return "Processing improved quality without significant degradation"
        elif overall_improvement and degradations:
            return "Processing improved quality but with some degradation in specific areas"
        elif not overall_improvement and improvements:
            return "Mixed results - some improvements but overall quality decreased"
        else:
            return "Processing degraded quality - consider different settings or approach"