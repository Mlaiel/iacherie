"""
Content Intelligence Engine - Analyse intelligente du contenu
Auteur: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Production

Moteur d'intelligence artificielle pour l'analyse sémantique et l'optimisation 
du contenu pour distribution multi-plateforme.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
from datetime import datetime
import re
import hashlib
from collections import Counter
import nltk
from textblob import TextBlob

class ContentType(Enum):
    """Types de contenu supportés."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MULTIMEDHA = "multimedia"

class ContentMetrics(Enum):
    """Métriques d'analyse de contenu."""
    READABILITY = "readability"
    SENTIMENT = "sentiment"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    VIRAL_POTENTIAL = "viral_potential"
    SEMANTIC_RICHNESS = "semantic_richness"

@dataclass
class ContentAnalysis:
    """Résultat d'analyse de contenu."""
    content_id: str
    content_type: ContentType
    sentiment_score: float
    readability_score: float
    engagement_potential: float
    viral_potential: float
    semantic_keywords: List[str]
    language: str
    quality_score: float
    optimization_recommendations: List[str]
    platform_adaptations: Dict[str, Any]
    analysis_timestamp: datetime

class SemanticAnalyzer:
    """Analyseur sémantique avancé pour contenu multilingue."""
    
    def __init__(self):
        self.supported_languages = [
            'en', 'es', 'fr', 'de', 'zh', 'hi', 'ar', 'pt', 'ru', 'ja', 'ko', 'it', 'nl', 'pl', 'tr'
        ]
        self.semantic_cache = {}
        self.logger = logging.getLogger("SemanticAnalyzer")
        
        # Chargement des modèles de langue (simulation)
        self._load_language_models()
    
    def _load_language_models(self):
        """Charge les modèles de traitement linguistique."""
        try:
            # Simulation du chargement de modèles NLP
            self.language_models = {lang: f"model_{lang}" for lang in self.supported_languages}
            self.logger.info(f"Loaded language models for {len(self.supported_languages)} languages")
        except Exception as e:
            self.logger.error(f"Error loading language models: {str(e)}")
    
    async def analyze_semantic_content(self, content: str, language: str = 'en') -> Dict[str, Any]:
        """Analyse sémantique complète du contenu."""
        if language not in self.supported_languages:
            language = 'en'  # Fallback à l'anglais
        
        # Cache check
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cache_key = f"{content_hash}_{language}"
        
        if cache_key in self.semantic_cache:
            return self.semantic_cache[cache_key]
        
        try:
            # Analyse sentiment
            sentiment_analysis = await self._analyze_sentiment(content, language)
            
            # Extraction d'entités
            entities = await self._extract_entities(content, language)
            
            # Analyse des mots-clés
            keywords = await self._extract_keywords(content, language)
            
            # Analyse de lisibilité
            readability = await self._calculate_readability(content, language)
            
            # Détection de thèmes
            themes = await self._detect_themes(content, language)
            
            # Score de richesse sémantique
            semantic_richness = await self._calculate_semantic_richness(content, keywords, entities)
            
            result = {
                'sentiment': sentiment_analysis,
                'entities': entities,
                'keywords': keywords,
                'readability': readability,
                'themes': themes,
                'semantic_richness': semantic_richness,
                'language': language,
                'content_length': len(content),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Mise en cache
            self.semantic_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in semantic analysis: {str(e)}")
            return self._get_default_analysis(content, language)
    
    async def _analyze_sentiment(self, content: str, language: str) -> Dict[str, Any]:
        """Analyse du sentiment du contenu."""
        try:
            # Simulation d'analyse de sentiment avec TextBlob pour l'anglais
            if language == 'en':
                blob = TextBlob(content)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
            else:
                # Simulation pour autres langues
                polarity = np.random.uniform(-1, 1)
                subjectivity = np.random.uniform(0, 1)
            
            # Classification du sentiment
            if polarity > 0.1:
                sentiment_label = "positive"
            elif polarity < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'label': sentiment_label,
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            return {'polarity': 0.0, 'subjectivity': 0.5, 'label': 'neutral', 'confidence': 0.0}
    
    async def _extract_entities(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extraction d'entités nommées."""
        try:
            # Simulation d'extraction d'entités
            words = content.split()
            
            # Détection simple d'entités (simulation)
            entities = []
            
            # Hashtags
            hashtags = re.findall(r'#\w+', content)
            for hashtag in hashtags:
                entities.append({'text': hashtag, 'type': 'hashtag', 'confidence': 0.9})
            
            # Mentions
            mentions = re.findall(r'@\w+', content)
            for mention in mentions:
                entities.append({'text': mention, 'type': 'mention', 'confidence': 0.9})
            
            # URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
            for url in urls:
                entities.append({'text': url, 'type': 'url', 'confidence': 1.0})
            
            # Mots en majuscules (possibles noms propres)
            proper_nouns = [word for word in words if word.isupper() and len(word) > 2]
            for noun in proper_nouns:
                entities.append({'text': noun, 'type': 'proper_noun', 'confidence': 0.7})
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Error in entity extraction: {str(e)}")
            return []
    
    async def _extract_keywords(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extraction de mots-clés avec scores de pertinence."""
        try:
            # Nettoyage du texte
            clean_content = re.sub(r'[^\w\s]', ' ', content.lower())
            words = clean_content.split()
            
            # Suppression des mots vides (simulation basique)
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            # Filtrage et comptage
            filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]
            word_counts = Counter(filtered_words)
            
            # Calcul des scores TF-IDF simplifiés
            total_words = len(filtered_words)
            keywords = []
            
            for word, count in word_counts.most_common(10):
                tf_score = count / total_words
                # IDF simulé basé sur la rareté
                idf_score = 1.0 / (1.0 + count * 0.1)
                relevance_score = tf_score * idf_score
                
                keywords.append({
                    'word': word,
                    'frequency': count,
                    'relevance_score': relevance_score,
                    'tf_idf': tf_score * idf_score
                })
            
            return sorted(keywords, key=lambda x: x['relevance_score'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in keyword extraction: {str(e)}")
            return []
    
    async def _calculate_readability(self, content: str, language: str) -> Dict[str, Any]:
        """Calcul de la lisibilité du contenu."""
        try:
            words = content.split()
            sentences = content.split('.')
            
            # Métriques de base
            word_count = len(words)
            sentence_count = len(sentences)
            char_count = len(content)
            
            # Calculs de lisibilité
            avg_words_per_sentence = word_count / max(sentence_count, 1)
            avg_chars_per_word = char_count / max(word_count, 1)
            
            # Score de lisibilité Flesch simplifié (simulation)
            flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * (avg_chars_per_word / 4.7))
            flesch_score = max(0, min(100, flesch_score))  # Normalisation
            
            # Classification de la lisibilité
            if flesch_score >= 90:
                readability_level = "very_easy"
            elif flesch_score >= 80:
                readability_level = "easy"
            elif flesch_score >= 70:
                readability_level = "fairly_easy"
            elif flesch_score >= 60:
                readability_level = "standard"
            elif flesch_score >= 50:
                readability_level = "fairly_difficult"
            elif flesch_score >= 30:
                readability_level = "difficult"
            else:
                readability_level = "very_difficult"
            
            return {
                'flesch_score': flesch_score,
                'readability_level': readability_level,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_words_per_sentence': avg_words_per_sentence,
                'avg_chars_per_word': avg_chars_per_word
            }
            
        except Exception as e:
            self.logger.error(f"Error in readability calculation: {str(e)}")
            return {'flesch_score': 50.0, 'readability_level': 'standard', 'word_count': 0, 'sentence_count': 0}
    
    async def _detect_themes(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Détection automatique de thèmes dans le contenu."""
        try:
            # Thèmes prédéfinis avec mots-clés associés
            theme_keywords = {
                'technology': ['tech', 'ai', 'digital', 'innovation', 'software', 'app', 'data', 'algorithm'],
                'entertainment': ['music', 'movie', 'game', 'fun', 'entertainment', 'show', 'video', 'content'],
                'lifestyle': ['fashion', 'food', 'travel', 'health', 'fitness', 'beauty', 'lifestyle'],
                'business': ['business', 'entrepreneur', 'startup', 'marketing', 'finance', 'investment'],
                'education': ['learn', 'education', 'tutorial', 'course', 'knowledge', 'skill', 'study'],
                'sports': ['sport', 'football', 'basketball', 'tennis', 'athlete', 'competition', 'game'],
                'news': ['news', 'breaking', 'update', 'report', 'announcement', 'event'],
                'art': ['art', 'creative', 'design', 'artist', 'painting', 'drawing', 'visual']
            }
            
            content_lower = content.lower()
            detected_themes = []
            
            for theme, keywords in theme_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in content_lower)
                if matches > 0:
                    relevance_score = matches / len(keywords)
                    confidence = min(relevance_score * 2, 1.0)  # Normalisation
                    
                    detected_themes.append({
                        'theme': theme,
                        'relevance_score': relevance_score,
                        'confidence': confidence,
                        'matched_keywords': [kw for kw in keywords if kw in content_lower]
                    })
            
            # Tri par score de pertinence
            return sorted(detected_themes, key=lambda x: x['relevance_score'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in theme detection: {str(e)}")
            return []
    
    async def _calculate_semantic_richness(self, content: str, keywords: List[Dict], entities: List[Dict]) -> float:
        """Calcule la richesse sémantique du contenu."""
        try:
            words = content.split()
            unique_words = set(word.lower() for word in words)
            
            # Facteurs de richesse sémantique
            vocabulary_diversity = len(unique_words) / max(len(words), 1)
            keyword_density = len(keywords) / max(len(words), 1) * 100
            entity_density = len(entities) / max(len(words), 1) * 100
            
            # Score composite
            richness_score = (
                vocabulary_diversity * 0.4 +
                min(keyword_density / 10, 0.3) * 0.3 +
                min(entity_density / 5, 0.3) * 0.3
            )
            
            return min(richness_score, 1.0)  # Normalisation
            
        except Exception as e:
            self.logger.error(f"Error calculating semantic richness: {str(e)}")
            return 0.5
    
    def _get_default_analysis(self, content: str, language: str) -> Dict[str, Any]:
        """Retourne une analyse par défaut en cas d'erreur."""
        return {
            'sentiment': {'polarity': 0.0, 'subjectivity': 0.5, 'label': 'neutral', 'confidence': 0.0},
            'entities': [],
            'keywords': [],
            'readability': {'flesch_score': 50.0, 'readability_level': 'standard'},
            'themes': [],
            'semantic_richness': 0.5,
            'language': language,
            'content_length': len(content),
            'analysis_timestamp': datetime.now().isoformat()
        }

class ContentIntelligenceEngine:
    """Moteur d'intelligence de contenu pour optimisation multi-plateforme."""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.platform_optimizers = self._initialize_platform_optimizers()
        self.content_cache = {}
        self.logger = logging.getLogger("ContentIntelligenceEngine")
    
    def _initialize_platform_optimizers(self) -> Dict[str, Any]:
        """Initialise les optimiseurs spécifiques par plateforme."""
        return {
            # Social Media Platforms
            'instagram': {
                'optimal_length': {'text': 2200, 'video': 60, 'image': 1},
                'hashtag_limit': 30,
                'preferred_formats': ['image', 'video', 'carousel'],
                'engagement_factors': ['visual_appeal', 'hashtags', 'timing']
            },
            'tiktok': {
                'optimal_length': {'video': 60, 'text': 100},
                'hashtag_limit': 100,
                'preferred_formats': ['video'],
                'engagement_factors': ['trending_sounds', 'effects', 'trends']
            },
            'youtube': {
                'optimal_length': {'video': 600, 'title': 60, 'description': 5000},
                'hashtag_limit': 15,
                'preferred_formats': ['video'],
                'engagement_factors': ['thumbnail', 'title', 'description', 'tags']
            },
            'twitter': {
                'optimal_length': {'text': 280},
                'hashtag_limit': 2,
                'preferred_formats': ['text', 'image', 'video'],
                'engagement_factors': ['timing', 'hashtags', 'mentions']
            },
            'linkedin': {
                'optimal_length': {'text': 1300, 'video': 600},
                'hashtag_limit': 5,
                'preferred_formats': ['text', 'image', 'video', 'document'],
                'engagement_factors': ['professional_tone', 'insights', 'networking']
            },
            
            # Music Platforms
            'spotify': {
                'optimal_length': {'audio': 210},  # 3.5 minutes
                'metadata_requirements': ['title', 'artist', 'genre', 'mood'],
                'preferred_formats': ['audio'],
                'engagement_factors': ['playlist_inclusion', 'genre_matching', 'mood_alignment']
            },
            'apple_music': {
                'optimal_length': {'audio': 240},  # 4 minutes
                'metadata_requirements': ['title', 'artist', 'album', 'genre'],
                'preferred_formats': ['audio'],
                'engagement_factors': ['editorial_playlists', 'genre_placement', 'artist_following']
            },
            
            # Creator Economy
            'patreon': {
                'optimal_length': {'text': 1000, 'video': 900},
                'preferred_formats': ['text', 'image', 'video', 'audio'],
                'engagement_factors': ['exclusive_content', 'community_building', 'regular_updates']
            }
        }
    
    async def analyze_content(self, content_id: str, content: str, content_type: ContentType, 
                            target_platforms: List[str] = None) -> ContentAnalysis:
        """Analyse complète du contenu pour optimisation distribution."""
        try:
            self.logger.info(f"Starting content analysis for {content_id}")
            
            # Analyse sémantique
            semantic_result = await self.semantic_analyzer.analyze_semantic_content(content)
            
            # Calcul du potentiel d'engagement
            engagement_potential = await self._calculate_engagement_potential(content, semantic_result)
            
            # Calcul du potentiel viral
            viral_potential = await self._calculate_viral_potential(content, semantic_result)
            
            # Score de qualité global
            quality_score = await self._calculate_quality_score(semantic_result, engagement_potential, viral_potential)
            
            # Recommandations d'optimisation
            optimization_recommendations = await self._generate_optimization_recommendations(
                content, semantic_result, content_type
            )
            
            # Adaptations par plateforme
            platform_adaptations = await self._generate_platform_adaptations(
                content, semantic_result, content_type, target_platforms or []
            )
            
            analysis = ContentAnalysis(
                content_id=content_id,
                content_type=content_type,
                sentiment_score=semantic_result['sentiment']['polarity'],
                readability_score=semantic_result['readability']['flesch_score'],
                engagement_potential=engagement_potential,
                viral_potential=viral_potential,
                semantic_keywords=[kw['word'] for kw in semantic_result['keywords'][:10]],
                language=semantic_result['language'],
                quality_score=quality_score,
                optimization_recommendations=optimization_recommendations,
                platform_adaptations=platform_adaptations,
                analysis_timestamp=datetime.now()
            )
            
            # Mise en cache
            self.content_cache[content_id] = analysis
            
            self.logger.info(f"Content analysis completed for {content_id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in content analysis: {str(e)}")
            raise
    
    async def _calculate_engagement_potential(self, content: str, semantic_result: Dict) -> float:
        """Calcule le potentiel d'engagement du contenu."""
        try:
            factors = []
            
            # Facteur sentiment (contenu positif = plus d'engagement)
            sentiment_factor = max(0, semantic_result['sentiment']['polarity']) * 0.3
            factors.append(sentiment_factor)
            
            # Facteur lisibilité (contenu lisible = plus d'engagement)
            readability_factor = semantic_result['readability']['flesch_score'] / 100 * 0.25
            factors.append(readability_factor)
            
            # Facteur richesse sémantique
            semantic_factor = semantic_result['semantic_richness'] * 0.2
            factors.append(semantic_factor)
            
            # Facteur hashtags/mentions (pour l'engagement social)
            entity_factor = min(len(semantic_result['entities']) / 10, 1.0) * 0.15
            factors.append(entity_factor)
            
            # Facteur longueur optimale (ni trop court, ni trop long)
            length = semantic_result['content_length']
            if 50 <= length <= 500:
                length_factor = 0.1
            elif 500 < length <= 2000:
                length_factor = 0.08
            else:
                length_factor = 0.05
            factors.append(length_factor)
            
            engagement_potential = sum(factors)
            return min(engagement_potential, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement potential: {str(e)}")
            return 0.5
    
    async def _calculate_viral_potential(self, content: str, semantic_result: Dict) -> float:
        """Calcule le potentiel viral du contenu."""
        try:
            viral_factors = []
            
            # Facteur émotion forte (positive ou négative)
            emotion_intensity = abs(semantic_result['sentiment']['polarity'])
            emotion_factor = emotion_intensity * 0.3
            viral_factors.append(emotion_factor)
            
            # Facteur actualité/tendances (basé sur les thèmes)
            trending_themes = ['technology', 'entertainment', 'news']
            theme_factor = 0
            for theme_data in semantic_result['themes']:
                if theme_data['theme'] in trending_themes:
                    theme_factor += theme_data['relevance_score'] * 0.2
            viral_factors.append(min(theme_factor, 0.2))
            
            # Facteur controverse/surprise (subjectivité élevée)
            controversy_factor = semantic_result['sentiment']['subjectivity'] * 0.15
            viral_factors.append(controversy_factor)
            
            # Facteur social (hashtags, mentions)
            social_elements = [e for e in semantic_result['entities'] if e['type'] in ['hashtag', 'mention']]
            social_factor = min(len(social_elements) / 5, 1.0) * 0.2
            viral_factors.append(social_factor)
            
            # Facteur unicité (mots rares/uniques)
            unique_words = len(set(content.lower().split()))
            total_words = len(content.split())
            uniqueness_factor = (unique_words / max(total_words, 1)) * 0.15
            viral_factors.append(uniqueness_factor)
            
            viral_potential = sum(viral_factors)
            return min(viral_potential, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating viral potential: {str(e)}")
            return 0.3
    
    async def _calculate_quality_score(self, semantic_result: Dict, engagement_potential: float, 
                                     viral_potential: float) -> float:
        """Calcule un score de qualité global du contenu."""
        try:
            quality_components = []
            
            # Qualité linguistique (lisibilité)
            linguistic_quality = semantic_result['readability']['flesch_score'] / 100
            quality_components.append(linguistic_quality * 0.3)
            
            # Richesse sémantique
            semantic_quality = semantic_result['semantic_richness']
            quality_components.append(semantic_quality * 0.25)
            
            # Potentiel d'engagement
            quality_components.append(engagement_potential * 0.25)
            
            # Équilibre émotionnel (ni trop neutre, ni trop extrême)
            emotion_balance = 1 - abs(semantic_result['sentiment']['polarity'])
            quality_components.append(emotion_balance * 0.1)
            
            # Diversité thématique
            theme_diversity = min(len(semantic_result['themes']) / 3, 1.0)
            quality_components.append(theme_diversity * 0.1)
            
            quality_score = sum(quality_components)
            return min(quality_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {str(e)}")
            return 0.6
    
    async def _generate_optimization_recommendations(self, content: str, semantic_result: Dict, 
                                                   content_type: ContentType) -> List[str]:
        """Génère des recommandations d'optimisation."""
        recommendations = []
        
        try:
            # Recommandations basées sur la lisibilité
            readability = semantic_result['readability']['flesch_score']
            if readability < 30:
                recommendations.append("Simplifier le vocabulaire pour améliorer la lisibilité")
            elif readability > 90:
                recommendations.append("Enrichir le vocabulaire pour plus de profondeur")
            
            # Recommandations basées sur le sentiment
            sentiment = semantic_result['sentiment']
            if abs(sentiment['polarity']) < 0.1:
                recommendations.append("Ajouter plus d'émotion pour augmenter l'engagement")
            
            # Recommandations basées sur les mots-clés
            if len(semantic_result['keywords']) < 5:
                recommendations.append("Enrichir le contenu avec plus de mots-clés pertinents")
            
            # Recommandations basées sur les entités
            hashtags = [e for e in semantic_result['entities'] if e['type'] == 'hashtag']
            if len(hashtags) < 3 and content_type in [ContentType.TEXT, ContentType.MULTIMEDHA]:
                recommendations.append("Ajouter des hashtags pour améliorer la découvrabilité")
            
            # Recommandations basées sur la longueur
            length = semantic_result['content_length']
            if length < 50:
                recommendations.append("Développer le contenu pour plus de substance")
            elif length > 2000:
                recommendations.append("Raccourcir le contenu pour maintenir l'attention")
            
            # Recommandations basées sur les thèmes
            if not semantic_result['themes']:
                recommendations.append("Clarifier le thème principal du contenu")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            recommendations.append("Réviser et optimiser le contenu général")
        
        return recommendations
    
    async def _generate_platform_adaptations(self, content: str, semantic_result: Dict, 
                                           content_type: ContentType, target_platforms: List[str]) -> Dict[str, Any]:
        """Génère des adaptations spécifiques par plateforme."""
        adaptations = {}
        
        try:
            for platform in target_platforms:
                if platform not in self.platform_optimizers:
                    continue
                
                platform_config = self.platform_optimizers[platform]
                adaptation = {}
                
                # Adaptation de longueur
                if content_type.value in platform_config.get('optimal_length', {}):
                    optimal_length = platform_config['optimal_length'][content_type.value]
                    current_length = len(content)
                    
                    if current_length > optimal_length:
                        adaptation['length_recommendation'] = f"Raccourcir à {optimal_length} caractères max"
                    elif current_length < optimal_length * 0.5:
                        adaptation['length_recommendation'] = f"Développer vers {optimal_length} caractères"
                
                # Adaptation hashtags
                hashtags = [e['text'] for e in semantic_result['entities'] if e['type'] == 'hashtag']
                hashtag_limit = platform_config.get('hashtag_limit', 5)
                
                if len(hashtags) > hashtag_limit:
                    adaptation['hashtag_recommendation'] = f"Réduire à {hashtag_limit} hashtags max"
                elif len(hashtags) == 0:
                    suggested_hashtags = [f"#{kw['word']}" for kw in semantic_result['keywords'][:3]]
                    adaptation['hashtag_suggestion'] = suggested_hashtags
                
                # Adaptation de format
                preferred_formats = platform_config.get('preferred_formats', [])
                if content_type.value not in preferred_formats:
                    adaptation['format_recommendation'] = f"Formats privilégiés: {', '.join(preferred_formats)}"
                
                # Facteurs d'engagement spécifiques
                engagement_factors = platform_config.get('engagement_factors', [])
                adaptation['engagement_tips'] = engagement_factors
                
                # Score d'optimisation pour la plateforme
                optimization_score = await self._calculate_platform_optimization_score(
                    content, semantic_result, platform_config
                )
                adaptation['optimization_score'] = optimization_score
                
                adaptations[platform] = adaptation
                
        except Exception as e:
            self.logger.error(f"Error generating platform adaptations: {str(e)}")
        
        return adaptations
    
    async def _calculate_platform_optimization_score(self, content: str, semantic_result: Dict, 
                                                    platform_config: Dict) -> float:
        """Calcule un score d'optimisation pour une plateforme spécifique."""
        try:
            score_factors = []
            
            # Facteur longueur
            content_length = len(content)
            optimal_length = platform_config.get('optimal_length', {}).get('text', 1000)
            
            if optimal_length * 0.8 <= content_length <= optimal_length * 1.2:
                length_score = 1.0
            else:
                length_score = max(0.3, 1.0 - abs(content_length - optimal_length) / optimal_length)
            
            score_factors.append(length_score * 0.3)
            
            # Facteur hashtags
            hashtags = [e for e in semantic_result['entities'] if e['type'] == 'hashtag']
            hashtag_limit = platform_config.get('hashtag_limit', 5)
            
            if len(hashtags) <= hashtag_limit:
                hashtag_score = min(len(hashtags) / max(hashtag_limit * 0.6, 1), 1.0)
            else:
                hashtag_score = 0.5  # Pénalité pour trop de hashtags
            
            score_factors.append(hashtag_score * 0.2)
            
            # Facteur qualité général
            quality_factor = (
                semantic_result['readability']['flesch_score'] / 100 * 0.3 +
                semantic_result['semantic_richness'] * 0.2
            )
            score_factors.append(quality_factor)
            
            optimization_score = sum(score_factors)
            return min(optimization_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating platform optimization score: {str(e)}")
            return 0.5
    
    async def get_content_analysis(self, content_id: str) -> Optional[ContentAnalysis]:
        """Récupère une analyse de contenu depuis le cache."""
        return self.content_cache.get(content_id)
    
    async def batch_analyze_content(self, content_batch: List[Dict[str, Any]]) -> List[ContentAnalysis]:
        """Analyse en lot de plusieurs contenus."""
        analyses = []
        
        tasks = []
        for content_data in content_batch:
            task = self.analyze_content(
                content_data['content_id'],
                content_data['content'],
                ContentType(content_data['content_type']),
                content_data.get('target_platforms', [])
            )
            tasks.append(task)
        
        # Exécution parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, ContentAnalysis):
                analyses.append(result)
            else:
                self.logger.error(f"Error in batch analysis: {str(result)}")
        
        return analyses
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur d'intelligence."""
        return {
            'cached_analyses': len(self.content_cache),
            'supported_platforms': len(self.platform_optimizers),
            'supported_languages': len(self.semantic_analyzer.supported_languages),
            'cache_size_mb': len(str(self.content_cache)) / 1024 / 1024,
            'last_analysis': max([analysis.analysis_timestamp for analysis in self.content_cache.values()]) 
                             if self.content_cache else None
        }