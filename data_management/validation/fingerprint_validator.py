"""🚀 AI Fingerprinting Validator - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/data_management/validation/fingerprint_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE VALIDATION D'EMPREINTES NUMÉRIQUES IA
Validation avancée des empreintes numériques pour protection du contenu
- Génération d'empreintes multi-format (audio, vidéo, image, texte)
- Validation d'unicité et détection de doublons
- Analyse de similarité avec base existante
- Intégration avec système de protection des droits
"""from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import os
import hashlib
import json
import numpy as np

# Audio fingerprinting
import librosa
import essentia.standard as es
from pyAudioAnalysis import audioBasicIO, audioFeatureExtraction
import chromaprint

# Video fingerprinting  
import cv2
from moviepy.editor import VideoFileClip
import imagehash

# Image fingerprinting
from PIL import Image
import imagehash
import cv2

# Text fingerprinting
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch

# Content similarity
import faiss
from scipy.spatial.distance import cosine

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types d'empreintes numériques"""    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_MFCC = "audio_mfcc"
    VIDEO_PERCEPTUAL = "video_perceptual"
    VIDEO_FRAME_HASH = "video_frame_hash"
    IMAGE_PERCEPTUAL = "image_perceptual"
    IMAGE_DHASH = "image_dhash"
    IMAGE_PHASH = "image_phash"
    TEXT_TFIDF = "text_tfidf"
    TEXT_EMBEDDING = "text_embedding"
    COMBINED = "combined"

@dataclass
class FingerprintResult:
    """Résultat de génération d'empreinte"""    fingerprint_type: FingerprintType
    fingerprint_data: Union[str, bytes, np.ndarray]
    hash_value: str
    similarity_threshold: float
    metadata: Dict[str, Any]
    generation_time: float
    confidence_score: float

@dataclass
class SimilarityMatch:
    """Résultat de correspondance de similarité"""    matched_fingerprint_id: str
    similarity_score: float
    fingerprint_type: FingerprintType
    matched_file_path: str
    match_metadata: Dict[str, Any]
    confidence_level: str

