"""📊 Analytics Transformation Engine - IA Influencer Agent Platform Enterprise
==========================================================================
Module: backend/data_management/transformers/analytics_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================================

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
"""
import asyncio
import logging
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics

# Analytics and ML libraries
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Audio/Video analysis
import librosa
import cv2
from PIL import Image
import face_recognition

# NLP for text analytics
from textstat import textstat
import spacy
from collections import Counter
import re

from ..models.analytics_models import (
    AnalyticsMetadata, ContentAnalytics, PerformanceMetrics,
    CreatorInsights, TrendAnalysis, AudienceAnalytics
)
from ...core.exceptions import AnalyticsError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager

settings = get_settings()
logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types d'analyses supportés"""    CONTENT_QUALITY = "content_quality"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    AUDIENCE_INSIGHTS = "audience_insights"
    TREND_ANALYSIS = "trend_analysis"
    CREATOR_SCORING = "creator_scoring"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    CONTENT_OPTIMIZATION = "content_optimization"
    COMPARATIVE_ANALYSIS = "comparative_analysis"

class MetricType(Enum):
    """Types de métriques"""    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    REVENUE = "revenue"

class ContentCategory(Enum):
    """Catégories de contenu"""    MUSIC = "music"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"
    LIVE_CONTENT = "live_content"

