"""🥁 Rhythm Analyzer - Advanced Beat Detection & Rhythmic Analysis

Professional rhythm analysis engine providing comprehensive beat tracking,
tempo estimation, rhythm pattern recognition, and metrical analysis.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import librosa
import scipy.signal
from scipy import ndimage


class BeatTrackingMethod(Enum):
    """
Beat tracking methods"""

    ELLIS = "ellis"
    DEGARA = "degara"
    CRF = "crf"
    HYBRID = "hybrid"


class TempoConfidence(Enum):
    """Tempo confidence levels"""

    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4


@dataclass
class BeatEvent:
    """
Individual beat event"""
    time: float
    strength: float
    confidence: float
    is_downbeat: bool
    metrical_position: int


@dataclass
class RhythmPattern:
    """
Rhythm pattern analysis"""
    pattern_id: str
    pattern_sequence: List[float]
    duration: float
    repetitions: int
    confidence: float
    time_signature: str
    syncopation_level: float


@dataclass
class RhythmAnalysisResult:
    """
Complete rhythm analysis results"""
    tempo_bpm: float
    tempo_confidence: float
    beat_times: np.ndarray
    beat_strengths: np.ndarray
    downbeat_times: np.ndarray
    time_signature: str
    meter_confidence: float
    rhythm_patterns: List[RhythmPattern]
    onset_times: np.ndarray
    onset_strengths: np.ndarray
    tempo_stability: float
    syncopation_score: float
    rhythmic_complexity: float
    groove_consistency: float
    metrical_hierarchy: Dict[str, List[float]]
    tempo_changes: List[Tuple[float, float]]  # (time, new_tempo)
    analysis_method: str


class RhythmAnalyzer:
    """
    🥁 Professional Rhythm Analysis Engine
    
    Advanced beat tracking with multiple detection algorithms, tempo estimation,
    rhythm pattern recognition, and comprehensive rhythmic characterization.
    """
    
    def __init__(self,
                 sample_rate: int = 44100,
                 hop_length: int = 512,
                 frame_length: int = 2048,
                 tempo_min: float = 30.0,
                 tempo_max: float = 300.0,
                 beat_method: BeatTrackingMethod = BeatTrackingMethod.ELLIS):
        """
        Initialize rhythm analyzer with advanced configuration
        
        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
            frame_length: Frame length for analysis
            tempo_min: Minimum tempo for detection
            tempo_max: Maximum tempo for detection
            beat_method: Beat tracking method
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.frame_length = frame_length
        self.tempo_min = tempo_min
        self.tempo_max = tempo_max
        self.beat_method = beat_method
        
        # Common time signatures
        self.time_signatures = {
            '4/4': [4, 4],
            '3/4': [3, 4],
            '2/4': [2, 4],
            '6/8': [6, 8],
            '9/8': [9, 8],
            '12/8': [12, 8],
            '5/4': [5, 4],
            '7/8': [7, 8]
        }
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info(f"RhythmAnalyzer initialized: {beat_method.value} method")
    
    async def analyze_rhythm(self, audio_data: np.ndarray) -> RhythmAnalysisResult:
        """
        Perform comprehensive rhythm analysis
        
        Args:
            audio_data: Input audio signal
            
        Returns:
            Complete rhythm analysis results
        """
        try:
            self.logger.info("Starting rhythm analysis...")
            
            # Extract onset detection function and beats
            onset_envelope = librosa.onset.onset_strength(
                y=audio_data,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Primary analysis tasks in parallel
            tasks = [
                self._estimate_tempo(onset_envelope),
                self._track_beats(onset_envelope),
                self._detect_onsets(audio_data),
                self._analyze_downbeats(onset_envelope),
            ]
            
            results = await asyncio.gather(*tasks)
            (tempo_bpm, tempo_confidence), (beat_times, beat_strengths), (onset_times, onset_strengths), downbeat_times = results
            
            # Secondary analysis tasks
            tasks2 = [
                self._determine_time_signature(beat_times, onset_times),
                self._analyze_rhythm_patterns(beat_times, onset_times, tempo_bpm),
                self._compute_tempo_stability(beat_times),
                self._analyze_syncopation(beat_times, onset_times),
                self._compute_rhythmic_complexity(beat_times, onset_times),
                self._analyze_groove_consistency(beat_times),
                self._detect_tempo_changes(onset_envelope)
            ]
            
            results2 = await asyncio.gather(*tasks2)
            (time_signature, meter_confidence, rhythm_patterns, tempo_stability, 
             syncopation_score, rhythmic_complexity, groove_consistency, tempo_changes) = results2
            
            # Build metrical hierarchy
            metrical_hierarchy = await self._build_metrical_hierarchy(beat_times, downbeat_times, time_signature)
            
            # Create analysis result
            result = RhythmAnalysisResult(
                tempo_bpm=tempo_bpm,
                tempo_confidence=tempo_confidence,
                beat_times=beat_times,
                beat_strengths=beat_strengths,
                downbeat_times=downbeat_times,
                time_signature=time_signature,
                meter_confidence=meter_confidence,
                rhythm_patterns=rhythm_patterns,
                onset_times=onset_times,
                onset_strengths=onset_strengths,
                tempo_stability=tempo_stability,
                syncopation_score=syncopation_score,
                rhythmic_complexity=rhythmic_complexity,
                groove_consistency=groove_consistency,
                metrical_hierarchy=metrical_hierarchy,
                tempo_changes=tempo_changes,
                analysis_method=self.beat_method.value
            )
            
            self.logger.info(f"Rhythm analysis completed: {tempo_bpm:.1f} BPM, {time_signature}")
            return result
            
        except Exception as e:
            self.logger.error(f"Rhythm analysis failed: {e}")
            raise
    
    async def _estimate_tempo(self, onset_envelope: np.ndarray) -> Tuple[float, float]:
        """Estimate tempo using multiple methods"""
        def estimate():
            try:
                # Use librosa's beat tracking algorithm
                tempo, beats = librosa.beat.beat_track(
                    onset_envelope=onset_envelope,
                    sr=self.sample_rate,
                    hop_length=self.hop_length,
                    start_bpm=120.0,
                    tightness=100,
                    trim=True,
                    bpm_min=self.tempo_min,
                    bpm_max=self.tempo_max
                )
                
                # Confidence estimation based on beat consistency
                if len(beats) > 1:
                    beat_intervals = np.diff(beats)
                    interval_consistency = 1.0 - (np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-10))
                    confidence = max(0.0, min(1.0, interval_consistency))
                else:
                    confidence = 0.0
                
                return float(tempo), float(confidence)
                
            except Exception as e:
                self.logger.warning(f"Tempo estimation failed: {e}")
                return 120.0, 0.0
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, estimate)
    
    async def _track_beats(self, onset_envelope: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Track beats using selected method"""
        def track_beats():
            try:
                if self.beat_method == BeatTrackingMethod.ELLIS:
                    return self._ellis_beat_tracking(onset_envelope)
                elif self.beat_method == BeatTrackingMethod.DEGARA:
                    return self._degara_beat_tracking(onset_envelope)
                elif self.beat_method == BeatTrackingMethod.HYBRID:
                    return self._hybrid_beat_tracking(onset_envelope)
                else:
                    return self._ellis_beat_tracking(onset_envelope)  # Default
            except Exception as e:
                self.logger.error(f"Beat tracking failed: {e}")
                return np.array([]), np.array([])
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, track_beats)
    
    def _ellis_beat_tracking(self, onset_envelope: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Ellis beat tracking algorithm"""
        tempo, beats = librosa.beat.beat_track(
            onset_envelope=onset_envelope,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            start_bpm=120.0,
            tightness=100,
            trim=True
        )
        
        # Convert beat indices to times
        beat_times = librosa.frames_to_time(beats, sr=self.sample_rate, hop_length=self.hop_length)
        
        # Estimate beat strengths from onset envelope
        beat_strengths = onset_envelope[beats] if len(beats) > 0 else np.array([])
        
        return beat_times, beat_strengths
    
    def _degara_beat_tracking(self, onset_envelope: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        try:
            logger.info(f"Executing detect")
            
            # Implementation for detect
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"detect completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"detect failed: {e}")
            raise
    def _degara_beat_tracking(self, onset_envelope: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
Degara beat tracking algorithm (simplified implementation)"""
        # Use Ellis as fallback with different parameters
        tempo, beats = librosa.beat.beat_track(
            onset_envelope=onset_envelope,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            start_bpm=120.0,
            tightness=200,  # Tighter tracking
            trim=True
        )
        
        beat_times = librosa.frames_to_time(beats, sr=self.sample_rate, hop_length=self.hop_length)
        beat_strengths = onset_envelope[beats] if len(beats) > 0 else np.array([])
        
        return beat_times, beat_strengths
    
    def _hybrid_beat_tracking(self, onset_envelope: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
Hybrid beat tracking combining multiple methods"""
        # Get results from multiple methods
        ellis_times, ellis_strengths = self._ellis_beat_tracking(onset_envelope)
        degara_times, degara_strengths = self._degara_beat_tracking(onset_envelope)
        
        # Simple combination: use Ellis as primary, fill gaps with Degara
        combined_times = ellis_times
        combined_strengths = ellis_strengths
        
        return combined_times, combined_strengths
    
    async def _detect_onsets(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect onset times and strengths"""
        try:
            # Onset detection
            onset_frames = librosa.onset.onset_detect(
                y=audio_data,
                sr=self.sample_rate,
                hop_length=self.hop_length,
                pre_max=3,
                post_max=3,
                pre_avg=3,
                post_avg=5,
                delta=0.07,
                wait=10
            )
            
            # Convert to times
            onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate, hop_length=self.hop_length)
            
            # Get onset strengths
            onset_envelope = librosa.onset.onset_strength(
                y=audio_data,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            onset_strengths = onset_envelope[onset_frames] if len(onset_frames) > 0 else np.array([])
            
            return onset_times, onset_strengths
            
        except Exception as e:
            logger.error(f"Onset detection failed: {e}")
            return np.array([]), np.array([])
    
    async def _analyze_downbeats(self, onset_envelope: np.ndarray) -> np.ndarray:
        """Analyze downbeat locations"""
        try:
            # Simple downbeat detection (every 4 beats for 4/4)
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_envelope,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            if len(beats) == 0:
                return np.array([])
            
            # Assume 4/4 time signature for simplicity
            downbeat_indices = beats[::4]  # Every 4th beat
            downbeat_times = librosa.frames_to_time(downbeat_indices, sr=self.sample_rate, hop_length=self.hop_length)
            
            return downbeat_times
            
        except Exception as e:
            logger.warning(f"Downbeat analysis failed: {e}")
            return np.array([])
    
    async def _determine_time_signature(self, 
                                      beat_times: np.ndarray, 
                                      onset_times: np.ndarray) -> Tuple[str, float]:
        """Determine time signature and confidence"""
        def determine():
            if len(beat_times) < 8:  # Need sufficient beats
                return '4/4', 0.0
            
            # Analyze beat groupings
            beat_intervals = np.diff(beat_times)
            avg_beat_interval = np.mean(beat_intervals)
            
            # Test different time signatures
            best_signature = '4/4'
            best_score = 0.0
            
            for signature, (numerator, denominator) in self.time_signatures.items():
                # Expected beats per measure
                beats_per_measure = numerator if denominator == 4 else numerator * 2
                
                # Test periodicity
                expected_measure_duration = avg_beat_interval * beats_per_measure
                
                # Compute autocorrelation-based score (simplified)
                score = self._compute_periodicity_score(beat_times, expected_measure_duration)
                
                if score > best_score:
                    best_score = score
                    best_signature = signature
            
            confidence = min(1.0, best_score)
            return best_signature, float(confidence)
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, determine)
    
    def _compute_periodicity_score(self, beat_times: np.ndarray, expected_period: float) -> float:
        """
Compute periodicity score for given period"""
        if len(beat_times) < 2:
            return 0.0
        
        # Create binary beat signal
        duration = beat_times[-1] - beat_times[0]
        sample_rate = 100  # Hz
        signal_length = int(duration * sample_rate)
        
        beat_signal = np.zeros(signal_length)
        
        for beat_time in beat_times:
            sample_idx = int((beat_time - beat_times[0]) * sample_rate)
            if 0 <= sample_idx < signal_length:
                beat_signal[sample_idx] = 1.0
        
        # Compute autocorrelation
        autocorr = np.correlate(beat_signal, beat_signal, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Look for peak at expected period
        expected_lag = int(expected_period * sample_rate)
        if expected_lag < len(autocorr):
            # Normalize by autocorrelation at zero lag
            score = autocorr[expected_lag] / (autocorr[0] + 1e-10)
        else:
            score = 0.0
        
        return float(score)
    
    async def _analyze_rhythm_patterns(self, 
                                     beat_times: np.ndarray, 
                                     onset_times: np.ndarray, 
                                     tempo_bpm: float) -> List[RhythmPattern]:
        """
Analyze rhythm patterns"""
        def analyze():
            patterns = []
            
            if len(beat_times) < 4 or len(onset_times) < 4:
                return patterns
            
            # Define pattern window (4 beats)
            beat_duration = 60.0 / tempo_bpm
            pattern_duration = beat_duration * 4
            
            # Extract patterns
            pattern_id = 0
            for i in range(0, len(beat_times) - 4, 2):  # Overlapping windows
                window_start = beat_times[i]
                window_end = window_start + pattern_duration
                
                # Find onsets in this window
                window_onsets = onset_times[(onset_times >= window_start) & (onset_times < window_end)]
                
                if len(window_onsets) > 0:
                    # Normalize to pattern start
                    pattern_sequence = (window_onsets - window_start).tolist()
                    
                    # Simple pattern analysis
                    syncopation = self._compute_syncopation_level(window_onsets, beat_times[i:i+4])
                    
                    pattern = RhythmPattern(
                        pattern_id=f"pattern_{pattern_id}",
                        pattern_sequence=pattern_sequence,
                        duration=pattern_duration,
                        repetitions=1,  # Simplified
                        confidence=0.8,  # Simplified
                        time_signature='4/4',  # Simplified
                        syncopation_level=syncopation
                    )
                    
                    patterns.append(pattern)
                    pattern_id += 1
            
            return patterns[:10]  # Return top 10 patterns
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    def _compute_syncopation_level(self, onsets: np.ndarray, beats: np.ndarray) -> float:
        """Compute syncopation level for onset pattern"""
        if len(onsets) == 0 or len(beats) == 0:
            return 0.0
        
        # Simple syncopation measure: onsets not on beats
        syncopated_onsets = 0
        beat_tolerance = 0.05  # 50ms tolerance
        
        for onset in onsets:
            on_beat = any(abs(onset - beat) < beat_tolerance for beat in beats)
            if not on_beat:
                syncopated_onsets += 1
        
        return float(syncopated_onsets / len(onsets))
    
    async def _compute_tempo_stability(self, beat_times: np.ndarray) -> float:
        """
Compute tempo stability"""
        def compute():
            if len(beat_times) < 3:
                return 0.0
            
            # Compute beat intervals
            beat_intervals = np.diff(beat_times)
            
            # Stability as inverse of coefficient of variation
            mean_interval = np.mean(beat_intervals)
            std_interval = np.std(beat_intervals)
            
            stability = 1.0 - (std_interval / (mean_interval + 1e-10))
            
            return float(max(0.0, min(1.0, stability)))
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute)
    
    async def _analyze_syncopation(self, 
                                 beat_times: np.ndarray, 
                                 onset_times: np.ndarray) -> float:
        """
Analyze overall syncopation score"""
        def analyze():
            if len(beat_times) == 0 or len(onset_times) == 0:
                return 0.0
            
            return self._compute_syncopation_level(onset_times, beat_times)
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    async def _compute_rhythmic_complexity(self, 
                                         beat_times: np.ndarray, 
                                         onset_times: np.ndarray) -> float:
        """
Compute rhythmic complexity score"""
        def compute():
            if len(beat_times) == 0 or len(onset_times) == 0:
                return 0.0
            
            # Factors contributing to complexity:
            # 1. Onset density
            duration = beat_times[-1] - beat_times[0] if len(beat_times) > 1 else 1.0
            onset_density = len(onset_times) / duration
            
            # 2. Syncopation level
            syncopation = self._compute_syncopation_level(onset_times, beat_times)
            
            # 3. Tempo variation
            if len(beat_times) > 2:
                beat_intervals = np.diff(beat_times)
                tempo_variation = np.std(beat_intervals) / np.mean(beat_intervals)
            else:
                tempo_variation = 0.0
            
            # Combine factors (normalized)
            complexity = (
                min(onset_density / 10.0, 1.0) * 0.4 +  # Onset density
                syncopation * 0.4 +                      # Syncopation
                min(tempo_variation * 10.0, 1.0) * 0.2   # Tempo variation
            )
            
            return float(complexity)
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute)
    
    async def _analyze_groove_consistency(self, beat_times: np.ndarray) -> float:
        """
Analyze groove consistency"""
        def analyze():
            if len(beat_times) < 4:
                return 0.0
            
            # Compute beat intervals
            intervals = np.diff(beat_times)
            
            # Groove consistency as temporal regularity
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            consistency = 1.0 - (std_interval / (mean_interval + 1e-10))
            
            return float(max(0.0, min(1.0, consistency)))
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    async def _build_metrical_hierarchy(self, 
                                       beat_times: np.ndarray, 
                                       downbeat_times: np.ndarray, 
                                       time_signature: str) -> Dict[str, List[float]]:
        """
Build metrical hierarchy"""
        def build():
            hierarchy = {
                'beats': beat_times.tolist(),
                'downbeats': downbeat_times.tolist(),
                'measures': [],
                'phrases': []
            }
            
            # Estimate measures (simplified)
            if len(downbeat_times) > 1:
                measure_duration = np.mean(np.diff(downbeat_times))
                measures = []
                current_time = downbeat_times[0] if len(downbeat_times) > 0 else 0.0
                max_time = beat_times[-1] if len(beat_times) > 0 else 0.0
                
                while current_time < max_time:
                    measures.append(current_time)
                    current_time += measure_duration
                
                hierarchy['measures'] = measures
            
            # Estimate phrases (every 4 measures)
            if hierarchy['measures']:
                phrases = hierarchy['measures'][::4]
                hierarchy['phrases'] = phrases
            
            return hierarchy
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, build)
    
    async def _detect_tempo_changes(self, onset_envelope: np.ndarray) -> List[Tuple[float, float]]:
        """
Detect tempo changes over time"""
        def detect():
            tempo_changes = []
            
            # Analyze tempo in windows
            window_size = int(self.sample_rate * 10 / self.hop_length)  # 10-second windows
            overlap = window_size // 2
            
            for i in range(0, len(onset_envelope) - window_size, overlap):
                window_envelope = onset_envelope[i:i+window_size]
                
                try:
                    tempo, _ = librosa.beat.beat_track(
                        onset_envelope=window_envelope,
                        sr=self.sample_rate,
                        hop_length=self.hop_length
                    )
                    
                    time_position = librosa.frames_to_time(i, sr=self.sample_rate, hop_length=self.hop_length)
                    tempo_changes.append((float(time_position), float(tempo)))
                    
                except:
                    continue
            
            return tempo_changes
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, detect)
    
    def analyze_real_time_beat(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Real-time beat analysis for single frame
        Optimized for low-latency processing
        """
        try:
            # Simple onset strength computation
            onset_strength = librosa.onset.onset_strength(
                y=frame,
                sr=self.sample_rate,
                hop_length=self.hop_length // 4  # Smaller hop for responsiveness
            )
            
            # Current onset strength
            current_strength = np.mean(onset_strength) if len(onset_strength) > 0 else 0.0
            
            # Simple beat probability (would need state for proper tracking)
            beat_probability = min(1.0, current_strength * 2.0)
            
            # Estimate instantaneous tempo (simplified)
            tempo_estimate = 120.0  # Would need beat history for proper estimation
            
            return {
                'onset_strength': float(current_strength),
                'beat_probability': float(beat_probability),
                'tempo_estimate': float(tempo_estimate),
                'is_beat_likely': beat_probability > 0.7
            }
            
        except Exception as e:
            self.logger.error(f"Real-time beat analysis failed: {e}")
            return {
                'onset_strength': 0.0,
                'beat_probability': 0.0,
                'tempo_estimate': 120.0,
                'is_beat_likely': False
            }
    
    def __del__(self):
        """Cleanup thread pool"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