@dataclass
class FingerprintValidationResult:
    """Résultat de validation d'empreinte"""    is_unique: bool
    is_valid: bool
    fingerprint_quality: float  # 0.0 - 1.0
    duplicate_matches: List[SimilarityMatch]
    similar_matches: List[SimilarityMatch]
    fingerprint_results: List[FingerprintResult]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class AudioFingerprintGenerator:
    """Générateur d'empreintes audio avancées"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AudioFingerprintGenerator")
        
        # Configuration Chromaprint
        self.chromaprint_config = {
            'algorithm': chromaprint.ALGORITHM_DEFAULT,
            'duration': 120  # Analyser les 2 premières minutes maximum
        }
        
        # Configuration analyse spectrale
        self.spectral_config = {
            'hop_length': 1024,
            'n_fft': 2048,
            'n_mels': 128,
            'window_size': 2048
        }
    
    def generate_chromaprint_fingerprint(self, file_path: str) -> FingerprintResult:
        """Génère une empreinte Chromaprint"""        start_time = datetime.now()
        
        try:
            # Chargement audio avec librosa
            y, sr = librosa.load(file_path, sr=None, duration=self.chromaprint_config['duration'])
            
            # Conversion pour Chromaprint (int16, mono, 11025 Hz)
            y_chromaprint = librosa.resample(y, orig_sr=sr, target_sr=11025)
            y_chromaprint = (y_chromaprint * 32767).astype(np.int16)
            
            # Génération empreinte Chromaprint
            fingerprint_raw = chromaprint.encode_fingerprint(
                chromaprint.decode_fingerprint(
                    chromaprint.fingerprint(
                        y_chromaprint, 
                        11025,
                        algorithm=self.chromaprint_config['algorithm']
                    )[1]
                )[0]
            )
            
            # Hash de l'empreinte
            hash_value = hashlib.sha256(fingerprint_raw).hexdigest()
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Calcul score de confiance basé sur la durée et qualité
            duration = len(y) / sr
            confidence_score = min(1.0, duration / 30.0)  # Confiance maximale à 30s+
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                fingerprint_data=fingerprint_raw,
                hash_value=hash_value,
                similarity_threshold=0.85,
                metadata={
                    "duration": duration,
                    "sample_rate": sr,
                    "algorithm": "chromaprint_default",
                    "fingerprint_length": len(fingerprint_raw)
                },
                generation_time=generation_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération Chromaprint {file_path}: {e}")
            return FingerprintResult(
                fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                fingerprint_data=b"",
                hash_value="",
                similarity_threshold=0.85,
                metadata={"error": str(e)},
                generation_time=0.0,
                confidence_score=0.0
            )
    
    def generate_spectral_fingerprint(self, file_path: str) -> FingerprintResult:
        """Génère une empreinte spectrale avancée"""        start_time = datetime.now()
        
        try:
            # Chargement audio
            y, sr = librosa.load(file_path, sr=None)
            
            # Extraction caractéristiques spectrales
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=sr, 
                n_mfcc=13,
                hop_length=self.spectral_config['hop_length']
            )
            
            spectral_centroids = librosa.feature.spectral_centroid(
                y=y, 
                sr=sr,
                hop_length=self.spectral_config['hop_length']
            )
            
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=y, 
                sr=sr,
                hop_length=self.spectral_config['hop_length']
            )
            
            chroma = librosa.feature.chroma_stft(
                y=y, 
                sr=sr,
                hop_length=self.spectral_config['hop_length']
            )
            
            # Combinaison des caractéristiques
            features = np.vstack([
                np.mean(mfccs, axis=1),
                np.std(mfccs, axis=1),
                np.mean(spectral_centroids),
                np.std(spectral_centroids), 
                np.mean(spectral_rolloff),
                np.std(spectral_rolloff),
                np.mean(chroma, axis=1),
                np.std(chroma, axis=1)
            ])
            
            # Normalisation
            features_normalized = (features - np.mean(features)) / (np.std(features) + 1e-8)
            
            # Hash de l'empreinte
            fingerprint_bytes = features_normalized.tobytes()
            hash_value = hashlib.sha256(fingerprint_bytes).hexdigest()
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Score de confiance basé sur la variance des caractéristiques
            variance_score = np.mean(np.std(features_normalized))
            confidence_score = min(1.0, variance_score * 10)
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.AUDIO_SPECTRAL,
                fingerprint_data=features_normalized,
                hash_value=hash_value,
                similarity_threshold=0.80,
                metadata={
                    "feature_vector_size": len(features_normalized),
                    "mfcc_coefficients": 13,
                    "sample_rate": sr,
                    "duration": len(y) / sr
                },
                generation_time=generation_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération empreinte spectrale {file_path}: {e}")
            return FingerprintResult(
                fingerprint_type=FingerprintType.AUDIO_SPECTRAL,
                fingerprint_data=np.array([]),
                hash_value="",
                similarity_threshold=0.80,
                metadata={"error": str(e)},
                generation_time=0.0,
                confidence_score=0.0
            )

class VideoFingerprintGenerator:
    """Générateur d'empreintes vidéo avancées"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VideoFingerprintGenerator")
        self.frame_sample_rate = 1.0  # Une frame par seconde
        self.max_frames = 60  # Maximum 60 frames analysées
    
    def generate_perceptual_fingerprint(self, file_path: str) -> FingerprintResult:
        """Génère une empreinte perceptuelle vidéo"""        start_time = datetime.now()
        
        try:
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                raise ValueError("Impossible d'ouvrir le fichier vidéo")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Calcul de l'échantillonnage
            frame_step = max(1, int(fps / self.frame_sample_rate))
            frames_to_process = min(self.max_frames, frame_count // frame_step)
            
            frame_hashes = []
            processed_frames = 0
            
            for i in range(0, frame_count, frame_step):
                if processed_frames >= frames_to_process:
                    break
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Conversion en niveaux de gris
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Redimensionnement pour uniformité
                resized = cv2.resize(gray, (64, 64))
                
                # Calcul hash perceptuel
                frame_hash = self._calculate_perceptual_hash(resized)
                frame_hashes.append(frame_hash)
                
                processed_frames += 1
            
            cap.release()
            
            # Combinaison des hashes
            if frame_hashes:
                combined_hash = hashlib.sha256(
                    ''.join(frame_hashes).encode()
                ).hexdigest()
                
                # Score de confiance basé sur le nombre de frames
                confidence_score = min(1.0, processed_frames / 30.0)
            else:
                combined_hash = ""
                confidence_score = 0.0
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.VIDEO_PERCEPTUAL,
                fingerprint_data=frame_hashes,
                hash_value=combined_hash,
                similarity_threshold=0.75,
                metadata={
                    "duration": duration,
                    "fps": fps,
                    "processed_frames": processed_frames,
                    "frame_step": frame_step
                },
                generation_time=generation_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération empreinte vidéo {file_path}: {e}")
            return FingerprintResult(
                fingerprint_type=FingerprintType.VIDEO_PERCEPTUAL,
                fingerprint_data=[],
                hash_value="",
                similarity_threshold=0.75,
                metadata={"error": str(e)},
                generation_time=0.0,
                confidence_score=0.0
            )
    
    def _calculate_perceptual_hash(self, frame: np.ndarray) -> str:
        """Calcule un hash perceptuel pour une frame"""        # Calcul de la moyenne
        avg = np.mean(frame)
        
        # Comparaison avec la moyenne
        binary_array = frame > avg
        
        # Conversion en string binaire
        binary_string = ''.join(['1' if pixel else '0' for pixel in binary_array.flatten()])
        
        # Hash hexadécimal
        hash_int = int(binary_string, 2)
        return format(hash_int, 'x')[:16]  # Limiter à 16 caractères hex

class ImageFingerprintGenerator:
    """Générateur d'empreintes image avancées"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ImageFingerprintGenerator")
        self.hash_size = 16  # Taille des hashes perceptuels
    
    def generate_perceptual_fingerprint(self, file_path: str) -> FingerprintResult:
        """Génère une empreinte perceptuelle image complète"""        start_time = datetime.now()
        
        try:
            with Image.open(file_path) as img:
                # Conversion en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Génération de plusieurs types de hashes
                dhash = str(imagehash.dhash(img, hash_size=self.hash_size))
                phash = str(imagehash.phash(img, hash_size=self.hash_size))
                ahash = str(imagehash.average_hash(img, hash_size=self.hash_size))
                whash = str(imagehash.whash(img, hash_size=self.hash_size))
                
                # Combinaison des hashes
                combined_hashes = {
                    'dhash': dhash,
                    'phash': phash,
                    'ahash': ahash,
                    'whash': whash
                }
                
                # Hash principal
                main_hash = hashlib.sha256(
                    (dhash + phash + ahash + whash).encode()
                ).hexdigest()
                
                # Calcul score de confiance basé sur la résolution
                width, height = img.size
                pixel_count = width * height
                confidence_score = min(1.0, pixel_count / (1024 * 1024))  # Confiance max à 1MP
                
                generation_time = (datetime.now() - start_time).total_seconds()
                
                return FingerprintResult(
                    fingerprint_type=FingerprintType.IMAGE_PERCEPTUAL,
                    fingerprint_data=combined_hashes,
                    hash_value=main_hash,
                    similarity_threshold=0.85,
                    metadata={
                        "width": width,
                        "height": height,
                        "pixel_count": pixel_count,
                        "mode": img.mode,
                        "hash_size": self.hash_size
                    },
                    generation_time=generation_time,
                    confidence_score=confidence_score
                )
                
        except Exception as e:
            self.logger.error(f"Erreur génération empreinte image {file_path}: {e}")
            return FingerprintResult(
                fingerprint_type=FingerprintType.IMAGE_PERCEPTUAL,
                fingerprint_data={},
                hash_value="",
                similarity_threshold=0.85,
                metadata={"error": str(e)},
                generation_time=0.0,
                confidence_score=0.0
            )

class TextFingerprintGenerator:
    """Générateur d'empreintes texte avancées"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TextFingerprintGenerator")
        
        # Configuration TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Configuration embeddings
        try:
            self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        except:
            self.tokenizer = None
            self.model = None
            self.logger.warning("Modèle d'embeddings non disponible")
    
    def generate_tfidf_fingerprint(self, file_path: str) -> FingerprintResult:
        """Génère une empreinte TF-IDF"""        start_time = datetime.now()
        
        try:
            # Lecture du fichier texte
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            if not text.strip():
                raise ValueError("Fichier texte vide")
            
            # Vectorisation TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            tfidf_vector = tfidf_matrix.toarray()[0]
            
            # Hash du vecteur
            vector_bytes = tfidf_vector.tobytes()
            hash_value = hashlib.sha256(vector_bytes).hexdigest()
            
            # Score de confiance basé sur la longueur du texte
            word_count = len(text.split())
            confidence_score = min(1.0, word_count / 500.0)  # Confiance max à 500 mots
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_TFIDF,
                fingerprint_data=tfidf_vector,
                hash_value=hash_value,
                similarity_threshold=0.70,
                metadata={
                    "word_count": word_count,
                    "character_count": len(text),
                    "vector_size": len(tfidf_vector),
                    "non_zero_features": np.count_nonzero(tfidf_vector)
                },
                generation_time=generation_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération empreinte TF-IDF {file_path}: {e}")
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_TFIDF,
                fingerprint_data=np.array([]),
                hash_value="",
                similarity_threshold=0.70,
                metadata={"error": str(e)},
                generation_time=0.0,
                confidence_score=0.0
            )
    
    def generate_embedding_fingerprint(self, file_path: str) -> FingerprintResult:
        """Génère une empreinte par embeddings sémantiques"""        start_time = datetime.now()
        
        if not self.model or not self.tokenizer:
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_EMBEDDING,
                fingerprint_data=np.array([]),
                hash_value="",
                similarity_threshold=0.80,
                metadata={"error": "Modèle d'embeddings non disponible"},
                generation_time=0.0,
                confidence_score=0.0
            )
        
        try:
            # Lecture du fichier texte
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            # Tokenisation et génération d'embeddings
            inputs = self.tokenizer(
                text[:512],  # Limiter à 512 tokens
                return_tensors='pt',
                truncation=True,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            # Hash des embeddings
            embedding_bytes = embeddings.tobytes()
            hash_value = hashlib.sha256(embedding_bytes).hexdigest()
            
            # Score de confiance basé sur la norme du vecteur
            embedding_norm = np.linalg.norm(embeddings)
            confidence_score = min(1.0, embedding_norm / 10.0)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_EMBEDDING,
                fingerprint_data=embeddings,
                hash_value=hash_value,
                similarity_threshold=0.80,
                metadata={
                    "embedding_dimension": len(embeddings),
                    "text_length": len(text),
                    "embedding_norm": float(embedding_norm),
                    "model": "all-MiniLM-L6-v2"
                },
                generation_time=generation_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération embedding {file_path}: {e}")
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_EMBEDDING,
                fingerprint_data=np.array([]),
                hash_value="",
                similarity_threshold=0.80,
                metadata={"error": str(e)},
                generation_time=0.0,
                confidence_score=0.0
            )

