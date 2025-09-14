"""Quality Analyzer - Advanced quality analysis and metrics for IA Influencer Agent Platform
===========================================================================================

Professional quality analysis engine providing comprehensive quality assessment,
metrics calculation, and improvement recommendations for content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import statistics
import math
import hashlib

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Quality dimensions for analysis."""
    
    TECHNICAL = "technical"         # Technical quality (resolution, bitrate, etc.)
    PERCEPTUAL = "perceptual"      # Human-perceived quality
    STRUCTURAL = "structural"       # File structure and integrity
    COMPRESSION = "compression"     # Compression efficiency
    AESTHETIC = "aesthetic"         # Visual/audio aesthetics
    SEMANTIC = "semantic"          # Content meaning and relevance
    ACCESSIBILITY = "accessibility" # Accessibility features
    PERFORMANCE = "performance"     # Processing performance impact


class QualityGrade(Enum):
    """Quality grades."""
    
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # 30-49%
    VERY_POOR = "very_poor" # 0-29%


class ContentType(Enum):
    """Content types for quality analysis."""
    
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED = "mixed"


@dataclass
class QualityMetric:
    """Individual quality metric."""
    
    name: str
    value: float  # 0.0 to 1.0
    weight: float = 1.0
    description: str = ""
    unit: str = ""
    benchmark: Optional[float] = None
    threshold_excellent: float = 0.9
    threshold_good: float = 0.7
    threshold_fair: float = 0.5
    threshold_poor: float = 0.3


@dataclass
class QualityReport:
    """Comprehensive quality analysis report."""
    
    overall_score: float  # 0.0 to 1.0
    overall_grade: QualityGrade
    content_type: ContentType
    analysis_timestamp: float = field(default_factory=time.time)
    
    # Dimension scores
    technical_score: float = 0.0
    perceptual_score: float = 0.0
    structural_score: float = 0.0
    compression_score: float = 0.0
    aesthetic_score: float = 0.0
    semantic_score: float = 0.0
    accessibility_score: float = 0.0
    performance_score: float = 0.0
    
    # Detailed metrics
    metrics: Dict[str, QualityMetric] = field(default_factory=dict)
    
    # Analysis details
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    improvement_potential: float = 0.0
    
    # Technical details
    file_size: Optional[int] = None
    processing_time: float = 0.0
    analysis_method: str = "comprehensive"
    
    # Warnings and issues
    warnings: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)


@dataclass
class QualityBenchmark:
    """Quality benchmark for comparison."""
    
    name: str
    content_type: ContentType
    benchmark_scores: Dict[str, float]
    description: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class ImprovementSuggestion:
    """Quality improvement suggestion."""
    
    area: str
    current_score: float
    target_score: float
    impact: str  # low, medium, high
    difficulty: str  # easy, medium, hard
    description: str
    steps: List[str] = field(default_factory=list)
    estimated_time: Optional[str] = None
    tools_required: List[str] = field(default_factory=list)


