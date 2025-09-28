"""
🔍 SEO Prompt Generator - Enterprise Search Optimization System
=============================================================

**🏢 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL**
Système de génération de prompts SEO avec intelligence de recherche et optimisation multi-plateforme

**🎯 Expert Team Implementation:**
- 🤖 Lead Dev IA: Search algorithm integration et SEO intelligence
- 🏗️ Backend Senior: Infrastructure de recherche et performance optimization
- 🧠 ML Engineer: Ranking algorithms et keyword prediction models
- 🗄️ DBA: Search index optimization et analytics storage
- 🔐 Sécurité: Content safety et search result validation
- 🔗 Microservices: Distributed search architecture
- 🎵 Audio: Voice search optimization
- ⚙️ DevOps: Search performance monitoring
- 🎯 IA Prompt Engineer: SEO-optimized prompt generation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime, timedelta
import hashlib
import uuid
from urllib.parse import urlparse, parse_qs
import aiohttp
import asyncpg
from redis import asyncio as aioredis
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import spacy
# from transformers import pipeline, AutoTokenizer, AutoModel
import openai
from anthropic import Anthropic
import google.generativeai as genai
from cohere import Client as CohereClient

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine(Enum):
    """Énumération des moteurs de recherche supportés"""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"

class ContentType(Enum):
    """Types de contenu pour optimisation SEO"""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    VIDEO_DESCRIPTION = "video_description"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"
    EMAIL_SUBJECT = "email_subject"
    META_TAG = "meta_tag"
    TITLE_TAG = "title_tag"

class OptimizationLevel(Enum):
    """Niveaux d'optimisation SEO"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class SEOKeyword:
    """Modèle de données pour un mot-clé SEO"""
    keyword: str
    search_volume: int
    competition: float
    cpc: float
    trend: List[float]
    difficulty: float
    intent: str  # informational, commercial, transactional, navigational
    related_keywords: List[str] = field(default_factory=list)
    long_tail_variants: List[str] = field(default_factory=list)

@dataclass
class SEOPromptResult:
    """Résultat de génération de prompt SEO"""
    optimized_prompt: str
    keywords: List[SEOKeyword]
    seo_score: float
    readability_score: float
    content_structure: Dict[str, Any]
    meta_tags: Dict[str, str]
    optimization_suggestions: List[str]
    performance_predictions: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SearchTrend:
    """Données de tendance de recherche"""
    keyword: str
    region: str
    timeframe: str
    trend_data: List[Tuple[datetime, int]]
    peak_times: List[datetime]
    seasonal_patterns: Dict[str, float]

