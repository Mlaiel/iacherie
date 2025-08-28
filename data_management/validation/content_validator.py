"""
🚀 Content Validation System - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/data_management/validation/content_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE VALIDATION DE CONTENU MULTIMÉDIA
Validation avancée pour musiciens, influenceurs, photographes, blogueurs, comédiens
- Analyse de qualité audio/vidéo/image/texte
- Détection de contenu inapproprié
- Validation métadonnées et structure
- Support multi-format avec AI
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import os
import magic
import hashlib
import json

# Audio processing
import librosa
import soundfile as sf
from pydub import AudioSegment
import numpy as np

# Video processing
import cv2
from moviepy.editor import VideoFileClip

# Image processing
from PIL import Image, ImageStat, ExifTags
import imagehash

# Text processing
import chardet
from textstat import flesch_reading_ease, lexicon_count
import language_tool_python

# ML/AI content analysis
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Content analysis
from nudenet import NudeDetector
import cv2

logger = logging.getLogger(__name__)

@dataclass
class ContentValidationResult:
    """Résultat de validation de contenu"""
    is_valid: bool
    quality_score: float  # 0.0 - 1.0
    content_type: str
    format_detected: str
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    analysis_data: Dict[str, Any]

class AudioContentValidator:
    """Validateur spécialisé pour contenu audio"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AudioContentValidator")
        self.min_duration = 1.0  # secondes
        self.max_duration = 3600.0  # 1 heure
        
    def validate_audio_content(self, file_path: str) -> ContentValidationResult:
        """Valide le contenu audio avec analyse avancée"""
        errors = []
        warnings = []
        metadata = {}
        analysis_data = {}
        
        try:
            # Lecture du fichier audio
            y, sr = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            metadata.update({
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[0],
                "samples": len(y)
            })
            
            # Validation durée
            if duration < self.min_duration:
                errors.append(f"Audio trop court: {duration:.2f}s (minimum: {self.min_duration}s)")
            elif duration > self.max_duration:
                errors.append(f"Audio trop long: {duration:.2f}s (maximum: {self.max_duration}s)")
            
            # Analyse qualité audio
            quality_score = self._analyze_audio_quality(y, sr, analysis_data)
            
            # Détection de silence
            self._detect_silence_issues(y, sr, warnings, analysis_data)
            
            # Analyse spectrale
            self._analyze_spectrum(y, sr, analysis_data, warnings)
            
            # Détection clipping
            self._detect_clipping(y, warnings, analysis_data)
            
            # Analyse dynamique
            self._analyze_dynamics(y, analysis_data, warnings)
            
            return ContentValidationResult(
                is_valid=len(errors) == 0,
                quality_score=quality_score,
                content_type="audio",
                format_detected=Path(file_path).suffix.lower(),
                errors=errors,
                warnings=warnings,
                metadata=metadata,
                analysis_data=analysis_data
            )
            
        except Exception as e:
            self.logger.error(f"Erreur validation audio {file_path}: {e}")
            return ContentValidationResult(
                is_valid=False,
                quality_score=0.0,
                content_type="audio",
                format_detected="unknown",
                errors=[f"Erreur lecture audio: {str(e)}"],
                warnings=[],
                metadata={},
                analysis_data={}
            )
    
    def _analyze_audio_quality(self, y: np.ndarray, sr: int, analysis_data: Dict) -> float:
        """Analyse la qualité audio globale"""
        scores = []
        
        # 1. Analyse du niveau RMS
        rms = librosa.feature.rms(y=y)[0]
        avg_rms = np.mean(rms)
        analysis_data["rms_level"] = float(avg_rms)
        
        if 0.01 <= avg_rms <= 0.7:
            scores.append(1.0)
        elif avg_rms < 0.001:
            scores.append(0.2)  # Trop faible
        else:
            scores.append(0.5)  # Trop fort
        
        # 2. Analyse de la bande passante
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        avg_centroid = np.mean(spectral_centroids)
        analysis_data["spectral_centroid"] = float(avg_centroid)
        
        if 1000 <= avg_centroid <= 4000:
            scores.append(1.0)
        else:
            scores.append(0.7)
        
        # 3. Analyse de la richesse spectrale
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        avg_rolloff = np.mean(spectral_rolloff)
        analysis_data["spectral_rolloff"] = float(avg_rolloff)
        
        if avg_rolloff > sr * 0.3:
            scores.append(1.0)
        else:
            scores.append(0.6)
        
        return np.mean(scores)
    
    def _detect_silence_issues(self, y: np.ndarray, sr: int, warnings: List[str], analysis_data: Dict):
        """Détecte les problèmes de silence"""
        # Détection des segments silencieux
        threshold = 0.01
        silent_samples = np.abs(y) < threshold
        silent_percentage = np.sum(silent_samples) / len(y) * 100
        
        analysis_data["silence_percentage"] = float(silent_percentage)
        
        if silent_percentage > 30:
            warnings.append(f"Contenu silencieux élevé: {silent_percentage:.1f}%")
        
        # Détection silence en début/fin
        start_silence = 0
        end_silence = 0
        
        for i, sample in enumerate(y):
            if abs(sample) > threshold:
                start_silence = i / sr
                break
        
        for i, sample in enumerate(reversed(y)):
            if abs(sample) > threshold:
                end_silence = i / sr
                break
        
        analysis_data["start_silence"] = start_silence
        analysis_data["end_silence"] = end_silence
        
        if start_silence > 2.0:
            warnings.append(f"Silence long en début: {start_silence:.1f}s")
        if end_silence > 2.0:
            warnings.append(f"Silence long en fin: {end_silence:.1f}s")
    
    def _analyze_spectrum(self, y: np.ndarray, sr: int, analysis_data: Dict, warnings: List[str]):
        """Analyse spectrale avancée"""
        # FFT analysis
        fft = np.fft.fft(y)
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        magnitude = np.abs(fft)
        
        # Analyse des fréquences dominantes
        dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
        dominant_freq = abs(freqs[dominant_freq_idx])
        analysis_data["dominant_frequency"] = float(dominant_freq)
        
        # Détection de problèmes spectraux
        if dominant_freq < 50:
            warnings.append("Fréquences très basses dominantes")
        elif dominant_freq > 8000:
            warnings.append("Fréquences très hautes dominantes")
    
    def _detect_clipping(self, y: np.ndarray, warnings: List[str], analysis_data: Dict):
        """Détecte l'écrêtage audio"""
        clipped_samples = np.sum(np.abs(y) >= 0.99)
        clipping_percentage = clipped_samples / len(y) * 100
        
        analysis_data["clipping_percentage"] = float(clipping_percentage)
        
        if clipping_percentage > 0.1:
            warnings.append(f"Écrêtage détecté: {clipping_percentage:.2f}%")
    
    def _analyze_dynamics(self, y: np.ndarray, analysis_data: Dict, warnings: List[str]):
        """Analyse la dynamique audio"""
        # Calcul de la plage dynamique
        rms = librosa.feature.rms(y=y)[0]
        dynamic_range = np.max(rms) / np.mean(rms) if np.mean(rms) > 0 else 0
        
        analysis_data["dynamic_range"] = float(dynamic_range)
        
        if dynamic_range < 2.0:
            warnings.append("Plage dynamique faible (audio compressé)")