class QualityAnalyzer:
    """Advanced quality analysis engine."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize quality analyzer with configuration."""
        self.config = config or {}
        
        # Quality benchmarks
        self.benchmarks = {}
        self._load_quality_benchmarks()
        
        # Analysis models and algorithms
        self.analysis_models = {}
        self._initialize_analysis_models()
        
        # Quality thresholds
        self.quality_thresholds = self._load_quality_thresholds()
        
        # Analysis history
        self.analysis_history = []
        
        logger.info("QualityAnalyzer initialized")
    
    def _load_quality_benchmarks(self) -> None:
        """Load quality benchmarks for different content types."""
        benchmarks = [
            QualityBenchmark(
                name="High-Quality Video",
                content_type=ContentType.VIDEO,
                benchmark_scores={
                    "resolution": 0.9,
                    "bitrate": 0.85,
                    "frame_rate": 0.8,
                    "compression_efficiency": 0.8,
                    "color_accuracy": 0.9,
                    "motion_smoothness": 0.85
                },
                description="Benchmark for high-quality video content"
            ),
            QualityBenchmark(
                name="Professional Audio",
                content_type=ContentType.AUDIO,
                benchmark_scores={
                    "sample_rate": 0.9,
                    "bit_depth": 0.85,
                    "dynamic_range": 0.8,
                    "frequency_response": 0.85,
                    "noise_floor": 0.9,
                    "distortion": 0.95
                },
                description="Benchmark for professional audio quality"
            ),
            QualityBenchmark(
                name="High-Resolution Image",
                content_type=ContentType.IMAGE,
                benchmark_scores={
                    "resolution": 0.9,
                    "color_depth": 0.85,
                    "sharpness": 0.8,
                    "noise_level": 0.9,
                    "compression_artifacts": 0.85,
                    "color_accuracy": 0.9
                },
                description="Benchmark for high-resolution images"
            ),
            QualityBenchmark(
                name="Professional Document",
                content_type=ContentType.DOCUMENT,
                benchmark_scores={
                    "readability": 0.9,
                    "structure": 0.85,
                    "formatting": 0.8,
                    "accessibility": 0.8,
                    "content_quality": 0.85,
                    "language_quality": 0.9
                },
                description="Benchmark for professional documents"
            )
        ]
        
        for benchmark in benchmarks:
            self.benchmarks[benchmark.name] = benchmark
    
    def _initialize_analysis_models(self) -> None:
        """Initialize analysis models and algorithms."""
        # Placeholder for ML models and analysis algorithms
        self.analysis_models = {
            "image_quality": {
                "sharpness_detector": None,
                "noise_analyzer": None,
                "color_analyzer": None,
                "composition_analyzer": None
            },
            "audio_quality": {
                "spectrum_analyzer": None,
                "distortion_detector": None,
                "dynamic_range_analyzer": None,
                "mastering_analyzer": None
            },
            "video_quality": {
                "motion_analyzer": None,
                "compression_analyzer": None,
                "frame_quality_analyzer": None,
                "temporal_analyzer": None
            },
            "text_quality": {
                "readability_analyzer": None,
                "grammar_checker": None,
                "coherence_analyzer": None,
                "style_analyzer": None
            }
        }
        
        logger.debug("Analysis models initialized (placeholder mode)")
    
    def _load_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load quality thresholds for different metrics."""
        return {
            "video": {
                "resolution_1080p": 0.8,
                "resolution_4k": 0.95,
                "bitrate_streaming": 0.7,
                "bitrate_broadcast": 0.9,
                "frame_rate_smooth": 0.8,
                "compression_efficient": 0.75
            },
            "audio": {
                "sample_rate_cd": 0.8,
                "sample_rate_hires": 0.95,
                "bit_depth_16": 0.7,
                "bit_depth_24": 0.9,
                "dynamic_range_good": 0.75,
                "thd_low": 0.9
            },
            "image": {
                "resolution_hd": 0.7,
                "resolution_uhd": 0.9,
                "color_depth_8bit": 0.7,
                "color_depth_16bit": 0.9,
                "sharpness_good": 0.75,
                "noise_low": 0.8
            },
            "text": {
                "readability_good": 0.7,
                "grammar_excellent": 0.9,
                "coherence_good": 0.75,
                "accessibility_compliant": 0.8
            }
        }
    
    async def analyze_quality(
        self,
        content: Union[str, bytes, Path],
        content_type: ContentType,
        analysis_depth: str = "comprehensive",  # basic, standard, comprehensive
        benchmark_name: Optional[str] = None
    ) -> QualityReport:
        """
        Analyze content quality comprehensively.
        
        Args:
            content: Content to analyze
            content_type: Type of content
            analysis_depth: Depth of analysis
            benchmark_name: Benchmark to compare against
            
        Returns:
            QualityReport with detailed analysis
        """
        start_time = time.time()
        
        try:
            # Prepare content for analysis
            content_data = await self._prepare_content(content)
            
            # Initialize quality report
            report = QualityReport(
                overall_score=0.0,
                overall_grade=QualityGrade.POOR,
                content_type=content_type,
                file_size=len(content_data) if isinstance(content_data, bytes) else len(str(content_data)),
                analysis_method=analysis_depth
            )
            
            # Perform dimension-specific analysis
            if content_type == ContentType.VIDEO:
                await self._analyze_video_quality(content_data, report, analysis_depth)
            elif content_type == ContentType.AUDIO:
                await self._analyze_audio_quality(content_data, report, analysis_depth)
            elif content_type == ContentType.IMAGE:
                await self._analyze_image_quality(content_data, report, analysis_depth)
            elif content_type == ContentType.TEXT:
                await self._analyze_text_quality(content_data, report, analysis_depth)
            elif content_type == ContentType.DOCUMENT:
                await self._analyze_document_quality(content_data, report, analysis_depth)
            else:
                await self._analyze_generic_quality(content_data, report, analysis_depth)
            
            # Calculate overall scores
            await self._calculate_overall_scores(report)
            
            # Compare against benchmark if specified
            if benchmark_name and benchmark_name in self.benchmarks:
                await self._compare_against_benchmark(report, self.benchmarks[benchmark_name])
            
            # Generate recommendations
            await self._generate_recommendations(report)
            
            # Calculate improvement potential
            report.improvement_potential = await self._calculate_improvement_potential(report)
            
            # Finalize report
            report.processing_time = time.time() - start_time
            report.overall_grade = self._score_to_grade(report.overall_score)
            
            # Store in history
            self.analysis_history.append(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {str(e)}")
            return QualityReport(
                overall_score=0.0,
                overall_grade=QualityGrade.POOR,
                content_type=content_type,
                processing_time=time.time() - start_time,
                critical_issues=[f"Analysis failed: {str(e)}"]
            )
    
    async def _prepare_content(self, content: Union[str, bytes, Path]) -> Union[str, bytes]:
        """Prepare content for analysis."""
        if isinstance(content, (str, bytes)):
            return content
        elif isinstance(content, Path):
            if content.exists():
                return content.read_bytes()
            else:
                raise FileNotFoundError(f"File not found: {content}")
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
    
    async def _analyze_video_quality(self, content -> None: bytes, report -> None: QualityReport, depth -> None: str) -> None:
        """Analyze video quality metrics."""
        # Placeholder implementation - would use actual video analysis
        
        # Technical quality metrics
        resolution_metric = QualityMetric(
            name="resolution",
            value=0.8,  # Placeholder
            description="Video resolution quality",
            unit="pixels",
            benchmark=1920*1080
        )
        report.metrics["resolution"] = resolution_metric
        
        bitrate_metric = QualityMetric(
            name="bitrate",
            value=0.75,
            description="Video bitrate adequacy",
            unit="mbps"
        )
        report.metrics["bitrate"] = bitrate_metric
        
        frame_rate_metric = QualityMetric(
            name="frame_rate",
            value=0.85,
            description="Frame rate smoothness",
            unit="fps"
        )
        report.metrics["frame_rate"] = frame_rate_metric
        
        # Perceptual quality metrics
        motion_smoothness = QualityMetric(
            name="motion_smoothness",
            value=0.8,
            description="Motion blur and smoothness",
            weight=1.2
        )
        report.metrics["motion_smoothness"] = motion_smoothness
        
        # Compression metrics
        compression_efficiency = QualityMetric(
            name="compression_efficiency",
            value=0.7,
            description="Compression efficiency vs quality",
            weight=0.8
        )
        report.metrics["compression_efficiency"] = compression_efficiency
        
        # Calculate dimension scores
        report.technical_score = statistics.mean([
            resolution_metric.value, bitrate_metric.value, frame_rate_metric.value
        ])
        report.perceptual_score = motion_smoothness.value
        report.compression_score = compression_efficiency.value
    
    async def _analyze_audio_quality(self, content -> None: bytes, report -> None: QualityReport, depth -> None: str) -> None:
        """Analyze audio quality metrics."""
        # Placeholder implementation - would use actual audio analysis
        
        # Technical metrics
        sample_rate_metric = QualityMetric(
            name="sample_rate",
            value=0.9,
            description="Audio sample rate quality",
            unit="Hz",
            benchmark=44100
        )
        report.metrics["sample_rate"] = sample_rate_metric
        
        bit_depth_metric = QualityMetric(
            name="bit_depth",
            value=0.8,
            description="Audio bit depth quality",
            unit="bits"
        )
        report.metrics["bit_depth"] = bit_depth_metric
        
        # Perceptual metrics
        dynamic_range_metric = QualityMetric(
            name="dynamic_range",
            value=0.85,
            description="Audio dynamic range",
            unit="dB",
            weight=1.3
        )
        report.metrics["dynamic_range"] = dynamic_range_metric
        
        frequency_response_metric = QualityMetric(
            name="frequency_response",
            value=0.8,
            description="Frequency response flatness",
            weight=1.1
        )
        report.metrics["frequency_response"] = frequency_response_metric
        
        # Quality metrics
        noise_floor_metric = QualityMetric(
            name="noise_floor",
            value=0.9,
            description="Background noise level",
            weight=1.2
        )
        report.metrics["noise_floor"] = noise_floor_metric
        
        distortion_metric = QualityMetric(
            name="distortion",
            value=0.95,
            description="Total harmonic distortion",
            weight=1.4
        )
        report.metrics["distortion"] = distortion_metric
        
        # Calculate dimension scores
        report.technical_score = statistics.mean([
            sample_rate_metric.value, bit_depth_metric.value
        ])
        report.perceptual_score = statistics.mean([
            dynamic_range_metric.value, frequency_response_metric.value,
            noise_floor_metric.value, distortion_metric.value
        ])
    
    async def _analyze_image_quality(self, content -> None: bytes, report -> None: QualityReport, depth -> None: str) -> None:
        """Analyze image quality metrics."""
        # Placeholder implementation - would use actual image analysis
        
        # Technical metrics
        resolution_metric = QualityMetric(
            name="resolution",
            value=0.85,
            description="Image resolution",
            unit="megapixels"
        )
        report.metrics["resolution"] = resolution_metric
        
        color_depth_metric = QualityMetric(
            name="color_depth",
            value=0.8,
            description="Color bit depth",
            unit="bits per channel"
        )
        report.metrics["color_depth"] = color_depth_metric
        
        # Perceptual metrics
        sharpness_metric = QualityMetric(
            name="sharpness",
            value=0.75,
            description="Image sharpness",
            weight=1.3
        )
        report.metrics["sharpness"] = sharpness_metric
        
        noise_level_metric = QualityMetric(
            name="noise_level",
            value=0.9,
            description="Image noise level (inverse)",
            weight=1.2
        )
        report.metrics["noise_level"] = noise_level_metric
        
        color_accuracy_metric = QualityMetric(
            name="color_accuracy",
            value=0.85,
            description="Color accuracy and saturation",
            weight=1.1
        )
        report.metrics["color_accuracy"] = color_accuracy_metric
        
        # Aesthetic metrics
        composition_metric = QualityMetric(
            name="composition",
            value=0.7,
            description="Image composition quality",
            weight=0.9
        )
        report.metrics["composition"] = composition_metric
        
        # Compression metrics
        compression_artifacts_metric = QualityMetric(
            name="compression_artifacts",
            value=0.8,
            description="Compression artifacts (inverse)",
            weight=1.1
        )
        report.metrics["compression_artifacts"] = compression_artifacts_metric
        
        # Calculate dimension scores
        report.technical_score = statistics.mean([
            resolution_metric.value, color_depth_metric.value
        ])
        report.perceptual_score = statistics.mean([
            sharpness_metric.value, noise_level_metric.value, color_accuracy_metric.value
        ])
        report.aesthetic_score = composition_metric.value
        report.compression_score = compression_artifacts_metric.value
    
    async def _analyze_text_quality(self, content -> None: Union[str, bytes], report -> None: QualityReport, depth -> None: str) -> None:
        """Analyze text quality metrics."""
        if isinstance(content, bytes):
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('utf-8', errors='ignore')
        else:
            text_content = content
        
        # Readability metrics
        readability_metric = QualityMetric(
            name="readability",
            value=self._calculate_readability_score(text_content),
            description="Text readability score",
            weight=1.4
        )
        report.metrics["readability"] = readability_metric
        
        # Grammar and language quality
        grammar_metric = QualityMetric(
            name="grammar",
            value=self._analyze_grammar_quality(text_content),
            description="Grammar and syntax quality",
            weight=1.3
        )
        report.metrics["grammar"] = grammar_metric
        
        # Coherence and structure
        coherence_metric = QualityMetric(
            name="coherence",
            value=self._analyze_text_coherence(text_content),
            description="Text coherence and flow",
            weight=1.2
        )
        report.metrics["coherence"] = coherence_metric
        
        # Content quality
        content_quality_metric = QualityMetric(
            name="content_quality",
            value=self._analyze_content_quality(text_content),
            description="Information quality and relevance",
            weight=1.1
        )
        report.metrics["content_quality"] = content_quality_metric
        
        # Accessibility
        accessibility_metric = QualityMetric(
            name="accessibility",
            value=self._analyze_text_accessibility(text_content),
            description="Text accessibility features",
            weight=1.0
        )
        report.metrics["accessibility"] = accessibility_metric
        
        # Calculate dimension scores
        report.structural_score = coherence_metric.value
        report.semantic_score = statistics.mean([
            grammar_metric.value, content_quality_metric.value
        ])
        report.accessibility_score = accessibility_metric.value
        report.perceptual_score = readability_metric.value
    
    async def _analyze_document_quality(self, content -> None: bytes, report -> None: QualityReport, depth -> None: str) -> None:
        """Analyze document quality metrics."""
        # Would implement document-specific analysis
        # For now, fall back to generic analysis
        await self._analyze_generic_quality(content, report, depth)
    
    async def _analyze_generic_quality(self, content -> None: Union[str, bytes], report -> None: QualityReport, depth -> None: str) -> None:
        """Analyze generic content quality."""
        # Basic structural metrics
        file_size = len(content) if isinstance(content, bytes) else len(content.encode())
        
        structural_metric = QualityMetric(
            name="structural_integrity",
            value=0.8,  # Placeholder
            description="Content structural integrity"
        )
        report.metrics["structural_integrity"] = structural_metric
        
        performance_metric = QualityMetric(
            name="performance_impact",
            value=0.7,  # Based on file size and complexity
            description="Performance impact of content"
        )
        report.metrics["performance_impact"] = performance_metric
        
        report.structural_score = structural_metric.value
        report.performance_score = performance_metric.value
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate text readability score."""
        if not text.strip():
            return 0.0
        
        # Simple readability calculation (Flesch-like)
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        # Simplified Flesch score, normalized to 0-1
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 range
        normalized_score = max(0.0, min(1.0, flesch_score / 100.0))
        
        return normalized_score
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _analyze_grammar_quality(self, text: str) -> float:
        """Analyze grammar quality (placeholder)."""
        # Placeholder implementation
        # Would use actual grammar checking library
        
        # Simple heuristics
        errors = 0
        
        # Check for basic punctuation
        if not any(p in text for p in '.!?'):
            errors += 1
        
        # Check for sentence case
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        for sentence in sentences:
            if sentence and not sentence[0].isupper():
                errors += 1
        
        # Normalize error rate
        total_sentences = len(sentences)
        if total_sentences == 0:
            return 0.5
        
        error_rate = errors / max(total_sentences, 1)
        quality_score = max(0.0, 1.0 - error_rate)
        
        return quality_score
    
    def _analyze_text_coherence(self, text: str) -> float:
        """Analyze text coherence and flow."""
        # Placeholder implementation
        # Would use semantic analysis
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 0.7  # Single sentence, assume decent coherence
        
        # Simple coherence metrics
        avg_sentence_length = statistics.mean(len(s.split()) for s in sentences)
        sentence_length_variance = statistics.variance(len(s.split()) for s in sentences) if len(sentences) > 1 else 0
        
        # Normalize variance (lower variance = better coherence)
        coherence_score = max(0.0, 1.0 - (sentence_length_variance / (avg_sentence_length ** 2)))
        
        return min(1.0, coherence_score)
    
    def _analyze_content_quality(self, text: str) -> float:
        """Analyze content information quality."""
        # Placeholder implementation
        # Would use semantic analysis and information density metrics
        
        words = text.split()
        
        if not words:
            return 0.0
        
        # Simple metrics
        unique_words = len(set(words))
        total_words = len(words)
        vocabulary_richness = unique_words / total_words if total_words > 0 else 0
        
        # Information density heuristic
        avg_word_length = statistics.mean(len(word) for word in words)
        
        # Combine metrics
        content_score = (vocabulary_richness * 0.6) + (min(avg_word_length / 10, 1.0) * 0.4)
        
        return min(1.0, content_score)
    
    def _analyze_text_accessibility(self, text: str) -> float:
        """Analyze text accessibility features."""
        # Placeholder implementation
        # Would check for accessibility features like alt text references, structure, etc.
        
        accessibility_score = 0.7  # Default moderate accessibility
        
        # Check for structure indicators
        if any(marker in text.lower() for marker in ['heading', 'title', 'caption']):
            accessibility_score += 0.1
        
        # Check for descriptive elements
        if any(desc in text.lower() for desc in ['description', 'alt text', 'figure']):
            accessibility_score += 0.1
        
        return min(1.0, accessibility_score)
    
    async def _calculate_overall_scores(self, report -> None: QualityReport) -> None:
        """Calculate overall quality scores from individual metrics."""
        # Calculate weighted average of all metrics
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for metric in report.metrics.values():
            weight = metric.weight
            total_weighted_score += metric.value * weight
            total_weight += weight
        
        if total_weight > 0:
            report.overall_score = total_weighted_score / total_weight
        else:
            report.overall_score = 0.0
        
        # Calculate dimension scores if not already set
        if report.technical_score == 0.0:
            technical_metrics = [m for m in report.metrics.values() 
                               if 'resolution' in m.name or 'bitrate' in m.name or 'sample_rate' in m.name]
            if technical_metrics:
                report.technical_score = statistics.mean(m.value for m in technical_metrics)
        
        if report.perceptual_score == 0.0:
            perceptual_metrics = [m for m in report.metrics.values() 
                                if 'quality' in m.name or 'smoothness' in m.name or 'clarity' in m.name]
            if perceptual_metrics:
                report.perceptual_score = statistics.mean(m.value for m in perceptual_metrics)
    
    async def _compare_against_benchmark(self, report -> None: QualityReport, benchmark -> None: QualityBenchmark) -> None:
        """Compare quality report against benchmark."""
        comparison_results = {}
        
        for metric_name, benchmark_score in benchmark.benchmark_scores.items():
            if metric_name in report.metrics:
                current_score = report.metrics[metric_name].value
                difference = current_score - benchmark_score
                comparison_results[metric_name] = {
                    "current": current_score,
                    "benchmark": benchmark_score,
                    "difference": difference,
                    "meets_benchmark": current_score >= benchmark_score
                }
        
        # Add comparison metadata
        report.metadata = report.metadata or {}
        report.metadata["benchmark_comparison"] = comparison_results
        report.metadata["benchmark_name"] = benchmark.name
    
    async def _generate_recommendations(self, report -> None: QualityReport) -> None:
        """Generate quality improvement recommendations."""
        recommendations = []
        strengths = []
        weaknesses = []
        
        # Analyze each metric
        for metric_name, metric in report.metrics.items():
            if metric.value >= metric.threshold_excellent:
                strengths.append(f"Excellent {metric_name} ({metric.value:.2f})")
            elif metric.value >= metric.threshold_good:
                strengths.append(f"Good {metric_name} ({metric.value:.2f})")
            elif metric.value <= metric.threshold_poor:
                weaknesses.append(f"Poor {metric_name} ({metric.value:.2f})")
                recommendations.append(f"Improve {metric_name} - currently below acceptable threshold")
            elif metric.value <= metric.threshold_fair:
                weaknesses.append(f"Fair {metric_name} ({metric.value:.2f})")
                recommendations.append(f"Consider improving {metric_name} for better quality")
        
        # Add general recommendations based on content type
        if report.content_type == ContentType.VIDEO:
            if report.technical_score < 0.7:
                recommendations.append("Consider increasing video bitrate and resolution")
            if report.compression_score < 0.6:
                recommendations.append("Optimize compression settings for better quality/size ratio")
        
        elif report.content_type == ContentType.AUDIO:
            if report.technical_score < 0.7:
                recommendations.append("Consider using higher sample rate and bit depth")
            if report.perceptual_score < 0.7:
                recommendations.append("Review audio mastering and dynamics processing")
        
        elif report.content_type == ContentType.IMAGE:
            if report.technical_score < 0.7:
                recommendations.append("Consider higher resolution and color depth")
            if report.aesthetic_score < 0.6:
                recommendations.append("Review image composition and visual appeal")
        
        elif report.content_type == ContentType.TEXT:
            if report.semantic_score < 0.7:
                recommendations.append("Review content for grammar and clarity")
            if report.accessibility_score < 0.7:
                recommendations.append("Improve accessibility features and structure")
        
        report.strengths = strengths
        report.weaknesses = weaknesses
        report.recommendations = recommendations
    
    async def _calculate_improvement_potential(self, report: QualityReport) -> float:
        """Calculate potential for quality improvement."""
        if not report.metrics:
            return 0.0
        
        # Calculate average distance from perfect score
        improvement_potential = 0.0
        total_weight = 0.0
        
        for metric in report.metrics.values():
            potential = (1.0 - metric.value) * metric.weight
            improvement_potential += potential
            total_weight += metric.weight
        
        if total_weight > 0:
            return improvement_potential / total_weight
        else:
            return 0.0
    
    def _score_to_grade(self, score: float) -> QualityGrade:
        """Convert numeric score to quality grade."""
        if score >= 0.9:
            return QualityGrade.EXCELLENT
        elif score >= 0.7:
            return QualityGrade.GOOD
        elif score >= 0.5:
            return QualityGrade.FAIR
        elif score >= 0.3:
            return QualityGrade.POOR
        else:
            return QualityGrade.VERY_POOR
    
    async def generate_improvement_suggestions(self, report: QualityReport) -> List[ImprovementSuggestion]:
        """Generate specific improvement suggestions based on quality analysis."""
        suggestions = []
        
        for metric_name, metric in report.metrics.items():
            if metric.value < metric.threshold_good:
                # Determine improvement target
                target_score = min(1.0, metric.threshold_excellent)
                improvement_needed = target_score - metric.value
                
                # Determine impact and difficulty
                if improvement_needed > 0.5:
                    impact = "high"
                    difficulty = "hard"
                elif improvement_needed > 0.3:
                    impact = "medium"
                    difficulty = "medium"
                else:
                    impact = "low"
                    difficulty = "easy"
                
                suggestion = ImprovementSuggestion(
                    area=metric_name,
                    current_score=metric.value,
                    target_score=target_score,
                    impact=impact,
                    difficulty=difficulty,
                    description=f"Improve {metric_name} from {metric.value:.2f} to {target_score:.2f}",
                    steps=self._get_improvement_steps(metric_name, report.content_type),
                    estimated_time=self._estimate_improvement_time(difficulty),
                    tools_required=self._get_required_tools(metric_name, report.content_type)
                )
                
                suggestions.append(suggestion)
        
        return suggestions
    
    def _get_improvement_steps(self, metric_name: str, content_type: ContentType) -> List[str]:
        """Get specific improvement steps for a metric."""
        steps_map = {
            "resolution": [
                "Increase capture resolution",
                "Use higher quality source material",
                "Avoid unnecessary downsampling"
            ],
            "bitrate": [
                "Increase encoding bitrate",
                "Use variable bitrate encoding",
                "Optimize encoder settings"
            ],
            "readability": [
                "Simplify sentence structure",
                "Use shorter sentences",
                "Improve paragraph organization"
            ],
            "grammar": [
                "Use grammar checking tools",
                "Proofread content carefully",
                "Consider professional editing"
            ]
        }
        
        return steps_map.get(metric_name, ["Review and optimize the specific quality aspect"])
    
    def _estimate_improvement_time(self, difficulty: str) -> str:
        """Estimate time required for improvement."""
        time_map = {
            "easy": "1-2 hours",
            "medium": "4-8 hours",
            "hard": "1-3 days"
        }
        return time_map.get(difficulty, "Variable")
    
    def _get_required_tools(self, metric_name: str, content_type: ContentType) -> List[str]:
        """Get tools required for improvement."""
        tool_map = {
            "resolution": ["High-resolution capture device", "Upscaling software"],
            "bitrate": ["Video encoder", "Bitrate analysis tools"],
            "readability": ["Text editor", "Readability analyzer"],
            "grammar": ["Grammar checker", "Spell checker", "Style guide"]
        }
        
        return tool_map.get(metric_name, ["Standard editing tools"])
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics and trends."""
        if not self.analysis_history:
            return {"message": "No analysis history available"}
        
        # Calculate statistics from history
        overall_scores = [report.overall_score for report in self.analysis_history]
        processing_times = [report.processing_time for report in self.analysis_history]
        
        # Content type distribution
        content_type_counts = {}
        for report in self.analysis_history:
            content_type = report.content_type.value
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        # Grade distribution
        grade_counts = {}
        for report in self.analysis_history:
            grade = report.overall_grade.value
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        return {
            "total_analyses": len(self.analysis_history),
            "average_quality_score": statistics.mean(overall_scores),
            "median_quality_score": statistics.median(overall_scores),
            "average_processing_time": statistics.mean(processing_times),
            "content_type_distribution": content_type_counts,
            "grade_distribution": grade_counts,
            "quality_trend": "improving" if len(overall_scores) > 5 and 
                            statistics.mean(overall_scores[-5:]) > statistics.mean(overall_scores[:-5]) 
                            else "stable"
        }


# Export all classes for module imports
__all__ = [
    "QualityAnalyzer",
    "QualityDimension",
    "QualityGrade",
    "ContentType",
    "QualityMetric",
    "QualityReport",
    "QualityBenchmark",
    "ImprovementSuggestion"
]

logger.info("Quality analyzer module loaded successfully")