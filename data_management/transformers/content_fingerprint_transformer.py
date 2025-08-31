"""🔐 Content Fingerprint Transformer - IA Influencer Agent Platform Enterprise
=========================================================================
Module: backend/data_management/transformers/content_fingerprint_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Fahed Mlaiel (mlaiel@live.de)
- ML Engineer: Fahed Mlaiel (mlaiel@live.de)
- AI Research Expert: Fahed Mlaiel (mlaiel@live.de)
- DevOps Engineer: Fahed Mlaiel (mlaiel@live.de)
- DBA: Fahed Mlaiel (mlaiel@live.de)
- Sécurité Expert: Fahed Mlaiel (mlaiel@live.de)
"""import asyncio
import logging
import time
import hashlib
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import tempfile

# AI/ML libraries for fingerprinting
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageHash
import cv2
import librosa
import essentia.standard as es
import chromaprint
import imagehash
from sentence_transformers import SentenceTransformer
import face_recognition
import numpy as np
from scipy.spatial.distance import cosine
import faiss

from ..models.fingerprint_models import (
    FingerprintMetadata, ContentSignature, FingerprintResult,
    AudioFingerprint, VideoFingerprint, ImageFingerprint, TextFingerprint
)
from ...core.exceptions import FingerprintError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager
from ...utils.validation import validate_content_file

settings = get_settings()
logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types d'empreintes supportées"""    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_MFCC = "audio_mfcc"
    VIDEO_PHASH = "video_phash"
    VIDEO_HISTOGRAM = "video_histogram"
    VIDEO_OPTICAL_FLOW = "video_optical_flow"
    IMAGE_PHASH = "image_phash"
    IMAGE_DHASH = "image_dhash"
    IMAGE_AHASH = "image_ahash"
    IMAGE_WHASH = "image_whash"
    IMAGE_FACE = "image_face"
    TEXT_SEMANTIC = "text_semantic"
    TEXT_SYNTACTIC = "text_syntactic"
    TEXT_STRUCTURAL = "text_structural"

class FingerprintAlgorithm(Enum):
    """Algorithmes d'empreintes supportés"""    CHROMAPRINT = "chromaprint"
    ESSENTIA = "essentia"
    PERCEPTUAL_HASH = "perceptual_hash"
    DIFFERENCE_HASH = "difference_hash"
    AVERAGE_HASH = "average_hash"
    WAVELET_HASH = "wavelet_hash"
    FACE_ENCODING = "face_encoding"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    BERT_EMBEDDINGS = "bert_embeddings"
    CLIP_EMBEDDINGS = "clip_embeddings"

@dataclass
class FingerprintConfig:
    """Configuration pour l'empreinte digitale"""    algorithm: FingerprintAlgorithm
    fingerprint_type: FingerprintType
    parameters: Dict[str, Any]
    similarity_threshold: float = 0.85
    vector_dimensions: Optional[int] = None
    preprocessing: Optional[Dict[str, Any]] = None

@dataclass
class ContentFingerprintResult:
    """Résultat d'empreinte de contenu"""    success: bool
    content_path: str
    fingerprint_type: FingerprintType
    algorithm: FingerprintAlgorithm
    fingerprint_data: Union[str, bytes, np.ndarray]
    vector_embedding: Optional[np.ndarray]
    metadata: Dict[str, Any]
    confidence_score: float
    processing_time: float
    errors: List[str]

