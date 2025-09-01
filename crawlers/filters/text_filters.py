"""IA Influencer Agent - Text Content Filters
==========================================

Ultra-advanced professional text content filtering for multimedia processing.
Implements enterprise-grade text analysis with AI-powered validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import hashlib
from pathlib import Path

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.stem import PorterStemmer
    import langdetect
    HAS_NLP_LIBS = True
except ImportError:
    HAS_NLP_LIBS = False
    logging.warning("NLP libraries not available. Install nltk, langdetect.")

from .config import TextFilterConfig
from .filter_engine import FilterResponse, FilterResult, FilterType, ContentItem


class TextQualityAnalyzer:
    """Text quality analysis and readability scoring."""
    
    def __init__(self):
        """
Initialize text quality analyzer."""
        self.logger = logging.getLogger(__name__)
        self.stemmer = PorterStemmer() if HAS_NLP_LIBS else None
    
    def analyze_text_quality(self, text: str) -> Dict[str, float]:
        """
Analyze comprehensive text quality metrics."""
        try:
            quality_metrics = {}
            
            # Basic statistics
            quality_metrics.update(self._calculate_basic_stats(text))
            
            # Readability scores
            quality_metrics.update(self._calculate_readability(text))
            
            # Language quality
            quality_metrics.update(self._analyze_language_quality(text))
            
            # Content structure
            quality_metrics.update(self._analyze_structure(text))
            
            # Overall quality score
            overall_score = self._calculate_quality_score(quality_metrics)
            quality_metrics['overall_score'] = float(overall_score)
            
            return quality_metrics
            
        except Exception as e:
            self.logger.warning(f"Text quality analysis failed: {str(e)}")
            return {'error': str(e), 'overall_score': 0.5}
    
    def _calculate_basic_stats(self, text: str) -> Dict[str, float]:
        """Calculate basic text statistics."""
        try:
            # Clean text for analysis
            clean_text = re.sub(r'\s+', ' ', text.strip())
            
            # Character and word counts
            char_count = len(clean_text)
            word_count = len(clean_text.split())
            
            # Sentence count
            sentences = re.split(r'[.!?]+', clean_text)
            sentence_count = len([s for s in sentences if s.strip()])
            
            # Paragraph count
            paragraphs = text.split('\n\n')
            paragraph_count = len([p for p in paragraphs if p.strip()])
            
            # Average metrics
            avg_words_per_sentence = word_count / max(1, sentence_count)
            avg_chars_per_word = char_count / max(1, word_count)
            avg_sentences_per_paragraph = sentence_count / max(1, paragraph_count)
            
            return {
                'character_count': float(char_count),
                'word_count': float(word_count),
                'sentence_count': float(sentence_count),
                'paragraph_count': float(paragraph_count),
                'avg_words_per_sentence': float(avg_words_per_sentence),
                'avg_chars_per_word': float(avg_chars_per_word),
                'avg_sentences_per_paragraph': float(avg_sentences_per_paragraph)
            }
            
        except Exception as e:
            self.logger.warning(f"Basic stats calculation failed: {str(e)}")
            return {}
    
    def _calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability scores."""
        try:
            # Clean text
            clean_text = re.sub(r'[^\w\s.!?]', '', text)
            
            # Count sentences and words
            sentences = re.split(r'[.!?]+', clean_text)
            sentence_count = len([s for s in sentences if s.strip()])
            
            words = clean_text.split()
            word_count = len(words)
            
            # Count syllables (simplified)
            syllable_count = 0
            for word in words:
                syllable_count += self._count_syllables(word.lower())
            
            if sentence_count == 0 or word_count == 0:
                return {'flesch_reading_ease': 50.0, 'flesch_kincaid_grade': 8.0}
            
            # Flesch Reading Ease
            avg_sentence_length = word_count / sentence_count
            avg_syllables_per_word = syllable_count / word_count
            
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            flesch_score = max(0.0, min(100.0, flesch_score))
            
            # Flesch-Kincaid Grade Level
            fk_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
            fk_grade = max(0.0, min(20.0, fk_grade))
            
            return {
                'flesch_reading_ease': float(flesch_score),
                'flesch_kincaid_grade': float(fk_grade),
                'avg_sentence_length': float(avg_sentence_length),
                'avg_syllables_per_word': float(avg_syllables_per_word)
            }
            
        except Exception as e:
            self.logger.warning(f"Readability calculation failed: {str(e)}")
            return {'flesch_reading_ease': 50.0, 'flesch_kincaid_grade': 8.0}
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)."""
        try:
            word = word.lower()
            vowels = 'aeiouy'
            syllable_count = 0
            previous_was_vowel = False
            
            for i, char in enumerate(word):
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = is_vowel
            
            # Handle silent 'e'
            if word.endswith('e') and syllable_count > 1:
                syllable_count -= 1
            
            return max(1, syllable_count)
            
        except Exception:
            return 1
    
    def _analyze_language_quality(self, text: str) -> Dict[str, float]:
        """
