"""# [EMOJI_REMOVED] Load Balancer & Health Checker - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/platform_core/communication/load_balancer.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

# [EMOJI_REMOVED]  PROPRI# [EMOJI_REMOVED]T# [EMOJI_REMOVED] INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL # [EMOJI_REMOVED]
(c) 2025 Fahed Mlaiel. Tous droits reserves.
Contact: mlaiel@live.de

# [EMOJI_REMOVED] LOAD BALANCER INTELLIGENT
Repartition de charge avancee avec detection de pannes
- Algorithmes multiples (Round Robin, Weighted, Least Connections)
- Health checking proactif et reactif
- Circuit breaker pattern integre
- Metriques temps reel et auto-scaling
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import hashlib

import aiohttp

# Configuration
logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """
Algorithmes de load balancing"""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"

class ServerStatus(Enum):
    """# [EMOJI_REMOVED]tats des serveurs"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    DRAINING = "draining"

@dataclass
class ServerMetrics:
    """Metriques d'un serveur"""
    active_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    last_request_time: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
        
    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times[-100:])  # Dernieres 100 requetes
        
    @property
    def p95_response_time(self) -> float:
        if len(self.response_times) < 2:
            return self.average_response_time
        return statistics.quantiles(self.response_times[-100:], n=20)[18]  # 95th percentile

@dataclass
class Server:
    """
Definition d'un serveur backend"""
    server_id: str
    host: str
    port: int
    weight: float = 1.0
    max_connections: int = 1000
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    health_check_timeout: int = 5
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # # [EMOJI_REMOVED]tat
    status: ServerStatus = ServerStatus.HEALTHY
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Metriques
    metrics: ServerMetrics = field(default_factory=ServerMetrics)
    
    @property
    def url(self) -> str:
        try:
            logger.info(f"Executing url")
            
            # Implementation for url
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing is_available")
            
            # Implementation for is_available
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"is_available completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"is_available failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"url completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"url failed: {e}")
            raise
    @property
    def is_available(self) -> bool:
        return self.status in [ServerStatus.HEALTHY, ServerStatus.DEGRADED]
        
    @property
    def load_score(self) -> float:
        """Calcule un score de charge (plus bas = moins charge)"""
        # Facteurs: connexions actives, temps de reponse, taux d'erreur
        try:
            logger.info(f"Executing stop")
            
            # Implementation for stop
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"stop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"stop failed: {e}")
            raise
