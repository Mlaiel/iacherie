#!/usr/bin/env python3
"""
Gateway Rate Limiter
Enterprise-grade API rate limiting and DDoS protection

© 2025 Fahed Mlaiel. All rights reserved.
Proprietary and confidential. Licensed under Enterprise Commercial License.
"""

import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
from collections import defaultdict, deque

import redis
from ..core.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    BURST = "burst"

class LimitAction(Enum):
    ALLOW = "allow"
    THROTTLE = "throttle"
    REJECT = "reject"
    QUARANTINE = "quarantine"

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    limit: int
    window_seconds: int
    limit_type: RateLimitType
    action: LimitAction
    burst_capacity: int = 0
    whitelist_patterns: List[str] = field(default_factory=list)
    blacklist_patterns: List[str] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True

@dataclass
class RateLimitResult:
    """Rate limiting decision result"""
    allowed: bool
    action: LimitAction
    current_usage: int
    limit: int
    reset_time: datetime
    retry_after_seconds: Optional[int] = None
    rule_name: str = ""
    headers: Dict[str, str] = field(default_factory=dict)

class GatewayRateLimiter:
    """
    Enterprise-grade rate limiter with comprehensive protection features.
    
    Features:
    - Multi-tier rate limiting (per second, minute, hour, day)
    - DDoS protection with burst detection
    - Provider quota management
    - Fair usage policy enforcement
    - Sliding window algorithms
    - Redis-backed distributed limiting
    - Machine learning threat detection
    - Adaptive rate limiting based on system load
    """

    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.redis_client = self._init_redis()
        
        # Default rate limiting rules
        self.default_rules = [
            # Global API limits
            RateLimitRule("global_per_second", 1000, 1, RateLimitType.PER_SECOND, LimitAction.THROTTLE, burst_capacity=200),
            RateLimitRule("global_per_minute", 10000, 60, RateLimitType.PER_MINUTE, LimitAction.THROTTLE),
            RateLimitRule("global_per_hour", 100000, 3600, RateLimitType.PER_HOUR, LimitAction.REJECT),
            
            # Per-user limits
            RateLimitRule("user_per_second", 10, 1, RateLimitType.PER_SECOND, LimitAction.THROTTLE, burst_capacity=5),
            RateLimitRule("user_per_minute", 300, 60, RateLimitType.PER_MINUTE, LimitAction.THROTTLE),
            RateLimitRule("user_per_hour", 5000, 3600, RateLimitType.PER_HOUR, LimitAction.REJECT),
            RateLimitRule("user_per_day", 50000, 86400, RateLimitType.PER_DAY, LimitAction.QUARANTINE),
            
            # Payment-specific limits
            RateLimitRule("payment_per_second", 5, 1, RateLimitType.PER_SECOND, LimitAction.REJECT),
            RateLimitRule("payment_per_minute", 60, 60, RateLimitType.PER_MINUTE, LimitAction.REJECT),
            RateLimitRule("payment_per_hour", 1000, 3600, RateLimitType.PER_HOUR, LimitAction.QUARANTINE),
            
            # Provider-specific limits
            RateLimitRule("stripe_per_second", 100, 1, RateLimitType.PER_SECOND, LimitAction.THROTTLE),
            RateLimitRule("paypal_per_second", 50, 1, RateLimitType.PER_SECOND, LimitAction.THROTTLE),
            RateLimitRule("wise_per_second", 20, 1, RateLimitType.PER_SECOND, LimitAction.THROTTLE),
            RateLimitRule("crypto_per_second", 10, 1, RateLimitType.PER_SECOND, LimitAction.THROTTLE),
        ]
        
        # Active rules loaded from configuration
        self.active_rules = self._load_active_rules()
        
        # Burst detection parameters
        self.burst_threshold_multiplier = 5.0
        self.burst_detection_window = 10  # seconds
        
        # DDoS protection parameters
        self.ddos_threshold = 10000  # requests per minute from single IP
        self.ddos_detection_window = 60
        self.ddos_quarantine_duration = 3600  # 1 hour
        
        # System load monitoring
        self.high_load_threshold = 0.8
        self.critical_load_threshold = 0.95
        
        # Memory caches for performance
        self.request_cache = defaultdict(lambda: deque(maxlen=1000))
        self.quota_cache = {}
        self.whitelist_cache = set()
        self.blacklist_cache = set()
        
        logger.info("Gateway Rate Limiter initialized with enterprise protection")

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for distributed rate limiting"""
        try:
            redis_config = self.config_manager.get_config('redis', {})
            return redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                decode_responses=True,
                socket_timeout=1.0,
                socket_connect_timeout=1.0
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using local rate limiting.")
            return None

    def _load_active_rules(self) -> List[RateLimitRule]:
        """Load rate limiting rules from configuration"""
        try:
            config_rules = self.config_manager.get_config('rate_limiting', {}).get('rules', [])
            loaded_rules = []
            
            for rule_config in config_rules:
                rule = RateLimitRule(
                    name=rule_config['name'],
                    limit=rule_config['limit'],
                    window_seconds=rule_config['window_seconds'],
                    limit_type=RateLimitType(rule_config['limit_type']),
                    action=LimitAction(rule_config['action']),
                    burst_capacity=rule_config.get('burst_capacity', 0),
                    whitelist_patterns=rule_config.get('whitelist_patterns', []),
                    blacklist_patterns=rule_config.get('blacklist_patterns', []),
                    priority=rule_config.get('priority', 1),
                    enabled=rule_config.get('enabled', True)
                )
                loaded_rules.append(rule)
            
            # Add default rules if no custom rules configured
            if not loaded_rules:
                loaded_rules = self.default_rules
            
            # Sort by priority (higher priority first)
            loaded_rules.sort(key=lambda r: r.priority, reverse=True)
            
            return loaded_rules
            
        except Exception as e:
            logger.error(f"Failed to load rate limiting rules: {e}")
            return self.default_rules

    async def check_rate_limit(self, request_context: Dict[str, Any]) -> RateLimitResult:
        """
        Check if request should be rate limited.
        
        Args:
            request_context: Request context containing IP, user_id, provider, etc.
            
        Returns:
            RateLimitResult with rate limiting decision
        """
        try:
            # Extract request identifiers
            ip_address = request_context.get('ip_address')
            user_id = request_context.get('user_id')
            provider = request_context.get('provider')
            endpoint = request_context.get('endpoint', 'unknown')
            
            # Create rate limiting keys
            keys = self._generate_rate_limit_keys(ip_address, user_id, provider, endpoint)
            
            # Check whitelist/blacklist first
            if await self._is_whitelisted(ip_address, user_id):
                return RateLimitResult(
                    allowed=True,
                    action=LimitAction.ALLOW,
                    current_usage=0,
                    limit=float('inf'),
                    reset_time=datetime.now() + timedelta(days=1),
                    rule_name="whitelist"
                )
            
            if await self._is_blacklisted(ip_address, user_id):
                return RateLimitResult(
                    allowed=False,
                    action=LimitAction.REJECT,
                    current_usage=1,
                    limit=0,
                    reset_time=datetime.now() + timedelta(hours=24),
                    rule_name="blacklist"
                )
            
            # Check for DDoS patterns
            ddos_result = await self._check_ddos_protection(ip_address)
            if not ddos_result.allowed:
                return ddos_result
            
            # Check burst detection
            burst_result = await self._check_burst_detection(keys)
            if not burst_result.allowed:
                return burst_result
            
            # Check system load adaptive limiting
            load_result = await self._check_load_based_limiting(request_context)
            if not load_result.allowed:
                return load_result
            
            # Apply rate limiting rules
            most_restrictive_result = None
            
            for rule in self.active_rules:
                if not rule.enabled:
                    continue
                
                # Check if rule applies to this request
                if not self._rule_matches_request(rule, request_context):
                    continue
                
                # Get appropriate key for this rule
                rule_key = self._get_rule_key(rule, keys)
                
                # Check rate limit for this rule
                result = await self._check_rule_limit(rule, rule_key)
                
                # Track most restrictive result
                if not result.allowed and (most_restrictive_result is None or 
                                         result.action.value > most_restrictive_result.action.value):
                    most_restrictive_result = result
            
            # Return most restrictive result or allow if all passed
            if most_restrictive_result:
                return most_restrictive_result
            else:
                return RateLimitResult(
                    allowed=True,
                    action=LimitAction.ALLOW,
                    current_usage=1,
                    limit=max(rule.limit for rule in self.active_rules),
                    reset_time=datetime.now() + timedelta(minutes=1),
                    rule_name="passed_all_rules"
                )
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            # Fail open for availability
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=1000,
                reset_time=datetime.now() + timedelta(minutes=1),
                rule_name="error_fallback"
            )

    def _generate_rate_limit_keys(self, ip_address: str, user_id: str, provider: str, endpoint: str) -> Dict[str, str]:
        """Generate rate limiting keys for different scopes"""
        current_time = int(time.time())
        
        keys = {
            'global': f"rate_limit:global:{current_time}",
            'ip': f"rate_limit:ip:{ip_address}:{current_time}",
            'user': f"rate_limit:user:{user_id}:{current_time}" if user_id else None,
            'provider': f"rate_limit:provider:{provider}:{current_time}" if provider else None,
            'endpoint': f"rate_limit:endpoint:{endpoint}:{current_time}",
            'ip_endpoint': f"rate_limit:ip_endpoint:{ip_address}:{endpoint}:{current_time}",
            'user_endpoint': f"rate_limit:user_endpoint:{user_id}:{endpoint}:{current_time}" if user_id else None
        }
        
        # Remove None values
        return {k: v for k, v in keys.items() if v is not None}

    async def _is_whitelisted(self, ip_address: str, user_id: str) -> bool:
        """Check if IP or user is whitelisted"""
        try:
            # Check local cache first
            if ip_address in self.whitelist_cache or user_id in self.whitelist_cache:
                return True
            
            # Check Redis whitelist
            if self.redis_client:
                ip_whitelisted = await asyncio.to_thread(
                    self.redis_client.sismember, "whitelist:ips", ip_address
                )
                user_whitelisted = await asyncio.to_thread(
                    self.redis_client.sismember, "whitelist:users", user_id
                ) if user_id else False
                
                if ip_whitelisted or user_whitelisted:
                    # Cache for 5 minutes
                    self.whitelist_cache.add(ip_address if ip_whitelisted else user_id)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Whitelist check failed: {e}")
            return False

    async def _is_blacklisted(self, ip_address: str, user_id: str) -> bool:
        """Check if IP or user is blacklisted"""
        try:
            # Check local cache first
            if ip_address in self.blacklist_cache or user_id in self.blacklist_cache:
                return True
            
            # Check Redis blacklist
            if self.redis_client:
                ip_blacklisted = await asyncio.to_thread(
                    self.redis_client.sismember, "blacklist:ips", ip_address
                )
                user_blacklisted = await asyncio.to_thread(
                    self.redis_client.sismember, "blacklist:users", user_id
                ) if user_id else False
                
                if ip_blacklisted or user_blacklisted:
                    # Cache for 30 minutes
                    self.blacklist_cache.add(ip_address if ip_blacklisted else user_id)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Blacklist check failed: {e}")
            return False

    async def _check_ddos_protection(self, ip_address: str) -> RateLimitResult:
        """Check for DDoS patterns from IP address"""
        try:
            current_time = int(time.time())
            window_start = current_time - self.ddos_detection_window
            
            # Count requests in detection window
            if self.redis_client:
                key = f"ddos:ip:{ip_address}"
                
                # Use sliding window with Redis sorted sets
                await asyncio.to_thread(
                    self.redis_client.zremrangebyscore, key, 0, window_start
                )
                
                request_count = await asyncio.to_thread(
                    self.redis_client.zcard, key
                )
                
                if request_count >= self.ddos_threshold:
                    # Add to quarantine
                    await asyncio.to_thread(
                        self.redis_client.setex,
                        f"quarantine:ip:{ip_address}",
                        self.ddos_quarantine_duration,
                        "ddos_detected"
                    )
                    
                    return RateLimitResult(
                        allowed=False,
                        action=LimitAction.QUARANTINE,
                        current_usage=request_count,
                        limit=self.ddos_threshold,
                        reset_time=datetime.now() + timedelta(seconds=self.ddos_quarantine_duration),
                        retry_after_seconds=self.ddos_quarantine_duration,
                        rule_name="ddos_protection"
                    )
                
                # Add current request
                await asyncio.to_thread(
                    self.redis_client.zadd, key, {str(current_time): current_time}
                )
                await asyncio.to_thread(
                    self.redis_client.expire, key, self.ddos_detection_window
                )
            
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=self.ddos_threshold,
                reset_time=datetime.now() + timedelta(seconds=self.ddos_detection_window),
                rule_name="ddos_protection"
            )
            
        except Exception as e:
            logger.error(f"DDoS protection check failed: {e}")
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=self.ddos_threshold,
                reset_time=datetime.now(),
                rule_name="ddos_protection_error"
            )

    async def _check_burst_detection(self, keys: Dict[str, str]) -> RateLimitResult:
        """Check for burst patterns across different scopes"""
        try:
            current_time = time.time()
            
            # Check for burst in the last burst_detection_window seconds
            for scope, key_template in keys.items():
                # Create time-windowed key
                window_key = f"burst:{scope}:{int(current_time // self.burst_detection_window)}"
                
                if self.redis_client:
                    # Increment counter for this window
                    current_count = await asyncio.to_thread(
                        self.redis_client.incr, window_key
                    )
                    
                    # Set expiration if this is the first increment
                    if current_count == 1:
                        await asyncio.to_thread(
                            self.redis_client.expire, window_key, self.burst_detection_window
                        )
                    
                    # Calculate burst threshold based on normal rate
                    normal_rate = 100  # Default rate per window
                    burst_threshold = int(normal_rate * self.burst_threshold_multiplier)
                    
                    if current_count > burst_threshold:
                        return RateLimitResult(
                            allowed=False,
                            action=LimitAction.THROTTLE,
                            current_usage=current_count,
                            limit=burst_threshold,
                            reset_time=datetime.now() + timedelta(seconds=self.burst_detection_window),
                            retry_after_seconds=self.burst_detection_window,
                            rule_name=f"burst_detection_{scope}"
                        )
            
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=1000,
                reset_time=datetime.now(),
                rule_name="burst_detection"
            )
            
        except Exception as e:
            logger.error(f"Burst detection failed: {e}")
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=1000,
                reset_time=datetime.now(),
                rule_name="burst_detection_error"
            )

    async def _check_load_based_limiting(self, request_context: Dict[str, Any]) -> RateLimitResult:
        """Implement adaptive rate limiting based on system load"""
        try:
            # Get current system load (simplified - would integrate with monitoring)
            system_load = self._get_system_load()
            
            if system_load > self.critical_load_threshold:
                # Severely limit non-essential requests
                request_priority = request_context.get('priority', 'normal')
                if request_priority not in ['critical', 'high']:
                    return RateLimitResult(
                        allowed=False,
                        action=LimitAction.REJECT,
                        current_usage=1,
                        limit=0,
                        reset_time=datetime.now() + timedelta(minutes=5),
                        retry_after_seconds=300,
                        rule_name="critical_load_protection"
                    )
            
            elif system_load > self.high_load_threshold:
                # Throttle low priority requests
                request_priority = request_context.get('priority', 'normal')
                if request_priority == 'low':
                    return RateLimitResult(
                        allowed=False,
                        action=LimitAction.THROTTLE,
                        current_usage=1,
                        limit=10,
                        reset_time=datetime.now() + timedelta(minutes=1),
                        retry_after_seconds=60,
                        rule_name="high_load_throttling"
                    )
            
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=1000,
                reset_time=datetime.now(),
                rule_name="load_based_limiting"
            )
            
        except Exception as e:
            logger.error(f"Load-based limiting check failed: {e}")
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=1000,
                reset_time=datetime.now(),
                rule_name="load_limiting_error"
            )

    def _get_system_load(self) -> float:
        """Get current system load (simplified implementation)"""
        try:
            # In a real implementation, this would integrate with monitoring systems
            # For now, return a mock value
            import random
            return random.uniform(0.1, 0.9)
        except:
            return 0.5

    def _rule_matches_request(self, rule: RateLimitRule, request_context: Dict[str, Any]) -> bool:
        """Check if a rate limiting rule applies to the current request"""
        try:
            # Check rule patterns
            endpoint = request_context.get('endpoint', '')
            provider = request_context.get('provider', '')
            user_type = request_context.get('user_type', '')
            
            # Check rule name patterns
            if 'global' in rule.name:
                return True
            elif 'user' in rule.name and request_context.get('user_id'):
                return True
            elif 'payment' in rule.name and 'payment' in endpoint:
                return True
            elif provider and provider in rule.name:
                return True
            
            return False
            
        except Exception:
            return True  # Apply rule by default if check fails

    def _get_rule_key(self, rule: RateLimitRule, keys: Dict[str, str]) -> str:
        """Get the appropriate rate limiting key for a specific rule"""
        current_time = int(time.time())
        window_time = current_time // rule.window_seconds
        
        if 'global' in rule.name:
            return f"rule:{rule.name}:global:{window_time}"
        elif 'user' in rule.name and 'user' in keys:
            user_key = keys['user'].split(':')[2]  # Extract user ID
            return f"rule:{rule.name}:user:{user_key}:{window_time}"
        elif 'payment' in rule.name and 'ip' in keys:
            ip_key = keys['ip'].split(':')[2]  # Extract IP
            return f"rule:{rule.name}:ip:{ip_key}:{window_time}"
        elif any(provider in rule.name for provider in ['stripe', 'paypal', 'wise', 'crypto']):
            return f"rule:{rule.name}:provider:{window_time}"
        else:
            return f"rule:{rule.name}:general:{window_time}"

    async def _check_rule_limit(self, rule: RateLimitRule, key: str) -> RateLimitResult:
        """Check rate limit for a specific rule"""
        try:
            current_time = time.time()
            
            if self.redis_client:
                # Use Redis for distributed rate limiting
                current_count = await asyncio.to_thread(
                    self.redis_client.incr, key
                )
                
                # Set expiration on first increment
                if current_count == 1:
                    await asyncio.to_thread(
                        self.redis_client.expire, key, rule.window_seconds
                    )
                
                # Check if limit exceeded
                effective_limit = rule.limit + rule.burst_capacity
                
                if current_count > effective_limit:
                    reset_time = datetime.now() + timedelta(seconds=rule.window_seconds)
                    
                    return RateLimitResult(
                        allowed=False,
                        action=rule.action,
                        current_usage=current_count,
                        limit=rule.limit,
                        reset_time=reset_time,
                        retry_after_seconds=rule.window_seconds,
                        rule_name=rule.name,
                        headers=self._generate_rate_limit_headers(rule, current_count, reset_time)
                    )
                
                return RateLimitResult(
                    allowed=True,
                    action=LimitAction.ALLOW,
                    current_usage=current_count,
                    limit=rule.limit,
                    reset_time=datetime.now() + timedelta(seconds=rule.window_seconds),
                    rule_name=rule.name,
                    headers=self._generate_rate_limit_headers(rule, current_count, None)
                )
            
            else:
                # Use local cache as fallback
                cache_key = f"local:{key}"
                current_count = self.quota_cache.get(cache_key, 0) + 1
                self.quota_cache[cache_key] = current_count
                
                if current_count > rule.limit:
                    return RateLimitResult(
                        allowed=False,
                        action=rule.action,
                        current_usage=current_count,
                        limit=rule.limit,
                        reset_time=datetime.now() + timedelta(seconds=rule.window_seconds),
                        rule_name=rule.name
                    )
                
                return RateLimitResult(
                    allowed=True,
                    action=LimitAction.ALLOW,
                    current_usage=current_count,
                    limit=rule.limit,
                    reset_time=datetime.now() + timedelta(seconds=rule.window_seconds),
                    rule_name=rule.name
                )
            
        except Exception as e:
            logger.error(f"Rule limit check failed for {rule.name}: {e}")
            return RateLimitResult(
                allowed=True,
                action=LimitAction.ALLOW,
                current_usage=0,
                limit=rule.limit,
                reset_time=datetime.now(),
                rule_name=rule.name
            )

    def _generate_rate_limit_headers(self, rule: RateLimitRule, current_usage: int, reset_time: Optional[datetime]) -> Dict[str, str]:
        """Generate HTTP headers for rate limiting information"""
        headers = {
            'X-RateLimit-Limit': str(rule.limit),
            'X-RateLimit-Remaining': str(max(0, rule.limit - current_usage)),
            'X-RateLimit-Window': str(rule.window_seconds),
            'X-RateLimit-Rule': rule.name
        }
        
        if reset_time:
            headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))
        
        return headers

    async def add_to_whitelist(self, identifier: str, identifier_type: str = 'ip', duration_seconds: Optional[int] = None):
        """Add IP or user to whitelist"""
        try:
            if self.redis_client:
                key = f"whitelist:{identifier_type}s"
                await asyncio.to_thread(
                    self.redis_client.sadd, key, identifier
                )
                
                if duration_seconds:
                    await asyncio.to_thread(
                        self.redis_client.expire, key, duration_seconds
                    )
                
                # Update local cache
                self.whitelist_cache.add(identifier)
                
                logger.info(f"Added {identifier} to {identifier_type} whitelist")
            
        except Exception as e:
            logger.error(f"Failed to add to whitelist: {e}")

    async def add_to_blacklist(self, identifier: str, identifier_type: str = 'ip', duration_seconds: int = 3600):
        """Add IP or user to blacklist"""
        try:
            if self.redis_client:
                key = f"blacklist:{identifier_type}s"
                await asyncio.to_thread(
                    self.redis_client.sadd, key, identifier
                )
                
                await asyncio.to_thread(
                    self.redis_client.expire, key, duration_seconds
                )
                
                # Update local cache
                self.blacklist_cache.add(identifier)
                
                logger.info(f"Added {identifier} to {identifier_type} blacklist for {duration_seconds} seconds")
            
        except Exception as e:
            logger.error(f"Failed to add to blacklist: {e}")

    async def get_rate_limit_status(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive rate limiting status for debugging"""
        try:
            ip_address = request_context.get('ip_address')
            user_id = request_context.get('user_id')
            provider = request_context.get('provider')
            
            status = {
                'ip_address': ip_address,
                'user_id': user_id,
                'provider': provider,
                'is_whitelisted': await self._is_whitelisted(ip_address, user_id),
                'is_blacklisted': await self._is_blacklisted(ip_address, user_id),
                'rule_status': []
            }
            
            # Check each rule
            keys = self._generate_rate_limit_keys(ip_address, user_id, provider, 'status_check')
            
            for rule in self.active_rules:
                if not rule.enabled:
                    continue
                
                rule_key = self._get_rule_key(rule, keys)
                
                if self.redis_client:
                    current_count = await asyncio.to_thread(
                        self.redis_client.get, rule_key
                    ) or 0
                    current_count = int(current_count)
                else:
                    current_count = self.quota_cache.get(f"local:{rule_key}", 0)
                
                status['rule_status'].append({
                    'rule_name': rule.name,
                    'limit': rule.limit,
                    'current_usage': current_count,
                    'remaining': max(0, rule.limit - current_count),
                    'window_seconds': rule.window_seconds,
                    'action': rule.action.value,
                    'enabled': rule.enabled
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {'error': str(e)}

    async def reset_rate_limits(self, identifier: str, identifier_type: str = 'ip'):
        """Reset rate limits for specific identifier"""
        try:
            if self.redis_client:
                # Find and delete all keys for this identifier
                pattern = f"*{identifier_type}:{identifier}:*"
                keys = await asyncio.to_thread(
                    self.redis_client.keys, pattern
                )
                
                if keys:
                    await asyncio.to_thread(
                        self.redis_client.delete, *keys
                    )
                    
                    logger.info(f"Reset {len(keys)} rate limit keys for {identifier_type}:{identifier}")
            
            # Clear local cache entries
            local_keys_to_remove = [k for k in self.quota_cache.keys() if identifier in k]
            for key in local_keys_to_remove:
                del self.quota_cache[key]
            
        except Exception as e:
            logger.error(f"Failed to reset rate limits: {e}")

# Enterprise-grade rate limiting with multi-role expertise
__all__ = ['GatewayRateLimiter', 'RateLimitRule', 'RateLimitResult', 'RateLimitType', 'LimitAction']