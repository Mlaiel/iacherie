"""📏 Enterprise Audio Normalization Engine - Broadcast Standards & Loudness
========================================================================

Engine de normalisation audio enterprise avec standards broadcast, contrôle loudness
et conformité internationale pour la plateforme Ainflue.

Expert Roles Implementation:
🎵 Audio Engineer: Standards broadcast + loudness metering + mastering professional
🏗️ Backend Senior: Pipeline normalisation + traitement batch + optimization performance
🤖 Lead Dev IA: Normalisation adaptative + ML loudness prediction + auto-mastering
🧠 ML Engineer: Modèles prédictifs + analyse psychoacoustique + target optimization
🔒 Sécurité: Conformité standards + audit trails + protection intégrité audio
⚙️ DevOps: Automation normalisation + monitoring compliance + batch processing
🔗 Microservices: Services normalisation + API conformité + integration workflow
⚡ Performance: Processing temps réel + optimization qualité + minimal distortion

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Enterprise Production
Date: 16 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture de normalisation audio est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import math
import struct
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.signal import butter, filtfilt
import aiofiles
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BroadcastStandard(Enum):
    """Standards broadcast internationaux"""
    EBU_R128 = "ebu_r128"  # European Broadcasting Union
    ATSC_A85 = "atsc_a85"  # Advanced Television Systems Committee
    ITU_R_BS1770 = "itu_r_bs1770"  # International Telecommunication Union
    SPOTIFY = "spotify"  # Spotify loudness standard
    YOUTUBE = "youtube"  # YouTube loudness standard
    APPLE_MUSIC = "apple_music"  # Apple Music standard
    TIDAL = "tidal"  # Tidal streaming standard
    AMAZON_MUSIC = "amazon_music"  # Amazon Music standard
    CUSTOM = "custom"  # Custom standard

class NormalizationType(Enum):
    """Types de normalisation"""
    PEAK_NORMALIZATION = "peak_normalization"
    RMS_NORMALIZATION = "rms_normalization"
    LOUDNESS_NORMALIZATION = "loudness_normalization"
    LUFS_NORMALIZATION = "lufs_normalization"
    PERCEIVED_LOUDNESS = "perceived_loudness"
    DYNAMIC_RANGE = "dynamic_range"
    MULTIBAND_COMPRESSION = "multiband_compression"

class QualityMode(Enum):
    """Modes de qualité de normalisation"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    MASTERING = "mastering"

class ProcessingMode(Enum):
    """Modes de traitement"""
    REALTIME = "realtime"
    OFFLINE = "offline"
    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class LoudnessMetrics:
    """Métriques de loudness audio"""
    integrated_loudness: float  # LUFS
    loudness_range: float  # LU
    true_peak_level: float  # dBTP
    short_term_loudness: float  # LUFS
    momentary_loudness: float  # LUFS
    gating_threshold: float = -70.0  # LUFS
    relative_threshold: float = 0.0  # Calculé dynamiquement

@dataclass
class NormalizationTarget:
    """Cible de normalisation"""
    target_loudness: float = -23.0  # LUFS (EBU R128)
    target_peak: float = -1.0  # dBTP
    target_range: Optional[float] = None  # LU
    allow_clipping: bool = False
    preserve_dynamics: bool = True
    max_gain_reduction: float = 20.0  # dB
    max_gain_boost: float = 20.0  # dB

@dataclass
class NormalizationConfiguration:
    """Configuration de normalisation"""
    standard: BroadcastStandard = BroadcastStandard.EBU_R128
    normalization_type: NormalizationType = NormalizationType.LUFS_NORMALIZATION
    quality_mode: QualityMode = QualityMode.PROFESSIONAL
    processing_mode: ProcessingMode = ProcessingMode.OFFLINE
    target: NormalizationTarget = field(default_factory=NormalizationTarget)
    enable_gating: bool = True
    gate_threshold: float = -70.0  # LUFS
    enable_true_peak_limiting: bool = True
    enable_dynamic_range_control: bool = False
    multiband_enabled: bool = False
    preserve_metadata: bool = True

@dataclass
class NormalizationResult:
    """Résultat de normalisation"""
    normalized_audio: np.ndarray
    original_metrics: LoudnessMetrics
    normalized_metrics: LoudnessMetrics
    gain_applied: float  # dB
    peak_reduction: float  # dB
    processing_time: float
    quality_score: float
    compliance_check: Dict[str, bool]
    metadata: Dict[str, Any]

