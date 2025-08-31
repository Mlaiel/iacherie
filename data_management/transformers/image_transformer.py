"""
 Image Transformation Engine - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/data_management/transformers/image_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.
"""

import asyncio
import logging
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import cv2
from skimage import filters, exposure, restoration, morphology
from skimage.metrics import structural_similarity as ssim
import torch
import torchvision.transforms as transforms
from ultralytics import YOLO
import face_recognition
from scipy import ndimage
import matplotlib.pyplot as plt

from ..models.image_models import ImageMetadata, ImageQualityMetrics
from ...core.exceptions import ImageProcessingError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager
from ...utils.validation import validate_image_file

settings = get_settings()
logger = logging.getLogger(__name__)

class ImageFormat(Enum):
    """Formats d'image supportés"""
    JPEG = "jpg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    HEIC = "heic"
    RAW = "raw"

class ImageQuality(Enum):
    """Niveaux de qualité d'image"""
    ULTRA = "ultra"      # Qualité maximale, pas de compression
    HIGH = "high"        # Haute qualité, compression minimale
    STANDARD = "standard" # Qualité équilibrée
    LOW = "low"          # Compression élevée pour web

class ColorSpace(Enum):
    """Espaces colorimétriques supportés"""
    RGB = "RGB"
    RGBA = "RGBA"
    CMYK = "CMYK"
    LAB = "LAB"
    HSV = "HSV"
    GRAYSCALE = "L"

class ContentType(Enum):
    """Types de contenu image pour optimisation"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    PRODUCT = "product"
    ARTWORK = "artwork"
    DOCUMENT = "document"
    SOCIAL_MEDIA = "social_media"
    PHOTOGRAPHY = "photography"

@dataclass
class ImageProcessingResult:
    """Résultat du traitement d'image"""
    success: bool
    input_file: str
    output_file: Optional[str]
    original_metadata: ImageMetadata
    processed_metadata: ImageMetadata
    quality_metrics: ImageQualityMetrics
    processing_time: float
    operations_performed: List[str]
    warnings: List[str]
    errors: List[str]

