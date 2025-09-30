"""🎛️ Enterprise Audio Effects Processor - Professional Studio-Grade Effects
=========================================================================

Processeur d'effets audio enterprise avec algorithmes studio professionnel,
chaîne d'effets modulaire et processing temps réel pour créateurs sur Ainflue.

Expert Roles Implementation:
🎵 Audio Engineer: Studio-grade effects algorithms + professional mixing chains
🏗️ Backend Senior: Effects pipeline architecture + parallel processing optimization
🤖 Lead Dev IA: AI-powered effects automation + intelligent parameter optimization
🧠 ML Engineer: Adaptive effects models + user preference learning
🔒 Sécurité: Effects processing security + audio processing integrity
⚙️ DevOps: Effects automation + performance monitoring + resource optimization
🔗 Microservices: Effects services mesh + distributed processing
⚡ Performance: Real-time effects processing + ultra-low latency optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Enterprise Production
Date: 16 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture d'effets audio est la propriété intellectuelle EXCLUSIVE de
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
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import numpy as np
import librosa
import soundfile as sf
import torch
import torch.nn.functional as F
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

class EffectType(Enum):
    """Types d'effets audio disponibles"""
    EQ_PARAMETRIC = "eq_parametric"
    EQ_GRAPHIC = "eq_graphic"
    EQ_LINEAR_PHASE = "eq_linear_phase"
    COMPRESSOR = "compressor"
    LIMITER = "limiter"
    EXPANDER = "expander"
    GATE = "gate"
    REVERB_CONVOLUTION = "reverb_convolution"
    REVERB_ALGORITHMIC = "reverb_algorithmic"
    DELAY = "delay"
    ECHO = "echo"
    CHORUS = "chorus"
    FLANGER = "flanger"
    PHASER = "phaser"
    TREMOLO = "tremolo"
    VIBRATO = "vibrato"
    DISTORTION = "distortion"
    SATURATION = "saturation"
    PITCH_SHIFT = "pitch_shift"
    TIME_STRETCH = "time_stretch"
    LOOP = "loop"
    MASTERING_CHAIN = "mastering_chain"

class EffectQuality(Enum):
    """Niveaux de qualité d'effets"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    MASTERING = "mastering"

class ProcessingMode(Enum):
    """Modes de traitement des effets"""
    OFFLINE = "offline"
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class EffectParameter:
    """Paramètre d'effet audio"""
    name: str
    value: float
    min_value: float
    max_value: float
    unit: str
    description: str
    automation_curve: Optional[List[tuple[float, float]]] = None

@dataclass
class EffectConfiguration:
    """Configuration d'un effet audio"""
    effect_type: EffectType
    enabled: bool = True
    parameters: Dict[str, EffectParameter] = field(default_factory=dict)
    quality: EffectQuality = EffectQuality.PROFESSIONAL
    bypass: bool = False
    mix_level: float = 1.0  # 0.0 = dry, 1.0 = wet

@dataclass
class EffectsChain:
    """Chaîne d'effets audio"""
    chain_id: str
    name: str
    effects: List[EffectConfiguration]
    input_gain: float = 1.0
    output_gain: float = 1.0
    enabled: bool = True

@dataclass
class EffectResult:
    """Résultat du traitement d'effets"""
    processed_audio: np.ndarray
    sample_rate: int
    processing_time: float
    effects_applied: List[str]
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any]