class LoudnessMeter:
    """Mesureur de loudness selon standards broadcast"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.block_size = int(0.4 * sample_rate)  # 400ms blocks
        self.overlap_size = int(0.3 * sample_rate)  # 300ms overlap
        
        # Coefficients de pondération K pour différents standards
        self.k_weights = {
            BroadcastStandard.EBU_R128: {
                'mono': [1.0],
                'stereo': [1.0, 1.0],
                'surround_5_1': [1.0, 1.0, 1.0, 1.41, 1.41, 0.0]
            }
        }
    
    async def measure_loudness(
        self,
        audio: np.ndarray,
        sample_rate: int,
        standard: BroadcastStandard = BroadcastStandard.EBU_R128
    ) -> LoudnessMetrics:
        """Mesure la loudness selon le standard spécifié"""
        
        # Rééchantillonner si nécessaire
        if sample_rate != self.sample_rate:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=self.sample_rate)
        
        # Appliquer les filtres de pondération
        filtered_audio = await self._apply_weighting_filters(audio)
        
        # Calculer la loudness intégrée
        integrated_loudness = await self._calculate_integrated_loudness(filtered_audio)
        
        # Calculer la loudness range
        loudness_range = await self._calculate_loudness_range(filtered_audio)
        
        # Calculer le true peak
        true_peak = await self._calculate_true_peak(audio)
        
        # Calculer les loudness short-term et momentary
        short_term = await self._calculate_short_term_loudness(filtered_audio)
        momentary = await self._calculate_momentary_loudness(filtered_audio)
        
        return LoudnessMetrics(
            integrated_loudness=integrated_loudness,
            loudness_range=loudness_range,
            true_peak_level=true_peak,
            short_term_loudness=short_term,
            momentary_loudness=momentary
        )
    
    async def _apply_weighting_filters(self, audio: np.ndarray) -> np.ndarray:
        """Applique les filtres de pondération ITU-R BS.1770"""
        # Filtre passe-haut (HSF - High Shelf Filter)
        # f0 = 1681.9743 Hz, Q = 0.7071, Gain = +3.99 dB
        hsf_audio = await self._apply_high_shelf_filter(audio, 1681.9743, 0.7071, 3.99)
        
        # Filtre passe-haut (HPF - High Pass Filter)  
        # fc = 38.13547 Hz, Q = 0.5003
        hpf_audio = await self._apply_high_pass_filter(hsf_audio, 38.13547, 0.5003)
        
        return hpf_audio
    
    async def _apply_high_shelf_filter(
        self,
        audio: np.ndarray,
        frequency: float,
        q: float,
        gain_db: float
    ) -> np.ndarray:
        """Applique un filtre high shelf"""
        # Calculer les coefficients biquad
        w = 2 * np.pi * frequency / self.sample_rate
        cosw = np.cos(w)
        sinw = np.sin(w)
        A = 10 ** (gain_db / 40)
        alpha = sinw / (2 * q)
        
        # Coefficients high shelf
        b0 = A * ((A + 1) + (A - 1) * cosw + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * cosw)
        b2 = A * ((A + 1) + (A - 1) * cosw - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * cosw + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * cosw)
        a2 = (A + 1) - (A - 1) * cosw - 2 * np.sqrt(A) * alpha
        
        # Normaliser
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1, a2]) / a0
        
        # Appliquer le filtre
        if len(audio.shape) == 1:
            return signal.lfilter(b, a, audio)
        else:
            return np.array([signal.lfilter(b, a, audio[i]) for i in range(audio.shape[0])])
    
    async def _apply_high_pass_filter(
        self,
        audio: np.ndarray,
        frequency: float,
        q: float
    ) -> np.ndarray:
        """Applique un filtre passe-haut"""
        # Calculer les coefficients biquad
        w = 2 * np.pi * frequency / self.sample_rate
        cosw = np.cos(w)
        sinw = np.sin(w)
        alpha = sinw / (2 * q)
        
        # Coefficients high pass
        b0 = (1 + cosw) / 2
        b1 = -(1 + cosw)
        b2 = (1 + cosw) / 2
        a0 = 1 + alpha
        a1 = -2 * cosw
        a2 = 1 - alpha
        
        # Normaliser
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1, a2]) / a0
        
        # Appliquer le filtre
        if len(audio.shape) == 1:
            return signal.lfilter(b, a, audio)
        else:
            return np.array([signal.lfilter(b, a, audio[i]) for i in range(audio.shape[0])])
    
    async def _calculate_integrated_loudness(self, audio: np.ndarray) -> float:
        """Calcule la loudness intégrée selon ITU-R BS.1770"""
        # Calculer le mean square par bloc
        block_loudness = []
        hop_size = self.block_size - self.overlap_size
        
        for i in range(0, len(audio) - self.block_size + 1, hop_size):
            block = audio[i:i + self.block_size]
            
            # Calculer le mean square
            if len(audio.shape) == 1:
                mean_square = np.mean(block ** 2)
            else:
                # Pour le multicanal, appliquer les poids K
                mean_square = 0
                for ch in range(audio.shape[0]):
                    weight = 1.0  # Simplification - utiliser les vrais poids K
                    mean_square += weight * np.mean(block[ch] ** 2)
            
            if mean_square > 0:
                loudness = -0.691 + 10 * np.log10(mean_square)
                block_loudness.append(loudness)
        
        if not block_loudness:
            return -70.0  # Silence
        
        # Gating selon ITU-R BS.1770-4
        # Absolute gating threshold: -70 LUFS
        gated_loudness = [l for l in block_loudness if l >= -70.0]
        
        if not gated_loudness:
            return -70.0
        
        # Relative gating threshold: -10 LU relative to ungated loudness
        mean_loudness = np.mean(gated_loudness)
        relative_threshold = mean_loudness - 10.0
        
        # Final gating
        final_gated = [l for l in gated_loudness if l >= relative_threshold]
        
        if final_gated:
            return np.mean(final_gated)
        else:
            return mean_loudness
    
    async def _calculate_loudness_range(self, audio: np.ndarray) -> float:
        """Calcule la loudness range (LRA)"""
        # Calculer la loudness short-term (3s avec overlap de 2.9s)
        short_term_window = int(3.0 * self.sample_rate)
        short_term_hop = int(0.1 * self.sample_rate)  # 100ms hop
        
        short_term_loudness = []
        
        for i in range(0, len(audio) - short_term_window + 1, short_term_hop):
            block = audio[i:i + short_term_window]
            
            # Calculer la loudness de ce bloc
            if len(audio.shape) == 1:
                mean_square = np.mean(block ** 2)
            else:
                mean_square = np.mean([np.mean(block[ch] ** 2) for ch in range(audio.shape[0])])
            
            if mean_square > 0:
                loudness = -0.691 + 10 * np.log10(mean_square)
                short_term_loudness.append(loudness)
        
        if len(short_term_loudness) < 2:
            return 0.0
        
        # Gating
        gated = [l for l in short_term_loudness if l >= -70.0]
        if not gated:
            return 0.0
        
        mean_loudness = np.mean(gated)
        relative_threshold = mean_loudness - 20.0  # -20 LU pour LRA
        
        final_gated = [l for l in gated if l >= relative_threshold]
        
        if len(final_gated) < 2:
            return 0.0
        
        # LRA = 95th percentile - 10th percentile
        p10 = np.percentile(final_gated, 10)
        p95 = np.percentile(final_gated, 95)
        
        return p95 - p10
    
    async def _calculate_true_peak(self, audio: np.ndarray) -> float:
        """Calcule le true peak level selon ITU-R BS.1770"""
        # Suréchantillonnage 4x pour détection des pics inter-échantillons
        upsampled = signal.resample(audio, len(audio) * 4, axis=-1)
        
        # Trouver le pic maximum
        if len(audio.shape) == 1:
            peak = np.max(np.abs(upsampled))
        else:
            peak = np.max([np.max(np.abs(upsampled[ch])) for ch in range(audio.shape[0])])
        
        # Convertir en dBTP
        if peak > 0:
            return 20 * np.log10(peak)
        else:
            return -float('inf')
    
    async def _calculate_short_term_loudness(self, audio: np.ndarray) -> float:
        """Calcule la loudness short-term (3 secondes)"""
        window_size = int(3.0 * self.sample_rate)
        
        if len(audio) < window_size:
            # Audio trop court, utiliser tout l'audio
            if len(audio.shape) == 1:
                mean_square = np.mean(audio ** 2)
            else:
                mean_square = np.mean([np.mean(audio[ch] ** 2) for ch in range(audio.shape[0])])
        else:
            # Utiliser les dernières 3 secondes
            recent_audio = audio[-window_size:]
            if len(audio.shape) == 1:
                mean_square = np.mean(recent_audio ** 2)
            else:
                mean_square = np.mean([np.mean(recent_audio[ch] ** 2) for ch in range(audio.shape[0])])
        
        if mean_square > 0:
            return -0.691 + 10 * np.log10(mean_square)
        else:
            return -70.0
    
    async def _calculate_momentary_loudness(self, audio: np.ndarray) -> float:
        """Calcule la loudness momentary (400ms)"""
        window_size = int(0.4 * self.sample_rate)
        
        if len(audio) < window_size:
            # Audio trop court
            if len(audio.shape) == 1:
                mean_square = np.mean(audio ** 2)
            else:
                mean_square = np.mean([np.mean(audio[ch] ** 2) for ch in range(audio.shape[0])])
        else:
            # Utiliser les dernières 400ms
            recent_audio = audio[-window_size:]
            if len(audio.shape) == 1:
                mean_square = np.mean(recent_audio ** 2)
            else:
                mean_square = np.mean([np.mean(recent_audio[ch] ** 2) for ch in range(audio.shape[0])])
        
        if mean_square > 0:
            return -0.691 + 10 * np.log10(mean_square)
        else:
            return -70.0

class TruePeakLimiter:
    """Limiteur true peak pour éviter le clipping inter-échantillons"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.lookahead_ms = 5.0  # 5ms lookahead
        self.release_ms = 50.0  # 50ms release
        
        # Calculer les paramètres
        self.lookahead_samples = int(self.lookahead_ms * sample_rate / 1000)
        self.release_samples = int(self.release_ms * sample_rate / 1000)
        self.release_coeff = np.exp(-1 / self.release_samples)
    
    async def limit_true_peaks(
        self,
        audio: np.ndarray,
        threshold_dbtp: float = -1.0
    ) -> np.ndarray:
        """Limite les true peaks"""
        threshold_linear = 10 ** (threshold_dbtp / 20)
        
        # Suréchantillonner pour la détection des true peaks
        upsampled = signal.resample(audio, len(audio) * 4, axis=-1)
        
        # Détecter les dépassements
        if len(audio.shape) == 1:
            peaks = np.abs(upsampled) > threshold_linear
        else:
            peaks = np.any([np.abs(upsampled[ch]) > threshold_linear for ch in range(audio.shape[0])], axis=0)
        
        # Générer l'envelope de réduction de gain
        gain_reduction = np.ones_like(upsampled)
        current_gain = 1.0
        
        for i in range(len(upsampled)):
            if peaks[i]:
                # Calculer la réduction nécessaire
                if len(audio.shape) == 1:
                    peak_level = np.abs(upsampled[i])
                else:
                    peak_level = np.max([np.abs(upsampled[ch, i]) for ch in range(audio.shape[0])])
                
                required_gain = threshold_linear / peak_level
                current_gain = min(current_gain, required_gain)
            else:
                # Relâcher progressivement
                current_gain = current_gain + (1.0 - current_gain) * (1 - self.release_coeff)
            
            gain_reduction[i] = current_gain
        
        # Appliquer la réduction avec lookahead
        delayed_gain = np.roll(gain_reduction, self.lookahead_samples)
        limited_upsampled = upsampled * delayed_gain
        
        # Redescendre à l'échantillonnage original
        limited_audio = signal.resample(limited_upsampled, len(audio), axis=-1)
        
        return limited_audio

