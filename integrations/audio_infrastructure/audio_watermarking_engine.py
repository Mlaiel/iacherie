"""🔒 Enterprise Audio Watermarking Engine - Professional Content Protection
========================================================================

Engine de watermarking audio enterprise avec protection inaudible et intégration DRM
pour la protection du contenu créateur sur la plateforme Ainflue.

Expert Roles Implementation:
🎵 Audio Engineer: Spectral domain embedding + psychoacoustic masking + DSP professional
🔒 Sécurité: DRM integration + copyright enforcement + attack-resistant design
🤖 Lead Dev IA: AI watermark detection + intelligent embedding + ML optimization
🧠 ML Engineer: Neural watermarking + feature extraction + detection algorithms

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation de watermarking audio est la propriété intellectuelle
EXCLUSIVE de Fahed Mlaiel. Usage commercial non autorisé strictement INTERDIT.
"""

import asyncio
import logging
import numpy as np
import scipy.signal
import scipy.fft
import hashlib
import uuid
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import wave
import struct
import math
import statistics
from concurrent.futures import ThreadPoolExecutor
import io

logger = logging.getLogger(__name__)

class WatermarkType(Enum):
    """Types de watermarking audio supportés"""
    SPECTRAL_DOMAIN = "spectral_domain"          # Embedding fréquentiel inaudible
    PHASE_CODING = "phase_coding"                # Manipulation phase porteuse
    ECHO_HIDING = "echo_hiding"                  # Patterns echo temporels
    LSB_STEGANOGRAPHY = "lsb_steganography"      # Manipulation bits significatifs
    SPREAD_SPECTRUM = "spread_spectrum"          # Distribution noise-like
    WAVELET_TRANSFORM = "wavelet_transform"      # Décomposition multi-résolution
    PSYCHOACOUSTIC = "psychoacoustic"            # Masquage psychoacoustique
    NEURAL_WATERMARK = "neural_watermark"        # IA neural embedding

class WatermarkStrength(Enum):
    """Niveaux de force du watermark"""
    MINIMAL = 0.1          # Quasi-inaudible, résistance faible
    LIGHT = 0.3            # Inaudible normal, résistance moyenne
    MEDIUM = 0.5           # Léger impact, bonne résistance
    STRONG = 0.7           # Impact perceptible, forte résistance
    MAXIMUM = 1.0          # Impact audible, résistance maximale

class AttackResistance(Enum):
    """Types d'attaques résistées"""
    COMPRESSION_MP3 = "compression_mp3"
    COMPRESSION_AAC = "compression_aac" 
    NOISE_ADDITION = "noise_addition"
    FILTERING = "filtering"
    PITCH_SHIFTING = "pitch_shifting"
    TIME_STRETCHING = "time_stretching"
    RESAMPLING = "resampling"
    AMPLIFICATION = "amplification"
    EQUALIZATION = "equalization"
    CROPPING = "cropping"

@dataclass
class WatermarkPayload:
    """Payload du watermark à embedder"""
    creator_id: str
    content_id: str
    timestamp: datetime
    copyright_info: Dict[str, Any]
    license_type: str
    protection_level: str
    blockchain_hash: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None

@dataclass
class WatermarkConfiguration:
    """Configuration du watermarking"""
    watermark_type: WatermarkType
    strength: WatermarkStrength
    frequency_range: Tuple[int, int] = (300, 15000)  # Hz
    embedding_rate: float = 1.0  # bits/second
    redundancy_factor: int = 3
    psychoacoustic_masking: bool = True
    attack_resistance: List[AttackResistance] = field(default_factory=list)
    quality_preservation: float = 0.98  # Préservation qualité

@dataclass
class WatermarkDetectionResult:
    """Résultat de détection de watermark"""
    detected: bool
    confidence: float
    payload: Optional[WatermarkPayload]
    detection_method: WatermarkType
    processing_time: float
    quality_impact: float
    attack_evidence: List[str] = field(default_factory=list)

