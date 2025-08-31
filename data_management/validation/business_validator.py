"""🚀 Business Rules Validation System - IA Influencer Agent Platform Enterprise
==========================================================================
Module: backend/data_management/validation/business_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE VALIDATION MÉTIER MULTI-CRÉATEURS
Validation des règles business pour musiciens, influenceurs, photographes, blogueurs, comédiens
- Respect quotas et limites par type d'utilisateur
- Validation cohérence contenu/profil créateur
- Contrôle qualité selon standards métier
- Validation workflows et processus
"""
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import os
import json
from decimal import Decimal

# Content analysis
import librosa
import cv2
from PIL import Image
import numpy as np

# Text analysis
from textstat import flesch_reading_ease, lexicon_count
import langdetect

logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Types de créateurs supportés"""
    MUSICIAN = "musician"
    INFLUENCER = "influencer" 
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"

class ContentCategory(Enum):
    """Catégories de contenu"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"

class QualityLevel(Enum):
    """Niveaux de qualité"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"

@dataclass
class BusinessValidationResult:
    """Résultat de validation métier"""
    is_valid: bool
    compliance_score: float  # 0.0 - 1.0
    business_category: str
    quality_level: QualityLevel
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]
    quotas_usage: Dict[str, Any]

class CreatorQuotaManager:
    """Gestionnaire des quotas par type de créateur"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CreatorQuotaManager")
        
        # Quotas par type de créateur (limites journalières/mensuelles)
        self.quotas_config = {
            CreatorType.MUSICIAN: {
                'daily_uploads': 50,
                'monthly_uploads': 1000,
                'max_file_size_mb': {
                    'audio': 500,
                    'video': 2000,
                    'image': 50,
                    'document': 10
                },
                'max_duration_minutes': {
                    'audio': 60,
                    'video': 120
                },
                'storage_quota_gb': 100,
                'collaboration_slots': 20
            },
            CreatorType.INFLUENCER: {
                'daily_uploads': 100,
                'monthly_uploads': 2000,
                'max_file_size_mb': {
                    'video': 1000,
                    'image': 25,
                    'audio': 100,
                    'document': 5
                },
                'max_duration_minutes': {
                    'video': 60,
                    'audio': 30
                },
                'storage_quota_gb': 75,
                'collaboration_slots': 50
            },
            CreatorType.PHOTOGRAPHER: {
                'daily_uploads': 200,
                'monthly_uploads': 5000,
                'max_file_size_mb': {
                    'image': 200,
                    'video': 500,
                    'document': 20,
                    'audio': 50
                },
                'max_duration_minutes': {
                    'video': 30,
                    'audio': 10
                },
                'storage_quota_gb': 200,
                'collaboration_slots': 15
            },
            CreatorType.BLOGGER: {
                'daily_uploads': 30,
                'monthly_uploads': 500,
                'max_file_size_mb': {
                    'document': 50,
                    'image': 30,
                    'video': 300,
                    'audio': 100
                },
                'max_duration_minutes': {
                    'video': 45,
                    'audio': 120
                },
                'storage_quota_gb': 50,
                'collaboration_slots': 10
            },
            CreatorType.COMEDIAN: {
                'daily_uploads': 40,
                'monthly_uploads': 800,
                'max_file_size_mb': {
                    'video': 800,
                    'audio': 300,
                    'image': 20,
                    'document': 15
                },
                'max_duration_minutes': {
                    'video': 90,
                    'audio': 60
                },
                'storage_quota_gb': 80,
                'collaboration_slots': 25
            }
        }
    
    def check_quotas(self, creator_type: CreatorType, file_info: Dict[str, Any], user_usage: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie les quotas pour un créateur"""
        quota_status = {
            'within_limits': True,
            'violations': [],
            'warnings': [],
            'usage_stats': {}
        }
        
        try:
            quotas = self.quotas_config.get(creator_type)
            if not quotas:
                quota_status['violations'].append(f"Type de créateur non supporté: {creator_type}")
                quota_status['within_limits'] = False
                return quota_status
            
            # Vérification uploads journaliers
            daily_uploads = user_usage.get('daily_uploads', 0)
            if daily_uploads >= quotas['daily_uploads']:
                quota_status['violations'].append(f"Limite d'uploads journaliers atteinte: {daily_uploads}/{quotas['daily_uploads']}")
                quota_status['within_limits'] = False
            elif daily_uploads >= quotas['daily_uploads'] * 0.8:
                quota_status['warnings'].append(f"Proche de la limite journalière: {daily_uploads}/{quotas['daily_uploads']}")
            
            # Vérification uploads mensuels
            monthly_uploads = user_usage.get('monthly_uploads', 0)
            if monthly_uploads >= quotas['monthly_uploads']:
                quota_status['violations'].append(f"Limite d'uploads mensuels atteinte: {monthly_uploads}/{quotas['monthly_uploads']}")
                quota_status['within_limits'] = False
            elif monthly_uploads >= quotas['monthly_uploads'] * 0.9:
                quota_status['warnings'].append(f"Proche de la limite mensuelle: {monthly_uploads}/{quotas['monthly_uploads']}")
            
            # Vérification taille fichier
            file_size_mb = file_info.get('file_size', 0) / (1024 * 1024)
            content_type = file_info.get('content_type', 'unknown')
            
            if content_type in quotas['max_file_size_mb']:
                max_size = quotas['max_file_size_mb'][content_type]
                if file_size_mb > max_size:
                    quota_status['violations'].append(f"Fichier trop volumineux: {file_size_mb:.1f}MB > {max_size}MB")
                    quota_status['within_limits'] = False
                elif file_size_mb > max_size * 0.8:
                    quota_status['warnings'].append(f"Fichier volumineux: {file_size_mb:.1f}MB (limite: {max_size}MB)")
            
            # Vérification durée contenu
            duration_minutes = file_info.get('duration', 0) / 60
            if content_type in quotas.get('max_duration_minutes', {}):
                max_duration = quotas['max_duration_minutes'][content_type]
                if duration_minutes > max_duration:
                    quota_status['violations'].append(f"Contenu trop long: {duration_minutes:.1f}min > {max_duration}min")
                    quota_status['within_limits'] = False
            
            # Vérification stockage total
            storage_used_gb = user_usage.get('storage_used_gb', 0)
            storage_quota = quotas['storage_quota_gb']
            if storage_used_gb >= storage_quota:
                quota_status['violations'].append(f"Quota de stockage atteint: {storage_used_gb:.1f}GB/{storage_quota}GB")
                quota_status['within_limits'] = False
            elif storage_used_gb >= storage_quota * 0.9:
                quota_status['warnings'].append(f"Stockage bientôt plein: {storage_used_gb:.1f}GB/{storage_quota}GB")
            
            # Statistiques d'usage
            quota_status['usage_stats'] = {
                'daily_uploads_percent': (daily_uploads / quotas['daily_uploads']) * 100,
                'monthly_uploads_percent': (monthly_uploads / quotas['monthly_uploads']) * 100,
                'storage_percent': (storage_used_gb / storage_quota) * 100,
                'file_size_percent': (file_size_mb / quotas['max_file_size_mb'].get(content_type, 1)) * 100
            }
            
            return quota_status
            
        except Exception as e:
            self.logger.error(f"Erreur vérification quotas: {e}")
            quota_status['violations'].append(f"Erreur système quotas: {str(e)}")
            quota_status['within_limits'] = False
            return quota_status

class ContentQualityAnalyzer:
    """Analyseur de qualité de contenu selon les standards métier"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ContentQualityAnalyzer")
        
        # Standards de qualité par type de créateur
        self.quality_standards = {
            CreatorType.MUSICIAN: {
                QualityLevel.BASIC: {
                    'audio_min_bitrate': 128,
                    'audio_min_sample_rate': 22050,
                    'video_min_resolution': [480, 360],
                    'video_min_fps': 15
                },
                QualityLevel.STANDARD: {
                    'audio_min_bitrate': 192,
                    'audio_min_sample_rate': 44100,
                    'video_min_resolution': [720, 480],
                    'video_min_fps': 24
                },
                QualityLevel.PROFESSIONAL: {
                    'audio_min_bitrate': 320,
                    'audio_min_sample_rate': 48000,
                    'video_min_resolution': [1280, 720],
                    'video_min_fps': 30
                },
                QualityLevel.PREMIUM: {
                    'audio_min_bitrate': 512,
                    'audio_min_sample_rate': 96000,
                    'video_min_resolution': [1920, 1080],
                    'video_min_fps': 60
                }
            },
            CreatorType.INFLUENCER: {
                QualityLevel.BASIC: {
                    'video_min_resolution': [640, 480],
                    'video_min_fps': 24,
                    'image_min_resolution': [800, 600]
                },
                QualityLevel.STANDARD: {
                    'video_min_resolution': [1280, 720],
                    'video_min_fps': 30,
                    'image_min_resolution': [1200, 900]
                },
                QualityLevel.PROFESSIONAL: {
                    'video_min_resolution': [1920, 1080],
                    'video_min_fps': 30,
                    'image_min_resolution': [1920, 1080]
                },
                QualityLevel.PREMIUM: {
                    'video_min_resolution': [3840, 2160],
                    'video_min_fps': 60,
                    'image_min_resolution': [4000, 3000]
                }
            },
            CreatorType.PHOTOGRAPHER: {
                QualityLevel.BASIC: {
                    'image_min_resolution': [1200, 800],
                    'image_min_quality': 70
                },
                QualityLevel.STANDARD: {
                    'image_min_resolution': [2000, 1333],
                    'image_min_quality': 80
                },
                QualityLevel.PROFESSIONAL: {
                    'image_min_resolution': [4000, 2667],
                    'image_min_quality': 90
                },
                QualityLevel.PREMIUM: {
                    'image_min_resolution': [6000, 4000],
                    'image_min_quality': 95
                }
            }
        }
    
    def analyze_content_quality(self, file_path: str, creator_type: CreatorType, content_type: str) -> Dict[str, Any]:
        """Analyse la qualité du contenu selon les standards métier"""
        quality_analysis = {
            'quality_level': QualityLevel.BASIC,
            'quality_score': 0.0,
            'meets_standards': {},
            'recommendations': []
        }
        
        try:
            if content_type == 'audio':
                quality_analysis.update(self._analyze_audio_quality(file_path, creator_type))
            elif content_type == 'video':
                quality_analysis.update(self._analyze_video_quality(file_path, creator_type))
            elif content_type == 'image':
                quality_analysis.update(self._analyze_image_quality(file_path, creator_type))
            elif content_type == 'document':
                quality_analysis.update(self._analyze_document_quality(file_path, creator_type))
            
            return quality_analysis
            
        except Exception as e:
            self.logger.error(f"Erreur analyse qualité {file_path}: {e}")
            quality_analysis['error'] = str(e)
            return quality_analysis
    
    def _analyze_audio_quality(self, file_path: str, creator_type: CreatorType) -> Dict[str, Any]:
        """Analyse spécifique qualité audio"""
        analysis = {
            'audio_bitrate': 0,
            'audio_sample_rate': 0,
            'dynamic_range': 0.0,
            'spectral_quality': 0.0
        }
        
        try:
            # Analyse avec librosa
            y, sr = librosa.load(file_path, sr=None)
            analysis['audio_sample_rate'] = sr
            
            # Estimation du bitrate (approximation)
            file_size = os.path.getsize(file_path)
            duration = librosa.get_duration(y=y, sr=sr)
            estimated_bitrate = (file_size * 8) / (duration * 1000) if duration > 0 else 0
            analysis['audio_bitrate'] = int(estimated_bitrate)
            
            # Analyse de la plage dynamique
            rms = librosa.feature.rms(y=y)[0]
            dynamic_range = np.max(rms) / np.mean(rms) if np.mean(rms) > 0 else 0
            analysis['dynamic_range'] = float(dynamic_range)
            
            # Analyse spectrale
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            spectral_quality = (np.mean(spectral_centroids) + np.mean(spectral_rolloff)) / (sr * 0.5)
            analysis['spectral_quality'] = float(spectral_quality)
            
            # Évaluation selon standards
            standards = self.quality_standards.get(creator_type, {})
            quality_level = QualityLevel.BASIC
            quality_scores = []
            
            for level in [QualityLevel.PREMIUM, QualityLevel.PROFESSIONAL, QualityLevel.STANDARD, QualityLevel.BASIC]:
                level_standards = standards.get(level, {})
                
                meets_bitrate = analysis['audio_bitrate'] >= level_standards.get('audio_min_bitrate', 0)
                meets_sample_rate = analysis['audio_sample_rate'] >= level_standards.get('audio_min_sample_rate', 0)
                
                if meets_bitrate and meets_sample_rate:
                    quality_level = level
                    quality_scores.append(1.0)
                    break
                else:
                    if not meets_bitrate:
                        quality_scores.append(0.5)
                    if not meets_sample_rate:
                        quality_scores.append(0.5)
            
            analysis['quality_level'] = quality_level
            analysis['quality_score'] = np.mean(quality_scores) if quality_scores else 0.0
            
            # Recommandations
            if analysis['audio_bitrate'] < 192:
                analysis.setdefault('recommendations', []).append("Augmenter le bitrate pour une meilleure qualité")
            if analysis['audio_sample_rate'] < 44100:
                analysis.setdefault('recommendations', []).append("Utiliser un taux d'échantillonnage de 44.1kHz minimum")
            if dynamic_range < 2.0:
                analysis.setdefault('recommendations', []).append("Améliorer la plage dynamique (éviter la compression excessive)")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur analyse audio {file_path}: {e}")
            return analysis
    
    def _analyze_video_quality(self, file_path: str, creator_type: CreatorType) -> Dict[str, Any]:
        """Analyse spécifique qualité vidéo"""
        analysis = {
            'video_width': 0,
            'video_height': 0,
            'video_fps': 0,
            'video_bitrate': 0,
            'visual_quality': 0.0
        }
        
        try:
            # Analyse avec OpenCV
            cap = cv2.VideoCapture(file_path)
            
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                analysis.update({
                    'video_width': width,
                    'video_height': height,
                    'video_fps': fps
                })
                
                # Estimation bitrate
                file_size = os.path.getsize(file_path)
                duration = frame_count / fps if fps > 0 else 0
                estimated_bitrate = (file_size * 8) / (duration * 1000) if duration > 0 else 0
                analysis['video_bitrate'] = int(estimated_bitrate)
                
                # Analyse de la qualité visuelle (échantillonnage de frames)
                visual_scores = []
                sample_frames = min(10, frame_count)
                frame_step = max(1, frame_count // sample_frames)
                
                for i in range(0, frame_count, frame_step):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Analyse de netteté (variance Laplacian)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                        
                        # Analyse de luminosité
                        brightness = np.mean(gray)
                        
                        # Score combiné
                        frame_score = min(1.0, (sharpness / 1000 + brightness / 255) / 2)
                        visual_scores.append(frame_score)
                        
                        if len(visual_scores) >= sample_frames:
                            break
                
                analysis['visual_quality'] = float(np.mean(visual_scores)) if visual_scores else 0.0
                cap.release()
            
            # Évaluation selon standards
            standards = self.quality_standards.get(creator_type, {})
            quality_level = QualityLevel.BASIC
            quality_scores = []
            
            for level in [QualityLevel.PREMIUM, QualityLevel.PROFESSIONAL, QualityLevel.STANDARD, QualityLevel.BASIC]:
                level_standards = standards.get(level, {})
                
                min_res = level_standards.get('video_min_resolution', [0, 0])
                min_fps = level_standards.get('video_min_fps', 0)
                
                meets_resolution = analysis['video_width'] >= min_res[0] and analysis['video_height'] >= min_res[1]
                meets_fps = analysis['video_fps'] >= min_fps
                
                if meets_resolution and meets_fps:
                    quality_level = level
                    quality_scores.append(1.0)
                    break
                else:
                    quality_scores.append(0.5)
            
            analysis['quality_level'] = quality_level
            analysis['quality_score'] = (np.mean(quality_scores) if quality_scores else 0.0) * analysis['visual_quality']
            
            # Recommandations
            analysis['recommendations'] = []
            if analysis['video_width'] < 1280 or analysis['video_height'] < 720:
                analysis['recommendations'].append("Utiliser une résolution HD minimum (720p)")
            if analysis['video_fps'] < 30:
                analysis['recommendations'].append("Enregistrer à 30 FPS minimum pour une meilleure fluidité")
            if analysis['visual_quality'] < 0.5:
                analysis['recommendations'].append("Améliorer l'éclairage et la netteté")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur analyse vidéo {file_path}: {e}")
            return analysis
    
    def _analyze_image_quality(self, file_path: str, creator_type: CreatorType) -> Dict[str, Any]:
        """Analyse spécifique qualité image"""
        analysis = {
            'image_width': 0,
            'image_height': 0,
            'image_quality': 0,
            'color_depth': 0,
            'composition_score': 0.0
        }
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                mode = img.mode
                
                analysis.update({
                    'image_width': width,
                    'image_height': height,
                    'color_depth': len(mode) * 8 if mode in ['RGB', 'RGBA'] else 8
                })
                
                # Analyse de la qualité JPEG si applicable
                if img.format == 'JPEG' and hasattr(img, 'quantization'):
                    # Estimation de la qualité basée sur les tables de quantification
                    quality_estimate = self._estimate_jpeg_quality(img)
                    analysis['image_quality'] = quality_estimate
                else:
                    analysis['image_quality'] = 95  # Valeur par défaut pour formats sans perte
                
                # Analyse de composition (règle des tiers, contraste)
                img_array = np.array(img.convert('RGB'))
                composition_score = self._analyze_image_composition(img_array)
                analysis['composition_score'] = composition_score
            
            # Évaluation selon standards
            standards = self.quality_standards.get(creator_type, {})
            quality_level = QualityLevel.BASIC
            quality_scores = []
            
            for level in [QualityLevel.PREMIUM, QualityLevel.PROFESSIONAL, QualityLevel.STANDARD, QualityLevel.BASIC]:
                level_standards = standards.get(level, {})
                
                min_res = level_standards.get('image_min_resolution', [0, 0])
                min_quality = level_standards.get('image_min_quality', 0)
                
                meets_resolution = analysis['image_width'] >= min_res[0] and analysis['image_height'] >= min_res[1]
                meets_quality = analysis['image_quality'] >= min_quality
                
                if meets_resolution and meets_quality:
                    quality_level = level
                    quality_scores.append(1.0)
                    break
                else:
                    quality_scores.append(0.5)
            
            analysis['quality_level'] = quality_level
            analysis['quality_score'] = (np.mean(quality_scores) if quality_scores else 0.0) * analysis['composition_score']
            
            # Recommandations
            analysis['recommendations'] = []
            if analysis['image_width'] < 1920 or analysis['image_height'] < 1080:
                analysis['recommendations'].append("Utiliser une résolution plus élevée pour un usage professionnel")
            if analysis['image_quality'] < 80:
                analysis['recommendations'].append("Améliorer la qualité de compression JPEG")
            if analysis['composition_score'] < 0.6:
                analysis['recommendations'].append("Améliorer la composition (éclairage, cadrage)")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur analyse image {file_path}: {e}")
            return analysis
    
    def _analyze_document_quality(self, file_path: str, creator_type: CreatorType) -> Dict[str, Any]:
        """Analyse spécifique qualité document"""
        analysis = {
            'word_count': 0,
            'readability_score': 0,
            'structure_score': 0.0,
            'language_detected': 'unknown'
        }
        
        try:
            # Analyse du contenu textuel
            content = ""
            extension = Path(file_path).suffix.lower()
            
            if extension == '.txt' or extension == '.md':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif extension == '.pdf':
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        content += page.extract_text()
            elif extension == '.docx':
                import docx
                doc = docx.Document(file_path)
                content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            if content:
                # Analyse statistiques
                word_count = lexicon_count(content)
                analysis['word_count'] = word_count
                
                # Analyse lisibilité
                if word_count > 10:
                    readability = flesch_reading_ease(content)
                    analysis['readability_score'] = readability
                
                # Détection de langue
                try:
                    if len(content) > 50:
                        language = langdetect.detect(content)
                        analysis['language_detected'] = language
                except:
                    pass
                
                # Analyse de structure
                lines = content.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                structure_score = len(non_empty_lines) / len(lines) if lines else 0
                analysis['structure_score'] = structure_score
            
            # Évaluation selon standards (adaptée pour documents)
            quality_level = QualityLevel.BASIC
            quality_scores = []
            
            if analysis['word_count'] >= 1000:
                quality_scores.append(1.0)
                quality_level = QualityLevel.PROFESSIONAL
            elif analysis['word_count'] >= 500:
                quality_scores.append(0.8)
                quality_level = QualityLevel.STANDARD
            elif analysis['word_count'] >= 100:
                quality_scores.append(0.6)
            else:
                quality_scores.append(0.3)
            
            if analysis['readability_score'] >= 60:
                quality_scores.append(1.0)
            elif analysis['readability_score'] >= 30:
                quality_scores.append(0.7)
            else:
                quality_scores.append(0.4)
            
            analysis['quality_level'] = quality_level
            analysis['quality_score'] = np.mean(quality_scores) if quality_scores else 0.0
            
            # Recommandations
            analysis['recommendations'] = []
            if analysis['word_count'] < 500:
                analysis['recommendations'].append("Développer le contenu pour plus d'impact")
            if analysis['readability_score'] < 50:
                analysis['recommendations'].append("Simplifier le style pour améliorer la lisibilité")
            if analysis['structure_score'] < 0.7:
                analysis['recommendations'].append("Améliorer la structure et l'organisation")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur analyse document {file_path}: {e}")
            return analysis
    
    def _estimate_jpeg_quality(self, img: Image.Image) -> int:
        """Estime la qualité JPEG basée sur les tables de quantification"""
        try:
            # Méthode approximative basée sur la taille et la résolution
            file_size = len(img.tobytes())
            pixel_count = img.width * img.height
            
            if pixel_count > 0:
                bytes_per_pixel = file_size / pixel_count
                
                if bytes_per_pixel > 3:
                    return 95
                elif bytes_per_pixel > 2:
                    return 85
                elif bytes_per_pixel > 1.5:
                    return 75
                elif bytes_per_pixel > 1:
                    return 65
                else:
                    return 50
            
            return 75  # Valeur par défaut
            
        except:
            return 75
    
    def _analyze_image_composition(self, img_array: np.ndarray) -> float:
        """Analyse la composition d'une image"""
        try:
            # Conversion en niveaux de gris pour l'analyse
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            scores = []
            
            # 1. Analyse du contraste
            contrast = np.std(gray)
            contrast_score = min(1.0, contrast / 50)
            scores.append(contrast_score)
            
            # 2. Analyse de la distribution de luminosité
            brightness_hist = np.histogram(gray, bins=10)[0]
            brightness_distribution = np.std(brightness_hist)
            brightness_score = min(1.0, brightness_distribution / 100)
            scores.append(brightness_score)
            
            # 3. Détection de contours (netteté approximative)
            from scipy import ndimage
            edges = ndimage.sobel(gray)
            edge_density = np.mean(np.abs(edges))
            edge_score = min(1.0, edge_density / 20)
            scores.append(edge_score)
            
            return np.mean(scores)
            
        except Exception as e:
            self.logger.error(f"Erreur analyse composition: {e}")
            return 0.5

class WorkflowValidator:
    """Validateur des workflows et processus métier"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WorkflowValidator")
        
        # Workflows par type de créateur
        self.creator_workflows = {
            CreatorType.MUSICIAN: {
                'content_pipeline': ['recording', 'editing', 'mastering', 'distribution'],
                'collaboration_flow': ['invitation', 'approval', 'content_merge', 'final_review'],
                'monetization_steps': ['content_upload', 'rights_verification', 'distribution_setup', 'revenue_tracking']
            },
            CreatorType.INFLUENCER: {
                'content_pipeline': ['creation', 'editing', 'optimization', 'publishing'],
                'collaboration_flow': ['brand_match', 'negotiation', 'content_creation', 'delivery'],
                'monetization_steps': ['audience_analysis', 'campaign_setup', 'content_delivery', 'performance_tracking']
            },
            CreatorType.PHOTOGRAPHER: {
                'content_pipeline': ['shooting', 'selection', 'post_processing', 'portfolio_integration'],
                'collaboration_flow': ['client_briefing', 'concept_approval', 'shooting', 'delivery'],
                'monetization_steps': ['portfolio_showcase', 'licensing_setup', 'client_matching', 'revenue_collection']
            }
        }
    
    def validate_workflow_compliance(self, creator_type: CreatorType, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide la conformité des workflows"""
        validation_result = {
            'is_compliant': True,
            'completed_steps': [],
            'missing_steps': [],
            'workflow_score': 0.0,
            'recommendations': []
        }
        
        try:
            workflows = self.creator_workflows.get(creator_type, {})
            
            for workflow_name, required_steps in workflows.items():
                if workflow_name in workflow_data:
                    user_steps = workflow_data[workflow_name]
                    completed = [step for step in required_steps if step in user_steps]
                    missing = [step for step in required_steps if step not in user_steps]
                    
                    validation_result['completed_steps'].extend(completed)
                    validation_result['missing_steps'].extend(missing)
                    
                    if missing:
                        validation_result['is_compliant'] = False
                        validation_result['recommendations'].append(
                            f"Compléter les étapes manquantes pour {workflow_name}: {', '.join(missing)}"
                        )
            
            # Calcul du score global
            total_steps = sum(len(steps) for steps in workflows.values())
            completed_count = len(validation_result['completed_steps'])
            validation_result['workflow_score'] = completed_count / total_steps if total_steps > 0 else 0.0
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erreur validation workflow: {e}")
            validation_result['is_compliant'] = False
            validation_result['recommendations'].append(f"Erreur système: {str(e)}")
            return validation_result

class BusinessValidator:
    """Validateur principal des règles métier"""
    
    def __init__(self, config: Optional[Any] = None):
        self.logger = logging.getLogger(f"{__name__}.BusinessValidator")
        self.config = config
        
        # Initialisation des composants
        self.quota_manager = CreatorQuotaManager()
        self.quality_analyzer = ContentQualityAnalyzer()
        self.workflow_validator = WorkflowValidator()
    
    def validate_business_rules(self, file_path: str, creator_type: str, content_type: str, user_data: Optional[Dict] = None) -> BusinessValidationResult:
        """Valide les règles métier pour un fichier"""
        
        try:
            # Conversion du type de créateur
            creator_enum = CreatorType(creator_type.lower())
        except ValueError:
            return BusinessValidationResult(
                is_valid=False,
                compliance_score=0.0,
                business_category='unknown',
                quality_level=QualityLevel.BASIC,
                errors=[f"Type de créateur non supporté: {creator_type}"],
                warnings=[],
                suggestions=[],
                metadata={},
                quotas_usage={}
            )
        
        errors = []
        warnings = []
        suggestions = []
        metadata = {}
        
        try:
            # Informations du fichier
            file_info = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'content_type': content_type
            }
            
            # Extraction durée si applicable
            if content_type in ['audio', 'video']:
                try:
                    if content_type == 'audio':
                        y, sr = librosa.load(file_path, sr=None)
                        duration = librosa.get_duration(y=y, sr=sr)
                    else:
                        cap = cv2.VideoCapture(file_path)
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        duration = frame_count / fps if fps > 0 else 0
                        cap.release()
                    
                    file_info['duration'] = duration
                except:
                    file_info['duration'] = 0
            
            # 1. Vérification des quotas
            user_usage = user_data.get('usage', {}) if user_data else {}
            quota_status = self.quota_manager.check_quotas(creator_enum, file_info, user_usage)
            
            if not quota_status['within_limits']:
                errors.extend(quota_status['violations'])
            warnings.extend(quota_status['warnings'])
            metadata['quotas'] = quota_status
            
            # 2. Analyse de la qualité
            quality_analysis = self.quality_analyzer.analyze_content_quality(file_path, creator_enum, content_type)
            metadata['quality'] = quality_analysis
            suggestions.extend(quality_analysis.get('recommendations', []))
            
            # 3. Validation des workflows (si données disponibles)
            if user_data and 'workflows' in user_data:
                workflow_validation = self.workflow_validator.validate_workflow_compliance(
                    creator_enum, user_data['workflows']
                )
                metadata['workflow'] = workflow_validation
                suggestions.extend(workflow_validation['recommendations'])
            
            # 4. Validation cohérence créateur/contenu
            content_coherence = self._validate_content_coherence(creator_enum, content_type, quality_analysis)
            if not content_coherence['is_coherent']:
                warnings.extend(content_coherence['warnings'])
            suggestions.extend(content_coherence['suggestions'])
            metadata['content_coherence'] = content_coherence
            
            # Calcul du score de conformité global
            compliance_score = self._calculate_compliance_score(quota_status, quality_analysis, metadata)
            
            # Détermination de la catégorie métier
            business_category = self._determine_business_category(creator_enum, content_type, quality_analysis)
            
            return BusinessValidationResult(
                is_valid=len(errors) == 0,
                compliance_score=compliance_score,
                business_category=business_category,
                quality_level=quality_analysis.get('quality_level', QualityLevel.BASIC),
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                metadata=metadata,
                quotas_usage=quota_status.get('usage_stats', {})
            )
            
        except Exception as e:
            self.logger.error(f"Erreur validation métier {file_path}: {e}")
            return BusinessValidationResult(
                is_valid=False,
                compliance_score=0.0,
                business_category='error',
                quality_level=QualityLevel.BASIC,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[],
                suggestions=[],
                metadata={},
                quotas_usage={}
            )
    
    def _validate_content_coherence(self, creator_type: CreatorType, content_type: str, quality_analysis: Dict) -> Dict[str, Any]:
        """Valide la cohérence entre le type de créateur et le contenu"""
        coherence_result = {
            'is_coherent': True,
            'warnings': [],
            'suggestions': []
        }
        
        # Règles de cohérence par type de créateur
        coherence_rules = {
            CreatorType.MUSICIAN: {
                'primary_content': ['audio', 'video'],
                'secondary_content': ['image', 'document'],
                'quality_focus': 'audio_quality'
            },
            CreatorType.INFLUENCER: {
                'primary_content': ['video', 'image'],
                'secondary_content': ['audio', 'document'],
                'quality_focus': 'visual_appeal'
            },
            CreatorType.PHOTOGRAPHER: {
                'primary_content': ['image'],
                'secondary_content': ['video', 'document'],
                'quality_focus': 'image_quality'
            },
            CreatorType.BLOGGER: {
                'primary_content': ['document'],
                'secondary_content': ['image', 'video', 'audio'],
                'quality_focus': 'content_quality'
            },
            CreatorType.COMEDIAN: {
                'primary_content': ['video', 'audio'],
                'secondary_content': ['image', 'document'],
                'quality_focus': 'entertainment_value'
            }
        }
        
        rules = coherence_rules.get(creator_type, {})
        
        # Vérification du type de contenu
        if content_type not in rules.get('primary_content', []):
            if content_type in rules.get('secondary_content', []):
                coherence_result['warnings'].append(
                    f"Contenu secondaire pour un {creator_type.value}: optimisez le contenu principal"
                )
                coherence_result['suggestions'].append(
                    f"Concentrez-vous sur {', '.join(rules['primary_content'])} pour maximiser l'impact"
                )
            else:
                coherence_result['is_coherent'] = False
                coherence_result['warnings'].append(
                    f"Type de contenu inhabituel pour un {creator_type.value}"
                )
        
        # Vérification de la qualité selon le focus
        quality_level = quality_analysis.get('quality_level', QualityLevel.BASIC)
        if quality_level == QualityLevel.BASIC and creator_type in [CreatorType.PHOTOGRAPHER, CreatorType.MUSICIAN]:
            coherence_result['suggestions'].append(
                "Améliorer la qualité technique pour un impact professionnel"
            )
        
        return coherence_result
    
    def _calculate_compliance_score(self, quota_status: Dict, quality_analysis: Dict, metadata: Dict) -> float:
        """Calcule le score de conformité global"""
        scores = []
        
        # Score quotas (50%)
        if quota_status['within_limits']:
            quota_score = 1.0
        else:
            violations = len(quota_status['violations'])
            quota_score = max(0.0, 1.0 - (violations * 0.2))
        scores.append(quota_score * 0.5)
        
        # Score qualité (30%)
        quality_score = quality_analysis.get('quality_score', 0.0)
        scores.append(quality_score * 0.3)
        
        # Score workflow (20%)
        workflow_data = metadata.get('workflow', {})
        workflow_score = workflow_data.get('workflow_score', 0.5)
        scores.append(workflow_score * 0.2)
        
        return sum(scores)
    
    def _determine_business_category(self, creator_type: CreatorType, content_type: str, quality_analysis: Dict) -> str:
        """Détermine la catégorie métier du contenu"""
        quality_level = quality_analysis.get('quality_level', QualityLevel.BASIC)
        
        categories = {
            (CreatorType.MUSICIAN, 'audio'): {
                QualityLevel.PREMIUM: 'professional_music',
                QualityLevel.PROFESSIONAL: 'semi_professional_music',
                QualityLevel.STANDARD: 'amateur_music',
                QualityLevel.BASIC: 'demo_music'
            },
            (CreatorType.INFLUENCER, 'video'): {
                QualityLevel.PREMIUM: 'premium_content',
                QualityLevel.PROFESSIONAL: 'professional_content',
                QualityLevel.STANDARD: 'social_content',
                QualityLevel.BASIC: 'user_generated_content'
            },
            (CreatorType.PHOTOGRAPHER, 'image'): {
                QualityLevel.PREMIUM: 'commercial_photography',
                QualityLevel.PROFESSIONAL: 'professional_photography',
                QualityLevel.STANDARD: 'artistic_photography',
                QualityLevel.BASIC: 'amateur_photography'
            }
        }
        
        category_map = categories.get((creator_type, content_type))
        if category_map:
            return category_map.get(quality_level, 'general_content')
        
        return f"{creator_type.value}_{content_type}"

class AsyncBusinessValidator:
    """Version asynchrone du validateur métier"""
    
    def __init__(self, config: Optional[Any] = None):
        self.sync_validator = BusinessValidator(config)
        self.logger = logging.getLogger(f"{__name__}.AsyncBusinessValidator")
    
    async def validate_business_rules(self, file_path: str, creator_type: str, content_type: str, user_data: Optional[Dict] = None) -> BusinessValidationResult:
        """Valide les règles métier de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_validator.validate_business_rules,
            file_path,
            creator_type,
            content_type,
            user_data
        )
        
        return result

# Export des classes principales
__all__ = [
    'BusinessValidator',
    'AsyncBusinessValidator',
    'BusinessValidationResult',
    'CreatorQuotaManager',
    'ContentQualityAnalyzer',
    'WorkflowValidator',
    'CreatorType',
    'ContentCategory',
    'QualityLevel'
]
