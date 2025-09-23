"""🔍 Enterprise Audio Fingerprinting System - Content Identification & Copyright
=============================================================================

Système de fingerprinting audio enterprise avec identification de contenu,
détection de copyright et protection intellectuelle pour Ainflue.

Expert Roles Implementation:
🎵 Audio Engineer: Algorithmes de fingerprinting + extraction de features audio
🏗️ Backend Senior: Architecture de base de données + recherche rapide
🤖 Lead Dev IA: Machine learning pour identification + matching intelligent
🧠 ML Engineer: Modèles de hashing perceptuel + similarité audio
🔒 Sécurité: Protection copyright + anti-piratage + détection DMCA
⚙️ DevOps: Pipeline de fingerprinting + indexation massive
🔗 Microservices: Services de matching + API de détection
⚡ Performance: Recherche ultra-rapide + base de données optimisée

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Enterprise Production
Date: 16 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture de fingerprinting audio est la propriété intellectuelle EXCLUSIVE de
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
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.spatial.distance import cosine, euclidean
from collections import defaultdict
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
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FingerprintAlgorithm(Enum):
    """Algorithmes de fingerprinting disponibles"""
    SPECTRAL_PEAKS = "spectral_peaks"
    CHROMAPRINT = "chromaprint"
    LANDMARK_HASH = "landmark_hash"
    MFCC_HASH = "mfcc_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    WAVELET_HASH = "wavelet_hash"
    NEURAL_EMBEDDING = "neural_embedding"

class MatchQuality(Enum):
    """Qualité de correspondance"""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class ContentType(Enum):
    """Types de contenu audio"""
    MUSIC = "music"
    SPEECH = "speech"
    PODCAST = "podcast"
    SOUND_EFFECT = "sound_effect"
    MIXED = "mixed"
    UNKNOWN = "unknown"

class ProtectionLevel(Enum):
    """Niveaux de protection copyright"""
    PUBLIC_DOMAIN = "public_domain"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    LICENSED = "licensed"
    COPYRIGHTED = "copyrighted"
    RESTRICTED = "restricted"

@dataclass
class AudioFingerprint:
    """Empreinte audio complète"""
    fingerprint_id: str
    audio_id: str
    algorithm: FingerprintAlgorithm
    hash_data: Union[str, bytes, np.ndarray]
    features: Dict[str, Any]
    duration: float
    sample_rate: int
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentMetadata:
    """Métadonnées de contenu audio"""
    content_id: str
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    genre: Optional[str]
    release_date: Optional[datetime]
    duration: float
    content_type: ContentType
    protection_level: ProtectionLevel
    copyright_owner: Optional[str]
    license_info: Dict[str, Any]
    isrc: Optional[str]  # International Standard Recording Code
    tags: List[str] = field(default_factory=list)

@dataclass
class MatchResult:
    """Résultat de correspondance de fingerprint"""
    match_id: str
    query_fingerprint: str
    matched_fingerprint: str
    confidence_score: float
    similarity_score: float
    match_quality: MatchQuality
    time_offset: float
    duration_match: float
    content_metadata: Optional[ContentMetadata]
    algorithm_used: FingerprintAlgorithm
    processing_time: float

@dataclass
class FingerprintingConfiguration:
    """Configuration du système de fingerprinting"""
    algorithms: List[FingerprintAlgorithm] = field(
        default_factory=lambda: [FingerprintAlgorithm.SPECTRAL_PEAKS, FingerprintAlgorithm.MFCC_HASH]
    )
    chunk_duration: float = 10.0  # secondes
    overlap_duration: float = 2.0  # secondes
    min_match_confidence: float = 0.8
    enable_content_type_detection: bool = True
    enable_quality_analysis: bool = True
    max_processing_time: float = 30.0  # secondes
    database_shards: int = 16

class SpectralPeaksFingerprinter:
    """Fingerprinting basé sur les pics spectraux (algorithme Shazam-like)"""
    
    def __init__(self):
        self.target_sample_rate = 22050
        self.nfft = 4096
        self.hop_length = 512
        self.peak_neighborhood_size = 10
        self.fanout = 15
        self.amp_min = 10
    
    async def generate_fingerprint(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Tuple[List[Tuple[int, int]], Dict[str, Any]]:
        """Génère une empreinte basée sur les pics spectraux"""
        
        # Rééchantillonner si nécessaire
        if sample_rate != self.target_sample_rate:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=self.target_sample_rate)
        
        # Calculer le spectrogramme
        stft = librosa.stft(
            audio, 
            n_fft=self.nfft, 
            hop_length=self.hop_length,
            window='hann'
        )
        magnitude = np.abs(stft)
        
        # Trouver les pics locaux
        peaks = await self._find_spectral_peaks(magnitude)
        
        # Générer les hashes de constellation
        hashes = await self._generate_constellation_hashes(peaks)
        
        # Métadonnées des features
        features = {
            'num_peaks': len(peaks),
            'num_hashes': len(hashes),
            'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=self.target_sample_rate))),
            'spectral_rolloff': float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=self.target_sample_rate))),
            'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(audio))),
            'tempo': float(librosa.beat.tempo(y=audio, sr=self.target_sample_rate)[0])
        }
        
        return hashes, features
    
    async def _find_spectral_peaks(self, magnitude: np.ndarray) -> List[Tuple[int, int]]:
        """Trouve les pics spectraux dans le spectrogramme"""
        peaks = []
        
        # Itérer sur les frames temporelles
        for t in range(magnitude.shape[1]):
            spectrum = magnitude[:, t]
            
            # Trouver les pics locaux
            peak_indices = signal.find_peaks(
                spectrum,
                height=self.amp_min,
                distance=self.peak_neighborhood_size
            )[0]
            
            # Garder seulement les pics les plus forts
            if len(peak_indices) > 5:
                peak_values = spectrum[peak_indices]
                top_peaks_idx = np.argsort(peak_values)[-5:]
                peak_indices = peak_indices[top_peaks_idx]
            
            # Ajouter les pics avec leurs coordonnées temps-fréquence
            for freq_idx in peak_indices:
                peaks.append((t, freq_idx))
        
        return peaks
    
    async def _generate_constellation_hashes(
        self,
        peaks: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Génère les hashes de constellation à partir des pics"""
        hashes = []
        
        for i, (t1, f1) in enumerate(peaks):
            # Pour chaque pic, regarder les pics suivants dans une fenêtre temporelle
            for j in range(i + 1, min(i + self.fanout + 1, len(peaks))):
                t2, f2 = peaks[j]
                
                # Vérifier que le pic suivant est dans la fenêtre temporelle
                if t2 - t1 <= 200:  # Fenêtre de 200 frames
                    # Créer un hash unique pour cette paire de pics
                    hash_value = self._hash_peak_pair(f1, f2, t2 - t1)
                    hashes.append((hash_value, t1))
        
        return hashes
    
    def _hash_peak_pair(self, f1: int, f2: int, dt: int) -> int:
        """Crée un hash pour une paire de pics"""
        # Combiner les fréquences et le delta temporel
        # Utiliser un salt pour éviter les collisions
        salt = 0x51ED270B
        hash_input = f1 | (f2 << 9) | (dt << 18)
        return hash_input ^ salt

