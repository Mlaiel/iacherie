"""🥁 Professional Tempo Detection & BPM Analysis Engine

Advanced tempo detection with multiple algorithms, time signature detection,
and comprehensive rhythmic analysis for professional audio applications.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import librosa
import scipy.signal
from scipy import ndimage


class TempoConfidence(Enum):
    """Tempo detection confidence levels"""
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
    UNKNOWN = "unknown"


class TimeSignature(Enum):
    """Common time signatures"""
    FOUR_FOUR = "4/4"
    THREE_FOUR = "3/4"
    TWO_FOUR = "2/4"
    SIX_EIGHT = "6/8"
    NINE_EIGHT = "9/8"
    TWELVE_EIGHT = "12/8"
    FIVE_FOUR = "5/4"
    SEVEN_EIGHT = "7/8"


@dataclass
class BPMAnalysisResult:
    """Comprehensive BPM analysis results"""
    tempo_bpm: float
    tempo_confidence: TempoConfidence
    tempo_stability: float
    beat_times: List[float]
    beat_strengths: List[float]
    time_signature: TimeSignature
    time_signature_confidence: float
    alternative_tempos: List[Tuple[float, float]]  # (tempo, confidence)
    downbeat_positions: List[float]
    rhythmic_complexity: float
    tempo_variations: List[Tuple[float, float]]  # (time, tempo)
    onset_density: float
    metrical_hierarchy: Dict[str, float]
    groove_consistency: float


class ProfessionalTempoDetector:
    """🎵 Professional-Grade Tempo Detection Engine
    
    Advanced BPM detection with multiple algorithms, time signature analysis,
    and comprehensive rhythmic characterization for professional audio applications.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 hop_length: int = 512,
                 frame_length: int = 2048,
                 tempo_min: float = 60.0,
                 tempo_max: float = 200.0):
        """Initialize professional tempo detector.
        
        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
            frame_length: Frame length for analysis  
            tempo_min: Minimum tempo for detection
            tempo_max: Maximum tempo for detection
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.frame_length = frame_length
        self.tempo_min = tempo_min
        self.tempo_max = tempo_max
        
        # Time signature patterns (beats per measure, beat unit)
        self.time_signatures = {
            TimeSignature.FOUR_FOUR: (4, 4),
            TimeSignature.THREE_FOUR: (3, 4),
            TimeSignature.TWO_FOUR: (2, 4),
            TimeSignature.SIX_EIGHT: (6, 8),
            TimeSignature.NINE_EIGHT: (9, 8),
            TimeSignature.TWELVE_EIGHT: (12, 8),
            TimeSignature.FIVE_FOUR: (5, 4),
            TimeSignature.SEVEN_EIGHT: (7, 8)
        }
        
        self.logger.info("Professional Tempo Detector initialized")
    
    async def analyze_bpm_comprehensive(self, audio_data: np.ndarray) -> BPMAnalysisResult:
        """Perform comprehensive BPM and rhythmic analysis.
        
        Args:
            audio_data: Input audio signal
            
        Returns:
            Complete BPM analysis results
        """
        try:
            self.logger.info("Starting comprehensive BPM analysis...")
            
            # Multi-algorithm tempo detection
            tempo_estimates = await self._multi_algorithm_tempo_detection(audio_data)
            
            # Select primary tempo estimate
            primary_tempo = self._select_primary_tempo(tempo_estimates)
            
            # Beat tracking with primary tempo
            beat_times, beat_strengths = await self._precise_beat_tracking(audio_data, primary_tempo)
            
            # Time signature detection
            time_sig, time_sig_confidence = await self._detect_time_signature(beat_times, primary_tempo)
            
            # Downbeat detection
            downbeat_positions = await self._detect_downbeats(beat_times, time_sig)
            
            # Advanced metrics
            tempo_stability = self._calculate_tempo_stability(beat_times)
            rhythmic_complexity = self._calculate_rhythmic_complexity(audio_data)
            tempo_variations = await self._analyze_tempo_variations(audio_data)
            onset_density = self._calculate_onset_density(audio_data)
            metrical_hierarchy = self._analyze_metrical_hierarchy(beat_times, time_sig)
            groove_consistency = self._analyze_groove_consistency(beat_times)
            
            # Determine confidence level
            confidence = self._determine_confidence_level(
                primary_tempo, tempo_stability, len(beat_times), onset_density
            )
            
            result = BPMAnalysisResult(
                tempo_bpm=primary_tempo,
                tempo_confidence=confidence,
                tempo_stability=tempo_stability,
                beat_times=beat_times.tolist() if isinstance(beat_times, np.ndarray) else beat_times,
                beat_strengths=beat_strengths.tolist() if isinstance(beat_strengths, np.ndarray) else beat_strengths,
                time_signature=time_sig,
                time_signature_confidence=time_sig_confidence,
                alternative_tempos=[(t, c) for t, c in tempo_estimates[1:4]],  # Top 3 alternatives
                downbeat_positions=downbeat_positions,
                rhythmic_complexity=rhythmic_complexity,
                tempo_variations=tempo_variations,
                onset_density=onset_density,
                metrical_hierarchy=metrical_hierarchy,
                groove_consistency=groove_consistency
            )
            
            self.logger.info(f"BPM analysis complete: {primary_tempo:.1f} BPM, {time_sig.value}, confidence: {confidence.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"BPM analysis failed: {e}")
            # Return safe default values
            return BPMAnalysisResult(
                tempo_bpm=120.0,
                tempo_confidence=TempoConfidence.UNKNOWN,
                tempo_stability=0.0,
                beat_times=[],
                beat_strengths=[],
                time_signature=TimeSignature.FOUR_FOUR,
                time_signature_confidence=0.0,
                alternative_tempos=[],
                downbeat_positions=[],
                rhythmic_complexity=0.0,
                tempo_variations=[],
                onset_density=0.0,
                metrical_hierarchy={},
                groove_consistency=0.0
            )
    
    async def detect_tempo(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Legacy interface for tempo detection (maintains compatibility)."""
        try:
            result = await self.analyze_bpm_comprehensive(audio_data)
            
            # Convert to legacy format
            return {
                'tempo_bpm': result.tempo_bpm,
                'tempo_confidence': 1.0 if result.tempo_confidence == TempoConfidence.HIGH else 
                                   0.7 if result.tempo_confidence == TempoConfidence.MEDIUM else
                                   0.3 if result.tempo_confidence == TempoConfidence.LOW else 0.0,
                'tempo_stability': result.tempo_stability,
                'beat_count': len(result.beat_times),
                'rhythm_regularity': result.groove_consistency,
                'time_signature': result.time_signature.value,
                'rhythmic_complexity': result.rhythmic_complexity
            }
            
        except Exception as e:
            self.logger.error(f"Legacy tempo detection failed: {e}")
            return {
                'tempo_bpm': 120.0, 
                'tempo_confidence': 0.0, 
                'tempo_stability': 0.0,
                'beat_count': 0,
                'rhythm_regularity': 0.0,
                'time_signature': '4/4',
                'rhythmic_complexity': 0.0
            }
    
    async def _multi_algorithm_tempo_detection(self, audio_data: np.ndarray) -> List[Tuple[float, float]]:
        """Use multiple algorithms for robust tempo detection."""
        tempo_estimates = []
        
        # Algorithm 1: librosa beat tracking
        try:
            tempo_lr, _ = librosa.beat.beat_track(
                y=audio_data, sr=self.sample_rate,
                start_bpm=120, tightness=100
            )
            tempo_estimates.append((float(tempo_lr), 0.8))
        except:
            pass
            
        # Algorithm 2: autocorrelation-based
        try:
            tempo_auto = await self._autocorrelation_tempo(audio_data)
            tempo_estimates.append((tempo_auto, 0.7))
        except:
            pass
            
        # Algorithm 3: onset-based with FFT
        try:
            tempo_onset = await self._onset_based_tempo(audio_data)
            tempo_estimates.append((tempo_onset, 0.6))
        except:
            pass
            
        # Sort by confidence
        tempo_estimates.sort(key=lambda x: x[1], reverse=True)
        
        # If no estimates, provide default
        if not tempo_estimates:
            tempo_estimates.append((120.0, 0.1))
            
        return tempo_estimates
    
    async def _autocorrelation_tempo(self, audio_data: np.ndarray) -> float:
        """Autocorrelation-based tempo detection."""
        # Calculate onset strength
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
        
        # Autocorrelation
        autocorr = np.correlate(onset_env, onset_env, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find peaks corresponding to tempo range
        min_period = int(60 * self.sample_rate / self.hop_length / self.tempo_max)
        max_period = int(60 * self.sample_rate / self.hop_length / self.tempo_min)
        
        if max_period < len(autocorr):
            peaks, _ = scipy.signal.find_peaks(autocorr[min_period:max_period])
            if len(peaks) > 0:
                period = peaks[np.argmax(autocorr[min_period:max_period][peaks])] + min_period
                tempo = 60 * self.sample_rate / self.hop_length / period
                return float(tempo)
        
        return 120.0
    
    async def _onset_based_tempo(self, audio_data: np.ndarray) -> float:
        """Onset-based tempo detection with spectral flux."""
        # Spectral flux for onset detection
        stft = librosa.stft(audio_data, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        
        # Calculate spectral flux
        flux = np.sum(np.diff(magnitude, axis=1), axis=0)
        flux = np.maximum(0, flux)  # Half-wave rectification
        
        # Smooth flux
        flux = ndimage.median_filter(flux, size=3)
        
        # Find tempo from flux periodicity
        autocorr = np.correlate(flux, flux, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Convert to tempo
        min_lag = int(60 * self.sample_rate / self.hop_length / self.tempo_max)
        max_lag = int(60 * self.sample_rate / self.hop_length / self.tempo_min)
        
        if max_lag < len(autocorr):
            peaks, _ = scipy.signal.find_peaks(autocorr[min_lag:max_lag])
            if len(peaks) > 0:
                lag = peaks[np.argmax(autocorr[min_lag:max_lag][peaks])] + min_lag
                tempo = 60 * self.sample_rate / self.hop_length / lag
                return float(tempo)
        
        return 120.0
    
    def _select_primary_tempo(self, tempo_estimates: List[Tuple[float, float]]) -> float:
        """Select the most likely tempo from multiple estimates."""
        if not tempo_estimates:
            return 120.0
            
        # Weight estimates by confidence and proximity to common tempos
        weighted_scores = []
        
        for tempo, confidence in tempo_estimates:
            # Boost confidence for common tempo ranges
            if 60 <= tempo <= 80 or 120 <= tempo <= 140:
                confidence *= 1.2
            elif 90 <= tempo <= 110 or 150 <= tempo <= 180:
                confidence *= 1.1
                
            weighted_scores.append((tempo, confidence))
        
        # Return highest weighted tempo
        best_tempo = max(weighted_scores, key=lambda x: x[1])[0]
        return float(best_tempo)
    
    async def _precise_beat_tracking(self, audio_data: np.ndarray, tempo: float) -> Tuple[np.ndarray, np.ndarray]:
        """Precise beat tracking given estimated tempo."""
        try:
            # Use dynamic programming beat tracker
            _, beat_frames = librosa.beat.beat_track(
                y=audio_data, sr=self.sample_rate,
                start_bpm=tempo, tightness=100
            )
            
            # Convert frames to time
            beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate, hop_length=self.hop_length)
            
            # Calculate beat strengths
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
            beat_strengths = onset_env[beat_frames] if len(beat_frames) > 0 else np.array([])
            
            return beat_times, beat_strengths
            
        except Exception as e:
            self.logger.warning(f"Beat tracking failed: {e}")
            return np.array([]), np.array([])
    
    async def _detect_time_signature(self, beat_times: np.ndarray, tempo: float) -> Tuple[TimeSignature, float]:
        """Detect time signature from beat pattern."""
        if len(beat_times) < 8:
            return TimeSignature.FOUR_FOUR, 0.0
        
        # Analyze beat interval patterns
        intervals = np.diff(beat_times)
        
        # Test different time signatures
        best_signature = TimeSignature.FOUR_FOUR
        best_confidence = 0.0
        
        for signature, (beats_per_measure, beat_unit) in self.time_signatures.items():
            confidence = self._test_time_signature(intervals, beats_per_measure, tempo)
            if confidence > best_confidence:
                best_confidence = confidence
                best_signature = signature
        
        return best_signature, best_confidence
    
    def _test_time_signature(self, intervals: np.ndarray, beats_per_measure: int, tempo: float) -> float:
        """Test how well intervals fit a given time signature."""
        if len(intervals) < beats_per_measure:
            return 0.0
        
        # Expected interval for this time signature
        expected_interval = 60.0 / tempo
        
        # Group intervals by measure
        measure_groups = []
        for i in range(0, len(intervals) - beats_per_measure + 1, beats_per_measure):
            group = intervals[i:i+beats_per_measure]
            measure_groups.append(group)
        
        if not measure_groups:
            return 0.0
        
        # Calculate consistency across measures
        consistency_scores = []
        for group in measure_groups:
            # How consistent are intervals within this measure?
            deviation = np.std(group) / (np.mean(group) + 1e-10)
            consistency = max(0, 1.0 - deviation)
            consistency_scores.append(consistency)
        
        return np.mean(consistency_scores)
    
    async def _detect_downbeats(self, beat_times: np.ndarray, time_signature: TimeSignature) -> List[float]:
        """Detect downbeat positions based on time signature."""
        if len(beat_times) == 0:
            return []
        
        beats_per_measure, _ = self.time_signatures[time_signature]
        
        # Simple downbeat detection - every N beats
        downbeats = []
        for i in range(0, len(beat_times), beats_per_measure):
            if i < len(beat_times):
                downbeats.append(float(beat_times[i]))
        
        return downbeats
    
    def _calculate_tempo_stability(self, beat_times: np.ndarray) -> float:
        """Calculate tempo stability from beat times."""
        if len(beat_times) < 2:
            return 0.0
        
        intervals = np.diff(beat_times)
        if len(intervals) == 0:
            return 0.0
        
        # Coefficient of variation (lower is more stable)
        cv = np.std(intervals) / (np.mean(intervals) + 1e-10)
        stability = max(0.0, 1.0 - cv)
        
        return float(stability)
    
    def _calculate_rhythmic_complexity(self, audio_data: np.ndarray) -> float:
        """Calculate rhythmic complexity score."""
        try:
            # Calculate onset strength
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
            
            # Onset detection
            onsets = librosa.onset.onset_detect(
                onset_envelope=onset_env, sr=self.sample_rate, units='time'
            )
            
            if len(onsets) < 2:
                return 0.0
            
            # Calculate inter-onset intervals
            intervals = np.diff(onsets)
            
            # Complexity based on interval variability
            if len(intervals) > 0:
                complexity = np.std(intervals) / (np.mean(intervals) + 1e-10)
                return float(min(1.0, complexity))
            
            return 0.0
            
        except:
            return 0.0
    
    async def _analyze_tempo_variations(self, audio_data: np.ndarray) -> List[Tuple[float, float]]:
        """Analyze tempo variations over time."""
        try:
            # Sliding window tempo analysis
            window_length = int(10 * self.sample_rate)  # 10 second windows
            hop_length = int(5 * self.sample_rate)      # 5 second hop
            
            tempo_variations = []
            
            for start in range(0, len(audio_data) - window_length, hop_length):
                window = audio_data[start:start + window_length]
                time_pos = start / self.sample_rate
                
                # Quick tempo estimate for this window
                try:
                    tempo, _ = librosa.beat.beat_track(y=window, sr=self.sample_rate)
                    tempo_variations.append((float(time_pos), float(tempo)))
                except:
                    pass
            
            return tempo_variations
            
        except:
            return []
    
    def _calculate_onset_density(self, audio_data: np.ndarray) -> float:
        """Calculate onset density (onsets per second)."""
        try:
            onsets = librosa.onset.onset_detect(y=audio_data, sr=self.sample_rate, units='time')
            duration = len(audio_data) / self.sample_rate
            density = len(onsets) / duration if duration > 0 else 0.0
            return float(density)
        except:
            return 0.0
    
    def _analyze_metrical_hierarchy(self, beat_times: np.ndarray, time_signature: TimeSignature) -> Dict[str, float]:
        """Analyze metrical hierarchy (beat, measure, phrase levels)."""
        hierarchy = {
            'beat_level': 1.0,
            'measure_level': 0.0,
            'phrase_level': 0.0
        }
        
        if len(beat_times) == 0:
            return hierarchy
        
        beats_per_measure, _ = self.time_signatures[time_signature]
        
        # Measure level strength
        if len(beat_times) >= beats_per_measure:
            hierarchy['measure_level'] = 0.8
        
        # Phrase level (typically 4 or 8 measures)
        if len(beat_times) >= beats_per_measure * 4:
            hierarchy['phrase_level'] = 0.6
        
        return hierarchy
    
    def _analyze_groove_consistency(self, beat_times: np.ndarray) -> float:
        """Analyze groove consistency and feel."""
        if len(beat_times) < 4:
            return 0.0
        
        # Micro-timing analysis - looking for consistent deviations
        intervals = np.diff(beat_times)
        
        if len(intervals) < 2:
            return 0.0
        
        # Calculate swing ratio if applicable
        even_intervals = intervals[::2]  # On-beats
        odd_intervals = intervals[1::2]  # Off-beats
        
        if len(even_intervals) > 0 and len(odd_intervals) > 0:
            swing_ratio = np.mean(odd_intervals) / (np.mean(even_intervals) + 1e-10)
            
            # Consistent swing indicates good groove
            swing_consistency = 1.0 - np.std([swing_ratio] * len(intervals)) if len(intervals) > 1 else 0.5
            return float(max(0.0, min(1.0, swing_consistency)))
        
        return 0.5
    
    def _determine_confidence_level(self, tempo: float, stability: float, beat_count: int, onset_density: float) -> TempoConfidence:
        """Determine overall confidence level for tempo detection."""
        confidence_score = 0.0
        
        # Tempo in reasonable range
        if 60 <= tempo <= 200:
            confidence_score += 0.3
        
        # Good stability
        if stability > 0.8:
            confidence_score += 0.3
        elif stability > 0.6:
            confidence_score += 0.2
        elif stability > 0.4:
            confidence_score += 0.1
        
        # Sufficient beats detected
        if beat_count > 16:
            confidence_score += 0.2
        elif beat_count > 8:
            confidence_score += 0.1
        
        # Reasonable onset density
        if 1.0 <= onset_density <= 10.0:
            confidence_score += 0.2
        
        if confidence_score >= 0.8:
            return TempoConfidence.HIGH
        elif confidence_score >= 0.6:
            return TempoConfidence.MEDIUM
        elif confidence_score >= 0.3:
            return TempoConfidence.LOW
        else:
            return TempoConfidence.UNKNOWN


# Maintain backward compatibility
TempoDetector = ProfessionalTempoDetector
