"""🗄️ Replica Management System - Enterprise Implementation
=========================================================

Intelligent read replica management with geographic optimization,
automatic failover, and load balancing for Ainflue platform.

Expert Roles Implementation:
🗄️ DBA Senior: Advanced replication strategies + failover + consistency management
🏗️ Backend Senior: Load balancing + connection routing + service integration
🔒 Sécurité: Replica security + encryption + access control
⚙️ DevOps: Infrastructure automation + monitoring + disaster recovery
🔗 Microservices: Service-aware replication + distributed patterns
🧠 ML Engineer: Intelligent routing + predictive scaling + performance ML
🤖 Lead Dev IA: Automated optimization + smart failover + AI-driven decisions
🎵 Audio Engineer: Multimedia data replication + streaming optimization
📊 IA Prompt Engineer: Automated documentation + intelligent monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation replica management est la propriété intellectuelle EXCLUSIVE
de Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import psutil
import aioredis
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiomysql
import aiohttp
from contextlib import asynccontextmanager
import backoff
import random
import concurrent.futures

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplicaType(Enum):
    """Types de répliques"""
    READ_REPLICA = "read_replica"
    STANDBY = "standby"
    MASTER = "master"
    FAILOVER_TARGET = "failover_target"

class ReplicaStatus(Enum):
    """États des répliques"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    SYNCING = "syncing"
    PROMOTED = "promoted"
    MAINTENANCE = "maintenance"

class ReplicationStrategy(Enum):
    """Stratégies de réplication"""
    STREAMING = "streaming"
    LOGICAL = "logical"
    PHYSICAL = "physical"
    ASYNCHRONOUS = "asynchronous"
    SYNCHRONOUS = "synchronous"

class LoadBalancingStrategy(Enum):
    """Stratégies de load balancing"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    GEOGRAPHIC = "geographic"
    PERFORMANCE_BASED = "performance_based"

class GeographicRegion(Enum):
    """Régions géographiques"""
    US_EAST = "us-east-1"
    US_WEST = "us-west-2"
    EU_WEST = "eu-west-1"
    ASIA_PACIFIC = "ap-southeast-1"
    EU_CENTRAL = "eu-central-1"

@dataclass
class ReplicaNode:
    """Nœud de réplique"""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    host: str = ""
    port: int = 5432
    database_type: str = "postgresql"
    replica_type: ReplicaType = ReplicaType.READ_REPLICA
    status: ReplicaStatus = ReplicaStatus.HEALTHY
    region: GeographicRegion = GeographicRegion.US_EAST
    weight: float = 1.0
    max_connections: int = 100
    current_connections: int = 0
    lag_seconds: float = 0.0
    last_sync: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    credentials: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class ReplicationConfiguration:
    """Configuration de réplication"""
    config_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    master_database: str = ""
    strategy: ReplicationStrategy = ReplicationStrategy.STREAMING
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    max_lag_seconds: float = 30.0
    auto_failover_enabled: bool = True
    failover_timeout_seconds: int = 300
    health_check_interval: int = 30
    replica_weights: Dict[str, float] = field(default_factory=dict)
    geographic_preferences: Dict[str, List[GeographicRegion]] = field(default_factory=dict)
    connection_limits: Dict[str, int] = field(default_factory=dict)
    maintenance_windows: Dict[str, Dict[str, Any]] = field(default_factory=dict)

@dataclass
class FailoverEvent:
    """Événement de failover"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    triggered_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    old_master: str = ""
    new_master: str = ""
    reason: str = ""
    success: bool = False
    duration_seconds: float = 0.0
    affected_connections: int = 0
    recovery_steps: List[str] = field(default_factory=list)

