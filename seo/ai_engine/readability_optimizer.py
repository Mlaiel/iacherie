"""Readability Optimizer
Advanced readability optimization for better SEO and user experience.

Features:
- Multiple readability metrics (Flesch, Gunning Fog, SMOG, etc.)
- Sentence structure optimization
- Vocabulary simplification
- Paragraph organization
- Reading level targeting

Author: Fahed Mlaiel (mlaiel@live.de)
ML Engineer + Content Optimization expertise applied
"""

import asyncio
import logging
import re
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json

try:
    import textstat
    from textstat import flesch_reading_ease, flesch_kincaid_grade, gunning_fog, smog_index
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords, wordnet
    from nltk.tag import pos_tag
    import spacy
    from collections import Counter
    import syllables
except ImportError as e:
    logging.warning(f"Optional dependencies not available: {e}")

logger = logging.getLogger(__name__)

@dataclass
class ReadabilityMetrics:
    """Comprehensive readability metrics."""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog_index: float
    smog_index: float
    automated_readability_index: float
    coleman_liau_index: float
    reading_level: str
    avg_sentence_length: float
    avg_syllables_per_word: float
    complex_word_ratio: float
    passive_voice_ratio: float
    vocabulary_diversity: float

@dataclass
class ReadabilityTarget:
    """Target readability configuration."""
    target_grade_level: float = 8.0
    max_sentence_length: int = 20
    max_syllables_per_word: float = 2.0
    min_vocabulary_diversity: float = 0.6
    max_complex_word_ratio: float = 0.1
    max_passive_voice_ratio: float = 0.1
    target_reading_ease: float = 60.0

@dataclass
class ReadabilityOptimizationResult:
    """Result of readability optimization."""
    original_metrics: ReadabilityMetrics
    optimized_content: str
    optimized_metrics: ReadabilityMetrics
    improvements: Dict[str, float]
    suggestions: List[str]
    problem_sentences: List[str]
    simplified_words: Dict[str, str]
    optimization_score: float

