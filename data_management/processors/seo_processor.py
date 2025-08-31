"""📈 SEO Processor - IA Influencer Agent Platform Enterprise
==========================================================
Module: backend/data_management/processors/seo_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial SEO Optimization - Enterprise Production-Ready Ultra Advanced
Responsibility: Optimisation SEO intelligente pour contenu créateurs multi-plateformes
====================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER SEO:
Content Analysis → Keyword Research → Competition Analysis → SEO Optimization → 
Hashtag Strategy → Platform-Specific SEO → Performance Tracking → Recommendation Engine
"""
import json
import logging
import asyncio
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
import requests
from textblob import TextBlob
import nltk
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
from concurrent.futures import ThreadPoolExecutor
import spacy

from .base_processor import BaseProcessor, AsyncBaseProcessor


class SEOProcessor(BaseProcessor):
    """Processeur SEO avancé multi-plateformes - Production Enterprise"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # SEO Configuration
        self.seo_config = {
            'platform_requirements': {
                'youtube': {
                    'title_length': {'min': 10, 'max': 60, 'optimal': 50},
                    'description_length': {'min': 125, 'max': 5000, 'optimal': 200},
                    'tags_count': {'min': 3, 'max': 15, 'optimal': 10},
                    'keywords_density': {'min': 0.5, 'max': 2.5, 'optimal': 1.5},
                    'thumbnail_requirements': ['high_contrast', 'text_overlay', 'faces']
                },
                'instagram': {
                    'caption_length': {'min': 20, 'max': 2200, 'optimal': 150},
                    'hashtags_count': {'min': 5, 'max': 30, 'optimal': 11},
                    'story_text_limit': 160,
                    'alt_text_length': {'min': 10, 'max': 125, 'optimal': 100}
                },
                'tiktok': {
                    'caption_length': {'min': 10, 'max': 300, 'optimal': 100},
                    'hashtags_count': {'min': 3, 'max': 10, 'optimal': 5},
                    'trending_hashtags_ratio': 0.3,
                    'keywords_in_audio': True
                },
                'twitter': {
                    'tweet_length': {'min': 10, 'max': 280, 'optimal': 100},
                    'hashtags_count': {'min': 1, 'max': 3, 'optimal': 2},
                    'media_engagement_boost': 2.5,
                    'thread_optimal_length': 5
                },
                'linkedin': {
                    'post_length': {'min': 50, 'max': 3000, 'optimal': 1500},
                    'hashtags_count': {'min': 3, 'max': 10, 'optimal': 5},
                    'professional_keywords': True,
                    'industry_relevance': True
                }
            },
            'seo_factors': {
                'keyword_optimization': 0.25,
                'content_structure': 0.20,
                'engagement_signals': 0.20,
                'platform_specificity': 0.15,
                'trending_relevance': 0.10,
                'competition_analysis': 0.10
            },
            'keyword_research_sources': {
                'google_trends': 'https://trends.google.com/trends/api',
                'youtube_suggestions': 'https://suggestqueries.google.com/complete/search',
                'hashtag_analytics': 'internal_api',
                'competitor_analysis': 'internal_scraping'
            }
        }
        
        # Trending Topics and Keywords
        self.trending_data = {
            'global_trends': [],
            'platform_trends': {},
            'seasonal_keywords': {},
            'industry_keywords': {},
            'last_updated': None
        }
        
        # NLP Models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            self.logger.warning("spaCy model not available")
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # SEO Keywords by Category
        self.keyword_categories = {
            'music': ['music', 'song', 'artist', 'album', 'concert', 'festival', 'musician', 'band'],
            'gaming': ['gaming', 'gamer', 'gameplay', 'review', 'walkthrough', 'esports', 'stream'],
            'tech': ['technology', 'tech', 'review', 'tutorial', 'gadget', 'software', 'app'],
            'lifestyle': ['lifestyle', 'daily', 'routine', 'tips', 'advice', 'wellness', 'self-care'],
            'education': ['tutorial', 'learn', 'guide', 'how-to', 'education', 'course', 'tips'],
            'entertainment': ['funny', 'comedy', 'entertainment', 'viral', 'trending', 'meme'],
            'fitness': ['workout', 'fitness', 'gym', 'health', 'exercise', 'training', 'nutrition'],
            'fashion': ['fashion', 'style', 'outfit', 'trend', 'beauty', 'makeup', 'ootd']
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite l'optimisation SEO complète"""
        content_data = input_data.get('content_data', {})
        platform = input_data.get('platform', 'youtube')
        target_audience = input_data.get('target_audience', {})
        competition_analysis = input_data.get('include_competition', True)
        
        seo_result = {
            'platform': platform,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'content_analysis': {},
            'keyword_optimization': {},
            'seo_score': 0,
            'platform_optimization': {},
            'competition_insights': {},
            'hashtag_strategy': {},
            'recommendations': [],
            'optimized_content': {}
        }
        
        try:
            # 1. Analyze current content
            content_analysis = self._analyze_content(content_data, platform)
            seo_result['content_analysis'] = content_analysis
            
            # 2. Keyword research and optimization
            keyword_optimization = self._perform_keyword_optimization(
                content_data, platform, target_audience
            )
            seo_result['keyword_optimization'] = keyword_optimization
            
            # 3. Platform-specific optimization
            platform_optimization = self._optimize_for_platform(
                content_data, platform, keyword_optimization
            )
            seo_result['platform_optimization'] = platform_optimization
            
            # 4. Competition analysis
            if competition_analysis:
                competition_insights = self._analyze_competition(
                    keyword_optimization.get('primary_keywords', []), platform
                )
                seo_result['competition_insights'] = competition_insights
            
            # 5. Hashtag strategy
            hashtag_strategy = self._develop_hashtag_strategy(
                keyword_optimization, platform, target_audience
            )
            seo_result['hashtag_strategy'] = hashtag_strategy
            
            # 6. Calculate SEO score
            seo_score = self._calculate_seo_score(
                content_analysis, keyword_optimization, platform_optimization, hashtag_strategy
            )
            seo_result['seo_score'] = seo_score
            
            # 7. Generate recommendations
            recommendations = self._generate_seo_recommendations(seo_result)
            seo_result['recommendations'] = recommendations
            
            # 8. Create optimized content
            optimized_content = self._create_optimized_content(
                content_data, keyword_optimization, platform_optimization, hashtag_strategy
            )
            seo_result['optimized_content'] = optimized_content
            
        except Exception as e:
            seo_result['error'] = str(e)
            self.logger.error(f"SEO processing failed: {e}")
        
        return seo_result
    
    def _analyze_content(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Analyse le contenu existant"""
        analysis = {
            'content_structure': {},
            'readability': {},
            'keyword_density': {},
            'semantic_analysis': {},
            'platform_compliance': {}
        }
        
        try:
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            tags = content_data.get('tags', [])
            
            # Content structure analysis
            analysis['content_structure'] = {
                'title_length': len(title),
                'description_length': len(description),
                'tags_count': len(tags),
                'word_count': len(description.split()) if description else 0,
                'character_count': len(description),
                'sentences_count': len(description.split('.')) if description else 0
            }
            
            # Readability analysis
            if description:
                analysis['readability'] = self._analyze_readability(description)
            
            # Keyword density analysis
            if description:
                analysis['keyword_density'] = self._analyze_keyword_density(description)
            
            # Semantic analysis
            combined_text = f"{title} {description} {' '.join(tags)}"
            if combined_text.strip():
                analysis['semantic_analysis'] = self._perform_semantic_analysis(combined_text)
            
            # Platform compliance check
            platform_reqs = self.seo_config['platform_requirements'].get(platform, {})
            analysis['platform_compliance'] = self._check_platform_compliance(
                analysis['content_structure'], platform_reqs
            )
            
        except Exception as e:
            analysis['error'] = str(e)
            self.logger.error(f"Content analysis failed: {e}")
        
        return analysis
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyse la lisibilité du texte"""
        try:
            blob = TextBlob(text)
            
            # Basic readability metrics
            sentences = blob.sentences
            words = blob.words
            
            if len(sentences) == 0 or len(words) == 0:
                return {'error': 'Insufficient text for analysis'}
            
            avg_sentence_length = len(words) / len(sentences)
            
            # Estimate reading level (simplified)
            complex_words = [word for word in words if len(word) > 6]
            complex_word_ratio = len(complex_words) / len(words)
            
            # Flesch-Kincaid approximation
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * complex_word_ratio)
            
            if flesch_score >= 90:
                reading_level = 'very_easy'
            elif flesch_score >= 80:
                reading_level = 'easy'
            elif flesch_score >= 70:
                reading_level = 'fairly_easy'
            elif flesch_score >= 60:
                reading_level = 'standard'
            elif flesch_score >= 50:
                reading_level = 'fairly_difficult'
            else:
                reading_level = 'difficult'
            
            return {
                'flesch_score': flesch_score,
                'reading_level': reading_level,
                'avg_sentence_length': avg_sentence_length,
                'complex_word_ratio': complex_word_ratio,
                'total_words': len(words),
                'total_sentences': len(sentences)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_keyword_density(self, text: str) -> Dict[str, Any]:
        """Analyse la densité des mots-clés"""
        try:
            # Clean and tokenize text
            words = re.findall(r'\b\w+\b', text.lower())
            total_words = len(words)
            
            if total_words == 0:
                return {'error': 'No words found'}
            
            # Count word frequencies
            word_counts = Counter(words)
            
            # Calculate densities for top words
            keyword_densities = {}
            for word, count in word_counts.most_common(20):
                if len(word) > 3:  # Skip very short words
                    density = (count / total_words) * 100
                    keyword_densities[word] = {
                        'count': count,
                        'density_percent': density
                    }
            
            # Find potential over-optimization
            over_optimized = [
                word for word, data in keyword_densities.items() 
                if data['density_percent'] > 3.0
            ]
            
            return {
                'total_words': total_words,
                'unique_words': len(word_counts),
                'keyword_densities': keyword_densities,
                'over_optimized_keywords': over_optimized,
                'density_score': 'good' if not over_optimized else 'needs_improvement'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _perform_semantic_analysis(self, text: str) -> Dict[str, Any]:
        """Effectue l'analyse sémantique du contenu"""
        analysis = {
            'sentiment': {},
            'entities': [],
            'topics': [],
            'themes': [],
            'content_category': 'general'
        }
        
        try:
            # Sentiment analysis
            blob = TextBlob(text)
            analysis['sentiment'] = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'sentiment_label': self._classify_sentiment(blob.sentiment.polarity)
            }
            
            # Named entity recognition (if spaCy available)
            if self.nlp:
                doc = self.nlp(text)
                analysis['entities'] = [
                    {'text': ent.text, 'label': ent.label_, 'description': spacy.explain(ent.label_)}
                    for ent in doc.ents
                ]
            
            # Topic identification
            analysis['topics'] = self._identify_topics(text)
            
            # Content categorization
            analysis['content_category'] = self._categorize_content(text)
            
            # Theme extraction
            analysis['themes'] = self._extract_themes(text)
            
        except Exception as e:
            analysis['error'] = str(e)
            self.logger.error(f"Semantic analysis failed: {e}")
        
        return analysis
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classifie le sentiment basé sur la polarité"""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _identify_topics(self, text: str) -> List[str]:
        """Identifie les sujets principaux"""
        topics = []
        
        for category, keywords in self.keyword_categories.items():
            if any(keyword in text.lower() for keyword in keywords):
                topics.append(category)
        
        return topics
    
    def _categorize_content(self, text: str) -> str:
        """Catégorise le contenu"""
        text_lower = text.lower()
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in self.keyword_categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'general'
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extrait les thèmes principaux"""
        themes = []
        
        # Look for common content themes
        theme_keywords = {
            'tutorial': ['how to', 'guide', 'step by step', 'learn', 'tutorial'],
            'review': ['review', 'opinion', 'rating', 'pros and cons', 'verdict'],
            'entertainment': ['funny', 'hilarious', 'entertaining', 'comedy', 'fun'],
            'inspirational': ['inspire', 'motivate', 'success', 'achieve', 'dream'],
            'educational': ['explain', 'understand', 'knowledge', 'facts', 'learn'],
            'news': ['update', 'breaking', 'latest', 'news', 'announcement'],
            'behind_scenes': ['behind the scenes', 'backstage', 'making of', 'process'],
            'collaboration': ['collab', 'featuring', 'with', 'together', 'partnership']
        }
        
        text_lower = text.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _check_platform_compliance(self, content_structure: Dict, platform_reqs: Dict) -> Dict[str, Any]:
        """Vérifie la conformité aux exigences de la plateforme"""
        compliance = {
            'overall_score': 0,
            'compliant_aspects': [],
            'non_compliant_aspects': [],
            'recommendations': []
        }
        
        try:
            total_checks = 0
            passed_checks = 0
            
            # Check title length
            if 'title_length' in platform_reqs:
                title_req = platform_reqs['title_length']
                title_len = content_structure.get('title_length', 0)
                total_checks += 1
                
                if title_req['min'] <= title_len <= title_req['max']:
                    passed_checks += 1
                    compliance['compliant_aspects'].append('title_length')
                else:
                    compliance['non_compliant_aspects'].append('title_length')
                    if title_len < title_req['min']:
                        compliance['recommendations'].append(f"Title too short. Minimum {title_req['min']} characters recommended.")
                    else:
                        compliance['recommendations'].append(f"Title too long. Maximum {title_req['max']} characters allowed.")
            
            # Check description length
            if 'description_length' in platform_reqs:
                desc_req = platform_reqs['description_length']
                desc_len = content_structure.get('description_length', 0)
                total_checks += 1
                
                if desc_req['min'] <= desc_len <= desc_req['max']:
                    passed_checks += 1
                    compliance['compliant_aspects'].append('description_length')
                else:
                    compliance['non_compliant_aspects'].append('description_length')
                    if desc_len < desc_req['min']:
                        compliance['recommendations'].append(f"Description too short. Minimum {desc_req['min']} characters recommended.")
                    else:
                        compliance['recommendations'].append(f"Description too long. Maximum {desc_req['max']} characters allowed.")
            
            # Check tags count
            if 'tags_count' in platform_reqs:
                tags_req = platform_reqs['tags_count']
                tags_count = content_structure.get('tags_count', 0)
                total_checks += 1
                
                if tags_req['min'] <= tags_count <= tags_req['max']:
                    passed_checks += 1
                    compliance['compliant_aspects'].append('tags_count')
                else:
                    compliance['non_compliant_aspects'].append('tags_count')
                    if tags_count < tags_req['min']:
                        compliance['recommendations'].append(f"Add more tags. Minimum {tags_req['min']} tags recommended.")
                    else:
                        compliance['recommendations'].append(f"Too many tags. Maximum {tags_req['max']} tags allowed.")
            
            # Calculate overall score
            if total_checks > 0:
                compliance['overall_score'] = (passed_checks / total_checks) * 100
            
        except Exception as e:
            compliance['error'] = str(e)
        
        return compliance
    
    def _perform_keyword_optimization(self, content_data: Dict, platform: str, target_audience: Dict) -> Dict[str, Any]:
        """Effectue l'optimisation des mots-clés"""
        optimization = {
            'primary_keywords': [],
            'secondary_keywords': [],
            'long_tail_keywords': [],
            'trending_keywords': [],
            'search_volume_data': {},
            'keyword_difficulty': {},
            'optimization_opportunities': []
        }
        
        try:
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            content_category = content_data.get('category', 'general')
            
            # Extract current keywords
            combined_text = f"{title} {description}"
            current_keywords = self._extract_keywords(combined_text)
            
            # Research trending keywords
            trending_keywords = self._get_trending_keywords(platform, content_category)
            optimization['trending_keywords'] = trending_keywords
            
            # Generate keyword suggestions
            suggested_keywords = self._generate_keyword_suggestions(
                current_keywords, content_category, target_audience
            )
            
            # Categorize keywords by intent and length
            optimization['primary_keywords'] = suggested_keywords['primary'][:5]
            optimization['secondary_keywords'] = suggested_keywords['secondary'][:10]
            optimization['long_tail_keywords'] = suggested_keywords['long_tail'][:8]
            
            # Analyze keyword difficulty (simulated)
            for keyword in optimization['primary_keywords']:
                optimization['keyword_difficulty'][keyword] = self._estimate_keyword_difficulty(keyword, platform)
            
            # Find optimization opportunities
            optimization['optimization_opportunities'] = self._find_keyword_opportunities(
                current_keywords, suggested_keywords, trending_keywords
            )
            
        except Exception as e:
            optimization['error'] = str(e)
            self.logger.error(f"Keyword optimization failed: {e}")
        
        return optimization
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés du texte"""
        try:
            # Clean text
            text = re.sub(r'[^\w\s]', '', text.lower())
            words = text.split()
            
            # Remove stop words and short words
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Count frequencies and return most common
            word_counts = Counter(keywords)
            return [word for word, count in word_counts.most_common(20)]
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def _get_trending_keywords(self, platform: str, category: str) -> List[str]:
        """Récupère les mots-clés tendance"""
        # Simulated trending keywords (would connect to real APIs in production)
        trending_by_platform = {
            'youtube': ['viral', 'trending', '2025', 'new', 'latest', 'best', 'top', 'amazing'],
            'instagram': ['aesthetic', 'vibes', 'mood', 'inspo', 'ootd', 'selfie', 'lifestyle'],
            'tiktok': ['fyp', 'viral', 'trending', 'challenge', 'dance', 'funny', 'relatable'],
            'twitter': ['breaking', 'update', 'news', 'thread', 'opinion', 'hot take'],
            'linkedin': ['professional', 'career', 'business', 'networking', 'industry', 'insights']
        }
        
        category_trending = {
            'music': ['song', 'artist', 'album', 'concert', 'festival', 'new music'],
            'gaming': ['gameplay', 'review', 'esports', 'tournament', 'stream', 'gaming news'],
            'tech': ['tech review', 'gadget', 'software', 'app', 'innovation', 'technology'],
            'lifestyle': ['daily routine', 'life hacks', 'wellness', 'self care', 'motivation'],
            'fitness': ['workout', 'fitness journey', 'gym', 'health tips', 'nutrition']
        }
        
        platform_keywords = trending_by_platform.get(platform, [])
        category_keywords = category_trending.get(category, [])
        
        return platform_keywords + category_keywords
    
    def _generate_keyword_suggestions(self, current_keywords: List[str], category: str, target_audience: Dict) -> Dict[str, List[str]]:
        """Génère des suggestions de mots-clés"""
        suggestions = {
            'primary': [],
            'secondary': [],
            'long_tail': []
        }
        
        try:
            # Base keywords from category
            base_keywords = self.keyword_categories.get(category, [])
            
            # Audience-based keywords
            audience_age = target_audience.get('age_group', 'all')
            audience_interests = target_audience.get('interests', [])
            
            # Primary keywords (high intent, competitive)
            suggestions['primary'] = base_keywords[:5] + current_keywords[:3]
            
            # Secondary keywords (related, moderate competition)
            secondary = []
            for keyword in base_keywords:
                secondary.extend([
                    f"{keyword} tutorial",
                    f"{keyword} guide",
                    f"best {keyword}",
                    f"{keyword} tips"
                ])
            suggestions['secondary'] = secondary[:10]
            
            # Long-tail keywords (specific, low competition)
            long_tail = []
            for keyword in base_keywords[:3]:
                long_tail.extend([
                    f"how to {keyword} for beginners",
                    f"{keyword} {audience_age} 2025",
                    f"best {keyword} for {audience_age}",
                    f"{keyword} step by step guide"
                ])
            suggestions['long_tail'] = long_tail[:8]
            
            # Add audience interest-based keywords
            for interest in audience_interests[:3]:
                suggestions['secondary'].append(f"{interest} {category}")
                suggestions['long_tail'].append(f"best {category} for {interest} lovers")
            
        except Exception as e:
            self.logger.error(f"Keyword suggestion generation failed: {e}")
        
        return suggestions
    
    def _estimate_keyword_difficulty(self, keyword: str, platform: str) -> Dict[str, Any]:
        """Estime la difficulté du mot-clé (simulé)"""
        # Simulated difficulty based on keyword characteristics
        keyword_length = len(keyword.split())
        
        if keyword_length == 1:
            difficulty = 'high'
            score = 80
        elif keyword_length == 2:
            difficulty = 'medium'
            score = 60
        else:
            difficulty = 'low'
            score = 40
        
        # Adjust based on platform
        platform_multipliers = {
            'youtube': 1.2,
            'instagram': 1.0,
            'tiktok': 0.8,
            'twitter': 1.1,
            'linkedin': 1.3
        }
        
        score *= platform_multipliers.get(platform, 1.0)
        score = min(100, max(0, score))
        
        return {
            'difficulty_score': score,
            'difficulty_level': difficulty,
            'competition_estimate': 'high' if score > 70 else 'medium' if score > 40 else 'low',
            'recommended_use': score < 60
        }
    
    def _find_keyword_opportunities(self, current: List[str], suggested: Dict, trending: List[str]) -> List[Dict[str, Any]]:
        """Trouve les opportunités d'optimisation des mots-clés"""
        opportunities = []
        
        # Missing trending keywords
        missing_trending = [kw for kw in trending if kw not in current]
        if missing_trending:
            opportunities.append({
                'type': 'trending_keywords',
                'priority': 'high',
                'description': 'Add trending keywords to increase discoverability',
                'keywords': missing_trending[:5],
                'expected_impact': 'Increased reach and visibility'
            })
        
        # Long-tail opportunities
        if len(current) < 10:
            opportunities.append({
                'type': 'long_tail_expansion',
                'priority': 'medium',
                'description': 'Add long-tail keywords for niche targeting',
                'keywords': suggested['long_tail'][:3],
                'expected_impact': 'Better ranking for specific searches'
            })
        
        # Semantic keyword gaps
        all_suggested = suggested['primary'] + suggested['secondary']
        missing_semantic = [kw for kw in all_suggested if kw not in current]
        if missing_semantic:
            opportunities.append({
                'type': 'semantic_expansion',
                'priority': 'medium',
                'description': 'Add semantically related keywords',
                'keywords': missing_semantic[:4],
                'expected_impact': 'Improved content relevance'
            })
        
        return opportunities
    
    def _optimize_for_platform(self, content_data: Dict, platform: str, keyword_data: Dict) -> Dict[str, Any]:
        """Optimise pour une plateforme spécifique"""
        optimization = {
            'platform_specific_tips': [],
            'content_structure_optimization': {},
            'engagement_optimization': {},
            'algorithm_considerations': {}
        }
        
        try:
            platform_config = self.seo_config['platform_requirements'].get(platform, {})
            
            if platform == 'youtube':
                optimization.update(self._optimize_for_youtube(content_data, keyword_data, platform_config))
            elif platform == 'instagram':
                optimization.update(self._optimize_for_instagram(content_data, keyword_data, platform_config))
            elif platform == 'tiktok':
                optimization.update(self._optimize_for_tiktok(content_data, keyword_data, platform_config))
            elif platform == 'twitter':
                optimization.update(self._optimize_for_twitter(content_data, keyword_data, platform_config))
            elif platform == 'linkedin':
                optimization.update(self._optimize_for_linkedin(content_data, keyword_data, platform_config))
            
        except Exception as e:
            optimization['error'] = str(e)
            self.logger.error(f"Platform optimization failed: {e}")
        
        return optimization
    
    def _optimize_for_youtube(self, content_data: Dict, keyword_data: Dict, config: Dict) -> Dict[str, Any]:
        """Optimisation spécifique à YouTube"""
        return {
            'platform_specific_tips': [
                'Use primary keyword in first 60 characters of title',
                'Include timestamps in description for better user experience',
                'Add closed captions for better accessibility and SEO',
                'Use custom thumbnail with high contrast and text overlay',
                'Create compelling hook in first 15 seconds'
            ],
            'content_structure_optimization': {
                'title_optimization': 'Front-load primary keyword, keep under 60 characters',
                'description_optimization': 'Use first 125 characters for key information, include links and CTAs',
                'tags_strategy': 'Mix broad and specific tags, include misspellings of popular terms'
            },
            'engagement_optimization': {
                'cta_placement': 'Ask for likes/subscribes at peak engagement moments',
                'retention_strategy': 'Use pattern interrupts and preview upcoming content',
                'comment_engagement': 'Respond to comments within first hour for algorithm boost'
            },
            'algorithm_considerations': {
                'watch_time_priority': 'Focus on average view duration over total views',
                'click_through_rate': 'A/B test thumbnails and titles for higher CTR',
                'session_duration': 'Create playlists and end screens to keep viewers on platform'
            }
        }
    
    def _optimize_for_instagram(self, content_data: Dict, keyword_data: Dict, config: Dict) -> Dict[str, Any]:
        """Optimisation spécifique à Instagram"""
        return {
            'platform_specific_tips': [
                'Use 11 hashtags for optimal reach',
                'Mix popular and niche hashtags',
                'Include location tags for local discovery',
                'Post during peak audience activity hours',
                'Use Stories highlights for evergreen content'
            ],
            'content_structure_optimization': {
                'caption_optimization': 'Hook in first line, use line breaks for readability',
                'hashtag_placement': 'Mix hashtags in caption and first comment',
                'alt_text_usage': 'Write descriptive alt text for accessibility and searchability'
            },
            'engagement_optimization': {
                'story_strategy': 'Use polls, questions, and interactive stickers',
                'reel_optimization': 'Use trending audio and participate in challenges',
                'ugc_encouragement': 'Create branded hashtags and encourage user-generated content'
            },
            'algorithm_considerations': {
                'relationship_signals': 'Prioritize engagement from close connections',
                'interest_indicators': 'Use relevant hashtags and location tags',
                'recency_factor': 'Post when audience is most active for immediate engagement'
            }
        }
    
    def _optimize_for_tiktok(self, content_data: Dict, keyword_data: Dict, config: Dict) -> Dict[str, Any]:
        """Optimisation spécifique à TikTok"""
        return {
            'platform_specific_tips': [
                'Use trending sounds and music',
                'Participate in trending challenges and hashtags',
                'Hook viewers in first 3 seconds',
                'Keep videos between 15-60 seconds for best performance',
                'Post 1-3 times daily for maximum reach'
            ],
            'content_structure_optimization': {
                'caption_optimization': 'Use questions and CTAs to encourage comments',
                'hashtag_strategy': 'Mix trending and niche hashtags, max 5 hashtags',
                'sound_selection': 'Use trending audio or create original sounds'
            },
            'engagement_optimization': {
                'comment_baiting': 'Ask questions or share controversial (safe) opinions',
                'duet_collaboration': 'Create content that encourages duets and stitches',
                'live_streaming': 'Go live to boost engagement and reach'
            },
            'algorithm_considerations': {
                'completion_rate': 'Create content that people watch to the end',
                'share_rate': 'Make shareable content with universal appeal',
                'fyp_optimization': 'Use relevant hashtags and trending elements for For You Page'
            }
        }
    
    def _optimize_for_twitter(self, content_data: Dict, keyword_data: Dict, config: Dict) -> Dict[str, Any]:
        """Optimisation spécifique à Twitter"""
        return {
            'platform_specific_tips': [
                'Tweet during peak hours (9-10 AM, 7-9 PM)',
                'Use 1-2 relevant hashtags maximum',
                'Include media for 2.5x more engagement',
                'Create threads for complex topics',
                'Engage with trending topics when relevant'
            ],
            'content_structure_optimization': {
                'tweet_optimization': 'Front-load important information, use line breaks',
                'hashtag_usage': 'Use hashtags strategically, not excessively',
                'thread_structure': 'Number tweets and use clear progression'
            },
            'engagement_optimization': {
                'timing_strategy': 'Tweet when target audience is most active',
                'retweet_strategy': 'Retweet with commentary to add value',
                'reply_engagement': 'Respond quickly to build relationships'
            },
            'algorithm_considerations': {
                'recency_factor': 'Tweet regularly for sustained visibility',
                'engagement_velocity': 'Encourage quick engagement after posting',
                'relationship_signals': 'Build genuine connections with audience'
            }
        }
    
    def _optimize_for_linkedin(self, content_data: Dict, keyword_data: Dict, config: Dict) -> Dict[str, Any]:
        """Optimisation spécifique à LinkedIn"""
        return {
            'platform_specific_tips': [
                'Post professional, value-driven content',
                'Use industry-specific keywords',
                'Share personal insights and experiences',
                'Engage with others\' content before posting',
                'Use LinkedIn native video for higher reach'
            ],
            'content_structure_optimization': {
                'post_optimization': 'Start with hook, use short paragraphs, end with question',
                'hashtag_strategy': 'Use 3-5 professional, industry-relevant hashtags',
                'professional_tone': 'Maintain professional but personable voice'
            },
            'engagement_optimization': {
                'network_engagement': 'Engage with connections\' content regularly',
                'thought_leadership': 'Share industry insights and professional opinions',
                'community_building': 'Build professional network through valuable content'
            },
            'algorithm_considerations': {
                'professional_relevance': 'Focus on career and industry-related content',
                'network_signals': 'Prioritize engagement from professional network',
                'value_creation': 'Share actionable insights and professional knowledge'
            }
        }
    
    def _develop_hashtag_strategy(self, keyword_data: Dict, platform: str, target_audience: Dict) -> Dict[str, Any]:
        """Développe une stratégie de hashtags"""
        strategy = {
            'recommended_hashtags': [],
            'hashtag_mix': {},
            'hashtag_research': {},
            'performance_prediction': {},
            'hashtag_calendar': {}
        }
        
        try:
            primary_keywords = keyword_data.get('primary_keywords', [])
            trending_keywords = keyword_data.get('trending_keywords', [])
            
            # Platform-specific hashtag limits
            hashtag_limits = {
                'instagram': 30,
                'tiktok': 10,
                'twitter': 3,
                'linkedin': 10,
                'youtube': 15
            }
            
            max_hashtags = hashtag_limits.get(platform, 10)
            
            # Generate hashtag mix
            if platform == 'instagram':
                strategy['hashtag_mix'] = {
                    'high_competition': 2,  # 1M+ posts
                    'medium_competition': 4,  # 100K-1M posts
                    'low_competition': 3,   # 10K-100K posts
                    'niche_specific': 2     # <10K posts
                }
            elif platform == 'tiktok':
                strategy['hashtag_mix'] = {
                    'trending': 2,
                    'niche': 2,
                    'branded': 1
                }
            else:
                strategy['hashtag_mix'] = {
                    'primary': 2,
                    'secondary': 3,
                    'trending': 2
                }
            
            # Generate recommended hashtags
            recommended = []
            
            # Add primary keyword hashtags
            for keyword in primary_keywords[:3]:
                recommended.append(f"#{keyword.replace(' ', '')}")
            
            # Add trending hashtags
            for trend in trending_keywords[:2]:
                recommended.append(f"#{trend.replace(' ', '')}")
            
            # Add platform-specific hashtags
            platform_hashtags = {
                'instagram': ['#instagram', '#insta', '#instagood'],
                'tiktok': ['#fyp', '#foryou', '#viral'],
                'twitter': ['#twitter', '#tweet'],
                'linkedin': ['#linkedin', '#professional'],
                'youtube': ['#youtube', '#video', '#subscribe']
            }
            
            recommended.extend(platform_hashtags.get(platform, [])[:2])
            
            # Limit to platform maximum
            strategy['recommended_hashtags'] = recommended[:max_hashtags]
            
            # Hashtag research data (simulated)
            for hashtag in strategy['recommended_hashtags'][:5]:
                strategy['hashtag_research'][hashtag] = {
                    'estimated_posts': np.random.randint(1000, 1000000),
                    'competition_level': np.random.choice(['low', 'medium', 'high']),
                    'engagement_rate': round(np.random.uniform(0.5, 5.0), 2)
                }
            
            # Performance prediction
            strategy['performance_prediction'] = {
                'expected_reach_boost': '15-25%',
                'engagement_increase': '10-20%',
                'discoverability_score': 85,
                'hashtag_optimization_score': self._calculate_hashtag_score(strategy['recommended_hashtags'], platform)
            }
            
        except Exception as e:
            strategy['error'] = str(e)
            self.logger.error(f"Hashtag strategy development failed: {e}")
        
        return strategy
    
    def _calculate_hashtag_score(self, hashtags: List[str], platform: str) -> int:
        """Calcule le score d'optimisation des hashtags"""
        try:
            score = 0
            total_possible = 100
            
            # Check hashtag count
            platform_optimal = {
                'instagram': 11,
                'tiktok': 5,
                'twitter': 2,
                'linkedin': 5,
                'youtube': 10
            }
            
            optimal_count = platform_optimal.get(platform, 5)
            count_score = min(len(hashtags) / optimal_count, 1.0) * 30
            score += count_score
            
            # Check hashtag diversity (different lengths and types)
            lengths = [len(tag) for tag in hashtags]
            if len(set(lengths)) > 1:
                score += 20  # Diversity bonus
            
            # Check for platform-specific hashtags
            platform_specific = {
                'instagram': ['insta', 'gram', 'ig'],
                'tiktok': ['fyp', 'foryou', 'viral'],
                'twitter': ['twitter', 'tweet'],
                'linkedin': ['linkedin', 'professional'],
                'youtube': ['youtube', 'video']
            }
            
            specific_tags = platform_specific.get(platform, [])
            if any(tag.lower() in ' '.join(hashtags).lower() for tag in specific_tags):
                score += 20
            
            # Check for overly generic hashtags (penalty)
            generic_tags = ['#love', '#instagood', '#follow', '#like']
            generic_count = sum(1 for tag in hashtags if tag in generic_tags)
            score -= generic_count * 5
            
            # Ensure score is within bounds
            return max(0, min(100, int(score)))
            
        except Exception as e:
            self.logger.error(f"Hashtag score calculation failed: {e}")
            return 50
    
    def _calculate_seo_score(self, content_analysis: Dict, keyword_opt: Dict, platform_opt: Dict, hashtag_strategy: Dict) -> int:
        """Calcule le score SEO global"""
        try:
            total_score = 0
            weights = self.seo_config['seo_factors']
            
            # Content structure score
            compliance = content_analysis.get('platform_compliance', {})
            structure_score = compliance.get('overall_score', 50)
            total_score += structure_score * weights.get('content_structure', 0.2)
            
            # Keyword optimization score
            primary_kw_count = len(keyword_opt.get('primary_keywords', []))
            keyword_score = min(primary_kw_count * 20, 100)
            total_score += keyword_score * weights.get('keyword_optimization', 0.25)
            
            # Platform specificity score
            platform_tips_count = len(platform_opt.get('platform_specific_tips', []))
            platform_score = min(platform_tips_count * 20, 100)
            total_score += platform_score * weights.get('platform_specificity', 0.15)
            
            # Hashtag optimization score
            hashtag_score = hashtag_strategy.get('performance_prediction', {}).get('hashtag_optimization_score', 50)
            total_score += hashtag_score * weights.get('trending_relevance', 0.1)
            
            # Readability score
            readability = content_analysis.get('readability', {})
            flesch_score = readability.get('flesch_score', 50)
            readability_normalized = min(max(flesch_score, 0), 100)
            total_score += readability_normalized * weights.get('engagement_signals', 0.2)
            
            # Competition analysis bonus
            opportunities = keyword_opt.get('optimization_opportunities', [])
            competition_score = max(0, 100 - len(opportunities) * 20)
            total_score += competition_score * weights.get('competition_analysis', 0.1)
            
            return max(0, min(100, int(total_score)))
            
        except Exception as e:
            self.logger.error(f"SEO score calculation failed: {e}")
            return 50
    
    def _analyze_competition(self, keywords: List[str], platform: str) -> Dict[str, Any]:
        """Analyse la concurrence (simulé)"""
        competition = {
            'competitor_analysis': {},
            'market_gaps': [],
            'competitive_keywords': [],
            'opportunity_score': 0
        }
        
        try:
            # Simulated competitor analysis
            for keyword in keywords[:3]:
                competition['competitor_analysis'][keyword] = {
                    'competition_level': np.random.choice(['low', 'medium', 'high']),
                    'top_creators': [f"creator_{i}" for i in range(3)],
                    'average_engagement': round(np.random.uniform(1.0, 10.0), 2),
                    'content_gap_opportunity': np.random.choice([True, False])
                }
            
            # Market gaps (simulated)
            competition['market_gaps'] = [
                'Long-form educational content',
                'Behind-the-scenes content',
                'Beginner-friendly tutorials',
                'Interactive Q&A sessions'
            ]
            
            # Opportunity score
            high_competition = sum(1 for data in competition['competitor_analysis'].values() 
                                 if data['competition_level'] == 'high')
            competition['opportunity_score'] = max(0, 100 - (high_competition * 25))
            
        except Exception as e:
            competition['error'] = str(e)
            self.logger.error(f"Competition analysis failed: {e}")
        
        return competition
    
    def _generate_seo_recommendations(self, seo_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations SEO"""
        recommendations = []
        
        try:
            seo_score = seo_result.get('seo_score', 0)
            platform = seo_result.get('platform')
            
            # High priority recommendations based on score
            if seo_score < 60:
                recommendations.append({
                    'priority': 'high',
                    'category': 'Overall SEO',
                    'title': 'Comprehensive SEO Optimization Needed',
                    'description': f'Your SEO score is {seo_score}/100. Focus on keyword optimization and platform compliance.',
                    'action_items': [
                        'Optimize title with primary keywords',
                        'Improve description length and structure',
                        'Add relevant hashtags',
                        'Follow platform-specific guidelines'
                    ],
                    'expected_impact': 'Significant improvement in discoverability'
                })
            
            # Content analysis recommendations
            content_analysis = seo_result.get('content_analysis', {})
            compliance = content_analysis.get('platform_compliance', {})
            
            for issue in compliance.get('non_compliant_aspects', []):
                recommendations.append({
                    'priority': 'medium',
                    'category': 'Platform Compliance',
                    'title': f'Fix {issue.replace("_", " ").title()}',
                    'description': f'Your {issue} doesn\'t meet platform requirements',
                    'action_items': compliance.get('recommendations', []),
                    'expected_impact': 'Better platform algorithm performance'
                })
            
            # Keyword optimization recommendations
            keyword_opt = seo_result.get('keyword_optimization', {})
            opportunities = keyword_opt.get('optimization_opportunities', [])
            
            for opportunity in opportunities[:2]:
                recommendations.append({
                    'priority': opportunity.get('priority', 'medium'),
                    'category': 'Keyword Optimization',
                    'title': opportunity.get('description', 'Keyword Optimization'),
                    'description': opportunity.get('expected_impact', 'Improve keyword targeting'),
                    'action_items': [f'Add keywords: {", ".join(opportunity.get("keywords", [])[:3])}'],
                    'expected_impact': opportunity.get('expected_impact', 'Better search visibility')
                })
            
            # Platform-specific recommendations
            platform_opt = seo_result.get('platform_optimization', {})
            platform_tips = platform_opt.get('platform_specific_tips', [])
            
            if platform_tips:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'Platform Optimization',
                    'title': f'Optimize for {platform.title()}',
                    'description': f'Implement {platform}-specific best practices',
                    'action_items': platform_tips[:3],
                    'expected_impact': f'Better performance on {platform}'
                })
            
            # Hashtag recommendations
            hashtag_strategy = seo_result.get('hashtag_strategy', {})
            hashtag_score = hashtag_strategy.get('performance_prediction', {}).get('hashtag_optimization_score', 100)
            
            if hashtag_score < 80:
                recommended_hashtags = hashtag_strategy.get('recommended_hashtags', [])
                recommendations.append({
                    'priority': 'medium',
                    'category': 'Hashtag Strategy',
                    'title': 'Improve Hashtag Strategy',
                    'description': 'Your hashtag strategy needs optimization',
                    'action_items': [
                        f'Use recommended hashtags: {", ".join(recommended_hashtags[:5])}',
                        'Mix high and low competition hashtags',
                        'Research trending hashtags in your niche'
                    ],
                    'expected_impact': 'Increased discoverability and reach'
                })
            
        except Exception as e:
            self.logger.error(f"SEO recommendations generation failed: {e}")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _create_optimized_content(self, content_data: Dict, keyword_opt: Dict, platform_opt: Dict, hashtag_strategy: Dict) -> Dict[str, Any]:
        """Crée du contenu optimisé"""
        optimized = {
            'optimized_title': '',
            'optimized_description': '',
            'optimized_tags': [],
            'recommended_hashtags': [],
            'seo_improvements': []
        }
        
        try:
            original_title = content_data.get('title', '')
            original_description = content_data.get('description', '')
            primary_keywords = keyword_opt.get('primary_keywords', [])
            
            # Optimize title
            if primary_keywords and original_title:
                primary_keyword = primary_keywords[0]
                if primary_keyword.lower() not in original_title.lower():
                    optimized['optimized_title'] = f"{primary_keyword.title()}: {original_title}"
                    optimized['seo_improvements'].append('Added primary keyword to title')
                else:
                    optimized['optimized_title'] = original_title
            else:
                optimized['optimized_title'] = original_title
            
            # Optimize description
            if original_description:
                optimized_desc = original_description
                
                # Add keywords naturally
                for keyword in primary_keywords[:2]:
                    if keyword.lower() not in optimized_desc.lower():
                        optimized_desc += f"\n\n#{keyword.replace(' ', '')} #content"
                        optimized['seo_improvements'].append(f'Added keyword: {keyword}')
                
                optimized['optimized_description'] = optimized_desc
            else:
                optimized['optimized_description'] = original_description
            
            # Optimize tags
            original_tags = content_data.get('tags', [])
            new_tags = list(set(original_tags + primary_keywords[:5]))
            optimized['optimized_tags'] = new_tags
            
            if len(new_tags) > len(original_tags):
                optimized['seo_improvements'].append('Added relevant tags')
            
            # Add hashtags
            optimized['recommended_hashtags'] = hashtag_strategy.get('recommended_hashtags', [])
            
            if not optimized['seo_improvements']:
                optimized['seo_improvements'] = ['Content already well optimized']
            
        except Exception as e:
            optimized['error'] = str(e)
            self.logger.error(f"Content optimization failed: {e}")
        
        return optimized
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour le SEO"""
        if not isinstance(input_data, dict):
            return False
        
        content_data = input_data.get('content_data')
        if not isinstance(content_data, dict):
            return False
        
        # At least title or description should be provided
        if not content_data.get('title') and not content_data.get('description'):
            return False
        
        return True


class AsyncSEOProcessor(AsyncBaseProcessor):
    """Version asynchrone du processeur SEO"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sync_processor = SEOProcessor(config)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Traitement asynchrone du SEO"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sync_processor.process_with_stats, 
            input_data
        )
    
    async def validate_input(self, input_data: Any) -> bool:
        """Validation asynchrone"""
        return self.sync_processor.validate_input(input_data)
