#!/usr/bin/env python3
"""
⚡ Gateway Rate Limiting Service - Enterprise Grade
Service de limitation de débit enterprise pour API Gateway Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import time
from collections import defaultdict, deque
import threading

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimitAlgorithm(Enum):
    """Algorithmes de limitation de débit"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"

class RateLimitScope(Enum):
    """Portées de limitation"""
    GLOBAL = "global"
    USER = "user"
    IP = "ip"
    API_KEY = "api_key"
    ENDPOINT = "endpoint"

@dataclass
class RateLimitRule:
    """Règle de limitation de débit"""
    rule_id: str
    name: str
    description: str
    scope: RateLimitScope
    algorithm: RateLimitAlgorithm
    limit: int
    window_size: int  # en secondes
    burst_limit: Optional[int] = None
    pattern: Optional[str] = None  # pattern d'endpoint
    exemptions: List[str] = None  # IDs exemptés
    is_active: bool = True
    priority: int = 1
    created_at: datetime = None
    
    def __post_init__(self):
        if self.exemptions is None:
            self.exemptions = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class RateLimitState:
    """État de limitation pour un client"""
    client_id: str
    rule_id: str
    current_count: int
    last_reset: datetime
    tokens: float = 0.0  # Pour token bucket
    last_refill: datetime = None
    request_times: deque = None  # Pour sliding window
    
    def __post_init__(self):
        if self.request_times is None:
            self.request_times = deque()
        if self.last_refill is None:
            self.last_refill = datetime.utcnow()

@dataclass
class RateLimitResult:
    """Résultat de vérification de débit"""
    allowed: bool
    rule_id: Optional[str] = None
    remaining: int = 0
    reset_time: Optional[datetime] = None
    retry_after: Optional[int] = None
    reason: Optional[str] = None
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}

