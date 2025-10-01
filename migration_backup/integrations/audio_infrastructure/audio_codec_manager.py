"""🔧 Enterprise Audio Codec Manager - Advanced Codec Optimization
=============================================================

Gestionnaire de codecs audio enterprise avec optimisation algorithmique,
compression intelligente et support multi-format pour IA Chéries.

Expert Roles Implementation:
🎵 Audio Engineer: Algorithmes de compression + optimisation qualité + codecs lossless
🏗️ Backend Senior: Pipeline encoding + traitement parallèle + gestion mémoire
🤖 Lead Dev IA: Compression intelligente + ML quality prediction + adaptive bitrate
🧠 ML Engineer: Modèles d'optimisation + perceptual encoding + quality assessment
🔒 Sécurité: Codec security + format validation + secure encoding pipelines
⚙️ DevOps: Automation encoding + performance monitoring + resource optimization
🔗 Microservices: Codec services + distributed encoding + API optimization
⚡ Performance: Encoding temps réel + parallel processing + memory efficiency

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Enterprise Production
Date: 16 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture de gestion de codecs audio est la propriété intellectuelle EXCLUSIVE de
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
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import numpy as np
import librosa
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
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

class AudioCodec(Enum):
    """Codecs audio supportés"""
    # Lossless Codecs
    FLAC = "flac"
    ALAC = "alac"  # Apple Lossless
    WV = "wavpack"
    APE = "ape"  # Monkey's Audio
    TTA = "tta"  # True Audio
    
    # Lossy Codecs
    MP3 = "mp3"
    AAC = "aac"
    OGG_VORBIS = "ogg"
    OPUS = "opus"
    WMA = "wma"
    AC3 = "ac3"
    DTS = "dts"
    
    # High-Resolution
    DSD = "dsd"  # Direct Stream Digital
    PCM = "pcm"  # Uncompressed
    
    # Streaming Optimized
    HE_AAC = "he_aac"  # High Efficiency AAC
    AAC_LC = "aac_lc"  # Low Complexity AAC
    OPUS_LOW_DELAY = "opus_ld"

class CompressionMode(Enum):
    """Modes de compression"""
    LOSSLESS = "lossless"
    LOSSY_HIGH = "lossy_high"
    LOSSY_MEDIUM = "lossy_medium"
    LOSSY_LOW = "lossy_low"
    TRANSPARENT = "transparent"
    STREAMING = "streaming"
    BROADCAST = "broadcast"

class EncodingSpeed(Enum):
    """Vitesses d'encodage"""
    REALTIME = "realtime"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    VERYSLOW = "veryslow"
    PLACEBO = "placebo"

class QualityMetric(Enum):
    """Métriques de qualité"""
    BITRATE = "bitrate"
    PSNR = "psnr"  # Peak Signal-to-Noise Ratio
    SNR = "snr"   # Signal-to-Noise Ratio
    THD_N = "thd_n"  # Total Harmonic Distortion + Noise
    PESQ = "pesq"  # Perceptual Evaluation of Speech Quality
    STOI = "stoi"  # Short-Time Objective Intelligibility
    SPECTRAL_DISTANCE = "spectral_distance"

@dataclass
class CodecParameters:
    """Paramètres de codec"""
    bitrate: Optional[int] = None  # bps
    sample_rate: Optional[int] = None  # Hz
    bit_depth: Optional[int] = None  # bits
    channels: Optional[int] = None
    quality: Optional[float] = None  # 0.0-1.0
    compression_level: Optional[int] = None
    vbr_mode: bool = False  # Variable Bitrate
    joint_stereo: bool = False
    metadata_encoding: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EncodingConfiguration:
    """Configuration d'encodage"""
    codec: AudioCodec
    mode: CompressionMode = CompressionMode.LOSSY_HIGH
    speed: EncodingSpeed = EncodingSpeed.MEDIUM
    parameters: CodecParameters = field(default_factory=CodecParameters)
    target_quality: float = 0.95  # 0.0-1.0
    preserve_metadata: bool = True
    enable_preprocessing: bool = True
    enable_postprocessing: bool = True
    parallel_processing: bool = True
    max_workers: int = 4