class SimilarityMatcher:
    """Moteur de correspondance et similarité"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SimilarityMatcher")
        
        # Base de données de vecteurs FAISS
        self.faiss_indexes: Dict[FingerprintType, faiss.Index] = {}
        self.fingerprint_database: Dict[str, Dict] = {}
    
    def add_fingerprint_to_database(self, fingerprint_id: str, fingerprint_result: FingerprintResult, file_path: str):
        """Ajoute une empreinte à la base de données"""        try:
            # Stockage métadonnées
            self.fingerprint_database[fingerprint_id] = {
                "fingerprint_result": fingerprint_result,
                "file_path": file_path,
                "created_at": datetime.now(),
                "fingerprint_type": fingerprint_result.fingerprint_type
            }
            
            # Ajout à l'index FAISS si applicable
            if isinstance(fingerprint_result.fingerprint_data, np.ndarray):
                self._add_to_faiss_index(fingerprint_id, fingerprint_result)
                
        except Exception as e:
            self.logger.error(f"Erreur ajout empreinte {fingerprint_id}: {e}")
    
    def find_similar_fingerprints(self, fingerprint_result: FingerprintResult, max_results: int = 10) -> List[SimilarityMatch]:
        """Trouve les empreintes similaires"""        matches = []
        
        try:
            fingerprint_type = fingerprint_result.fingerprint_type
            
            # Recherche par type d'empreinte
            if fingerprint_type in [FingerprintType.AUDIO_SPECTRAL, FingerprintType.TEXT_TFIDF, FingerprintType.TEXT_EMBEDDING]:
                matches = self._find_vector_similarities(fingerprint_result, max_results)
            elif fingerprint_type in [FingerprintType.IMAGE_PERCEPTUAL]:
                matches = self._find_hash_similarities(fingerprint_result, max_results)
            elif fingerprint_type == FingerprintType.VIDEO_PERCEPTUAL:
                matches = self._find_sequence_similarities(fingerprint_result, max_results)
            
            # Tri par score de similarité
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Erreur recherche similarités: {e}")
        
        return matches[:max_results]
    
    def _find_vector_similarities(self, fingerprint_result: FingerprintResult, max_results: int) -> List[SimilarityMatch]:
        """Recherche de similarités vectorielles"""        matches = []
        fingerprint_type = fingerprint_result.fingerprint_type
        
        if fingerprint_type not in self.faiss_indexes:
            return matches
        
        try:
            index = self.faiss_indexes[fingerprint_type]
            query_vector = fingerprint_result.fingerprint_data.reshape(1, -1).astype(np.float32)
            
            # Recherche des k plus proches voisins
            k = min(max_results, index.ntotal)
            if k > 0:
                distances, indices = index.search(query_vector, k)
                
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx != -1:  # Index valide
                        similarity_score = 1.0 - distance  # Conversion distance -> similarité
                        
                        if similarity_score >= fingerprint_result.similarity_threshold:
                            # Récupération des métadonnées
                            fingerprint_id = list(self.fingerprint_database.keys())[idx]
                            db_entry = self.fingerprint_database[fingerprint_id]
                            
                            confidence_level = self._get_confidence_level(similarity_score)
                            
                            matches.append(SimilarityMatch(
                                matched_fingerprint_id=fingerprint_id,
                                similarity_score=similarity_score,
                                fingerprint_type=fingerprint_type,
                                matched_file_path=db_entry["file_path"],
                                match_metadata={
                                    "distance": float(distance),
                                    "index_position": int(idx),
                                    "created_at": db_entry["created_at"].isoformat()
                                },
                                confidence_level=confidence_level
                            ))
                            
        except Exception as e:
            self.logger.error(f"Erreur recherche vectorielle: {e}")
        
        return matches
    
    def _find_hash_similarities(self, fingerprint_result: FingerprintResult, max_results: int) -> List[SimilarityMatch]:
        """Recherche de similarités par hash"""        matches = []
        
        try:
            if isinstance(fingerprint_result.fingerprint_data, dict):
                query_hashes = fingerprint_result.fingerprint_data
                
                for fingerprint_id, db_entry in self.fingerprint_database.items():
                    if db_entry["fingerprint_type"] == fingerprint_result.fingerprint_type:
                        stored_result = db_entry["fingerprint_result"]
                        
                        if isinstance(stored_result.fingerprint_data, dict):
                            similarity_score = self._calculate_hash_similarity(
                                query_hashes, 
                                stored_result.fingerprint_data
                            )
                            
                            if similarity_score >= fingerprint_result.similarity_threshold:
                                confidence_level = self._get_confidence_level(similarity_score)
                                
                                matches.append(SimilarityMatch(
                                    matched_fingerprint_id=fingerprint_id,
                                    similarity_score=similarity_score,
                                    fingerprint_type=fingerprint_result.fingerprint_type,
                                    matched_file_path=db_entry["file_path"],
                                    match_metadata={
                                        "hash_comparison": "perceptual_hashes",
                                        "created_at": db_entry["created_at"].isoformat()
                                    },
                                    confidence_level=confidence_level
                                ))
                                
        except Exception as e:
            self.logger.error(f"Erreur recherche hash: {e}")
        
        return matches
    
    def _calculate_hash_similarity(self, hash1: Dict, hash2: Dict) -> float:
        """Calcule la similarité entre deux sets de hashes"""        if not hash1 or not hash2:
            return 0.0
        
        similarities = []
        
        for hash_type in ['dhash', 'phash', 'ahash', 'whash']:
            if hash_type in hash1 and hash_type in hash2:
                # Calcul distance de Hamming pour hashes perceptuels
                h1 = hash1[hash_type]
                h2 = hash2[hash_type]
                
                if len(h1) == len(h2):
                    hamming_distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
                    max_distance = len(h1)
                    similarity = 1.0 - (hamming_distance / max_distance)
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _add_to_faiss_index(self, fingerprint_id: str, fingerprint_result: FingerprintResult):
        """Ajoute un vecteur à l'index FAISS"""        try:
            fingerprint_type = fingerprint_result.fingerprint_type
            vector = fingerprint_result.fingerprint_data.astype(np.float32)
            
            if fingerprint_type not in self.faiss_indexes:
                # Création nouvel index
                dimension = len(vector)
                index = faiss.IndexFlatIP(dimension)  # Inner Product pour similarité cosinus
                self.faiss_indexes[fingerprint_type] = index
            
            # Ajout du vecteur
            self.faiss_indexes[fingerprint_type].add(vector.reshape(1, -1))
            
        except Exception as e:
            self.logger.error(f"Erreur ajout FAISS: {e}")
    
    def _get_confidence_level(self, similarity_score: float) -> str:
        """Détermine le niveau de confiance"""        if similarity_score >= 0.95:
            return "very_high"
        elif similarity_score >= 0.85:
            return "high"
        elif similarity_score >= 0.75:
            return "medium"
        elif similarity_score >= 0.65:
            return "low"
        else:
            return "very_low"

