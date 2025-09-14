"""SEO Content Engine - Moteur de Contenu SEO Principal
===============================================

Composant principal consolidé pour l'optimisation de contenu SEO
avec intelligence artificielle et analyses prédictives.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.

VERSION: 2.0.0 - CONSOLIDATION MASSIVE
DATE: 2025-09-09
STATUS: ✅ NOUVEAU COMPOSANT CONSOLIDÉ
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import asyncio
import logging
import re
import json
from dataclasses import dataclass, field
import hashlib

# === ÉNUMÉRATIONS ===

class ContentType(Enum):
    """Types de contenu supportés"""
    ARTICLE = "article"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SOCIAL_POST = "social_post"
    BLOG_POST = "blog_post"
    NEWSLETTER = "newsletter"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    CASE_STUDY = "case_study"

class OptimizationLevel(Enum):
    """Niveaux d'optimisation SEO"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    AI_POWERED = "ai_powered"

class ContentQualityScore(Enum):
    """Scores de qualité de contenu"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    OUTSTANDING = "outstanding"

class SEOOptimizationTactic(Enum):
    """Tactiques d'optimisation SEO"""
    KEYWORD_DENSITY = "keyword_density"
    SEMANTIC_KEYWORDS = "semantic_keywords"
    READABILITY = "readability"
    STRUCTURE = "structure"
    META_OPTIMIZATION = "meta_optimization"
    INTERNAL_LINKING = "internal_linking"
    FEATURED_SNIPPETS = "featured_snippets"
    VOICE_SEARCH = "voice_search"

# === CLASSES DE DONNÉES ===