@dataclass
class EncodingResult:
    """Résultat d'encodage"""
    encoded_file_path: str
    original_size: int  # bytes
    encoded_size: int  # bytes
    compression_ratio: float
    encoding_time: float
    quality_metrics: Dict[QualityMetric, float]
    bitrate_achieved: int  # bps
    codec_used: AudioCodec
    parameters_used: CodecParameters
    metadata: Dict[str, Any]

class AudioPreprocessor:
    """Préprocesseur audio pour l'encodage"""
    
    def __init__(self):
        self.default_sample_rate = 44100
        self.default_bit_depth = 16
    
    async def preprocess_for_encoding(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_codec: AudioCodec,
        target_params: CodecParameters
    ) -> tuple[np.ndarray, int, Dict[str, Any]]:
        """Prétraite l'audio pour l'encodage"""
        
        processed_audio = audio.copy()
        processing_info = {}
        
        # Conversion de sample rate si nécessaire
        target_sr = target_params.sample_rate or sample_rate
        if sample_rate != target_sr:
            processed_audio = librosa.resample(
                processed_audio, orig_sr=sample_rate, target_sr=target_sr
            )
            processing_info['sample_rate_converted'] = True
            processing_info['original_sample_rate'] = sample_rate
            processing_info['target_sample_rate'] = target_sr
            sample_rate = target_sr
        
        # Conversion de canaux si nécessaire
        target_channels = target_params.channels
        if target_channels and len(processed_audio.shape) > 1:
            if target_channels == 1 and processed_audio.shape[0] > 1:
                # Convertir en mono
                processed_audio = np.mean(processed_audio, axis=0)
                processing_info['converted_to_mono'] = True
            elif target_channels == 2 and processed_audio.shape[0] == 1:
                # Convertir en stéréo
                processed_audio = np.array([processed_audio[0], processed_audio[0]])
                processing_info['converted_to_stereo'] = True
        
        # Normalisation pour éviter le clipping
        peak = np.max(np.abs(processed_audio))
        if peak > 0.99:
            processed_audio = processed_audio * (0.99 / peak)
            processing_info['peak_normalized'] = True
            processing_info['original_peak'] = float(peak)
        
        # Dithering pour la conversion de bit depth
        if target_params.bit_depth and target_params.bit_depth < 24:
            processed_audio = await self._apply_dithering(
                processed_audio, target_params.bit_depth
            )
            processing_info['dithering_applied'] = True
        
        # Filtrage anti-aliasing si nécessaire
        if target_sr < sample_rate:
            processed_audio = await self._apply_anti_aliasing_filter(
                processed_audio, sample_rate, target_sr
            )
            processing_info['anti_aliasing_applied'] = True
        
        return processed_audio, sample_rate, processing_info
    
    async def _apply_dithering(
        self,
        audio: np.ndarray,
        target_bit_depth: int
    ) -> np.ndarray:
        """Applique le dithering pour la conversion de bit depth"""
        # TPDF (Triangular Probability Density Function) dithering
        noise_amplitude = 1.0 / (2 ** target_bit_depth)
        
        # Générer du bruit triangulaire
        noise1 = np.random.uniform(-noise_amplitude, noise_amplitude, audio.shape)
        noise2 = np.random.uniform(-noise_amplitude, noise_amplitude, audio.shape)
        triangular_noise = noise1 + noise2
        
        # Ajouter le bruit de dithering
        dithered_audio = audio + triangular_noise
        
        # Quantifier
        quantization_step = 2.0 / (2 ** target_bit_depth)
        quantized_audio = np.round(dithered_audio / quantization_step) * quantization_step
        
        return quantized_audio
    
    async def _apply_anti_aliasing_filter(
        self,
        audio: np.ndarray,
        original_sr: int,
        target_sr: int
    ) -> np.ndarray:
        """Applique un filtre anti-aliasing"""
        from scipy.signal import butter, filtfilt
        
        # Fréquence de coupure à 80% de la nouvelle fréquence de Nyquist
        nyquist = target_sr / 2
        cutoff = 0.8 * nyquist
        
        # Filtre passe-bas Butterworth
        normalized_cutoff = cutoff / (original_sr / 2)
        if normalized_cutoff < 1.0:
            b, a = butter(8, normalized_cutoff, btype='low')
            
            if len(audio.shape) == 1:
                filtered_audio = filtfilt(b, a, audio)
            else:
                filtered_audio = np.array([
                    filtfilt(b, a, audio[ch]) for ch in range(audio.shape[0])
                ])
            
            return filtered_audio
        
        return audio

