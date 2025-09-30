"""
Semantic SEO Engine for Ainflue Platform
Advanced semantic understanding and optimization for content

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple, Set, Union
import re
from dataclasses import dataclass
from datetime import datetime
import json
from collections import defaultdict, Counter
import math


@dataclass
class SemanticEntity:
    """Semantic entity representation"""
    text: str
    entity_type: str
    confidence: float
    context: str
    related_entities: List[str] = None
    synonyms: List[str] = None


@dataclass
class SemanticTopic:
    """Semantic topic representation"""
    name: str
    keywords: List[str]
    weight: float
    intent: str
    related_topics: List[str] = None


@dataclass
class SemanticContent:
    """Semantic content analysis result"""
    content_id: str
    main_topics: List[SemanticTopic]
    entities: List[SemanticEntity]
    intent_classification: str
    semantic_keywords: List[str]
    content_quality_score: float
    readability_score: float
    semantic_density: float


class SemanticSEOEngine:
    """
    Advanced semantic SEO engine for content understanding and optimization
    Provides semantic analysis, entity extraction, and intent classification
    """
    
    def __init__(self):
        self.entity_types = [
            'PERSON', 'ORGANIZATION', 'LOCATION', 'EVENT', 
            'PRODUCT', 'TECHNOLOGY', 'SKILL', 'GENRE', 'INSTRUMENT'
        ]
        self.intent_types = [
            'informational', 'navigational', 'transactional', 
            'commercial', 'entertainment', 'educational'
        ]
        self.semantic_patterns = self._load_semantic_patterns()
        self.topic_models = self._initialize_topic_models()
        
    def _load_semantic_patterns(self) -> Dict[str, List[str]]:
        """Load semantic patterns for different content types"""
        return {
            'music': [
                r'(song|track|album|EP|single)',
                r'(genre|style|sound)',
                r'(instrumental|vocal|melody|harmony|rhythm)',
                r'(studio|live|acoustic|electric)',
                r'(collaboration|featuring|remix)'
            ],
            'photography': [
                r'(photo|image|picture|shot)',
                r'(portrait|landscape|macro|street)',
                r'(camera|lens|exposure|lighting)',
                r'(digital|film|black and white|color)',
                r'(composition|framing|focus)'
            ],
            'blog': [
                r'(article|post|guide|tutorial)',
                r'(opinion|review|analysis|comparison)',
                r'(how to|step by step|tips|tricks)',
                r'(beginner|advanced|intermediate)',
                r'(update|news|announcement)'
            ],
            'video': [
                r'(video|film|movie|clip)',
                r'(documentary|tutorial|vlog|review)',
                r'(HD|4K|resolution|quality)',
                r'(editing|effects|cinematography)',
                r'(streaming|download|premiere)'
            ]
        }
        
    def _initialize_topic_models(self) -> Dict[str, Dict]:
        """Initialize topic models for different content categories"""
        return {
            'music': {
                'genres': ['rock', 'pop', 'jazz', 'classical', 'electronic', 'hip-hop', 'country', 'blues'],
                'instruments': ['guitar', 'piano', 'drums', 'violin', 'saxophone', 'bass', 'keyboard'],
                'moods': ['upbeat', 'melancholic', 'energetic', 'relaxing', 'romantic', 'aggressive']
            },
            'photography': {
                'styles': ['portrait', 'landscape', 'street', 'macro', 'wedding', 'fashion', 'nature'],
                'techniques': ['bokeh', 'long exposure', 'HDR', 'panoramic', 'time-lapse'],
                'equipment': ['DSLR', 'mirrorless', 'lens', 'tripod', 'flash', 'filter']
            },
            'content': {
                'formats': ['tutorial', 'review', 'guide', 'news', 'interview', 'analysis'],
                'industries': ['technology', 'entertainment', 'business', 'health', 'education'],
                'audiences': ['beginners', 'professionals', 'students', 'enthusiasts']
            }
        }
        
    def extract_semantic_entities(self, text: str, content_type: str = None) -> List[SemanticEntity]:
        """Extract semantic entities from text"""
        entities = []
        
        # Basic named entity patterns
        entity_patterns = {
            'PERSON': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'ORGANIZATION': r'\b[A-Z][a-zA-Z]+ (?:Inc|Corp|LLC|Ltd|Studio|Records|Label)\b',
            'LOCATION': r'\b(?:in|at|from) ([A-Z][a-z]+(?:, [A-Z][a-z]+)*)\b',
            'EVENT': r'\b(?:concert|festival|tour|show|exhibition|premiere)\b',
            'TECHNOLOGY': r'\b(?:AI|ML|VR|AR|4K|HD|digital|analog)\b'
        }
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_text = match.group(1) if match.groups() else match.group(0)
                
                # Calculate confidence based on context
                context = text[max(0, match.start()-50):match.end()+50]
                confidence = self._calculate_entity_confidence(entity_text, entity_type, context)
                
                entities.append(SemanticEntity(
                    text=entity_text.strip(),
                    entity_type=entity_type,
                    confidence=confidence,
                    context=context.strip(),
                    related_entities=[],
                    synonyms=[]
                ))
                
        # Content-specific entity extraction
        if content_type and content_type in self.topic_models:
            entities.extend(self._extract_domain_entities(text, content_type))
            
        return self._deduplicate_entities(entities)
        
    def _extract_domain_entities(self, text: str, content_type: str) -> List[SemanticEntity]:
        """Extract domain-specific entities"""
        entities = []
        domain_data = self.topic_models.get(content_type, {})
        
        for category, items in domain_data.items():
            for item in items:
                if re.search(rf'\b{re.escape(item)}\b', text, re.IGNORECASE):
                    entities.append(SemanticEntity(
                        text=item,
                        entity_type=category.upper(),
                        confidence=0.8,
                        context='',
                        related_entities=[],
                        synonyms=[]
                    ))
                    
        return entities
        
    def _calculate_entity_confidence(self, entity_text: str, entity_type: str, context: str) -> float:
        """Calculate confidence score for entity extraction"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on context clues
        context_lower = context.lower()
        
        if entity_type == 'PERSON':
            if any(title in context_lower for title in ['artist', 'musician', 'singer', 'creator']):
                confidence += 0.3
        elif entity_type == 'ORGANIZATION':
            if any(word in context_lower for word in ['company', 'studio', 'label']):
                confidence += 0.2
        elif entity_type == 'LOCATION':
            if any(word in context_lower for word in ['city', 'country', 'venue']):
                confidence += 0.2
                
        # Penalize if in quotes (might be song/album title)
        if f'"{entity_text}"' in context or f"'{entity_text}'" in context:
            confidence -= 0.2
            
        return min(1.0, max(0.1, confidence))
        
    def _deduplicate_entities(self, entities: List[SemanticEntity]) -> List[SemanticEntity]:
        """Remove duplicate entities and merge similar ones"""
        seen = {}
        deduplicated = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.entity_type)
            if key not in seen:
                seen[key] = entity
                deduplicated.append(entity)
            else:
                # Merge confidence scores
                existing = seen[key]
                existing.confidence = max(existing.confidence, entity.confidence)
                
        return deduplicated
        
    def classify_content_intent(self, title: str, content: str, metadata: Dict = None) -> str:
        """Classify the intent of the content"""
        
        # Combine title and content for analysis
        full_text = f"{title} {content}".lower()
        
        intent_signals = {
            'informational': [
                'what is', 'how to', 'guide', 'tutorial', 'learn', 'understand',
                'explanation', 'definition', 'information', 'facts'
            ],
            'navigational': [
                'home', 'about', 'contact', 'portfolio', 'profile', 'biography',
                'official', 'main page', 'website'
            ],
            'transactional': [
                'buy', 'purchase', 'order', 'booking', 'hire', 'commission',
                'download', 'subscribe', 'premium', 'paid'
            ],
            'commercial': [
                'price', 'cost', 'compare', 'review', 'best', 'top rated',
                'recommend', 'vs', 'versus', 'alternative'
            ],
            'entertainment': [
                'music', 'video', 'photo', 'gallery', 'performance', 'show',
                'entertainment', 'fun', 'creative'
            ],
            'educational': [
                'course', 'lesson', 'training', 'workshop', 'masterclass',
                'skills', 'technique', 'method'
            ]
        }
        
        intent_scores = {}
        
        for intent, signals in intent_signals.items():
            score = sum(1 for signal in signals if signal in full_text)
            # Normalize by number of signals
            intent_scores[intent] = score / len(signals)
            
        # Additional context from metadata
        if metadata:
            content_type = metadata.get('content_type', '')
            if content_type == 'product':
                intent_scores['transactional'] += 0.3
            elif content_type == 'article':
                intent_scores['informational'] += 0.2
            elif content_type == 'portfolio':
                intent_scores['navigational'] += 0.3
                
        # Return intent with highest score
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'informational'  # Default
            
    def extract_semantic_keywords(self, content: str, target_keywords: List[str] = None) -> List[str]:
        """Extract semantically related keywords from content"""
        
        # Basic keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        word_freq = Counter(words)
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
            'did', 'man', 'men', 'say', 'she', 'too', 'use', 'way', 'been', 'have',
            'that', 'with', 'will', 'this', 'they', 'from', 'your', 'what', 'were'
        }
        
        filtered_words = {word: freq for word, freq in word_freq.items() 
                         if word not in stop_words and len(word) > 3}
        
        # Get top keywords by frequency
        semantic_keywords = [word for word, freq in 
                           sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:20]]
        
        # Add semantic variations if target keywords provided
        if target_keywords:
            semantic_keywords.extend(self._find_semantic_variations(target_keywords, content))
            
        return list(set(semantic_keywords))
        
    def _find_semantic_variations(self, target_keywords: List[str], content: str) -> List[str]:
        """Find semantic variations of target keywords in content"""
        variations = []
        
        # Simple semantic patterns - in real implementation, use word embeddings
        semantic_mappings = {
            'music': ['song', 'track', 'audio', 'melody', 'sound'],
            'photo': ['image', 'picture', 'photograph', 'shot', 'visual'],
            'video': ['film', 'movie', 'clip', 'recording', 'footage'],
            'artist': ['creator', 'musician', 'performer', 'talent'],
            'portfolio': ['gallery', 'collection', 'showcase', 'work'],
        }
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in semantic_mappings:
                for variation in semantic_mappings[keyword_lower]:
                    if variation in content.lower():
                        variations.append(variation)
                        
        return variations
        
    def analyze_topic_clusters(self, content: str, content_type: str = None) -> List[SemanticTopic]:
        """Analyze and extract topic clusters from content"""
        
        # Extract potential topics using keyword co-occurrence
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Create co-occurrence matrix (simplified)
        topics = []
        
        if content_type and content_type in self.topic_models:
            domain_topics = self.topic_models[content_type]
            
            for category, items in domain_topics.items():
                relevant_items = [item for item in items if item.lower() in content.lower()]
                
                if relevant_items:
                    # Calculate topic weight based on frequency and content length
                    weight = len(relevant_items) / len(items) * min(1.0, len(content) / 1000)
                    
                    topic = SemanticTopic(
                        name=category,
                        keywords=relevant_items,
                        weight=weight,
                        intent=self._infer_topic_intent(relevant_items, content),
                        related_topics=[]
                    )
                    topics.append(topic)
                    
        return sorted(topics, key=lambda x: x.weight, reverse=True)
        
    def _infer_topic_intent(self, keywords: List[str], content: str) -> str:
        """Infer the intent of a topic based on keywords and context"""
        
        content_lower = content.lower()
        
        # Check for instructional content
        if any(word in content_lower for word in ['how to', 'tutorial', 'guide', 'learn']):
            return 'educational'
            
        # Check for review/comparison content
        if any(word in content_lower for word in ['review', 'compare', 'vs', 'best']):
            return 'commercial'
            
        # Check for entertainment content
        if any(word in content_lower for word in ['music', 'video', 'photo', 'creative']):
            return 'entertainment'
            
        return 'informational'
        
    def calculate_semantic_density(self, content: str, target_keywords: List[str]) -> float:
        """Calculate semantic density of target keywords in content"""
        
        if not target_keywords or not content:
            return 0.0
            
        content_lower = content.lower()
        total_words = len(re.findall(r'\b\w+\b', content))
        
        # Count direct keyword occurrences
        keyword_count = 0
        for keyword in target_keywords:
            keyword_count += len(re.findall(rf'\b{re.escape(keyword.lower())}\b', content_lower))
            
        # Count semantic variations
        semantic_variations = self._find_semantic_variations(target_keywords, content)
        for variation in semantic_variations:
            keyword_count += len(re.findall(rf'\b{re.escape(variation.lower())}\b', content_lower))
            
        # Calculate density (target: 1-3% for optimal SEO)
        density = (keyword_count / total_words) * 100 if total_words > 0 else 0
        
        return round(density, 2)
        
    def analyze_content_quality(self, content: str, title: str = "") -> float:
        """Analyze content quality for SEO"""
        
        quality_score = 0.0
        max_score = 100.0
        
        # Content length (20 points)
        content_length = len(content)
        if content_length >= 1000:
            quality_score += 20
        elif content_length >= 500:
            quality_score += 15
        elif content_length >= 300:
            quality_score += 10
        else:
            quality_score += 5
            
        # Title presence and quality (15 points)
        if title:
            if 30 <= len(title) <= 60:
                quality_score += 15
            elif 20 <= len(title) <= 80:
                quality_score += 10
            else:
                quality_score += 5
                
        # Paragraph structure (15 points)
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            if 50 <= avg_paragraph_length <= 150:
                quality_score += 15
            elif 30 <= avg_paragraph_length <= 200:
                quality_score += 10
            else:
                quality_score += 5
                
        # Sentence variety (10 points)
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) >= 5:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                length_variance = max(sentence_lengths) - min(sentence_lengths)
                if length_variance >= 10:
                    quality_score += 10
                elif length_variance >= 5:
                    quality_score += 7
                else:
                    quality_score += 3
                    
        # Readability indicators (15 points)
        # Simple readability check based on average word and sentence length
        words = content.split()
        sentences_clean = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        if words and sentences_clean:
            avg_words_per_sentence = len(words) / len(sentences_clean)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Optimal ranges for readability
            if 10 <= avg_words_per_sentence <= 20 and 4 <= avg_word_length <= 6:
                quality_score += 15
            elif 8 <= avg_words_per_sentence <= 25 and 3 <= avg_word_length <= 7:
                quality_score += 10
            else:
                quality_score += 5
                
        # Content uniqueness indicators (10 points)
        unique_words = len(set(word.lower() for word in words))
        total_words = len(words)
        
        if total_words > 0:
            uniqueness_ratio = unique_words / total_words
            if uniqueness_ratio >= 0.6:
                quality_score += 10
            elif uniqueness_ratio >= 0.4:
                quality_score += 7
            else:
                quality_score += 3
                
        # Formatting and structure (15 points)
        has_headers = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
        has_lists = bool(re.search(r'^\s*[-*+]\s', content, re.MULTILINE))
        has_emphasis = bool(re.search(r'\*\*.*\*\*|\*.*\*', content))
        
        structure_score = 0
        if has_headers:
            structure_score += 5
        if has_lists:
            structure_score += 5
        if has_emphasis:
            structure_score += 5
            
        quality_score += structure_score
        
        return round(min(quality_score, max_score), 1)
        
    def analyze_semantic_content(self, content_id: str, title: str, content: str,
                                content_type: str = None, target_keywords: List[str] = None,
                                metadata: Dict = None) -> SemanticContent:
        """Comprehensive semantic content analysis"""
        
        # Extract entities
        entities = self.extract_semantic_entities(content, content_type)
        
        # Classify intent
        intent = self.classify_content_intent(title, content, metadata)
        
        # Extract semantic keywords
        semantic_keywords = self.extract_semantic_keywords(content, target_keywords)
        
        # Analyze topics
        topics = self.analyze_topic_clusters(content, content_type)
        
        # Calculate quality metrics
        quality_score = self.analyze_content_quality(content, title)
        
        # Calculate semantic density
        semantic_density = self.calculate_semantic_density(content, target_keywords or [])
        
        # Simple readability score (Flesch-like approximation)
        readability_score = self._calculate_readability_score(content)
        
        return SemanticContent(
            content_id=content_id,
            main_topics=topics,
            entities=entities,
            intent_classification=intent,
            semantic_keywords=semantic_keywords,
            content_quality_score=quality_score,
            readability_score=readability_score,
            semantic_density=semantic_density
        )
        
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate simplified readability score"""
        
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return 0.0
            
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (simplified: vowel groups)
        syllable_count = 0
        for word in words:
            vowels = re.findall(r'[aeiouAEIOU]', word)
            syllable_count += max(1, len(vowels))
            
        avg_syllables_per_word = syllable_count / len(words)
        
        # Simplified Flesch Reading Ease formula
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-100 scale
        return max(0, min(100, readability))
        
    def generate_semantic_recommendations(self, analysis: SemanticContent,
                                        target_keywords: List[str] = None) -> List[str]:
        """Generate SEO recommendations based on semantic analysis"""
        
        recommendations = []
        
        # Content quality recommendations
        if analysis.content_quality_score < 70:
            recommendations.append("Improve content quality by adding more detailed information and better structure")
            
        if analysis.readability_score < 50:
            recommendations.append("Improve readability by using shorter sentences and simpler words")
        elif analysis.readability_score > 90:
            recommendations.append("Content might be too simple - consider adding more detailed explanations")
            
        # Semantic density recommendations
        if analysis.semantic_density < 1:
            recommendations.append("Increase keyword density by naturally incorporating more relevant terms")
        elif analysis.semantic_density > 3:
            recommendations.append("Reduce keyword density to avoid over-optimization")
            
        # Entity recommendations
        if len(analysis.entities) < 3:
            recommendations.append("Add more relevant entities (people, places, organizations) to improve semantic richness")
            
        # Topic recommendations
        if len(analysis.main_topics) < 2:
            recommendations.append("Expand content to cover more related topics and improve topical authority")
            
        # Intent-specific recommendations
        if analysis.intent_classification == 'informational':
            recommendations.append("Consider adding 'how-to' sections or detailed explanations to improve informational value")
        elif analysis.intent_classification == 'commercial':
            recommendations.append("Include comparison elements or detailed reviews to enhance commercial intent")
            
        return recommendations


# Example usage and testing
if __name__ == "__main__":
    engine = SemanticSEOEngine()
    
    # Test content
    title = "How to Create Amazing Music with AI Tools"
    content = """
    Creating music with artificial intelligence has become increasingly popular among musicians and producers. 
    AI tools like GPT-based music generators and machine learning algorithms can help artists compose melodies, 
    harmonies, and even complete songs. In this comprehensive guide, we'll explore the best AI music creation 
    tools available today.
    
    First, let's discuss the basics of AI in music production. Artificial intelligence can analyze patterns 
    in existing music to generate new compositions. Tools like OpenAI's MuseNet and Google's Magenta project 
    have revolutionized how we think about computer-generated music.
    
    When choosing an AI music tool, consider factors like genre compatibility, ease of use, and integration 
    with your existing digital audio workstation (DAW). Popular options include AIVA, Amper Music, and Boomy.
    """
    
    # Analyze content
    analysis = engine.analyze_semantic_content(
        content_id="test_001",
        title=title,
        content=content,
        content_type="music",
        target_keywords=["AI music", "music creation", "artificial intelligence"]
    )
    
    print("Semantic Analysis Results:")
    print(f"Content Quality Score: {analysis.content_quality_score}/100")
    print(f"Readability Score: {analysis.readability_score}/100")
    print(f"Semantic Density: {analysis.semantic_density}%")
    print(f"Intent Classification: {analysis.intent_classification}")
    print(f"Main Topics: {[topic.name for topic in analysis.main_topics]}")
    print(f"Entities: {[entity.text for entity in analysis.entities]}")
    print(f"Semantic Keywords: {analysis.semantic_keywords[:10]}")
    
    # Generate recommendations
    recommendations = engine.generate_semantic_recommendations(analysis)
    print(f"\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")