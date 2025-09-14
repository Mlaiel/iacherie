"""AI Content Optimization Engine
Advanced AI-powered content optimization for maximum SEO performance.

Features:
- GPT-powered content enhancement
- Semantic keyword optimization
- Content structure analysis
- Readability optimization
- Multi-language support

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + ML Engineer expertise applied
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json

try:
    import openai
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    import spacy
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
except ImportError as e:
    logging.warning(f"Optional dependencies not available: {e}")

logger = logging.getLogger(__name__)

@dataclass
class ContentOptimizationResult:
    """Result of AI content optimization."""
    original_content: str
    optimized_content: str
    seo_score: float
    keywords_added: List[str]
    readability_score: float
    semantic_score: float
    optimization_suggestions: List[str]
    meta_suggestions: Dict[str, str]
    performance_metrics: Dict[str, Any]

@dataclass
class SEOOptimizationConfig:
    """Configuration for SEO optimization."""
    target_keywords: List[str]
    content_type: str  # blog, product, landing, social
    target_audience: str
    language: str = "en"
    max_content_length: int = 2000
    min_keyword_density: float = 0.01
    max_keyword_density: float = 0.03
    target_readability: float = 60.0
    enable_ai_enhancement: bool = True

class AIContentOptimizer:
    """Advanced AI-powered content optimization engine."""
    
    def __init__(self, openai_api_key -> None: Optional[str] = None) -> None:
        """Initialize the AI Content Optimizer.
        
        Args:
            openai_api_key: OpenAI API key for GPT models
        """
        self.openai_api_key = openai_api_key
        self.nlp_model = None
        self.sentiment_analyzer = None
        self._load_models()
        
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            pass
            
    def _load_models(self) -> None:
        """Load AI models for content optimization."""
        try:
            # Load spaCy model for NLP processing
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found. Some features may be limited.")
                
            # Load sentiment analysis model
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
            except Exception as e:
                logger.warning(f"Could not load sentiment analyzer: {e}")
                
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
    
    async def optimize_content(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> ContentOptimizationResult:
        """Optimize content using AI algorithms.
        
        Args:
            content: Original content to optimize
            config: Optimization configuration
            
        Returns:
            ContentOptimizationResult with optimized content and metrics
        """
        try:
            # Analyze original content
            original_analysis = await self._analyze_content(content, config)
            
            # Apply AI optimizations
            optimized_content = content
            optimization_suggestions = []
            keywords_added = []
            
            # 1. Keyword optimization
            optimized_content, added_keywords = await self._optimize_keywords(
                optimized_content, config.target_keywords, config
            )
            keywords_added.extend(added_keywords)
            
            # 2. Readability optimization
            optimized_content, readability_suggestions = await self._optimize_readability(
                optimized_content, config
            )
            optimization_suggestions.extend(readability_suggestions)
            
            # 3. Semantic optimization
            optimized_content, semantic_score = await self._optimize_semantics(
                optimized_content, config
            )
            
            # 4. Structure optimization
            optimized_content, structure_suggestions = await self._optimize_structure(
                optimized_content, config
            )
            optimization_suggestions.extend(structure_suggestions)
            
            # 5. AI enhancement (if enabled)
            if config.enable_ai_enhancement and self.openai_api_key:
                optimized_content, ai_suggestions = await self._enhance_with_ai(
                    optimized_content, config
                )
                optimization_suggestions.extend(ai_suggestions)
            
            # Analyze optimized content
            optimized_analysis = await self._analyze_content(optimized_content, config)
            
            # Generate meta suggestions
            meta_suggestions = await self._generate_meta_suggestions(
                optimized_content, config
            )
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                original_analysis, optimized_analysis
            )
            
            return ContentOptimizationResult(
                original_content=content,
                optimized_content=optimized_content,
                seo_score=optimized_analysis["seo_score"],
                keywords_added=keywords_added,
                readability_score=optimized_analysis["readability_score"],
                semantic_score=semantic_score,
                optimization_suggestions=optimization_suggestions,
                meta_suggestions=meta_suggestions,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            raise
    
    async def _analyze_content(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> Dict[str, Any]:
        """Analyze content for SEO metrics.
        
        Args:
            content: Content to analyze
            config: Optimization configuration
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {}
            
            # Basic metrics
            analysis["word_count"] = len(content.split())
            analysis["character_count"] = len(content)
            analysis["sentence_count"] = len(sent_tokenize(content))
            
            # Readability analysis
            try:
                analysis["readability_score"] = flesch_reading_ease(content)
                analysis["grade_level"] = flesch_kincaid_grade(content)
            except:
                analysis["readability_score"] = 50.0
                analysis["grade_level"] = 8.0
            
            # Keyword analysis
            keyword_analysis = self._analyze_keywords(content, config.target_keywords)
            analysis.update(keyword_analysis)
            
            # SEO score calculation
            analysis["seo_score"] = self._calculate_seo_score(analysis, config)
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                try:
                    sentiment_results = self.sentiment_analyzer(content[:512])  # Limit for model
                    analysis["sentiment"] = sentiment_results[0] if sentiment_results else {"label": "NEUTRAL", "score": 0.5}
                except:
                    analysis["sentiment"] = {"label": "NEUTRAL", "score": 0.5}
            else:
                analysis["sentiment"] = {"label": "NEUTRAL", "score": 0.5}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {"seo_score": 0.0, "readability_score": 0.0}
    
    def _analyze_keywords(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword usage in content."""
        try:
            content_lower = content.lower()
            total_words = len(content.split())
            
            keyword_analysis = {
                "keyword_density": {},
                "keyword_positions": {},
                "total_keyword_mentions": 0
            }
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                mentions = content_lower.count(keyword_lower)
                density = mentions / total_words if total_words > 0 else 0
                
                keyword_analysis["keyword_density"][keyword] = density
                keyword_analysis["keyword_positions"][keyword] = [
                    m.start() for m in re.finditer(re.escape(keyword_lower), content_lower)
                ]
                keyword_analysis["total_keyword_mentions"] += mentions
            
            return keyword_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing keywords: {e}")
            return {"keyword_density": {}, "keyword_positions": {}, "total_keyword_mentions": 0}
    
    def _calculate_seo_score(self, analysis: Dict[str, Any], config: SEOOptimizationConfig) -> float:
        """Calculate overall SEO score based on analysis."""
        try:
            score_components = []
            
            # Readability score (0-100, higher is better)
            readability_score = min(analysis.get("readability_score", 0) / 100, 1.0)
            score_components.append(readability_score * 0.3)
            
            # Keyword density score
            keyword_density_score = 0
            for keyword, density in analysis.get("keyword_density", {}).items():
                if config.min_keyword_density <= density <= config.max_keyword_density:
                    keyword_density_score += 1
            keyword_density_score = min(keyword_density_score / len(config.target_keywords) if config.target_keywords else 0, 1.0)
            score_components.append(keyword_density_score * 0.4)
            
            # Content length score
            word_count = analysis.get("word_count", 0)
            length_score = min(word_count / 300, 1.0) if word_count > 0 else 0  # Optimal around 300+ words
            score_components.append(length_score * 0.2)
            
            # Sentiment score (positive sentiment is generally better for SEO)
            sentiment = analysis.get("sentiment", {})
            sentiment_score = sentiment.get("score", 0.5) if sentiment.get("label") == "POSITIVE" else 0.5
            score_components.append(sentiment_score * 0.1)
            
            return sum(score_components)
            
        except Exception as e:
            logger.error(f"Error calculating SEO score: {e}")
            return 0.0
    
    async def _optimize_keywords(
        self,
        content: str,
        target_keywords: List[str],
        config: SEOOptimizationConfig
    ) -> Tuple[str, List[str]]:
        """Optimize keyword placement and density."""
        try:
            optimized_content = content
            added_keywords = []
            
            for keyword in target_keywords:
                current_density = content.lower().count(keyword.lower()) / len(content.split())
                
                if current_density < config.min_keyword_density:
                    # Add keyword naturally to content
                    sentences = sent_tokenize(optimized_content)
                    if sentences:
                        # Insert keyword in a natural way
                        insertion_point = len(sentences) // 2
                        keyword_sentence = f"This relates to {keyword} in important ways."
                        sentences.insert(insertion_point, keyword_sentence)
                        optimized_content = " ".join(sentences)
                        added_keywords.append(keyword)
            
            return optimized_content, added_keywords
            
        except Exception as e:
            logger.error(f"Error optimizing keywords: {e}")
            return content, []
    
    async def _optimize_readability(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> Tuple[str, List[str]]:
        """Optimize content readability."""
        try:
            suggestions = []
            optimized_content = content
            
            # Check sentence length
            sentences = sent_tokenize(content)
            long_sentences = [s for s in sentences if len(s.split()) > 20]
            
            if long_sentences:
                suggestions.append(f"Consider breaking down {len(long_sentences)} long sentences for better readability")
            
            # Check paragraph structure
            paragraphs = content.split('\n\n')
            long_paragraphs = [p for p in paragraphs if len(p.split()) > 150]
            
            if long_paragraphs:
                suggestions.append(f"Consider breaking down {len(long_paragraphs)} long paragraphs")
            
            return optimized_content, suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing readability: {e}")
            return content, []
    
    async def _optimize_semantics(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> Tuple[str, float]:
        """Optimize semantic content structure."""
        try:
            semantic_score = 0.7  # Default semantic score
            
            if self.nlp_model:
                doc = self.nlp_model(content[:1000000])  # Limit for processing
                
                # Extract entities and key phrases
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                
                # Calculate semantic richness
                unique_entities = len(set([ent[0].lower() for ent in entities]))
                semantic_score = min(unique_entities / 10, 1.0)  # Normalize
            
            return content, semantic_score
            
        except Exception as e:
            logger.error(f"Error optimizing semantics: {e}")
            return content, 0.5
    
    async def _optimize_structure(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> Tuple[str, List[str]]:
        """Optimize content structure for SEO."""
        try:
            suggestions = []
            optimized_content = content
            
            # Check for headers
            if not any(line.startswith('#') for line in content.split('\n')):
                suggestions.append("Consider adding headers (H1, H2, H3) to improve content structure")
            
            # Check for lists
            if '•' not in content and not any(line.strip().startswith(('1.', '2.', '-', '*')) for line in content.split('\n')):
                suggestions.append("Consider adding bullet points or numbered lists for better readability")
            
            return optimized_content, suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing structure: {e}")
            return content, []
    
    async def _enhance_with_ai(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> Tuple[str, List[str]]:
        """Enhance content using AI models."""
        try:
            suggestions = []
            
            if not self.openai_api_key:
                return content, ["AI enhancement requires OpenAI API key"]
            
            # Use OpenAI for content enhancement
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Enhance the following content for SEO optimization:
            - Target keywords: {', '.join(config.target_keywords)}
            - Content type: {config.content_type}
            - Target audience: {config.target_audience}
            
            Original content:
            {content}
            
            Please provide an enhanced version that:
            1. Naturally incorporates target keywords
            2. Improves readability
            3. Maintains the original meaning
            4. Optimizes for search engines
            
            Enhanced content:
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            enhanced_content = response.choices[0].message.content.strip()
            suggestions.append("Content enhanced using AI optimization")
            
            return enhanced_content, suggestions
            
        except Exception as e:
            logger.error(f"Error enhancing with AI: {e}")
            return content, [f"AI enhancement failed: {str(e)}"]
    
    async def _generate_meta_suggestions(
        self,
        content: str,
        config: SEOOptimizationConfig
    ) -> Dict[str, str]:
        """Generate meta tag suggestions."""
        try:
            # Extract first sentence for description
            sentences = sent_tokenize(content)
            first_sentence = sentences[0] if sentences else ""
            
            # Generate title from content
            words = content.split()
            title_words = words[:10]  # First 10 words
            suggested_title = " ".join(title_words)
            
            # Include target keywords in suggestions
            primary_keyword = config.target_keywords[0] if config.target_keywords else "content"
            
            return {
                "title": f"{suggested_title} - {primary_keyword}",
                "description": f"{first_sentence[:150]}...",
                "keywords": ", ".join(config.target_keywords),
                "og_title": suggested_title,
                "og_description": first_sentence[:200]
            }
            
        except Exception as e:
            logger.error(f"Error generating meta suggestions: {e}")
            return {}
    
    def _calculate_performance_metrics(
        self,
        original_analysis: Dict[str, Any],
        optimized_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate performance improvement metrics."""
        try:
            return {
                "seo_score_improvement": optimized_analysis["seo_score"] - original_analysis["seo_score"],
                "readability_improvement": optimized_analysis["readability_score"] - original_analysis["readability_score"],
                "keyword_mentions_added": optimized_analysis["total_keyword_mentions"] - original_analysis["total_keyword_mentions"],
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}

    async def batch_optimize(
        self,
        contents: List[str],
        configs: List[SEOOptimizationConfig]
    ) -> List[ContentOptimizationResult]:
        """Optimize multiple contents in batch."""
        try:
            tasks = [
                self.optimize_content(content, config)
                for content, config in zip(contents, configs)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error optimizing content {i}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch optimization: {e}")
            return []