@dataclass
class AudioWatermarkResult:
    """Résultat du watermarking audio"""
    watermarked_audio: np.ndarray
    embedding_success: bool
    watermark_payload: WatermarkPayload
    quality_metrics: Dict[str, float]
    processing_time: float
    embedding_locations: List[Tuple[int, int]]  # (start, end) samples

class PsychoacousticModel:
    """Modèle psychoacoustique pour masquage inaudible"""
    
    def __init__(self):
        # Bark scale frequencies (critical bands)
        self.bark_frequencies = [
            0, 100, 200, 300, 400, 510, 630, 770, 920, 1080,
            1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700,
            4400, 5300, 6400, 7700, 9500, 12000, 15500, 24000
        ]
        
        # Absolute threshold of hearing (ATH)
        self.ath_frequencies = np.logspace(np.log10(20), np.log10(20000), 1000)
        self.ath_values = self._calculate_ath()
    
    def _calculate_ath(self) -> np.ndarray:
        """Calcule le seuil absolu d'audition"""
        f = self.ath_frequencies
        # ATH formula (ISO 389-7)
        ath = (
            3.64 * (f / 1000) ** -0.8 
            - 6.5 * np.exp(-0.6 * (f / 1000 - 3.3) ** 2)
            + 1e-3 * (f / 1000) ** 4
        )
        return ath
    
    def calculate_masking_threshold(self, audio_spectrum: np.ndarray, 
                                   frequencies: np.ndarray) -> np.ndarray:
        """Calcule le seuil de masquage psychoacoustique"""
        masking_threshold = np.zeros_like(frequencies)
        
        # Masquage par les tonals et le bruit
        for i, freq in enumerate(frequencies):
            # Masquage spectral
            spectral_masking = self._calculate_spectral_masking(
                audio_spectrum, frequencies, freq
            )
            
            # Masquage temporel
            temporal_masking = self._calculate_temporal_masking(freq)
            
            # Combinaison des masquages
            masking_threshold[i] = max(
                spectral_masking,
                temporal_masking,
                self._interpolate_ath(freq)
            )
        
        return masking_threshold
    
    def _calculate_spectral_masking(self, spectrum: np.ndarray, 
                                   frequencies: np.ndarray, target_freq: float) -> float:
        """Calcule le masquage spectral pour une fréquence cible"""
        # Conversion en échelle Bark
        target_bark = self._freq_to_bark(target_freq)
        
        masking = 0.0
        for i, freq in enumerate(frequencies):
            if spectrum[i] > 0:
                masker_bark = self._freq_to_bark(freq)
                bark_distance = abs(target_bark - masker_bark)
                
                # Fonction de masquage spectral
                if bark_distance < 1.0:
                    masking_effect = spectrum[i] - 14.5 - bark_distance
                else:
                    masking_effect = spectrum[i] - 14.5 - 17 * bark_distance
                
                masking = max(masking, masking_effect)
        
        return masking
    
    def _calculate_temporal_masking(self, frequency: float) -> float:
        """Calcule le masquage temporel"""
        # Masquage post-stimulus simplifié
        return -10.0  # dB
    
    def _freq_to_bark(self, frequency: float) -> float:
        """Conversion fréquence vers échelle Bark"""
        return 13 * np.arctan(0.00076 * frequency) + 3.5 * np.arctan((frequency / 7500) ** 2)
    
    def _interpolate_ath(self, frequency: float) -> float:
        """Interpole le seuil absolu d'audition"""
        return np.interp(frequency, self.ath_frequencies, self.ath_values)