class MFCCHashFingerprinter:
    """Fingerprinting basé sur les coefficients MFCC"""
    
    def __init__(self):
        self.target_sample_rate = 22050
        self.n_mfcc = 13
        self.frame_size = 1024
        self.hop_length = 512
        self.hash_length = 32
    
    async def generate_fingerprint(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Génère une empreinte MFCC"""
        
        # Rééchantillonner si nécessaire
        if sample_rate != self.target_sample_rate:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=self.target_sample_rate)
        
        # Extraire les MFCC
        mfccs = librosa.feature.mfcc(
            y=audio,
            sr=self.target_sample_rate,
            n_mfcc=self.n_mfcc,
            n_fft=self.frame_size,
            hop_length=self.hop_length
        )
        
        # Normaliser
        mfccs = (mfccs - np.mean(mfccs, axis=1, keepdims=True)) / (np.std(mfccs, axis=1, keepdims=True) + 1e-8)
        
        # Générer le hash perceptuel
        hash_value = await self._generate_mfcc_hash(mfccs)
        
        # Features
        features = {
            'mfcc_mean': mfccs.mean(axis=1).tolist(),
            'mfcc_std': mfccs.std(axis=1).tolist(),
            'spectral_flatness': float(np.mean(librosa.feature.spectral_flatness(y=audio, hop_length=self.hop_length))),
            'spectral_bandwidth': float(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=self.target_sample_rate, hop_length=self.hop_length)))
        }
        
        return hash_value, features
    
    async def _generate_mfcc_hash(self, mfccs: np.ndarray) -> str:
        """Génère un hash basé sur les MFCC"""
        # Calculer la moyenne temporelle des MFCC
        mfcc_mean = np.mean(mfccs, axis=1)
        
        # Quantifier les valeurs
        mfcc_quantized = np.round(mfcc_mean * 100).astype(int)
        
        # Créer un hash binaire
        hash_bits = []
        for i in range(len(mfcc_quantized) - 1):
            # Comparer les coefficients adjacents
            if mfcc_quantized[i] > mfcc_quantized[i + 1]:
                hash_bits.append('1')
            else:
                hash_bits.append('0')
        
        # Compléter avec des bits supplémentaires si nécessaire
        while len(hash_bits) < self.hash_length:
            hash_bits.append('0')
        
        # Convertir en hexadécimal
        bit_string = ''.join(hash_bits[:self.hash_length])
        hash_value = hex(int(bit_string, 2))[2:].zfill(8)
        
        return hash_value

class PerceptualHashFingerprinter:
    """Fingerprinting basé sur le hashing perceptuel"""
    
    def __init__(self):
        self.target_sample_rate = 22050
        self.hash_size = 64
    
    async def generate_fingerprint(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Génère une empreinte perceptuelle"""
        
        # Rééchantillonner si nécessaire
        if sample_rate != self.target_sample_rate:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=self.target_sample_rate)
        
        # Calculer le spectrogramme
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        
        # Réduire la résolution pour le hashing perceptuel
        reduced_spec = await self._reduce_spectrogram(magnitude)
        
        # Générer le hash perceptuel
        hash_value = await self._compute_perceptual_hash(reduced_spec)
        
        # Features
        features = {
            'perceptual_hash': hash_value,
            'spectral_entropy': float(await self._compute_spectral_entropy(magnitude)),
            'harmonic_ratio': float(await self._compute_harmonic_ratio(audio)),
            'rms_energy': float(np.sqrt(np.mean(audio ** 2)))
        }
        
        return hash_value, features
    
    async def _reduce_spectrogram(self, magnitude: np.ndarray) -> np.ndarray:
        """Réduit la résolution du spectrogramme"""
        # Réduire la résolution fréquentielle
        freq_bins = min(32, magnitude.shape[0])
        time_bins = min(32, magnitude.shape[1])
        
        # Redimensionner
        from scipy.ndimage import zoom
        zoom_factors = (freq_bins / magnitude.shape[0], time_bins / magnitude.shape[1])
        reduced = zoom(magnitude, zoom_factors, order=1)
        
        return reduced
    
    async def _compute_perceptual_hash(self, reduced_spec: np.ndarray) -> str:
        """Calcule le hash perceptuel"""
        # Appliquer DCT 2D
        from scipy.fft import dct
        dct_2d = dct(dct(reduced_spec, axis=0), axis=1)
        
        # Garder seulement les basses fréquences (coin supérieur gauche)
        hash_size = int(np.sqrt(self.hash_size))
        low_freq = dct_2d[:hash_size, :hash_size]
        
        # Calculer la médiane
        median = np.median(low_freq)
        
        # Générer le hash binaire
        hash_bits = (low_freq > median).flatten()
        
        # Convertir en hexadécimal
        bit_string = ''.join(['1' if bit else '0' for bit in hash_bits])
        hash_value = hex(int(bit_string, 2))[2:].zfill(16)
        
        return hash_value
    
    async def _compute_spectral_entropy(self, magnitude: np.ndarray) -> float:
        """Calcule l'entropie spectrale"""
        # Normaliser le spectre
        spectrum_sum = np.sum(magnitude, axis=0)
        spectrum_norm = spectrum_sum / (np.sum(spectrum_sum) + 1e-8)
        
        # Calculer l'entropie
        entropy = -np.sum(spectrum_norm * np.log2(spectrum_norm + 1e-8))
        return entropy / np.log2(len(spectrum_norm))  # Normaliser
    
    async def _compute_harmonic_ratio(self, audio: np.ndarray) -> float:
        """Calcule le ratio harmonique"""
        # Décomposition harmonique/percussive
        y_harmonic, y_percussive = librosa.effects.hpss(audio)
        
        # Calculer les énergies
        harmonic_energy = np.sum(y_harmonic ** 2)
        total_energy = np.sum(audio ** 2)
        
        return harmonic_energy / (total_energy + 1e-8)

