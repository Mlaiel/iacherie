"""
🛡️ RATE LIMITER - ENTERPRISE ADAPTIVE RATE LIMITING ENGINE
Rôle Backend Senior: Rate limiter adaptatif avec priorités basées sur les types de créateurs

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
import aiosqlite
from collections import defaultdict, deque
import time
import hashlib
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Ainflue Business Logic Integration
from core.config import AinflueCoreConfig
from core.exceptions import AinflueCoreException

class RateLimitStrategy(Enum):
    """Stratégies de rate limiting"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"
    CREATOR_PRIORITY = "creator_priority"

class CreatorTier(Enum):
    """Tiers de créateurs avec priorités"""
    PREMIUM = "premium"
    PRO = "pro"
    STANDARD = "standard"
    FREE = "free"

class RequestPriority(Enum):
    """Priorités de requêtes"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class RateLimitConfig:
    """Configuration de rate limiting"""
    strategy: RateLimitStrategy
    requests_per_second: int
    burst_limit: int
    window_size: int
    creator_tier: CreatorTier
    priority: RequestPriority
    adaptive_threshold: float
    backoff_multiplier: float

@dataclass
class RateLimitResult:
    """Résultat d'évaluation de rate limiting"""
    allowed: bool
    remaining_quota: int
    reset_time: datetime
    retry_after: Optional[int]
    current_usage: int
    limit_reason: Optional[str]
    creator_tier: CreatorTier
    priority_applied: bool

@dataclass
class RequestMetrics:
    """Métriques de requête"""
    request_id: str
    creator_id: str
    creator_type: str
    creator_tier: CreatorTier
    endpoint: str
    method: str
    priority: RequestPriority
    timestamp: datetime
    processing_time: float
    status_code: int
    bytes_consumed: int