class KeywordResearchEngine:
    """
    🔍 Moteur de recherche de mots-clés avec ML
    Lead Dev IA + ML Engineer implementation
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
        self.nlp_model = None
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.keyword_predictor = None
        self._initialize_nlp()
    
    def _initialize_nlp(self):
        """Initialisation des modèles NLP"""
        try:
            self.nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using basic tokenization")
            self.nlp_model = None
    
    async def research_keywords(
        self,
        topic: str,
        target_audience: str,
        content_type: ContentType,
        language: str = "en",
        region: str = "US"
    ) -> List[SEOKeyword]:
        """Recherche et analyse de mots-clés avec ML"""
        try:
            # 1. Génération de mots-clés candidats
            candidate_keywords = await self._generate_candidate_keywords(
                topic, target_audience, content_type, language
            )
            
            # 2. Analyse des volumes de recherche
            keyword_data = await self._analyze_search_volumes(
                candidate_keywords, region, language
            )
            
            # 3. Analyse de la concurrence
            competition_data = await self._analyze_competition(
                keyword_data, content_type
            )
            
            # 4. Prédiction des tendances
            trend_data = await self._predict_keyword_trends(
                competition_data, region
            )
            
            # 5. Classification des intentions
            classified_keywords = await self._classify_search_intent(
                trend_data, target_audience
            )
            
            return classified_keywords
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de mots-clés: {e}")
            return []
    
    async def _generate_candidate_keywords(
        self,
        topic: str,
        target_audience: str,
        content_type: ContentType,
        language: str
    ) -> List[str]:
        """Génération de mots-clés candidats avec IA"""
        # Génération avec modèles de langage
        base_keywords = [topic]
        
        # Synonymes et variations
        if self.nlp_model:
            doc = self.nlp_model(topic)
            for token in doc:
                if token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop:
                    base_keywords.append(token.lemma_)
        
        # Génération contextuelle
        context_keywords = await self._generate_contextual_keywords(
            topic, target_audience, content_type, language
        )
        
        # Long-tail keywords
        long_tail_keywords = await self._generate_long_tail_keywords(
            base_keywords + context_keywords, target_audience
        )
        
        return list(set(base_keywords + context_keywords + long_tail_keywords))
    
    async def _generate_contextual_keywords(
        self,
        topic: str,
        target_audience: str,
        content_type: ContentType,
        language: str
    ) -> List[str]:
        """Génération de mots-clés contextuels avec IA"""
        # Utilisation de modèles de langage pour génération contextuelle
        prompts = {
            "google_trends": f"Generate trending keywords related to {topic} for {target_audience}",
            "semantic_variants": f"Generate semantic variations of {topic}",
            "user_intent": f"Generate keywords based on user intent for {content_type.value}",
            "question_keywords": f"Generate question-based keywords about {topic}"
        }
        
        contextual_keywords = []
        
        for prompt_type, prompt in prompts.items():
            try:
                # Simulation de génération avec IA
                # En production, utiliser OpenAI/Anthropic/etc.
                generated = await self._simulate_ai_keyword_generation(prompt)
                contextual_keywords.extend(generated)
            except Exception as e:
                logger.error(f"Erreur génération {prompt_type}: {e}")
        
        return contextual_keywords
    
    async def _simulate_ai_keyword_generation(self, prompt: str) -> List[str]:
        """Simulation de génération IA (remplacer par vraie IA en production)"""
        # Simulation basique pour développement
        base_words = prompt.lower().split()
        keywords = []
        
        for word in base_words:
            if len(word) > 3:
                keywords.extend([
                    f"{word}s",
                    f"best {word}",
                    f"{word} guide",
                    f"how to {word}",
                    f"{word} tips"
                ])
        
        return keywords[:10]  # Limiter pour simulation

class SEOOptimizationEngine:
    """
    ⚡ Moteur d'optimisation SEO avec algorithmes ML
    ML Engineer + Backend Senior implementation
    """
    
    def __init__(self):
        self.optimization_models = {}
        self.ranking_predictor = None
        self.content_analyzer = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialisation des modèles d'optimisation"""
        # Modèles pour différents aspects SEO
        self.optimization_models = {
            'keyword_density': self._keyword_density_optimizer,
            'content_structure': self._content_structure_optimizer,
            'readability': self._readability_optimizer,
            'semantic_relevance': self._semantic_relevance_optimizer,
            'user_intent': self._user_intent_optimizer
        }
    
    async def optimize_content(
        self,
        content: str,
        target_keywords: List[SEOKeyword],
        content_type: ContentType,
        optimization_level: OptimizationLevel
    ) -> Dict[str, Any]:
        """Optimisation complète du contenu pour SEO"""
        try:
            optimization_results = {}
            
            # 1. Optimisation de la densité des mots-clés
            keyword_optimization = await self._optimize_keyword_density(
                content, target_keywords, content_type
            )
            optimization_results['keyword_density'] = keyword_optimization
            
            # 2. Optimisation de la structure du contenu
            structure_optimization = await self._optimize_content_structure(
                content, target_keywords, content_type
            )
            optimization_results['content_structure'] = structure_optimization
            
            # 3. Optimisation de la lisibilité
            readability_optimization = await self._optimize_readability(
                content, optimization_level
            )
            optimization_results['readability'] = readability_optimization
            
            # 4. Optimisation sémantique
            semantic_optimization = await self._optimize_semantic_relevance(
                content, target_keywords
            )
            optimization_results['semantic_relevance'] = semantic_optimization
            
            # 5. Optimisation pour l'intention utilisateur
            intent_optimization = await self._optimize_user_intent(
                content, target_keywords, content_type
            )
            optimization_results['user_intent'] = intent_optimization
            
            # 6. Score global d'optimisation
            global_score = await self._calculate_optimization_score(
                optimization_results
            )
            optimization_results['global_score'] = global_score
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation SEO: {e}")
            return {}
    
    async def _optimize_keyword_density(
        self,
        content: str,
        target_keywords: List[SEOKeyword],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Optimisation de la densité des mots-clés"""
        word_count = len(content.split())
        keyword_densities = {}
        recommendations = []
        
        # Densités optimales par type de contenu
        optimal_densities = {
            ContentType.BLOG_POST: (1.0, 3.0),
            ContentType.SOCIAL_MEDIA: (2.0, 5.0),
            ContentType.VIDEO_DESCRIPTION: (1.5, 4.0),
            ContentType.PRODUCT_DESCRIPTION: (2.0, 6.0),
            ContentType.LANDING_PAGE: (1.0, 2.5)
        }
        
        optimal_range = optimal_densities.get(content_type, (1.0, 3.0))
        
        for keyword_obj in target_keywords:
            keyword = keyword_obj.keyword.lower()
            keyword_count = content.lower().count(keyword)
            density = (keyword_count / word_count) * 100 if word_count > 0 else 0
            
            keyword_densities[keyword] = {
                'current_density': density,
                'optimal_range': optimal_range,
                'count': keyword_count,
                'is_optimized': optimal_range[0] <= density <= optimal_range[1]
            }
            
            if density < optimal_range[0]:
                recommendations.append(
                    f"Augmenter la fréquence du mot-clé '{keyword}' "
                    f"({density:.1f}% -> {optimal_range[0]:.1f}%+)"
                )
            elif density > optimal_range[1]:
                recommendations.append(
                    f"Réduire la fréquence du mot-clé '{keyword}' "
                    f"({density:.1f}% -> {optimal_range[1]:.1f}%-)"
                )
        
        return {
            'keyword_densities': keyword_densities,
            'recommendations': recommendations,
            'overall_score': sum(
                1 for kd in keyword_densities.values()
                if kd['is_optimized']
            ) / len(keyword_densities) if keyword_densities else 0
        }
    
    async def _optimize_content_structure(
        self,
        content: str,
        target_keywords: List[SEOKeyword],
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Optimisation de la structure du contenu"""
        structure_analysis = {
            'headings': self._analyze_headings(content),
            'paragraphs': self._analyze_paragraphs(content),
            'sentences': self._analyze_sentences(content),
            'keyword_placement': self._analyze_keyword_placement(content, target_keywords)
        }
        
        recommendations = []
        
        # Analyse des titres
        if structure_analysis['headings']['count'] == 0:
            recommendations.append("Ajouter des titres (H1, H2, H3) pour structurer le contenu")
        
        # Analyse des paragraphes
        avg_paragraph_length = structure_analysis['paragraphs']['average_length']
        if avg_paragraph_length > 150:
            recommendations.append("Réduire la longueur moyenne des paragraphes (< 150 mots)")
        
        # Analyse des phrases
        avg_sentence_length = structure_analysis['sentences']['average_length']
        if avg_sentence_length > 20:
            recommendations.append("Réduire la longueur moyenne des phrases (< 20 mots)")
        
        return {
            'structure_analysis': structure_analysis,
            'recommendations': recommendations,
            'structure_score': self._calculate_structure_score(structure_analysis)
        }
    
    def _analyze_headings(self, content: str) -> Dict[str, Any]:
        """Analyse des titres dans le contenu"""
        # Recherche de patterns de titres (markdown, HTML, etc.)
        h1_pattern = r'^#\s+(.+)$|<h1.*?>(.*?)</h1>'
        h2_pattern = r'^##\s+(.+)$|<h2.*?>(.*?)</h2>'
        h3_pattern = r'^###\s+(.+)$|<h3.*?>(.*?)</h3>'
        
        h1_matches = re.findall(h1_pattern, content, re.MULTILINE | re.IGNORECASE)
        h2_matches = re.findall(h2_pattern, content, re.MULTILINE | re.IGNORECASE)
        h3_matches = re.findall(h3_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        return {
            'h1_count': len(h1_matches),
            'h2_count': len(h2_matches),
            'h3_count': len(h3_matches),
            'count': len(h1_matches) + len(h2_matches) + len(h3_matches),
            'hierarchy_score': self._calculate_heading_hierarchy_score(
                len(h1_matches), len(h2_matches), len(h3_matches)
            )
        }
    
    def _calculate_heading_hierarchy_score(self, h1: int, h2: int, h3: int) -> float:
        """Calcul du score de hiérarchie des titres"""
        if h1 == 0:
            return 0.0
        if h1 > 1:
            return 0.5  # Trop de H1
        if h2 == 0:
            return 0.7  # Pas de H2
        return min(1.0, (h2 + h3) / 5)  # Score basé sur la richesse de la structure

class SearchTrendAnalyzer:
    """
    📈 Analyseur de tendances de recherche
    ML Engineer + DBA implementation
    """
    
    def __init__(self):
        self.trend_models = {}
        self.seasonal_patterns = {}
        self.prediction_cache = {}
    
    async def analyze_search_trends(
        self,
        keywords: List[str],
        timeframe: str = "12m",
        region: str = "US"
    ) -> List[SearchTrend]:
        """Analyse des tendances de recherche"""
        try:
            trends = []
            
            for keyword in keywords:
                # Simulation de données de tendance
                # En production, utiliser Google Trends API, etc.
                trend_data = await self._fetch_trend_data(
                    keyword, timeframe, region
                )
                
                # Analyse des patterns saisonniers
                seasonal_patterns = await self._analyze_seasonal_patterns(
                    trend_data
                )
                
                # Identification des pics
                peak_times = await self._identify_peak_times(trend_data)
                
                trend = SearchTrend(
                    keyword=keyword,
                    region=region,
                    timeframe=timeframe,
                    trend_data=trend_data,
                    peak_times=peak_times,
                    seasonal_patterns=seasonal_patterns
                )
                
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Erreur analyse tendances: {e}")
            return []
    
    async def _fetch_trend_data(
        self,
        keyword: str,
        timeframe: str,
        region: str
    ) -> List[Tuple[datetime, int]]:
        """Récupération des données de tendance"""
        # Simulation de données (remplacer par vraie API)
        base_date = datetime.now() - timedelta(days=365)
        trend_data = []
        
        for i in range(52):  # 52 semaines
            date = base_date + timedelta(weeks=i)
            # Simulation de volume avec patterns
            volume = int(100 + 50 * np.sin(i * 0.1) + np.random.normal(0, 10))
            volume = max(0, volume)  # Pas de volumes négatifs
            trend_data.append((date, volume))
        
        return trend_data
    
    async def predict_future_trends(
        self,
        keyword: str,
        historical_data: List[Tuple[datetime, int]],
        prediction_horizon: int = 12
    ) -> List[Tuple[datetime, int, float]]:
        """Prédiction des tendances futures avec ML"""
        try:
            if len(historical_data) < 10:
                return []
            
            # Extraction des features temporelles
            dates = [item[0] for item in historical_data]
            volumes = [item[1] for item in historical_data]
            
            # Simulation de prédiction ML
            # En production, utiliser des modèles ARIMA, LSTM, etc.
            predictions = []
            last_date = dates[-1]
            last_volume = volumes[-1]
            
            for i in range(1, prediction_horizon + 1):
                pred_date = last_date + timedelta(weeks=i)
                # Simulation simple avec tendance + bruit
                trend_factor = 1 + (i * 0.01)  # Légère croissance
                seasonal_factor = 1 + 0.1 * np.sin(i * 0.2)  # Pattern saisonnier
                noise = np.random.normal(0, 0.05)
                
                predicted_volume = int(
                    last_volume * trend_factor * seasonal_factor * (1 + noise)
                )
                confidence = max(0.5, 1 - (i * 0.05))  # Confiance décroissante
                
                predictions.append((pred_date, predicted_volume, confidence))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erreur prédiction tendances: {e}")
            return []

class SEOPromptGenerator:
    """
    🎯 Générateur principal de prompts SEO
    Intégration de tous les composants expert
    """
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis):
        self.db_pool = db_pool
        self.redis_client = redis_client
        
        # Composants spécialisés
        self.keyword_engine = KeywordResearchEngine()
        self.optimization_engine = SEOOptimizationEngine()
        self.trend_analyzer = SearchTrendAnalyzer()
        
        # Modèles IA
        self.ai_providers = {
            'openai': None,  # Initialiser avec vraies clés API
            'anthropic': None,
            'google': None,
            'cohere': None
        }
        
        # Cache et métriques
        self.generation_cache = {}
        self.performance_metrics = {}
    
    async def generate_seo_prompt(
        self,
        topic: str,
        target_audience: str,
        content_type: ContentType,
        optimization_level: OptimizationLevel = OptimizationLevel.INTERMEDIATE,
        language: str = "en",
        region: str = "US",
        additional_context: Optional[Dict[str, Any]] = None
    ) -> SEOPromptResult:
        """
        Génération complète de prompt SEO optimisé
        Multi-expert implementation avec tous les rôles
        """
        try:
            logger.info(f"Génération prompt SEO: {topic} pour {target_audience}")
            
            # 1. Recherche et analyse des mots-clés (ML Engineer + Lead Dev IA)
            keywords = await self.keyword_engine.research_keywords(
                topic, target_audience, content_type, language, region
            )
            
            # 2. Analyse des tendances (ML Engineer + DBA)
            keyword_strings = [kw.keyword for kw in keywords[:10]]  # Top 10
            trends = await self.trend_analyzer.analyze_search_trends(
                keyword_strings, "12m", region
            )
            
            # 3. Génération du prompt de base (IA Prompt Engineer)
            base_prompt = await self._generate_base_prompt(
                topic, target_audience, content_type, keywords, trends
            )
            
            # 4. Optimisation SEO du prompt (Backend Senior + ML Engineer)
            optimized_prompt = await self._optimize_prompt_for_seo(
                base_prompt, keywords, optimization_level, content_type
            )
            
            # 5. Génération des méta-tags (Sécurité + Backend Senior)
            meta_tags = await self._generate_meta_tags(
                optimized_prompt, keywords, content_type
            )
            
            # 6. Calcul des scores et métriques (DBA + DevOps)
            seo_score = await self._calculate_seo_score(
                optimized_prompt, keywords, meta_tags
            )
            
            readability_score = await self._calculate_readability_score(
                optimized_prompt, language
            )
            
            # 7. Prédictions de performance (ML Engineer)
            performance_predictions = await self._predict_performance(
                optimized_prompt, keywords, trends, content_type
            )
            
            # 8. Suggestions d'optimisation (Multi-expert)
            optimization_suggestions = await self._generate_optimization_suggestions(
                optimized_prompt, keywords, seo_score, readability_score
            )
            
            # 9. Structure de contenu recommandée (Backend Senior)
            content_structure = await self._recommend_content_structure(
                optimized_prompt, keywords, content_type
            )
            
            # 10. Stockage et mise en cache (DBA + DevOps)
            result = SEOPromptResult(
                optimized_prompt=optimized_prompt,
                keywords=keywords,
                seo_score=seo_score,
                readability_score=readability_score,
                content_structure=content_structure,
                meta_tags=meta_tags,
                optimization_suggestions=optimization_suggestions,
                performance_predictions=performance_predictions
            )
            
            await self._store_generation_result(result, additional_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur génération prompt SEO: {e}")
            raise
    
    async def _generate_base_prompt(
        self,
        topic: str,
        target_audience: str,
        content_type: ContentType,
        keywords: List[SEOKeyword],
        trends: List[SearchTrend]
    ) -> str:
        """Génération du prompt de base avec contexte SEO"""
        
        # Analyse de l'intention principale
        primary_intent = self._determine_primary_intent(keywords)
        
        # Mots-clés prioritaires
        primary_keywords = [kw.keyword for kw in keywords[:5]]
        secondary_keywords = [kw.keyword for kw in keywords[5:15]]
        
        # Tendances actuelles
        trending_keywords = []
        for trend in trends:
            if any(data[1] > 80 for data in trend.trend_data[-4:]):  # 4 dernières semaines
                trending_keywords.append(trend.keyword)
        
        # Construction du prompt selon le type de contenu
        prompt_templates = {
            ContentType.BLOG_POST: self._get_blog_post_template(),
            ContentType.SOCIAL_MEDIA: self._get_social_media_template(),
            ContentType.VIDEO_DESCRIPTION: self._get_video_description_template(),
            ContentType.PRODUCT_DESCRIPTION: self._get_product_description_template(),
            ContentType.LANDING_PAGE: self._get_landing_page_template()
        }
        
        template = prompt_templates.get(content_type, self._get_generic_template())
        
        # Remplacement des variables dans le template
        base_prompt = template.format(
            topic=topic,
            target_audience=target_audience,
            primary_keywords=", ".join(primary_keywords),
            secondary_keywords=", ".join(secondary_keywords),
            trending_keywords=", ".join(trending_keywords),
            intent=primary_intent
        )
        
        return base_prompt
    
    def _get_blog_post_template(self) -> str:
        """Template pour articles de blog optimisés SEO"""
        return """
Créez un article de blog optimisé SEO sur le sujet: "{topic}"

🎯 Audience cible: {target_audience}
🔑 Mots-clés principaux: {primary_keywords}
📊 Mots-clés secondaires: {secondary_keywords}
📈 Tendances actuelles: {trending_keywords}
💡 Intention de recherche: {intent}

📋 Structure recommandée:
- Titre accrocheur avec mot-clé principal (60 caractères max)
- Introduction engageante (150 mots) avec mots-clés naturellement intégrés
- 3-5 sous-sections avec titres H2 optimisés
- Conclusion avec appel à l'action
- Méta-description (155 caractères max)

✅ Optimisations SEO à inclure:
- Densité de mots-clés: 1-3% pour le mot-clé principal
- Utilisation de synonymes et variations
- Liens internes et externes pertinents
- Balises alt pour les images
- Schema markup approprié
- Optimisation pour featured snippets

📱 Compatible: mobile-first, Core Web Vitals
🌍 Localisé pour la région et la langue cible
"""
    
    def _get_social_media_template(self) -> str:
        """Template pour contenu social media optimisé"""
        return """
Créez du contenu social media optimisé pour le sujet: "{topic}"

🎯 Audience: {target_audience}
🔑 Mots-clés: {primary_keywords}
📈 Trending: {trending_keywords}
💡 Intent: {intent}

📱 Format adapté à chaque plateforme:
- Instagram: Visuel + caption (2200 caractères max)
- LinkedIn: Professionnel + hashtags pertinents
- Twitter: Concis + hashtags tendances
- TikTok: Descriptif vidéo engageant
- YouTube: Titre + description optimisés

✅ Optimisations:
- Hashtags recherchés et populaires
- Timing optimal selon les tendances
- Appel à l'action clair
- Engagement metrics optimization
- Cross-platform consistency
"""
    
    async def _optimize_prompt_for_seo(
        self,
        base_prompt: str,
        keywords: List[SEOKeyword],
        optimization_level: OptimizationLevel,
        content_type: ContentType
    ) -> str:
        """Optimisation SEO avancée du prompt"""
        
        # Analyse du prompt actuel
        current_optimization = await self.optimization_engine.optimize_content(
            base_prompt, keywords, content_type, optimization_level
        )
        
        # Améliorations basées sur l'analyse
        optimizations = []
        
        # 1. Optimisation des mots-clés
        keyword_suggestions = current_optimization.get('keyword_density', {}).get('recommendations', [])
        for suggestion in keyword_suggestions:
            optimizations.append(f"🔑 {suggestion}")
        
        # 2. Optimisation de structure
        structure_suggestions = current_optimization.get('content_structure', {}).get('recommendations', [])
        for suggestion in structure_suggestions:
            optimizations.append(f"🏗️ {suggestion}")
        
        # 3. Optimisation de lisibilité
        readability_suggestions = current_optimization.get('readability', {}).get('recommendations', [])
        for suggestion in readability_suggestions:
            optimizations.append(f"📖 {suggestion}")
        
        # 4. Ajout des optimisations au prompt
        if optimizations:
            optimization_section = "\n\n🚀 Optimisations SEO supplémentaires:\n" + "\n".join(optimizations)
            optimized_prompt = base_prompt + optimization_section
        else:
            optimized_prompt = base_prompt
        
        # 5. Optimisations avancées selon le niveau
        if optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
            advanced_optimizations = await self._add_advanced_seo_optimizations(
                optimized_prompt, keywords, content_type
            )
            optimized_prompt += advanced_optimizations
        
        return optimized_prompt
    
    async def _add_advanced_seo_optimizations(
        self,
        prompt: str,
        keywords: List[SEOKeyword],
        content_type: ContentType
    ) -> str:
        """Ajout d'optimisations SEO avancées"""
        
        advanced_section = "\n\n🎯 Optimisations SEO Avancées:\n"
        
        # Schema markup
        schema_types = {
            ContentType.BLOG_POST: "Article",
            ContentType.PRODUCT_DESCRIPTION: "Product",
            ContentType.VIDEO_DESCRIPTION: "VideoObject",
            ContentType.LANDING_PAGE: "WebPage"
        }
        
        if content_type in schema_types:
            advanced_section += f"📊 Schema Markup: {schema_types[content_type]}\n"
        
        # Core Web Vitals
        advanced_section += "⚡ Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1\n"
        
        # Featured snippets optimization
        advanced_section += "🌟 Featured Snippets: Format questions/réponses, listes, tableaux\n"
        
        # Voice search optimization
        advanced_section += "🎤 Voice Search: Questions naturelles, langage conversationnel\n"
        
        # Semantic SEO
        semantic_keywords = []
        for keyword in keywords[:5]:
            if keyword.related_keywords:
                semantic_keywords.extend(keyword.related_keywords[:2])
        
        if semantic_keywords:
            advanced_section += f"🧠 SEO Sémantique: {', '.join(semantic_keywords)}\n"
        
        # E-A-T optimization
        advanced_section += "🏆 E-A-T: Expertise, Authority, Trustworthiness - Citer sources fiables\n"
        
        return advanced_section

    async def _calculate_seo_score(
        self,
        prompt: str,
        keywords: List[SEOKeyword],
        meta_tags: Dict[str, str]
    ) -> float:
        """Calcul du score SEO global"""
        
        scores = {
            'keyword_optimization': 0.0,
            'content_structure': 0.0,
            'meta_tags': 0.0,
            'readability': 0.0,
            'semantic_relevance': 0.0
        }
        
        # 1. Score optimisation mots-clés
        keyword_count = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword.keyword.lower() in prompt.lower():
                keyword_count += 1
        
        scores['keyword_optimization'] = keyword_count / total_keywords if total_keywords > 0 else 0
        
        # 2. Score structure du contenu
        has_title = bool(re.search(r'#|\btitle\b|\btitre\b', prompt, re.IGNORECASE))
        has_headers = bool(re.search(r'##|h2|h3|\bsection\b', prompt, re.IGNORECASE))
        has_structure = bool(re.search(r'structure|plan|organisation', prompt, re.IGNORECASE))
        
        structure_elements = sum([has_title, has_headers, has_structure])
        scores['content_structure'] = structure_elements / 3
        
        # 3. Score méta-tags
        required_meta = ['title', 'description']
        meta_score = sum(1 for tag in required_meta if tag in meta_tags and meta_tags[tag])
        scores['meta_tags'] = meta_score / len(required_meta)
        
        # 4. Score lisibilité
        sentences = re.split(r'[.!?]+', prompt)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Score basé sur longueur moyenne des phrases (optimal: 15-20 mots)
        if 15 <= avg_sentence_length <= 20:
            scores['readability'] = 1.0
        elif 10 <= avg_sentence_length < 15 or 20 < avg_sentence_length <= 25:
            scores['readability'] = 0.8
        else:
            scores['readability'] = 0.6
        
        # 5. Score pertinence sémantique
        semantic_terms = ['optimis', 'seo', 'recherche', 'audience', 'contenu', 'performan']
        semantic_count = sum(1 for term in semantic_terms if term in prompt.lower())
        scores['semantic_relevance'] = min(1.0, semantic_count / len(semantic_terms))
        
        # Calcul du score global pondéré
        weights = {
            'keyword_optimization': 0.3,
            'content_structure': 0.2,
            'meta_tags': 0.2,
            'readability': 0.15,
            'semantic_relevance': 0.15
        }
        
        global_score = sum(scores[key] * weights[key] for key in scores)
        
        return round(global_score, 3)

    async def _store_generation_result(
        self,
        result: SEOPromptResult,
        context: Optional[Dict[str, Any]]
    ):
        """Stockage du résultat avec métriques (DBA + DevOps)"""
        try:
            # Génération d'un ID unique
            result_id = str(uuid.uuid4())
            
            # Stockage en base de données
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO seo_prompt_results 
                    (id, optimized_prompt, keywords, seo_score, readability_score, 
                     meta_tags, optimization_suggestions, performance_predictions, 
                     context, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    result_id,
                    result.optimized_prompt,
                    json.dumps([kw.__dict__ for kw in result.keywords]),
                    result.seo_score,
                    result.readability_score,
                    json.dumps(result.meta_tags),
                    json.dumps(result.optimization_suggestions),
                    json.dumps(result.performance_predictions),
                    json.dumps(context or {}),
                    result.timestamp
                )
            
            # Cache Redis pour accès rapide
            cache_key = f"seo_prompt:{hashlib.md5(result.optimized_prompt.encode()).hexdigest()}"
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 heure
                json.dumps({
                    'seo_score': result.seo_score,
                    'readability_score': result.readability_score,
                    'keywords_count': len(result.keywords)
                })
            )
            
            logger.info(f"Résultat SEO stocké avec ID: {result_id}")
            
        except Exception as e:
            logger.error(f"Erreur stockage résultat SEO: {e}")

# Fonctions utilitaires et helpers
async def initialize_seo_database(db_pool: asyncpg.Pool):
    """Initialisation de la base de données SEO"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seo_prompt_results (
                id UUID PRIMARY KEY,
                optimized_prompt TEXT NOT NULL,
                keywords JSONB,
                seo_score DECIMAL(5,3),
                readability_score DECIMAL(5,3),
                meta_tags JSONB,
                optimization_suggestions JSONB,
                performance_predictions JSONB,
                context JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_seo_results_score ON seo_prompt_results(seo_score);
            CREATE INDEX IF NOT EXISTS idx_seo_results_created ON seo_prompt_results(created_at);
            CREATE INDEX IF NOT EXISTS idx_seo_results_keywords ON seo_prompt_results USING GIN(keywords);
            """
        )

# Factory pour création d'instances
class SEOPromptGeneratorFactory:
    """Factory pour création d'instances SEO Prompt Generator"""
    
    @staticmethod
    async def create(
        database_url: str,
        redis_url: str,
        **kwargs
    ) -> SEOPromptGenerator:
        """Création d'une instance configurée"""
        
        # Connection à la base de données
        db_pool = await asyncpg.create_pool(database_url)
        await initialize_seo_database(db_pool)
        
        # Connection Redis
        redis_client = await aioredis.from_url(redis_url)
        
        # Création de l'instance
        generator = SEOPromptGenerator(db_pool, redis_client)
        
        return generator

# Export des classes principales
__all__ = [
    'SEOPromptGenerator',
    'SEOPromptGeneratorFactory',
    'SEOKeyword',
    'SEOPromptResult',
    'SearchTrend',
    'ContentType',
    'OptimizationLevel',
    'SearchEngine'
]