class VideoContentValidator:
    """Validateur spécialisé pour contenu vidéo"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VideoContentValidator")
        self.min_duration = 1.0
        self.max_duration = 7200.0  # 2 heures
        self.min_resolution = (240, 240)
        self.max_resolution = (7680, 4320)  # 8K
        
    def validate_video_content(self, file_path: str) -> ContentValidationResult:
        """Valide le contenu vidéo avec analyse avancée"""
        errors = []
        warnings = []
        metadata = {}
        analysis_data = {}
        
        try:
            # Analyse avec OpenCV
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                errors.append("Impossible d'ouvrir le fichier vidéo")
                return self._create_error_result(errors)
            
            # Métadonnées de base
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            metadata.update({
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "resolution": f"{width}x{height}"
            })
            
            # Validations de base
            if duration < self.min_duration:
                errors.append(f"Vidéo trop courte: {duration:.2f}s")
            elif duration > self.max_duration:
                errors.append(f"Vidéo trop longue: {duration:.2f}s")
            
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                errors.append(f"Résolution trop faible: {width}x{height}")
            elif width > self.max_resolution[0] or height > self.max_resolution[1]:
                warnings.append(f"Résolution très élevée: {width}x{height}")
            
            if fps < 15:
                warnings.append(f"FPS faible: {fps}")
            elif fps > 120:
                warnings.append(f"FPS très élevé: {fps}")
            
            # Analyse qualité vidéo
            quality_score = self._analyze_video_quality(cap, analysis_data, warnings)
            
            # Analyse du contenu
            self._analyze_video_content(cap, analysis_data, warnings)
            
            cap.release()
            
            return ContentValidationResult(
                is_valid=len(errors) == 0,
                quality_score=quality_score,
                content_type="video",
                format_detected=Path(file_path).suffix.lower(),
                errors=errors,
                warnings=warnings,
                metadata=metadata,
                analysis_data=analysis_data
            )
            
        except Exception as e:
            self.logger.error(f"Erreur validation vidéo {file_path}: {e}")
            return self._create_error_result([f"Erreur lecture vidéo: {str(e)}"])
    
    def _analyze_video_quality(self, cap: cv2.VideoCapture, analysis_data: Dict, warnings: List[str]) -> float:
        """Analyse la qualité vidéo"""
        scores = []
        frame_count = 0
        brightness_values = []
        blur_values = []
        
        # Échantillonnage de frames pour analyse
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_frames = min(30, total_frames)  # Maximum 30 frames
        frame_step = max(1, total_frames // sample_frames)
        
        for i in range(0, total_frames, frame_step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Analyse de la luminosité
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            brightness_values.append(brightness)
            
            # Analyse du flou (Laplacian variance)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_values.append(blur_score)
            
            if frame_count >= sample_frames:
                break
        
        if brightness_values:
            avg_brightness = np.mean(brightness_values)
            analysis_data["average_brightness"] = float(avg_brightness)
            
            # Score luminosité
            if 50 <= avg_brightness <= 200:
                scores.append(1.0)
            elif avg_brightness < 30 or avg_brightness > 220:
                scores.append(0.3)
                warnings.append("Problème de luminosité détecté")
            else:
                scores.append(0.7)
        
        if blur_values:
            avg_blur = np.mean(blur_values)
            analysis_data["average_blur_score"] = float(avg_blur)
            
            # Score netteté
            if avg_blur > 100:
                scores.append(1.0)
            elif avg_blur < 50:
                scores.append(0.4)
                warnings.append("Vidéo floue détectée")
            else:
                scores.append(0.7)
        
        analysis_data["analyzed_frames"] = frame_count
        
        return np.mean(scores) if scores else 0.5
    
    def _analyze_video_content(self, cap: cv2.VideoCapture, analysis_data: Dict, warnings: List[str]):
        """Analyse le contenu vidéo pour détecter des problèmes"""
        # Détection de frames corrompues ou noires
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        black_frames = 0
        corrupted_frames = 0
        
        sample_frames = min(20, total_frames)
        frame_step = max(1, total_frames // sample_frames)
        
        for i in range(0, total_frames, frame_step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                corrupted_frames += 1
                continue
            
            # Détection frame noire
            if np.mean(frame) < 10:
                black_frames += 1
        
        black_frame_percentage = (black_frames / sample_frames) * 100 if sample_frames > 0 else 0
        corrupted_frame_percentage = (corrupted_frames / sample_frames) * 100 if sample_frames > 0 else 0
        
        analysis_data["black_frames_percentage"] = black_frame_percentage
        analysis_data["corrupted_frames_percentage"] = corrupted_frame_percentage
        
        if black_frame_percentage > 10:
            warnings.append(f"Frames noires détectées: {black_frame_percentage:.1f}%")
        
        if corrupted_frame_percentage > 5:
            warnings.append(f"Frames corrompues: {corrupted_frame_percentage:.1f}%")
    
    def _create_error_result(self, errors: List[str]) -> ContentValidationResult:
        """Crée un résultat d'erreur"""
        return ContentValidationResult(
            is_valid=False,
            quality_score=0.0,
            content_type="video",
            format_detected="unknown",
            errors=errors,
            warnings=[],
            metadata={},
            analysis_data={}
        )