class AudioFingerprintingSystem:
    """Système de fingerprinting audio enterprise"""
    
    def __init__(self, config: Optional[FingerprintingConfiguration] = None):
        """Initialise le système de fingerprinting"""
        self.config = config or FingerprintingConfiguration()
        
        # Initialiser les fingerprinters
        self.fingerprinters = {
            FingerprintAlgorithm.SPECTRAL_PEAKS: SpectralPeaksFingerprinter(),
            FingerprintAlgorithm.MFCC_HASH: MFCCHashFingerprinter(),
            FingerprintAlgorithm.PERCEPTUAL_HASH: PerceptualHashFingerprinter()
        }
        
        # Base de données en mémoire (en production, utiliser une vraie DB)
        self.fingerprint_database = {}
        self.content_database = {}
        self.index_by_algorithm = defaultdict(dict)
        
        # Cache Redis
        self.redis_client = None
        
        # Statistiques
        self.stats = {
            'total_fingerprints': 0,
            'total_matches': 0,
            'average_matching_time': 0,
            'algorithm_usage': defaultdict(int),
            'false_positive_rate': 0
        }
        
        logger.info("AudioFingerprintingSystem initialized successfully")
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialise la connexion Redis"""
        try:
            self.redis_client = await aioredis.from_url(redis_url)
            logger.info("Redis connection established for fingerprinting cache")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
    
    async def add_content(
        self,
        audio_file_path: str,
        metadata: ContentMetadata
    ) -> List[AudioFingerprint]:
        """Ajoute du contenu à la base de données de fingerprints"""
        try:
            # Charger l'audio
            audio, sample_rate = sf.read(audio_file_path)
            
            # Convertir en mono si nécessaire
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=0)
            
            # Générer les fingerprints avec tous les algorithmes configurés
            fingerprints = []
            
            for algorithm in self.config.algorithms:
                if algorithm in self.fingerprinters:
                    fingerprint = await self._generate_fingerprint(
                        audio, sample_rate, algorithm, metadata.content_id
                    )
                    fingerprints.append(fingerprint)
                    
                    # Ajouter à la base de données
                    await self._store_fingerprint(fingerprint)
            
            # Stocker les métadonnées du contenu
            self.content_database[metadata.content_id] = metadata
            
            # Mettre à jour les statistiques
            self.stats['total_fingerprints'] += len(fingerprints)
            
            logger.info(f"Added content {metadata.content_id} with {len(fingerprints)} fingerprints")
            return fingerprints
            
        except Exception as e:
            logger.error(f"Failed to add content: {e}")
            raise
    
    async def search_matches(
        self,
        audio_file_path: str,
        max_results: int = 10
    ) -> List[MatchResult]:
        """Recherche les correspondances pour un fichier audio"""
        start_time = time.time()
        
        try:
            # Charger l'audio
            audio, sample_rate = sf.read(audio_file_path)
            
            # Convertir en mono si nécessaire
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=0)
            
            # Générer les fingerprints de requête
            query_fingerprints = {}
            for algorithm in self.config.algorithms:
                if algorithm in self.fingerprinters:
                    fingerprint = await self._generate_fingerprint(
                        audio, sample_rate, algorithm, f"query_{uuid.uuid4()}"
                    )
                    query_fingerprints[algorithm] = fingerprint
            
            # Rechercher les correspondances
            all_matches = []
            
            for algorithm, query_fp in query_fingerprints.items():
                matches = await self._search_algorithm_matches(
                    query_fp, algorithm, max_results
                )
                all_matches.extend(matches)
            
            # Combiner et trier les résultats
            combined_matches = await self._combine_and_rank_matches(all_matches)
            
            # Limiter le nombre de résultats
            final_matches = combined_matches[:max_results]
            
            # Mettre à jour les statistiques
            processing_time = time.time() - start_time
            self.stats['total_matches'] += len(final_matches)
            
            current_avg = self.stats['average_matching_time']
            total_matches = self.stats['total_matches']
            self.stats['average_matching_time'] = (
                (current_avg * (total_matches - len(final_matches)) + processing_time) / total_matches
            )
            
            return final_matches
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def _generate_fingerprint(
        self,
        audio: np.ndarray,
        sample_rate: int,
        algorithm: FingerprintAlgorithm,
        audio_id: str
    ) -> AudioFingerprint:
        """Génère un fingerprint avec l'algorithme spécifié"""
        fingerprinter = self.fingerprinters[algorithm]
        
        # Générer l'empreinte
        if algorithm == FingerprintAlgorithm.SPECTRAL_PEAKS:
            hash_data, features = await fingerprinter.generate_fingerprint(audio, sample_rate)
        else:
            hash_data, features = await fingerprinter.generate_fingerprint(audio, sample_rate)
        
        # Créer l'objet AudioFingerprint
        fingerprint = AudioFingerprint(
            fingerprint_id=str(uuid.uuid4()),
            audio_id=audio_id,
            algorithm=algorithm,
            hash_data=hash_data,
            features=features,
            duration=len(audio) / sample_rate,
            sample_rate=sample_rate,
            created_at=datetime.now()
        )
        
        return fingerprint
    
    async def _store_fingerprint(self, fingerprint: AudioFingerprint):
        """Stocke un fingerprint dans la base de données"""
        # Stocker dans la base principale
        self.fingerprint_database[fingerprint.fingerprint_id] = fingerprint
        
        # Indexer par algorithme
        algorithm_index = self.index_by_algorithm[fingerprint.algorithm]
        
        if fingerprint.algorithm == FingerprintAlgorithm.SPECTRAL_PEAKS:
            # Pour les pics spectraux, indexer par hash
            for hash_value, time_offset in fingerprint.hash_data:
                if hash_value not in algorithm_index:
                    algorithm_index[hash_value] = []
                algorithm_index[hash_value].append((fingerprint.fingerprint_id, time_offset))
        else:
            # Pour les autres algorithmes, indexer directement
            algorithm_index[fingerprint.hash_data] = fingerprint.fingerprint_id
        
        # Mettre à jour les statistiques d'usage
        self.stats['algorithm_usage'][fingerprint.algorithm] += 1
    
    async def _search_algorithm_matches(
        self,
        query_fingerprint: AudioFingerprint,
        algorithm: FingerprintAlgorithm,
        max_results: int
    ) -> List[MatchResult]:
        """Recherche les correspondances pour un algorithme spécifique"""
        matches = []
        algorithm_index = self.index_by_algorithm[algorithm]
        
        if algorithm == FingerprintAlgorithm.SPECTRAL_PEAKS:
            # Recherche par pics spectraux
            matches = await self._search_spectral_peaks(
                query_fingerprint, algorithm_index, max_results
            )
        elif algorithm in [FingerprintAlgorithm.MFCC_HASH, FingerprintAlgorithm.PERCEPTUAL_HASH]:
            # Recherche par similarité de hash
            matches = await self._search_hash_similarity(
                query_fingerprint, algorithm_index, max_results
            )
        
        return matches
    
    async def _search_spectral_peaks(
        self,
        query_fingerprint: AudioFingerprint,
        algorithm_index: Dict,
        max_results: int
    ) -> List[MatchResult]:
        """Recherche par correspondance de pics spectraux"""
        match_counts = defaultdict(lambda: defaultdict(int))
        
        # Compter les correspondances de hash pour chaque fingerprint
        for hash_value, query_time in query_fingerprint.hash_data:
            if hash_value in algorithm_index:
                for fp_id, fp_time in algorithm_index[hash_value]:
                    time_offset = fp_time - query_time
                    match_counts[fp_id][time_offset] += 1
        
        # Créer les résultats de correspondance
        matches = []
        for fp_id, time_offsets in match_counts.items():
            # Trouver le meilleur offset temporel
            best_offset = max(time_offsets, key=time_offsets.get)
            match_count = time_offsets[best_offset]
            
            # Calculer la confiance
            total_query_hashes = len(query_fingerprint.hash_data)
            confidence = match_count / total_query_hashes if total_query_hashes > 0 else 0
            
            if confidence >= self.config.min_match_confidence:
                matched_fingerprint = self.fingerprint_database[fp_id]
                content_metadata = self.content_database.get(matched_fingerprint.audio_id)
                
                match_result = MatchResult(
                    match_id=str(uuid.uuid4()),
                    query_fingerprint=query_fingerprint.fingerprint_id,
                    matched_fingerprint=fp_id,
                    confidence_score=confidence,
                    similarity_score=confidence,  # Pour les pics spectraux, même valeur
                    match_quality=self._determine_match_quality(confidence),
                    time_offset=best_offset,
                    duration_match=min(query_fingerprint.duration, matched_fingerprint.duration),
                    content_metadata=content_metadata,
                    algorithm_used=query_fingerprint.algorithm,
                    processing_time=0  # Sera mis à jour plus tard
                )
                
                matches.append(match_result)
        
        # Trier par confiance décroissante
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return matches[:max_results]
    
    async def _search_hash_similarity(
        self,
        query_fingerprint: AudioFingerprint,
        algorithm_index: Dict,
        max_results: int
    ) -> List[MatchResult]:
        """Recherche par similarité de hash"""
        matches = []
        query_hash = query_fingerprint.hash_data
        
        for stored_hash, fp_id in algorithm_index.items():
            # Calculer la similarité
            similarity = await self._calculate_hash_similarity(query_hash, stored_hash)
            
            if similarity >= self.config.min_match_confidence:
                matched_fingerprint = self.fingerprint_database[fp_id]
                content_metadata = self.content_database.get(matched_fingerprint.audio_id)
                
                match_result = MatchResult(
                    match_id=str(uuid.uuid4()),
                    query_fingerprint=query_fingerprint.fingerprint_id,
                    matched_fingerprint=fp_id,
                    confidence_score=similarity,
                    similarity_score=similarity,
                    match_quality=self._determine_match_quality(similarity),
                    time_offset=0,  # Non applicable pour ces algorithmes
                    duration_match=min(query_fingerprint.duration, matched_fingerprint.duration),
                    content_metadata=content_metadata,
                    algorithm_used=query_fingerprint.algorithm,
                    processing_time=0
                )
                
                matches.append(match_result)
        
        # Trier par similarité décroissante
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches[:max_results]
    
    async def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calcule la similarité entre deux hash"""
        if len(hash1) != len(hash2):
            return 0.0
        
        # Calculer la distance de Hamming pour les hash hexadécimaux
        try:
            int1 = int(hash1, 16)
            int2 = int(hash2, 16)
            
            # XOR pour trouver les bits différents
            xor_result = int1 ^ int2
            
            # Compter les bits différents
            different_bits = bin(xor_result).count('1')
            total_bits = len(hash1) * 4  # 4 bits par caractère hexadécimal
            
            # Similarité = 1 - (bits différents / total bits)
            similarity = 1.0 - (different_bits / total_bits)
            return max(0.0, similarity)
            
        except ValueError:
            # Fallback pour les hash non-hexadécimaux
            different_chars = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            return 1.0 - (different_chars / len(hash1))
    
    def _determine_match_quality(self, confidence: float) -> MatchQuality:
        """Détermine la qualité de correspondance basée sur la confiance"""
        if confidence >= 0.95:
            return MatchQuality.EXACT
        elif confidence >= 0.85:
            return MatchQuality.HIGH
        elif confidence >= 0.70:
            return MatchQuality.MEDIUM
        elif confidence >= 0.50:
            return MatchQuality.LOW
        else:
            return MatchQuality.NONE
    
    async def _combine_and_rank_matches(
        self,
        all_matches: List[MatchResult]
    ) -> List[MatchResult]:
        """Combine et classe les correspondances de différents algorithmes"""
        # Grouper par contenu audio
        content_matches = defaultdict(list)
        
        for match in all_matches:
            if match.content_metadata:
                content_id = match.content_metadata.content_id
                content_matches[content_id].append(match)
        
        # Combiner les scores pour chaque contenu
        combined_matches = []
        
        for content_id, matches in content_matches.items():
            # Calculer le score combiné
            combined_confidence = np.mean([m.confidence_score for m in matches])
            combined_similarity = np.mean([m.similarity_score for m in matches])
            
            # Bonus pour les correspondances multiples
            algorithm_bonus = len(matches) * 0.05
            final_confidence = min(1.0, combined_confidence + algorithm_bonus)
            
            # Prendre la meilleure correspondance pour ce contenu
            best_match = max(matches, key=lambda x: x.confidence_score)
            best_match.confidence_score = final_confidence
            best_match.similarity_score = combined_similarity
            best_match.match_quality = self._determine_match_quality(final_confidence)
            
            combined_matches.append(best_match)
        
        # Trier par confiance décroissante
        combined_matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return combined_matches
    
    async def detect_content_type(self, audio: np.ndarray, sample_rate: int) -> ContentType:
        """Détecte le type de contenu audio"""
        try:
            # Analyser les caractéristiques audio
            tempo = librosa.beat.tempo(y=audio, sr=sample_rate)[0]
            harmonic, percussive = librosa.effects.hpss(audio)
            
            # Calculer les ratios
            harmonic_ratio = np.sum(harmonic ** 2) / (np.sum(audio ** 2) + 1e-8)
            percussive_ratio = np.sum(percussive ** 2) / (np.sum(audio ** 2) + 1e-8)
            
            # Features spectrales
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sample_rate))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
            
            # Classification heuristique
            if harmonic_ratio > 0.6 and tempo > 60 and percussive_ratio > 0.2:
                return ContentType.MUSIC
            elif zero_crossing_rate > 0.1 and spectral_centroid < 2000:
                return ContentType.SPEECH
            elif harmonic_ratio < 0.3 and percussive_ratio > 0.5:
                return ContentType.SOUND_EFFECT
            elif harmonic_ratio > 0.4 and zero_crossing_rate > 0.05:
                return ContentType.MIXED
            else:
                return ContentType.UNKNOWN
                
        except Exception as e:
            logger.warning(f"Content type detection failed: {e}")
            return ContentType.UNKNOWN
    
    async def batch_process_directory(
        self,
        directory_path: str,
        content_metadata_template: ContentMetadata
    ) -> List[AudioFingerprint]:
        """Traite un répertoire entier de fichiers audio"""
        directory = Path(directory_path)
        supported_formats = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        
        all_fingerprints = []
        
        for audio_file in directory.rglob('*'):
            if audio_file.suffix.lower() in supported_formats:
                try:
                    # Créer des métadonnées basées sur le nom de fichier
                    metadata = ContentMetadata(
                        content_id=str(uuid.uuid4()),
                        title=audio_file.stem,
                        artist=content_metadata_template.artist,
                        album=content_metadata_template.album,
                        genre=content_metadata_template.genre,
                        release_date=content_metadata_template.release_date,
                        duration=0,  # Sera mis à jour
                        content_type=ContentType.UNKNOWN,  # Sera détecté
                        protection_level=content_metadata_template.protection_level,
                        copyright_owner=content_metadata_template.copyright_owner,
                        license_info=content_metadata_template.license_info
                    )
                    
                    # Traiter le fichier
                    fingerprints = await self.add_content(str(audio_file), metadata)
                    all_fingerprints.extend(fingerprints)
                    
                    logger.info(f"Processed: {audio_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {audio_file.name}: {e}")
        
        return all_fingerprints
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        return {
            'total_fingerprints': self.stats['total_fingerprints'],
            'total_matches': self.stats['total_matches'],
            'average_matching_time': self.stats['average_matching_time'],
            'algorithm_usage': dict(self.stats['algorithm_usage']),
            'database_size': len(self.fingerprint_database),
            'content_database_size': len(self.content_database),
            'algorithms_enabled': [alg.value for alg in self.config.algorithms]
        }
    
    async def cleanup_old_fingerprints(self, max_age_days: int = 365):
        """Nettoie les anciens fingerprints"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        fingerprints_to_remove = []
        for fp_id, fingerprint in self.fingerprint_database.items():
            if fingerprint.created_at < cutoff_date:
                fingerprints_to_remove.append(fp_id)
        
        for fp_id in fingerprints_to_remove:
            fingerprint = self.fingerprint_database.pop(fp_id)
            
            # Nettoyer les index
            algorithm_index = self.index_by_algorithm[fingerprint.algorithm]
            if fingerprint.algorithm == FingerprintAlgorithm.SPECTRAL_PEAKS:
                for hash_value, _ in fingerprint.hash_data:
                    if hash_value in algorithm_index:
                        algorithm_index[hash_value] = [
                            (fid, offset) for fid, offset in algorithm_index[hash_value] 
                            if fid != fp_id
                        ]
                        if not algorithm_index[hash_value]:
                            del algorithm_index[hash_value]
            else:
                if fingerprint.hash_data in algorithm_index:
                    del algorithm_index[fingerprint.hash_data]
        
        logger.info(f"Cleaned up {len(fingerprints_to_remove)} old fingerprints")