class QualityAnalyzer:
    """Analyseur de qualité audio"""
    
    def __init__(self):
        pass
    
    async def analyze_quality(
        self,
        original_audio: np.ndarray,
        encoded_audio: np.ndarray,
        sample_rate: int
    ) -> Dict[QualityMetric, float]:
        """Analyse la qualité entre l'audio original et encodé"""
        
        # Synchroniser les longueurs
        min_length = min(len(original_audio), len(encoded_audio))
        orig = original_audio[:min_length]
        enc = encoded_audio[:min_length]
        
        metrics = {}
        
        # Signal-to-Noise Ratio
        metrics[QualityMetric.SNR] = await self._calculate_snr(orig, enc)
        
        # Peak Signal-to-Noise Ratio
        metrics[QualityMetric.PSNR] = await self._calculate_psnr(orig, enc)
        
        # Total Harmonic Distortion + Noise
        metrics[QualityMetric.THD_N] = await self._calculate_thd_n(orig, enc, sample_rate)
        
        # Distance spectrale
        metrics[QualityMetric.SPECTRAL_DISTANCE] = await self._calculate_spectral_distance(
            orig, enc, sample_rate
        )
        
        return metrics
    
    async def _calculate_snr(self, original: np.ndarray, encoded: np.ndarray) -> float:
        """Calcule le Signal-to-Noise Ratio"""
        signal_power = np.mean(original ** 2)
        noise_power = np.mean((original - encoded) ** 2)
        
        if noise_power == 0:
            return float('inf')
        
        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)
    
    async def _calculate_psnr(self, original: np.ndarray, encoded: np.ndarray) -> float:
        """Calcule le Peak Signal-to-Noise Ratio"""
        max_signal = np.max(original) ** 2
        mse = np.mean((original - encoded) ** 2)
        
        if mse == 0:
            return float('inf')
        
        psnr = 10 * np.log10(max_signal / mse)
        return float(psnr)
    
    async def _calculate_thd_n(
        self,
        original: np.ndarray,
        encoded: np.ndarray,
        sample_rate: int
    ) -> float:
        """Calcule le Total Harmonic Distortion + Noise"""
        # Calculer la différence (bruit + distortion)
        noise = encoded - original
        
        # Puissance du signal
        signal_power = np.mean(original ** 2)
        
        # Puissance du bruit + distortion
        noise_power = np.mean(noise ** 2)
        
        if signal_power == 0:
            return 100.0  # 100% THD+N
        
        thd_n = 100 * np.sqrt(noise_power / signal_power)
        return float(thd_n)
    
    async def _calculate_spectral_distance(
        self,
        original: np.ndarray,
        encoded: np.ndarray,
        sample_rate: int
    ) -> float:
        """Calcule la distance spectrale entre les signaux"""
        # Calculer les spectres
        orig_fft = np.abs(np.fft.fft(original))
        enc_fft = np.abs(np.fft.fft(encoded))
        
        # Normaliser
        orig_fft = orig_fft / (np.sum(orig_fft) + 1e-8)
        enc_fft = enc_fft / (np.sum(enc_fft) + 1e-8)
        
        # Distance euclidienne
        distance = np.sqrt(np.sum((orig_fft - enc_fft) ** 2))
        return float(distance)