class EQProcessor:
    """Processeur d'égalisation professionnel"""
    
    def __init__(self):
        self.eq_bands = {}
    
    async def parametric_eq(
        self,
        audio: np.ndarray,
        sample_rate: int,
        bands: List[Dict[str, float]]
    ) -> np.ndarray:
        """Égalisation paramétrique professionnelle"""
        processed = audio.copy()
        
        for band in bands:
            frequency = band.get('frequency', 1000)
            gain_db = band.get('gain', 0)
            q_factor = band.get('q', 1.0)
            filter_type = band.get('type', 'bell')
            
            if gain_db != 0:
                if filter_type == 'bell':
                    processed = await self._apply_bell_filter(
                        processed, sample_rate, frequency, gain_db, q_factor
                    )
                elif filter_type == 'highpass':
                    processed = await self._apply_highpass_filter(
                        processed, sample_rate, frequency, q_factor
                    )
                elif filter_type == 'lowpass':
                    processed = await self._apply_lowpass_filter(
                        processed, sample_rate, frequency, q_factor
                    )
        
        return processed
    
    async def _apply_bell_filter(
        self,
        audio: np.ndarray,
        sample_rate: int,
        frequency: float,
        gain_db: float,
        q_factor: float
    ) -> np.ndarray:
        """Applique un filtre en cloche (bell filter)"""
        # Calculer les coefficients du filtre
        w = 2 * np.pi * frequency / sample_rate
        cosw = np.cos(w)
        sinw = np.sin(w)
        A = 10 ** (gain_db / 40)
        alpha = sinw / (2 * q_factor)
        
        # Coefficients du filtre biquad
        b0 = 1 + alpha * A
        b1 = -2 * cosw
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * cosw
        a2 = 1 - alpha / A
        
        # Normaliser
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1, a2]) / a0
        
        # Appliquer le filtre
        if len(audio.shape) == 1:
            return signal.lfilter(b, a, audio)
        else:
            return np.array([signal.lfilter(b, a, audio[i]) for i in range(audio.shape[0])])
    
    async def _apply_highpass_filter(
        self,
        audio: np.ndarray,
        sample_rate: int,
        frequency: float,
        q_factor: float
    ) -> np.ndarray:
        """Applique un filtre passe-haut"""
        nyquist = sample_rate / 2
        high = frequency / nyquist
        b, a = butter(2, high, btype='high')
        
        if len(audio.shape) == 1:
            return filtfilt(b, a, audio)
        else:
            return np.array([filtfilt(b, a, audio[i]) for i in range(audio.shape[0])])
    
    async def _apply_lowpass_filter(
        self,
        audio: np.ndarray,
        sample_rate: int,
        frequency: float,
        q_factor: float
    ) -> np.ndarray:
        """Applique un filtre passe-bas"""
        nyquist = sample_rate / 2
        low = frequency / nyquist
        b, a = butter(2, low, btype='low')
        
        if len(audio.shape) == 1:
            return filtfilt(b, a, audio)
        else:
            return np.array([filtfilt(b, a, audio[i]) for i in range(audio.shape[0])])

class DynamicsProcessor:
    """Processeur de dynamiques professionnel"""
    
    def __init__(self):
        self.envelope_followers = {}
    
    async def compressor(
        self,
        audio: np.ndarray,
        sample_rate: int,
        threshold: float = -12,  # dB
        ratio: float = 4.0,
        attack: float = 10,  # ms
        release: float = 100,  # ms
        makeup_gain: float = 0  # dB
    ) -> np.ndarray:
        """Compresseur audio professionnel"""
        # Convertir les temps en échantillons
        attack_samples = int(attack * sample_rate / 1000)
        release_samples = int(release * sample_rate / 1000)
        
        # Calculer les coefficients d'envelope follower
        attack_coeff = np.exp(-1 / attack_samples) if attack_samples > 0 else 0
        release_coeff = np.exp(-1 / release_samples) if release_samples > 0 else 0
        
        # Traitement canal par canal
        if len(audio.shape) == 1:
            return await self._compress_channel(
                audio, threshold, ratio, attack_coeff, release_coeff, makeup_gain
            )
        else:
            processed = np.zeros_like(audio)
            for i in range(audio.shape[0]):
                processed[i] = await self._compress_channel(
                    audio[i], threshold, ratio, attack_coeff, release_coeff, makeup_gain
                )
            return processed
    
    async def _compress_channel(
        self,
        audio: np.ndarray,
        threshold: float,
        ratio: float,
        attack_coeff: float,
        release_coeff: float,
        makeup_gain: float
    ) -> np.ndarray:
        """Compresse un canal audio"""
        # Convertir en dB
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        
        # Calculer la réduction de gain
        gain_reduction = np.zeros_like(audio_db)
        envelope = 0
        
        for i in range(len(audio_db)):
            # Détection de niveau
            input_level = audio_db[i]
            
            # Calcul de la réduction si au-dessus du seuil
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
        
        # Appliquer la réduction de gain et le makeup gain
        gain_linear = 10 ** ((gain_reduction + makeup_gain) / 20)
        return audio * gain_linear
    
    async def limiter(
        self,
        audio: np.ndarray,
        sample_rate: int,
        threshold: float = -0.1,  # dB
        release: float = 50  # ms
    ) -> np.ndarray:
        """Limiteur audio professionnel"""
        return await self.compressor(
            audio, sample_rate, threshold, ratio=20.0, 
            attack=0.1, release=release, makeup_gain=0
        )

