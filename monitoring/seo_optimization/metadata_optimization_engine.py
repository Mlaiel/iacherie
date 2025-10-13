"""
Metadata Optimization Engine - SEO Optimization Module
=====================================================

Advanced metadata optimization engine for maximizing search visibility
and discoverability across all platforms with AI-powered optimization.

Features:
- Intelligent metadata analysis and optimization
- Platform-specific metadata adaptation
- Keyword density and semantic optimization
- Meta tag generation and optimization
- Schema markup implementation
- Multilingual metadata optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import re
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class MetadataType(Enum):
    """Types of metadata for optimization"""
    TITLE = "title"
    DESCRIPTION = "description"
    KEYWORDS = "keywords"
    TAGS = "tags"
    HASHTAGS = "hashtags"
    THUMBNAIL_ALT = "thumbnail_alt"
    CATEGORIES = "categories"
    SCHEMA_MARKUP = "schema_markup"
    META_TAGS = "meta_tags"

class OptimizationLevel(Enum):
    """Optimization intensity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class PlatformRequirement(Enum):
    """Platform-specific requirements"""
    YOUTUBE_TITLE_MAX = 100
    INSTAGRAM_CAPTION_MAX = 2200
    TIKTOK_DESCRIPTION_MAX = 150
    TWITTER_TEXT_MAX = 280
    LINKEDIN_POST_MAX = 3000

@dataclass
class MetadataOptimization:
    """Metadata optimization recommendation"""
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    platform: str = ""
    metadata_type: MetadataType = MetadataType.TITLE
    
    # Original vs optimized
    original_value: str = ""
    optimized_value: str = ""
    improvement_score: float = 0.0
    
    # Optimization details
    optimization_reasons: List[str] = field(default_factory=list)
    keyword_improvements: Dict[str, float] = field(default_factory=dict)
    readability_score: float = 0.0
    seo_score: float = 0.0
    
    # Performance prediction
    expected_visibility_increase: float = 0.0
    expected_click_increase: float = 0.0
    confidence_score: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    applied: bool = False

@dataclass
class KeywordAnalysis:
    """Keyword analysis and optimization"""
    keyword: str = ""
    search_volume: int = 0
    competition_level: float = 0.0
    relevance_score: float = 0.0
    current_density: float = 0.0
    optimal_density: float = 0.0
    suggested_placement: List[str] = field(default_factory=list)
    semantic_variations: List[str] = field(default_factory=list)

@dataclass
class MetadataQualityScore:
    """Comprehensive metadata quality assessment"""
    content_id: str = ""
    platform: str = ""
    overall_score: float = 0.0
    
    # Individual scores
    title_score: float = 0.0
    description_score: float = 0.0
    keyword_score: float = 0.0
    readability_score: float = 0.0
    length_score: float = 0.0
    uniqueness_score: float = 0.0
    
    # Improvement areas
    improvement_areas: List[str] = field(default_factory=list)
    optimization_potential: float = 0.0
    
    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)