class ImageContentValidator:
    """Validateur spécialisé pour contenu image"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ImageContentValidator")
        self.min_resolution = (100, 100)
        self.max_resolution = (16384, 16384)  # 16K
        
        # Initialisation détecteur de contenu inapproprié
        try:
            self.nude_detector = NudeDetector()
        except:
            self.nude_detector = None
            self.logger.warning("NudeDetector non disponible")
    
    def validate_image_content(self, file_path: str) -> ContentValidationResult:
        """Valide le contenu image avec analyse avancée"""
        errors = []
        warnings = []
        metadata = {}
        analysis_data = {}
        
        try:
            # Ouverture de l'image
            with Image.open(file_path) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format
                
                metadata.update({
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "format": format_name,
                    "resolution": f"{width}x{height}"
                })
                
                # Validation résolution
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    errors.append(f"Résolution trop faible: {width}x{height}")
                elif width > self.max_resolution[0] or height > self.max_resolution[1]:
                    warnings.append(f"Résolution très élevée: {width}x{height}")
                
                # Analyse qualité image
                quality_score = self._analyze_image_quality(img, analysis_data, warnings)
                
                # Extraction métadonnées EXIF
                self._extract_exif_data(img, metadata, analysis_data)
                
                # Analyse du contenu
                self._analyze_image_content(file_path, analysis_data, warnings)
                
                return ContentValidationResult(
                    is_valid=len(errors) == 0,
                    quality_score=quality_score,
                    content_type="image",
                    format_detected=Path(file_path).suffix.lower(),
                    errors=errors,
                    warnings=warnings,
                    metadata=metadata,
                    analysis_data=analysis_data
                )
                
        except Exception as e:
            self.logger.error(f"Erreur validation image {file_path}: {e}")
            return ContentValidationResult(
                is_valid=False,
                quality_score=0.0,
                content_type="image",
                format_detected="unknown",
                errors=[f"Erreur lecture image: {str(e)}"],
                warnings=[],
                metadata={},
                analysis_data={}
            )
    
    def _analyze_image_quality(self, img: Image.Image, analysis_data: Dict, warnings: List[str]) -> float:
        """Analyse la qualité de l'image"""
        scores = []
        
        # Conversion en RGB si nécessaire
        if img.mode != 'RGB':
            img_rgb = img.convert('RGB')
        else:
            img_rgb = img
        
        # Analyse statistiques couleur
        stat = ImageStat.Stat(img_rgb)
        
        # Analyse luminosité
        brightness = sum(stat.mean) / len(stat.mean)
        analysis_data["brightness"] = brightness
        
        if 50 <= brightness <= 200:
            scores.append(1.0)
        elif brightness < 20 or brightness > 235:
            scores.append(0.3)
            warnings.append("Problème de luminosité")
        else:
            scores.append(0.7)
        
        # Analyse contraste
        contrast = sum(stat.stddev) / len(stat.stddev)
        analysis_data["contrast"] = contrast
        
        if contrast > 30:
            scores.append(1.0)
        elif contrast < 10:
            scores.append(0.4)
            warnings.append("Contraste faible")
        else:
            scores.append(0.7)
        
        # Analyse netteté (approximation via variance)
        import numpy as np
        img_array = np.array(img_rgb.convert('L'))
        
        # Filtre Laplacian pour détecter les contours
        from scipy import ndimage
        laplacian_var = ndimage.laplace(img_array).var()
        analysis_data["sharpness"] = float(laplacian_var)
        
        if laplacian_var > 500:
            scores.append(1.0)
        elif laplacian_var < 100:
            scores.append(0.4)
            warnings.append("Image floue")
        else:
            scores.append(0.7)
        
        return np.mean(scores)
    
    def _extract_exif_data(self, img: Image.Image, metadata: Dict, analysis_data: Dict):
        """Extrait les données EXIF"""
        try:
            exif = img._getexif()
            if exif:
                exif_data = {}
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)
                
                analysis_data["exif"] = exif_data
                
                # Extraction des informations importantes
                if "DateTime" in exif_data:
                    metadata["creation_date"] = exif_data["DateTime"]
                if "Make" in exif_data:
                    metadata["camera_make"] = exif_data["Make"]
                if "Model" in exif_data:
                    metadata["camera_model"] = exif_data["Model"]
                
        except Exception as e:
            self.logger.debug(f"Impossible d'extraire EXIF: {e}")
    
    def _analyze_image_content(self, file_path: str, analysis_data: Dict, warnings: List[str]):
        """Analyse le contenu de l'image"""
        try:
            # Détection de contenu inapproprié
            if self.nude_detector:
                detections = self.nude_detector.detect(file_path)
                
                inappropriate_content = []
                for detection in detections:
                    if detection['score'] > 0.6:  # Seuil de confiance
                        inappropriate_content.append({
                            "class": detection['class'],
                            "score": detection['score']
                        })
                
                if inappropriate_content:
                    analysis_data["content_warnings"] = inappropriate_content
                    warnings.append("Contenu potentiellement inapproprié détecté")
            
            # Calcul du hash pour déduplication
            with Image.open(file_path) as img:
                dhash = str(imagehash.dhash(img))
                analysis_data["image_hash"] = dhash
                
        except Exception as e:
            self.logger.debug(f"Erreur analyse contenu image: {e}")

