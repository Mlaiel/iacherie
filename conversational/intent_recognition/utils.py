"""
Utility Functions for Intent Recognition

Comprehensive utility functions for text preprocessing, confidence calibration,
performance monitoring, and general helper operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

import re
import time
import hashlib
import unicodedata
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import json

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import calibration_curve
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

from .intent_classifier import IntentCategory
from .exceptions import ValidationError, ProcessingTimeoutError


# Text preprocessing utilities

def intent_preprocessing(
    text: str,
    clean_html: bool = True,
    normalize_unicode: bool = True,
    remove_extra_whitespace: bool = True,
    lowercase: bool = True,
    remove_special_chars: bool = False,
    max_length: Optional[int] = None
) -> str:
    """
    Comprehensive text preprocessing for intent recognition
    
    Args:
        text: Input text to preprocess
        clean_html: Remove HTML tags and entities
        normalize_unicode: Normalize unicode characters
        remove_extra_whitespace: Remove excessive whitespace
        lowercase: Convert to lowercase
        remove_special_chars: Remove special characters
        max_length: Maximum text length (truncate if longer)
        
    Returns:
        Preprocessed text ready for classification
    """
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # Clean HTML tags and entities if requested
        if clean_html:
            text = clean_html_content(text)
        
        # Normalize unicode characters
        if normalize_unicode:
            text = unicodedata.normalize('NFKC', text)
        
        # Remove or replace special characters
        if remove_special_chars:
            # Keep only alphanumeric, spaces, and basic punctuation
            text = re.sub(r'[^\w\s.,!?;:\'-]', ' ', text)
        
        # Convert to lowercase
        if lowercase:
            text = text.lower()
        
        # Remove extra whitespace
        if remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        if max_length and len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0]  # Truncate at word boundary
        
        return text
        
    except Exception as e:
        logging.warning(f"Text preprocessing failed: {str(e)}")
        return text.strip() if text else ""


def clean_html_content(text: str) -> str:
    """Remove HTML tags and decode HTML entities"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' ',
        '&copy;': '©',
        '&reg;': '®'
    }
    
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    return text


def extract_keywords(
    text: str,
    max_keywords: int = 10,
    min_length: int = 3,
    exclude_stopwords: bool = True
) -> List[str]:
    """
    Extract important keywords from text for intent analysis
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        min_length: Minimum keyword length
        exclude_stopwords: Whether to exclude stop words
        
    Returns:
        List of extracted keywords
    """



    try:
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter by length
        words = [word for word in words if len(word) >= min_length]
        
        # Remove stop words if requested
        if exclude_stopwords:
            words = [word for word in words if word not in STOP_WORDS]
        
        # Count word frequencies
        word_freq = defaultdict(int)
        for word in words:
            word_freq[word] += 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:max_keywords]]
        
    except Exception as e:
        logging.warning(f"Keyword extraction failed: {str(e)}")
        return []


def detect_intent_patterns(text: str) -> Dict[str, bool]:
    """
    Detect common intent patterns in text
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary of detected patterns
    """
    patterns = {
        'question': bool(re.search(r'\?|^(what|how|when|where|why|who|which|can|could|would|should|do|does|is|are)', text.lower())),
        'request': bool(re.search(r'^(please|could you|can you|would you|i need|i want|help me)', text.lower())),
        'command': bool(re.search(r'^(upload|download|create|delete|share|protect|analyze|show|get|set)', text.lower())),
        'negative': bool(re.search(r'\b(not|no|never|none|nothing|nowhere|nobody)\b', text.lower())),
        'urgent': bool(re.search(r'\b(urgent|asap|immediately|quickly|fast|emergency)\b', text.lower())),
        'temporal': bool(re.search(r'\b(today|tomorrow|yesterday|now|later|soon|schedule)\b', text.lower())),
        'collaborative': bool(re.search(r'\b(share|collaborate|team|together|with|invite)\b', text.lower())),
        'analytics': bool(re.search(r'\b(analyze|report|stats|metrics|performance|insights)\b', text.lower()))
    }
    
    return patterns