class FingerprintValidator:
    """Validateur principal d'empreintes numériques"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.FingerprintValidator")
        
        # Générateurs d'empreintes
        self.audio_generator = AudioFingerprintGenerator()
        self.video_generator = VideoFingerprintGenerator()
        self.image_generator = ImageFingerprintGenerator()
        self.text_generator = TextFingerprintGenerator()
        
        # Moteur de correspondance
        self.similarity_matcher = SimilarityMatcher()
        
        # Configuration
        self.duplicate_threshold = 0.95
        self.similarity_threshold = 0.80
    
    def validate_fingerprint(self, file_path: str, content_type: str) -> FingerprintValidationResult:
        """Valide l'empreinte d'un fichier"""        errors = []
        warnings = []
        fingerprint_results = []
        
        try:
            # Génération des empreintes selon le type de contenu
            if content_type == 'audio':
                fingerprint_results = self._generate_audio_fingerprints(file_path)
            elif content_type == 'video':
                fingerprint_results = self._generate_video_fingerprints(file_path)
            elif content_type == 'image':
                fingerprint_results = self._generate_image_fingerprints(file_path)
            elif content_type == 'text':
                fingerprint_results = self._generate_text_fingerprints(file_path)
            else:
                errors.append(f"Type de contenu non supporté: {content_type}")
                return self._create_error_result(errors)
            
            # Vérification de la qualité des empreintes
            quality_score = self._calculate_fingerprint_quality(fingerprint_results)
            
            if quality_score < 0.5:
                warnings.append("Qualité d'empreinte faible")
            
            # Recherche de doublons et similarités
            duplicate_matches = []
            similar_matches = []
            
            for fingerprint_result in fingerprint_results:
                if fingerprint_result.confidence_score > 0.5:
                    matches = self.similarity_matcher.find_similar_fingerprints(fingerprint_result)
                    
                    for match in matches:
                        if match.similarity_score >= self.duplicate_threshold:
                            duplicate_matches.append(match)
                        elif match.similarity_score >= self.similarity_threshold:
                            similar_matches.append(match)
            
            # Détermination de l'unicité
            is_unique = len(duplicate_matches) == 0
            is_valid = len(errors) == 0 and quality_score >= 0.3
            
            if duplicate_matches:
                warnings.append(f"Contenu dupliqué détecté ({len(duplicate_matches)} correspondances)")
            
            if similar_matches:
                warnings.append(f"Contenu similaire détecté ({len(similar_matches)} correspondances)")
            
            return FingerprintValidationResult(
                is_unique=is_unique,
                is_valid=is_valid,
                fingerprint_quality=quality_score,
                duplicate_matches=duplicate_matches,
                similar_matches=similar_matches,
                fingerprint_results=fingerprint_results,
                errors=errors,
                warnings=warnings,
                metadata={
                    "content_type": content_type,
                    "file_path": file_path,
                    "total_fingerprints": len(fingerprint_results),
                    "validation_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erreur validation empreinte {file_path}: {e}")
            return self._create_error_result([f"Erreur système: {str(e)}"])
    
    def _generate_audio_fingerprints(self, file_path: str) -> List[FingerprintResult]:
        """Génère toutes les empreintes audio"""        results = []
        
        # Chromaprint
        chromaprint_result = self.audio_generator.generate_chromaprint_fingerprint(file_path)
        if chromaprint_result.confidence_score > 0:
            results.append(chromaprint_result)
        
        # Spectral
        spectral_result = self.audio_generator.generate_spectral_fingerprint(file_path)
        if spectral_result.confidence_score > 0:
            results.append(spectral_result)
        
        return results
    
    def _generate_video_fingerprints(self, file_path: str) -> List[FingerprintResult]:
        """Génère toutes les empreintes vidéo"""        results = []
        
        # Perceptual
        perceptual_result = self.video_generator.generate_perceptual_fingerprint(file_path)
        if perceptual_result.confidence_score > 0:
            results.append(perceptual_result)
        
        return results
    
    def _generate_image_fingerprints(self, file_path: str) -> List[FingerprintResult]:
        """Génère toutes les empreintes image"""        results = []
        
        # Perceptual
        perceptual_result = self.image_generator.generate_perceptual_fingerprint(file_path)
        if perceptual_result.confidence_score > 0:
            results.append(perceptual_result)
        
        return results
    
    def _generate_text_fingerprints(self, file_path: str) -> List[FingerprintResult]:
        """Génère toutes les empreintes texte"""        results = []
        
        # TF-IDF
        tfidf_result = self.text_generator.generate_tfidf_fingerprint(file_path)
        if tfidf_result.confidence_score > 0:
            results.append(tfidf_result)
        
        # Embeddings
        embedding_result = self.text_generator.generate_embedding_fingerprint(file_path)
        if embedding_result.confidence_score > 0:
            results.append(embedding_result)
        
        return results
    
    def _calculate_fingerprint_quality(self, fingerprint_results: List[FingerprintResult]) -> float:
        """Calcule la qualité globale des empreintes"""        if not fingerprint_results:
            return 0.0
        
        # Moyenne pondérée des scores de confiance
        total_score = sum(result.confidence_score for result in fingerprint_results)
        return total_score / len(fingerprint_results)
    
    def _create_error_result(self, errors: List[str]) -> FingerprintValidationResult:
        """Crée un résultat d'erreur"""        return FingerprintValidationResult(
            is_unique=False,
            is_valid=False,
            fingerprint_quality=0.0,
            duplicate_matches=[],
            similar_matches=[],
            fingerprint_results=[],
            errors=errors,
            warnings=[],
            metadata={}
        )
    
    def register_fingerprint(self, fingerprint_id: str, validation_result: FingerprintValidationResult, file_path: str):
        """Enregistre une empreinte validée dans la base"""        try:
            for fingerprint_result in validation_result.fingerprint_results:
                if fingerprint_result.confidence_score > 0.5:
                    self.similarity_matcher.add_fingerprint_to_database(
                        f"{fingerprint_id}_{fingerprint_result.fingerprint_type.value}",
                        fingerprint_result,
                        file_path
                    )
                    
            self.logger.info(f"Empreinte enregistrée: {fingerprint_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement empreinte {fingerprint_id}: {e}")

