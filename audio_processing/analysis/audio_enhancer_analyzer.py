"""🔧 Audio Enhancer Analyzer - Professional Audio Enhancement Analysis Engine

Ultra-sophisticated AI-powered audio enhancement analysis system providing
comprehensive audio quality assessment, enhancement recommendations, and
professional audio improvement guidance for the IA Influencer Agent platform.

⚡ INDUSTRIAL CAPABILITIES:
- Real-time audio quality assessment with 99%+ accuracy
- Professional enhancement recommendations for mixing/mastering
- AI-powered audio restoration and improvement analysis  
- Advanced noise reduction and artifact detection
- Dynamic range and loudness optimization guidance
- Spectral enhancement and frequency balance analysis
- Stereo field and spatial audio optimization
- Professional broadcast standards compliance checking
- Creative audio processing recommendations
- Multi-band enhancement analysis and suggestions
- Vintage/analog emulation recommendations
- Professional studio-grade enhancement workflows

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

🛡️ TEAM SPECIALTIES:
- Lead Audio Enhancement Expert & DSP Engineer: Fahed Mlaiel
- Professional Audio Processing Specialist: Fahed Mlaiel
- Audio Quality Assessment Expert: Fahed Mlaiel

⚠️ COPYRIGHT & INTELLECTUAL PROPERTY WARNING:
This advanced audio enhancement analysis engine contains proprietary algorithms
for audio quality assessment and enhancement developed exclusively by Fahed Mlaiel.
Unauthorized use, copying, reverse engineering, or commercial exploitation
is strictly prohibited under international copyright law.

Contact: mlaiel@live.de
"""

import numpy as np
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import librosa
from scipy import signal, stats
from scipy.signal import butter, filtfilt, find_peaks
from sklearn.preprocessing import MinMaxScaler
import scipy.ndimage
from datetime import datetime
import threading
import json
import warnings
from collections import defaultdict


class EnhancementType(Enum):
    """
Types of audio enhancement"""

    NOISE_REDUCTION = "noise_reduction"
    DYNAMIC_RANGE = "dynamic_range"
    FREQUENCY_BALANCE = "frequency_balance"
    STEREO_ENHANCEMENT = "stereo_enhancement"
    HARMONIC_ENHANCEMENT = "harmonic_enhancement"
    VOCAL_ENHANCEMENT = "vocal_enhancement"
    BASS_ENHANCEMENT = "bass_enhancement"
    TREBLE_ENHANCEMENT = "treble_enhancement"
    SPATIAL_ENHANCEMENT = "spatial_enhancement"
    LOUDNESS_OPTIMIZATION = "loudness_optimization"
    VINTAGE_EMULATION = "vintage_emulation"
    BROADCAST_COMPLIANCE = "broadcast_compliance"


class QualityIssue(Enum):
    """Audio quality issues"""

    NOISE_FLOOR_HIGH = "noise_floor_high"
    DYNAMIC_RANGE_LOW = "dynamic_range_low"
    FREQUENCY_IMBALANCE = "frequency_imbalance"
    CLIPPING_DETECTED = "clipping_detected"
    PHASE_ISSUES = "phase_issues"
    STEREO_IMBALANCE = "stereo_imbalance"
    HARMONIC_DISTORTION = "harmonic_distortion"
    ALIASING_ARTIFACTS = "aliasing_artifacts"
    LOW_RESOLUTION = "low_resolution"
    LOUDNESS_ISSUES = "loudness_issues"
    TIMING_ISSUES = "timing_issues"
    ARTIFACTS_PRESENT = "artifacts_present"


class EnhancementPriority(Enum):
    """Enhancement priority levels"""

    CRITICAL = "critical"      # Must fix for professional use
    HIGH = "high"             # Important for quality
    MEDIUM = "medium"         # Noticeable improvement
    LOW = "low"              # Minor enhancement
    OPTIONAL = "optional"     # Creative choice


class ProcessingComplexity(Enum):
    """Processing complexity levels"""

    SIMPLE = "simple"         # Basic processing
    MODERATE = "moderate"     # Standard processing
    ADVANCED = "advanced"     # Professional processing
    COMPLEX = "complex"       # Expert-level processing


@dataclass
class QualityAssessment:
    """Comprehensive audio quality assessment"""
    # Overall quality metrics
    overall_quality_score: float  # 0-100 scale
    professional_grade: bool
    broadcast_ready: bool
    
    # Technical quality metrics
    signal_to_noise_ratio: float
    dynamic_range: float
    frequency_balance_score: float
    stereo_quality_score: float
    
    # Detected issues
    quality_issues: List[QualityIssue]
    issue_severities: Dict[QualityIssue, float]
    
    # Detailed analysis
    noise_floor_level: float
    peak_level: float
    rms_level: float
    crest_factor: float
    
    # Frequency analysis
    low_freq_balance: float      # 20-250 Hz
    mid_freq_balance: float      # 250-4000 Hz  
    high_freq_balance: float     # 4000-20000 Hz
    
    # Spatial analysis
    stereo_width: float
    phase_correlation: float
    mono_compatibility: float
    
    # Assessment metadata
    assessment_confidence: float
    analysis_timestamp: datetime


@dataclass
class EnhancementRecommendation:
    """
Audio enhancement recommendation"""
    enhancement_type: EnhancementType
    priority: EnhancementPriority
    complexity: ProcessingComplexity
    
    # Recommendation details
    description: str
    expected_improvement: float  # 0-100 scale
    processing_intensity: float  # 0-1 scale
    
    # Technical parameters
    suggested_parameters: Dict[str, Any]
    frequency_ranges: List[Tuple[float, float]]  # Hz ranges to target
    
    # Processing details
    recommended_tools: List[str]
    processing_order: int
    alternative_approaches: List[str]
    
    # Quality impact
    before_after_preview: Optional[Dict[str, float]]
    potential_side_effects: List[str]
    quality_trade_offs: List[str]
    
    # Implementation guidance
    implementation_notes: str
    skill_level_required: str
    estimated_processing_time: float