def calculate_text_complexity(text: str) -> Dict[str, float]:
    """
    Calculate various text complexity metrics
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary of complexity metrics
    """



    try:
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        char_count = len(text)
        
        # Avoid division by zero
        if word_count == 0:
            return {
                'word_count': 0,
                'sentence_count': 0,
                'avg_word_length': 0,
                'avg_sentence_length': 0,
                'lexical_diversity': 0,
                'complexity_score': 0
            }
        
        # Advanced metrics
        avg_word_length = sum(len(word) for word in words) / word_count
        avg_sentence_length = word_count / max(sentence_count, 1)
        unique_words = len(set(word.lower() for word in words))
        lexical_diversity = unique_words / word_count
        
        # Complexity score (0-1, higher = more complex)
        complexity_score = min(1.0, (
            (avg_word_length / 10) * 0.3 +
            (avg_sentence_length / 20) * 0.3 +
            (1 - lexical_diversity) * 0.2 +
            (char_count / 1000) * 0.2
        ))
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'lexical_diversity': lexical_diversity,
            'complexity_score': complexity_score
        }
        
    except Exception as e:
        logging.warning(f"Text complexity calculation failed: {str(e)}")
        return {
            'word_count': 0,
            'sentence_count': 0,
            'avg_word_length': 0,
            'avg_sentence_length': 0,
            'lexical_diversity': 0,
            'complexity_score': 0
        }


# Confidence calibration utilities

class ConfidenceCalibrator:
    """
    Calibrate confidence scores using historical data
    
    Provides methods for isotonic regression calibration and
    temperature scaling for improved confidence estimates.
    """
    
    def __init__(self):
        self.calibrators = {}  # Per-intent calibrators
        self.global_calibrator = None
        self.calibration_data = defaultdict(list)
        self.is_fitted = False
    
    def add_calibration_data(
        self,
        intent: IntentCategory,
        confidence: float,
        correct: bool
    ) -> None:
        """Add calibration data point"""
        self.calibration_data[intent].append((confidence, correct))
    
    def fit_calibrators(self) -> None:
        """Fit calibration models using collected data"""



        try:
            # Fit per-intent calibrators
            for intent, data in self.calibration_data.items():
                if len(data) >= 10:  # Minimum data points
                    confidences, labels = zip(*data)
                    
                    calibrator = IsotonicRegression(out_of_bounds='clip')
                    calibrator.fit(confidences, labels)
                    self.calibrators[intent] = calibrator
            
            # Fit global calibrator
            all_data = []
            for data in self.calibration_data.values():
                all_data.extend(data)
            
            if len(all_data) >= 50:
                confidences, labels = zip(*all_data)
                
                self.global_calibrator = IsotonicRegression(out_of_bounds='clip')
                self.global_calibrator.fit(confidences, labels)
            
            self.is_fitted = True
            logging.info("Confidence calibrators fitted successfully")
            
        except Exception as e:
            logging.error(f"Calibrator fitting failed: {str(e)}")
    
    def calibrate_confidence(
        self,
        intent: IntentCategory,
        confidence: float
    ) -> float:
        """Calibrate confidence score for specific intent"""
        if not self.is_fitted:
            return confidence
        
        try:
            # Use intent-specific calibrator if available
            if intent in self.calibrators:
                return float(self.calibrators[intent].predict([confidence])[0])
            
            # Fall back to global calibrator
            elif self.global_calibrator:
                return float(self.global_calibrator.predict([confidence])[0])
            
            # Return original confidence if no calibrator available
            else:
                return confidence
                
        except Exception as e:
            logging.warning(f"Confidence calibration failed: {str(e)}")
            return confidence


def confidence_calibration(
    confidences: List[float],
    true_labels: List[bool],
    method: str = "isotonic"
) -> Callable[[float], float]:
    """
    Create confidence calibration function
    
    Args:
        confidences: List of confidence scores
        true_labels: List of true/false labels
        method: Calibration method ("isotonic" or "platt")
        
    Returns:
        Calibration function
    """
    try:
        if method == "isotonic":
            from sklearn.isotonic import IsotonicRegression
            calibrator = IsotonicRegression(out_of_bounds='clip')
        else:
            from sklearn.linear_model import LogisticRegression
            calibrator = LogisticRegression()
        
        # Reshape data for sklearn
        X = np.array(confidences).reshape(-1, 1)
        y = np.array(true_labels)
        
        # Fit calibrator
        calibrator.fit(X, y)
        
        def calibrate_score(confidence: float) -> float:
            try:
                calibrated = calibrator.predict_proba([[confidence]])
                return float(calibrated[0][1])  # Probability of positive class
            except:
                return confidence
        
        return calibrate_score
        
    except Exception as e:
        logging.error(f"Calibration function creation failed: {str(e)}")
        return lambda x: x  # Identity function as fallback


# Performance monitoring utilities

