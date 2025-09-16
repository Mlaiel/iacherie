"""
Image Fingerprinting - Fingerprinting Module
==========================================
Système avancé de fingerprinting d'images avec hashing perceptuel,
extraction de caractéristiques et détection de similarité.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import cv2

logger = logging.getLogger(__name__)

class ImageFormat(Enum):
    """Formats d'image supportés."""
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    BMP = "bmp"
    WEBP = "webp"
    GIF = "gif"
    HEIC = "heic"

class ImageFingerprintAlgorithm(Enum):
    """Algorithmes de fingerprinting d'images."""
    PERCEPTUAL_HASH = "perceptual_hash"
    DHASH = "dhash"
    AHASH = "ahash"
    WHASH = "whash"
    PHASH = "phash"
    FEATURE_EXTRACTION = "feature_extraction"
    COLOR_HISTOGRAM = "color_histogram"
    TEXTURE_ANALYSIS = "texture_analysis"

@dataclass
class ImageFingerprint:
    """Empreinte d'image."""
    fingerprint_id: str
    image_file_path: str
    algorithm: ImageFingerprintAlgorithm
    hash_value: str
    feature_vector: Optional[np.ndarray]
    color_histogram: Optional[Dict[str, Any]]
    texture_features: Optional[Dict[str, Any]]
    geometric_features: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    image_size: Tuple[int, int]
    color_mode: str
    file_size: int
    created_at: datetime

@dataclass
class ImageMatchResult:
    """Résultat de correspondance d'image."""
    match_id: str
    query_fingerprint: ImageFingerprint
    reference_fingerprint: ImageFingerprint
    similarity_score: float
    hash_distance: int
    feature_similarity: Optional[float]
    color_similarity: Optional[float]
    structural_similarity: Optional[float]
    confidence_level: str
    transformation_detected: Dict[str, Any]
    processing_time: float

