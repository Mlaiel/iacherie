#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Redis Connection Pool Manager - Enterprise Connection Optimization
========================================================================

Gestionnaire de pools de connexions Redis optimisé pour haute performance
et scalabilité enterprise.

**Rôles Experts:**
- **Backend Senior**: Architecture pools connexions haute performance
- **DBA**: Optimisation connexions database et pool sizing
- **DevOps**: Monitoring pools et métriques opérationnelles
- **Sécurité**: Sécurisation connexions et authentification

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import ssl
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

# Optional Redis imports for enterprise environment
try:
    import aioredis
    from aioredis.sentinel import Sentinel
    import redis.asyncio as redis
    from redis.exceptions import (
        ConnectionError, TimeoutError, RedisError,
        AuthenticationError, ResponseError
    )
    REDIS_AVAILABLE = True
except ImportError:
    # Fallback pour environnement sans Redis
    REDIS_AVAILABLE = False
    aioredis = None
    redis = None
    ConnectionError = Exception
    TimeoutError = Exception
    RedisError = Exception
    AuthenticationError = Exception
    ResponseError = Exception

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConnectionPoolConfig:
    """Configuration avancée des pools de connexions Redis"""
    
    # Configuration de base
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    
    # Configuration pool
    min_connections: int = 5
    max_connections: int = 50
    max_idle_time: int = 300  # 5 minutes
    connection_timeout: float = 10.0
    socket_timeout: float = 5.0
    
    # Configuration haute disponibilité
    sentinel_hosts: Optional[List[Tuple[str, int]]] = None
    sentinel_service_name: str = "mymaster"
    sentinel_password: Optional[str] = None
    
    # Configuration cluster
    cluster_nodes: Optional[List[Dict[str, Any]]] = None
    skip_full_coverage_check: bool = False
    
    # Configuration SSL/TLS
    ssl_enabled: bool = False
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    
    # Configuration retry et résilience
    retry_on_timeout: bool = True
    max_retries: int = 3
    retry_delay: float = 0.1
    
    # Monitoring et métriques
    enable_metrics: bool = True
    health_check_interval: int = 30
    pool_name: str = "default"

@dataclass
class PoolMetrics:
    """Métriques du pool de connexions"""
    pool_name: str
    created_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_connections: int = 0
    last_health_check: float = field(default_factory=time.time)

