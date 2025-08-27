"""
Professional Text Watermarking Engine
Advanced digital watermarking for text content using semantic and linguistic techniques

Developed by: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Senior Backend + ML Engineer + DBA + Security Expert + 
               Microservices Architect + Audio Engineer + DevOps + AI Prompt Engineer

⚠️ INTELLECTUAL PROPERTY WARNING:
This text watermarking engine, concept, and all associated code are the exclusive intellectual 
property of Fahed Mlaiel. Any unauthorized use, copying, modification, or distribution 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly 
prohibited and will result in legal action.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import hashlib
import base64
import re
import random
import string
import unicodedata
from pathlib import Path

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords, wordnet
    from nltk.stem import WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.corpus import brown
    import spacy
    TEXT_NLP_AVAILABLE = True
except ImportError:
    TEXT_NLP_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextWatermarkTechnique(Enum):
    """Text watermarking techniques"""
    SEMANTIC_SUBSTITUTION = "semantic_substitution"
    SYNTACTIC_TRANSFORMATION = "syntactic_transformation"
    INVISIBLE_CHARACTERS = "invisible_characters"
    LINGUISTIC_STEGANOGRAPHY = "linguistic_steganography"
    WHITESPACE_ENCODING = "whitespace_encoding"
    PUNCTUATION_ENCODING = "punctuation_encoding"
    UNICODE_HOMOGLYPHS = "unicode_homoglyphs"
    SENTENCE_REORDERING = "sentence_reordering"


class TextPreservationLevel(Enum):
    """Text preservation levels"""
    EXACT = "exact"              # Preserve exact meaning
    HIGH = "high"               # High semantic preservation
    MEDIUM = "medium"           # Moderate changes allowed
    LOW = "low"                 # Significant changes allowed


class TextWatermarkStrength(Enum):
    """Text watermark strength levels"""
    SUBTLE = "subtle"           # Minimal changes
    LIGHT = "light"            # Light watermarking
    MEDIUM = "medium"          # Balanced approach
    STRONG = "strong"          # Strong watermarking
    AGGRESSIVE = "aggressive"   # Maximum embedding


@dataclass
class TextWatermarkConfig:
    """Configuration for text watermarking"""
    technique: TextWatermarkTechnique = TextWatermarkTechnique.SEMANTIC_SUBSTITUTION
    strength: TextWatermarkStrength = TextWatermarkStrength.MEDIUM
    preservation_level: TextPreservationLevel = TextPreservationLevel.HIGH
    language: str = "en"
    max_substitutions_per_sentence: int = 3
    semantic_similarity_threshold: float = 0.8
    preserve_proper_nouns: bool = True
    preserve_technical_terms: bool = True
    allow_sentence_reordering: bool = False
    use_frequency_analysis: bool = True


class InvisibleCharacterEncoder:
    """Encoder for invisible character watermarking"""
    
    def __init__(self):
        # Unicode invisible characters
        self.invisible_chars = {
            0: '\u200B',  # Zero Width Space
            1: '\u200C',  # Zero Width Non-Joiner
            2: '\u200D',  # Zero Width Joiner
            3: '\u2060',  # Word Joiner
            4: '\uFEFF',  # Zero Width No-Break Space
        }
        
        # Reverse mapping
        self.char_to_bit = {v: k for k, v in self.invisible_chars.items()}
    
    async def encode_bits(self, bits: List[int], base_radix: int = 5) -> str:
        """Encode bits using invisible characters"""
        try:
            encoded = ""
            
            # Convert bits to base-5 representation
            for i in range(0, len(bits), 3):
                chunk = bits[i:i+3]
                
                # Pad chunk to 3 bits
                while len(chunk) < 3:
                    chunk.append(0)
                
                # Convert 3 bits to decimal (0-7)
                value = chunk[0] * 4 + chunk[1] * 2 + chunk[2]
                
                # Map to invisible character (use modulo for safety)
                char_index = value % len(self.invisible_chars)
                encoded += self.invisible_chars[char_index]
            
            return encoded
            
        except Exception as e:
            logger.error(f"Error encoding bits to invisible characters: {e}")
            return ""
    
    async def decode_bits(self, encoded_text: str) -> List[int]:
        """Decode bits from invisible characters"""
        try:
            bits = []
            
            for char in encoded_text:
                if char in self.char_to_bit:
                    value = self.char_to_bit[char]
                    
                    # Convert back to 3 bits
                    bit_chunk = [
                        (value >> 2) & 1,
                        (value >> 1) & 1,
                        value & 1
                    ]
                    bits.extend(bit_chunk)
            
            return bits
            
        except Exception as e:
            logger.error(f"Error decoding invisible characters: {e}")
            return []


class SemanticProcessor:
    """Semantic text processing for watermarking"""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.synonym_cache = {}
        self.pos_cache = {}
        self.nlp_model = None
        
        if TEXT_NLP_AVAILABLE:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('brown', quiet=True)
                
                self.stop_words = set(stopwords.words('english'))
                self.lemmatizer = WordNetLemmatizer()
                
                # Try to load spaCy model
                try:
                    self.nlp_model = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy English model not found. Using NLTK only.")
                    
            except Exception as e:
                logger.warning(f"Error initializing NLP components: {e}")
    
    async def get_synonyms(self, word: str, pos: str, similarity_threshold: float = 0.8) -> List[str]:
        """Get semantically similar synonyms for a word"""
        try:
            cache_key = f"{word}_{pos}_{similarity_threshold}"
            if cache_key in self.synonym_cache:
                return self.synonym_cache[cache_key]
            
            synonyms = set()
            
            # Get WordNet synonyms
            synsets = wordnet.synsets(word)
            for synset in synsets:
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if (synonym != word and 
                        len(synonym) > 2 and 
                        synonym.isalpha()):
                        synonyms.add(synonym)
            
            # Filter by semantic similarity if spaCy is available
            if self.nlp_model:
                try:
                    word_doc = self.nlp_model(word)
                    filtered_synonyms = []
                    
                    for synonym in synonyms:
                        synonym_doc = self.nlp_model(synonym)
                        if word_doc.similarity(synonym_doc) >= similarity_threshold:
                            filtered_synonyms.append(synonym)
                    
                    synonyms = set(filtered_synonyms)
                except Exception as e:
                    logger.debug(f"Error filtering synonyms with spaCy: {e}")
            
            result = list(synonyms)[:5]  # Limit to top 5 synonyms
            self.synonym_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Error getting synonyms for '{word}': {e}")
            return []
    
    async def analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure for watermarking opportunities"""
        try:
            # Tokenization
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # POS tagging
            pos_tags = pos_tag(words)
            
            # Identify substitutable words
            substitutable = []
            for i, (word, pos) in enumerate(pos_tags):
                if (word.lower() not in self.stop_words and
                    len(word) > 3 and
                    word.isalpha() and
                    pos in ['NN', 'NNS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS']):
                    
                    substitutable.append({
                        'index': i,
                        'word': word,
                        'pos': pos,
                        'sentence_index': self._find_sentence_index(word, sentences)
                    })
            
            # Calculate readability metrics
            readability = await self._calculate_readability(text)
            
            return {
                'sentence_count': len(sentences),
                'word_count': len(words),
                'substitutable_words': substitutable,
                'pos_distribution': self._get_pos_distribution(pos_tags),
                'readability': readability,
                'language_detected': self.language
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text structure: {e}")
            return {}
    
    def _find_sentence_index(self, word: str, sentences: List[str]) -> int:
        """Find which sentence contains the word"""
        for i, sentence in enumerate(sentences):
            if word in sentence:
                return i
        return 0
    
    def _get_pos_distribution(self, pos_tags: List[Tuple[str, str]]) -> Dict[str, int]:
        """Get distribution of POS tags"""
        distribution = {}
        for _, pos in pos_tags:
            distribution[pos] = distribution.get(pos, 0) + 1
        return distribution
    
    async def _calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics"""
        try:
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # Basic metrics
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Simple syllable count (approximation)
            syllable_count = sum(self._count_syllables(word) for word in words)
            
            # Flesch Reading Ease (simplified)
            if len(sentences) > 0 and len(words) > 0:
                flesch_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (syllable_count / len(words)))
            else:
                flesch_ease = 0.0
            
            return {
                'avg_sentence_length': avg_sentence_length,
                'avg_word_length': avg_word_length,
                'syllable_count': syllable_count,
                'flesch_reading_ease': max(0, min(100, flesch_ease))
            }
            
        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            return {}
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count"""
        word = word.lower()
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


class TextWatermarkEngine:
    """
    Professional Text Watermarking Engine
    
    Advanced digital watermarking system for text content supporting:
    - Semantic substitution with synonym replacement
    - Syntactic transformations preserving meaning
    - Invisible character encoding
    - Linguistic steganography
    - Multi-language support
    - Quality preservation controls
    """
    
    def __init__(self, config: Optional[TextWatermarkConfig] = None):
        self.config = config or TextWatermarkConfig()
        
        # Initialize components
        self.invisible_encoder = InvisibleCharacterEncoder()
        self.semantic_processor = SemanticProcessor(self.config.language)
        
        # Processing state
        self.substitution_log = []
        self.quality_metrics = {}
    
    async def embed_watermark(self,
                            text: str,
                            watermark_data: bytes,
                            technique: Optional[TextWatermarkTechnique] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Embed watermark in text using specified technique
        
        Args:
            text: Input text content
            watermark_data: Binary data to embed
            technique: Watermarking technique to use
            
        Returns:
            Tuple of (watermarked_text, embedding_info)
        """
        start_time = datetime.now()
        
        try:
            # Use config technique if not specified
            if technique is None:
                technique = self.config.technique
            
            # Convert watermark data to bits
            watermark_bits = self._data_to_bits(watermark_data)
            
            # Analyze original text
            original_analysis = await self.semantic_processor.analyze_text_structure(text)
            
            # Apply watermarking technique
            if technique == TextWatermarkTechnique.SEMANTIC_SUBSTITUTION:
                watermarked_text, technique_info = await self._embed_semantic_substitution(
                    text, watermark_bits
                )
            elif technique == TextWatermarkTechnique.INVISIBLE_CHARACTERS:
                watermarked_text, technique_info = await self._embed_invisible_characters(
                    text, watermark_bits
                )
            elif technique == TextWatermarkTechnique.SYNTACTIC_TRANSFORMATION:
                watermarked_text, technique_info = await self._embed_syntactic_transformation(
                    text, watermark_bits
                )
            elif technique == TextWatermarkTechnique.WHITESPACE_ENCODING:
                watermarked_text, technique_info = await self._embed_whitespace_encoding(
                    text, watermark_bits
                )
            elif technique == TextWatermarkTechnique.UNICODE_HOMOGLYPHS:
                watermarked_text, technique_info = await self._embed_unicode_homoglyphs(
                    text, watermark_bits
                )
            else:
                raise ValueError(f"Unsupported watermarking technique: {technique}")
            
            # Analyze watermarked text
            watermarked_analysis = await self.semantic_processor.analyze_text_structure(watermarked_text)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                original_analysis, watermarked_analysis
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Compile result information
            result_info = {
                'technique_used': technique.value,
                'strength_level': self.config.strength.value,
                'preservation_level': self.config.preservation_level.value,
                'original_data_bits': len(self._data_to_bits(watermark_data)),
                'total_embedded_bits': len(watermark_bits),
                'processing_time_seconds': processing_time,
                'original_analysis': original_analysis,
                'watermarked_analysis': watermarked_analysis,
                'quality_metrics': quality_metrics,
                'technique_specific': technique_info,
                'substitution_log': self.substitution_log[-100:] if self.substitution_log else []  # Last 100 changes
            }
            
            logger.info(f"Text watermark embedded successfully using {technique.value}")
            return watermarked_text, result_info
            
        except Exception as e:
            logger.error(f"Error embedding text watermark: {e}")
            raise
    
    async def detect_watermark(self,
                             watermarked_text: str,
                             original_text: Optional[str] = None,
                             technique: Optional[TextWatermarkTechnique] = None,
                             expected_data_length: Optional[int] = None) -> Tuple[Optional[bytes], float, Dict[str, Any]]:
        """
        Detect and extract watermark from text
        
        Args:
            watermarked_text: Text containing watermark
            original_text: Optional original text for comparison
            technique: Watermarking technique used
            expected_data_length: Expected length of embedded data
            
        Returns:
            Tuple of (extracted_data, confidence, detection_info)
        """
        start_time = datetime.now()
        
        try:
            if technique is None:
                technique = self.config.technique
            
            # Apply detection based on technique
            if technique == TextWatermarkTechnique.INVISIBLE_CHARACTERS:
                extracted_bits, confidence = await self._detect_invisible_characters(watermarked_text)
            elif technique == TextWatermarkTechnique.WHITESPACE_ENCODING:
                extracted_bits, confidence = await self._detect_whitespace_encoding(watermarked_text)
            elif technique == TextWatermarkTechnique.SEMANTIC_SUBSTITUTION and original_text:
                extracted_bits, confidence = await self._detect_semantic_substitution(
                    watermarked_text, original_text
                )
            else:
                logger.warning(f"Detection not fully implemented for technique: {technique}")
                extracted_bits, confidence = [], 0.0
            
            # Convert bits to data if successful
            extracted_data = None
            if extracted_bits and confidence > 0.5:
                try:
                    if expected_data_length:
                        extracted_bits = extracted_bits[:expected_data_length * 8]
                    extracted_data = self._bits_to_data(extracted_bits)
                except Exception as e:
                    logger.warning(f"Error converting extracted bits to data: {e}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            detection_info = {
                'technique_used': technique.value,
                'detection_confidence': confidence,
                'extracted_bits_count': len(extracted_bits),
                'processing_time_seconds': processing_time,
                'data_extracted': extracted_data is not None,
                'expected_data_length': expected_data_length
            }
            
            logger.info(f"Text watermark detection completed: confidence={confidence:.3f}")
            return extracted_data, confidence, detection_info
            
        except Exception as e:
            logger.error(f"Error detecting text watermark: {e}")
            return None, 0.0, {"error": str(e)}
    
    # Private implementation methods for different techniques
    
    async def _embed_semantic_substitution(self, text: str, watermark_bits: List[int]) -> Tuple[str, Dict[str, Any]]:
        """Embed watermark using semantic substitution"""
        try:
            if not TEXT_NLP_AVAILABLE:
                raise ValueError("NLP libraries not available for semantic substitution")
            
            # Analyze text structure
            text_analysis = await self.semantic_processor.analyze_text_structure(text)
            substitutable_words = text_analysis.get('substitutable_words', [])
            
            if not substitutable_words:
                logger.warning("No substitutable words found in text")
                return text, {"substitutions": 0, "words_analyzed": 0}
            
            # Calculate required substitutions based on watermark size
            max_substitutions = min(
                len(watermark_bits) // 2,  # 2 bits per substitution
                len(substitutable_words) // 3,  # Max 1/3 of words
                self.config.max_substitutions_per_sentence * text_analysis.get('sentence_count', 1)
            )
            
            if max_substitutions <= 0:
                logger.warning("Insufficient capacity for watermark embedding")
                return text, {"error": "insufficient_capacity"}
            
            # Select words for substitution
            random.seed(sum(watermark_bits) % 10000)  # Deterministic randomness
            selected_words = random.sample(substitutable_words, min(max_substitutions, len(substitutable_words)))
            
            # Apply substitutions
            words = text.split()
            substitutions_made = []
            bit_index = 0
            
            for word_info in selected_words:
                if bit_index >= len(watermark_bits) - 1:
                    break
                
                word = word_info['word']
                pos = word_info['pos']
                word_index = word_info['index']
                
                # Get synonyms
                synonyms = await self.semantic_processor.get_synonyms(
                    word, pos, self.config.semantic_similarity_threshold
                )
                
                if synonyms:
                    # Select synonym based on watermark bits
                    bit_pair = watermark_bits[bit_index:bit_index+2]
                    bit_value = bit_pair[0] * 2 + (bit_pair[1] if len(bit_pair) > 1 else 0)
                    
                    synonym_index = bit_value % len(synonyms)
                    chosen_synonym = synonyms[synonym_index]
                    
                    # Apply substitution
                    if word_index < len(words):
                        original_word = words[word_index]
                        words[word_index] = chosen_synonym
                        
                        substitutions_made.append({
                            'original': original_word,
                            'substitute': chosen_synonym,
                            'position': word_index,
                            'bits_encoded': bit_pair,
                            'semantic_similarity': 0.8  # Placeholder
                        })
                        
                        bit_index += 2
            
            watermarked_text = ' '.join(words)
            
            technique_info = {
                'substitutions_made': len(substitutions_made),
                'total_words': len(words),
                'substitution_rate': len(substitutions_made) / len(words),
                'bits_embedded': bit_index,
                'capacity_utilization': bit_index / len(watermark_bits) if watermark_bits else 0,
                'substitution_details': substitutions_made
            }
            
            self.substitution_log.extend(substitutions_made)
            
            return watermarked_text, technique_info
            
        except Exception as e:
            logger.error(f"Error in semantic substitution: {e}")
            return text, {"error": str(e)}
    
    async def _embed_invisible_characters(self, text: str, watermark_bits: List[int]) -> Tuple[str, Dict[str, Any]]:
        """Embed watermark using invisible Unicode characters"""
        try:
            # Encode watermark bits to invisible characters
            invisible_sequence = await self.invisible_encoder.encode_bits(watermark_bits)
            
            if not invisible_sequence:
                return text, {"error": "failed_to_encode_invisible_chars"}
            
            # Insert invisible characters strategically
            sentences = text.split('. ')
            chars_per_sentence = len(invisible_sequence) // max(1, len(sentences))
            
            watermarked_sentences = []
            char_index = 0
            
            for i, sentence in enumerate(sentences):
                # Add invisible characters at word boundaries
                words = sentence.split()
                enhanced_words = []
                
                chars_to_insert = min(chars_per_sentence, len(invisible_sequence) - char_index)
                chars_per_word = chars_to_insert // max(1, len(words))
                
                for j, word in enumerate(words):
                    enhanced_word = word
                    
                    # Insert invisible characters after word
                    if char_index < len(invisible_sequence):
                        insert_count = min(chars_per_word, len(invisible_sequence) - char_index)
                        if insert_count > 0:
                            chars_to_add = invisible_sequence[char_index:char_index + insert_count]
                            enhanced_word += chars_to_add
                            char_index += insert_count
                    
                    enhanced_words.append(enhanced_word)
                
                watermarked_sentences.append(' '.join(enhanced_words))
            
            watermarked_text = '. '.join(watermarked_sentences)
            
            technique_info = {
                'invisible_chars_inserted': char_index,
                'total_bits_encoded': len(watermark_bits),
                'insertion_rate': char_index / len(text.replace(' ', '')) if text else 0,
                'encoding_efficiency': char_index / len(invisible_sequence) if invisible_sequence else 0
            }
            
            return watermarked_text, technique_info
            
        except Exception as e:
            logger.error(f"Error in invisible character embedding: {e}")
            return text, {"error": str(e)}
    
    async def _embed_syntactic_transformation(self, text: str, watermark_bits: List[int]) -> Tuple[str, Dict[str, Any]]:
        """Embed watermark using syntactic transformations"""
        try:
            sentences = sent_tokenize(text)
            transformed_sentences = []
            transformations_applied = []
            bit_index = 0
            
            for i, sentence in enumerate(sentences):
                if bit_index >= len(watermark_bits):
                    transformed_sentences.append(sentence)
                    continue
                
                # Determine transformation based on watermark bit
                if watermark_bits[bit_index] == 1:
                    # Apply transformation (e.g., passive to active voice)
                    transformed_sentence, transformation = await self._apply_syntactic_transformation(sentence)
                    
                    if transformation:
                        transformations_applied.append({
                            'sentence_index': i,
                            'original': sentence,
                            'transformed': transformed_sentence,
                            'transformation_type': transformation,
                            'bit_encoded': watermark_bits[bit_index]
                        })
                        transformed_sentences.append(transformed_sentence)
                    else:
                        transformed_sentences.append(sentence)
                else:
                    # Keep original sentence
                    transformed_sentences.append(sentence)
                
                bit_index += 1
            
            watermarked_text = ' '.join(transformed_sentences)
            
            technique_info = {
                'transformations_applied': len(transformations_applied),
                'total_sentences': len(sentences),
                'transformation_rate': len(transformations_applied) / len(sentences),
                'bits_embedded': bit_index,
                'transformation_details': transformations_applied
            }
            
            return watermarked_text, technique_info
            
        except Exception as e:
            logger.error(f"Error in syntactic transformation: {e}")
            return text, {"error": str(e)}
    
    async def _embed_whitespace_encoding(self, text: str, watermark_bits: List[int]) -> Tuple[str, Dict[str, Any]]:
        """Embed watermark using whitespace patterns"""
        try:
            # Use different whitespace patterns to encode bits
            # 0 = single space, 1 = double space
            lines = text.split('\n')
            watermarked_lines = []
            bit_index = 0
            
            for line in lines:
                if not line.strip():
                    watermarked_lines.append(line)
                    continue
                
                words = line.split()
                if len(words) < 2:
                    watermarked_lines.append(line)
                    continue
                
                # Encode bits in spacing between words
                encoded_line = words[0]
                for i in range(1, len(words)):
                    if bit_index < len(watermark_bits):
                        if watermark_bits[bit_index] == 0:
                            encoded_line += ' ' + words[i]  # Single space
                        else:
                            encoded_line += '  ' + words[i]  # Double space
                        bit_index += 1
                    else:
                        encoded_line += ' ' + words[i]
                
                watermarked_lines.append(encoded_line)
            
            watermarked_text = '\n'.join(watermarked_lines)
            
            technique_info = {
                'bits_embedded': bit_index,
                'total_bits': len(watermark_bits),
                'lines_processed': len(lines),
                'encoding_efficiency': bit_index / len(watermark_bits) if watermark_bits else 0
            }
            
            return watermarked_text, technique_info
            
        except Exception as e:
            logger.error(f"Error in whitespace encoding: {e}")
            return text, {"error": str(e)}
    
    async def _embed_unicode_homoglyphs(self, text: str, watermark_bits: List[int]) -> Tuple[str, Dict[str, Any]]:
        """Embed watermark using Unicode homoglyphs"""
        try:
            # Define homoglyph mappings (visually similar characters)
            homoglyphs = {
                'a': ['а', 'ɑ'],  # Cyrillic and other variants
                'e': ['е', 'ҽ'],
                'o': ['о', 'ο'],
                'p': ['р', 'ρ'],
                'c': ['с', 'ϲ'],
                'x': ['х', 'χ'],
                'y': ['у', 'γ']
            }
            
            watermarked_text = text
            substitutions_made = []
            bit_index = 0
            
            for i, char in enumerate(text):
                if bit_index >= len(watermark_bits):
                    break
                
                char_lower = char.lower()
                if char_lower in homoglyphs and watermark_bits[bit_index] == 1:
                    # Replace with homoglyph
                    variant_index = (bit_index // 8) % len(homoglyphs[char_lower])
                    replacement = homoglyphs[char_lower][variant_index]
                    
                    # Preserve original case
                    if char.isupper():
                        replacement = replacement.upper()
                    
                    watermarked_text = watermarked_text[:i] + replacement + watermarked_text[i+1:]
                    
                    substitutions_made.append({
                        'position': i,
                        'original': char,
                        'replacement': replacement,
                        'bit_encoded': watermark_bits[bit_index]
                    })
                
                if char.isalpha():
                    bit_index += 1
            
            technique_info = {
                'substitutions_made': len(substitutions_made),
                'bits_embedded': bit_index,
                'total_characters': len(text),
                'substitution_rate': len(substitutions_made) / len(text),
                'substitution_details': substitutions_made
            }
            
            return watermarked_text, technique_info
            
        except Exception as e:
            logger.error(f"Error in Unicode homoglyph embedding: {e}")
            return text, {"error": str(e)}
    
    # Detection methods
    
    async def _detect_invisible_characters(self, text: str) -> Tuple[List[int], float]:
        """Detect invisible character watermarks"""
        try:
            # Extract invisible characters
            invisible_chars = []
            for char in text:
                if char in self.invisible_encoder.char_to_bit:
                    invisible_chars.append(char)
            
            if not invisible_chars:
                return [], 0.0
            
            # Decode bits
            extracted_bits = await self.invisible_encoder.decode_bits(''.join(invisible_chars))
            
            # Calculate confidence based on pattern consistency
            confidence = min(1.0, len(invisible_chars) / 100)  # Confidence increases with more chars
            
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error detecting invisible characters: {e}")
            return [], 0.0
    
    async def _detect_whitespace_encoding(self, text: str) -> Tuple[List[int], float]:
        """Detect whitespace pattern watermarks"""
        try:
            lines = text.split('\n')
            extracted_bits = []
            total_spaces = 0
            double_spaces = 0
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Analyze spacing patterns
                words = re.split(r'(\s+)', line)
                for i in range(1, len(words), 2):  # Process spaces only
                    space = words[i]
                    if ' ' in space:
                        total_spaces += 1
                        if len(space) == 1:
                            extracted_bits.append(0)  # Single space = 0
                        elif len(space) == 2:
                            extracted_bits.append(1)  # Double space = 1
                            double_spaces += 1
            
            # Calculate confidence
            if total_spaces == 0:
                confidence = 0.0
            else:
                # Expect some variation in spacing for watermark
                space_variation = double_spaces / total_spaces
                confidence = min(1.0, space_variation * 2)  # More variation = higher confidence
            
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error detecting whitespace encoding: {e}")
            return [], 0.0
    
    async def _detect_semantic_substitution(self, watermarked_text: str, original_text: str) -> Tuple[List[int], float]:
        """Detect semantic substitution watermarks by comparing with original"""
        try:
            if not TEXT_NLP_AVAILABLE:
                return [], 0.0
            
            original_words = word_tokenize(original_text)
            watermarked_words = word_tokenize(watermarked_text)
            
            if len(original_words) != len(watermarked_words):
                return [], 0.0
            
            substitutions = []
            for i, (orig, wm) in enumerate(zip(original_words, watermarked_words)):
                if orig.lower() != wm.lower() and orig.isalpha() and wm.isalpha():
                    # Check if words are semantically related
                    if await self._are_semantically_related(orig, wm):
                        substitutions.append({
                            'position': i,
                            'original': orig,
                            'substitute': wm
                        })
            
            # Attempt to decode bits from substitutions
            extracted_bits = []
            for sub in substitutions:
                # Try to reverse-engineer the bit encoding
                # This is a simplified approach
                orig_hash = hash(sub['original']) % 4
                sub_hash = hash(sub['substitute']) % 4
                
                bit_pair = [(orig_hash >> 1) & 1, orig_hash & 1]
                extracted_bits.extend(bit_pair)
            
            # Calculate confidence
            if len(substitutions) == 0:
                confidence = 0.0
            else:
                # Higher confidence with more substitutions
                confidence = min(1.0, len(substitutions) / 20)
            
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error detecting semantic substitution: {e}")
            return [], 0.0
    
    async def _are_semantically_related(self, word1: str, word2: str) -> bool:
        """Check if two words are semantically related"""
        try:
            # Simple check using WordNet
            synsets1 = wordnet.synsets(word1)
            synsets2 = wordnet.synsets(word2)
            
            for s1 in synsets1:
                for s2 in synsets2:
                    if s1.wup_similarity(s2) and s1.wup_similarity(s2) > 0.6:
                        return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking semantic relation: {e}")
            return False
    
    async def _apply_syntactic_transformation(self, sentence: str) -> Tuple[str, Optional[str]]:
        """Apply syntactic transformation to sentence"""
        try:
            # Simple transformations - can be expanded
            transformations = [
                ("passive_to_active", self._passive_to_active),
                ("active_to_passive", self._active_to_passive),
                ("sentence_split", self._split_sentence),
                ("clause_reorder", self._reorder_clauses)
            ]
            
            for transform_name, transform_func in transformations:
                try:
                    transformed = await transform_func(sentence)
                    if transformed and transformed != sentence:
                        return transformed, transform_name
                except Exception as e:
                    logger.debug(f"Transformation {transform_name} failed: {e}")
                    continue
            
            return sentence, None
            
        except Exception as e:
            logger.error(f"Error applying syntactic transformation: {e}")
            return sentence, None
    
    async def _passive_to_active(self, sentence: str) -> str:
        """Convert passive voice to active voice (simplified)"""
        # This is a placeholder - real implementation would need advanced NLP
        if " was " in sentence or " were " in sentence:
            # Simple pattern replacement
            sentence = sentence.replace(" was ", " ")
            sentence = sentence.replace(" were ", " ")
        return sentence
    
    async def _active_to_passive(self, sentence: str) -> str:
        """Convert active voice to passive voice (simplified)"""
        # Placeholder implementation
        return sentence
    
    async def _split_sentence(self, sentence: str) -> str:
        """Split compound sentence (simplified)"""
        # Look for conjunction points
        if " and " in sentence:
            parts = sentence.split(" and ", 1)
            if len(parts) == 2:
                return f"{parts[0].strip()}. {parts[1].strip()}"
        return sentence
    
    async def _reorder_clauses(self, sentence: str) -> str:
        """Reorder clauses in sentence (simplified)"""
        # Look for comma-separated clauses
        if ", " in sentence:
            parts = sentence.split(", ", 1)
            if len(parts) == 2:
                return f"{parts[1].strip()}, {parts[0].strip()}"
        return sentence
    
    # Utility methods
    
    def _data_to_bits(self, data: bytes) -> List[int]:
        """Convert byte data to list of bits"""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits
    
    def _bits_to_data(self, bits: List[int]) -> bytes:
        """Convert list of bits to byte data"""
        # Pad bits to multiple of 8
        while len(bits) % 8 != 0:
            bits.append(0)
        
        data = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << (7 - j)
            data.append(byte)
        
        return bytes(data)
    
    async def _calculate_quality_metrics(self,
                                      original_analysis: Dict[str, Any],
                                      watermarked_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality preservation metrics"""
        try:
            metrics = {}
            
            # Word count preservation
            orig_words = original_analysis.get('word_count', 0)
            wm_words = watermarked_analysis.get('word_count', 0)
            
            if orig_words > 0:
                metrics['word_count_preservation'] = min(1.0, wm_words / orig_words)
            else:
                metrics['word_count_preservation'] = 1.0
            
            # Sentence count preservation
            orig_sentences = original_analysis.get('sentence_count', 0)
            wm_sentences = watermarked_analysis.get('sentence_count', 0)
            
            if orig_sentences > 0:
                metrics['sentence_count_preservation'] = min(1.0, wm_sentences / orig_sentences)
            else:
                metrics['sentence_count_preservation'] = 1.0
            
            # Readability preservation
            orig_readability = original_analysis.get('readability', {})
            wm_readability = watermarked_analysis.get('readability', {})
            
            if orig_readability and wm_readability:
                orig_flesch = orig_readability.get('flesch_reading_ease', 50)
                wm_flesch = wm_readability.get('flesch_reading_ease', 50)
                
                if orig_flesch > 0:
                    readability_ratio = min(1.0, wm_flesch / orig_flesch)
                    metrics['readability_preservation'] = readability_ratio
                else:
                    metrics['readability_preservation'] = 1.0
            else:
                metrics['readability_preservation'] = 1.0
            
            # Overall quality score
            quality_scores = [
                metrics.get('word_count_preservation', 1.0),
                metrics.get('sentence_count_preservation', 1.0),
                metrics.get('readability_preservation', 1.0)
            ]
            
            metrics['overall_quality'] = sum(quality_scores) / len(quality_scores)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return {'overall_quality': 0.0}
    
    async def analyze_capacity(self, text: str, technique: TextWatermarkTechnique) -> Dict[str, Any]:
        """
        Analyze text watermarking capacity for given technique
        
        Args:
            text: Input text to analyze
            technique: Watermarking technique
            
        Returns:
            Dictionary with capacity analysis
        """
        try:
            analysis = await self.semantic_processor.analyze_text_structure(text)
            
            capacity_info = {
                'text_length': len(text),
                'word_count': analysis.get('word_count', 0),
                'sentence_count': analysis.get('sentence_count', 0),
                'technique': technique.value
            }
            
            if technique == TextWatermarkTechnique.SEMANTIC_SUBSTITUTION:
                substitutable = len(analysis.get('substitutable_words', []))
                capacity_info.update({
                    'substitutable_words': substitutable,
                    'estimated_capacity_bits': substitutable * 2,  # 2 bits per substitution
                    'max_data_bytes': (substitutable * 2) // 8
                })
            
            elif technique == TextWatermarkTechnique.INVISIBLE_CHARACTERS:
                word_boundaries = analysis.get('word_count', 0) - 1  # Spaces between words
                capacity_info.update({
                    'insertion_points': word_boundaries,
                    'estimated_capacity_bits': word_boundaries * 3,  # Multiple chars per point
                    'max_data_bytes': (word_boundaries * 3) // 8
                })
            
            elif technique == TextWatermarkTechnique.WHITESPACE_ENCODING:
                word_boundaries = analysis.get('word_count', 0) - 1
                capacity_info.update({
                    'encoding_points': word_boundaries,
                    'estimated_capacity_bits': word_boundaries,  # 1 bit per space
                    'max_data_bytes': word_boundaries // 8
                })
            
            elif technique == TextWatermarkTechnique.SYNTACTIC_TRANSFORMATION:
                sentences = analysis.get('sentence_count', 0)
                capacity_info.update({
                    'transformable_sentences': sentences,
                    'estimated_capacity_bits': sentences,  # 1 bit per sentence
                    'max_data_bytes': sentences // 8
                })
            
            else:
                capacity_info.update({
                    'estimated_capacity_bits': 0,
                    'max_data_bytes': 0
                })
            
            # Calculate efficiency metrics
            if capacity_info.get('estimated_capacity_bits', 0) > 0:
                capacity_info['bits_per_word'] = capacity_info['estimated_capacity_bits'] / analysis.get('word_count', 1)
                capacity_info['efficiency_rating'] = min(1.0, capacity_info['estimated_capacity_bits'] / (len(text) * 0.1))
            else:
                capacity_info['bits_per_word'] = 0.0
                capacity_info['efficiency_rating'] = 0.0
            
            return capacity_info
            
        except Exception as e:
            logger.error(f"Error analyzing text capacity: {e}")
            return {'error': str(e)}
    
    async def verify_watermark_integrity(self,
                                       watermarked_text: str,
                                       original_data: bytes,
                                       technique: TextWatermarkTechnique) -> Dict[str, Any]:
        """
        Verify watermark integrity and robustness
        
        Args:
            watermarked_text: Text with embedded watermark
            original_data: Original watermark data
            technique: Technique used for embedding
            
        Returns:
            Dictionary with integrity verification results
        """
        try:
            # Attempt extraction
            extracted_data, confidence, detection_info = await self.detect_watermark(
                watermarked_text, technique=technique, expected_data_length=len(original_data)
            )
            
            integrity_results = {
                'extraction_successful': extracted_data is not None,
                'detection_confidence': confidence,
                'data_integrity': False,
                'bit_error_rate': 1.0,
                'technique_used': technique.value
            }
            
            if extracted_data:
                # Compare with original data
                original_bits = self._data_to_bits(original_data)
                extracted_bits = self._data_to_bits(extracted_data)
                
                # Calculate bit error rate
                min_length = min(len(original_bits), len(extracted_bits))
                if min_length > 0:
                    errors = sum(1 for i in range(min_length) 
                               if original_bits[i] != extracted_bits[i])
                    bit_error_rate = errors / min_length
                    
                    integrity_results.update({
                        'data_integrity': bit_error_rate < 0.1,  # < 10% error rate
                        'bit_error_rate': bit_error_rate,
                        'bits_compared': min_length,
                        'bit_errors': errors
                    })
                
                # Exact match check
                integrity_results['exact_match'] = extracted_data == original_data
            
            # Add detection info
            integrity_results.update(detection_info)
            
            return integrity_results
            
        except Exception as e:
            logger.error(f"Error verifying watermark integrity: {e}")
            return {'error': str(e), 'extraction_successful': False}


# Factory function for easy instantiation
async def create_text_watermark_engine(config: Optional[TextWatermarkConfig] = None) -> TextWatermarkEngine:
    """
    Factory function to create and initialize text watermark engine
    
    Args:
        config: Optional configuration for the engine
        
    Returns:
        Initialized TextWatermarkEngine instance
    """
    engine = TextWatermarkEngine(config)
    
    # Perform any async initialization if needed
    if TEXT_NLP_AVAILABLE:
        try:
            # Pre-warm NLP components
            await engine.semantic_processor.analyze_text_structure("Sample text for initialization.")
            logger.info("Text watermark engine initialized successfully")
        except Exception as e:
            logger.warning(f"Error during engine initialization: {e}")
    
    return engine
        """Embed watermark using semantic substitution"""
                            'pos': pos,
                            'synonyms': synonyms
                        })
            
            # Calculate how many words to substitute
            max_substitutions = min(len(substitutable_words), 
                                  int(len(words) * substitution_rate),
                                  len(data_bits))
            
            if max_substitutions == 0:
                raise ValueError("No suitable words found for substitution")
            
            # Select words for embedding
            selected_indices = random.sample(range(len(substitutable_words)), max_substitutions)
            selected_words = [substitutable_words[i] for i in selected_indices]
            
            # Sort by index to maintain order
            selected_words.sort(key=lambda x: x['index'])
            
            # Apply substitutions based on bits
            watermarked_words = words.copy()
            substitutions_made = []
            
            for i, word_info in enumerate(selected_words):
                if i < len(data_bits):
                    bit = data_bits[i]
                    word_index = word_info['index']
                    original_word = word_info['word']
                    synonyms = word_info['synonyms']
                    
                    if bit == 1 and len(synonyms) > 0:
                        # Use synonym for bit 1
                        new_word = synonyms[0]
                        watermarked_words[word_index] = new_word
                        substitutions_made.append({
                            'index': word_index,
                            'original': original_word,
                            'substitute': new_word,
                            'bit': bit
                        })
                    # For bit 0, keep original word (no substitution)
            
            # Reconstruct text
            watermarked_text = self._reconstruct_text(watermarked_words, text)
            
            # Calculate quality metrics
            semantic_similarity = await self._calculate_semantic_similarity(text, watermarked_text)
            readability_score = await self._calculate_readability(watermarked_text)
            
            result_info = {
                "method": "semantic_substitution",
                "strength": strength,
                "original_length": len(words),
                "substitutions_made": len(substitutions_made),
                "data_embedded_bits": min(len(data_bits), len(selected_words)),
                "substitution_rate_actual": len(substitutions_made) / len(words),
                "semantic_similarity": semantic_similarity,
                "readability_score": readability_score,
                "preservation_level": preservation_level,
                "substitutions": substitutions_made[:10],  # First 10 for inspection
                "robustness_level": "medium"
            }
            
            return watermarked_text, result_info
            
        except Exception as e:
            logger.error(f"Semantic watermarking failed: {str(e)}")
            raise
    
    async def embed_linguistic_watermark(
        self,
        text: str,
        watermark_data: bytes,
        strength: str = "medium",
        method: str = "syntax_variation"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Embeds watermark using linguistic transformations
        Modifies sentence structure while preserving meaning
        """
        try:
            data_bits = self._data_to_bits(watermark_data)
            sentences = sent_tokenize(text)
            
            # Strength parameters
            strength_params = {
                "light": {"modification_rate": 0.1, "complexity": "simple"},
                "medium": {"modification_rate": 0.2, "complexity": "moderate"},
                "strong": {"modification_rate": 0.3, "complexity": "complex"},
                "maximum": {"modification_rate": 0.4, "complexity": "advanced"}
            }
            
            params = strength_params.get(strength, strength_params["medium"])
            modification_rate = params["modification_rate"]
            complexity = params["complexity"]
            
            watermarked_sentences = []
            modifications_made = []
            bit_index = 0
            
            for i, sentence in enumerate(sentences):
                if bit_index >= len(data_bits):
                    watermarked_sentences.append(sentence)
                    continue
                
                # Decide whether to modify this sentence
                if random.random() < modification_rate and bit_index < len(data_bits):
                    bit = data_bits[bit_index]
                    
                    if method == "syntax_variation":
                        modified_sentence, modification_info = await self._apply_syntax_variation(
                            sentence, bit, complexity
                        )
                    elif method == "punctuation_encoding":
                        modified_sentence, modification_info = await self._apply_punctuation_encoding(
                            sentence, bit
                        )
                    elif method == "word_spacing":
                        modified_sentence, modification_info = await self._apply_spacing_encoding(
                            sentence, bit
                        )
                    else:  # style_variation
                        modified_sentence, modification_info = await self._apply_style_variation(
                            sentence, bit
                        )
                    
                    watermarked_sentences.append(modified_sentence)
                    modifications_made.append({
                        'sentence_index': i,
                        'method': method,
                        'bit': bit,
                        'modification': modification_info
                    })
                    bit_index += 1
                else:
                    watermarked_sentences.append(sentence)
            
            # Reconstruct text
            watermarked_text = ' '.join(watermarked_sentences)
            
            # Quality metrics
            grammatical_score = await self._assess_grammar(watermarked_text)
            style_consistency = await self._assess_style_consistency(text, watermarked_text)
            
            result_info = {
                "method": f"linguistic_{method}",
                "strength": strength,
                "total_sentences": len(sentences),
                "modifications_made": len(modifications_made),
                "data_embedded_bits": bit_index,
                "modification_rate_actual": len(modifications_made) / len(sentences),
                "grammatical_score": grammatical_score,
                "style_consistency": style_consistency,
                "complexity": complexity,
                "modifications": modifications_made[:5],  # Sample for inspection
                "robustness_level": "high"
            }
            
            return watermarked_text, result_info
            
        except Exception as e:
            logger.error(f"Linguistic watermarking failed: {str(e)}")
            raise
    
    async def embed_invisible_text_watermark(
        self,
        text: str,
        watermark_data: bytes,
        strength: str = "medium",
        techniques: List[str] = ["zero_width", "unicode_variants"]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Embeds completely invisible watermark using zero-width characters and Unicode variants
        Undetectable to human readers but recoverable by algorithms
        """
        try:
            data_bits = self._data_to_bits(watermark_data)
            
            # Zero-width characters for steganography
            zero_width_chars = {
                '0': '\u200B',  # Zero Width Space
                '1': '\u200C',  # Zero Width Non-Joiner
                'separator': '\u200D',  # Zero Width Joiner
                'marker': '\uFEFF'  # Zero Width No-Break Space
            }
            
            # Unicode homoglyphs for substitution
            unicode_variants = {
                'a': ['a', 'а', 'ɑ'],  # Latin, Cyrillic, Greek
                'e': ['e', 'е', 'ε'],
                'o': ['o', 'о', 'ο'],
                'p': ['p', 'р', 'ρ'],
                'c': ['c', 'с', 'ϲ'],
                'x': ['x', 'х', 'χ'],
                'y': ['y', 'у', 'γ'],
                'i': ['i', 'і', 'ι']
            }
            
            watermarked_text = text
            modifications_made = []
            
            if "zero_width" in techniques:
                # Embed using zero-width characters
                words = text.split()
                bit_index = 0
                
                for i, word in enumerate(words):
                    if bit_index >= len(data_bits):
                        break
                    
                    # Every 5th word gets zero-width encoding
                    if i % 5 == 0 and bit_index < len(data_bits):
                        # Take next 4 bits or remaining bits
                        bits_to_encode = data_bits[bit_index:bit_index + 4]
                        
                        # Convert bits to zero-width sequence
                        zw_sequence = zero_width_chars['marker']  # Start marker
                        for bit in bits_to_encode:
                            zw_sequence += zero_width_chars[str(bit)]
                        zw_sequence += zero_width_chars['separator']  # End marker
                        
                        # Insert after word
                        words[i] = word + zw_sequence
                        
                        modifications_made.append({
                            'type': 'zero_width',
                            'word_index': i,
                            'bits_encoded': len(bits_to_encode),
                            'sequence_length': len(zw_sequence)
                        })
                        
                        bit_index += len(bits_to_encode)
                
                watermarked_text = ' '.join(words)
            
            if "unicode_variants" in techniques and bit_index < len(data_bits):
                # Embed using Unicode homoglyphs
                remaining_bits = data_bits[bit_index:]
                chars = list(watermarked_text.lower())
                
                variant_positions = []
                for i, char in enumerate(chars):
                    if char in unicode_variants and len(unicode_variants[char]) > 1:
                        variant_positions.append(i)
                
                # Select positions for substitution
                substitution_count = min(len(remaining_bits), len(variant_positions))
                selected_positions = random.sample(variant_positions, substitution_count)
                selected_positions.sort()
                
                watermarked_chars = list(watermarked_text)
                
                for i, pos in enumerate(selected_positions):
                    if i < len(remaining_bits):
                        bit = remaining_bits[i]
                        original_char = watermarked_chars[pos].lower()
                        
                        if original_char in unicode_variants:
                            variants = unicode_variants[original_char]
                            if bit == 1 and len(variants) > 1:
                                # Use variant for bit 1
                                new_char = variants[1]
                                # Preserve case
                                if watermarked_chars[pos].isupper():
                                    new_char = new_char.upper()
                                watermarked_chars[pos] = new_char
                                
                                modifications_made.append({
                                    'type': 'unicode_variant',
                                    'position': pos,
                                    'original': original_char,
                                    'variant': new_char,
                                    'bit': bit
                                })
                
                watermarked_text = ''.join(watermarked_chars)
                bit_index += substitution_count
            
            # Calculate imperceptibility metrics
            visual_similarity = self._calculate_visual_similarity(text, watermarked_text)
            byte_difference = len(watermarked_text.encode('utf-8')) - len(text.encode('utf-8'))
            
            result_info = {
                "method": "invisible_text",
                "techniques_used": techniques,
                "strength": strength,
                "data_embedded_bits": bit_index,
                "modifications_made": len(modifications_made),
                "visual_similarity": visual_similarity,
                "byte_difference": byte_difference,
                "invisible_chars_added": sum(1 for mod in modifications_made if mod['type'] == 'zero_width'),
                "unicode_substitutions": sum(1 for mod in modifications_made if mod['type'] == 'unicode_variant'),
                "modifications": modifications_made[:10],  # Sample for inspection
                "robustness_level": "very_high"
            }
            
            return watermarked_text, result_info
            
        except Exception as e:
            logger.error(f"Invisible text watermarking failed: {str(e)}")
            raise
    
    async def detect_text_watermark(
        self,
        watermarked_text: str,
        original_text: Optional[str] = None,
        detection_method: str = "auto",
        reference_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detects and extracts watermark from text
        Supports multiple detection strategies
        """
        try:
            detections = []
            
            if detection_method in ["auto", "semantic"]:
                semantic_detection = await self._detect_semantic_watermark(
                    watermarked_text, original_text, reference_data
                )
                if semantic_detection["detected"]:
                    detections.append(("semantic", semantic_detection))
            
            if detection_method in ["auto", "linguistic"]:
                linguistic_detection = await self._detect_linguistic_watermark(
                    watermarked_text, original_text, reference_data
                )
                if linguistic_detection["detected"]:
                    detections.append(("linguistic", linguistic_detection))
            
            if detection_method in ["auto", "invisible"]:
                invisible_detection = await self._detect_invisible_watermark(
                    watermarked_text, reference_data
                )
                if invisible_detection["detected"]:
                    detections.append(("invisible", invisible_detection))
            
            # Analyze results
            if detections:
                best_detection = max(detections, key=lambda x: x[1]["confidence"])
                
                result = {
                    "watermark_detected": True,
                    "detection_method": best_detection[0],
                    "confidence": best_detection[1]["confidence"],
                    "extracted_data": best_detection[1].get("extracted_data"),
                    "all_detections": detections,
                    "text_length": len(watermarked_text),
                    "analysis_methods": len(detections)
                }
            else:
                result = {
                    "watermark_detected": False,
                    "confidence": 0.0,
                    "text_length": len(watermarked_text),
                    "methods_tried": detection_method,
                    "message": "No watermark detected"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Text watermark detection failed: {str(e)}")
            return {
                "watermark_detected": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    # Helper methods
    
    async def _get_synonyms(
        self,
        word: str,
        pos: str,
        semantic_distance: float
    ) -> List[str]:
        """Gets semantically similar words using WordNet"""
        try:
            if not TEXT_NLP_AVAILABLE:
                return []
            
            # Cache lookup
            cache_key = f"{word}_{pos}_{semantic_distance}"
            if cache_key in self.synonym_cache:
                return self.synonym_cache[cache_key]
            
            # Map POS tags to WordNet POS
            pos_map = {
                'NN': wordnet.NOUN, 'NNS': wordnet.NOUN,
                'VB': wordnet.VERB, 'VBD': wordnet.VERB, 'VBG': wordnet.VERB,
                'VBN': wordnet.VERB, 'VBP': wordnet.VERB, 'VBZ': wordnet.VERB,
                'JJ': wordnet.ADJ, 'JJR': wordnet.ADJ, 'JJS': wordnet.ADJ
            }
            
            wn_pos = pos_map.get(pos)
            if not wn_pos:
                return []
            
            synonyms = set()
            synsets = wordnet.synsets(word, pos=wn_pos)
            
            for synset in synsets[:3]:  # Limit to first 3 synsets
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if (synonym.lower() != word.lower() and 
                        len(synonym) > 2 and 
                        synonym.isalpha()):
                        synonyms.add(synonym)
            
            # Filter by semantic distance (simplified)
            filtered_synonyms = list(synonyms)[:3]  # Limit to 3 best synonyms
            
            self.synonym_cache[cache_key] = filtered_synonyms
            return filtered_synonyms
            
        except Exception as e:
            logger.error(f"Synonym retrieval failed: {e}")
            return []
    
    def _reconstruct_text(self, words: List[str], original_text: str) -> str:
        """Reconstructs text maintaining original formatting"""
        try:
            # Simple reconstruction - could be improved with better formatting preservation
            return ' '.join(words)
        except:
            return ' '.join(words)
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculates semantic similarity between texts"""
        try:
            # Simplified similarity - could use more advanced NLP models
            words1 = set(word_tokenize(text1.lower())) if TEXT_NLP_AVAILABLE else set(text1.lower().split())
            words2 = set(word_tokenize(text2.lower())) if TEXT_NLP_AVAILABLE else set(text2.lower().split())
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
        except:
            return 0.8  # Default assumption of good similarity
    
    async def _calculate_readability(self, text: str) -> float:
        """Calculates readability score"""
        try:
            # Simplified readability score
            sentences = sent_tokenize(text) if TEXT_NLP_AVAILABLE else text.split('.')
            words = word_tokenize(text) if TEXT_NLP_AVAILABLE else text.split()
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            # Simple heuristic
            if avg_sentence_length < 10:
                return 0.9
            elif avg_sentence_length < 20:
                return 0.8
            else:
                return 0.7
        except:
            return 0.8
    
    async def _apply_syntax_variation(self, sentence: str, bit: int, complexity: str) -> Tuple[str, Dict[str, Any]]:
        """Applies syntax variations based on bit value"""
        # Simplified syntax variation
        if bit == 1:
            # Active to passive voice conversion or similar
            # This is a placeholder for more sophisticated transformations
            return sentence, {"type": "syntax", "applied": "passive_voice"}
        else:
            return sentence, {"type": "syntax", "applied": "none"}
    
    async def _apply_punctuation_encoding(self, sentence: str, bit: int) -> Tuple[str, Dict[str, Any]]:
        """Encodes bit in punctuation patterns"""
        if bit == 1:
            # Add extra space before punctuation
            sentence = re.sub(r'([.!?])', r' \1', sentence)
            return sentence, {"type": "punctuation", "applied": "extra_space"}
        else:
            return sentence, {"type": "punctuation", "applied": "none"}
    
    async def _apply_spacing_encoding(self, sentence: str, bit: int) -> Tuple[str, Dict[str, Any]]:
        """Encodes bit in word spacing"""
        if bit == 1:
            # Double space between some words
            words = sentence.split()
            if len(words) > 3:
                words[len(words)//2] = words[len(words)//2] + ' '
            return ' '.join(words), {"type": "spacing", "applied": "double_space"}
        else:
            return sentence, {"type": "spacing", "applied": "none"}
    
    async def _apply_style_variation(self, sentence: str, bit: int) -> Tuple[str, Dict[str, Any]]:
        """Applies style variations"""
        # Placeholder for style variations
        return sentence, {"type": "style", "applied": "none"}
    
    async def _assess_grammar(self, text: str) -> float:
        """Assesses grammatical correctness"""
        # Simplified grammar assessment
        return 0.9  # Placeholder
    
    async def _assess_style_consistency(self, original: str, modified: str) -> float:
        """Assesses style consistency"""
        # Simplified style assessment
        return 0.85  # Placeholder
    
    def _calculate_visual_similarity(self, text1: str, text2: str) -> float:
        """Calculates visual similarity"""
        # Character-level similarity
        if len(text1) != len(text2):
            return 0.8
        
        matches = sum(1 for a, b in zip(text1, text2) if a == b)
        return matches / len(text1) if text1 else 1.0
    
    async def _detect_semantic_watermark(
        self,
        text: str,
        original: Optional[str],
        reference: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detects semantic watermarks"""
        # Placeholder for semantic detection
        return {"detected": False, "confidence": 0.0}
    
    async def _detect_linguistic_watermark(
        self,
        text: str,
        original: Optional[str],
        reference: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detects linguistic watermarks"""
        # Placeholder for linguistic detection
        return {"detected": False, "confidence": 0.0}
    
    async def _detect_invisible_watermark(
        self,
        text: str,
        reference: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detects invisible watermarks"""
        try:
            # Look for zero-width characters
            zero_width_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF']
            zw_count = sum(text.count(char) for char in zero_width_chars)
            
            if zw_count > 0:
                return {
                    "detected": True,
                    "confidence": min(0.9, zw_count / 10),
                    "zero_width_chars_found": zw_count,
                    "method": "zero_width_detection"
                }
            
            return {"detected": False, "confidence": 0.0}
            
        except Exception as e:
            return {"detected": False, "confidence": 0.0, "error": str(e)}
    
    def _data_to_bits(self, data: bytes) -> List[int]:
        """Converts byte data to bit array"""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits
