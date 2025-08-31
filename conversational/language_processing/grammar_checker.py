"""Enterprise Grammar Checker and Writing Assistant Module
======================================================

Professional-grade grammar and writing assistance for content creators:
- Real-time grammar and spelling correction with AI models
- Advanced style and tone analysis for audience targeting
- Context-aware writing improvement suggestions
- Multi-language grammar rules and cultural writing standards
- Professional writing standards compliance
- Content authenticity and plagiarism detection
- Writing performance analytics and improvement tracking
- Automated proofreading with quality scoring

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: Fahed Mlaiel - All Rights Reserved

⚠️  STRICT LEGAL WARNING: 
    This proprietary code is protected by international copyright law.
    Unauthorized use, copying, distribution, modification, or reverse engineering 
    is STRICTLY PROHIBITED and will result in immediate legal action.
    This includes any attempt to steal, replicate, or use this concept without 
    explicit written authorization from Fahed Mlaiel.
    
    Contact: mlaiel@live.de for licensing inquiries ONLY.
    Violators will be prosecuted to the full extent of German and EU law.
"""import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone

import spacy
import language_tool_python
from spellchecker import SpellChecker
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline
import torch

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode

logger = get_logger(__name__)


class ErrorType(Enum):
    """Types of writing errors"""    SPELLING = "spelling"
    GRAMMAR = "grammar"
    PUNCTUATION = "punctuation"
    STYLE = "style"
    WORD_CHOICE = "word_choice"
    SENTENCE_STRUCTURE = "sentence_structure"
    REDUNDANCY = "redundancy"
    CLARITY = "clarity"


class ErrorSeverity(Enum):
    """Error severity levels"""    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


@dataclass
class WritingError:
    """Represents a writing error or suggestion"""    error_type: ErrorType
    severity: ErrorSeverity
    position: Tuple[int, int]  # (start, end)
    original_text: str
    suggested_correction: str
    explanation: str
    rule_id: Optional[str] = None
    confidence: float = 1.0


@dataclass
class WritingAnalysis:
    """Complete writing analysis result"""    original_text: str
    corrected_text: str
    errors: List[WritingError]
    style_score: float
    clarity_score: float
    readability_score: float
    tone_analysis: Dict[str, float]
    vocabulary_level: str
    writing_quality: str
    improvement_suggestions: List[str]
    word_count: int
    sentence_count: int
    avg_sentence_length: float