class ReadabilityOptimizer:
    """Advanced readability optimization engine."""
    
    def __init__(self) -> None:
        """Initialize the Readability Optimizer."""
        self.nlp_model = None
        self.word_replacements = self._load_word_replacements()
        self.complex_words = set()
        self._load_models()
        
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
        except:
            pass
    
    def _load_models(self) -> None:
        """Load NLP models for readability analysis."""
        try:
            # Load spaCy model
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found")
            
            # Load complex words list
            self._load_complex_words()
            
        except Exception as e:
            logger.error(f"Error loading readability models: {e}")
    
    def _load_word_replacements(self) -> Dict[str, str]:
        """Load word replacement dictionary for simplification."""
        return {
            # Complex -> Simple replacements
            "utilize": "use",
            "facilitate": "help",
            "demonstrate": "show",
            "implement": "do",
            "accomplish": "do",
            "consequently": "so",
            "furthermore": "also",
            "nevertheless": "but",
            "subsequently": "then",
            "previously": "before",
            "currently": "now",
            "approximately": "about",
            "additionally": "also",
            "specifically": "exactly",
            "particularly": "especially",
            "essentially": "basically",
            "frequently": "often",
            "immediately": "now",
            "obviously": "clearly",
            "definitely": "surely",
            "absolutely": "totally",
            "extremely": "very",
            "significantly": "much",
            "considerably": "much",
            "substantially": "much",
            "comprehensive": "complete",
            "methodology": "method",
            "optimization": "improvement",
            "enhancement": "improvement",
            "establishment": "setup",
            "documentation": "records",
            "specification": "details",
            "recommendation": "advice",
            "requirements": "needs",
            "alternatives": "options",
            "characteristics": "features",
            "fundamental": "basic",
            "preliminary": "early",
            "substantial": "large",
            "equivalent": "equal",
            "sufficient": "enough",
            "appropriate": "right",
            "individual": "person",
            "opportunity": "chance",
            "possibility": "chance",
            "probability": "chance",
            "capability": "ability",
            "responsibility": "duty",
            "difficulty": "problem",
            "necessity": "need",
            "importance": "value",
            "significance": "meaning",
            "efficiency": "speed",
            "effectiveness": "success",
            "performance": "results",
            "achievement": "success",
            "improvement": "better",
            "development": "growth",
            "maintenance": "upkeep",
            "operation": "work",
            "procedure": "steps",
            "technique": "method",
            "strategy": "plan",
            "approach": "way",
            "solution": "answer",
            "situation": "case",
            "condition": "state",
            "position": "place",
            "location": "place",
            "destination": "goal",
            "direction": "way",
            "information": "facts",
            "knowledge": "facts",
            "understanding": "knowledge",
            "experience": "practice",
            "education": "learning",
            "instruction": "teaching",
            "explanation": "reason",
            "description": "details",
            "definition": "meaning",
            "illustration": "example",
            "demonstration": "example",
            "examination": "check",
            "investigation": "study",
            "analysis": "study",
            "research": "study",
            "evaluation": "review",
            "assessment": "review",
            "consideration": "thought",
            "discussion": "talk",
            "conversation": "talk",
            "communication": "talk",
            "correspondence": "letters",
            "notification": "notice",
            "announcement": "news",
            "advertisement": "ad",
            "publication": "article",
            "distribution": "sharing",
            "transmission": "sending",
            "transportation": "moving",
            "accommodation": "housing",
            "reservation": "booking",
            "registration": "signup",
            "participation": "taking part",
            "collaboration": "teamwork",
            "cooperation": "teamwork",
            "assistance": "help",
            "contribution": "input",
            "presentation": "showing",
            "representation": "showing",
            "organization": "group",
            "administration": "management",
            "supervision": "oversight",
            "coordination": "planning",
            "preparation": "getting ready",
            "arrangement": "setup",
            "configuration": "setup",
            "installation": "setup",
            "construction": "building",
            "destruction": "breaking",
            "elimination": "removal",
            "reduction": "cutting",
            "increase": "growth",
            "expansion": "growth",
            "extension": "stretching",
            "modification": "change",
            "transformation": "change",
            "conversion": "change",
            "adjustment": "change",
            "revision": "change",
            "correction": "fix",
            "verification": "check",
            "confirmation": "proof",
            "validation": "check",
            "authorization": "permission",
            "permission": "OK",
            "acceptance": "OK",
            "approval": "OK",
            "agreement": "deal",
            "contract": "deal",
            "commitment": "promise",
            "obligation": "duty",
            "requirement": "need",
            "expectation": "hope",
            "assumption": "guess",
            "conclusion": "end",
            "decision": "choice",
            "selection": "choice",
            "preference": "choice",
            "recommendation": "advice",
            "suggestion": "idea",
            "proposal": "plan",
            "application": "use",
            "implementation": "use",
            "utilization": "use",
            "employment": "work",
            "occupation": "job",
            "profession": "job",
            "specialization": "focus",
            "concentration": "focus",
            "attention": "focus",
            "consideration": "thought",
            "reflection": "thought",
            "contemplation": "thought",
            "meditation": "thought",
            "observation": "watching",
            "examination": "looking",
            "inspection": "checking",
            "supervision": "watching",
            "monitoring": "watching"
        }
    
    def _load_complex_words(self) -> None:
        """Load list of complex words to identify."""
        # Complex words that typically have simpler alternatives
        complex_word_list = [
            "accommodate", "accordance", "achievement", "acknowledge", "acquisition",
            "administration", "advantageous", "alternative", "appropriate", "approximate",
            "assistance", "association", "automatically", "availability", "beneficial",
            "capability", "characteristic", "circumstance", "collaboration", "combination",
            "comfortable", "communicate", "competent", "competitive", "complicated",
            "comprehensive", "concentration", "conclusion", "condition", "confidence",
            "connection", "consequence", "consideration", "consistent", "constitute",
            "construction", "contribution", "conventional", "cooperation", "coordinate",
            "corresponding", "demonstrate", "description", "destination", "development",
            "difference", "difficulty", "discussion", "distribution", "effectively",
            "efficiency", "eliminate", "emergency", "employment", "environment",
            "equipment", "especially", "essential", "establish", "evaluation",
            "examination", "excellent", "exception", "exercise", "exhibition",
            "expansion", "experience", "experiment", "explanation", "expression",
            "extension", "extraordinary", "facilitate", "familiar", "flexibility",
            "frequently", "fundamental", "generation", "government", "gradually",
            "illustration", "immediately", "implementation", "importance", "improvement",
            "inclusion", "increase", "independence", "individual", "information",
            "installation", "instruction", "intelligence", "international", "introduction",
            "investigation", "knowledge", "leadership", "maintenance", "management",
            "manufacturer", "maximum", "measurement", "mechanism", "minimum",
            "modification", "necessary", "observation", "occupation", "operation",
            "opportunity", "organization", "orientation", "outstanding", "participation",
            "particular", "performance", "permanent", "permission", "personality",
            "perspective", "photography", "possibility", "potential", "preparation",
            "presentation", "preservation", "previously", "probability", "procedure",
            "production", "professional", "protection", "publication", "qualification",
            "reasonable", "recognition", "recommendation", "relationship", "representative",
            "requirement", "responsibility", "satisfaction", "significant", "specification",
            "subsequently", "substantial", "successfully", "sufficient", "suggestion",
            "temperature", "traditional", "transformation", "transportation", "understanding",
            "unfortunately", "university", "utilization", "vegetable", "verification"
        ]
        
        self.complex_words = set(complex_word_list)
    
    async def analyze_readability(
        self,
        content: str,
        language: str = "en"
    ) -> ReadabilityMetrics:
        """Analyze comprehensive readability metrics.
        
        Args:
            content: Text content to analyze
            language: Language code (default: en)
            
        Returns:
            ReadabilityMetrics with detailed analysis
        """
        try:
            if not content.strip():
                return self._create_empty_metrics()
            
            # Basic readability scores
            flesch_ease = textstat.flesch_reading_ease(content)
            flesch_grade = textstat.flesch_kincaid_grade(content)
            gunning_fog = textstat.gunning_fog(content)
            smog = textstat.smog_index(content)
            ari = textstat.automated_readability_index(content)
            coleman_liau = textstat.coleman_liau_index(content)
            
            # Determine reading level
            reading_level = self._determine_reading_level(flesch_grade)
            
            # Sentence analysis
            sentences = sent_tokenize(content)
            words = word_tokenize(content)
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            # Syllable analysis
            avg_syllables = self._calculate_avg_syllables(words)
            
            # Complex word analysis
            complex_word_ratio = self._calculate_complex_word_ratio(words)
            
            # Passive voice analysis
            passive_voice_ratio = await self._calculate_passive_voice_ratio(content)
            
            # Vocabulary diversity (Type-Token Ratio)
            vocabulary_diversity = self._calculate_vocabulary_diversity(words)
            
            return ReadabilityMetrics(
                flesch_reading_ease=flesch_ease,
                flesch_kincaid_grade=flesch_grade,
                gunning_fog_index=gunning_fog,
                smog_index=smog,
                automated_readability_index=ari,
                coleman_liau_index=coleman_liau,
                reading_level=reading_level,
                avg_sentence_length=avg_sentence_length,
                avg_syllables_per_word=avg_syllables,
                complex_word_ratio=complex_word_ratio,
                passive_voice_ratio=passive_voice_ratio,
                vocabulary_diversity=vocabulary_diversity
            )
            
        except Exception as e:
            logger.error(f"Error analyzing readability: {e}")
            return self._create_empty_metrics()
    
    async def optimize_readability(
        self,
        content: str,
        target: ReadabilityTarget
    ) -> ReadabilityOptimizationResult:
        """Optimize content for better readability.
        
        Args:
            content: Original content
            target: Readability targets
            
        Returns:
            ReadabilityOptimizationResult with optimized content and metrics
        """
        try:
            # Analyze original content
            original_metrics = await self.analyze_readability(content)
            
            # Apply optimizations
            optimized_content = content
            suggestions = []
            problem_sentences = []
            simplified_words = {}
            
            # 1. Simplify complex words
            optimized_content, word_replacements = self._simplify_complex_words(optimized_content)
            simplified_words.update(word_replacements)
            
            # 2. Break down long sentences
            optimized_content, long_sentences = self._break_long_sentences(
                optimized_content, target.max_sentence_length
            )
            problem_sentences.extend(long_sentences)
            
            # 3. Reduce passive voice
            optimized_content, passive_sentences = await self._reduce_passive_voice(optimized_content)
            problem_sentences.extend(passive_sentences)
            
            # 4. Improve paragraph structure
            optimized_content = self._improve_paragraph_structure(optimized_content)
            
            # 5. Add transition words
            optimized_content = self._add_transition_words(optimized_content)
            
            # 6. Simplify vocabulary
            optimized_content, vocab_improvements = self._simplify_vocabulary(optimized_content)
            simplified_words.update(vocab_improvements)
            
            # Analyze optimized content
            optimized_metrics = await self.analyze_readability(optimized_content)
            
            # Calculate improvements
            improvements = self._calculate_improvements(original_metrics, optimized_metrics)
            
            # Generate suggestions
            suggestions = self._generate_readability_suggestions(
                original_metrics, optimized_metrics, target
            )
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(
                original_metrics, optimized_metrics, target
            )
            
            return ReadabilityOptimizationResult(
                original_metrics=original_metrics,
                optimized_content=optimized_content,
                optimized_metrics=optimized_metrics,
                improvements=improvements,
                suggestions=suggestions,
                problem_sentences=problem_sentences,
                simplified_words=simplified_words,
                optimization_score=optimization_score
            )
            
        except Exception as e:
            logger.error(f"Error optimizing readability: {e}")
            return self._create_default_optimization_result(content)
    
    def _determine_reading_level(self, grade_level: float) -> str:
        """Determine reading level description from grade level."""
        if grade_level <= 6:
            return "Elementary School"
        elif grade_level <= 8:
            return "Middle School"
        elif grade_level <= 12:
            return "High School"
        elif grade_level <= 16:
            return "College"
        else:
            return "Graduate"
    
    def _calculate_avg_syllables(self, words: List[str]) -> float:
        """Calculate average syllables per word."""
        try:
            total_syllables = 0
            valid_words = 0
            
            for word in words:
                if word.isalpha():
                    try:
                        # Use syllables library if available
                        syllable_count = syllables.estimate(word)
                    except:
                        # Fallback syllable counting
                        syllable_count = self._count_syllables_fallback(word)
                    
                    total_syllables += syllable_count
                    valid_words += 1
            
            return total_syllables / valid_words if valid_words > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating average syllables: {e}")
            return 0
    
    def _count_syllables_fallback(self, word: str) -> int:
        """Fallback syllable counting method."""
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
                
            return max(count, 1)
            
        except:
            return 1
    
    def _calculate_complex_word_ratio(self, words: List[str]) -> float:
        """Calculate ratio of complex words."""
        try:
            total_words = 0
            complex_count = 0
            
            for word in words:
                if word.isalpha() and len(word) > 2:
                    total_words += 1
                    
                    # Check if word is in complex words list
                    if word.lower() in self.complex_words:
                        complex_count += 1
                    
                    # Check syllable count (3+ syllables = complex)
                    try:
                        syllable_count = syllables.estimate(word)
                    except:
                        syllable_count = self._count_syllables_fallback(word)
                    
                    if syllable_count >= 3:
                        complex_count += 1
            
            return complex_count / total_words if total_words > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating complex word ratio: {e}")
            return 0
    
    async def _calculate_passive_voice_ratio(self, content: str) -> float:
        """Calculate ratio of passive voice constructions."""
        try:
            if not self.nlp_model:
                return 0.0
            
            doc = self.nlp_model(content)
            total_sentences = 0
            passive_sentences = 0
            
            for sent in doc.sents:
                total_sentences += 1
                
                # Look for passive voice patterns
                tokens = list(sent)
                for i, token in enumerate(tokens):
                    # Look for "be" verb + past participle
                    if (token.lemma_ in ["be", "is", "are", "was", "were", "been", "being"] and
                        i + 1 < len(tokens) and tokens[i + 1].tag_ == "VBN"):
                        passive_sentences += 1
                        break
            
            return passive_sentences / total_sentences if total_sentences > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating passive voice ratio: {e}")
            return 0
    
    def _calculate_vocabulary_diversity(self, words: List[str]) -> float:
        """Calculate vocabulary diversity (Type-Token Ratio)."""
        try:
            # Filter to alphabetic words only
            alpha_words = [word.lower() for word in words if word.isalpha()]
            
            if not alpha_words:
                return 0
            
            unique_words = set(alpha_words)
            return len(unique_words) / len(alpha_words)
            
        except Exception as e:
            logger.error(f"Error calculating vocabulary diversity: {e}")
            return 0
    
    def _simplify_complex_words(self, content: str) -> Tuple[str, Dict[str, str]]:
        """Replace complex words with simpler alternatives."""
        try:
            simplified_content = content
            replacements_made = {}
            
            for complex_word, simple_word in self.word_replacements.items():
                # Case-insensitive replacement
                pattern = r'\b' + re.escape(complex_word) + r'\b'
                
                def replace_func(match) -> None:
                    original = match.group()
                    replacement = simple_word
                    
                    # Preserve capitalization
                    if original[0].isupper():
                        replacement = replacement.capitalize()
                    if original.isupper():
                        replacement = replacement.upper()
                    
                    replacements_made[original] = replacement
                    return replacement
                
                simplified_content = re.sub(pattern, replace_func, simplified_content, flags=re.IGNORECASE)
            
            return simplified_content, replacements_made
            
        except Exception as e:
            logger.error(f"Error simplifying complex words: {e}")
            return content, {}
    
    def _break_long_sentences(
        self,
        content: str,
        max_length: int
    ) -> Tuple[str, List[str]]:
        """Break down long sentences into shorter ones."""
        try:
            sentences = sent_tokenize(content)
            improved_sentences = []
            long_sentences = []
            
            for sentence in sentences:
                words = word_tokenize(sentence)
                
                if len(words) > max_length:
                    long_sentences.append(sentence)
                    
                    # Try to break at conjunctions
                    broken_sentences = self._break_at_conjunctions(sentence)
                    improved_sentences.extend(broken_sentences)
                else:
                    improved_sentences.append(sentence)
            
            return " ".join(improved_sentences), long_sentences
            
        except Exception as e:
            logger.error(f"Error breaking long sentences: {e}")
            return content, []
    
    def _break_at_conjunctions(self, sentence: str) -> List[str]:
        """Break sentence at conjunctions and connecting words."""
        try:
            # Common break points
            break_points = [
                ", and ", ", but ", ", or ", ", so ", ", yet ",
                ", which ", ", that ", ", because ", ", since ",
                ", although ", ", while ", ", whereas ", ", however "
            ]
            
            for break_point in break_points:
                if break_point in sentence:
                    parts = sentence.split(break_point, 1)
                    if len(parts) == 2:
                        first_part = parts[0].strip() + "."
                        second_part = parts[1].strip()
                        
                        # Capitalize first letter of second part
                        if second_part:
                            second_part = second_part[0].upper() + second_part[1:]
                            return [first_part, second_part]
            
            return [sentence]
            
        except Exception as e:
            logger.error(f"Error breaking sentence at conjunctions: {e}")
            return [sentence]
    
    async def _reduce_passive_voice(self, content: str) -> Tuple[str, List[str]]:
        """Convert passive voice to active voice where possible."""
        try:
            if not self.nlp_model:
                return content, []
            
            sentences = sent_tokenize(content)
            improved_sentences = []
            passive_sentences = []
            
            for sentence in sentences:
                doc = self.nlp_model(sentence)
                
                # Check for passive voice patterns
                is_passive = False
                for token in doc:
                    if (token.lemma_ in ["be", "is", "are", "was", "were", "been", "being"] and
                        token.head.tag_ == "VBN"):
                        is_passive = True
                        break
                
                if is_passive:
                    passive_sentences.append(sentence)
                    # Simple passive to active conversion
                    active_sentence = self._convert_passive_to_active(sentence)
                    improved_sentences.append(active_sentence)
                else:
                    improved_sentences.append(sentence)
            
            return " ".join(improved_sentences), passive_sentences
            
        except Exception as e:
            logger.error(f"Error reducing passive voice: {e}")
            return content, []
    
    def _convert_passive_to_active(self, sentence: str) -> str:
        """Simple passive to active voice conversion."""
        try:
            # Basic passive voice patterns to convert
            passive_patterns = [
                (r'\b(is|are|was|were)\s+(\w+ed)\b', r'\2'),
                (r'\b(is|are|was|were)\s+being\s+(\w+ed)\b', r'\2'),
                (r'\b(has|have|had)\s+been\s+(\w+ed)\b', r'\2')
            ]
            
            active_sentence = sentence
            
            for pattern, replacement in passive_patterns:
                active_sentence = re.sub(pattern, replacement, active_sentence)
            
            return active_sentence
            
        except Exception as e:
            logger.error(f"Error converting passive to active: {e}")
            return sentence
    
    def _improve_paragraph_structure(self, content: str) -> str:
        """Improve paragraph structure for better readability."""
        try:
            # Split into paragraphs
            paragraphs = content.split('\n\n')
            improved_paragraphs = []
            
            for paragraph in paragraphs:
                sentences = sent_tokenize(paragraph)
                
                # If paragraph is too long (>5 sentences), break it up
                if len(sentences) > 5:
                    # Split roughly in half
                    mid_point = len(sentences) // 2
                    first_half = " ".join(sentences[:mid_point])
                    second_half = " ".join(sentences[mid_point:])
                    improved_paragraphs.extend([first_half, second_half])
                else:
                    improved_paragraphs.append(paragraph)
            
            return '\n\n'.join(improved_paragraphs)
            
        except Exception as e:
            logger.error(f"Error improving paragraph structure: {e}")
            return content
    
    def _add_transition_words(self, content: str) -> str:
        """Add transition words for better flow."""
        try:
            sentences = sent_tokenize(content)
            if len(sentences) <= 1:
                return content
            
            transition_words = [
                "Furthermore", "Additionally", "Moreover", "However",
                "Therefore", "Consequently", "Meanwhile", "Similarly",
                "In contrast", "On the other hand", "As a result",
                "For example", "In addition", "Nevertheless"
            ]
            
            improved_sentences = [sentences[0]]  # Keep first sentence as is
            
            for i in range(1, len(sentences)):
                # Add transition word occasionally (every 3-4 sentences)
                if i % 3 == 0 and len(improved_sentences) > 1:
                    transition = transition_words[i % len(transition_words)]
                    sentence = sentences[i]
                    
                    # Add transition at the beginning
                    if sentence[0].islower():
                        sentence = sentence[0].upper() + sentence[1:]
                    
                    improved_sentence = f"{transition}, {sentence[0].lower() + sentence[1:]}"
                    improved_sentences.append(improved_sentence)
                else:
                    improved_sentences.append(sentences[i])
            
            return " ".join(improved_sentences)
            
        except Exception as e:
            logger.error(f"Error adding transition words: {e}")
            return content
    
    def _simplify_vocabulary(self, content: str) -> Tuple[str, Dict[str, str]]:
        """Further simplify vocabulary beyond word replacements."""
        try:
            simplified_content = content
            improvements = {}
            
            # Additional vocabulary simplifications
            additional_replacements = {
                # Technical terms
                "infrastructure": "system",
                "architecture": "structure",
                "implementation": "setup",
                "optimization": "improvement",
                "configuration": "settings",
                "specification": "details",
                "functionality": "features",
                "compatibility": "works with",
                "accessibility": "easy to use",
                "scalability": "can grow",
                "reliability": "dependable",
                "sustainability": "lasting",
                "transparency": "openness",
                "accountability": "responsibility",
                "collaboration": "teamwork",
                "synchronization": "matching",
                "customization": "personal setup",
                "authorization": "permission",
                "authentication": "login",
                "integration": "combining",
                "migration": "moving",
                "deployment": "setup",
                "maintenance": "upkeep",
                "troubleshooting": "fixing problems",
                "documentation": "instructions",
                "validation": "checking",
                "verification": "confirming"
            }
            
            for complex_term, simple_term in additional_replacements.items():
                if complex_term in simplified_content.lower():
                    pattern = r'\b' + re.escape(complex_term) + r'\b'
                    
                    def replace_func(match) -> None:
                        original = match.group()
                        replacement = simple_term
                        
                        # Preserve capitalization
                        if original[0].isupper():
                            replacement = replacement.capitalize()
                        
                        improvements[original] = replacement
                        return replacement
                    
                    simplified_content = re.sub(
                        pattern, replace_func, simplified_content, flags=re.IGNORECASE
                    )
            
            return simplified_content, improvements
            
        except Exception as e:
            logger.error(f"Error simplifying vocabulary: {e}")
            return content, {}
    
    def _calculate_improvements(
        self,
        original: ReadabilityMetrics,
        optimized: ReadabilityMetrics
    ) -> Dict[str, float]:
        """Calculate improvements in readability metrics."""
        try:
            improvements = {
                "flesch_reading_ease": optimized.flesch_reading_ease - original.flesch_reading_ease,
                "flesch_kincaid_grade": original.flesch_kincaid_grade - optimized.flesch_kincaid_grade,  # Lower is better
                "avg_sentence_length": original.avg_sentence_length - optimized.avg_sentence_length,  # Lower is better
                "complex_word_ratio": original.complex_word_ratio - optimized.complex_word_ratio,  # Lower is better
                "passive_voice_ratio": original.passive_voice_ratio - optimized.passive_voice_ratio,  # Lower is better
                "vocabulary_diversity": optimized.vocabulary_diversity - original.vocabulary_diversity
            }
            
            return improvements
            
        except Exception as e:
            logger.error(f"Error calculating improvements: {e}")
            return {}
    
    def _generate_readability_suggestions(
        self,
        original: ReadabilityMetrics,
        optimized: ReadabilityMetrics,
        target: ReadabilityTarget
    ) -> List[str]:
        """Generate readability improvement suggestions."""
        try:
            suggestions = []
            
            # Check if targets are met
            if optimized.flesch_kincaid_grade > target.target_grade_level:
                suggestions.append(f"Consider simplifying content further - current grade level: {optimized.flesch_kincaid_grade:.1f}, target: {target.target_grade_level}")
            
            if optimized.avg_sentence_length > target.max_sentence_length:
                suggestions.append(f"Break down long sentences - average length: {optimized.avg_sentence_length:.1f} words, target: {target.max_sentence_length}")
            
            if optimized.complex_word_ratio > target.max_complex_word_ratio:
                suggestions.append(f"Replace more complex words - current ratio: {optimized.complex_word_ratio:.2%}, target: {target.max_complex_word_ratio:.2%}")
            
            if optimized.passive_voice_ratio > target.max_passive_voice_ratio:
                suggestions.append(f"Convert more passive voice to active - current ratio: {optimized.passive_voice_ratio:.2%}, target: {target.max_passive_voice_ratio:.2%}")
            
            if optimized.vocabulary_diversity < target.min_vocabulary_diversity:
                suggestions.append(f"Increase vocabulary diversity - current: {optimized.vocabulary_diversity:.2%}, target: {target.min_vocabulary_diversity:.2%}")
            
            # Positive feedback for improvements
            if optimized.flesch_reading_ease > original.flesch_reading_ease:
                suggestions.append(f"✓ Improved reading ease from {original.flesch_reading_ease:.1f} to {optimized.flesch_reading_ease:.1f}")
            
            if optimized.flesch_kincaid_grade < original.flesch_kincaid_grade:
                suggestions.append(f"✓ Reduced grade level from {original.flesch_kincaid_grade:.1f} to {optimized.flesch_kincaid_grade:.1f}")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating readability suggestions: {e}")
            return []
    
    def _calculate_optimization_score(
        self,
        original: ReadabilityMetrics,
        optimized: ReadabilityMetrics,
        target: ReadabilityTarget
    ) -> float:
        """Calculate overall optimization score."""
        try:
            score_components = []
            
            # Flesch Reading Ease improvement (0-1)
            ease_improvement = (optimized.flesch_reading_ease - original.flesch_reading_ease) / 100
            score_components.append(max(0, min(ease_improvement, 1)))
            
            # Grade level improvement (0-1)
            grade_improvement = (original.flesch_kincaid_grade - optimized.flesch_kincaid_grade) / 10
            score_components.append(max(0, min(grade_improvement, 1)))
            
            # Sentence length improvement (0-1)
            sentence_improvement = (original.avg_sentence_length - optimized.avg_sentence_length) / 20
            score_components.append(max(0, min(sentence_improvement, 1)))
            
            # Complex word reduction (0-1)
            complex_improvement = (original.complex_word_ratio - optimized.complex_word_ratio) / 0.5
            score_components.append(max(0, min(complex_improvement, 1)))
            
            # Passive voice reduction (0-1)
            passive_improvement = (original.passive_voice_ratio - optimized.passive_voice_ratio) / 0.5
            score_components.append(max(0, min(passive_improvement, 1)))
            
            # Calculate weighted average
            weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Emphasize reading ease and grade level
            weighted_score = sum(score * weight for score, weight in zip(score_components, weights))
            
            return min(weighted_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return 0.0
    
    def _create_empty_metrics(self) -> ReadabilityMetrics:
        """Create empty metrics for error cases."""
        return ReadabilityMetrics(
            flesch_reading_ease=0.0,
            flesch_kincaid_grade=0.0,
            gunning_fog_index=0.0,
            smog_index=0.0,
            automated_readability_index=0.0,
            coleman_liau_index=0.0,
            reading_level="Unknown",
            avg_sentence_length=0.0,
            avg_syllables_per_word=0.0,
            complex_word_ratio=0.0,
            passive_voice_ratio=0.0,
            vocabulary_diversity=0.0
        )
    
    def _create_default_optimization_result(self, content: str) -> ReadabilityOptimizationResult:
        """Create default optimization result for error cases."""
        empty_metrics = self._create_empty_metrics()
        
        return ReadabilityOptimizationResult(
            original_metrics=empty_metrics,
            optimized_content=content,
            optimized_metrics=empty_metrics,
            improvements={},
            suggestions=[],
            problem_sentences=[],
            simplified_words={},
            optimization_score=0.0
        )

    async def batch_optimize_readability(
        self,
        contents: List[str],
        targets: List[ReadabilityTarget]
    ) -> List[ReadabilityOptimizationResult]:
        """Optimize readability for multiple contents in batch."""
        try:
            tasks = [
                self.optimize_readability(content, target)
                for content, target in zip(contents, targets)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error optimizing readability for content {i}: {result}")
                    valid_results.append(self._create_default_optimization_result(contents[i]))
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch readability optimization: {e}")
            return [self._create_default_optimization_result(content) for content in contents]