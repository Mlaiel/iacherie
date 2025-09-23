"""🔍 SEO Optimization Storage - Enterprise Grade
============================================
Expert: SEO + ML ENGINEER + BACKEND SENIOR + IA PROMPT ENGINEER
Technologies: SEO Analytics + AI Content Optimization + Search Intelligence + SERP Tracking
Architecture: Level 2 - Storage Layer - Creator Economy
Date: 2025-01-14

Enterprise storage solution for SEO optimization with AI-driven content analysis,
search performance tracking, keyword intelligence and creator economy SEO features.
============================================
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
import re
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class SearchEngine(Enum):
    """Moteurs de recherche supportés"""
    GOOGLE = "google"
    BING = "bing"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"

class ContentType(Enum):
    """Types de contenu pour SEO"""
    ARTICLE = "article"
    VIDEO = "video"
    IMAGE = "image"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    PRODUCT = "product"

class SEOMetricType(Enum):
    """Types de métriques SEO"""
    RANKING_POSITION = "ranking_position"
    SEARCH_VOLUME = "search_volume"
    CLICK_THROUGH_RATE = "click_through_rate"
    ORGANIC_TRAFFIC = "organic_traffic"
    BACKLINKS = "backlinks"
    DOMAIN_AUTHORITY = "domain_authority"
    PAGE_AUTHORITY = "page_authority"
    ENGAGEMENT_RATE = "engagement_rate"

class OptimizationStatus(Enum):
    """États d'optimisation"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWING = "reviewing"

@dataclass
class SEOOptimizationConfig:
    """Configuration stockage optimisation SEO"""
    redis_url: str = "redis://localhost:6379"
    max_pool_size: int = 25
    keyword_ttl: int = 86400 * 30  # 30 jours
    ranking_ttl: int = 86400 * 7   # 7 jours
    content_ttl: int = 86400 * 90  # 90 jours
    enable_ai_optimization: bool = True
    enable_real_time_tracking: bool = True
    max_keywords_per_content: int = 50
    max_tracking_urls: int = 1000
    supported_languages: Set[str] = field(default_factory=lambda: {
        'en', 'fr', 'es', 'de', 'it', 'pt', 'ja', 'ko', 'zh', 'ar'
    })

@dataclass
class KeywordData:
    """Données mot-clé"""
    keyword: str
    search_volume: int = 0
    competition_score: float = 0.0
    difficulty_score: float = 0.0
    cpc_estimate: float = 0.0
    trend_data: List[float] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    search_intent: str = "informational"
    language: str = "en"
    geo_location: str = "global"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SEORankingData:
    """Données classement SEO"""
    content_id: str
    keyword: str
    search_engine: SearchEngine
    ranking_position: int = 0
    previous_position: int = 0
    ranking_url: str = ""
    featured_snippet: bool = False
    local_pack: bool = False
    image_pack: bool = False
    video_pack: bool = False
    serp_features: List[str] = field(default_factory=list)
    click_through_rate: float = 0.0
    impressions: int = 0
    clicks: int = 0
    tracked_date: datetime = field(default_factory=datetime.now)

@dataclass
class ContentSEOProfile:
    """Profil SEO contenu"""
    content_id: str
    creator_id: str
    title: str
    description: str
    content_type: ContentType
    target_keywords: List[str] = field(default_factory=list)
    meta_title: str = ""
    meta_description: str = ""
    canonical_url: str = ""
    schema_markup: Dict[str, Any] = field(default_factory=dict)
    alt_texts: List[str] = field(default_factory=list)
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    word_count: int = 0
    readability_score: float = 0.0
    seo_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    optimized_at: Optional[datetime] = None
    status: OptimizationStatus = OptimizationStatus.PENDING

@dataclass
class SEOAnalyticsReport:
    """Rapport analytics SEO"""
    creator_id: str
    period_start: datetime
    period_end: datetime
    total_keywords: int = 0
    avg_ranking_position: float = 0.0
    total_organic_traffic: int = 0
    total_impressions: int = 0
    total_clicks: int = 0
    avg_ctr: float = 0.0
    top_performing_keywords: List[Dict[str, Any]] = field(default_factory=list)
    ranking_improvements: List[Dict[str, Any]] = field(default_factory=list)
    content_performance: Dict[str, Any] = field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    optimization_impact: Dict[str, Any] = field(default_factory=dict)