# Factory functions
async def create_audio_fingerprinting_system(
    config: Optional[FingerprintingConfiguration] = None
) -> AudioFingerprintingSystem:
    """Crée une instance du système de fingerprinting"""
    system = AudioFingerprintingSystem(config)
    return system

async def create_content_metadata(
    title: str,
    artist: Optional[str] = None,
    protection_level: str = "copyrighted",
    content_type: str = "unknown"
) -> ContentMetadata:
    """Crée des métadonnées de contenu"""
    return ContentMetadata(
        content_id=str(uuid.uuid4()),
        title=title,
        artist=artist,
        album=None,
        genre=None,
        release_date=None,
        duration=0,
        content_type=ContentType(content_type),
        protection_level=ProtectionLevel(protection_level),
        copyright_owner=artist,
        license_info={}
    )

# Export des classes et fonctions principales
__all__ = [
    'AudioFingerprintingSystem',
    'FingerprintAlgorithm',
    'MatchQuality',
    'ContentType',
    'ProtectionLevel',
    'AudioFingerprint',
    'ContentMetadata',
    'MatchResult',
    'FingerprintingConfiguration',
    'SpectralPeaksFingerprinter',
    'MFCCHashFingerprinter',
    'PerceptualHashFingerprinter',
    'create_audio_fingerprinting_system',
    'create_content_metadata'
]