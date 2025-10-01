"""🔄 Enterprise Audio Format Converter - Universal Format Support & Optimization
===============================================================================

Convertisseur de formats audio enterprise avec support universel, préservation
qualité et optimisation multi-plateforme pour créateurs sur IA Chéries.

Expert Roles Implementation:
🏗️ Backend Senior: Architecture conversion + pipeline parallel + optimization
⚙️ DevOps: Automation processing + CDN integration + performance monitoring
🎵 Audio Engineer: Quality preservation + codec optimization + format specs
🔒 Sécurité: Format validation + content protection + secure processing
🧠 ML Engineer: Quality prediction + adaptive optimization + format selection

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation de conversion audio est la propriété intellectuelle
EXCLUSIVE de Fahed Mlaiel. Usage commercial non autorisé strictement INTERDIT.
"""

import asyncio
import logging
import numpy as np
import subprocess
import tempfile
import shutil
import json
import time
import uuid
import threading
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, BinaryIO, Generator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import io
import wave
import struct
import math
import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import aiofiles
import aiohttp
from collections import defaultdict
import librosa
import soundfile as sf
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC

logger = logging.getLogger(__name__)

class AudioCodec(Enum):
    """Codecs audio supportés"""
    PCM = "pcm"
    MP3 = "mp3"
    AAC = "aac"
    FLAC = "flac"
    OGG_VORBIS = "ogg"
    OPUS = "opus"
    M4A = "m4a"
    WAV = "wav"
    AIFF = "aiff"
    WMA = "wma"
    AC3 = "ac3"
    DTS = "dts"
    ALAC = "alac"
    AMR = "amr"
    WEBM = "webm"
    DSD = "dsd"

class ConversionQuality(Enum):
    """Niveaux de qualité de conversion"""
    LOWEST = "lowest"        # Compression maximale
    LOW = "low"             # Qualité web basique
    MEDIUM = "medium"       # Qualité standard
    HIGH = "high"           # Qualité premium
    LOSSLESS = "lossless"   # Sans perte
    ARCHIVAL = "archival"   # Archivage professionnel

class PlatformTarget(Enum):
    """Plateformes cibles avec specs optimisées"""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    DISCORD = "discord"
    TWITCH = "twitch"
    PODCAST_RSS = "podcast_rss"
    BROADCAST_RADIO = "broadcast_radio"
    MASTERING = "mastering"
    MOBILE_STREAMING = "mobile_streaming"
    WEB_STREAMING = "web_streaming"

class ConversionMode(Enum):
    """Modes de conversion"""
    FAST = "fast"           # Conversion rapide
    BALANCED = "balanced"   # Équilibre qualité/vitesse
    QUALITY = "quality"     # Qualité maximale
    REALTIME = "realtime"   # Temps réel
    BATCH = "batch"         # Traitement par lots

@dataclass
class AudioFormatSpec:
    """Spécifications de format audio"""
    codec: AudioCodec
    sample_rate: int
    bit_depth: Optional[int]
    channels: int
    bitrate: Optional[int]  # Pour codecs avec perte
    quality_setting: Optional[str]
    container_format: Optional[str]
    metadata_support: bool = True

@dataclass
class PlatformSpecs:
    """Spécifications plateforme"""
    recommended_format: AudioFormatSpec
    alternative_formats: List[AudioFormatSpec]
    max_file_size_mb: Optional[int]
    max_duration_seconds: Optional[int]
    supported_sample_rates: List[int]
    metadata_requirements: Dict[str, bool]
    loudness_standards: Optional[Dict[str, float]]

@dataclass
class ConversionConfig:
    """Configuration de conversion"""
    target_codec: AudioCodec
    quality: ConversionQuality
    platform_target: Optional[PlatformTarget] = None
    mode: ConversionMode = ConversionMode.BALANCED
    preserve_metadata: bool = True
    apply_loudness_normalization: bool = False
    target_loudness_lufs: float = -23.0
    custom_specs: Optional[AudioFormatSpec] = None
    output_directory: Optional[Path] = None
    parallel_processing: bool = True

@dataclass
class ConversionResult:
    """Résultat de conversion"""
    success: bool
    output_file_path: Optional[Path]
    output_audio_data: Optional[np.ndarray]
    original_format: AudioFormatSpec
    converted_format: AudioFormatSpec
    file_size_original: int
    file_size_converted: int
    quality_metrics: Dict[str, float]
    conversion_time: float
    metadata_preserved: Dict[str, Any]
    platform_compliance: bool
    error_message: Optional[str] = None

@dataclass
class BatchConversionJob:
    """Job de conversion par lots"""
    job_id: str
    input_files: List[Path]
    conversion_config: ConversionConfig
    progress: float = 0.0
    completed_files: List[ConversionResult] = field(default_factory=list)
    failed_files: List[tuple[Path, str]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

class PlatformSpecsRegistry:
    """Registre des spécifications plateformes"""
    
    def __init__(self):
        self.platform_specs = self._initialize_platform_specs()
    
    def _initialize_platform_specs(self) -> Dict[PlatformTarget, PlatformSpecs]:
        """Initialise les spécifications des plateformes"""
        
        return {
            PlatformTarget.YOUTUBE: PlatformSpecs(
                recommended_format=AudioFormatSpec(
                    codec=AudioCodec.AAC,
                    sample_rate=48000,
                    bit_depth=16,
                    channels=2,
                    bitrate=320,
                    quality_setting="high",
                    container_format="mp4"
                ),
                alternative_formats=[
                    AudioFormatSpec(AudioCodec.MP3, 44100, 16, 2, 320, "high", "mp3")
                ],
                max_file_size_mb=128000,  # 128GB
                max_duration_seconds=43200,  # 12 heures
                supported_sample_rates=[44100, 48000],
                metadata_requirements={
                    "title": True, "artist": True, "description": False
                },
                loudness_standards={"LUFS": -14.0, "peak": -1.0}
            ),
            
            PlatformTarget.SPOTIFY: PlatformSpecs(
                recommended_format=AudioFormatSpec(
                    codec=AudioCodec.FLAC,
                    sample_rate=44100,
                    bit_depth=16,
                    channels=2,
                    bitrate=None,
                    quality_setting="lossless",
                    container_format="flac"
                ),
                alternative_formats=[
                    AudioFormatSpec(AudioCodec.MP3, 44100, 16, 2, 320, "high", "mp3"),
                    AudioFormatSpec(AudioCodec.OGG_VORBIS, 44100, 16, 2, 320, "high", "ogg")
                ],
                max_file_size_mb=200,
                max_duration_seconds=None,
                supported_sample_rates=[44100, 48000, 88200, 96000],
                metadata_requirements={
                    "title": True, "artist": True, "album": True, "genre": True
                },
                loudness_standards={"LUFS": -14.0, "peak": -2.0}
            ),
            
            PlatformTarget.TIKTOK: PlatformSpecs(
                recommended_format=AudioFormatSpec(
                    codec=AudioCodec.AAC,
                    sample_rate=44100,
                    bit_depth=16,
                    channels=2,
                    bitrate=128,
                    quality_setting="medium",
                    container_format="mp4"
                ),
                alternative_formats=[
                    AudioFormatSpec(AudioCodec.MP3, 44100, 16, 2, 128, "medium", "mp3")
                ],
                max_file_size_mb=500,
                max_duration_seconds=600,  # 10 minutes
                supported_sample_rates=[44100],
                metadata_requirements={
                    "title": False, "artist": False
                },
                loudness_standards={"LUFS": -16.0, "peak": -1.0}
            ),
            
            PlatformTarget.PODCAST_RSS: PlatformSpecs(
                recommended_format=AudioFormatSpec(
                    codec=AudioCodec.MP3,
                    sample_rate=44100,
                    bit_depth=16,
                    channels=2,
                    bitrate=128,
                    quality_setting="medium",
                    container_format="mp3"
                ),
                alternative_formats=[
                    AudioFormatSpec(AudioCodec.AAC, 44100, 16, 2, 128, "medium", "m4a")
                ],
                max_file_size_mb=500,
                max_duration_seconds=None,
                supported_sample_rates=[22050, 44100],
                metadata_requirements={
                    "title": True, "artist": True, "album": True, "description": True
                },
                loudness_standards={"LUFS": -16.0, "peak": -3.0}
            ),
            
            PlatformTarget.MASTERING: PlatformSpecs(
                recommended_format=AudioFormatSpec(
                    codec=AudioCodec.WAV,
                    sample_rate=96000,
                    bit_depth=24,
                    channels=2,
                    bitrate=None,
                    quality_setting="lossless",
                    container_format="wav"
                ),
                alternative_formats=[
                    AudioFormatSpec(AudioCodec.FLAC, 96000, 24, 2, None, "lossless", "flac"),
                    AudioFormatSpec(AudioCodec.AIFF, 96000, 24, 2, None, "lossless", "aiff")
                ],
                max_file_size_mb=None,
                max_duration_seconds=None,
                supported_sample_rates=[44100, 48000, 88200, 96000, 192000],
                metadata_requirements={
                    "title": True, "artist": True, "album": True, "isrc": True
                },
                loudness_standards=None  # Pas de normalisation pour mastering
            )
        }
    
    def get_platform_specs(self, platform: PlatformTarget) -> PlatformSpecs:
        """Retourne les spécifications d'une plateforme"""
        return self.platform_specs.get(platform, self._get_default_specs())
    
    def _get_default_specs(self) -> PlatformSpecs:
        """Spécifications par défaut"""
        return PlatformSpecs(
            recommended_format=AudioFormatSpec(
                codec=AudioCodec.MP3,
                sample_rate=44100,
                bit_depth=16,
                channels=2,
                bitrate=192,
                quality_setting="medium",
                container_format="mp3"
            ),
            alternative_formats=[],
            max_file_size_mb=100,
            max_duration_seconds=3600,
            supported_sample_rates=[44100, 48000],
            metadata_requirements={"title": True, "artist": True},
            loudness_standards={"LUFS": -18.0, "peak": -1.0}
        )

class AudioFormatAnalyzer:
    """Analyseur de formats audio"""
    
    def __init__(self):
        self.supported_extensions = {
            '.wav': AudioCodec.WAV,
            '.mp3': AudioCodec.MP3,
            '.flac': AudioCodec.FLAC,
            '.aac': AudioCodec.AAC,
            '.m4a': AudioCodec.M4A,
            '.ogg': AudioCodec.OGG_VORBIS,
            '.opus': AudioCodec.OPUS,
            '.aiff': AudioCodec.AIFF,
            '.aif': AudioCodec.AIFF,
            '.wma': AudioCodec.WMA
        }
    
    def analyze_audio_file(self, file_path: Path) -> AudioFormatSpec:
        """Analyse un fichier audio et extrait ses spécifications"""
        
        try:
            # Utilisation de librosa pour l'analyse de base
            audio_data, sample_rate = librosa.load(str(file_path), sr=None, mono=False)
            
            # Détection du nombre de canaux
            if audio_data.ndim == 1:
                channels = 1
            else:
                channels = audio_data.shape[0]
            
            # Détection du codec depuis l'extension
            extension = file_path.suffix.lower()
            codec = self.supported_extensions.get(extension, AudioCodec.WAV)
            
            # Analyse avec soundfile pour plus de détails
            with sf.SoundFile(str(file_path)) as f:
                sample_rate = f.samplerate
                channels = f.channels
                bit_depth = None
                
                # Tentative de détection du bit depth
                if hasattr(f, 'subtype'):
                    subtype = f.subtype
                    if 'PCM_16' in subtype:
                        bit_depth = 16
                    elif 'PCM_24' in subtype:
                        bit_depth = 24
                    elif 'PCM_32' in subtype:
                        bit_depth = 32
                    elif 'FLOAT' in subtype:
                        bit_depth = 32  # Float est considéré comme 32-bit
            
            # Estimation du bitrate pour les codecs avec perte
            bitrate = None
            if codec in [AudioCodec.MP3, AudioCodec.AAC, AudioCodec.OGG_VORBIS]:
                file_size = file_path.stat().st_size
                duration = len(audio_data) / sample_rate if audio_data.ndim == 1 else len(audio_data[0]) / sample_rate
                if duration > 0:
                    bitrate = int((file_size * 8) / (duration * 1000))  # kbps
            
            return AudioFormatSpec(
                codec=codec,
                sample_rate=int(sample_rate),
                bit_depth=bit_depth,
                channels=int(channels),
                bitrate=bitrate,
                quality_setting=self._determine_quality_setting(codec, bitrate, bit_depth),
                container_format=extension[1:],  # Sans le point
                metadata_support=True
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse fichier {file_path}: {e}")
            return self._create_fallback_spec()
    
    def _determine_quality_setting(self, codec: AudioCodec, bitrate: Optional[int], 
                                  bit_depth: Optional[int]) -> str:
        """Détermine le niveau de qualité"""
        
        if codec in [AudioCodec.FLAC, AudioCodec.WAV, AudioCodec.AIFF, AudioCodec.ALAC]:
            return "lossless"
        
        if bitrate:
            if bitrate >= 320:
                return "high"
            elif bitrate >= 192:
                return "medium"
            elif bitrate >= 128:
                return "low"
            else:
                return "lowest"
        
        if bit_depth:
            if bit_depth >= 24:
                return "high"
            elif bit_depth >= 16:
                return "medium"
            else:
                return "low"
        
        return "medium"
    
    def _create_fallback_spec(self) -> AudioFormatSpec:
        """Crée une spec de fallback"""
        return AudioFormatSpec(
            codec=AudioCodec.WAV,
            sample_rate=44100,
            bit_depth=16,
            channels=2,
            bitrate=None,
            quality_setting="medium",
            container_format="wav"
        )

class FFmpegConverter:
    """Convertisseur utilisant FFmpeg pour performance optimale"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.conversion_presets = self._initialize_presets()
    
    def _find_ffmpeg(self) -> str:
        """Trouve l'exécutable FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'ffmpeg'
        except:
            pass
        
        # Chemins alternatifs
        possible_paths = [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg',
            'C:\\ffmpeg\\bin\\ffmpeg.exe'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise RuntimeError("FFmpeg non trouvé. Installation requise.")
    
    def _initialize_presets(self) -> Dict[tuple[AudioCodec, ConversionQuality], List[str]]:
        """Initialise les presets de conversion FFmpeg"""
        
        presets = {}
        
        # MP3 Presets
        presets[(AudioCodec.MP3, ConversionQuality.LOWEST)] = [
            '-codec:a', 'libmp3lame', '-b:a', '64k', '-ar', '22050'
        ]
        presets[(AudioCodec.MP3, ConversionQuality.LOW)] = [
            '-codec:a', 'libmp3lame', '-b:a', '128k', '-ar', '44100'
        ]
        presets[(AudioCodec.MP3, ConversionQuality.MEDIUM)] = [
            '-codec:a', 'libmp3lame', '-b:a', '192k', '-ar', '44100'
        ]
        presets[(AudioCodec.MP3, ConversionQuality.HIGH)] = [
            '-codec:a', 'libmp3lame', '-b:a', '320k', '-ar', '48000'
        ]
        
        # AAC Presets
        presets[(AudioCodec.AAC, ConversionQuality.LOW)] = [
            '-codec:a', 'aac', '-b:a', '128k', '-ar', '44100'
        ]
        presets[(AudioCodec.AAC, ConversionQuality.MEDIUM)] = [
            '-codec:a', 'aac', '-b:a', '192k', '-ar', '44100'
        ]
        presets[(AudioCodec.AAC, ConversionQuality.HIGH)] = [
            '-codec:a', 'aac', '-b:a', '320k', '-ar', '48000'
        ]
        
        # FLAC Presets
        presets[(AudioCodec.FLAC, ConversionQuality.LOSSLESS)] = [
            '-codec:a', 'flac', '-compression_level', '5', '-ar', '44100'
        ]
        presets[(AudioCodec.FLAC, ConversionQuality.ARCHIVAL)] = [
            '-codec:a', 'flac', '-compression_level', '8', '-ar', '96000'
        ]
        
        # WAV Presets
        presets[(AudioCodec.WAV, ConversionQuality.MEDIUM)] = [
            '-codec:a', 'pcm_s16le', '-ar', '44100'
        ]
        presets[(AudioCodec.WAV, ConversionQuality.HIGH)] = [
            '-codec:a', 'pcm_s24le', '-ar', '48000'
        ]
        presets[(AudioCodec.WAV, ConversionQuality.ARCHIVAL)] = [
            '-codec:a', 'pcm_s24le', '-ar', '96000'
        ]
        
        # Opus Presets
        presets[(AudioCodec.OPUS, ConversionQuality.LOW)] = [
            '-codec:a', 'libopus', '-b:a', '64k', '-ar', '48000'
        ]
        presets[(AudioCodec.OPUS, ConversionQuality.MEDIUM)] = [
            '-codec:a', 'libopus', '-b:a', '128k', '-ar', '48000'
        ]
        presets[(AudioCodec.OPUS, ConversionQuality.HIGH)] = [
            '-codec:a', 'libopus', '-b:a', '256k', '-ar', '48000'
        ]
        
        # OGG Vorbis Presets
        presets[(AudioCodec.OGG_VORBIS, ConversionQuality.LOW)] = [
            '-codec:a', 'libvorbis', '-q:a', '3', '-ar', '44100'
        ]
        presets[(AudioCodec.OGG_VORBIS, ConversionQuality.MEDIUM)] = [
            '-codec:a', 'libvorbis', '-q:a', '5', '-ar', '44100'
        ]
        presets[(AudioCodec.OGG_VORBIS, ConversionQuality.HIGH)] = [
            '-codec:a', 'libvorbis', '-q:a', '8', '-ar', '48000'
        ]
        
        return presets
    
    async def convert_audio_async(self, input_path: Path, output_path: Path,
                                 target_spec: AudioFormatSpec,
                                 mode: ConversionMode = ConversionMode.BALANCED) -> bool:
        """Convertit un fichier audio de manière asynchrone"""
        
        try:
            # Construction de la commande FFmpeg
            cmd = [self.ffmpeg_path, '-i', str(input_path)]
            
            # Ajout des paramètres de conversion
            preset_key = (target_spec.codec, self._spec_to_quality(target_spec))
            preset_args = self.conversion_presets.get(preset_key, [])
            
            if preset_args:
                cmd.extend(preset_args)
            else:
                # Configuration manuelle si pas de preset
                cmd.extend(self._build_manual_config(target_spec))
            
            # Configuration selon le mode
            if mode == ConversionMode.FAST:
                cmd.extend(['-threads', '0', '-preset', 'ultrafast'])
            elif mode == ConversionMode.QUALITY:
                cmd.extend(['-threads', '0', '-preset', 'slow'])
            elif mode == ConversionMode.REALTIME:
                cmd.extend(['-threads', '1', '-preset', 'veryfast'])
            
            # Paramètres de sortie
            cmd.extend(['-y', str(output_path)])
            
            # Exécution asynchrone
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Conversion réussie: {input_path} -> {output_path}")
                return True
            else:
                logger.error(f"Erreur FFmpeg: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur conversion {input_path}: {e}")
            return False
    
    def _spec_to_quality(self, spec: AudioFormatSpec) -> ConversionQuality:
        """Convertit une spec en niveau de qualité"""
        
        if spec.quality_setting:
            quality_mapping = {
                "lowest": ConversionQuality.LOWEST,
                "low": ConversionQuality.LOW,
                "medium": ConversionQuality.MEDIUM,
                "high": ConversionQuality.HIGH,
                "lossless": ConversionQuality.LOSSLESS,
                "archival": ConversionQuality.ARCHIVAL
            }
            return quality_mapping.get(spec.quality_setting, ConversionQuality.MEDIUM)
        
        return ConversionQuality.MEDIUM
    
    def _build_manual_config(self, spec: AudioFormatSpec) -> List[str]:
        """Construit une configuration manuelle"""
        
        config = []
        
        # Codec
        codec_mapping = {
            AudioCodec.MP3: 'libmp3lame',
            AudioCodec.AAC: 'aac',
            AudioCodec.FLAC: 'flac',
            AudioCodec.OGG_VORBIS: 'libvorbis',
            AudioCodec.OPUS: 'libopus',
            AudioCodec.WAV: 'pcm_s16le'
        }
        
        codec = codec_mapping.get(spec.codec, 'pcm_s16le')
        config.extend(['-codec:a', codec])
        
        # Sample rate
        config.extend(['-ar', str(spec.sample_rate)])
        
        # Channels
        config.extend(['-ac', str(spec.channels)])
        
        # Bitrate pour codecs avec perte
        if spec.bitrate and spec.codec in [AudioCodec.MP3, AudioCodec.AAC, AudioCodec.OGG_VORBIS]:
            config.extend(['-b:a', f'{spec.bitrate}k'])
        
        return config

class QualityMetricsCalculator:
    """Calculateur de métriques de qualité"""
    
    def __init__(self):
        self.metrics_cache = {}
    
    def calculate_conversion_quality(self, original_audio: np.ndarray,
                                   converted_audio: np.ndarray,
                                   original_sr: int, converted_sr: int) -> Dict[str, float]:
        """Calcule les métriques de qualité de conversion"""
        
        metrics = {}
        
        # Alignement des audios pour comparaison
        if original_sr != converted_sr:
            # Resampling pour comparaison
            import librosa
            original_resampled = librosa.resample(original_audio, orig_sr=original_sr, target_sr=converted_sr)
        else:
            original_resampled = original_audio
        
        # Synchronisation de longueur
        min_length = min(len(original_resampled), len(converted_audio))
        orig_sync = original_resampled[:min_length]
        conv_sync = converted_audio[:min_length]
        
        # SNR (Signal-to-Noise Ratio)
        noise = conv_sync - orig_sync
        signal_power = np.mean(orig_sync ** 2)
        noise_power = np.mean(noise ** 2)
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = float('inf')
        
        metrics['snr_db'] = float(snr)
        
        # PESQ estimé (version simplifiée)
        correlation = np.corrcoef(orig_sync, conv_sync)[0, 1] if len(orig_sync) > 1 else 0
        pesq_estimate = 1.0 + 4.0 * max(0, correlation)
        metrics['pesq_estimate'] = float(pesq_estimate)
        
        # THD+N estimation
        thd_percent = (np.sqrt(noise_power) / np.sqrt(signal_power)) * 100 if signal_power > 0 else 100
        metrics['thd_percent'] = float(min(thd_percent, 100))
        
        # Analyse spectrale
        orig_spectrum = np.abs(np.fft.fft(orig_sync))
        conv_spectrum = np.abs(np.fft.fft(conv_sync))
        
        # Cohérence spectrale
        spectral_correlation = np.corrcoef(orig_spectrum, conv_spectrum)[0, 1] if len(orig_spectrum) > 1 else 0
        metrics['spectral_coherence'] = float(max(0, spectral_correlation))
        
        # Score de qualité global
        quality_score = (
            min(snr / 60, 1.0) * 0.4 +  # SNR normalisé
            (pesq_estimate - 1) / 4 * 0.3 +  # PESQ normalisé
            spectral_correlation * 0.3  # Cohérence spectrale
        )
        metrics['overall_quality'] = float(max(0, min(1, quality_score)))
        
        return metrics
    
    def estimate_perceived_quality(self, audio: np.ndarray, sample_rate: int,
                                  codec: AudioCodec, bitrate: Optional[int]) -> float:
        """Estime la qualité perçue basée sur les caractéristiques"""
        
        # Analyse des caractéristiques audio
        rms = np.sqrt(np.mean(audio ** 2))
        peak = np.max(np.abs(audio))
        dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
        
        # Score de base selon le codec
        codec_scores = {
            AudioCodec.WAV: 1.0,
            AudioCodec.FLAC: 0.98,
            AudioCodec.ALAC: 0.97,
            AudioCodec.AAC: 0.85,
            AudioCodec.MP3: 0.8,
            AudioCodec.OGG_VORBIS: 0.82,
            AudioCodec.OPUS: 0.87
        }
        
        base_score = codec_scores.get(codec, 0.7)
        
        # Ajustement selon le bitrate
        if bitrate:
            if bitrate >= 320:
                bitrate_factor = 1.0
            elif bitrate >= 192:
                bitrate_factor = 0.9
            elif bitrate >= 128:
                bitrate_factor = 0.8
            else:
                bitrate_factor = 0.6
        else:
            bitrate_factor = 1.0  # Lossless
        
        # Ajustement selon la plage dynamique
        if dynamic_range > 20:
            dynamic_factor = 1.0
        elif dynamic_range > 10:
            dynamic_factor = 0.9
        else:
            dynamic_factor = 0.8
        
        # Score final
        perceived_quality = base_score * bitrate_factor * dynamic_factor
        return float(max(0, min(1, perceived_quality)))

class AudioFormatConverter:
    """Convertisseur de formats audio enterprise principal"""
    
    def __init__(self):
        self.platform_registry = PlatformSpecsRegistry()
        self.format_analyzer = AudioFormatAnalyzer()
        self.ffmpeg_converter = FFmpegConverter()
        self.quality_calculator = QualityMetricsCalculator()
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.process_executor = ProcessPoolExecutor(max_workers=4)
        self.conversion_cache = {}
        self.active_jobs = {}
        
        logger.info("🔄 Audio Format Converter initialized - Fahed Mlaiel Enterprise")
    
    async def convert_single_async(self, input_data: Union[Path, np.ndarray],
                                  config: ConversionConfig,
                                  output_path: Optional[Path] = None) -> ConversionResult:
        """Convertit un seul fichier audio de manière asynchrone"""
        
        start_time = time.time()
        
        try:
            # Préparation des fichiers
            if isinstance(input_data, Path):
                input_path = input_data
                # Analyse du format d'entrée
                original_format = self.format_analyzer.analyze_audio_file(input_path)
            else:
                # Création d'un fichier temporaire depuis numpy array
                input_path = await self._numpy_to_temp_file(input_data)
                original_format = self._infer_format_from_array(input_data)
            
            # Détermination du format cible
            target_format = self._determine_target_format(config, original_format)
            
            # Génération du chemin de sortie
            if not output_path:
                output_path = self._generate_output_path(input_path, target_format, config)
            
            # Vérification de compliance plateforme
            platform_compliance = True
            if config.platform_target:
                platform_compliance = self._check_platform_compliance(target_format, config.platform_target)
            
            # Cache check
            cache_key = self._generate_cache_key(input_path, config)
            if cache_key in self.conversion_cache:
                logger.info(f"Utilisation cache pour {input_path}")
                cached_result = self.conversion_cache[cache_key]
                cached_result.conversion_time = time.time() - start_time
                return cached_result
            
            # Conversion
            conversion_success = await self.ffmpeg_converter.convert_audio_async(
                input_path, output_path, target_format, config.mode
            )
            
            if not conversion_success:
                return ConversionResult(
                    success=False,
                    output_file_path=None,
                    output_audio_data=None,
                    original_format=original_format,
                    converted_format=target_format,
                    file_size_original=input_path.stat().st_size if input_path.exists() else 0,
                    file_size_converted=0,
                    quality_metrics={},
                    conversion_time=time.time() - start_time,
                    metadata_preserved={},
                    platform_compliance=False,
                    error_message="Échec conversion FFmpeg"
                )
            
            # Calcul des métriques qualité
            quality_metrics = {}
            if config.mode in [ConversionMode.QUALITY, ConversionMode.BALANCED]:
                quality_metrics = await self._calculate_quality_metrics_async(
                    input_path, output_path, original_format, target_format
                )
            
            # Préservation métadonnées
            metadata_preserved = {}
            if config.preserve_metadata:
                metadata_preserved = await self._preserve_metadata_async(input_path, output_path)
            
            # Normalisation loudness si demandée
            if config.apply_loudness_normalization:
                await self._apply_loudness_normalization_async(output_path, config.target_loudness_lufs)
            
            # Chargement audio résultat si demandé
            output_audio_data = None
            if config.mode == ConversionMode.REALTIME:
                output_audio_data, _ = librosa.load(str(output_path), sr=None)
            
            # Calcul tailles fichiers
            original_size = input_path.stat().st_size if input_path.exists() else 0
            converted_size = output_path.stat().st_size if output_path.exists() else 0
            
            result = ConversionResult(
                success=True,
                output_file_path=output_path,
                output_audio_data=output_audio_data,
                original_format=original_format,
                converted_format=target_format,
                file_size_original=original_size,
                file_size_converted=converted_size,
                quality_metrics=quality_metrics,
                conversion_time=time.time() - start_time,
                metadata_preserved=metadata_preserved,
                platform_compliance=platform_compliance
            )
            
            # Mise en cache
            self.conversion_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur conversion {input_data}: {e}")
            return ConversionResult(
                success=False,
                output_file_path=None,
                output_audio_data=None,
                original_format=original_format if 'original_format' in locals() else AudioFormatSpec(AudioCodec.WAV, 44100, 16, 2, None, "medium", "wav"),
                converted_format=target_format if 'target_format' in locals() else AudioFormatSpec(AudioCodec.WAV, 44100, 16, 2, None, "medium", "wav"),
                file_size_original=0,
                file_size_converted=0,
                quality_metrics={},
                conversion_time=time.time() - start_time,
                metadata_preserved={},
                platform_compliance=False,
                error_message=str(e)
            )
    
    async def convert_batch_async(self, input_files: List[Path],
                                 config: ConversionConfig,
                                 progress_callback: Optional[callable] = None) -> BatchConversionJob:
        """Convertit plusieurs fichiers en lot"""
        
        job_id = str(uuid.uuid4())
        job = BatchConversionJob(
            job_id=job_id,
            input_files=input_files,
            conversion_config=config,
            start_time=datetime.now()
        )
        
        self.active_jobs[job_id] = job
        
        # Estimation du temps de completion
        estimated_time_per_file = 30  # secondes, estimation basique
        job.estimated_completion = job.start_time + timedelta(
            seconds=len(input_files) * estimated_time_per_file
        )
        
        try:
            # Traitement parallèle avec limitation
            max_concurrent = min(config.parallel_processing and 4 or 1, len(input_files))
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_file(file_path: Path) -> Optional[ConversionResult]:
                async with semaphore:
                    try:
                        result = await self.convert_single_async(file_path, config)
                        
                        if result.success:
                            job.completed_files.append(result)
                        else:
                            job.failed_files.append((file_path, result.error_message or "Erreur inconnue"))
                        
                        # Mise à jour du progrès
                        completed = len(job.completed_files) + len(job.failed_files)
                        job.progress = completed / len(input_files)
                        
                        if progress_callback:
                            await progress_callback(job)
                        
                        return result
                        
                    except Exception as e:
                        job.failed_files.append((file_path, str(e)))
                        return None
            
            # Lancement des conversions
            tasks = [process_file(file_path) for file_path in input_files]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            job.progress = 1.0
            
        except Exception as e:
            logger.error(f"Erreur batch conversion {job_id}: {e}")
            job.failed_files.extend([(f, str(e)) for f in input_files if f not in [r.output_file_path for r in job.completed_files]])
        
        finally:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
        
        return job
    
    def optimize_for_platform(self, platform: PlatformTarget, 
                             input_format: AudioFormatSpec) -> ConversionConfig:
        """Crée une configuration optimisée pour une plateforme"""
        
        platform_specs = self.platform_registry.get_platform_specs(platform)
        target_format = platform_specs.recommended_format
        
        # Détermination de la qualité optimale
        if input_format.codec in [AudioCodec.FLAC, AudioCodec.WAV, AudioCodec.AIFF]:
            # Source lossless - utiliser la meilleure qualité
            quality = ConversionQuality.HIGH
        else:
            # Source avec perte - qualité équilibrée
            quality = ConversionQuality.MEDIUM
        
        return ConversionConfig(
            target_codec=target_format.codec,
            quality=quality,
            platform_target=platform,
            mode=ConversionMode.BALANCED,
            preserve_metadata=True,
            apply_loudness_normalization=platform_specs.loudness_standards is not None,
            target_loudness_lufs=platform_specs.loudness_standards.get("LUFS", -23.0) if platform_specs.loudness_standards else -23.0,
            custom_specs=target_format
        )
    
    def _determine_target_format(self, config: ConversionConfig, 
                                original_format: AudioFormatSpec) -> AudioFormatSpec:
        """Détermine le format cible optimal"""
        
        if config.custom_specs:
            return config.custom_specs
        
        if config.platform_target:
            platform_specs = self.platform_registry.get_platform_specs(config.platform_target)
            return platform_specs.recommended_format
        
        # Format par défaut basé sur la qualité demandée
        quality_formats = {
            ConversionQuality.LOWEST: AudioFormatSpec(
                AudioCodec.MP3, 22050, 16, 1, 64, "lowest", "mp3"
            ),
            ConversionQuality.LOW: AudioFormatSpec(
                AudioCodec.MP3, 44100, 16, 2, 128, "low", "mp3"
            ),
            ConversionQuality.MEDIUM: AudioFormatSpec(
                AudioCodec.MP3, 44100, 16, 2, 192, "medium", "mp3"
            ),
            ConversionQuality.HIGH: AudioFormatSpec(
                AudioCodec.AAC, 48000, 16, 2, 320, "high", "aac"
            ),
            ConversionQuality.LOSSLESS: AudioFormatSpec(
                AudioCodec.FLAC, original_format.sample_rate, 16, original_format.channels, None, "lossless", "flac"
            ),
            ConversionQuality.ARCHIVAL: AudioFormatSpec(
                AudioCodec.WAV, max(48000, original_format.sample_rate), 24, original_format.channels, None, "archival", "wav"
            )
        }
        
        return quality_formats.get(config.quality, quality_formats[ConversionQuality.MEDIUM])
    
    def _check_platform_compliance(self, format_spec: AudioFormatSpec, 
                                  platform: PlatformTarget) -> bool:
        """Vérifie la compliance avec les specs de plateforme"""
        
        platform_specs = self.platform_registry.get_platform_specs(platform)
        
        # Vérification codec
        supported_codecs = [platform_specs.recommended_format.codec]
        supported_codecs.extend([spec.codec for spec in platform_specs.alternative_formats])
        
        if format_spec.codec not in supported_codecs:
            return False
        
        # Vérification sample rate
        if format_spec.sample_rate not in platform_specs.supported_sample_rates:
            return False
        
        return True
    
    def _generate_output_path(self, input_path: Path, target_format: AudioFormatSpec,
                             config: ConversionConfig) -> Path:
        """Génère le chemin de fichier de sortie"""
        
        if config.output_directory:
            output_dir = config.output_directory
        else:
            output_dir = input_path.parent
        
        # Nom de base
        base_name = input_path.stem
        
        # Extension selon le format
        extension_mapping = {
            AudioCodec.MP3: '.mp3',
            AudioCodec.AAC: '.aac',
            AudioCodec.M4A: '.m4a',
            AudioCodec.FLAC: '.flac',
            AudioCodec.OGG_VORBIS: '.ogg',
            AudioCodec.OPUS: '.opus',
            AudioCodec.WAV: '.wav',
            AudioCodec.AIFF: '.aiff'
        }
        
        extension = extension_mapping.get(target_format.codec, '.wav')
        
        # Suffixe qualité si nécessaire
        if config.quality != ConversionQuality.MEDIUM:
            base_name += f"_{config.quality.value}"
        
        # Suffixe plateforme si spécifiée
        if config.platform_target:
            base_name += f"_{config.platform_target.value}"
        
        output_path = output_dir / f"{base_name}{extension}"
        
        # Évitement des conflits
        counter = 1
        while output_path.exists():
            output_path = output_dir / f"{base_name}_{counter}{extension}"
            counter += 1
        
        return output_path
    
    async def _numpy_to_temp_file(self, audio_data: np.ndarray, 
                                 sample_rate: int = 44100) -> Path:
        """Convertit un array numpy en fichier temporaire"""
        
        temp_file = Path(tempfile.mktemp(suffix='.wav'))
        
        # Normalisation si nécessaire
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # Sauvegarde avec soundfile
        sf.write(str(temp_file), audio_data, sample_rate)
        
        return temp_file
    
    def _infer_format_from_array(self, audio_data: np.ndarray) -> AudioFormatSpec:
        """Infère le format depuis un array numpy"""
        
        channels = 1 if audio_data.ndim == 1 else audio_data.shape[0]
        
        return AudioFormatSpec(
            codec=AudioCodec.WAV,
            sample_rate=44100,  # Valeur par défaut
            bit_depth=32 if audio_data.dtype == np.float32 else 16,
            channels=channels,
            bitrate=None,
            quality_setting="high",
            container_format="wav"
        )
    
    async def _calculate_quality_metrics_async(self, input_path: Path, output_path: Path,
                                              original_format: AudioFormatSpec,
                                              converted_format: AudioFormatSpec) -> Dict[str, float]:
        """Calcule les métriques de qualité de manière asynchrone"""
        
        loop = asyncio.get_event_loop()
        
        def calculate_metrics():
            try:
                # Chargement des audios
                original_audio, orig_sr = librosa.load(str(input_path), sr=None)
                converted_audio, conv_sr = librosa.load(str(output_path), sr=None)
                
                return self.quality_calculator.calculate_conversion_quality(
                    original_audio, converted_audio, orig_sr, conv_sr
                )
            except Exception as e:
                logger.error(f"Erreur calcul métriques: {e}")
                return {"error": str(e)}
        
        return await loop.run_in_executor(self.executor, calculate_metrics)
    
    async def _preserve_metadata_async(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """Préserve les métadonnées de manière asynchrone"""
        
        preserved_metadata = {}
        
        try:
            # Lecture métadonnées source avec mutagen
            source_file = mutagen.File(str(input_path))
            if source_file:
                # Extraction des tags principaux
                preserved_metadata = {
                    "title": source_file.get("TIT2", [None])[0] if hasattr(source_file.get("TIT2", []), '__getitem__') else source_file.get("TITLE", [None])[0] if source_file.get("TITLE") else None,
                    "artist": source_file.get("TPE1", [None])[0] if hasattr(source_file.get("TPE1", []), '__getitem__') else source_file.get("ARTIST", [None])[0] if source_file.get("ARTIST") else None,
                    "album": source_file.get("TALB", [None])[0] if hasattr(source_file.get("TALB", []), '__getitem__') else source_file.get("ALBUM", [None])[0] if source_file.get("ALBUM") else None,
                    "date": source_file.get("TDRC", [None])[0] if hasattr(source_file.get("TDRC", []), '__getitem__') else source_file.get("DATE", [None])[0] if source_file.get("DATE") else None,
                    "genre": source_file.get("TCON", [None])[0] if hasattr(source_file.get("TCON", []), '__getitem__') else source_file.get("GENRE", [None])[0] if source_file.get("GENRE") else None
                }
                
                # Application au fichier destination
                dest_file = mutagen.File(str(output_path), easy=True)
                if dest_file:
                    for key, value in preserved_metadata.items():
                        if value:
                            if key in ["title", "artist", "album", "date", "genre"]:
                                dest_file[key] = str(value)
                    dest_file.save()
        
        except Exception as e:
            logger.warning(f"Erreur préservation métadonnées: {e}")
            preserved_metadata["error"] = str(e)
        
        return preserved_metadata
    
    async def _apply_loudness_normalization_async(self, audio_path: Path, target_lufs: float):
        """Applique la normalisation loudness"""
        
        try:
            # Chargement audio
            audio, sr = librosa.load(str(audio_path), sr=None)
            
            # Estimation loudness actuelle (approximation)
            rms = np.sqrt(np.mean(audio ** 2))
            current_lufs_estimate = 20 * np.log10(rms + 1e-10) - 9  # Approximation
            
            # Calcul du gain nécessaire
            gain_db = target_lufs - current_lufs_estimate
            gain_linear = 10 ** (gain_db / 20)
            
            # Application du gain avec limitation
            normalized_audio = audio * gain_linear
            
            # Limitation pour éviter l'écrêtage
            peak = np.max(np.abs(normalized_audio))
            if peak > 0.95:
                normalized_audio = normalized_audio * (0.95 / peak)
            
            # Sauvegarde
            sf.write(str(audio_path), normalized_audio, sr)
            
        except Exception as e:
            logger.error(f"Erreur normalisation loudness: {e}")
    
    def _generate_cache_key(self, input_path: Path, config: ConversionConfig) -> str:
        """Génère une clé de cache pour la conversion"""
        
        # Hash basé sur le fichier et la configuration
        file_hash = hashlib.md5(str(input_path).encode()).hexdigest()
        config_hash = hashlib.md5(str(config).encode()).hexdigest()
        
        return f"{file_hash}_{config_hash}"
    
    def get_supported_formats(self) -> List[AudioCodec]:
        """Retourne la liste des formats supportés"""
        return list(AudioCodec)
    
    def get_platform_requirements(self, platform: PlatformTarget) -> PlatformSpecs:
        """Retourne les exigences d'une plateforme"""
        return self.platform_registry.get_platform_specs(platform)

# Factory functions
def create_audio_format_converter() -> AudioFormatConverter:
    """Factory pour créer une instance du convertisseur"""
    return AudioFormatConverter()

def create_conversion_config(target_codec: str = "mp3", quality: str = "medium",
                           platform: Optional[str] = None) -> ConversionConfig:
    """Factory pour créer une configuration de conversion"""
    
    return ConversionConfig(
        target_codec=AudioCodec(target_codec),
        quality=ConversionQuality(quality),
        platform_target=PlatformTarget(platform) if platform else None
    )

# Export pour intégration
__all__ = [
    'AudioFormatConverter',
    'AudioCodec',
    'ConversionQuality',
    'PlatformTarget',
    'ConversionMode',
    'AudioFormatSpec',
    'ConversionConfig',
    'ConversionResult',
    'BatchConversionJob',
    'PlatformSpecs',
    'create_audio_format_converter',
    'create_conversion_config'
]