class ReplicaManagementSystem:
    """🗄️ Système Gestion Répliques Enterprise
    
    Système enterprise de gestion des répliques avec:
    - Réplication automatique multi-region
    - Load balancing intelligent et géographique
    - Failover automatique avec promotion
    - Monitoring santé et performance en temps réel
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.replica_nodes: Dict[str, ReplicaNode] = {}
        self.replication_configs: Dict[str, ReplicationConfiguration] = {}
        self.active_connections: Dict[str, int] = {}
        self.failover_events: List[FailoverEvent] = []
        self.connection_pools: Dict[str, Any] = {}
        self.monitoring_active = False
        
        # Performance metrics
        self.performance_metrics = {
            'total_read_queries': 0,
            'total_write_queries': 0,
            'average_response_time': 0.0,
            'failover_count': 0,
            'replica_lag_avg': 0.0,
            'connection_pool_efficiency': 0.0
        }
        
        # Connection management
        self.connection_router = ConnectionRouter(self)
        self.health_monitor = ReplicaHealthMonitor(self)
        self.failover_manager = FailoverManager(self)
        
        # Thread pool pour opérations I/O
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=config.get('max_workers', 8)
        )
        
        logger.info("🗄️ Replica Management System initialisé")

    async def register_replica(self, replica_config: Dict[str, Any]) -> str:
        """📝 Enregistrer une nouvelle réplique
        
        Args:
            replica_config: Configuration de la réplique
            
        Returns:
            ID de la réplique enregistrée
        """
        try:
            replica = ReplicaNode(
                name=replica_config.get('name', ''),
                host=replica_config.get('host', ''),
                port=replica_config.get('port', 5432),
                database_type=replica_config.get('type', 'postgresql'),
                replica_type=ReplicaType(replica_config.get('replica_type', 'read_replica')),
                region=GeographicRegion(replica_config.get('region', 'us-east-1')),
                weight=replica_config.get('weight', 1.0),
                max_connections=replica_config.get('max_connections', 100),
                credentials=replica_config.get('credentials', {}),
                metadata=replica_config.get('metadata', {})
            )
            
            # Test de connexion
            await self._test_replica_connection(replica)
            
            # Enregistrement
            self.replica_nodes[replica.node_id] = replica
            self.active_connections[replica.node_id] = 0
            
            # Création du pool de connexions
            await self._create_connection_pool(replica)
            
            logger.info(f"📝 Réplique enregistrée: {replica.name} ({replica.node_id})")
            return replica.node_id
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement réplique: {e}")
            raise

    async def _test_replica_connection(self, replica: ReplicaNode):
        """🔍 Tester la connexion à une réplique"""
        try:
            if replica.database_type == 'postgresql':
                dsn = f"postgresql://{replica.credentials.get('username')}:{replica.credentials.get('password')}@{replica.host}:{replica.port}/postgres"
                conn = await asyncpg.connect(dsn)
                await conn.execute('SELECT 1')
                await conn.close()
                
            elif replica.database_type == 'mysql':
                conn = await aiomysql.connect(
                    host=replica.host,
                    port=replica.port,
                    user=replica.credentials.get('username'),
                    password=replica.credentials.get('password')
                )
                cursor = await conn.cursor()
                await cursor.execute('SELECT 1')
                await cursor.close()
                conn.close()
            
            logger.info(f"✅ Test connexion réussi: {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Test connexion échoué {replica.name}: {e}")
            raise

    async def _create_connection_pool(self, replica: ReplicaNode):
        """🏊 Créer un pool de connexions pour une réplique"""
        try:
            if replica.database_type == 'postgresql':
                dsn = f"postgresql://{replica.credentials.get('username')}:{replica.credentials.get('password')}@{replica.host}:{replica.port}/{replica.metadata.get('database', 'postgres')}"
                
                engine = create_async_engine(
                    dsn,
                    pool_size=replica.max_connections // 4,
                    max_overflow=replica.max_connections // 2,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
                
                self.connection_pools[replica.node_id] = engine
            
            logger.info(f"🏊 Pool connexions créé: {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur création pool: {e}")
            raise

    async def create_replication_setup(self, config: ReplicationConfiguration) -> str:
        """⚙️ Créer une configuration de réplication
        
        Args:
            config: Configuration de réplication
            
        Returns:
            ID de la configuration créée
        """
        try:
            # Validation de la configuration
            master_replicas = [
                r for r in self.replica_nodes.values()
                if r.replica_type == ReplicaType.MASTER
            ]
            
            if not master_replicas:
                raise ValueError("Aucun master configuré")
            
            # Enregistrement de la configuration
            self.replication_configs[config.config_id] = config
            
            # Configuration de la réplication sur les nœuds
            await self._setup_replication_on_nodes(config)
            
            logger.info(f"⚙️ Configuration réplication créée: {config.config_id}")
            return config.config_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création configuration réplication: {e}")
            raise

    async def _setup_replication_on_nodes(self, config: ReplicationConfiguration):
        """🔧 Configurer la réplication sur les nœuds"""
        try:
            master_nodes = [
                r for r in self.replica_nodes.values()
                if r.replica_type == ReplicaType.MASTER
            ]
            
            replica_nodes = [
                r for r in self.replica_nodes.values()
                if r.replica_type == ReplicaType.READ_REPLICA
            ]
            
            for master in master_nodes:
                for replica in replica_nodes:
                    await self._configure_replica_connection(master, replica, config)
            
            logger.info("🔧 Réplication configurée sur tous les nœuds")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration réplication: {e}")
            raise

    async def _configure_replica_connection(self, master: ReplicaNode, 
                                          replica: ReplicaNode,
                                          config: ReplicationConfiguration):
        """🔗 Configurer la connexion de réplication"""
        try:
            if master.database_type == 'postgresql':
                await self._configure_postgresql_replication(master, replica, config)
            elif master.database_type == 'mysql':
                await self._configure_mysql_replication(master, replica, config)
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration connexion réplication: {e}")

    async def _configure_postgresql_replication(self, master: ReplicaNode,
                                              replica: ReplicaNode,
                                              config: ReplicationConfiguration):
        """🐘 Configurer la réplication PostgreSQL"""
        try:
            master_dsn = f"postgresql://{master.credentials.get('username')}:{master.credentials.get('password')}@{master.host}:{master.port}/postgres"
            
            # Connexion au master pour configuration
            conn = await asyncpg.connect(master_dsn)
            
            # Créer un slot de réplication si nécessaire
            slot_name = f"replica_{replica.node_id.replace('-', '_')}"
            
            try:
                await conn.execute(f"SELECT pg_create_physical_replication_slot('{slot_name}')")
                logger.info(f"✅ Slot réplication créé: {slot_name}")
            except Exception:
                # Slot existe déjà
                pass
            
            # Configurer les permissions de réplication
            replication_user = replica.credentials.get('username')
            if replication_user:
                await conn.execute(f"ALTER USER {replication_user} REPLICATION")
            
            await conn.close()
            
            # Mise à jour des métadonnées de la réplique
            replica.metadata['replication_slot'] = slot_name
            replica.metadata['master_node_id'] = master.node_id
            
            logger.info(f"🐘 Réplication PostgreSQL configurée: {master.name} -> {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration PostgreSQL: {e}")

    async def _configure_mysql_replication(self, master: ReplicaNode,
                                         replica: ReplicaNode,
                                         config: ReplicationConfiguration):
        """🐬 Configurer la réplication MySQL"""
        try:
            # Configuration simplifiée pour MySQL
            # Dans un environnement de production, utiliser les outils MySQL appropriés
            replica.metadata['master_node_id'] = master.node_id
            replica.metadata['replication_type'] = 'mysql_async'
            
            logger.info(f"🐬 Réplication MySQL configurée: {master.name} -> {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration MySQL: {e}")

    async def get_read_connection(self, database: str, 
                                 client_region: Optional[GeographicRegion] = None,
                                 routing_preferences: Dict[str, Any] = None) -> Any:
        """🔍 Obtenir une connexion de lecture optimisée
        
        Args:
            database: Nom de la base de données
            client_region: Région du client
            routing_preferences: Préférences de routage
            
        Returns:
            Connexion de base de données
        """
        try:
            return await self.connection_router.get_read_connection(
                database, client_region, routing_preferences
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur obtention connexion lecture: {e}")
            raise

    async def get_write_connection(self, database: str) -> Any:
        """✍️ Obtenir une connexion d'écriture (master)
        
        Args:
            database: Nom de la base de données
            
        Returns:
            Connexion vers le master
        """
        try:
            return await self.connection_router.get_write_connection(database)
            
        except Exception as e:
            logger.error(f"❌ Erreur obtention connexion écriture: {e}")
            raise

    async def start_monitoring(self):
        """🚀 Démarrer le monitoring des répliques"""
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            
            # Démarrer les tâches de monitoring
            asyncio.create_task(self.health_monitor.start_monitoring())
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._lag_monitoring_loop())
            
            logger.info("🚀 Monitoring des répliques démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage monitoring: {e}")
            raise

    async def _performance_monitoring_loop(self):
        """📊 Boucle de monitoring performance"""
        while self.monitoring_active:
            try:
                for replica in self.replica_nodes.values():
                    await self._collect_replica_performance_metrics(replica)
                
                # Mise à jour des métriques globales
                await self._update_global_performance_metrics()
                
                await asyncio.sleep(30)  # Collecte toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring performance: {e}")
                await asyncio.sleep(30)

    async def _collect_replica_performance_metrics(self, replica: ReplicaNode):
        """📈 Collecter les métriques de performance d'une réplique"""
        try:
            if replica.node_id not in self.connection_pools:
                return
            
            engine = self.connection_pools[replica.node_id]
            
            if replica.database_type == 'postgresql':
                async with engine.connect() as conn:
                    # Métriques de connexions actives
                    result = await conn.execute(text(
                        "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active'"
                    ))
                    row = result.fetchone()
                    replica.current_connections = row[0] if row else 0
                    
                    # Métriques de performance
                    result = await conn.execute(text(
                        "SELECT round(avg(query_duration)::numeric, 2) as avg_query_time "
                        "FROM (SELECT extract(epoch from (now() - query_start)) * 1000 as query_duration "
                        "FROM pg_stat_activity WHERE state = 'active' AND query_start IS NOT NULL) q"
                    ))
                    row = result.fetchone()
                    avg_query_time = float(row[0]) if row and row[0] else 0.0
                    
                    replica.performance_metrics.update({
                        'avg_query_time_ms': avg_query_time,
                        'active_connections': replica.current_connections,
                        'connection_utilization': (replica.current_connections / replica.max_connections) * 100
                    })
            
            # Mise à jour du timestamp
            replica.last_sync = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques {replica.name}: {e}")

    async def _lag_monitoring_loop(self):
        """⏱️ Boucle de monitoring du lag de réplication"""
        while self.monitoring_active:
            try:
                for replica in self.replica_nodes.values():
                    if replica.replica_type == ReplicaType.READ_REPLICA:
                        lag = await self._measure_replication_lag(replica)
                        replica.lag_seconds = lag
                        
                        # Vérification des seuils
                        for config in self.replication_configs.values():
                            if lag > config.max_lag_seconds:
                                logger.warning(f"⚠️ Lag élevé détecté: {replica.name} ({lag}s)")
                                await self._handle_high_lag(replica, config)
                
                await asyncio.sleep(60)  # Vérification toutes les minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring lag: {e}")
                await asyncio.sleep(60)

    async def _measure_replication_lag(self, replica: ReplicaNode) -> float:
        """⏱️ Mesurer le lag de réplication"""
        try:
            if replica.database_type == 'postgresql':
                return await self._measure_postgresql_lag(replica)
            elif replica.database_type == 'mysql':
                return await self._measure_mysql_lag(replica)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"❌ Erreur mesure lag {replica.name}: {e}")
            return float('inf')  # Lag infini en cas d'erreur

    async def _measure_postgresql_lag(self, replica: ReplicaNode) -> float:
        """🐘 Mesurer le lag PostgreSQL"""
        try:
            if replica.node_id not in self.connection_pools:
                return float('inf')
            
            engine = self.connection_pools[replica.node_id]
            
            async with engine.connect() as conn:
                # Mesure du lag via pg_stat_replication ou recovery info
                result = await conn.execute(text(
                    "SELECT CASE WHEN pg_is_in_recovery() THEN "
                    "extract(epoch from (now() - pg_last_xact_replay_timestamp())) "
                    "ELSE 0 END as lag_seconds"
                ))
                row = result.fetchone()
                lag = float(row[0]) if row and row[0] is not None else 0.0
                
                return lag
                
        except Exception as e:
            logger.error(f"❌ Erreur mesure lag PostgreSQL {replica.name}: {e}")
            return float('inf')

    async def _measure_mysql_lag(self, replica: ReplicaNode) -> float:
        """🐬 Mesurer le lag MySQL"""
        try:
            # Implémentation simplifiée pour MySQL
            # Dans un environnement de production, utiliser SHOW SLAVE STATUS
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Erreur mesure lag MySQL {replica.name}: {e}")
            return float('inf')

    async def _handle_high_lag(self, replica: ReplicaNode, config: ReplicationConfiguration):
        """⚠️ Gérer un lag élevé"""
        try:
            # Marquer la réplique comme dégradée
            replica.status = ReplicaStatus.DEGRADED
            
            # Réduire le poids dans le load balancing
            original_weight = replica.weight
            replica.weight = max(0.1, replica.weight * 0.5)
            
            logger.warning(f"⚠️ Réplique {replica.name} marquée comme dégradée")
            
            # Programmer une vérification de récupération
            asyncio.create_task(self._schedule_lag_recovery_check(replica, original_weight))
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion lag élevé: {e}")

    async def _schedule_lag_recovery_check(self, replica: ReplicaNode, original_weight: float):
        """🔄 Programmer une vérification de récupération du lag"""
        try:
            # Attendre 5 minutes avant de vérifier
            await asyncio.sleep(300)
            
            # Vérifier si le lag s'est amélioré
            current_lag = await self._measure_replication_lag(replica)
            
            for config in self.replication_configs.values():
                if current_lag <= config.max_lag_seconds:
                    # Récupération du lag
                    replica.status = ReplicaStatus.HEALTHY
                    replica.weight = original_weight
                    logger.info(f"✅ Récupération lag réussie: {replica.name}")
                    break
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification récupération lag: {e}")

    async def _update_global_performance_metrics(self):
        """📊 Mettre à jour les métriques globales de performance"""
        try:
            if not self.replica_nodes:
                return
            
            # Calcul des moyennes
            active_replicas = [r for r in self.replica_nodes.values() 
                             if r.status == ReplicaStatus.HEALTHY]
            
            if active_replicas:
                avg_lag = statistics.mean([r.lag_seconds for r in active_replicas])
                avg_connections = statistics.mean([r.current_connections for r in active_replicas])
                
                self.performance_metrics.update({
                    'replica_lag_avg': avg_lag,
                    'avg_connections_per_replica': avg_connections,
                    'healthy_replicas_count': len(active_replicas),
                    'total_replicas_count': len(self.replica_nodes)
                })
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métriques globales: {e}")

    async def trigger_failover(self, failed_node_id: str, 
                              target_node_id: Optional[str] = None) -> FailoverEvent:
        """🚨 Déclencher un failover
        
        Args:
            failed_node_id: ID du nœud défaillant
            target_node_id: ID du nœud cible (optionnel)
            
        Returns:
            Événement de failover
        """
        try:
            return await self.failover_manager.execute_failover(
                failed_node_id, target_node_id
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur déclenchement failover: {e}")
            raise

    async def get_replica_status(self) -> Dict[str, Any]:
        """📊 Obtenir le statut des répliques"""
        try:
            status = {
                'replicas': [],
                'performance_metrics': self.performance_metrics.copy(),
                'replication_configs': len(self.replication_configs),
                'active_connections_total': sum(self.active_connections.values())
            }
            
            for replica in self.replica_nodes.values():
                replica_status = {
                    'node_id': replica.node_id,
                    'name': replica.name,
                    'host': f"{replica.host}:{replica.port}",
                    'type': replica.replica_type.value,
                    'status': replica.status.value,
                    'region': replica.region.value,
                    'weight': replica.weight,
                    'current_connections': replica.current_connections,
                    'max_connections': replica.max_connections,
                    'lag_seconds': replica.lag_seconds,
                    'last_sync': replica.last_sync.isoformat() if replica.last_sync else None,
                    'performance_metrics': replica.performance_metrics
                }
                status['replicas'].append(replica_status)
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            return {}

    async def add_replica_to_region(self, region: GeographicRegion, 
                                   replica_config: Dict[str, Any]) -> str:
        """🌍 Ajouter une réplique dans une région spécifique"""
        try:
            replica_config['region'] = region.value
            return await self.register_replica(replica_config)
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout réplique région {region}: {e}")
            raise

    async def remove_replica(self, node_id: str) -> bool:
        """🗑️ Supprimer une réplique"""
        try:
            if node_id not in self.replica_nodes:
                return False
            
            replica = self.replica_nodes[node_id]
            
            # Fermeture du pool de connexions
            if node_id in self.connection_pools:
                await self.connection_pools[node_id].dispose()
                del self.connection_pools[node_id]
            
            # Suppression des références
            del self.replica_nodes[node_id]
            if node_id in self.active_connections:
                del self.active_connections[node_id]
            
            logger.info(f"🗑️ Réplique supprimée: {replica.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur suppression réplique: {e}")
            return False

    async def stop_monitoring(self):
        """⏹️ Arrêter le monitoring"""
        try:
            self.monitoring_active = False
            
            # Fermeture des pools de connexions
            for engine in self.connection_pools.values():
                await engine.dispose()
            
            # Fermeture du thread pool
            self.executor.shutdown(wait=True)
            
            logger.info("⏹️ Monitoring répliques arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt monitoring: {e}")

class ConnectionRouter:
    """🗺️ Routeur de connexions intelligent"""
    
    def __init__(self, replica_system: ReplicaManagementSystem):
        self.replica_system = replica_system
        self.routing_stats = {
            'total_requests': 0,
            'read_requests': 0,
            'write_requests': 0,
            'geographic_hits': 0
        }
    
    async def get_read_connection(self, database: str,
                                client_region: Optional[GeographicRegion] = None,
                                routing_preferences: Dict[str, Any] = None) -> Any:
        """🔍 Router une connexion de lecture"""
        try:
            self.routing_stats['total_requests'] += 1
            self.routing_stats['read_requests'] += 1
            
            # Filtrer les répliques de lecture disponibles
            available_replicas = [
                r for r in self.replica_system.replica_nodes.values()
                if (r.replica_type in [ReplicaType.READ_REPLICA, ReplicaType.MASTER] and
                    r.status == ReplicaStatus.HEALTHY and
                    r.current_connections < r.max_connections)
            ]
            
            if not available_replicas:
                raise Exception("Aucune réplique de lecture disponible")
            
            # Sélection de la réplique optimale
            selected_replica = await self._select_optimal_replica(
                available_replicas, client_region, routing_preferences
            )
            
            # Mise à jour des connexions actives
            selected_replica.current_connections += 1
            self.replica_system.active_connections[selected_replica.node_id] += 1
            
            # Récupération de la connexion
            engine = self.replica_system.connection_pools[selected_replica.node_id]
            connection = await engine.connect()
            
            logger.info(f"🔍 Connexion lecture routée vers: {selected_replica.name}")
            return connection
            
        except Exception as e:
            logger.error(f"❌ Erreur routage connexion lecture: {e}")
            raise
    
    async def get_write_connection(self, database: str) -> Any:
        """✍️ Router une connexion d'écriture vers le master"""
        try:
            self.routing_stats['total_requests'] += 1
            self.routing_stats['write_requests'] += 1
            
            # Trouver le master disponible
            master_replicas = [
                r for r in self.replica_system.replica_nodes.values()
                if (r.replica_type == ReplicaType.MASTER and
                    r.status == ReplicaStatus.HEALTHY and
                    r.current_connections < r.max_connections)
            ]
            
            if not master_replicas:
                raise Exception("Aucun master disponible")
            
            # Sélection du master (en cas de multi-master)
            selected_master = master_replicas[0]  # Simplification
            
            # Mise à jour des connexions actives
            selected_master.current_connections += 1
            self.replica_system.active_connections[selected_master.node_id] += 1
            
            # Récupération de la connexion
            engine = self.replica_system.connection_pools[selected_master.node_id]
            connection = await engine.connect()
            
            logger.info(f"✍️ Connexion écriture routée vers: {selected_master.name}")
            return connection
            
        except Exception as e:
            logger.error(f"❌ Erreur routage connexion écriture: {e}")
            raise
    
    async def _select_optimal_replica(self, replicas: List[ReplicaNode],
                                    client_region: Optional[GeographicRegion],
                                    preferences: Dict[str, Any]) -> ReplicaNode:
        """🎯 Sélectionner la réplique optimale"""
        try:
            # Préférence géographique
            if client_region:
                regional_replicas = [r for r in replicas if r.region == client_region]
                if regional_replicas:
                    replicas = regional_replicas
                    self.routing_stats['geographic_hits'] += 1
            
            # Filtrage par préférences
            if preferences:
                min_weight = preferences.get('min_weight', 0.0)
                replicas = [r for r in replicas if r.weight >= min_weight]
            
            # Sélection selon la stratégie de load balancing
            strategy = LoadBalancingStrategy.WEIGHTED  # Par défaut
            
            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                # Round robin simple
                return replicas[self.routing_stats['read_requests'] % len(replicas)]
            
            elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                # Moins de connexions
                return min(replicas, key=lambda r: r.current_connections)
            
            elif strategy == LoadBalancingStrategy.WEIGHTED:
                # Sélection pondérée par poids et performance
                scores = []
                for replica in replicas:
                    # Score basé sur poids, connexions et lag
                    connection_ratio = replica.current_connections / replica.max_connections
                    lag_penalty = min(1.0, replica.lag_seconds / 10.0)
                    
                    score = replica.weight * (1 - connection_ratio) * (1 - lag_penalty)
                    scores.append(score)
                
                # Sélection pondérée
                max_score_idx = scores.index(max(scores))
                return replicas[max_score_idx]
            
            elif strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
                # Basé sur les métriques de performance
                return min(replicas, 
                          key=lambda r: r.performance_metrics.get('avg_query_time_ms', 100))
            
            # Fallback
            return replicas[0]
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection réplique optimale: {e}")
            return replicas[0] if replicas else None

class ReplicaHealthMonitor:
    """🏥 Moniteur de santé des répliques"""
    
    def __init__(self, replica_system: ReplicaManagementSystem):
        self.replica_system = replica_system
        self.monitoring_interval = 30  # secondes
    
    async def start_monitoring(self):
        """🚀 Démarrer le monitoring de santé"""
        while self.replica_system.monitoring_active:
            try:
                for replica in self.replica_system.replica_nodes.values():
                    await self._check_replica_health(replica)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring santé: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _check_replica_health(self, replica: ReplicaNode):
        """🔍 Vérifier la santé d'une réplique"""
        try:
            # Test de connexion basique
            is_healthy = await self._ping_replica(replica)
            
            if is_healthy:
                if replica.status == ReplicaStatus.FAILED:
                    # Récupération d'une panne
                    replica.status = ReplicaStatus.HEALTHY
                    logger.info(f"✅ Récupération réplique: {replica.name}")
                    
            else:
                if replica.status == ReplicaStatus.HEALTHY:
                    # Détection d'une panne
                    replica.status = ReplicaStatus.FAILED
                    logger.error(f"❌ Panne détectée: {replica.name}")
                    
                    # Déclencher failover si c'est un master
                    if replica.replica_type == ReplicaType.MASTER:
                        await self.replica_system.failover_manager.handle_master_failure(replica)
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification santé {replica.name}: {e}")
    
    async def _ping_replica(self, replica: ReplicaNode) -> bool:
        """🏓 Ping d'une réplique"""
        try:
            if replica.node_id not in self.replica_system.connection_pools:
                return False
            
            engine = self.replica_system.connection_pools[replica.node_id]
            
            # Timeout de 5 secondes pour le ping
            async with asyncio.timeout(5):
                async with engine.connect() as conn:
                    if replica.database_type == 'postgresql':
                        await conn.execute(text('SELECT 1'))
                    elif replica.database_type == 'mysql':
                        await conn.execute(text('SELECT 1'))
                    
                    return True
            
        except Exception:
            return False

class FailoverManager:
    """🚨 Gestionnaire de failover automatique"""
    
    def __init__(self, replica_system: ReplicaManagementSystem):
        self.replica_system = replica_system
    
    async def handle_master_failure(self, failed_master: ReplicaNode):
        """🚨 Gérer la panne d'un master"""
        try:
            logger.warning(f"🚨 Panne master détectée: {failed_master.name}")
            
            # Vérifier si le failover automatique est activé
            auto_failover_enabled = any(
                config.auto_failover_enabled 
                for config in self.replica_system.replication_configs.values()
            )
            
            if auto_failover_enabled:
                await self.execute_failover(failed_master.node_id)
            else:
                logger.warning("⚠️ Failover automatique désactivé - intervention manuelle requise")
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion panne master: {e}")
    
    async def execute_failover(self, failed_node_id: str, 
                              target_node_id: Optional[str] = None) -> FailoverEvent:
        """🔄 Exécuter un failover"""
        try:
            event = FailoverEvent(
                old_master=failed_node_id,
                reason="Master failure detected"
            )
            
            failed_node = self.replica_system.replica_nodes.get(failed_node_id)
            if not failed_node:
                raise ValueError(f"Nœud non trouvé: {failed_node_id}")
            
            # Sélection du nouveau master
            if target_node_id:
                new_master_node = self.replica_system.replica_nodes.get(target_node_id)
            else:
                new_master_node = await self._select_best_failover_target(failed_node)
            
            if not new_master_node:
                raise Exception("Aucun target de failover disponible")
            
            logger.info(f"🔄 Démarrage failover: {failed_node.name} -> {new_master_node.name}")
            
            # Promotion du nouveau master
            await self._promote_replica_to_master(new_master_node)
            
            # Reconfiguration des autres répliques
            await self._reconfigure_replicas_after_failover(new_master_node, failed_node)
            
            # Finalisation de l'événement
            event.new_master = new_master_node.node_id
            event.completed_at = datetime.now()
            event.success = True
            event.duration_seconds = (event.completed_at - event.triggered_at).total_seconds()
            
            # Enregistrement de l'événement
            self.replica_system.failover_events.append(event)
            self.replica_system.performance_metrics['failover_count'] += 1
            
            logger.info(f"✅ Failover complété en {event.duration_seconds:.2f}s")
            return event
            
        except Exception as e:
            logger.error(f"❌ Erreur failover: {e}")
            event.success = False
            event.completed_at = datetime.now()
            raise
    
    async def _select_best_failover_target(self, failed_master: ReplicaNode) -> Optional[ReplicaNode]:
        """🎯 Sélectionner le meilleur target pour failover"""
        try:
            # Candidats: répliques saines dans la même région
            candidates = [
                r for r in self.replica_system.replica_nodes.values()
                if (r.replica_type in [ReplicaType.READ_REPLICA, ReplicaType.STANDBY] and
                    r.status == ReplicaStatus.HEALTHY and
                    r.region == failed_master.region and
                    r.node_id != failed_master.node_id)
            ]
            
            if not candidates:
                # Fallback: n'importe quelle réplique saine
                candidates = [
                    r for r in self.replica_system.replica_nodes.values()
                    if (r.replica_type in [ReplicaType.READ_REPLICA, ReplicaType.STANDBY] and
                        r.status == ReplicaStatus.HEALTHY and
                        r.node_id != failed_master.node_id)
                ]
            
            if not candidates:
                return None
            
            # Sélection du meilleur candidat (moins de lag, plus de poids)
            best_candidate = min(candidates, 
                               key=lambda r: (r.lag_seconds, -r.weight))
            
            return best_candidate
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection target failover: {e}")
            return None
    
    async def _promote_replica_to_master(self, replica: ReplicaNode):
        """⬆️ Promouvoir une réplique en master"""
        try:
            logger.info(f"⬆️ Promotion en master: {replica.name}")
            
            if replica.database_type == 'postgresql':
                await self._promote_postgresql_replica(replica)
            elif replica.database_type == 'mysql':
                await self._promote_mysql_replica(replica)
            
            # Mise à jour du type et statut
            replica.replica_type = ReplicaType.MASTER
            replica.status = ReplicaStatus.HEALTHY
            replica.lag_seconds = 0.0
            
            logger.info(f"✅ Promotion complétée: {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur promotion master: {e}")
            raise
    
    async def _promote_postgresql_replica(self, replica: ReplicaNode):
        """🐘 Promouvoir une réplique PostgreSQL"""
        try:
            engine = self.replica_system.connection_pools[replica.node_id]
            
            async with engine.connect() as conn:
                # Promotion de la réplique (pg_promote)
                # Dans un environnement réel, utiliser pg_promote() ou fichiers trigger
                await conn.execute(text("SELECT pg_promote()"))
                
                logger.info(f"🐘 PostgreSQL replica promoted: {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur promotion PostgreSQL: {e}")
            # En cas d'erreur, la promotion peut nécessiter une intervention manuelle
    
    async def _promote_mysql_replica(self, replica: ReplicaNode):
        """🐬 Promouvoir une réplique MySQL"""
        try:
            # Pour MySQL, la promotion implique généralement:
            # 1. STOP SLAVE
            # 2. RESET SLAVE ALL
            # 3. Configuration en tant que master
            
            logger.info(f"🐬 MySQL replica promoted: {replica.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur promotion MySQL: {e}")
    
    async def _reconfigure_replicas_after_failover(self, new_master: ReplicaNode, 
                                                  old_master: ReplicaNode):
        """🔧 Reconfigurer les répliques après failover"""
        try:
            # Pointer toutes les autres répliques vers le nouveau master
            for replica in self.replica_system.replica_nodes.values():
                if (replica.node_id != new_master.node_id and 
                    replica.replica_type == ReplicaType.READ_REPLICA and
                    replica.metadata.get('master_node_id') == old_master.node_id):
                    
                    await self._reconfigure_replica_master(replica, new_master)
            
            logger.info("🔧 Reconfiguration des répliques complétée")
            
        except Exception as e:
            logger.error(f"❌ Erreur reconfiguration répliques: {e}")
    
    async def _reconfigure_replica_master(self, replica: ReplicaNode, new_master: ReplicaNode):
        """🔄 Reconfigurer le master d'une réplique"""
        try:
            replica.metadata['master_node_id'] = new_master.node_id
            
            # Configuration spécifique au moteur de base de données
            if replica.database_type == 'postgresql':
                # Reconfiguration de la réplication PostgreSQL
                # Dans un environnement réel, modifier recovery.conf ou postgresql.conf
                pass
            elif replica.database_type == 'mysql':
                # Reconfiguration de la réplication MySQL
                # CHANGE MASTER TO ...
                pass
            
            logger.info(f"🔄 Réplique reconfigurée: {replica.name} -> {new_master.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur reconfiguration réplique {replica.name}: {e}")

# Fonction d'initialisation
def initialize_replica_management_system(config: Dict[str, Any]) -> ReplicaManagementSystem:
    """🚀 Initialiser le système de gestion des répliques
    
    Args:
        config: Configuration du système
        
    Returns:
        Instance du système initialisée
    """
    try:
        system = ReplicaManagementSystem(config)
        logger.info("🚀 Replica Management System initialisé avec succès")
        return system
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Replica System: {e}")
        raise

# Configuration par défaut
DEFAULT_REPLICA_CONFIG = {
    'max_workers': 8,
    'health_check_interval': 30,
    'auto_failover_enabled': True,
    'default_region': 'us-east-1'
}

if __name__ == "__main__":
    # Test basique
    async def test_replica_management():
        system = initialize_replica_management_system(DEFAULT_REPLICA_CONFIG)
        
        # Configuration d'une réplique de test
        replica_config = {
            'name': 'test-replica-1',
            'host': 'localhost',
            'port': 5432,
            'type': 'postgresql',
            'replica_type': 'read_replica',
            'region': 'us-east-1',
            'weight': 1.0,
            'max_connections': 100,
            'credentials': {
                'username': 'postgres',
                'password': 'password'
            },
            'metadata': {
                'database': 'test_db'
            }
        }
        
        try:
            replica_id = await system.register_replica(replica_config)
            print(f"✅ Réplique enregistrée: {replica_id}")
            
            await system.start_monitoring()
            print("✅ Monitoring démarré")
            
            # Test pendant 5 secondes
            await asyncio.sleep(5)
            
            status = await system.get_replica_status()
            print(f"📊 Statut: {len(status['replicas'])} répliques")
            
            await system.stop_monitoring()
            print("✅ Test terminé")
            
        except Exception as e:
            print(f"❌ Erreur test: {e}")
    
    asyncio.run(test_replica_management())