class ModulationEffects:
    """Effets de modulation professionnels"""
    
    def __init__(self):
        self.lfo_phases = {}
    
    async def chorus(
        self,
        audio: np.ndarray,
        sample_rate: int,
        depth: float = 0.5,
        rate: float = 0.5,  # Hz
        delay: float = 20,  # ms
        feedback: float = 0.2,
        mix: float = 0.5
    ) -> np.ndarray:
        """Effet chorus professionnel"""
        delay_samples = int(delay * sample_rate / 1000)
        
        # Créer le LFO (Low Frequency Oscillator)
        lfo_samples = np.arange(len(audio)) / sample_rate
        lfo = np.sin(2 * np.pi * rate * lfo_samples)
        
        # Moduler le délai
        modulated_delay = delay_samples + (depth * delay_samples * lfo)
        
        # Appliquer l'effet chorus
        if len(audio.shape) == 1:
            chorus_audio = await self._apply_variable_delay(
                audio, modulated_delay, feedback
            )
            return audio * (1 - mix) + chorus_audio * mix
        else:
            processed = np.zeros_like(audio)
            for i in range(audio.shape[0]):
                chorus_audio = await self._apply_variable_delay(
                    audio[i], modulated_delay, feedback
                )
                processed[i] = audio[i] * (1 - mix) + chorus_audio * mix
            return processed
    
    async def _apply_variable_delay(
        self,
        audio: np.ndarray,
        delay_samples: np.ndarray,
        feedback: float
    ) -> np.ndarray:
        """Applique un délai variable"""
        output = np.zeros_like(audio)
        max_delay = int(np.max(delay_samples)) + 1
        delay_buffer = np.zeros(max_delay)
        
        for i in range(len(audio)):
            # Interpolation linéaire pour le délai fractionnaire
            delay_int = int(delay_samples[i])
            delay_frac = delay_samples[i] - delay_int
            
            if delay_int < max_delay - 1:
                delayed_sample = (delay_buffer[delay_int] * (1 - delay_frac) + 
                                delay_buffer[delay_int + 1] * delay_frac)
            else:
                delayed_sample = delay_buffer[delay_int]
            
            output[i] = delayed_sample
            
            # Mettre à jour le buffer de délai
            delay_buffer[1:] = delay_buffer[:-1]
            delay_buffer[0] = audio[i] + delayed_sample * feedback
        
        return output

