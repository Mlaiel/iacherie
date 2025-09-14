"""
Audio Fingerprinting - Fingerprinting Module
===========================================
Système avancé de fingerprinting audio avec détection
de similarité, analyse spectrale et protection copyright.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """Formats audio supportés."""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    M4A = "m4a"
    OGG = "ogg"

class FingerprintAlgorithm(Enum):
    """Algorithmes de fingerprinting disponibles."""
    CHROMAPRINT = "chromaprint"
    SPECTRAL_HASH = "spectral_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    MFCC_FINGERPRINT = "mfcc_fingerprint"
    AUDIO_SHAZAM_LIKE = "audio_shazam_like"

@dataclass
class AudioFingerprint:
    """Empreinte audio."""
    fingerprint_id: str
    audio_file_path: str
    algorithm: FingerprintAlgorithm
    hash_value: str
    spectral_features: Dict[str, Any]
    temporal_features: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    confidence_score: float

@dataclass
class AudioMatch:
    """Résultat de matching audio."""
    match_id: str
    original_fingerprint_id: str
    detected_fingerprint_id: str
    similarity_score: float
    time_offset: Optional[float]
    duration_overlap: Optional[float]
    match_segments: List[Dict[str, Any]]
    confidence_level: str

class AudioFingerprinting:
    """
    Système de fingerprinting audio enterprise.
    Détection de similarité et protection copyright.
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialise le système de fingerprinting audio."""
        self.config = config or {}
        self.fingerprint_database: Dict[str, AudioFingerprint] = {}
        self.algorithm_configs = self._load_algorithm_configs()
        self.similarity_threshold = self.config.get('similarity_threshold', 0.85)
        logger.info("Audio Fingerprinting initialisé")
    
    def _load_algorithm_configs(self) -> Dict[str, Dict]:
        """Charge les configurations des algorithmes."""
        return {
            'chromaprint': {
                'sample_rate': 11025,
                'fft_size': 2048,
                'hop_length': 512,
                'chroma_bins': 12,
                'window': 'hann'
            },
            'spectral_hash': {
                'frequency_bands': 32,
                'time_frames': 64,
                'hash_bits': 256,
                'overlap': 0.5
            },
            'mfcc_fingerprint': {
                'n_mfcc': 13,
                'n_fft': 2048,
                'hop_length': 512,
                'n_mel': 40,
                'fmin': 0,
                'fmax': 8000
            }
        }
    
    async def create_fingerprint(
        self,
        audio_file_path: str,
        algorithm: FingerprintAlgorithm = FingerprintAlgorithm.CHROMAPRINT,
        metadata: Dict[str, Any] = None
    ) -> AudioFingerprint:
        """Crée une empreinte audio."""
        fingerprint_id = str(uuid.uuid4())
        
        # Analyser le fichier audio
        spectral_features = await self._extract_spectral_features(
            audio_file_path, algorithm
        )
        temporal_features = await self._extract_temporal_features(
            audio_file_path, algorithm
        )
        
        # Générer hash principal
        hash_value = self._generate_hash(spectral_features, temporal_features)
        
        # Calculer score de confiance
        confidence_score = self._calculate_confidence(
            spectral_features, temporal_features
        )
        
        fingerprint = AudioFingerprint(
            fingerprint_id=fingerprint_id,
            audio_file_path=audio_file_path,
            algorithm=algorithm,
            hash_value=hash_value,
            spectral_features=spectral_features,
            temporal_features=temporal_features,
            metadata=metadata or {},
            created_at=datetime.now(),
            confidence_score=confidence_score
        )
        
        # Stocker dans la base
        self.fingerprint_database[fingerprint_id] = fingerprint
        
        logger.info(f"Fingerprint créé: {fingerprint_id} pour {audio_file_path}")
        return fingerprint
    
    async def find_matches(
        self,
        query_fingerprint: AudioFingerprint,
        threshold: Optional[float] = None
    ) -> List[AudioMatch]:
        """Trouve les matches pour une empreinte."""
        if not threshold:
            threshold = self.similarity_threshold
        
        matches = []
        
        for stored_fingerprint in self.fingerprint_database.values():
            if stored_fingerprint.fingerprint_id == query_fingerprint.fingerprint_id:
                continue
            
            # Calculer similarité
            similarity = await self._calculate_similarity(
                query_fingerprint, stored_fingerprint
            )
            
            if similarity >= threshold:
                match = await self._create_match_result(
                    query_fingerprint, stored_fingerprint, similarity
                )
                matches.append(match)
        
        # Trier par score de similarité
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        
        logger.info(f"Trouvé {len(matches)} matches pour {query_fingerprint.fingerprint_id}")
        return matches
    
    async def _extract_spectral_features(
        self,
        audio_file_path: str,
        algorithm: FingerprintAlgorithm
    ) -> Dict[str, Any]:
        """Extrait les caractéristiques spectrales."""
        # Simulation extraction - en production utiliser librosa, essentia
        
        if algorithm == FingerprintAlgorithm.CHROMAPRINT:
            return {
                'chroma_vector': np.random.rand(12).tolist(),
                'spectral_centroid': np.random.rand(100).tolist(),
                'spectral_rolloff': np.random.rand(100).tolist(),
                'zero_crossing_rate': np.random.rand(100).tolist()
            }
        
        elif algorithm == FingerprintAlgorithm.SPECTRAL_HASH:
            return {
                'frequency_bands': np.random.rand(32, 64).tolist(),
                'spectral_peaks': np.random.rand(20, 2).tolist(),
                'harmonic_structure': np.random.rand(10).tolist()
            }
        
        elif algorithm == FingerprintAlgorithm.MFCC_FINGERPRINT:
            return {
                'mfcc_coefficients': np.random.rand(13, 100).tolist(),
                'delta_mfcc': np.random.rand(13, 100).tolist(),
                'delta2_mfcc': np.random.rand(13, 100).tolist()
            }
        
        else:
            return {
                'generic_spectrum': np.random.rand(512).tolist(),
                'energy_distribution': np.random.rand(32).tolist()
            }
    
    async def _extract_temporal_features(
        self,
        audio_file_path: str,
        algorithm: FingerprintAlgorithm
    ) -> Dict[str, Any]:
        """Extrait les caractéristiques temporelles."""
        # Simulation extraction temporelle
        return {
            'tempo': 120 + np.random.rand() * 60,  # BPM
            'onset_strength': np.random.rand(50).tolist(),
            'rhythm_pattern': np.random.rand(16).tolist(),
            'energy_envelope': np.random.rand(100).tolist(),
            'silence_segments': [(1.0, 1.5), (45.2, 46.1)],  # Segments silencieux
            'duration': 180.5 + np.random.rand() * 60  # Durée en secondes
        }
    
    def _generate_hash(
        self,
        spectral_features: Dict[str, Any],
        temporal_features: Dict[str, Any]
    ) -> str:
        """Génère le hash principal de l'empreinte."""
        # Combiner toutes les features en un vecteur
        combined_data = []
        
        # Features spectrales
        for key, value in spectral_features.items():
            if isinstance(value, list):
                combined_data.extend(value)
            else:
                combined_data.append(value)
        
        # Features temporelles
        for key, value in temporal_features.items():
            if isinstance(value, list):
                combined_data.extend(value)
            elif isinstance(value, (int, float)):
                combined_data.append(value)
        
        # Convertir en bytes et hasher
        data_str = json.dumps(combined_data, sort_keys=True)
        hash_object = hashlib.sha256(data_str.encode())
        
        return hash_object.hexdigest()
    
    def _calculate_confidence(
        self,
        spectral_features: Dict[str, Any],
        temporal_features: Dict[str, Any]
    ) -> float:
        """Calcule le score de confiance de l'empreinte."""
        confidence_factors = []
        
        # Confiance basée sur la richesse spectrale
        spectral_richness = len(spectral_features.get('chroma_vector', []))
        if spectral_richness > 0:
            confidence_factors.append(min(1.0, spectral_richness / 12))
        
        # Confiance basée sur la stabilité temporelle
        tempo = temporal_features.get('tempo', 0)
        if tempo > 60 and tempo < 200:  # Tempo normal
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        # Confiance basée sur la durée
        duration = temporal_features.get('duration', 0)
        if duration > 30:  # Plus de 30 secondes = plus fiable
            confidence_factors.append(0.95)
        else:
            confidence_factors.append(0.7)
        
        # Score final
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5
    
    async def _calculate_similarity(
        self,
        fingerprint1: AudioFingerprint,
        fingerprint2: AudioFingerprint
    ) -> float:
        """Calcule la similarité entre deux empreintes."""
        # Vérifier algorithme compatible
        if fingerprint1.algorithm != fingerprint2.algorithm:
            return 0.0
        
        similarities = []
        
        # Similarité spectrale
        spectral_sim = self._calculate_spectral_similarity(
            fingerprint1.spectral_features,
            fingerprint2.spectral_features
        )
        similarities.append(spectral_sim)
        
        # Similarité temporelle
        temporal_sim = self._calculate_temporal_similarity(
            fingerprint1.temporal_features,
            fingerprint2.temporal_features
        )
        similarities.append(temporal_sim)
        
        # Similarité de hash (exact match)
        hash_sim = 1.0 if fingerprint1.hash_value == fingerprint2.hash_value else 0.0
        similarities.append(hash_sim)
        
        # Score pondéré
        weights = [0.5, 0.3, 0.2]  # Spectral plus important
        weighted_similarity = sum(s * w for s, w in zip(similarities, weights))
        
        return weighted_similarity
    
    def _calculate_spectral_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calcule similarité spectrale."""
        similarities = []
        
        # Chroma similarity
        if 'chroma_vector' in features1 and 'chroma_vector' in features2:
            chroma1 = np.array(features1['chroma_vector'])
            chroma2 = np.array(features2['chroma_vector'])
            
            if len(chroma1) == len(chroma2):
                # Corrélation croisée pour invariance de transposition
                correlations = []
                for shift in range(12):  # 12 tons chromatiques
                    shifted_chroma2 = np.roll(chroma2, shift)
                    correlation = np.corrcoef(chroma1, shifted_chroma2)[0, 1]
                    if not np.isnan(correlation):
                        correlations.append(abs(correlation))
                
                if correlations:
                    similarities.append(max(correlations))
        
        # MFCC similarity
        if 'mfcc_coefficients' in features1 and 'mfcc_coefficients' in features2:
            mfcc1 = np.array(features1['mfcc_coefficients'])
            mfcc2 = np.array(features2['mfcc_coefficients'])
            
            if mfcc1.shape == mfcc2.shape:
                # Distance euclidienne normalisée
                distance = np.linalg.norm(mfcc1 - mfcc2)
                max_distance = np.linalg.norm(mfcc1) + np.linalg.norm(mfcc2)
                if max_distance > 0:
                    similarity = 1 - (distance / max_distance)
                    similarities.append(max(0, similarity))
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_temporal_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calcule similarité temporelle."""
        similarities = []
        
        # Similarité de tempo
        tempo1 = features1.get('tempo', 0)
        tempo2 = features2.get('tempo', 0)
        
        if tempo1 > 0 and tempo2 > 0:
            tempo_diff = abs(tempo1 - tempo2)
            max_tempo = max(tempo1, tempo2)
            tempo_similarity = 1 - (tempo_diff / max_tempo)
            similarities.append(max(0, tempo_similarity))
        
        # Similarité de durée
        duration1 = features1.get('duration', 0)
        duration2 = features2.get('duration', 0)
        
        if duration1 > 0 and duration2 > 0:
            duration_ratio = min(duration1, duration2) / max(duration1, duration2)
            similarities.append(duration_ratio)
        
        # Similarité de patterns rythmiques
        if 'rhythm_pattern' in features1 and 'rhythm_pattern' in features2:
            rhythm1 = np.array(features1['rhythm_pattern'])
            rhythm2 = np.array(features2['rhythm_pattern'])
            
            if len(rhythm1) == len(rhythm2):
                correlation = np.corrcoef(rhythm1, rhythm2)[0, 1]
                if not np.isnan(correlation):
                    similarities.append(abs(correlation))
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _create_match_result(
        self,
        query_fingerprint: AudioFingerprint,
        matched_fingerprint: AudioFingerprint,
        similarity_score: float
    ) -> AudioMatch:
        """Crée un résultat de match détaillé."""
        match_id = str(uuid.uuid4())
        
        # Analyser segments de match
        match_segments = await self._analyze_match_segments(
            query_fingerprint, matched_fingerprint
        )
        
        # Calculer offset temporel
        time_offset = self._calculate_time_offset(
            query_fingerprint.temporal_features,
            matched_fingerprint.temporal_features
        )
        
        # Calculer durée de chevauchement
        duration_overlap = self._calculate_duration_overlap(
            query_fingerprint.temporal_features,
            matched_fingerprint.temporal_features
        )
        
        # Déterminer niveau de confiance
        confidence_level = self._determine_confidence_level(similarity_score)
        
        return AudioMatch(
            match_id=match_id,
            original_fingerprint_id=matched_fingerprint.fingerprint_id,
            detected_fingerprint_id=query_fingerprint.fingerprint_id,
            similarity_score=similarity_score,
            time_offset=time_offset,
            duration_overlap=duration_overlap,
            match_segments=match_segments,
            confidence_level=confidence_level
        )
    
    async def _analyze_match_segments(
        self,
        fingerprint1: AudioFingerprint,
        fingerprint2: AudioFingerprint
    ) -> List[Dict[str, Any]]:
        """Analyse les segments de match entre deux empreintes."""
        # Simulation analyse de segments
        segments = []
        
        # Créer des segments fictifs pour la démo
        num_segments = np.random.randint(1, 6)
        
        for i in range(num_segments):
            start_time = np.random.rand() * 60  # 0-60 secondes
            duration = 5 + np.random.rand() * 20  # 5-25 secondes
            confidence = 0.7 + np.random.rand() * 0.3  # 0.7-1.0
            
            segments.append({
                'segment_id': i + 1,
                'start_time': start_time,
                'duration': duration,
                'end_time': start_time + duration,
                'confidence': confidence,
                'match_type': 'full_match' if confidence > 0.9 else 'partial_match'
            })
        
        return segments
    
    def _calculate_time_offset(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> Optional[float]:
        """Calcule l'offset temporel entre deux audios."""
        # Simulation calcul d'offset
        # En production, utiliser cross-correlation des features temporelles
        return np.random.rand() * 10  # 0-10 secondes d'offset
    
    def _calculate_duration_overlap(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> Optional[float]:
        """Calcule la durée de chevauchement."""
        duration1 = features1.get('duration', 0)
        duration2 = features2.get('duration', 0)
        
        if duration1 > 0 and duration2 > 0:
            return min(duration1, duration2)
        
        return None
    
    def _determine_confidence_level(self, similarity_score: float) -> str:
        """Détermine le niveau de confiance textuel."""
        if similarity_score >= 0.95:
            return "very_high"
        elif similarity_score >= 0.85:
            return "high"
        elif similarity_score >= 0.70:
            return "medium"
        elif similarity_score >= 0.50:
            return "low"
        else:
            return "very_low"
    
    async def batch_fingerprint(
        self,
        audio_files: List[str],
        algorithm: FingerprintAlgorithm = FingerprintAlgorithm.CHROMAPRINT
    ) -> List[AudioFingerprint]:
        """Traite un batch de fichiers audio."""
        fingerprints = []
        
        # Traitement parallèle
        tasks = []
        for audio_file in audio_files:
            task = self.create_fingerprint(audio_file, algorithm)
            tasks.append(task)
        
        fingerprints = await asyncio.gather(*tasks)
        
        logger.info(f"Batch fingerprinting terminé: {len(fingerprints)} fichiers")
        return fingerprints
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Retourne analytics du système."""
        total_fingerprints = len(self.fingerprint_database)
        
        # Répartition par algorithme
        algorithm_distribution = {}
        for fp in self.fingerprint_database.values():
            algo = fp.algorithm.value
            algorithm_distribution[algo] = algorithm_distribution.get(algo, 0) + 1
        
        # Score de confiance moyen
        confidence_scores = [fp.confidence_score for fp in self.fingerprint_database.values()]
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        return {
            'total_fingerprints': total_fingerprints,
            'algorithm_distribution': algorithm_distribution,
            'average_confidence_score': avg_confidence,
            'similarity_threshold': self.similarity_threshold,
            'supported_formats': [fmt.value for fmt in AudioFormat],
            'available_algorithms': [algo.value for algo in FingerprintAlgorithm]
        }