#!/usr/bin/env python3
"""
🚀 Enterprise Notification Rate Limiter - IA Chéries Platform Core
Advanced anti-spam intelligent rate limiting with ML detection

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import asyncio
import logging
import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import aiohttp

class RateLimitType(Enum):
    """Rate limit types"""
    USER = "user"
    EMAIL = "email"
    PHONE = "phone"
    IP = "ip"
    DEVICE = "device"
    GLOBAL = "global"
    CAMPAIGN = "campaign"

class ViolationSeverity(Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"

@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit_type: RateLimitType
    max_requests: int
    time_window: int  # seconds
    strategy: LimitStrategy
    burst_allowance: int = 0
    adaptive_factor: float = 1.0
    priority_boost: int = 0

@dataclass
class ViolationRecord:
    """Rate limit violation record"""
    id: str
    limit_type: RateLimitType
    identifier: str
    violation_count: int
    severity: ViolationSeverity
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class UsagePattern:
    """User usage pattern for ML analysis"""
    identifier: str
    request_count: int
    time_span: int
    peak_usage: int
    off_peak_usage: int
    variance: float
    anomaly_score: float
    is_suspicious: bool

class NotificationRateLimiter:
    """Enterprise notification rate limiter with ML-based fraud detection"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # Default rate limits
        self.default_limits = {
            RateLimitType.USER: RateLimit(
                limit_type=RateLimitType.USER,
                max_requests=1000,
                time_window=3600,  # 1 hour
                strategy=LimitStrategy.SLIDING_WINDOW,
                burst_allowance=50
            ),
            RateLimitType.EMAIL: RateLimit(
                limit_type=RateLimitType.EMAIL,
                max_requests=100,
                time_window=3600,
                strategy=LimitStrategy.TOKEN_BUCKET,
                burst_allowance=10
            ),
            RateLimitType.IP: RateLimit(
                limit_type=RateLimitType.IP,
                max_requests=500,
                time_window=3600,
                strategy=LimitStrategy.ADAPTIVE,
                burst_allowance=25
            ),
            RateLimitType.GLOBAL: RateLimit(
                limit_type=RateLimitType.GLOBAL,
                max_requests=100000,
                time_window=3600,
                strategy=LimitStrategy.SLIDING_WINDOW
            )
        }
        
        # ML models for anomaly detection
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Violation tracking
        self.violations: Dict[str, ViolationRecord] = {}
        self.suspicious_patterns: Set[str] = set()
        
        # Performance metrics
        self.metrics = {
            'requests_processed': 0,
            'requests_blocked': 0,
            'violations_detected': 0,
            'ml_detections': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    async def initialize(self):
        """Initialize rate limiter with Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("✅ Rate limiter initialized with Redis connection")
            
            # Load existing ML model if available
            await self._load_ml_model()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize rate limiter: {e}")
            raise

    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: RateLimitType,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limits
        
        Returns:
            Tuple[bool, Dict]: (is_allowed, limit_info)
        """
        try:
            self.metrics['requests_processed'] += 1
            
            # Get rate limit configuration
            rate_limit = self.default_limits.get(limit_type)
            if not rate_limit:
                return True, {'error': 'Invalid rate limit type'}
            
            # Check current usage
            current_usage = await self._get_current_usage(identifier, limit_type)
            
            # Apply rate limiting strategy
            is_allowed = await self._apply_rate_limiting_strategy(
                identifier, rate_limit, current_usage, request_metadata
            )
            
            # Update usage counters
            if is_allowed:
                await self._update_usage_counter(identifier, limit_type)
            else:
                self.metrics['requests_blocked'] += 1
                await self._record_violation(identifier, limit_type, request_metadata)
            
            # ML-based anomaly detection
            await self._analyze_usage_pattern(identifier, limit_type, request_metadata)
            
            # Prepare response
            limit_info = {
                'limit_type': limit_type.value,
                'max_requests': rate_limit.max_requests,
                'time_window': rate_limit.time_window,
                'current_usage': current_usage,
                'remaining': max(0, rate_limit.max_requests - current_usage),
                'reset_time': time.time() + rate_limit.time_window,
                'strategy': rate_limit.strategy.value
            }
            
            return is_allowed, limit_info
            
        except Exception as e:
            self.logger.error(f"❌ Rate limit check failed: {e}")
            # Fail open for availability
            return True, {'error': str(e)}

    async def _apply_rate_limiting_strategy(
        self,
        identifier: str,
        rate_limit: RateLimit,
        current_usage: int,
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """Apply specific rate limiting strategy"""
        
        if rate_limit.strategy == LimitStrategy.TOKEN_BUCKET:
            return await self._token_bucket_check(identifier, rate_limit)
            
        elif rate_limit.strategy == LimitStrategy.SLIDING_WINDOW:
            return await self._sliding_window_check(identifier, rate_limit)
            
        elif rate_limit.strategy == LimitStrategy.FIXED_WINDOW:
            return current_usage < rate_limit.max_requests
            
        elif rate_limit.strategy == LimitStrategy.ADAPTIVE:
            return await self._adaptive_rate_limit_check(
                identifier, rate_limit, current_usage, metadata
            )
        
        return current_usage < rate_limit.max_requests

    async def _token_bucket_check(self, identifier: str, rate_limit: RateLimit) -> bool:
        """Token bucket rate limiting implementation"""
        key = f"rate_limit:token_bucket:{identifier}:{rate_limit.limit_type.value}"
        
        # Get current bucket state
        bucket_data = await self.redis_client.get(key)
        
        if bucket_data:
            bucket = json.loads(bucket_data)
            last_refill = bucket['last_refill']
            tokens = bucket['tokens']
        else:
            last_refill = time.time()
            tokens = rate_limit.max_requests
        
        # Calculate tokens to add
        now = time.time()
        time_passed = now - last_refill
        tokens_to_add = (time_passed / rate_limit.time_window) * rate_limit.max_requests
        tokens = min(rate_limit.max_requests, tokens + tokens_to_add)
        
        # Check if request can be processed
        if tokens >= 1:
            tokens -= 1
            
            # Update bucket state
            bucket_state = {
                'tokens': tokens,
                'last_refill': now
            }
            await self.redis_client.setex(
                key, rate_limit.time_window, json.dumps(bucket_state)
            )
            return True
        
        return False

    async def _sliding_window_check(self, identifier: str, rate_limit: RateLimit) -> bool:
        """Sliding window rate limiting implementation"""
        key = f"rate_limit:sliding:{identifier}:{rate_limit.limit_type.value}"
        now = time.time()
        window_start = now - rate_limit.time_window
        
        # Remove expired entries and count current requests
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        current_count = await self.redis_client.zcard(key)
        
        if current_count < rate_limit.max_requests:
            # Add current request
            await self.redis_client.zadd(key, {str(uuid.uuid4()): now})
            await self.redis_client.expire(key, rate_limit.time_window)
            return True
        
        return False

    async def _adaptive_rate_limit_check(
        self,
        identifier: str,
        rate_limit: RateLimit,
        current_usage: int,
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """Adaptive rate limiting based on user behavior and system load"""
        
        # Base limit check
        if current_usage >= rate_limit.max_requests:
            return False
        
        # Adjust limit based on user reputation
        user_reputation = await self._get_user_reputation(identifier)
        adjusted_limit = int(rate_limit.max_requests * user_reputation)
        
        # Check for suspicious patterns
        if identifier in self.suspicious_patterns:
            adjusted_limit = int(adjusted_limit * 0.5)  # Reduce limit by 50%
        
        # Consider system load
        system_load = await self._get_system_load()
        if system_load > 0.8:  # High load
            adjusted_limit = int(adjusted_limit * 0.7)
        
        return current_usage < adjusted_limit

    async def _get_current_usage(self, identifier: str, limit_type: RateLimitType) -> int:
        """Get current usage count for identifier"""
        key = f"rate_limit:usage:{identifier}:{limit_type.value}"
        
        try:
            usage = await self.redis_client.get(key)
            self.metrics['cache_hits'] += 1
            return int(usage) if usage else 0
        except Exception:
            self.metrics['cache_misses'] += 1
            return 0

    async def _update_usage_counter(self, identifier: str, limit_type: RateLimitType):
        """Update usage counter in Redis"""
        key = f"rate_limit:usage:{identifier}:{limit_type.value}"
        rate_limit = self.default_limits[limit_type]
        
        # Increment counter with expiration
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, rate_limit.time_window)
        await pipe.execute()

    async def _record_violation(
        self,
        identifier: str,
        limit_type: RateLimitType,
        metadata: Optional[Dict[str, Any]]
    ):
        """Record rate limit violation"""
        violation_id = str(uuid.uuid4())
        
        # Determine severity based on violation frequency
        violation_count = await self._get_violation_count(identifier)
        severity = self._calculate_violation_severity(violation_count)
        
        violation = ViolationRecord(
            id=violation_id,
            limit_type=limit_type,
            identifier=identifier,
            violation_count=violation_count + 1,
            severity=severity,
            timestamp=datetime.utcnow(),
            ip_address=metadata.get('ip_address') if metadata else None,
            user_agent=metadata.get('user_agent') if metadata else None,
            metadata=metadata or {}
        )
        
        # Store violation
        key = f"rate_limit:violations:{identifier}"
        await self.redis_client.lpush(key, json.dumps(asdict(violation)))
        await self.redis_client.expire(key, 86400)  # 24 hours
        
        self.violations[violation_id] = violation
        self.metrics['violations_detected'] += 1
        
        self.logger.warning(
            f"⚠️ Rate limit violation: {identifier} - Type: {limit_type.value} - "
            f"Severity: {severity.value}"
        )

    async def _analyze_usage_pattern(
        self,
        identifier: str,
        limit_type: RateLimitType,
        metadata: Optional[Dict[str, Any]]
    ):
        """Analyze usage pattern for anomaly detection"""
        
        if not self.is_trained:
            return
        
        try:
            # Collect usage statistics
            usage_stats = await self._collect_usage_statistics(identifier, limit_type)
            
            if not usage_stats:
                return
            
            # Prepare features for ML model
            features = self._extract_usage_features(usage_stats, metadata)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict anomaly
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            if is_anomaly:
                self.suspicious_patterns.add(identifier)
                self.metrics['ml_detections'] += 1
                
                self.logger.warning(
                    f"🤖 ML anomaly detected: {identifier} - Score: {anomaly_score:.3f}"
                )
                
                # Record ML-based violation
                await self._record_ml_violation(identifier, anomaly_score, metadata)
        
        except Exception as e:
            self.logger.error(f"❌ ML analysis failed: {e}")

    def _extract_usage_features(
        self,
        usage_stats: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> List[float]:
        """Extract features for ML anomaly detection"""
        
        features = [
            usage_stats.get('request_count', 0),
            usage_stats.get('time_span', 0),
            usage_stats.get('peak_usage', 0),
            usage_stats.get('variance', 0),
            usage_stats.get('burst_factor', 0),
            usage_stats.get('frequency', 0),
            usage_stats.get('pattern_score', 0)
        ]
        
        # Add metadata features if available
        if metadata:
            features.extend([
                len(metadata.get('user_agent', '')),
                1 if metadata.get('is_mobile') else 0,
                metadata.get('request_size', 0),
                metadata.get('geographic_distance', 0)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        return features

    async def _collect_usage_statistics(
        self,
        identifier: str,
        limit_type: RateLimitType
    ) -> Optional[Dict[str, Any]]:
        """Collect usage statistics for analysis"""
        
        key = f"rate_limit:stats:{identifier}:{limit_type.value}"
        
        try:
            # Get recent usage data
            usage_data = await self.redis_client.lrange(key, 0, -1)
            
            if not usage_data:
                return None
            
            timestamps = [float(ts) for ts in usage_data]
            
            if len(timestamps) < 2:
                return None
            
            # Calculate statistics
            request_count = len(timestamps)
            time_span = max(timestamps) - min(timestamps)
            
            # Calculate peak and off-peak usage
            hourly_counts = {}
            for ts in timestamps:
                hour = int(ts // 3600)
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            peak_usage = max(hourly_counts.values()) if hourly_counts else 0
            variance = np.var(list(hourly_counts.values())) if hourly_counts else 0
            
            # Calculate burst factor
            intervals = np.diff(sorted(timestamps))
            burst_factor = len([i for i in intervals if i < 1]) / len(intervals) if intervals.size > 0 else 0
            
            return {
                'request_count': request_count,
                'time_span': time_span,
                'peak_usage': peak_usage,
                'variance': variance,
                'burst_factor': burst_factor,
                'frequency': request_count / max(time_span, 1),
                'pattern_score': self._calculate_pattern_score(timestamps)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect usage statistics: {e}")
            return None

    def _calculate_pattern_score(self, timestamps: List[float]) -> float:
        """Calculate pattern regularity score"""
        if len(timestamps) < 3:
            return 0.0
        
        intervals = np.diff(sorted(timestamps))
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Regular patterns have low standard deviation
        if mean_interval > 0:
            return std_interval / mean_interval
        return 1.0

    async def _get_user_reputation(self, identifier: str) -> float:
        """Get user reputation score (0.1 to 1.0)"""
        key = f"rate_limit:reputation:{identifier}"
        
        try:
            reputation = await self.redis_client.get(key)
            return float(reputation) if reputation else 1.0
        except Exception:
            return 1.0

    async def _get_system_load(self) -> float:
        """Get current system load (0.0 to 1.0)"""
        # This would typically integrate with monitoring systems
        # For now, return a simulated load based on request volume
        try:
            recent_requests = await self.redis_client.get("system:recent_requests")
            if recent_requests and int(recent_requests) > 10000:
                return 0.9
            elif recent_requests and int(recent_requests) > 5000:
                return 0.7
            return 0.3
        except Exception:
            return 0.5

    async def _get_violation_count(self, identifier: str) -> int:
        """Get violation count for identifier"""
        key = f"rate_limit:violations:{identifier}"
        return await self.redis_client.llen(key)

    def _calculate_violation_severity(self, violation_count: int) -> ViolationSeverity:
        """Calculate violation severity based on count"""
        if violation_count >= 20:
            return ViolationSeverity.CRITICAL
        elif violation_count >= 10:
            return ViolationSeverity.HIGH
        elif violation_count >= 5:
            return ViolationSeverity.MEDIUM
        return ViolationSeverity.LOW

    async def _record_ml_violation(
        self,
        identifier: str,
        anomaly_score: float,
        metadata: Optional[Dict[str, Any]]
    ):
        """Record ML-detected violation"""
        violation_id = str(uuid.uuid4())
        
        violation = ViolationRecord(
            id=violation_id,
            limit_type=RateLimitType.USER,  # Default for ML violations
            identifier=identifier,
            violation_count=1,
            severity=ViolationSeverity.HIGH,
            timestamp=datetime.utcnow(),
            metadata={
                'type': 'ml_anomaly',
                'anomaly_score': anomaly_score,
                'original_metadata': metadata or {}
            }
        )
        
        # Store ML violation
        key = f"rate_limit:ml_violations:{identifier}"
        await self.redis_client.lpush(key, json.dumps(asdict(violation)))
        await self.redis_client.expire(key, 86400)

    async def train_anomaly_detector(self, training_data: List[Dict[str, Any]]):
        """Train ML anomaly detector with historical data"""
        
        if not training_data:
            self.logger.warning("⚠️ No training data provided for anomaly detector")
            return
        
        try:
            # Extract features from training data
            features = []
            for data in training_data:
                feature_vector = self._extract_usage_features(
                    data.get('usage_stats', {}),
                    data.get('metadata', {})
                )
                features.append(feature_vector)
            
            # Scale features
            features_array = np.array(features)
            self.scaler.fit(features_array)
            features_scaled = self.scaler.transform(features_array)
            
            # Train anomaly detector
            self.anomaly_detector.fit(features_scaled)
            self.is_trained = True
            
            # Save model
            await self._save_ml_model()
            
            self.logger.info(f"✅ Anomaly detector trained with {len(training_data)} samples")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to train anomaly detector: {e}")

    async def _save_ml_model(self):
        """Save trained ML model to Redis"""
        try:
            model_data = {
                'anomaly_detector': pickle.dumps(self.anomaly_detector),
                'scaler': pickle.dumps(self.scaler),
                'is_trained': self.is_trained,
                'timestamp': time.time()
            }
            
            await self.redis_client.set(
                "rate_limit:ml_model",
                json.dumps({k: v.hex() if isinstance(v, bytes) else v for k, v in model_data.items()}),
                ex=86400 * 7  # 7 days
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save ML model: {e}")

    async def _load_ml_model(self):
        """Load trained ML model from Redis"""
        try:
            model_data = await self.redis_client.get("rate_limit:ml_model")
            
            if model_data:
                data = json.loads(model_data)
                
                self.anomaly_detector = pickle.loads(bytes.fromhex(data['anomaly_detector']))
                self.scaler = pickle.loads(bytes.fromhex(data['scaler']))
                self.is_trained = data['is_trained']
                
                self.logger.info("✅ ML model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load ML model: {e}")

    async def get_rate_limit_status(self, identifier: str) -> Dict[str, Any]:
        """Get comprehensive rate limit status for identifier"""
        
        status = {
            'identifier': identifier,
            'limits': {},
            'violations': [],
            'reputation': await self._get_user_reputation(identifier),
            'is_suspicious': identifier in self.suspicious_patterns,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get status for each limit type
        for limit_type in RateLimitType:
            if limit_type in self.default_limits:
                current_usage = await self._get_current_usage(identifier, limit_type)
                rate_limit = self.default_limits[limit_type]
                
                status['limits'][limit_type.value] = {
                    'current_usage': current_usage,
                    'max_requests': rate_limit.max_requests,
                    'remaining': max(0, rate_limit.max_requests - current_usage),
                    'reset_time': time.time() + rate_limit.time_window,
                    'strategy': rate_limit.strategy.value
                }
        
        # Get recent violations
        violations_key = f"rate_limit:violations:{identifier}"
        recent_violations = await self.redis_client.lrange(violations_key, 0, 9)
        
        for violation_data in recent_violations:
            try:
                violation = json.loads(violation_data)
                status['violations'].append(violation)
            except Exception:
                continue
        
        return status

    async def update_rate_limit(
        self,
        limit_type: RateLimitType,
        max_requests: int,
        time_window: int,
        strategy: LimitStrategy = LimitStrategy.SLIDING_WINDOW
    ):
        """Update rate limit configuration"""
        
        self.default_limits[limit_type] = RateLimit(
            limit_type=limit_type,
            max_requests=max_requests,
            time_window=time_window,
            strategy=strategy
        )
        
        self.logger.info(
            f"✅ Updated rate limit: {limit_type.value} - "
            f"{max_requests} requests per {time_window} seconds"
        )

    async def clear_rate_limit(self, identifier: str, limit_type: RateLimitType):
        """Clear rate limit for specific identifier"""
        key = f"rate_limit:usage:{identifier}:{limit_type.value}"
        await self.redis_client.delete(key)
        
        self.logger.info(f"✅ Cleared rate limit: {identifier} - {limit_type.value}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get rate limiter performance metrics"""
        
        # Calculate additional metrics
        total_requests = self.metrics['requests_processed']
        block_rate = (self.metrics['requests_blocked'] / total_requests * 100) if total_requests > 0 else 0
        cache_hit_rate = (self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100) if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        
        return {
            **self.metrics,
            'block_rate_percentage': round(block_rate, 2),
            'cache_hit_rate_percentage': round(cache_hit_rate, 2),
            'ml_detection_rate': round((self.metrics['ml_detections'] / total_requests * 100) if total_requests > 0 else 0, 2),
            'suspicious_identifiers': len(self.suspicious_patterns),
            'total_violations': len(self.violations),
            'is_ml_trained': self.is_trained
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("✅ Rate limiter cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_rate_limiter():
        """Test rate limiter functionality"""
        
        # Initialize rate limiter
        limiter = NotificationRateLimiter()
        await limiter.initialize()
        
        # Test normal usage
        for i in range(5):
            allowed, info = await limiter.check_rate_limit(
                "user123", RateLimitType.USER, {"ip_address": "192.168.1.1"}
            )
            print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} - {info}")
        
        # Test rate limit exceeding
        for i in range(1005):  # Exceed default limit
            allowed, info = await limiter.check_rate_limit("user456", RateLimitType.USER)
            if not allowed:
                print(f"Request {i+1}: Rate limit exceeded")
                break
        
        # Get status
        status = await limiter.get_rate_limit_status("user123")
        print(f"\nRate limit status: {json.dumps(status, indent=2)}")
        
        # Get metrics
        metrics = await limiter.get_metrics()
        print(f"\nMetrics: {json.dumps(metrics, indent=2)}")
        
        await limiter.cleanup()
    
    # Run test
    asyncio.run(test_rate_limiter())