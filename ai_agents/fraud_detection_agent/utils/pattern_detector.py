"""
Pattern Detector - Advanced Fraud Pattern Recognition System

Sophisticated pattern detection engine for identifying known fraud patterns,
attack signatures, and emerging threats through machine learning and rule-based analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import redis.asyncio as aioredis

try:
    from core.exceptions import PatternDetectionError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    PatternDetectionError = globals().get('PatternDetectionError', Exception)
from ...utils.pattern_matcher import PatternMatcher
from ...data.models.fraud_patterns import FraudPatternModel, PatternSignature

logger = logging.getLogger(__name__)

class PatternCategory(Enum):
    """Fraud pattern categories"""
    AUTOMATED_BEHAVIOR = "automated_behavior"
    CONTENT_SCRAPING = "content_scraping" 
    ACCOUNT_TAKEOVER = "account_takeover"
    FAKE_ENGAGEMENT = "fake_engagement"
    REVENUE_MANIPULATION = "revenue_manipulation"
    IDENTITY_THEFT = "identity_theft"
    PLATFORM_ABUSE = "platform_abuse"
    COORDINATED_ATTACKS = "coordinated_attacks"
    DATA_EXFILTRATION = "data_exfiltration"
    PAYMENT_FRAUD = "payment_fraud"

@dataclass
class PatternSignature:
    """Fraud pattern signature definition"""
    pattern_id: str
    category: PatternCategory
    name: str
    description: str
    indicators: List[str]
    thresholds: Dict[str, float]
    severity: int
    confidence_weight: float
    last_updated: datetime

@dataclass 
class PatternMatch:
    """Pattern detection match result"""
    pattern_id: str
    pattern_name: str
    category: PatternCategory
    confidence: float
    severity: int
    matched_indicators: List[str]
    evidence: Dict[str, Any]
    timestamp: datetime

class PatternDetector:
    """
    Advanced Fraud Pattern Detection Engine
    
    Detects fraud patterns through:
    - Signature-based pattern matching
    - Machine learning pattern recognition
    - Behavioral sequence analysis
    - Temporal pattern analysis
    - Statistical anomaly detection
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.pattern_matcher = PatternMatcher()
        
        # ML models for pattern recognition
        self.pattern_classifier = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            random_state=42
        )
        self.sequence_analyzer = KMeans(n_clusters=10, random_state=42)
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Known fraud patterns
        self.fraud_patterns: Dict[str, PatternSignature] = {}
        self.pattern_statistics: Dict[str, Dict] = {}
        
        # Sequence patterns for detecting automated behavior
        self.known_sequences: Set[str] = set()
        self.sequence_frequency: Dict[str, int] = defaultdict(int)
        
        # Initialize with built-in patterns
        asyncio.create_task(self._initialize_builtin_patterns())
        
        logger.info("Pattern Detector initialized successfully")

    async def detect_patterns(
        self,
        user_id: str,
        platform: str,
        metadata: Dict[str, Any],
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect fraud patterns in user activity
        
        Args:
            user_id: User identifier
            platform: Platform name
            metadata: Request metadata
            historical_data: Historical user data
            
        Returns:
            Pattern detection results
        """
        try:
            # Extract activity sequence
            activity_sequence = self._extract_activity_sequence(metadata, historical_data)
            
            # Run pattern detection methods in parallel
            detection_tasks = await asyncio.gather(
                self._detect_signature_patterns(activity_sequence, metadata),
                self._detect_behavioral_sequences(activity_sequence, user_id),
                self._detect_temporal_patterns(activity_sequence, metadata),
                self._detect_coordinated_patterns(user_id, platform, metadata),
                self._detect_content_patterns(metadata),
                return_exceptions=True
            )
            
            # Collect all pattern matches
            all_matches = []
            for task_result in detection_tasks:
                if not isinstance(task_result, Exception) and task_result:
                    all_matches.extend(task_result)
                    
            # Calculate composite confidence score
            composite_confidence = await self._calculate_composite_confidence(all_matches)
            
            # Filter and rank matches
            filtered_matches = self._filter_and_rank_matches(all_matches)
            
            # Generate pattern analysis
            pattern_analysis = await self._generate_pattern_analysis(
                filtered_matches, activity_sequence, metadata
            )
            
            # Update pattern statistics
            await self._update_pattern_statistics(filtered_matches, user_id)
            
            result = {
                'matches': [match.pattern_name for match in filtered_matches],
                'detailed_matches': [
                    {
                        'pattern_id': match.pattern_id,
                        'name': match.pattern_name,
                        'category': match.category.value,
                        'confidence': match.confidence,
                        'severity': match.severity,
                        'indicators': match.matched_indicators,
                        'evidence': match.evidence
                    }
                    for match in filtered_matches
                ],
                'confidence': composite_confidence,
                'total_patterns': len(filtered_matches),
                'highest_severity': max([m.severity for m in filtered_matches], default=0),
                'pattern_analysis': pattern_analysis,
                'detection_timestamp': datetime.now().isoformat()
            }
            
            logger.info(
                f"Pattern detection completed for user {user_id}: "
                f"patterns={len(filtered_matches)}, confidence={composite_confidence:.3f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Pattern detection failed for user {user_id}: {str(e)}")
            raise PatternDetectionError(f"Pattern detection failed: {str(e)}")

    def _extract_activity_sequence(
        self, 
        metadata: Dict[str, Any], 
        historical_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract chronological activity sequence from metadata and history"""
        activities = []
        
        # Current session activities
        current_activities = metadata.get('activities', [])
        activities.extend(current_activities)
        
        # Recent historical activities
        recent_activities = historical_data.get('recent_activities', [])
        activities.extend(recent_activities)
        
        # Sort by timestamp
        activities.sort(key=lambda x: x.get('timestamp', 0))
        
        return activities

    async def _detect_signature_patterns(
        self,
        activity_sequence: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> List[PatternMatch]:
        """Detect known fraud signatures in activity sequence"""
        matches = []
        
        try:
            for pattern_id, pattern in self.fraud_patterns.items():
                # Check if pattern indicators are present
                matched_indicators = []
                evidence = {}
                
                for indicator in pattern.indicators:
                    if await self._check_indicator_match(indicator, activity_sequence, metadata):
                        matched_indicators.append(indicator)
                        evidence[indicator] = await self._get_indicator_evidence(
                            indicator, activity_sequence, metadata
                        )
                
                # Calculate match confidence
                match_ratio = len(matched_indicators) / len(pattern.indicators)
                
                if match_ratio >= pattern.thresholds.get('min_indicator_ratio', 0.5):
                    confidence = match_ratio * pattern.confidence_weight
                    
                    match = PatternMatch(
                        pattern_id=pattern_id,
                        pattern_name=pattern.name,
                        category=pattern.category,
                        confidence=confidence,
                        severity=pattern.severity,
                        matched_indicators=matched_indicators,
                        evidence=evidence,
                        timestamp=datetime.now()
                    )
                    matches.append(match)
                    
        except Exception as e:
            logger.error(f"Signature pattern detection failed: {str(e)}")
            
        return matches

    async def _detect_behavioral_sequences(
        self,
        activity_sequence: List[Dict[str, Any]],
        user_id: str
    ) -> List[PatternMatch]:
        """Detect automated behavioral sequences"""
        matches = []
        
        try:
            if len(activity_sequence) < 3:
                return matches
                
            # Extract action sequences
            action_sequence = [activity.get('action', '') for activity in activity_sequence]
            sequence_string = ','.join(action_sequence)
            
            # Check for repetitive patterns
            repetitive_patterns = self._find_repetitive_patterns(action_sequence)
            
            for pattern in repetitive_patterns:
                if len(pattern) >= 3:  # Minimum pattern length
                    # Calculate confidence based on repetition frequency
                    pattern_count = action_sequence.count(pattern)
                    confidence = min(1.0, pattern_count * 0.15)
                    
                    if confidence >= 0.3:
                        match = PatternMatch(
                            pattern_id=f"behavioral_sequence_{hash(pattern)}",
                            pattern_name=f"Repetitive Behavior Pattern",
                            category=PatternCategory.AUTOMATED_BEHAVIOR,
                            confidence=confidence,
                            severity=3,
                            matched_indicators=[f"repetitive_sequence: {pattern}"],
                            evidence={'sequence': pattern, 'frequency': pattern_count},
                            timestamp=datetime.now()
                        )
                        matches.append(match)
            
            # Check against known bot sequences
            if sequence_string in self.known_sequences:
                match = PatternMatch(
                    pattern_id="known_bot_sequence",
                    pattern_name="Known Bot Sequence",
                    category=PatternCategory.AUTOMATED_BEHAVIOR,
                    confidence=0.9,
                    severity=4,
                    matched_indicators=["known_bot_signature"],
                    evidence={'sequence': sequence_string},
                    timestamp=datetime.now()
                )
                matches.append(match)
                
        except Exception as e:
            logger.error(f"Behavioral sequence detection failed: {str(e)}")
            
        return matches

    async def _detect_temporal_patterns(
        self,
        activity_sequence: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> List[PatternMatch]:
        """Detect suspicious temporal patterns"""
        matches = []
        
        try:
            if len(activity_sequence) < 5:
                return matches
                
            timestamps = [activity.get('timestamp', 0) for activity in activity_sequence]
            intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            
            # Check for uniform intervals (bot behavior)
            if len(set(intervals)) <= 2 and len(intervals) >= 5:
                confidence = 0.85
                match = PatternMatch(
                    pattern_id="uniform_timing",
                    pattern_name="Uniform Timing Pattern",
                    category=PatternCategory.AUTOMATED_BEHAVIOR,
                    confidence=confidence,
                    severity=3,
                    matched_indicators=["uniform_intervals"],
                    evidence={'intervals': intervals, 'variance': np.var(intervals)},
                    timestamp=datetime.now()
                )
                matches.append(match)
                
            # Check for burst activity patterns
            burst_threshold = 10  # 10 actions within 1 second
            burst_count = 0
            
            for i in range(len(intervals)):
                if intervals[i] < 1.0:
                    burst_count += 1
                else:
                    if burst_count >= burst_threshold:
                        confidence = min(1.0, burst_count * 0.05)
                        match = PatternMatch(
                            pattern_id="burst_activity",
                            pattern_name="Burst Activity Pattern",
                            category=PatternCategory.AUTOMATED_BEHAVIOR,
                            confidence=confidence,
                            severity=4,
                            matched_indicators=["rapid_burst_activity"],
                            evidence={'burst_size': burst_count, 'max_interval': max(intervals)},
                            timestamp=datetime.now()
                        )
                        matches.append(match)
                        break
                    burst_count = 0
                    
        except Exception as e:
            logger.error(f"Temporal pattern detection failed: {str(e)}")
            
        return matches

    async def _detect_coordinated_patterns(
        self,
        user_id: str,
        platform: str,
        metadata: Dict[str, Any]
    ) -> List[PatternMatch]:
        """Detect coordinated attack patterns across users"""
        matches = []
        
        try:
            # Check for coordinated behavior indicators
            user_agent = metadata.get('user_agent', '')
            ip_address = metadata.get('ip_address', '')
            device_fingerprint = metadata.get('device_fingerprint', '')
            
            # Check for shared infrastructure
            coordination_indicators = []
            
            # Similar user agents across multiple accounts
            similar_ua_key = f"user_agents:{platform}"
            ua_count = await self.redis_client.scard(similar_ua_key)
            if ua_count > 100:  # High reuse of same user agent
                coordination_indicators.append("shared_user_agent")
                
            # IP address clustering
            ip_key = f"ip_addresses:{platform}"
            ip_users = await self.redis_client.scard(f"{ip_key}:{ip_address}")
            if ip_users > 50:  # Many users from same IP
                coordination_indicators.append("ip_clustering")
                
            # Device fingerprint similarities
            fingerprint_key = f"fingerprints:{platform}"
            fp_similarity = await self._check_fingerprint_similarity(
                device_fingerprint, fingerprint_key
            )
            if fp_similarity > 0.9:
                coordination_indicators.append("similar_fingerprints")
                
            if coordination_indicators:
                confidence = min(1.0, len(coordination_indicators) * 0.3)
                match = PatternMatch(
                    pattern_id="coordinated_attack",
                    pattern_name="Coordinated Attack Pattern",
                    category=PatternCategory.COORDINATED_ATTACKS,
                    confidence=confidence,
                    severity=5,
                    matched_indicators=coordination_indicators,
                    evidence={
                        'user_agent': user_agent,
                        'ip_address': ip_address[:10] + "...",  # Partial IP for privacy
                        'indicators': coordination_indicators
                    },
                    timestamp=datetime.now()
                )
                matches.append(match)
                
        except Exception as e:
            logger.error(f"Coordinated pattern detection failed: {str(e)}")
            
        return matches

    async def _detect_content_patterns(self, metadata: Dict[str, Any]) -> List[PatternMatch]:
        """Detect content-based fraud patterns"""
        matches = []
        
        try:
            content_data = metadata.get('content', {})
            
            # Check for scraped content indicators
            if self._has_scraping_indicators(content_data):
                match = PatternMatch(
                    pattern_id="content_scraping",
                    pattern_name="Content Scraping Pattern",
                    category=PatternCategory.CONTENT_SCRAPING,
                    confidence=0.8,
                    severity=3,
                    matched_indicators=["scraping_indicators"],
                    evidence=content_data,
                    timestamp=datetime.now()
                )
                matches.append(match)
                
            # Check for duplicate content patterns
            content_hash = content_data.get('content_hash', '')
            if content_hash:
                duplicate_key = f"content_hashes:duplicates"
                duplicate_count = await self.redis_client.scard(f"{duplicate_key}:{content_hash}")
                
                if duplicate_count > 10:  # High duplication
                    match = PatternMatch(
                        pattern_id="duplicate_content",
                        pattern_name="Duplicate Content Pattern",
                        category=PatternCategory.CONTENT_SCRAPING,
                        confidence=0.7,
                        severity=2,
                        matched_indicators=["high_content_duplication"],
                        evidence={'duplicate_count': duplicate_count},
                        timestamp=datetime.now()
                    )
                    matches.append(match)
                    
        except Exception as e:
            logger.error(f"Content pattern detection failed: {str(e)}")
            
        return matches

    async def _check_indicator_match(
        self, 
        indicator: str, 
        activity_sequence: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> bool:
        """Check if a specific indicator matches the current data"""
        try:
            # User agent pattern matching
            if indicator.startswith("user_agent:"):
                pattern = indicator.split(":", 1)[1]
                user_agent = metadata.get('user_agent', '')
                return pattern in user_agent.lower()
                
            # Activity frequency patterns
            elif indicator.startswith("frequency:"):
                threshold = float(indicator.split(":", 1)[1])
                activity_count = len(activity_sequence)
                time_span = self._get_activity_timespan(activity_sequence)
                frequency = activity_count / max(time_span, 1)
                return frequency > threshold
                
            # Sequential action patterns
            elif indicator.startswith("sequence:"):
                pattern = indicator.split(":", 1)[1].split(",")
                actions = [a.get('action', '') for a in activity_sequence]
                return self._contains_subsequence(actions, pattern)
                
            # Timing patterns
            elif indicator.startswith("timing:"):
                timing_type = indicator.split(":", 1)[1]
                return self._check_timing_pattern(timing_type, activity_sequence)
                
            return False
            
        except Exception as e:
            logger.error(f"Indicator match check failed for {indicator}: {str(e)}")
            return False

    async def _get_indicator_evidence(
        self,
        indicator: str,
        activity_sequence: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get evidence for a matched indicator"""
        evidence = {}
        
        try:
            if indicator.startswith("user_agent:"):
                evidence['user_agent'] = metadata.get('user_agent', '')
                
            elif indicator.startswith("frequency:"):
                activity_count = len(activity_sequence)
                time_span = self._get_activity_timespan(activity_sequence)
                evidence['activity_count'] = activity_count
                evidence['time_span'] = time_span
                evidence['frequency'] = activity_count / max(time_span, 1)
                
            elif indicator.startswith("sequence:"):
                actions = [a.get('action', '') for a in activity_sequence]
                evidence['action_sequence'] = actions[:20]  # Limit for readability
                
            elif indicator.startswith("timing:"):
                timestamps = [a.get('timestamp', 0) for a in activity_sequence]
                intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                evidence['timing_intervals'] = intervals[:10]
                
        except Exception as e:
            logger.error(f"Evidence extraction failed for {indicator}: {str(e)}")
            
        return evidence

    def _find_repetitive_patterns(self, action_sequence: List[str]) -> List[str]:
        """Find repetitive patterns in action sequence"""
        patterns = []
        
        # Look for repeating subsequences of length 2-5
        for pattern_length in range(2, min(6, len(action_sequence) // 2)):
            for i in range(len(action_sequence) - pattern_length + 1):
                pattern = action_sequence[i:i + pattern_length]
                pattern_str = ','.join(pattern)
                
                # Count occurrences of this pattern
                count = 0
                for j in range(len(action_sequence) - pattern_length + 1):
                    if action_sequence[j:j + pattern_length] == pattern:
                        count += 1
                        
                # If pattern repeats at least 3 times, consider it suspicious
                if count >= 3:
                    patterns.append(pattern_str)
                    
        return list(set(patterns))  # Remove duplicates

    def _has_scraping_indicators(self, content_data: Dict[str, Any]) -> bool:
        """Check for content scraping indicators"""
        indicators = [
            # Metadata preservation from original source
            'original_url' in content_data,
            'source_platform' in content_data,
            # Unusual content structure
            content_data.get('metadata_count', 0) > 20,
            # Rapid content creation
            content_data.get('creation_speed', 0) < 30,  # seconds
        ]
        
        return sum(indicators) >= 2

    async def _check_fingerprint_similarity(
        self, 
        fingerprint: str, 
        fingerprint_key: str
    ) -> float:
        """Check fingerprint similarity with existing fingerprints"""
        try:
            # Get sample of existing fingerprints
            existing_fps = await self.redis_client.srandmember(fingerprint_key, 100)
            
            if not existing_fps:
                return 0.0
                
            # Simple similarity check (in production, use more sophisticated methods)
            max_similarity = 0.0
            
            for existing_fp in existing_fps:
                similarity = self._calculate_string_similarity(fingerprint, existing_fp)
                max_similarity = max(max_similarity, similarity)
                
            return max_similarity
            
        except Exception as e:
            logger.error(f"Fingerprint similarity check failed: {str(e)}")
            return 0.0

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
            
        # Use Levenshtein distance ratio
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()

    def _get_activity_timespan(self, activity_sequence: List[Dict[str, Any]]) -> float:
        """Get timespan of activity sequence in seconds"""
        if len(activity_sequence) < 2:
            return 1.0
            
        timestamps = [a.get('timestamp', 0) for a in activity_sequence]
        return max(timestamps) - min(timestamps)

    def _contains_subsequence(self, sequence: List[str], pattern: List[str]) -> bool:
        """Check if sequence contains the pattern subsequence"""
        if len(pattern) > len(sequence):
            return False
            
        for i in range(len(sequence) - len(pattern) + 1):
            if sequence[i:i + len(pattern)] == pattern:
                return True
                
        return False

    def _check_timing_pattern(self, timing_type: str, activity_sequence: List[Dict[str, Any]]) -> bool:
        """Check specific timing patterns"""
        if len(activity_sequence) < 2:
            return False
            
        timestamps = [a.get('timestamp', 0) for a in activity_sequence]
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        if timing_type == "uniform":
            # Check if intervals are suspiciously uniform
            variance = np.var(intervals) if intervals else 0
            return variance < 0.01  # Very low variance
            
        elif timing_type == "rapid":
            # Check for rapid-fire actions
            rapid_count = sum(1 for interval in intervals if interval < 0.1)
            return rapid_count > len(intervals) * 0.5
            
        return False

    async def _calculate_composite_confidence(self, matches: List[PatternMatch]) -> float:
        """Calculate composite confidence score from all matches"""
        if not matches:
            return 0.0
            
        # Weight by severity and confidence
        weighted_scores = []
        for match in matches:
            weighted_score = match.confidence * (match.severity / 5.0)
            weighted_scores.append(weighted_score)
            
        # Use maximum weighted score with diminishing returns
        sorted_scores = sorted(weighted_scores, reverse=True)
        composite = sorted_scores[0] if sorted_scores else 0.0
        
        # Add diminishing contribution from additional matches
        for i, score in enumerate(sorted_scores[1:], 1):
            composite += score * (0.5 ** i)
            
        return min(1.0, composite)

    def _filter_and_rank_matches(self, matches: List[PatternMatch]) -> List[PatternMatch]:
        """Filter and rank pattern matches by relevance"""
        # Filter low-confidence matches
        filtered = [match for match in matches if match.confidence >= 0.3]
        
        # Sort by composite score (confidence * severity)
        filtered.sort(key=lambda m: m.confidence * m.severity, reverse=True)
        
        # Limit to top 10 matches
        return filtered[:10]

    async def _generate_pattern_analysis(
        self,
        matches: List[PatternMatch],
        activity_sequence: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive pattern analysis"""
        if not matches:
            return {
                'summary': 'No significant fraud patterns detected',
                'risk_level': 'LOW',
                'recommendations': ['Continue monitoring for pattern emergence']
            }
            
        # Categorize matches
        categories = defaultdict(list)
        for match in matches:
            categories[match.category.value].append(match)
            
        # Determine overall risk level
        max_severity = max(match.severity for match in matches)
        if max_severity >= 5:
            risk_level = 'CRITICAL'
        elif max_severity >= 4:
            risk_level = 'HIGH'
        elif max_severity >= 3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
            
        # Generate recommendations
        recommendations = []
        if PatternCategory.AUTOMATED_BEHAVIOR.value in categories:
            recommendations.append('Implement CAPTCHA verification')
            recommendations.append('Apply rate limiting')
            
        if PatternCategory.COORDINATED_ATTACKS.value in categories:
            recommendations.append('Investigate coordinated account activity')
            recommendations.append('Implement IP-based restrictions')
            
        if PatternCategory.CONTENT_SCRAPING.value in categories:
            recommendations.append('Apply content protection measures')
            recommendations.append('Monitor for unauthorized content usage')
            
        return {
            'summary': f'Detected {len(matches)} fraud patterns across {len(categories)} categories',
            'risk_level': risk_level,
            'pattern_categories': list(categories.keys()),
            'highest_confidence_pattern': matches[0].pattern_name if matches else None,
            'recommendations': recommendations,
            'total_indicators': sum(len(m.matched_indicators) for m in matches)
        }

    async def _update_pattern_statistics(self, matches: List[PatternMatch], user_id: str):
        """Update pattern detection statistics"""
        try:
            for match in matches:
                # Update global pattern statistics
                stats_key = f"pattern_stats:{match.pattern_id}"
                await self.redis_client.hincrby(stats_key, "detection_count", 1)
                await self.redis_client.hset(stats_key, "last_detected", datetime.now().isoformat())
                
                # Update user pattern history
                user_patterns_key = f"user_patterns:{user_id}"
                await self.redis_client.lpush(user_patterns_key, match.pattern_id)
                await self.redis_client.ltrim(user_patterns_key, 0, 99)  # Keep last 100
                await self.redis_client.expire(user_patterns_key, 86400 * 30)  # 30 days
                
        except Exception as e:
            logger.error(f"Failed to update pattern statistics: {str(e)}")

    async def _initialize_builtin_patterns(self):
        """Initialize built-in fraud patterns"""
        try:
            # Automated behavior patterns
            self.fraud_patterns["bot_behavior_1"] = PatternSignature(
                pattern_id="bot_behavior_1",
                category=PatternCategory.AUTOMATED_BEHAVIOR,
                name="Rapid Action Bot",
                description="Bot performing actions at inhuman speed",
                indicators=["frequency:10", "timing:rapid", "user_agent:bot"],
                thresholds={"min_indicator_ratio": 0.6},
                severity=4,
                confidence_weight=0.9,
                last_updated=datetime.now()
            )
            
            # Content scraping patterns
            self.fraud_patterns["content_scraper_1"] = PatternSignature(
                pattern_id="content_scraper_1",
                category=PatternCategory.CONTENT_SCRAPING,
                name="Content Scraper",
                description="Automated content scraping behavior",
                indicators=["sequence:view,download,exit", "timing:uniform", "frequency:5"],
                thresholds={"min_indicator_ratio": 0.5},
                severity=3,
                confidence_weight=0.8,
                last_updated=datetime.now()
            )
            
            # Account takeover patterns
            self.fraud_patterns["account_takeover_1"] = PatternSignature(
                pattern_id="account_takeover_1",
                category=PatternCategory.ACCOUNT_TAKEOVER,
                name="Account Takeover",
                description="Suspicious account access patterns",
                indicators=["user_agent:changed", "frequency:20", "sequence:login,settings,password"],
                thresholds={"min_indicator_ratio": 0.7},
                severity=5,
                confidence_weight=0.95,
                last_updated=datetime.now()
            )
            
            logger.info(f"Initialized {len(self.fraud_patterns)} built-in fraud patterns")
            
        except Exception as e:
            logger.error(f"Failed to initialize built-in patterns: {str(e)}")

    async def learn_pattern(
        self,
        fraud_type: str,
        evidence: Dict[str, Any], 
        confidence: float
    ):
        """Learn new fraud pattern from confirmed fraud case"""
        try:
            # Extract pattern features from evidence
            pattern_features = self._extract_pattern_features(evidence)
            
            if not pattern_features:
                return
                
            # Generate pattern signature
            pattern_id = f"learned_{fraud_type}_{hash(str(pattern_features))}"
            
            # Create new pattern if it doesn't exist
            if pattern_id not in self.fraud_patterns:
                self.fraud_patterns[pattern_id] = PatternSignature(
                    pattern_id=pattern_id,
                    category=PatternCategory(fraud_type) if fraud_type in [c.value for c in PatternCategory] else PatternCategory.PLATFORM_ABUSE,
                    name=f"Learned {fraud_type.replace('_', ' ').title()} Pattern",
                    description=f"Machine learned pattern for {fraud_type}",
                    indicators=pattern_features,
                    thresholds={"min_indicator_ratio": max(0.4, confidence * 0.6)},
                    severity=min(5, int(confidence * 5) + 1),
                    confidence_weight=confidence,
                    last_updated=datetime.now()
                )
                
                logger.info(f"Learned new fraud pattern: {pattern_id}")
            else:
                # Update existing pattern
                existing_pattern = self.fraud_patterns[pattern_id]
                existing_pattern.confidence_weight = (existing_pattern.confidence_weight + confidence) / 2
                existing_pattern.last_updated = datetime.now()
                
                logger.info(f"Updated existing fraud pattern: {pattern_id}")
                
        except Exception as e:
            logger.error(f"Failed to learn pattern: {str(e)}")

    def _extract_pattern_features(self, evidence: Dict[str, Any]) -> List[str]:
        """Extract pattern features from fraud evidence"""
        features = []
        
        try:
            # Behavioral features
            behavioral_anomalies = evidence.get('behavioral_anomalies', [])
            for anomaly in behavioral_anomalies[:3]:  # Limit features
                features.append(f"behavior:{anomaly}")
                
            # Temporal features
            statistical_anomalies = evidence.get('statistical_anomalies', [])
            for anomaly in statistical_anomalies[:2]:
                features.append(f"timing:{anomaly}")
                
            # Content features
            content_manipulation = evidence.get('content_manipulation', [])
            for manipulation in content_manipulation[:2]:
                features.append(f"content:{manipulation}")
                
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            
        return features[:10]  # Limit total features

    async def get_learned_patterns(self) -> Dict[str, Any]:
        """Get all learned patterns for persistence"""
        learned_patterns = {}
        
        for pattern_id, pattern in self.fraud_patterns.items():
            if pattern_id.startswith("learned_"):
                learned_patterns[pattern_id] = {
                    'category': pattern.category.value,
                    'name': pattern.name,
                    'description': pattern.description,
                    'indicators': pattern.indicators,
                    'thresholds': pattern.thresholds,
                    'severity': pattern.severity,
                    'confidence_weight': pattern.confidence_weight,
                    'last_updated': pattern.last_updated.isoformat()
                }
                
        return learned_patterns

    async def load_learned_patterns(self, patterns: Dict[str, Any]):
        """Load previously learned patterns"""
        try:
            for pattern_id, pattern_data in patterns.items():
                self.fraud_patterns[pattern_id] = PatternSignature(
                    pattern_id=pattern_id,
                    category=PatternCategory(pattern_data['category']),
                    name=pattern_data['name'],
                    description=pattern_data['description'],
                    indicators=pattern_data['indicators'],
                    thresholds=pattern_data['thresholds'],
                    severity=pattern_data['severity'],
                    confidence_weight=pattern_data['confidence_weight'],
                    last_updated=datetime.fromisoformat(pattern_data['last_updated'])
                )
                
            logger.info(f"Loaded {len(patterns)} learned patterns")
            
        except Exception as e:
            logger.error(f"Failed to load learned patterns: {str(e)}")

    async def get_pattern_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive pattern detection statistics"""
        try:
            stats = {
                'total_patterns': len(self.fraud_patterns),
                'learned_patterns': len([p for p in self.fraud_patterns if p.startswith('learned_')]),
                'builtin_patterns': len([p for p in self.fraud_patterns if not p.startswith('learned_')]),
                'pattern_categories': {},
                'detection_frequency': {},
                'top_detected_patterns': []
            }
            
            # Count patterns by category
            for pattern in self.fraud_patterns.values():
                category = pattern.category.value
                stats['pattern_categories'][category] = stats['pattern_categories'].get(category, 0) + 1
                
            # Get detection frequencies from Redis
            pattern_detections = []
            for pattern_id in self.fraud_patterns.keys():
                stats_key = f"pattern_stats:{pattern_id}"
                detection_count = await self.redis_client.hget(stats_key, "detection_count")
                if detection_count:
                    pattern_detections.append({
                        'pattern_id': pattern_id,
                        'name': self.fraud_patterns[pattern_id].name,
                        'detections': int(detection_count)
                    })
                    
            # Sort by detection frequency
            pattern_detections.sort(key=lambda x: x['detections'], reverse=True)
            stats['top_detected_patterns'] = pattern_detections[:10]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get pattern statistics: {str(e)}")
            return {'error': str(e)}