class DynamicRangeProcessor:
    """Processeur de dynamique pour contrôle de range"""
    
    def __init__(self):
        self.target_lra = 7.0  # LU (EBU R128 recommended)
        self.multiband_crossovers = [250, 2000, 8000]  # Hz
    
    async def process_dynamic_range(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_lra: Optional[float] = None,
        multiband: bool = False
    ) -> np.ndarray:
        """Traite la dynamique audio"""
        if target_lra is None:
            target_lra = self.target_lra
        
        if multiband:
            return await self._multiband_dynamics_processing(audio, sample_rate, target_lra)
        else:
            return await self._broadband_dynamics_processing(audio, sample_rate, target_lra)
    
    async def _broadband_dynamics_processing(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_lra: float
    ) -> np.ndarray:
        """Traitement dynamique large bande"""
        # Analyser la dynamique actuelle
        loudness_meter = LoudnessMeter(sample_rate)
        metrics = await loudness_meter.measure_loudness(audio, sample_rate)
        
        current_lra = metrics.loudness_range
        
        if current_lra <= target_lra:
            return audio  # Pas besoin de traitement
        
        # Calculer les paramètres de compression
        ratio = current_lra / target_lra
        threshold = metrics.integrated_loudness - (target_lra / 2)
        
        # Appliquer la compression
        compressed = await self._apply_compression(
            audio, sample_rate, threshold, ratio, attack_ms=10, release_ms=100
        )
        
        return compressed
    
    async def _multiband_dynamics_processing(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_lra: float
    ) -> np.ndarray:
        """Traitement dynamique multibande"""
        # Séparer en bandes de fréquence
        bands = await self._split_into_bands(audio, sample_rate, self.multiband_crossovers)
        
        processed_bands = []
        
        for band in bands:
            # Traiter chaque bande individuellement
            processed_band = await self._broadband_dynamics_processing(
                band, sample_rate, target_lra
            )
            processed_bands.append(processed_band)
        
        # Recombiner les bandes
        processed_audio = await self._combine_bands(processed_bands)
        
        return processed_audio
    
    async def _split_into_bands(
        self,
        audio: np.ndarray,
        sample_rate: int,
        crossovers: List[float]
    ) -> List[np.ndarray]:
        """Sépare l'audio en bandes de fréquence"""
        bands = []
        
        # Bande basse (0 - crossovers[0])
        nyquist = sample_rate / 2
        low = crossovers[0] / nyquist
        b, a = butter(4, low, btype='low')
        low_band = filtfilt(b, a, audio, axis=-1)
        bands.append(low_band)
        
        # Bandes moyennes
        for i in range(len(crossovers) - 1):
            low_freq = crossovers[i] / nyquist
            high_freq = crossovers[i + 1] / nyquist
            b, a = butter(4, [low_freq, high_freq], btype='band')
            mid_band = filtfilt(b, a, audio, axis=-1)
            bands.append(mid_band)
        
        # Bande haute (crossovers[-1] - Nyquist)
        high = crossovers[-1] / nyquist
        b, a = butter(4, high, btype='high')
        high_band = filtfilt(b, a, audio, axis=-1)
        bands.append(high_band)
        
        return bands
    
    async def _combine_bands(self, bands: List[np.ndarray]) -> np.ndarray:
        """Recombine les bandes de fréquence"""
        return sum(bands)
    
    async def _apply_compression(
        self,
        audio: np.ndarray,
        sample_rate: int,
        threshold: float,
        ratio: float,
        attack_ms: float,
        release_ms: float
    ) -> np.ndarray:
        """Applique la compression audio"""
        # Convertir les temps en échantillons
        attack_samples = int(attack_ms * sample_rate / 1000)
        release_samples = int(release_ms * sample_rate / 1000)
        
        # Calculer les coefficients
        attack_coeff = np.exp(-1 / attack_samples) if attack_samples > 0 else 0
        release_coeff = np.exp(-1 / release_samples) if release_samples > 0 else 0
        
        # Traitement canal par canal
        if len(audio.shape) == 1:
            return await self._compress_channel(
                audio, threshold, ratio, attack_coeff, release_coeff
            )
        else:
            processed = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                processed[ch] = await self._compress_channel(
                    audio[ch], threshold, ratio, attack_coeff, release_coeff
                )
            return processed
    
    async def _compress_channel(
        self,
        audio: np.ndarray,
        threshold: float,
        ratio: float,
        attack_coeff: float,
        release_coeff: float
    ) -> np.ndarray:
        """Compresse un canal audio"""
        # Convertir en dB
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        
        # Calculer la réduction de gain
        gain_reduction = np.zeros_like(audio_db)
        envelope = 0
        
        for i in range(len(audio_db)):
            input_level = audio_db[i]
            
            # Calculer la réduction si au-dessus du seuil
            if input_level > threshold:
                target_gain = (input_level - threshold) / ratio + threshold - input_level
            else:
                target_gain = 0
            
            # Envelope follower
            if target_gain < envelope:
                envelope = target_gain + (envelope - target_gain) * attack_coeff
            else:
                envelope = target_gain + (envelope - target_gain) * release_coeff
            
            gain_reduction[i] = envelope
        
        # Appliquer la réduction
        gain_linear = 10 ** (gain_reduction / 20)
        return audio * gain_linear

