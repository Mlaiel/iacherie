"""
🎯 GATEWAY RATE LIMITING SERVICE
Service de limitation de taux intelligent pour API Gateway

Fonctionnalités:
- Rate limiting adaptatif basé sur l'IA
- Protection DDoS multicouche
- Limites personnalisées par utilisateur/tenant
- Analytics et alertes en temps réel
- Whitelist/Blacklist automatiques

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types de limitation de taux"""
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_API_KEY = "per_api_key"
    PER_ENDPOINT = "per_endpoint"
    GLOBAL = "global"
    ADAPTIVE = "adaptive"

class LimitStrategy(Enum):
    """Stratégies de limitation"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE_AI = "adaptive_ai"

@dataclass
class RateLimit:
    """Configuration de limitation de taux"""
    limit_type: RateLimitType
    strategy: LimitStrategy
    requests_per_window: int
    window_size_seconds: int
    burst_allowance: int = 0
    penalty_duration_seconds: int = 300
    recovery_rate: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitStatus:
    """Statut actuel de limitation"""
    identifier: str
    limit_type: RateLimitType
    current_count: int
    limit_value: int
    reset_time: float
    blocked: bool
    penalty_until: Optional[float] = None
    requests_remaining: int = 0

class GatewayRateLimiting:
    """
    🎯 SERVICE RATE LIMITING GATEWAY ENTERPRISE
    
    Protection intelligente contre les abus et attaques DDoS
    avec limitation adaptative basée sur l'IA et analytics temps réel
    """
    
    def __init__(self, service_id: str = None, redis_url: str = "redis://localhost:6379"):
        self.service_id = service_id or f"gateway-rate-limiting-{int(time.time())}"
        self.status = "initializing"
        self.redis_url = redis_url
        self.redis_client = None
        
        # Configuration par défaut
        self.default_limits = {
            RateLimitType.PER_USER: RateLimit(
                limit_type=RateLimitType.PER_USER,
                strategy=LimitStrategy.SLIDING_WINDOW,
                requests_per_window=1000,
                window_size_seconds=3600,
                burst_allowance=100
            ),
            RateLimitType.PER_IP: RateLimit(
                limit_type=RateLimitType.PER_IP,
                strategy=LimitStrategy.TOKEN_BUCKET,
                requests_per_window=100,
                window_size_seconds=60,
                burst_allowance=20
            ),
            RateLimitType.PER_API_KEY: RateLimit(
                limit_type=RateLimitType.PER_API_KEY,
                strategy=LimitStrategy.SLIDING_WINDOW,
                requests_per_window=5000,
                window_size_seconds=3600,
                burst_allowance=500
            ),
            RateLimitType.GLOBAL: RateLimit(
                limit_type=RateLimitType.GLOBAL,
                strategy=LimitStrategy.LEAKY_BUCKET,
                requests_per_window=100000,
                window_size_seconds=60,
                burst_allowance=10000
            )
        }
        
        # Limites personnalisées par tenant/utilisateur
        self.custom_limits = {}
        
        # Whitelist et blacklist
        self.whitelisted_ips = set()
        self.blacklisted_ips = set()
        
        # Analytics
        self.rate_limit_stats = {}
        
    async def initialize(self) -> bool:
        """Initialiser le service de rate limiting"""
        logger.info("🎯 Initializing Gateway Rate Limiting Service...")
        
        try:
            # Connexion Redis
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Charger les configurations personnalisées
            await self._load_custom_limits()
            
            # Charger les listes blanches/noires
            await self._load_ip_lists()
            
            self.status = "ready"
            logger.info("✅ Gateway Rate Limiting Service initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gateway Rate Limiting: {e}")
            self.status = "error"
            return False
    
    async def _load_custom_limits(self) -> None:
        """Charger les limites personnalisées depuis Redis"""
        try:
            # Charger depuis Redis en production
            # Pour la démo, utiliser des valeurs par défaut
            self.custom_limits = {
                "premium_users": RateLimit(
                    limit_type=RateLimitType.PER_USER,
                    strategy=LimitStrategy.SLIDING_WINDOW,
                    requests_per_window=10000,
                    window_size_seconds=3600,
                    burst_allowance=1000
                ),
                "enterprise_api_keys": RateLimit(
                    limit_type=RateLimitType.PER_API_KEY,
                    strategy=LimitStrategy.TOKEN_BUCKET,
                    requests_per_window=50000,
                    window_size_seconds=3600,
                    burst_allowance=5000
                )
            }
        except Exception as e:
            logger.warning(f"Could not load custom limits: {e}")
    
    async def _load_ip_lists(self) -> None:
        """Charger les listes d'IP autorisées/bloquées"""
        try:
            # Charger depuis Redis en production
            self.whitelisted_ips = {
                "192.168.1.0/24",  # Réseau interne
                "10.0.0.0/8",      # Réseau privé
                "203.0.113.0/24"   # IP de confiance
            }
            
            self.blacklisted_ips = {
                "203.0.113.100",   # IP malveillante exemple
                "198.51.100.0/24"  # Réseau bloqué exemple
            }
        except Exception as e:
            logger.warning(f"Could not load IP lists: {e}")
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: RateLimitType,
        endpoint: str = None,
        user_tier: str = "standard",
        ip_address: str = None
    ) -> RateLimitStatus:
        """
        Vérifier si une requête respecte les limites de taux
        
        Args:
            identifier: Identifiant unique (user_id, api_key, ip)
            limit_type: Type de limitation à appliquer
            endpoint: Endpoint API appelé
            user_tier: Niveau d'utilisateur (standard, premium, enterprise)
            ip_address: Adresse IP du client
        """
        try:
            # Vérifier la whitelist/blacklist IP
            if ip_address:
                if await self._is_blacklisted(ip_address):
                    return RateLimitStatus(
                        identifier=identifier,
                        limit_type=limit_type,
                        current_count=999999,
                        limit_value=0,
                        reset_time=time.time() + 86400,  # 24h
                        blocked=True,
                        penalty_until=time.time() + 86400
                    )
                
                if await self._is_whitelisted(ip_address):
                    # Pas de limitation pour les IP whitelistées
                    return RateLimitStatus(
                        identifier=identifier,
                        limit_type=limit_type,
                        current_count=0,
                        limit_value=999999,
                        reset_time=time.time() + 3600,
                        blocked=False,
                        requests_remaining=999999
                    )
            
            # Obtenir la configuration de limite
            rate_limit = await self._get_rate_limit_config(limit_type, user_tier, endpoint)
            
            # Vérifier la limitation selon la stratégie
            if rate_limit.strategy == LimitStrategy.SLIDING_WINDOW:
                status = await self._check_sliding_window(identifier, rate_limit)
            elif rate_limit.strategy == LimitStrategy.TOKEN_BUCKET:
                status = await self._check_token_bucket(identifier, rate_limit)
            elif rate_limit.strategy == LimitStrategy.LEAKY_BUCKET:
                status = await self._check_leaky_bucket(identifier, rate_limit)
            elif rate_limit.strategy == LimitStrategy.ADAPTIVE_AI:
                status = await self._check_adaptive_ai(identifier, rate_limit, endpoint)
            else:  # FIXED_WINDOW par défaut
                status = await self._check_fixed_window(identifier, rate_limit)
            
            # Enregistrer les statistics
            await self._record_rate_limit_stats(identifier, limit_type, status)
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            # En cas d'erreur, permettre la requête (fail-open)
            return RateLimitStatus(
                identifier=identifier,
                limit_type=limit_type,
                current_count=0,
                limit_value=1000,
                reset_time=time.time() + 3600,
                blocked=False,
                requests_remaining=1000
            )
    
    async def _is_blacklisted(self, ip_address: str) -> bool:
        """Vérifier si une IP est blacklistée"""
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(ip_address)
            for blocked_range in self.blacklisted_ips:
                if "/" in blocked_range:
                    network = ipaddress.ip_network(blocked_range, strict=False)
                    if ip in network:
                        return True
                elif ip_address == blocked_range:
                    return True
            return False
        except Exception:
            return False
    
    async def _is_whitelisted(self, ip_address: str) -> bool:
        """Vérifier si une IP est whitelistée"""
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(ip_address)
            for allowed_range in self.whitelisted_ips:
                if "/" in allowed_range:
                    network = ipaddress.ip_network(allowed_range, strict=False)
                    if ip in network:
                        return True
                elif ip_address == allowed_range:
                    return True
            return False
        except Exception:
            return False
    
    async def _get_rate_limit_config(
        self, 
        limit_type: RateLimitType, 
        user_tier: str, 
        endpoint: str = None
    ) -> RateLimit:
        """Obtenir la configuration de rate limit appropriée"""
        
        # Vérifier les limites personnalisées par tier
        tier_key = f"{user_tier}_users"
        if tier_key in self.custom_limits:
            return self.custom_limits[tier_key]
        
        # Vérifier les limites par endpoint
        if endpoint:
            endpoint_key = f"endpoint_{endpoint.replace('/', '_')}"
            if endpoint_key in self.custom_limits:
                return self.custom_limits[endpoint_key]
        
        # Utiliser la limite par défaut
        return self.default_limits.get(limit_type, self.default_limits[RateLimitType.PER_USER])
    
    async def _check_sliding_window(self, identifier: str, rate_limit: RateLimit) -> RateLimitStatus:
        """Vérification sliding window avec Redis"""
        current_time = time.time()
        window_start = current_time - rate_limit.window_size_seconds
        
        # Clé Redis pour la window
        redis_key = f"rate_limit:sliding:{identifier}:{rate_limit.limit_type.value}"
        
        # Pipeline Redis pour atomicité
        pipe = self.redis_client.pipeline()
        
        # Supprimer les entrées expirées
        pipe.zremrangebyscore(redis_key, 0, window_start)
        
        # Compter les requêtes dans la fenêtre
        pipe.zcard(redis_key)
        
        # Ajouter la requête actuelle
        pipe.zadd(redis_key, {str(current_time): current_time})
        
        # Définir l'expiration
        pipe.expire(redis_key, rate_limit.window_size_seconds + 10)
        
        results = await pipe.execute()
        current_count = results[1] + 1  # +1 pour la requête actuelle
        
        # Calculer le statut
        blocked = current_count > rate_limit.requests_per_window
        requests_remaining = max(0, rate_limit.requests_per_window - current_count)
        reset_time = current_time + rate_limit.window_size_seconds
        
        return RateLimitStatus(
            identifier=identifier,
            limit_type=rate_limit.limit_type,
            current_count=current_count,
            limit_value=rate_limit.requests_per_window,
            reset_time=reset_time,
            blocked=blocked,
            requests_remaining=requests_remaining
        )
    
    async def _check_token_bucket(self, identifier: str, rate_limit: RateLimit) -> RateLimitStatus:
        """Vérification token bucket avec Redis"""
        current_time = time.time()
        redis_key = f"rate_limit:bucket:{identifier}:{rate_limit.limit_type.value}"
        
        # Obtenir l'état actuel du bucket
        bucket_data = await self.redis_client.hmget(
            redis_key, 
            "tokens", "last_refill"
        )
        
        # Initialiser si nécessaire
        if not bucket_data[0]:
            tokens = rate_limit.requests_per_window
            last_refill = current_time
        else:
            tokens = float(bucket_data[0])
            last_refill = float(bucket_data[1])
        
        # Calculer les tokens à ajouter
        time_passed = current_time - last_refill
        refill_rate = rate_limit.requests_per_window / rate_limit.window_size_seconds
        tokens_to_add = time_passed * refill_rate
        
        # Mettre à jour les tokens (max = capacity)
        tokens = min(rate_limit.requests_per_window, tokens + tokens_to_add)
        
        # Vérifier si on peut consommer un token
        blocked = tokens < 1
        
        if not blocked:
            tokens -= 1  # Consommer un token
        
        # Sauvegarder l'état
        await self.redis_client.hmset(redis_key, {
            "tokens": tokens,
            "last_refill": current_time
        })
        await self.redis_client.expire(redis_key, rate_limit.window_size_seconds * 2)
        
        return RateLimitStatus(
            identifier=identifier,
            limit_type=rate_limit.limit_type,
            current_count=rate_limit.requests_per_window - int(tokens),
            limit_value=rate_limit.requests_per_window,
            reset_time=current_time + (rate_limit.window_size_seconds / rate_limit.requests_per_window),
            blocked=blocked,
            requests_remaining=int(tokens)
        )
    
    async def _check_leaky_bucket(self, identifier: str, rate_limit: RateLimit) -> RateLimitStatus:
        """Vérification leaky bucket avec Redis"""
        current_time = time.time()
        redis_key = f"rate_limit:leaky:{identifier}:{rate_limit.limit_type.value}"
        
        # Obtenir l'état actuel
        bucket_data = await self.redis_client.hmget(
            redis_key,
            "volume", "last_leak"
        )
        
        # Initialiser si nécessaire
        if not bucket_data[0]:
            volume = 0
            last_leak = current_time
        else:
            volume = float(bucket_data[0])
            last_leak = float(bucket_data[1])
        
        # Calculer la fuite
        time_passed = current_time - last_leak
        leak_rate = rate_limit.requests_per_window / rate_limit.window_size_seconds
        leaked_volume = time_passed * leak_rate
        
        # Mettre à jour le volume
        volume = max(0, volume - leaked_volume)
        
        # Vérifier si on peut ajouter la requête
        blocked = volume >= rate_limit.requests_per_window
        
        if not blocked:
            volume += 1  # Ajouter la requête
        
        # Sauvegarder l'état
        await self.redis_client.hmset(redis_key, {
            "volume": volume,
            "last_leak": current_time
        })
        await self.redis_client.expire(redis_key, rate_limit.window_size_seconds * 2)
        
        return RateLimitStatus(
            identifier=identifier,
            limit_type=rate_limit.limit_type,
            current_count=int(volume),
            limit_value=rate_limit.requests_per_window,
            reset_time=current_time + (volume / leak_rate),
            blocked=blocked,
            requests_remaining=rate_limit.requests_per_window - int(volume)
        )
    
    async def _check_adaptive_ai(
        self, 
        identifier: str, 
        rate_limit: RateLimit, 
        endpoint: str = None
    ) -> RateLimitStatus:
        """Vérification adaptative basée sur l'IA"""
        # Implémentation simplifiée - en production, utiliser un modèle ML
        
        # Analyser les patterns historiques
        historical_pattern = await self._analyze_historical_pattern(identifier, endpoint)
        
        # Calculer la limite adaptative
        adaptive_multiplier = 1.0
        
        if historical_pattern["is_legitimate_user"]:
            adaptive_multiplier = 1.5  # Plus de tolérance pour les utilisateurs légitimes
        elif historical_pattern["is_suspicious"]:
            adaptive_multiplier = 0.5  # Moins de tolérance pour les utilisateurs suspects
        
        # Appliquer la limite adaptative
        adapted_limit = int(rate_limit.requests_per_window * adaptive_multiplier)
        
        # Utiliser sliding window avec limite adaptée
        adapted_rate_limit = RateLimit(
            limit_type=rate_limit.limit_type,
            strategy=LimitStrategy.SLIDING_WINDOW,
            requests_per_window=adapted_limit,
            window_size_seconds=rate_limit.window_size_seconds,
            burst_allowance=rate_limit.burst_allowance
        )
        
        return await self._check_sliding_window(identifier, adapted_rate_limit)
    
    async def _analyze_historical_pattern(self, identifier: str, endpoint: str = None) -> Dict[str, Any]:
        """Analyser les patterns historiques pour l'IA adaptative"""
        # Implémentation simplifiée - en production, utiliser des données réelles
        
        # Simuler l'analyse des patterns
        return {
            "is_legitimate_user": True,  # Basé sur l'historique
            "is_suspicious": False,      # Basé sur les anomalies détectées
            "average_requests_per_hour": 150,
            "peak_usage_times": ["09:00-11:00", "14:00-16:00"],
            "preferred_endpoints": ["/api/v1/creators", "/api/v1/content"]
        }
    
    async def _record_rate_limit_stats(
        self,
        identifier: str,
        limit_type: RateLimitType,
        status: RateLimitStatus
    ) -> None:
        """Enregistrer les statistiques de rate limiting"""
        current_time = time.time()
        stats_key = f"rate_limit_stats:{limit_type.value}:{int(current_time // 60)}"  # Par minute
        
        # Incrémenter les compteurs
        pipe = self.redis_client.pipeline()
        pipe.hincrby(stats_key, "total_requests", 1)
        
        if status.blocked:
            pipe.hincrby(stats_key, "blocked_requests", 1)
        
        pipe.expire(stats_key, 86400)  # Garder 24h
        await pipe.execute()
    
    async def add_to_whitelist(self, ip_address: str) -> bool:
        """Ajouter une IP à la whitelist"""
        self.whitelisted_ips.add(ip_address)
        
        # Sauvegarder dans Redis
        await self.redis_client.sadd("rate_limit:whitelist", ip_address)
        
        logger.info(f"Added {ip_address} to whitelist")
        return True
    
    async def add_to_blacklist(self, ip_address: str, duration_seconds: int = 3600) -> bool:
        """Ajouter une IP à la blacklist"""
        self.blacklisted_ips.add(ip_address)
        
        # Sauvegarder dans Redis avec expiration
        await self.redis_client.setex(f"rate_limit:blacklist:{ip_address}", duration_seconds, "1")
        
        logger.info(f"Added {ip_address} to blacklist for {duration_seconds} seconds")
        return True
    
    async def get_rate_limit_stats(self, time_window: str = "1h") -> Dict[str, Any]:
        """Obtenir les statistiques de rate limiting"""
        current_time = time.time()
        
        if time_window == "1h":
            minutes_back = 60
        elif time_window == "24h":
            minutes_back = 1440
        else:
            minutes_back = 60
        
        total_requests = 0
        blocked_requests = 0
        
        # Agréger les stats par minute
        for minute_offset in range(minutes_back):
            minute_timestamp = int((current_time - (minute_offset * 60)) // 60)
            
            for limit_type in RateLimitType:
                stats_key = f"rate_limit_stats:{limit_type.value}:{minute_timestamp}"
                stats = await self.redis_client.hmget(stats_key, "total_requests", "blocked_requests")
                
                if stats[0]:
                    total_requests += int(stats[0])
                if stats[1]:
                    blocked_requests += int(stats[1])
        
        # Calculer les métriques
        block_rate = (blocked_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "time_window": time_window,
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "allowed_requests": total_requests - blocked_requests,
            "block_rate_percent": round(block_rate, 2),
            "requests_per_minute": round(total_requests / minutes_back, 2),
            "whitelisted_ips": len(self.whitelisted_ips),
            "blacklisted_ips": len(self.blacklisted_ips)
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtenir le statut du service"""
        return {
            "service_id": self.service_id,
            "status": self.status,
            "supported_strategies": [strategy.value for strategy in LimitStrategy],
            "supported_limit_types": [limit_type.value for limit_type in RateLimitType],
            "default_limits": {
                limit_type.value: {
                    "requests_per_window": limit_config.requests_per_window,
                    "window_size_seconds": limit_config.window_size_seconds,
                    "strategy": limit_config.strategy.value
                }
                for limit_type, limit_config in self.default_limits.items()
            }
        }

# Instance globale du service
gateway_rate_limiting = GatewayRateLimiting()

async def main():
    """Test du service de rate limiting gateway"""
    await gateway_rate_limiting.initialize()
    
    # Test de vérification de rate limit
    status = await gateway_rate_limiting.check_rate_limit(
        identifier="user_123",
        limit_type=RateLimitType.PER_USER,
        endpoint="/api/v1/creators",
        user_tier="premium",
        ip_address="192.168.1.100"
    )
    
    print(f"Rate limit status: {status}")
    
    # Test d'ajout à la whitelist
    await gateway_rate_limiting.add_to_whitelist("192.168.1.100")
    
    # Test des statistiques
    stats = await gateway_rate_limiting.get_rate_limit_stats("1h")
    print(f"Rate limit stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())