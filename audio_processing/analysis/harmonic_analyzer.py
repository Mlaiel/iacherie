"""🎼 Professional Harmonic Analysis Engine

Advanced harmonic content analysis, chord detection, key detection,
and comprehensive tonal analysis for professional audio applications.

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


class MusicalKey(Enum):
    """Musical keys and modes"""
    C_MAJOR = "C Major"
    G_MAJOR = "G Major"
    D_MAJOR = "D Major"
    A_MAJOR = "A Major"
    E_MAJOR = "E Major"
    B_MAJOR = "B Major"
    F_SHARP_MAJOR = "F# Major"
    C_SHARP_MAJOR = "C# Major"
    F_MAJOR = "F Major"
    B_FLAT_MAJOR = "Bb Major"
    E_FLAT_MAJOR = "Eb Major"
    A_FLAT_MAJOR = "Ab Major"
    D_FLAT_MAJOR = "Db Major"
    G_FLAT_MAJOR = "Gb Major"
    
    A_MINOR = "A Minor"
    E_MINOR = "E Minor"
    B_MINOR = "B Minor"
    F_SHARP_MINOR = "F# Minor"
    C_SHARP_MINOR = "C# Minor"
    G_SHARP_MINOR = "G# Minor"
    D_SHARP_MINOR = "D# Minor"
    A_SHARP_MINOR = "A# Minor"
    D_MINOR = "D Minor"
    G_MINOR = "G Minor"
    C_MINOR = "C Minor"
    F_MINOR = "F Minor"
    B_FLAT_MINOR = "Bb Minor"
    E_FLAT_MINOR = "Eb Minor"


class ChordQuality(Enum):
    """Chord qualities"""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_7 = "dominant_7"
    MAJOR_7 = "major_7"
    MINOR_7 = "minor_7"
    HALF_DIMINISHED_7 = "half_diminished_7"
    DIMINISHED_7 = "diminished_7"
    SUSPENDED_2 = "suspended_2"
    SUSPENDED_4 = "suspended_4"


@dataclass
class ChordDetection:
    """Detected chord information"""
    start_time: float
    end_time: float
    root: str
    quality: ChordQuality
    confidence: float
    bass_note: Optional[str]
    inversions: List[str]


@dataclass
class HarmonicAnalysisResult:
    """Comprehensive harmonic analysis results"""
    key: MusicalKey
    key_confidence: float
    mode_brightness: float  # Major/minor tendency
    harmonic_ratio: float
    spectral_centroid: float
    spectral_rolloff: float
    chroma_features: np.ndarray
    chroma_deviation: float
    dominant_pitch_classes: List[Tuple[str, float]]
    chord_progression: List[ChordDetection]
    harmonic_complexity: float
    tonal_stability: float
    harmonic_rhythm: float  # Rate of harmonic change
    consonance_score: float
    modulation_points: List[Tuple[float, MusicalKey]]  # Key changes
    cadence_points: List[Tuple[float, str]]  # Detected cadences
    voice_leading_quality: float
    harmonic_tension_curve: List[Tuple[float, float]]  # Time, tension


class ProfessionalHarmonicAnalyzer:
    """🎼 Professional Harmonic Analysis Engine
    
    Advanced harmonic content analysis with chord detection, key analysis,
    and comprehensive tonal characterization for professional audio applications.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 hop_length: int = 512,
                 frame_length: int = 2048,
                 n_chroma: int = 12):
        """Initialize professional harmonic analyzer.
        
        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
            frame_length: Frame length for analysis
            n_chroma: Number of chroma bins
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.frame_length = frame_length
        self.n_chroma = n_chroma
        
        # Musical note names
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Key profiles (Krumhansl-Schmuckler profiles)
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Chord templates
        self.chord_templates = self._create_chord_templates()
        
        self.logger.info("Professional Harmonic Analyzer initialized")
    
    async def analyze_harmonics_comprehensive(self, audio_data: np.ndarray) -> HarmonicAnalysisResult:
        """Perform comprehensive harmonic analysis.
        
        Args:
            audio_data: Input audio signal
            
        Returns:
            Complete harmonic analysis results
        """
        try:
            self.logger.info("Starting comprehensive harmonic analysis...")
            
            # Extract harmonic component
            harmonic, percussive = librosa.effects.hpss(audio_data)
            
            # Chroma analysis
            chroma = librosa.feature.chroma_stft(
                y=harmonic, sr=self.sample_rate, 
                hop_length=self.hop_length, n_chroma=self.n_chroma
            )
            
            # Key detection
            key, key_confidence, mode_brightness = await self._detect_key_comprehensive(chroma)
            
            # Chord progression analysis
            chord_progression = await self._analyze_chord_progression(chroma)
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=harmonic, sr=self.sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=harmonic, sr=self.sample_rate))
            
            # Harmonic metrics
            harmonic_ratio = self._calculate_harmonic_ratio(harmonic, audio_data)
            chroma_deviation = np.std(chroma.mean(axis=1))
            dominant_pitch_classes = self._extract_dominant_pitch_classes(chroma)
            harmonic_complexity = self._calculate_harmonic_complexity(chroma)
            tonal_stability = self._calculate_tonal_stability(chroma)
            harmonic_rhythm = self._calculate_harmonic_rhythm(chord_progression)
            consonance_score = self._calculate_consonance_score(chroma)
            
            # Advanced analysis
            modulation_points = await self._detect_modulations(chroma)
            cadence_points = await self._detect_cadences(chord_progression)
            voice_leading_quality = self._analyze_voice_leading(chord_progression)
            harmonic_tension_curve = self._calculate_harmonic_tension_curve(chroma)
            
            result = HarmonicAnalysisResult(
                key=key,
                key_confidence=key_confidence,
                mode_brightness=mode_brightness,
                harmonic_ratio=harmonic_ratio,
                spectral_centroid=float(spectral_centroid),
                spectral_rolloff=float(spectral_rolloff),
                chroma_features=chroma,
                chroma_deviation=chroma_deviation,
                dominant_pitch_classes=dominant_pitch_classes,
                chord_progression=chord_progression,
                harmonic_complexity=harmonic_complexity,
                tonal_stability=tonal_stability,
                harmonic_rhythm=harmonic_rhythm,
                consonance_score=consonance_score,
                modulation_points=modulation_points,
                cadence_points=cadence_points,
                voice_leading_quality=voice_leading_quality,
                harmonic_tension_curve=harmonic_tension_curve
            )
            
            self.logger.info(f"Harmonic analysis complete: Key={key.value}, Confidence={key_confidence:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Harmonic analysis failed: {e}")
            # Return safe defaults
            return HarmonicAnalysisResult(
                key=MusicalKey.C_MAJOR,
                key_confidence=0.0,
                mode_brightness=0.5,
                harmonic_ratio=0.0,
                spectral_centroid=0.0,
                spectral_rolloff=0.0,
                chroma_features=np.zeros((12, 1)),
                chroma_deviation=0.0,
                dominant_pitch_classes=[],
                chord_progression=[],
                harmonic_complexity=0.0,
                tonal_stability=0.0,
                harmonic_rhythm=0.0,
                consonance_score=0.0,
                modulation_points=[],
                cadence_points=[],
                voice_leading_quality=0.0,
                harmonic_tension_curve=[]
            )
    
    async def analyze_harmonics(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Legacy interface for harmonic analysis (maintains compatibility)."""
        try:
            # Separate harmonic and percussive components
            harmonic, percussive = librosa.effects.hpss(audio_data)
            
            # Basic chroma features for harmonic analysis
            chroma = librosa.feature.chroma_stft(y=harmonic, sr=self.sample_rate)
            
            # Calculate basic metrics
            harmonic_ratio = float(np.sum(harmonic**2) / (np.sum(audio_data**2) + 1e-10))
            chroma_mean = chroma.mean(axis=1).tolist()
            chroma_variance = chroma.var(axis=1).tolist()
            dominant_pitch_class = int(np.argmax(chroma.mean(axis=1)))
            harmonic_complexity = float(np.std(chroma.mean(axis=1)))
            
            # Key detection (simplified)
            key_strength = []
            for key_idx in range(12):
                shifted_profile = np.roll(self.major_profile, key_idx)
                correlation = np.corrcoef(chroma.mean(axis=1), shifted_profile)[0, 1]
                key_strength.append(correlation if not np.isnan(correlation) else 0.0)
            
            detected_key_idx = np.argmax(key_strength)
            key_confidence = float(max(key_strength))
            
            analysis = {
                'harmonic_ratio': harmonic_ratio,
                'chroma_mean': chroma_mean,
                'chroma_variance': chroma_variance,
                'dominant_pitch_class': dominant_pitch_class,
                'dominant_note': self.note_names[dominant_pitch_class],
                'harmonic_complexity': harmonic_complexity,
                'detected_key': self.note_names[detected_key_idx] + ' Major',
                'key_confidence': key_confidence,
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=harmonic, sr=self.sample_rate))),
                'tonal_stability': float(1.0 - np.std(chroma.mean(axis=1)))
            }
            
            self.logger.info("Basic harmonic analysis completed")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Harmonic analysis failed: {e}")
            return {
                'harmonic_ratio': 0.0,
                'chroma_mean': [0.0] * 12,
                'chroma_variance': [0.0] * 12,
                'dominant_pitch_class': 0,
                'dominant_note': 'C',
                'harmonic_complexity': 0.0,
                'detected_key': 'C Major',
                'key_confidence': 0.0,
                'spectral_centroid': 0.0,
                'tonal_stability': 0.0
            }
    
    def _create_chord_templates(self) -> Dict[str, np.ndarray]:
        """Create chord templates for recognition."""
        templates = {}
        
        # Major triads
        for root in range(12):
            template = np.zeros(12)
            template[root] = 1.0  # Root
            template[(root + 4) % 12] = 0.8  # Major third
            template[(root + 7) % 12] = 0.6  # Perfect fifth
            templates[f"{self.note_names[root]}_major"] = template
        
        # Minor triads  
        for root in range(12):
            template = np.zeros(12)
            template[root] = 1.0  # Root
            template[(root + 3) % 12] = 0.8  # Minor third
            template[(root + 7) % 12] = 0.6  # Perfect fifth
            templates[f"{self.note_names[root]}_minor"] = template
        
        # Dominant 7th chords
        for root in range(12):
            template = np.zeros(12)
            template[root] = 1.0  # Root
            template[(root + 4) % 12] = 0.8  # Major third
            template[(root + 7) % 12] = 0.6  # Perfect fifth
            template[(root + 10) % 12] = 0.7  # Minor seventh
            templates[f"{self.note_names[root]}_dom7"] = template
        
        return templates
    
    async def _detect_key_comprehensive(self, chroma: np.ndarray) -> Tuple[MusicalKey, float, float]:
        """Comprehensive key detection with mode analysis."""
        chroma_mean = chroma.mean(axis=1)
        
        best_correlation = -1
        best_key = MusicalKey.C_MAJOR
        mode_brightness = 0.5
        
        # Test all major keys
        for key_idx in range(12):
            shifted_profile = np.roll(self.major_profile, key_idx)
            correlation = np.corrcoef(chroma_mean, shifted_profile)[0, 1]
            
            if not np.isnan(correlation) and correlation > best_correlation:
                best_correlation = correlation
                best_key = list(MusicalKey)[key_idx]  # Major keys first in enum
                mode_brightness = 0.7  # Major tendency
        
        # Test all minor keys
        for key_idx in range(12):
            shifted_profile = np.roll(self.minor_profile, key_idx)
            correlation = np.corrcoef(chroma_mean, shifted_profile)[0, 1]
            
            if not np.isnan(correlation) and correlation > best_correlation:
                best_correlation = correlation
                best_key = list(MusicalKey)[key_idx + 14]  # Minor keys offset in enum
                mode_brightness = 0.3  # Minor tendency
        
        confidence = max(0.0, best_correlation) if not np.isnan(best_correlation) else 0.0
        
        return best_key, confidence, mode_brightness
    
    async def _analyze_chord_progression(self, chroma: np.ndarray) -> List[ChordDetection]:
        """Analyze chord progression from chroma features."""
        chord_progression = []
        
        # Segment chroma into chord-sized chunks (roughly 1-2 seconds)
        frames_per_chord = int(2 * self.sample_rate / self.hop_length)
        
        for i in range(0, chroma.shape[1], frames_per_chord):
            end_frame = min(i + frames_per_chord, chroma.shape[1])
            chord_chroma = chroma[:, i:end_frame].mean(axis=1)
            
            # Find best matching chord
            best_chord = None
            best_score = -1
            
            for chord_name, template in self.chord_templates.items():
                score = np.corrcoef(chord_chroma, template)[0, 1]
                if not np.isnan(score) and score > best_score:
                    best_score = score
                    best_chord = chord_name
            
            if best_chord and best_score > 0.3:  # Minimum confidence threshold
                root, quality_str = best_chord.split('_')
                quality = ChordQuality.MAJOR if quality_str == 'major' else \
                         ChordQuality.MINOR if quality_str == 'minor' else \
                         ChordQuality.DOMINANT_7
                
                start_time = i * self.hop_length / self.sample_rate
                end_time = end_frame * self.hop_length / self.sample_rate
                
                chord_detection = ChordDetection(
                    start_time=start_time,
                    end_time=end_time,
                    root=root,
                    quality=quality,
                    confidence=float(best_score),
                    bass_note=None,  # Could be enhanced with bass detection
                    inversions=[]
                )
                
                chord_progression.append(chord_detection)
        
        return chord_progression
    
    def _calculate_harmonic_ratio(self, harmonic: np.ndarray, original: np.ndarray) -> float:
        """Calculate ratio of harmonic to total energy."""
        harmonic_energy = np.sum(harmonic**2)
        total_energy = np.sum(original**2)
        return float(harmonic_energy / (total_energy + 1e-10))
    
    def _extract_dominant_pitch_classes(self, chroma: np.ndarray) -> List[Tuple[str, float]]:
        """Extract dominant pitch classes with their strengths."""
        chroma_mean = chroma.mean(axis=1)
        
        # Sort by strength
        sorted_indices = np.argsort(chroma_mean)[::-1]
        
        dominant_classes = []
        for i in range(min(5, len(sorted_indices))):  # Top 5
            idx = sorted_indices[i]
            note = self.note_names[idx]
            strength = float(chroma_mean[idx])
            dominant_classes.append((note, strength))
        
        return dominant_classes
    
    def _calculate_harmonic_complexity(self, chroma: np.ndarray) -> float:
        """Calculate harmonic complexity based on chroma distribution."""
        chroma_mean = chroma.mean(axis=1)
        
        # Entropy-based complexity
        probabilities = chroma_mean / (chroma_mean.sum() + 1e-10)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Normalize to 0-1 range
        max_entropy = np.log2(12)  # 12 pitch classes
        complexity = entropy / max_entropy
        
        return float(complexity)
    
    def _calculate_tonal_stability(self, chroma: np.ndarray) -> float:
        """Calculate tonal stability over time."""
        if chroma.shape[1] < 2:
            return 0.0
        
        # Calculate variance in chroma over time
        chroma_variance = np.var(chroma, axis=1)
        overall_variance = np.mean(chroma_variance)
        
        # Higher variance = less stability
        stability = max(0.0, 1.0 - overall_variance)
        
        return float(stability)
    
    def _calculate_harmonic_rhythm(self, chord_progression: List[ChordDetection]) -> float:
        """Calculate rate of harmonic change."""
        if len(chord_progression) < 2:
            return 0.0
        
        total_duration = chord_progression[-1].end_time - chord_progression[0].start_time
        chord_changes = len(chord_progression) - 1
        
        # Chords per second
        harmonic_rhythm = chord_changes / (total_duration + 1e-10)
        
        return float(harmonic_rhythm)
    
    def _calculate_consonance_score(self, chroma: np.ndarray) -> float:
        """Calculate consonance score based on interval relationships."""
        chroma_mean = chroma.mean(axis=1)
        
        # Consonant intervals (in semitones): unison(0), octave(0), fifth(7), fourth(5), major third(4), minor third(3)
        consonant_intervals = [0, 3, 4, 5, 7]
        
        consonance_score = 0.0
        total_energy = np.sum(chroma_mean)
        
        for i in range(12):
            for j in range(i, 12):
                interval = (j - i) % 12
                if interval in consonant_intervals:
                    # Weight by the energy of both pitch classes
                    weight = chroma_mean[i] * chroma_mean[j]
                    consonance_score += weight
        
        # Normalize
        consonance_score = consonance_score / (total_energy**2 + 1e-10)
        
        return float(min(1.0, consonance_score))
    
    async def _detect_modulations(self, chroma: np.ndarray) -> List[Tuple[float, MusicalKey]]:
        """Detect key modulations over time."""
        modulations = []
        
        # Sliding window key analysis
        window_frames = int(4 * self.sample_rate / self.hop_length)  # 4 second windows
        hop_frames = int(2 * self.sample_rate / self.hop_length)     # 2 second hop
        
        previous_key = None
        
        for start_frame in range(0, chroma.shape[1] - window_frames, hop_frames):
            end_frame = start_frame + window_frames
            window_chroma = chroma[:, start_frame:end_frame]
            
            key, confidence, _ = await self._detect_key_comprehensive(window_chroma)
            
            if confidence > 0.5 and key != previous_key and previous_key is not None:
                time_pos = start_frame * self.hop_length / self.sample_rate
                modulations.append((time_pos, key))
            
            if confidence > 0.5:
                previous_key = key
        
        return modulations
    
    async def _detect_cadences(self, chord_progression: List[ChordDetection]) -> List[Tuple[float, str]]:
        """Detect cadential patterns in chord progression."""
        cadences = []
        
        for i in range(len(chord_progression) - 1):
            current_chord = chord_progression[i]
            next_chord = chord_progression[i + 1]
            
            # Detect common cadences
            cadence_type = self._identify_cadence_type(current_chord, next_chord)
            
            if cadence_type:
                cadences.append((current_chord.end_time, cadence_type))
        
        return cadences
    
    def _identify_cadence_type(self, chord1: ChordDetection, chord2: ChordDetection) -> Optional[str]:
        """Identify cadence type between two chords."""
        # Simplified cadence detection
        if chord1.quality == ChordQuality.DOMINANT_7 and chord2.quality == ChordQuality.MAJOR:
            return "Authentic Cadence"
        elif chord1.quality == ChordQuality.MINOR and chord2.quality == ChordQuality.MAJOR:
            return "Plagal Cadence"
        elif chord1.quality == ChordQuality.MAJOR and chord2.quality == ChordQuality.MINOR:
            return "Deceptive Cadence"
        
        return None
    
    def _analyze_voice_leading(self, chord_progression: List[ChordDetection]) -> float:
        """Analyze voice leading quality in chord progression."""
        if len(chord_progression) < 2:
            return 0.0
        
        # Simplified voice leading analysis
        # Look for smooth voice leading (stepwise motion)
        
        smooth_transitions = 0
        total_transitions = len(chord_progression) - 1
        
        for i in range(total_transitions):
            current_chord = chord_progression[i]
            next_chord = chord_progression[i + 1]
            
            # Check if chords share common tones or have stepwise motion
            # This is a simplified check
            if self._has_smooth_voice_leading(current_chord, next_chord):
                smooth_transitions += 1
        
        quality = smooth_transitions / total_transitions if total_transitions > 0 else 0.0
        return float(quality)
    
    def _has_smooth_voice_leading(self, chord1: ChordDetection, chord2: ChordDetection) -> bool:
        """Check if two chords have smooth voice leading."""
        # Simplified check - could be much more sophisticated
        # For now, just check if roots are close
        
        root1_idx = self.note_names.index(chord1.root)
        root2_idx = self.note_names.index(chord2.root)
        
        # Consider movement of 2 semitones or less as smooth
        distance = min(abs(root2_idx - root1_idx), 12 - abs(root2_idx - root1_idx))
        
        return distance <= 2
    
    def _calculate_harmonic_tension_curve(self, chroma: np.ndarray) -> List[Tuple[float, float]]:
        """Calculate harmonic tension over time."""
        tension_curve = []
        
        # Calculate tension for each frame
        for i in range(chroma.shape[1]):
            frame_chroma = chroma[:, i]
            
            # Tension based on dissonance
            tension = 0.0
            
            # Dissonant intervals: minor 2nd(1), major 7th(11), tritone(6)
            dissonant_intervals = [1, 6, 11]
            
            for pitch1 in range(12):
                for pitch2 in range(pitch1 + 1, 12):
                    interval = pitch2 - pitch1
                    if interval in dissonant_intervals:
                        # Weight by energy in both pitch classes
                        tension += frame_chroma[pitch1] * frame_chroma[pitch2]
            
            time_pos = i * self.hop_length / self.sample_rate
            tension_curve.append((time_pos, float(tension)))
        
        return tension_curve


# Maintain backward compatibility
HarmonicAnalyzer = ProfessionalHarmonicAnalyzer