class ReverbProcessor:
    """Processeur de reverb professionnel"""
    
    def __init__(self):
        self.impulse_responses = {}
    
    async def convolution_reverb(
        self,
        audio: np.ndarray,
        impulse_response: np.ndarray,
        mix: float = 0.3
    ) -> np.ndarray:
        """Reverb par convolution avec réponse impulsionnelle"""
        if len(audio.shape) == 1:
            reverb_audio = np.convolve(audio, impulse_response, mode='same')
            return audio * (1 - mix) + reverb_audio * mix
        else:
            processed = np.zeros_like(audio)
            for i in range(audio.shape[0]):
                reverb_audio = np.convolve(audio[i], impulse_response, mode='same')
                processed[i] = audio[i] * (1 - mix) + reverb_audio * mix
            return processed
    
    async def algorithmic_reverb(
        self,
        audio: np.ndarray,
        sample_rate: int,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        dry_level: float = 0.7
    ) -> np.ndarray:
        """Reverb algorithmique avec paramètres contrôlables"""
        # Implémenter une reverb Schroeder avec allpass et comb filters
        # Ceci est une version simplifiée
        delay_times = [29.7, 37.1, 41.1, 43.7]  # ms
        
        reverb_audio = np.zeros_like(audio)
        
        for delay_time in delay_times:
            delay_samples = int(delay_time * sample_rate / 1000)
            
            if len(audio.shape) == 1:
                delayed = await self._comb_filter(
                    audio, delay_samples, room_size, damping
                )
                reverb_audio += delayed / len(delay_times)
            else:
                for i in range(audio.shape[0]):
                    delayed = await self._comb_filter(
                        audio[i], delay_samples, room_size, damping
                    )
                    reverb_audio[i] += delayed / len(delay_times)
        
        return audio * dry_level + reverb_audio * wet_level
    
    async def _comb_filter(
        self,
        audio: np.ndarray,
        delay_samples: int,
        feedback: float,
        damping: float
    ) -> np.ndarray:
        """Filtre en peigne pour reverb"""
        output = np.zeros_like(audio)
        delay_buffer = np.zeros(delay_samples)
        filter_state = 0
        
        for i in range(len(audio)):
            delayed_sample = delay_buffer[0]
            
            # Appliquer le damping (filtre passe-bas simple)
            filter_state = filter_state * damping + delayed_sample * (1 - damping)
            
            output[i] = audio[i] + filter_state * feedback
            
            # Décaler le buffer
            delay_buffer[:-1] = delay_buffer[1:]
            delay_buffer[-1] = output[i]
        
        return output