Analyze language quality metrics."""
        try:
            # Vocabulary diversity (Type-Token Ratio)
            words = re.findall(r'\b\w+\b', text.lower())
            unique_words = set(words)
            
            vocabulary_diversity = len(unique_words) / max(1, len(words))
            
            # Word length variety
            word_lengths = [len(word) for word in words]
            avg_word_length = sum(word_lengths) / max(1, len(word_lengths))
            word_length_variance = sum((l - avg_word_length) ** 2 for l in word_lengths) / max(1, len(word_lengths))
            
            # Spelling and grammar approximation
            # Count potential spelling errors (words with unusual character patterns)
            potential_errors = 0
            for word in words:
                if len(word) > 2:
                    # Simple heuristics for potential errors
                    if re.search(r'(.)\1{2,}', word):  # Repeated characters
                        potential_errors += 1
                    if re.search(r'[0-9]', word) and not word.isdigit():  # Mixed numbers
                        potential_errors += 1
            
            error_rate = potential_errors / max(1, len(words))
            
            return {
                'vocabulary_diversity': float(vocabulary_diversity),
                'avg_word_length': float(avg_word_length),
                'word_length_variance': float(word_length_variance),
                'potential_error_rate': float(error_rate),
                'language_quality_score': float((vocabulary_diversity + (1.0 - error_rate)) / 2)
            }
            
        except Exception as e:
            self.logger.warning(f"Language quality analysis failed: {str(e)}")
            return {'language_quality_score': 0.5}
    
    def _analyze_structure(self, text: str) -> Dict[str, float]:
        """Analyze text structure and organization."""
        try:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            # Paragraph consistency
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            if paragraph_lengths:
                avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths)
                paragraph_variance = sum((l - avg_paragraph_length) ** 2 for l in paragraph_lengths) / len(paragraph_lengths)
                paragraph_consistency = 1.0 / (1.0 + paragraph_variance / max(1, avg_paragraph_length))
            else:
                paragraph_consistency = 0.5
            
            # Transition words and phrases
            transition_words = {
                'however', 'therefore', 'furthermore', 'moreover', 'additionally',
                'consequently', 'meanwhile', 'nevertheless', 'nonetheless', 'subsequently',
                'first', 'second', 'third', 'finally', 'in conclusion', 'for example',
                'for instance', 'in other words', 'on the other hand', 'as a result'
            }
            
            text_lower = text.lower()
            transition_count = sum(1 for word in transition_words if word in text_lower)
            transition_density = transition_count / max(1, len(paragraphs))
            
            # Sentence variety (length distribution)
            sentences = re.split(r'[.!?]+', text)
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            
            if sentence_lengths:
                sentence_variety = len(set(sentence_lengths)) / len(sentence_lengths)
            else:
                sentence_variety = 0.5
            
            structure_score = (paragraph_consistency + min(1.0, transition_density) + sentence_variety) / 3
            
            return {
                'paragraph_consistency': float(paragraph_consistency),
                'transition_density': float(transition_density),
                'sentence_variety': float(sentence_variety),
                'structure_score': float(structure_score)
            }
            
        except Exception as e:
            self.logger.warning(f"Structure analysis failed: {str(e)}")
            return {'structure_score': 0.5}
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from individual metrics."""
        try:
            scores = []
            weights = []
            
            # Readability score
            flesch_score = metrics.get('flesch_reading_ease', 50.0)
            readability_score = flesch_score / 100.0  # Normalize to 0-1
            scores.append(readability_score)
            weights.append(0.3)
            
            # Language quality
            lang_score = metrics.get('language_quality_score', 0.5)
            scores.append(lang_score)
            weights.append(0.3)
            
            # Structure score
            struct_score = metrics.get('structure_score', 0.5)
            scores.append(struct_score)
            weights.append(0.2)
            
            # Vocabulary diversity
            vocab_score = min(1.0, metrics.get('vocabulary_diversity', 0.5) * 2)
            scores.append(vocab_score)
            weights.append(0.2)
            
            # Calculate weighted average
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            
            return weighted_sum / total_weight
            
        except Exception as e:
            self.logger.warning(f"Quality score calculation failed: {str(e)}")
            return 0.5


class TextSentimentAnalyzer:
    """Text sentiment analysis and emotional content detection."""
    
    def __init__(self):
        """
Initialize sentiment analyzer."""
        self.logger = logging.getLogger(__name__)
        self.sentiment_analyzer = None
        
        if HAS_NLP_LIBS:
            try:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                self.logger.warning(f"Failed to initialize sentiment analyzer: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze text sentiment and emotional content."""
        try:
            if not self.sentiment_analyzer:
                return self._fallback_sentiment_analysis(text)
            
            # NLTK VADER sentiment analysis
            scores = self.sentiment_analyzer.polarity_scores(text)
            
            # Additional emotional analysis
            emotional_metrics = self._analyze_emotional_content(text)
            
            # Combine results
            result = {
                'positive_score': float(scores['pos']),
                'negative_score': float(scores['neg']),
                'neutral_score': float(scores['neu']),
                'compound_score': float(scores['compound']),
                'overall_sentiment': self._classify_sentiment(scores['compound']),
                'confidence': float(abs(scores['compound']))
            }
            
            result.update(emotional_metrics)
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {str(e)}")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, float]:
        """Fallback sentiment analysis without NLTK."""
        try:
            text_lower = text.lower()
            
            # Simple positive/negative word lists
            positive_words = {
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'awesome', 'brilliant', 'outstanding', 'perfect', 'love', 'like',
                'happy', 'joy', 'pleased', 'satisfied', 'beautiful', 'nice'
            }
            
            negative_words = {
                'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
                'dislike', 'angry', 'sad', 'frustrated', 'disappointed', 'ugly',
                'wrong', 'fail', 'failure', 'worst', 'boring', 'annoying'
            }
            
            words = re.findall(r'\b\w+\b', text_lower)
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            total_words = len(words)
            
            if total_words == 0:
                return {
                    'positive_score': 0.0,
                    'negative_score': 0.0,
                    'neutral_score': 1.0,
                    'compound_score': 0.0,
                    'overall_sentiment': 'neutral',
                    'confidence': 0.0
                }
            
            pos_score = positive_count / total_words
            neg_score = negative_count / total_words
            neu_score = 1.0 - pos_score - neg_score
            
            compound = pos_score - neg_score
            sentiment = self._classify_sentiment(compound)
            
            return {
                'positive_score': float(pos_score),
                'negative_score': float(neg_score),
                'neutral_score': float(max(0.0, neu_score)),
                'compound_score': float(compound),
                'overall_sentiment': sentiment,
                'confidence': float(abs(compound))
            }
            
        except Exception as e:
            self.logger.warning(f"Fallback sentiment analysis failed: {str(e)}")
            return {
                'overall_sentiment': 'neutral',
                'compound_score': 0.0,
                'confidence': 0.0
            }
    
    def _classify_sentiment(self, compound_score: float) -> str:
        """Classify sentiment based on compound score."""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_emotional_content(self, text: str) -> Dict[str, float]:
        """
Analyze emotional content beyond basic sentiment."""
        try:
            text_lower = text.lower()
            
            # Emotion keyword dictionaries
            emotions = {
                'anger': {'angry', 'furious', 'rage', 'mad', 'irritated', 'annoyed'},
                'fear': {'afraid', 'scared', 'terrified', 'worried', 'anxious', 'nervous'},
                'joy': {'happy', 'joyful', 'cheerful', 'delighted', 'excited', 'thrilled'},
                'sadness': {'sad', 'depressed', 'miserable', 'unhappy', 'gloomy', 'melancholy'},
                'surprise': {'surprised', 'amazed', 'astonished', 'shocked', 'stunned'},
                'disgust': {'disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated'}
            }
            
            words = re.findall(r'\b\w+\b', text_lower)
            total_words = max(1, len(words))
            
            emotion_scores = {}
            for emotion, keywords in emotions.items():
                count = sum(1 for word in words if word in keywords)
                emotion_scores[f'{emotion}_score'] = float(count / total_words)
            
            # Dominant emotion
            if emotion_scores:
                dominant_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
                emotion_scores['dominant_emotion'] = dominant_emotion.replace('_score', '')
                emotion_scores['emotion_intensity'] = emotion_scores[dominant_emotion]
            else:
                emotion_scores['dominant_emotion'] = 'neutral'
                emotion_scores['emotion_intensity'] = 0.0
            
            return emotion_scores
            
        except Exception as e:
            self.logger.warning(f"Emotional analysis failed: {str(e)}")
            return {'dominant_emotion': 'neutral', 'emotion_intensity': 0.0}


class TextToxicityDetector:
    """Text toxicity and harmful content detection."""
    
    def __init__(self):
        """
Initialize toxicity detector."""
        self.logger = logging.getLogger(__name__)
    
    def detect_toxicity(self, text: str) -> Dict[str, Any]:
        """
Detect toxic and harmful content in text."""
        try:
            toxicity_metrics = {}
            
            # Profanity detection
            toxicity_metrics.update(self._detect_profanity(text))
            
            # Hate speech detection
            toxicity_metrics.update(self._detect_hate_speech(text))
            
            # Spam detection
            toxicity_metrics.update(self._detect_spam_patterns(text))
            
            # Overall toxicity score
            overall_toxicity = self._calculate_toxicity_score(toxicity_metrics)
            toxicity_metrics['overall_toxicity'] = float(overall_toxicity)
            toxicity_metrics['is_toxic'] = overall_toxicity > 0.5
            
            return toxicity_metrics
            
        except Exception as e:
            self.logger.warning(f"Toxicity detection failed: {str(e)}")
            return {'error': str(e), 'overall_toxicity': 0.0, 'is_toxic': False}
    
    def _detect_profanity(self, text: str) -> Dict[str, float]:
        """Detect profanity in text."""
        try:
            # Basic profanity list (simplified)
            profanity_words = {
                'damn', 'hell', 'crap', 'stupid', 'idiot', 'moron',
                # Add more as needed, but keep it professional
            }
            
            text_lower = text.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            profanity_count = sum(1 for word in words if word in profanity_words)
            profanity_ratio = profanity_count / max(1, len(words))
            
            return {
                'profanity_count': profanity_count,
                'profanity_ratio': float(profanity_ratio),
                'contains_profanity': profanity_count > 0
            }
            
        except Exception as e:
            self.logger.warning(f"Profanity detection failed: {str(e)}")
            return {'profanity_ratio': 0.0, 'contains_profanity': False}
    
    def _detect_hate_speech(self, text: str) -> Dict[str, float]:
        """Detect hate speech patterns."""
        try:
            text_lower = text.lower()
            
            # Hate speech indicators (simplified)
            hate_patterns = [
                r'\b(hate|kill|destroy|eliminate)\s+(all|every)\s+\w+',
                r'\b\w+\s+(are|is)\s+(stupid|worthless|evil|disgusting)',
                r'\b(go\s+back\s+to|get\s+out\s+of)',
                r'\b(should\s+die|deserve\s+to\s+die)',
            ]
            
            hate_matches = 0
            for pattern in hate_patterns:
                if re.search(pattern, text_lower):
                    hate_matches += 1
            
            hate_score = min(1.0, hate_matches / 2.0)  # Normalize
            
            return {
                'hate_speech_score': float(hate_score),
                'hate_patterns_found': hate_matches,
                'contains_hate_speech': hate_score > 0.3
            }
            
        except Exception as e:
            self.logger.warning(f"Hate speech detection failed: {str(e)}")
            return {'hate_speech_score': 0.0, 'contains_hate_speech': False}
    
    def _detect_spam_patterns(self, text: str) -> Dict[str, float]:
        """Detect spam-like patterns in text."""
        try:
            spam_indicators = 0
            
            # Excessive repetition
            words = text.split()
            if len(words) > 0:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                max_repetition = max(word_counts.values())
                if max_repetition > len(words) * 0.3:  # 30% repetition
                    spam_indicators += 1
            
            # Excessive capitalization
            if len(text) > 0:
                caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
                if caps_ratio > 0.5:
                    spam_indicators += 1
            
            # Excessive punctuation
            punct_ratio = sum(1 for c in text if c in '!?.,;:') / max(1, len(text))
            if punct_ratio > 0.2:
                spam_indicators += 1
            
            # URLs and promotional content
            if re.search(r'(https?://|www\.|\.com|\.org)', text.lower()):
                if re.search(r'(buy|sell|discount|offer|deal|free)', text.lower()):
                    spam_indicators += 1
            
            spam_score = min(1.0, spam_indicators / 3.0)
            
            return {
                'spam_score': float(spam_score),
                'spam_indicators': spam_indicators,
                'is_spam': spam_score > 0.6
            }
            
        except Exception as e:
            self.logger.warning(f"Spam detection failed: {str(e)}")
            return {'spam_score': 0.0, 'is_spam': False}
    
    def _calculate_toxicity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall toxicity score."""
        try:
            scores = []
            
            # Profanity weight
            profanity_score = metrics.get('profanity_ratio', 0.0)
            scores.append(profanity_score * 0.3)
            
            # Hate speech weight
            hate_score = metrics.get('hate_speech_score', 0.0)
            scores.append(hate_score * 0.5)
            
            # Spam weight
            spam_score = metrics.get('spam_score', 0.0)
            scores.append(spam_score * 0.2)
            
            return sum(scores)
            
        except Exception as e:
            self.logger.warning(f"Toxicity score calculation failed: {str(e)}")
            return 0.0


class TextContentFilter:
    """Enterprise-grade text content filter."""
    
    def __init__(self, config: TextFilterConfig):
        """
Initialize text content filter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.quality_analyzer = TextQualityAnalyzer()
        self.sentiment_analyzer = TextSentimentAnalyzer()
        self.toxicity_detector = TextToxicityDetector()
        
        self.logger.info("Text content filter initialized")
    
    async def filter_async(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Asynchronously filter text content."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.filter, content, ai_validation, strict_mode
        )
    
    def filter(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """
Filter text content with comprehensive analysis."""
        start_time = time.time()
        
        try:
            # Extract and validate text
            text_data, metadata = self._extract_text_content(content)
            
            if not text_data:
                return FilterResponse(
                    filter_type=FilterType.TEXT,
                    result=FilterResult.FAILED,
                    score=0.0,
                    confidence=1.0,
                    metadata={'error': 'Failed to extract text content'},
                    processing_time=time.time() - start_time,
                    errors=['Text extraction failed']
                )
            
            # Perform comprehensive text analysis
            analysis_results = self._analyze_text_content(
                text_data, ai_validation, strict_mode
            )
            
            # Calculate overall score and result
            overall_score = self._calculate_overall_score(analysis_results, strict_mode)
            result = self._determine_filter_result(overall_score, analysis_results, strict_mode)
            
            # Prepare response
            response = FilterResponse(
                filter_type=FilterType.TEXT,
                result=result,
                score=overall_score,
                confidence=analysis_results.get('confidence', 0.85),
                metadata={
                    'text_properties': metadata,
                    'quality_analysis': analysis_results.get('quality', {}),
                    'sentiment_analysis': analysis_results.get('sentiment', {}),
                    'toxicity_analysis': analysis_results.get('toxicity', {}),
                    'language_analysis': analysis_results.get('language', {}),
                    'ai_validation_enabled': ai_validation,
                    'strict_mode': strict_mode
                },
                processing_time=time.time() - start_time,
                warnings=analysis_results.get('warnings', []),
                errors=analysis_results.get('errors', [])
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Text filtering failed: {str(e)}")
            return FilterResponse(
                filter_type=FilterType.TEXT,
                result=FilterResult.FAILED,
                score=0.0,
                confidence=0.0,
                metadata={'error': str(e)},
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    def _extract_text_content(self, content: ContentItem) -> Tuple[str, Dict[str, Any]]:
        """Extract and validate text content."""
        try:
            metadata = {}
            text_data = ""
            
            if isinstance(content.content_data, str):
                text_data = content.content_data
            elif isinstance(content.content_data, bytes):
                try:
                    text_data = content.content_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text_data = content.content_data.decode('latin-1')
                    except UnicodeDecodeError:
                        self.logger.error("Failed to decode text content")
                        return "", {'error': 'Text decoding failed'}
            elif content.file_path:
                try:
                    with open(content.file_path, 'r', encoding='utf-8') as f:
                        text_data = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(content.file_path, 'r', encoding='latin-1') as f:
                            text_data = f.read()
                    except Exception as e:
                        self.logger.error(f"Failed to read text file: {str(e)}")
                        return "", {'error': f'File reading failed: {str(e)}'}
                except Exception as e:
                    self.logger.error(f"Failed to open text file: {str(e)}")
                    return "", {'error': f'File access failed: {str(e)}'}
            else:
                return "", {'error': 'No text content provided'}
            
            # Calculate basic metadata
            char_count = len(text_data)
            word_count = len(text_data.split())
            line_count = len(text_data.splitlines())
            
            metadata.update({
                'character_count': char_count,
                'word_count': word_count,
                'line_count': line_count,
                'encoding': 'utf-8'  # Assumed after successful decoding
            })
            
            # Validate against config constraints
            if char_count < self.config.min_length:
                metadata['validation_error'] = f"Text length {char_count} below minimum {self.config.min_length}"
                return "", metadata
            
            if char_count > self.config.max_length:
                metadata['validation_warning'] = f"Text length {char_count} exceeds maximum {self.config.max_length}"
                # Truncate if too long
                text_data = text_data[:self.config.max_length]
                metadata['truncated'] = True
            
            if word_count < self.config.min_words:
                metadata['validation_error'] = f"Word count {word_count} below minimum {self.config.min_words}"
                return "", metadata
            
            if word_count > self.config.max_words:
                metadata['validation_warning'] = f"Word count {word_count} exceeds maximum {self.config.max_words}"
                # Truncate by words if too many
                words = text_data.split()[:self.config.max_words]
                text_data = ' '.join(words)
                metadata['word_truncated'] = True
            
            return text_data, metadata
            
        except Exception as e:
            self.logger.error(f"Text extraction failed: {str(e)}")
            return "", {'error': str(e)}
    
    def _analyze_text_content(
        self,
        text: str,
        ai_validation: bool,
        strict_mode: bool
    ) -> Dict[str, Any]:
        """Perform comprehensive text content analysis."""
        analysis_results = {
            'warnings': [],
            'errors': [],
            'confidence': 0.85
        }
        
        try:
            # Quality analysis
            if self.config.enable_quality_scoring:
                analysis_results['quality'] = self.quality_analyzer.analyze_text_quality(text)
            
            # Language detection
            if self.config.enable_language_detection:
                analysis_results['language'] = self._detect_language(text)
            
            # Sentiment analysis
            if self.config.enable_sentiment_analysis and ai_validation:
                analysis_results['sentiment'] = self.sentiment_analyzer.analyze_sentiment(text)
            
            # Toxicity detection
            if self.config.enable_toxicity_detection:
                analysis_results['toxicity'] = self.toxicity_detector.detect_toxicity(text)
            
            # Spam detection
            if self.config.enable_spam_detection:
                spam_metrics = self.toxicity_detector._detect_spam_patterns(text)
                analysis_results['spam'] = spam_metrics
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {str(e)}")
            analysis_results['errors'].append(str(e))
            analysis_results['confidence'] = 0.0
            return analysis_results
    
    def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the text."""
        try:
            if HAS_NLP_LIBS:
                try:
                    import langdetect
                    detected_lang = langdetect.detect(text)
                    confidence = 0.8  # langdetect doesn't provide confidence directly
                    
                    return {
                        'detected_language': detected_lang,
                        'confidence': confidence,
                        'is_supported': detected_lang in self.config.supported_languages
                    }
                except Exception as e:
                    self.logger.warning(f"Language detection failed: {str(e)}")
            
            # Fallback: simple heuristic based on character patterns
            text_sample = text[:1000].lower()
            
            # Check for common language patterns
            if re.search(r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b', text_sample):
                detected_lang = 'en'
            elif re.search(r'\b(le|la|les|de|du|des|et|ou|mais|dans|sur|pour|avec)\b', text_sample):
                detected_lang = 'fr'
            elif re.search(r'\b(der|die|das|und|oder|aber|in|auf|für|mit|von)\b', text_sample):
                detected_lang = 'de'
            elif re.search(r'\b(el|la|los|las|de|del|y|o|pero|en|sobre|para|con)\b', text_sample):
                detected_lang = 'es'
            else:
                detected_lang = 'unknown'
            
            return {
                'detected_language': detected_lang,
                'confidence': 0.5,  # Lower confidence for heuristic
                'is_supported': detected_lang in self.config.supported_languages,
                'method': 'heuristic'
            }
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {str(e)}")
            return {
                'detected_language': 'unknown',
                'confidence': 0.0,
                'is_supported': False,
                'error': str(e)
            }
    
    def _calculate_overall_score(self, analysis_results: Dict[str, Any], strict_mode: bool) -> float:
        """Calculate overall text filter score."""
        scores = []
        weights = []
        
        # Quality score
        quality_score = analysis_results.get('quality', {}).get('overall_score')
        if quality_score is not None:
            scores.append(quality_score)
            weights.append(0.3)
        
        # Sentiment score (neutral to positive preferred)
        sentiment_data = analysis_results.get('sentiment', {})
        if 'compound_score' in sentiment_data:
            # Convert sentiment to 0-1 scale (negative sentiment reduces score)
            sentiment_score = max(0.0, (sentiment_data['compound_score'] + 1.0) / 2.0)
            scores.append(sentiment_score)
            weights.append(0.2)
        
        # Toxicity penalty (inverted - lower toxicity = higher score)
        toxicity_data = analysis_results.get('toxicity', {})
        if 'overall_toxicity' in toxicity_data:
            toxicity_penalty = toxicity_data['overall_toxicity']
            toxicity_score = 1.0 - toxicity_penalty
            scores.append(toxicity_score)
            weights.append(0.3 if strict_mode else 0.2)
        
        # Language support bonus
        language_data = analysis_results.get('language', {})
        if language_data.get('is_supported'):
            language_score = language_data.get('confidence', 0.5)
            scores.append(language_score)
            weights.append(0.1)
        
        # Spam penalty
        spam_data = analysis_results.get('spam', {})
        if 'spam_score' in spam_data:
            spam_penalty = spam_data['spam_score']
            spam_score = 1.0 - spam_penalty
            scores.append(spam_score)
            weights.append(0.1)
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return 0.5  # Default neutral score
    
    def _determine_filter_result(
        self,
        overall_score: float,
        analysis_results: Dict[str, Any],
        strict_mode: bool
    ) -> FilterResult:
        """
Determine filter result based on analysis."""
        # Check for blocking conditions
        toxicity_data = analysis_results.get('toxicity', {})
        if toxicity_data.get('is_toxic') and toxicity_data.get('overall_toxicity', 0) > 0.7:
            return FilterResult.BLOCKED
        
        # Check for spam
        spam_data = analysis_results.get('spam', {})
        if spam_data.get('is_spam') and spam_data.get('spam_score', 0) > 0.8:
            return FilterResult.BLOCKED
        
        # Language support check
        language_data = analysis_results.get('language', {})
        if not language_data.get('is_supported') and strict_mode:
            return FilterResult.WARNING
        
        # Quality thresholds
        quality_data = analysis_results.get('quality', {})
        quality_score = quality_data.get('overall_score', 1.0)
        
        if quality_score < 0.3:  # Very poor quality
            return FilterResult.WARNING if not strict_mode else FilterResult.FAILED
        
        # Overall score thresholds
        if strict_mode:
            if overall_score >= 0.8:
                return FilterResult.PASSED
            elif overall_score >= 0.6:
                return FilterResult.WARNING
            else:
                return FilterResult.FAILED
        else:
            if overall_score >= 0.6:
                return FilterResult.PASSED
            elif overall_score >= 0.4:
                return FilterResult.WARNING
            else:
                return FilterResult.FAILED
    
    async def health_check(self) -> Dict[str, Any]:
        """
Perform health check on text filter."""
        health_status = {
            'status': 'healthy',
            'libraries': {
                'nltk': HAS_NLP_LIBS,
                'langdetect': HAS_NLP_LIBS
            },
            'config': {
                'sentiment_analysis': self.config.enable_sentiment_analysis,
                'toxicity_detection': self.config.enable_toxicity_detection,
                'language_detection': self.config.enable_language_detection,
                'quality_scoring': self.config.enable_quality_scoring,
                'supported_languages': len(self.config.supported_languages)
            }
        }
        
        if not HAS_NLP_LIBS:
            health_status['status'] = 'warning'
            health_status['message'] = 'NLP libraries not available'
        
        return health_status