@dataclass
class AnalyticsConfig:
    """Configuration pour l'analyse"""    analytics_type: AnalyticsType
    content_category: ContentCategory
    time_period: Optional[Tuple[datetime, datetime]] = None
    metrics_to_analyze: List[MetricType] = field(default_factory=list)
    comparison_enabled: bool = True
    prediction_enabled: bool = True
    visualization_enabled: bool = True
    creator_type: Optional[str] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsResult:
    """Résultat d'analyse"""    success: bool
    analytics_type: AnalyticsType
    content_category: ContentCategory
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    visualizations: Dict[str, str]  # Paths to generated charts
    confidence_score: float
    processing_time: float
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class ContentQualityAnalyzer:
    """Analyseur de qualité de contenu professionnel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chargement des modèles NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Modèle spaCy non trouvé, fonctionnalités NLP limitées")
            self.nlp = None
    
    def analyze_audio_quality(
        self,
        audio_path: str,
        config: AnalyticsConfig
    ) -> Dict[str, Any]:
        """Analyse la qualité audio avancée"""        
        try:
            # Chargement audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Métriques de qualité audio
            quality_metrics = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'dynamic_range': self._calculate_dynamic_range(y),
                'signal_to_noise_ratio': self._calculate_snr(y),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
                'spectral_bandwidth': np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
                'spectral_rolloff': np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
                'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(y)),
                'tempo': librosa.beat.tempo(y=y, sr=sr)[0] if len(librosa.beat.tempo(y=y, sr=sr)) > 0 else 0,
                'rms_energy': np.mean(librosa.feature.rms(y=y)),
                'harmonic_ratio': self._calculate_harmonic_ratio(y, sr)
            }
            
            # Score de qualité global
            quality_score = self._calculate_audio_quality_score(quality_metrics)
            
            # Recommandations
            recommendations = self._generate_audio_recommendations(quality_metrics)
            
            return {
                'quality_metrics': quality_metrics,
                'overall_quality_score': quality_score,
                'recommendations': recommendations,
                'analysis_type': 'audio_quality'
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse audio {audio_path}: {e}")
            return {'error': str(e)}
    
    def analyze_image_quality(
        self,
        image_path: str,
        config: AnalyticsConfig
    ) -> Dict[str, Any]:
        """Analyse la qualité image avancée"""        
        try:
            # Chargement image
            image = cv2.imread(image_path)
            image_pil = Image.open(image_path)
            
            # Métriques de qualité image
            quality_metrics = {
                'resolution': image.shape[:2],
                'aspect_ratio': image.shape[1] / image.shape[0],
                'file_size': Path(image_path).stat().st_size,
                'color_channels': image.shape[2] if len(image.shape) == 3 else 1,
                'brightness': np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)),
                'contrast': np.std(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)),
                'sharpness': self._calculate_image_sharpness(image),
                'noise_level': self._estimate_noise_level(image),
                'color_diversity': self._calculate_color_diversity(image),
                'composition_score': self._analyze_composition(image),
                'face_detection': self._detect_faces_quality(image_path)
            }
            
            # Score de qualité global
            quality_score = self._calculate_image_quality_score(quality_metrics)
            
            # Recommandations
            recommendations = self._generate_image_recommendations(quality_metrics)
            
            return {
                'quality_metrics': quality_metrics,
                'overall_quality_score': quality_score,
                'recommendations': recommendations,
                'analysis_type': 'image_quality'
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse image {image_path}: {e}")
            return {'error': str(e)}
    
    def analyze_text_quality(
        self,
        text_content: str,
        config: AnalyticsConfig
    ) -> Dict[str, Any]:
        """Analyse la qualité textuelle avancée"""        
        try:
            # Métriques de base
            word_count = len(text_content.split())
            char_count = len(text_content)
            sentence_count = len(re.split(r'[.!?]+', text_content))
            
            # Métriques de lisibilité
            readability_metrics = {
                'flesch_reading_ease': textstat.flesch_reading_ease(text_content),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text_content),
                'gunning_fog': textstat.gunning_fog(text_content),
                'automated_readability_index': textstat.automated_readability_index(text_content),
                'coleman_liau_index': textstat.coleman_liau_index(text_content),
                'avg_sentence_length': word_count / max(sentence_count, 1),
                'avg_word_length': char_count / max(word_count, 1)
            }
            
            # Analyse linguistique avec spaCy
            linguistic_analysis = {}
            if self.nlp:
                doc = self.nlp(text_content[:1000000])  # Limite pour performance
                
                linguistic_analysis = {
                    'sentiment_polarity': self._calculate_sentiment(doc),
                    'named_entities': len(doc.ents),
                    'pos_distribution': self._analyze_pos_distribution(doc),
                    'lexical_diversity': len(set([token.lemma_ for token in doc])) / max(len(doc), 1),
                    'complexity_score': self._calculate_text_complexity(doc)
                }
            
            # Métriques SEO
            seo_metrics = {
                'keyword_density': self._calculate_keyword_density(text_content),
                'heading_structure': self._analyze_heading_structure(text_content),
                'internal_links': len(re.findall(r'<a[^>]*href[^>]*>', text_content)),
                'meta_description_length': len(text_content[:160]),
                'word_count_seo_score': self._score_word_count_seo(word_count)
            }
            
            # Score de qualité global
            quality_score = self._calculate_text_quality_score(
                readability_metrics, linguistic_analysis, seo_metrics
            )
            
            # Recommandations
            recommendations = self._generate_text_recommendations(
                readability_metrics, linguistic_analysis, seo_metrics
            )
            
            return {
                'basic_metrics': {
                    'word_count': word_count,
                    'character_count': char_count,
                    'sentence_count': sentence_count
                },
                'readability_metrics': readability_metrics,
                'linguistic_analysis': linguistic_analysis,
                'seo_metrics': seo_metrics,
                'overall_quality_score': quality_score,
                'recommendations': recommendations,
                'analysis_type': 'text_quality'
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse texte: {e}")
            return {'error': str(e)}
    
    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calcule la plage dynamique audio"""        if len(audio) == 0:
            return 0.0
        
        # Calcul RMS par segments
        segment_length = len(audio) // 100
        if segment_length == 0:
            return 0.0
        
        rms_values = []
        for i in range(0, len(audio), segment_length):
            segment = audio[i:i+segment_length]
            if len(segment) > 0:
                rms = np.sqrt(np.mean(segment**2))
                if rms > 0:
                    rms_values.append(rms)
        
        if len(rms_values) < 2:
            return 0.0
        
        # Plage dynamique en dB
        max_rms = max(rms_values)
        min_rms = min(rms_values)
        
        if min_rms > 0:
            dynamic_range = 20 * np.log10(max_rms / min_rms)
            return max(0.0, dynamic_range)
        
        return 0.0
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """Calcule le rapport signal/bruit"""        if len(audio) == 0:
            return 0.0
        
        # Estimation simple du bruit (segments de faible énergie)
        rms = np.sqrt(np.mean(audio**2))
        
        # Segments triés par énergie
        segment_length = len(audio) // 50
        if segment_length == 0:
            return 0.0
        
        segment_energies = []
        for i in range(0, len(audio), segment_length):
            segment = audio[i:i+segment_length]
            if len(segment) > 0:
                energy = np.mean(segment**2)
                segment_energies.append(energy)
        
        if len(segment_energies) < 10:
            return 0.0
        
        # Bruit estimé comme la médiane des 20% segments les plus faibles
        sorted_energies = sorted(segment_energies)
        noise_threshold = int(len(sorted_energies) * 0.2)
        noise_energy = np.median(sorted_energies[:max(1, noise_threshold)])
        
        signal_energy = np.mean(segment_energies)
        
        if noise_energy > 0:
            snr = 10 * np.log10(signal_energy / noise_energy)
            return max(0.0, snr)
        
        return 0.0
    
    def _calculate_harmonic_ratio(self, audio: np.ndarray, sr: int) -> float:
        """Calcule le ratio harmonique/percussif"""        try:
            harmonic, percussive = librosa.effects.hpss(audio)
            
            harmonic_energy = np.mean(harmonic**2)
            percussive_energy = np.mean(percussive**2)
            
            total_energy = harmonic_energy + percussive_energy
            
            if total_energy > 0:
                return harmonic_energy / total_energy
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_audio_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calcule un score de qualité audio global"""        
        score = 0.0
        weights = {
            'dynamic_range': 0.25,
            'signal_to_noise_ratio': 0.25,
            'spectral_centroid': 0.15,
            'harmonic_ratio': 0.15,
            'sample_rate': 0.1,
            'rms_energy': 0.1
        }
        
        # Normalisation et scoring
        for metric, weight in weights.items():
            if metric in metrics:
                value = metrics[metric]
                
                if metric == 'dynamic_range':
                    # Bon: 20-60 dB
                    normalized = min(1.0, max(0.0, (value - 10) / 50))
                elif metric == 'signal_to_noise_ratio':
                    # Bon: > 40 dB
                    normalized = min(1.0, max(0.0, value / 60))
                elif metric == 'sample_rate':
                    # Bon: >= 44100 Hz
                    normalized = min(1.0, value / 48000)
                elif metric == 'harmonic_ratio':
                    # Dépend du type de contenu, 0.3-0.7 est bon
                    normalized = 1.0 - abs(0.5 - value) * 2
                else:
                    # Normalisation générique
                    normalized = min(1.0, max(0.0, value))
                
                score += normalized * weight
        
        return score
    
    def _generate_audio_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'amélioration audio"""        
        recommendations = []
        
        if metrics.get('dynamic_range', 0) < 15:
            recommendations.append("Augmenter la plage dynamique pour plus d'expressivité")
        
        if metrics.get('signal_to_noise_ratio', 0) < 30:
            recommendations.append("Réduire le bruit de fond pour améliorer la clarté")
        
        if metrics.get('sample_rate', 0) < 44100:
            recommendations.append("Utiliser une fréquence d'échantillonnage plus élevée (44.1kHz minimum)")
        
        if metrics.get('rms_energy', 0) < 0.1:
            recommendations.append("Augmenter le niveau général de l'audio")
        
        if metrics.get('spectral_centroid', 0) < 1000:
            recommendations.append("Ajouter plus de hautes fréquences pour la brillance")
        
        return recommendations
    
    def _calculate_image_sharpness(self, image: np.ndarray) -> float:
        """Calcule la netteté de l'image"""        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Utilisation du Laplacien pour mesurer la netteté
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return laplacian_var
    
    def _estimate_noise_level(self, image: np.ndarray) -> float:
        """Estime le niveau de bruit dans l'image"""        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Utilisation d'un filtre pour estimer le bruit
        noise = cv2.Laplacian(gray, cv2.CV_64F)
        noise_level = np.var(noise)
        
        return noise_level
    
    def _calculate_color_diversity(self, image: np.ndarray) -> float:
        """Calcule la diversité des couleurs"""        
        # Réduction de résolution pour performance
        small_image = cv2.resize(image, (100, 100))
        
        # Conversion en liste de couleurs uniques
        colors = small_image.reshape(-1, 3)
        unique_colors = np.unique(colors, axis=0)
        
        # Ratio de couleurs uniques
        diversity = len(unique_colors) / len(colors)
        
        return diversity
    
    def _analyze_composition(self, image: np.ndarray) -> float:
        """Analyse la composition de l'image (règle des tiers, etc.)"""        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Points d'intérêt selon la règle des tiers
        third_points = [
            (w//3, h//3), (2*w//3, h//3),
            (w//3, 2*h//3), (2*w//3, 2*h//3)
        ]
        
        # Calcul de l'intensité aux points d'intérêt
        interest_score = 0.0
        for x, y in third_points:
            # Région autour du point
            region = gray[max(0, y-20):min(h, y+20), max(0, x-20):min(w, x+20)]
            if region.size > 0:
                # Variance comme mesure d'intérêt
                interest_score += np.var(region)
        
        # Normalisation
        return min(1.0, interest_score / (4 * 10000))
    
    def _detect_faces_quality(self, image_path: str) -> Dict[str, Any]:
        """Détecte et analyse la qualité des visages"""        
        try:
            # Chargement avec face_recognition
            image = face_recognition.load_image_file(image_path)
            
            # Détection des visages
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return {
                'face_count': len(face_locations),
                'face_locations': face_locations,
                'face_quality': len(face_encodings) / max(1, len(face_locations)),
                'has_faces': len(face_locations) > 0
            }
            
        except Exception as e:
            logger.warning(f"Erreur détection visages: {e}")
            return {
                'face_count': 0,
                'face_locations': [],
                'face_quality': 0.0,
                'has_faces': False
            }
    
    def _calculate_image_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calcule un score de qualité image global"""        
        score = 0.0
        weights = {
            'sharpness': 0.25,
            'brightness': 0.15,
            'contrast': 0.15,
            'color_diversity': 0.15,
            'composition_score': 0.15,
            'resolution': 0.15
        }
        
        for metric, weight in weights.items():
            if metric in metrics:
                value = metrics[metric]
                
                if metric == 'sharpness':
                    # Bon: > 500
                    normalized = min(1.0, value / 1000)
                elif metric == 'brightness':
                    # Bon: 100-150
                    normalized = 1.0 - abs(125 - value) / 125
                elif metric == 'contrast':
                    # Bon: > 30
                    normalized = min(1.0, value / 60)
                elif metric == 'resolution':
                    # Score basé sur la résolution
                    pixels = value[0] * value[1]
                    if pixels > 2000000:  # > 2MP
                        normalized = 1.0
                    elif pixels > 1000000:  # > 1MP
                        normalized = 0.8
                    else:
                        normalized = 0.6
                else:
                    normalized = min(1.0, max(0.0, value))
                
                score += normalized * weight
        
        return score
    
    def _generate_image_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'amélioration image"""        
        recommendations = []
        
        if metrics.get('sharpness', 0) < 300:
            recommendations.append("Améliorer la netteté de l'image")
        
        if metrics.get('noise_level', 0) > 1000:
            recommendations.append("Réduire le bruit avec un filtre de débruitage")
        
        brightness = metrics.get('brightness', 128)
        if brightness < 80:
            recommendations.append("Augmenter la luminosité")
        elif brightness > 180:
            recommendations.append("Réduire la luminosité")
        
        if metrics.get('contrast', 0) < 25:
            recommendations.append("Augmenter le contraste")
        
        if metrics.get('color_diversity', 0) < 0.1:
            recommendations.append("Ajouter plus de variété dans les couleurs")
        
        resolution = metrics.get('resolution', (0, 0))
        if resolution[0] * resolution[1] < 1000000:
            recommendations.append("Utiliser une résolution plus élevée")
        
        return recommendations
    
    def _calculate_sentiment(self, doc) -> float:
        """Calcule le sentiment du texte (polarité)"""        
        # Sentiment basique basé sur les mots positifs/négatifs
        positive_words = set(['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'])
        negative_words = set(['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate'])
        
        words = [token.text.lower() for token in doc if token.is_alpha]
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count > 0:
            return (positive_count - negative_count) / (positive_count + negative_count)
        
        return 0.0
    
    def _analyze_pos_distribution(self, doc) -> Dict[str, float]:
        """Analyse la distribution des parties du discours"""        
        pos_counts = Counter([token.pos_ for token in doc])
        total_tokens = len(doc)
        
        if total_tokens == 0:
            return {}
        
        return {pos: count / total_tokens for pos, count in pos_counts.items()}
    
    def _calculate_text_complexity(self, doc) -> float:
        """Calcule la complexité du texte"""        
        # Facteurs de complexité
        avg_word_length = np.mean([len(token.text) for token in doc if token.is_alpha])
        unique_words_ratio = len(set([token.lemma_ for token in doc])) / max(len(doc), 1)
        
        # Complexité basée sur les mots longs et la diversité
        complexity = (avg_word_length / 10) * 0.5 + unique_words_ratio * 0.5
        
        return min(1.0, complexity)
    
    def _calculate_keyword_density(self, text: str) -> Dict[str, float]:
        """Calcule la densité des mots-clés"""        
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        if word_count == 0:
            return {}
        
        word_freq = Counter(words)
        
        # Top 10 mots les plus fréquents
        top_words = dict(word_freq.most_common(10))
        
        # Calcul de la densité (pourcentage)
        densities = {word: (count / word_count) * 100 for word, count in top_words.items()}
        
        return densities
    
    def _analyze_heading_structure(self, text: str) -> Dict[str, int]:
        """Analyse la structure des titres (HTML)"""        
        headings = {
            'h1': len(re.findall(r'<h1[^>]*>', text, re.IGNORECASE)),
            'h2': len(re.findall(r'<h2[^>]*>', text, re.IGNORECASE)),
            'h3': len(re.findall(r'<h3[^>]*>', text, re.IGNORECASE)),
            'h4': len(re.findall(r'<h4[^>]*>', text, re.IGNORECASE)),
            'h5': len(re.findall(r'<h5[^>]*>', text, re.IGNORECASE)),
            'h6': len(re.findall(r'<h6[^>]*>', text, re.IGNORECASE))
        }
        
        return headings
    
    def _score_word_count_seo(self, word_count: int) -> float:
        """Score SEO basé sur le nombre de mots"""        
        if word_count >= 1500:
            return 1.0
        elif word_count >= 1000:
            return 0.8
        elif word_count >= 500:
            return 0.6
        elif word_count >= 300:
            return 0.4
        else:
            return 0.2
    
    def _calculate_text_quality_score(
        self,
        readability: Dict[str, Any],
        linguistic: Dict[str, Any],
        seo: Dict[str, Any]
    ) -> float:
        """Calcule un score de qualité textuelle global"""        
        score = 0.0
        
        # Score de lisibilité (0.4)
        flesch_score = readability.get('flesch_reading_ease', 0)
        if flesch_score >= 60:
            readability_score = 1.0
        elif flesch_score >= 30:
            readability_score = 0.7
        else:
            readability_score = 0.4
        
        score += readability_score * 0.4
        
        # Score linguistique (0.3)
        if linguistic:
            diversity = linguistic.get('lexical_diversity', 0)
            complexity = linguistic.get('complexity_score', 0)
            linguistic_score = (diversity + complexity) / 2
        else:
            linguistic_score = 0.5
        
        score += linguistic_score * 0.3
        
        # Score SEO (0.3)
        seo_word_score = seo.get('word_count_seo_score', 0)
        seo_structure_score = 1.0 if sum(seo.get('heading_structure', {}).values()) > 0 else 0.5
        seo_score = (seo_word_score + seo_structure_score) / 2
        
        score += seo_score * 0.3
        
        return score
    
    def _generate_text_recommendations(
        self,
        readability: Dict[str, Any],
        linguistic: Dict[str, Any],
        seo: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations d'amélioration textuelle"""        
        recommendations = []
        
        # Lisibilité
        flesch_score = readability.get('flesch_reading_ease', 0)
        if flesch_score < 30:
            recommendations.append("Simplifier le vocabulaire pour améliorer la lisibilité")
        
        avg_sentence_length = readability.get('avg_sentence_length', 0)
        if avg_sentence_length > 20:
            recommendations.append("Raccourcir les phrases pour faciliter la lecture")
        
        # Linguistique
        if linguistic:
            diversity = linguistic.get('lexical_diversity', 0)
            if diversity < 0.3:
                recommendations.append("Enrichir le vocabulaire pour éviter les répétitions")
        
        # SEO
        word_count_score = seo.get('word_count_seo_score', 0)
        if word_count_score < 0.6:
            recommendations.append("Augmenter le nombre de mots (minimum 500 pour le SEO)")
        
        heading_count = sum(seo.get('heading_structure', {}).values())
        if heading_count == 0:
            recommendations.append("Ajouter des titres pour structurer le contenu")
        
        return recommendations

class PerformanceAnalyzer:
    """Analyseur de performance de contenu professionnel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_engagement_metrics(
        self,
        metrics_data: Dict[str, List[float]],
        config: AnalyticsConfig
    ) -> Dict[str, Any]:
        """Analyse les métriques d'engagement"""        
        try:
            results = {}
            
            for metric_name, values in metrics_data.items():
                if not values:
                    continue
                
                metric_analysis = {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'trend': self._calculate_trend(values),
                    'growth_rate': self._calculate_growth_rate(values),
                    'volatility': self._calculate_volatility(values),
                    'percentiles': {
                        '25th': np.percentile(values, 25),
                        '75th': np.percentile(values, 75),
                        '90th': np.percentile(values, 90)
                    }
                }
                
                results[metric_name] = metric_analysis
            
            # Analyse comparative entre métriques
            correlation_matrix = self._calculate_correlation_matrix(metrics_data)
            
            # Score de performance global
            overall_score = self._calculate_performance_score(results)
            
            # Insights et recommandations
            insights = self._generate_performance_insights(results, correlation_matrix)
            recommendations = self._generate_performance_recommendations(results)
            
            return {
                'metrics_analysis': results,
                'correlation_matrix': correlation_matrix,
                'overall_performance_score': overall_score,
                'insights': insights,
                'recommendations': recommendations,
                'analysis_type': 'performance_analysis'
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse performance: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcule la tendance des valeurs"""        
        if len(values) < 2:
            return 'insufficient_data'
        
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        if p_value < 0.05:  # Significatif
            if slope > 0:
                return 'increasing'
            else:
                return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calcule le taux de croissance"""        
        if len(values) < 2 or values[0] == 0:
            return 0.0
        
        first_value = values[0]
        last_value = values[-1]
        
        periods = len(values) - 1
        
        # Taux de croissance composé annuel (CAGR)
        if first_value > 0:
            growth_rate = (last_value / first_value) ** (1/periods) - 1
            return growth_rate
        
        return 0.0
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calcule la volatilité (coefficient de variation)"""        
        if len(values) < 2:
            return 0.0
        
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        if mean_value > 0:
            return std_value / mean_value
        
        return 0.0
    
    def _calculate_correlation_matrix(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calcule la matrice de corrélation entre métriques"""        
        # Filtrer les métriques avec des données suffisantes
        valid_metrics = {k: v for k, v in metrics_data.items() if len(v) > 1}
        
        if len(valid_metrics) < 2:
            return {}
        
        # Créer un DataFrame pandas pour faciliter les calculs
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in valid_metrics.items()]))
        
        # Matrice de corrélation
        corr_matrix = df.corr()
        
        # Conversion en dictionnaire
        return corr_matrix.to_dict()
    
    def _calculate_performance_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """Calcule un score de performance global"""        
        if not results:
            return 0.0
        
        scores = []
        
        for metric_name, analysis in results.items():
            # Score basé sur la tendance et la croissance
            trend = analysis.get('trend', 'stable')
            growth_rate = analysis.get('growth_rate', 0)
            volatility = analysis.get('volatility', 1)
            
            metric_score = 0.5  # Score de base
            
            # Bonus pour tendance positive
            if trend == 'increasing':
                metric_score += 0.3
            elif trend == 'decreasing':
                metric_score -= 0.2
            
            # Bonus pour croissance positive
            if growth_rate > 0:
                metric_score += min(0.2, growth_rate * 0.1)
            
            # Pénalité pour volatilité élevée
            if volatility > 0.5:
                metric_score -= min(0.1, (volatility - 0.5) * 0.2)
            
            scores.append(max(0.0, min(1.0, metric_score)))
        
        return np.mean(scores) if scores else 0.0
    
    def _generate_performance_insights(
        self,
        results: Dict[str, Dict[str, Any]],
        correlation_matrix: Dict[str, Dict[str, float]]
    ) -> List[str]:
        """Génère des insights sur la performance"""        
        insights = []
        
        # Insights sur les tendances
        increasing_metrics = [name for name, data in results.items() if data.get('trend') == 'increasing']
        decreasing_metrics = [name for name, data in results.items() if data.get('trend') == 'decreasing']
        
        if increasing_metrics:
            insights.append(f"Métriques en hausse: {', '.join(increasing_metrics)}")
        
        if decreasing_metrics:
            insights.append(f"Métriques en baisse: {', '.join(decreasing_metrics)}")
        
        # Insights sur les corrélations
        strong_correlations = []
        for metric1, correlations in correlation_matrix.items():
            for metric2, corr_value in correlations.items():
                if metric1 != metric2 and abs(corr_value) > 0.7:
                    strong_correlations.append(f"{metric1} ↔ {metric2} (r={corr_value:.2f})")
        
        if strong_correlations:
            insights.append(f"Corrélations fortes détectées: {'; '.join(strong_correlations[:3])}")
        
        # Insights sur la volatilité
        volatile_metrics = [name for name, data in results.items() if data.get('volatility', 0) > 0.5]
        if volatile_metrics:
            insights.append(f"Métriques volatiles nécessitant attention: {', '.join(volatile_metrics)}")
        
        return insights
    
    def _generate_performance_recommendations(self, results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Génère des recommandations d'amélioration"""        
        recommendations = []
        
        # Recommandations basées sur les tendances
        for metric_name, analysis in results.items():
            trend = analysis.get('trend', 'stable')
            growth_rate = analysis.get('growth_rate', 0)
            
            if trend == 'decreasing':
                recommendations.append(f"Analyser les causes de la baisse de {metric_name}")
            
            if growth_rate < 0:
                recommendations.append(f"Développer une stratégie pour relancer {metric_name}")
        
        # Recommandations générales
        all_trends = [data.get('trend') for data in results.values()]
        if all_trends.count('decreasing') > len(all_trends) / 2:
            recommendations.append("Revoir la stratégie globale de contenu")
        
        return recommendations

class AnalyticsTransformer:
    """Gestionnaire principal des analyses de contenu"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des analyseurs spécialisés
        self.quality_analyzer = ContentQualityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Configuration par type de créateur
        self.creator_analytics_config = {
            'musician': {
                'primary_metrics': [MetricType.VIEWS, MetricType.LIKES, MetricType.SHARES],
                'quality_focus': ['audio_quality', 'metadata_richness'],
                'performance_benchmarks': {'engagement_rate': 0.05, 'growth_rate': 0.1}
            },
            'photographer': {
                'primary_metrics': [MetricType.VIEWS, MetricType.LIKES, MetricType.SHARES],
                'quality_focus': ['image_quality', 'composition', 'color_analysis'],
                'performance_benchmarks': {'engagement_rate': 0.08, 'growth_rate': 0.15}
            },
            'influencer': {
                'primary_metrics': [MetricType.ENGAGEMENT_RATE, MetricType.REACH, MetricType.IMPRESSIONS],
                'quality_focus': ['content_consistency', 'audience_alignment'],
                'performance_benchmarks': {'engagement_rate': 0.06, 'growth_rate': 0.2}
            },
            'blogger': {
                'primary_metrics': [MetricType.VIEWS, MetricType.CLICK_THROUGH_RATE],
                'quality_focus': ['text_quality', 'seo_optimization', 'readability'],
                'performance_benchmarks': {'engagement_rate': 0.03, 'growth_rate': 0.12}
            },
            'comedian': {
                'primary_metrics': [MetricType.VIEWS, MetricType.LIKES, MetricType.SHARES],
                'quality_focus': ['video_quality', 'audio_clarity', 'engagement_timing'],
                'performance_benchmarks': {'engagement_rate': 0.07, 'growth_rate': 0.18}
            }
        }
    
    def analyze_content(
        self,
        content_path: str,
        analytics_config: AnalyticsConfig
    ) -> AnalyticsResult:
        """Analyse complète du contenu"""        
        start_time = time.time()
        
        try:
            results = {}
            insights = []
            recommendations = []
            visualizations = {}
            errors = []
            warnings = []
            
            # Analyse de qualité
            if analytics_config.analytics_type in [AnalyticsType.CONTENT_QUALITY, AnalyticsType.CONTENT_OPTIMIZATION]:
                quality_result = self._analyze_content_quality(content_path, analytics_config)
                if 'error' not in quality_result:
                    results['quality_analysis'] = quality_result
                    insights.extend(self._extract_quality_insights(quality_result))
                    recommendations.extend(quality_result.get('recommendations', []))
                else:
                    errors.append(quality_result['error'])
            
            # Génération de visualisations
            if analytics_config.visualization_enabled and results:
                viz_paths = self._generate_visualizations(results, analytics_config)
                visualizations.update(viz_paths)
            
            # Score de confiance global
            confidence_score = self._calculate_analysis_confidence(results, errors)
            
            processing_time = time.time() - start_time
            
            return AnalyticsResult(
                success=len(errors) == 0,
                analytics_type=analytics_config.analytics_type,
                content_category=analytics_config.content_category,
                metrics=results,
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations,
                confidence_score=confidence_score,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings,
                metadata={
                    'content_path': content_path,
                    'creator_type': analytics_config.creator_type,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse contenu {content_path}: {e}")
            return AnalyticsResult(
                success=False,
                analytics_type=analytics_config.analytics_type,
                content_category=analytics_config.content_category,
                metrics={},
                insights=[],
                recommendations=[],
                visualizations={},
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[],
                metadata={}
            )
    
    def _analyze_content_quality(
        self,
        content_path: str,
        config: AnalyticsConfig
    ) -> Dict[str, Any]:
        """Analyse la qualité du contenu"""        
        content_type = self._detect_content_type(content_path)
        
        if content_type == 'audio':
            return self.quality_analyzer.analyze_audio_quality(content_path, config)
        elif content_type == 'image':
            return self.quality_analyzer.analyze_image_quality(content_path, config)
        elif content_type == 'text':
            # Lecture du contenu textuel
            try:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                return self.quality_analyzer.analyze_text_quality(text_content, config)
            except Exception as e:
                return {'error': f"Erreur lecture fichier texte: {e}"}
        else:
            return {'error': f"Type de contenu non supporté: {content_type}"}
    
    def _detect_content_type(self, content_path: str) -> str:
        """Détecte le type de contenu"""        
        ext = Path(content_path).suffix.lower()
        
        audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        image_exts = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp'}
        text_exts = {'.txt', '.md', '.html', '.xml'}
        
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
    
    def _extract_quality_insights(self, quality_result: Dict[str, Any]) -> List[str]:
        """Extrait des insights de l'analyse de qualité"""        
        insights = []
        
        overall_score = quality_result.get('overall_quality_score', 0)
        
        if overall_score > 0.8:
            insights.append("Excellente qualité de contenu détectée")
        elif overall_score > 0.6:
            insights.append("Bonne qualité avec possibilités d'amélioration")
        elif overall_score > 0.4:
            insights.append("Qualité moyenne nécessitant des améliorations")
        else:
            insights.append("Qualité faible nécessitant une révision complète")
        
        # Insights spécifiques par type d'analyse
        analysis_type = quality_result.get('analysis_type')
        
        if analysis_type == 'audio_quality':
            metrics = quality_result.get('quality_metrics', {})
            if metrics.get('dynamic_range', 0) > 30:
                insights.append("Excellente plage dynamique audio")
            if metrics.get('signal_to_noise_ratio', 0) > 40:
                insights.append("Très bon rapport signal/bruit")
        
        elif analysis_type == 'image_quality':
            metrics = quality_result.get('quality_metrics', {})
            if metrics.get('sharpness', 0) > 500:
                insights.append("Image très nette")
            if metrics.get('face_detection', {}).get('has_faces'):
                insights.append("Visages détectés dans l'image")
        
        elif analysis_type == 'text_quality':
            readability = quality_result.get('readability_metrics', {})
            if readability.get('flesch_reading_ease', 0) > 60:
                insights.append("Texte facilement lisible")
            
            seo = quality_result.get('seo_metrics', {})
            if seo.get('word_count_seo_score', 0) > 0.8:
                insights.append("Longueur optimale pour le SEO")
        
        return insights
    
    def _generate_visualizations(
        self,
        results: Dict[str, Any],
        config: AnalyticsConfig
    ) -> Dict[str, str]:
        """Génère des visualisations des résultats"""        
        viz_paths = {}
        
        try:
            # Création du dossier de visualisations
            viz_dir = Path("analytics_visualizations")
            viz_dir.mkdir(exist_ok=True)
            
            # Génération selon le type d'analyse
            if 'quality_analysis' in results:
                quality_viz = self._create_quality_dashboard(
                    results['quality_analysis'], 
                    viz_dir / "quality_dashboard.png"
                )
                if quality_viz:
                    viz_paths['quality_dashboard'] = str(quality_viz)
            
            if 'performance_analysis' in results:
                performance_viz = self._create_performance_charts(
                    results['performance_analysis'],
                    viz_dir / "performance_charts.png"
                )
                if performance_viz:
                    viz_paths['performance_charts'] = str(performance_viz)
                    
        except Exception as e:
            logger.warning(f"Erreur génération visualisations: {e}")
        
        return viz_paths
    
    def _create_quality_dashboard(
        self,
        quality_data: Dict[str, Any],
        output_path: Path
    ) -> Optional[Path]:
        """Crée un dashboard de qualité"""        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Dashboard Qualité de Contenu', fontsize=16)
            
            # Score global
            overall_score = quality_data.get('overall_quality_score', 0)
            ax1 = axes[0, 0]
            ax1.pie([overall_score, 1-overall_score], 
                   labels=['Qualité', 'Amélioration'], 
                   colors=['green', 'lightgray'],
                   startangle=90)
            ax1.set_title(f'Score Global: {overall_score:.2f}')
            
            # Métriques par catégorie
            analysis_type = quality_data.get('analysis_type', 'unknown')
            
            if analysis_type == 'audio_quality':
                metrics = quality_data.get('quality_metrics', {})
                ax2 = axes[0, 1]
                metric_names = list(metrics.keys())[:5]
                metric_values = [metrics[name] for name in metric_names]
                ax2.bar(range(len(metric_names)), metric_values)
                ax2.set_xticks(range(len(metric_names)))
                ax2.set_xticklabels(metric_names, rotation=45)
                ax2.set_title('Métriques Audio')
            
            # Recommandations
            recommendations = quality_data.get('recommendations', [])
            ax3 = axes[1, 0]
            ax3.text(0.1, 0.9, 'Recommandations:', fontsize=12, weight='bold')
            for i, rec in enumerate(recommendations[:5]):
                ax3.text(0.1, 0.8 - i*0.15, f"• {rec}", fontsize=10)
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
            ax3.axis('off')
            
            # Insights
            insights = ['Analyse complétée avec succès']
            ax4 = axes[1, 1]
            ax4.text(0.1, 0.9, 'Insights:', fontsize=12, weight='bold')
            for i, insight in enumerate(insights[:5]):
                ax4.text(0.1, 0.8 - i*0.15, f"• {insight}", fontsize=10)
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            ax4.axis('off')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur création dashboard qualité: {e}")
            return None
    
    def _create_performance_charts(
        self,
        performance_data: Dict[str, Any],
        output_path: Path
    ) -> Optional[Path]:
        """Crée des graphiques de performance"""        
        try:
            # Placeholder pour les graphiques de performance
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Données d'exemple
            x = range(10)
            y = [i + np.random.random() for i in x]
            
            ax.plot(x, y, marker='o')
            ax.set_title('Évolution des Performances')
            ax.set_xlabel('Période')
            ax.set_ylabel('Métrique')
            ax.grid(True)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur création graphiques performance: {e}")
            return None
    
    def _calculate_analysis_confidence(
        self,
        results: Dict[str, Any],
        errors: List[str]
    ) -> float:
        """Calcule le score de confiance de l'analyse"""        
        if errors:
            return 0.0
        
        confidence = 0.5  # Base
        
        # Bonus pour chaque type d'analyse réussie
        if 'quality_analysis' in results:
            confidence += 0.3
        
        if 'performance_analysis' in results:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def get_creator_optimized_config(
        self,
        creator_type: str,
        content_category: ContentCategory,
        analytics_type: AnalyticsType
    ) -> AnalyticsConfig:
        """Génère une configuration d'analyse optimisée pour le créateur"""        
        creator_config = self.creator_analytics_config.get(
            creator_type, 
            self.creator_analytics_config['influencer']
        )
        
        return AnalyticsConfig(
            analytics_type=analytics_type,
            content_category=content_category,
            metrics_to_analyze=creator_config['primary_metrics'],
            comparison_enabled=True,
            prediction_enabled=True,
            visualization_enabled=True,
            creator_type=creator_type,
            custom_parameters={
                'quality_focus': creator_config['quality_focus'],
                'performance_benchmarks': creator_config['performance_benchmarks']
            }
        )
    
    async def batch_analyze_content(
        self,
        content_paths: List[str],
        analytics_config: AnalyticsConfig
    ) -> List[AnalyticsResult]:
        """Analyse plusieurs contenus en lot"""        
        tasks = []
        for path in content_paths:
            task = asyncio.create_task(
                self._async_analyze_content(path, analytics_config)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erreur analyse {content_paths[i]}: {result}")
                processed_results.append(AnalyticsResult(
                    success=False,
                    analytics_type=analytics_config.analytics_type,
                    content_category=analytics_config.content_category,
                    metrics={},
                    insights=[],
                    recommendations=[],
                    visualizations={},
                    confidence_score=0.0,
                    processing_time=0.0,
                    errors=[f"Exception: {str(result)}"],
                    warnings=[],
                    metadata={}
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _async_analyze_content(
        self,
        content_path: str,
        analytics_config: AnalyticsConfig
    ) -> AnalyticsResult:
        """Version asynchrone de l'analyse de contenu"""        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.analyze_content,
            content_path,
            analytics_config
        )

# Instance globale
analytics_transformer = AnalyticsTransformer()

# Export des classes principales
__all__ = [
    'AnalyticsTransformer',
    'ContentQualityAnalyzer',
    'PerformanceAnalyzer',
    'AnalyticsConfig',
    'AnalyticsResult',
    'AnalyticsType',
    'MetricType',
    'ContentCategory',
    'analytics_transformer'
]
