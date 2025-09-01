"""Entity Extraction Utilities - IA Influencer Agent

Advanced utility functions and helper classes for entity extraction module
with performance optimization, data processing, and validation utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
import asyncio
import hashlib
import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import unicodedata
import functools

import numpy as np
from fuzzywuzzy import fuzz
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TextProcessor:
    """Advanced text processing utilities for entity extraction"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for consistent processing"""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common encoding issues
        text = text.replace('\u2019', "'").replace('\u2018', "'")  # Smart quotes
        text = text.replace('\u201c', '"').replace('\u201d', '"')  # Smart quotes
        text = text.replace('\u2013', '-').replace('\u2014', '-')  # Dashes
        
        return text
    
    @staticmethod
    def extract_handles_hashtags(text: str) -> Tuple[List[str], List[str]]:
        """Extract social media handles and hashtags from text"""
        # Extract handles (@username)
        handle_pattern = r'@([a-zA-Z0-9_]{1,50})'
        handles = re.findall(handle_pattern, text)
        
        # Extract hashtags (#hashtag)
        hashtag_pattern = r'#([a-zA-Z0-9_]{1,100})'
        hashtags = re.findall(hashtag_pattern, text)
        
        return handles, hashtags
    
    @staticmethod
    def clean_entity_text(text: str) -> str:
        """Clean extracted entity text"""
        if not text:
            return ""
        
        # Remove special characters but preserve important ones
        text = re.sub(r'[^\w\s\-&.\']', '', text)
        
        # Normalize case for consistency
        text = text.strip()
        
        # Remove redundant words
        stop_words = {'the', 'and', 'or', 'but', 'a', 'an'}
        words = text.split()
        words = [word for word in words if word.lower() not in stop_words or len(words) <= 2]
        
        return ' '.join(words)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect text language (simplified)"""
        # Simple language detection based on character patterns
        if re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', text.lower()):
            return 'fr'  # French
        elif re.search(r'[äöüß]', text.lower()):
            return 'de'  # German
        elif re.search(r'[ñáéíóúü]', text.lower()):
            return 'es'  # Spanish
        else:
            return 'en'  # English (default)


class SimilarityCalculator:
    """Advanced similarity calculation utilities"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.is_fitted = False
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Use fuzzy string matching for basic similarity
        fuzzy_score = fuzz.ratio(text1.lower(), text2.lower()) / 100.0
        
        # Use token sort ratio for word order independence
        token_score = fuzz.token_sort_ratio(text1.lower(), text2.lower()) / 100.0
        
        # Combine scores
        return (fuzzy_score + token_score) / 2.0
    
    def calculate_semantic_similarity(self, texts: List[str]) -> np.ndarray:
        """Calculate semantic similarity matrix for multiple texts"""
        if len(texts) < 2:
            return np.array([[1.0]])
        
        try:
            # Fit and transform texts
            if not self.is_fitted:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                self.is_fitted = True
            else:
                tfidf_matrix = self.tfidf_vectorizer.transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return similarity_matrix
            
        except Exception as e:
            logging.warning(f"Semantic similarity calculation failed: {e}")
            # Fallback to identity matrix
            return np.eye(len(texts))
    
    def find_similar_entities(self, target: str, candidates: List[str], threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar entities from candidate list"""
        similar_entities = []
        
        for candidate in candidates:
            similarity = self.calculate_text_similarity(target, candidate)
            if similarity >= threshold:
                similar_entities.append((candidate, similarity))
        
        # Sort by similarity score (descending)
        similar_entities.sort(key=lambda x: x[1], reverse=True)
        return similar_entities


class PerformanceTimer:
    """Performance timing utilities for optimization"""
    
    def __init__(self):
        self.start_times = {}
        self.durations = {}
    
    def start(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def stop(self, operation: str) -> float:
        """Stop timing and return duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.durations[operation] = duration
            del self.start_times[operation]
            return duration
        return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'completed_operations': len(self.durations),
            'active_operations': len(self.start_times),
            'average_duration': sum(self.durations.values()) / len(self.durations) if self.durations else 0.0,
            'total_time': sum(self.durations.values()),
            'operation_stats': self.durations.copy()
        }