class GrammarChecker:
    """Advanced grammar and style checker"""    
    def __init__(self):
        self.language_tool = None
        self.spell_checker = SpellChecker()
        self.nlp = None
        self._initialize_tools()
        
    def _initialize_tools(self):
        """Initialize grammar checking tools"""        try:
            # Initialize LanguageTool
            self.language_tool = language_tool_python.LanguageTool('en-US')
            
            # Initialize spaCy
            self.nlp = spacy.load("en_core_web_sm")
            
            # Initialize style checker
            self.style_checker = pipeline(
                "text-classification",
                model="unitary/toxic-bert"
            )
            
            logger.info("Grammar checker tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize grammar tools: {e}")
            
    async def check_grammar(self, text: str, language: str = "en") -> WritingAnalysis:
        """        Perform comprehensive grammar and writing analysis
        
        Args:
            text: Text to check
            language: Language code
            
        Returns:
            WritingAnalysis with detailed results
        """        try:
            # Clean text
            cleaned_text = clean_text(text)
            
            # Grammar checking
            grammar_errors = await self._check_grammar_errors(cleaned_text)
            
            # Spelling checking
            spelling_errors = await self._check_spelling_errors(cleaned_text)
            
            # Style analysis
            style_errors = await self._analyze_style(cleaned_text)
            
            # Combine all errors
            all_errors = grammar_errors + spelling_errors + style_errors
            
            # Generate corrected text
            corrected_text = await self._apply_corrections(cleaned_text, all_errors)
            
            # Calculate scores
            style_score = await self._calculate_style_score(cleaned_text, style_errors)
            clarity_score = await self._calculate_clarity_score(cleaned_text)
            readability_score = await self._calculate_readability_score(cleaned_text)
            
            # Tone analysis
            tone_analysis = await self._analyze_tone(cleaned_text)
            
            # Vocabulary analysis
            vocabulary_level = await self._analyze_vocabulary_level(cleaned_text)
            
            # Overall quality assessment
            writing_quality = await self._assess_writing_quality(style_score, clarity_score, readability_score)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                cleaned_text, all_errors, style_score, clarity_score
            )
            
            # Text statistics
            word_count = len(cleaned_text.split())
            sentences = sent_tokenize(cleaned_text)
            sentence_count = len(sentences)
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            return WritingAnalysis(
                original_text=text,
                corrected_text=corrected_text,
                errors=all_errors,
                style_score=style_score,
                clarity_score=clarity_score,
                readability_score=readability_score,
                tone_analysis=tone_analysis,
                vocabulary_level=vocabulary_level,
                writing_quality=writing_quality,
                improvement_suggestions=improvement_suggestions,
                word_count=word_count,
                sentence_count=sentence_count,
                avg_sentence_length=avg_sentence_length
            )
            
        except Exception as e:
            logger.error(f"Grammar checking failed: {e}")
            raise
            
    async def _check_grammar_errors(self, text: str) -> List[WritingError]:
        """Check for grammar errors using LanguageTool"""        try:
            if not self.language_tool:
                return []
                
            matches = self.language_tool.check(text)
            errors = []
            
            for match in matches:
                error = WritingError(
                    error_type=self._categorize_error(match.ruleId),
                    severity=self._determine_severity(match.ruleId),
                    position=(match.offset, match.offset + match.errorLength),
                    original_text=text[match.offset:match.offset + match.errorLength],
                    suggested_correction=match.replacements[0] if match.replacements else "",
                    explanation=match.message,
                    rule_id=match.ruleId,
                    confidence=0.9
                )
                errors.append(error)
                
            return errors
            
        except Exception as e:
            logger.error(f"Grammar error checking failed: {e}")
            return []
            
    def _categorize_error(self, rule_id: str) -> ErrorType:
        """Categorize error based on rule ID"""        if not rule_id:
            return ErrorType.GRAMMAR
            
        rule_id_lower = rule_id.lower()
        
        if any(keyword in rule_id_lower for keyword in ['spell', 'typo']):
            return ErrorType.SPELLING
        elif any(keyword in rule_id_lower for keyword in ['punct', 'comma', 'period']):
            return ErrorType.PUNCTUATION
        elif any(keyword in rule_id_lower for keyword in ['style', 'wordy', 'redundant']):
            return ErrorType.STYLE
        elif any(keyword in rule_id_lower for keyword in ['word', 'choice', 'confusion']):
            return ErrorType.WORD_CHOICE
        elif any(keyword in rule_id_lower for keyword in ['sentence', 'fragment', 'run']):
            return ErrorType.SENTENCE_STRUCTURE
        else:
            return ErrorType.GRAMMAR
            
    def _determine_severity(self, rule_id: str) -> ErrorSeverity:
        """Determine error severity"""        if not rule_id:
            return ErrorSeverity.MINOR
            
        critical_patterns = ['FRAGMENT', 'RUN_ON', 'SUBJECT_VERB']
        major_patterns = ['COMMA', 'APOSTROPHE', 'SPELLING']
        
        rule_id_upper = rule_id.upper()
        
        if any(pattern in rule_id_upper for pattern in critical_patterns):
            return ErrorSeverity.CRITICAL
        elif any(pattern in rule_id_upper for pattern in major_patterns):
            return ErrorSeverity.MAJOR
        else:
            return ErrorSeverity.MINOR
            
    async def _check_spelling_errors(self, text: str) -> List[WritingError]:
        """Check for spelling errors"""        try:
            words = word_tokenize(text)
            errors = []
            current_pos = 0
            
            for word in words:
                # Find word position in text
                word_start = text.find(word, current_pos)
                if word_start == -1:
                    current_pos += len(word)
                    continue
                    
                word_end = word_start + len(word)
                current_pos = word_end
                
                # Check if word is misspelled
                if (word.isalpha() and 
                    word.lower() not in self.spell_checker and 
                    len(word) > 2):
                    
                    # Get suggestions
                    suggestions = list(self.spell_checker.candidates(word))
                    suggested_correction = suggestions[0] if suggestions else word
                    
                    error = WritingError(
                        error_type=ErrorType.SPELLING,
                        severity=ErrorSeverity.MAJOR,
                        position=(word_start, word_end),
                        original_text=word,
                        suggested_correction=suggested_correction,
                        explanation=f"Possible spelling error: '{word}'",
                        confidence=0.8
                    )
                    errors.append(error)
                    
            return errors
            
        except Exception as e:
            logger.error(f"Spelling error checking failed: {e}")
            return []
            
    async def _analyze_style(self, text: str) -> List[WritingError]:
        """Analyze writing style and suggest improvements"""        try:
            errors = []
            
            # Check for passive voice
            passive_errors = await self._check_passive_voice(text)
            errors.extend(passive_errors)
            
            # Check for redundancy
            redundancy_errors = await self._check_redundancy(text)
            errors.extend(redundancy_errors)
            
            # Check for clarity issues
            clarity_errors = await self._check_clarity_issues(text)
            errors.extend(clarity_errors)
            
            return errors
            
        except Exception as e:
            logger.error(f"Style analysis failed: {e}")
            return []
            
    async def _check_passive_voice(self, text: str) -> List[WritingError]:
        """Check for excessive passive voice usage"""        try:
            errors = []
            
            if not self.nlp:
                return errors
                
            doc = self.nlp(text)
            
            for sent in doc.sents:
                # Simple passive voice detection
                has_be_verb = any(token.lemma_ == "be" for token in sent)
                has_past_participle = any(token.tag_ == "VBN" for token in sent)
                
                if has_be_verb and has_past_participle:
                    error = WritingError(
                        error_type=ErrorType.STYLE,
                        severity=ErrorSeverity.SUGGESTION,
                        position=(sent.start_char, sent.end_char),
                        original_text=sent.text,
                        suggested_correction=f"Consider rewriting in active voice: {sent.text}",
                        explanation="Passive voice can make writing less direct and engaging",
                        confidence=0.6
                    )
                    errors.append(error)
                    
            return errors
            
        except Exception as e:
            logger.error(f"Passive voice checking failed: {e}")
            return []
            
    async def _check_redundancy(self, text: str) -> List[WritingError]:
        """Check for redundant phrases and words"""        try:
            errors = []
            
            # Common redundant phrases
            redundant_phrases = [
                "advance planning", "basic fundamentals", "close proximity",
                "end result", "final outcome", "free gift", "past history",
                "personal opinion", "true facts", "very unique"
            ]
            
            text_lower = text.lower()
            
            for phrase in redundant_phrases:
                if phrase in text_lower:
                    start_pos = text_lower.find(phrase)
                    end_pos = start_pos + len(phrase)
                    
                    # Suggest removal of redundant word
                    words = phrase.split()
                    suggested = words[1] if len(words) == 2 else phrase
                    
                    error = WritingError(
                        error_type=ErrorType.REDUNDANCY,
                        severity=ErrorSeverity.MINOR,
                        position=(start_pos, end_pos),
                        original_text=phrase,
                        suggested_correction=suggested,
                        explanation=f"'{phrase}' contains redundant words",
                        confidence=0.9
                    )
                    errors.append(error)
                    
            return errors
            
        except Exception as e:
            logger.error(f"Redundancy checking failed: {e}")
            return []
            
    async def _check_clarity_issues(self, text: str) -> List[WritingError]:
        """Check for clarity and readability issues"""        try:
            errors = []
            sentences = sent_tokenize(text)
            
            for i, sentence in enumerate(sentences):
                words = sentence.split()
                
                # Check for overly long sentences
                if len(words) > 30:
                    error = WritingError(
                        error_type=ErrorType.CLARITY,
                        severity=ErrorSeverity.MINOR,
                        position=(0, len(sentence)),  # Approximate position
                        original_text=sentence,
                        suggested_correction="Consider breaking this into shorter sentences",
                        explanation="Long sentences can be difficult to follow",
                        confidence=0.7
                    )
                    errors.append(error)
                    
                # Check for complex words that could be simplified
                complex_words = [word for word in words if len(word) > 12]
                if len(complex_words) > len(words) * 0.1:  # More than 10% complex words
                    error = WritingError(
                        error_type=ErrorType.CLARITY,
                        severity=ErrorSeverity.SUGGESTION,
                        position=(0, len(sentence)),
                        original_text=sentence,
                        suggested_correction="Consider using simpler vocabulary",
                        explanation="Complex words may reduce readability",
                        confidence=0.6
                    )
                    errors.append(error)
                    
            return errors
            
        except Exception as e:
            logger.error(f"Clarity checking failed: {e}")
            return []
            
    async def _apply_corrections(self, text: str, errors: List[WritingError]) -> str:
        """Apply corrections to text"""        try:
            corrected_text = text
            
            # Sort errors by position (reverse order to maintain positions)
            sorted_errors = sorted(errors, key=lambda x: x.position[0], reverse=True)
            
            for error in sorted_errors:
                if (error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.MAJOR] and
                    error.suggested_correction and
                    error.confidence > 0.8):
                    
                    start, end = error.position
                    corrected_text = (corrected_text[:start] + 
                                    error.suggested_correction + 
                                    corrected_text[end:])
                    
            return corrected_text
            
        except Exception as e:
            logger.error(f"Applying corrections failed: {e}")
            return text
            
    async def _calculate_style_score(self, text: str, style_errors: List[WritingError]) -> float:
        """Calculate style quality score"""        try:
            if not text:
                return 0.0
                
            # Base score
            score = 1.0
            
            # Deduct points for style errors
            for error in style_errors:
                if error.severity == ErrorSeverity.CRITICAL:
                    score -= 0.2
                elif error.severity == ErrorSeverity.MAJOR:
                    score -= 0.1
                elif error.severity == ErrorSeverity.MINOR:
                    score -= 0.05
                    
            return max(score, 0.0)
            
        except Exception as e:
            logger.error(f"Style score calculation failed: {e}")
            return 0.5
            
    async def _calculate_clarity_score(self, text: str) -> float:
        """Calculate clarity score"""        try:
            sentences = sent_tokenize(text)
            if not sentences:
                return 0.0
                
            clarity_factors = []
            
            # Average sentence length
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            length_score = 1.0 if avg_length <= 20 else max(0.3, 1.0 - (avg_length - 20) / 30)
            clarity_factors.append(length_score)
            
            # Sentence length variation
            lengths = [len(s.split()) for s in sentences]
            if len(lengths) > 1:
                variation = np.std(lengths) / max(np.mean(lengths), 1)
                variation_score = min(variation / 10, 1.0)
                clarity_factors.append(variation_score)
                
            return np.mean(clarity_factors) if clarity_factors else 0.5
            
        except Exception as e:
            logger.error(f"Clarity score calculation failed: {e}")
            return 0.5
            
    async def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score"""        try:
            import textstat
            flesch_score = textstat.flesch_reading_ease(text)
            return min(flesch_score / 100, 1.0)
        except Exception as e:
            logger.error(f"Readability calculation failed: {e}")
            return 0.5
            
    async def _analyze_tone(self, text: str) -> Dict[str, float]:
        """Analyze tone of the text"""        try:
            # Simple tone analysis based on word patterns
            tone_indicators = {
                'formal': ['therefore', 'furthermore', 'however', 'nevertheless'],
                'informal': ['gonna', 'wanna', 'yeah', 'cool', 'awesome'],
                'positive': ['great', 'excellent', 'amazing', 'wonderful'],
                'negative': ['bad', 'terrible', 'awful', 'disappointing'],
                'confident': ['will', 'definitely', 'certainly', 'absolutely'],
                'uncertain': ['maybe', 'perhaps', 'possibly', 'might']
            }
            
            text_lower = text.lower()
            tone_scores = {}
            
            for tone, indicators in tone_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text_lower)
                tone_scores[tone] = min(score / len(indicators), 1.0)
                
            return tone_scores
            
        except Exception as e:
            logger.error(f"Tone analysis failed: {e}")
            return {}
            
    async def _analyze_vocabulary_level(self, text: str) -> str:
        """Analyze vocabulary complexity level"""        try:
            words = [word.lower() for word in word_tokenize(text) if word.isalpha()]
            
            if not words:
                return "basic"
                
            # Simple vocabulary analysis based on word length
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            if avg_word_length < 4.5:
                return "basic"
            elif avg_word_length < 5.5:
                return "intermediate"
            elif avg_word_length < 6.5:
                return "advanced"
            else:
                return "expert"
                
        except Exception as e:
            logger.error(f"Vocabulary analysis failed: {e}")
            return "intermediate"
            
    async def _assess_writing_quality(
        self,
        style_score: float,
        clarity_score: float,
        readability_score: float
    ) -> str:
        """Assess overall writing quality"""        try:
            overall_score = (style_score + clarity_score + readability_score) / 3
            
            if overall_score >= 0.9:
                return "excellent"
            elif overall_score >= 0.7:
                return "good"
            elif overall_score >= 0.5:
                return "fair"
            elif overall_score >= 0.3:
                return "poor"
            else:
                return "needs_improvement"
                
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return "fair"
            
    async def _generate_improvement_suggestions(
        self,
        text: str,
        errors: List[WritingError],
        style_score: float,
        clarity_score: float
    ) -> List[str]:
        """Generate writing improvement suggestions"""        try:
            suggestions = []
            
            # Error-based suggestions
            error_types = [error.error_type for error in errors]
            
            if ErrorType.SPELLING in error_types:
                suggestions.append("Review spelling carefully - consider using a spell checker")
                
            if ErrorType.GRAMMAR in error_types:
                suggestions.append("Check grammar rules and sentence structure")
                
            if ErrorType.PUNCTUATION in error_types:
                suggestions.append("Pay attention to punctuation usage")
                
            # Score-based suggestions
            if style_score < 0.7:
                suggestions.append("Improve writing style by varying sentence structure and word choice")
                
            if clarity_score < 0.7:
                suggestions.append("Enhance clarity by using shorter sentences and simpler words")
                
            # Content-specific suggestions
            sentences = sent_tokenize(text)
            avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            
            if avg_length > 25:
                suggestions.append("Break down long sentences for better readability")
                
            # Engagement suggestions
            if '?' not in text:
                suggestions.append("Consider adding questions to engage readers")
                
            if not any(word in text.lower() for word in ['you', 'your']):
                suggestions.append("Use second person (you/your) to connect with readers")
                
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []


class WritingAssistant:
    """Advanced writing assistant with AI-powered suggestions"""    
    def __init__(self):
        self.grammar_checker = GrammarChecker()
        
    async def improve_writing(
        self,
        text: str,
        target_audience: str = "general",
        writing_goal: str = "inform"
    ) -> WritingAnalysis:
        """        Provide comprehensive writing improvement assistance
        
        Args:
            text: Text to improve
            target_audience: Target audience (general, professional, academic, etc.)
            writing_goal: Writing goal (inform, persuade, entertain, etc.)
            
        Returns:
            WritingAnalysis with improvements and suggestions
        """        try:
            # Basic grammar and style check
            analysis = await self.grammar_checker.check_grammar(text)
            
            # Add audience-specific suggestions
            audience_suggestions = await self._get_audience_specific_suggestions(
                text, target_audience
            )
            analysis.improvement_suggestions.extend(audience_suggestions)
            
            # Add goal-specific suggestions
            goal_suggestions = await self._get_goal_specific_suggestions(
                text, writing_goal
            )
            analysis.improvement_suggestions.extend(goal_suggestions)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Writing improvement failed: {e}")
            raise
            
    async def _get_audience_specific_suggestions(
        self,
        text: str,
        target_audience: str
    ) -> List[str]:
        """Get suggestions based on target audience"""        try:
            suggestions = []
            
            if target_audience == "professional":
                if any(word in text.lower() for word in ['gonna', 'wanna', 'yeah']):
                    suggestions.append("Use more formal language for professional audience")
                    
            elif target_audience == "academic":
                if not any(word in text.lower() for word in ['research', 'study', 'analysis']):
                    suggestions.append("Consider adding more academic terminology and references")
                    
            elif target_audience == "social_media":
                if len(text) > 280:
                    suggestions.append("Consider shorter content for social media platforms")
                if '?' not in text:
                    suggestions.append("Add questions to encourage social media engagement")
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Audience-specific suggestions failed: {e}")
            return []
            
    async def _get_goal_specific_suggestions(
        self,
        text: str,
        writing_goal: str
    ) -> List[str]:
        """Get suggestions based on writing goal"""        try:
            suggestions = []
            
            if writing_goal == "persuade":
                if not any(word in text.lower() for word in ['should', 'must', 'need to']):
                    suggestions.append("Add persuasive language to convince readers")
                    
            elif writing_goal == "entertain":
                if not any(word in text.lower() for word in ['funny', 'amazing', 'incredible']):
                    suggestions.append("Add more engaging and entertaining language")
                    
            elif writing_goal == "inform":
                if not any(word in text.lower() for word in ['fact', 'data', 'information']):
                    suggestions.append("Include more factual information and data")
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Goal-specific suggestions failed: {e}")
            return []