class FFmpegCodecManager:
    """Gestionnaire de codecs utilisant FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.codec_mappings = {
            AudioCodec.MP3: "libmp3lame",
            AudioCodec.AAC: "aac",
            AudioCodec.OGG_VORBIS: "libvorbis",
            AudioCodec.OPUS: "libopus",
            AudioCodec.FLAC: "flac",
            AudioCodec.ALAC: "alac",
            AudioCodec.AC3: "ac3",
            AudioCodec.PCM: "pcm_s16le"
        }
    
    def _find_ffmpeg(self) -> str:
        """Trouve l'exécutable FFmpeg"""
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Chemins communs
        common_paths = [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            'ffmpeg'
        ]
        
        for path in common_paths:
            try:
                subprocess.run([path, '-version'], capture_output=True, check=True)
                return path
            except:
                continue
        
        logger.warning("FFmpeg not found, some codec operations may fail")
        return 'ffmpeg'  # Fallback
    
    async def encode_with_ffmpeg(
        self,
        input_path: str,
        output_path: str,
        config: EncodingConfiguration
    ) -> Dict[str, Any]:
        """Encode avec FFmpeg"""
        
        cmd = [self.ffmpeg_path, '-i', input_path]
        
        # Codec
        if config.codec in self.codec_mappings:
            cmd.extend(['-c:a', self.codec_mappings[config.codec]])
        
        # Paramètres de qualité
        if config.parameters.bitrate:
            cmd.extend(['-b:a', f'{config.parameters.bitrate}'])
        
        if config.parameters.sample_rate:
            cmd.extend(['-ar', str(config.parameters.sample_rate)])
        
        if config.parameters.channels:
            cmd.extend(['-ac', str(config.parameters.channels)])
        
        # Qualité variable
        if config.parameters.vbr_mode and config.codec == AudioCodec.MP3:
            cmd.extend(['-q:a', '2'])  # VBR quality
        
        # Vitesse d'encodage
        if config.codec == AudioCodec.OPUS:
            speed_map = {
                EncodingSpeed.REALTIME: '10',
                EncodingSpeed.FAST: '6',
                EncodingSpeed.MEDIUM: '4',
                EncodingSpeed.SLOW: '2',
                EncodingSpeed.VERYSLOW: '0'
            }
            cmd.extend(['-compression_level', speed_map.get(config.speed, '4')])
        
        # Métadonnées
        if not config.preserve_metadata:
            cmd.append('-map_metadata')
            cmd.append('-1')
        
        cmd.extend(['-y', output_path])  # Overwrite output
        
        # Exécuter FFmpeg
        start_time = time.time()
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            encoding_time = time.time() - start_time
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg encoding failed: {stderr.decode()}")
            
            return {
                'encoding_time': encoding_time,
                'stdout': stdout.decode(),
                'stderr': stderr.decode(),
                'returncode': result.returncode
            }
            
        except Exception as e:
            logger.error(f"FFmpeg encoding error: {e}")
            raise