class ImageAnalyzer:
    """Analyseur d'image intelligent pour créateurs visuels"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chargement du modèle YOLO pour détection d'objets
        try:
            self.yolo_model = YOLO('yolov8n.pt')
        except Exception as e:
            self.logger.warning(f"YOLO non disponible: {e}")
            self.yolo_model = None
        
        # Transformations pour analyse IA
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def analyze_image_file(self, image_path: str) -> ImageMetadata:
        """Analyse complète d'un fichier image"""



        try:
            # Ouverture avec PIL
            with Image.open(image_path) as img:
                # Métadonnées basiques
                width, height = img.size
                format_name = img.format or Path(image_path).suffix.lstrip('.')
                mode = img.mode
                
                # Extraction des métadonnées EXIF
                exif_data = self._extract_exif_data(img)
                
                # Conversion en array pour analyse
                img_array = np.array(img.convert('RGB'))
                
                # Analyses avancées
                color_analysis = self._analyze_colors(img_array)
                composition_analysis = self._analyze_composition(img_array)
                quality_assessment = self._assess_image_quality(img_array)
                
                # Détection de contenu
                face_detection = self._detect_faces(img_array)
                object_detection = self._detect_objects(img_array)
                
                # Classification du type de contenu
                content_classification = self._classify_content_type(
                    img_array, face_detection, object_detection, width, height
                )
                
                # Calcul de la taille de fichier
                file_size = Path(image_path).stat().st_size
                
                return ImageMetadata(
                    filename=Path(image_path).name,
                    format=format_name.lower(),
                    width=width,
                    height=height,
                    color_mode=mode,
                    file_size=file_size,
                    dpi=exif_data.get('dpi', (72, 72)),
                    
                    # Métadonnées EXIF
                    camera_make=exif_data.get('camera_make'),
                    camera_model=exif_data.get('camera_model'),
                    datetime_taken=exif_data.get('datetime'),
                    focal_length=exif_data.get('focal_length'),
                    aperture=exif_data.get('aperture'),
                    iso=exif_data.get('iso'),
                    exposure_time=exif_data.get('exposure_time'),
                    
                    # Analyse colorimétrique
                    dominant_colors=color_analysis['dominant_colors'],
                    color_palette=color_analysis['palette'],
                    brightness=color_analysis['brightness'],
                    contrast=color_analysis['contrast'],
                    saturation=color_analysis['saturation'],
                    
                    # Composition
                    rule_of_thirds_score=composition_analysis['rule_of_thirds'],
                    symmetry_score=composition_analysis['symmetry'],
                    balance_score=composition_analysis['balance'],
                    
                    # Qualité
                    sharpness_score=quality_assessment['sharpness'],
                    noise_level=quality_assessment['noise'],
                    exposure_quality=quality_assessment['exposure'],
                    
                    # Détection de contenu
                    faces_detected=len(face_detection),
                    objects_detected=len(object_detection),
                    content_type=content_classification,
                    
                    # Tags automatiques
                    tags=self._generate_tags(face_detection, object_detection, color_analysis),
                    
                    # Score global
                    overall_quality_score=self._calculate_overall_quality(
                        quality_assessment, composition_analysis
                    )
                )
                
        except Exception as e:
            self.logger.error(f"Erreur analyse image {image_path}: {e}")
            raise ImageProcessingError(f"Échec analyse image: {str(e)}")
    
    def _extract_exif_data(self, img: Image.Image) -> Dict[str, Any]:
        """Extrait les métadonnées EXIF de l'image"""
        exif_data = {}
        
        try:
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    if tag == 'Make':
                        exif_data['camera_make'] = str(value)
                    elif tag == 'Model':
                        exif_data['camera_model'] = str(value)
                    elif tag == 'DateTime':
                        exif_data['datetime'] = str(value)
                    elif tag == 'FocalLength':
                        exif_data['focal_length'] = float(value)
                    elif tag == 'FNumber':
                        exif_data['aperture'] = float(value)
                    elif tag == 'ISOSpeedRatings':
                        exif_data['iso'] = int(value)
                    elif tag == 'ExposureTime':
                        exif_data['exposure_time'] = float(value)
                    elif tag == 'XResolution':
                        exif_data['dpi'] = (float(value), exif_data.get('dpi', (72, 72))[1])
                    elif tag == 'YResolution':
                        exif_data['dpi'] = (exif_data.get('dpi', (72, 72))[0], float(value))
        
        except Exception as e:
            self.logger.warning(f"Erreur extraction EXIF: {e}")
        
        return exif_data
    
    def _analyze_colors(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyse colorimétrique avancée"""
        
        # Conversion en différents espaces colorimétriques
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        
        # Calcul des métriques de base
        brightness = np.mean(cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY))
        
        # Contraste (écart-type des niveaux de gris)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        contrast = np.std(gray)
        
        # Saturation moyenne
        saturation = np.mean(hsv[:, :, 1])
        
        # Couleurs dominantes (k-means clustering)
        dominant_colors = self._extract_dominant_colors(img_array, k=5)
        
        # Palette de couleurs (quantification)
        palette = self._extract_color_palette(img_array, n_colors=8)
        
        return {
            'brightness': float(brightness) / 255.0,
            'contrast': float(contrast) / 255.0,
            'saturation': float(saturation) / 255.0,
            'dominant_colors': dominant_colors,
            'palette': palette
        }
    
    def _extract_dominant_colors(self, img_array: np.ndarray, k: int = 5) -> List[List[int]]:
        """Extrait les couleurs dominantes par k-means"""



        
        try:
            # Reshape pour k-means
            pixels = img_array.reshape(-1, 3)
            
            # Échantillonnage pour performance
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]
            
            # K-means clustering
            pixels_float = pixels.astype(np.float32)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            _, labels, centers = cv2.kmeans(pixels_float, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Conversion en liste de couleurs
            centers = centers.astype(int)
            return [color.tolist() for color in centers]
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction couleurs dominantes: {e}")
            return [[128, 128, 128]] * k  # Gris par défaut
    
    def _extract_color_palette(self, img_array: np.ndarray, n_colors: int = 8) -> List[List[int]]:
        """Extrait une palette de couleurs représentative"""



        
        try:
            # Quantification des couleurs
            img_pil = Image.fromarray(img_array)
            img_quantized = img_pil.quantize(colors=n_colors)
            
            # Extraction de la palette
            palette = img_quantized.getpalette()
            if palette:
                # Regroupement par triplets RGB
                rgb_palette = [palette[i:i+3] for i in range(0, min(len(palette), n_colors*3), 3)]
                return rgb_palette[:n_colors]
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction palette: {e}")
        
        return [[i*32, i*32, i*32] for i in range(n_colors)]  # Palette en niveaux de gris
    
    def _analyze_composition(self, img_array: np.ndarray) -> Dict[str, float]:
        """Analyse de la composition photographique"""
        
        height, width = img_array.shape[:2]
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Score de la règle des tiers
        rule_of_thirds_score = self._calculate_rule_of_thirds(gray)
        
        # Score de symétrie
        symmetry_score = self._calculate_symmetry(gray)
        
        # Score d'équilibre
        balance_score = self._calculate_balance(gray)
        
        return {
            'rule_of_thirds': rule_of_thirds_score,
            'symmetry': symmetry_score,
            'balance': balance_score
        }
    
    def _calculate_rule_of_thirds(self, gray: np.ndarray) -> float:
        """Calcule le score de la règle des tiers"""
        
        height, width = gray.shape
        
        # Lignes de tiers
        third_h = height // 3
        third_w = width // 3
        
        # Zones d'intérêt (intersections des lignes de tiers)
        interest_points = [
            (third_w, third_h),
            (2 * third_w, third_h),
            (third_w, 2 * third_h),
            (2 * third_w, 2 * third_h)
        ]
        
        # Détection des contours pour trouver les points d'intérêt
        edges = cv2.Canny(gray, 50, 150)
        
        # Calcul de l'activité visuelle près des points de tiers
        total_activity = 0
        for x, y in interest_points:
            # Zone autour du point d'intérêt
            x_start = max(0, x - 20)
            x_end = min(width, x + 20)
            y_start = max(0, y - 20)
            y_end = min(height, y + 20)
            
            region = edges[y_start:y_end, x_start:x_end]
            activity = np.sum(region) / 255.0
            total_activity += activity
        
        # Normalisation
        max_possible_activity = len(interest_points) * 40 * 40
        score = min(1.0, total_activity / max_possible_activity)
        
        return score
    
    def _calculate_symmetry(self, gray: np.ndarray) -> float:
        """Calcule le score de symétrie"""
        
        height, width = gray.shape
        
        # Symétrie verticale
        left_half = gray[:, :width//2]
        right_half = np.fliplr(gray[:, width//2:])
        
        # Redimensionnement pour correspondance
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Calcul de la similarité
        vertical_symmetry = ssim(left_half, right_half, data_range=255)
        
        # Symétrie horizontale
        top_half = gray[:height//2, :]
        bottom_half = np.flipud(gray[height//2:, :])
        
        min_height = min(top_half.shape[0], bottom_half.shape[0])
        top_half = top_half[:min_height, :]
        bottom_half = bottom_half[:min_height, :]
        
        horizontal_symmetry = ssim(top_half, bottom_half, data_range=255)
        
        # Score global de symétrie
        symmetry_score = max(vertical_symmetry, horizontal_symmetry)
        
        return max(0.0, symmetry_score)
    
    def _calculate_balance(self, gray: np.ndarray) -> float:
        """Calcule le score d'équilibre visuel"""
        
        height, width = gray.shape
        
        # Calcul du centre de masse visuel
        y_indices, x_indices = np.indices(gray.shape)
        
        # Pondération par l'intensité
        total_weight = np.sum(gray)
        if total_weight == 0:
            return 0.5  # Image vide
        
        center_x = np.sum(x_indices * gray) / total_weight
        center_y = np.sum(y_indices * gray) / total_weight
        
        # Centre géométrique de l'image
        geometric_center_x = width / 2
        geometric_center_y = height / 2
        
        # Distance du centre de masse au centre géométrique
        distance = np.sqrt(
            (center_x - geometric_center_x) ** 2 + 
            (center_y - geometric_center_y) ** 2
        )
        
        # Normalisation (distance maximale possible)
        max_distance = np.sqrt((width/2) ** 2 + (height/2) ** 2)
        balance_score = 1.0 - (distance / max_distance)
        
        return max(0.0, balance_score)
    
    def _assess_image_quality(self, img_array: np.ndarray) -> Dict[str, float]:
        """Évaluation de la qualité technique de l'image"""
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Netteté (variance du Laplacien)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_normalized = min(1.0, sharpness / 1000.0)  # Normalisation empirique
        
        # Niveau de bruit (estimation via filtrage)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        noise = np.mean(np.abs(gray.astype(float) - denoised.astype(float)))
        noise_normalized = min(1.0, noise / 50.0)  # Normalisation empirique
        
        # Qualité d'exposition (distribution des histogrammes)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist / np.sum(hist)
        
        # Détection de sur/sous-exposition
        overexposed = np.sum(hist_normalized[240:])  # Pixels très clairs
        underexposed = np.sum(hist_normalized[:15])  # Pixels très sombres
        
        exposure_quality = 1.0 - max(overexposed, underexposed)
        
        return {
            'sharpness': sharpness_normalized,
            'noise': 1.0 - noise_normalized,  # Inversé pour que plus = mieux
            'exposure': exposure_quality
        }
    
    def _detect_faces(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Détecte les visages dans l'image"""
        
        faces_info = []
        
        try:
            # Détection avec face_recognition
            face_locations = face_recognition.face_locations(img_array)
            
            for i, face_location in enumerate(face_locations):
                top, right, bottom, left = face_location
                
                # Calcul des propriétés du visage
                width = right - left
                height = bottom - top
                area = width * height
                center = ((left + right) // 2, (top + bottom) // 2)
                
                faces_info.append({
                    'id': i,
                    'location': face_location,
                    'width': width,
                    'height': height,
                    'area': area,
                    'center': center,
                    'aspect_ratio': width / height if height > 0 else 1.0
                })
                
        except Exception as e:
            self.logger.warning(f"Erreur détection visages: {e}")
        
        return faces_info
    
    def _detect_objects(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Détecte les objets dans l'image avec YOLO"""
        
        objects_info = []
        
        if not self.yolo_model:
            return objects_info
        
        try:
            # Détection YOLO
            results = self.yolo_model(img_array)
            
            for result in results:
                if result.boxes is not None:
                    for i, box in enumerate(result.boxes):
                        bbox = box.xyxy.tolist()[0]  # [x1, y1, x2, y2]
                        
                        objects_info.append({
                            'id': i,
                            'class': result.names[int(box.cls)],
                            'confidence': float(box.conf),
                            'bbox': bbox,
                            'area': (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]),
                            'center': ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                        })
                        
        except Exception as e:
            self.logger.warning(f"Erreur détection objets: {e}")
        
        return objects_info
    
    def _classify_content_type(
        self,
        img_array: np.ndarray,
        faces: List[Dict],
        objects: List[Dict],
        width: int,
        height: int
    ) -> str:
        """Classifie automatiquement le type de contenu"""
        
        aspect_ratio = width / height
        
        # Logique de classification
        if len(faces) > 0:
            if len(faces) == 1 and len(objects) <= 3:
                return ContentType.PORTRAIT.value
            else:
                return ContentType.SOCIAL_MEDIA.value
        
        elif aspect_ratio > 1.5:
            return ContentType.LANDSCAPE.value
        
        elif any(obj['class'] in ['book', 'laptop', 'keyboard'] for obj in objects):
            return ContentType.DOCUMENT.value
        
        elif any(obj['class'] in ['bottle', 'cup', 'bowl', 'knife'] for obj in objects):
            return ContentType.PRODUCT.value
        
        elif aspect_ratio == 1.0:  # Carré
            return ContentType.SOCIAL_MEDIA.value
        
        else:
            return ContentType.PHOTOGRAPHY.value
    
    def _generate_tags(
        self,
        faces: List[Dict],
        objects: List[Dict],
        color_analysis: Dict
    ) -> List[str]:
        """Génère des tags automatiques"""
        
        tags = []
        
        # Tags basés sur les visages
        if faces:
            tags.append("people")
            if len(faces) == 1:
                tags.append("portrait")
            elif len(faces) > 1:
                tags.append("group")
        
        # Tags basés sur les objets
        object_classes = [obj['class'] for obj in objects]
        for obj_class in set(object_classes):
            tags.append(obj_class)
        
        # Tags basés sur les couleurs dominantes
        dominant_colors = color_analysis.get('dominant_colors', [])
        for color in dominant_colors[:3]:  # Top 3 couleurs
            color_name = self._color_to_name(color)
            if color_name:
                tags.append(color_name)
        
        # Tags basés sur les métriques
        brightness = color_analysis.get('brightness', 0.5)
        if brightness > 0.8:
            tags.append("bright")
        elif brightness < 0.3:
            tags.append("dark")
        
        saturation = color_analysis.get('saturation', 0.5)
        if saturation > 0.7:
            tags.append("vibrant")
        elif saturation < 0.3:
            tags.append("muted")
        
        return tags[:10]  # Limite à 10 tags
    
    def _color_to_name(self, rgb: List[int]) -> Optional[str]:
        """Convertit une couleur RGB en nom approximatif"""
        
        r, g, b = rgb
        
        # Définition de couleurs de base
        color_definitions = {
            'red': [255, 0, 0],
            'green': [0, 255, 0],
            'blue': [0, 0, 255],
            'yellow': [255, 255, 0],
            'orange': [255, 165, 0],
            'purple': [128, 0, 128],
            'pink': [255, 192, 203],
            'brown': [165, 42, 42],
            'black': [0, 0, 0],
            'white': [255, 255, 255],
            'gray': [128, 128, 128]
        }
        
        # Recherche de la couleur la plus proche
        min_distance = float('inf')
        closest_color = None
        
        for color_name, color_rgb in color_definitions.items():
            distance = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb, color_rgb)))
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        # Retourner seulement si la distance est raisonnable
        return closest_color if min_distance < 100 else None
    
    def _calculate_overall_quality(
        self,
        quality_assessment: Dict[str, float],
        composition_analysis: Dict[str, float]
    ) -> float:
        """Calcule un score de qualité global"""
        
        # Pondération des différents aspects
        technical_score = (
            quality_assessment['sharpness'] * 0.4 +
            quality_assessment['noise'] * 0.3 +
            quality_assessment['exposure'] * 0.3
        )
        
        composition_score = (
            composition_analysis['rule_of_thirds'] * 0.4 +
            composition_analysis['symmetry'] * 0.3 +
            composition_analysis['balance'] * 0.3
        )
        
        # Score global (technique 60%, composition 40%)
        overall_score = technical_score * 0.6 + composition_score * 0.4
        
        return round(overall_score, 3)