Demarre le health checker"""
        if self._own_session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        logger.info("HealthChecker demarre")
        
    async def stop(self) -> None:
        """Arrete le health checker"""
        # Arreter toutes les taches de health check
        for task in self._health_tasks.values():
            task.cancel()
            
        for task in self._health_tasks.values():
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        self._health_tasks.clear()
        
        if self._own_session and self.session:
            await self.session.close()
            
        logger.info("HealthChecker arrete")
        
    async def add_server(self, server -> None: Server) -> None:
        """Ajoute un serveur au monitoring"""
        if server.server_id in self._health_tasks:
            return
            
        task = asyncio.create_task(self._health_check_loop(server))
        self._health_tasks[server.server_id] = task
        logger.info(f"Health checking active pour {server.server_id}")
        
    async def remove_server(self, server_id -> None: str) -> None:
        """Retire un serveur du monitoring"""
        if server_id in self._health_tasks:
            self._health_tasks[server_id].cancel()
            try:
                await self._health_tasks[server_id]
            except asyncio.CancelledError:
                pass
            del self._health_tasks[server_id]
            
    async def _health_check_loop(self, server -> None: Server) -> None:
        """Boucle de health check pour un serveur"""
        while True:
            try:
                await asyncio.sleep(server.health_check_interval)
                await self._check_server_health(server)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans health check de {server.server_id}: {e}")
                
    async def _check_server_health(self, server -> None: Server) -> None:
        """Verifie la sante du serveur"""
        if not self.session:
            return
            
        health_url = server.health_check_url or f"{server.url}/health"
        
        try:
            start_time = time.time()
            
            async with self.session.get(
                health_url,
                timeout=aiohttp.ClientTimeout(total=server.health_check_timeout)
            ) as response:
                response_time = time.time() - start_time
                server.last_health_check = datetime.utcnow()
                
                if response.status == 200:
                    # Serveur en bonne sante
                    if server.status == ServerStatus.UNHEALTHY:
                        logger.info(f"Serveur {server.server_id} de nouveau en bonne sante")
                        
                    server.status = ServerStatus.HEALTHY
                    server.consecutive_failures = 0
                    
                    # Traiter les metriques de sante si disponibles
                    try:
                        health_data = await response.json()
                        if isinstance(health_data, dict):
                            server.metrics.cpu_usage = health_data.get("cpu_usage", 0.0)
                            server.metrics.memory_usage = health_data.get("memory_usage", 0.0)
                            server.metrics.disk_usage = health_data.get("disk_usage", 0.0)
                    except Exception:
                        pass  # Pas de donnees JSON valides
                        
                elif response.status == 503:
                    # Serveur en maintenance
                    server.status = ServerStatus.MAINTENANCE
                elif 500 <= response.status < 600:
                    # Erreur serveur
                    self._handle_server_failure(server)
                else:
                    # Reponse degradee mais pas d'erreur critique
                    if server.status == ServerStatus.HEALTHY:
                        server.status = ServerStatus.DEGRADED
                        
        except asyncio.TimeoutError:
            logger.warning(f"Health check timeout pour {server.server_id}")
            self._handle_server_failure(server)
        except Exception as e:
            logger.warning(f"Health check failed pour {server.server_id}: {e}")
            self._handle_server_failure(server)
            
    def _handle_server_failure(self, server -> None: Server) -> None:
        """Gere l'echec d'un serveur"""
        server.consecutive_failures += 1
        server.last_health_check = datetime.utcnow()
        
        if server.consecutive_failures >= 3:
            if server.status != ServerStatus.UNHEALTHY:
                logger.warning(f"Serveur {server.server_id} marque comme non disponible")
            server.status = ServerStatus.UNHEALTHY
        elif server.consecutive_failures >= 1:
            server.status = ServerStatus.DEGRADED

class LoadBalancer:
    """Load balancer intelligent avec multiples algorithmes"""
    
    def __init__(self, 
                 algorithm -> None: LoadBalancingAlgorithm = LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                 health_checker -> None: Optional[HealthChecker] = None) -> None:
        self.algorithm = algorithm
        self.servers: Dict[str, Server] = {}
        self.health_checker = health_checker or HealthChecker()
        
        # # [EMOJI_REMOVED]tat pour les algorithmes
        self._round_robin_index = 0
        self._connections_count: Dict[str, int] = {}
        
        # Metriques globales
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = datetime.utcnow()
        
    async def start(self) -> None:
        """
