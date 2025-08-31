"""Quality Assessor - Advanced Content Quality Assessment Engine

Comprehensive quality assessment system for multi-format content analysis.
Provides detailed scoring, metrics calculation, and quality benchmarking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path
import cv2
import librosa
import nltk
from textstat import flesch_kincaid_grade, gunning_fog
import spacy

try:
    from core.exceptions import AssessmentError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AssessmentError, ValidationError = globals().get('AssessmentError, ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.content_analyzer import ContentAnalyzer
from ...utils.metrics_calculator import MetricsCalculator
from ...ml.quality_models import QualityModelManager
from ...database.models.assessment import AssessmentResult, QualityMetric
from ..quality_agent import QualityScore, QualityLevel, ContentType

logger = logging.getLogger(__name__)

class AssessmentCategory(Enum):
    """Quality assessment categories"""    TECHNICAL = "technical"
    CREATIVE = "creative"
    COMMERCIAL = "commercial"
    COMPLIANCE = "compliance"
    ACCESSIBILITY = "accessibility"
    ENGAGEMENT = "engagement"

@dataclass
class AssessmentCriteria:
    """Quality assessment criteria definition"""    category: AssessmentCategory
    name: str
    weight: float
    min_threshold: float
    target_threshold: float
    max_score: float
    evaluation_method: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssessmentResult:
    """Individual assessment result"""    criteria_name: str
    score: float
    max_score: float
    percentage: float
    status: str  # pass, warning, fail
    details: Dict[str, Any]
    recommendations: List[str]
    processing_time: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class DetailedAssessment:
    """Comprehensive assessment results"""    content_id: str
    content_type: ContentType
    overall_score: float
    category_scores: Dict[str, float]
    individual_results: List[AssessmentResult]
    quality_grade: str
    compliance_status: str
    improvement_potential: float
    benchmark_comparison: Dict[str, Any]
    metadata: Dict[str, Any]
    assessment_duration: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class QualityAssessor:
    """    Advanced Quality Assessor for comprehensive content evaluation.
    
    Features:
    - Multi-dimensional quality assessment
    - Industry-standard compliance checking
    - Automated benchmarking and comparison
    - Real-time quality scoring
    - Detailed improvement recommendations
    - Performance optimization analysis
    - Accessibility compliance validation
    - Commercial viability assessment
    """    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.content_analyzer = ContentAnalyzer()
        self.metrics_calculator = MetricsCalculator()
        self.quality_models = QualityModelManager()
        
        # Initialize NLP models
        self._initialize_nlp_models()
        
        # Load assessment criteria
        self.assessment_criteria = self._load_assessment_criteria()
        
        # Load industry benchmarks
        self.benchmarks = self._load_industry_benchmarks()
        
        # Performance tracking
        self.assessment_cache = {}
        self.performance_metrics = {}
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("QualityAssessor initialized successfully")

    async def assess_content_quality(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        assessment_categories: Optional[List[AssessmentCategory]] = None,
        custom_criteria: Optional[List[AssessmentCriteria]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DetailedAssessment:
        """        Perform comprehensive quality assessment of content.
        
        Args:
            content_id: Unique identifier for the content
            content_path: Path to content file
            content_type: Type of content being assessed
            assessment_categories: Specific categories to assess
            custom_criteria: Additional custom assessment criteria
            metadata: Content metadata for context
            
        Returns:
            DetailedAssessment: Complete quality assessment results
        """        start_time = time.time()
        
        try:
            self.logger.info(f"Starting quality assessment for {content_id}")
            
            # Determine assessment categories
            categories = assessment_categories or list(AssessmentCategory)
            
            # Get relevant criteria for content type and categories
            criteria = self._get_assessment_criteria(content_type, categories, custom_criteria)
            
            # Perform individual assessments
            individual_results = []
            category_scores = {}
            
            for category in categories:
                category_criteria = [c for c in criteria if c.category == category]
                if not category_criteria:
                    continue
                    
                category_results = await self._assess_category(
                    content_path, content_type, category, category_criteria, metadata
                )
                
                individual_results.extend(category_results)
                
                # Calculate category score
                if category_results:
                    category_score = np.mean([r.percentage for r in category_results])
                    category_scores[category.value] = category_score
                    
            # Calculate overall score
            overall_score = self._calculate_overall_score(category_scores, categories)
            
            # Determine quality grade
            quality_grade = self._determine_quality_grade(overall_score)
            
            # Check compliance status
            compliance_status = self._check_compliance_status(individual_results)
            
            # Calculate improvement potential
            improvement_potential = self._calculate_improvement_potential(individual_results)
            
            # Generate benchmark comparison
            benchmark_comparison = await self._compare_with_benchmarks(
                content_type, category_scores, overall_score
            )
            
            # Create detailed assessment
            assessment = DetailedAssessment(
                content_id=content_id,
                content_type=content_type,
                overall_score=overall_score,
                category_scores=category_scores,
                individual_results=individual_results,
                quality_grade=quality_grade,
                compliance_status=compliance_status,
                improvement_potential=improvement_potential,
                benchmark_comparison=benchmark_comparison,
                metadata=metadata or {},
                assessment_duration=time.time() - start_time
            )
            
            # Cache results
            self.assessment_cache[content_id] = assessment
            
            # Update performance metrics
            await self._update_assessment_metrics(assessment)
            
            self.logger.info(
                f"Quality assessment completed for {content_id} in "
                f"{assessment.assessment_duration:.2f}s - Score: {overall_score:.1f}%"
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed for {content_id}: {str(e)}")
            raise AssessmentError(f"Quality assessment failed: {str(e)}")

    async def _assess_category(
        self,
        content_path: str,
        content_type: ContentType,
        category: AssessmentCategory,
        criteria: List[AssessmentCriteria],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[AssessmentResult]:
        """Assess specific quality category"""        
        results = []
        
        for criterion in criteria:
            try:
                start_time = time.time()
                
                # Perform assessment based on evaluation method
                if criterion.evaluation_method == "technical_analysis":
                    result = await self._assess_technical_quality(
                        content_path, content_type, criterion, metadata
                    )
                elif criterion.evaluation_method == "creative_analysis":
                    result = await self._assess_creative_quality(
                        content_path, content_type, criterion, metadata
                    )
                elif criterion.evaluation_method == "commercial_analysis":
                    result = await self._assess_commercial_viability(
                        content_path, content_type, criterion, metadata
                    )
                elif criterion.evaluation_method == "compliance_check":
                    result = await self._assess_compliance(
                        content_path, content_type, criterion, metadata
                    )
                elif criterion.evaluation_method == "accessibility_check":
                    result = await self._assess_accessibility(
                        content_path, content_type, criterion, metadata
                    )
                elif criterion.evaluation_method == "engagement_prediction":
                    result = await self._assess_engagement_potential(
                        content_path, content_type, criterion, metadata
                    )
                else:
                    # Default generic assessment
                    result = await self._assess_generic_quality(
                        content_path, content_type, criterion, metadata
                    )
                    
                result.processing_time = time.time() - start_time
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Assessment failed for {criterion.name}: {str(e)}")
                
                # Create error result
                error_result = AssessmentResult(
                    criteria_name=criterion.name,
                    score=0.0,
                    max_score=criterion.max_score,
                    percentage=0.0,
                    status="error",
                    details={"error": str(e)},
                    recommendations=[f"Fix error: {str(e)}"],
                    processing_time=time.time() - start_time
                )
                results.append(error_result)
                
        return results

    async def _assess_technical_quality(
        self,
        content_path: str,
        content_type: ContentType,
        criterion: AssessmentCriteria,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssessmentResult:
        """Assess technical quality aspects"""        
        try:
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                return await self._assess_audio_technical_quality(content_path, criterion)
                
            elif content_type == ContentType.VIDEO:
                return await self._assess_video_technical_quality(content_path, criterion)
                
            elif content_type == ContentType.IMAGE:
                return await self._assess_image_technical_quality(content_path, criterion)
                
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                return await self._assess_text_technical_quality(content_path, criterion)
                
            else:
                return await self._assess_generic_technical_quality(content_path, criterion)
                
        except Exception as e:
            raise AssessmentError(f"Technical assessment failed: {str(e)}")

    async def _assess_audio_technical_quality(
        self,
        content_path: str,
        criterion: AssessmentCriteria
    ) -> AssessmentResult:
        """Assess audio technical quality"""        
        try:
            # Load audio file
            y, sr = librosa.load(content_path)
            
            # Calculate technical metrics
            metrics = {}
            
            if criterion.name == "audio_bitrate":
                # Estimate bitrate quality
                duration = len(y) / sr
                file_size = Path(content_path).stat().st_size
                estimated_bitrate = (file_size * 8) / duration / 1000  # kbps
                
                score = min(estimated_bitrate / 320, 1.0) * criterion.max_score
                metrics["estimated_bitrate"] = estimated_bitrate
                
            elif criterion.name == "audio_dynamic_range":
                # Calculate dynamic range
                rms = librosa.feature.rms(y=y)[0]
                dynamic_range = np.max(rms) / (np.mean(rms) + 1e-8)
                
                score = min(dynamic_range / 10, 1.0) * criterion.max_score
                metrics["dynamic_range"] = dynamic_range
                
            elif criterion.name == "audio_frequency_response":
                # Analyze frequency response
                stft = librosa.stft(y)
                magnitude = np.abs(stft)
                freq_balance = np.std(np.mean(magnitude, axis=1))
                
                score = max(0, (1.0 - freq_balance / 1000)) * criterion.max_score
                metrics["frequency_balance"] = freq_balance
                
            elif criterion.name == "audio_noise_floor":
                # Estimate noise floor
                noise_estimate = np.percentile(np.abs(y), 10)
                noise_score = max(0, 1.0 - (noise_estimate * 1000))
                
                score = noise_score * criterion.max_score
                metrics["noise_floor"] = noise_estimate
                
            else:
                # Generic audio quality
                score = 0.7 * criterion.max_score
                
            # Determine status
            percentage = (score / criterion.max_score) * 100
            status = self._determine_assessment_status(percentage, criterion)
            
            # Generate recommendations
            recommendations = self._generate_audio_recommendations(
                criterion.name, score, criterion.max_score, metrics
            )
            
            return AssessmentResult(
                criteria_name=criterion.name,
                score=score,
                max_score=criterion.max_score,
                percentage=percentage,
                status=status,
                details=metrics,
                recommendations=recommendations,
                processing_time=0.0
            )
            
        except Exception as e:
            raise AssessmentError(f"Audio technical assessment failed: {str(e)}")

    async def _assess_video_technical_quality(
        self,
        content_path: str,
        criterion: AssessmentCriteria
    ) -> AssessmentResult:
        """Assess video technical quality"""        
        try:
            # Open video file
            cap = cv2.VideoCapture(content_path)
            
            metrics = {}
            
            if criterion.name == "video_resolution":
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total_pixels = width * height
                
                # Score based on resolution
                if total_pixels >= 8294400:  # 4K
                    score = 1.0
                elif total_pixels >= 2073600:  # 1080p
                    score = 0.8
                elif total_pixels >= 921600:   # 720p
                    score = 0.6
                else:
                    score = 0.3
                    
                score *= criterion.max_score
                metrics.update({"width": width, "height": height, "total_pixels": total_pixels})
                
            elif criterion.name == "video_framerate":
                fps = cap.get(cv2.CAP_PROP_FPS)
                score = min(fps / 60, 1.0) * criterion.max_score
                metrics["fps"] = fps
                
            elif criterion.name == "video_stability":
                # Analyze frame-to-frame stability
                frames = []
                for i in range(min(30, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
                    ret, frame = cap.read()
                    if ret:
                        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                    else:
                        break
                        
                if len(frames) > 1:
                    stability_score = self._calculate_video_stability(frames)
                    score = stability_score * criterion.max_score
                    metrics["stability_score"] = stability_score
                else:
                    score = 0.5 * criterion.max_score
                    
            else:
                # Generic video quality
                score = 0.7 * criterion.max_score
                
            cap.release()
            
            # Determine status and generate recommendations
            percentage = (score / criterion.max_score) * 100
            status = self._determine_assessment_status(percentage, criterion)
            recommendations = self._generate_video_recommendations(
                criterion.name, score, criterion.max_score, metrics
            )
            
            return AssessmentResult(
                criteria_name=criterion.name,
                score=score,
                max_score=criterion.max_score,
                percentage=percentage,
                status=status,
                details=metrics,
                recommendations=recommendations,
                processing_time=0.0
            )
            
        except Exception as e:
            raise AssessmentError(f"Video technical assessment failed: {str(e)}")

    async def _assess_creative_quality(
        self,
        content_path: str,
        content_type: ContentType,
        criterion: AssessmentCriteria,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssessmentResult:
        """Assess creative and artistic quality"""        
        try:
            metrics = {}
            
            if content_type == ContentType.IMAGE:
                # Image composition analysis
                image = cv2.imread(content_path)
                composition_score = self._analyze_image_composition(image)
                color_harmony_score = self._analyze_color_harmony(image)
                
                score = np.mean([composition_score, color_harmony_score]) * criterion.max_score
                metrics.update({
                    "composition_score": composition_score,
                    "color_harmony_score": color_harmony_score
                })
                
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                # Text creativity analysis
                with open(content_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
                creativity_score = self._analyze_text_creativity(text)
                style_score = self._analyze_writing_style(text)
                
                score = np.mean([creativity_score, style_score]) * criterion.max_score
                metrics.update({
                    "creativity_score": creativity_score,
                    "style_score": style_score
                })
                
            elif content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                # Musical creativity analysis
                y, sr = librosa.load(content_path)
                
                harmony_score = self._analyze_musical_harmony(y, sr)
                rhythm_score = self._analyze_rhythm_complexity(y, sr)
                
                score = np.mean([harmony_score, rhythm_score]) * criterion.max_score
                metrics.update({
                    "harmony_score": harmony_score,
                    "rhythm_score": rhythm_score
                })
                
            else:
                # Generic creative assessment
                score = 0.6 * criterion.max_score
                
            # Determine status and generate recommendations
            percentage = (score / criterion.max_score) * 100
            status = self._determine_assessment_status(percentage, criterion)
            recommendations = self._generate_creative_recommendations(
                content_type, criterion.name, score, criterion.max_score, metrics
            )
            
            return AssessmentResult(
                criteria_name=criterion.name,
                score=score,
                max_score=criterion.max_score,
                percentage=percentage,
                status=status,
                details=metrics,
                recommendations=recommendations,
                processing_time=0.0
            )
            
        except Exception as e:
            raise AssessmentError(f"Creative assessment failed: {str(e)}")

    # Helper methods for specific analysis tasks
    def _calculate_video_stability(self, frames: List[np.ndarray]) -> float:
        """Calculate video stability score"""        try:
            if len(frames) < 2:
                return 0.5
                
            motion_vectors = []
            for i in range(1, len(frames)):
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    frames[i-1], frames[i], 
                    corners=cv2.goodFeaturesToTrack(frames[i-1], 100, 0.3, 7),
                    nextPts=None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    motion_magnitude = np.mean(np.linalg.norm(flow, axis=1))
                    motion_vectors.append(motion_magnitude)
                    
            if motion_vectors:
                stability = 1.0 / (1.0 + np.std(motion_vectors))
                return min(stability, 1.0)
            else:
                return 0.5
                
        except Exception:
            return 0.5

    def _analyze_image_composition(self, image: np.ndarray) -> float:
        """Analyze image composition quality"""        try:
            # Rule of thirds analysis
            height, width = image.shape[:2]
            thirds_h = height // 3
            thirds_w = width // 3
            
            # Check for interesting points along rule of thirds lines
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Detect corners/features
            corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
            
            if corners is not None:
                rule_of_thirds_score = 0
                for corner in corners:
                    x, y = corner.ravel()
                    
                    # Check proximity to rule of thirds lines
                    if (abs(x - thirds_w) < width * 0.05 or 
                        abs(x - 2*thirds_w) < width * 0.05 or
                        abs(y - thirds_h) < height * 0.05 or 
                        abs(y - 2*thirds_h) < height * 0.05):
                        rule_of_thirds_score += 1
                        
                rule_of_thirds_score = min(rule_of_thirds_score / 10, 1.0)
            else:
                rule_of_thirds_score = 0.5
                
            # Balance analysis
            left_half = gray[:, :width//2]
            right_half = gray[:, width//2:]
            balance_score = 1.0 - abs(np.mean(left_half) - np.mean(right_half)) / 255
            
            return np.mean([rule_of_thirds_score, balance_score])
            
        except Exception:
            return 0.5

    def _analyze_color_harmony(self, image: np.ndarray) -> float:
        """Analyze color harmony in image"""        try:
            if len(image.shape) != 3:
                return 0.5
                
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Analyze hue distribution
            hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hue_hist = hue_hist.flatten() / hue_hist.sum()
            
            # Check for complementary colors (opposite hues)
            complementary_score = 0
            for i in range(90):
                if hue_hist[i] > 0.01 and hue_hist[i + 90] > 0.01:
                    complementary_score += min(hue_hist[i], hue_hist[i + 90])
                    
            # Check for analogous colors (adjacent hues)
            analogous_score = 0
            for i in range(len(hue_hist) - 30):
                window = hue_hist[i:i+30]
                if np.sum(window) > 0.3:  # 30% of colors in 30-degree range
                    analogous_score += np.sum(window)
                    
            # Combine scores
            harmony_score = np.mean([
                min(complementary_score * 10, 1.0),
                min(analogous_score, 1.0)
            ])
            
            return harmony_score
            
        except Exception:
            return 0.5

    def _analyze_text_creativity(self, text: str) -> float:
        """Analyze text creativity and originality"""        try:
            # Vocabulary diversity
            words = text.lower().split()
            unique_words = set(words)
            vocabulary_diversity = len(unique_words) / max(len(words), 1)
            
            # Sentence structure variety
            sentences = text.split('.')
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            
            if sentence_lengths:
                length_variety = np.std(sentence_lengths) / max(np.mean(sentence_lengths), 1)
                length_variety = min(length_variety, 1.0)
            else:
                length_variety = 0.5
                
            # Metaphor and imagery detection (simplified)
            metaphor_indicators = ['like', 'as', 'metaphor', 'symbol', 'represents', 'embodies']
            metaphor_count = sum(1 for word in metaphor_indicators if word in text.lower())
            metaphor_score = min(metaphor_count / max(len(words) / 100, 1), 1.0)
            
            return np.mean([vocabulary_diversity, length_variety, metaphor_score])
            
        except Exception:
            return 0.5

    def _analyze_musical_harmony(self, y: np.ndarray, sr: int) -> float:
        """Analyze musical harmony and chord progressions"""        try:
            # Chromagram analysis
            chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Chord diversity
            chord_changes = np.diff(chromagram, axis=1)
            chord_variety = np.mean(np.std(chord_changes, axis=0))
            
            # Harmonic consistency
            harmonic_consistency = 1.0 - np.std(np.mean(chromagram, axis=1))
            
            return np.mean([min(chord_variety * 2, 1.0), harmonic_consistency])
            
        except Exception:
            return 0.5

    def _analyze_rhythm_complexity(self, y: np.ndarray, sr: int) -> float:
        """Analyze rhythmic complexity and patterns"""        try:
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            if len(beats) > 1:
                # Beat consistency
                beat_intervals = np.diff(beats)
                beat_consistency = 1.0 - (np.std(beat_intervals) / max(np.mean(beat_intervals), 1))
                
                # Rhythmic complexity (syncopation detection)
                onset_strength = librosa.onset.onset_strength(y=y, sr=sr)
                rhythmic_complexity = np.std(onset_strength) / max(np.mean(onset_strength), 1)
                rhythmic_complexity = min(rhythmic_complexity, 1.0)
                
                return np.mean([beat_consistency, rhythmic_complexity])
            else:
                return 0.5
                
        except Exception:
            return 0.5

    def _determine_assessment_status(
        self, 
        percentage: float, 
        criterion: AssessmentCriteria
    ) -> str:
        """Determine assessment status based on thresholds"""        
        if percentage >= criterion.target_threshold * 100:
            return "pass"
        elif percentage >= criterion.min_threshold * 100:
            return "warning"
        else:
            return "fail"

    def _generate_audio_recommendations(
        self,
        criteria_name: str,
        score: float,
        max_score: float,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate audio quality improvement recommendations"""        
        recommendations = []
        percentage = (score / max_score) * 100
        
        if criteria_name == "audio_bitrate" and percentage < 70:
            recommendations.extend([
                "Increase audio bitrate to at least 256kbps for better quality",
                "Consider using lossless formats for master recordings",
                "Optimize encoding settings for target platform"
            ])
            
        elif criteria_name == "audio_dynamic_range" and percentage < 70:
            recommendations.extend([
                "Improve dynamic range by reducing over-compression",
                "Use gentle compression ratios (3:1 or less)",
                "Leave headroom for natural dynamics"
            ])
            
        elif criteria_name == "audio_noise_floor" and percentage < 70:
            recommendations.extend([
                "Reduce background noise using noise reduction tools",
                "Record in acoustically treated environment",
                "Use high-quality recording equipment"
            ])
            
        return recommendations

    def _generate_video_recommendations(
        self,
        criteria_name: str,
        score: float,
        max_score: float,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate video quality improvement recommendations"""        
        recommendations = []
        percentage = (score / max_score) * 100
        
        if criteria_name == "video_resolution" and percentage < 70:
            recommendations.extend([
                "Increase recording resolution to at least 1080p",
                "Use 4K recording for future-proofing",
                "Ensure proper camera settings and focus"
            ])
            
        elif criteria_name == "video_stability" and percentage < 70:
            recommendations.extend([
                "Use tripod or stabilization equipment",
                "Apply post-production stabilization",
                "Consider gimbal for smooth camera movements"
            ])
            
        return recommendations

    def _generate_creative_recommendations(
        self,
        content_type: ContentType,
        criteria_name: str,
        score: float,
        max_score: float,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate creative quality improvement recommendations"""        
        recommendations = []
        percentage = (score / max_score) * 100
        
        if percentage < 70:
            if content_type == ContentType.IMAGE:
                recommendations.extend([
                    "Apply rule of thirds for better composition",
                    "Improve color harmony and balance",
                    "Consider different angles and perspectives"
                ])
                
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                recommendations.extend([
                    "Increase vocabulary diversity",
                    "Vary sentence structure and length",
                    "Add more creative elements like metaphors"
                ])
                
            elif content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                recommendations.extend([
                    "Explore more complex chord progressions",
                    "Add rhythmic variety and syncopation",
                    "Incorporate creative production techniques"
                ])
                
        return recommendations

    def _calculate_overall_score(
        self, 
        category_scores: Dict[str, float], 
        categories: List[AssessmentCategory]
    ) -> float:
        """Calculate weighted overall quality score"""        
        # Default weights for categories
        default_weights = {
            AssessmentCategory.TECHNICAL: 0.30,
            AssessmentCategory.CREATIVE: 0.25,
            AssessmentCategory.COMMERCIAL: 0.15,
            AssessmentCategory.COMPLIANCE: 0.10,
            AssessmentCategory.ACCESSIBILITY: 0.10,
            AssessmentCategory.ENGAGEMENT: 0.10
        }
        
        # Calculate weighted score
        total_weight = 0
        weighted_sum = 0
        
        for category in categories:
            if category.value in category_scores:
                weight = default_weights.get(category, 0.1)
                weighted_sum += category_scores[category.value] * weight
                total_weight += weight
                
        return weighted_sum / max(total_weight, 1.0) if total_weight > 0 else 0.0

    def _determine_quality_grade(self, overall_score: float) -> str:
        """Determine quality grade from overall score"""        
        if overall_score >= 90:
            return "A+"
        elif overall_score >= 85:
            return "A"
        elif overall_score >= 80:
            return "B+"
        elif overall_score >= 75:
            return "B"
        elif overall_score >= 70:
            return "C+"
        elif overall_score >= 65:
            return "C"
        elif overall_score >= 60:
            return "D+"
        elif overall_score >= 55:
            return "D"
        else:
            return "F"

    def _check_compliance_status(self, results: List[AssessmentResult]) -> str:
        """Check overall compliance status"""        
        compliance_results = [r for r in results if "compliance" in r.criteria_name.lower()]
        
        if not compliance_results:
            return "not_assessed"
            
        failed_count = sum(1 for r in compliance_results if r.status == "fail")
        warning_count = sum(1 for r in compliance_results if r.status == "warning")
        
        if failed_count > 0:
            return "non_compliant"
        elif warning_count > 0:
            return "partially_compliant"
        else:
            return "compliant"

    def _calculate_improvement_potential(self, results: List[AssessmentResult]) -> float:
        """Calculate improvement potential percentage"""        
        if not results:
            return 0.0
            
        current_total = sum(r.score for r in results)
        max_total = sum(r.max_score for r in results)
        
        if max_total > 0:
            current_percentage = (current_total / max_total) * 100
            return 100 - current_percentage
        else:
            return 0.0

    def _initialize_nlp_models(self):
        """Initialize NLP models for text analysis"""        try:
            # Download required NLTK data
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Load spaCy model if available
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.nlp = None
                self.logger.warning("spaCy model not available, using basic text analysis")
                
        except Exception as e:
            self.logger.warning(f"NLP model initialization failed: {str(e)}")

    def _load_assessment_criteria(self) -> Dict[str, List[AssessmentCriteria]]:
        """Load assessment criteria for different content types"""        
        criteria = {
            "audio": [
                AssessmentCriteria(
                    category=AssessmentCategory.TECHNICAL,
                    name="audio_bitrate",
                    weight=0.3,
                    min_threshold=0.5,
                    target_threshold=0.8,
                    max_score=100,
                    evaluation_method="technical_analysis"
                ),
                AssessmentCriteria(
                    category=AssessmentCategory.TECHNICAL,
                    name="audio_dynamic_range",
                    weight=0.25,
                    min_threshold=0.4,
                    target_threshold=0.7,
                    max_score=100,
                    evaluation_method="technical_analysis"
                ),
                AssessmentCriteria(
                    category=AssessmentCategory.CREATIVE,
                    name="musical_creativity",
                    weight=0.4,
                    min_threshold=0.5,
                    target_threshold=0.75,
                    max_score=100,
                    evaluation_method="creative_analysis"
                )
            ],
            "video": [
                AssessmentCriteria(
                    category=AssessmentCategory.TECHNICAL,
                    name="video_resolution",
                    weight=0.3,
                    min_threshold=0.6,
                    target_threshold=0.8,
                    max_score=100,
                    evaluation_method="technical_analysis"
                ),
                AssessmentCriteria(
                    category=AssessmentCategory.TECHNICAL,
                    name="video_stability",
                    weight=0.25,
                    min_threshold=0.5,
                    target_threshold=0.8,
                    max_score=100,
                    evaluation_method="technical_analysis"
                )
            ],
            "text": [
                AssessmentCriteria(
                    category=AssessmentCategory.TECHNICAL,
                    name="readability",
                    weight=0.3,
                    min_threshold=0.6,
                    target_threshold=0.8,
                    max_score=100,
                    evaluation_method="technical_analysis"
                ),
                AssessmentCriteria(
                    category=AssessmentCategory.CREATIVE,
                    name="creativity",
                    weight=0.35,
                    min_threshold=0.5,
                    target_threshold=0.75,
                    max_score=100,
                    evaluation_method="creative_analysis"
                )
            ]
        }
        
        return criteria

    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry quality benchmarks"""        
        return {
            "audio": {
                "professional": 90.0,
                "prosumer": 75.0,
                "consumer": 60.0,
                "minimum": 40.0
            },
            "video": {
                "broadcast": 95.0,
                "professional": 85.0,
                "prosumer": 70.0,
                "consumer": 55.0
            },
            "image": {
                "professional": 90.0,
                "stock_photo": 80.0,
                "social_media": 65.0,
                "web": 50.0
            },
            "text": {
                "professional": 85.0,
                "editorial": 75.0,
                "blog": 65.0,
                "social": 50.0
            }
        }

    def _get_assessment_criteria(
        self,
        content_type: ContentType,
        categories: List[AssessmentCategory],
        custom_criteria: Optional[List[AssessmentCriteria]] = None
    ) -> List[AssessmentCriteria]:
        """Get assessment criteria for content type and categories"""        
        criteria = []
        
        # Get standard criteria
        content_type_key = content_type.value.lower()
        if content_type_key in self.assessment_criteria:
            for criterion in self.assessment_criteria[content_type_key]:
                if criterion.category in categories:
                    criteria.append(criterion)
                    
        # Add custom criteria
        if custom_criteria:
            criteria.extend(custom_criteria)
            
        return criteria

    async def _compare_with_benchmarks(
        self,
        content_type: ContentType,
        category_scores: Dict[str, float],
        overall_score: float
    ) -> Dict[str, Any]:
        """Compare scores with industry benchmarks"""        
        content_benchmarks = self.benchmarks.get(content_type.value.lower(), {})
        
        comparison = {
            "content_type": content_type.value,
            "overall_score": overall_score,
            "benchmark_comparison": {},
            "ranking": "unknown",
            "improvement_targets": {}
        }
        
        # Compare with benchmarks
        for benchmark_name, benchmark_score in content_benchmarks.items():
            if overall_score >= benchmark_score:
                comparison["benchmark_comparison"][benchmark_name] = "exceeds"
            elif overall_score >= benchmark_score * 0.9:
                comparison["benchmark_comparison"][benchmark_name] = "meets"
            else:
                comparison["benchmark_comparison"][benchmark_name] = "below"
                comparison["improvement_targets"][benchmark_name] = benchmark_score - overall_score
                
        # Determine overall ranking
        if overall_score >= content_benchmarks.get("professional", 90):
            comparison["ranking"] = "professional"
        elif overall_score >= content_benchmarks.get("prosumer", 75):
            comparison["ranking"] = "prosumer"
        elif overall_score >= content_benchmarks.get("consumer", 60):
            comparison["ranking"] = "consumer"
        else:
            comparison["ranking"] = "below_standard"
            
        return comparison

    async def _update_assessment_metrics(self, assessment: DetailedAssessment) -> None:
        """Update performance metrics for assessment"""        
        # Update processing time metrics
        content_type = assessment.content_type.value
        if content_type not in self.performance_metrics:
            self.performance_metrics[content_type] = {
                "total_assessments": 0,
                "total_time": 0.0,
                "average_time": 0.0,
                "score_distribution": []
            }
            
        metrics = self.performance_metrics[content_type]
        metrics["total_assessments"] += 1
        metrics["total_time"] += assessment.assessment_duration
        metrics["average_time"] = metrics["total_time"] / metrics["total_assessments"]
        metrics["score_distribution"].append(assessment.overall_score)
        
        # Keep only last 1000 scores for distribution
        if len(metrics["score_distribution"]) > 1000:
            metrics["score_distribution"] = metrics["score_distribution"][-1000:]

class ContentScorer:
    """    Specialized content scoring engine for rapid quality evaluation.
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def quick_score(
        self,
        content_path: str,
        content_type: ContentType
    ) -> float:
        """Generate quick quality score (0-100)"""        
        try:
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                return await self._quick_audio_score(content_path)
            elif content_type == ContentType.VIDEO:
                return await self._quick_video_score(content_path)
            elif content_type == ContentType.IMAGE:
                return await self._quick_image_score(content_path)
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                return await self._quick_text_score(content_path)
            else:
                return 50.0  # Default score
                
        except Exception as e:
            self.logger.error(f"Quick scoring failed: {str(e)}")
            return 0.0

    async def _quick_audio_score(self, content_path: str) -> float:
        """Quick audio quality score"""        try:
            y, sr = librosa.load(content_path, duration=30)  # Analyze first 30 seconds
            
            # Basic quality indicators
            rms = np.mean(librosa.feature.rms(y=y))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            
            # Normalize scores
            rms_score = min(rms * 10, 1.0) * 30
            spectral_score = min(spectral_centroid / 2000, 1.0) * 30
            duration_score = min(len(y) / sr / 60, 1.0) * 40  # Prefer longer content
            
            return rms_score + spectral_score + duration_score
            
        except Exception:
            return 25.0

    async def _quick_video_score(self, content_path: str) -> float:
        """Quick video quality score"""        try:
            cap = cv2.VideoCapture(content_path)
            
            # Basic video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            cap.release()
            
            # Score based on resolution and framerate
            resolution_score = min((width * height) / 2073600, 1.0) * 50  # 1080p reference
            fps_score = min(fps / 30, 1.0) * 50
            
            return resolution_score + fps_score
            
        except Exception:
            return 25.0

    async def _quick_image_score(self, content_path: str) -> float:
        """Quick image quality score"""        try:
            image = cv2.imread(content_path)
            height, width = image.shape[:2]
            
            # Resolution score
            resolution_score = min((width * height) / 2000000, 1.0) * 40  # 2MP reference
            
            # Basic sharpness detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000, 1.0) * 60
            
            return resolution_score + sharpness_score
            
        except Exception:
            return 25.0

    async def _quick_text_score(self, content_path: str) -> float:
        """Quick text quality score"""        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            # Basic metrics
            word_count = len(text.split())
            char_count = len(text)
            
            # Length score (prefer moderate length)
            if 100 <= word_count <= 2000:
                length_score = 40
            else:
                length_score = max(0, 40 - abs(word_count - 500) / 50)
                
            # Readability score
            try:
                fk_score = flesch_kincaid_grade(text)
                readability_score = max(0, 60 - abs(fk_score - 10) * 5)  # Target grade 10
            except:
                readability_score = 30
                
            return length_score + readability_score
            
        except Exception:
            return 25.0