class PerformanceMonitor:
    """
    Monitor and track performance metrics for intent recognition
    
    Provides real-time metrics collection, statistical analysis,
    and performance alerting capabilities.
    """
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        
        # Metric storage
        self.response_times = deque(maxlen=window_size)
        self.confidence_scores = deque(maxlen=window_size)
        self.error_counts = defaultdict(int)
        self.intent_counts = defaultdict(int)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'avg_response_time': 0.0,
            'avg_confidence': 0.0,
            'error_rate': 0.0
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': 1000.0,  # ms
            'min_confidence': 0.7,
            'max_error_rate': 0.05
        }
    
    def record_request(
        self,
        response_time_ms: float,
        confidence: float,
        intent: IntentCategory,
        success: bool = True,
        error_type: Optional[str] = None
    ) -> None:
        """Record performance metrics for a request"""
        
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
            self.response_times.append(response_time_ms)
            self.confidence_scores.append(confidence)
            self.intent_counts[intent] += 1
        else:
            if error_type:
                self.error_counts[error_type] += 1
        
        # Update running statistics
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """Update running statistics"""
        total = self.stats['total_requests']
        
        if total > 0:
            self.stats['error_rate'] = 1.0 - (self.stats['successful_requests'] / total)
        
        if self.response_times:
            self.stats['avg_response_time'] = sum(self.response_times) / len(self.response_times)
        
        if self.confidence_scores:
            self.stats['avg_confidence'] = sum(self.confidence_scores) / len(self.confidence_scores)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""



        return {
            'statistics': self.stats.copy(),
            'recent_response_times': {
                'min': min(self.response_times) if self.response_times else 0,
                'max': max(self.response_times) if self.response_times else 0,
                'median': np.median(self.response_times) if self.response_times else 0,
                'p95': np.percentile(self.response_times, 95) if self.response_times else 0
            },
            'recent_confidence_scores': {
                'min': min(self.confidence_scores) if self.confidence_scores else 0,
                'max': max(self.confidence_scores) if self.confidence_scores else 0,
                'median': np.median(self.confidence_scores) if self.confidence_scores else 0
            },
            'error_breakdown': dict(self.error_counts),
            'intent_distribution': dict(self.intent_counts),
            'alerts': self.check_alerts()
        }
    
    def check_alerts(self) -> List[str]:
        """Check for performance alerts"""
        alerts = []
        
        # Response time alert
        if (self.response_times and 
            self.stats['avg_response_time'] > self.thresholds['max_response_time']):
            alerts.append(f"High response time: {self.stats['avg_response_time']:.1f}ms")
        
        # Confidence alert
        if (self.confidence_scores and 
            self.stats['avg_confidence'] < self.thresholds['min_confidence']):
            alerts.append(f"Low confidence: {self.stats['avg_confidence']:.2f}")
        
        # Error rate alert
        if self.stats['error_rate'] > self.thresholds['max_error_rate']:
            alerts.append(f"High error rate: {self.stats['error_rate']:.1%}")
        
        return alerts


def performance_monitoring(
    func: Callable,
    monitor: Optional[PerformanceMonitor] = None
) -> Callable:
    """
    Decorator for monitoring function performance
    
    Args:
        func: Function to monitor
        monitor: Performance monitor instance
        
    Returns:
        Decorated function with performance monitoring
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Record successful execution
            if monitor:
                execution_time = (time.time() - start_time) * 1000
                monitor.record_request(
                    response_time_ms=execution_time,
                    confidence=getattr(result, 'confidence', 0.5),
                    intent=getattr(result, 'primary_intent', IntentCategory.UNKNOWN),
                    success=True
                )
            
            return result
            
        except Exception as e:
            # Record failed execution
            if monitor:
                execution_time = (time.time() - start_time) * 1000
                monitor.record_request(
                    response_time_ms=execution_time,
                    confidence=0.0,
                    intent=IntentCategory.UNKNOWN,
                    success=False,
                    error_type=e.__class__.__name__
                )
            
            raise
    
    return wrapper


# General utility functions

def generate_request_id(prefix: str = "intent") -> str:
    """Generate unique request ID"""
    timestamp = str(int(time.time() * 1000))
    return f"{prefix}_{timestamp}_{hash(timestamp) % 10000}"


def hash_text(text: str, algorithm: str = "md5") -> str:
    """Generate hash for text content"""
    text_bytes = text.encode('utf-8')
    
    if algorithm == "md5":
        return hashlib.md5(text_bytes).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text_bytes).hexdigest()
    else:
        return hashlib.md5(text_bytes).hexdigest()


def validate_text_input(
    text: str,
    min_length: int = 1,
    max_length: int = 10000,
    allowed_languages: Optional[List[str]] = None,
    blocked_patterns: Optional[List[str]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate text input for intent recognition
    
    Args:
        text: Input text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        allowed_languages: List of allowed language codes
        blocked_patterns: List of blocked regex patterns
        
    Returns:
        Tuple of (is_valid, error_message)
    """



    try:
        # Check basic requirements
        if not text or not isinstance(text, str):
            return False, "Text input is required"
        
        text = text.strip()
        
        # Length validation
        if len(text) < min_length:
            return False, f"Text too short (minimum {min_length} characters)"
        
        if len(text) > max_length:
            return False, f"Text too long (maximum {max_length} characters)"
        
        # Check for blocked patterns
        if blocked_patterns:
            for pattern in blocked_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return False, "Text contains blocked content"
        
        # Language validation (simplified)
        if allowed_languages:
            # This would typically use a language detection library
            # For now, just check for basic ASCII
            if not text.isascii() and 'en' not in allowed_languages:
                return False, "Text language not supported"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def format_confidence_score(confidence: float, precision: int = 2) -> str:
    """Format confidence score for display"""
    percentage = confidence * 100
    return f"{percentage:.{precision}f}%"


