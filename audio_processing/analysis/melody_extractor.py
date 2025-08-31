"""🎵 Melody Extractor - AI-Powered Melody Line Detection & Analysis

Advanced melody extraction engine using machine learning and signal processing
to identify, track, and analyze melodic content in audio signals.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
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


class MelodyExtractionMethod(Enum):
    """Methods for melody extraction"""    PYIN = "pyin"
    CREPE = "crepe"
    YIN = "yin"
    HYBRID = "hybrid"


class MelodyConfidence(Enum):
    """Melody confidence levels"""    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4


@dataclass
class MelodySegment:
    """Individual melody segment"""    start_time: float
    end_time: float
    frequencies: np.ndarray
    confidences: np.ndarray
    notes: List[str]
    average_frequency: float
    stability: float
    vibrato_rate: float
    vibrato_depth: float


@dataclass
class MelodyAnalysisResult:
    """Complete melody analysis results"""    fundamental_frequencies: np.ndarray
    confidence_scores: np.ndarray
    time_stamps: np.ndarray
    voiced_segments: np.ndarray
    melody_segments: List[MelodySegment]
    key_signature: Optional[str]
    scale_analysis: Dict[str, Any]
    melodic_intervals: List[float]
    melodic_contour: np.ndarray
    pitch_stability: float
    vibrato_analysis: Dict[str, float]
    note_transitions: Dict[str, int]
    melodic_complexity: float
    extraction_method: str
    confidence_threshold: float


class MelodyExtractor:
    """    🎼 Professional Melody Extraction Engine
    
    Advanced AI-powered melody line detection with multiple extraction methods,
    confidence scoring, vibrato analysis, and comprehensive melodic characterization.
    """    
    def __init__(self, 
                 sample_rate: int = 44100,
                 frame_length: int = 2048,
                 hop_length: int = 512,
                 fmin: float = 80.0,
                 fmax: float = 2000.0,
                 extraction_method: MelodyExtractionMethod = MelodyExtractionMethod.PYIN,
                 confidence_threshold: float = 0.6):
        """        Initialize melody extractor with advanced configuration
        
        Args:
            sample_rate: Audio sample rate
            frame_length: Analysis frame length
            hop_length: Hop length between frames
            fmin: Minimum frequency for pitch detection
            fmax: Maximum frequency for pitch detection
            extraction_method: Primary extraction method
            confidence_threshold: Minimum confidence for melody detection
        """        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.fmin = fmin
        self.fmax = fmax
        self.extraction_method = extraction_method
        self.confidence_threshold = confidence_threshold
        
        # Musical note mapping
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Scale templates for key detection
        self.scale_templates = {
            'major': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            'minor': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'dorian': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
            'mixolydian': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0]
        }
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info(f"MelodyExtractor initialized: {extraction_method.value} method")
    
    async def extract_melody(self, audio_data: np.ndarray) -> MelodyAnalysisResult:
        """        Extract and analyze melody from audio signal
        
        Args:
            audio_data: Input audio signal
            
        Returns:
            Complete melody analysis results
        """        try:
            self.logger.info("Starting melody extraction...")
            
            # Primary melody extraction
            f0, confidence, voiced = await self._extract_fundamental_frequencies(audio_data)
            
            # Time stamps
            time_stamps = librosa.frames_to_time(
                np.arange(len(f0)), 
                sr=self.sample_rate, 
                hop_length=self.hop_length
            )
            
            # Analyze melody in parallel
            tasks = [
                self._segment_melody(f0, confidence, voiced, time_stamps),
                self._analyze_key_signature(f0, voiced),
                self._compute_melodic_intervals(f0, voiced),
                self._analyze_melodic_contour(f0, voiced),
                self._analyze_vibrato(f0, voiced, time_stamps),
                self._compute_melodic_complexity(f0, voiced)
            ]
            
            results = await asyncio.gather(*tasks)
            (melody_segments, key_signature, scale_analysis, melodic_intervals, 
             melodic_contour, vibrato_analysis, melodic_complexity) = results
            
            # Compute pitch stability
            pitch_stability = await self._compute_pitch_stability(f0, voiced)
            
            # Analyze note transitions
            note_transitions = await self._analyze_note_transitions(f0, voiced)
            
            # Create analysis result
            result = MelodyAnalysisResult(
                fundamental_frequencies=f0,
                confidence_scores=confidence,
                time_stamps=time_stamps,
                voiced_segments=voiced,
                melody_segments=melody_segments,
                key_signature=key_signature,
                scale_analysis=scale_analysis,
                melodic_intervals=melodic_intervals,
                melodic_contour=melodic_contour,
                pitch_stability=pitch_stability,
                vibrato_analysis=vibrato_analysis,
                note_transitions=note_transitions,
                melodic_complexity=melodic_complexity,
                extraction_method=self.extraction_method.value,
                confidence_threshold=self.confidence_threshold
            )
            
            self.logger.info(f"Melody extraction completed. Found {len(melody_segments)} segments")
            return result
            
        except Exception as e:
            self.logger.error(f"Melody extraction failed: {e}")
            raise
    
    async def _extract_fundamental_frequencies(self, 
                                             audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Extract fundamental frequencies using selected method"""        def extract_f0():
            if self.extraction_method == MelodyExtractionMethod.PYIN:
                return self._pyin_extraction(audio_data)
            elif self.extraction_method == MelodyExtractionMethod.YIN:
                return self._yin_extraction(audio_data)
            elif self.extraction_method == MelodyExtractionMethod.HYBRID:
                return self._hybrid_extraction(audio_data)
            else:
                return self._pyin_extraction(audio_data)  # Default
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, extract_f0)
    
    def _pyin_extraction(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """PYIN-based fundamental frequency extraction"""        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_data,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sample_rate,
                frame_length=self.frame_length,
                hop_length=self.hop_length,
                threshold=0.1,
                resolution=0.1
            )
            
            # Use voiced probabilities as confidence
            confidence = voiced_probs
            voiced = voiced_flag
            
            return f0, confidence, voiced
            
        except Exception as e:
            self.logger.error(f"PYIN extraction failed: {e}")
            # Return dummy data
            n_frames = 1 + len(audio_data) // self.hop_length
            return np.zeros(n_frames), np.zeros(n_frames), np.zeros(n_frames, dtype=bool)
    
    def _yin_extraction(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """YIN-based fundamental frequency extraction"""        try:
            # Simplified YIN implementation
            f0 = librosa.yin(
                audio_data,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sample_rate,
                frame_length=self.frame_length,
                hop_length=self.hop_length
            )
            
            # Estimate confidence and voiced segments
            confidence = np.ones_like(f0) * 0.8  # Simplified confidence
            voiced = ~np.isnan(f0)
            
            # Replace NaN values with 0
            f0 = np.nan_to_num(f0)
            
            return f0, confidence, voiced
            
        except Exception as e:
            self.logger.error(f"YIN extraction failed: {e}")
            n_frames = 1 + len(audio_data) // self.hop_length
            return np.zeros(n_frames), np.zeros(n_frames), np.zeros(n_frames, dtype=bool)
    
    def _hybrid_extraction(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Hybrid extraction combining multiple methods"""        try:
            # Get results from multiple methods
            f0_pyin, conf_pyin, voiced_pyin = self._pyin_extraction(audio_data)
            f0_yin, conf_yin, voiced_yin = self._yin_extraction(audio_data)
            
            # Combine results based on confidence
            f0_combined = np.where(conf_pyin > conf_yin, f0_pyin, f0_yin)
            conf_combined = np.maximum(conf_pyin, conf_yin)
            voiced_combined = voiced_pyin | voiced_yin
            
            return f0_combined, conf_combined, voiced_combined
            
        except Exception as e:
            self.logger.error(f"Hybrid extraction failed: {e}")
            return self._pyin_extraction(audio_data)
    
    async def _segment_melody(self, 
                            f0: np.ndarray, 
                            confidence: np.ndarray, 
                            voiced: np.ndarray, 
                            time_stamps: np.ndarray) -> List[MelodySegment]:
        """Segment melody into coherent phrases"""        def segment():
            segments = []
            
            # Find voiced segments above confidence threshold
            valid_mask = voiced & (confidence > self.confidence_threshold)
            
            if not np.any(valid_mask):
                return segments
            
            # Find continuous segments
            segment_boundaries = np.diff(np.concatenate(([False], valid_mask, [False])).astype(int))
            segment_starts = np.where(segment_boundaries == 1)[0]
            segment_ends = np.where(segment_boundaries == -1)[0]
            
            for start_idx, end_idx in zip(segment_starts, segment_ends):
                if end_idx - start_idx < 3:  # Skip very short segments
                    continue
                
                # Extract segment data
                segment_f0 = f0[start_idx:end_idx]
                segment_conf = confidence[start_idx:end_idx]
                segment_times = time_stamps[start_idx:end_idx]
                
                # Convert frequencies to note names
                notes = [self._frequency_to_note(freq) for freq in segment_f0]
                
                # Compute segment statistics
                avg_freq = np.mean(segment_f0)
                stability = 1.0 - (np.std(segment_f0) / (avg_freq + 1e-10))
                
                # Analyze vibrato
                vibrato_rate, vibrato_depth = self._analyze_segment_vibrato(segment_f0, segment_times)
                
                segment = MelodySegment(
                    start_time=segment_times[0],
                    end_time=segment_times[-1],
                    frequencies=segment_f0,
                    confidences=segment_conf,
                    notes=notes,
                    average_frequency=avg_freq,
                    stability=stability,
                    vibrato_rate=vibrato_rate,
                    vibrato_depth=vibrato_depth
                )
                
                segments.append(segment)
            
            return segments
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, segment)
    
    def _frequency_to_note(self, frequency: float) -> str:
        """Convert frequency to musical note name"""        if frequency <= 0:
            return "Rest"
        
        # A4 = 440 Hz is note number 69
        A4 = 440.0
        note_number = 12 * np.log2(frequency / A4) + 69
        
        # Get note name and octave
        note_idx = int(note_number) % 12
        octave = int(note_number) // 12 - 1
        
        return f"{self.note_names[note_idx]}{octave}"
    
    def _analyze_segment_vibrato(self, 
                               frequencies: np.ndarray, 
                               times: np.ndarray) -> Tuple[float, float]:
        """Analyze vibrato characteristics in a melody segment"""        if len(frequencies) < 10:  # Need sufficient data for vibrato analysis
            return 0.0, 0.0
        
        # Remove linear trend to isolate vibrato
        detrended = scipy.signal.detrend(frequencies)
        
        # Find peaks and troughs
        peaks, _ = scipy.signal.find_peaks(detrended, height=np.std(detrended) * 0.5)
        troughs, _ = scipy.signal.find_peaks(-detrended, height=np.std(detrended) * 0.5)
        
        if len(peaks) < 2 or len(troughs) < 2:
            return 0.0, 0.0
        
        # Estimate vibrato rate (cycles per second)
        peak_times = times[peaks]
        if len(peak_times) > 1:
            avg_period = np.mean(np.diff(peak_times))
            vibrato_rate = 1.0 / avg_period if avg_period > 0 else 0.0
        else:
            vibrato_rate = 0.0
        
        # Estimate vibrato depth (peak-to-peak variation)
        vibrato_depth = np.std(detrended) * 2.0  # Approximate peak-to-peak
        
        return float(vibrato_rate), float(vibrato_depth)
    
    async def _analyze_key_signature(self, 
                                   f0: np.ndarray, 
                                   voiced: np.ndarray) -> Tuple[Optional[str], Dict[str, Any]]:
        """Analyze key signature and scale characteristics"""        def analyze_key():
            if not np.any(voiced):
                return None, {}
            
            # Get voiced frequencies
            voiced_f0 = f0[voiced]
            
            # Convert to pitch classes
            pitch_classes = np.zeros(12)
            for freq in voiced_f0:
                if freq > 0:
                    note_number = 12 * np.log2(freq / 440.0) + 69
                    pitch_class = int(note_number) % 12
                    pitch_classes[pitch_class] += 1
            
            # Normalize
            if np.sum(pitch_classes) > 0:
                pitch_classes /= np.sum(pitch_classes)
            
            # Find best matching scale
            best_key = None
            best_score = 0
            scale_analysis = {}
            
            for key in range(12):
                for scale_name, template in self.scale_templates.items():
                    # Rotate template to match key
                    rotated_template = np.roll(template, key)
                    
                    # Compute correlation
                    score = np.corrcoef(pitch_classes, rotated_template)[0, 1]
                    
                    if not np.isnan(score) and score > best_score:
                        best_score = score
                        best_key = f"{self.note_names[key]} {scale_name}"
            
            scale_analysis = {
                'pitch_class_distribution': pitch_classes.tolist(),
                'best_match_score': float(best_score),
                'scale_confidence': float(best_score)
            }
            
            return best_key, scale_analysis
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze_key)
    
    async def _compute_melodic_intervals(self, 
                                       f0: np.ndarray, 
                                       voiced: np.ndarray) -> List[float]:
        """Compute melodic intervals in semitones"""        def compute_intervals():
            if not np.any(voiced):
                return []
            
            voiced_f0 = f0[voiced]
            intervals = []
            
            for i in range(1, len(voiced_f0)):
                if voiced_f0[i] > 0 and voiced_f0[i-1] > 0:
                    # Convert to semitones
                    interval = 12 * np.log2(voiced_f0[i] / voiced_f0[i-1])
                    intervals.append(float(interval))
            
            return intervals
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute_intervals)
    
    async def _analyze_melodic_contour(self, 
                                     f0: np.ndarray, 
                                     voiced: np.ndarray) -> np.ndarray:
        """Analyze melodic contour (shape)"""        def analyze_contour():
            if not np.any(voiced):
                return np.array([])
            
            voiced_f0 = f0[voiced]
            
            # Smooth the contour
            if len(voiced_f0) > 5:
                contour = ndimage.gaussian_filter1d(voiced_f0, sigma=2.0)
            else:
                contour = voiced_f0
            
            # Normalize to relative changes
            if len(contour) > 1:
                contour = (contour - contour[0]) / (np.std(contour) + 1e-10)
            
            return contour
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze_contour)
    
    async def _analyze_vibrato(self, 
                             f0: np.ndarray, 
                             voiced: np.ndarray, 
                             time_stamps: np.ndarray) -> Dict[str, float]:
        """Analyze global vibrato characteristics"""        def analyze():
            if not np.any(voiced):
                return {'rate': 0.0, 'depth': 0.0, 'presence': 0.0}
            
            voiced_f0 = f0[voiced]
            voiced_times = time_stamps[voiced]
            
            # Overall vibrato analysis
            vibrato_rates = []
            vibrato_depths = []
            
            # Analyze in windows
            window_size = int(self.sample_rate / self.hop_length * 2.0)  # 2-second windows
            
            for i in range(0, len(voiced_f0) - window_size, window_size // 2):
                window_f0 = voiced_f0[i:i+window_size]
                window_times = voiced_times[i:i+window_size]
                
                rate, depth = self._analyze_segment_vibrato(window_f0, window_times)
                
                if rate > 0.5:  # Valid vibrato rate
                    vibrato_rates.append(rate)
                    vibrato_depths.append(depth)
            
            # Compute averages
            avg_rate = np.mean(vibrato_rates) if vibrato_rates else 0.0
            avg_depth = np.mean(vibrato_depths) if vibrato_depths else 0.0
            presence = len(vibrato_rates) / max(1, len(voiced_f0) // (window_size // 2))
            
            return {
                'rate': float(avg_rate),
                'depth': float(avg_depth),
                'presence': float(presence)
            }
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    async def _compute_pitch_stability(self, 
                                     f0: np.ndarray, 
                                     voiced: np.ndarray) -> float:
        """Compute overall pitch stability"""        def compute():
            if not np.any(voiced):
                return 0.0
            
            voiced_f0 = f0[voiced]
            
            # Compute coefficient of variation
            mean_f0 = np.mean(voiced_f0)
            std_f0 = np.std(voiced_f0)
            
            stability = 1.0 - (std_f0 / (mean_f0 + 1e-10))
            
            return float(max(0.0, stability))
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute)
    
    async def _analyze_note_transitions(self, 
                                      f0: np.ndarray, 
                                      voiced: np.ndarray) -> Dict[str, int]:
        """Analyze note transition patterns"""        def analyze():
            if not np.any(voiced):
                return {}
            
            voiced_f0 = f0[voiced]
            notes = [self._frequency_to_note(freq) for freq in voiced_f0]
            
            transitions = {}
            
            for i in range(1, len(notes)):
                transition = f"{notes[i-1]} -> {notes[i]}"
                transitions[transition] = transitions.get(transition, 0) + 1
            
            return transitions
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    async def _compute_melodic_complexity(self, 
                                        f0: np.ndarray, 
                                        voiced: np.ndarray) -> float:
        """Compute melodic complexity score"""        def compute():
            if not np.any(voiced):
                return 0.0
            
            voiced_f0 = f0[voiced]
            
            # Factors contributing to complexity:
            # 1. Number of unique pitches
            unique_pitches = len(set(voiced_f0[voiced_f0 > 0]))
            
            # 2. Pitch range
            pitch_range = np.max(voiced_f0) - np.min(voiced_f0[voiced_f0 > 0])
            
            # 3. Interval variety
            intervals = []
            for i in range(1, len(voiced_f0)):
                if voiced_f0[i] > 0 and voiced_f0[i-1] > 0:
                    interval = abs(12 * np.log2(voiced_f0[i] / voiced_f0[i-1]))
                    intervals.append(interval)
            
            interval_variety = len(set(np.round(intervals))) if intervals else 0
            
            # 4. Rhythmic complexity (simplified)
            note_changes = np.sum(np.diff(voiced_f0) != 0)
            
            # Normalize and combine factors
            complexity = (
                unique_pitches / 20.0 +  # Normalize to typical range
                pitch_range / 1000.0 +   # Normalize pitch range
                interval_variety / 12.0 + # Normalize to semitones
                note_changes / len(voiced_f0)
            ) / 4.0
            
            return float(min(1.0, complexity))
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute)
    
    def extract_real_time_melody(self, frame: np.ndarray) -> Dict[str, Any]:
        """        Real-time melody extraction for single frame
        Optimized for low-latency processing
        """        try:
            # Simple YIN-based pitch detection
            f0 = librosa.yin(
                frame,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sample_rate
            )
            
            # Take median frequency
            median_f0 = np.nanmedian(f0)
            
            if np.isnan(median_f0) or median_f0 <= 0:
                return {
                    'frequency': 0.0,
                    'note': "Rest",
                    'confidence': 0.0,
                    'is_voiced': False
                }
            
            # Convert to note
            note = self._frequency_to_note(median_f0)
            
            # Simple confidence estimate
            confidence = 1.0 - (np.nanstd(f0) / (median_f0 + 1e-10))
            confidence = max(0.0, min(1.0, confidence))
            
            return {
                'frequency': float(median_f0),
                'note': note,
                'confidence': float(confidence),
                'is_voiced': confidence > self.confidence_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Real-time melody extraction failed: {e}")
            return {
                'frequency': 0.0,
                'note': "Rest",
                'confidence': 0.0,
                'is_voiced': False
            }
    
    def __del__(self):
        """Cleanup thread pool"""        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