class AsyncFingerprintValidator:
    """Version asynchrone du validateur d'empreintes"""    
    def __init__(self):
        self.sync_validator = FingerprintValidator()
        self.logger = logging.getLogger(f"{__name__}.AsyncFingerprintValidator")
    
    async def validate_fingerprint(self, file_path: str, content_type: str) -> FingerprintValidationResult:
        """Valide l'empreinte de manière asynchrone"""        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_validator.validate_fingerprint,
            file_path,
            content_type
        )
        
        return result
    
    async def validate_batch_fingerprints(self, files: List[Tuple[str, str]]) -> Dict[str, FingerprintValidationResult]:
        """Valide un lot d'empreintes de manière asynchrone"""        tasks = []
        
        for file_path, content_type in files:
            task = self.validate_fingerprint(file_path, content_type)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Formatage des résultats
        validation_results = {}
        for i, result in enumerate(results):
            file_path = files[i][0]
            
            if isinstance(result, Exception):
                validation_results[file_path] = FingerprintValidationResult(
                    is_unique=False,
                    is_valid=False,
                    fingerprint_quality=0.0,
                    duplicate_matches=[],
                    similar_matches=[],
                    fingerprint_results=[],
                    errors=[f"Erreur validation: {str(result)}"],
                    warnings=[],
                    metadata={}
                )
            else:
                validation_results[file_path] = result
        
        return validation_results

# Export des classes principales
__all__ = [
    'FingerprintValidator',
    'AsyncFingerprintValidator',
    'FingerprintValidationResult',
    'FingerprintResult',
    'SimilarityMatch',
    'FingerprintType',
    'AudioFingerprintGenerator',
    'VideoFingerprintGenerator',
    'ImageFingerprintGenerator',
    'TextFingerprintGenerator',
    'SimilarityMatcher'
]
