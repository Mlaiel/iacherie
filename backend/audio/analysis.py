"""🔍 Audio Analysis Module - Professional Audio Intelligence & Analysis System

Advanced audio analysis capabilities for comprehensive audio content understanding,
featuring spectral analysis, melody extraction, rhythm detection, and AI-powered
music intelligence for the IA Influencer Agent platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ COPYRIGHT & INTELLECTUAL PROPERTY WARNING:
This software and all related concepts, algorithms, and implementations are the 
exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 

UNAUTHORIZED USE, COPYING, MODIFICATION, DISTRIBUTION, OR REVERSE ENGINEERING 
IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
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
from scipy.fft import fft, fftfreq
from scipy import ndimage
import time


class WindowType(Enum):
    """Audio window types for spectral analysis"""
    HANN = "hann"
    HAMMING = "hamming"
    BLACKMAN = "blackman"
    KAISER = "kaiser"
    TUKEY = "tukey"


class MelodyExtractionMethod(Enum):
    """Methods for melody extraction"""
    PYIN = "pyin"
    CREPE = "crepe"
    YIN = "yin"
    HYBRID = "hybrid"


@dataclass
class SpectralAnalysisResult:
    """Complete spectral analysis results"""
    sample_rate: int
    duration: float
    frequency_bins: np.ndarray
    magnitude_spectrum: np.ndarray
    phase_spectrum: np.ndarray
    power_spectrum: np.ndarray
    spectral_features: Dict[str, np.ndarray]
    peak_frequencies: List[Tuple[float, float]]  # (frequency, magnitude)
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    spectral_bandwidth: np.ndarray
    zero_crossing_rate: np.ndarray
    energy_distribution: Dict[str, float]
    harmonic_analysis: Dict[str, Any]
    noise_floor: float
    dynamic_range: float
    analysis_timestamp: float


@dataclass
class MelodySegment:
    """Individual melody segment"""
    start_time: float
    end_time: float
    frequencies: np.ndarray
    confidences: np.ndarray
    notes: List[str]
    average_frequency: float
    stability: float


@dataclass
class AudioQualityMetrics:
    """Audio quality assessment metrics"""
    overall_score: float
    dynamic_range: float
    signal_to_noise_ratio: float
    thd_plus_noise: float
    frequency_response: Dict[str, float]
    stereo_balance: float
    peak_level: float
    rms_level: float
    loudness_lufs: float
    clipping_percentage: float


class SpectralAnalyzer:
    """🎼 Professional Spectral Analysis Engine
    
    Advanced frequency domain analysis with comprehensive spectral feature
    extraction, peak detection, harmonic analysis, and noise characterization.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 frame_size: int = 2048,
                 hop_length: int = 512,
                 window_type: WindowType = WindowType.HANN,
                 n_fft: Optional[int] = None):
        """Initialize spectral analyzer with advanced configuration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.hop_length = hop_length
        self.window_type = window_type
        self.n_fft = n_fft or frame_size
        
        # Initialize analysis parameters
        self.nyquist_freq = sample_rate / 2
        self.freq_resolution = sample_rate / self.n_fft
        
        # Create window function
        self.window = self._create_window()
        
        self.logger.info(f"SpectralAnalyzer initialized - Sample Rate: {sample_rate}Hz, Frame Size: {frame_size}")
    
    def _create_window(self) -> np.ndarray:
        """Create window function based on type"""
        if self.window_type == WindowType.HANN:
            return np.hanning(self.frame_size)
        elif self.window_type == WindowType.HAMMING:
            return np.hamming(self.frame_size)
        elif self.window_type == WindowType.BLACKMAN:
            return np.blackman(self.frame_size)
        elif self.window_type == WindowType.KAISER:
            return np.kaiser(self.frame_size, beta=8.6)
        elif self.window_type == WindowType.TUKEY:
            return scipy.signal.tukey(self.frame_size, alpha=0.5)
        else:
            return np.hanning(self.frame_size)
    
    def analyze(self, audio_data: np.ndarray) -> SpectralAnalysisResult:
        """Perform comprehensive spectral analysis"""
        start_time = time.time()
        
        # Compute spectrogram
        stft_matrix = librosa.stft(
            audio_data, 
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            window=self.window_type.value
        )
        
        magnitude_spectrum = np.abs(stft_matrix)
        phase_spectrum = np.angle(stft_matrix)
        power_spectrum = magnitude_spectrum ** 2
        
        # Frequency bins
        frequency_bins = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        # Extract spectral features
        spectral_features = self._extract_spectral_features(audio_data, magnitude_spectrum)
        
        # Peak detection
        peak_frequencies = self._detect_peaks(magnitude_spectrum, frequency_bins)
        
        # Energy distribution analysis
        energy_distribution = self._analyze_energy_distribution(power_spectrum, frequency_bins)
        
        # Harmonic analysis
        harmonic_analysis = self._analyze_harmonics(magnitude_spectrum, frequency_bins)
        
        # Noise floor and dynamic range
        noise_floor = self._estimate_noise_floor(magnitude_spectrum)
        dynamic_range = self._calculate_dynamic_range(magnitude_spectrum)
        
        return SpectralAnalysisResult(
            sample_rate=self.sample_rate,
            duration=len(audio_data) / self.sample_rate,
            frequency_bins=frequency_bins,
            magnitude_spectrum=magnitude_spectrum,
            phase_spectrum=phase_spectrum,
            power_spectrum=power_spectrum,
            spectral_features=spectral_features,
            peak_frequencies=peak_frequencies,
            spectral_centroid=spectral_features['spectral_centroid'],
            spectral_rolloff=spectral_features['spectral_rolloff'],
            spectral_bandwidth=spectral_features['spectral_bandwidth'],
            zero_crossing_rate=spectral_features['zero_crossing_rate'],
            energy_distribution=energy_distribution,
            harmonic_analysis=harmonic_analysis,
            noise_floor=noise_floor,
            dynamic_range=dynamic_range,
            analysis_timestamp=time.time() - start_time
        )
    
    def _extract_spectral_features(self, audio_data: np.ndarray, magnitude_spectrum: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract comprehensive spectral features"""
        features = {}
        
        # Basic spectral features
        features['spectral_centroid'] = librosa.feature.spectral_centroid(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        )[0]
        
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        )[0]
        
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        )[0]
        
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(
            audio_data, hop_length=self.hop_length
        )[0]
        
        # Advanced spectral features
        features['spectral_contrast'] = librosa.feature.spectral_contrast(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        )
        
        features['mfcc'] = librosa.feature.mfcc(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length, n_mfcc=13
        )
        
        features['chroma'] = librosa.feature.chroma_stft(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        )
        
        return features
    
    def _detect_peaks(self, magnitude_spectrum: np.ndarray, frequency_bins: np.ndarray) -> List[Tuple[float, float]]:
        """Detect spectral peaks"""
        # Average across time frames for peak detection
        avg_spectrum = np.mean(magnitude_spectrum, axis=1)
        
        # Find peaks
        peaks, properties = scipy.signal.find_peaks(
            avg_spectrum, 
            height=np.max(avg_spectrum) * 0.1,
            distance=10
        )
        
        peak_frequencies = []
        for peak_idx in peaks:
            frequency = frequency_bins[peak_idx]
            magnitude = avg_spectrum[peak_idx]
            peak_frequencies.append((frequency, magnitude))
        
        # Sort by magnitude (descending)
        peak_frequencies.sort(key=lambda x: x[1], reverse=True)
        
        return peak_frequencies[:20]  # Return top 20 peaks
    
    def _analyze_energy_distribution(self, power_spectrum: np.ndarray, frequency_bins: np.ndarray) -> Dict[str, float]:
        """Analyze energy distribution across frequency bands"""
        total_energy = np.sum(power_spectrum)
        
        # Define frequency bands
        bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_midrange': (250, 500),
            'midrange': (500, 2000),
            'upper_midrange': (2000, 4000),
            'presence': (4000, 6000),
            'brilliance': (6000, 20000)
        }
        
        energy_distribution = {}
        for band_name, (low_freq, high_freq) in bands.items():
            band_mask = (frequency_bins >= low_freq) & (frequency_bins <= high_freq)
            band_energy = np.sum(power_spectrum[band_mask])
            energy_distribution[band_name] = float(band_energy / total_energy) if total_energy > 0 else 0.0
        
        return energy_distribution
    
    def _analyze_harmonics(self, magnitude_spectrum: np.ndarray, frequency_bins: np.ndarray) -> Dict[str, Any]:
        """Analyze harmonic content"""
        avg_spectrum = np.mean(magnitude_spectrum, axis=1)
        
        # Find fundamental frequency (strongest peak)
        fundamental_idx = np.argmax(avg_spectrum)
        fundamental_freq = frequency_bins[fundamental_idx]
        
        # Find harmonics
        harmonics = []
        for harmonic in range(2, 8):  # 2nd to 7th harmonic
            target_freq = fundamental_freq * harmonic
            
            # Find closest frequency bin
            closest_idx = np.argmin(np.abs(frequency_bins - target_freq))
            if frequency_bins[closest_idx] <= self.nyquist_freq:
                harmonics.append({
                    'harmonic': harmonic,
                    'frequency': frequency_bins[closest_idx],
                    'magnitude': avg_spectrum[closest_idx],
                    'relative_magnitude': avg_spectrum[closest_idx] / avg_spectrum[fundamental_idx]
                })
        
        return {
            'fundamental_frequency': fundamental_freq,
            'fundamental_magnitude': avg_spectrum[fundamental_idx],
            'harmonics': harmonics,
            'harmonic_to_noise_ratio': self._calculate_harmonic_to_noise_ratio(avg_spectrum, harmonics)
        }
    
    def _calculate_harmonic_to_noise_ratio(self, spectrum: np.ndarray, harmonics: List[Dict]) -> float:
        """Calculate harmonic-to-noise ratio"""
        harmonic_energy = sum(h['magnitude'] for h in harmonics)
        total_energy = np.sum(spectrum)
        noise_energy = total_energy - harmonic_energy
        
        return float(harmonic_energy / noise_energy) if noise_energy > 0 else 0.0
    
    def _estimate_noise_floor(self, magnitude_spectrum: np.ndarray) -> float:
        """Estimate noise floor level"""
        # Use 10th percentile as noise floor estimate
        return float(np.percentile(magnitude_spectrum, 10))
    
    def _calculate_dynamic_range(self, magnitude_spectrum: np.ndarray) -> float:
        """Calculate dynamic range"""
        max_magnitude = np.max(magnitude_spectrum)
        noise_floor = self._estimate_noise_floor(magnitude_spectrum)
        
        return float(20 * np.log10(max_magnitude / noise_floor)) if noise_floor > 0 else 0.0