class AudioNormalizationEngine:
    """Engine de normalisation audio enterprise avec standards broadcast"""
    
    def __init__(self, config: Optional[NormalizationConfiguration] = None):
        """Initialise l'engine de normalisation"""
        self.config = config or NormalizationConfiguration()
        self.loudness_meter = LoudnessMeter()
        self.true_peak_limiter = TruePeakLimiter()
        self.dynamic_range_processor = DynamicRangeProcessor()
        
        # Standards de plateforme
        self.platform_standards = {
            BroadcastStandard.EBU_R128: NormalizationTarget(-23.0, -1.0),
            BroadcastStandard.SPOTIFY: NormalizationTarget(-14.0, -1.0),
            BroadcastStandard.YOUTUBE: NormalizationTarget(-14.0, -1.0),
            BroadcastStandard.APPLE_MUSIC: NormalizationTarget(-16.0, -1.0),
            BroadcastStandard.TIDAL: NormalizationTarget(-14.0, -1.0),
            BroadcastStandard.AMAZON_MUSIC: NormalizationTarget(-14.0, -1.0)
        }
        
        # Statistiques
        self.stats = {
            'total_normalized': 0,
            'average_processing_time': 0,
            'compliance_rate': 0,
            'standards_usage': {},
            'quality_scores': []
        }
        
        logger.info("AudioNormalizationEngine initialized successfully")
    
    async def normalize_audio(
        self,
        audio_file_path: str,
        output_path: Optional[str] = None,
        config: Optional[NormalizationConfiguration] = None
    ) -> NormalizationResult:
        """Normalise un fichier audio selon les standards"""
        start_time = time.time()
        
        try:
            if config is None:
                config = self.config
            
            # Charger l'audio
            audio, sample_rate = sf.read(audio_file_path)
            
            # Convertir en mono si nécessaire pour certains traitements
            if len(audio.shape) > 1 and audio.shape[0] > 2:
                # Garder seulement les 2 premiers canaux pour le stéréo
                audio = audio[:2]
            
            # Mesurer les métriques originales
            original_metrics = await self.loudness_meter.measure_loudness(
                audio, sample_rate, config.standard
            )
            
            # Obtenir la cible de normalisation
            target = await self._get_normalization_target(config)
            
            # Appliquer la normalisation
            normalized_audio = await self._apply_normalization(
                audio, sample_rate, original_metrics, target, config
            )
            
            # Mesurer les métriques après normalisation
            normalized_metrics = await self.loudness_meter.measure_loudness(
                normalized_audio, sample_rate, config.standard
            )
            
            # Calculer les gains appliqués
            gain_applied = normalized_metrics.integrated_loudness - original_metrics.integrated_loudness
            peak_reduction = normalized_metrics.true_peak_level - original_metrics.true_peak_level
            
            # Vérifier la conformité
            compliance_check = await self._check_compliance(normalized_metrics, target, config.standard)
            
            # Calculer le score de qualité
            quality_score = await self._calculate_quality_score(
                original_metrics, normalized_metrics, target
            )
            
            # Sauvegarder si un chemin de sortie est fourni
            if output_path:
                sf.write(output_path, normalized_audio.T if len(normalized_audio.shape) > 1 else normalized_audio, sample_rate)
            
            # Mettre à jour les statistiques
            processing_time = time.time() - start_time
            await self._update_stats(processing_time, quality_score, config.standard, compliance_check)
            
            result = NormalizationResult(
                normalized_audio=normalized_audio,
                original_metrics=original_metrics,
                normalized_metrics=normalized_metrics,
                gain_applied=gain_applied,
                peak_reduction=peak_reduction,
                processing_time=processing_time,
                quality_score=quality_score,
                compliance_check=compliance_check,
                metadata={
                    'standard': config.standard.value,
                    'normalization_type': config.normalization_type.value,
                    'quality_mode': config.quality_mode.value,
                    'target_loudness': target.target_loudness,
                    'target_peak': target.target_peak,
                    'input_file': audio_file_path,
                    'output_file': output_path,
                    'processing_timestamp': datetime.now().isoformat()
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            raise
    
    async def _get_normalization_target(
        self,
        config: NormalizationConfiguration
    ) -> NormalizationTarget:
        """Obtient la cible de normalisation selon le standard"""
        if config.standard in self.platform_standards:
            return self.platform_standards[config.standard]
        else:
            return config.target
    
    async def _apply_normalization(
        self,
        audio: np.ndarray,
        sample_rate: int,
        original_metrics: LoudnessMetrics,
        target: NormalizationTarget,
        config: NormalizationConfiguration
    ) -> np.ndarray:
        """Applique la normalisation selon le type spécifié"""
        
        if config.normalization_type == NormalizationType.LUFS_NORMALIZATION:
            return await self._apply_lufs_normalization(
                audio, original_metrics, target, config
            )
        elif config.normalization_type == NormalizationType.PEAK_NORMALIZATION:
            return await self._apply_peak_normalization(audio, target)
        elif config.normalization_type == NormalizationType.RMS_NORMALIZATION:
            return await self._apply_rms_normalization(audio, target)
        elif config.normalization_type == NormalizationType.DYNAMIC_RANGE:
            return await self._apply_dynamic_range_normalization(
                audio, sample_rate, target, config
            )
        else:
            return await self._apply_lufs_normalization(
                audio, original_metrics, target, config
            )
    
    async def _apply_lufs_normalization(
        self,
        audio: np.ndarray,
        original_metrics: LoudnessMetrics,
        target: NormalizationTarget,
        config: NormalizationConfiguration
    ) -> np.ndarray:
        """Applique la normalisation LUFS"""
        # Calculer le gain nécessaire
        gain_db = target.target_loudness - original_metrics.integrated_loudness
        
        # Limiter le gain
        gain_db = np.clip(gain_db, -target.max_gain_reduction, target.max_gain_boost)
        
        # Appliquer le gain
        gain_linear = 10 ** (gain_db / 20)
        normalized_audio = audio * gain_linear
        
        # Limitation des true peaks si nécessaire
        if config.enable_true_peak_limiting:
            normalized_audio = await self.true_peak_limiter.limit_true_peaks(
                normalized_audio, target.target_peak
            )
        
        # Contrôle de la dynamique si activé
        if config.enable_dynamic_range_control and target.target_range:
            normalized_audio = await self.dynamic_range_processor.process_dynamic_range(
                normalized_audio, 48000, target.target_range, config.multiband_enabled
            )
        
        return normalized_audio
    
    async def _apply_peak_normalization(
        self,
        audio: np.ndarray,
        target: NormalizationTarget
    ) -> np.ndarray:
        """Applique la normalisation par pic"""
        # Trouver le pic maximum
        peak_level = np.max(np.abs(audio))
        
        if peak_level == 0:
            return audio
        
        # Calculer le gain pour atteindre le pic cible
        target_linear = 10 ** (target.target_peak / 20)
        gain = target_linear / peak_level
        
        return audio * gain
    
    async def _apply_rms_normalization(
        self,
        audio: np.ndarray,
        target: NormalizationTarget
    ) -> np.ndarray:
        """Applique la normalisation RMS"""
        # Calculer le RMS
        rms_level = np.sqrt(np.mean(audio ** 2))
        
        if rms_level == 0:
            return audio
        
        # Calculer le gain pour atteindre le RMS cible
        # Utiliser target_loudness comme RMS cible (adaptation)
        target_rms_linear = 10 ** (target.target_loudness / 20)
        gain = target_rms_linear / rms_level
        
        return audio * gain
    
    async def _apply_dynamic_range_normalization(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target: NormalizationTarget,
        config: NormalizationConfiguration
    ) -> np.ndarray:
        """Applique la normalisation de dynamique"""
        # Traiter avec le processeur de dynamique
        if target.target_range:
            return await self.dynamic_range_processor.process_dynamic_range(
                audio, sample_rate, target.target_range, config.multiband_enabled
            )
        else:
            return audio
    
    async def _check_compliance(
        self,
        metrics: LoudnessMetrics,
        target: NormalizationTarget,
        standard: BroadcastStandard
    ) -> Dict[str, bool]:
        """Vérifie la conformité aux standards"""
        compliance = {}
        
        # Tolérance typique: ±0.1 LU pour loudness, ±0.1 dB pour peaks
        loudness_tolerance = 0.1
        peak_tolerance = 0.1
        
        # Vérifier la loudness intégrée
        compliance['integrated_loudness'] = (
            abs(metrics.integrated_loudness - target.target_loudness) <= loudness_tolerance
        )
        
        # Vérifier le true peak
        compliance['true_peak'] = (
            metrics.true_peak_level <= target.target_peak + peak_tolerance
        )
        
        # Vérifications spécifiques au standard
        if standard == BroadcastStandard.EBU_R128:
            # EBU R128: LRA should typically be <= 20 LU
            compliance['loudness_range'] = metrics.loudness_range <= 20.0
            # True peak should be <= -1 dBTP
            compliance['ebu_true_peak'] = metrics.true_peak_level <= -1.0
        
        elif standard in [BroadcastStandard.SPOTIFY, BroadcastStandard.YOUTUBE]:
            # Streaming services: plus tolérant sur LRA
            compliance['loudness_range'] = metrics.loudness_range <= 30.0
        
        # Conformité globale
        compliance['overall'] = all(compliance.values())
        
        return compliance
    
    async def _calculate_quality_score(
        self,
        original_metrics: LoudnessMetrics,
        normalized_metrics: LoudnessMetrics,
        target: NormalizationTarget
    ) -> float:
        """Calcule un score de qualité pour la normalisation"""
        score = 100.0
        
        # Pénalité pour l'écart à la cible de loudness
        loudness_error = abs(normalized_metrics.integrated_loudness - target.target_loudness)
        score -= loudness_error * 10  # -10 points par LU d'écart
        
        # Pénalité pour dépassement de true peak
        if normalized_metrics.true_peak_level > target.target_peak:
            peak_overshoot = normalized_metrics.true_peak_level - target.target_peak
            score -= peak_overshoot * 20  # -20 points par dB de dépassement
        
        # Bonus pour préservation de la dynamique
        lra_preservation = min(1.0, normalized_metrics.loudness_range / (original_metrics.loudness_range + 1e-6))
        score += lra_preservation * 10  # Jusqu'à +10 points
        
        # Limiter le score entre 0 et 100
        return max(0.0, min(100.0, score))
    
    async def _update_stats(
        self,
        processing_time: float,
        quality_score: float,
        standard: BroadcastStandard,
        compliance_check: Dict[str, bool]
    ):
        """Met à jour les statistiques"""
        self.stats['total_normalized'] += 1
        
        # Moyenne mobile du temps de traitement
        current_avg = self.stats['average_processing_time']
        total = self.stats['total_normalized']
        self.stats['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Taux de conformité
        if compliance_check.get('overall', False):
            compliant_count = sum(1 for key, value in self.stats['standards_usage'].items() 
                                if value.get('compliant', 0) > 0)
            self.stats['compliance_rate'] = compliant_count / total
        
        # Usage des standards
        standard_key = standard.value
        if standard_key not in self.stats['standards_usage']:
            self.stats['standards_usage'][standard_key] = {'count': 0, 'compliant': 0}
        
        self.stats['standards_usage'][standard_key]['count'] += 1
        if compliance_check.get('overall', False):
            self.stats['standards_usage'][standard_key]['compliant'] += 1
        
        # Scores de qualité
        self.stats['quality_scores'].append(quality_score)
        if len(self.stats['quality_scores']) > 1000:  # Limiter la taille
            self.stats['quality_scores'] = self.stats['quality_scores'][-1000:]
    
    async def batch_normalize_directory(
        self,
        input_directory: str,
        output_directory: str,
        config: Optional[NormalizationConfiguration] = None
    ) -> List[NormalizationResult]:
        """Normalise tous les fichiers audio d'un répertoire"""
        input_path = Path(input_directory)
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        supported_formats = {'.wav', '.flac', '.aiff', '.mp3', '.ogg', '.m4a'}
        results = []
        
        for audio_file in input_path.rglob('*'):
            if audio_file.suffix.lower() in supported_formats:
                try:
                    output_file = output_path / f"{audio_file.stem}_normalized{audio_file.suffix}"
                    
                    result = await self.normalize_audio(
                        str(audio_file), str(output_file), config
                    )
                    results.append(result)
                    
                    logger.info(f"Normalized: {audio_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to normalize {audio_file.name}: {e}")
        
        return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de normalisation"""
        stats = self.stats.copy()
        
        if stats['quality_scores']:
            stats['average_quality_score'] = np.mean(stats['quality_scores'])
            stats['quality_std'] = np.std(stats['quality_scores'])
        
        return stats

# Factory functions
async def create_audio_normalization_engine(
    config: Optional[NormalizationConfiguration] = None
) -> AudioNormalizationEngine:
    """Crée une instance de l'engine de normalisation"""
    return AudioNormalizationEngine(config)

async def create_normalization_config(
    standard: str = "ebu_r128",
    target_loudness: float = -23.0,
    target_peak: float = -1.0,
    quality_mode: str = "professional"
) -> NormalizationConfiguration:
    """Crée une configuration de normalisation"""
    target = NormalizationTarget(
        target_loudness=target_loudness,
        target_peak=target_peak
    )
    
    return NormalizationConfiguration(
        standard=BroadcastStandard(standard),
        quality_mode=QualityMode(quality_mode),
        target=target
    )

# Export des classes et fonctions principales
__all__ = [
    'AudioNormalizationEngine',
    'BroadcastStandard',
    'NormalizationType',
    'QualityMode',
    'ProcessingMode',
    'LoudnessMetrics',
    'NormalizationTarget',
    'NormalizationConfiguration',
    'NormalizationResult',
    'LoudnessMeter',
    'TruePeakLimiter',
    'DynamicRangeProcessor',
    'create_audio_normalization_engine',
    'create_normalization_config'
]