class SEOOptimizationStorage:
    """Gestionnaire stockage optimisation SEO enterprise"""
    
    def __init__(self, config: SEOOptimizationConfig):
        self.config = config
        self.redis_pool = None
        self.keyword_cache = {}
        self.ranking_cache = {}
        self.content_profiles = {}
        self.optimization_queue = asyncio.Queue()
        
        # Métriques de performance
        self.metrics = {
            'total_keywords_tracked': 0,
            'total_content_optimized': 0,
            'avg_ranking_improvement': 0.0,
            'active_creators': 0,
            'optimization_success_rate': 0.0,
            'ai_suggestions_generated': 0
        }
        
        logger.info("SEOOptimizationStorage initialisé")
    
    async def initialize(self):
        """Initialisation connexions Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis non disponible - mode dégradé")
            return
        
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_pool_size,
                retry_on_timeout=True
            )
            
            # Test connexion
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                await r.ping()
            
            # Démarrage processus optimisation
            if self.config.enable_ai_optimization:
                asyncio.create_task(self._optimization_processor())
            
            if self.config.enable_real_time_tracking:
                asyncio.create_task(self._ranking_tracker())
            
            logger.info("Connexion Redis établie pour l'optimisation SEO")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Redis SEO: {e}")
            self.redis_pool = None
    
    async def create_content_seo_profile(self, creator_id: str, 
                                        content_data: Dict[str, Any]) -> str:
        """Création profil SEO contenu"""
        try:
            content_id = content_data.get('content_id', str(uuid.uuid4()))
            
            # Création profil SEO
            profile = ContentSEOProfile(
                content_id=content_id,
                creator_id=creator_id,
                title=content_data.get('title', ''),
                description=content_data.get('description', ''),
                content_type=ContentType(content_data.get('content_type', ContentType.ARTICLE.value)),
                target_keywords=content_data.get('keywords', []),
                meta_title=content_data.get('meta_title', ''),
                meta_description=content_data.get('meta_description', ''),
                canonical_url=content_data.get('url', '')
            )
            
            # Analyse automatique contenu
            if 'content_text' in content_data:
                await self._analyze_content_seo(profile, content_data['content_text'])
            
            # Génération suggestions IA
            if self.config.enable_ai_optimization:
                await self._generate_ai_suggestions(profile)
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_content_profile_to_redis(profile)
            
            # Cache local
            self.content_profiles[content_id] = profile
            
            # Ajout à la queue d'optimisation
            await self.optimization_queue.put({
                'action': 'optimize_content',
                'content_id': content_id,
                'creator_id': creator_id
            })
            
            # Mise à jour métriques
            self.metrics['total_content_optimized'] += 1
            
            logger.info(f"Profil SEO créé: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Erreur création profil SEO: {e}")
            raise
    
    async def track_keyword_rankings(self, content_id: str, keywords: List[str],
                                   search_engines: List[SearchEngine] = None) -> bool:
        """Suivi classements mots-clés"""
        try:
            if not search_engines:
                search_engines = [SearchEngine.GOOGLE, SearchEngine.BING]
            
            tracking_tasks = []
            
            for keyword in keywords[:self.config.max_keywords_per_content]:
                for search_engine in search_engines:
                    task = self._track_single_keyword(content_id, keyword, search_engine)
                    tracking_tasks.append(task)
            
            # Exécution parallèle
            results = await asyncio.gather(*tracking_tasks, return_exceptions=True)
            
            # Comptage succès
            successful_tracks = sum(1 for result in results if isinstance(result, bool) and result)
            
            logger.info(f"Suivi classements: {successful_tracks}/{len(tracking_tasks)} réussis")
            return successful_tracks > 0
            
        except Exception as e:
            logger.error(f"Erreur suivi classements {content_id}: {e}")
            return False
    
    async def get_keyword_research(self, seed_keywords: List[str], 
                                  language: str = "en") -> Dict[str, Any]:
        """Recherche mots-clés avec données enrichies"""
        try:
            keyword_research = {
                'seed_keywords': seed_keywords,
                'expanded_keywords': [],
                'keyword_clusters': {},
                'content_gaps': [],
                'competition_analysis': {},
                'opportunity_score': 0.0
            }
            
            expanded_keywords = []
            
            for seed_keyword in seed_keywords:
                # Récupération données mot-clé
                keyword_data = await self._get_keyword_data(seed_keyword, language)
                
                if keyword_data:
                    expanded_keywords.append({
                        'keyword': keyword_data.keyword,
                        'search_volume': keyword_data.search_volume,
                        'difficulty': keyword_data.difficulty_score,
                        'competition': keyword_data.competition_score,
                        'cpc': keyword_data.cpc_estimate,
                        'intent': keyword_data.search_intent
                    })
                    
                    # Ajout mots-clés connexes
                    for related in keyword_data.related_keywords[:5]:
                        related_data = await self._get_keyword_data(related, language)
                        if related_data:
                            expanded_keywords.append({
                                'keyword': related_data.keyword,
                                'search_volume': related_data.search_volume,
                                'difficulty': related_data.difficulty_score,
                                'competition': related_data.competition_score,
                                'cpc': related_data.cpc_estimate,
                                'intent': related_data.search_intent,
                                'source': f"related_to_{seed_keyword}"
                            })
            
            # Tri par potentiel (volume/difficulté)
            expanded_keywords.sort(key=lambda k: k['search_volume'] / max(k['difficulty'], 0.1), reverse=True)
            keyword_research['expanded_keywords'] = expanded_keywords[:50]
            
            # Clustering par intention de recherche
            keyword_research['keyword_clusters'] = await self._cluster_keywords_by_intent(
                expanded_keywords
            )
            
            # Analyse des gaps de contenu
            keyword_research['content_gaps'] = await self._identify_content_gaps(
                expanded_keywords
            )
            
            # Score d'opportunité global
            keyword_research['opportunity_score'] = self._calculate_opportunity_score(
                expanded_keywords
            )
            
            return keyword_research
            
        except Exception as e:
            logger.error(f"Erreur recherche mots-clés: {e}")
            return {'error': str(e)}
    
    async def optimize_content_for_seo(self, content_id: str, 
                                      optimization_targets: Dict[str, Any]) -> Dict[str, Any]:
        """Optimisation contenu pour SEO"""
        try:
            # Récupération profil actuel
            profile = await self._get_content_profile(content_id)
            if not profile:
                return {'success': False, 'error': 'Profil introuvable'}
            
            optimization_results = {
                'content_id': content_id,
                'optimizations_applied': [],
                'seo_score_before': profile.seo_score,
                'seo_score_after': 0.0,
                'estimated_impact': {},
                'recommendations': []
            }
            
            # Application optimisations demandées
            if 'target_keywords' in optimization_targets:
                await self._optimize_keywords(profile, optimization_targets['target_keywords'])
                optimization_results['optimizations_applied'].append('keyword_optimization')
            
            if 'meta_tags' in optimization_targets:
                await self._optimize_meta_tags(profile, optimization_targets['meta_tags'])
                optimization_results['optimizations_applied'].append('meta_tag_optimization')
            
            if 'content_structure' in optimization_targets:
                await self._optimize_content_structure(profile)
                optimization_results['optimizations_applied'].append('content_structure')
            
            if 'internal_linking' in optimization_targets:
                await self._optimize_internal_linking(profile, optimization_targets.get('related_content', []))
                optimization_results['optimizations_applied'].append('internal_linking')
            
            # Recalcul score SEO
            profile.seo_score = await self._calculate_seo_score(profile)
            profile.optimized_at = datetime.now()
            profile.status = OptimizationStatus.COMPLETED
            
            optimization_results['seo_score_after'] = profile.seo_score
            
            # Estimation impact
            optimization_results['estimated_impact'] = await self._estimate_optimization_impact(
                profile, optimization_results['optimizations_applied']
            )
            
            # Recommandations additionnelles
            optimization_results['recommendations'] = await self._generate_additional_recommendations(
                profile
            )
            
            # Sauvegarde profil mis à jour
            if self.redis_pool:
                await self._store_content_profile_to_redis(profile)
            
            self.content_profiles[content_id] = profile
            
            logger.info(f"Contenu optimisé: {content_id} (score: {profile.seo_score:.2f})")
            return {'success': True, **optimization_results}
            
        except Exception as e:
            logger.error(f"Erreur optimisation contenu {content_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_seo_analytics(self, creator_id: str, period_days: int = 30) -> SEOAnalyticsReport:
        """Analytics SEO pour créateur"""
        try:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            report = SEOAnalyticsReport(
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end
            )
            
            # Récupération données de classement
            ranking_data = await self._get_creator_ranking_data(creator_id, period_start, period_end)
            
            if ranking_data:
                # Métriques globales
                report.total_keywords = len(set(r.keyword for r in ranking_data))
                report.avg_ranking_position = sum(r.ranking_position for r in ranking_data) / len(ranking_data)
                report.total_impressions = sum(r.impressions for r in ranking_data)
                report.total_clicks = sum(r.clicks for r in ranking_data)
                
                if report.total_impressions > 0:
                    report.avg_ctr = report.total_clicks / report.total_impressions
                
                # Top keywords performants
                keyword_performance = defaultdict(lambda: {'clicks': 0, 'impressions': 0, 'position': 0, 'count': 0})
                
                for ranking in ranking_data:
                    kp = keyword_performance[ranking.keyword]
                    kp['clicks'] += ranking.clicks
                    kp['impressions'] += ranking.impressions
                    kp['position'] += ranking.ranking_position
                    kp['count'] += 1
                
                # Calcul moyennes et tri
                for keyword, data in keyword_performance.items():
                    data['avg_position'] = data['position'] / data['count']
                    data['ctr'] = data['clicks'] / max(data['impressions'], 1)
                
                report.top_performing_keywords = sorted(
                    [
                        {
                            'keyword': k,
                            'clicks': data['clicks'],
                            'impressions': data['impressions'],
                            'avg_position': data['avg_position'],
                            'ctr': data['ctr']
                        }
                        for k, data in keyword_performance.items()
                    ],
                    key=lambda x: x['clicks'],
                    reverse=True
                )[:20]
                
                # Améliorations de classement
                report.ranking_improvements = await self._calculate_ranking_improvements(
                    creator_id, ranking_data
                )
            
            # Performance du contenu
            report.content_performance = await self._analyze_content_performance(
                creator_id, period_start, period_end
            )
            
            # Analyse concurrentielle
            report.competitor_analysis = await self._generate_competitor_analysis(
                creator_id, report.top_performing_keywords
            )
            
            # Impact des optimisations
            report.optimization_impact = await self._measure_optimization_impact(
                creator_id, period_start, period_end
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur analytics SEO {creator_id}: {e}")
            return SEOAnalyticsReport(creator_id=creator_id, period_start=period_start, period_end=period_end)
    
    async def _analyze_content_seo(self, profile: ContentSEOProfile, content_text: str):
        """Analyse SEO automatique du contenu"""
        # Comptage mots
        profile.word_count = len(content_text.split())
        
        # Score de lisibilité simplifié (Flesch Reading Ease approximatif)
        sentences = len(re.split(r'[.!?]+', content_text))
        words = profile.word_count
        syllables = sum(self._count_syllables(word) for word in content_text.split())
        
        if sentences > 0 and words > 0:
            profile.readability_score = 206.835 - (1.015 * words / sentences) - (84.6 * syllables / words)
            profile.readability_score = max(0, min(100, profile.readability_score))
        
        # Extraction mots-clés automatique (TF-IDF simplifié)
        if not profile.target_keywords:
            profile.target_keywords = self._extract_keywords_from_text(content_text)[:10]
    
    def _count_syllables(self, word: str) -> int:
        """Comptage syllables approximatif"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    syllable_count += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        # Mot doit avoir au moins 1 syllabe
        return max(1, syllable_count)
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extraction mots-clés basique du texte"""
        # Nettoyage et tokenisation
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Mots vides basiques
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Comptage fréquences
        word_freq = defaultdict(int)
        for word in words:
            if word not in stop_words:
                word_freq[word] += 1
        
        # Tri par fréquence
        return [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)]
    
    async def _generate_ai_suggestions(self, profile: ContentSEOProfile):
        """Génération suggestions IA pour optimisation"""
        suggestions = []
        
        # Suggestions basées sur le type de contenu
        if profile.content_type == ContentType.ARTICLE:
            suggestions.extend([
                "Ajouter des sous-titres H2/H3 pour structurer le contenu",
                "Inclure des mots-clés dans les 100 premiers mots",
                "Optimiser la méta-description pour améliorer le CTR"
            ])
        elif profile.content_type == ContentType.VIDEO:
            suggestions.extend([
                "Ajouter des timestamps dans la description",
                "Utiliser des mots-clés dans le titre et la description",
                "Créer des miniatures attrayantes avec texte"
            ])
        
        # Suggestions basées sur le score de lisibilité
        if profile.readability_score < 50:
            suggestions.append("Simplifier les phrases pour améliorer la lisibilité")
        
        # Suggestions basées sur le nombre de mots
        if profile.word_count < 300:
            suggestions.append("Développer le contenu (minimum 300 mots recommandé)")
        
        profile.optimization_suggestions = suggestions
        self.metrics['ai_suggestions_generated'] += len(suggestions)
    
    async def _track_single_keyword(self, content_id: str, keyword: str, 
                                   search_engine: SearchEngine) -> bool:
        """Suivi classement mot-clé unique"""
        try:
            # Simulation appel API moteur de recherche (à remplacer par vraie API)
            ranking_position = await self._simulate_ranking_check(keyword, search_engine)
            
            # Récupération données précédentes
            previous_ranking = await self._get_previous_ranking(content_id, keyword, search_engine)
            previous_position = previous_ranking.ranking_position if previous_ranking else 0
            
            # Création nouvelle entrée de classement
            ranking_data = SEORankingData(
                content_id=content_id,
                keyword=keyword,
                search_engine=search_engine,
                ranking_position=ranking_position,
                previous_position=previous_position,
                ranking_url=f"https://example.com/content/{content_id}",  # URL réelle à adapter
                clicks=self._simulate_clicks(ranking_position),
                impressions=self._simulate_impressions(ranking_position),
                click_through_rate=self._calculate_ctr(ranking_position)
            )
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_ranking_data_to_redis(ranking_data)
            
            # Cache local
            cache_key = f"{content_id}:{keyword}:{search_engine.value}"
            self.ranking_cache[cache_key] = ranking_data
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur suivi mot-clé {keyword}: {e}")
            return False
    
    async def _simulate_ranking_check(self, keyword: str, search_engine: SearchEngine) -> int:
        """Simulation vérification classement (à remplacer par vraie API)"""
        # Simulation basée sur hash du mot-clé pour cohérence
        hash_value = hash(keyword + search_engine.value) % 100
        
        if hash_value < 10:
            return hash_value + 1  # Top 10
        elif hash_value < 30:
            return hash_value + 20  # Positions 20-50
        else:
            return hash_value + 50  # Positions 50-100
    
    def _simulate_clicks(self, position: int) -> int:
        """Simulation clics basée sur position"""
        if position <= 3:
            return 100 + (4 - position) * 50
        elif position <= 10:
            return 50 - (position - 3) * 5
        else:
            return max(1, 20 - position)
    
    def _simulate_impressions(self, position: int) -> int:
        """Simulation impressions basée sur position"""
        if position <= 10:
            return 1000 - position * 50
        else:
            return max(100, 500 - position * 10)
    
    def _calculate_ctr(self, position: int) -> float:
        """Calcul CTR basé sur position"""
        # CTR moyens par position (données approximatives)
        ctr_by_position = {
            1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.07,
            6: 0.05, 7: 0.04, 8: 0.03, 9: 0.025, 10: 0.02
        }
        
        return ctr_by_position.get(position, max(0.001, 0.02 - position * 0.001))
    
    async def _get_keyword_data(self, keyword: str, language: str) -> Optional[KeywordData]:
        """Récupération données mot-clé"""
        # Cache local d'abord
        cache_key = f"{keyword}:{language}"
        if cache_key in self.keyword_cache:
            return self.keyword_cache[cache_key]
        
        # Simulation données mot-clé (à remplacer par vraie API)
        keyword_data = KeywordData(
            keyword=keyword,
            search_volume=max(100, hash(keyword) % 10000),
            competition_score=min(1.0, (hash(keyword) % 100) / 100),
            difficulty_score=min(1.0, (hash(keyword + "diff") % 100) / 100),
            cpc_estimate=max(0.1, (hash(keyword + "cpc") % 500) / 100),
            related_keywords=self._generate_related_keywords(keyword),
            search_intent=self._determine_search_intent(keyword),
            language=language
        )
        
        # Cache et retour
        self.keyword_cache[cache_key] = keyword_data
        
        # Stockage Redis si disponible
        if self.redis_pool:
            await self._store_keyword_data_to_redis(keyword_data)
        
        return keyword_data
    
    def _generate_related_keywords(self, keyword: str) -> List[str]:
        """Génération mots-clés connexes"""
        base_words = keyword.split()
        related = []
        
        # Ajout variations simples
        for word in base_words:
            related.extend([
                f"{keyword} guide",
                f"{keyword} tutorial",
                f"{keyword} tips",
                f"best {keyword}",
                f"{keyword} 2024",
                f"how to {keyword}",
                f"{keyword} review"
            ])
        
        return list(set(related))[:10]
    
    def _determine_search_intent(self, keyword: str) -> str:
        """Détermination intention de recherche"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ['buy', 'price', 'cost', 'cheap', 'discount']):
            return 'commercial'
        elif any(word in keyword_lower for word in ['how', 'what', 'why', 'guide', 'tutorial']):
            return 'informational'
        elif any(word in keyword_lower for word in ['best', 'top', 'review', 'compare']):
            return 'commercial_investigation'
        else:
            return 'navigational'
    
    async def _cluster_keywords_by_intent(self, keywords: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Clustering mots-clés par intention"""
        clusters = defaultdict(list)
        
        for keyword in keywords:
            intent = keyword.get('intent', 'informational')
            clusters[intent].append(keyword)
        
        return dict(clusters)
    
    async def _identify_content_gaps(self, keywords: List[Dict[str, Any]]) -> List[str]:
        """Identification gaps de contenu"""
        gaps = []
        
        # Analyse par intention de recherche
        intent_counts = defaultdict(int)
        for keyword in keywords:
            intent_counts[keyword.get('intent', 'informational')] += 1
        
        # Identification intentions sous-représentées
        if intent_counts['commercial'] < intent_counts['informational'] * 0.3:
            gaps.append("Opportunité de créer du contenu commercial/produit")
        
        if intent_counts['commercial_investigation'] < len(keywords) * 0.2:
            gaps.append("Manque de contenu comparatif/évaluatif")
        
        # Analyse par volume de recherche
        high_volume_keywords = [k for k in keywords if k.get('search_volume', 0) > 1000]
        if len(high_volume_keywords) < len(keywords) * 0.3:
            gaps.append("Opportunité de cibler des mots-clés à plus fort volume")
        
        return gaps
    
    def _calculate_opportunity_score(self, keywords: List[Dict[str, Any]]) -> float:
        """Calcul score d'opportunité global"""
        if not keywords:
            return 0.0
        
        total_score = 0
        for keyword in keywords:
            volume = keyword.get('search_volume', 0)
            difficulty = keyword.get('difficulty', 1.0)
            
            # Score = volume / difficulté (normalisé)
            keyword_score = volume / max(difficulty * 1000, 1)
            total_score += keyword_score
        
        return min(1.0, total_score / len(keywords) / 10)  # Normalisation
    
    async def _optimize_keywords(self, profile: ContentSEOProfile, target_keywords: List[str]):
        """Optimisation mots-clés"""
        profile.target_keywords = target_keywords
        
        # Mise à jour méta-titre si vide
        if not profile.meta_title and target_keywords:
            primary_keyword = target_keywords[0]
            profile.meta_title = f"{profile.title} - {primary_keyword}"
        
        # Mise à jour méta-description si vide
        if not profile.meta_description and target_keywords:
            profile.meta_description = f"Découvrez tout sur {target_keywords[0]}. {profile.description[:100]}..."
    
    async def _optimize_meta_tags(self, profile: ContentSEOProfile, meta_data: Dict[str, str]):
        """Optimisation balises meta"""
        if 'title' in meta_data:
            profile.meta_title = meta_data['title'][:60]  # Limitation Google
        
        if 'description' in meta_data:
            profile.meta_description = meta_data['description'][:160]  # Limitation Google
        
        if 'canonical' in meta_data:
            profile.canonical_url = meta_data['canonical']
    
    async def _optimize_content_structure(self, profile: ContentSEOProfile):
        """Optimisation structure contenu"""
        suggestions = []
        
        # Vérification structure basique
        if profile.word_count < 300:
            suggestions.append("Augmenter le contenu à minimum 300 mots")
        
        if not profile.meta_title:
            suggestions.append("Ajouter un méta-titre optimisé")
        
        if not profile.meta_description:
            suggestions.append("Ajouter une méta-description attrayante")
        
        profile.optimization_suggestions.extend(suggestions)
    
    async def _optimize_internal_linking(self, profile: ContentSEOProfile, related_content: List[str]):
        """Optimisation liens internes"""
        # Ajout liens vers contenu connexe
        profile.internal_links.extend(related_content)
        
        # Limitation nombre de liens
        profile.internal_links = profile.internal_links[:10]
    
    async def _calculate_seo_score(self, profile: ContentSEOProfile) -> float:
        """Calcul score SEO composite"""
        score = 0.0
        max_score = 100.0
        
        # Score titre (20 points)
        if profile.meta_title:
            title_score = min(20, len(profile.meta_title) / 3)  # Score basé sur longueur
            if any(keyword.lower() in profile.meta_title.lower() for keyword in profile.target_keywords):
                title_score *= 1.5  # Bonus mot-clé
            score += min(20, title_score)
        
        # Score description (15 points)
        if profile.meta_description:
            desc_score = min(15, len(profile.meta_description) / 8)
            if any(keyword.lower() in profile.meta_description.lower() for keyword in profile.target_keywords):
                desc_score *= 1.3
            score += min(15, desc_score)
        
        # Score contenu (25 points)
        if profile.word_count >= 300:
            content_score = min(25, profile.word_count / 20)
            score += min(25, content_score)
        
        # Score lisibilité (15 points)
        if profile.readability_score > 0:
            readability_score = profile.readability_score / 100 * 15
            score += readability_score
        
        # Score mots-clés (15 points)
        if profile.target_keywords:
            keyword_score = min(15, len(profile.target_keywords) * 2)
            score += keyword_score
        
        # Score liens (10 points)
        link_score = min(10, len(profile.internal_links) * 2)
        score += link_score
        
        return min(100, score)
    
    async def _estimate_optimization_impact(self, profile: ContentSEOProfile, 
                                          optimizations: List[str]) -> Dict[str, Any]:
        """Estimation impact optimisations"""
        impact = {
            'estimated_ranking_improvement': 0,
            'estimated_traffic_increase': 0.0,
            'confidence_level': 0.0
        }
        
        # Impact estimé par type d'optimisation
        optimization_impacts = {
            'keyword_optimization': {'ranking': 5, 'traffic': 0.15},
            'meta_tag_optimization': {'ranking': 3, 'traffic': 0.10},
            'content_structure': {'ranking': 2, 'traffic': 0.05},
            'internal_linking': {'ranking': 1, 'traffic': 0.03}
        }
        
        for optimization in optimizations:
            if optimization in optimization_impacts:
                impact['estimated_ranking_improvement'] += optimization_impacts[optimization]['ranking']
                impact['estimated_traffic_increase'] += optimization_impacts[optimization]['traffic']
        
        # Niveau de confiance basé sur score SEO
        impact['confidence_level'] = min(1.0, profile.seo_score / 100)
        
        return impact
    
    async def _generate_additional_recommendations(self, profile: ContentSEOProfile) -> List[str]:
        """Génération recommandations additionnelles"""
        recommendations = []
        
        if profile.seo_score < 70:
            recommendations.append("Améliorer le score SEO global pour une meilleure visibilité")
        
        if len(profile.target_keywords) < 3:
            recommendations.append("Ajouter plus de mots-clés cibles pour élargir la portée")
        
        if not profile.canonical_url:
            recommendations.append("Définir une URL canonique pour éviter le contenu dupliqué")
        
        if profile.readability_score < 60:
            recommendations.append("Améliorer la lisibilité pour une meilleure expérience utilisateur")
        
        return recommendations
    
    async def _store_content_profile_to_redis(self, profile: ContentSEOProfile):
        """Stockage profil contenu Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            profile_key = f"seo:content:{profile.content_id}"
            profile_data = {
                'content_id': profile.content_id,
                'creator_id': profile.creator_id,
                'title': profile.title,
                'description': profile.description,
                'content_type': profile.content_type.value,
                'target_keywords': profile.target_keywords,
                'meta_title': profile.meta_title,
                'meta_description': profile.meta_description,
                'canonical_url': profile.canonical_url,
                'schema_markup': profile.schema_markup,
                'alt_texts': profile.alt_texts,
                'internal_links': profile.internal_links,
                'external_links': profile.external_links,
                'word_count': profile.word_count,
                'readability_score': profile.readability_score,
                'seo_score': profile.seo_score,
                'optimization_suggestions': profile.optimization_suggestions,
                'ai_insights': profile.ai_insights,
                'created_at': profile.created_at.isoformat(),
                'optimized_at': profile.optimized_at.isoformat() if profile.optimized_at else None,
                'status': profile.status.value
            }
            
            await r.setex(profile_key, self.config.content_ttl, json.dumps(profile_data))
            
            # Index par créateur
            creator_content_key = f"seo:creator:{profile.creator_id}:content"
            await r.sadd(creator_content_key, profile.content_id)
    
    async def _store_ranking_data_to_redis(self, ranking: SEORankingData):
        """Stockage données classement Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            ranking_key = f"seo:ranking:{ranking.content_id}:{ranking.keyword}:{ranking.search_engine.value}"
            ranking_data = {
                'content_id': ranking.content_id,
                'keyword': ranking.keyword,
                'search_engine': ranking.search_engine.value,
                'ranking_position': ranking.ranking_position,
                'previous_position': ranking.previous_position,
                'ranking_url': ranking.ranking_url,
                'featured_snippet': ranking.featured_snippet,
                'local_pack': ranking.local_pack,
                'image_pack': ranking.image_pack,
                'video_pack': ranking.video_pack,
                'serp_features': ranking.serp_features,
                'click_through_rate': ranking.click_through_rate,
                'impressions': ranking.impressions,
                'clicks': ranking.clicks,
                'tracked_date': ranking.tracked_date.isoformat()
            }
            
            await r.setex(ranking_key, self.config.ranking_ttl, json.dumps(ranking_data))
            
            # Index temporel pour analytics
            timeline_key = f"seo:timeline:{ranking.content_id}"
            await r.zadd(timeline_key, {ranking_key: ranking.tracked_date.timestamp()})
    
    async def _store_keyword_data_to_redis(self, keyword_data: KeywordData):
        """Stockage données mot-clé Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            keyword_key = f"seo:keyword:{keyword_data.keyword}:{keyword_data.language}"
            data = {
                'keyword': keyword_data.keyword,
                'search_volume': keyword_data.search_volume,
                'competition_score': keyword_data.competition_score,
                'difficulty_score': keyword_data.difficulty_score,
                'cpc_estimate': keyword_data.cpc_estimate,
                'trend_data': keyword_data.trend_data,
                'related_keywords': keyword_data.related_keywords,
                'search_intent': keyword_data.search_intent,
                'language': keyword_data.language,
                'geo_location': keyword_data.geo_location,
                'last_updated': keyword_data.last_updated.isoformat()
            }
            
            await r.setex(keyword_key, self.config.keyword_ttl, json.dumps(data))
    
    async def _get_content_profile(self, content_id: str) -> Optional[ContentSEOProfile]:
        """Récupération profil contenu"""
        # Cache local d'abord
        if content_id in self.content_profiles:
            return self.content_profiles[content_id]
        
        # Redis ensuite
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            profile_key = f"seo:content:{content_id}"
            profile_json = await r.get(profile_key)
            
            if not profile_json:
                return None
            
            data = json.loads(profile_json)
            
            profile = ContentSEOProfile(
                content_id=data['content_id'],
                creator_id=data['creator_id'],
                title=data['title'],
                description=data['description'],
                content_type=ContentType(data['content_type']),
                target_keywords=data['target_keywords'],
                meta_title=data['meta_title'],
                meta_description=data['meta_description'],
                canonical_url=data['canonical_url'],
                schema_markup=data['schema_markup'],
                alt_texts=data['alt_texts'],
                internal_links=data['internal_links'],
                external_links=data['external_links'],
                word_count=data['word_count'],
                readability_score=data['readability_score'],
                seo_score=data['seo_score'],
                optimization_suggestions=data['optimization_suggestions'],
                ai_insights=data['ai_insights'],
                created_at=datetime.fromisoformat(data['created_at']),
                optimized_at=datetime.fromisoformat(data['optimized_at']) if data['optimized_at'] else None,
                status=OptimizationStatus(data['status'])
            )
            
            # Mise en cache
            self.content_profiles[content_id] = profile
            return profile
    
    async def _get_previous_ranking(self, content_id: str, keyword: str, 
                                   search_engine: SearchEngine) -> Optional[SEORankingData]:
        """Récupération classement précédent"""
        cache_key = f"{content_id}:{keyword}:{search_engine.value}"
        return self.ranking_cache.get(cache_key)
    
    async def _get_creator_ranking_data(self, creator_id: str, start_date: datetime, 
                                       end_date: datetime) -> List[SEORankingData]:
        """Récupération données classement créateur"""
        ranking_data = []
        
        # Récupération contenus du créateur
        creator_content = await self._get_creator_content_ids(creator_id)
        
        for content_id in creator_content:
            # Récupération rankings pour ce contenu
            content_rankings = await self._get_content_rankings(content_id, start_date, end_date)
            ranking_data.extend(content_rankings)
        
        return ranking_data
    
    async def _get_creator_content_ids(self, creator_id: str) -> List[str]:
        """Récupération IDs contenu créateur"""
        if not self.redis_pool:
            return []
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            creator_content_key = f"seo:creator:{creator_id}:content"
            content_ids = await r.smembers(creator_content_key)
            return list(content_ids)
    
    async def _get_content_rankings(self, content_id: str, start_date: datetime, 
                                   end_date: datetime) -> List[SEORankingData]:
        """Récupération classements contenu"""
        rankings = []
        
        if not self.redis_pool:
            return rankings
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            timeline_key = f"seo:timeline:{content_id}"
            
            # Récupération clés dans la plage temporelle
            ranking_keys = await r.zrangebyscore(
                timeline_key,
                start_date.timestamp(),
                end_date.timestamp()
            )
            
            for ranking_key in ranking_keys:
                ranking_json = await r.get(ranking_key)
                if ranking_json:
                    data = json.loads(ranking_json)
                    ranking = SEORankingData(
                        content_id=data['content_id'],
                        keyword=data['keyword'],
                        search_engine=SearchEngine(data['search_engine']),
                        ranking_position=data['ranking_position'],
                        previous_position=data['previous_position'],
                        ranking_url=data['ranking_url'],
                        featured_snippet=data['featured_snippet'],
                        local_pack=data['local_pack'],
                        image_pack=data['image_pack'],
                        video_pack=data['video_pack'],
                        serp_features=data['serp_features'],
                        click_through_rate=data['click_through_rate'],
                        impressions=data['impressions'],
                        clicks=data['clicks'],
                        tracked_date=datetime.fromisoformat(data['tracked_date'])
                    )
                    rankings.append(ranking)
        
        return rankings
    
    async def _calculate_ranking_improvements(self, creator_id: str, 
                                            ranking_data: List[SEORankingData]) -> List[Dict[str, Any]]:
        """Calcul améliorations classement"""
        improvements = []
        
        # Groupement par mot-clé
        keyword_rankings = defaultdict(list)
        for ranking in ranking_data:
            keyword_rankings[ranking.keyword].append(ranking)
        
        for keyword, rankings in keyword_rankings.items():
            if len(rankings) >= 2:
                # Tri par date
                rankings.sort(key=lambda r: r.tracked_date)
                latest = rankings[-1]
                previous = rankings[-2]
                
                if latest.ranking_position < previous.ranking_position:  # Amélioration
                    improvement = previous.ranking_position - latest.ranking_position
                    improvements.append({
                        'keyword': keyword,
                        'previous_position': previous.ranking_position,
                        'current_position': latest.ranking_position,
                        'improvement': improvement,
                        'search_engine': latest.search_engine.value
                    })
        
        return sorted(improvements, key=lambda x: x['improvement'], reverse=True)
    
    async def _analyze_content_performance(self, creator_id: str, start_date: datetime, 
                                         end_date: datetime) -> Dict[str, Any]:
        """Analyse performance contenu"""
        # Récupération profils contenu créateur
        content_ids = await self._get_creator_content_ids(creator_id)
        
        performance = {
            'total_content': len(content_ids),
            'avg_seo_score': 0.0,
            'top_performing_content': [],
            'optimization_completion_rate': 0.0
        }
        
        if content_ids:
            seo_scores = []
            optimized_count = 0
            content_performance = []
            
            for content_id in content_ids:
                profile = await self._get_content_profile(content_id)
                if profile:
                    seo_scores.append(profile.seo_score)
                    if profile.status == OptimizationStatus.COMPLETED:
                        optimized_count += 1
                    
                    content_performance.append({
                        'content_id': content_id,
                        'title': profile.title,
                        'seo_score': profile.seo_score,
                        'target_keywords': len(profile.target_keywords)
                    })
            
            if seo_scores:
                performance['avg_seo_score'] = sum(seo_scores) / len(seo_scores)
            
            performance['optimization_completion_rate'] = optimized_count / len(content_ids)
            performance['top_performing_content'] = sorted(
                content_performance, key=lambda x: x['seo_score'], reverse=True
            )[:10]
        
        return performance
    
    async def _generate_competitor_analysis(self, creator_id: str, 
                                          top_keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génération analyse concurrentielle"""
        # Placeholder pour analyse concurrentielle
        return {
            'competitor_keywords_overlap': 0.65,
            'market_share_estimate': 0.15,
            'competitive_advantage_areas': [
                'Long-tail keywords',
                'Video content optimization',
                'Mobile-first optimization'
            ],
            'opportunities': [
                'Target underutilized high-volume keywords',
                'Improve content depth and quality',
                'Enhance technical SEO'
            ]
        }
    
    async def _measure_optimization_impact(self, creator_id: str, start_date: datetime, 
                                         end_date: datetime) -> Dict[str, Any]:
        """Mesure impact optimisations"""
        # Placeholder pour mesure d'impact
        return {
            'avg_ranking_improvement': 8.5,
            'traffic_increase_percentage': 25.3,
            'click_through_rate_improvement': 0.08,
            'optimizations_with_positive_impact': 0.82
        }
    
    async def _optimization_processor(self):
        """Processeur optimisations asynchrone"""
        while True:
            try:
                optimization_task = await self.optimization_queue.get()
                
                if optimization_task['action'] == 'optimize_content':
                    await self._process_content_optimization(optimization_task)
                
            except Exception as e:
                logger.error(f"Erreur processeur optimisation: {e}")
                await asyncio.sleep(1)
    
    async def _process_content_optimization(self, task: Dict[str, Any]):
        """Traitement optimisation contenu"""
        content_id = task['content_id']
        
        # Récupération profil
        profile = await self._get_content_profile(content_id)
        if not profile:
            return
        
        # Optimisations automatiques
        if profile.status == OptimizationStatus.PENDING:
            profile.status = OptimizationStatus.ANALYZING
            
            # Génération suggestions additionnelles
            await self._generate_ai_suggestions(profile)
            
            # Calcul score SEO
            profile.seo_score = await self._calculate_seo_score(profile)
            
            profile.status = OptimizationStatus.COMPLETED
            profile.optimized_at = datetime.now()
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_content_profile_to_redis(profile)
            
            self.content_profiles[content_id] = profile
    
    async def _ranking_tracker(self):
        """Traqueur classements temps réel"""
        while True:
            try:
                await asyncio.sleep(3600)  # Toutes les heures
                
                # Récupération contenus à tracker
                content_to_track = await self._get_content_for_tracking()
                
                for content_id, keywords in content_to_track.items():
                    await self.track_keyword_rankings(
                        content_id, 
                        keywords, 
                        [SearchEngine.GOOGLE, SearchEngine.BING]
                    )
                
            except Exception as e:
                logger.error(f"Erreur traqueur classements: {e}")
                await asyncio.sleep(3600)
    
    async def _get_content_for_tracking(self) -> Dict[str, List[str]]:
        """Récupération contenu à tracker"""
        content_to_track = {}
        
        # Récupération échantillon de contenus avec mots-clés
        for content_id, profile in list(self.content_profiles.items())[:10]:
            if profile.target_keywords:
                content_to_track[content_id] = profile.target_keywords[:5]
        
        return content_to_track
    
    async def get_seo_statistics(self) -> Dict[str, Any]:
        """Statistiques SEO globales"""
        try:
            stats = self.metrics.copy()
            
            if self.redis_pool:
                async with redis.Redis(connection_pool=self.redis_pool) as r:
                    # Comptage créateurs actifs
                    creator_keys = await r.keys("seo:creator:*:content")
                    stats['active_creators'] = len(creator_keys)
                    
                    # Comptage total contenus
                    content_keys = await r.keys("seo:content:*")
                    stats['total_content_profiles'] = len(content_keys)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques SEO: {e}")
            return self.metrics

# Factory function
def create_seo_optimization_storage(
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> SEOOptimizationStorage:
    """Factory pour création stockage optimisation SEO"""
    config = SEOOptimizationConfig(redis_url=redis_url, **kwargs)
    return SEOOptimizationStorage(config)

# Export classes principales
__all__ = [
    'SEOOptimizationStorage',
    'SEOOptimizationConfig',
    'KeywordData',
    'SEORankingData',
    'ContentSEOProfile',
    'SEOAnalyticsReport',
    'SearchEngine',
    'ContentType',
    'SEOMetricType',
    'OptimizationStatus',
    'create_seo_optimization_storage'
]