class MelodyExtractor:
    """🎵 AI-Powered Melody Line Detection & Analysis
    
    Advanced melody extraction engine using machine learning and signal processing
    to identify, track, and analyze melodic content in audio signals.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 frame_length: int = 2048,
                 hop_length: int = 512,
                 method: MelodyExtractionMethod = MelodyExtractionMethod.PYIN):
        """Initialize melody extractor"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.method = method
        
        # Frequency range for melody detection
        self.fmin = librosa.note_to_hz('C2')  # ~65.4 Hz
        self.fmax = librosa.note_to_hz('C7')  # ~2093 Hz
        
        self.logger.info(f"MelodyExtractor initialized - Method: {method.value}")
    
    def extract_melody(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Extract melody from audio data"""
        if self.method == MelodyExtractionMethod.PYIN:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_data,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
        else:
            # Fallback to basic pitch tracking
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_data,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
        
        # Time frames
        times = librosa.frames_to_time(
            np.arange(len(f0)), 
            sr=self.sample_rate, 
            hop_length=self.hop_length
        )
        
        # Convert frequencies to note names
        notes = []
        for freq in f0:
            if np.isfinite(freq) and freq > 0:
                note = librosa.hz_to_note(freq)
                notes.append(note)
            else:
                notes.append(None)
        
        # Segment melody into continuous parts
        segments = self._segment_melody(f0, voiced_probs, times, notes)
        
        return {
            'frequencies': f0,
            'times': times,
            'voiced_flags': voiced_flag,
            'voiced_probabilities': voiced_probs,
            'notes': notes,
            'segments': segments,
            'average_pitch': np.nanmean(f0[voiced_flag]),
            'pitch_range': np.nanmax(f0[voiced_flag]) - np.nanmin(f0[voiced_flag]) if np.any(voiced_flag) else 0,
            'voiced_percentage': np.mean(voiced_flag) * 100
        }
    
    def _segment_melody(self, f0: np.ndarray, voiced_probs: np.ndarray, times: np.ndarray, notes: List[str]) -> List[MelodySegment]:
        """Segment melody into continuous parts"""
        segments = []
        current_segment_start = None
        
        for i, (freq, prob, time, note) in enumerate(zip(f0, voiced_probs, times, notes)):
            if prob > 0.5 and np.isfinite(freq):  # Voice detected
                if current_segment_start is None:
                    current_segment_start = i
            else:  # Voice not detected or end of audio
                if current_segment_start is not None:
                    # End current segment
                    segment_f0 = f0[current_segment_start:i]
                    segment_probs = voiced_probs[current_segment_start:i]
                    segment_notes = notes[current_segment_start:i]
                    
                    segments.append(MelodySegment(
                        start_time=times[current_segment_start],
                        end_time=times[i-1] if i > 0 else times[current_segment_start],
                        frequencies=segment_f0,
                        confidences=segment_probs,
                        notes=[n for n in segment_notes if n is not None],
                        average_frequency=np.nanmean(segment_f0),
                        stability=np.std(segment_f0[np.isfinite(segment_f0)]) if np.any(np.isfinite(segment_f0)) else 0
                    ))
                    current_segment_start = None
        
        return segments


class RhythmAnalyzer:
    """🥁 Professional Rhythm & Tempo Analysis Engine"""
    
    def __init__(self, sample_rate: int = 44100, hop_length: int = 512):
        """Initialize rhythm analyzer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.hop_length = hop_length
    
    def analyze_rhythm(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze rhythm and tempo"""
        # Tempo estimation
        tempo, beats = librosa.beat.beat_track(
            y=audio_data, 
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        
        # Beat times
        beat_times = librosa.frames_to_time(beats, sr=self.sample_rate, hop_length=self.hop_length)
        
        # Onset detection
        onsets = librosa.onset.onset_detect(
            y=audio_data,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            units='time'
        )
        
        # Rhythmic features
        tempogram = librosa.feature.tempogram(
            y=audio_data,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        
        return {
            'tempo': float(tempo),
            'beat_times': beat_times,
            'onset_times': onsets,
            'tempogram': tempogram,
            'beat_count': len(beats),
            'average_beat_interval': np.mean(np.diff(beat_times)) if len(beat_times) > 1 else 0,
            'rhythm_stability': self._calculate_rhythm_stability(beat_times)
        }
    
    def _calculate_rhythm_stability(self, beat_times: np.ndarray) -> float:
        """Calculate rhythm stability based on beat consistency"""
        if len(beat_times) < 3:
            return 0.0
        
        intervals = np.diff(beat_times)
        return float(1.0 / (1.0 + np.std(intervals)))


class AudioQualityAssessment:
    """🎯 Professional Audio Quality Assessment Engine"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize quality assessment engine"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def assess_quality(self, audio_data: np.ndarray) -> AudioQualityMetrics:
        """Perform comprehensive audio quality assessment"""
        # Dynamic range
        dynamic_range = self._calculate_dynamic_range(audio_data)
        
        # Signal-to-noise ratio
        snr = self._calculate_snr(audio_data)
        
        # THD+N (Total Harmonic Distortion + Noise)
        thd_plus_noise = self._calculate_thd_plus_noise(audio_data)
        
        # Frequency response analysis
        frequency_response = self._analyze_frequency_response(audio_data)
        
        # Peak and RMS levels
        peak_level = float(20 * np.log10(np.max(np.abs(audio_data))))
        rms_level = float(20 * np.log10(np.sqrt(np.mean(audio_data ** 2))))
        
        # Clipping detection
        clipping_percentage = self._detect_clipping(audio_data)
        
        # Overall quality score
        overall_score = self._calculate_overall_score(
            dynamic_range, snr, thd_plus_noise, clipping_percentage
        )
        
        return AudioQualityMetrics(
            overall_score=overall_score,
            dynamic_range=dynamic_range,
            signal_to_noise_ratio=snr,
            thd_plus_noise=thd_plus_noise,
            frequency_response=frequency_response,
            stereo_balance=1.0,  # Placeholder for mono signals
            peak_level=peak_level,
            rms_level=rms_level,
            loudness_lufs=-23.0,  # Placeholder
            clipping_percentage=clipping_percentage
        )
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range"""
        peak = np.max(np.abs(audio_data))
        noise_floor = np.percentile(np.abs(audio_data), 10)
        return float(20 * np.log10(peak / noise_floor)) if noise_floor > 0 else 0.0
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        signal_power = np.mean(audio_data ** 2)
        noise_power = np.var(audio_data - np.mean(audio_data))
        return float(10 * np.log10(signal_power / noise_power)) if noise_power > 0 else 0.0
    
    def _calculate_thd_plus_noise(self, audio_data: np.ndarray) -> float:
        """Calculate Total Harmonic Distortion + Noise"""
        # Simplified THD+N calculation
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data)
        
        # Find fundamental frequency
        fundamental_idx = np.argmax(magnitude[1:len(magnitude)//2]) + 1
        fundamental_power = magnitude[fundamental_idx] ** 2
        
        # Calculate total power and THD+N
        total_power = np.sum(magnitude[1:len(magnitude)//2] ** 2)
        thd_plus_noise = float(10 * np.log10((total_power - fundamental_power) / fundamental_power)) if fundamental_power > 0 else 0.0
        
        return thd_plus_noise
    
    def _analyze_frequency_response(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Analyze frequency response characteristics"""
        # Simplified frequency response analysis
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)[:len(magnitude)]
        
        # Frequency bands
        bands = {
            'bass_response': np.mean(magnitude[(freqs >= 20) & (freqs <= 250)]),
            'midrange_response': np.mean(magnitude[(freqs >= 250) & (freqs <= 4000)]),
            'treble_response': np.mean(magnitude[(freqs >= 4000) & (freqs <= 20000)])
        }
        
        return {k: float(v) for k, v in bands.items()}
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """Detect audio clipping percentage"""
        threshold = 0.99
        clipped_samples = np.sum(np.abs(audio_data) >= threshold)
        return float(clipped_samples / len(audio_data) * 100)
    
    def _calculate_overall_score(self, dynamic_range: float, snr: float, thd_plus_noise: float, clipping: float) -> float:
        """Calculate overall quality score"""
        # Normalized scoring (0-100)
        dr_score = min(dynamic_range / 60.0, 1.0) * 25  # Max 25 points
        snr_score = min(snr / 60.0, 1.0) * 25  # Max 25 points
        thd_score = max(0, (60 + thd_plus_noise) / 60.0) * 25  # Max 25 points (lower THD is better)
        clip_score = max(0, (100 - clipping) / 100.0) * 25  # Max 25 points (no clipping is best)
        
        return float(dr_score + snr_score + thd_score + clip_score)


class GenreClassifier:
    """🎼 AI-Powered Music Genre Classification"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize genre classifier"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Genre categories
        self.genres = [
            'rock', 'pop', 'jazz', 'classical', 'electronic', 
            'hip_hop', 'country', 'blues', 'reggae', 'folk'
        ]
    
    def classify(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Classify audio genre using feature analysis"""
        # Extract features for classification
        features = self._extract_genre_features(audio_data)
        
        # Simple rule-based classification (placeholder)
        genre_scores = self._calculate_genre_scores(features)
        
        return genre_scores
    
    def _extract_genre_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract features relevant for genre classification"""
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # Rhythm features
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        
        # Harmonic features
        harmonic = librosa.effects.harmonic(audio_data)
        percussive = librosa.effects.percussive(audio_data)
        harmonic_ratio = np.mean(np.abs(harmonic)) / (np.mean(np.abs(percussive)) + 1e-10)
        
        return {
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'zero_crossing_rate': float(zero_crossing_rate),
            'tempo': float(tempo),
            'harmonic_ratio': float(harmonic_ratio)
        }
    
    def _calculate_genre_scores(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate genre scores based on features"""
        scores = {}
        
        # Simple rule-based scoring (placeholder for ML model)
        for genre in self.genres:
            if genre == 'electronic':
                scores[genre] = features['spectral_centroid'] / 2000.0
            elif genre == 'classical':
                scores[genre] = features['harmonic_ratio'] / 2.0
            elif genre == 'hip_hop':
                scores[genre] = (200 - abs(features['tempo'] - 100)) / 200.0
            else:
                scores[genre] = 0.1  # Default low score
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores


class InstrumentIdentifier:
    """🎺 AI-Powered Musical Instrument Recognition"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize instrument identifier"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Instrument categories
        self.instruments = [
            'piano', 'guitar', 'violin', 'drums', 'flute', 
            'trumpet', 'saxophone', 'voice', 'bass', 'cello'
        ]
    
    def identify(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Identify instruments in audio"""
        # Extract instrument-specific features
        features = self._extract_instrument_features(audio_data)
        
        # Calculate instrument probabilities
        instrument_scores = self._calculate_instrument_scores(features)
        
        return instrument_scores
    
    def _extract_instrument_features(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Extract features for instrument identification"""
        # Spectral features
        mfcc = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=self.sample_rate)
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
        
        # Attack/decay characteristics
        onset_envelope = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
        
        return {
            'mfcc_mean': np.mean(mfcc, axis=1),
            'spectral_contrast_mean': np.mean(spectral_contrast, axis=1),
            'chroma_mean': np.mean(chroma, axis=1),
            'onset_strength': np.mean(onset_envelope)
        }
    
    def _calculate_instrument_scores(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate instrument identification scores"""
        scores = {}
        
        # Simple rule-based scoring (placeholder for ML model)
        for instrument in self.instruments:
            if instrument == 'drums':
                scores[instrument] = features['onset_strength'] / 10.0
            elif instrument == 'piano':
                scores[instrument] = np.mean(features['chroma_mean'])
            else:
                scores[instrument] = 0.1  # Default low score
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores


class VoiceActivityDetector:
    """🎤 Advanced Voice Activity Detection"""
    
    def __init__(self, sample_rate: int = 44100, frame_length: int = 2048):
        """Initialize voice activity detector"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.frame_length = frame_length
    
    def detect(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Detect voice activity in audio"""
        # Energy-based VAD
        frame_energy = self._calculate_frame_energy(audio_data)
        
        # Spectral features for VAD
        spectral_features = self._extract_vad_features(audio_data)
        
        # Voice activity decision
        voice_activity = self._make_vad_decision(frame_energy, spectral_features)
        
        # Voice segments
        voice_segments = self._extract_voice_segments(voice_activity)
        
        return {
            'voice_activity': voice_activity,
            'voice_segments': voice_segments,
            'speech_percentage': np.mean(voice_activity) * 100,
            'frame_energy': frame_energy
        }
    
    def _calculate_frame_energy(self, audio_data: np.ndarray) -> np.ndarray:
        """Calculate frame-based energy"""
        hop_length = self.frame_length // 2
        frame_energy = []
        
        for i in range(0, len(audio_data) - self.frame_length, hop_length):
            frame = audio_data[i:i + self.frame_length]
            energy = np.sum(frame ** 2)
            frame_energy.append(energy)
        
        return np.array(frame_energy)
    
    def _extract_vad_features(self, audio_data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract features for VAD"""
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        
        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)[0]
        
        return {
            'zero_crossing_rate': zcr,
            'spectral_centroid': spectral_centroid
        }
    
    def _make_vad_decision(self, frame_energy: np.ndarray, features: Dict[str, np.ndarray]) -> np.ndarray:
        """Make voice activity decision"""
        # Simple threshold-based VAD
        energy_threshold = np.mean(frame_energy) + np.std(frame_energy)
        energy_vad = frame_energy > energy_threshold
        
        # Combine with spectral features
        zcr_threshold = np.mean(features['zero_crossing_rate'])
        zcr_vad = features['zero_crossing_rate'][:len(energy_vad)] < zcr_threshold
        
        # Combined decision
        voice_activity = energy_vad & zcr_vad
        
        return voice_activity
    
    def _extract_voice_segments(self, voice_activity: np.ndarray) -> List[Tuple[float, float]]:
        """Extract continuous voice segments"""
        segments = []
        in_voice = False
        start_frame = 0
        
        hop_length = self.frame_length // 2
        
        for i, is_voice in enumerate(voice_activity):
            if is_voice and not in_voice:
                # Start of voice segment
                start_frame = i
                in_voice = True
            elif not is_voice and in_voice:
                # End of voice segment
                start_time = start_frame * hop_length / self.sample_rate
                end_time = i * hop_length / self.sample_rate
                segments.append((start_time, end_time))
                in_voice = False
        
        # Handle case where voice continues to end
        if in_voice:
            start_time = start_frame * hop_length / self.sample_rate
            end_time = len(voice_activity) * hop_length / self.sample_rate
            segments.append((start_time, end_time))
        
        return segments


class AudioMetadataExtractor:
    """📊 Comprehensive Audio Metadata Extraction"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize metadata extractor"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def extract_metadata(self, audio_data: np.ndarray, filename: Optional[str] = None) -> Dict[str, Any]:
        """Extract comprehensive audio metadata"""
        duration = len(audio_data) / self.sample_rate
        
        # Basic properties
        metadata = {
            'duration': duration,
            'sample_rate': self.sample_rate,
            'channels': 1 if audio_data.ndim == 1 else audio_data.shape[0],
            'total_samples': len(audio_data),
            'bit_depth': 'float32',  # Assuming float32 data
            'file_size_bytes': audio_data.nbytes if hasattr(audio_data, 'nbytes') else len(audio_data) * 4
        }
        
        # Audio characteristics
        metadata.update({
            'peak_amplitude': float(np.max(np.abs(audio_data))),
            'rms_amplitude': float(np.sqrt(np.mean(audio_data ** 2))),
            'dynamic_range_db': self._calculate_dynamic_range(audio_data),
            'silence_percentage': self._calculate_silence_percentage(audio_data),
            'dc_offset': float(np.mean(audio_data))
        })
        
        # Frequency domain analysis
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)[:len(magnitude)]
        
        dominant_freq_idx = np.argmax(magnitude)
        metadata.update({
            'dominant_frequency': float(freqs[dominant_freq_idx]),
            'spectral_bandwidth': self._calculate_spectral_bandwidth(magnitude, freqs),
            'spectral_centroid': self._calculate_spectral_centroid(magnitude, freqs)
        })
        
        return metadata
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range in dB"""
        peak = np.max(np.abs(audio_data))
        noise_floor = np.percentile(np.abs(audio_data), 10)
        return float(20 * np.log10(peak / noise_floor)) if noise_floor > 0 else 0.0
    
    def _calculate_silence_percentage(self, audio_data: np.ndarray) -> float:
        """Calculate percentage of silence"""
        threshold = 0.01 * np.max(np.abs(audio_data))
        silent_samples = np.sum(np.abs(audio_data) < threshold)
        return float(silent_samples / len(audio_data) * 100)
    
    def _calculate_spectral_bandwidth(self, magnitude: np.ndarray, freqs: np.ndarray) -> float:
        """Calculate spectral bandwidth"""
        # Weighted average frequency
        centroid = self._calculate_spectral_centroid(magnitude, freqs)
        
        # Bandwidth as weighted standard deviation
        variance = np.sum(((freqs - centroid) ** 2) * magnitude) / np.sum(magnitude)
        return float(np.sqrt(variance))
    
    def _calculate_spectral_centroid(self, magnitude: np.ndarray, freqs: np.ndarray) -> float:
        """Calculate spectral centroid"""
        return float(np.sum(freqs * magnitude) / np.sum(magnitude))


class HarmonicAnalyzer:
    """🎼 Advanced Harmonic Content Analysis"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize harmonic analyzer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def analyze_harmonics(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze harmonic content"""
        # Separate harmonic and percussive components
        harmonic = librosa.effects.harmonic(audio_data, margin=8)
        percussive = librosa.effects.percussive(audio_data, margin=8)
        
        # Harmonic-to-percussive ratio
        harmonic_energy = np.sum(harmonic ** 2)
        percussive_energy = np.sum(percussive ** 2)
        hpr = harmonic_energy / (percussive_energy + 1e-10)
        
        # Pitch analysis
        pitches, magnitudes = librosa.piptrack(y=harmonic, sr=self.sample_rate)
        
        return {
            'harmonic_component': harmonic,
            'percussive_component': percussive,
            'harmonic_to_percussive_ratio': float(hpr),
            'harmonic_energy_percentage': float(harmonic_energy / (harmonic_energy + percussive_energy) * 100),
            'pitch_stability': self._calculate_pitch_stability(pitches),
            'harmonic_richness': self._calculate_harmonic_richness(harmonic)
        }
    
    def _calculate_pitch_stability(self, pitches: np.ndarray) -> float:
        """Calculate pitch stability"""
        # Extract non-zero pitches
        non_zero_pitches = pitches[pitches > 0]
        if len(non_zero_pitches) < 2:
            return 0.0
        
        # Calculate stability as inverse of standard deviation
        stability = 1.0 / (1.0 + np.std(non_zero_pitches))
        return float(stability)
    
    def _calculate_harmonic_richness(self, harmonic_component: np.ndarray) -> float:
        """Calculate harmonic richness"""
        # FFT of harmonic component
        fft_data = np.fft.fft(harmonic_component)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Find peaks (harmonics)
        peaks, _ = scipy.signal.find_peaks(magnitude, height=np.max(magnitude) * 0.1)
        
        # Richness as number of significant harmonics
        return float(len(peaks))


class TempoDetector:
    """🥁 Professional Tempo Detection & Beat Tracking"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize tempo detector"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def detect_tempo(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Detect tempo and beat information"""
        # Beat tracking
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        
        # Beat times
        beat_times = librosa.frames_to_time(beats, sr=self.sample_rate)
        
        # Tempo stability
        tempo_stability = self._calculate_tempo_stability(beat_times)
        
        # Multiple tempo hypotheses
        tempo_histogram = self._calculate_tempo_histogram(audio_data)
        
        return {
            'primary_tempo': float(tempo),
            'beat_times': beat_times,
            'beat_count': len(beats),
            'tempo_stability': tempo_stability,
            'tempo_confidence': self._calculate_tempo_confidence(tempo_histogram, tempo),
            'tempo_histogram': tempo_histogram
        }
    
    def _calculate_tempo_stability(self, beat_times: np.ndarray) -> float:
        """Calculate tempo stability"""
        if len(beat_times) < 3:
            return 0.0
        
        intervals = np.diff(beat_times)
        stability = 1.0 / (1.0 + np.std(intervals))
        return float(stability)
    
    def _calculate_tempo_histogram(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Calculate tempo histogram"""
        # Multiple tempo analysis with different parameters
        tempos = []
        
        for win_length in [2048, 4096, 8192]:
            try:
                tempo, _ = librosa.beat.beat_track(
                    y=audio_data, 
                    sr=self.sample_rate,
                    hop_length=win_length//4
                )
                tempos.append(tempo)
            except:
                continue
        
        # Create histogram
        tempo_ranges = [(60, 80), (80, 100), (100, 120), (120, 140), (140, 160), (160, 180)]
        histogram = {}
        
        for low, high in tempo_ranges:
            range_name = f"{low}-{high}_bpm"
            count = sum(1 for t in tempos if low <= t < high)
            histogram[range_name] = count / len(tempos) if tempos else 0.0
        
        return histogram
    
    def _calculate_tempo_confidence(self, tempo_histogram: Dict[str, float], primary_tempo: float) -> float:
        """Calculate confidence in primary tempo"""
        # Find which range the primary tempo falls into
        for range_name, probability in tempo_histogram.items():
            low, high = map(int, range_name.split('-')[0].split('_')[0]), map(int, range_name.split('-')[1].split('_')[0])
            if low <= primary_tempo < high:
                return float(probability)
        
        return 0.0


class KeyDetector:
    """🎹 Musical Key Detection & Tonal Analysis"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize key detector"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Key profiles (Krumhansl-Schmuckler)
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    def detect_key(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Detect musical key"""
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
        
        # Average chroma over time
        chroma_avg = np.mean(chroma, axis=1)
        
        # Key detection using correlation with key profiles
        major_correlations = []
        minor_correlations = []
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        for i in range(12):
            # Rotate profiles for each key
            major_rotated = np.roll(self.major_profile, i)
            minor_rotated = np.roll(self.minor_profile, i)
            
            # Calculate correlations
            major_corr = np.corrcoef(chroma_avg, major_rotated)[0, 1]
            minor_corr = np.corrcoef(chroma_avg, minor_rotated)[0, 1]
            
            major_correlations.append(major_corr)
            minor_correlations.append(minor_corr)
        
        # Find best matches
        best_major_idx = np.argmax(major_correlations)
        best_minor_idx = np.argmax(minor_correlations)
        
        best_major_corr = major_correlations[best_major_idx]
        best_minor_corr = minor_correlations[best_minor_idx]
        
        if best_major_corr > best_minor_corr:
            detected_key = f"{note_names[best_major_idx]} major"
            confidence = float(best_major_corr)
        else:
            detected_key = f"{note_names[best_minor_idx]} minor"
            confidence = float(best_minor_corr)
        
        return {
            'detected_key': detected_key,
            'confidence': confidence,
            'chroma_vector': chroma_avg,
            'major_correlations': dict(zip(note_names, major_correlations)),
            'minor_correlations': dict(zip(note_names, minor_correlations)),
            'key_stability': self._calculate_key_stability(chroma)
        }
    
    def _calculate_key_stability(self, chroma: np.ndarray) -> float:
        """Calculate key stability over time"""
        if chroma.shape[1] < 2:
            return 0.0
        
        # Calculate frame-to-frame chroma correlation
        correlations = []
        for i in range(chroma.shape[1] - 1):
            corr = np.corrcoef(chroma[:, i], chroma[:, i + 1])[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
        
        return float(np.mean(correlations)) if correlations else 0.0


class MoodAnalyzer:
    """😊 AI-Powered Music Mood & Emotion Analysis"""
    
    def __init__(self, sample_rate: int = 44100):
        """Initialize mood analyzer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Mood categories
        self.moods = [
            'happy', 'sad', 'angry', 'calm', 'energetic', 
            'melancholic', 'uplifting', 'dark', 'romantic', 'dramatic'
        ]
    
    def analyze_mood(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze musical mood and emotion"""
        # Extract mood-relevant features
        features = self._extract_mood_features(audio_data)
        
        # Calculate mood probabilities
        mood_scores = self._calculate_mood_scores(features)
        
        # Emotional dimensions (valence, arousal, dominance)
        emotional_dimensions = self._calculate_emotional_dimensions(features)
        
        return {
            'mood_scores': mood_scores,
            'dominant_mood': max(mood_scores.items(), key=lambda x: x[1])[0],
            'emotional_dimensions': emotional_dimensions,
            'mood_intensity': self._calculate_mood_intensity(features),
            'emotional_stability': self._calculate_emotional_stability(audio_data)
        }
    
    def _extract_mood_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract features relevant for mood analysis"""
        # Tempo and rhythm
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate))
        
        # Harmonic vs percussive
        harmonic = librosa.effects.harmonic(audio_data)
        percussive = librosa.effects.percussive(audio_data)
        harmonic_ratio = np.mean(np.abs(harmonic)) / (np.mean(np.abs(percussive)) + 1e-10)
        
        # Dynamic range
        dynamic_range = np.max(audio_data) - np.min(audio_data)
        
        # Zero crossing rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # MFCC for timbral characteristics
        mfcc = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        return {
            'tempo': float(tempo),
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'harmonic_ratio': float(harmonic_ratio),
            'dynamic_range': float(dynamic_range),
            'zero_crossing_rate': float(zcr),
            'mfcc_brightness': float(mfcc_mean[1]),  # Second MFCC coefficient
            'energy': float(np.mean(audio_data ** 2))
        }
    
    def _calculate_mood_scores(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate mood scores based on features"""
        scores = {}
        
        # Simple rule-based mood scoring (placeholder for ML model)
        tempo = features['tempo']
        brightness = features['spectral_centroid']
        energy = features['energy']
        harmonic_ratio = features['harmonic_ratio']
        
        # Happy: high tempo, bright, energetic
        scores['happy'] = min(1.0, (tempo - 60) / 140.0 + brightness / 5000.0 + energy * 10)
        
        # Sad: low tempo, dark, low energy
        scores['sad'] = min(1.0, 2.0 - (tempo / 100.0) - (brightness / 3000.0) - energy * 5)
        
        # Energetic: high tempo, high energy
        scores['energetic'] = min(1.0, (tempo - 80) / 120.0 + energy * 15)
        
        # Calm: moderate tempo, harmonic
        scores['calm'] = min(1.0, 1.0 - abs(tempo - 80) / 40.0 + harmonic_ratio / 3.0)
        
        # Default scores for other moods
        for mood in self.moods:
            if mood not in scores:
                scores[mood] = 0.1
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
    
    def _calculate_emotional_dimensions(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate emotional dimensions (valence, arousal, dominance)"""
        # Valence (positive/negative emotion)
        valence = (features['spectral_centroid'] / 5000.0 + features['harmonic_ratio'] / 3.0) / 2.0
        
        # Arousal (activation level)
        arousal = (features['tempo'] / 200.0 + features['energy'] * 10 + features['dynamic_range']) / 3.0
        
        # Dominance (control/power)
        dominance = (features['dynamic_range'] + features['energy'] * 5) / 2.0
        
        return {
            'valence': min(1.0, max(0.0, float(valence))),
            'arousal': min(1.0, max(0.0, float(arousal))),
            'dominance': min(1.0, max(0.0, float(dominance)))
        }
    
    def _calculate_mood_intensity(self, features: Dict[str, float]) -> float:
        """Calculate overall mood intensity"""
        # Intensity based on energy and dynamic range
        intensity = (features['energy'] * 10 + features['dynamic_range']) / 2.0
        return min(1.0, max(0.0, float(intensity)))
    
    def _calculate_emotional_stability(self, audio_data: np.ndarray) -> float:
        """Calculate emotional stability over time"""
        # Divide audio into segments and analyze mood variation
        segment_length = len(audio_data) // 10
        if segment_length < 1024:
            return 1.0  # Too short for stability analysis
        
        segment_features = []
        for i in range(0, len(audio_data) - segment_length, segment_length):
            segment = audio_data[i:i + segment_length]
            features = self._extract_mood_features(segment)
            segment_features.append(features['energy'])
        
        # Stability as inverse of energy variation
        if len(segment_features) > 1:
            stability = 1.0 / (1.0 + np.std(segment_features))
        else:
            stability = 1.0
        
        return float(stability)


# Export all classes
__all__ = [
    'SpectralAnalyzer',
    'MelodyExtractor',
    'RhythmAnalyzer',
    'AudioQualityAssessment',
    'GenreClassifier',
    'InstrumentIdentifier',
    'VoiceActivityDetector',
    'AudioMetadataExtractor',
    'HarmonicAnalyzer',
    'TempoDetector',
    'KeyDetector',
    'MoodAnalyzer',
    'SpectralAnalysisResult',
    'MelodySegment',
    'AudioQualityMetrics',
    'WindowType',
    'MelodyExtractionMethod'
]