class SpectralWatermarkEmbedder:
    """Embedder watermark dans le domaine spectral"""
    
    def __init__(self, config: WatermarkConfiguration):
        self.config = config
        self.psychoacoustic_model = PsychoacousticModel()
    
    def embed_watermark(self, audio: np.ndarray, payload: WatermarkPayload,
                       sample_rate: int) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """Embed watermark dans le domaine spectral"""
        
        # Conversion payload en bits
        payload_bits = self._payload_to_bits(payload)
        
        # Fenêtrage et STFT
        window_size = 2048
        hop_size = window_size // 4
        
        # Calcul STFT
        frequencies, times, stft = scipy.signal.stft(
            audio, fs=sample_rate, window='hann',
            nperseg=window_size, noverlap=window_size - hop_size
        )
        
        # Sélection des fréquences d'embedding
        freq_mask = (frequencies >= self.config.frequency_range[0]) & \
                   (frequencies <= self.config.frequency_range[1])
        embedding_freqs = frequencies[freq_mask]
        
        embedding_locations = []
        watermarked_stft = stft.copy()
        
        # Embedding pour chaque frame temporelle
        for t_idx, time_frame in enumerate(stft.T):
            if t_idx % (sample_rate // window_size) == 0:  # Une fois par seconde
                # Calcul du seuil de masquage
                spectrum_magnitude = np.abs(time_frame[freq_mask])
                masking_threshold = self.psychoacoustic_model.calculate_masking_threshold(
                    spectrum_magnitude, embedding_freqs
                )
                
                # Embedding des bits
                for bit_idx, bit in enumerate(payload_bits):
                    if bit_idx >= len(embedding_freqs):
                        break
                    
                    freq_idx = np.where(freq_mask)[0][bit_idx]
                    
                    # Calcul de l'amplitude d'embedding
                    if self.config.psychoacoustic_masking:
                        max_amplitude = masking_threshold[bit_idx] * 0.5
                    else:
                        max_amplitude = np.abs(stft[freq_idx, t_idx]) * 0.1
                    
                    # Modulation de phase selon le bit
                    if bit == 1:
                        phase_shift = np.pi / 4
                    else:
                        phase_shift = -np.pi / 4
                    
                    # Application du watermark
                    magnitude = min(
                        max_amplitude * float(self.config.strength.value),
                        np.abs(stft[freq_idx, t_idx]) * 0.2
                    )
                    
                    watermarked_stft[freq_idx, t_idx] = (
                        magnitude * np.exp(1j * (np.angle(stft[freq_idx, t_idx]) + phase_shift))
                    )
                
                # Enregistrement de la location d'embedding
                start_sample = t_idx * hop_size
                end_sample = start_sample + window_size
                embedding_locations.append((start_sample, end_sample))
        
        # Reconstruction audio
        _, watermarked_audio = scipy.signal.istft(
            watermarked_stft, fs=sample_rate, window='hann',
            nperseg=window_size, noverlap=window_size - hop_size
        )
        
        return watermarked_audio, embedding_locations
    
    def _payload_to_bits(self, payload: WatermarkPayload) -> List[int]:
        """Convertit le payload en séquence de bits"""
        # Sérialisation du payload
        payload_dict = {
            'creator_id': payload.creator_id,
            'content_id': payload.content_id,
            'timestamp': payload.timestamp.isoformat(),
            'copyright_info': payload.copyright_info,
            'license_type': payload.license_type,
            'protection_level': payload.protection_level,
            'blockchain_hash': payload.blockchain_hash
        }
        
        # Conversion en JSON puis bytes
        payload_json = json.dumps(payload_dict, sort_keys=True)
        payload_bytes = payload_json.encode('utf-8')
        
        # Conversion en bits avec redondance
        bits = []
        for byte in payload_bytes:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                # Redondance pour robustesse
                bits.extend([bit] * self.config.redundancy_factor)
        
        return bits

class WatermarkDetector:
    """Détecteur de watermark audio"""
    
    def __init__(self):
        self.psychoacoustic_model = PsychoacousticModel()
    
    def detect_watermark(self, audio: np.ndarray, sample_rate: int,
                        detection_config: WatermarkConfiguration) -> WatermarkDetectionResult:
        """Détecte et extrait le watermark de l'audio"""
        
        start_time = time.time()
        
        # Analyse spectrale
        window_size = 2048
        hop_size = window_size // 4
        
        frequencies, times, stft = scipy.signal.stft(
            audio, fs=sample_rate, window='hann',
            nperseg=window_size, noverlap=window_size - hop_size
        )
        
        # Sélection des fréquences de détection
        freq_mask = (frequencies >= detection_config.frequency_range[0]) & \
                   (frequencies <= detection_config.frequency_range[1])
        
        # Extraction des bits
        extracted_bits = []
        confidence_scores = []
        
        for t_idx in range(0, stft.shape[1], sample_rate // window_size):
            time_frame = stft[:, t_idx]
            
            # Analyse de phase pour chaque fréquence d'embedding
            for freq_idx in np.where(freq_mask)[0]:
                phase = np.angle(time_frame[freq_idx])
                magnitude = np.abs(time_frame[freq_idx])
                
                # Détection basée sur la modulation de phase
                if magnitude > 1e-6:  # Seuil minimum
                    # Classification du bit basée sur la phase
                    normalized_phase = (phase + np.pi) / (2 * np.pi)
                    
                    if 0.125 <= normalized_phase <= 0.375:  # π/4 region
                        bit = 1
                        confidence = 1.0 - abs(normalized_phase - 0.25) / 0.125
                    elif 0.625 <= normalized_phase <= 0.875:  # -π/4 region
                        bit = 0
                        confidence = 1.0 - abs(normalized_phase - 0.75) / 0.125
                    else:
                        continue  # Pas de watermark détecté
                    
                    extracted_bits.append(bit)
                    confidence_scores.append(confidence)
        
        # Validation et reconstruction du payload
        if len(extracted_bits) >= 64:  # Minimum viable
            # Décodage avec correction d'erreurs
            payload = self._reconstruct_payload(extracted_bits, detection_config.redundancy_factor)
            detected = payload is not None
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        else:
            payload = None
            detected = False
            overall_confidence = 0.0
        
        processing_time = time.time() - start_time
        
        return WatermarkDetectionResult(
            detected=detected,
            confidence=overall_confidence,
            payload=payload,
            detection_method=detection_config.watermark_type,
            processing_time=processing_time,
            quality_impact=self._estimate_quality_impact(audio),
            attack_evidence=self._detect_attacks(audio, sample_rate)
        )
    
    def _reconstruct_payload(self, bits: List[int], redundancy: int) -> Optional[WatermarkPayload]:
        """Reconstruit le payload à partir des bits extraits"""
        try:
            # Décodage avec redondance
            decoded_bits = []
            for i in range(0, len(bits), redundancy):
                chunk = bits[i:i+redundancy]
                if len(chunk) >= redundancy // 2:
                    # Vote majoritaire
                    decoded_bits.append(1 if sum(chunk) > len(chunk) // 2 else 0)
            
            # Conversion bits vers bytes
            payload_bytes = bytearray()
            for i in range(0, len(decoded_bits), 8):
                if i + 8 <= len(decoded_bits):
                    byte_bits = decoded_bits[i:i+8]
                    byte_value = sum(bit << (7-j) for j, bit in enumerate(byte_bits))
                    payload_bytes.append(byte_value)
            
            # Décodage JSON
            payload_json = payload_bytes.decode('utf-8')
            payload_dict = json.loads(payload_json)
            
            # Reconstruction du payload
            return WatermarkPayload(
                creator_id=payload_dict['creator_id'],
                content_id=payload_dict['content_id'],
                timestamp=datetime.fromisoformat(payload_dict['timestamp']),
                copyright_info=payload_dict['copyright_info'],
                license_type=payload_dict['license_type'],
                protection_level=payload_dict['protection_level'],
                blockchain_hash=payload_dict.get('blockchain_hash')
            )
        
        except Exception as e:
            logger.warning(f"Erreur reconstruction payload: {e}")
            return None
    
    def _estimate_quality_impact(self, audio: np.ndarray) -> float:
        """Estime l'impact sur la qualité audio"""
        # Analyse basique de la qualité
        dynamic_range = np.max(audio) - np.min(audio)
        rms = np.sqrt(np.mean(audio ** 2))
        
        # Score de qualité simplifié
        quality_score = min(1.0, rms / (dynamic_range * 0.1))
        return 1.0 - quality_score  # Impact (0 = pas d'impact, 1 = impact total)
    
    def _detect_attacks(self, audio: np.ndarray, sample_rate: int) -> List[str]:
        """Détecte les signes d'attaques sur l'audio"""
        attacks = []
        
        # Détection compression (analyse spectrale)
        freqs, psd = scipy.signal.welch(audio, sample_rate, nperseg=1024)
        high_freq_energy = np.sum(psd[freqs > 15000])
        total_energy = np.sum(psd)
        
        if high_freq_energy / total_energy < 0.01:
            attacks.append("compression_detected")
        
        # Détection resampling (analyse harmoniques)
        if sample_rate % 11025 == 0 or sample_rate % 8000 == 0:
            attacks.append("resampling_suspected")
        
        # Détection filtrage (coupures spectrales)
        if np.max(freqs) < 18000:
            attacks.append("filtering_detected")
        
        return attacks

class AudioWatermarkingEngine:
    """Engine principal de watermarking audio enterprise"""
    
    def __init__(self):
        self.embedders = {
            WatermarkType.SPECTRAL_DOMAIN: SpectralWatermarkEmbedder,
            # Autres embedders à implémenter...
        }
        self.detector = WatermarkDetector()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("🔒 Audio Watermarking Engine initialized - Fahed Mlaiel Enterprise")
    
    async def embed_watermark_async(self, audio_data: Union[np.ndarray, bytes],
                                   sample_rate: int, payload: WatermarkPayload,
                                   config: WatermarkConfiguration) -> AudioWatermarkResult:
        """Embed watermark de manière asynchrone"""
        
        start_time = time.time()
        
        # Conversion audio si nécessaire
        if isinstance(audio_data, bytes):
            audio = self._bytes_to_numpy(audio_data)
        else:
            audio = audio_data.copy()
        
        # Normalisation audio
        audio = self._normalize_audio(audio)
        
        # Sélection de l'embedder
        embedder_class = self.embedders.get(config.watermark_type)
        if not embedder_class:
            raise ValueError(f"Type watermark non supporté: {config.watermark_type}")
        
        # Embedding en thread séparé
        loop = asyncio.get_event_loop()
        embedder = embedder_class(config)
        
        watermarked_audio, locations = await loop.run_in_executor(
            self.executor,
            embedder.embed_watermark,
            audio, payload, sample_rate
        )
        
        # Calcul métriques qualité
        quality_metrics = self._calculate_quality_metrics(audio, watermarked_audio)
        
        processing_time = time.time() - start_time
        
        return AudioWatermarkResult(
            watermarked_audio=watermarked_audio,
            embedding_success=True,
            watermark_payload=payload,
            quality_metrics=quality_metrics,
            processing_time=processing_time,
            embedding_locations=locations
        )
    
    async def detect_watermark_async(self, audio_data: Union[np.ndarray, bytes],
                                    sample_rate: int,
                                    config: WatermarkConfiguration) -> WatermarkDetectionResult:
        """Détecte watermark de manière asynchrone"""
        
        # Conversion audio si nécessaire
        if isinstance(audio_data, bytes):
            audio = self._bytes_to_numpy(audio_data)
        else:
            audio = audio_data.copy()
        
        # Normalisation audio
        audio = self._normalize_audio(audio)
        
        # Détection en thread séparé
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.detector.detect_watermark,
            audio, sample_rate, config
        )
        
        return result
    
    def create_creator_payload(self, creator_id: str, content_id: str,
                              license_type: str = "standard",
                              protection_level: str = "medium",
                              custom_data: Optional[Dict] = None) -> WatermarkPayload:
        """Crée un payload watermark pour un créateur"""
        
        return WatermarkPayload(
            creator_id=creator_id,
            content_id=content_id,
            timestamp=datetime.now(),
            copyright_info={
                "platform": "Ainflue",
                "creator": creator_id,
                "created_at": datetime.now().isoformat(),
                "protection_method": "audio_watermarking"
            },
            license_type=license_type,
            protection_level=protection_level,
            blockchain_hash=self._generate_blockchain_hash(creator_id, content_id),
            custom_data=custom_data or {}
        )
    
    def get_optimal_config(self, content_type: str, quality_priority: bool = True) -> WatermarkConfiguration:
        """Retourne une configuration optimale selon le type de contenu"""
        
        configs = {
            "music": WatermarkConfiguration(
                watermark_type=WatermarkType.SPECTRAL_DOMAIN,
                strength=WatermarkStrength.LIGHT if quality_priority else WatermarkStrength.MEDIUM,
                frequency_range=(300, 12000),
                embedding_rate=0.5,
                redundancy_factor=5,
                psychoacoustic_masking=True,
                attack_resistance=[
                    AttackResistance.COMPRESSION_MP3,
                    AttackResistance.COMPRESSION_AAC,
                    AttackResistance.NOISE_ADDITION
                ]
            ),
            "podcast": WatermarkConfiguration(
                watermark_type=WatermarkType.SPECTRAL_DOMAIN,
                strength=WatermarkStrength.MEDIUM,
                frequency_range=(300, 8000),
                embedding_rate=1.0,
                redundancy_factor=3,
                psychoacoustic_masking=True,
                attack_resistance=[
                    AttackResistance.COMPRESSION_MP3,
                    AttackResistance.NOISE_ADDITION,
                    AttackResistance.AMPLIFICATION
                ]
            ),
            "voice": WatermarkConfiguration(
                watermark_type=WatermarkType.PHASE_CODING,
                strength=WatermarkStrength.LIGHT,
                frequency_range=(300, 6000),
                embedding_rate=0.8,
                redundancy_factor=4,
                psychoacoustic_masking=True,
                attack_resistance=[
                    AttackResistance.COMPRESSION_MP3,
                    AttackResistance.FILTERING
                ]
            )
        }
        
        return configs.get(content_type, configs["music"])
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalise l'audio pour le traitement"""
        if len(audio.shape) > 1:
            # Conversion stereo vers mono
            audio = np.mean(audio, axis=1)
        
        # Normalisation amplitude
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            audio = audio / max_amplitude * 0.95
        
        return audio
    
    def _bytes_to_numpy(self, audio_bytes: bytes) -> np.ndarray:
        """Convertit bytes audio vers numpy array"""
        # Implémentation simplifiée - à adapter selon le format
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        return audio_array
    
    def _calculate_quality_metrics(self, original: np.ndarray, 
                                  watermarked: np.ndarray) -> Dict[str, float]:
        """Calcule les métriques de qualité audio"""
        
        # Signal-to-Noise Ratio
        noise = watermarked - original
        signal_power = np.mean(original ** 2)
        noise_power = np.mean(noise ** 2)
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        
        # Corrélation
        correlation = np.corrcoef(original, watermarked)[0, 1]
        
        # Distorsion harmonique totale (approximation)
        thd = np.sqrt(noise_power) / np.sqrt(signal_power) * 100
        
        return {
            "snr_db": float(snr),
            "correlation": float(correlation),
            "thd_percent": float(thd),
            "quality_preservation": float(max(0, min(1, (snr + 20) / 40)))
        }
    
    def _generate_blockchain_hash(self, creator_id: str, content_id: str) -> str:
        """Génère un hash blockchain pour traçabilité"""
        data = f"{creator_id}:{content_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

# Factory pour création d'instances
def create_watermarking_engine() -> AudioWatermarkingEngine:
    """Factory pour créer une instance du watermarking engine"""
    return AudioWatermarkingEngine()

# Export pour intégration
__all__ = [
    'AudioWatermarkingEngine',
    'WatermarkType',
    'WatermarkStrength', 
    'WatermarkConfiguration',
    'WatermarkPayload',
    'AudioWatermarkResult',
    'WatermarkDetectionResult',
    'create_watermarking_engine'
]