@dataclass
class RateLimitRequest:
    """Requête pour vérification de débit"""
    client_id: str
    endpoint: str
    method: str
    ip_address: Optional[str] = None
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class GatewayRateLimitingService:
    """
    ⚡ Service de limitation de débit API Gateway enterprise
    Implémentation multi-algorithmes avec haute performance
    """
    
    def __init__(self):
        """Initialisation du service de rate limiting"""
        
        # Stockage des règles et états
        self.rules: Dict[str, RateLimitRule] = {}
        self.client_states: Dict[str, Dict[str, RateLimitState]] = defaultdict(dict)
        
        # Verrous pour concurrence
        self.locks: Dict[str, threading.RLock] = defaultdict(threading.RLock)
        
        # Métriques enterprise
        self.metrics = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'rate_limited_clients': 0,
            'active_rules': 0,
            'avg_response_time': 0.0
        }
        
        # Configuration par défaut
        self._setup_default_rules()
        
        # Nettoyage automatique
        self._start_cleanup_task()
        
        logger.info("⚡ Gateway Rate Limiting Service initialisé")
    
    def _setup_default_rules(self):
        """Configuration des règles par défaut"""
        try:
            # Limitation globale agressive
            global_rule = RateLimitRule(
                rule_id="global_limit",
                name="Limitation globale",
                description="Limitation globale pour tous les clients",
                scope=RateLimitScope.GLOBAL,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                limit=10000,
                window_size=60,
                priority=1
            )
            self.rules[global_rule.rule_id] = global_rule
            
            # Limitation par utilisateur
            user_rule = RateLimitRule(
                rule_id="user_limit",
                name="Limitation par utilisateur",
                description="Limitation par utilisateur authentifié",
                scope=RateLimitScope.USER,
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                limit=1000,
                window_size=60,
                burst_limit=100,
                priority=10
            )
            self.rules[user_rule.rule_id] = user_rule
            
            # Limitation par IP
            ip_rule = RateLimitRule(
                rule_id="ip_limit",
                name="Limitation par IP",
                description="Limitation par adresse IP",
                scope=RateLimitScope.IP,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                limit=100,
                window_size=60,
                priority=20
            )
            self.rules[ip_rule.rule_id] = ip_rule
            
            # Limitation API sensibles
            api_rule = RateLimitRule(
                rule_id="sensitive_api_limit",
                name="APIs sensibles",
                description="Limitation pour les APIs sensibles",
                scope=RateLimitScope.ENDPOINT,
                algorithm=RateLimitAlgorithm.FIXED_WINDOW,
                limit=10,
                window_size=60,
                pattern="/api/admin/*",
                priority=100
            )
            self.rules[api_rule.rule_id] = api_rule
            
            self.metrics['active_rules'] = len(self.rules)
            logger.info("✅ Règles de rate limiting par défaut configurées")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration règles par défaut: {e}")
    
    async def create_rule(
        self,
        name: str,
        description: str,
        scope: RateLimitScope,
        algorithm: RateLimitAlgorithm,
        limit: int,
        window_size: int,
        burst_limit: Optional[int] = None,
        pattern: Optional[str] = None,
        exemptions: Optional[List[str]] = None,
        priority: int = 1
    ) -> str:
        """
        Créer une nouvelle règle de rate limiting
        
        Args:
            name: Nom de la règle
            description: Description
            scope: Portée de la limitation
            algorithm: Algorithme utilisé
            limit: Limite de requêtes
            window_size: Taille de la fenêtre (secondes)
            burst_limit: Limite de rafale (pour token bucket)
            pattern: Pattern d'endpoint (optionnel)
            exemptions: IDs exemptés
            priority: Priorité (plus élevé = plus prioritaire)
        
        Returns:
            ID de la règle créée
        """
        try:
            rule_id = f"rule_{uuid.uuid4().hex[:8]}"
            
            rule = RateLimitRule(
                rule_id=rule_id,
                name=name,
                description=description,
                scope=scope,
                algorithm=algorithm,
                limit=limit,
                window_size=window_size,
                burst_limit=burst_limit,
                pattern=pattern,
                exemptions=exemptions or [],
                priority=priority
            )
            
            self.rules[rule_id] = rule
            self.metrics['active_rules'] = len([r for r in self.rules.values() if r.is_active])
            
            logger.info(f"✅ Règle de rate limiting créée: {rule_id} - {name}")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création règle: {e}")
            raise
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResult:
        """
        Vérifier les limites de débit pour une requête
        
        Args:
            request: Requête à vérifier
        
        Returns:
            Résultat de la vérification
        """
        try:
            start_time = time.time()
            self.metrics['total_requests'] += 1
            
            # Évaluation des règles applicables
            applicable_rules = self._get_applicable_rules(request)
            
            if not applicable_rules:
                self.metrics['allowed_requests'] += 1
                return RateLimitResult(allowed=True, reason="Aucune règle applicable")
            
            # Vérification de chaque règle
            for rule in applicable_rules:
                result = await self._check_rule(request, rule)
                
                if not result.allowed:
                    self.metrics['blocked_requests'] += 1
                    self._update_response_time(start_time)
                    return result
            
            self.metrics['allowed_requests'] += 1
            self._update_response_time(start_time)
            
            return RateLimitResult(
                allowed=True,
                reason="Toutes les vérifications passées",
                headers=self._generate_headers(request, applicable_rules[0])
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification rate limit: {e}")
            return RateLimitResult(
                allowed=False,
                reason=f"Erreur de vérification: {str(e)}"
            )
    
    def _get_applicable_rules(self, request: RateLimitRequest) -> List[RateLimitRule]:
        """Obtenir les règles applicables à une requête"""
        try:
            applicable = []
            
            for rule in self.rules.values():
                if not rule.is_active:
                    continue
                
                # Vérification des exemptions
                if self._is_exempted(request, rule):
                    continue
                
                # Vérification du scope
                if rule.scope == RateLimitScope.GLOBAL:
                    applicable.append(rule)
                elif rule.scope == RateLimitScope.USER and request.user_id:
                    applicable.append(rule)
                elif rule.scope == RateLimitScope.IP and request.ip_address:
                    applicable.append(rule)
                elif rule.scope == RateLimitScope.API_KEY and request.api_key:
                    applicable.append(rule)
                elif rule.scope == RateLimitScope.ENDPOINT:
                    if self._match_endpoint_pattern(rule.pattern, request.endpoint):
                        applicable.append(rule)
            
            # Tri par priorité
            return sorted(applicable, key=lambda r: r.priority, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération règles applicables: {e}")
            return []
    
    def _is_exempted(self, request: RateLimitRequest, rule: RateLimitRule) -> bool:
        """Vérifier si la requête est exemptée"""
        try:
            exemptions = rule.exemptions
            
            return (
                request.client_id in exemptions or
                (request.user_id and request.user_id in exemptions) or
                (request.ip_address and request.ip_address in exemptions) or
                (request.api_key and request.api_key in exemptions)
            )
        except:
            return False
    
    def _match_endpoint_pattern(self, pattern: Optional[str], endpoint: str) -> bool:
        """Vérifier si l'endpoint correspond au pattern"""
        try:
            if not pattern:
                return True
            
            import re
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            return bool(re.match(regex_pattern, endpoint))
        except:
            return False
    
    async def _check_rule(self, request: RateLimitRequest, rule: RateLimitRule) -> RateLimitResult:
        """Vérifier une règle spécifique"""
        try:
            # Génération de l'ID client selon le scope
            client_id = self._generate_client_id(request, rule)
            
            # Verrou pour éviter les race conditions
            with self.locks[f"{rule.rule_id}_{client_id}"]:
                # Récupération ou création de l'état
                state = self._get_or_create_state(client_id, rule)
                
                # Vérification selon l'algorithme
                if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    return await self._check_token_bucket(request, rule, state)
                elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                    return await self._check_sliding_window(request, rule, state)
                elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                    return await self._check_fixed_window(request, rule, state)
                elif rule.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
                    return await self._check_leaky_bucket(request, rule, state)
                else:
                    return RateLimitResult(
                        allowed=False,
                        reason=f"Algorithme non supporté: {rule.algorithm}"
                    )
                    
        except Exception as e:
            logger.error(f"❌ Erreur vérification règle {rule.rule_id}: {e}")
            return RateLimitResult(allowed=False, reason="Erreur de vérification")
    
    def _generate_client_id(self, request: RateLimitRequest, rule: RateLimitRule) -> str:
        """Générer un ID client selon le scope"""
        try:
            if rule.scope == RateLimitScope.GLOBAL:
                return "global"
            elif rule.scope == RateLimitScope.USER:
                return f"user_{request.user_id}"
            elif rule.scope == RateLimitScope.IP:
                return f"ip_{request.ip_address}"
            elif rule.scope == RateLimitScope.API_KEY:
                return f"apikey_{request.api_key}"
            elif rule.scope == RateLimitScope.ENDPOINT:
                return f"endpoint_{request.endpoint}_{request.user_id or request.ip_address}"
            else:
                return request.client_id
        except:
            return "unknown"
    
    def _get_or_create_state(self, client_id: str, rule: RateLimitRule) -> RateLimitState:
        """Récupérer ou créer l'état d'un client"""
        try:
            if rule.rule_id not in self.client_states[client_id]:
                self.client_states[client_id][rule.rule_id] = RateLimitState(
                    client_id=client_id,
                    rule_id=rule.rule_id,
                    current_count=0,
                    last_reset=datetime.utcnow(),
                    tokens=float(rule.limit)  # Initialisation avec limite complète
                )
            
            return self.client_states[client_id][rule.rule_id]
        except Exception as e:
            logger.error(f"❌ Erreur création état: {e}")
            # État par défaut en cas d'erreur
            return RateLimitState(
                client_id=client_id,
                rule_id=rule.rule_id,
                current_count=0,
                last_reset=datetime.utcnow()
            )
    
    async def _check_token_bucket(
        self,
        request: RateLimitRequest,
        rule: RateLimitRule,
        state: RateLimitState
    ) -> RateLimitResult:
        """Vérification Token Bucket"""
        try:
            now = datetime.utcnow()
            
            # Calcul du rechargement des tokens
            time_elapsed = (now - state.last_refill).total_seconds()
            tokens_to_add = time_elapsed * (rule.limit / rule.window_size)
            
            # Ajout des tokens (sans dépasser la limite)
            state.tokens = min(rule.limit, state.tokens + tokens_to_add)
            state.last_refill = now
            
            # Vérification de la disponibilité
            if state.tokens >= 1.0:
                state.tokens -= 1.0
                return RateLimitResult(
                    allowed=True,
                    rule_id=rule.rule_id,
                    remaining=int(state.tokens),
                    headers=self._generate_headers(request, rule, state)
                )
            else:
                # Calcul du temps d'attente
                retry_after = int((1.0 - state.tokens) * (rule.window_size / rule.limit))
                
                return RateLimitResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    remaining=0,
                    retry_after=retry_after,
                    reason=f"Token bucket vide pour {rule.name}",
                    headers=self._generate_headers(request, rule, state)
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur token bucket: {e}")
            return RateLimitResult(allowed=False, reason="Erreur token bucket")
    
    async def _check_sliding_window(
        self,
        request: RateLimitRequest,
        rule: RateLimitRule,
        state: RateLimitState
    ) -> RateLimitResult:
        """Vérification Sliding Window"""
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=rule.window_size)
            
            # Nettoyage des anciens timestamps
            while state.request_times and datetime.fromisoformat(state.request_times[0]) < window_start:
                state.request_times.popleft()
            
            # Vérification de la limite
            if len(state.request_times) < rule.limit:
                state.request_times.append(now.isoformat())
                
                return RateLimitResult(
                    allowed=True,
                    rule_id=rule.rule_id,
                    remaining=rule.limit - len(state.request_times),
                    reset_time=window_start + timedelta(seconds=rule.window_size),
                    headers=self._generate_headers(request, rule, state)
                )
            else:
                # Calcul du temps de reset
                oldest_request = datetime.fromisoformat(state.request_times[0])
                reset_time = oldest_request + timedelta(seconds=rule.window_size)
                retry_after = int((reset_time - now).total_seconds())
                
                return RateLimitResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=max(1, retry_after),
                    reason=f"Limite sliding window atteinte pour {rule.name}",
                    headers=self._generate_headers(request, rule, state)
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur sliding window: {e}")
            return RateLimitResult(allowed=False, reason="Erreur sliding window")
    
    async def _check_fixed_window(
        self,
        request: RateLimitRequest,
        rule: RateLimitRule,
        state: RateLimitState
    ) -> RateLimitResult:
        """Vérification Fixed Window"""
        try:
            now = datetime.utcnow()
            
            # Calcul de la fenêtre actuelle
            window_start = datetime(
                now.year, now.month, now.day, now.hour,
                (now.minute // (rule.window_size // 60)) * (rule.window_size // 60)
            )
            
            # Reset si nouvelle fenêtre
            if state.last_reset < window_start:
                state.current_count = 0
                state.last_reset = window_start
            
            # Vérification de la limite
            if state.current_count < rule.limit:
                state.current_count += 1
                
                return RateLimitResult(
                    allowed=True,
                    rule_id=rule.rule_id,
                    remaining=rule.limit - state.current_count,
                    reset_time=window_start + timedelta(seconds=rule.window_size),
                    headers=self._generate_headers(request, rule, state)
                )
            else:
                reset_time = window_start + timedelta(seconds=rule.window_size)
                retry_after = int((reset_time - now).total_seconds())
                
                return RateLimitResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=max(1, retry_after),
                    reason=f"Limite fixed window atteinte pour {rule.name}",
                    headers=self._generate_headers(request, rule, state)
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur fixed window: {e}")
            return RateLimitResult(allowed=False, reason="Erreur fixed window")
    
    async def _check_leaky_bucket(
        self,
        request: RateLimitRequest,
        rule: RateLimitRule,
        state: RateLimitState
    ) -> RateLimitResult:
        """Vérification Leaky Bucket"""
        try:
            now = datetime.utcnow()
            
            # Calcul de la fuite
            time_elapsed = (now - state.last_refill).total_seconds()
            leak_amount = time_elapsed * (rule.limit / rule.window_size)
            
            # Application de la fuite
            state.current_count = max(0, state.current_count - leak_amount)
            state.last_refill = now
            
            # Vérification de la capacité
            bucket_capacity = rule.burst_limit or rule.limit
            
            if state.current_count < bucket_capacity:
                state.current_count += 1
                
                return RateLimitResult(
                    allowed=True,
                    rule_id=rule.rule_id,
                    remaining=int(bucket_capacity - state.current_count),
                    headers=self._generate_headers(request, rule, state)
                )
            else:
                # Calcul du temps d'attente
                excess = state.current_count - bucket_capacity + 1
                retry_after = int(excess * (rule.window_size / rule.limit))
                
                return RateLimitResult(
                    allowed=False,
                    rule_id=rule.rule_id,
                    remaining=0,
                    retry_after=retry_after,
                    reason=f"Leaky bucket plein pour {rule.name}",
                    headers=self._generate_headers(request, rule, state)
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur leaky bucket: {e}")
            return RateLimitResult(allowed=False, reason="Erreur leaky bucket")
    
    def _generate_headers(
        self,
        request: RateLimitRequest,
        rule: RateLimitRule,
        state: Optional[RateLimitState] = None
    ) -> Dict[str, str]:
        """Générer les headers de rate limiting"""
        try:
            headers = {
                'X-RateLimit-Limit': str(rule.limit),
                'X-RateLimit-Window': str(rule.window_size),
                'X-RateLimit-Algorithm': rule.algorithm.value
            }
            
            if state:
                if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    headers['X-RateLimit-Remaining'] = str(int(state.tokens))
                elif rule.algorithm in [RateLimitAlgorithm.SLIDING_WINDOW, RateLimitAlgorithm.FIXED_WINDOW]:
                    remaining = rule.limit - (len(state.request_times) if hasattr(state, 'request_times') else state.current_count)
                    headers['X-RateLimit-Remaining'] = str(max(0, remaining))
            
            return headers
            
        except Exception as e:
            logger.error(f"❌ Erreur génération headers: {e}")
            return {}
    
    def _update_response_time(self, start_time: float):
        """Mettre à jour le temps de réponse moyen"""
        try:
            response_time = time.time() - start_time
            
            if self.metrics['avg_response_time'] == 0:
                self.metrics['avg_response_time'] = response_time
            else:
                # Moyenne mobile simple
                self.metrics['avg_response_time'] = (
                    self.metrics['avg_response_time'] * 0.9 + response_time * 0.1
                )
        except:
            pass
    
    def _start_cleanup_task(self):
        """Démarrer la tâche de nettoyage automatique"""
        def cleanup_loop():
            while True:
                try:
                    asyncio.run(self._cleanup_expired_states())
                    time.sleep(300)  # Nettoyage toutes les 5 minutes
                except Exception as e:
                    logger.error(f"❌ Erreur nettoyage: {e}")
        
        import threading
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    async def _cleanup_expired_states(self):
        """Nettoyer les états expirés"""
        try:
            now = datetime.utcnow()
            expired_clients = []
            
            for client_id, states in self.client_states.items():
                expired_rules = []
                
                for rule_id, state in states.items():
                    rule = self.rules.get(rule_id)
                    if not rule:
                        expired_rules.append(rule_id)
                        continue
                    
                    # Vérification de l'expiration selon l'algorithme
                    expiry_time = timedelta(seconds=rule.window_size * 2)  # 2x la fenêtre
                    
                    if now - state.last_refill > expiry_time:
                        expired_rules.append(rule_id)
                
                # Suppression des règles expirées
                for rule_id in expired_rules:
                    del states[rule_id]
                
                # Suppression du client s'il n'a plus d'états
                if not states:
                    expired_clients.append(client_id)
            
            # Suppression des clients expirés
            for client_id in expired_clients:
                del self.client_states[client_id]
            
            if expired_clients:
                logger.info(f"🧹 {len(expired_clients)} clients expirés nettoyés")
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage états: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Récupération des métriques
        
        Returns:
            Métriques de rate limiting
        """
        return {
            **self.metrics,
            'active_clients': len(self.client_states),
            'total_states': sum(len(states) for states in self.client_states.values()),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """
        Obtenir le statut d'un client
        
        Args:
            client_id: ID du client
        
        Returns:
            Statut du client
        """
        try:
            if client_id not in self.client_states:
                return {'client_id': client_id, 'states': [], 'active': False}
            
            states = []
            for rule_id, state in self.client_states[client_id].items():
                rule = self.rules.get(rule_id)
                if not rule:
                    continue
                
                state_info = {
                    'rule_id': rule_id,
                    'rule_name': rule.name,
                    'algorithm': rule.algorithm.value,
                    'current_count': state.current_count,
                    'tokens': getattr(state, 'tokens', 0),
                    'last_reset': state.last_reset.isoformat(),
                    'last_refill': state.last_refill.isoformat() if state.last_refill else None
                }
                states.append(state_info)
            
            return {
                'client_id': client_id,
                'states': states,
                'active': len(states) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut client: {e}")
            return {'client_id': client_id, 'error': str(e)}

# Instance globale du service
gateway_rate_limiting = GatewayRateLimitingService()

# API publique
__all__ = [
    'GatewayRateLimitingService',
    'RateLimitAlgorithm',
    'RateLimitScope',
    'RateLimitRule',
    'RateLimitState',
    'RateLimitResult',
    'RateLimitRequest',
    'gateway_rate_limiting'
]

if __name__ == "__main__":
    # Test de démonstration
    async def demo():
        service = GatewayRateLimitingService()
        
        # Création d'une règle personnalisée
        rule_id = await service.create_rule(
            name="Test API Limit",
            description="Limitation pour test",
            scope=RateLimitScope.USER,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            limit=5,
            window_size=60,
            burst_limit=10
        )
        
        # Simulation de requêtes
        for i in range(7):
            request = RateLimitRequest(
                client_id="test_client",
                endpoint="/api/test",
                method="GET",
                user_id="test_user",
                ip_address="192.168.1.1"
            )
            
            result = await service.check_rate_limit(request)
            print(f"Requête {i+1}: {result.allowed} - {result.reason}")
            
            if not result.allowed:
                print(f"Retry after: {result.retry_after} secondes")
        
        # Métriques
        metrics = service.get_metrics()
        print(f"Métriques: {metrics}")
        
        # Statut client
        status = await service.get_client_status("user_test_user")
        print(f"Statut client: {status}")
    
    # Exécution du test
    asyncio.run(demo())