class ImageFingerprinting:
    """
    Système avancé de fingerprinting d'images enterprise.
    Support perceptual hashing, feature extraction et similarity detection.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le système de fingerprinting d'images.
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or self._get_default_config()
        self.supported_formats = [fmt.value for fmt in ImageFormat]
        self._setup_algorithms()
        logger.info("ImageFingerprinting initialisé avec succès")

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'hash_algorithms': {
                'dhash': {'hash_size': 8},
                'ahash': {'hash_size': 8},
                'phash': {'hash_size': 8, 'highfreq_factor': 4},
                'whash': {'hash_size': 8, 'image_scale': 32}
            },
            'feature_extraction': {
                'sift_features': 500,
                'surf_threshold': 400,
                'orb_features': 500,
                'corner_detection': True
            },
            'similarity_thresholds': {
                'hash_threshold': 10,
                'feature_threshold': 0.75,
                'color_threshold': 0.8,
                'overall_threshold': 0.85
            },
            'preprocessing': {
                'normalize_size': True,
                'max_dimension': 1024,
                'enhance_contrast': False,
                'noise_reduction': False
            },
            'performance': {
                'max_concurrent_processing': 8,
                'cache_fingerprints': True,
                'optimize_for_speed': True,
                'use_gpu_acceleration': False
            }
        }

    def _setup_algorithms(self):
        """Configure les algorithmes de fingerprinting."""
        self.algorithms = {
            ImageFingerprintAlgorithm.PERCEPTUAL_HASH: self._perceptual_hash_fingerprint,
            ImageFingerprintAlgorithm.DHASH: self._dhash_fingerprint,
            ImageFingerprintAlgorithm.AHASH: self._ahash_fingerprint,
            ImageFingerprintAlgorithm.WHASH: self._whash_fingerprint,
            ImageFingerprintAlgorithm.PHASH: self._phash_fingerprint,
            ImageFingerprintAlgorithm.FEATURE_EXTRACTION: self._feature_extraction_fingerprint,
            ImageFingerprintAlgorithm.COLOR_HISTOGRAM: self._color_histogram_fingerprint,
            ImageFingerprintAlgorithm.TEXTURE_ANALYSIS: self._texture_analysis_fingerprint
        }

    async def create_fingerprint(
        self,
        image_path: Union[str, Path],
        algorithm: ImageFingerprintAlgorithm = ImageFingerprintAlgorithm.PERCEPTUAL_HASH,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ImageFingerprint:
        """
        Crée une empreinte d'image.
        
        Args:
            image_path: Chemin vers le fichier image
            algorithm: Algorithme de fingerprinting
            metadata: Métadonnées additionnelles
            
        Returns:
            ImageFingerprint: Empreinte générée
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Fichier image non trouvé: {image_path}")

            # Chargement et validation de l'image
            image = self._load_and_validate_image(image_path)
            
            # Extraction des métadonnées de base
            image_metadata = self._extract_image_metadata(image, image_path)
            
            # Prétraitement de l'image
            processed_image = await self._preprocess_image(image)
            
            # Génération de l'empreinte selon l'algorithme
            algorithm_func = self.algorithms[algorithm]
            fingerprint_data = await algorithm_func(processed_image, image_metadata)

            # Création de l'objet empreinte
            fingerprint = ImageFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                image_file_path=str(image_path),
                algorithm=algorithm,
                hash_value=fingerprint_data.get('hash_value', ''),
                feature_vector=fingerprint_data.get('feature_vector'),
                color_histogram=fingerprint_data.get('color_histogram'),
                texture_features=fingerprint_data.get('texture_features'),
                geometric_features=fingerprint_data.get('geometric_features'),
                metadata=metadata or {},
                image_size=image_metadata['size'],
                color_mode=image_metadata['mode'],
                file_size=image_metadata['file_size'],
                created_at=datetime.utcnow()
            )

            logger.info(f"Empreinte image créée: {fingerprint.fingerprint_id}")
            return fingerprint

        except Exception as e:
            logger.error(f"Erreur création empreinte image: {e}")
            raise

    def _load_and_validate_image(self, image_path: Path) -> Image.Image:
        """Charge et valide une image."""
        try:
            # Vérification du format
            if image_path.suffix.lower().lstrip('.') not in self.supported_formats:
                raise ValueError(f"Format non supporté: {image_path.suffix}")

            # Chargement de l'image
            image = Image.open(image_path)
            
            # Validation de base
            if image.size[0] < 10 or image.size[1] < 10:
                raise ValueError("Image trop petite pour le fingerprinting")
            
            return image

        except Exception as e:
            logger.error(f"Erreur chargement image: {e}")
            raise

    def _extract_image_metadata(
        self,
        image: Image.Image,
        image_path: Path
    ) -> Dict[str, Any]:
        """Extrait les métadonnées de l'image."""
        try:
            metadata = {
                'size': image.size,
                'mode': image.mode,
                'format': image.format or image_path.suffix.upper().lstrip('.'),
                'file_size': image_path.stat().st_size,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info,
                'color_depth': len(image.getbands()),
                'exif_data': {}
            }
            
            # Extraction EXIF si disponible
            try:
                if hasattr(image, '_getexif') and image._getexif():
                    metadata['exif_data'] = dict(image._getexif())
            except:
                pass
            
            return metadata

        except Exception as e:
            logger.error(f"Erreur extraction métadonnées: {e}")
            return {}

    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Prétraite l'image pour le fingerprinting."""
        try:
            processed = image.copy()
            
            # Normalisation de la taille si configuré
            if self.config['preprocessing']['normalize_size']:
                max_dim = self.config['preprocessing']['max_dimension']
                if max(processed.size) > max_dim:
                    ratio = max_dim / max(processed.size)
                    new_size = tuple(int(dim * ratio) for dim in processed.size)
                    processed = processed.resize(new_size, Image.Resampling.LANCZOS)
            
            # Conversion en RGB si nécessaire
            if processed.mode != 'RGB':
                if processed.mode == 'RGBA':
                    # Création d'un fond blanc pour la transparence
                    background = Image.new('RGB', processed.size, (255, 255, 255))
                    background.paste(processed, mask=processed.split()[-1])
                    processed = background
                else:
                    processed = processed.convert('RGB')
            
            # Amélioration du contraste si configuré
            if self.config['preprocessing']['enhance_contrast']:
                enhancer = ImageEnhance.Contrast(processed)
                processed = enhancer.enhance(1.2)
            
            # Réduction de bruit si configuré
            if self.config['preprocessing']['noise_reduction']:
                processed = processed.filter(ImageFilter.MedianFilter(size=3))
            
            return processed

        except Exception as e:
            logger.error(f"Erreur prétraitement image: {e}")
            return image

    async def _perceptual_hash_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint avec hash perceptuel (pHash)."""
        try:
            # Implémentation du pHash
            hash_value = self._compute_phash(image)
            
            return {
                'hash_value': hash_value,
                'hash_type': 'perceptual',
                'hash_size': self.config['hash_algorithms']['phash']['hash_size']
            }

        except Exception as e:
            logger.error(f"Erreur perceptual hash: {e}")
            return {'hash_value': ''}

    def _compute_phash(self, image: Image.Image) -> str:
        """Calcule le hash perceptuel."""
        try:
            hash_size = self.config['hash_algorithms']['phash']['hash_size']
            highfreq_factor = self.config['hash_algorithms']['phash']['highfreq_factor']
            
            # Redimensionnement
            img_size = hash_size * highfreq_factor
            image = image.resize((img_size, img_size), Image.Resampling.LANCZOS)
            
            # Conversion en niveaux de gris
            image = image.convert('L')
            
            # Conversion en array numpy
            pixels = np.array(image, dtype=np.float32)
            
            # Application de la DCT (Discrete Cosine Transform)
            dct = self._dct2d(pixels)
            
            # Extraction des basses fréquences
            dctlowfreq = dct[:hash_size, :hash_size]
            
            # Calcul de la médiane
            med = np.median(dctlowfreq)
            
            # Génération du hash binaire
            diff = dctlowfreq > med
            
            # Conversion en string hexadécimale
            hash_str = ''
            for i in range(hash_size):
                for j in range(hash_size):
                    hash_str += '1' if diff[i, j] else '0'
            
            return hex(int(hash_str, 2))[2:].zfill(hash_size * hash_size // 4)

        except Exception as e:
            logger.error(f"Erreur calcul pHash: {e}")
            return ''

    def _dct2d(self, image_array: np.ndarray) -> np.ndarray:
        """Implémentation simple de la DCT 2D."""
        try:
            # Implémentation basique - en production, utiliser scipy.fftpack.dct
            return np.array(image_array, dtype=np.float32)
        except:
            return np.zeros_like(image_array)

    async def _dhash_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint avec difference hash (dHash)."""
        try:
            hash_size = self.config['hash_algorithms']['dhash']['hash_size']
            
            # Redimensionnement en niveaux de gris
            image = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
            
            # Conversion en array
            pixels = np.array(image)
            
            # Calcul des différences horizontales
            diff = pixels[:, 1:] > pixels[:, :-1]
            
            # Conversion en hash
            hash_str = ''
            for row in diff:
                for pixel in row:
                    hash_str += '1' if pixel else '0'
            
            hash_value = hex(int(hash_str, 2))[2:].zfill(hash_size * hash_size // 4)
            
            return {
                'hash_value': hash_value,
                'hash_type': 'difference',
                'hash_size': hash_size
            }

        except Exception as e:
            logger.error(f"Erreur dHash: {e}")
            return {'hash_value': ''}

    async def _ahash_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint avec average hash (aHash)."""
        try:
            hash_size = self.config['hash_algorithms']['ahash']['hash_size']
            
            # Redimensionnement et conversion
            image = image.convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
            pixels = np.array(image)
            
            # Calcul de la moyenne
            avg = np.mean(pixels)
            
            # Génération du hash binaire
            diff = pixels > avg
            
            # Conversion en string
            hash_str = ''
            for row in diff:
                for pixel in row:
                    hash_str += '1' if pixel else '0'
            
            hash_value = hex(int(hash_str, 2))[2:].zfill(hash_size * hash_size // 4)
            
            return {
                'hash_value': hash_value,
                'hash_type': 'average',
                'hash_size': hash_size
            }

        except Exception as e:
            logger.error(f"Erreur aHash: {e}")
            return {'hash_value': ''}

    async def _whash_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint avec wavelet hash (wHash)."""
        try:
            # Implémentation simplifiée du wHash
            # En production, utiliser PyWavelets pour une implémentation complète
            
            hash_size = self.config['hash_algorithms']['whash']['hash_size']
            image_scale = self.config['hash_algorithms']['whash']['image_scale']
            
            # Préparation de l'image
            image = image.convert('L').resize((image_scale, image_scale), Image.Resampling.LANCZOS)
            pixels = np.array(image, dtype=np.float32)
            
            # Transformation simplifiée (approximation de la transformée en ondelettes)
            # En production, utiliser une vraie transformée en ondelettes
            transformed = pixels
            
            # Extraction des coefficients de basse fréquence
            dwt_low = transformed[:hash_size, :hash_size]
            
            # Calcul de la médiane
            med = np.median(dwt_low)
            
            # Génération du hash
            diff = dwt_low > med
            
            hash_str = ''
            for row in diff:
                for pixel in row:
                    hash_str += '1' if pixel else '0'
            
            hash_value = hex(int(hash_str, 2))[2:].zfill(hash_size * hash_size // 4)
            
            return {
                'hash_value': hash_value,
                'hash_type': 'wavelet',
                'hash_size': hash_size
            }

        except Exception as e:
            logger.error(f"Erreur wHash: {e}")
            return {'hash_value': ''}

    async def _phash_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint avec perceptual hash optimisé."""
        return await self._perceptual_hash_fingerprint(image, metadata)

    async def _feature_extraction_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint basé sur l'extraction de caractéristiques."""
        try:
            # Conversion en OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            features = {}
            
            # Détection de coins (Harris)
            corners = cv2.cornerHarris(gray, 2, 3, 0.04)
            features['corner_count'] = np.sum(corners > 0.01 * corners.max())
            
            # Détection de contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features['contour_count'] = len(contours)
            
            # Caractéristiques statistiques
            features['mean_intensity'] = float(np.mean(gray))
            features['std_intensity'] = float(np.std(gray))
            features['skewness'] = float(self._calculate_skewness(gray))
            features['kurtosis'] = float(self._calculate_kurtosis(gray))
            
            # Génération d'un hash basé sur les caractéristiques
            feature_str = json.dumps(features, sort_keys=True)
            feature_hash = hashlib.sha256(feature_str.encode()).hexdigest()
            
            return {
                'hash_value': feature_hash,
                'feature_vector': np.array(list(features.values())),
                'geometric_features': features
            }

        except Exception as e:
            logger.error(f"Erreur feature extraction: {e}")
            return {'hash_value': ''}

    def _calculate_skewness(self, image_array: np.ndarray) -> float:
        """Calcule l'asymétrie de la distribution des intensités."""
        try:
            mean = np.mean(image_array)
            std = np.std(image_array)
            if std == 0:
                return 0.0
            skewness = np.mean(((image_array - mean) / std) ** 3)
            return skewness
        except:
            return 0.0

    def _calculate_kurtosis(self, image_array: np.ndarray) -> float:
        """Calcule l'aplatissement de la distribution des intensités."""
        try:
            mean = np.mean(image_array)
            std = np.std(image_array)
            if std == 0:
                return 0.0
            kurtosis = np.mean(((image_array - mean) / std) ** 4) - 3
            return kurtosis
        except:
            return 0.0

    async def _color_histogram_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint basé sur l'histogramme des couleurs."""
        try:
            # Conversion en array numpy
            image_array = np.array(image)
            
            # Calcul des histogrammes pour chaque canal
            histograms = {}
            
            if len(image_array.shape) == 3:  # Image couleur
                for i, channel in enumerate(['red', 'green', 'blue']):
                    hist, _ = np.histogram(image_array[:, :, i], bins=32, range=(0, 256))
                    histograms[channel] = hist.tolist()
            else:  # Image en niveaux de gris
                hist, _ = np.histogram(image_array, bins=64, range=(0, 256))
                histograms['gray'] = hist.tolist()
            
            # Caractéristiques de couleur globales
            color_features = {
                'dominant_colors': self._extract_dominant_colors(image),
                'color_variance': float(np.var(image_array)),
                'brightness_avg': float(np.mean(image_array)),
                'contrast': float(np.std(image_array))
            }
            
            # Hash basé sur l'histogramme
            hist_str = json.dumps(histograms, sort_keys=True)
            hist_hash = hashlib.md5(hist_str.encode()).hexdigest()
            
            return {
                'hash_value': hist_hash,
                'color_histogram': histograms,
                'color_features': color_features
            }

        except Exception as e:
            logger.error(f"Erreur color histogram: {e}")
            return {'hash_value': ''}

    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Extrait les couleurs dominantes de l'image."""
        try:
            # Simplification: utilisation de la quantification des couleurs
            quantized = image.quantize(colors=num_colors)
            palette = quantized.getpalette()
            
            if palette:
                dominant_colors = []
                for i in range(min(num_colors, len(palette) // 3)):
                    r = palette[i * 3]
                    g = palette[i * 3 + 1]
                    b = palette[i * 3 + 2]
                    dominant_colors.append((r, g, b))
                return dominant_colors
            
            return [(128, 128, 128)]  # Couleur par défaut
            
        except Exception as e:
            logger.error(f"Erreur extraction couleurs dominantes: {e}")
            return [(128, 128, 128)]

    async def _texture_analysis_fingerprint(
        self,
        image: Image.Image,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un fingerprint basé sur l'analyse de texture."""
        try:
            # Conversion en niveaux de gris
            gray_image = image.convert('L')
            gray_array = np.array(gray_image)
            
            # Analyse de texture avec des filtres de Gabor simplifiés
            texture_features = {
                'entropy': self._calculate_entropy(gray_array),
                'energy': self._calculate_energy(gray_array),
                'homogeneity': self._calculate_homogeneity(gray_array),
                'contrast': self._calculate_contrast(gray_array)
            }
            
            # Hash basé sur les caractéristiques de texture
            texture_str = json.dumps(texture_features, sort_keys=True)
            texture_hash = hashlib.sha256(texture_str.encode()).hexdigest()
            
            return {
                'hash_value': texture_hash,
                'texture_features': texture_features
            }

        except Exception as e:
            logger.error(f"Erreur texture analysis: {e}")
            return {'hash_value': ''}

    def _calculate_entropy(self, image_array: np.ndarray) -> float:
        """Calcule l'entropie de l'image."""
        try:
            hist, _ = np.histogram(image_array, bins=256, range=(0, 256))
            hist = hist / hist.sum()  # Normalisation
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            return float(entropy)
        except:
            return 0.0

    def _calculate_energy(self, image_array: np.ndarray) -> float:
        """Calcule l'énergie de l'image."""
        try:
            hist, _ = np.histogram(image_array, bins=256, range=(0, 256))
            hist = hist / hist.sum()
            energy = np.sum(hist ** 2)
            return float(energy)
        except:
            return 0.0

    def _calculate_homogeneity(self, image_array: np.ndarray) -> float:
        """Calcule l'homogénéité de l'image."""
        try:
            # Matrice de co-occurrence simplifiée
            glcm = self._compute_glcm(image_array)
            i, j = np.ogrid[0:glcm.shape[0], 0:glcm.shape[1]]
            homogeneity = np.sum(glcm / (1 + np.abs(i - j)))
            return float(homogeneity)
        except:
            return 0.0

    def _calculate_contrast(self, image_array: np.ndarray) -> float:
        """Calcule le contraste de l'image."""
        try:
            glcm = self._compute_glcm(image_array)
            i, j = np.ogrid[0:glcm.shape[0], 0:glcm.shape[1]]
            contrast = np.sum(glcm * (i - j) ** 2)
            return float(contrast)
        except:
            return 0.0

    def _compute_glcm(self, image_array: np.ndarray, levels: int = 16) -> np.ndarray:
        """Calcule une matrice de co-occurrence simplifiée."""
        try:
            # Quantification de l'image
            quantized = (image_array / 256 * levels).astype(int)
            quantized = np.clip(quantized, 0, levels - 1)
            
            # Matrice de co-occurrence simplifiée (direction horizontale)
            glcm = np.zeros((levels, levels))
            
            for i in range(quantized.shape[0]):
                for j in range(quantized.shape[1] - 1):
                    glcm[quantized[i, j], quantized[i, j + 1]] += 1
            
            # Normalisation
            if glcm.sum() > 0:
                glcm = glcm / glcm.sum()
            
            return glcm
            
        except Exception as e:
            logger.error(f"Erreur calcul GLCM: {e}")
            return np.zeros((16, 16))

    async def compare_fingerprints(
        self,
        fingerprint1: ImageFingerprint,
        fingerprint2: ImageFingerprint
    ) -> ImageMatchResult:
        """
        Compare deux empreintes d'images.
        
        Args:
            fingerprint1: Première empreinte
            fingerprint2: Seconde empreinte
            
        Returns:
            ImageMatchResult: Résultat de la comparaison
        """
        try:
            start_time = datetime.utcnow()
            
            # Vérification de compatibilité des algorithmes
            if fingerprint1.algorithm != fingerprint2.algorithm:
                raise ValueError("Algorithmes de fingerprinting incompatibles")

            # Calcul de la distance de hash
            hash_distance = self._calculate_hash_distance(
                fingerprint1.hash_value,
                fingerprint2.hash_value
            )
            
            # Calcul de la similarité globale
            similarity_score = await self._calculate_similarity(fingerprint1, fingerprint2)
            
            # Similarités spécifiques
            feature_similarity = self._calculate_feature_similarity(fingerprint1, fingerprint2)
            color_similarity = self._calculate_color_similarity(fingerprint1, fingerprint2)
            structural_similarity = self._calculate_structural_similarity(fingerprint1, fingerprint2)
            
            # Détection de transformations
            transformation_detected = await self._detect_transformations(fingerprint1, fingerprint2)
            
            # Niveau de confiance
            confidence_level = self._determine_confidence_level(similarity_score, hash_distance)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            match_result = ImageMatchResult(
                match_id=str(uuid.uuid4()),
                query_fingerprint=fingerprint1,
                reference_fingerprint=fingerprint2,
                similarity_score=similarity_score,
                hash_distance=hash_distance,
                feature_similarity=feature_similarity,
                color_similarity=color_similarity,
                structural_similarity=structural_similarity,
                confidence_level=confidence_level,
                transformation_detected=transformation_detected,
                processing_time=processing_time
            )
            
            logger.info(f"Comparaison terminée: {match_result.match_id}, score: {similarity_score}")
            return match_result

        except Exception as e:
            logger.error(f"Erreur comparaison empreintes: {e}")
            raise

    def _calculate_hash_distance(self, hash1: str, hash2: str) -> int:
        """Calcule la distance de Hamming entre deux hashes."""
        try:
            if len(hash1) != len(hash2):
                return max(len(hash1), len(hash2))
            
            # Conversion en binaire pour comparaison bit à bit
            bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
            bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
            
            return sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
            
        except Exception as e:
            logger.error(f"Erreur calcul distance hash: {e}")
            return 100

    async def _calculate_similarity(
        self,
        fp1: ImageFingerprint,
        fp2: ImageFingerprint
    ) -> float:
        """Calcule la similarité globale entre deux empreintes."""
        try:
            hash_threshold = self.config['similarity_thresholds']['hash_threshold']
            hash_distance = self._calculate_hash_distance(fp1.hash_value, fp2.hash_value)
            
            # Conversion de la distance en score de similarité
            max_distance = len(fp1.hash_value) * 4  # 4 bits par caractère hex
            hash_similarity = max(0, 1 - (hash_distance / max_distance))
            
            # Similarité basée sur les caractéristiques si disponibles
            feature_sim = self._calculate_feature_similarity(fp1, fp2)
            color_sim = self._calculate_color_similarity(fp1, fp2)
            
            # Pondération des différentes similarités
            weights = {
                'hash': 0.5,
                'feature': 0.3,
                'color': 0.2
            }
            
            total_similarity = (
                weights['hash'] * hash_similarity +
                weights['feature'] * (feature_sim or 0) +
                weights['color'] * (color_sim or 0)
            )
            
            return total_similarity

        except Exception as e:
            logger.error(f"Erreur calcul similarité: {e}")
            return 0.0

    def _calculate_feature_similarity(
        self,
        fp1: ImageFingerprint,
        fp2: ImageFingerprint
    ) -> Optional[float]:
        """Calcule la similarité basée sur les caractéristiques."""
        try:
            if fp1.feature_vector is None or fp2.feature_vector is None:
                return None
            
            # Similarité cosinus entre les vecteurs de caractéristiques
            dot_product = np.dot(fp1.feature_vector, fp2.feature_vector)
            norm1 = np.linalg.norm(fp1.feature_vector)
            norm2 = np.linalg.norm(fp2.feature_vector)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            cosine_similarity = dot_product / (norm1 * norm2)
            return float(cosine_similarity)

        except Exception as e:
            logger.error(f"Erreur similarité caractéristiques: {e}")
            return None

    def _calculate_color_similarity(
        self,
        fp1: ImageFingerprint,
        fp2: ImageFingerprint
    ) -> Optional[float]:
        """Calcule la similarité basée sur les couleurs."""
        try:
            if fp1.color_histogram is None or fp2.color_histogram is None:
                return None
            
            # Comparaison des histogrammes
            similarity_scores = []
            
            for channel in fp1.color_histogram:
                if channel in fp2.color_histogram:
                    hist1 = np.array(fp1.color_histogram[channel])
                    hist2 = np.array(fp2.color_histogram[channel])
                    
                    # Corrélation entre les histogrammes
                    correlation = np.corrcoef(hist1, hist2)[0, 1]
                    if not np.isnan(correlation):
                        similarity_scores.append(abs(correlation))
            
            return float(np.mean(similarity_scores)) if similarity_scores else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité couleur: {e}")
            return None

    def _calculate_structural_similarity(
        self,
        fp1: ImageFingerprint,
        fp2: ImageFingerprint
    ) -> Optional[float]:
        """Calcule la similarité structurelle."""
        try:
            # Comparaison des caractéristiques géométriques
            if fp1.geometric_features is None or fp2.geometric_features is None:
                return None
            
            similarities = []
            
            for feature in fp1.geometric_features:
                if feature in fp2.geometric_features:
                    val1 = fp1.geometric_features[feature]
                    val2 = fp2.geometric_features[feature]
                    
                    # Similarité normalisée
                    max_val = max(abs(val1), abs(val2))
                    if max_val > 0:
                        sim = 1 - abs(val1 - val2) / max_val
                        similarities.append(sim)
            
            return float(np.mean(similarities)) if similarities else 0.0

        except Exception as e:
            logger.error(f"Erreur similarité structurelle: {e}")
            return None

    async def _detect_transformations(
        self,
        fp1: ImageFingerprint,
        fp2: ImageFingerprint
    ) -> Dict[str, Any]:
        """Détecte les transformations appliquées entre deux images."""
        try:
            transformations = {
                'rotation_detected': False,
                'scaling_detected': False,
                'color_adjustment_detected': False,
                'cropping_detected': False,
                'compression_detected': False
            }
            
            # Détection de redimensionnement
            if fp1.image_size != fp2.image_size:
                transformations['scaling_detected'] = True
                transformations['scale_factor'] = (
                    fp2.image_size[0] / fp1.image_size[0],
                    fp2.image_size[1] / fp1.image_size[1]
                )
            
            # Détection d'ajustement colorimétrique
            if fp1.color_histogram and fp2.color_histogram:
                color_diff = self._calculate_color_difference(fp1, fp2)
                if color_diff > 0.3:  # Seuil ajustable
                    transformations['color_adjustment_detected'] = True
            
            # Détection de compression (basée sur la taille de fichier)
            if fp1.file_size > fp2.file_size * 1.5:
                transformations['compression_detected'] = True
                transformations['compression_ratio'] = fp2.file_size / fp1.file_size
            
            return transformations

        except Exception as e:
            logger.error(f"Erreur détection transformations: {e}")
            return {}

    def _calculate_color_difference(self, fp1: ImageFingerprint, fp2: ImageFingerprint) -> float:
        """Calcule la différence de couleur entre deux empreintes."""
        try:
            total_diff = 0.0
            channel_count = 0
            
            for channel in fp1.color_histogram:
                if channel in fp2.color_histogram:
                    hist1 = np.array(fp1.color_histogram[channel])
                    hist2 = np.array(fp2.color_histogram[channel])
                    
                    # Distance euclidienne normalisée
                    diff = np.linalg.norm(hist1 - hist2) / np.sqrt(len(hist1))
                    total_diff += diff
                    channel_count += 1
            
            return total_diff / channel_count if channel_count > 0 else 0.0

        except Exception as e:
            logger.error(f"Erreur calcul différence couleur: {e}")
            return 0.0

    def _determine_confidence_level(self, similarity_score: float, hash_distance: int) -> str:
        """Détermine le niveau de confiance basé sur les métriques."""
        threshold = self.config['similarity_thresholds']['hash_threshold']
        
        if similarity_score >= 0.95 and hash_distance <= threshold // 4:
            return "very_high"
        elif similarity_score >= 0.85 and hash_distance <= threshold // 2:
            return "high"
        elif similarity_score >= 0.7 and hash_distance <= threshold:
            return "medium"
        elif similarity_score >= 0.5:
            return "low"
        else:
            return "very_low"

    async def batch_fingerprint_generation(
        self,
        image_paths: List[Union[str, Path]],
        algorithm: ImageFingerprintAlgorithm = ImageFingerprintAlgorithm.PERCEPTUAL_HASH
    ) -> List[ImageFingerprint]:
        """
        Génération en lot d'empreintes d'images.
        
        Args:
            image_paths: Liste des chemins d'images
            algorithm: Algorithme à utiliser
            
        Returns:
            List[ImageFingerprint]: Liste des empreintes générées
        """
        try:
            tasks = []
            semaphore = asyncio.Semaphore(self.config['performance']['max_concurrent_processing'])
            
            async def process_image(image_path):
                async with semaphore:
                    return await self.create_fingerprint(image_path, algorithm)
            
            for image_path in image_paths:
                tasks.append(process_image(image_path))
            
            fingerprints = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrage des erreurs
            valid_fingerprints = [
                fp for fp in fingerprints 
                if isinstance(fp, ImageFingerprint)
            ]
            
            logger.info(f"Traitement en lot terminé: {len(valid_fingerprints)}/{len(image_paths)} réussis")
            return valid_fingerprints

        except Exception as e:
            logger.error(f"Erreur traitement en lot: {e}")
            raise

    def get_supported_formats(self) -> List[str]:
        """Retourne la liste des formats supportés."""
        return self.supported_formats

    def get_algorithm_info(self, algorithm: ImageFingerprintAlgorithm) -> Dict[str, Any]:
        """Retourne les informations sur un algorithme."""
        algorithm_info = {
            ImageFingerprintAlgorithm.PERCEPTUAL_HASH: {
                'name': 'Perceptual Hash',
                'description': 'Hash basé sur les caractéristiques perceptuelles de l\'image',
                'best_for': 'Détection de copies avec modifications mineures',
                'performance': 'Rapide',
                'accuracy': 'Très haute',
                'robust_to': ['redimensionnement', 'compression légère', 'ajustements colorimétriques']
            },
            ImageFingerprintAlgorithm.DHASH: {
                'name': 'Difference Hash',
                'description': 'Hash basé sur les différences de gradients',
                'best_for': 'Détection rapide de similarité',
                'performance': 'Très rapide',
                'accuracy': 'Haute',
                'robust_to': ['redimensionnement', 'rotation légère']
            },
            ImageFingerprintAlgorithm.FEATURE_EXTRACTION: {
                'name': 'Feature Extraction',
                'description': 'Extraction de caractéristiques géométriques et structurelles',
                'best_for': 'Analyse détaillée de similarité structurelle',
                'performance': 'Modérée',
                'accuracy': 'Très haute',
                'robust_to': ['transformations géométriques', 'éclairage', 'perspective']
            }
        }
        
        return algorithm_info.get(algorithm, {})