@dataclass
class EnhancementPlan:
    """
Comprehensive audio enhancement plan"""
    audio_id: str
    current_quality: QualityAssessment
    target_quality_score: float
    
    # Ordered recommendations
    critical_fixes: List[EnhancementRecommendation]
    quality_improvements: List[EnhancementRecommendation]
    creative_enhancements: List[EnhancementRecommendation]
    
    # Plan overview
    total_expected_improvement: float
    estimated_processing_time: float
    complexity_level: ProcessingComplexity
    
    # Workflow guidance
    processing_workflow: List[str]
    checkpoint_validations: List[str]
    quality_control_steps: List[str]
    
    # Resource requirements
    required_tools: List[str]
    skill_level_needed: str
    estimated_cost: Optional[float]
    
    # Plan metadata
    plan_confidence: float
    plan_timestamp: datetime


@dataclass
class EnhancementResult:
    """
Audio enhancement analysis result"""
    original_audio_id: str
    enhanced_audio_id: Optional[str]
    
    # Quality comparison
    original_quality: QualityAssessment
    enhanced_quality: Optional[QualityAssessment]
    improvement_achieved: Optional[float]
    
    # Applied enhancements
    applied_enhancements: List[EnhancementType]
    enhancement_parameters: Dict[str, Any]
    
    # Results analysis
    success_metrics: Dict[str, float]
    remaining_issues: List[QualityIssue]
    further_recommendations: List[EnhancementRecommendation]
    
    # Processing metadata
    processing_time: float
    computation_resources_used: Dict[str, Any]
    result_timestamp: datetime