class DataValidator:
    """Data validation utilities for entity extraction"""
    
    @staticmethod
    def validate_entity_data(entity_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate entity data structure"""
        errors = []
        
        # Required fields
        required_fields = ['text', 'entity_type', 'confidence']
        for field in required_fields:
            if field not in entity_data:
                errors.append(f"Missing required field: {field}")
        
        # Data type validation
        if 'confidence' in entity_data:
            confidence = entity_data['confidence']
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                errors.append("Confidence must be a number between 0.0 and 1.0")
        
        if 'text' in entity_data:
            if not isinstance(entity_data['text'], str) or len(entity_data['text'].strip()) == 0:
                errors.append("Text must be a non-empty string")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_platform_url(url: str, expected_platform: str) -> bool:
        """Validate platform URL format"""
        platform_patterns = {
            'youtube': r'(?:youtube\.com|youtu\.be)',
            'instagram': r'instagram\.com',
            'tiktok': r'tiktok\.com',
            'spotify': r'spotify\.com',
            'soundcloud': r'soundcloud\.com',
            'twitter': r'(?:twitter\.com|x\.com)',
            'facebook': r'facebook\.com',
            'linkedin': r'linkedin\.com'
        }
        
        pattern = platform_patterns.get(expected_platform.lower())
        if pattern:
            return bool(re.search(pattern, url, re.IGNORECASE))
        
        return False
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """Sanitize input text for security"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return text.strip()


class CacheManager:
    """Advanced caching utilities for entity extraction"""
    
    def __init__(self, max_size: int = 10000, ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get_cache_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, str):
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        elif isinstance(data, dict):
            return hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(str(data).encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        if key in self.cache:
            # Check if expired
            if time.time() - self.timestamps[key] > self.ttl:
                self.remove(key)
                return None
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set item in cache"""
        # Remove oldest items if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def remove(self, key: str):
        """Remove item from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def _evict_oldest(self):
        """Evict oldest cache entries"""
        # Remove 10% of oldest entries
        num_to_remove = max(1, self.max_size // 10)
        oldest_keys = sorted(self.timestamps.keys(), key=lambda k: self.timestamps[k])[:num_to_remove]
        
        for key in oldest_keys:
            self.remove(key)
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        expired_count = sum(1 for ts in self.timestamps.values() if now - ts > self.ttl)
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'expired_entries': expired_count,
            'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1),
            'memory_usage_mb': sum(len(str(v)) for v in self.cache.values()) / (1024 * 1024)
        }


def timing_decorator(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logging.debug(f"{func.__name__} took {duration:.3f} seconds")
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logging.debug(f"{func.__name__} took {duration:.3f} seconds")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def retry_decorator(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class EntityDeduplicator:
    """Advanced entity deduplication utilities"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.similarity_calculator = SimilarityCalculator()
    
    def deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities based on text similarity"""
        if len(entities) <= 1:
            return entities
        
        unique_entities = []
        entity_texts = [entity.get('text', '') for entity in entities]
        
        # Calculate similarity matrix
        similarity_matrix = self.similarity_calculator.calculate_semantic_similarity(entity_texts)
        
        # Track which entities to keep
        keep_indices = set(range(len(entities)))
        
        for i in range(len(entities)):
            if i not in keep_indices:
                continue
                
            for j in range(i + 1, len(entities)):
                if j not in keep_indices:
                    continue
                    
                if similarity_matrix[i][j] > self.similarity_threshold:
                    # Keep the entity with higher confidence
                    entity_i_conf = entities[i].get('confidence', 0.0)
                    entity_j_conf = entities[j].get('confidence', 0.0)
                    
                    if entity_i_conf >= entity_j_conf:
                        keep_indices.discard(j)
                    else:
                        keep_indices.discard(i)
                        break
        
        # Return unique entities
        return [entities[i] for i in sorted(keep_indices)]


# Global instances
text_processor = TextProcessor()
similarity_calculator = SimilarityCalculator()
performance_timer = PerformanceTimer()
data_validator = DataValidator()
cache_manager = CacheManager()
entity_deduplicator = EntityDeduplicator()


# Utility functions
def create_entity_fingerprint(entity_data: Dict[str, Any]) -> str:
    """Create unique fingerprint for entity"""
    key_fields = ['text', 'entity_type', 'start_pos', 'end_pos']
    fingerprint_data = {k: v for k, v in entity_data.items() if k in key_fields}
    return hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()


def merge_entity_metadata(base_entity: Dict[str, Any], additional_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Merge additional metadata into base entity"""
    merged = base_entity.copy()
    
    if 'metadata' not in merged:
        merged['metadata'] = {}
    
    merged['metadata'].update(additional_metadata)
    
    # Update confidence if new metadata provides higher confidence
    if 'confidence' in additional_metadata:
        current_confidence = merged.get('confidence', 0.0)
        new_confidence = additional_metadata['confidence']
        merged['confidence'] = max(current_confidence, new_confidence)
    
    return merged


def format_extraction_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Format extraction results for API response"""
    return {
        'entities': results.get('entities', []),
        'total_count': len(results.get('entities', [])),
        'processing_time': results.get('processing_time', 0.0),
        'confidence_stats': {
            'average': np.mean([e.get('confidence', 0.0) for e in results.get('entities', [])]) if results.get('entities') else 0.0,
            'min': min([e.get('confidence', 0.0) for e in results.get('entities', [])], default=0.0),
            'max': max([e.get('confidence', 0.0) for e in results.get('entities', [])], default=0.0)
        },
        'entity_types': list(set([e.get('entity_type') for e in results.get('entities', []) if e.get('entity_type')])),
        'extracted_at': datetime.now().isoformat(),
        'version': '1.0.0'
    }
