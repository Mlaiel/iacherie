"""
🎵 Audio Fingerprinting Engine - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/fingerprinting/audio_fingerprint.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Audio Fingerprinting - Ultra Enterprise Production-Ready
Responsibility: Advanced audio fingerprinting with Chromaprint, Essentia, and spectral analysis
===========================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC AUDIO FINGERPRINTING:
Audio Upload (Musicians/Influencers/Comédiens) → Format Validation → 
Audio Processing → Feature Extraction → Chromaprint Generation → 
Spectral Analysis → Mel Spectrogram → Vector Embedding → FAISS Indexing → 
Real-time Monitoring → Violation Detection → Revenue Protection

AUDIO FINGERPRINTING TECHNOLOGIES:
├── 🎼 Chromaprint (Acoustic Fingerprinting)
├── 🔊 Essentia (Music Information Retrieval)
├── 📊 Spectral Analysis (FFT + STFT)
├── 🎛️ Mel Spectrograms (MFCC Features)
├── 🧠 Deep Audio Features (CNN + RNN)
├── 🔍 Similarity Matching (Cosine + Euclidean)
├── ⚡ Real-time Processing (Stream + Batch)
└── 🛡️ Protection System (Monitoring + Alerts)
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import numpy as np
import asyncio
import logging
import librosa
import soundfile as sf
from pathlib import Path
import hashlib
import time
from datetime import datetime

# Audio processing libraries
try:
    import chromaprint
    CHROMAPRINT_AVAILABLE = True
except ImportError:
    CHROMAPRINT_AVAILABLE = False
    logging.warning("Chromaprint not available - install pyacouseid")

try:
    import essentia
    import essentia.standard as es
    ESSENTIA_AVAILABLE = True
except ImportError:
    ESSENTIA_AVAILABLE = False
    logging.warning("Essentia not available - install essentia-tensorflow")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

@dataclass
class AudioFingerprintConfig:
    """Configuration avancée pour le fingerprinting audio"""
    
    # Paramètres audio de base
    sample_rate: int = 22050
    duration_limit: int = 600  # 10 minutes max
    min_duration: float = 10.0  # 10 secondes min
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    
    # Chromaprint configuration
    chromaprint_enabled: bool = True
    chromaprint_algorithm: int = 2  # CHROMAPRINT_ALGORITHM_DEFAULT
    
    # Essentia configuration
    essentia_enabled: bool = True
    essentia_features: List[str] = field(default_factory=lambda: [
        "mfcc", "spectral_centroid", "spectral_rolloff", 
        "zero_crossing_rate", "chroma", "tonnetz"
    ])
    
    # Spectral analysis
    spectral_analysis: bool = True
    n_fft: int = 2048
    hop_length: int = 512
    n_mels: int = 128
    n_mfcc: int = 13
    
    # Feature extraction
    segment_duration: float = 30.0  # 30 seconds segments
    overlap_ratio: float = 0.5  # 50% overlap
    normalize_features: bool = True
    
    # Performance optimization
    parallel_processing: bool = True
    max_workers: int = 4
    batch_size: int = 32
    
    # Quality thresholds
    min_quality_score: float = 0.7
    noise_threshold: float = 0.1
    silence_threshold: float = 0.05
    use_gpu: bool = True
    batch_size: int = 16
    max_workers: int = 4

class AudioProcessor(ABC):
    """Classe abstraite pour les processeurs audio"""
    
    @abstractmethod
    async def process(self, audio_path: str, config: AudioFingerprintConfig) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass

class ChromaprintProcessor(AudioProcessor):
    """Processeur Chromaprint pour empreintes acoustiques"""
    
    def __init__(self):
        if not CHROMAPRINT_AVAILABLE:
            raise ImportError("Chromaprint library not available")
        self.algorithm = chromaprint.ALGORITHM_DEFAULT
    
    async def process(self, audio_path: str, config: AudioFingerprintConfig) -> Dict[str, Any]:
        """Génère une empreinte Chromaprint"""
        try:
            start_time = time.time()
            
            # Chargement audio
            audio, sr = librosa.load(audio_path, sr=config.sample_rate, mono=True)
            
            # Limitation de durée
            max_samples = int(config.duration_limit * sr)
            if len(audio) > max_samples:
                audio = audio[:max_samples]
            
            # Génération de l'empreinte Chromaprint
            # Note: chromaprint.encode prend des données audio brutes
            audio_int16 = (audio * 32767).astype(np.int16)
            
            fingerprint_raw, version = chromaprint.encode(config.chromaprint_algorithm, audio_int16, sr)
            fingerprint_hash = chromaprint.hash_fingerprint(fingerprint_raw)
            
            processing_time = time.time() - start_time
            
            return {
                "processor": "chromaprint",
                "fingerprint_raw": fingerprint_raw,
                "fingerprint_hash": fingerprint_hash,
                "version": version,
                "algorithm": config.chromaprint_algorithm,
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "processing_time": processing_time,
                "quality_score": self._calculate_quality_score(audio, sr)
            }
            
        except Exception as e:
            logger.error(f"Chromaprint processing failed: {e}")
            raise
    
    def get_name(self) -> str:
        return "chromaprint"
    
    def _calculate_quality_score(self, audio: np.ndarray, sr: int) -> float:
        """Calcule un score de qualité pour l'audio"""
        try:
            # Analyse RMS pour le niveau audio
            rms = librosa.feature.rms(y=audio)[0]
            rms_mean = np.mean(rms)
            
            # Analyse spectrale pour la richesse fréquentielle
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_mean = np.mean(spectral_centroid)
            
            # Score basé sur RMS et richesse spectrale
            quality_score = min(1.0, (rms_mean * 10 + spectral_mean / 5000) / 2)
            return float(quality_score)
            
        except Exception:
            return 0.5  # Score neutre en cas d'erreur

class EssentiaProcessor(AudioProcessor):
    """Processeur Essentia pour l'analyse musicale avancée"""
    
    def __init__(self):
        if not ESSENTIA_AVAILABLE:
            raise ImportError("Essentia library not available")
        
        # Initialisation des algorithmes Essentia
        self.windowing = es.Windowing(type='hann')
        self.spectrum = es.Spectrum()
        self.mfcc = es.MFCC()
        self.spectral_peaks = es.SpectralPeaks()
        self.harmonic_peaks = es.HarmonicPeaks()
    
    async def process(self, audio_path: str, config: AudioFingerprintConfig) -> Dict[str, Any]:
        """Analyse audio avec Essentia"""
        try:
            start_time = time.time()
            
            # Chargement audio
            audio, sr = librosa.load(audio_path, sr=config.sample_rate, mono=True)
            
            # Analyse par fenêtres
            frame_size = 1024
            hop_size = 512
            
            features = {
                "mfcc": [],
                "spectral_centroid": [],
                "spectral_rolloff": [],
                "zero_crossing_rate": [],
                "chroma": [],
                "tonnetz": [],
                "tempo": None,
                "key": None,
                "energy": []
            }
            
            # Traitement par frames
            for i in range(0, len(audio) - frame_size, hop_size):
                frame = audio[i:i + frame_size]
                
                # Fenêtrage et spectre
                windowed_frame = self.windowing(frame)
                spectrum = self.spectrum(windowed_frame)
                
                # MFCC
                mfcc_bands, mfcc_coeffs = self.mfcc(spectrum)
                features["mfcc"].append(mfcc_coeffs)
                
                # Énergie
                energy = np.sum(spectrum ** 2)
                features["energy"].append(energy)
            
            # Features globales avec librosa (plus robuste)
            features["spectral_centroid"] = librosa.feature.spectral_centroid(y=audio, sr=sr)[0].tolist()
            features["spectral_rolloff"] = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0].tolist()
            features["zero_crossing_rate"] = librosa.feature.zero_crossing_rate(audio)[0].tolist()
            features["chroma"] = librosa.feature.chroma_stft(y=audio, sr=sr).tolist()
            features["tonnetz"] = librosa.feature.tonnetz(y=audio, sr=sr).tolist()
            
            # Tempo et tonalité
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            features["tempo"] = float(tempo)
            
            # Analyse harmonique simple
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            key_profile = np.mean(chroma, axis=1)
            features["key"] = int(np.argmax(key_profile))
            
            processing_time = time.time() - start_time
            
            return {
                "processor": "essentia",
                "features": features,
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "processing_time": processing_time,
                "feature_vector": self._create_feature_vector(features)
            }
            
        except Exception as e:
            logger.error(f"Essentia processing failed: {e}")
            raise
    
    def get_name(self) -> str:
        return "essentia"
    
    def _create_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Crée un vecteur de caractéristiques unifié"""
        try:
            vector_parts = []
            
            # MFCC moyenné
            if features["mfcc"]:
                mfcc_mean = np.mean(features["mfcc"], axis=0)
                vector_parts.append(mfcc_mean)
            
            # Caractéristiques spectrales moyennées
            if features["spectral_centroid"]:
                vector_parts.append([np.mean(features["spectral_centroid"])])
            
            if features["spectral_rolloff"]:
                vector_parts.append([np.mean(features["spectral_rolloff"])])
            
            if features["zero_crossing_rate"]:
                vector_parts.append([np.mean(features["zero_crossing_rate"])])
            
            # Tempo et tonalité
            if features["tempo"]:
                vector_parts.append([features["tempo"] / 200.0])  # Normalisation
            
            if features["key"] is not None:
                key_one_hot = np.zeros(12)
                key_one_hot[features["key"]] = 1.0
                vector_parts.append(key_one_hot)
            
            # Chroma moyenné
            if features["chroma"]:
                chroma_mean = np.mean(features["chroma"], axis=1)
                vector_parts.append(chroma_mean)
            
            # Concaténation
            if vector_parts:
                feature_vector = np.concatenate(vector_parts)
                return feature_vector.astype(np.float32)
            else:
                return np.zeros(128, dtype=np.float32)
                
        except Exception as e:
            logger.warning(f"Feature vector creation failed: {e}")
            return np.zeros(128, dtype=np.float32)

class SpectralHashProcessor(AudioProcessor):
    """Processeur pour les hash spectraux avancés"""
    
    def __init__(self):
        pass
    
    async def process(self, audio_path: str, config: AudioFingerprintConfig) -> Dict[str, Any]:
        """Génère des hash spectraux"""
        try:
            start_time = time.time()
            
            # Chargement audio
            audio, sr = librosa.load(audio_path, sr=config.sample_rate, mono=True)
            
            # Analyse spectrale
            stft = librosa.stft(audio, n_fft=config.n_fft, hop_length=config.hop_length)
            magnitude = np.abs(stft)
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio, 
                sr=sr, 
                n_mels=config.n_mels,
                n_fft=config.n_fft,
                hop_length=config.hop_length
            )
            
            # Log mel spectrogram
            log_mel = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Spectral hash
            spectral_hash = self._compute_spectral_hash(magnitude)
            mel_hash = self._compute_mel_hash(log_mel)
            
            processing_time = time.time() - start_time
            
            return {
                "processor": "spectral_hash",
                "spectral_hash": spectral_hash,
                "mel_hash": mel_hash,
                "magnitude_shape": magnitude.shape,
                "mel_shape": log_mel.shape,
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "processing_time": processing_time,
                "spectral_features": self._extract_spectral_features(magnitude, log_mel)
            }
            
        except Exception as e:
            logger.error(f"Spectral hash processing failed: {e}")
            raise
    
    def get_name(self) -> str:
        return "spectral_hash"
    
    def _compute_spectral_hash(self, magnitude: np.ndarray) -> str:
        """Calcule un hash spectral"""
        try:
            # Réduction dimensionnelle par moyennage
            reduced = np.mean(magnitude, axis=1)
            
            # Quantification
            quantized = (reduced / np.max(reduced) * 255).astype(np.uint8)
            
            # Hash MD5
            hash_obj = hashlib.md5(quantized.tobytes())
            return hash_obj.hexdigest()
            
        except Exception:
            return "error_hash"
    
    def _compute_mel_hash(self, mel_spec: np.ndarray) -> str:
        """Calcule un hash mel"""
        try:
            # Réduction par moyennage temporel
            mel_mean = np.mean(mel_spec, axis=1)
            
            # Quantification
            quantized = ((mel_mean - np.min(mel_mean)) / 
                        (np.max(mel_mean) - np.min(mel_mean)) * 255).astype(np.uint8)
            
            # Hash SHA256
            hash_obj = hashlib.sha256(quantized.tobytes())
            return hash_obj.hexdigest()
            
        except Exception:
            return "error_mel_hash"
    
    def _extract_spectral_features(self, magnitude: np.ndarray, mel_spec: np.ndarray) -> Dict[str, float]:
        """Extrait des caractéristiques spectrales avancées"""
        try:
            features = {}
            
            # Caractéristiques de magnitude
            features["spectral_mean"] = float(np.mean(magnitude))
            features["spectral_std"] = float(np.std(magnitude))
            features["spectral_max"] = float(np.max(magnitude))
            features["spectral_energy"] = float(np.sum(magnitude ** 2))
            
            # Caractéristiques mel
            features["mel_mean"] = float(np.mean(mel_spec))
            features["mel_std"] = float(np.std(mel_spec))
            features["mel_range"] = float(np.max(mel_spec) - np.min(mel_spec))
            
            # Caractéristiques de distribution
            mel_flat = mel_spec.flatten()
            features["mel_skewness"] = float(self._calculate_skewness(mel_flat))
            features["mel_kurtosis"] = float(self._calculate_kurtosis(mel_flat))
            
            return features
            
        except Exception as e:
            logger.warning(f"Spectral features extraction failed: {e}")
            return {}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calcule l'asymétrie"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            return np.mean(((data - mean) / std) ** 3)
        except Exception:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calcule l'aplatissement"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            return np.mean(((data - mean) / std) ** 4) - 3.0
        except Exception:
            return 0.0

class MelSpectrogramProcessor(AudioProcessor):
    """Processeur pour spectrogrammes mel avancés"""
    
    def __init__(self):
        pass
    
    async def process(self, audio_path: str, config: AudioFingerprintConfig) -> Dict[str, Any]:
        """Traite les spectrogrammes mel"""
        try:
            start_time = time.time()
            
            # Chargement audio
            audio, sr = librosa.load(audio_path, sr=config.sample_rate, mono=True)
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=sr,
                n_mels=config.n_mels,
                n_fft=config.n_fft,
                hop_length=config.hop_length
            )
            
            # Log mel spectrogram
            log_mel = librosa.power_to_db(mel_spec, ref=np.max)
            
            # MFCC
            mfcc = librosa.feature.mfcc(
                y=audio,
                sr=sr,
                n_mfcc=config.n_mfcc,
                n_mels=config.n_mels,
                n_fft=config.n_fft,
                hop_length=config.hop_length
            )
            
            # Delta MFCC
            mfcc_delta = librosa.feature.delta(mfcc)
            mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
            
            processing_time = time.time() - start_time
            
            return {
                "processor": "mel_spectrogram",
                "mel_spectrogram": log_mel.tolist(),
                "mfcc": mfcc.tolist(),
                "mfcc_delta": mfcc_delta.tolist(),
                "mfcc_delta2": mfcc_delta2.tolist(),
                "mel_shape": log_mel.shape,
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "processing_time": processing_time,
                "feature_statistics": self._compute_feature_stats(log_mel, mfcc)
            }
            
        except Exception as e:
            logger.error(f"Mel spectrogram processing failed: {e}")
            raise
    
    def get_name(self) -> str:
        return "mel_spectrogram"
    
    def _compute_feature_stats(self, mel_spec: np.ndarray, mfcc: np.ndarray) -> Dict[str, Any]:
        """Calcule des statistiques sur les caractéristiques"""
        try:
            stats = {}
            
            # Statistiques mel
            stats["mel_mean"] = float(np.mean(mel_spec))
            stats["mel_std"] = float(np.std(mel_spec))
            stats["mel_min"] = float(np.min(mel_spec))
            stats["mel_max"] = float(np.max(mel_spec))
            
            # Statistiques MFCC
            stats["mfcc_mean"] = float(np.mean(mfcc))
            stats["mfcc_std"] = float(np.std(mfcc))
            stats["mfcc_min"] = float(np.min(mfcc))
            stats["mfcc_max"] = float(np.max(mfcc))
            
            # Entropie spectrale
            mel_flat = mel_spec.flatten()
            mel_norm = mel_flat - np.min(mel_flat)
            if np.max(mel_norm) > 0:
                mel_norm = mel_norm / np.max(mel_norm)
                mel_norm = mel_norm + 1e-10  # Éviter log(0)
                stats["spectral_entropy"] = float(-np.sum(mel_norm * np.log2(mel_norm)))
            else:
                stats["spectral_entropy"] = 0.0
            
            return stats
            
        except Exception as e:
            logger.warning(f"Feature statistics computation failed: {e}")
            return {}

class AudioFingerprintEngine:
    """
    Moteur principal de fingerprinting audio entreprise
    
    Combine Chromaprint, Essentia, analyse spectrale et MFCC
    pour créer des empreintes audio robustes et précises
    """
    
    def __init__(self, config: Optional[AudioFingerprintConfig] = None):
        self.config = config or AudioFingerprintConfig()
        
        # Initialisation des processeurs
        self.processors = {}
        
        if self.config.chromaprint_enabled and CHROMAPRINT_AVAILABLE:
            self.processors["chromaprint"] = ChromaprintProcessor()
        
        if self.config.essentia_enabled and ESSENTIA_AVAILABLE:
            self.processors["essentia"] = EssentiaProcessor()
        
        if self.config.spectral_analysis:
            self.processors["spectral_hash"] = SpectralHashProcessor()
            self.processors["mel_spectrogram"] = MelSpectrogramProcessor()
        
        logger.info(f"AudioFingerprintEngine initialized with {len(self.processors)} processors")
    
    async def generate_fingerprint(self, audio_path: str) -> Dict[str, Any]:
        """
        Génère une empreinte audio complète
        
        Args:
            audio_path: Chemin vers le fichier audio
            
        Returns:
            Dictionnaire contenant toutes les empreintes générées
        """
        try:
            start_time = datetime.now()
            
            # Validation du fichier
            self._validate_audio_file(audio_path)
            
            # Traitement par tous les processeurs
            fingerprint_data = {
                "audio_path": audio_path,
                "timestamp": start_time.isoformat(),
                "processors": {},
                "combined_features": {},
                "metadata": {}
            }
            
            # Exécution des processeurs
            for name, processor in self.processors.items():
                try:
                    result = await processor.process(audio_path, self.config)
                    fingerprint_data["processors"][name] = result
                    logger.info(f"Processor {name} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Processor {name} failed: {e}")
                    fingerprint_data["processors"][name] = {"error": str(e)}
            
            # Combinaison des caractéristiques
            fingerprint_data["combined_features"] = self._combine_features(
                fingerprint_data["processors"]
            )
            
            # Métadonnées finales
            processing_time = (datetime.now() - start_time).total_seconds()
            fingerprint_data["metadata"] = {
                "total_processing_time": processing_time,
                "processors_count": len(self.processors),
                "processors_success": len([
                    p for p in fingerprint_data["processors"].values() 
                    if "error" not in p
                ]),
                "config": {
                    "sample_rate": self.config.sample_rate,
                    "duration_limit": self.config.duration_limit,
                    "chromaprint_enabled": self.config.chromaprint_enabled,
                    "essentia_enabled": self.config.essentia_enabled,
                    "spectral_analysis": self.config.spectral_analysis
                }
            }
            
            logger.info(f"Audio fingerprint generated successfully in {processing_time:.2f}s")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Audio fingerprint generation failed: {e}")
            raise
    
    def _validate_audio_file(self, audio_path: str) -> None:
        """Valide le fichier audio"""
        path = Path(audio_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if path.stat().st_size > self.config.max_file_size:
            raise ValueError(f"File size exceeds limit: {path.stat().st_size} > {self.config.max_file_size}")
        
        # Validation du format
        valid_extensions = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff", ".wma"}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Unsupported audio format: {path.suffix}")
    
    def _combine_features(self, processors_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine les caractéristiques de tous les processeurs"""
        try:
            combined = {
                "primary_hashes": {},
                "feature_vectors": {},
                "statistics": {},
                "quality_metrics": {}
            }
            
            # Extraction des hash principaux
            for proc_name, result in processors_results.items():
                if "error" in result:
                    continue
                
                if proc_name == "chromaprint":
                    combined["primary_hashes"]["chromaprint"] = result.get("fingerprint_hash")
                elif proc_name == "spectral_hash":
                    combined["primary_hashes"]["spectral"] = result.get("spectral_hash")
                    combined["primary_hashes"]["mel"] = result.get("mel_hash")
            
            # Extraction des vecteurs de caractéristiques
            for proc_name, result in processors_results.items():
                if "error" in result:
                    continue
                
                if proc_name == "essentia" and "feature_vector" in result:
                    combined["feature_vectors"]["essentia"] = result["feature_vector"].tolist()
                elif proc_name == "mel_spectrogram":
                    # Création d'un vecteur résumé du mel spectrogram
                    mel_data = result.get("mel_spectrogram", [])
                    if mel_data:
                        mel_array = np.array(mel_data)
                        mel_summary = np.mean(mel_array, axis=1).tolist()  # Moyenne temporelle
                        combined["feature_vectors"]["mel_summary"] = mel_summary
            
            # Statistiques globales
            durations = [r.get("duration", 0) for r in processors_results.values() if "error" not in r]
            if durations:
                combined["statistics"]["duration"] = np.mean(durations)
            
            processing_times = [r.get("processing_time", 0) for r in processors_results.values() if "error" not in r]
            if processing_times:
                combined["statistics"]["total_processing_time"] = sum(processing_times)
            
            # Métriques de qualité
            quality_scores = [r.get("quality_score", 0) for r in processors_results.values() if "quality_score" in r]
            if quality_scores:
                combined["quality_metrics"]["average_quality"] = np.mean(quality_scores)
                combined["quality_metrics"]["min_quality"] = np.min(quality_scores)
                combined["quality_metrics"]["max_quality"] = np.max(quality_scores)
            
            return combined
            
        except Exception as e:
            logger.warning(f"Feature combination failed: {e}")
            return {}
    
    def get_supported_formats(self) -> List[str]:
        """Retourne les formats audio supportés"""
        return [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff", ".wma"]
    
    def get_processor_status(self) -> Dict[str, bool]:
        """Retourne le statut des processeurs"""
        return {
            "chromaprint": "chromaprint" in self.processors,
            "essentia": "essentia" in self.processors,
            "spectral_hash": "spectral_hash" in self.processors,
            "mel_spectrogram": "mel_spectrogram" in self.processors
        }

# Export des classes principales
__all__ = [
    "AudioFingerprintEngine",
    "AudioFingerprintConfig",
    "AudioProcessor",
    "ChromaprintProcessor",
    "EssentiaProcessor", 
    "SpectralHashProcessor",
    "MelSpectrogramProcessor"
]
