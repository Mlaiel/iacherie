"""🎵 Audio Transformation Engine - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/data_management/transformers/audio_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import subprocess
import tempfile
import shutil

import numpy as np
import librosa
import soundfile as sf
import pydub
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import essentia
import essentia.standard as es
from scipy import signal
from scipy.signal import butter, filtfilt, wiener
import noisereduce as nr

from ..models.audio_models import AudioMetadata, AudioQualityMetrics
from ...core.exceptions import AudioProcessingError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager
from ...utils.validation import validate_audio_file

settings = get_settings()
logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """
Formats audio supportés"""

    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"

class AudioQuality(Enum):
    """Niveaux de qualité audio"""

    ULTRA = "ultra"      # 24-bit, 96kHz+
    HIGH = "high"        # 16-bit, 44.1kHz
    STANDARD = "standard" # Compressed, optimized
    LOW = "low"          # Highly compressed

class NormalizationType(Enum):
    """Types de normalisation audio"""

    PEAK = "peak"           # Peak normalization
    LUFS = "lufs"          # Loudness normalization
    RMS = "rms"            # RMS normalization
    DYNAMIC = "dynamic"     # Dynamic range preservation

@dataclass
class AudioProcessingResult:
    """Résultat du traitement audio"""
    success: bool
    input_file: str
    output_file: Optional[str]
    original_metadata: AudioMetadata
    processed_metadata: AudioMetadata
    quality_metrics: AudioQualityMetrics
    processing_time: float
    operations_performed: List[str]
    warnings: List[str]
    errors: List[str]

class AudioAnalyzer:
    """
