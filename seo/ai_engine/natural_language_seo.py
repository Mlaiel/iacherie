"""Natural Language SEO Engine
Advanced NLP-powered SEO optimization for natural content enhancement.

Features:
- Natural language understanding
- Semantic search optimization
- Context-aware keyword integration
- Intent-based content optimization
- Multi-language NLP support

Author: Fahed Mlaiel (mlaiel@live.de)
ML Engineer + IA Prompt Engineer expertise applied
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
import json
import math
from collections import Counter

try:
    import spacy
    from spacy.matcher import Matcher
    import nltk
    from nltk.corpus import wordnet, stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
except ImportError as e:
    logging.warning(f"Optional dependencies not available: {e}")

logger = logging.getLogger(__name__)

@dataclass
class NLPAnalysisResult:
    """Result of NLP analysis."""
    entities: List[Tuple[str, str]]  # (entity, label)
    semantic_keywords: List[str]
    topic_clusters: List[List[str]]
    intent_classification: str
    readability_metrics: Dict[str, float]
    language_quality_score: float
    semantic_density: float
    coherence_score: float

@dataclass
class SemanticOptimizationConfig:
    """Configuration for semantic optimization."""
    target_keywords: List[str]
    semantic_keywords: List[str]
    content_intent: str  # informational, transactional, navigational
    target_language: str = "en"
    context_window: int = 100
    semantic_similarity_threshold: float = 0.7
    enable_entity_linking: bool = True
    enable_topic_modeling: bool = True

class NaturalLanguageSEOEngine:
    """Advanced Natural Language SEO optimization engine."""
    
    def __init__(self) -> None:
        """Initialize the Natural Language SEO Engine."""
        self.nlp_models = {}
        self.semantic_models = {}
        self.entity_matcher = None
        self._load_nlp_models()
        
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
    
    def _load_nlp_models(self) -> None:
        """Load NLP models for different languages."""
        try:
            # Load spaCy models for different languages
            language_models = {
                "en": "en_core_web_sm",
                "fr": "fr_core_news_sm", 
                "de": "de_core_news_sm",
                "es": "es_core_news_sm"
            }
            
            for lang, model_name in language_models.items():
                try:
                    self.nlp_models[lang] = spacy.load(model_name)
                    logger.info(f"Loaded {model_name} for {lang}")
                except OSError:
                    logger.warning(f"Model {model_name} not found for {lang}")
            
            # Load semantic similarity model
            try:
                self.semantic_models["similarity"] = pipeline(
                    "feature-extraction",
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
            except Exception as e:
                logger.warning(f"Could not load semantic similarity model: {e}")
            
            # Load intent classification model
            try:
                self.semantic_models["intent"] = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
            except Exception as e:
                logger.warning(f"Could not load intent classification model: {e}")
                
        except Exception as e:
            logger.error(f"Error loading NLP models: {e}")
    
    async def analyze_natural_language(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> NLPAnalysisResult:
        """Perform comprehensive NLP analysis of content.
        
        Args:
            content: Text content to analyze
            config: Analysis configuration
            
        Returns:
            NLPAnalysisResult with detailed NLP analysis
        """
        try:
            # Get NLP model for target language
            nlp_model = self.nlp_models.get(config.target_language)
            if not nlp_model:
                nlp_model = self.nlp_models.get("en")  # Fallback to English
            
            if not nlp_model:
                logger.warning("No NLP model available")
                return self._create_empty_analysis()
            
            # Process content with spaCy
            doc = nlp_model(content)
            
            # Extract entities
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Extract semantic keywords
            semantic_keywords = await self._extract_semantic_keywords(content, config)
            
            # Perform topic clustering
            topic_clusters = await self._cluster_topics(content, config)
            
            # Classify content intent
            intent = await self._classify_intent(content, config)
            
            # Calculate readability metrics
            readability_metrics = self._calculate_readability_metrics(content, doc)
            
            # Calculate language quality score
            language_quality_score = self._calculate_language_quality(doc)
            
            # Calculate semantic density
            semantic_density = self._calculate_semantic_density(content, config.target_keywords)
            
            # Calculate coherence score
            coherence_score = self._calculate_coherence_score(doc)
            
            return NLPAnalysisResult(
                entities=entities,
                semantic_keywords=semantic_keywords,
                topic_clusters=topic_clusters,
                intent_classification=intent,
                readability_metrics=readability_metrics,
                language_quality_score=language_quality_score,
                semantic_density=semantic_density,
                coherence_score=coherence_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing natural language: {e}")
            return self._create_empty_analysis()
    
    async def optimize_for_natural_language(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> Tuple[str, Dict[str, Any]]:
        """Optimize content for natural language SEO.
        
        Args:
            content: Original content
            config: Optimization configuration
            
        Returns:
            Tuple of (optimized_content, optimization_metrics)
        """
        try:
            # Analyze current content
            analysis = await self.analyze_natural_language(content, config)
            
            # Apply natural language optimizations
            optimized_content = content
            optimization_metrics = {}
            
            # 1. Enhance semantic keywords
            optimized_content = await self._enhance_semantic_keywords(
                optimized_content, analysis.semantic_keywords, config
            )
            
            # 2. Improve entity mentions
            optimized_content = await self._enhance_entity_mentions(
                optimized_content, analysis.entities, config
            )
            
            # 3. Optimize for intent
            optimized_content = await self._optimize_for_intent(
                optimized_content, analysis.intent_classification, config
            )
            
            # 4. Improve coherence
            optimized_content = await self._improve_coherence(
                optimized_content, config
            )
            
            # 5. Enhance topic clustering
            optimized_content = await self._enhance_topic_structure(
                optimized_content, analysis.topic_clusters, config
            )
            
            # Calculate optimization metrics
            final_analysis = await self.analyze_natural_language(optimized_content, config)
            optimization_metrics = {
                "semantic_density_improvement": final_analysis.semantic_density - analysis.semantic_density,
                "coherence_improvement": final_analysis.coherence_score - analysis.coherence_score,
                "language_quality_improvement": final_analysis.language_quality_score - analysis.language_quality_score,
                "entities_added": len(final_analysis.entities) - len(analysis.entities),
                "semantic_keywords_added": len(final_analysis.semantic_keywords) - len(analysis.semantic_keywords)
            }
            
            return optimized_content, optimization_metrics
            
        except Exception as e:
            logger.error(f"Error optimizing for natural language: {e}")
            return content, {}
    
    async def _extract_semantic_keywords(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> List[str]:
        """Extract semantically related keywords."""
        try:
            semantic_keywords = set()
            
            # Use WordNet for semantic expansion
            for keyword in config.target_keywords:
                synsets = wordnet.synsets(keyword.replace(" ", "_"))
                for synset in synsets[:3]:  # Limit to top 3 synsets
                    for lemma in synset.lemmas():
                        semantic_keyword = lemma.name().replace("_", " ")
                        if len(semantic_keyword) > 2 and semantic_keyword != keyword:
                            semantic_keywords.add(semantic_keyword)
            
            # Extract keywords using TF-IDF
            try:
                sentences = sent_tokenize(content)
                if len(sentences) > 1:
                    vectorizer = TfidfVectorizer(
                        max_features=20,
                        stop_words='english',
                        ngram_range=(1, 2)
                    )
                    tfidf_matrix = vectorizer.fit_transform(sentences)
                    feature_names = vectorizer.get_feature_names_out()
                    
                    # Get top TF-IDF keywords
                    scores = tfidf_matrix.sum(axis=0).A1
                    keyword_scores = list(zip(feature_names, scores))
                    keyword_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    for keyword, score in keyword_scores[:10]:
                        semantic_keywords.add(keyword)
            except:
                pass
            
            return list(semantic_keywords)[:20]  # Limit to top 20
            
        except Exception as e:
            logger.error(f"Error extracting semantic keywords: {e}")
            return []
    
    async def _cluster_topics(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> List[List[str]]:
        """Cluster content into topic groups."""
        try:
            sentences = sent_tokenize(content)
            if len(sentences) < 2:
                return []
            
            # Simple topic clustering based on keyword co-occurrence
            topic_clusters = []
            
            # Group sentences by keyword mentions
            keyword_sentences = {keyword: [] for keyword in config.target_keywords}
            
            for i, sentence in enumerate(sentences):
                sentence_lower = sentence.lower()
                for keyword in config.target_keywords:
                    if keyword.lower() in sentence_lower:
                        keyword_sentences[keyword].append(i)
            
            # Create clusters of related sentences
            for keyword, sentence_indices in keyword_sentences.items():
                if sentence_indices:
                    cluster_sentences = [sentences[i] for i in sentence_indices]
                    topic_clusters.append(cluster_sentences)
            
            return topic_clusters
            
        except Exception as e:
            logger.error(f"Error clustering topics: {e}")
            return []
    
    async def _classify_intent(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> str:
        """Classify content intent."""
        try:
            if self.semantic_models.get("intent"):
                intent_labels = ["informational", "transactional", "navigational", "commercial"]
                
                result = self.semantic_models["intent"](
                    content[:512],  # Limit for model
                    intent_labels
                )
                
                return result["labels"][0] if result else "informational"
            
            # Fallback keyword-based classification
            transactional_keywords = ["buy", "purchase", "order", "shop", "price", "cost"]
            navigational_keywords = ["about", "contact", "home", "menu", "navigate"]
            commercial_keywords = ["review", "compare", "best", "top", "vs", "versus"]
            
            content_lower = content.lower()
            
            transactional_score = sum(1 for keyword in transactional_keywords if keyword in content_lower)
            navigational_score = sum(1 for keyword in navigational_keywords if keyword in content_lower)
            commercial_score = sum(1 for keyword in commercial_keywords if keyword in content_lower)
            
            if transactional_score >= max(navigational_score, commercial_score):
                return "transactional"
            elif navigational_score >= commercial_score:
                return "navigational"
            elif commercial_score > 0:
                return "commercial"
            else:
                return "informational"
                
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return "informational"
    
    def _calculate_readability_metrics(self, content: str, doc) -> Dict[str, float]:
        """Calculate readability metrics."""
        try:
            metrics = {}
            
            sentences = list(doc.sents)
            words = [token for token in doc if not token.is_punct and not token.is_space]
            
            # Average sentence length
            metrics["avg_sentence_length"] = len(words) / len(sentences) if sentences else 0
            
            # Lexical diversity (type-token ratio)
            unique_words = set(token.lemma_.lower() for token in words if token.is_alpha)
            metrics["lexical_diversity"] = len(unique_words) / len(words) if words else 0
            
            # Complex word ratio (words with 3+ syllables)
            complex_words = 0
            for token in words:
                if token.is_alpha and self._count_syllables(token.text) >= 3:
                    complex_words += 1
            metrics["complex_word_ratio"] = complex_words / len(words) if words else 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating readability metrics: {e}")
            return {}
    
    def _calculate_language_quality(self, doc) -> float:
        """Calculate language quality score."""
        try:
            total_tokens = len([token for token in doc if not token.is_punct and not token.is_space])
            if total_tokens == 0:
                return 0.0
            
            # Grammar quality (based on POS tags)
            proper_grammar_score = 0
            for sent in doc.sents:
                sent_tokens = [token for token in sent if not token.is_punct and not token.is_space]
                if sent_tokens:
                    # Check for proper sentence structure (subject-verb)
                    has_noun = any(token.pos_ in ["NOUN", "PRON"] for token in sent_tokens)
                    has_verb = any(token.pos_ == "VERB" for token in sent_tokens)
                    if has_noun and has_verb:
                        proper_grammar_score += 1
            
            grammar_ratio = proper_grammar_score / len(list(doc.sents)) if list(doc.sents) else 0
            
            # Spelling quality (simplified - based on known words)
            known_words = 0
            for token in doc:
                if token.is_alpha and not token.is_oov:
                    known_words += 1
            
            spelling_ratio = known_words / total_tokens if total_tokens else 0
            
            # Combine scores
            quality_score = (grammar_ratio * 0.6 + spelling_ratio * 0.4)
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating language quality: {e}")
            return 0.5
    
    def _calculate_semantic_density(self, content: str, target_keywords: List[str]) -> float:
        """Calculate semantic density of target keywords."""
        try:
            content_lower = content.lower()
            total_words = len(content.split())
            
            if total_words == 0:
                return 0.0
            
            semantic_mentions = 0
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                semantic_mentions += content_lower.count(keyword_lower)
                
                # Add semantic variations
                synsets = wordnet.synsets(keyword.replace(" ", "_"))
                for synset in synsets[:2]:
                    for lemma in synset.lemmas():
                        variation = lemma.name().replace("_", " ").lower()
                        if variation != keyword_lower:
                            semantic_mentions += content_lower.count(variation)
            
            return min(semantic_mentions / total_words, 0.1)  # Cap at 10%
            
        except Exception as e:
            logger.error(f"Error calculating semantic density: {e}")
            return 0.0
    
    def _calculate_coherence_score(self, doc) -> float:
        """Calculate text coherence score."""
        try:
            sentences = list(doc.sents)
            if len(sentences) < 2:
                return 1.0
            
            # Simple coherence based on entity and keyword continuity
            coherence_score = 0
            
            for i in range(1, len(sentences)):
                prev_entities = set(ent.text.lower() for ent in sentences[i-1].ents)
                curr_entities = set(ent.text.lower() for ent in sentences[i].ents)
                
                # Calculate entity overlap
                if prev_entities and curr_entities:
                    overlap = len(prev_entities.intersection(curr_entities))
                    coherence_score += overlap / max(len(prev_entities), len(curr_entities))
            
            return coherence_score / (len(sentences) - 1) if len(sentences) > 1 else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating coherence score: {e}")
            return 0.5
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting."""
        try:
            word = word.lower()
            vowels = "aeiouy"
            count = 0
            prev_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    count += 1
                prev_was_vowel = is_vowel
            
            # Handle special cases
            if word.endswith('e'):
                count -= 1
            if count == 0:
                count = 1
                
            return count
            
        except:
            return 1
    
    async def _enhance_semantic_keywords(
        self,
        content: str,
        semantic_keywords: List[str],
        config: SemanticOptimizationConfig
    ) -> str:
        """Enhance content with semantic keywords."""
        try:
            enhanced_content = content
            
            # Add semantic keywords naturally
            sentences = sent_tokenize(enhanced_content)
            
            for keyword in semantic_keywords[:5]:  # Limit to top 5
                if keyword.lower() not in enhanced_content.lower():
                    # Find best insertion point
                    insertion_point = len(sentences) // 3  # Insert in first third
                    keyword_sentence = f"This also relates to {keyword}."
                    sentences.insert(insertion_point, keyword_sentence)
            
            return " ".join(sentences)
            
        except Exception as e:
            logger.error(f"Error enhancing semantic keywords: {e}")
            return content
    
    async def _enhance_entity_mentions(
        self,
        content: str,
        entities: List[Tuple[str, str]],
        config: SemanticOptimizationConfig
    ) -> str:
        """Enhance entity mentions for better SEO."""
        try:
            enhanced_content = content
            
            # Ensure important entities are mentioned multiple times
            for entity, label in entities[:3]:  # Top 3 entities
                if label in ["PERSON", "ORG", "PRODUCT"]:
                    mentions = enhanced_content.lower().count(entity.lower())
                    if mentions == 1:  # Only mentioned once
                        # Add another mention
                        sentences = sent_tokenize(enhanced_content)
                        if len(sentences) > 1:
                            insertion_point = len(sentences) // 2
                            entity_sentence = f"As mentioned, {entity} plays an important role."
                            sentences.insert(insertion_point, entity_sentence)
                            enhanced_content = " ".join(sentences)
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Error enhancing entity mentions: {e}")
            return content
    
    async def _optimize_for_intent(
        self,
        content: str,
        intent: str,
        config: SemanticOptimizationConfig
    ) -> str:
        """Optimize content based on search intent."""
        try:
            optimized_content = content
            
            # Add intent-specific phrases
            intent_phrases = {
                "transactional": ["buy now", "get started", "purchase", "order"],
                "informational": ["learn more", "understand", "discover", "find out"],
                "navigational": ["visit", "go to", "navigate", "access"],
                "commercial": ["compare", "review", "best option", "top choice"]
            }
            
            phrases = intent_phrases.get(intent, [])
            if phrases and not any(phrase in optimized_content.lower() for phrase in phrases):
                # Add appropriate phrase
                sentences = sent_tokenize(optimized_content)
                if sentences:
                    last_sentence = sentences[-1]
                    intent_addition = f" {phrases[0].capitalize()} to learn more."
                    sentences[-1] = last_sentence + intent_addition
                    optimized_content = " ".join(sentences)
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing for intent: {e}")
            return content
    
    async def _improve_coherence(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> str:
        """Improve content coherence."""
        try:
            sentences = sent_tokenize(content)
            if len(sentences) < 2:
                return content
            
            # Add transition words for better flow
            transition_words = [
                "furthermore", "additionally", "moreover", "however", 
                "therefore", "consequently", "meanwhile", "similarly"
            ]
            
            improved_sentences = [sentences[0]]  # Keep first sentence as is
            
            for i in range(1, len(sentences)):
                # Add transition word occasionally
                if i % 3 == 0 and len(improved_sentences) > 1:
                    transition = np.random.choice(transition_words)
                    improved_sentences.append(f"{transition.capitalize()}, {sentences[i][0].lower() + sentences[i][1:]}")
                else:
                    improved_sentences.append(sentences[i])
            
            return " ".join(improved_sentences)
            
        except Exception as e:
            logger.error(f"Error improving coherence: {e}")
            return content
    
    async def _enhance_topic_structure(
        self,
        content: str,
        topic_clusters: List[List[str]],
        config: SemanticOptimizationConfig
    ) -> str:
        """Enhance topic structure for better organization."""
        try:
            if not topic_clusters:
                return content
            
            # Group related sentences together
            structured_content = []
            used_sentences = set()
            
            # Process each topic cluster
            for cluster in topic_clusters:
                if cluster:
                    structured_content.extend(cluster)
                    used_sentences.update(cluster)
            
            # Add any remaining sentences
            all_sentences = sent_tokenize(content)
            for sentence in all_sentences:
                if sentence not in used_sentences:
                    structured_content.append(sentence)
            
            return " ".join(structured_content)
            
        except Exception as e:
            logger.error(f"Error enhancing topic structure: {e}")
            return content
    
    def _create_empty_analysis(self) -> NLPAnalysisResult:
        """Create empty analysis result for error cases."""
        return NLPAnalysisResult(
            entities=[],
            semantic_keywords=[],
            topic_clusters=[],
            intent_classification="informational",
            readability_metrics={},
            language_quality_score=0.5,
            semantic_density=0.0,
            coherence_score=0.5
        )

    async def get_semantic_suggestions(
        self,
        content: str,
        config: SemanticOptimizationConfig
    ) -> Dict[str, List[str]]:
        """Get semantic optimization suggestions."""
        try:
            analysis = await self.analyze_natural_language(content, config)
            
            suggestions = {
                "semantic_keywords": analysis.semantic_keywords[:10],
                "entities_to_expand": [entity[0] for entity in analysis.entities[:5]],
                "topic_improvements": [],
                "coherence_improvements": [],
                "intent_optimization": []
            }
            
            # Topic improvement suggestions
            if len(analysis.topic_clusters) < 2:
                suggestions["topic_improvements"].append("Consider organizing content into distinct topic sections")
            
            # Coherence improvement suggestions
            if analysis.coherence_score < 0.5:
                suggestions["coherence_improvements"].append("Add transition words between sentences")
                suggestions["coherence_improvements"].append("Ensure better connection between paragraphs")
            
            # Intent optimization suggestions
            intent_suggestions = {
                "informational": ["Add more explanatory content", "Include educational examples"],
                "transactional": ["Add clear call-to-action", "Include pricing information"],
                "navigational": ["Add clear navigation elements", "Include site structure"],
                "commercial": ["Add comparison elements", "Include review information"]
            }
            
            suggestions["intent_optimization"] = intent_suggestions.get(
                analysis.intent_classification, 
                ["Optimize for current intent classification"]
            )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting semantic suggestions: {e}")
            return {}