class AudioCodecManager:
    """Gestionnaire de codecs audio enterprise avec optimisation avancée"""
    
    def __init__(self):
        self.preprocessor = AudioPreprocessor()
        self.quality_analyzer = QualityAnalyzer()
        self.ffmpeg_manager = FFmpegCodecManager()
        
        # Configurations prédéfinies
        self.preset_configs = {
            "web_streaming": EncodingConfiguration(
                codec=AudioCodec.AAC,
                mode=CompressionMode.STREAMING,
                parameters=CodecParameters(bitrate=128000, sample_rate=44100, channels=2)
            ),
            "high_quality": EncodingConfiguration(
                codec=AudioCodec.FLAC,
                mode=CompressionMode.LOSSLESS,
                parameters=CodecParameters(sample_rate=44100, bit_depth=16)
            ),
            "podcast": EncodingConfiguration(
                codec=AudioCodec.MP3,
                mode=CompressionMode.LOSSY_MEDIUM,
                parameters=CodecParameters(bitrate=128000, sample_rate=44100, channels=1)
            ),
            "music_streaming": EncodingConfiguration(
                codec=AudioCodec.AAC,
                mode=CompressionMode.LOSSY_HIGH,
                parameters=CodecParameters(bitrate=256000, sample_rate=44100, channels=2)
            ),
            "broadcast": EncodingConfiguration(
                codec=AudioCodec.AC3,
                mode=CompressionMode.BROADCAST,
                parameters=CodecParameters(bitrate=384000, sample_rate=48000, channels=2)
            )
        }
        
        # Statistiques
        self.stats = {
            'total_encodings': 0,
            'encoding_times': [],
            'compression_ratios': [],
            'quality_scores': [],
            'codec_usage': {},
            'error_count': 0
        }
        
        logger.info("AudioCodecManager initialized successfully")
    
    async def encode_audio(
        self,
        input_path: str,
        output_path: str,
        config: EncodingConfiguration
    ) -> EncodingResult:
        """Encode un fichier audio"""
        start_time = time.time()
        
        try:
            # Charger l'audio original
            original_audio, sample_rate = sf.read(input_path)
            original_size = Path(input_path).stat().st_size
            
            # Prétraitement si activé
            if config.enable_preprocessing:
                processed_audio, sample_rate, preprocessing_info = await self.preprocessor.preprocess_for_encoding(
                    original_audio, sample_rate, config.codec, config.parameters
                )
            else:
                processed_audio = original_audio
                preprocessing_info = {}
            
            # Sauvegarder l'audio prétraité temporairement
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
            sf.write(temp_path, processed_audio.T if len(processed_audio.shape) > 1 else processed_audio, sample_rate)
            
            try:
                # Encodage avec FFmpeg
                encoding_info = await self.ffmpeg_manager.encode_with_ffmpeg(
                    temp_path, output_path, config
                )
                
                # Calculer les métriques
                encoded_size = Path(output_path).stat().st_size
                compression_ratio = original_size / encoded_size if encoded_size > 0 else 0
                
                # Analyser la qualité si possible
                quality_metrics = {}
                if config.enable_postprocessing:
                    try:
                        encoded_audio, _ = sf.read(output_path)
                        # Assurer la même longueur pour la comparaison
                        min_length = min(len(processed_audio), len(encoded_audio))
                        quality_metrics = await self.quality_analyzer.analyze_quality(
                            processed_audio[:min_length],
                            encoded_audio[:min_length],
                            sample_rate
                        )
                    except Exception as e:
                        logger.warning(f"Quality analysis failed: {e}")
                
                # Calculer le bitrate effectif
                duration = len(processed_audio) / sample_rate
                bitrate_achieved = int(encoded_size * 8 / duration) if duration > 0 else 0
                
                encoding_time = time.time() - start_time
                
                # Mettre à jour les statistiques
                await self._update_stats(encoding_time, compression_ratio, quality_metrics, config.codec)
                
                result = EncodingResult(
                    encoded_file_path=output_path,
                    original_size=original_size,
                    encoded_size=encoded_size,
                    compression_ratio=compression_ratio,
                    encoding_time=encoding_time,
                    quality_metrics=quality_metrics,
                    bitrate_achieved=bitrate_achieved,
                    codec_used=config.codec,
                    parameters_used=config.parameters,
                    metadata={
                        'preprocessing_info': preprocessing_info,
                        'encoding_info': encoding_info,
                        'input_file': input_path,
                        'output_file': output_path,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                return result
                
            finally:
                # Nettoyer le fichier temporaire
                try:
                    Path(temp_path).unlink()
                except:
                    pass
                    
        except Exception as e:
            self.stats['error_count'] += 1
            logger.error(f"Encoding failed: {e}")
            raise
    
    async def batch_encode_directory(
        self,
        input_directory: str,
        output_directory: str,
        config: EncodingConfiguration,
        file_pattern: str = "*.wav"
    ) -> List[EncodingResult]:
        """Encode tous les fichiers d'un répertoire"""
        
        input_path = Path(input_directory)
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        tasks = []
        
        # Collecter tous les fichiers à traiter
        for input_file in input_path.glob(file_pattern):
            output_file = output_path / f"{input_file.stem}.{self._get_file_extension(config.codec)}"
            
            if config.parallel_processing:
                task = self.encode_audio(str(input_file), str(output_file), config)
                tasks.append(task)
            else:
                try:
                    result = await self.encode_audio(str(input_file), str(output_file), config)
                    results.append(result)
                    logger.info(f"Encoded: {input_file.name}")
                except Exception as e:
                    logger.error(f"Failed to encode {input_file.name}: {e}")
        
        # Traitement parallèle si activé
        if tasks:
            try:
                # Limiter le nombre de tâches concurrentes
                semaphore = asyncio.Semaphore(config.max_workers)
                
                async def limited_encode(task):
                    async with semaphore:
                        return await task
                
                batch_results = await asyncio.gather(
                    *[limited_encode(task) for task in tasks],
                    return_exceptions=True
                )
                
                for i, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Batch encoding error: {result}")
                    else:
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
        
        return results
    
    async def optimize_for_platform(
        self,
        input_path: str,
        platform: str,
        target_quality: float = 0.9
    ) -> EncodingConfiguration:
        """Optimise la configuration pour une plateforme spécifique"""
        
        platform_configs = {
            'youtube': {
                'codec': AudioCodec.AAC,
                'bitrate': 128000,
                'sample_rate': 44100,
                'channels': 2
            },
            'spotify': {
                'codec': AudioCodec.OGG_VORBIS,
                'bitrate': 160000,
                'sample_rate': 44100,
                'channels': 2
            },
            'apple_music': {
                'codec': AudioCodec.AAC,
                'bitrate': 256000,
                'sample_rate': 44100,
                'channels': 2
            },
            'tidal': {
                'codec': AudioCodec.FLAC,
                'sample_rate': 44100,
                'bit_depth': 16,
                'channels': 2
            },
            'soundcloud': {
                'codec': AudioCodec.MP3,
                'bitrate': 128000,
                'sample_rate': 44100,
                'channels': 2
            },
            'podcast': {
                'codec': AudioCodec.MP3,
                'bitrate': 64000,
                'sample_rate': 22050,
                'channels': 1
            }
        }
        
        if platform.lower() not in platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        platform_config = platform_configs[platform.lower()]
        
        # Analyser l'audio source pour optimiser
        try:
            audio, sample_rate = sf.read(input_path)
            source_info = await self._analyze_source_audio(audio, sample_rate)
            
            # Ajuster la configuration basée sur l'analyse
            if source_info['is_mono'] and platform_config['channels'] == 2:
                platform_config['channels'] = 1
                # Réduire le bitrate pour mono
                if platform_config.get('bitrate'):
                    platform_config['bitrate'] = int(platform_config['bitrate'] * 0.7)
            
        except Exception as e:
            logger.warning(f"Source analysis failed: {e}")
        
        # Créer la configuration
        params = CodecParameters(
            bitrate=platform_config.get('bitrate'),
            sample_rate=platform_config.get('sample_rate'),
            bit_depth=platform_config.get('bit_depth'),
            channels=platform_config.get('channels'),
            quality=target_quality
        )
        
        config = EncodingConfiguration(
            codec=AudioCodec(platform_config['codec']),
            mode=CompressionMode.STREAMING if platform_config.get('bitrate') else CompressionMode.LOSSLESS,
            parameters=params,
            target_quality=target_quality
        )
        
        return config
    
    async def _analyze_source_audio(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Analyse l'audio source"""
        
        analysis = {}
        
        # Détection mono/stéréo
        if len(audio.shape) == 1:
            analysis['is_mono'] = True
            analysis['channels'] = 1
        else:
            analysis['channels'] = audio.shape[0]
            # Vérifier si c'est du pseudo-stéréo
            if audio.shape[0] == 2:
                correlation = np.corrcoef(audio[0], audio[1])[0, 1]
                analysis['is_mono'] = correlation > 0.99
            else:
                analysis['is_mono'] = False
        
        # Analyse spectrale
        fft = np.abs(np.fft.fft(audio.flatten()))
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
        
        # Fréquence maximale effective
        energy_threshold = 0.01 * np.max(fft)
        effective_max_freq = 0
        
        for i, (freq, magnitude) in enumerate(zip(freqs[:len(freqs)//2], fft[:len(fft)//2])):
            if magnitude > energy_threshold:
                effective_max_freq = freq
        
        analysis['effective_bandwidth'] = effective_max_freq
        analysis['can_downsample'] = effective_max_freq < sample_rate / 4
        
        # Analyse dynamique
        rms = np.sqrt(np.mean(audio.flatten() ** 2))
        peak = np.max(np.abs(audio.flatten()))
        analysis['dynamic_range'] = 20 * np.log10(peak / (rms + 1e-8))
        analysis['is_heavily_compressed'] = analysis['dynamic_range'] < 6.0
        
        return analysis
    
    def _get_file_extension(self, codec: AudioCodec) -> str:
        """Retourne l'extension de fichier pour un codec"""
        extensions = {
            AudioCodec.MP3: 'mp3',
            AudioCodec.AAC: 'm4a',
            AudioCodec.OGG_VORBIS: 'ogg',
            AudioCodec.OPUS: 'opus',
            AudioCodec.FLAC: 'flac',
            AudioCodec.ALAC: 'm4a',
            AudioCodec.WV: 'wv',
            AudioCodec.AC3: 'ac3',
            AudioCodec.PCM: 'wav'
        }
        return extensions.get(codec, 'audio')
    
    async def _update_stats(
        self,
        encoding_time: float,
        compression_ratio: float,
        quality_metrics: Dict[QualityMetric, float],
        codec: AudioCodec
    ):
        """Met à jour les statistiques"""
        self.stats['total_encodings'] += 1
        self.stats['encoding_times'].append(encoding_time)
        self.stats['compression_ratios'].append(compression_ratio)
        
        # Score de qualité global
        if quality_metrics:
            # Calculer un score composite
            snr = quality_metrics.get(QualityMetric.SNR, 0)
            quality_score = min(100, max(0, snr * 2))  # Approximation
            self.stats['quality_scores'].append(quality_score)
        
        # Usage des codecs
        codec_name = codec.value
        if codec_name not in self.stats['codec_usage']:
            self.stats['codec_usage'][codec_name] = 0
        self.stats['codec_usage'][codec_name] += 1
        
        # Limiter la taille des listes
        for key in ['encoding_times', 'compression_ratios', 'quality_scores']:
            if len(self.stats[key]) > 1000:
                self.stats[key] = self.stats[key][-1000:]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du gestionnaire de codecs"""
        stats = self.stats.copy()
        
        if stats['encoding_times']:
            stats['average_encoding_time'] = np.mean(stats['encoding_times'])
            stats['encoding_time_std'] = np.std(stats['encoding_times'])
        
        if stats['compression_ratios']:
            stats['average_compression_ratio'] = np.mean(stats['compression_ratios'])
        
        if stats['quality_scores']:
            stats['average_quality_score'] = np.mean(stats['quality_scores'])
        
        return stats
    
    def get_preset_config(self, preset_name: str) -> EncodingConfiguration:
        """Retourne une configuration prédéfinie"""
        if preset_name not in self.preset_configs:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        return self.preset_configs[preset_name]
    
    async def test_codec_performance(
        self,
        test_audio_path: str,
        codecs_to_test: List[AudioCodec]
    ) -> Dict[AudioCodec, Dict[str, float]]:
        """Teste les performances de différents codecs"""
        
        results = {}
        
        for codec in codecs_to_test:
            try:
                # Configuration de test
                config = EncodingConfiguration(
                    codec=codec,
                    mode=CompressionMode.LOSSY_HIGH,
                    parameters=CodecParameters(bitrate=128000)
                )
                
                # Fichier de sortie temporaire
                with tempfile.NamedTemporaryFile(suffix=f'.{self._get_file_extension(codec)}', delete=False) as temp_file:
                    temp_output = temp_file.name
                
                try:
                    # Encoder
                    result = await self.encode_audio(test_audio_path, temp_output, config)
                    
                    results[codec] = {
                        'encoding_time': result.encoding_time,
                        'compression_ratio': result.compression_ratio,
                        'bitrate_achieved': result.bitrate_achieved,
                        'file_size': result.encoded_size
                    }
                    
                    # Ajouter les métriques de qualité
                    for metric, value in result.quality_metrics.items():
                        results[codec][metric.value] = value
                        
                finally:
                    # Nettoyer
                    try:
                        Path(temp_output).unlink()
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Codec test failed for {codec}: {e}")
                results[codec] = {'error': str(e)}
        
        return results

# Factory functions
async def create_audio_codec_manager() -> AudioCodecManager:
    """Crée une instance du gestionnaire de codecs"""
    return AudioCodecManager()

async def create_encoding_config(
    codec: str,
    bitrate: Optional[int] = None,
    quality: float = 0.9
) -> EncodingConfiguration:
    """Crée une configuration d'encodage"""
    params = CodecParameters(
        bitrate=bitrate,
        quality=quality
    )
    
    return EncodingConfiguration(
        codec=AudioCodec(codec),
        parameters=params,
        target_quality=quality
    )

# Export des classes et fonctions principales
__all__ = [
    'AudioCodecManager',
    'AudioCodec',
    'CompressionMode',
    'EncodingSpeed',
    'QualityMetric',
    'CodecParameters',
    'EncodingConfiguration',
    'EncodingResult',
    'AudioPreprocessor',
    'QualityAnalyzer',
    'FFmpegCodecManager',
    'create_audio_codec_manager',
    'create_encoding_config'
]