@dataclass
class ContentSEOAnalysis:
    """Résultat d'analyse SEO de contenu"""
    content_id: str
    content_type: ContentType
    content_length: int
    keyword_density: Dict[str, float]
    readability_score: float
    seo_score: float
    quality_score: ContentQualityScore
    optimization_opportunities: List[str]
    semantic_keywords: List[str]
    content_structure_analysis: Dict[str, Any]
    meta_analysis: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ContentOptimizationResult:
    """Résultat d'optimisation de contenu"""
    original_content: str
    optimized_content: str
    optimization_level: OptimizationLevel
    applied_tactics: List[SEOOptimizationTactic]
    improvement_metrics: Dict[str, float]
    seo_score_improvement: float
    optimization_recommendations: List[str]
    meta_tags_suggestions: Dict[str, str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ContentSEOStrategy:
    """Stratégie SEO pour le contenu"""
    strategy_id: str
    target_keywords: List[str]
    content_objectives: List[str]
    optimization_tactics: List[SEOOptimizationTactic]
    target_audience: Dict[str, Any]
    platform_specific_optimizations: Dict[str, Any]
    success_metrics: Dict[str, float]
    implementation_timeline: Dict[str, str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# === CLASSE PRINCIPALE ===

class SEOContentEngine:
    """
    Moteur principal de contenu SEO consolidé
    
    Combine toutes les capacités d'optimisation de contenu SEO
    en une interface unifiée avec intelligence artificielle.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialise le moteur de contenu SEO
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration par défaut
        self.default_config = {
            "ai_analysis_enabled": True,
            "real_time_optimization": True,
            "semantic_analysis": True,
            "voice_search_optimization": True,
            "featured_snippet_optimization": True,
            "multi_language_support": True,
            "enterprise_features": True,
            "max_content_length": 50000,
            "min_seo_score": 70.0,
            "target_readability_score": 60.0
        }
        
        # Fusion des configurations
        self.active_config = {**self.default_config, **self.config}
        
        # Cache pour les analyses
        self.analysis_cache: Dict[str, ContentSEOAnalysis] = {}
        self.optimization_cache: Dict[str, ContentOptimizationResult] = {}
        
        # Statistiques
        self.stats = {
            "total_analyses": 0,
            "total_optimizations": 0,
            "average_seo_improvement": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        self.logger.info("SEO Content Engine initialisé avec succès")
    
    def _generate_content_id(self, content: str) -> str:
        """Génère un ID unique pour le contenu"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def analyze_content(
        self,
        content: str,
        target_keywords: Optional[List[str]] = None,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> ContentSEOAnalysis:
        """
        Analyse complète du contenu pour le SEO
        
        Args:
            content: Contenu à analyser
            target_keywords: Mots-clés cibles
            creator_context: Contexte du créateur
            
        Returns:
            Analyse SEO complète du contenu
        """
        content_id = self._generate_content_id(content)
        
        # Vérifier le cache
        if content_id in self.analysis_cache:
            self.stats["cache_hits"] += 1
            return self.analysis_cache[content_id]
        
        self.stats["cache_misses"] += 1
        self.stats["total_analyses"] += 1
        
        try:
            # Détection automatique du type de contenu
            content_type = self._detect_content_type(content)
            
            # Analyse de la densité des mots-clés
            keyword_density = self._analyze_keyword_density(content, target_keywords or [])
            
            # Score de lisibilité
            readability_score = self._calculate_readability_score(content)
            
            # Score SEO global
            seo_score = self._calculate_seo_score(content, keyword_density, readability_score)
            
            # Score de qualité
            quality_score = self._determine_quality_score(seo_score, readability_score)
            
            # Opportunités d'optimisation
            optimization_opportunities = self._identify_optimization_opportunities(
                content, keyword_density, readability_score, seo_score
            )
            
            # Mots-clés sémantiques
            semantic_keywords = self._extract_semantic_keywords(content, target_keywords or [])
            
            # Analyse de structure
            structure_analysis = self._analyze_content_structure(content)
            
            # Analyse des méta-données
            meta_analysis = self._analyze_meta_potential(content, target_keywords or [])
            
            # Création de l'analyse
            analysis = ContentSEOAnalysis(
                content_id=content_id,
                content_type=content_type,
                content_length=len(content),
                keyword_density=keyword_density,
                readability_score=readability_score,
                seo_score=seo_score,
                quality_score=quality_score,
                optimization_opportunities=optimization_opportunities,
                semantic_keywords=semantic_keywords,
                content_structure_analysis=structure_analysis,
                meta_analysis=meta_analysis
            )
            
            # Mise en cache
            self.analysis_cache[content_id] = analysis
            
            self.logger.info(f"Analyse de contenu terminée - Score SEO: {seo_score:.2f}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de contenu: {str(e)}")
            raise
    
    async def optimize_content(
        self,
        content: str,
        target_keywords: Optional[List[str]] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
        target_audience: Optional[Dict[str, Any]] = None,
        platform_targets: Optional[List[str]] = None
    ) -> ContentOptimizationResult:
        """
        Optimise le contenu pour le SEO
        
        Args:
            content: Contenu à optimiser
            target_keywords: Mots-clés cibles
            optimization_level: Niveau d'optimisation
            target_audience: Audience cible
            platform_targets: Plateformes cibles
            
        Returns:
            Résultat d'optimisation avec contenu optimisé
        """
        content_id = self._generate_content_id(content)
        cache_key = f"{content_id}_{optimization_level.value}"
        
        # Vérifier le cache
        if cache_key in self.optimization_cache:
            self.stats["cache_hits"] += 1
            return self.optimization_cache[cache_key]
        
        self.stats["cache_misses"] += 1
        self.stats["total_optimizations"] += 1
        
        try:
            # Analyse initiale du contenu
            initial_analysis = await self.analyze_content(content, target_keywords)
            
            # Déterminer les tactiques d'optimisation
            optimization_tactics = self._determine_optimization_tactics(
                initial_analysis, optimization_level, platform_targets or []
            )
            
            # Appliquer les optimisations
            optimized_content = content
            applied_tactics = []
            
            for tactic in optimization_tactics:
                if tactic == SEOOptimizationTactic.KEYWORD_DENSITY:
                    optimized_content = self._optimize_keyword_density(
                        optimized_content, target_keywords or []
                    )
                    applied_tactics.append(tactic)
                
                elif tactic == SEOOptimizationTactic.SEMANTIC_KEYWORDS:
                    optimized_content = self._optimize_semantic_keywords(
                        optimized_content, initial_analysis.semantic_keywords
                    )
                    applied_tactics.append(tactic)
                
                elif tactic == SEOOptimizationTactic.READABILITY:
                    optimized_content = self._optimize_readability(optimized_content)
                    applied_tactics.append(tactic)
                
                elif tactic == SEOOptimizationTactic.STRUCTURE:
                    optimized_content = self._optimize_content_structure(optimized_content)
                    applied_tactics.append(tactic)
                
                elif tactic == SEOOptimizationTactic.FEATURED_SNIPPETS:
                    optimized_content = self._optimize_for_featured_snippets(optimized_content)
                    applied_tactics.append(tactic)
                
                elif tactic == SEOOptimizationTactic.VOICE_SEARCH:
                    optimized_content = self._optimize_for_voice_search(optimized_content)
                    applied_tactics.append(tactic)
            
            # Analyse post-optimisation
            final_analysis = await self.analyze_content(optimized_content, target_keywords)
            
            # Calcul des métriques d'amélioration
            improvement_metrics = self._calculate_improvement_metrics(
                initial_analysis, final_analysis
            )
            
            # Score d'amélioration SEO
            seo_improvement = final_analysis.seo_score - initial_analysis.seo_score
            
            # Recommandations supplémentaires
            recommendations = self._generate_optimization_recommendations(
                initial_analysis, final_analysis, optimization_level
            )
            
            # Suggestions de méta-tags
            meta_suggestions = self._generate_meta_tags_suggestions(
                optimized_content, target_keywords or []
            )
            
            # Création du résultat
            result = ContentOptimizationResult(
                original_content=content,
                optimized_content=optimized_content,
                optimization_level=optimization_level,
                applied_tactics=applied_tactics,
                improvement_metrics=improvement_metrics,
                seo_score_improvement=seo_improvement,
                optimization_recommendations=recommendations,
                meta_tags_suggestions=meta_suggestions
            )
            
            # Mise en cache
            self.optimization_cache[cache_key] = result
            
            # Mise à jour des statistiques
            self._update_optimization_stats(seo_improvement)
            
            self.logger.info(f"Optimisation terminée - Amélioration SEO: {seo_improvement:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'optimisation: {str(e)}")
            raise
    
    async def create_seo_strategy(
        self,
        content_analysis: ContentSEOAnalysis,
        business_objectives: List[str],
        target_audience: Dict[str, Any],
        competitive_landscape: Optional[Dict[str, Any]] = None
    ) -> ContentSEOStrategy:
        """
        Crée une stratégie SEO personnalisée pour le contenu
        """
        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Analyse des objectifs business
            content_objectives = self._align_content_with_business_objectives(
                content_analysis, business_objectives
            )
            
            # Détermination des tactiques optimales
            optimization_tactics = self._select_strategic_tactics(
                content_analysis, content_objectives, competitive_landscape
            )
            
            # Analyse de l'audience cible
            audience_keywords = self._extract_audience_keywords(target_audience)
            
            # Optimisations spécifiques par plateforme
            platform_optimizations = self._create_platform_specific_optimizations(
                content_analysis, target_audience
            )
            
            # Métriques de succès
            success_metrics = self._define_success_metrics(
                content_objectives, optimization_tactics
            )
            
            # Timeline d'implémentation
            implementation_timeline = self._create_implementation_timeline(
                optimization_tactics, content_objectives
            )
            
            strategy = ContentSEOStrategy(
                strategy_id=strategy_id,
                target_keywords=audience_keywords,
                content_objectives=content_objectives,
                optimization_tactics=optimization_tactics,
                target_audience=target_audience,
                platform_specific_optimizations=platform_optimizations,
                success_metrics=success_metrics,
                implementation_timeline=implementation_timeline
            )
            
            self.logger.info(f"Stratégie SEO créée: {strategy_id}")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Erreur création stratégie: {str(e)}")
            raise
    
    # === MÉTHODES PRIVÉES D'ANALYSE ===
    
    def _detect_content_type(self, content: str) -> ContentType:
        """Détecte automatiquement le type de contenu"""
        content_lower = content.lower()
        
        # Détection basée sur des patterns
        if any(marker in content_lower for marker in ['#', '##', '###']):
            return ContentType.ARTICLE
        elif len(content) < 500 and any(marker in content_lower for marker in ['@', '#hashtag']):
            return ContentType.SOCIAL_POST
        elif 'podcast' in content_lower or 'écouter' in content_lower:
            return ContentType.PODCAST
        elif 'vidéo' in content_lower or 'regarder' in content_lower:
            return ContentType.VIDEO
        elif len(content) > 2000:
            return ContentType.BLOG_POST
        else:
            return ContentType.ARTICLE
    
    def _analyze_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Analyse la densité des mots-clés"""
        if not keywords:
            return {}
        
        content_words = re.findall(r'\w+', content.lower())
        total_words = len(content_words)
        
        if total_words == 0:
            return {}
        
        keyword_density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content.lower().count(keyword_lower)
            density = (count / total_words) * 100
            keyword_density[keyword] = density
        
        return keyword_density
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calcule le score de lisibilité (simplifié)"""
        sentences = re.split(r'[.!?]+', content)
        words = re.findall(r'\w+', content)
        
        if not sentences or not words:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)
        
        # Formule simplifiée de Flesch
        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """Compte les syllabes dans un mot (estimation)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_seo_score(self, content: str, keyword_density: Dict[str, float], readability: float) -> float:
        """Calcule le score SEO global"""
        base_score = 50.0
        
        # Bonus pour la longueur appropriée
        length_bonus = min(10.0, len(content) / 200)
        
        # Bonus pour la densité de mots-clés optimale
        density_bonus = 0.0
        for density in keyword_density.values():
            if 1.0 <= density <= 3.0:  # Densité optimale
                density_bonus += 5.0
            elif density > 5.0:  # Pénalité pour sur-optimisation
                density_bonus -= 3.0
        
        # Bonus pour la lisibilité
        readability_bonus = min(15.0, readability / 5)
        
        # Score de structure (simplifié)
        structure_bonus = 5.0 if self._has_good_structure(content) else 0.0
        
        total_score = base_score + length_bonus + density_bonus + readability_bonus + structure_bonus
        return max(0.0, min(100.0, total_score))
    
    def _has_good_structure(self, content: str) -> bool:
        """Vérifie si le contenu a une bonne structure"""
        return bool(
            re.search(r'^#+ ', content, re.MULTILINE) or  # Titres markdown
            re.search(r'\n\n', content) or  # Paragraphes
            len(re.findall(r'[.!?]+', content)) > 3  # Phrases multiples
        )
    
    def _determine_quality_score(self, seo_score: float, readability_score: float) -> ContentQualityScore:
        """Détermine le score de qualité basé sur les métriques"""
        combined_score = (seo_score + readability_score) / 2
        
        if combined_score >= 90:
            return ContentQualityScore.OUTSTANDING
        elif combined_score >= 75:
            return ContentQualityScore.EXCELLENT
        elif combined_score >= 60:
            return ContentQualityScore.GOOD
        elif combined_score >= 40:
            return ContentQualityScore.FAIR
        else:
            return ContentQualityScore.POOR
    
    def _identify_optimization_opportunities(
        self, content: str, keyword_density: Dict[str, float], 
        readability: float, seo_score: float
    ) -> List[str]:
        """Identifie les opportunités d'optimisation"""
        opportunities = []
        
        if seo_score < 70:
            opportunities.append("Améliorer le score SEO global")
        
        if readability < 50:
            opportunities.append("Améliorer la lisibilité du contenu")
        
        if not keyword_density:
            opportunities.append("Intégrer des mots-clés cibles")
        
        if any(density > 5.0 for density in keyword_density.values()):
            opportunities.append("Réduire la sur-optimisation des mots-clés")
        
        if len(content) < 300:
            opportunities.append("Augmenter la longueur du contenu")
        
        if not self._has_good_structure(content):
            opportunities.append("Améliorer la structure du contenu")
        
        return opportunities
    
    def _extract_semantic_keywords(self, content: str, target_keywords: List[str]) -> List[str]:
        """Extrait les mots-clés sémantiques du contenu"""
        # Simulation d'extraction de mots-clés sémantiques
        words = re.findall(r'\w+', content.lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 3 and word not in ['dans', 'avec', 'pour', 'cette', 'sont']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Retourne les mots les plus fréquents (excluant les mots-clés cibles)
        semantic_keywords = [
            word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            if word not in [kw.lower() for kw in target_keywords]
        ]
        
        return semantic_keywords
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyse la structure du contenu"""
        return {
            "has_headings": bool(re.search(r'^#+ ', content, re.MULTILINE)),
            "paragraph_count": len(re.split(r'\n\s*\n', content)),
            "sentence_count": len(re.findall(r'[.!?]+', content)),
            "has_lists": bool(re.search(r'^[\*\-\+] ', content, re.MULTILINE)),
            "has_emphasis": bool(re.search(r'\*\*|__|\*|_', content)),
            "avg_paragraph_length": len(content) / max(1, len(re.split(r'\n\s*\n', content)))
        }
    
    def _analyze_meta_potential(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyse le potentiel des méta-données"""
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:160]
        
        return {
            "suggested_title_length": min(60, len(content.split('.')[0])),
            "suggested_description": first_paragraph[:160],
            "title_keywords_present": len([kw for kw in keywords if kw.lower() in content[:100].lower()]),
            "description_keywords_present": len([kw for kw in keywords if kw.lower() in first_paragraph.lower()]),
            "meta_optimization_score": 75.0  # Score simplifié
        }
    
    # === MÉTHODES D'OPTIMISATION ===
    
    def _determine_optimization_tactics(
        self, analysis: ContentSEOAnalysis, level: OptimizationLevel, platforms: List[str]
    ) -> List[SEOOptimizationTactic]:
        """Détermine les tactiques d'optimisation à appliquer"""
        tactics = []
        
        # Tactiques de base
        if level in [OptimizationLevel.BASIC, OptimizationLevel.STANDARD, OptimizationLevel.ADVANCED, OptimizationLevel.ENTERPRISE, OptimizationLevel.AI_POWERED]:
            if analysis.seo_score < 70:
                tactics.append(SEOOptimizationTactic.KEYWORD_DENSITY)
            
            if analysis.readability_score < 60:
                tactics.append(SEOOptimizationTactic.READABILITY)
        
        # Tactiques avancées
        if level in [OptimizationLevel.ADVANCED, OptimizationLevel.ENTERPRISE, OptimizationLevel.AI_POWERED]:
            tactics.extend([
                SEOOptimizationTactic.SEMANTIC_KEYWORDS,
                SEOOptimizationTactic.STRUCTURE,
                SEOOptimizationTactic.META_OPTIMIZATION
            ])
        
        # Tactiques enterprise et IA
        if level in [OptimizationLevel.ENTERPRISE, OptimizationLevel.AI_POWERED]:
            tactics.extend([
                SEOOptimizationTactic.FEATURED_SNIPPETS,
                SEOOptimizationTactic.VOICE_SEARCH,
                SEOOptimizationTactic.INTERNAL_LINKING
            ])
        
        return tactics
    
    def _optimize_keyword_density(self, content: str, keywords: List[str]) -> str:
        """Optimise la densité des mots-clés"""
        if not keywords:
            return content
        
        # Simulation d'optimisation de densité
        # Dans une vraie implémentation, ceci serait plus sophistiqué
        optimized = content
        
        for keyword in keywords:
            # Ajout naturel du mot-clé si absent
            if keyword.lower() not in content.lower():
                sentences = optimized.split('.')
                if sentences:
                    # Ajoute le mot-clé dans la première phrase
                    sentences[0] = sentences[0] + f" {keyword}"
                    optimized = '.'.join(sentences)
        
        return optimized
    
    def _optimize_semantic_keywords(self, content: str, semantic_keywords: List[str]) -> str:
        """Optimise l'usage des mots-clés sémantiques"""
        # Simulation d'optimisation sémantique
        return content  # Dans une vraie implémentation, intégrerait les mots-clés sémantiques
    
    def _optimize_readability(self, content: str) -> str:
        """Optimise la lisibilité du contenu"""
        # Simulation d'amélioration de lisibilité
        sentences = re.split(r'([.!?]+)', content)
        optimized_sentences = []
        
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                sentence = sentences[i].strip()
                if len(sentence.split()) > 25:  # Phrase trop longue
                    # Divise la phrase (simulation)
                    words = sentence.split()
                    mid = len(words) // 2
                    optimized_sentences.append(' '.join(words[:mid]) + '.')
                    optimized_sentences.append(' '.join(words[mid:]))
                else:
                    optimized_sentences.append(sentence)
                
                if i + 1 < len(sentences):
                    optimized_sentences.append(sentences[i + 1])
        
        return ''.join(optimized_sentences)
    
    def _optimize_content_structure(self, content: str) -> str:
        """Optimise la structure du contenu"""
        # Simulation d'amélioration de structure
        if not re.search(r'^#+ ', content, re.MULTILINE):
            # Ajoute un titre principal
            content = "# Titre Principal\n\n" + content
        
        # Ajoute des sous-titres si le contenu est long
        if len(content) > 1000 and content.count('\n\n') < 3:
            paragraphs = content.split('\n\n')
            if len(paragraphs) > 2:
                paragraphs[len(paragraphs)//2] = "## Section Importante\n\n" + paragraphs[len(paragraphs)//2]
            content = '\n\n'.join(paragraphs)
        
        return content
    
    def _optimize_for_featured_snippets(self, content: str) -> str:
        """Optimise pour les featured snippets"""
        # Ajoute des questions-réponses
        if '?' not in content[:200]:
            question = "## Qu'est-ce que cela signifie?\n\n"
            content = question + content
        
        return content
    
    def _optimize_for_voice_search(self, content: str) -> str:
        """Optimise pour la recherche vocale"""
        # Ajoute des phrases conversationnelles
        if not any(phrase in content.lower() for phrase in ['comment', 'pourquoi', 'qu\'est-ce']):
            content = "Vous vous demandez comment cela fonctionne? " + content
        
        return content
    
    # === MÉTHODES UTILITAIRES ===
    
    def _calculate_improvement_metrics(
        self, initial: ContentSEOAnalysis, final: ContentSEOAnalysis
    ) -> Dict[str, float]:
        """Calcule les métriques d'amélioration"""
        return {
            "seo_score_improvement": final.seo_score - initial.seo_score,
            "readability_improvement": final.readability_score - initial.readability_score,
            "keyword_density_optimization": len(final.keyword_density) - len(initial.keyword_density),
            "semantic_keywords_added": len(final.semantic_keywords) - len(initial.semantic_keywords)
        }
    
    def _generate_optimization_recommendations(
        self, initial: ContentSEOAnalysis, final: ContentSEOAnalysis, level: OptimizationLevel
    ) -> List[str]:
        """Génère des recommandations d'optimisation supplémentaires"""
        recommendations = []
        
        if final.seo_score < 80:
            recommendations.append("Continuer l'optimisation pour atteindre un score SEO de 80+")
        
        if final.readability_score < 70:
            recommendations.append("Améliorer davantage la lisibilité du contenu")
        
        if level == OptimizationLevel.AI_POWERED:
            recommendations.append("Intégrer des éléments d'IA pour la personnalisation")
        
        return recommendations
    
    def _generate_meta_tags_suggestions(self, content: str, keywords: List[str]) -> Dict[str, str]:
        """Génère des suggestions de méta-tags"""
        first_sentence = content.split('.')[0] if '.' in content else content[:60]
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:160]
        
        return {
            "title": f"{first_sentence[:60]}..." if len(first_sentence) > 60 else first_sentence,
            "description": f"{first_paragraph[:160]}..." if len(first_paragraph) > 160 else first_paragraph,
            "keywords": ", ".join(keywords[:5]) if keywords else "",
            "og_title": first_sentence[:60],
            "og_description": first_paragraph[:300]
        }
    
    def _update_optimization_stats(self, improvement -> None: float) -> None:
        """Met à jour les statistiques d'optimisation"""
        total_optimizations = self.stats["total_optimizations"]
        current_avg = self.stats["average_seo_improvement"]
        
        new_avg = ((current_avg * (total_optimizations - 1)) + improvement) / total_optimizations
        self.stats["average_seo_improvement"] = new_avg
    
    # === MÉTHODES DE STRATÉGIE ===
    
    def _align_content_with_business_objectives(
        self, analysis: ContentSEOAnalysis, objectives: List[str]
    ) -> List[str]:
        """Aligne le contenu avec les objectifs business"""
        content_objectives = []
        
        for objective in objectives:
            if "conversion" in objective.lower():
                content_objectives.append("Optimiser pour la conversion")
            elif "engagement" in objective.lower():
                content_objectives.append("Maximiser l'engagement")
            elif "autorité" in objective.lower():
                content_objectives.append("Établir l'autorité du domaine")
            elif "trafic" in objective.lower():
                content_objectives.append("Augmenter le trafic organique")
        
        return content_objectives
    
    def _select_strategic_tactics(
        self, analysis: ContentSEOAnalysis, objectives: List[str], competitive_data: Optional[Dict[str, Any]]
    ) -> List[SEOOptimizationTactic]:
        """Sélectionne les tactiques stratégiques optimales"""
        tactics = []
        
        # Tactiques basées sur les objectifs
        for objective in objectives:
            if "conversion" in objective.lower():
                tactics.extend([SEOOptimizationTactic.META_OPTIMIZATION, SEOOptimizationTactic.FEATURED_SNIPPETS])
            elif "engagement" in objective.lower():
                tactics.extend([SEOOptimizationTactic.READABILITY, SEOOptimizationTactic.STRUCTURE])
            elif "trafic" in objective.lower():
                tactics.extend([SEOOptimizationTactic.KEYWORD_DENSITY, SEOOptimizationTactic.SEMANTIC_KEYWORDS])
        
        return list(set(tactics))  # Supprime les doublons
    
    def _extract_audience_keywords(self, audience: Dict[str, Any]) -> List[str]:
        """Extrait les mots-clés pertinents pour l'audience"""
        keywords = []
        
        if "interests" in audience:
            keywords.extend(audience["interests"][:5])
        
        if "demographics" in audience:
            demo = audience["demographics"]
            if "age_group" in demo:
                keywords.append(demo["age_group"])
            if "profession" in demo:
                keywords.append(demo["profession"])
        
        return keywords
    
    def _create_platform_specific_optimizations(
        self, analysis: ContentSEOAnalysis, audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crée des optimisations spécifiques par plateforme"""
        return {
            "google": {
                "focus": "featured_snippets",
                "tactics": ["keyword_density", "structure"]
            },
            "social_media": {
                "focus": "engagement",
                "tactics": ["readability", "visual_appeal"]
            },
            "youtube": {
                "focus": "video_seo",
                "tactics": ["transcript_optimization", "thumbnail_text"]
            }
        }
    
    def _define_success_metrics(
        self, objectives: List[str], tactics: List[SEOOptimizationTactic]
    ) -> Dict[str, float]:
        """Définit les métriques de succès"""
        return {
            "target_seo_score": 85.0,
            "target_readability": 70.0,
            "target_keyword_density": 2.5,
            "expected_traffic_increase": 25.0,
            "expected_engagement_boost": 15.0
        }
    
    def _create_implementation_timeline(
        self, tactics: List[SEOOptimizationTactic], objectives: List[str]
    ) -> Dict[str, str]:
        """Crée un timeline d'implémentation"""
        return {
            "phase_1": "Optimisations techniques (1-2 semaines)",
            "phase_2": "Optimisation de contenu (2-3 semaines)",
            "phase_3": "Optimisations avancées (3-4 semaines)",
            "monitoring": "Surveillance continue (ongoing)"
        }
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur"""
        return {
            "version": "2.0.0",
            "total_analyses": self.stats["total_analyses"],
            "total_optimizations": self.stats["total_optimizations"],
            "average_seo_improvement": self.stats["average_seo_improvement"],
            "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"]),
            "cache_size": len(self.analysis_cache) + len(self.optimization_cache),
            "active_config": self.active_config
        }


# === EXPORTS ===
__all__ = [
    'SEOContentEngine',
    'ContentSEOAnalysis',
    'ContentOptimizationResult', 
    'ContentSEOStrategy',
    'ContentType',
    'OptimizationLevel',
    'ContentQualityScore',
    'SEOOptimizationTactic'
]