class AudioFingerprintTransformer:
    """Transformateur d'empreintes audio professionnel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
        
        # Initialisation des modèles audio
        self._init_audio_models()
    
    def _init_audio_models(self):
        """Initialise les modèles pour l'analyse audio"""        try:
            # Essentia algorithms
            self.onset_detector = es.OnsetDetection(method='hfc')
            self.spectral_peaks = es.SpectralPeaks()
            self.hpcp = es.HPCP()
            self.tempo_detector = es.PercivalBpmEstimator()
            
            # MFCCs
            self.mfcc = es.MFCC()
            
            logger.info("Modèles audio initialisés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles audio: {e}")
            raise FingerprintError(f"Échec initialisation audio: {e}")
    
    def generate_chromaprint_fingerprint(
        self,
        audio_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte Chromaprint"""        
        start_time = time.time()
        
        try:
            # Chargement audio avec librosa
            y, sr = librosa.load(audio_path, sr=config.parameters.get('sample_rate', 22050))
            
            # Génération Chromaprint
            duration = config.parameters.get('duration', 120)  # 2 minutes par défaut
            if len(y) / sr > duration:
                y = y[:int(duration * sr)]
            
            # Conversion pour chromaprint
            y_int16 = (y * 32767).astype(np.int16)
            
            # Génération de l'empreinte
            fingerprint = chromaprint.encode(y_int16, sr)
            
            # Extraction des caractéristiques spectrales
            spectral_features = self._extract_spectral_features(y, sr)
            
            processing_time = time.time() - start_time
            
            return ContentFingerprintResult(
                success=True,
                content_path=audio_path,
                fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                algorithm=FingerprintAlgorithm.CHROMAPRINT,
                fingerprint_data=fingerprint,
                vector_embedding=spectral_features,
                metadata={
                    'sample_rate': sr,
                    'duration': len(y) / sr,
                    'channels': 1,
                    'format': Path(audio_path).suffix
                },
                confidence_score=0.95,
                processing_time=processing_time,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur génération Chromaprint {audio_path}: {e}")
            return ContentFingerprintResult(
                success=False,
                content_path=audio_path,
                fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                algorithm=FingerprintAlgorithm.CHROMAPRINT,
                fingerprint_data="",
                vector_embedding=None,
                metadata={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur Chromaprint: {str(e)}"]
            )
    
    def generate_spectral_fingerprint(
        self,
        audio_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte spectrale avancée"""        
        start_time = time.time()
        
        try:
            # Chargement audio
            y, sr = librosa.load(audio_path, sr=config.parameters.get('sample_rate', 22050))
            
            # Analyse spectrale complète
            spectral_features = {
                'chroma': librosa.feature.chroma_stft(y=y, sr=sr),
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
                'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr),
                'spectral_bandwidth': librosa.feature.spectral_bandwidth(y=y, sr=sr),
                'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr),
                'zero_crossing_rate': librosa.feature.zero_crossing_rate(y),
                'tempo': librosa.beat.tempo(y=y, sr=sr)
            }
            
            # Création d'un vecteur de caractéristiques unifié
            feature_vector = self._create_unified_audio_vector(spectral_features)
            
            # Hash de l'empreinte spectrale
            feature_hash = hashlib.sha256(feature_vector.tobytes()).hexdigest()
            
            processing_time = time.time() - start_time
            
            return ContentFingerprintResult(
                success=True,
                content_path=audio_path,
                fingerprint_type=FingerprintType.AUDIO_SPECTRAL,
                algorithm=FingerprintAlgorithm.ESSENTIA,
                fingerprint_data=feature_hash,
                vector_embedding=feature_vector,
                metadata={
                    'spectral_features': {k: v.tolist() if hasattr(v, 'tolist') else v 
                                        for k, v in spectral_features.items()},
                    'sample_rate': sr,
                    'duration': len(y) / sr
                },
                confidence_score=0.92,
                processing_time=processing_time,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur génération spectrale {audio_path}: {e}")
            return ContentFingerprintResult(
                success=False,
                content_path=audio_path,
                fingerprint_type=FingerprintType.AUDIO_SPECTRAL,
                algorithm=FingerprintAlgorithm.ESSENTIA,
                fingerprint_data="",
                vector_embedding=None,
                metadata={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur spectrale: {str(e)}"]
            )
    
    def _extract_spectral_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extrait les caractéristiques spectrales"""        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # MFCC features
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        
        # Combinaison des caractéristiques
        features = np.concatenate([
            chroma_mean,
            mfcc_mean,
            [spectral_centroid, spectral_bandwidth, spectral_rolloff]
        ])
        
        return features
    
    def _create_unified_audio_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Crée un vecteur unifié à partir des caractéristiques audio"""        
        vectors = []
        
        for key, value in features.items():
            if isinstance(value, np.ndarray):
                if value.ndim > 1:
                    vectors.append(np.mean(value, axis=1))
                else:
                    vectors.append(value)
            else:
                vectors.append(np.array([value]))
        
        return np.concatenate(vectors)

class VideoFingerprintTransformer:
    """Transformateur d'empreintes vidéo professionnel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        
        # Initialisation des détecteurs
        self._init_video_models()
    
    def _init_video_models(self):
        """Initialise les modèles pour l'analyse vidéo"""        try:
            # Détecteur de caractéristiques
            self.feature_detector = cv2.SIFT_create()
            self.orb_detector = cv2.ORB_create()
            
            # Détecteur de flux optique
            self.optical_flow = cv2.FarnebackOpticalFlow_create()
            
            logger.info("Modèles vidéo initialisés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles vidéo: {e}")
            raise FingerprintError(f"Échec initialisation vidéo: {e}")
    
    def generate_perceptual_hash(
        self,
        video_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère un hash perceptuel vidéo"""        
        start_time = time.time()
        
        try:
            cap = cv2.VideoCapture(video_path)
            frame_hashes = []
            frame_count = 0
            
            # Paramètres de sampling
            frame_skip = config.parameters.get('frame_skip', 30)  # 1 frame toutes les 30
            max_frames = config.parameters.get('max_frames', 100)
            
            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_skip == 0:
                    # Conversion en niveaux de gris
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Redimensionnement pour cohérence
                    resized = cv2.resize(gray, (64, 64))
                    
                    # Hash perceptuel
                    frame_hash = self._compute_perceptual_hash(resized)
                    frame_hashes.append(frame_hash)
                
                frame_count += 1
            
            cap.release()
            
            # Combinaison des hashes de frames
            if frame_hashes:
                combined_hash = self._combine_frame_hashes(frame_hashes)
                video_vector = np.array(frame_hashes).flatten()
            else:
                combined_hash = ""
                video_vector = np.array([])
            
            processing_time = time.time() - start_time
            
            return ContentFingerprintResult(
                success=True,
                content_path=video_path,
                fingerprint_type=FingerprintType.VIDEO_PHASH,
                algorithm=FingerprintAlgorithm.PERCEPTUAL_HASH,
                fingerprint_data=combined_hash,
                vector_embedding=video_vector,
                metadata={
                    'total_frames': frame_count,
                    'sampled_frames': len(frame_hashes),
                    'frame_skip': frame_skip
                },
                confidence_score=0.88,
                processing_time=processing_time,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur génération hash vidéo {video_path}: {e}")
            return ContentFingerprintResult(
                success=False,
                content_path=video_path,
                fingerprint_type=FingerprintType.VIDEO_PHASH,
                algorithm=FingerprintAlgorithm.PERCEPTUAL_HASH,
                fingerprint_data="",
                vector_embedding=None,
                metadata={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur hash vidéo: {str(e)}"]
            )
    
    def _compute_perceptual_hash(self, frame: np.ndarray) -> str:
        """Calcule le hash perceptuel d'une frame"""        
        # Réduction à 8x8 pixels
        resized = cv2.resize(frame, (8, 8))
        
        # Calcul de la moyenne
        avg = resized.mean()
        
        # Génération du hash binaire
        hash_bits = []
        for row in resized:
            for pixel in row:
                hash_bits.append('1' if pixel > avg else '0')
        
        # Conversion en hexadécimal
        binary_str = ''.join(hash_bits)
        hex_hash = hex(int(binary_str, 2))[2:]
        
        return hex_hash
    
    def _combine_frame_hashes(self, frame_hashes: List[str]) -> str:
        """Combine les hashes de frames en un hash vidéo global"""        
        combined = ''.join(frame_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()

class ImageFingerprintTransformer:
    """Transformateur d'empreintes image professionnel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp', '.gif'}
        
        # Initialisation des modèles
        self._init_image_models()
    
    def _init_image_models(self):
        """Initialise les modèles pour l'analyse d'images"""        try:
            # Détecteur de visages
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Détecteur de caractéristiques
            self.sift = cv2.SIFT_create()
            self.orb = cv2.ORB_create()
            
            logger.info("Modèles image initialisés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles image: {e}")
            raise FingerprintError(f"Échec initialisation image: {e}")
    
    def generate_multiple_hashes(
        self,
        image_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère plusieurs types de hashes pour robustesse"""        
        start_time = time.time()
        
        try:
            # Chargement de l'image
            image = Image.open(image_path)
            
            # Génération de multiples hashes
            hashes = {
                'phash': str(imagehash.phash(image)),
                'ahash': str(imagehash.average_hash(image)),
                'dhash': str(imagehash.dhash(image)),
                'whash': str(imagehash.whash(image))
            }
            
            # Détection de visages si demandé
            face_encodings = []
            if config.parameters.get('detect_faces', False):
                face_encodings = self._extract_face_encodings(image_path)
            
            # Création d'un vecteur de caractéristiques combiné
            combined_vector = self._create_image_feature_vector(image, hashes, face_encodings)
            
            # Hash combiné
            combined_hash = hashlib.sha256(
                ''.join(hashes.values()).encode()
            ).hexdigest()
            
            processing_time = time.time() - start_time
            
            return ContentFingerprintResult(
                success=True,
                content_path=image_path,
                fingerprint_type=FingerprintType.IMAGE_PHASH,
                algorithm=FingerprintAlgorithm.PERCEPTUAL_HASH,
                fingerprint_data=combined_hash,
                vector_embedding=combined_vector,
                metadata={
                    'individual_hashes': hashes,
                    'image_size': image.size,
                    'image_mode': image.mode,
                    'face_count': len(face_encodings),
                    'has_faces': len(face_encodings) > 0
                },
                confidence_score=0.93,
                processing_time=processing_time,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur génération hashes image {image_path}: {e}")
            return ContentFingerprintResult(
                success=False,
                content_path=image_path,
                fingerprint_type=FingerprintType.IMAGE_PHASH,
                algorithm=FingerprintAlgorithm.PERCEPTUAL_HASH,
                fingerprint_data="",
                vector_embedding=None,
                metadata={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur hashes image: {str(e)}"]
            )
    
    def _extract_face_encodings(self, image_path: str) -> List[np.ndarray]:
        """Extrait les encodages de visages"""        
        try:
            # Chargement de l'image pour face_recognition
            image = face_recognition.load_image_file(image_path)
            
            # Détection des visages
            face_locations = face_recognition.face_locations(image)
            
            # Encodage des visages
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return face_encodings
            
        except Exception as e:
            logger.warning(f"Erreur extraction visages {image_path}: {e}")
            return []
    
    def _create_image_feature_vector(
        self,
        image: Image.Image,
        hashes: Dict[str, str],
        face_encodings: List[np.ndarray]
    ) -> np.ndarray:
        """Crée un vecteur de caractéristiques d'image"""        
        features = []
        
        # Conversion des hashes en valeurs numériques
        for hash_type, hash_value in hashes.items():
            # Conversion hex en int puis normalisation
            hash_int = int(hash_value, 16) if hash_value else 0
            features.append(hash_int % 1000)  # Normalisation simple
        
        # Ajout des caractéristiques d'image de base
        features.extend([
            image.size[0],  # largeur
            image.size[1],  # hauteur
            len(image.getbands()),  # nombre de canaux
        ])
        
        # Ajout d'un représentant des visages si présents
        if face_encodings:
            # Moyenne des encodages de visages
            face_mean = np.mean(face_encodings, axis=0)
            features.extend(face_mean[:10])  # Premiers 10 composants
        else:
            features.extend([0] * 10)  # Padding si pas de visages
        
        return np.array(features, dtype=np.float32)

class TextFingerprintTransformer:
    """Transformateur d'empreintes texte professionnel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des modèles NLP
        self._init_text_models()
    
    def _init_text_models(self):
        """Initialise les modèles pour l'analyse de texte"""        try:
            # Modèle de sentence embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Modèles texte initialisés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation modèles texte: {e}")
            raise FingerprintError(f"Échec initialisation texte: {e}")
    
    def generate_semantic_fingerprint(
        self,
        text_content: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte sémantique du texte"""        
        start_time = time.time()
        
        try:
            # Nettoyage du texte
            cleaned_text = self._clean_text(text_content)
            
            # Génération d'embeddings sémantiques
            semantic_embedding = self.sentence_model.encode(cleaned_text)
            
            # Caractéristiques structurelles
            structural_features = self._extract_structural_features(cleaned_text)
            
            # Combinaison des caractéristiques
            combined_features = np.concatenate([
                semantic_embedding,
                structural_features
            ])
            
            # Hash du contenu textuel
            content_hash = hashlib.sha256(cleaned_text.encode('utf-8')).hexdigest()
            
            processing_time = time.time() - start_time
            
            return ContentFingerprintResult(
                success=True,
                content_path="text_content",
                fingerprint_type=FingerprintType.TEXT_SEMANTIC,
                algorithm=FingerprintAlgorithm.SENTENCE_TRANSFORMERS,
                fingerprint_data=content_hash,
                vector_embedding=combined_features,
                metadata={
                    'text_length': len(cleaned_text),
                    'word_count': len(cleaned_text.split()),
                    'character_count': len(text_content),
                    'language_detected': self._detect_language(cleaned_text),
                    'structural_complexity': float(np.mean(structural_features))
                },
                confidence_score=0.90,
                processing_time=processing_time,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur génération empreinte texte: {e}")
            return ContentFingerprintResult(
                success=False,
                content_path="text_content",
                fingerprint_type=FingerprintType.TEXT_SEMANTIC,
                algorithm=FingerprintAlgorithm.SENTENCE_TRANSFORMERS,
                fingerprint_data="",
                vector_embedding=None,
                metadata={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur empreinte texte: {str(e)}"]
            )
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte pour l'analyse"""        
        # Suppression des caractères spéciaux en excès
        import re
        
        # Normalisation des espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Suppression des caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def _extract_structural_features(self, text: str) -> np.ndarray:
        """Extrait les caractéristiques structurelles du texte"""        
        import re
        
        features = []
        
        # Longueurs
        features.append(len(text))
        features.append(len(text.split()))
        features.append(len(text.split('.')))
        
        # Caractéristiques lexicales
        features.append(len(re.findall(r'[A-Z]', text)))  # Majuscules
        features.append(len(re.findall(r'[0-9]', text)))  # Chiffres
        features.append(len(re.findall(r'[^\w\s]', text)))  # Ponctuation
        
        # Ratios
        if len(text) > 0:
            features.append(len(text.split()) / len(text))  # Densité de mots
            features.append(len(re.findall(r'[A-Z]', text)) / len(text))  # Ratio majuscules
        else:
            features.extend([0, 0])
        
        # Moyenne de longueur des mots
        words = text.split()
        if words:
            features.append(np.mean([len(word) for word in words]))
        else:
            features.append(0)
        
        return np.array(features, dtype=np.float32)
    
    def _detect_language(self, text: str) -> str:
        """Détection simple de la langue"""        
        # Détection basique basée sur les caractères fréquents
        if re.search(r'[àâäçéèêëïîôùûüÿñæœ]', text.lower()):
            return 'fr'
        elif re.search(r'[äöüß]', text.lower()):
            return 'de'
        elif re.search(r'[áéíóúüñ¿¡]', text.lower()):
            return 'es'
        else:
            return 'en'

class ContentFingerprintTransformer:
    """Gestionnaire principal des empreintes de contenu"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des transformateurs spécialisés
        self.audio_transformer = AudioFingerprintTransformer()
        self.video_transformer = VideoFingerprintTransformer()
        self.image_transformer = ImageFingerprintTransformer()
        self.text_transformer = TextFingerprintTransformer()
        
        # Configuration de FAISS pour la recherche vectorielle
        self.vector_index = None
        self._init_vector_search()
    
    def _init_vector_search(self):
        """Initialise l'index FAISS pour la recherche vectorielle"""        try:
            # Index FAISS pour la similarité cosinus
            dimension = 512  # Dimension par défaut
            self.vector_index = faiss.IndexFlatIP(dimension)
            
            logger.info("Index FAISS initialisé avec succès")
            
        except Exception as e:
            logger.warning(f"Erreur initialisation FAISS: {e}")
    
    def generate_fingerprint(
        self,
        content_path: str,
        fingerprint_config: FingerprintConfig,
        creator_type: Optional[str] = None
    ) -> ContentFingerprintResult:
        """Génère une empreinte pour tout type de contenu"""        
        try:
            # Validation du fichier
            if not Path(content_path).exists():
                raise ValidationError(f"Fichier non trouvé: {content_path}")
            
            # Détermination du type de contenu
            content_type = self._detect_content_type(content_path)
            
            # Routage vers le transformateur approprié
            if content_type == 'audio':
                return self._generate_audio_fingerprint(content_path, fingerprint_config)
            elif content_type == 'video':
                return self._generate_video_fingerprint(content_path, fingerprint_config)
            elif content_type == 'image':
                return self._generate_image_fingerprint(content_path, fingerprint_config)
            elif content_type == 'text':
                return self._generate_text_fingerprint(content_path, fingerprint_config)
            else:
                raise ValidationError(f"Type de contenu non supporté: {content_type}")
                
        except Exception as e:
            logger.error(f"Erreur génération empreinte {content_path}: {e}")
            return ContentFingerprintResult(
                success=False,
                content_path=content_path,
                fingerprint_type=fingerprint_config.fingerprint_type,
                algorithm=fingerprint_config.algorithm,
                fingerprint_data="",
                vector_embedding=None,
                metadata={},
                confidence_score=0.0,
                processing_time=0.0,
                errors=[f"Erreur génération: {str(e)}"]
            )
    
    def _detect_content_type(self, content_path: str) -> str:
        """Détecte le type de contenu basé sur l'extension"""        
        ext = Path(content_path).suffix.lower()
        
        audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        image_exts = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp', '.gif'}
        text_exts = {'.txt', '.md', '.html', '.xml', '.json'}
        
        if ext in audio_exts:
            return 'audio'
        elif ext in video_exts:
            return 'video'
        elif ext in image_exts:
            return 'image'
        elif ext in text_exts:
            return 'text'
        else:
            return 'unknown'
    
    def _generate_audio_fingerprint(
        self,
        audio_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte audio"""        
        if config.fingerprint_type == FingerprintType.AUDIO_CHROMAPRINT:
            return self.audio_transformer.generate_chromaprint_fingerprint(audio_path, config)
        elif config.fingerprint_type == FingerprintType.AUDIO_SPECTRAL:
            return self.audio_transformer.generate_spectral_fingerprint(audio_path, config)
        else:
            raise ValidationError(f"Type d'empreinte audio non supporté: {config.fingerprint_type}")
    
    def _generate_video_fingerprint(
        self,
        video_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte vidéo"""        
        if config.fingerprint_type == FingerprintType.VIDEO_PHASH:
            return self.video_transformer.generate_perceptual_hash(video_path, config)
        else:
            raise ValidationError(f"Type d'empreinte vidéo non supporté: {config.fingerprint_type}")
    
    def _generate_image_fingerprint(
        self,
        image_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte image"""        
        if config.fingerprint_type in [
            FingerprintType.IMAGE_PHASH,
            FingerprintType.IMAGE_DHASH,
            FingerprintType.IMAGE_AHASH,
            FingerprintType.IMAGE_WHASH
        ]:
            return self.image_transformer.generate_multiple_hashes(image_path, config)
        else:
            raise ValidationError(f"Type d'empreinte image non supporté: {config.fingerprint_type}")
    
    def _generate_text_fingerprint(
        self,
        text_path: str,
        config: FingerprintConfig
    ) -> ContentFingerprintResult:
        """Génère une empreinte texte"""        
        # Lecture du contenu textuel
        with open(text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        if config.fingerprint_type == FingerprintType.TEXT_SEMANTIC:
            return self.text_transformer.generate_semantic_fingerprint(text_content, config)
        else:
            raise ValidationError(f"Type d'empreinte texte non supporté: {config.fingerprint_type}")
    
    def compare_fingerprints(
        self,
        fingerprint1: ContentFingerprintResult,
        fingerprint2: ContentFingerprintResult,
        similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """Compare deux empreintes pour déterminer la similarité"""        
        if fingerprint1.fingerprint_type != fingerprint2.fingerprint_type:
            return {
                'similarity_score': 0.0,
                'is_similar': False,
                'comparison_type': 'incompatible_types',
                'details': 'Types d\'empreintes différents'
            }
        
        try:
            # Comparaison des vecteurs d'embedding si disponibles
            if (fingerprint1.vector_embedding is not None and 
                fingerprint2.vector_embedding is not None):
                
                similarity = self._compute_vector_similarity(
                    fingerprint1.vector_embedding,
                    fingerprint2.vector_embedding
                )
            else:
                # Comparaison des hashes
                similarity = self._compute_hash_similarity(
                    fingerprint1.fingerprint_data,
                    fingerprint2.fingerprint_data
                )
            
            is_similar = similarity >= similarity_threshold
            
            return {
                'similarity_score': similarity,
                'is_similar': is_similar,
                'comparison_type': 'vector' if fingerprint1.vector_embedding is not None else 'hash',
                'threshold_used': similarity_threshold,
                'details': f'Score de similarité: {similarity:.4f}'
            }
            
        except Exception as e:
            logger.error(f"Erreur comparaison empreintes: {e}")
            return {
                'similarity_score': 0.0,
                'is_similar': False,
                'comparison_type': 'error',
                'details': f'Erreur: {str(e)}'
            }
    
    def _compute_vector_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray
    ) -> float:
        """Calcule la similarité entre deux vecteurs"""        
        # Normalisation des vecteurs
        v1_norm = vector1 / np.linalg.norm(vector1)
        v2_norm = vector2 / np.linalg.norm(vector2)
        
        # Similarité cosinus
        similarity = 1 - cosine(v1_norm, v2_norm)
        
        return max(0.0, min(1.0, similarity))
    
    def _compute_hash_similarity(
        self,
        hash1: Union[str, bytes],
        hash2: Union[str, bytes]
    ) -> float:
        """Calcule la similarité entre deux hashes"""        
        if hash1 == hash2:
            return 1.0
        
        # Conversion en chaînes si nécessaire
        if isinstance(hash1, bytes):
            hash1 = hash1.hex()
        if isinstance(hash2, bytes):
            hash2 = hash2.hex()
        
        # Distance de Hamming pour hashes binaires
        if len(hash1) == len(hash2):
            differences = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            similarity = 1.0 - (differences / len(hash1))
            return max(0.0, similarity)
        
        return 0.0
    
    async def batch_generate_fingerprints(
        self,
        content_paths: List[str],
        config: FingerprintConfig,
        creator_type: Optional[str] = None
    ) -> List[ContentFingerprintResult]:
        """Génère des empreintes en lot de manière asynchrone"""        
        tasks = []
        for path in content_paths:
            task = asyncio.create_task(
                self._async_generate_fingerprint(path, config, creator_type)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des résultats et exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erreur fingerprint {content_paths[i]}: {result}")
                processed_results.append(ContentFingerprintResult(
                    success=False,
                    content_path=content_paths[i],
                    fingerprint_type=config.fingerprint_type,
                    algorithm=config.algorithm,
                    fingerprint_data="",
                    vector_embedding=None,
                    metadata={},
                    confidence_score=0.0,
                    processing_time=0.0,
                    errors=[f"Exception: {str(result)}"]
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _async_generate_fingerprint(
        self,
        content_path: str,
        config: FingerprintConfig,
        creator_type: Optional[str] = None
    ) -> ContentFingerprintResult:
        """Version asynchrone de la génération d'empreinte"""        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_fingerprint,
            content_path,
            config,
            creator_type
        )

# Instance globale
content_fingerprint_transformer = ContentFingerprintTransformer()

# Export des classes principales
__all__ = [
    'ContentFingerprintTransformer',
    'AudioFingerprintTransformer',
    'VideoFingerprintTransformer',
    'ImageFingerprintTransformer',
    'TextFingerprintTransformer',
    'FingerprintConfig',
    'ContentFingerprintResult',
    'FingerprintType',
    'FingerprintAlgorithm',
    'content_fingerprint_transformer'
]