class MetadataOptimizationEngine:
    """Main metadata optimization engine"""
    
    def __init__(self):
        self.optimizations: List[MetadataOptimization] = []
        self.quality_scores: List[MetadataQualityScore] = []
        self.keyword_database = self._initialize_keyword_database()
        self.platform_requirements = self._initialize_platform_requirements()
        self.optimization_rules = self._initialize_optimization_rules()
        
    def _initialize_keyword_database(self) -> Dict[str, KeywordAnalysis]:
        """Initialize keyword database with popular terms"""
        keywords = {
            # Entertainment keywords
            "viral": KeywordAnalysis(
                keyword="viral",
                search_volume=500000,
                competition_level=0.8,
                relevance_score=0.9,
                optimal_density=0.02,
                suggested_placement=["title", "description", "tags"],
                semantic_variations=["trending", "popular", "hit", "sensation"]
            ),
            "music": KeywordAnalysis(
                keyword="music",
                search_volume=1000000,
                competition_level=0.9,
                relevance_score=0.8,
                optimal_density=0.03,
                suggested_placement=["title", "description", "tags"],
                semantic_variations=["song", "track", "audio", "melody", "beats"]
            ),
            "tutorial": KeywordAnalysis(
                keyword="tutorial",
                search_volume=800000,
                competition_level=0.7,
                relevance_score=0.9,
                optimal_density=0.025,
                suggested_placement=["title", "description"],
                semantic_variations=["how-to", "guide", "learn", "tips", "instructions"]
            ),
            "review": KeywordAnalysis(
                keyword="review",
                search_volume=600000,
                competition_level=0.6,
                relevance_score=0.8,
                optimal_density=0.02,
                suggested_placement=["title", "description"],
                semantic_variations=["analysis", "opinion", "rating", "evaluation"]
            ),
            "gaming": KeywordAnalysis(
                keyword="gaming",
                search_volume=900000,
                competition_level=0.8,
                relevance_score=0.9,
                optimal_density=0.03,
                suggested_placement=["title", "description", "tags"],
                semantic_variations=["gameplay", "game", "esports", "streamer"]
            )
        }
        
        return keywords
        
    def _initialize_platform_requirements(self) -> Dict[str, Dict[MetadataType, Dict[str, Any]]]:
        """Initialize platform-specific metadata requirements"""
        return {
            "youtube": {
                MetadataType.TITLE: {
                    "max_length": 100,
                    "min_length": 10,
                    "optimal_length": 60,
                    "keyword_positions": [0, 1, 2],  # First 3 words most important
                    "capitalization": "title_case"
                },
                MetadataType.DESCRIPTION: {
                    "max_length": 5000,
                    "min_length": 125,
                    "optimal_length": 200,
                    "keyword_density": 0.02,
                    "call_to_action": True
                },
                MetadataType.TAGS: {
                    "max_count": 15,
                    "max_length_per_tag": 100,
                    "optimal_count": 10,
                    "keyword_focus": True
                }
            },
            "instagram": {
                MetadataType.TITLE: {
                    "max_length": 65,
                    "optimal_length": 50,
                    "emoji_allowed": True,
                    "capitalization": "sentence_case"
                },
                MetadataType.DESCRIPTION: {
                    "max_length": 2200,
                    "optimal_length": 125,
                    "hashtag_integration": True,
                    "emoji_encouraged": True
                },
                MetadataType.HASHTAGS: {
                    "max_count": 30,
                    "optimal_count": 15,
                    "trending_focus": True,
                    "niche_mix": True
                }
            },
            "tiktok": {
                MetadataType.TITLE: {
                    "max_length": 150,
                    "optimal_length": 100,
                    "trending_terms": True,
                    "hook_required": True
                },
                MetadataType.DESCRIPTION: {
                    "max_length": 2200,
                    "optimal_length": 100,
                    "hashtag_integration": True,
                    "challenge_tags": True
                }
            }
        }
        
    def _initialize_optimization_rules(self) -> Dict[str, Any]:
        """Initialize optimization rules and best practices"""
        return {
            "title_optimization": {
                "include_primary_keyword": True,
                "keyword_front_loading": True,
                "emotional_words": ["amazing", "incredible", "ultimate", "secret"],
                "power_words": ["how", "why", "what", "best", "top", "guide"],
                "avoid_clickbait": True,
                "length_optimization": True
            },
            "description_optimization": {
                "keyword_density_range": (0.01, 0.03),
                "semantic_keywords": True,
                "call_to_action": True,
                "social_proof": True,
                "structure_paragraphs": True
            },
            "keyword_optimization": {
                "primary_keyword_count": 1,
                "secondary_keyword_count": 3,
                "long_tail_keywords": True,
                "semantic_variations": True,
                "keyword_cannibalization_check": True
            },
            "readability": {
                "min_readability_score": 60,
                "optimal_readability_score": 70,
                "sentence_length_max": 20,
                "paragraph_length_max": 3
            }
        }
        
    async def analyze_metadata_quality(self, 
                                     content_id: str,
                                     platform: str,
                                     metadata: Dict[str, str]) -> MetadataQualityScore:
        """Analyze metadata quality and provide comprehensive scoring"""
        
        # Analyze individual components
        title_score = await self._analyze_title_quality(metadata.get("title", ""), platform)
        description_score = await self._analyze_description_quality(metadata.get("description", ""), platform)
        keyword_score = await self._analyze_keyword_optimization(metadata, platform)
        readability_score = await self._calculate_readability_score(metadata)
        length_score = await self._analyze_length_optimization(metadata, platform)
        uniqueness_score = await self._analyze_uniqueness(metadata, platform)
        
        # Calculate overall score
        weights = {
            "title": 0.25,
            "description": 0.20,
            "keywords": 0.20,
            "readability": 0.15,
            "length": 0.10,
            "uniqueness": 0.10
        }
        
        overall_score = (
            title_score * weights["title"] +
            description_score * weights["description"] +
            keyword_score * weights["keywords"] +
            readability_score * weights["readability"] +
            length_score * weights["length"] +
            uniqueness_score * weights["uniqueness"]
        )
        
        # Identify improvement areas
        improvement_areas = []
        if title_score < 0.7:
            improvement_areas.append("title_optimization")
        if description_score < 0.7:
            improvement_areas.append("description_enhancement")
        if keyword_score < 0.7:
            improvement_areas.append("keyword_optimization")
        if readability_score < 0.6:
            improvement_areas.append("readability_improvement")
            
        # Calculate optimization potential
        max_possible_score = 1.0
        optimization_potential = max_possible_score - overall_score
        
        quality_score = MetadataQualityScore(
            content_id=content_id,
            platform=platform,
            overall_score=overall_score,
            title_score=title_score,
            description_score=description_score,
            keyword_score=keyword_score,
            readability_score=readability_score,
            length_score=length_score,
            uniqueness_score=uniqueness_score,
            improvement_areas=improvement_areas,
            optimization_potential=optimization_potential
        )
        
        self.quality_scores.append(quality_score)
        logger.info(f"Analyzed metadata quality for {content_id}: {overall_score:.2f}")
        
        return quality_score
        
    async def _analyze_title_quality(self, title: str, platform: str) -> float:
        """Analyze title quality and SEO optimization"""
        if not title:
            return 0.0
            
        score = 0.0
        platform_reqs = self.platform_requirements.get(platform, {}).get(MetadataType.TITLE, {})
        
        # Length optimization
        max_length = platform_reqs.get("max_length", 100)
        optimal_length = platform_reqs.get("optimal_length", 60)
        
        if len(title) <= max_length:
            if len(title) >= optimal_length * 0.8:
                score += 0.3
            else:
                score += 0.15
        else:
            score += 0.0  # Too long
            
        # Keyword presence
        title_lower = title.lower()
        keyword_found = False
        for keyword in self.keyword_database.keys():
            if keyword in title_lower:
                score += 0.2
                keyword_found = True
                break
                
        if not keyword_found:
            # Check for semantic variations
            for keyword_data in self.keyword_database.values():
                for variation in keyword_data.semantic_variations:
                    if variation in title_lower:
                        score += 0.1
                        break
                        
        # Power words and emotional triggers
        power_words = self.optimization_rules["title_optimization"]["power_words"]
        emotional_words = self.optimization_rules["title_optimization"]["emotional_words"]
        
        for word in power_words:
            if word in title_lower:
                score += 0.1
                break
                
        for word in emotional_words:
            if word in title_lower:
                score += 0.1
                break
                
        # Readability and structure
        word_count = len(title.split())
        if 5 <= word_count <= 12:  # Optimal word count
            score += 0.2
        elif word_count > 15:
            score -= 0.1
            
        # Capitalization check
        if title.isupper():
            score -= 0.1  # ALL CAPS is bad
        elif title.istitle() or title[0].isupper():
            score += 0.1
            
        return min(1.0, score)
        
    async def _analyze_description_quality(self, description: str, platform: str) -> float:
        """Analyze description quality and optimization"""
        if not description:
            return 0.0
            
        score = 0.0
        platform_reqs = self.platform_requirements.get(platform, {}).get(MetadataType.DESCRIPTION, {})
        
        # Length optimization
        max_length = platform_reqs.get("max_length", 5000)
        optimal_length = platform_reqs.get("optimal_length", 200)
        
        if len(description) <= max_length:
            if len(description) >= optimal_length * 0.8:
                score += 0.25
            else:
                score += 0.15
                
        # Keyword density analysis
        word_count = len(description.split())
        keyword_density = 0
        description_lower = description.lower()
        
        for keyword in self.keyword_database.keys():
            keyword_count = description_lower.count(keyword)
            if keyword_count > 0:
                density = keyword_count / word_count
                optimal_density = self.keyword_database[keyword].optimal_density
                
                if 0.5 * optimal_density <= density <= 1.5 * optimal_density:
                    score += 0.2
                elif density > 2 * optimal_density:
                    score -= 0.1  # Keyword stuffing penalty
                    
        # Call to action presence
        cta_phrases = ["subscribe", "like", "comment", "share", "follow", "click", "watch", "listen"]
        for cta in cta_phrases:
            if cta in description_lower:
                score += 0.1
                break
                
        # Structure and readability
        sentences = description.split('.')
        if len(sentences) > 1:  # Multiple sentences
            score += 0.1
            
        # Paragraph structure (if contains line breaks)
        if '\n' in description:
            score += 0.1
            
        return min(1.0, score)
        
    async def _analyze_keyword_optimization(self, metadata: Dict[str, str], platform: str) -> float:
        """Analyze keyword optimization across all metadata"""
        score = 0.0
        
        # Combine all text for analysis
        all_text = " ".join([
            metadata.get("title", ""),
            metadata.get("description", ""),
            " ".join(metadata.get("tags", [])) if isinstance(metadata.get("tags"), list) else metadata.get("tags", "")
        ]).lower()
        
        if not all_text.strip():
            return 0.0
            
        word_count = len(all_text.split())
        
        # Primary keyword analysis
        primary_keywords_found = 0
        for keyword, keyword_data in self.keyword_database.items():
            if keyword in all_text:
                keyword_count = all_text.count(keyword)
                density = keyword_count / word_count
                
                # Check if density is in optimal range
                if keyword_data.optimal_density * 0.5 <= density <= keyword_data.optimal_density * 2:
                    score += 0.15
                    primary_keywords_found += 1
                    
        # Semantic keyword analysis
        semantic_score = 0
        for keyword_data in self.keyword_database.values():
            for variation in keyword_data.semantic_variations:
                if variation in all_text:
                    semantic_score += 0.05
                    
        score += min(0.3, semantic_score)
        
        # Long-tail keyword presence
        long_tail_phrases = [
            "how to", "what is", "best way", "step by step", "complete guide"
        ]
        for phrase in long_tail_phrases:
            if phrase in all_text:
                score += 0.1
                break
                
        # Keyword distribution across metadata types
        title_has_keyword = any(keyword in metadata.get("title", "").lower() 
                               for keyword in self.keyword_database.keys())
        description_has_keyword = any(keyword in metadata.get("description", "").lower() 
                                    for keyword in self.keyword_database.keys())
        
        if title_has_keyword:
            score += 0.2
        if description_has_keyword:
            score += 0.1
            
        return min(1.0, score)
        
    async def _calculate_readability_score(self, metadata: Dict[str, str]) -> float:
        """Calculate readability score using Flesch Reading Ease approximation"""
        combined_text = metadata.get("description", "") + " " + metadata.get("title", "")
        
        if not combined_text.strip():
            return 0.0
            
        # Simple readability calculation
        sentences = len([s for s in combined_text.split('.') if s.strip()])
        words = len(combined_text.split())
        syllables = self._count_syllables(combined_text)
        
        if sentences == 0 or words == 0:
            return 0.0
            
        # Simplified Flesch Reading Ease formula
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale (60-100 is good readability)
        normalized_score = max(0, min(1, (flesch_score - 30) / 70))
        
        return normalized_score
        
    def _count_syllables(self, text: str) -> int:
        """Approximate syllable count"""
        # Simple syllable counting heuristic
        vowels = "aeiouy"
        text = text.lower()
        syllable_count = 0
        
        for word in text.split():
            word = re.sub(r'[^a-z]', '', word)
            if not word:
                continue
                
            # Count vowel groups
            prev_was_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = is_vowel
                
            # Adjust for silent e
            if word.endswith('e') and syllable_count > 1:
                syllable_count -= 1
                
            # Ensure minimum of 1 syllable per word
            if syllable_count == 0:
                syllable_count = 1
                
        return syllable_count
        
    async def _analyze_length_optimization(self, metadata: Dict[str, str], platform: str) -> float:
        """Analyze length optimization for platform requirements"""
        score = 0.0
        platform_reqs = self.platform_requirements.get(platform, {})
        
        # Title length
        title = metadata.get("title", "")
        title_reqs = platform_reqs.get(MetadataType.TITLE, {})
        if title_reqs:
            optimal_length = title_reqs.get("optimal_length", 60)
            max_length = title_reqs.get("max_length", 100)
            
            if len(title) <= max_length:
                if optimal_length * 0.8 <= len(title) <= optimal_length * 1.2:
                    score += 0.5
                else:
                    score += 0.25
                    
        # Description length
        description = metadata.get("description", "")
        desc_reqs = platform_reqs.get(MetadataType.DESCRIPTION, {})
        if desc_reqs:
            optimal_length = desc_reqs.get("optimal_length", 200)
            max_length = desc_reqs.get("max_length", 5000)
            
            if len(description) <= max_length:
                if optimal_length * 0.8 <= len(description) <= optimal_length * 1.5:
                    score += 0.5
                else:
                    score += 0.25
                    
        return min(1.0, score)
        
    async def _analyze_uniqueness(self, metadata: Dict[str, str], platform: str) -> float:
        """Analyze metadata uniqueness (simplified implementation)"""
        # In a real implementation, this would check against a database of existing content
        # For now, return a baseline score based on length and complexity
        
        title = metadata.get("title", "")
        description = metadata.get("description", "")
        
        uniqueness_score = 0.0
        
        # Check for generic/template-like phrases
        generic_phrases = [
            "check out", "don't forget to", "like and subscribe",
            "click here", "watch now", "amazing video"
        ]
        
        combined_text = (title + " " + description).lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in combined_text)
        
        if generic_count == 0:
            uniqueness_score += 0.4
        elif generic_count <= 2:
            uniqueness_score += 0.2
            
        # Length-based uniqueness (longer content is typically more unique)
        if len(combined_text) > 200:
            uniqueness_score += 0.3
        elif len(combined_text) > 100:
            uniqueness_score += 0.2
            
        # Word variety (simplified measure)
        words = combined_text.split()
        unique_words = set(words)
        if len(words) > 0:
            word_variety = len(unique_words) / len(words)
            uniqueness_score += word_variety * 0.3
            
        return min(1.0, uniqueness_score)
        
    async def optimize_metadata(self, 
                              content_id: str,
                              platform: str,
                              metadata: Dict[str, str],
                              optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED) -> List[MetadataOptimization]:
        """Generate comprehensive metadata optimizations"""
        
        optimizations = []
        
        # Optimize title
        if "title" in metadata:
            title_optimization = await self._optimize_title(
                content_id, platform, metadata["title"], optimization_level
            )
            if title_optimization:
                optimizations.append(title_optimization)
                
        # Optimize description
        if "description" in metadata:
            description_optimization = await self._optimize_description(
                content_id, platform, metadata["description"], optimization_level
            )
            if description_optimization:
                optimizations.append(description_optimization)
                
        # Optimize keywords/tags
        if "tags" in metadata or "keywords" in metadata:
            keyword_optimization = await self._optimize_keywords(
                content_id, platform, metadata, optimization_level
            )
            if keyword_optimization:
                optimizations.append(keyword_optimization)
                
        # Store optimizations
        self.optimizations.extend(optimizations)
        
        logger.info(f"Generated {len(optimizations)} optimizations for {content_id}")
        return optimizations
        
    async def _optimize_title(self, 
                            content_id: str,
                            platform: str,
                            original_title: str,
                            optimization_level: OptimizationLevel) -> Optional[MetadataOptimization]:
        """Optimize title for SEO and platform requirements"""
        
        platform_reqs = self.platform_requirements.get(platform, {}).get(MetadataType.TITLE, {})
        max_length = platform_reqs.get("max_length", 100)
        optimal_length = platform_reqs.get("optimal_length", 60)
        
        # Start with original title
        optimized_title = original_title.strip()
        optimization_reasons = []
        keyword_improvements = {}
        
        # Add primary keyword if missing
        title_lower = optimized_title.lower()
        primary_keyword = None
        
        for keyword, keyword_data in self.keyword_database.items():
            if keyword_data.relevance_score > 0.8:  # High relevance keywords
                if keyword not in title_lower:
                    # Try to add keyword at the beginning
                    optimized_title = f"{keyword.title()} {optimized_title}"
                    optimization_reasons.append(f"Added primary keyword '{keyword}'")
                    keyword_improvements[keyword] = 0.3
                    primary_keyword = keyword
                    break
                    
        # Optimize length
        if len(optimized_title) > max_length:
            # Truncate intelligently
            words = optimized_title.split()
            truncated_words = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= max_length - 3:  # Leave space for "..."
                    truncated_words.append(word)
                    current_length += len(word) + 1
                else:
                    break
                    
            optimized_title = " ".join(truncated_words) + "..."
            optimization_reasons.append("Truncated to meet platform length requirements")
            
        # Add power words if optimization level is advanced
        if optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
            power_words = self.optimization_rules["title_optimization"]["power_words"]
            title_words = optimized_title.lower().split()
            
            if not any(pw in title_words for pw in power_words):
                # Try to add a relevant power word
                if "how" not in title_words and len(optimized_title) + 4 <= max_length:
                    optimized_title = f"How {optimized_title}"
                    optimization_reasons.append("Added power word 'How'")
                    
        # Calculate improvement scores
        original_score = await self._analyze_title_quality(original_title, platform)
        optimized_score = await self._analyze_title_quality(optimized_title, platform)
        improvement_score = optimized_score - original_score
        
        if improvement_score > 0.05:  # Only suggest if meaningful improvement
            return MetadataOptimization(
                content_id=content_id,
                platform=platform,
                metadata_type=MetadataType.TITLE,
                original_value=original_title,
                optimized_value=optimized_title,
                improvement_score=improvement_score,
                optimization_reasons=optimization_reasons,
                keyword_improvements=keyword_improvements,
                seo_score=optimized_score,
                expected_visibility_increase=improvement_score * 0.5,
                expected_click_increase=improvement_score * 0.3,
                confidence_score=0.8
            )
            
        return None
        
    async def _optimize_description(self, 
                                  content_id: str,
                                  platform: str,
                                  original_description: str,
                                  optimization_level: OptimizationLevel) -> Optional[MetadataOptimization]:
        """Optimize description for SEO and engagement"""
        
        platform_reqs = self.platform_requirements.get(platform, {}).get(MetadataType.DESCRIPTION, {})
        max_length = platform_reqs.get("max_length", 5000)
        optimal_length = platform_reqs.get("optimal_length", 200)
        
        optimized_description = original_description.strip()
        optimization_reasons = []
        keyword_improvements = {}
        
        # Keyword optimization
        description_lower = optimized_description.lower()
        
        for keyword, keyword_data in self.keyword_database.items():
            current_count = description_lower.count(keyword)
            word_count = len(optimized_description.split())
            current_density = current_count / word_count if word_count > 0 else 0
            
            if current_density < keyword_data.optimal_density * 0.5:
                # Add keyword naturally
                if len(optimized_description) + len(keyword) + 10 <= max_length:
                    optimized_description += f" {keyword.title()}"
                    optimization_reasons.append(f"Added keyword '{keyword}' for better SEO")
                    keyword_improvements[keyword] = 0.2
                    
        # Add call to action if missing
        cta_phrases = ["subscribe", "like", "comment", "share", "follow"]
        has_cta = any(cta in description_lower for cta in cta_phrases)
        
        if not has_cta and optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
            if len(optimized_description) + 50 <= max_length:
                optimized_description += "\n\nDon't forget to like and subscribe for more content!"
                optimization_reasons.append("Added call-to-action for engagement")
                
        # Improve readability with paragraph breaks
        if "\n" not in optimized_description and len(optimized_description) > 100:
            sentences = optimized_description.split('. ')
            if len(sentences) > 2:
                mid_point = len(sentences) // 2
                optimized_description = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
                optimization_reasons.append("Added paragraph breaks for better readability")
                
        # Calculate improvement scores
        original_score = await self._analyze_description_quality(original_description, platform)
        optimized_score = await self._analyze_description_quality(optimized_description, platform)
        improvement_score = optimized_score - original_score
        
        if improvement_score > 0.05:
            return MetadataOptimization(
                content_id=content_id,
                platform=platform,
                metadata_type=MetadataType.DESCRIPTION,
                original_value=original_description,
                optimized_value=optimized_description,
                improvement_score=improvement_score,
                optimization_reasons=optimization_reasons,
                keyword_improvements=keyword_improvements,
                seo_score=optimized_score,
                expected_visibility_increase=improvement_score * 0.4,
                expected_click_increase=improvement_score * 0.2,
                confidence_score=0.7
            )
            
        return None
        
    async def _optimize_keywords(self, 
                               content_id: str,
                               platform: str,
                               metadata: Dict[str, str],
                               optimization_level: OptimizationLevel) -> Optional[MetadataOptimization]:
        """Optimize keywords and tags"""
        
        original_tags = metadata.get("tags", [])
        if isinstance(original_tags, str):
            original_tags = [tag.strip() for tag in original_tags.split(",")]
            
        platform_reqs = self.platform_requirements.get(platform, {}).get(MetadataType.TAGS, {})
        max_count = platform_reqs.get("max_count", 15)
        optimal_count = platform_reqs.get("optimal_count", 10)
        
        optimized_tags = list(original_tags)
        optimization_reasons = []
        keyword_improvements = {}
        
        # Add high-value keywords as tags
        for keyword, keyword_data in self.keyword_database.items():
            if keyword_data.relevance_score > 0.7 and keyword not in [tag.lower() for tag in optimized_tags]:
                if len(optimized_tags) < max_count:
                    optimized_tags.append(keyword.title())
                    optimization_reasons.append(f"Added high-value keyword '{keyword}'")
                    keyword_improvements[keyword] = 0.25
                    
        # Add semantic variations
        if optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
            for keyword_data in self.keyword_database.values():
                for variation in keyword_data.semantic_variations[:2]:  # Add top 2 variations
                    if variation not in [tag.lower() for tag in optimized_tags] and len(optimized_tags) < max_count:
                        optimized_tags.append(variation.title())
                        optimization_reasons.append(f"Added semantic variation '{variation}'")
                        
        # Remove duplicate or very similar tags
        unique_tags = []
        for tag in optimized_tags:
            if not any(tag.lower() in existing.lower() or existing.lower() in tag.lower() 
                      for existing in unique_tags):
                unique_tags.append(tag)
                
        optimized_tags = unique_tags[:max_count]
        
        # Calculate improvement
        original_tag_string = ", ".join(original_tags)
        optimized_tag_string = ", ".join(optimized_tags)
        
        improvement_score = len(optimized_tags) / max(len(original_tags), 1) if original_tags else 1.0
        improvement_score = min(improvement_score, 1.0)
        
        if len(optimized_tags) > len(original_tags) or keyword_improvements:
            return MetadataOptimization(
                content_id=content_id,
                platform=platform,
                metadata_type=MetadataType.TAGS,
                original_value=original_tag_string,
                optimized_value=optimized_tag_string,
                improvement_score=improvement_score,
                optimization_reasons=optimization_reasons,
                keyword_improvements=keyword_improvements,
                seo_score=0.8,
                expected_visibility_increase=improvement_score * 0.3,
                expected_click_increase=improvement_score * 0.1,
                confidence_score=0.6
            )
            
        return None
        
    def get_optimization_summary(self, content_id: str = None) -> Dict[str, Any]:
        """Get comprehensive optimization summary"""
        
        # Filter optimizations if content_id provided
        relevant_optimizations = [
            opt for opt in self.optimizations
            if not content_id or opt.content_id == content_id
        ]
        
        if not relevant_optimizations:
            return {"message": "No optimizations available"}
            
        # Calculate summary statistics
        total_optimizations = len(relevant_optimizations)
        applied_optimizations = len([opt for opt in relevant_optimizations if opt.applied])
        
        avg_improvement = sum(opt.improvement_score for opt in relevant_optimizations) / total_optimizations
        avg_confidence = sum(opt.confidence_score for opt in relevant_optimizations) / total_optimizations
        
        # Breakdown by metadata type
        type_breakdown = defaultdict(int)
        for opt in relevant_optimizations:
            type_breakdown[opt.metadata_type.value] += 1
            
        # Keyword improvements
        all_keyword_improvements = {}
        for opt in relevant_optimizations:
            for keyword, improvement in opt.keyword_improvements.items():
                if keyword not in all_keyword_improvements:
                    all_keyword_improvements[keyword] = []
                all_keyword_improvements[keyword].append(improvement)
                
        avg_keyword_improvements = {
            keyword: sum(improvements) / len(improvements)
            for keyword, improvements in all_keyword_improvements.items()
        }
        
        return {
            "total_optimizations": total_optimizations,
            "applied_optimizations": applied_optimizations,
            "application_rate": applied_optimizations / total_optimizations if total_optimizations > 0 else 0,
            "average_improvement_score": avg_improvement,
            "average_confidence_score": avg_confidence,
            "optimization_breakdown": dict(type_breakdown),
            "keyword_improvements": avg_keyword_improvements,
            "estimated_visibility_increase": avg_improvement * 0.4,
            "estimated_click_increase": avg_improvement * 0.2
        }

# Export main classes
__all__ = [
    'MetadataOptimizationEngine',
    'MetadataOptimization',
    'KeywordAnalysis',
    'MetadataQualityScore',
    'MetadataType',
    'OptimizationLevel'
]