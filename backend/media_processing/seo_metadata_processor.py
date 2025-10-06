"""
Enterprise SEO Metadata Processor pour IA Chérie
Optimisation SEO automatique des métadonnées
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SEOPlatform(Enum):
    """Plateformes SEO supportées"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class OptimizationLevel(Enum):
    """Niveaux d'optimisation"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class SEOMetadata:
    """Métadonnées SEO optimisées"""
    title: str
    description: str
    keywords: List[str]
    hashtags: List[str]
    schema_markup: Dict[str, Any]
    open_graph: Dict[str, str]
    twitter_card: Dict[str, str]
    canonical_url: str
    meta_robots: str


@dataclass
class SEOScore:
    """Score SEO"""
    overall: float
    title_score: float
    description_score: float
    keywords_score: float
    technical_score: float
    recommendations: List[str]


@dataclass
class SEOOptimizationResult:
    """Résultat d'optimisation SEO"""
    content_id: str
    platform: SEOPlatform
    original_metadata: Dict[str, Any]
    optimized_metadata: SEOMetadata
    seo_score: SEOScore
    improvements: Dict[str, float]


class SEOMetadataProcessor:
    """
    Processeur de métadonnées SEO ultra-avancé
    Optimisation multi-plateformes avec AI
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SEO processor"""
        self.config = config or {}
        self.optimization_history: Dict[str, List[SEOOptimizationResult]] = {}
        logger.info("SEOMetadataProcessor initialized")
    
    async def optimize_seo(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: SEOPlatform = SEOPlatform.GOOGLE,
        level: OptimizationLevel = OptimizationLevel.ADVANCED
    ) -> SEOOptimizationResult:
        """
        Optimisation SEO complète
        
        Args:
            content_id: ID du contenu
            content_data: Données du contenu
            platform: Plateforme cible
            level: Niveau d'optimisation
        
        Returns:
            Résultat d'optimisation
        """
        # Analyse initiale
        original_metadata = content_data.get("metadata", {})
        original_score = await self._calculate_seo_score(original_metadata)
        
        # Optimisation des métadonnées
        optimized_metadata = await self._optimize_metadata(
            content_data,
            platform,
            level
        )
        
        # Nouveau score
        optimized_score = await self._calculate_seo_score(
            self._metadata_to_dict(optimized_metadata)
        )
        
        # Calcul des améliorations
        improvements = {
            "overall": optimized_score.overall - original_score.overall,
            "title": optimized_score.title_score - original_score.title_score,
            "description": optimized_score.description_score - original_score.description_score,
            "keywords": optimized_score.keywords_score - original_score.keywords_score,
            "technical": optimized_score.technical_score - original_score.technical_score
        }
        
        result = SEOOptimizationResult(
            content_id=content_id,
            platform=platform,
            original_metadata=original_metadata,
            optimized_metadata=optimized_metadata,
            seo_score=optimized_score,
            improvements=improvements
        )
        
        # Store history
        if content_id not in self.optimization_history:
            self.optimization_history[content_id] = []
        self.optimization_history[content_id].append(result)
        
        return result
    
    async def _optimize_metadata(
        self,
        content_data: Dict[str, Any],
        platform: SEOPlatform,
        level: OptimizationLevel
    ) -> SEOMetadata:
        """Optimise les métadonnées"""
        await asyncio.sleep(0.02)
        
        # Titre optimisé
        title = await self._optimize_title(
            content_data.get("title", ""),
            platform,
            level
        )
        
        # Description optimisée
        description = await self._optimize_description(
            content_data.get("description", ""),
            platform,
            level
        )
        
        # Keywords optimisés
        keywords = await self._optimize_keywords(
            content_data,
            platform,
            level
        )
        
        # Hashtags
        hashtags = await self._generate_hashtags(
            content_data,
            platform
        )
        
        # Schema markup
        schema = self._generate_schema_markup(content_data)
        
        # Open Graph
        og = self._generate_open_graph(title, description, content_data)
        
        # Twitter Card
        twitter = self._generate_twitter_card(title, description)
        
        return SEOMetadata(
            title=title,
            description=description,
            keywords=keywords,
            hashtags=hashtags,
            schema_markup=schema,
            open_graph=og,
            twitter_card=twitter,
            canonical_url=content_data.get("url", ""),
            meta_robots="index, follow"
        )
    
    async def _optimize_title(
        self,
        original_title: str,
        platform: SEOPlatform,
        level: OptimizationLevel
    ) -> str:
        """Optimise le titre"""
        await asyncio.sleep(0.005)
        
        if not original_title:
            original_title = "Untitled Content"
        
        # Règles selon la plateforme
        max_length = {
            SEOPlatform.GOOGLE: 60,
            SEOPlatform.YOUTUBE: 100,
            SEOPlatform.INSTAGRAM: 125,
            SEOPlatform.TIKTOK: 100,
            SEOPlatform.FACEBOOK: 80,
            SEOPlatform.TWITTER: 70,
            SEOPlatform.LINKEDIN: 70
        }[platform]
        
        # Ajout de power words selon le niveau
        if level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
            power_words = ["Ultimate", "Complete", "Professional", "Expert"]
            if not any(word in original_title for word in power_words):
                original_title = f"{power_words[0]} {original_title}"
        
        # Troncature si nécessaire
        if len(original_title) > max_length:
            original_title = original_title[:max_length-3] + "..."
        
        return original_title
    
    async def _optimize_description(
        self,
        original_desc: str,
        platform: SEOPlatform,
        level: OptimizationLevel
    ) -> str:
        """Optimise la description"""
        await asyncio.sleep(0.005)
        
        if not original_desc:
            original_desc = "High-quality content optimized for engagement"
        
        max_length = {
            SEOPlatform.GOOGLE: 160,
            SEOPlatform.YOUTUBE: 5000,
            SEOPlatform.INSTAGRAM: 2200,
            SEOPlatform.TIKTOK: 150,
            SEOPlatform.FACEBOOK: 250,
            SEOPlatform.TWITTER: 280,
            SEOPlatform.LINKEDIN: 200
        }[platform]
        
        # Ajout de call-to-action
        if level == OptimizationLevel.EXPERT:
            cta = " 👉 Click to learn more!"
            if len(original_desc) + len(cta) <= max_length:
                original_desc += cta
        
        return original_desc[:max_length]
    
    async def _optimize_keywords(
        self,
        content_data: Dict[str, Any],
        platform: SEOPlatform,
        level: OptimizationLevel
    ) -> List[str]:
        """Optimise les keywords"""
        await asyncio.sleep(0.01)
        
        base_keywords = content_data.get("keywords", [])
        if not base_keywords:
            base_keywords = ["content", "digital", "media"]
        
        # Ajout de keywords tendance
        trending = ["AI", "2025", "viral", "trending", "best"]
        
        if level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
            base_keywords.extend(trending[:3])
        
        # Long-tail keywords
        if level == OptimizationLevel.EXPERT:
            long_tail = [
                "how to",
                "best practices",
                "step by step",
                "ultimate guide"
            ]
            base_keywords.extend(long_tail[:2])
        
        return list(set(base_keywords))[:20]  # Max 20 keywords
    
    async def _generate_hashtags(
        self,
        content_data: Dict[str, Any],
        platform: SEOPlatform
    ) -> List[str]:
        """Génère les hashtags optimisés"""
        await asyncio.sleep(0.008)
        
        base_tags = ["AI", "Technology", "Innovation", "Digital"]
        
        # Hashtags spécifiques à la plateforme
        platform_specific = {
            SEOPlatform.INSTAGRAM: ["InstaGood", "PhotoOfTheDay", "Viral"],
            SEOPlatform.TIKTOK: ["FYP", "ForYou", "Trending"],
            SEOPlatform.TWITTER: ["Tech", "News", "Breaking"],
            SEOPlatform.LINKEDIN: ["Professional", "Business", "Career"]
        }
        
        if platform in platform_specific:
            base_tags.extend(platform_specific[platform])
        
        return [f"#{tag.replace(' ', '')}" for tag in base_tags[:10]]
    
    def _generate_schema_markup(
        self,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère le schema markup"""
        return {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": content_data.get("title", ""),
            "description": content_data.get("description", ""),
            "author": {
                "@type": "Person",
                "name": content_data.get("author", "")
            },
            "datePublished": "2025-10-04",
            "image": content_data.get("thumbnail", ""),
            "inLanguage": "en"
        }
    
    def _generate_open_graph(
        self,
        title: str,
        description: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Génère les Open Graph tags"""
        return {
            "og:title": title,
            "og:description": description,
            "og:type": "website",
            "og:url": content_data.get("url", ""),
            "og:image": content_data.get("thumbnail", ""),
            "og:site_name": "IA Chérie",
            "og:locale": "en_US"
        }
    
    def _generate_twitter_card(
        self,
        title: str,
        description: str
    ) -> Dict[str, str]:
        """Génère les Twitter Card tags"""
        return {
            "twitter:card": "summary_large_image",
            "twitter:title": title,
            "twitter:description": description,
            "twitter:site": "@iacherie",
            "twitter:creator": "@iacherie"
        }
    
    async def _calculate_seo_score(
        self,
        metadata: Dict[str, Any]
    ) -> SEOScore:
        """Calcule le score SEO"""
        await asyncio.sleep(0.01)
        
        # Title score
        title = metadata.get("title", "")
        title_score = 0.8 if len(title) > 10 and len(title) < 60 else 0.5
        
        # Description score
        description = metadata.get("description", "")
        desc_score = 0.85 if len(description) > 50 and len(description) < 160 else 0.6
        
        # Keywords score
        keywords = metadata.get("keywords", [])
        kw_score = 0.9 if len(keywords) >= 5 else 0.7
        
        # Technical score
        tech_score = 0.88
        
        overall = (title_score * 0.3 + desc_score * 0.3 + kw_score * 0.2 + tech_score * 0.2)
        
        recommendations = []
        if title_score < 0.7:
            recommendations.append("Optimize title length (10-60 characters)")
        if desc_score < 0.75:
            recommendations.append("Improve description (50-160 characters)")
        if kw_score < 0.8:
            recommendations.append("Add more relevant keywords")
        
        return SEOScore(
            overall=overall,
            title_score=title_score,
            description_score=desc_score,
            keywords_score=kw_score,
            technical_score=tech_score,
            recommendations=recommendations
        )
    
    def _metadata_to_dict(self, metadata: SEOMetadata) -> Dict[str, Any]:
        """Convertit SEOMetadata en dict"""
        return {
            "title": metadata.title,
            "description": metadata.description,
            "keywords": metadata.keywords,
            "hashtags": metadata.hashtags
        }
    
    async def batch_optimize(
        self,
        contents: List[Dict[str, Any]],
        platform: SEOPlatform = SEOPlatform.GOOGLE
    ) -> Dict[str, SEOOptimizationResult]:
        """Optimisation SEO en batch"""
        results_dict = {}
        for content in contents:
            content_id = content.get("id", "unknown")
            result = await self.optimize_seo(content_id, content, platform)
            results_dict[content_id] = result
        
        return results_dict
    
    def get_optimization_history(
        self,
        content_id: str
    ) -> List[SEOOptimizationResult]:
        """Récupère l'historique d'optimisation"""
        return self.optimization_history.get(content_id, [])


# Factory function
_seo_processor_instance: Optional[SEOMetadataProcessor] = None

def get_seo_processor(
    config: Optional[Dict[str, Any]] = None
) -> SEOMetadataProcessor:
    """Factory pour obtenir une instance du processeur SEO"""
    global _seo_processor_instance
    if _seo_processor_instance is None:
        _seo_processor_instance = SEOMetadataProcessor(config)
    return _seo_processor_instance


__all__ = [
    "SEOMetadataProcessor",
    "get_seo_processor",
    "SEOMetadata",
    "SEOScore",
    "SEOOptimizationResult",
    "SEOPlatform",
    "OptimizationLevel"
]