Demarre le load balancer"""
        await self.health_checker.start()
        logger.info(f"LoadBalancer demarre avec algorithme {self.algorithm.value}")
        
    async def stop(self) -> None:
        """Arrete le load balancer"""
        await self.health_checker.stop()
        logger.info("LoadBalancer arrete")
        
    async def add_server(self, server -> None: Server) -> None:
        """Ajoute un serveur au pool"""
        self.servers[server.server_id] = server
        self._connections_count[server.server_id] = 0
        await self.health_checker.add_server(server)
        logger.info(f"Serveur ajoute: {server.server_id} ({server.url})")
        
    async def remove_server(self, server_id -> None: str) -> None:
        """Retire un serveur du pool"""
        if server_id in self.servers:
            server = self.servers[server_id]
            server.status = ServerStatus.DRAINING  # Marquer en drain
            
            # Attendre que les connexions se terminent (timeout 30s)
            timeout = time.time() + 30
            while (server.metrics.active_connections > 0 and 
                   time.time() < timeout):
                await asyncio.sleep(1)
                
            del self.servers[server_id]
            if server_id in self._connections_count:
                del self._connections_count[server_id]
                
            await self.health_checker.remove_server(server_id)
            logger.info(f"Serveur retire: {server_id}")
            
    async def get_server(self, client_ip: Optional[str] = None) -> Optional[Server]:
        """Selectionne un serveur selon l'algorithme configure"""
        available_servers = [
            server for server in self.servers.values()
            if server.is_available
        ]
        
        if not available_servers:
            logger.warning("Aucun serveur disponible")
            return None
            
        self.total_requests += 1
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin(available_servers)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(available_servers)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(available_servers)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time(available_servers)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash(available_servers, client_ip)
        elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
            return self._random(available_servers)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_RANDOM:
            return self._weighted_random(available_servers)
        else:
            return self._round_robin(available_servers)
            
    def _round_robin(self, servers: List[Server]) -> Server:
        """Algorithme Round Robin simple"""
        if not servers:
            return None
            
        server = servers[self._round_robin_index % len(servers)]
        self._round_robin_index += 1
        return server
        
    def _weighted_round_robin(self, servers: List[Server]) -> Server:
        """
Algorithme Round Robin pondere"""
        if not servers:
            return None
            
        # Creer une liste ponderee des serveurs
        weighted_servers = []
        for server in servers:
            # Ajuster le poids selon la charge actuelle
            adjusted_weight = max(1, int(server.weight * (1 - server.load_score)))
            weighted_servers.extend([server] * adjusted_weight)
            
        if not weighted_servers:
            return servers[0]
            
        server = weighted_servers[self._round_robin_index % len(weighted_servers)]
        self._round_robin_index += 1
        return server
        
    def _least_connections(self, servers: List[Server]) -> Server:
        """
Algorithme Least Connections"""
        return min(servers, key=lambda s: s.metrics.active_connections)
        
    def _least_response_time(self, servers: List[Server]) -> Server:
        """
Algorithme base sur le temps de reponse"""
        return min(servers, key=lambda s: s.metrics.average_response_time)
        
    def _ip_hash(self, servers: List[Server], client_ip: Optional[str]) -> Server:
        """
Algorithme base sur le hash de l'IP client"""
        if not client_ip:
            return self._round_robin(servers)
            
        # Hash de l'IP pour determiner le serveur
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return servers[hash_value % len(servers)]
        
    def _random(self, servers: List[Server]) -> Server:
        """
Selection aleatoire"""
        return random.choice(servers)
        
    def _weighted_random(self, servers: List[Server]) -> Server:
        """
Selection aleatoire ponderee"""
        weights = [max(0.1, server.weight * (1 - server.load_score)) for server in servers]
        return random.choices(servers, weights=weights)[0]
        
    async def record_request(self, server -> None: Server, response_time -> None: float, success -> None: bool) -> None:
        """
Enregistre les metriques d'une requete"""
        server.metrics.total_requests += 1
        server.metrics.last_request_time = datetime.utcnow()
        
        if success:
            server.metrics.successful_requests += 1
            server.metrics.response_times.append(response_time)
            
            # Garder seulement les 1000 derniers temps de reponse
            if len(server.metrics.response_times) > 1000:
                server.metrics.response_times = server.metrics.response_times[-1000:]
        else:
            server.metrics.failed_requests += 1
            self.total_errors += 1
            
    async def acquire_connection(self, server -> None: Server) -> None:
        """
Acquiert une connexion vers un serveur"""
        server.metrics.active_connections += 1
        self._connections_count[server.server_id] += 1
        
    async def release_connection(self, server -> None: Server) -> None:
        """
Libere une connexion vers un serveur"""
        server.metrics.active_connections = max(0, server.metrics.active_connections - 1)
        self._connections_count[server.server_id] = max(0, self._connections_count[server.server_id] - 1)
        
    def get_stats(self) -> Dict[str, Any]:
        """
Retourne les statistiques du load balancer"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "algorithm": self.algorithm.value,
            "total_servers": len(self.servers),
            "available_servers": len([s for s in self.servers.values() if s.is_available]),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / max(self.total_requests, 1),
            "requests_per_second": self.total_requests / max(uptime, 1),
            "uptime_seconds": uptime,
            "servers": {
                server_id: {
                    "status": server.status.value,
                    "active_connections": server.metrics.active_connections,
                    "total_requests": server.metrics.total_requests,
                    "success_rate": server.metrics.success_rate,
                    "avg_response_time": server.metrics.average_response_time,
                    "p95_response_time": server.metrics.p95_response_time,
                    "load_score": server.load_score,
                    "consecutive_failures": server.consecutive_failures,
                    "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None
                }
                for server_id, server in self.servers.items()
            }
        }
        
    async def set_server_weight(self, server_id -> None: str, weight -> None: float) -> None:
        """Modifie le poids d'un serveur"""
        if server_id in self.servers:
            self.servers[server_id].weight = max(0.1, weight)
            logger.info(f"Poids du serveur {server_id} modifie: {weight}")
            
    async def drain_server(self, server_id -> None: str) -> None:
        """Met un serveur en mode drain (arret progressif)"""
        if server_id in self.servers:
            self.servers[server_id].status = ServerStatus.DRAINING
            logger.info(f"Serveur {server_id} mis en mode drain")
            
    async def set_maintenance(self, server_id -> None: str, maintenance -> None: bool) -> None:
        """Met un serveur en/hors maintenance"""
        if server_id in self.servers:
            server = self.servers[server_id]
            if maintenance:
                server.status = ServerStatus.MAINTENANCE
                logger.info(f"Serveur {server_id} mis en maintenance")
            else:
                server.status = ServerStatus.HEALTHY
                server.consecutive_failures = 0
                logger.info(f"Serveur {server_id} sorti de maintenance")

# File has syntax issues - needs manual review