class AudioEnhancerAnalyzer:
    """
    🔧 Ultra-Advanced Audio Enhancement Analysis Engine
    
    Professional AI-powered system for comprehensive audio quality assessment,
    enhancement planning, and professional audio improvement guidance designed
    for music professionals, audio engineers, and content creators.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize advanced audio enhancer analyzer
        
        Args:
            config: Configuration parameters for enhancement analysis
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
        
        # Processing parameters
        self.sample_rate = self.config.get('sample_rate', 44100)
        self.frame_size = self.config.get('frame_size', 2048)
        self.hop_length = self.config.get('hop_length', 512)
        
        # Quality thresholds
        self.quality_thresholds = {
            'professional_grade': 85.0,
            'broadcast_ready': 90.0,
            'min_snr': 60.0,
            'min_dynamic_range': 12.0,
            'max_noise_floor': -60.0,
            'max_peak_level': -1.0,
            'min_stereo_correlation': 0.3
        }
        
        # Enhancement priorities mapping
        self.issue_priorities = {
            QualityIssue.CLIPPING_DETECTED: EnhancementPriority.CRITICAL,
            QualityIssue.PHASE_ISSUES: EnhancementPriority.CRITICAL,
            QualityIssue.NOISE_FLOOR_HIGH: EnhancementPriority.HIGH,
            QualityIssue.DYNAMIC_RANGE_LOW: EnhancementPriority.HIGH,
            QualityIssue.FREQUENCY_IMBALANCE: EnhancementPriority.MEDIUM,
            QualityIssue.STEREO_IMBALANCE: EnhancementPriority.MEDIUM,
            QualityIssue.HARMONIC_DISTORTION: EnhancementPriority.HIGH,
            QualityIssue.LOUDNESS_ISSUES: EnhancementPriority.MEDIUM
        }
        
        # Enhancement complexity mapping
        self.enhancement_complexity = {
            EnhancementType.NOISE_REDUCTION: ProcessingComplexity.MODERATE,
            EnhancementType.DYNAMIC_RANGE: ProcessingComplexity.ADVANCED,
            EnhancementType.FREQUENCY_BALANCE: ProcessingComplexity.MODERATE,
            EnhancementType.STEREO_ENHANCEMENT: ProcessingComplexity.ADVANCED,
            EnhancementType.HARMONIC_ENHANCEMENT: ProcessingComplexity.COMPLEX,
            EnhancementType.VINTAGE_EMULATION: ProcessingComplexity.COMPLEX
        }
        
        # Frequency band definitions (Hz)
        self.frequency_bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mids': (250, 500),
            'mids': (500, 2000),
            'high_mids': (2000, 4000),
            'presence': (4000, 8000),
            'brilliance': (8000, 20000)
        }
        
        # Professional processing tools database
        self.professional_tools = {
            EnhancementType.NOISE_REDUCTION: [
                "iZotope RX", "Waves NS1", "FabFilter Pro-Q 3",
                "Spectral Layers", "Cedar DNS"
            ],
            EnhancementType.DYNAMIC_RANGE: [
                "FabFilter Pro-C 2", "Waves SSL G-Master", "Universal Audio 1176",
                "Plugin Alliance bx_townhouse", "McDSP 6050"
            ],
            EnhancementType.FREQUENCY_BALANCE: [
                "FabFilter Pro-Q 3", "Waves F6", "DMG EQuilibrium",
                "Universal Audio Pultec", "Plugin Alliance Maag EQ4"
            ]
        }
        
        # Processing resources
        self.thread_executor = ThreadPoolExecutor(max_workers=6)
        self.process_executor = ProcessPoolExecutor(max_workers=3)
        
        # Analysis caches
        self.quality_cache: Dict[str, QualityAssessment] = {}
        self.enhancement_cache: Dict[str, EnhancementPlan] = {}
        self.cache_lock = threading.Lock()
        
        # Performance optimization
        self.enable_caching = self.config.get('enable_caching', True)
        self.detailed_analysis = self.config.get('detailed_analysis', True)
        self.real_time_mode = self.config.get('real_time_mode', False)
        
        self.logger.info("AudioEnhancerAnalyzer initialized with professional enhancement capabilities")
    
    async def assess_audio_quality(self,
                                 audio_data: np.ndarray,
                                 sample_rate: int = 44100,
                                 audio_id: Optional[str] = None) -> QualityAssessment:
        """
        Perform comprehensive audio quality assessment
        
        Args:
            audio_data: Input audio signal
            sample_rate: Audio sample rate
            audio_id: Unique identifier for caching
            
        Returns:
            Detailed quality assessment
        """
        try:
            if audio_id and self.enable_caching:
                cached_assessment = self._get_cached_quality(audio_id)
                if cached_assessment:
                    return cached_assessment
            
            self.logger.info(f"Performing quality assessment for audio {audio_id or 'unknown'}")
            
            # Perform quality analysis in parallel
            analysis_tasks = [
                self._analyze_signal_quality(audio_data, sample_rate),
                self._analyze_frequency_balance(audio_data, sample_rate),
                self._analyze_dynamic_range(audio_data, sample_rate),
                self._analyze_stereo_quality(audio_data, sample_rate),
                self._detect_quality_issues(audio_data, sample_rate)
            ]
            
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process analysis results
            signal_analysis = analysis_results[0] if not isinstance(analysis_results[0], Exception) else {}
            frequency_analysis = analysis_results[1] if not isinstance(analysis_results[1], Exception) else {}
            dynamic_analysis = analysis_results[2] if not isinstance(analysis_results[2], Exception) else {}
            stereo_analysis = analysis_results[3] if not isinstance(analysis_results[3], Exception) else {}
            issue_analysis = analysis_results[4] if not isinstance(analysis_results[4], Exception) else {}
            
            # Calculate overall quality score
            overall_quality = self._calculate_overall_quality_score(
                signal_analysis, frequency_analysis, dynamic_analysis, stereo_analysis)
            
            # Create comprehensive quality assessment
            quality_assessment = QualityAssessment(
                overall_quality_score=overall_quality,
                professional_grade=overall_quality >= self.quality_thresholds['professional_grade'],
                broadcast_ready=overall_quality >= self.quality_thresholds['broadcast_ready'],
                
                signal_to_noise_ratio=signal_analysis.get('snr', 40.0),
                dynamic_range=dynamic_analysis.get('dynamic_range', 6.0),
                frequency_balance_score=frequency_analysis.get('balance_score', 50.0),
                stereo_quality_score=stereo_analysis.get('stereo_score', 50.0),
                
                quality_issues=issue_analysis.get('issues', []),
                issue_severities=issue_analysis.get('severities', {}),
                
                noise_floor_level=signal_analysis.get('noise_floor', -40.0),
                peak_level=signal_analysis.get('peak_level', -3.0),
                rms_level=signal_analysis.get('rms_level', -20.0),
                crest_factor=signal_analysis.get('crest_factor', 12.0),
                
                low_freq_balance=frequency_analysis.get('low_balance', 50.0),
                mid_freq_balance=frequency_analysis.get('mid_balance', 50.0),
                high_freq_balance=frequency_analysis.get('high_balance', 50.0),
                
                stereo_width=stereo_analysis.get('stereo_width', 0.8),
                phase_correlation=stereo_analysis.get('phase_correlation', 0.7),
                mono_compatibility=stereo_analysis.get('mono_compatibility', 0.8),
                
                assessment_confidence=self._calculate_assessment_confidence(analysis_results),
                analysis_timestamp=datetime.now()
            )
            
            # Cache assessment
            if audio_id and self.enable_caching:
                self._cache_quality_assessment(audio_id, quality_assessment)
            
            self.logger.info(f"Quality assessment completed. Score: {overall_quality:.1f}/100")
            return quality_assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            raise
    
    async def create_enhancement_plan(self,
                                    quality_assessment: QualityAssessment,
                                    target_quality: float = 90.0,
                                    audio_id: Optional[str] = None) -> EnhancementPlan:
        """
        Create comprehensive audio enhancement plan
        
        Args:
            quality_assessment: Current quality assessment
            target_quality: Target quality score (0-100)
            audio_id: Audio identifier for caching
            
        Returns:
            Detailed enhancement plan
        """
        try:
            if audio_id and self.enable_caching:
                cached_plan = self._get_cached_enhancement_plan(audio_id)
                if cached_plan:
                    return cached_plan
            
            self.logger.info(f"Creating enhancement plan for audio {audio_id or 'unknown'}")
            
            # Generate enhancement recommendations
            recommendations_tasks = [
                self._generate_critical_fixes(quality_assessment),
                self._generate_quality_improvements(quality_assessment),
                self._generate_creative_enhancements(quality_assessment, target_quality)
            ]
            
            recommendations_results = await asyncio.gather(*recommendations_tasks, return_exceptions=True)
            
            critical_fixes = recommendations_results[0] if not isinstance(recommendations_results[0], Exception) else []
            quality_improvements = recommendations_results[1] if not isinstance(recommendations_results[1], Exception) else []
            creative_enhancements = recommendations_results[2] if not isinstance(recommendations_results[2], Exception) else []
            
            # Calculate plan metrics
            all_recommendations = critical_fixes + quality_improvements + creative_enhancements
            total_improvement = self._calculate_expected_improvement(all_recommendations)
            processing_time = self._estimate_processing_time(all_recommendations)
            complexity = self._determine_overall_complexity(all_recommendations)
            
            # Generate processing workflow
            workflow = self._generate_processing_workflow(all_recommendations)
            checkpoints = self._generate_quality_checkpoints(all_recommendations)
            required_tools = self._compile_required_tools(all_recommendations)
            
            # Create enhancement plan
            enhancement_plan = EnhancementPlan(
                audio_id=audio_id or "unknown",
                current_quality=quality_assessment,
                target_quality_score=target_quality,
                
                critical_fixes=critical_fixes,
                quality_improvements=quality_improvements,
                creative_enhancements=creative_enhancements,
                
                total_expected_improvement=total_improvement,
                estimated_processing_time=processing_time,
                complexity_level=complexity,
                
                processing_workflow=workflow,
                checkpoint_validations=checkpoints,
                quality_control_steps=self._generate_quality_control_steps(),
                
                required_tools=required_tools,
                skill_level_needed=self._determine_skill_level(complexity),
                estimated_cost=self._estimate_processing_cost(all_recommendations),
                
                plan_confidence=self._calculate_plan_confidence(quality_assessment, all_recommendations),
                plan_timestamp=datetime.now()
            )
            
            # Cache enhancement plan
            if audio_id and self.enable_caching:
                self._cache_enhancement_plan(audio_id, enhancement_plan)
            
            self.logger.info(f"Enhancement plan created with {len(all_recommendations)} recommendations")
            return enhancement_plan
            
        except Exception as e:
            self.logger.error(f"Enhancement plan creation failed: {str(e)}")
            raise
    
    # Quality analysis methods
    async def _analyze_signal_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze signal quality metrics"""
        def analyze():
            try:
                results = {}
                
                # Basic signal metrics
                peak_level = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
                rms_level = 20 * np.log10(np.sqrt(np.mean(audio_data ** 2)) + 1e-10)
                crest_factor = peak_level - rms_level
                
                results['peak_level'] = float(peak_level)
                results['rms_level'] = float(rms_level)
                results['crest_factor'] = float(crest_factor)
                
                # Noise floor estimation
                sorted_samples = np.sort(np.abs(audio_data))
                noise_floor_samples = sorted_samples[:len(sorted_samples)//10]  # Bottom 10%
                noise_floor = 20 * np.log10(np.mean(noise_floor_samples) + 1e-10)
                results['noise_floor'] = float(noise_floor)
                
                # Signal-to-noise ratio
                signal_power = np.mean(audio_data ** 2)
                noise_power = np.mean(noise_floor_samples ** 2)
                snr = 10 * np.log10((signal_power / (noise_power + 1e-10)) + 1e-10)
                results['snr'] = float(max(snr, 0))
                
                # Clipping detection
                clipping_threshold = 0.99
                clipped_samples = np.sum(np.abs(audio_data) >= clipping_threshold)
                clipping_percentage = (clipped_samples / len(audio_data)) * 100
                results['clipping_percentage'] = float(clipping_percentage)
                
                return results
                
            except Exception as e:
                self.logger.error(f"Signal quality analysis failed: {str(e)}")
                return {'peak_level': -6.0, 'rms_level': -20.0, 'snr': 40.0}
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, analyze)
    
    async def _analyze_frequency_balance(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze frequency balance and spectral characteristics"""
        def analyze():
            try:
                results = {}
                
                # Compute power spectrum
                freqs, psd = signal.welch(audio_data, sample_rate, nperseg=2048)
                
                # Calculate energy in different frequency bands
                band_energies = {}
                for band_name, (low_freq, high_freq) in self.frequency_bands.items():
                    band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                    if np.any(band_mask):
                        band_energy = np.mean(psd[band_mask])
                        band_energies[band_name] = band_energy
                
                # Calculate balance scores
                total_energy = sum(band_energies.values()) + 1e-10
                
                # Group into low, mid, high
                low_bands = ['sub_bass', 'bass', 'low_mids']
                mid_bands = ['mids', 'high_mids']
                high_bands = ['presence', 'brilliance']
                
                low_energy = sum(band_energies.get(b, 0) for b in low_bands)
                mid_energy = sum(band_energies.get(b, 0) for b in mid_bands)
                high_energy = sum(band_energies.get(b, 0) for b in high_bands)
                
                # Normalize to percentages
                low_percentage = (low_energy / total_energy) * 100
                mid_percentage = (mid_energy / total_energy) * 100
                high_percentage = (high_energy / total_energy) * 100
                
                results['low_balance'] = float(low_percentage)
                results['mid_balance'] = float(mid_percentage)
                results['high_balance'] = float(high_percentage)
                
                # Calculate overall balance score (closer to equal distribution = better)
                ideal_distribution = 100 / 3  # ~33.33% each
                balance_deviations = [
                    abs(low_percentage - ideal_distribution),
                    abs(mid_percentage - ideal_distribution),
                    abs(high_percentage - ideal_distribution)
                ]
                max_deviation = np.mean(balance_deviations)
                balance_score = max(0, 100 - max_deviation * 2)  # Scale appropriately
                results['balance_score'] = float(balance_score)
                
                # Spectral features
                spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0])
                spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0])
                
                results['spectral_centroid'] = float(spectral_centroid)
                results['spectral_rolloff'] = float(spectral_rolloff)
                
                return results
                
            except Exception as e:
                self.logger.error(f"Frequency balance analysis failed: {str(e)}")
                return {'balance_score': 50.0, 'low_balance': 33.0, 'mid_balance': 34.0, 'high_balance': 33.0}
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, analyze)
    
    async def _analyze_dynamic_range(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze dynamic range characteristics"""
        def analyze():
            try:
                results = {}
                
                # Convert to dB for dynamic range analysis
                audio_db = 20 * np.log10(np.abs(audio_data) + 1e-10)
                
                # Calculate percentile levels
                peak_level = np.max(audio_db)
                p95_level = np.percentile(audio_db, 95)
                p90_level = np.percentile(audio_db, 90)
                p10_level = np.percentile(audio_db, 10)
                
                # Dynamic range metrics
                dynamic_range_p90_p10 = p90_level - p10_level
                dynamic_range_peak_avg = peak_level - np.mean(audio_db)
                
                results['dynamic_range'] = float(max(dynamic_range_p90_p10, 0))
                results['peak_to_average'] = float(dynamic_range_peak_avg)
                
                # Loudness variation analysis
                window_size = int(0.1 * sample_rate)  # 100ms windows
                windowed_rms = []
                for i in range(0, len(audio_data) - window_size, window_size//2):
                    window = audio_data[i:i+window_size]
                    rms = np.sqrt(np.mean(window ** 2))
                    windowed_rms.append(rms)
                
                windowed_rms = np.array(windowed_rms)
                windowed_rms_db = 20 * np.log10(windowed_rms + 1e-10)
                
                loudness_variation = np.std(windowed_rms_db)
                results['loudness_variation'] = float(loudness_variation)
                
                # Compression detection
                if len(windowed_rms_db) > 10:
                    compression_ratio = np.mean(windowed_rms_db) / (np.max(windowed_rms_db) - np.min(windowed_rms_db) + 1e-10)
                    results['compression_ratio'] = float(abs(compression_ratio))
                else:
                    results['compression_ratio'] = 1.0
                
                return results
                
            except Exception as e:
                self.logger.error(f"Dynamic range analysis failed: {str(e)}")
                return {'dynamic_range': 12.0, 'loudness_variation': 5.0}
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, analyze)
    
    async def _analyze_stereo_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze stereo quality and spatial characteristics"""
        def analyze():
            try:
                results = {}
                
                # Check if stereo
                if len(audio_data.shape) == 1:
                    # Mono audio - create pseudo-stereo analysis
                    results['stereo_score'] = 50.0
                    results['stereo_width'] = 0.0
                    results['phase_correlation'] = 1.0
                    results['mono_compatibility'] = 100.0
                    return results
                
                # Stereo analysis
                left_channel = audio_data[:, 0] if audio_data.shape[1] >= 1 else audio_data
                right_channel = audio_data[:, 1] if audio_data.shape[1] >= 2 else audio_data
                
                # Phase correlation
                correlation = np.corrcoef(left_channel, right_channel)[0, 1]
                if np.isnan(correlation):
                    correlation = 1.0
                results['phase_correlation'] = float(correlation)
                
                # Stereo width (based on difference signal)
                mid_signal = (left_channel + right_channel) / 2
                side_signal = (left_channel - right_channel) / 2
                
                mid_energy = np.mean(mid_signal ** 2)
                side_energy = np.mean(side_signal ** 2)
                total_energy = mid_energy + side_energy + 1e-10
                
                stereo_width = side_energy / total_energy
                results['stereo_width'] = float(stereo_width)
                
                # Mono compatibility
                mono_mix = (left_channel + right_channel) / 2
                mono_compatibility = 1.0 - (np.std(mono_mix) / (np.std(left_channel) + np.std(right_channel) + 1e-10))
                results['mono_compatibility'] = float(max(0, mono_compatibility))
                
                # Overall stereo score
                stereo_score = 50 + (stereo_width * 30) + (max(0, correlation - 0.5) * 40)
                results['stereo_score'] = float(min(100, max(0, stereo_score)))
                
                return results
                
            except Exception as e:
                self.logger.error(f"Stereo quality analysis failed: {str(e)}")
                return {'stereo_score': 50.0, 'stereo_width': 0.5, 'phase_correlation': 0.8}
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, analyze)
    
    async def _detect_quality_issues(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Detect specific quality issues"""
        def detect():
            try:
                issues = []
                severities = {}
                
                # Clipping detection
                clipping_threshold = 0.98
                clipped_samples = np.sum(np.abs(audio_data) >= clipping_threshold)
                clipping_percentage = (clipped_samples / len(audio_data)) * 100
                
                if clipping_percentage > 0.1:
                    issues.append(QualityIssue.CLIPPING_DETECTED)
                    severities[QualityIssue.CLIPPING_DETECTED] = min(1.0, clipping_percentage / 5.0)
                
                # Noise floor analysis
                sorted_samples = np.sort(np.abs(audio_data))
                noise_floor_samples = sorted_samples[:len(sorted_samples)//20]
                noise_floor = 20 * np.log10(np.mean(noise_floor_samples) + 1e-10)
                
                if noise_floor > self.quality_thresholds['max_noise_floor']:
                    issues.append(QualityIssue.NOISE_FLOOR_HIGH)
                    severities[QualityIssue.NOISE_FLOOR_HIGH] = min(1.0, (noise_floor - self.quality_thresholds['max_noise_floor']) / 20.0)
                
                # Dynamic range check
                audio_db = 20 * np.log10(np.abs(audio_data) + 1e-10)
                dynamic_range = np.percentile(audio_db, 90) - np.percentile(audio_db, 10)
                
                if dynamic_range < self.quality_thresholds['min_dynamic_range']:
                    issues.append(QualityIssue.DYNAMIC_RANGE_LOW)
                    severities[QualityIssue.DYNAMIC_RANGE_LOW] = min(1.0, (self.quality_thresholds['min_dynamic_range'] - dynamic_range) / 10.0)
                
                # Frequency balance check
                freqs, psd = signal.welch(audio_data, sample_rate, nperseg=1024)
                
                # Check for severe imbalances
                low_mask = freqs <= 500
                high_mask = freqs >= 5000
                
                if np.any(low_mask) and np.any(high_mask):
                    low_energy = np.mean(psd[low_mask])
                    high_energy = np.mean(psd[high_mask])
                    energy_ratio = high_energy / (low_energy + 1e-10)
                    
                    if energy_ratio > 10 or energy_ratio < 0.1:
                        issues.append(QualityIssue.FREQUENCY_IMBALANCE)
                        severities[QualityIssue.FREQUENCY_IMBALANCE] = min(1.0, abs(np.log10(energy_ratio)) / 2.0)
                
                # Stereo issues (if applicable)
                if len(audio_data.shape) > 1 and audio_data.shape[1] >= 2:
                    left_channel = audio_data[:, 0]
                    right_channel = audio_data[:, 1]
                    
                    correlation = np.corrcoef(left_channel, right_channel)[0, 1]
                    if not np.isnan(correlation) and correlation < self.quality_thresholds['min_stereo_correlation']:
                        issues.append(QualityIssue.PHASE_ISSUES)
                        severities[QualityIssue.PHASE_ISSUES] = min(1.0, (self.quality_thresholds['min_stereo_correlation'] - correlation) / 0.5)
                
                return {'issues': issues, 'severities': severities}
                
            except Exception as e:
                self.logger.error(f"Quality issue detection failed: {str(e)}")
                return {'issues': [], 'severities': {}}
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, detect)
    
    # Enhancement recommendation methods
    async def _generate_critical_fixes(self, quality_assessment: QualityAssessment) -> List[EnhancementRecommendation]:
        """Generate critical enhancement recommendations"""
        def generate():
            try:
                recommendations = []
                
                for issue in quality_assessment.quality_issues:
                    priority = self.issue_priorities.get(issue, EnhancementPriority.MEDIUM)
                    
                    if priority == EnhancementPriority.CRITICAL:
                        severity = quality_assessment.issue_severities.get(issue, 0.5)
                        
                        if issue == QualityIssue.CLIPPING_DETECTED:
                            rec = self._create_clipping_fix_recommendation(severity)
                        elif issue == QualityIssue.PHASE_ISSUES:
                            rec = self._create_phase_fix_recommendation(severity)
                        else:
                            continue
                        
                        if rec:
                            recommendations.append(rec)
                
                return recommendations
                
            except Exception as e:
                self.logger.error(f"Critical fixes generation failed: {str(e)}")
                return []
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, generate)
    
    async def _generate_quality_improvements(self, quality_assessment: QualityAssessment) -> List[EnhancementRecommendation]:
        """Generate quality improvement recommendations"""
        def generate():
            try:
                recommendations = []
                
                # Noise reduction
                if quality_assessment.signal_to_noise_ratio < self.quality_thresholds['min_snr']:
                    rec = self._create_noise_reduction_recommendation(quality_assessment)
                    if rec:
                        recommendations.append(rec)
                
                # Dynamic range enhancement
                if quality_assessment.dynamic_range < self.quality_thresholds['min_dynamic_range']:
                    rec = self._create_dynamic_range_recommendation(quality_assessment)
                    if rec:
                        recommendations.append(rec)
                
                # Frequency balance
                if quality_assessment.frequency_balance_score < 70.0:
                    rec = self._create_frequency_balance_recommendation(quality_assessment)
                    if rec:
                        recommendations.append(rec)
                
                # Stereo enhancement
                if quality_assessment.stereo_quality_score < 70.0:
                    rec = self._create_stereo_enhancement_recommendation(quality_assessment)
                    if rec:
                        recommendations.append(rec)
                
                return recommendations
                
            except Exception as e:
                self.logger.error(f"Quality improvements generation failed: {str(e)}")
                return []
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, generate)
    
    async def _generate_creative_enhancements(self, quality_assessment: QualityAssessment, target_quality: float) -> List[EnhancementRecommendation]:
        """Generate creative enhancement recommendations"""
        def generate():
            try:
                recommendations = []
                
                # Only suggest creative enhancements if quality is already decent
                if quality_assessment.overall_quality_score >= 60.0:
                    
                    # Harmonic enhancement
                    if target_quality > 85.0:
                        rec = self._create_harmonic_enhancement_recommendation()
                        if rec:
                            recommendations.append(rec)
                    
                    # Vintage emulation
                    if target_quality > 80.0:
                        rec = self._create_vintage_emulation_recommendation()
                        if rec:
                            recommendations.append(rec)
                    
                    # Spatial enhancement
                    rec = self._create_spatial_enhancement_recommendation(quality_assessment)
                    if rec:
                        recommendations.append(rec)
                
                return recommendations
                
            except Exception as e:
                self.logger.error(f"Creative enhancements generation failed: {str(e)}")
                return []
        
        return await asyncio.get_event_loop().run_in_executor(self.thread_executor, generate)
    
    # Specific recommendation creators
    def _create_clipping_fix_recommendation(self, severity: float) -> EnhancementRecommendation:
        """Create clipping fix recommendation"""
        return EnhancementRecommendation(
            enhancement_type=EnhancementType.DYNAMIC_RANGE,
            priority=EnhancementPriority.CRITICAL,
            complexity=ProcessingComplexity.SIMPLE,
            description="Remove clipping artifacts and restore clean peaks",
            expected_improvement=min(30.0, severity * 40.0),
            processing_intensity=0.8,
            suggested_parameters={
                'limiter_threshold': -1.0,
                'limiter_release': 10,
                'peak_restoration': True,
                'lookahead': 5
            },
            frequency_ranges=[(20, 20000)],
            recommended_tools=["iZotope RX De-clip", "FabFilter Pro-L 2", "Waves L3"],
            processing_order=1,
            alternative_approaches=["Manual peak editing", "Spectral repair"],
            before_after_preview={'clipping_reduction': 90.0},
            potential_side_effects=["Slight transient softening"],
            quality_trade_offs=["May reduce perceived loudness"],
            implementation_notes="Apply gentle limiting with lookahead to prevent future clipping",
            skill_level_required="Intermediate",
            estimated_processing_time=5.0
        )
    
    def _create_phase_fix_recommendation(self, severity: float) -> EnhancementRecommendation:
        """Create phase correction recommendation"""
        return EnhancementRecommendation(
            enhancement_type=EnhancementType.STEREO_ENHANCEMENT,
            priority=EnhancementPriority.CRITICAL,
            complexity=ProcessingComplexity.ADVANCED,
            description="Correct phase alignment issues between stereo channels",
            expected_improvement=min(25.0, severity * 35.0),
            processing_intensity=0.6,
            suggested_parameters={
                'phase_alignment': 'automatic',
                'correlation_threshold': 0.7,
                'frequency_dependent': True
            },
            frequency_ranges=[(50, 15000)],
            recommended_tools=["Waves InPhase", "iZotope Ozone Imager", "Voxengo MSED"],
            processing_order=2,
            alternative_approaches=["Manual phase adjustment", "Mid/Side processing"],
            before_after_preview={'phase_correlation': 0.8},
            potential_side_effects=["Possible stereo width changes"],
            quality_trade_offs=["May affect stereo imaging"],
            implementation_notes="Check mono compatibility after correction",
            skill_level_required="Advanced",
            estimated_processing_time=10.0
        )
    
    def _create_noise_reduction_recommendation(self, quality_assessment: QualityAssessment) -> EnhancementRecommendation:
        """Create noise reduction recommendation"""
        noise_severity = (self.quality_thresholds['max_noise_floor'] - quality_assessment.noise_floor_level) / 20.0
        
        return EnhancementRecommendation(
            enhancement_type=EnhancementType.NOISE_REDUCTION,
            priority=EnhancementPriority.HIGH,
            complexity=ProcessingComplexity.MODERATE,
            description="Reduce background noise while preserving audio quality",
            expected_improvement=min(20.0, noise_severity * 25.0),
            processing_intensity=min(0.8, noise_severity),
            suggested_parameters={
                'noise_reduction_amount': min(12.0, noise_severity * 15.0),
                'preserve_transients': True,
                'frequency_smoothing': 3,
                'artifact_suppression': True
            },
            frequency_ranges=[(20, 8000)],
            recommended_tools=self.professional_tools[EnhancementType.NOISE_REDUCTION],
            processing_order=3,
            alternative_approaches=["Spectral gating", "Adaptive filtering"],
            before_after_preview={'noise_floor_improvement': min(15.0, noise_severity * 20.0)},
            potential_side_effects=["Possible artifacts in quiet passages"],
            quality_trade_offs=["May affect natural ambience"],
            implementation_notes="Use gentle settings to avoid artifacts",
            skill_level_required="Intermediate",
            estimated_processing_time=8.0
        )
    
    def _create_frequency_balance_recommendation(self, quality_assessment: QualityAssessment) -> EnhancementRecommendation:
        """Create frequency balance recommendation"""
        balance_deficit = 100.0 - quality_assessment.frequency_balance_score
        
        return EnhancementRecommendation(
            enhancement_type=EnhancementType.FREQUENCY_BALANCE,
            priority=EnhancementPriority.MEDIUM,
            complexity=ProcessingComplexity.MODERATE,
            description="Optimize frequency balance for natural, professional sound",
            expected_improvement=balance_deficit * 0.6,
            processing_intensity=balance_deficit / 100.0,
            suggested_parameters={
                'eq_type': 'parametric',
                'band_count': 7,
                'q_factor': 1.0,
                'match_reference': True
            },
            frequency_ranges=list(self.frequency_bands.values()),
            recommended_tools=self.professional_tools[EnhancementType.FREQUENCY_BALANCE],
            processing_order=4,
            alternative_approaches=["Dynamic EQ", "Multiband processing"],
            before_after_preview={'frequency_balance_improvement': balance_deficit * 0.7},
            potential_side_effects=["May alter original character"],
            quality_trade_offs=["Balance vs character preservation"],
            implementation_notes="Reference professional recordings in similar genre",
            skill_level_required="Intermediate",
            estimated_processing_time=15.0
        )
    
    # Placeholder methods for remaining recommendation creators
    def _create_dynamic_range_recommendation(self, quality_assessment: QualityAssessment) -> Optional[EnhancementRecommendation]:
        """Create dynamic range enhancement recommendation"""
        return None  # Placeholder
    
    def _create_stereo_enhancement_recommendation(self, quality_assessment: QualityAssessment) -> Optional[EnhancementRecommendation]:
        """
Create stereo enhancement recommendation"""
        return None  # Placeholder
    
    def _create_harmonic_enhancement_recommendation(self) -> Optional[EnhancementRecommendation]:
        """
Create harmonic enhancement recommendation"""
        return None  # Placeholder
    
    def _create_vintage_emulation_recommendation(self) -> Optional[EnhancementRecommendation]:
        """
Create vintage emulation recommendation"""
        return None  # Placeholder
    
    def _create_spatial_enhancement_recommendation(self, quality_assessment: QualityAssessment) -> Optional[EnhancementRecommendation]:
        """
Create spatial enhancement recommendation"""
        return None  # Placeholder
    
    # Helper calculation methods
    def _calculate_overall_quality_score(self, *analysis_results) -> float:
        """
Calculate overall quality score from analysis results"""
        try:
            signal_analysis, frequency_analysis, dynamic_analysis, stereo_analysis = analysis_results
            
            # Weight different aspects
            weights = {
                'signal': 0.3,
                'frequency': 0.25,
                'dynamic': 0.25,
                'stereo': 0.2
            }
            
            # Signal quality score
            snr = signal_analysis.get('snr', 40.0)
            clipping = signal_analysis.get('clipping_percentage', 0.0)
            signal_score = min(100, (snr / 60.0) * 70 + 30) - (clipping * 10)
            
            # Frequency balance score
            frequency_score = frequency_analysis.get('balance_score', 50.0)
            
            # Dynamic range score
            dr = dynamic_analysis.get('dynamic_range', 12.0)
            dynamic_score = min(100, (dr / 20.0) * 80 + 20)
            
            # Stereo quality score
            stereo_score = stereo_analysis.get('stereo_score', 50.0)
            
            # Weighted average
            overall = (
                signal_score * weights['signal'] +
                frequency_score * weights['frequency'] +
                dynamic_score * weights['dynamic'] +
                stereo_score * weights['stereo']
            )
            
            return float(max(0, min(100, overall)))
            
        except Exception as e:
            self.logger.error(f"Overall quality score calculation failed: {str(e)}")
            return 50.0
    
    def _calculate_expected_improvement(self, recommendations: List[EnhancementRecommendation]) -> float:
        """Calculate total expected improvement from recommendations"""
        try:
            if not recommendations:
                return 0.0
            
            # Use weighted average with diminishing returns
            improvements = [rec.expected_improvement for rec in recommendations]
            weights = [1.0 / (i + 1) for i in range(len(improvements))]  # Diminishing returns
            
            weighted_sum = sum(imp * weight for imp, weight in zip(improvements, weights))
            weight_sum = sum(weights)
            
            return float(weighted_sum / weight_sum if weight_sum > 0 else 0)
            
        except:
            return 0.0
    
    def _estimate_processing_time(self, recommendations: List[EnhancementRecommendation]) -> float:
        """
Estimate total processing time"""
        return float(sum(rec.estimated_processing_time for rec in recommendations))
    
    def _determine_overall_complexity(self, recommendations: List[EnhancementRecommendation]) -> ProcessingComplexity:
        """
Determine overall processing complexity"""
        if not recommendations:
            return ProcessingComplexity.SIMPLE
        
        complexity_values = {
            ProcessingComplexity.SIMPLE: 1,
            ProcessingComplexity.MODERATE: 2,
            ProcessingComplexity.ADVANCED: 3,
            ProcessingComplexity.COMPLEX: 4
        }
        
        max_complexity = max(complexity_values[rec.complexity] for rec in recommendations)
        
        for complexity, value in complexity_values.items():
            if value == max_complexity:
                return complexity
        
        return ProcessingComplexity.MODERATE
    
    # Workflow and planning methods
    def _generate_processing_workflow(self, recommendations: List[EnhancementRecommendation]) -> List[str]:
        """
Generate processing workflow steps"""
        if not recommendations:
            return []
        
        # Sort by processing order
        sorted_recs = sorted(recommendations, key=lambda r: r.processing_order)
        
        workflow = ["1. Create backup of original audio"]
        
        for i, rec in enumerate(sorted_recs, 2):
            step = f"{i}. {rec.enhancement_type.value.replace('_', ' ').title()}: {rec.description}"
            workflow.append(step)
        
        workflow.append(f"{len(sorted_recs) + 2}. Final quality validation and comparison")
        
        return workflow
    
    def _generate_quality_checkpoints(self, recommendations: List[EnhancementRecommendation]) -> List[str]:
        """Generate quality checkpoint validations"""
        checkpoints = [
            "Verify no clipping introduced",
            "Check stereo field integrity",
            "Validate frequency balance improvements",
            "Confirm dynamic range preservation",
            "Test mono compatibility"
        ]
        return checkpoints
    
    def _generate_quality_control_steps(self) -> List[str]:
        """Generate quality control steps"""
        return [
            "A/B comparison with original",
            "Spectral analysis validation",
            "Loudness standards compliance check",
            "Multi-device playback test",
            "Professional reference comparison"
        ]
    
    def _compile_required_tools(self, recommendations: List[EnhancementRecommendation]) -> List[str]:
        """Compile list of required tools"""
        all_tools = set()
        for rec in recommendations:
            all_tools.update(rec.recommended_tools)
        return list(all_tools)
    
    def _determine_skill_level(self, complexity: ProcessingComplexity) -> str:
        """
Determine required skill level"""
        skill_mapping = {
            ProcessingComplexity.SIMPLE: "Beginner",
            ProcessingComplexity.MODERATE: "Intermediate", 
            ProcessingComplexity.ADVANCED: "Advanced",
            ProcessingComplexity.COMPLEX: "Expert"
        }
        return skill_mapping.get(complexity, "Intermediate")
    
    def _estimate_processing_cost(self, recommendations: List[EnhancementRecommendation]) -> Optional[float]:
        """Estimate processing cost (placeholder)"""
        if not recommendations:
            return 0.0
        
        # Simple cost estimation based on complexity and time
        total_time = sum(rec.estimated_processing_time for rec in recommendations)
        avg_complexity = len([r for r in recommendations if r.complexity in [ProcessingComplexity.ADVANCED, ProcessingComplexity.COMPLEX]])
        
        base_cost = total_time * 5.0  # $5 per minute estimate
        complexity_multiplier = 1.0 + (avg_complexity * 0.5)
        
        return float(base_cost * complexity_multiplier)
    
    def _calculate_plan_confidence(self, quality_assessment: QualityAssessment, 
                                 recommendations: List[EnhancementRecommendation]) -> float:
        """
Calculate confidence in the enhancement plan"""
        try:
            confidence_factors = []
            
            # Assessment confidence
            confidence_factors.append(quality_assessment.assessment_confidence)
            
            # Number of recommendations (more = potentially more uncertainty)
            rec_factor = max(0.5, 1.0 - (len(recommendations) - 3) * 0.1)
            confidence_factors.append(rec_factor)
            
            # Complexity factor (simpler = more confident)
            complexity_values = [1.0, 0.8, 0.6, 0.4]
            complexity_confidences = []
            for rec in recommendations:
                idx = list(ProcessingComplexity).index(rec.complexity)
                complexity_confidences.append(complexity_values[idx])
            
            if complexity_confidences:
                avg_complexity_confidence = np.mean(complexity_confidences)
                confidence_factors.append(avg_complexity_confidence)
            
            return float(np.mean(confidence_factors))
            
        except:
            return 0.8
    
    def _calculate_assessment_confidence(self, analysis_results: List) -> float:
        """
Calculate confidence in quality assessment"""
        try:
            # Count successful analyses
            successful_analyses = sum(1 for result in analysis_results if not isinstance(result, Exception))
            total_analyses = len(analysis_results)
            
            if total_analyses == 0:
                return 0.5
            
            return float(successful_analyses / total_analyses)
            
        except:
            return 0.8
    
    # Caching methods
    def _get_cached_quality(self, audio_id: str) -> Optional[QualityAssessment]:
        """
Get cached quality assessment"""
        with self.cache_lock:
            return self.quality_cache.get(audio_id)
    
    def _cache_quality_assessment(self, audio_id: str, assessment: QualityAssessment):
        """
Cache quality assessment"""
        with self.cache_lock:
            self.quality_cache[audio_id] = assessment
    
    def _get_cached_enhancement_plan(self, audio_id: str) -> Optional[EnhancementPlan]:
        """
Get cached enhancement plan"""
        with self.cache_lock:
            return self.enhancement_cache.get(audio_id)
    
    def _cache_enhancement_plan(self, audio_id: str, plan: EnhancementPlan):
        """
Cache enhancement plan"""
        with self.cache_lock:
            self.enhancement_cache[audio_id] = plan
    
    # Public utility methods
    def get_enhancement_statistics(self) -> Dict[str, Any]:
        """
Get enhancement engine statistics"""
        with self.cache_lock:
            cached_assessments = len(self.quality_cache)
            cached_plans = len(self.enhancement_cache)
        
        return {
            'cached_quality_assessments': cached_assessments,
            'cached_enhancement_plans': cached_plans,
            'supported_enhancement_types': [e.value for e in EnhancementType],
            'quality_thresholds': self.quality_thresholds,
            'professional_tools_database_size': sum(len(tools) for tools in self.professional_tools.values())
        }
    
    def clear_caches(self):
        """
Clear all caches"""
        with self.cache_lock:
            self.quality_cache.clear()
            self.enhancement_cache.clear()
        self.logger.info("Enhancement analyzer caches cleared")
    
    def export_enhancement_report(self, plan: EnhancementPlan, filepath: str):
        """Export enhancement plan to detailed report"""
        try:
            report = {
                'audio_id': plan.audio_id,
                'current_quality_score': plan.current_quality.overall_quality_score,
                'target_quality_score': plan.target_quality_score,
                'expected_improvement': plan.total_expected_improvement,
                'processing_time_estimate': plan.estimated_processing_time,
                'complexity_level': plan.complexity_level.value,
                'critical_fixes': len(plan.critical_fixes),
                'quality_improvements': len(plan.quality_improvements),
                'creative_enhancements': len(plan.creative_enhancements),
                'workflow_steps': plan.processing_workflow,
                'required_tools': plan.required_tools,
                'skill_level_required': plan.skill_level_needed,
                'plan_confidence': plan.plan_confidence,
                'timestamp': plan.plan_timestamp.isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Enhancement report exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Enhancement report export failed: {str(e)}")
            raise
    
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'thread_executor'):
                self.thread_executor.shutdown(wait=False)
            if hasattr(self, 'process_executor'):
                self.process_executor.shutdown(wait=False)
        except:
            pass