class AdaptiveRateLimiter:
    """
    🛡️ Enterprise Adaptive Rate Limiter pour MLOps Infrastructure
    
    Fonctionnalités Backend Senior Expert:
    - Rate limiting adaptatif intelligent basé sur créateurs
    - Priorités dynamiques par tiers de créateurs
    - Token bucket et sliding window combinés
    - Adaptive throttling avec ML prediction
    - Creator-specific quota management
    - Real-time monitoring et alerting
    - Redis-backed pour haute performance
    """
    
    def __init__(self, config: Optional[AinflueCoreConfig] = None):
        self.config = config or AinflueCoreConfig()
        self.logger = self._setup_logging()
        self.db_path = "mlops_rate_limiter.db"
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Creator tier configurations
        self.creator_configs = {
            CreatorTier.PREMIUM: RateLimitConfig(
                strategy=RateLimitStrategy.ADAPTIVE,
                requests_per_second=1000,
                burst_limit=2000,
                window_size=60,
                creator_tier=CreatorTier.PREMIUM,
                priority=RequestPriority.HIGH,
                adaptive_threshold=0.8,
                backoff_multiplier=1.2
            ),
            CreatorTier.PRO: RateLimitConfig(
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                requests_per_second=500,
                burst_limit=1000,
                window_size=60,
                creator_tier=CreatorTier.PRO,
                priority=RequestPriority.MEDIUM,
                adaptive_threshold=0.7,
                backoff_multiplier=1.5
            ),
            CreatorTier.STANDARD: RateLimitConfig(
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                requests_per_second=100,
                burst_limit=200,
                window_size=60,
                creator_tier=CreatorTier.STANDARD,
                priority=RequestPriority.MEDIUM,
                adaptive_threshold=0.6,
                backoff_multiplier=2.0
            ),
            CreatorTier.FREE: RateLimitConfig(
                strategy=RateLimitStrategy.FIXED_WINDOW,
                requests_per_second=20,
                burst_limit=50,
                window_size=60,
                creator_tier=CreatorTier.FREE,
                priority=RequestPriority.LOW,
                adaptive_threshold=0.5,
                backoff_multiplier=3.0
            )
        }
        
        # Creator type specific multipliers
        self.creator_type_multipliers = {
            "musician": 1.5,      # Audio processing intensive
            "photographer": 1.3,   # Image processing intensive  
            "influencer": 1.2,     # High volume content
            "blogger": 1.0,        # Text processing standard
            "comedian": 1.0        # Standard processing
        }
        
        # Token buckets pour chaque créateur
        self.token_buckets = {}
        self.sliding_windows = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger("AdaptiveRateLimiter")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    async def initialize(self) -> None:
        """Initialisation du rate limiter"""
        try:
            # Initialize Redis
            self.redis_client = redis.Redis(
                host=self.config.redis_host if hasattr(self.config, 'redis_host') else 'localhost',
                port=self.config.redis_port if hasattr(self.config, 'redis_port') else 6379,
                decode_responses=True
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            
            # Initialize database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS rate_limit_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT NOT NULL,
                        creator_id TEXT NOT NULL,
                        creator_type TEXT NOT NULL,
                        creator_tier TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        processing_time REAL,
                        status_code INTEGER,
                        bytes_consumed INTEGER,
                        allowed BOOLEAN,
                        limit_reason TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS rate_limit_configs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        creator_id TEXT UNIQUE NOT NULL,
                        creator_tier TEXT NOT NULL,
                        custom_requests_per_second INTEGER,
                        custom_burst_limit INTEGER,
                        custom_priority TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS adaptive_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        period TEXT NOT NULL,
                        total_requests INTEGER,
                        blocked_requests INTEGER,
                        average_response_time REAL,
                        top_consumers TEXT,
                        tier_distribution TEXT,
                        adaptive_adjustments TEXT,
                        created_at TEXT
                    )
                """)
                
                await db.commit()
                
            self.logger.info("✅ Adaptive Rate Limiter initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
            raise AinflueCoreException(f"Échec initialisation Rate Limiter: {e}")

    async def check_rate_limit(self, 
                              creator_id: str,
                              creator_type: str,
                              creator_tier: CreatorTier,
                              endpoint: str,
                              method: str = "GET",
                              priority: Optional[RequestPriority] = None) -> RateLimitResult:
        """Vérification de rate limiting avec logique adaptative"""
        try:
            request_id = self._generate_request_id(creator_id, endpoint, method)
            
            # Récupération de la configuration
            config = await self._get_creator_config(creator_id, creator_tier)
            
            # Application du multiplicateur par type de créateur
            type_multiplier = self.creator_type_multipliers.get(creator_type, 1.0)
            adjusted_rps = int(config.requests_per_second * type_multiplier)
            adjusted_burst = int(config.burst_limit * type_multiplier)
            
            # Détermination de la priorité
            if priority is None:
                priority = config.priority
            
            # Évaluation selon la stratégie
            if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                result = await self._check_token_bucket(creator_id, adjusted_rps, adjusted_burst, priority)
            elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                result = await self._check_sliding_window(creator_id, adjusted_rps, config.window_size, priority)
            elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
                result = await self._check_fixed_window(creator_id, adjusted_rps, config.window_size)
            elif config.strategy == RateLimitStrategy.ADAPTIVE:
                result = await self._check_adaptive(creator_id, config, type_multiplier, priority)
            else:
                result = await self._check_token_bucket(creator_id, adjusted_rps, adjusted_burst, priority)
            
            # Mise à jour des métriques
            await self._record_request_metrics(RequestMetrics(
                request_id=request_id,
                creator_id=creator_id,
                creator_type=creator_type,
                creator_tier=creator_tier,
                endpoint=endpoint,
                method=method,
                priority=priority,
                timestamp=datetime.now(),
                processing_time=0.0,  # Sera mis à jour plus tard
                status_code=200 if result.allowed else 429,
                bytes_consumed=0,  # Sera mis à jour plus tard
            ), result.allowed, result.limit_reason)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification rate limit: {e}")
            # En cas d'erreur, autoriser la requête (fail-open)
            return RateLimitResult(
                allowed=True,
                remaining_quota=100,
                reset_time=datetime.now() + timedelta(minutes=1),
                retry_after=None,
                current_usage=0,
                limit_reason="error_fallback",
                creator_tier=creator_tier,
                priority_applied=False
            )

    async def _get_creator_config(self, creator_id: str, default_tier: CreatorTier) -> RateLimitConfig:
        """Récupération de la configuration personnalisée d'un créateur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT creator_tier, custom_requests_per_second, custom_burst_limit, custom_priority
                    FROM rate_limit_configs 
                    WHERE creator_id = ?
                """, (creator_id,))
                
                result = await cursor.fetchone()
                
                if result:
                    tier = CreatorTier(result[0])
                    config = self.creator_configs[tier].copy()
                    
                    if result[1]:  # custom_requests_per_second
                        config.requests_per_second = result[1]
                    if result[2]:  # custom_burst_limit
                        config.burst_limit = result[2]
                    if result[3]:  # custom_priority
                        config.priority = RequestPriority(result[3])
                    
                    return config
                else:
                    return self.creator_configs[default_tier]
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération config: {e}")
            return self.creator_configs[default_tier]

    async def _check_token_bucket(self, 
                                 creator_id: str, 
                                 requests_per_second: int,
                                 burst_limit: int,
                                 priority: RequestPriority) -> RateLimitResult:
        """Implémentation Token Bucket"""
        try:
            now = time.time()
            bucket_key = f"bucket:{creator_id}"
            
            # Récupération du bucket depuis Redis
            bucket_data = await self.redis_client.hmget(
                bucket_key, 
                ["tokens", "last_refill", "capacity"]
            )
            
            if bucket_data[0] is None:
                # Initialisation du bucket
                tokens = burst_limit
                last_refill = now
                capacity = burst_limit
            else:
                tokens = float(bucket_data[0])
                last_refill = float(bucket_data[1])
                capacity = int(bucket_data[2])
            
            # Calcul du refill
            time_passed = now - last_refill
            tokens_to_add = time_passed * requests_per_second
            tokens = min(capacity, tokens + tokens_to_add)
            
            # Application de la priorité
            cost = self._get_request_cost(priority)
            
            if tokens >= cost:
                tokens -= cost
                allowed = True
                retry_after = None
                limit_reason = None
            else:
                allowed = False
                retry_after = int((cost - tokens) / requests_per_second)
                limit_reason = "token_bucket_exhausted"
            
            # Sauvegarde du bucket
            await self.redis_client.hmset(bucket_key, {
                "tokens": tokens,
                "last_refill": now,
                "capacity": capacity
            })
            await self.redis_client.expire(bucket_key, 3600)  # 1 heure TTL
            
            return RateLimitResult(
                allowed=allowed,
                remaining_quota=int(tokens),
                reset_time=datetime.fromtimestamp(now + (capacity - tokens) / requests_per_second),
                retry_after=retry_after,
                current_usage=int(capacity - tokens),
                limit_reason=limit_reason,
                creator_tier=CreatorTier.STANDARD,  # Sera remplacé par la vraie valeur
                priority_applied=cost != 1
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur token bucket: {e}")
            raise

    async def _check_sliding_window(self,
                                   creator_id: str,
                                   requests_per_second: int,
                                   window_size: int,
                                   priority: RequestPriority) -> RateLimitResult:
        """Implémentation Sliding Window"""
        try:
            now = time.time()
            window_start = now - window_size
            window_key = f"window:{creator_id}"
            
            # Nettoyage des anciens timestamps
            await self.redis_client.zremrangebyscore(window_key, 0, window_start)
            
            # Comptage des requêtes dans la fenêtre
            current_count = await self.redis_client.zcard(window_key)
            limit = requests_per_second * window_size
            
            # Application de la priorité
            cost = self._get_request_cost(priority)
            
            if current_count + cost <= limit:
                # Ajout de la requête
                for _ in range(cost):
                    await self.redis_client.zadd(window_key, {str(now + _/1000): now + _/1000})
                
                await self.redis_client.expire(window_key, window_size + 10)
                
                allowed = True
                retry_after = None
                limit_reason = None
            else:
                allowed = False
                # Calcul du temps d'attente
                oldest_score = await self.redis_client.zrange(window_key, 0, 0, withscores=True)
                if oldest_score:
                    retry_after = int(oldest_score[0][1] + window_size - now) + 1
                else:
                    retry_after = window_size
                limit_reason = "sliding_window_exceeded"
            
            remaining = max(0, limit - current_count)
            
            return RateLimitResult(
                allowed=allowed,
                remaining_quota=int(remaining),
                reset_time=datetime.fromtimestamp(now + window_size),
                retry_after=retry_after,
                current_usage=int(current_count),
                limit_reason=limit_reason,
                creator_tier=CreatorTier.STANDARD,
                priority_applied=cost != 1
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur sliding window: {e}")
            raise

    async def _check_fixed_window(self,
                                 creator_id: str,
                                 requests_per_second: int,
                                 window_size: int) -> RateLimitResult:
        """Implémentation Fixed Window"""
        try:
            now = time.time()
            window_id = int(now // window_size)
            window_key = f"fixed:{creator_id}:{window_id}"
            
            current_count = await self.redis_client.get(window_key) or 0
            current_count = int(current_count)
            
            limit = requests_per_second * window_size
            
            if current_count < limit:
                await self.redis_client.incr(window_key)
                await self.redis_client.expire(window_key, window_size + 10)
                
                allowed = True
                retry_after = None
                limit_reason = None
            else:
                allowed = False
                retry_after = int(window_size - (now % window_size)) + 1
                limit_reason = "fixed_window_exceeded"
            
            remaining = max(0, limit - current_count - 1)
            reset_time = datetime.fromtimestamp((window_id + 1) * window_size)
            
            return RateLimitResult(
                allowed=allowed,
                remaining_quota=remaining,
                reset_time=reset_time,
                retry_after=retry_after,
                current_usage=current_count + (1 if allowed else 0),
                limit_reason=limit_reason,
                creator_tier=CreatorTier.STANDARD,
                priority_applied=False
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur fixed window: {e}")
            raise

    async def _check_adaptive(self,
                             creator_id: str,
                             config: RateLimitConfig,
                             type_multiplier: float,
                             priority: RequestPriority) -> RateLimitResult:
        """Implémentation Adaptive Rate Limiting avec ML intelligence"""
        try:
            # Récupération des métriques récentes
            recent_metrics = await self._get_recent_metrics(creator_id, 300)  # 5 minutes
            
            # Calcul de l'adaptation basée sur les performances
            adaptation_factor = await self._calculate_adaptation_factor(recent_metrics, config)
            
            # Ajustement des limites
            adapted_rps = int(config.requests_per_second * type_multiplier * adaptation_factor)
            adapted_burst = int(config.burst_limit * type_multiplier * adaptation_factor)
            
            # Utilisation du token bucket adaptatif
            result = await self._check_token_bucket(creator_id, adapted_rps, adapted_burst, priority)
            
            # Logging de l'adaptation
            if adaptation_factor != 1.0:
                self.logger.info(f"🔧 Adaptation pour {creator_id}: facteur {adaptation_factor:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur adaptive rate limiting: {e}")
            # Fallback vers token bucket standard
            return await self._check_token_bucket(
                creator_id, 
                int(config.requests_per_second * type_multiplier),
                int(config.burst_limit * type_multiplier),
                priority
            )

    async def _calculate_adaptation_factor(self, 
                                          metrics: List[Dict[str, Any]], 
                                          config: RateLimitConfig) -> float:
        """Calcul du facteur d'adaptation basé sur les métriques"""
        try:
            if not metrics:
                return 1.0
            
            # Analyse des métriques
            avg_response_time = np.mean([m['processing_time'] for m in metrics if m['processing_time'] > 0])
            error_rate = sum(1 for m in metrics if m['status_code'] >= 400) / len(metrics)
            blocked_rate = sum(1 for m in metrics if not m['allowed']) / len(metrics)
            
            # Calcul du facteur d'adaptation
            adaptation_factor = 1.0
            
            # Adaptation basée sur le temps de réponse
            if avg_response_time > 2.0:  # > 2 secondes
                adaptation_factor *= 0.8  # Réduction de 20%
            elif avg_response_time < 0.5:  # < 500ms
                adaptation_factor *= 1.2  # Augmentation de 20%
            
            # Adaptation basée sur le taux d'erreur
            if error_rate > 0.1:  # > 10% d'erreurs
                adaptation_factor *= 0.7  # Réduction importante
            elif error_rate < 0.01:  # < 1% d'erreurs
                adaptation_factor *= 1.1  # Légère augmentation
            
            # Adaptation basée sur le taux de blocage
            if blocked_rate > config.adaptive_threshold:
                adaptation_factor *= 0.9  # Réduction modérée
            elif blocked_rate < 0.1:
                adaptation_factor *= 1.15  # Augmentation
            
            # Limitation des extremes
            adaptation_factor = max(0.3, min(3.0, adaptation_factor))
            
            return adaptation_factor
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul adaptation: {e}")
            return 1.0

    def _get_request_cost(self, priority: RequestPriority) -> int:
        """Calcul du coût d'une requête basé sur sa priorité"""
        costs = {
            RequestPriority.CRITICAL: 1,
            RequestPriority.HIGH: 1,
            RequestPriority.MEDIUM: 2,
            RequestPriority.LOW: 3
        }
        return costs.get(priority, 2)

    def _generate_request_id(self, creator_id: str, endpoint: str, method: str) -> str:
        """Génération d'un ID unique de requête"""
        timestamp = str(int(time.time() * 1000))
        raw = f"{creator_id}:{endpoint}:{method}:{timestamp}"
        return hashlib.md5(raw.encode()).hexdigest()

    async def _get_recent_metrics(self, creator_id: str, seconds: int) -> List[Dict[str, Any]]:
        """Récupération des métriques récentes"""
        try:
            since = datetime.now() - timedelta(seconds=seconds)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT processing_time, status_code, allowed
                    FROM rate_limit_metrics
                    WHERE creator_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (creator_id, since.isoformat()))
                
                rows = await cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metrics.append({
                        'processing_time': row[0] or 0.0,
                        'status_code': row[1] or 200,
                        'allowed': bool(row[2])
                    })
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération métriques: {e}")
            return []

    async def _record_request_metrics(self, 
                                     metrics: RequestMetrics, 
                                     allowed: bool, 
                                     limit_reason: Optional[str]) -> None:
        """Enregistrement des métriques de requête"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO rate_limit_metrics 
                    (request_id, creator_id, creator_type, creator_tier, endpoint, method,
                     priority, timestamp, processing_time, status_code, bytes_consumed,
                     allowed, limit_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.request_id, metrics.creator_id, metrics.creator_type,
                    metrics.creator_tier.value, metrics.endpoint, metrics.method,
                    metrics.priority.value, metrics.timestamp.isoformat(),
                    metrics.processing_time, metrics.status_code, metrics.bytes_consumed,
                    allowed, limit_reason
                ))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement métriques: {e}")

    async def update_creator_config(self, 
                                   creator_id: str,
                                   creator_tier: CreatorTier,
                                   custom_rps: Optional[int] = None,
                                   custom_burst: Optional[int] = None,
                                   custom_priority: Optional[RequestPriority] = None) -> bool:
        """Mise à jour de la configuration d'un créateur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO rate_limit_configs 
                    (creator_id, creator_tier, custom_requests_per_second, 
                     custom_burst_limit, custom_priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    creator_id, creator_tier.value, custom_rps, custom_burst,
                    custom_priority.value if custom_priority else None,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                await db.commit()
            
            self.logger.info(f"✅ Configuration mise à jour pour {creator_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour config: {e}")
            return False

    async def get_rate_limit_analytics(self, period_hours: int = 24) -> Dict[str, Any]:
        """Analytics de rate limiting"""
        try:
            since = datetime.now() - timedelta(hours=period_hours)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Métriques générales
                cursor = await db.execute("""
                    SELECT COUNT(*) as total_requests,
                           SUM(CASE WHEN allowed = 1 THEN 1 ELSE 0 END) as allowed_requests,
                           SUM(CASE WHEN allowed = 0 THEN 1 ELSE 0 END) as blocked_requests,
                           AVG(processing_time) as avg_response_time
                    FROM rate_limit_metrics
                    WHERE timestamp >= ?
                """, (since.isoformat(),))
                
                general_metrics = await cursor.fetchone()
                
                # Top consommateurs
                cursor = await db.execute("""
                    SELECT creator_id, creator_type, COUNT(*) as request_count,
                           SUM(CASE WHEN allowed = 0 THEN 1 ELSE 0 END) as blocked_count
                    FROM rate_limit_metrics
                    WHERE timestamp >= ?
                    GROUP BY creator_id, creator_type
                    ORDER BY request_count DESC
                    LIMIT 10
                """, (since.isoformat(),))
                
                top_consumers = await cursor.fetchall()
                
                # Distribution par tiers
                cursor = await db.execute("""
                    SELECT creator_tier, COUNT(*) as request_count
                    FROM rate_limit_metrics
                    WHERE timestamp >= ?
                    GROUP BY creator_tier
                """, (since.isoformat(),))
                
                tier_distribution = await cursor.fetchall()
            
            analytics = {
                "period_hours": period_hours,
                "total_requests": general_metrics[0] or 0,
                "allowed_requests": general_metrics[1] or 0,
                "blocked_requests": general_metrics[2] or 0,
                "block_rate": (general_metrics[2] or 0) / max(general_metrics[0] or 1, 1) * 100,
                "average_response_time": general_metrics[3] or 0.0,
                "top_consumers": [
                    {
                        "creator_id": row[0],
                        "creator_type": row[1],
                        "requests": row[2],
                        "blocked": row[3],
                        "block_rate": (row[3] / max(row[2], 1)) * 100
                    } for row in top_consumers
                ],
                "tier_distribution": {row[0]: row[1] for row in tier_distribution},
                "health_status": "healthy" if (general_metrics[2] or 0) / max(general_metrics[0] or 1, 1) < 0.1 else "degraded"
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analytics: {e}")
            raise AinflueCoreException(f"Échec génération analytics: {e}")

    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            self.executor.shutdown(wait=True)
            self.logger.info("✅ Rate Limiter nettoyé")
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")

# Example usage
async def main():
    limiter = AdaptiveRateLimiter()
    await limiter.initialize()
    
    # Test rate limiting pour différents types de créateurs
    creators = [
        ("musician_001", "musician", CreatorTier.PREMIUM),
        ("blogger_002", "blogger", CreatorTier.PRO),
        ("photographer_003", "photographer", CreatorTier.STANDARD),
        ("influencer_004", "influencer", CreatorTier.FREE)
    ]
    
    for creator_id, creator_type, tier in creators:
        result = await limiter.check_rate_limit(
            creator_id=creator_id,
            creator_type=creator_type,
            creator_tier=tier,
            endpoint="/api/ml/inference",
            method="POST",
            priority=RequestPriority.HIGH
        )
        
        print(f"{creator_type} ({tier.value}): {'✅ Allowed' if result.allowed else '❌ Blocked'} - {result.remaining_quota} remaining")
    
    # Analytics
    analytics = await limiter.get_rate_limit_analytics()
    print(f"Analytics: {analytics['total_requests']} requests, {analytics['block_rate']:.1f}% blocked")
    
    await limiter.cleanup()

if __name__ == "__main__":
    asyncio.run(main())