class TextContentValidator:
    """Validateur spécialisé pour contenu textuel"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TextContentValidator")
        self.min_words = 5
        self.max_words = 100000
        
        # Initialisation détecteur de langue et correcteur
        try:
            self.language_tool = language_tool_python.LanguageTool('en-US')
        except:
            self.language_tool = None
            self.logger.warning("LanguageTool non disponible")
        
        # Initialisation modèle de classification de contenu
        try:
            self.content_classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=0 if torch.cuda.is_available() else -1
            )
        except:
            self.content_classifier = None
            self.logger.warning("Content classifier non disponible")
    
    def validate_text_content(self, file_path: str) -> ContentValidationResult:
        """Valide le contenu textuel avec analyse avancée"""
        errors = []
        warnings = []
        metadata = {}
        analysis_data = {}
        
        try:
            # Détection de l'encodage
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_detection = chardet.detect(raw_data)
                encoding = encoding_detection.get('encoding', 'utf-8')
                confidence = encoding_detection.get('confidence', 0)
            
            metadata["encoding"] = encoding
            metadata["encoding_confidence"] = confidence
            
            if confidence < 0.8:
                warnings.append(f"Détection d'encodage incertaine: {confidence:.2f}")
            
            # Lecture du contenu
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Fallback vers UTF-8
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                warnings.append("Problème d'encodage, fallback vers UTF-8")
            
            # Analyse statistiques de base
            word_count = lexicon_count(content)
            char_count = len(content)
            line_count = content.count('\n') + 1
            
            metadata.update({
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count
            })
            
            # Validation longueur
            if word_count < self.min_words:
                errors.append(f"Texte trop court: {word_count} mots (minimum: {self.min_words})")
            elif word_count > self.max_words:
                errors.append(f"Texte trop long: {word_count} mots (maximum: {self.max_words})")
            
            # Analyse qualité textuelle
            quality_score = self._analyze_text_quality(content, analysis_data, warnings)
            
            # Analyse du contenu
            self._analyze_text_content(content, analysis_data, warnings)
            
            return ContentValidationResult(
                is_valid=len(errors) == 0,
                quality_score=quality_score,
                content_type="text",
                format_detected=Path(file_path).suffix.lower(),
                errors=errors,
                warnings=warnings,
                metadata=metadata,
                analysis_data=analysis_data
            )
            
        except Exception as e:
            self.logger.error(f"Erreur validation texte {file_path}: {e}")
            return ContentValidationResult(
                is_valid=False,
                quality_score=0.0,
                content_type="text",
                format_detected="unknown",
                errors=[f"Erreur lecture texte: {str(e)}"],
                warnings=[],
                metadata={},
                analysis_data={}
            )
    
    def _analyze_text_quality(self, content: str, analysis_data: Dict, warnings: List[str]) -> float:
        """Analyse la qualité du texte"""
        scores = []
        
        # Analyse lisibilité
        try:
            readability = flesch_reading_ease(content)
            analysis_data["readability_score"] = readability
            
            if 60 <= readability <= 90:
                scores.append(1.0)
            elif readability < 30 or readability > 100:
                scores.append(0.5)
                warnings.append("Lisibilité faible ou problématique")
            else:
                scores.append(0.7)
        except:
            scores.append(0.5)
        
        # Analyse grammaticale
        if self.language_tool:
            try:
                # Limiter à 1000 caractères pour performance
                sample_text = content[:1000] if len(content) > 1000 else content
                matches = self.language_tool.check(sample_text)
                error_count = len(matches)
                
                analysis_data["grammar_errors"] = error_count
                
                if error_count == 0:
                    scores.append(1.0)
                elif error_count <= 5:
                    scores.append(0.8)
                elif error_count <= 10:
                    scores.append(0.6)
                    warnings.append(f"Erreurs grammaticales détectées: {error_count}")
                else:
                    scores.append(0.4)
                    warnings.append(f"Nombreuses erreurs grammaticales: {error_count}")
            except:
                scores.append(0.7)  # Score neutre si vérification impossible
        
        # Analyse de la structure
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        empty_line_ratio = (len(lines) - len(non_empty_lines)) / len(lines)
        
        analysis_data["empty_line_ratio"] = empty_line_ratio
        
        if 0.1 <= empty_line_ratio <= 0.3:
            scores.append(1.0)  # Bonne structure
        elif empty_line_ratio > 0.5:
            scores.append(0.6)
            warnings.append("Beaucoup de lignes vides")
        else:
            scores.append(0.8)
        
        return np.mean(scores) if scores else 0.5
    
    def _analyze_text_content(self, content: str, analysis_data: Dict, warnings: List[str]):
        """Analyse le contenu textuel pour détecter des problèmes"""
        # Détection de contenu toxique
        if self.content_classifier:
            try:
                # Analyser par chunks pour gérer les longs textes
                chunk_size = 512
                chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                
                toxic_scores = []
                for chunk in chunks[:5]:  # Limiter à 5 chunks
                    if chunk.strip():
                        result = self.content_classifier(chunk)
                        if result[0]['label'] == 'TOXIC' and result[0]['score'] > 0.7:
                            toxic_scores.append(result[0]['score'])
                
                if toxic_scores:
                    avg_toxic_score = np.mean(toxic_scores)
                    analysis_data["toxicity_score"] = avg_toxic_score
                    warnings.append("Contenu potentiellement inapproprié détecté")
                    
            except Exception as e:
                self.logger.debug(f"Erreur analyse toxicité: {e}")
        
        # Détection de spam/contenu répétitif
        words = content.lower().split()
        unique_words = set(words)
        repetition_ratio = len(words) / len(unique_words) if unique_words else 1
        
        analysis_data["word_repetition_ratio"] = repetition_ratio
        
        if repetition_ratio > 3:
            warnings.append("Contenu très répétitif détecté")
        
        # Analyse de la diversité du vocabulaire
        vocabulary_richness = len(unique_words) / len(words) if words else 0
        analysis_data["vocabulary_richness"] = vocabulary_richness
        
        if vocabulary_richness < 0.3:
            warnings.append("Vocabulaire limité")

class ContentValidator:
    """Validateur principal de contenu multimédia"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ContentValidator")
        
        # Initialisation des validateurs spécialisés
        self.audio_validator = AudioContentValidator()
        self.video_validator = VideoContentValidator()
        self.image_validator = ImageContentValidator()
        self.text_validator = TextContentValidator()
        
        # Mapping des types de contenu
        self.content_type_mapping = {
            'audio': ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aiff', 'wma'],
            'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'raw', 'dng'],
            'text': ['txt', 'md', 'html', 'pdf', 'docx', 'rtf', 'json', 'xml']
        }
    
    def validate_content(self, file_path: str, content_type: Optional[str] = None) -> ContentValidationResult:
        """Valide le contenu d'un fichier selon son type"""
        
        if not os.path.exists(file_path):
            return ContentValidationResult(
                is_valid=False,
                quality_score=0.0,
                content_type="unknown",
                format_detected="unknown",
                errors=["Fichier introuvable"],
                warnings=[],
                metadata={},
                analysis_data={}
            )
        
        # Détection automatique du type si non spécifié
        if not content_type:
            content_type = self._detect_content_type(file_path)
        
        # Validation selon le type détecté
        try:
            if content_type == 'audio':
                return self.audio_validator.validate_audio_content(file_path)
            elif content_type == 'video':
                return self.video_validator.validate_video_content(file_path)
            elif content_type == 'image':
                return self.image_validator.validate_image_content(file_path)
            elif content_type == 'text':
                return self.text_validator.validate_text_content(file_path)
            else:
                return ContentValidationResult(
                    is_valid=False,
                    quality_score=0.0,
                    content_type="unknown",
                    format_detected="unknown",
                    errors=[f"Type de contenu non supporté: {content_type}"],
                    warnings=[],
                    metadata={},
                    analysis_data={}
                )
                
        except Exception as e:
            self.logger.error(f"Erreur validation contenu {file_path}: {e}")
            return ContentValidationResult(
                is_valid=False,
                quality_score=0.0,
                content_type=content_type or "unknown",
                format_detected="unknown",
                errors=[f"Erreur système: {str(e)}"],
                warnings=[],
                metadata={},
                analysis_data={}
            )
    
    def _detect_content_type(self, file_path: str) -> str:
        """Détecte automatiquement le type de contenu"""
        try:
            # Détection par extension
            extension = Path(file_path).suffix.lower().lstrip('.')
            
            for content_type, extensions in self.content_type_mapping.items():
                if extension in extensions:
                    return content_type
            
            # Détection par libmagic si disponible
            try:
                file_type = magic.from_file(file_path, mime=True)
                
                if file_type.startswith('audio/'):
                    return 'audio'
                elif file_type.startswith('video/'):
                    return 'video'
                elif file_type.startswith('image/'):
                    return 'image'
                elif file_type.startswith('text/') or 'text' in file_type:
                    return 'text'
            except Exception as detection_error:
                self.logger.debug(f"Could not detect MIME type for {file_path}: {detection_error}")
                # Fallback to file extension
                if file_path.suffix.lower() in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
                    return 'audio'
                elif file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    return 'video'
                elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                    return 'image'
                elif file_path.suffix.lower() in ['.txt', '.md', '.json', '.xml', '.csv']:
                    return 'text'
            
            return 'unknown'
            
        except Exception as e:
            self.logger.error(f"Erreur détection type {file_path}: {e}")
            return 'unknown'

