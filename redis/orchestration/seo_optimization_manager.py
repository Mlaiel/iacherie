#!/usr/bin/env python3
"""🔍 SEO Optimization Manager - Advanced Search Engine Optimization Platform
================================================================
Expert: SEO SPECIALIST + CONTENT STRATEGIST + DATA ANALYST + BACKEND SENIOR
Technologies: SEO Analytics + Content Optimization + Keyword Intelligence + Performance Tracking
Architecture: Level 3 - SEO Intelligence Layer
Date: 2025-01-25

Ultra-advanced SEO optimization system with AI-powered content analysis,
keyword intelligence, competitor tracking and automated optimization strategies.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import statistics
from collections import defaultdict, Counter
from urllib.parse import urlparse, parse_qs
import hashlib

logger = logging.getLogger(__name__)

class SEOMetricType(Enum):
    """Types de métriques SEO"""
    KEYWORD_RANKING = "keyword_ranking"
    ORGANIC_TRAFFIC = "organic_traffic"
    CLICK_THROUGH_RATE = "click_through_rate"
    BOUNCE_RATE = "bounce_rate"
    DWELL_TIME = "dwell_time"
    CONVERSION_RATE = "conversion_rate"
    BACKLINK_SCORE = "backlink_score"
    DOMAIN_AUTHORITY = "domain_authority"
    PAGE_SPEED = "page_speed"
    MOBILE_USABILITY = "mobile_usability"
    CORE_WEB_VITALS = "core_web_vitals"
    CONTENT_QUALITY = "content_quality"

class ContentType(Enum):
    """Types de contenu"""
    BLOG_POST = "blog_post"
    VIDEO = "video"
    PODCAST = "podcast"
    IMAGE = "image"
    INFOGRAPHIC = "infographic"
    EBOOK = "ebook"
    COURSE = "course"
    LIVE_STREAM = "live_stream"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"

class SearchEngine(Enum):
    """Moteurs de recherche"""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"

@dataclass
class KeywordData:
    """Données de mot-clé"""
    keyword: str
    search_volume: int
    competition: float  # 0.0 to 1.0
    cpc: float
    trend: List[float]  # Historical trend data
    difficulty: float  # 0.0 to 1.0
    intent: str  # informational, navigational, transactional, commercial
    related_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    semantic_keywords: List[str] = field(default_factory=list)
    
@dataclass
class ContentSEOAnalysis:
    """Analyse SEO du contenu"""
    content_id: str
    url: str
    title: str
    meta_description: str
    content_type: ContentType
    word_count: int
    readability_score: float
    keyword_density: Dict[str, float]
    headings_structure: Dict[str, List[str]]
    internal_links: List[str]
    external_links: List[str]
    images: Dict[str, Dict[str, str]]  # alt, title, etc.
    schema_markup: Dict[str, Any]
    performance_metrics: Dict[SEOMetricType, float]
    recommendations: List[str] = field(default_factory=list)
    optimization_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SEOStrategy:
    """Stratégie SEO"""
    strategy_id: str
    creator_id: str
    target_keywords: List[str]
    content_topics: List[str]
    competitor_urls: List[str]
    goals: Dict[str, float]  # metric -> target value
    timeline: Dict[str, datetime]  # milestone -> date
    budget: float
    priority: int = 1
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)

class KeywordResearcher:
    """Recherche de mots-clés intelligente"""
    
    def __init__(self):
        self.keyword_database: Dict[str, KeywordData] = {}
        self.trend_patterns: Dict[str, List[float]] = {}
    
    async def research_keywords(self, seed_keywords: List[str], niche: str) -> List[KeywordData]:
        """Rechercher des mots-clés optimaux"""
        try:
            researched_keywords = []
            
            for seed_keyword in seed_keywords:
                # Simulate keyword research (in real implementation, use APIs like SEMrush, Ahrefs)
                keyword_variations = await self._generate_keyword_variations(seed_keyword, niche)
                
                for variation in keyword_variations:
                    keyword_data = await self._analyze_keyword(variation, niche)
                    if keyword_data:
                        researched_keywords.append(keyword_data)
                        self.keyword_database[variation] = keyword_data
            
            # Sort by opportunity score (high volume, low competition)
            researched_keywords.sort(
                key=lambda k: (k.search_volume * (1 - k.competition)) / (k.difficulty + 0.1),
                reverse=True
            )
            
            logger.info(f"Researched {len(researched_keywords)} keywords for seeds: {seed_keywords}")
            return researched_keywords[:50]  # Return top 50
            
        except Exception as e:
            logger.error(f"Error researching keywords: {e}")
            return []
    
    async def _generate_keyword_variations(self, seed_keyword: str, niche: str) -> List[str]:
        """Générer des variations de mots-clés"""
        variations = []
        
        # Long-tail variations
        long_tail_prefixes = ["how to", "best", "top", "guide to", "tips for", "learn"]
        long_tail_suffixes = ["tutorial", "guide", "tips", "strategies", "techniques", "examples"]
        
        for prefix in long_tail_prefixes:
            variations.append(f"{prefix} {seed_keyword}")
        
        for suffix in long_tail_suffixes:
            variations.append(f"{seed_keyword} {suffix}")
        
        # Niche-specific variations
        niche_modifiers = {
            "tech": ["software", "app", "digital", "online", "mobile"],
            "health": ["wellness", "fitness", "nutrition", "mental health"],
            "business": ["marketing", "strategy", "growth", "management"],
            "education": ["course", "training", "learning", "skills"]
        }
        
        if niche in niche_modifiers:
            for modifier in niche_modifiers[niche]:
                variations.extend([
                    f"{modifier} {seed_keyword}",
                    f"{seed_keyword} {modifier}",
                    f"{seed_keyword} for {modifier}"
                ])
        
        # Remove duplicates and seed keyword
        variations = list(set(variations))
        if seed_keyword in variations:
            variations.remove(seed_keyword)
        
        return variations[:30]  # Limit variations
    
    async def _analyze_keyword(self, keyword: str, niche: str) -> Optional[KeywordData]:
        """Analyser un mot-clé"""
        try:
            # Simulate keyword analysis (real implementation would use API)
            word_count = len(keyword.split())
            
            # Estimate metrics based on keyword characteristics
            base_volume = max(100, 10000 // (word_count * 2))
            search_volume = base_volume + hash(keyword) % 5000
            
            competition = min(0.9, (len(keyword) - 10) / 20 + 0.1)
            difficulty = min(0.9, competition * 0.8 + 0.1)
            cpc = max(0.1, (competition * 5.0) + (hash(keyword) % 100) / 100)
            
            # Generate trend data
            trend = [max(0.1, 1.0 + (hash(f"{keyword}{i}") % 200 - 100) / 1000) for i in range(12)]
            
            # Determine intent
            intent = self._determine_search_intent(keyword)
            
            return KeywordData(
                keyword=keyword,
                search_volume=search_volume,
                competition=competition,
                cpc=cpc,
                trend=trend,
                difficulty=difficulty,
                intent=intent,
                related_keywords=await self._get_related_keywords(keyword),
                long_tail_keywords=await self._get_long_tail_keywords(keyword),
                semantic_keywords=await self._get_semantic_keywords(keyword)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing keyword {keyword}: {e}")
            return None
    
    def _determine_search_intent(self, keyword: str) -> str:
        """Déterminer l'intention de recherche"""
        keyword_lower = keyword.lower()
        
        # Transactional intent
        transactional_words = ["buy", "purchase", "order", "book", "hire", "subscribe", "download"]
        if any(word in keyword_lower for word in transactional_words):
            return "transactional"
        
        # Commercial intent
        commercial_words = ["best", "top", "review", "compare", "vs", "price", "cost", "cheap"]
        if any(word in keyword_lower for word in commercial_words):
            return "commercial"
        
        # Navigational intent
        if any(word in keyword_lower for word in ["login", "sign in", "official", "website"]):
            return "navigational"
        
        # Informational intent (default)
        return "informational"
    
    async def _get_related_keywords(self, keyword: str) -> List[str]:
        """Obtenir des mots-clés liés"""
        # Simplified related keywords generation
        words = keyword.split()
        related = []
        
        synonyms = {
            "guide": ["tutorial", "howto", "manual"],
            "best": ["top", "great", "excellent"],
            "tips": ["advice", "strategies", "techniques"],
            "learn": ["study", "master", "understand"]
        }
        
        for word in words:
            if word.lower() in synonyms:
                for synonym in synonyms[word.lower()]:
                    related_keyword = keyword.replace(word, synonym)
                    if related_keyword != keyword:
                        related.append(related_keyword)
        
        return related[:5]
    
    async def _get_long_tail_keywords(self, keyword: str) -> List[str]:
        """Obtenir des mots-clés longue traîne"""
        modifiers = ["for beginners", "step by step", "complete guide", "2025", "free", "online"]
        return [f"{keyword} {modifier}" for modifier in modifiers[:3]]
    
    async def _get_semantic_keywords(self, keyword: str) -> List[str]:
        """Obtenir des mots-clés sémantiques"""
        # Simplified semantic keyword generation
        semantic_map = {
            "marketing": ["advertising", "promotion", "branding", "SEO"],
            "programming": ["coding", "development", "software", "algorithms"],
            "fitness": ["workout", "exercise", "health", "training"],
            "cooking": ["recipe", "food", "kitchen", "ingredients"]
        }
        
        semantic_keywords = []
        keyword_lower = keyword.lower()
        
        for base_word, related_words in semantic_map.items():
            if base_word in keyword_lower:
                semantic_keywords.extend(related_words)
        
        return semantic_keywords[:4]