Analyseur audio professionnel pour créateurs musicaux"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des algorithmes Essentia
        self.feature_extractors = {
            'spectral': {
                'spectral_centroid': es.SpectralCentroid(),
                'spectral_rolloff': es.SpectralRolloffPoint(),
                'spectral_flux': es.SpectralFlux(),
                'mfcc': es.MFCC(),
                'chroma': es.HPCP()
            },
            'rhythm': {
                'bpm': es.PercivalBpmEstimator(),
                'onset_rate': es.OnsetRate(),
                'beats': es.BeatTrackerMultiFeature()
            },
            'tonal': {
                'key': es.KeyExtractor(),
                'dissonance': es.Dissonance(),
                'harmony': es.HarmonicPeaks()
            },
            'loudness': {
                'loudness': es.Loudness(),
                'dynamic_range': es.DynamicComplexity(),
                'level': es.Level()
            }
        }
    
    def analyze_audio_file(self, audio_path: str) -> AudioMetadata:
        """
Analyse complète d'un fichier audio"""
        try:
            # Chargement audio avec librosa pour analyse
            y, sr = librosa.load(audio_path, sr=None)
            
            # Analyse basique
            duration = len(y) / sr
            sample_rate = sr
            channels = 1 if y.ndim == 1 else y.shape[0]
            
            # Calcul des métriques avancées
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Analyse spectrale
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Analyse harmonique
            harmonics, percussives = librosa.effects.hpss(y)
            harmonic_ratio = np.mean(harmonics ** 2) / np.mean(y ** 2)
            
            # Calcul du niveau RMS et dynamique
            rms = np.sqrt(np.mean(y ** 2))
            peak = np.max(np.abs(y))
            dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
            
            # Estimation de la tonalité avec librosa
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            key_profile = np.mean(chroma, axis=1)
            estimated_key = np.argmax(key_profile)
            
            # Détection de la présence vocale
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            vocal_confidence = self._estimate_vocal_presence(y, sr)
            
            return AudioMetadata(
                filename=Path(audio_path).name,
                format=Path(audio_path).suffix.lower().lstrip('.'),
                duration=float(duration),
                sample_rate=int(sample_rate),
                channels=int(channels),
                bitrate=None,  # À calculer selon le format
                file_size=Path(audio_path).stat().st_size,
                
                # Métriques musicales
                tempo=float(tempo),
                key=self._key_number_to_name(estimated_key),
                loudness_lufs=float(20 * np.log10(rms + 1e-10)),
                dynamic_range=float(dynamic_range),
                
                # Métriques spectrales
                spectral_centroid=float(spectral_centroid),
                spectral_rolloff=float(spectral_rolloff),
                spectral_bandwidth=float(spectral_bandwidth),
                zero_crossing_rate=float(zero_crossing_rate),
                
                # Métriques avancées
                harmonic_ratio=float(harmonic_ratio),
                vocal_confidence=float(vocal_confidence),
                
                # Tags automatiques
                genre_predictions=[],
                mood_predictions=[],
                instrument_predictions=[]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse audio {audio_path}: {e}")
            raise AudioProcessingError(f"Échec analyse audio: {str(e)}")
    
    def _estimate_vocal_presence(self, y: np.ndarray, sr: int) -> float:
        """Estime la présence vocale dans l'audio"""
        # Analyse dans la bande de fréquence vocale (80-255 Hz pour fondamentale)
        # et (1-8 kHz pour formants)
        
        # Calcul du spectrogramme
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        # Focus sur les fréquences vocales
        freqs = librosa.fft_frequencies(sr=sr)
        vocal_freq_mask = (freqs >= 80) & (freqs <= 8000)
        
        if np.any(vocal_freq_mask):
            vocal_energy = np.mean(D[vocal_freq_mask, :])
            total_energy = np.mean(D)
            
            # Ratio d'énergie vocale
            vocal_ratio = vocal_energy / (total_energy + 1e-10)
            return min(1.0, max(0.0, vocal_ratio))
        
        return 0.0
    
    def _key_number_to_name(self, key_number: int) -> str:
        """
Convertit un numéro de tonalité en nom"""
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return keys[key_number % 12]

class AudioEnhancer:
    """
Améliorateur audio IA pour créateurs musicaux"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enhance_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        enhancement_type: str = "balanced",
        intensity: float = 0.5
    ) -> np.ndarray:
        """Améliore la qualité audio avec IA"""
        
        try:
            enhanced = audio_data.copy()
            
            if enhancement_type == "vocal":
                enhanced = self._enhance_vocals(enhanced, sample_rate, intensity)
            elif enhancement_type == "instrumental":
                enhanced = self._enhance_instrumental(enhanced, sample_rate, intensity)
            elif enhancement_type == "master":
                enhanced = self._master_audio(enhanced, sample_rate, intensity)
            elif enhancement_type == "noise_reduction":
                enhanced = self._reduce_noise(enhanced, sample_rate, intensity)
            else:  # balanced
                enhanced = self._balanced_enhancement(enhanced, sample_rate, intensity)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Erreur amélioration audio: {e}")
            return audio_data
    
    def _enhance_vocals(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """Améliore les voix dans l'audio"""
        # Séparation harmonique/percussive
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Boost des fréquences vocales (1-4 kHz)
        enhanced = self._apply_eq_boost(harmonic, sr, center_freq=2500, bandwidth=2000, gain=intensity * 6)
        
        # Ajout de clarté haute fréquence
        enhanced = self._apply_eq_boost(enhanced, sr, center_freq=8000, bandwidth=4000, gain=intensity * 3)
        
        # Recombinaison avec les percussions
        return enhanced + percussive * 0.8
    
    def _enhance_instrumental(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """
Améliore les instruments dans l'audio"""
        # Séparation harmonique/percussive
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Amélioration des graves (60-250 Hz)
        enhanced = self._apply_eq_boost(audio, sr, center_freq=150, bandwidth=190, gain=intensity * 4)
        
        # Clarté dans les médiums (250-4000 Hz)
        enhanced = self._apply_eq_boost(enhanced, sr, center_freq=1000, bandwidth=2000, gain=intensity * 2)
        
        # Présence haute (4-12 kHz)
        enhanced = self._apply_eq_boost(enhanced, sr, center_freq=6000, bandwidth=4000, gain=intensity * 3)
        
        return enhanced
    
    def _master_audio(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """
Mastering audio professionnel"""
        enhanced = audio.copy()
        
        # 1. Compression douce
        enhanced = self._apply_compression(enhanced, ratio=1 + intensity * 2, threshold=0.7)
        
        # 2. EQ de mastering
        enhanced = self._apply_mastering_eq(enhanced, sr, intensity)
        
        # 3. Excitation harmonique
        enhanced = self._apply_harmonic_excitation(enhanced, intensity)
        
        # 4. Limitation finale
        enhanced = self._apply_limiter(enhanced, ceiling=0.95)
        
        return enhanced
    
    def _reduce_noise(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """
Réduction de bruit avancée"""
        try:
            # Utilisation de noisereduce
            reduced = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=False,
                prop_decrease=intensity
            )
            return reduced
        except Exception:
            # Fallback vers filtrage spectral simple
            return self._spectral_gating(audio, sr, intensity)
    
    def _balanced_enhancement(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """
Amélioration équilibrée pour tous types de contenu"""
        enhanced = audio.copy()
        
        # EQ douce globale
        enhanced = self._apply_eq_boost(enhanced, sr, center_freq=100, bandwidth=50, gain=intensity * 2)    # Sub-bass
        enhanced = self._apply_eq_boost(enhanced, sr, center_freq=3000, bandwidth=2000, gain=intensity * 1) # Présence
        enhanced = self._apply_eq_boost(enhanced, sr, center_freq=10000, bandwidth=6000, gain=intensity * 2) # Air
        
        # Compression douce
        enhanced = self._apply_compression(enhanced, ratio=1 + intensity, threshold=0.8)
        
        return enhanced
    
    def _apply_eq_boost(
        self,
        audio: np.ndarray,
        sr: int,
        center_freq: float,
        bandwidth: float,
        gain: float
    ) -> np.ndarray:
        """
Applique un boost EQ à une fréquence spécifique"""
        # Conversion en dB
        gain_linear = 10 ** (gain / 20)
        
        # Calcul des fréquences de coupure
        low_freq = max(20, center_freq - bandwidth / 2)
        high_freq = min(sr / 2 - 1, center_freq + bandwidth / 2)
        
        # Normalisation des fréquences
        nyquist = sr / 2
        low_norm = low_freq / nyquist
        high_norm = high_freq / nyquist
        
        if low_norm >= 1.0 or high_norm >= 1.0:
            return audio
        
        # Filtre passe-bande
        try:
            b, a = butter(4, [low_norm, high_norm], btype='band')
            filtered = filtfilt(b, a, audio)
            
            # Application du gain
            boosted = filtered * (gain_linear - 1)
            
            return audio + boosted
        except Exception:
            return audio
    
    def _apply_compression(
        self,
        audio: np.ndarray,
        ratio: float = 2.0,
        threshold: float = 0.7,
        attack: float = 0.003,
        release: float = 0.1
    ) -> np.ndarray:
        """
Applique une compression dynamique"""
        # Conversion en PyDub pour compression
        try:
            # Normalisation pour PyDub
            audio_int = (audio * 32767).astype(np.int16)
            audio_segment = AudioSegment(
                audio_int.tobytes(),
                frame_rate=22050,  # Default fallback
                sample_width=2,
                channels=1
            )
            
            # Application compression
            compressed = compress_dynamic_range(
                audio_segment,
                threshold=threshold * 100,
                ratio=ratio,
                attack=attack * 1000,
                release=release * 1000
            )
            
            # Reconversion en numpy
            compressed_array = np.array(compressed.get_array_of_samples(), dtype=np.float32)
            return compressed_array / 32767.0
            
        except Exception:
            # Fallback vers compression simple
            return np.tanh(audio * ratio) / ratio
    
    def _apply_mastering_eq(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """
EQ de mastering professionnel"""
        enhanced = audio.copy()
        
        # Courbe de mastering typique
        eq_points = [
            (60, intensity * 1),      # Sub-bass control
            (200, intensity * -0.5),  # Mud reduction
            (1000, intensity * 0.5),  # Midrange clarity
            (3000, intensity * 1),    # Presence
            (8000, intensity * 1.5),  # Brilliance
            (15000, intensity * 1)    # Air
        ]
        
        for freq, gain in eq_points:
            enhanced = self._apply_eq_boost(enhanced, sr, freq, freq * 0.8, gain)
        
        return enhanced
    
    def _apply_harmonic_excitation(self, audio: np.ndarray, intensity: float) -> np.ndarray:
        """
Ajoute de l'excitation harmonique"""
        # Saturation douce pour harmoniques
        drive = 1 + intensity * 2
        excited = np.tanh(audio * drive) / drive
        
        # Mélange avec signal original
        mix = intensity * 0.3
        return audio * (1 - mix) + excited * mix
    
    def _apply_limiter(self, audio: np.ndarray, ceiling: float = 0.95) -> np.ndarray:
        """
Applique une limitation finale"""
        # Limitation douce
        limited = np.where(
            np.abs(audio) > ceiling,
            np.sign(audio) * ceiling,
            audio
        )
        return limited
    
    def _spectral_gating(self, audio: np.ndarray, sr: int, intensity: float) -> np.ndarray:
        """
Réduction de bruit par gating spectral"""
        # STFT
        D = librosa.stft(audio)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Estimation du bruit (premiers frames)
        noise_frames = min(10, magnitude.shape[1] // 10)
        noise_profile = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Seuil adaptatif
        threshold = noise_profile * (1 + intensity * 2)
        
        # Gating
        mask = magnitude > threshold
        magnitude_gated = magnitude * mask + noise_profile * 0.1 * (~mask)
        
        # Reconstruction
        D_gated = magnitude_gated * np.exp(1j * phase)
        return librosa.istft(D_gated)

class AudioTransformer:
    """
Transformateur audio principal pour créateurs de contenu"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager()
        self.analyzer = AudioAnalyzer()
        self.enhancer = AudioEnhancer()
        
        # Configurations par défaut selon le type de créateur
        self.creator_presets = {
            'musician': {
                'quality': AudioQuality.HIGH,
                'normalization': NormalizationType.LUFS,
                'enhancement': 'master',
                'preserve_dynamics': True
            },
            'podcaster': {
                'quality': AudioQuality.STANDARD,
                'normalization': NormalizationType.LUFS,
                'enhancement': 'vocal',
                'noise_reduction': True
            },
            'content_creator': {
                'quality': AudioQuality.STANDARD,
                'normalization': NormalizationType.PEAK,
                'enhancement': 'balanced',
                'compression': True
            }
        }
    
    def transform(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """
Transformation audio selon configuration"""
        
        start_time = time.time()
        operations = []
        warnings = []
        errors = []
        
        try:
            # Validation du fichier d'entrée
            if not validate_audio_file(input_path):
                raise ValidationError(f"Fichier audio invalide: {input_path}")
            
            # Analyse du fichier source
            original_metadata = self.analyzer.analyze_audio_file(input_path)
            operations.append("Analyse métadonnées")
            
            # Chargement audio
            audio_data, sample_rate = librosa.load(input_path, sr=None)
            operations.append("Chargement audio")
            
            # Préparation du chemin de sortie
            if not output_path:
                output_path = self._generate_output_path(input_path, config)
            
            # Application des transformations selon le type
            if config.type.value == 'audio_normalize':
                audio_data = self._normalize_audio(audio_data, config.parameters)
                operations.append("Normalisation")
                
            elif config.type.value == 'audio_convert':
                audio_data = self._convert_format(audio_data, sample_rate, config.parameters, output_path)
                operations.append("Conversion format")
                
            elif config.type.value == 'audio_compress':
                audio_data = self._compress_audio(audio_data, config.parameters)
                operations.append("Compression")
                
            elif config.type.value == 'audio_enhance':
                audio_data = self._enhance_audio(audio_data, sample_rate, config.parameters)
                operations.append("Amélioration IA")
            
            # Sauvegarde du fichier traité
            self._save_audio(audio_data, sample_rate, output_path, config)
            operations.append("Sauvegarde")
            
            # Analyse finale
            processed_metadata = self.analyzer.analyze_audio_file(output_path)
            
            # Calcul des métriques de qualité
            quality_metrics = self._calculate_quality_metrics(
                original_metadata, processed_metadata
            )
            
            processing_time = time.time() - start_time
            
            from . import TransformationResult, TransformationType
            return TransformationResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                transformation_type=TransformationType(config.type.value),
                metadata={
                    'original': original_metadata.__dict__,
                    'processed': processed_metadata.__dict__,
                    'quality_metrics': quality_metrics.__dict__
                },
                errors=errors,
                warnings=warnings,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Erreur transformation audio {input_path}: {e}")
            processing_time = time.time() - start_time
            
            from . import TransformationResult, TransformationType
            return TransformationResult(
                success=False,
                input_path=input_path,
                output_path=None,
                transformation_type=TransformationType(config.type.value),
                metadata={},
                errors=[str(e)],
                warnings=warnings,
                processing_time=processing_time
            )
    
    def _normalize_audio(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Normalise l'audio selon le type spécifié"""
        
        norm_type = params.get('type', 'peak')
        target_level = params.get('target_level', -3.0)
        
        if norm_type == 'peak':
            # Normalisation peak
            peak = np.max(np.abs(audio_data))
            if peak > 0:
                target_linear = 10 ** (target_level / 20)
                return audio_data * (target_linear / peak)
        
        elif norm_type == 'rms':
            # Normalisation RMS
            rms = np.sqrt(np.mean(audio_data ** 2))
            if rms > 0:
                target_linear = 10 ** (target_level / 20)
                return audio_data * (target_linear / rms)
        
        elif norm_type == 'lufs':
            # Normalisation LUFS (loudness)
            # Calcul approximatif du LUFS
            rms = np.sqrt(np.mean(audio_data ** 2))
            lufs_estimate = -0.691 + 10 * np.log10(rms ** 2 + 1e-10)
            
            lufs_adjustment = target_level - lufs_estimate
            gain_linear = 10 ** (lufs_adjustment / 20)
            
            return audio_data * gain_linear
        
        return audio_data
    
    def _convert_format(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        params: Dict[str, Any],
        output_path: str
    ) -> np.ndarray:
        """
Convertit le format audio"""
        
        target_format = params.get('format', 'mp3')
        bitrate = params.get('bitrate', 192)
        quality = params.get('quality', 'standard')
        
        # Les paramètres de format seront appliqués lors de la sauvegarde
        # Ici on peut appliquer des prétraitements selon le format cible
        
        if target_format in ['mp3', 'aac', 'ogg']:
            # Formats compressés - filtrage anti-aliasing
            if sample_rate > 44100:
                # Downsampling pour formats compressés
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=44100)
                sample_rate = 44100
        
        return audio_data
    
    def _compress_audio(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """
Applique une compression dynamique"""
        
        ratio = params.get('ratio', 2.0)
        threshold = params.get('threshold', 0.7)
        attack = params.get('attack', 0.003)
        release = params.get('release', 0.1)
        
        return self.enhancer._apply_compression(
            audio_data, ratio, threshold, attack, release
        )
    
    def _enhance_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        params: Dict[str, Any]
    ) -> np.ndarray:
        """
Améliore la qualité audio"""
        
        enhancement_type = params.get('type', 'balanced')
        intensity = params.get('intensity', 0.5)
        
        return self.enhancer.enhance_audio(
            audio_data, sample_rate, enhancement_type, intensity
        )
    
    def _save_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        output_path: str,
        config: 'TransformationConfig'
    ) -> None:
        """
Sauvegarde l'audio traité"""
        
        output_format = config.output_format or Path(output_path).suffix.lstrip('.')
        params = config.parameters
        
        # Création du répertoire si nécessaire
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if output_format in ['wav', 'flac']:
            # Formats non compressés
            subtype = 'PCM_24' if config.quality == 'ultra' else 'PCM_16'
            sf.write(output_path, audio_data, sample_rate, subtype=subtype)
            
        elif output_format == 'mp3':
            # Conversion MP3 via PyDub
            self._save_mp3(audio_data, sample_rate, output_path, params)
            
        else:
            # Autres formats via soundfile
            sf.write(output_path, audio_data, sample_rate)
    
    def _save_mp3(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        output_path: str,
        params: Dict[str, Any]
    ) -> None:
        """
Sauvegarde spécialisée MP3"""
        
        bitrate = params.get('bitrate', 192)
        
        # Conversion en format PyDub
        audio_int = (audio_data * 32767).astype(np.int16)
        audio_segment = AudioSegment(
            audio_int.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1 if audio_data.ndim == 1 else audio_data.shape[0]
        )
        
        # Export MP3
        audio_segment.export(
            output_path,
            format='mp3',
            bitrate=f'{bitrate}k'
        )
    
    def _generate_output_path(self, input_path: str, config: 'TransformationConfig') -> str:
        """
Génère le chemin de sortie automatiquement"""
        
        input_path_obj = Path(input_path)
        output_format = config.output_format or input_path_obj.suffix.lstrip('.')
        
        # Nom de fichier avec suffixe de transformation
        transform_suffix = config.type.value.replace('audio_', '')
        new_name = f"{input_path_obj.stem}_{transform_suffix}.{output_format}"
        
        return str(input_path_obj.parent / new_name)
    
    def _calculate_quality_metrics(
        self,
        original: AudioMetadata,
        processed: AudioMetadata
    ) -> AudioQualityMetrics:
        """Calcule les métriques de qualité de la transformation"""
        
        # Comparaison des niveaux
        loudness_change = processed.loudness_lufs - original.loudness_lufs
        dynamic_range_change = processed.dynamic_range - original.dynamic_range
        
        # Métriques de fidélité spectrale
        spectral_similarity = 1.0 - abs(
            (processed.spectral_centroid - original.spectral_centroid) / 
            (original.spectral_centroid + 1e-10)
        )
        
        # Score de qualité globale
        quality_score = (spectral_similarity + 
                        (1.0 - abs(loudness_change) / 20.0) +
                        (1.0 - abs(dynamic_range_change) / 10.0)) / 3.0
        
        return AudioQualityMetrics(
            snr_db=None,  # Nécessiterait signal de référence
            thd_percent=None,  # Calcul complexe
            frequency_response_flatness=spectral_similarity,
            dynamic_range_db=processed.dynamic_range,
            loudness_lufs=processed.loudness_lufs,
            quality_score=max(0.0, min(1.0, quality_score)),
            artifacts_detected=[],
            processing_artifacts_score=0.95  # Estimation par défaut
        )

class AsyncAudioTransformer:
    """
Version asynchrone du transformateur audio"""
    
    def __init__(self):
        self.sync_transformer = AudioTransformer()
        self.logger = logging.getLogger(__name__)
    
    async def transform_async(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """
Transformation audio asynchrone"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.sync_transformer.transform,
            input_path,
            config,
            output_path
        )
    
    async def transform_batch_async(
        self,
        inputs: List[Tuple[str, 'TransformationConfig']],
        max_concurrent: int = 4
    ) -> List['TransformationResult']:
        """
Transformation en lot asynchrone"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def transform_single(input_config_tuple):
            async with semaphore:
                input_path, config = input_config_tuple
                return await self.transform_async(input_path, config)
        
        tasks = [transform_single(item) for item in inputs]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Export des classes
__all__ = [
    'AudioTransformer',
    'AsyncAudioTransformer',
    'AudioAnalyzer',
    'AudioEnhancer',
    'AudioFormat',
    'AudioQuality',
    'NormalizationType',
    'AudioProcessingResult'
]