def calculate_entropy(probabilities: List[float]) -> float:
    """Calculate entropy of probability distribution"""



    try:
        probabilities = np.array(probabilities)
        # Add small epsilon to avoid log(0)
        probabilities = probabilities + 1e-10
        # Normalize
        probabilities = probabilities / np.sum(probabilities)
        # Calculate entropy
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return float(entropy)
    except:
        return 0.0


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay
    
    Args:
        attempt: Attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
        
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        import random
        delay *= (0.5 + random.random() * 0.5)  # +/- 25% jitter
    
    return delay


def batch_iterator(items: List[Any], batch_size: int):
    """Iterate over items in batches"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def safe_json_serialize(obj: Any) -> str:
    """Safely serialize object to JSON"""



    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception as e:
        logging.warning(f"JSON serialization failed: {str(e)}")
        return "{}"


def timestamp_to_iso(timestamp: Optional[datetime] = None) -> str:
    """Convert timestamp to ISO format string"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.isoformat()


# Creative industry specific utilities

def extract_creative_entities(text: str) -> Dict[str, List[str]]:
    """Extract creative industry specific entities"""
    entities = {
        'platforms': [],
        'content_types': [],
        'actions': [],
        'genres': [],
        'tools': []
    }
    
    # Platform patterns
    platform_patterns = r'\b(spotify|youtube|instagram|tiktok|soundcloud|bandcamp|facebook|twitter|linkedin)\b'
    entities['platforms'] = re.findall(platform_patterns, text.lower())
    
    # Content type patterns
    content_patterns = r'\b(song|track|album|playlist|video|photo|image|post|story|reel|podcast)\b'
    entities['content_types'] = re.findall(content_patterns, text.lower())
    
    # Action patterns
    action_patterns = r'\b(upload|download|share|create|edit|delete|publish|schedule|analyze|protect|monetize)\b'
    entities['actions'] = re.findall(action_patterns, text.lower())
    
    # Genre patterns
    genre_patterns = r'\b(pop|rock|jazz|classical|electronic|hip-hop|country|folk|blues|reggae)\b'
    entities['genres'] = re.findall(genre_patterns, text.lower())
    
    # Tool patterns
    tool_patterns = r'\b(camera|microphone|studio|daw|photoshop|premiere|audacity|garageband)\b'
    entities['tools'] = re.findall(tool_patterns, text.lower())
    
    return entities


def detect_collaboration_intent(text: str) -> Dict[str, Any]:
    """Detect collaboration-related intent indicators"""
    collaboration_indicators = {
        'sharing': bool(re.search(r'\b(share|sharing|shared)\b', text.lower())),
        'inviting': bool(re.search(r'\b(invite|invitation|join|collaborate)\b', text.lower())),
        'team_work': bool(re.search(r'\b(team|together|group|collaboration|partner)\b', text.lower())),
        'permissions': bool(re.search(r'\b(permission|access|rights|allow|restrict)\b', text.lower())),
        'feedback': bool(re.search(r'\b(feedback|review|comment|approve|reject)\b', text.lower()))
    }
    
    collaboration_score = sum(collaboration_indicators.values()) / len(collaboration_indicators)
    
    return {
        'indicators': collaboration_indicators,
        'collaboration_score': collaboration_score,
        'likely_collaboration': collaboration_score > 0.3
    }