class AsyncContentValidator:
    """Version asynchrone du validateur de contenu"""
    
    def __init__(self):
        self.sync_validator = ContentValidator()
        self.logger = logging.getLogger(f"{__name__}.AsyncContentValidator")
    
    async def validate_content(self, file_path: str, content_type: Optional[str] = None) -> ContentValidationResult:
        """Valide le contenu de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        # Exécution synchrone dans un thread pool
        result = await loop.run_in_executor(
            None,
            self.sync_validator.validate_content,
            file_path,
            content_type
        )
        
        return result
    
    async def validate_batch(self, file_paths: List[str], content_types: Optional[List[str]] = None) -> Dict[str, ContentValidationResult]:
        """Valide un lot de fichiers de manière asynchrone"""
        if content_types is None:
            content_types = [None] * len(file_paths)
        
        # Création des tâches asynchrones
        tasks = []
        for i, file_path in enumerate(file_paths):
            content_type = content_types[i] if i < len(content_types) else None
            task = self.validate_content(file_path, content_type)
            tasks.append(task)
        
        # Exécution en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Formatage des résultats
        validation_results = {}
        for i, result in enumerate(results):
            file_path = file_paths[i]
            
            if isinstance(result, Exception):
                validation_results[file_path] = ContentValidationResult(
                    is_valid=False,
                    quality_score=0.0,
                    content_type="unknown",
                    format_detected="unknown",
                    errors=[f"Erreur validation: {str(result)}"],
                    warnings=[],
                    metadata={},
                    analysis_data={}
                )
            else:
                validation_results[file_path] = result
        
        return validation_results

# Export des classes principales
__all__ = [
    'ContentValidator',
    'AsyncContentValidator',
    'ContentValidationResult',
    'AudioContentValidator',
    'VideoContentValidator', 
    'ImageContentValidator',
    'TextContentValidator'
]
