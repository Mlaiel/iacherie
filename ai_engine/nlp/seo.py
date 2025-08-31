"""SEO Optimization Module for IA Influencer Agent Platform

Advanced SEO content optimization for creators and influencers to maximize
discoverability and engagement across platforms and search engines.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import json
from collections import Counter
import requests
from urllib.parse import quote, urlparse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

logger = logging.getLogger(__name__)

@dataclass
class SEOAnalysis:
    """SEO analysis result"""    content_id: str
    overall_score: float
    keyword_score: float
    readability_score: float
    structure_score: float
    metadata_score: float
    recommendations: List[str] = field(default_factory=list)
    optimized_content: Optional[str] = None
    suggested_keywords: List[str] = field(default_factory=list)
    meta_suggestions: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KeywordResearch:
    """Keyword research result"""    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    trending_keywords: List[str]
    competition_analysis: Dict[str, Any]
    search_volume_estimates: Dict[str, int]
    difficulty_scores: Dict[str, float]

class SEOOptimizer:
    """    Advanced SEO optimization engine
    
    Capabilities:
    - Keyword research and optimization
    - Content structure analysis
    - Readability assessment
    - Meta tag optimization
    - Social media SEO
    - Platform-specific optimization
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.stop_words = self._load_stop_words()
        self.trending_keywords_cache = {}
        self.seo_rules = self._load_seo_rules()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default SEO configuration"""        return {
            'target_keyword_density': 0.02,  # 2%
            'max_keyword_density': 0.05,     # 5%
            'min_content_length': 300,
            'ideal_content_length': 1500,
            'max_title_length': 60,
            'max_description_length': 160,
            'readability_target': 'intermediate',  # beginner, intermediate, advanced
            'include_trending': True,
            'platform_optimization': True,
            'language': 'en'
        }
    
    def _load_stop_words(self) -> set:
        """Load stop words for filtering"""        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        return set(stopwords.words('english'))
    
    def _load_seo_rules(self) -> Dict[str, Any]:
        """Load SEO optimization rules"""        return {
            'title_rules': {
                'max_length': 60,
                'include_primary_keyword': True,
                'power_words': ['ultimate', 'complete', 'essential', 'proven', 'effective'],
                'avoid_words': ['click here', 'read more', 'obviously', 'literally']
            },
            'description_rules': {
                'max_length': 160,
                'include_call_to_action': True,
                'include_benefits': True,
                'avoid_duplicate_title': True
            },
            'content_rules': {
                'header_structure': ['h1', 'h2', 'h3'],
                'paragraph_length': {'min': 50, 'max': 150},
                'sentence_length': {'min': 10, 'max': 25},
                'keyword_placement': ['title', 'first_paragraph', 'headers', 'conclusion']
            },
            'social_media_rules': {
                'hashtag_optimization': True,
                'platform_character_limits': {
                    'twitter': 280,
                    'instagram': 2200,
                    'facebook': 63206,
                    'linkedin': 3000,
                    'tiktok': 2200
                }
            }
        }
    
    async def analyze_content_seo(self, content: str, target_keywords: List[str] = None, metadata: Dict[str, Any] = None) -> SEOAnalysis:
        """Comprehensive SEO analysis of content"""        content_id = self._generate_content_id(content)
        metadata = metadata or {}
        
        try:
            # If no target keywords provided, extract them
            if not target_keywords:
                target_keywords = await self._extract_primary_keywords(content)
            
            # Analyze different SEO aspects
            keyword_analysis = await self._analyze_keywords(content, target_keywords)
            readability_analysis = await self._analyze_readability(content)
            structure_analysis = await self._analyze_content_structure(content)
            metadata_analysis = await self._analyze_metadata(metadata, target_keywords)
            
            # Calculate overall score
            scores = {
                'keyword_score': keyword_analysis['score'],
                'readability_score': readability_analysis['score'],
                'structure_score': structure_analysis['score'],
                'metadata_score': metadata_analysis['score']
            }
            
            overall_score = sum(scores.values()) / len(scores)
            
            # Generate recommendations
            recommendations = await self._generate_seo_recommendations(
                keyword_analysis, readability_analysis, structure_analysis, metadata_analysis
            )
            
            # Generate optimized content
            optimized_content = await self._optimize_content(content, target_keywords, recommendations)
            
            # Suggest additional keywords
            suggested_keywords = await self._suggest_related_keywords(target_keywords, content)
            
            # Generate meta suggestions
            meta_suggestions = await self._generate_meta_suggestions(content, target_keywords)
            
            return SEOAnalysis(
                content_id=content_id,
                overall_score=overall_score,
                keyword_score=scores['keyword_score'],
                readability_score=scores['readability_score'],
                structure_score=scores['structure_score'],
                metadata_score=scores['metadata_score'],
                recommendations=recommendations,
                optimized_content=optimized_content,
                suggested_keywords=suggested_keywords,
                meta_suggestions=meta_suggestions
            )
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}")
            return SEOAnalysis(
                content_id=content_id,
                overall_score=0.0,
                keyword_score=0.0,
                readability_score=0.0,
                structure_score=0.0,
                metadata_score=0.0,
                recommendations=[f"Analysis failed: {str(e)}"]
            )
    
    async def research_keywords(self, topic: str, niche: str = None) -> KeywordResearch:
        """Research keywords for a given topic"""        
        # Extract seed keywords from topic
        seed_keywords = self._extract_seed_keywords(topic)
        
        # Generate keyword variations
        primary_keywords = await self._generate_primary_keywords(seed_keywords, topic)
        secondary_keywords = await self._generate_secondary_keywords(primary_keywords, topic)
        long_tail_keywords = await self._generate_long_tail_keywords(primary_keywords, topic)
        
        # Get trending keywords
        trending_keywords = await self._get_trending_keywords(niche or 'general')
        
        # Analyze competition (simplified)
        competition_analysis = await self._analyze_keyword_competition(primary_keywords)
        
        # Estimate search volumes (simplified)
        search_volume_estimates = await self._estimate_search_volumes(primary_keywords + secondary_keywords)
        
        # Calculate difficulty scores
        difficulty_scores = await self._calculate_keyword_difficulty(primary_keywords + secondary_keywords)
        
        return KeywordResearch(
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            long_tail_keywords=long_tail_keywords,
            trending_keywords=trending_keywords,
            competition_analysis=competition_analysis,
            search_volume_estimates=search_volume_estimates,
            difficulty_scores=difficulty_scores
        )
    
    async def optimize_for_platform(self, content: str, platform: str, keywords: List[str] = None) -> Dict[str, Any]:
        """Optimize content for specific platform"""        
        platform_rules = self.seo_rules['social_media_rules']['platform_character_limits']
        max_length = platform_rules.get(platform, 2200)
        
        # Platform-specific optimizations
        if platform == 'instagram':
            return await self._optimize_for_instagram(content, keywords, max_length)
        elif platform == 'twitter':
            return await self._optimize_for_twitter(content, keywords, max_length)
        elif platform == 'linkedin':
            return await self._optimize_for_linkedin(content, keywords, max_length)
        elif platform == 'tiktok':
            return await self._optimize_for_tiktok(content, keywords, max_length)
        elif platform == 'youtube':
            return await self._optimize_for_youtube(content, keywords)
        else:
            return await self._optimize_for_general(content, keywords, max_length)
    
    async def _extract_primary_keywords(self, content: str) -> List[str]:
        """Extract primary keywords from content"""        # Tokenize and clean
        tokens = word_tokenize(content.lower())
        tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
        
        # Get word frequencies
        word_freq = Counter(tokens)
        
        # Extract multi-word phrases (bigrams and trigrams)
        sentences = sent_tokenize(content)
        phrases = []
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [w for w in words if w.isalpha() and w not in self.stop_words]
            
            # Generate bigrams and trigrams
            for i in range(len(words) - 1):
                phrases.append(' '.join(words[i:i+2]))
            for i in range(len(words) - 2):
                phrases.append(' '.join(words[i:i+3]))
        
        phrase_freq = Counter(phrases)
        
        # Combine single words and phrases
        keywords = []
        keywords.extend([word for word, freq in word_freq.most_common(10) if freq > 1])
        keywords.extend([phrase for phrase, freq in phrase_freq.most_common(5) if freq > 1])
        
        return keywords[:15]  # Return top 15 keywords
    
    async def _analyze_keywords(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword usage in content"""        content_lower = content.lower()
        word_count = len(content.split())
        
        keyword_analysis = {
            'found_keywords': [],
            'missing_keywords': [],
            'keyword_density': {},
            'keyword_placement': {},
            'over_optimization': False,
            'score': 0.0
        }
        
        total_keyword_density = 0.0
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            keyword_count = content_lower.count(keyword_lower)
            density = keyword_count / word_count if word_count > 0 else 0
            
            keyword_analysis['keyword_density'][keyword] = density
            total_keyword_density += density
            
            if keyword_count > 0:
                keyword_analysis['found_keywords'].append(keyword)
                
                # Analyze placement
                placement = self._analyze_keyword_placement(content, keyword)
                keyword_analysis['keyword_placement'][keyword] = placement
            else:
                keyword_analysis['missing_keywords'].append(keyword)
        
        # Check for over-optimization
        max_density = self.config['max_keyword_density']
        keyword_analysis['over_optimization'] = total_keyword_density > max_density
        
        # Calculate score
        target_density = self.config['target_keyword_density']
        density_score = min(1.0, total_keyword_density / target_density) if target_density > 0 else 0
        placement_score = self._calculate_placement_score(keyword_analysis['keyword_placement'])
        
        keyword_analysis['score'] = (density_score * 0.6 + placement_score * 0.4) * 0.9 if keyword_analysis['over_optimization'] else (density_score * 0.6 + placement_score * 0.4)
        
        return keyword_analysis
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""        sentences = sent_tokenize(content)
        words = word_tokenize(content)
        
        # Basic readability metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Count syllables (simplified)
        syllable_count = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = syllable_count / len(words) if words else 0
        
        # Flesch Reading Ease Score (simplified)
        if sentences and words:
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            flesch_score = max(0, min(100, flesch_score))
        else:
            flesch_score = 0
        
        # Readability assessment
        if flesch_score >= 90:
            readability_level = 'very_easy'
        elif flesch_score >= 80:
            readability_level = 'easy'
        elif flesch_score >= 70:
            readability_level = 'fairly_easy'
        elif flesch_score >= 60:
            readability_level = 'standard'
        elif flesch_score >= 50:
            readability_level = 'fairly_difficult'
        elif flesch_score >= 30:
            readability_level = 'difficult'
        else:
            readability_level = 'very_difficult'
        
        # Score based on target readability
        target_readability = self.config['readability_target']
        
        if target_readability == 'beginner' and readability_level in ['very_easy', 'easy']:
            score = 1.0
        elif target_readability == 'intermediate' and readability_level in ['fairly_easy', 'standard']:
            score = 1.0
        elif target_readability == 'advanced' and readability_level in ['fairly_difficult', 'difficult']:
            score = 1.0
        else:
            score = 0.7
        
        return {
            'flesch_score': flesch_score,
            'readability_level': readability_level,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'avg_syllables_per_word': avg_syllables_per_word,
            'score': score
        }
    
    async def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure for SEO"""        lines = content.split('\n')
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        structure_analysis = {
            'has_title': False,
            'has_headers': False,
            'header_hierarchy': [],
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': 0,
            'has_bullet_points': False,
            'has_numbered_lists': False,
            'content_length': len(content),
            'score': 0.0
        }
        
        # Check for headers (markdown style)
        headers = []
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                headers.append(level)
                structure_analysis['has_headers'] = True
                if level == 1:
                    structure_analysis['has_title'] = True
        
        structure_analysis['header_hierarchy'] = headers
        
        # Calculate average paragraph length
        if paragraphs:
            avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            structure_analysis['avg_paragraph_length'] = avg_para_length
        
        # Check for lists
        structure_analysis['has_bullet_points'] = bool(re.search(r'^\s*[•\-\*]\s', content, re.MULTILINE))
        structure_analysis['has_numbered_lists'] = bool(re.search(r'^\s*\d+\.\s', content, re.MULTILINE))
        
        # Calculate structure score
        score = 0.0
        
        # Title presence
        if structure_analysis['has_title']:
            score += 0.2
        
        # Headers presence
        if structure_analysis['has_headers']:
            score += 0.2
        
        # Content length
        content_length = structure_analysis['content_length']
        ideal_length = self.config['ideal_content_length']
        min_length = self.config['min_content_length']
        
        if content_length >= min_length:
            if content_length >= ideal_length:
                score += 0.3
            else:
                score += 0.2
        
        # Paragraph structure
        if 3 <= structure_analysis['paragraph_count'] <= 10:
            score += 0.15
        
        # List usage
        if structure_analysis['has_bullet_points'] or structure_analysis['has_numbered_lists']:
            score += 0.15
        
        structure_analysis['score'] = score
        
        return structure_analysis
    
    async def _analyze_metadata(self, metadata: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Analyze metadata for SEO"""        title = metadata.get('title', '')
        description = metadata.get('description', '')
        tags = metadata.get('tags', [])
        
        metadata_analysis = {
            'title_analysis': self._analyze_title(title, keywords),
            'description_analysis': self._analyze_description(description, keywords),
            'tags_analysis': self._analyze_tags(tags, keywords),
            'score': 0.0
        }
        
        # Calculate metadata score
        title_score = metadata_analysis['title_analysis']['score']
        description_score = metadata_analysis['description_analysis']['score']
        tags_score = metadata_analysis['tags_analysis']['score']
        
        metadata_analysis['score'] = (title_score * 0.5 + description_score * 0.3 + tags_score * 0.2)
        
        return metadata_analysis
    
    def _analyze_title(self, title: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze title for SEO"""        title_rules = self.seo_rules['title_rules']
        
        analysis = {
            'length': len(title),
            'within_limit': len(title) <= title_rules['max_length'],
            'has_primary_keyword': False,
            'has_power_words': False,
            'has_avoid_words': False,
            'score': 0.0
        }
        
        if not title:
            return analysis
        
        title_lower = title.lower()
        
        # Check for primary keyword
        if keywords:
            primary_keyword = keywords[0].lower()
            analysis['has_primary_keyword'] = primary_keyword in title_lower
        
        # Check for power words
        power_words = title_rules['power_words']
        analysis['has_power_words'] = any(word in title_lower for word in power_words)
        
        # Check for words to avoid
        avoid_words = title_rules['avoid_words']
        analysis['has_avoid_words'] = any(word in title_lower for word in avoid_words)
        
        # Calculate score
        score = 0.0
        
        if analysis['within_limit']:
            score += 0.3
        
        if analysis['has_primary_keyword']:
            score += 0.4
        
        if analysis['has_power_words']:
            score += 0.2
        
        if not analysis['has_avoid_words']:
            score += 0.1
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_description(self, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze description for SEO"""        description_rules = self.seo_rules['description_rules']
        
        analysis = {
            'length': len(description),
            'within_limit': len(description) <= description_rules['max_length'],
            'has_keywords': False,
            'has_call_to_action': False,
            'score': 0.0
        }
        
        if not description:
            return analysis
        
        description_lower = description.lower()
        
        # Check for keywords
        if keywords:
            analysis['has_keywords'] = any(keyword.lower() in description_lower for keyword in keywords)
        
        # Check for call-to-action
        cta_words = ['learn', 'discover', 'find', 'get', 'download', 'read', 'watch', 'try', 'start', 'join']
        analysis['has_call_to_action'] = any(word in description_lower for word in cta_words)
        
        # Calculate score
        score = 0.0
        
        if analysis['within_limit'] and len(description) > 120:  # Minimum useful length
            score += 0.3
        
        if analysis['has_keywords']:
            score += 0.4
        
        if analysis['has_call_to_action']:
            score += 0.3
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_tags(self, tags: List[str], keywords: List[str]) -> Dict[str, Any]:
        """Analyze tags for SEO"""        analysis = {
            'tag_count': len(tags),
            'keyword_overlap': 0,
            'score': 0.0
        }
        
        if not tags:
            return analysis
        
        # Calculate keyword overlap
        if keywords:
            tag_set = {tag.lower() for tag in tags}
            keyword_set = {keyword.lower() for keyword in keywords}
            overlap = len(tag_set.intersection(keyword_set))
            analysis['keyword_overlap'] = overlap / len(keywords)
        
        # Calculate score
        score = 0.0
        
        # Good number of tags
        if 3 <= len(tags) <= 10:
            score += 0.5
        
        # Keyword overlap
        score += analysis['keyword_overlap'] * 0.5
        
        analysis['score'] = score
        
        return analysis
    
    def _analyze_keyword_placement(self, content: str, keyword: str) -> Dict[str, bool]:
        """Analyze keyword placement in content"""        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        # Split content into sections
        paragraphs = content.split('\n\n')
        first_paragraph = paragraphs[0] if paragraphs else ""
        last_paragraph = paragraphs[-1] if paragraphs else ""
        
        # Check title (first line)
        lines = content.split('\n')
        title = lines[0] if lines else ""
        
        return {
            'in_title': keyword_lower in title.lower(),
            'in_first_paragraph': keyword_lower in first_paragraph.lower(),
            'in_last_paragraph': keyword_lower in last_paragraph.lower(),
            'in_headers': self._keyword_in_headers(content, keyword_lower)
        }
    
    def _keyword_in_headers(self, content: str, keyword: str) -> bool:
        """Check if keyword appears in headers"""        lines = content.split('\n')
        headers = [line for line in lines if line.startswith('#')]
        return any(keyword in header.lower() for header in headers)
    
    def _calculate_placement_score(self, placement_analysis: Dict[str, Dict[str, bool]]) -> float:
        """Calculate score based on keyword placement"""        if not placement_analysis:
            return 0.0
        
        total_score = 0.0
        keyword_count = len(placement_analysis)
        
        for keyword, placement in placement_analysis.items():
            keyword_score = 0.0
            
            if placement['in_title']:
                keyword_score += 0.4
            if placement['in_first_paragraph']:
                keyword_score += 0.3
            if placement['in_headers']:
                keyword_score += 0.2
            if placement['in_last_paragraph']:
                keyword_score += 0.1
            
            total_score += keyword_score
        
        return total_score / keyword_count if keyword_count > 0 else 0.0
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _generate_seo_recommendations(self, keyword_analysis: Dict[str, Any], 
                                          readability_analysis: Dict[str, Any],
                                          structure_analysis: Dict[str, Any],
                                          metadata_analysis: Dict[str, Any]) -> List[str]:
        """Generate SEO improvement recommendations"""        recommendations = []
        
        # Keyword recommendations
        if keyword_analysis['score'] < 0.7:
            if keyword_analysis['missing_keywords']:
                recommendations.append(f"Include missing keywords: {', '.join(keyword_analysis['missing_keywords'][:3])}")
            
            if not any(placement.get('in_title', False) for placement in keyword_analysis['keyword_placement'].values()):
                recommendations.append("Include primary keyword in title or main heading")
            
            if keyword_analysis['over_optimization']:
                recommendations.append("Reduce keyword density to avoid over-optimization")
        
        # Readability recommendations
        if readability_analysis['score'] < 0.8:
            if readability_analysis['avg_sentence_length'] > 25:
                recommendations.append("Break down long sentences for better readability")
            
            if readability_analysis['readability_level'] in ['difficult', 'very_difficult']:
                recommendations.append("Simplify language for better audience engagement")
        
        # Structure recommendations
        if structure_analysis['score'] < 0.7:
            if not structure_analysis['has_title']:
                recommendations.append("Add a clear title or main heading")
            
            if not structure_analysis['has_headers']:
                recommendations.append("Use headers (H2, H3) to structure content")
            
            if structure_analysis['content_length'] < self.config['min_content_length']:
                recommendations.append(f"Expand content to at least {self.config['min_content_length']} characters")
            
            if structure_analysis['paragraph_count'] < 3:
                recommendations.append("Break content into more paragraphs for better readability")
        
        # Metadata recommendations
        if metadata_analysis['score'] < 0.7:
            title_analysis = metadata_analysis['title_analysis']
            if not title_analysis['within_limit']:
                recommendations.append(f"Optimize title length (current: {title_analysis['length']}, max: {self.seo_rules['title_rules']['max_length']})")
            
            if not title_analysis['has_primary_keyword']:
                recommendations.append("Include primary keyword in title")
            
            description_analysis = metadata_analysis['description_analysis']
            if not description_analysis['within_limit']:
                recommendations.append("Optimize meta description length")
            
            if not description_analysis['has_call_to_action']:
                recommendations.append("Add call-to-action to meta description")
        
        return recommendations
    
    async def _optimize_content(self, content: str, keywords: List[str], recommendations: List[str]) -> str:
        """Generate optimized version of content"""        # This is a simplified optimization - in practice, would be more sophisticated
        optimized = content
        
        # Add primary keyword to first paragraph if missing
        if keywords and "Include primary keyword" in ' '.join(recommendations):
            primary_keyword = keywords[0]
            paragraphs = optimized.split('\n\n')
            if paragraphs and primary_keyword.lower() not in paragraphs[0].lower():
                # Try to naturally integrate the keyword
                first_para = paragraphs[0]
                if first_para:
                    # Simple integration - add at the end of first sentence
                    sentences = first_para.split('.')
                    if sentences:
                        sentences[0] = f"{sentences[0]} related to {primary_keyword}"
                        paragraphs[0] = '.'.join(sentences)
                        optimized = '\n\n'.join(paragraphs)
        
        return optimized
    
    async def _suggest_related_keywords(self, keywords: List[str], content: str) -> List[str]:
        """Suggest related keywords"""        if not keywords:
            return []
        
        # Extract potential related keywords from content
        content_keywords = await self._extract_primary_keywords(content)
        
        # Simple related keyword suggestions based on common patterns
        related = []
        for keyword in keywords[:3]:  # Focus on top 3 keywords
            # Add variations
            related.extend([
                f"{keyword} tips",
                f"{keyword} guide",
                f"best {keyword}",
                f"{keyword} tutorial",
                f"how to {keyword}"
            ])
        
        # Add content-derived keywords that aren't in original list
        for content_keyword in content_keywords:
            if content_keyword not in keywords:
                related.append(content_keyword)
        
        return related[:10]  # Return top 10 suggestions
    
    async def _generate_meta_suggestions(self, content: str, keywords: List[str]) -> Dict[str, str]:
        """Generate meta tag suggestions"""        # Extract first sentence or paragraph for description base
        sentences = sent_tokenize(content)
        first_sentence = sentences[0] if sentences else ""
        
        # Generate title suggestion
        primary_keyword = keywords[0] if keywords else "Content"
        title_suggestions = [
            f"Complete Guide to {primary_keyword}",
            f"Everything You Need to Know About {primary_keyword}",
            f"Ultimate {primary_keyword} Tips and Strategies",
            f"Master {primary_keyword}: Expert Insights"
        ]
        
        # Generate description suggestion
        description_base = first_sentence[:100] if len(first_sentence) > 100 else first_sentence
        description_suggestion = f"{description_base} Learn more about {primary_keyword} and discover proven strategies."
        
        # Ensure description is within limits
        if len(description_suggestion) > 160:
            description_suggestion = description_suggestion[:157] + "..."
        
        return {
            'title': title_suggestions[0],
            'title_alternatives': title_suggestions[1:],
            'description': description_suggestion,
            'keywords': ', '.join(keywords[:5])
        }
    
    def _extract_seed_keywords(self, topic: str) -> List[str]:
        """Extract seed keywords from topic"""        # Clean and tokenize topic
        topic_clean = re.sub(r'[^\w\s]', '', topic.lower())
        words = topic_clean.split()
        
        # Remove stop words
        seeds = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Add topic as phrase
        if len(words) > 1:
            seeds.append(topic_clean)
        
        return seeds
    
    async def _generate_primary_keywords(self, seeds: List[str], topic: str) -> List[str]:
        """Generate primary keywords from seeds"""        primary = []
        
        # Use seeds as primary keywords
        primary.extend(seeds)
        
        # Add topic variations
        for seed in seeds:
            primary.extend([
                f"{seed} tips",
                f"{seed} guide",
                f"best {seed}",
                f"{seed} strategies"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_primary = []
        for keyword in primary:
            if keyword not in seen:
                seen.add(keyword)
                unique_primary.append(keyword)
        
        return unique_primary[:10]
    
    async def _generate_secondary_keywords(self, primary: List[str], topic: str) -> List[str]:
        """Generate secondary keywords"""        secondary = []
        
        for keyword in primary[:5]:  # Top 5 primary keywords
            secondary.extend([
                f"how to {keyword}",
                f"{keyword} examples",
                f"{keyword} benefits",
                f"{keyword} techniques",
                f"{keyword} methods"
            ])
        
        return secondary[:15]
    
    async def _generate_long_tail_keywords(self, primary: List[str], topic: str) -> List[str]:
        """Generate long-tail keywords"""        long_tail = []
        
        for keyword in primary[:3]:  # Top 3 primary keywords
            long_tail.extend([
                f"what is the best way to {keyword}",
                f"how to improve {keyword} for beginners",
                f"complete guide to {keyword} step by step",
                f"common mistakes when learning {keyword}",
                f"expert tips for mastering {keyword}"
            ])
        
        return long_tail[:10]
    
    async def _get_trending_keywords(self, niche: str) -> List[str]:
        """Get trending keywords for niche"""        # Simplified trending keywords - in production, would fetch from APIs
        trending_by_niche = {
            'general': ['trending', 'viral', 'popular', '2025', 'new'],
            'technology': ['AI', 'machine learning', 'blockchain', 'cloud', 'automation'],
            'lifestyle': ['wellness', 'minimalism', 'self-care', 'productivity', 'mindfulness'],
            'business': ['digital marketing', 'remote work', 'entrepreneurship', 'startup', 'growth'],
            'health': ['mental health', 'fitness', 'nutrition', 'wellness', 'exercise'],
            'education': ['online learning', 'skill development', 'certification', 'training', 'courses']
        }
        
        return trending_by_niche.get(niche, trending_by_niche['general'])
    
    async def _analyze_keyword_competition(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword competition (simplified)"""        # Simplified competition analysis
        competition = {}
        
        for keyword in keywords:
            # Simple heuristic: longer keywords = less competition
            if len(keyword.split()) >= 3:
                competition[keyword] = 'low'
            elif len(keyword.split()) == 2:
                competition[keyword] = 'medium'
            else:
                competition[keyword] = 'high'
        
        return {
            'individual_competition': competition,
            'avg_competition': 'medium',  # Simplified
            'high_competition_count': len([k for k, v in competition.items() if v == 'high']),
            'opportunities': [k for k, v in competition.items() if v == 'low']
        }
    
    async def _estimate_search_volumes(self, keywords: List[str]) -> Dict[str, int]:
        """Estimate search volumes (simplified)"""        # Simplified volume estimation based on keyword characteristics
        volumes = {}
        
        for keyword in keywords:
            # Heuristic: single words have higher volume
            if len(keyword.split()) == 1:
                volumes[keyword] = 10000
            elif len(keyword.split()) == 2:
                volumes[keyword] = 5000
            else:
                volumes[keyword] = 1000
        
        return volumes
    
    async def _calculate_keyword_difficulty(self, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword difficulty scores"""        # Simplified difficulty calculation
        difficulty = {}
        
        for keyword in keywords:
            # Heuristic: longer keywords = easier to rank
            word_count = len(keyword.split())
            if word_count >= 4:
                difficulty[keyword] = 0.3  # Easy
            elif word_count == 3:
                difficulty[keyword] = 0.5  # Medium
            elif word_count == 2:
                difficulty[keyword] = 0.7  # Hard
            else:
                difficulty[keyword] = 0.9  # Very hard
        
        return difficulty
    
    async def _optimize_for_instagram(self, content: str, keywords: List[str], max_length: int) -> Dict[str, Any]:
        """Optimize content for Instagram"""        # Ensure content fits within Instagram limits
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        # Generate Instagram-specific hashtags
        hashtags = []
        if keywords:
            for keyword in keywords[:5]:
                hashtag = keyword.replace(' ', '').lower()
                hashtags.append(f"#{hashtag}")
        
        # Add popular Instagram hashtags
        hashtags.extend(['#instagood', '#photooftheday', '#instadaily'])
        
        return {
            'optimized_content': content,
            'hashtags': hashtags[:30],  # Instagram limit
            'caption_length': len(content),
            'engagement_tips': [
                'Use engaging first line to capture attention',
                'Include call-to-action',
                'Ask questions to encourage comments',
                'Use relevant hashtags',
                'Post at optimal times'
            ]
        }
    
    async def _optimize_for_twitter(self, content: str, keywords: List[str], max_length: int) -> Dict[str, Any]:
        """Optimize content for Twitter"""        # Twitter character limit
        available_chars = max_length - 50  # Reserve space for hashtags/mentions
        
        if len(content) > available_chars:
            # Create thread or trim content
            content = content[:available_chars-3] + "..."
        
        # Generate Twitter hashtags
        hashtags = []
        if keywords:
            for keyword in keywords[:2]:  # Limit hashtags on Twitter
                hashtag = keyword.replace(' ', '').lower()
                hashtags.append(f"#{hashtag}")
        
        return {
            'optimized_content': content,
            'hashtags': hashtags,
            'char_count': len(content),
            'thread_suggestion': len(content) > 200,
            'engagement_tips': [
                'Keep it concise and punchy',
                'Use relevant hashtags (max 2-3)',
                'Include engaging questions',
                'Retweet and engage with others',
                'Use trending hashtags when relevant'
            ]
        }
    
    async def _optimize_for_linkedin(self, content: str, keywords: List[str], max_length: int) -> Dict[str, Any]:
        """Optimize content for LinkedIn"""        # LinkedIn professional optimization
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        # Professional hashtags
        hashtags = []
        if keywords:
            for keyword in keywords[:5]:
                hashtag = keyword.replace(' ', '').lower()
                hashtags.append(f"#{hashtag}")
        
        # Add professional hashtags
        hashtags.extend(['#professional', '#career', '#business', '#networking'])
        
        return {
            'optimized_content': content,
            'hashtags': hashtags[:10],
            'professional_tone': True,
            'engagement_tips': [
                'Use professional tone',
                'Share industry insights',
                'Ask for professional opinions',
                'Use relevant industry hashtags',
                'Engage with industry leaders'
            ]
        }
    
    async def _optimize_for_tiktok(self, content: str, keywords: List[str], max_length: int) -> Dict[str, Any]:
        """Optimize content for TikTok"""        # TikTok is video-focused, but optimize caption
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        # TikTok trending hashtags
        hashtags = ['#fyp', '#foryou', '#trending']
        
        if keywords:
            for keyword in keywords[:3]:
                hashtag = keyword.replace(' ', '').lower()
                hashtags.append(f"#{hashtag}")
        
        return {
            'optimized_content': content,
            'hashtags': hashtags[:20],
            'video_focus': True,
            'engagement_tips': [
                'Hook viewers in first 3 seconds',
                'Use trending sounds and effects',
                'Jump on trending challenges',
                'Keep captions short and punchy',
                'Use popular hashtags like #fyp #foryou'
            ]
        }
    
    async def _optimize_for_youtube(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for YouTube"""        # YouTube allows longer descriptions
        
        # Generate video title suggestions
        title_suggestions = []
        if keywords:
            primary_keyword = keywords[0]
            title_suggestions = [
                f"Ultimate Guide to {primary_keyword}",
                f"How to Master {primary_keyword} in 2025",
                f"{primary_keyword} Tutorial - Complete Walkthrough",
                f"Everything About {primary_keyword} Explained"
            ]
        
        # Generate hashtags
        hashtags = []
        if keywords:
            for keyword in keywords[:15]:
                hashtag = keyword.replace(' ', '').lower()
                hashtags.append(f"#{hashtag}")
        
        return {
            'optimized_content': content,
            'title_suggestions': title_suggestions,
            'hashtags': hashtags,
            'description_length': len(content),
            'seo_tips': [
                'Include keywords in title',
                'Write detailed descriptions',
                'Use timestamps for longer videos',
                'Add end screens and cards',
                'Optimize thumbnail for clicks'
            ]
        }
    
    async def _optimize_for_general(self, content: str, keywords: List[str], max_length: int) -> Dict[str, Any]:
        """General platform optimization"""        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        hashtags = []
        if keywords:
            for keyword in keywords[:10]:
                hashtag = keyword.replace(' ', '').lower()
                hashtags.append(f"#{hashtag}")
        
        return {
            'optimized_content': content,
            'hashtags': hashtags,
            'content_length': len(content),
            'general_tips': [
                'Adapt content to platform audience',
                'Use platform-appropriate hashtags',
                'Maintain consistent brand voice',
                'Engage with community',
                'Monitor performance metrics'
            ]
        }
    
    def _generate_content_id(self, content: str) -> str:
        """Generate unique content ID"""        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:12]

# Utility functions
async def analyze_seo_quick(content: str, keywords: List[str] = None) -> Dict[str, Any]:
    """Quick SEO analysis function"""    optimizer = SEOOptimizer()
    analysis = await optimizer.analyze_content_seo(content, keywords)
    
    return {
        'overall_score': analysis.overall_score,
        'scores': {
            'keywords': analysis.keyword_score,
            'readability': analysis.readability_score,
            'structure': analysis.structure_score,
            'metadata': analysis.metadata_score
        },
        'recommendations': analysis.recommendations[:5],  # Top 5 recommendations
        'suggested_keywords': analysis.suggested_keywords[:10]
    }

async def optimize_for_platform_quick(content: str, platform: str, keywords: List[str] = None) -> str:
    """Quick platform optimization function"""    optimizer = SEOOptimizer()
    result = await optimizer.optimize_for_platform(content, platform, keywords)
    return result.get('optimized_content', content)

# SEO monitoring and tracking
class SEOTracker:
    """Track SEO performance over time"""    
    def __init__(self):
        self.performance_history = []
        self.keyword_rankings = {}
        self.optimization_impact = {}
    
    def track_performance(self, content_id: str, seo_analysis: SEOAnalysis):
        """Track SEO performance for content"""        self.performance_history.append({
            'content_id': content_id,
            'timestamp': datetime.utcnow(),
            'scores': {
                'overall': seo_analysis.overall_score,
                'keywords': seo_analysis.keyword_score,
                'readability': seo_analysis.readability_score,
                'structure': seo_analysis.structure_score,
                'metadata': seo_analysis.metadata_score
            },
            'recommendations_count': len(seo_analysis.recommendations)
        })
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get SEO performance trends"""        if not self.performance_history:
            return {}
        
        recent_scores = [entry['scores']['overall'] for entry in self.performance_history[-10:]]
        avg_score = sum(recent_scores) / len(recent_scores)
        
        # Calculate trend
        if len(recent_scores) >= 2:
            trend = 'improving' if recent_scores[-1] > recent_scores[0] else 'declining'
        else:
            trend = 'stable'
        
        return {
            'average_score': avg_score,
            'trend': trend,
            'total_content_analyzed': len(self.performance_history),
            'latest_score': recent_scores[-1] if recent_scores else 0
        }