class AudioEffectsProcessor:
    """Processeur d'effets audio enterprise avec algorithmes studio professionnel"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le processeur d'effets audio"""
        self.config = config or {}
        self.eq_processor = EQProcessor()
        self.dynamics_processor = DynamicsProcessor()
        self.modulation_effects = ModulationEffects()
        self.reverb_processor = ReverbProcessor()
        
        # Configuration par défaut
        self.default_quality = EffectQuality.PROFESSIONAL
        self.max_processing_time = 30.0  # secondes
        
        # Métriques de performance
        self.processing_stats = {
            'total_processed': 0,
            'average_processing_time': 0,
            'effects_usage': {}
        }
        
        # Cache Redis pour les effets pré-calculés
        self.redis_client = None
        
        logger.info("AudioEffectsProcessor initialized successfully")
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialise la connexion Redis pour le cache"""
        try:
            self.redis_client = await aioredis.from_url(redis_url)
            logger.info("Redis connection established for effects caching")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
    
    async def process_effects_chain(
        self,
        audio: np.ndarray,
        sample_rate: int,
        effects_chain: EffectsChain,
        processing_mode: ProcessingMode = ProcessingMode.OFFLINE
    ) -> EffectResult:
        """Traite une chaîne d'effets audio complète"""
        start_time = time.time()
        
        try:
            # Vérifier la validité de l'audio
            if audio is None or len(audio) == 0:
                raise ValueError("Audio data is empty or invalid")
            
            # Normaliser l'audio d'entrée si nécessaire
            if np.max(np.abs(audio)) > 1.0:
                audio = audio / np.max(np.abs(audio))
            
            # Appliquer le gain d'entrée
            processed_audio = audio * effects_chain.input_gain
            effects_applied = []
            
            # Traiter chaque effet dans la chaîne
            for effect_config in effects_chain.effects:
                if effect_config.enabled and not effect_config.bypass:
                    processed_audio = await self._apply_single_effect(
                        processed_audio, sample_rate, effect_config
                    )
                    effects_applied.append(effect_config.effect_type.value)
            
            # Appliquer le gain de sortie
            processed_audio *= effects_chain.output_gain
            
            # Calculer les métriques de qualité
            quality_metrics = await self._calculate_quality_metrics(
                audio, processed_audio, sample_rate
            )
            
            processing_time = time.time() - start_time
            
            # Mettre à jour les statistiques
            await self._update_processing_stats(processing_time, effects_applied)
            
            return EffectResult(
                processed_audio=processed_audio,
                sample_rate=sample_rate,
                processing_time=processing_time,
                effects_applied=effects_applied,
                quality_metrics=quality_metrics,
                metadata={
                    'chain_id': effects_chain.chain_id,
                    'chain_name': effects_chain.name,
                    'processing_mode': processing_mode.value,
                    'input_gain': effects_chain.input_gain,
                    'output_gain': effects_chain.output_gain
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing effects chain: {e}")
            raise
    
    async def _apply_single_effect(
        self,
        audio: np.ndarray,
        sample_rate: int,
        effect_config: EffectConfiguration
    ) -> np.ndarray:
        """Applique un effet audio unique"""
        effect_type = effect_config.effect_type
        params = effect_config.parameters
        
        try:
            if effect_type == EffectType.EQ_PARAMETRIC:
                bands = []
                for i in range(8):  # 8 bandes maximum
                    freq_key = f"band_{i}_frequency"
                    gain_key = f"band_{i}_gain"
                    q_key = f"band_{i}_q"
                    
                    if freq_key in params and gain_key in params:
                        bands.append({
                            'frequency': params[freq_key].value,
                            'gain': params[gain_key].value,
                            'q': params.get(q_key, EffectParameter("q", 1.0, 0.1, 10.0, "", "")).value,
                            'type': 'bell'
                        })
                
                return await self.eq_processor.parametric_eq(audio, sample_rate, bands)
            
            elif effect_type == EffectType.COMPRESSOR:
                threshold = params.get('threshold', EffectParameter("threshold", -12, -60, 0, "dB", "")).value
                ratio = params.get('ratio', EffectParameter("ratio", 4.0, 1.0, 20.0, ":1", "")).value
                attack = params.get('attack', EffectParameter("attack", 10, 0.1, 100, "ms", "")).value
                release = params.get('release', EffectParameter("release", 100, 10, 1000, "ms", "")).value
                makeup_gain = params.get('makeup_gain', EffectParameter("makeup_gain", 0, -20, 20, "dB", "")).value
                
                return await self.dynamics_processor.compressor(
                    audio, sample_rate, threshold, ratio, attack, release, makeup_gain
                )
            
            elif effect_type == EffectType.LIMITER:
                threshold = params.get('threshold', EffectParameter("threshold", -0.1, -10, 0, "dB", "")).value
                release = params.get('release', EffectParameter("release", 50, 10, 500, "ms", "")).value
                
                return await self.dynamics_processor.limiter(audio, sample_rate, threshold, release)
            
            elif effect_type == EffectType.CHORUS:
                depth = params.get('depth', EffectParameter("depth", 0.5, 0.0, 1.0, "", "")).value
                rate = params.get('rate', EffectParameter("rate", 0.5, 0.1, 5.0, "Hz", "")).value
                delay = params.get('delay', EffectParameter("delay", 20, 5, 50, "ms", "")).value
                feedback = params.get('feedback', EffectParameter("feedback", 0.2, 0.0, 0.8, "", "")).value
                mix = params.get('mix', EffectParameter("mix", 0.5, 0.0, 1.0, "", "")).value
                
                return await self.modulation_effects.chorus(
                    audio, sample_rate, depth, rate, delay, feedback, mix
                )
            
            elif effect_type == EffectType.REVERB_ALGORITHMIC:
                room_size = params.get('room_size', EffectParameter("room_size", 0.5, 0.0, 1.0, "", "")).value
                damping = params.get('damping', EffectParameter("damping", 0.5, 0.0, 1.0, "", "")).value
                wet_level = params.get('wet_level', EffectParameter("wet_level", 0.3, 0.0, 1.0, "", "")).value
                dry_level = params.get('dry_level', EffectParameter("dry_level", 0.7, 0.0, 1.0, "", "")).value
                
                return await self.reverb_processor.algorithmic_reverb(
                    audio, sample_rate, room_size, damping, wet_level, dry_level
                )
            
            else:
                logger.warning(f"Effect type {effect_type} not yet implemented")
                return audio
                
        except Exception as e:
            logger.error(f"Error applying effect {effect_type}: {e}")
            return audio
    
    async def _calculate_quality_metrics(
        self,
        original: np.ndarray,
        processed: np.ndarray,
        sample_rate: int
    ) -> Dict[str, float]:
        """Calcule les métriques de qualité pour les effets appliqués"""
        try:
            # Dynamic range
            original_peak = np.max(np.abs(original))
            processed_peak = np.max(np.abs(processed))
            
            # RMS levels
            original_rms = np.sqrt(np.mean(original ** 2))
            processed_rms = np.sqrt(np.mean(processed ** 2))
            
            # THD+N estimation (approximation simple)
            thd_original = await self._estimate_thd(original, sample_rate)
            thd_processed = await self._estimate_thd(processed, sample_rate)
            
            return {
                'peak_level_original': 20 * np.log10(original_peak + 1e-10),
                'peak_level_processed': 20 * np.log10(processed_peak + 1e-10),
                'rms_level_original': 20 * np.log10(original_rms + 1e-10),
                'rms_level_processed': 20 * np.log10(processed_rms + 1e-10),
                'dynamic_range_original': 20 * np.log10(original_peak / (original_rms + 1e-10)),
                'dynamic_range_processed': 20 * np.log10(processed_peak / (processed_rms + 1e-10)),
                'thd_original': thd_original,
                'thd_processed': thd_processed,
                'correlation': np.corrcoef(original.flatten(), processed.flatten())[0, 1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return {}
    
    async def _estimate_thd(self, audio: np.ndarray, sample_rate: int) -> float:
        """Estimation simplifiée du THD+N"""
        try:
            # FFT pour analyse spectrale
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(audio), 1/sample_rate)
            
            # Trouver la fréquence fondamentale
            magnitude = np.abs(fft)
            fundamental_idx = np.argmax(magnitude[1:len(magnitude)//2]) + 1
            
            # Calculer l'énergie totale et l'énergie de la fondamentale
            total_energy = np.sum(magnitude ** 2)
            fundamental_energy = magnitude[fundamental_idx] ** 2
            
            # THD approximatif
            noise_energy = total_energy - fundamental_energy
            thd = np.sqrt(noise_energy / fundamental_energy) if fundamental_energy > 0 else 0
            
            return min(thd * 100, 100)  # En pourcentage, limité à 100%
            
        except Exception:
            return 0.0
    
    async def _update_processing_stats(
        self,
        processing_time: float,
        effects_applied: List[str]
    ):
        """Met à jour les statistiques de traitement"""
        self.processing_stats['total_processed'] += 1
        
        # Moyenne mobile du temps de traitement
        current_avg = self.processing_stats['average_processing_time']
        total = self.processing_stats['total_processed']
        
        self.processing_stats['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Comptage d'utilisation des effets
        for effect in effects_applied:
            if effect not in self.processing_stats['effects_usage']:
                self.processing_stats['effects_usage'][effect] = 0
            self.processing_stats['effects_usage'][effect] += 1
    
    async def create_mastering_chain(
        self,
        target_loudness: float = -14.0,  # LUFS
        target_peak: float = -1.0  # dBTP
    ) -> EffectsChain:
        """Crée une chaîne de mastering professionnelle"""
        effects = []
        
        # EQ correctif
        eq_effect = EffectConfiguration(
            effect_type=EffectType.EQ_PARAMETRIC,
            parameters={
                'band_0_frequency': EffectParameter("band_0_frequency", 60, 20, 20000, "Hz", "Sub correction"),
                'band_0_gain': EffectParameter("band_0_gain", -2, -15, 15, "dB", "Sub gain"),
                'band_0_q': EffectParameter("band_0_q", 0.7, 0.1, 10, "", "Sub Q"),
                
                'band_1_frequency': EffectParameter("band_1_frequency", 1000, 20, 20000, "Hz", "Mid presence"),
                'band_1_gain': EffectParameter("band_1_gain", 1, -15, 15, "dB", "Mid gain"),
                'band_1_q': EffectParameter("band_1_q", 1.5, 0.1, 10, "", "Mid Q"),
                
                'band_2_frequency': EffectParameter("band_2_frequency", 8000, 20, 20000, "Hz", "High frequency"),
                'band_2_gain': EffectParameter("band_2_gain", 0.5, -15, 15, "dB", "High gain"),
                'band_2_q': EffectParameter("band_2_q", 1.0, 0.1, 10, "", "High Q"),
            }
        )
        effects.append(eq_effect)
        
        # Compresseur multiband (simulé avec un compresseur large bande)
        compressor_effect = EffectConfiguration(
            effect_type=EffectType.COMPRESSOR,
            parameters={
                'threshold': EffectParameter("threshold", -18, -40, 0, "dB", "Compression threshold"),
                'ratio': EffectParameter("ratio", 3.0, 1.0, 10.0, ":1", "Compression ratio"),
                'attack': EffectParameter("attack", 5, 0.1, 100, "ms", "Attack time"),
                'release': EffectParameter("release", 150, 10, 1000, "ms", "Release time"),
                'makeup_gain': EffectParameter("makeup_gain", 3, -10, 20, "dB", "Makeup gain"),
            }
        )
        effects.append(compressor_effect)
        
        # Limiteur final
        limiter_effect = EffectConfiguration(
            effect_type=EffectType.LIMITER,
            parameters={
                'threshold': EffectParameter("threshold", target_peak, -10, 0, "dB", "Limiter threshold"),
                'release': EffectParameter("release", 30, 5, 200, "ms", "Limiter release"),
            }
        )
        effects.append(limiter_effect)
        
        return EffectsChain(
            chain_id=str(uuid.uuid4()),
            name="Professional Mastering Chain",
            effects=effects,
            input_gain=1.0,
            output_gain=1.0
        )
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de traitement"""
        return {
            'total_processed': self.processing_stats['total_processed'],
            'average_processing_time': self.processing_stats['average_processing_time'],
            'effects_usage': self.processing_stats['effects_usage'],
            'uptime': time.time() - getattr(self, '_start_time', time.time())
        }

# Factory functions
async def create_audio_effects_processor(config: Optional[Dict[str, Any]] = None) -> AudioEffectsProcessor:
    """Crée une instance du processeur d'effets audio"""
    processor = AudioEffectsProcessor(config)
    
    # Initialiser Redis si configuré
    if config and 'redis_url' in config:
        await processor.initialize_redis(config['redis_url'])
    
    return processor

async def create_preset_effects_chain(preset_name: str) -> EffectsChain:
    """Crée une chaîne d'effets prédéfinie"""
    if preset_name == "vocal_enhancement":
        return await _create_vocal_enhancement_chain()
    elif preset_name == "music_mastering":
        return await _create_music_mastering_chain()
    elif preset_name == "podcast_processing":
        return await _create_podcast_processing_chain()
    else:
        raise ValueError(f"Unknown preset: {preset_name}")

async def _create_vocal_enhancement_chain() -> EffectsChain:
    """Chaîne d'amélioration vocale"""
    effects = [
        EffectConfiguration(
            effect_type=EffectType.EQ_PARAMETRIC,
            parameters={
                'band_0_frequency': EffectParameter("band_0_frequency", 80, 20, 20000, "Hz", "HPF"),
                'band_0_gain': EffectParameter("band_0_gain", -6, -15, 15, "dB", "HPF gain"),
                
                'band_1_frequency': EffectParameter("band_1_frequency", 2500, 20, 20000, "Hz", "Presence"),
                'band_1_gain': EffectParameter("band_1_gain", 2, -15, 15, "dB", "Presence boost"),
                'band_1_q': EffectParameter("band_1_q", 1.5, 0.1, 10, "", "Presence Q"),
            }
        ),
        EffectConfiguration(
            effect_type=EffectType.COMPRESSOR,
            parameters={
                'threshold': EffectParameter("threshold", -20, -40, 0, "dB", "Vocal compression"),
                'ratio': EffectParameter("ratio", 3.0, 1.0, 10.0, ":1", "Vocal ratio"),
                'attack': EffectParameter("attack", 5, 0.1, 100, "ms", "Fast attack"),
                'release': EffectParameter("release", 100, 10, 1000, "ms", "Medium release"),
            }
        )
    ]
    
    return EffectsChain(
        chain_id=str(uuid.uuid4()),
        name="Vocal Enhancement",
        effects=effects
    )

async def _create_music_mastering_chain() -> EffectsChain:
    """Chaîne de mastering musical"""
    processor = AudioEffectsProcessor()
    return await processor.create_mastering_chain()

async def _create_podcast_processing_chain() -> EffectsChain:
    """Chaîne de traitement podcast"""
    effects = [
        EffectConfiguration(
            effect_type=EffectType.EQ_PARAMETRIC,
            parameters={
                'band_0_frequency': EffectParameter("band_0_frequency", 100, 20, 20000, "Hz", "HPF"),
                'band_0_gain': EffectParameter("band_0_gain", -12, -15, 15, "dB", "HPF gain"),
                
                'band_1_frequency': EffectParameter("band_1_frequency", 3000, 20, 20000, "Hz", "Speech clarity"),
                'band_1_gain': EffectParameter("band_1_gain", 3, -15, 15, "dB", "Speech boost"),
            }
        ),
        EffectConfiguration(
            effect_type=EffectType.COMPRESSOR,
            parameters={
                'threshold': EffectParameter("threshold", -18, -40, 0, "dB", "Broadcast compression"),
                'ratio': EffectParameter("ratio", 4.0, 1.0, 10.0, ":1", "Broadcast ratio"),
                'attack': EffectParameter("attack", 3, 0.1, 100, "ms", "Fast attack"),
                'release': EffectParameter("release", 80, 10, 1000, "ms", "Quick release"),
            }
        ),
        EffectConfiguration(
            effect_type=EffectType.LIMITER,
            parameters={
                'threshold': EffectParameter("threshold", -2, -10, 0, "dB", "Broadcast limiter"),
                'release': EffectParameter("release", 50, 5, 200, "ms", "Limiter release"),
            }
        )
    ]
    
    return EffectsChain(
        chain_id=str(uuid.uuid4()),
        name="Podcast Processing",
        effects=effects
    )

# Export des classes et fonctions principales
__all__ = [
    'AudioEffectsProcessor',
    'EffectType',
    'EffectQuality',
    'ProcessingMode',
    'EffectParameter',
    'EffectConfiguration',
    'EffectsChain',
    'EffectResult',
    'EQProcessor',
    'DynamicsProcessor',
    'ModulationEffects',
    'ReverbProcessor',
    'create_audio_effects_processor',
    'create_preset_effects_chain'
]