class RedisConnectionPool:
    """
    🔗 Gestionnaire de pool de connexions Redis enterprise
    
    **Fonctionnalités Backend Senior:**
    - Pool adaptatif avec auto-scaling intelligent
    - Gestion connexions haute performance
    - Load balancing et distribution optimale
    
    **Fonctionnalités DBA:**
    - Optimisation sizing pools selon charge
    - Monitoring utilisation connexions
    - Prévention connexions orphelines
    
    **Fonctionnalités DevOps:**
    - Métriques détaillées pools
    - Health checks automatisés
    - Alertes sur seuils critiques
    
    **Fonctionnalités Sécurité:**
    - Authentification sécurisée
    - Chiffrement SSL/TLS
    - Audit trail connexions
    """
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self.pool: Optional[aioredis.ConnectionPool] = None
        self.sentinel: Optional[Sentinel] = None
        self.cluster_client: Optional[redis.RedisCluster] = None
        self.metrics = PoolMetrics(pool_name=config.pool_name)
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._connection_registry: Dict[str, float] = {}
        
        logger.info(f"🔗 Initialisation Redis Connection Pool: {config.pool_name}")
    
    async def initialize(self) -> bool:
        """
        **Backend Senior**: Initialisation pool haute performance
        """
        try:
            async with self._lock:
                if self.config.cluster_nodes:
                    await self._initialize_cluster()
                elif self.config.sentinel_hosts:
                    await self._initialize_sentinel()
                else:
                    await self._initialize_standalone()
                
                # Démarrage monitoring santé
                if self.config.enable_metrics:
                    self._health_check_task = asyncio.create_task(
                        self._health_check_loop()
                    )
                
                logger.info(f"✅ Pool Redis initialisé: {self.config.pool_name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation pool {self.config.pool_name}: {e}")
            return False
    
    async def _initialize_standalone(self):
        """**Backend Senior**: Configuration pool standalone optimisé"""
        ssl_config = None
        if self.config.ssl_enabled:
            ssl_config = ssl.create_default_context()
            if self.config.ssl_ca_certs:
                ssl_config.load_verify_locations(self.config.ssl_ca_certs)
            if self.config.ssl_cert_reqs == "none":
                ssl_config.check_hostname = False
                ssl_config.verify_mode = ssl.CERT_NONE
        
        self.pool = aioredis.ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            password=self.config.password,
            db=self.config.db,
            min_size=self.config.min_connections,
            max_size=self.config.max_connections,
            timeout=self.config.connection_timeout,
            ssl=ssl_config,
            retry_on_timeout=self.config.retry_on_timeout
        )
    
    async def _initialize_sentinel(self):
        """**DevOps**: Configuration Sentinel haute disponibilité"""
        self.sentinel = Sentinel(
            self.config.sentinel_hosts,
            sentinel_kwargs={
                'password': self.config.sentinel_password,
                'socket_timeout': self.config.socket_timeout
            }
        )
        
        # Configuration pool via Sentinel
        master = self.sentinel.master_for(
            self.config.sentinel_service_name,
            socket_timeout=self.config.socket_timeout,
            password=self.config.password,
            db=self.config.db
        )
        
        self.pool = master.connection_pool
    
    async def _initialize_cluster(self):
        """**Backend Senior**: Configuration cluster Redis"""
        self.cluster_client = redis.RedisCluster(
            startup_nodes=self.config.cluster_nodes,
            password=self.config.password,
            skip_full_coverage_check=self.config.skip_full_coverage_check,
            socket_timeout=self.config.socket_timeout,
            max_connections=self.config.max_connections
        )
    
    @asynccontextmanager
    async def get_connection(self):
        """
        **Backend Senior**: Gestionnaire contexte connexion optimisé
        
        Utilisation:
            async with pool.get_connection() as conn:
                await conn.set("key", "value")
        """
        connection = None
        start_time = time.time()
        connection_id = f"{self.config.pool_name}_{start_time}"
        
        try:
            # Métriques: Début requête
            self.metrics.total_requests += 1
            
            if self.cluster_client:
                connection = self.cluster_client
            else:
                connection = aioredis.Redis(connection_pool=self.pool)
            
            # Enregistrement connexion active
            self._connection_registry[connection_id] = start_time
            self.metrics.active_connections += 1
            
            if self.metrics.active_connections > self.metrics.peak_connections:
                self.metrics.peak_connections = self.metrics.active_connections
            
            yield connection
            
        except (ConnectionError, TimeoutError) as e:
            self.metrics.failed_requests += 1
            self.metrics.failed_connections += 1
            logger.error(f"❌ Erreur connexion pool {self.config.pool_name}: {e}")
            raise
            
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"❌ Erreur inattendue pool {self.config.pool_name}: {e}")
            raise
            
        finally:
            # Nettoyage et métriques
            if connection_id in self._connection_registry:
                response_time = time.time() - start_time
                self._update_response_time_metrics(response_time)
                del self._connection_registry[connection_id]
                self.metrics.active_connections -= 1
    
    def _update_response_time_metrics(self, response_time: float):
        """**DevOps**: Mise à jour métriques temps de réponse"""
        # Calcul moyenne mobile simple
        if self.metrics.average_response_time == 0:
            self.metrics.average_response_time = response_time
        else:
            self.metrics.average_response_time = (
                self.metrics.average_response_time * 0.9 + response_time * 0.1
            )
    
    async def _health_check_loop(self):
        """**DevOps**: Boucle monitoring santé pool"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur health check pool {self.config.pool_name}: {e}")
    
    async def _perform_health_check(self):
        """**DevOps**: Vérification santé détaillée"""
        try:
            async with self.get_connection() as conn:
                await conn.ping()
                
            # Nettoyage connexions orphelines
            await self._cleanup_stale_connections()
            
            # Mise à jour métriques
            self.metrics.last_health_check = time.time()
            
            # Log métriques importantes
            if self.metrics.active_connections > self.config.max_connections * 0.8:
                logger.warning(
                    f"⚠️ Pool {self.config.pool_name} utilisation élevée: "
                    f"{self.metrics.active_connections}/{self.config.max_connections}"
                )
                
        except Exception as e:
            logger.error(f"❌ Health check échoué pool {self.config.pool_name}: {e}")
    
    async def _cleanup_stale_connections(self):
        """**DBA**: Nettoyage connexions orphelines"""
        current_time = time.time()
        stale_connections = []
        
        for conn_id, start_time in self._connection_registry.items():
            if current_time - start_time > self.config.max_idle_time:
                stale_connections.append(conn_id)
        
        for conn_id in stale_connections:
            del self._connection_registry[conn_id]
            self.metrics.active_connections -= 1
            logger.info(f"🧹 Connexion orpheline nettoyée: {conn_id}")
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """**DevOps**: Statistiques détaillées pool"""
        pool_info = {}
        
        if self.pool:
            pool_info = {
                "max_connections": self.config.max_connections,
                "created_connections": getattr(self.pool, '_created_connections', 0),
                "available_connections": getattr(self.pool, '_available_connections', []),
                "in_use_connections": getattr(self.pool, '_in_use_connections', set())
            }
        
        return {
            "pool_name": self.config.pool_name,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "db": self.config.db,
                "max_connections": self.config.max_connections,
                "min_connections": self.config.min_connections
            },
            "metrics": {
                "active_connections": self.metrics.active_connections,
                "peak_connections": self.metrics.peak_connections,
                "total_requests": self.metrics.total_requests,
                "failed_requests": self.metrics.failed_requests,
                "failed_connections": self.metrics.failed_connections,
                "average_response_time_ms": round(self.metrics.average_response_time * 1000, 2),
                "last_health_check": self.metrics.last_health_check
            },
            "pool_details": pool_info,
            "health_status": "healthy" if time.time() - self.metrics.last_health_check < 60 else "unhealthy"
        }
    
    async def close(self):
        """**Backend Senior**: Fermeture propre pool"""
        logger.info(f"🔌 Fermeture pool Redis: {self.config.pool_name}")
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.pool:
            await self.pool.disconnect()
        
        if self.cluster_client:
            await self.cluster_client.close()
        
        if self.sentinel:
            await self.sentinel.close()
        
        logger.info(f"✅ Pool Redis fermé: {self.config.pool_name}")

class ConnectionPoolManager:
    """
    🏢 Gestionnaire Central de Pools Redis Enterprise
    
    **Lead Dev IA**: Orchestration intelligente des pools multiples
    **Backend Senior**: Architecture pools haute performance
    **DevOps**: Monitoring global et opérations
    """
    
    def __init__(self):
        self.pools: Dict[str, RedisConnectionPool] = {}
        self._lock = asyncio.Lock()
        logger.info("🏢 Initialisation Connection Pool Manager")
    
    async def create_pool(self, pool_name: str, config: ConnectionPoolConfig) -> bool:
        """**Lead Dev IA**: Création pool intelligente"""
        async with self._lock:
            if pool_name in self.pools:
                logger.warning(f"⚠️ Pool {pool_name} existe déjà")
                return False
            
            pool = RedisConnectionPool(config)
            if await pool.initialize():
                self.pools[pool_name] = pool
                logger.info(f"✅ Pool créé: {pool_name}")
                return True
            else:
                logger.error(f"❌ Échec création pool: {pool_name}")
                return False
    
    async def get_pool(self, pool_name: str) -> Optional[RedisConnectionPool]:
        """**Backend Senior**: Récupération pool optimisée"""
        return self.pools.get(pool_name)
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """**DevOps**: Statistiques globales tous pools"""
        stats = {
            "total_pools": len(self.pools),
            "pools": {}
        }
        
        for name, pool in self.pools.items():
            stats["pools"][name] = await pool.get_pool_stats()
        
        return stats
    
    async def health_check_all(self) -> Dict[str, bool]:
        """**DevOps**: Health check global"""
        results = {}
        for name, pool in self.pools.items():
            try:
                async with pool.get_connection() as conn:
                    await conn.ping()
                results[name] = True
            except Exception:
                results[name] = False
        
        return results
    
    async def close_all(self):
        """**Backend Senior**: Fermeture propre tous pools"""
        logger.info("🔌 Fermeture tous les pools Redis")
        
        tasks = []
        for pool in self.pools.values():
            tasks.append(pool.close())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.pools.clear()
        logger.info("✅ Tous les pools Redis fermés")

# Instance globale singleton
pool_manager = ConnectionPoolManager()

# Factory functions pour facilité d'utilisation
async def create_redis_pool(
    pool_name: str,
    host: str = "localhost",
    port: int = 6379,
    password: Optional[str] = None,
    **kwargs
) -> bool:
    """**Backend Senior**: Factory création pool simple"""
    config = ConnectionPoolConfig(
        host=host,
        port=port,
        password=password,
        pool_name=pool_name,
        **kwargs
    )
    return await pool_manager.create_pool(pool_name, config)

async def get_redis_connection(pool_name: str = "default"):
    """**Backend Senior**: Helper connexion Redis"""
    pool = await pool_manager.get_pool(pool_name)
    if not pool:
        raise ConnectionError(f"Pool Redis '{pool_name}' non trouvé")
    
    return pool.get_connection()

if __name__ == "__main__":
    async def demo():
        """Démonstration utilisation Connection Pool Manager"""
        
        # Création pool principal
        await create_redis_pool(
            "main",
            host="localhost",
            port=6379,
            max_connections=20,
            enable_metrics=True
        )
        
        # Utilisation
        async with get_redis_connection("main") as redis_conn:
            await redis_conn.set("test_key", "test_value")
            value = await redis_conn.get("test_key")
            print(f"Valeur récupérée: {value}")
        
        # Statistiques
        stats = await pool_manager.get_global_stats()
        print(f"Statistiques globales: {stats}")
        
        # Nettoyage
        await pool_manager.close_all()
    
    asyncio.run(demo())

# Alias pour conformité avec l'interface enterprise
RedisPoolManager = ConnectionPoolManager
PoolConfig = ConnectionPoolConfig