class ContentAnalyzer:
    """Analyseur de contenu SEO"""
    
    def __init__(self):
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"
        }
    
    async def analyze_content(self, content_id: str, url: str, title: str, content: str, meta_description: str) -> ContentSEOAnalysis:
        """Analyser le contenu pour le SEO"""
        try:
            # Basic content metrics
            word_count = len(content.split())
            content_type = self._determine_content_type(content, title)
            
            # Readability analysis
            readability_score = await self._calculate_readability(content)
            
            # Keyword analysis
            keyword_density = await self._analyze_keyword_density(content)
            
            # Structure analysis
            headings_structure = await self._analyze_headings(content)
            
            # Link analysis
            internal_links, external_links = await self._analyze_links(content, url)
            
            # Image analysis
            images = await self._analyze_images(content)
            
            # Schema markup detection
            schema_markup = await self._detect_schema_markup(content)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                title, content, meta_description, word_count, keyword_density, headings_structure
            )
            
            # Calculate optimization score
            optimization_score = await self._calculate_optimization_score(
                title, content, meta_description, word_count, readability_score, 
                keyword_density, headings_structure, internal_links, external_links
            )
            
            analysis = ContentSEOAnalysis(
                content_id=content_id,
                url=url,
                title=title,
                meta_description=meta_description,
                content_type=content_type,
                word_count=word_count,
                readability_score=readability_score,
                keyword_density=keyword_density,
                headings_structure=headings_structure,
                internal_links=internal_links,
                external_links=external_links,
                images=images,
                schema_markup=schema_markup,
                performance_metrics={},
                recommendations=recommendations,
                optimization_score=optimization_score
            )
            
            logger.info(f"Content analysis completed for {content_id} with score {optimization_score:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return None
    
    def _determine_content_type(self, content: str, title: str) -> ContentType:
        """Déterminer le type de contenu"""
        word_count = len(content.split())
        
        if word_count < 500:
            return ContentType.SHORT_FORM
        elif word_count > 2000:
            return ContentType.LONG_FORM
        else:
            # Check for specific indicators
            title_lower = title.lower()
            if any(word in title_lower for word in ["tutorial", "guide", "how to"]):
                return ContentType.BLOG_POST
            elif "course" in title_lower:
                return ContentType.COURSE
            else:
                return ContentType.BLOG_POST
    
    async def _calculate_readability(self, content: str) -> float:
        """Calculer le score de lisibilité (Flesch-Kincaid simplifiée)"""
        try:
            sentences = len(re.findall(r'[.!?]+', content))
            words = len(content.split())
            syllables = sum(self._count_syllables(word) for word in content.split())
            
            if sentences == 0 or words == 0:
                return 0.0
            
            # Simplified Flesch Reading Ease
            avg_sentence_length = words / sentences
            avg_syllables_per_word = syllables / words
            
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            return max(0.0, min(100.0, score))
            
        except Exception:
            return 50.0  # Default average score
    
    def _count_syllables(self, word: str) -> int:
        """Compter les syllabes dans un mot"""
        word = word.lower().strip(".,!?;:")
        if not word:
            return 0
        
        # Simple syllable counting
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _analyze_keyword_density(self, content: str) -> Dict[str, float]:
        """Analyser la densité des mots-clés"""
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)
        
        # Filter out stop words
        filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Count word frequency
        word_freq = Counter(filtered_words)
        
        # Calculate density for top words
        keyword_density = {}
        for word, count in word_freq.most_common(20):
            density = (count / word_count) * 100
            keyword_density[word] = round(density, 2)
        
        return keyword_density
    
    async def _analyze_headings(self, content: str) -> Dict[str, List[str]]:
        """Analyser la structure des en-têtes"""
        headings = {
            "h1": re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE),
            "h2": re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE),
            "h3": re.findall(r'<h3[^>]*>(.*?)</h3>', content, re.IGNORECASE),
            "h4": re.findall(r'<h4[^>]*>(.*?)</h4>', content, re.IGNORECASE),
            "h5": re.findall(r'<h5[^>]*>(.*?)</h5>', content, re.IGNORECASE),
            "h6": re.findall(r'<h6[^>]*>(.*?)</h6>', content, re.IGNORECASE)
        }
        
        # Clean HTML tags from headings
        for level, heading_list in headings.items():
            headings[level] = [re.sub(r'<[^>]+>', '', h).strip() for h in heading_list]
        
        return headings
    
    async def _analyze_links(self, content: str, base_url: str) -> Tuple[List[str], List[str]]:
        """Analyser les liens internes et externes"""
        # Extract all links
        links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        
        base_domain = urlparse(base_url).netloc
        internal_links = []
        external_links = []
        
        for link in links:
            parsed = urlparse(link)
            if parsed.netloc == "" or parsed.netloc == base_domain:
                internal_links.append(link)
            else:
                external_links.append(link)
        
        return internal_links, external_links
    
    async def _analyze_images(self, content: str) -> Dict[str, Dict[str, str]]:
        """Analyser les images et leurs attributs SEO"""
        img_pattern = r'<img[^>]+>'
        images = {}
        
        for i, img_tag in enumerate(re.findall(img_pattern, content, re.IGNORECASE)):
            img_id = f"image_{i}"
            
            # Extract attributes
            src = re.search(r'src=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
            alt = re.search(r'alt=["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
            title = re.search(r'title=["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
            
            images[img_id] = {
                "src": src.group(1) if src else "",
                "alt": alt.group(1) if alt else "",
                "title": title.group(1) if title else "",
                "has_alt": bool(alt and alt.group(1).strip()),
                "has_title": bool(title and title.group(1).strip())
            }
        
        return images
    
    async def _detect_schema_markup(self, content: str) -> Dict[str, Any]:
        """Détecter le balisage Schema.org"""
        schema_types = {
            "Article": r'itemtype=["\']https?://schema\.org/Article["\']',
            "Person": r'itemtype=["\']https?://schema\.org/Person["\']',
            "Organization": r'itemtype=["\']https?://schema\.org/Organization["\']',
            "Product": r'itemtype=["\']https?://schema\.org/Product["\']',
            "Recipe": r'itemtype=["\']https?://schema\.org/Recipe["\']',
            "Event": r'itemtype=["\']https?://schema\.org/Event["\']'
        }
        
        detected_schemas = {}
        for schema_type, pattern in schema_types.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected_schemas[schema_type] = True
        
        # Also check for JSON-LD
        json_ld_pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        json_ld_scripts = re.findall(json_ld_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if json_ld_scripts:
            detected_schemas["JSON-LD"] = len(json_ld_scripts)
        
        return detected_schemas
    
    async def _generate_recommendations(
        self, 
        title: str, 
        content: str, 
        meta_description: str, 
        word_count: int,
        keyword_density: Dict[str, float],
        headings_structure: Dict[str, List[str]]
    ) -> List[str]:
        """Générer des recommandations SEO"""
        recommendations = []
        
        # Title recommendations
        if len(title) < 30:
            recommendations.append("Titre trop court - visez 50-60 caractères pour un meilleur SEO")
        elif len(title) > 60:
            recommendations.append("Titre trop long - risque de troncature dans les SERP")
        
        # Meta description recommendations
        if len(meta_description) < 120:
            recommendations.append("Meta description trop courte - visez 150-160 caractères")
        elif len(meta_description) > 160:
            recommendations.append("Meta description trop longue - risque de troncature")
        
        # Content length recommendations
        if word_count < 300:
            recommendations.append("Contenu trop court - visez au moins 500 mots pour un bon référencement")
        elif word_count > 3000:
            recommendations.append("Contenu très long - considérez diviser en plusieurs pages")
        
        # Keyword density recommendations
        max_density = max(keyword_density.values()) if keyword_density else 0
        if max_density > 5:
            recommendations.append("Densité de mots-clés trop élevée - risque de sur-optimisation")
        elif max_density < 0.5:
            recommendations.append("Densité de mots-clés faible - intégrez plus naturellement vos mots-clés cibles")
        
        # Heading structure recommendations
        if not headings_structure.get("h1"):
            recommendations.append("Aucun H1 détecté - ajoutez un titre principal")
        elif len(headings_structure.get("h1", [])) > 1:
            recommendations.append("Plusieurs H1 détectés - utilisez un seul H1 par page")
        
        if not headings_structure.get("h2"):
            recommendations.append("Aucun H2 détecté - structurez votre contenu avec des sous-titres")
        
        return recommendations
    
    async def _calculate_optimization_score(
        self,
        title: str,
        content: str,
        meta_description: str,
        word_count: int,
        readability_score: float,
        keyword_density: Dict[str, float],
        headings_structure: Dict[str, List[str]],
        internal_links: List[str],
        external_links: List[str]
    ) -> float:
        """Calculer le score d'optimisation global"""
        score = 0.0
        max_score = 100.0
        
        # Title score (15 points)
        title_score = 0
        if 30 <= len(title) <= 60:
            title_score = 15
        elif 20 <= len(title) < 30 or 60 < len(title) <= 70:
            title_score = 10
        else:
            title_score = 5
        score += title_score
        
        # Meta description score (10 points)
        meta_score = 0
        if 120 <= len(meta_description) <= 160:
            meta_score = 10
        elif 100 <= len(meta_description) < 120 or 160 < len(meta_description) <= 180:
            meta_score = 7
        else:
            meta_score = 3
        score += meta_score
        
        # Content length score (15 points)
        content_score = 0
        if 500 <= word_count <= 2000:
            content_score = 15
        elif 300 <= word_count < 500 or 2000 < word_count <= 3000:
            content_score = 10
        else:
            content_score = 5
        score += content_score
        
        # Readability score (20 points)
        if readability_score >= 60:
            score += 20
        elif readability_score >= 30:
            score += 15
        else:
            score += 10
        
        # Keyword density score (15 points)
        max_density = max(keyword_density.values()) if keyword_density else 0
        if 1 <= max_density <= 3:
            score += 15
        elif 0.5 <= max_density < 1 or 3 < max_density <= 5:
            score += 10
        else:
            score += 5
        
        # Heading structure score (15 points)
        heading_score = 0
        if headings_structure.get("h1") and len(headings_structure["h1"]) == 1:
            heading_score += 5
        if headings_structure.get("h2"):
            heading_score += 5
        if len(headings_structure.get("h3", [])) > 0:
            heading_score += 5
        score += heading_score
        
        # Link score (10 points)
        link_score = 0
        if len(internal_links) >= 2:
            link_score += 5
        if len(external_links) >= 1:
            link_score += 5
        score += link_score
        
        return round((score / max_score) * 100, 2)

class CompetitorAnalyzer:
    """Analyseur de concurrence"""
    
    def __init__(self):
        self.competitor_data: Dict[str, Dict[str, Any]] = {}
    
    async def analyze_competitors(self, competitors: List[str], target_keywords: List[str]) -> Dict[str, Any]:
        """Analyser la concurrence"""
        try:
            analysis_results = {}
            
            for competitor_url in competitors:
                competitor_analysis = await self._analyze_single_competitor(competitor_url, target_keywords)
                domain = urlparse(competitor_url).netloc
                analysis_results[domain] = competitor_analysis
            
            # Generate competitive insights
            insights = await self._generate_competitive_insights(analysis_results, target_keywords)
            
            return {
                "competitor_analysis": analysis_results,
                "competitive_insights": insights,
                "opportunities": await self._identify_opportunities(analysis_results),
                "threats": await self._identify_threats(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}")
            return {}
    
    async def _analyze_single_competitor(self, url: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyser un seul concurrent"""
        # Simulate competitor analysis (real implementation would scrape/use APIs)
        domain = urlparse(url).netloc
        
        return {
            "domain": domain,
            "estimated_traffic": hash(domain) % 100000 + 10000,
            "domain_authority": min(100, (hash(domain) % 80) + 20),
            "backlink_count": hash(domain) % 50000 + 1000,
            "top_keywords": target_keywords[:5],  # Simplified
            "content_gaps": ["long-form guides", "video content", "infographics"],
            "strengths": ["high domain authority", "consistent content", "good technical SEO"],
            "weaknesses": ["limited social presence", "slow page speed", "poor mobile optimization"]
        }
    
    async def _generate_competitive_insights(self, competitor_data: Dict[str, Dict[str, Any]], target_keywords: List[str]) -> List[str]:
        """Générer des insights compétitifs"""
        insights = []
        
        # Average domain authority
        avg_da = statistics.mean([data["domain_authority"] for data in competitor_data.values()])
        insights.append(f"Domain Authority moyenne des concurrents: {avg_da:.1f}")
        
        # Traffic distribution
        total_traffic = sum([data["estimated_traffic"] for data in competitor_data.values()])
        insights.append(f"Trafic total estimé des concurrents: {total_traffic:,}")
        
        # Common content gaps
        all_gaps = []
        for data in competitor_data.values():
            all_gaps.extend(data.get("content_gaps", []))
        
        common_gaps = Counter(all_gaps).most_common(3)
        if common_gaps:
            gap_list = ", ".join([gap[0] for gap in common_gaps])
            insights.append(f"Opportunités de contenu communes: {gap_list}")
        
        return insights
    
    async def _identify_opportunities(self, competitor_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identifier les opportunités"""
        opportunities = []
        
        # Low DA competitors
        low_da_competitors = [domain for domain, data in competitor_data.items() if data["domain_authority"] < 50]
        if low_da_competitors:
            opportunities.append(f"Concurrents avec faible autorité de domaine: {', '.join(low_da_competitors[:2])}")
        
        # Common weaknesses
        all_weaknesses = []
        for data in competitor_data.values():
            all_weaknesses.extend(data.get("weaknesses", []))
        
        common_weaknesses = Counter(all_weaknesses).most_common(2)
        for weakness, count in common_weaknesses:
            if count >= len(competitor_data) * 0.6:  # 60% of competitors
                opportunities.append(f"Faiblesse commune exploitable: {weakness}")
        
        return opportunities
    
    async def _identify_threats(self, competitor_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identifier les menaces"""
        threats = []
        
        # High DA competitors
        high_da_competitors = [
            (domain, data["domain_authority"]) 
            for domain, data in competitor_data.items() 
            if data["domain_authority"] > 70
        ]
        
        if high_da_competitors:
            highest_da = max(high_da_competitors, key=lambda x: x[1])
            threats.append(f"Concurrent avec très haute autorité: {highest_da[0]} (DA: {highest_da[1]})")
        
        # High traffic competitors
        high_traffic_competitors = [
            (domain, data["estimated_traffic"]) 
            for domain, data in competitor_data.items() 
            if data["estimated_traffic"] > 50000
        ]
        
        if high_traffic_competitors:
            highest_traffic = max(high_traffic_competitors, key=lambda x: x[1])
            threats.append(f"Concurrent avec trafic élevé: {highest_traffic[0]} ({highest_traffic[1]:,} visites)")
        
        return threats

class SEOOptimizationManager:
    """🔍 Gestionnaire d'Optimisation SEO Enterprise pour Creators"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.keyword_researcher = KeywordResearcher()
        self.content_analyzer = ContentAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.seo_strategies: Dict[str, SEOStrategy] = {}
        self.content_analyses: Dict[str, ContentSEOAnalysis] = {}
        self.optimization_queue: List[str] = []
        
        logger.info("🔍 SEO Optimization Manager initialized")
    
    async def create_seo_strategy(
        self,
        creator_id: str,
        target_keywords: List[str],
        content_topics: List[str],
        competitor_urls: List[str],
        goals: Dict[str, float],
        budget: float = 0.0
    ) -> Optional[SEOStrategy]:
        """Créer une stratégie SEO personnalisée"""
        try:
            strategy_id = str(uuid.uuid4())
            
            # Research keywords
            researched_keywords = await self.keyword_researcher.research_keywords(target_keywords, "general")
            optimized_keywords = [kw.keyword for kw in researched_keywords[:20]]
            
            # Analyze competitors
            competitor_analysis = await self.competitor_analyzer.analyze_competitors(competitor_urls, target_keywords)
            
            # Create timeline
            timeline = {
                "keyword_research": datetime.now() + timedelta(days=7),
                "content_creation": datetime.now() + timedelta(days=30),
                "optimization": datetime.now() + timedelta(days=60),
                "performance_review": datetime.now() + timedelta(days=90)
            }
            
            strategy = SEOStrategy(
                strategy_id=strategy_id,
                creator_id=creator_id,
                target_keywords=optimized_keywords,
                content_topics=content_topics,
                competitor_urls=competitor_urls,
                goals=goals,
                timeline=timeline,
                budget=budget
            )
            
            self.seo_strategies[strategy_id] = strategy
            
            # Store in Redis
            await self.redis_client.hset(
                f"seo:strategy:{strategy_id}",
                mapping={
                    "creator_id": creator_id,
                    "target_keywords": json.dumps(optimized_keywords),
                    "content_topics": json.dumps(content_topics),
                    "goals": json.dumps(goals),
                    "budget": str(budget),
                    "created_at": strategy.created_at.isoformat()
                }
            )
            
            logger.info(f"SEO strategy created: {strategy_id} for creator {creator_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating SEO strategy: {e}")
            return None
    
    async def analyze_content_seo(
        self,
        content_id: str,
        url: str,
        title: str,
        content: str,
        meta_description: str = "",
        target_keywords: List[str] = None
    ) -> Optional[ContentSEOAnalysis]:
        """Analyser le SEO d'un contenu"""
        try:
            # Analyze content
            analysis = await self.content_analyzer.analyze_content(
                content_id, url, title, content, meta_description
            )
            
            if not analysis:
                return None
            
            # Check target keyword optimization if provided
            if target_keywords:
                keyword_optimization = await self._analyze_keyword_optimization(content, title, target_keywords)
                analysis.performance_metrics[SEOMetricType.KEYWORD_RANKING] = keyword_optimization
            
            # Add to analyses
            self.content_analyses[content_id] = analysis
            
            # Store in Redis
            await self.redis_client.hset(
                f"seo:analysis:{content_id}",
                mapping={
                    "url": url,
                    "title": title,
                    "optimization_score": str(analysis.optimization_score),
                    "word_count": str(analysis.word_count),
                    "readability_score": str(analysis.readability_score),
                    "recommendations": json.dumps(analysis.recommendations),
                    "analyzed_at": analysis.created_at.isoformat()
                }
            )
            
            logger.info(f"Content SEO analysis completed: {content_id} (score: {analysis.optimization_score})")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content SEO: {e}")
            return None
    
    async def _analyze_keyword_optimization(self, content: str, title: str, target_keywords: List[str]) -> float:
        """Analyser l'optimisation des mots-clés cibles"""
        try:
            content_lower = content.lower()
            title_lower = title.lower()
            
            total_score = 0.0
            keyword_count = len(target_keywords)
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                score = 0.0
                
                # Check title optimization (40% weight)
                if keyword_lower in title_lower:
                    score += 40
                
                # Check content presence (30% weight)
                content_mentions = content_lower.count(keyword_lower)
                if content_mentions > 0:
                    # Optimal density: 1-3%
                    word_count = len(content.split())
                    density = (content_mentions / word_count) * 100
                    
                    if 1 <= density <= 3:
                        score += 30
                    elif 0.5 <= density < 1 or 3 < density <= 5:
                        score += 20
                    else:
                        score += 10
                
                # Check heading optimization (20% weight)
                headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
                for heading in headings:
                    if keyword_lower in heading.lower():
                        score += 20
                        break
                
                # Check meta optimization (10% weight)
                # This would be checked in actual meta description analysis
                score += 5  # Partial credit for demonstration
                
                total_score += min(100, score)
            
            return round(total_score / keyword_count, 2) if keyword_count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing keyword optimization: {e}")
            return 0.0
    
    async def optimize_content_automatically(self, content_id: str) -> Dict[str, Any]:
        """Optimiser automatiquement le contenu"""
        try:
            if content_id not in self.content_analyses:
                return {"error": "Content analysis not found"}
            
            analysis = self.content_analyses[content_id]
            optimizations = []
            
            # Title optimization
            if len(analysis.title) < 30:
                optimizations.append({
                    "type": "title",
                    "issue": "Title too short",
                    "suggestion": f"Extend title to 50-60 characters (current: {len(analysis.title)})",
                    "priority": "high"
                })
            
            # Meta description optimization
            if len(analysis.meta_description) < 120:
                optimizations.append({
                    "type": "meta_description",
                    "issue": "Meta description too short",
                    "suggestion": f"Extend to 150-160 characters (current: {len(analysis.meta_description)})",
                    "priority": "high"
                })
            
            # Content length optimization
            if analysis.word_count < 500:
                optimizations.append({
                    "type": "content_length",
                    "issue": "Content too short",
                    "suggestion": f"Add {500 - analysis.word_count} more words for better SEO",
                    "priority": "medium"
                })
            
            # Heading structure optimization
            if not analysis.headings_structure.get("h1"):
                optimizations.append({
                    "type": "headings",
                    "issue": "Missing H1 tag",
                    "suggestion": "Add a main H1 heading",
                    "priority": "high"
                })
            
            # Image optimization
            images_without_alt = sum(1 for img in analysis.images.values() if not img["has_alt"])
            if images_without_alt > 0:
                optimizations.append({
                    "type": "images",
                    "issue": f"{images_without_alt} images missing alt text",
                    "suggestion": "Add descriptive alt text to all images",
                    "priority": "medium"
                })
            
            # Internal linking optimization
            if len(analysis.internal_links) < 2:
                optimizations.append({
                    "type": "internal_links",
                    "issue": "Few internal links",
                    "suggestion": "Add 2-3 relevant internal links",
                    "priority": "low"
                })
            
            # Add to optimization queue
            if content_id not in self.optimization_queue:
                self.optimization_queue.append(content_id)
            
            result = {
                "content_id": content_id,
                "current_score": analysis.optimization_score,
                "potential_improvements": len(optimizations),
                "optimizations": optimizations,
                "estimated_score_improvement": self._estimate_score_improvement(optimizations)
            }
            
            logger.info(f"Automatic optimization analysis completed for {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing content automatically: {e}")
            return {"error": str(e)}
    
    def _estimate_score_improvement(self, optimizations: List[Dict[str, Any]]) -> float:
        """Estimer l'amélioration du score"""
        improvement = 0.0
        
        priority_weights = {
            "high": 15.0,
            "medium": 10.0,
            "low": 5.0
        }
        
        for optimization in optimizations:
            priority = optimization.get("priority", "low")
            improvement += priority_weights.get(priority, 5.0)
        
        return round(min(30.0, improvement), 1)  # Cap at 30 points improvement
    
    async def track_keyword_rankings(self, strategy_id: str, keywords: List[str]) -> Dict[str, Any]:
        """Suivre le classement des mots-clés"""
        try:
            if strategy_id not in self.seo_strategies:
                return {"error": "Strategy not found"}
            
            # Simulate ranking tracking (real implementation would use ranking APIs)
            rankings = {}
            
            for keyword in keywords:
                # Simulate position tracking over time
                current_position = max(1, (hash(keyword) % 50) + 1)
                previous_position = current_position + (hash(f"{keyword}_prev") % 10) - 5
                
                rankings[keyword] = {
                    "current_position": current_position,
                    "previous_position": max(1, previous_position),
                    "change": previous_position - current_position,
                    "search_volume": hash(keyword) % 10000 + 1000,
                    "url_ranking": f"https://example.com/page-{hash(keyword) % 10}",
                    "last_updated": datetime.now().isoformat()
                }
            
            # Store rankings in Redis
            await self.redis_client.hset(
                f"seo:rankings:{strategy_id}",
                mapping={
                    "rankings": json.dumps(rankings, default=str),
                    "last_check": datetime.now().isoformat()
                }
            )
            
            # Calculate summary metrics
            avg_position = statistics.mean([r["current_position"] for r in rankings.values()])
            improved_keywords = len([r for r in rankings.values() if r["change"] > 0])
            declined_keywords = len([r for r in rankings.values() if r["change"] < 0])
            
            summary = {
                "strategy_id": strategy_id,
                "total_keywords": len(keywords),
                "average_position": round(avg_position, 1),
                "improved_keywords": improved_keywords,
                "declined_keywords": declined_keywords,
                "stable_keywords": len(keywords) - improved_keywords - declined_keywords,
                "rankings": rankings
            }
            
            logger.info(f"Keyword rankings tracked for strategy {strategy_id}: avg position {avg_position:.1f}")
            return summary
            
        except Exception as e:
            logger.error(f"Error tracking keyword rankings: {e}")
            return {"error": str(e)}
    
    async def generate_seo_report(self, creator_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Générer un rapport SEO complet"""
        try:
            # Get creator's strategies
            creator_strategies = [
                strategy for strategy in self.seo_strategies.values() 
                if strategy.creator_id == creator_id
            ]
            
            # Get creator's content analyses
            creator_analyses = [
                analysis for analysis in self.content_analyses.values()
                if analysis.created_at >= datetime.now() - timedelta(days=period_days)
            ]
            
            if not creator_strategies and not creator_analyses:
                return {"error": "No SEO data found for creator"}
            
            # Calculate metrics
            avg_optimization_score = statistics.mean([a.optimization_score for a in creator_analyses]) if creator_analyses else 0
            total_content_analyzed = len(creator_analyses)
            
            # Content performance distribution
            score_distribution = {
                "excellent": len([a for a in creator_analyses if a.optimization_score >= 80]),
                "good": len([a for a in creator_analyses if 60 <= a.optimization_score < 80]),
                "needs_improvement": len([a for a in creator_analyses if a.optimization_score < 60])
            }
            
            # Top performing content
            top_content = sorted(creator_analyses, key=lambda x: x.optimization_score, reverse=True)[:5]
            
            # Common recommendations
            all_recommendations = []
            for analysis in creator_analyses:
                all_recommendations.extend(analysis.recommendations)
            
            common_recommendations = Counter(all_recommendations).most_common(5)
            
            # Strategy progress
            strategy_progress = []
            for strategy in creator_strategies:
                days_since_creation = (datetime.now() - strategy.created_at).days
                progress_percentage = min(100, (days_since_creation / 90) * 100)  # 90-day strategy
                
                strategy_progress.append({
                    "strategy_id": strategy.strategy_id,
                    "target_keywords": len(strategy.target_keywords),
                    "progress": round(progress_percentage, 1),
                    "status": strategy.status
                })
            
            report = {
                "creator_id": creator_id,
                "report_period": f"{period_days} days",
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_strategies": len(creator_strategies),
                    "total_content_analyzed": total_content_analyzed,
                    "average_optimization_score": round(avg_optimization_score, 2),
                    "score_distribution": score_distribution
                },
                "top_performing_content": [
                    {
                        "content_id": content.content_id,
                        "title": content.title,
                        "optimization_score": content.optimization_score,
                        "word_count": content.word_count
                    } for content in top_content
                ],
                "common_recommendations": [
                    {"recommendation": rec[0], "frequency": rec[1]} 
                    for rec in common_recommendations
                ],
                "strategy_progress": strategy_progress,
                "next_actions": await self._generate_next_actions(creator_analyses, creator_strategies)
            }
            
            logger.info(f"SEO report generated for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating SEO report: {e}")
            return {"error": str(e)}
    
    async def _generate_next_actions(self, analyses: List[ContentSEOAnalysis], strategies: List[SEOStrategy]) -> List[str]:
        """Générer les prochaines actions recommandées"""
        actions = []
        
        if analyses:
            avg_score = statistics.mean([a.optimization_score for a in analyses])
            
            if avg_score < 60:
                actions.append("Priorité haute: Optimiser le contenu existant (score moyen faible)")
            
            # Check for common issues
            low_word_count = len([a for a in analyses if a.word_count < 500])
            if low_word_count > len(analyses) * 0.5:
                actions.append("Étendre le contenu: 50%+ des articles sont trop courts")
            
            missing_meta = len([a for a in analyses if len(a.meta_description) < 120])
            if missing_meta > 0:
                actions.append(f"Optimiser les meta descriptions: {missing_meta} contenus nécessitent des améliorations")
        
        if strategies:
            active_strategies = [s for s in strategies if s.status == "active"]
            if len(active_strategies) < 2:
                actions.append("Développer des stratégies SEO: Créer plus de stratégies ciblées")
        
        if not actions:
            actions.append("Continuer l'optimisation: Maintenir la qualité SEO actuelle")
        
        return actions

# Export
__all__ = [
    'SEOOptimizationManager',
    'SEOMetricType',
    'ContentType',
    'SearchEngine',
    'KeywordData',
    'ContentSEOAnalysis',
    'SEOStrategy'
]