class ImageEnhancer:
    """Améliorateur d'image IA pour créateurs visuels"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enhance_image(
        self,
        img_array: np.ndarray,
        enhancement_type: str = "balanced",
        intensity: float = 0.5
    ) -> np.ndarray:
        """Améliore la qualité d'image avec IA"""



        
        try:
            if enhancement_type == "sharpen":
                return self._sharpen_image(img_array, intensity)
            elif enhancement_type == "denoise":
                return self._denoise_image(img_array, intensity)
            elif enhancement_type == "color_enhance":
                return self._enhance_colors(img_array, intensity)
            elif enhancement_type == "contrast":
                return self._enhance_contrast(img_array, intensity)
            elif enhancement_type == "upscale":
                return self._upscale_image(img_array, intensity)
            else:  # balanced
                return self._balanced_enhancement(img_array, intensity)
            
        except Exception as e:
            self.logger.error(f"Erreur amélioration image: {e}")
            return img_array
    
    def _sharpen_image(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Améliore la netteté de l'image"""
        
        # Conversion en PIL pour enhancement
        img_pil = Image.fromarray(img_array)
        
        # Application du sharpening
        enhancer = ImageEnhance.Sharpness(img_pil)
        factor = 1.0 + intensity * 2.0  # Facteur de 1.0 à 3.0
        enhanced = enhancer.enhance(factor)
        
        return np.array(enhanced)
    
    def _denoise_image(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Réduit le bruit dans l'image"""
        
        # Débruitage avec filtrage bilatéral
        h = int(intensity * 20 + 5)  # Force du débruitage
        denoised = cv2.bilateralFilter(img_array, 9, h, h)
        
        return denoised
    
    def _enhance_colors(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Améliore les couleurs de l'image"""
        
        img_pil = Image.fromarray(img_array)
        
        # Amélioration de la saturation
        color_enhancer = ImageEnhance.Color(img_pil)
        factor = 1.0 + intensity * 0.5
        enhanced = color_enhancer.enhance(factor)
        
        return np.array(enhanced)
    
    def _enhance_contrast(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Améliore le contraste de l'image"""
        
        # Égalisation d'histogramme adaptative
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clip_limit = 1.0 + intensity * 3.0
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        
        # Application du contraste amélioré aux canaux couleur
        enhanced = img_array.copy()
        for i in range(3):  # RGB
            enhanced[:, :, i] = cv2.equalizeHist(enhanced[:, :, i])
        
        return enhanced
    
    def _upscale_image(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Upscale l'image avec interpolation avancée"""
        
        # Facteur d'upscaling basé sur l'intensité
        scale_factor = 1.0 + intensity
        
        height, width = img_array.shape[:2]
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)
        
        # Upscaling avec interpolation LANCZOS
        upscaled = cv2.resize(
            img_array,
            (new_width, new_height),
            interpolation=cv2.INTER_LANCZOS4
        )
        
        return upscaled
    
    def _balanced_enhancement(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Amélioration équilibrée"""
        
        enhanced = img_array.copy()
        
        # Léger sharpening
        enhanced = self._sharpen_image(enhanced, intensity * 0.3)
        
        # Amélioration couleur subtile
        enhanced = self._enhance_colors(enhanced, intensity * 0.4)
        
        # Contraste adaptatif léger
        enhanced = self._enhance_contrast(enhanced, intensity * 0.2)
        
        return enhanced

class ImageTransformer:
    """Transformateur d'image principal pour créateurs visuels"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager()
        self.analyzer = ImageAnalyzer()
        self.enhancer = ImageEnhancer()
        
        # Presets optimisés par plateforme
        self.platform_presets = {
            'instagram_post': {
                'resolution': [1080, 1080],
                'format': 'jpg',
                'quality': 85
            },
            'instagram_story': {
                'resolution': [1080, 1920],
                'format': 'jpg',
                'quality': 85
            },
            'facebook_post': {
                'resolution': [1200, 630],
                'format': 'jpg',
                'quality': 85
            },
            'twitter_post': {
                'resolution': [1200, 675],
                'format': 'jpg',
                'quality': 85
            },
            'linkedin_post': {
                'resolution': [1200, 627],
                'format': 'jpg',
                'quality': 90
            },
            'youtube_thumbnail': {
                'resolution': [1280, 720],
                'format': 'jpg',
                'quality': 90
            },
            'web_optimized': {
                'resolution': None,  # Keep original
                'format': 'webp',
                'quality': 80
            },
            'print_ready': {
                'resolution': None,
                'format': 'tiff',
                'quality': 100,
                'dpi': 300
            }
        }
    
    def transform(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """Transformation d'image selon configuration"""
        
        start_time = time.time()
        operations = []
        warnings = []
        errors = []
        
        try:
            # Validation du fichier d'entrée
            if not validate_image_file(input_path):
                raise ValidationError(f"Fichier image invalide: {input_path}")
            
            # Analyse du fichier source
            original_metadata = self.analyzer.analyze_image_file(input_path)
            operations.append("Analyse métadonnées")
            
            # Chargement de l'image
            with Image.open(input_path) as img:
                # Conversion en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img_array = np.array(img)
                operations.append("Chargement image")
            
            # Préparation du chemin de sortie
            if not output_path:
                output_path = self._generate_output_path(input_path, config)
            
            # Application des transformations selon le type
            if config.type.value == 'image_resize':
                img_array = self._resize_image(img_array, config.parameters)
                operations.append("Redimensionnement")
                
            elif config.type.value == 'image_convert':
                # La conversion se fait lors de la sauvegarde
                operations.append("Conversion format")
                
            elif config.type.value == 'image_compress':
                # La compression se fait lors de la sauvegarde
                operations.append("Compression")
                
            elif config.type.value == 'image_enhance':
                img_array = self._enhance_image(img_array, config.parameters)
                operations.append("Amélioration IA")
            
            # Sauvegarde de l'image traitée
            self._save_image(img_array, output_path, config)
            operations.append("Sauvegarde")
            
            # Analyse finale
            processed_metadata = self.analyzer.analyze_image_file(output_path)
            
            # Calcul des métriques de qualité
            quality_metrics = self._calculate_quality_metrics(
                original_metadata, processed_metadata
            )
            
            processing_time = time.time() - start_time
            
            from . import TransformationResult, TransformationType
            return TransformationResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                transformation_type=TransformationType(config.type.value),
                metadata={
                    'original': original_metadata.__dict__,
                    'processed': processed_metadata.__dict__,
                    'quality_metrics': quality_metrics.__dict__
                },
                errors=errors,
                warnings=warnings,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Erreur transformation image {input_path}: {e}")
            processing_time = time.time() - start_time
            
            from . import TransformationResult, TransformationType
            return TransformationResult(
                success=False,
                input_path=input_path,
                output_path=None,
                transformation_type=TransformationType(config.type.value),
                metadata={},
                errors=[str(e)],
                warnings=warnings,
                processing_time=processing_time
            )
    
    def _resize_image(self, img_array: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Redimensionne l'image"""
        
        target_resolution = params.get('resolution', [1920, 1080])
        maintain_aspect = params.get('maintain_aspect', True)
        platform = params.get('platform')
        
        # Utilisation du preset de plateforme si spécifié
        if platform and platform in self.platform_presets:
            preset = self.platform_presets[platform]
            target_resolution = preset['resolution']
        
        if not target_resolution:
            return img_array  # Pas de redimensionnement
        
        target_width, target_height = target_resolution
        current_height, current_width = img_array.shape[:2]
        
        if maintain_aspect:
            # Calcul du ratio pour conserver les proportions
            width_ratio = target_width / current_width
            height_ratio = target_height / current_height
            
            # Utilisation du plus petit ratio pour que l'image tienne dans les dimensions cibles
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(current_width * ratio)
            new_height = int(current_height * ratio)
            
            # Redimensionnement
            resized = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Padding si nécessaire pour atteindre les dimensions exactes
            if new_width != target_width or new_height != target_height:
                # Création d'une image de la taille cible avec fond noir
                result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                
                # Centrage de l'image redimensionnée
                start_y = (target_height - new_height) // 2
                start_x = (target_width - new_width) // 2
                
                result[start_y:start_y + new_height, start_x:start_x + new_width] = resized
                
                return result
            else:
                return resized
        else:
            # Redimensionnement forcé sans conservation du ratio
            return cv2.resize(img_array, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
    
    def _enhance_image(self, img_array: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Améliore l'image"""
        
        enhancement_type = params.get('type', 'balanced')
        intensity = params.get('intensity', 0.5)
        
        return self.enhancer.enhance_image(img_array, enhancement_type, intensity)
    
    def _save_image(
        self,
        img_array: np.ndarray,
        output_path: str,
        config: 'TransformationConfig'
    ) -> None:
        """Sauvegarde l'image traitée"""
        
        # Création du répertoire si nécessaire
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Conversion en PIL
        img_pil = Image.fromarray(img_array)
        
        # Détermination du format et des options de sauvegarde
        output_format = config.output_format or Path(output_path).suffix.lstrip('.').lower()
        save_params = {}
        
        # Application des presets de plateforme si spécifié
        platform = config.parameters.get('platform')
        if platform and platform in self.platform_presets:
            preset = self.platform_presets[platform]
            if 'format' in preset:
                output_format = preset['format']
            if 'quality' in preset:
                save_params['quality'] = preset['quality']
            if 'dpi' in preset:
                save_params['dpi'] = (preset['dpi'], preset['dpi'])
        
        # Configuration par format
        if output_format in ['jpg', 'jpeg']:
            save_params['format'] = 'JPEG'
            if 'quality' not in save_params:
                quality_mapping = {
                    'ultra': 100,
                    'high': 95,
                    'standard': 85,
                    'low': 70
                }
                save_params['quality'] = quality_mapping.get(config.quality, 85)
            save_params['optimize'] = True
            
        elif output_format == 'png':
            save_params['format'] = 'PNG'
            save_params['optimize'] = True
            
        elif output_format == 'webp':
            save_params['format'] = 'WEBP'
            if 'quality' not in save_params:
                save_params['quality'] = 80
            save_params['method'] = 6  # Meilleure compression
            
        elif output_format == 'tiff':
            save_params['format'] = 'TIFF'
            save_params['compression'] = 'lzw'
            
        else:
            save_params['format'] = output_format.upper()
        
        # Sauvegarde
        img_pil.save(output_path, **save_params)
    
    def _generate_output_path(self, input_path: str, config: 'TransformationConfig') -> str:
        """Génère le chemin de sortie automatiquement"""
        
        input_path_obj = Path(input_path)
        
        # Détermination de l'extension selon la transformation
        output_format = config.output_format
        
        # Utilisation du preset de plateforme si spécifié
        platform = config.parameters.get('platform')
        if platform and platform in self.platform_presets:
            preset = self.platform_presets[platform]
            if 'format' in preset:
                output_format = preset['format']
        
        if not output_format:
            output_format = input_path_obj.suffix.lstrip('.')
        
        # Nom de fichier avec suffixe de transformation
        transform_suffix = config.type.value.replace('image_', '')
        new_name = f"{input_path_obj.stem}_{transform_suffix}.{output_format}"
        
        return str(input_path_obj.parent / new_name)
    
    def _calculate_quality_metrics(
        self,
        original: ImageMetadata,
        processed: ImageMetadata
    ) -> ImageQualityMetrics:
        """Calcule les métriques de qualité de la transformation"""
        
        # Calcul des changements de résolution
        resolution_change = (processed.width * processed.height) / (original.width * original.height)
        
        # Calcul de la compression
        compression_ratio = original.file_size / processed.file_size if processed.file_size > 0 else 1.0
        
        # Estimation de la préservation de qualité
        quality_preservation = min(1.0, processed.overall_quality_score / original.overall_quality_score)
        
        return ImageQualityMetrics(
            psnr_db=None,  # Nécessiterait comparaison pixel par pixel
            ssim_score=None,  # Calcul complexe
            compression_ratio=compression_ratio,
            color_accuracy=quality_preservation,  # Estimation
            sharpness_retention=processed.sharpness_score / original.sharpness_score,
            noise_reduction_score=processed.noise_level / original.noise_level,
            overall_quality_score=quality_preservation,
            file_size_efficiency=compression_ratio
        )

class AsyncImageTransformer:
    """Version asynchrone du transformateur d'image"""
    
    def __init__(self):
        self.sync_transformer = ImageTransformer()
        self.logger = logging.getLogger(__name__)
    
    async def transform_async(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """Transformation d'image asynchrone"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.sync_transformer.transform,
            input_path,
            config,
            output_path
        )
    
    async def transform_batch_async(
        self,
        inputs: List[Tuple[str, 'TransformationConfig']],
        max_concurrent: int = 6  # Plus de concurrence pour images
    ) -> List['TransformationResult']:
        """Transformation en lot asynchrone"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def transform_single(input_config_tuple):
            async with semaphore:
                input_path, config = input_config_tuple
                return await self.transform_async(input_path, config)
        
        tasks = [transform_single(item) for item in inputs]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Export des classes
__all__ = [
    'ImageTransformer',
    'AsyncImageTransformer',
    'ImageAnalyzer',
    'ImageEnhancer',
    'ImageFormat',
    'ImageQuality',
    'ColorSpace',
    'ContentType',
    'ImageProcessingResult'
]
