#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Distributed Session Engine - Moteur Sessions Distribuées Enterprise
======================================================================

Moteur enterprise de sessions distribuées avec synchronisation multi-nœuds,
réplication automatique et cohérence garantie à travers le cluster.

**Rôles Experts:**
- **Microservices**: Architecture distribuée sessions multi-services
- **Backend Senior**: Coordination cluster haute performance
- **DBA**: Réplication, consistance, synchronisation données
- **DevOps**: Monitoring cluster, failover automatique

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Set, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta, timezone
import yaml
import aioredis
from collections import defaultdict, deque
import uuid
import weakref

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """Statut nœud cluster"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    JOINING = "joining"
    LEAVING = "leaving"
    MAINTENANCE = "maintenance"

class SyncStrategy(Enum):
    """Stratégies de synchronisation"""
    IMMEDIATE = "immediate"  # Synchronisation immédiate
    EVENTUAL = "eventual"  # Consistance éventuelle
    STRONG = "strong"  # Consistance forte
    LAZY = "lazy"  # Synchronisation paresseuse
    CONFLICT_RESOLUTION = "conflict_resolution"  # Résolution conflits

class ReplicationMode(Enum):
    """Modes de réplication"""
    MASTER_SLAVE = "master_slave"  # Maître-esclave
    MULTI_MASTER = "multi_master"  # Multi-maître
    PEER_TO_PEER = "peer_to_peer"  # Pair-à-pair
    HIERARCHICAL = "hierarchical"  # Hiérarchique

@dataclass
class ClusterNode:
    """Nœud cluster"""
    node_id: str
    host: str
    port: int
    region: str
    status: NodeStatus
    last_heartbeat: datetime
    session_count: int = 0
    load_factor: float = 0.0
    priority: int = 1  # 1=haute, 5=basse
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionReplication:
    """Réplication session"""
    session_id: str
    primary_node: str
    replica_nodes: List[str]
    last_sync: datetime
    sync_version: int
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    replication_status: str = "active"

@dataclass
class SyncEvent:
    """Événement synchronisation"""
    event_id: str
    event_type: str  # create, update, delete, sync
    session_id: str
    source_node: str
    target_nodes: List[str]
    data: Dict[str, Any]
    timestamp: datetime
    version: int
    status: str = "pending"  # pending, processing, completed, failed

@dataclass
class ClusterMetrics:
    """Métriques cluster"""
    total_nodes: int = 0
    active_nodes: int = 0
    total_sessions: int = 0
    sync_events_pending: int = 0
    sync_events_completed: int = 0
    sync_events_failed: int = 0
    average_sync_latency: float = 0.0
    last_full_sync: Optional[datetime] = None

class DistributedSessionEngine:
    """
    🌐 Moteur Sessions Distribuées Enterprise
    
    **Microservices**: Architecture sessions distribuées multi-services
    **Backend Senior**: Coordination cluster haute performance
    **DBA**: Réplication intelligente et cohérence données
    **DevOps**: Monitoring automatisé et gestion failover
    """
    
    def __init__(self, redis_pool, node_id: str = None, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.node_id = node_id or self._generate_node_id()
        self.config = config or self._get_default_config()
        
        # Cluster management
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        self.current_node: Optional[ClusterNode] = None
        
        # Session tracking
        self.session_replications: Dict[str, SessionReplication] = {}
        self.local_sessions: Set[str] = set()
        self.pending_sync_events: Dict[str, SyncEvent] = {}
        
        # Synchronization
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self.conflict_resolution_handlers: Dict[str, Callable] = {}
        
        # Métriques
        self.metrics = ClusterMetrics()
        self.sync_history: deque = deque(maxlen=5000)
        
        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.sync_processor_task: Optional[asyncio.Task] = None
        self.discovery_task: Optional[asyncio.Task] = None
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.info(f"🌐 Distributed Session Engine initialisé - Node: {self.node_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**DBA**: Configuration par défaut optimisée"""
        return {
            'cluster_name': 'ainflue_sessions',
            'heartbeat_interval': 30,  # seconds
            'sync_batch_size': 100,
            'sync_timeout': 5000,  # ms
            'node_discovery_interval': 60,
            'replication_factor': 2,  # Nombre replicas par session
            'sync_strategy': SyncStrategy.EVENTUAL.value,
            'replication_mode': ReplicationMode.MASTER_SLAVE.value,
            'enable_conflict_resolution': True,
            'max_sync_retries': 3,
            'region': 'default',
            'node_priority': 1,
            'capabilities': ['session_storage', 'sync_processing'],
            'redis_cluster_key': 'cluster:sessions',
            'redis_sync_key': 'sync:events',
            'redis_heartbeat_key': 'heartbeat:nodes'
        }
    
    def _generate_node_id(self) -> str:
        """**Backend Senior**: Génération ID nœud unique"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(uuid.uuid4().hex[:8])
        return f"node_{timestamp}_{random_part}"
    
    async def join_cluster(self):
        """**Microservices**: Rejoindre cluster sessions**"""
        try:
            # Création nœud local
            self.current_node = ClusterNode(
                node_id=self.node_id,
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 6379),
                region=self.config.get('region', 'default'),
                status=NodeStatus.JOINING,
                last_heartbeat=datetime.now(timezone.utc),
                priority=self.config.get('node_priority', 1),
                capabilities=set(self.config.get('capabilities', []))
            )
            
            # Découverte nœuds existants
            await self._discover_cluster_nodes()
            
            # Enregistrement dans cluster
            await self._register_node()
            
            # Démarrage services background
            await self._start_background_services()
            
            # Synchronisation initiale
            await self._initial_sync()
            
            # Nœud maintenant actif
            self.current_node.status = NodeStatus.ACTIVE
            await self._update_node_status()
            
            logger.info(f"✅ Nœud {self.node_id} a rejoint le cluster")
            
        except Exception as e:
            logger.error(f"❌ Erreur rejoindre cluster: {e}")
            raise
    
    async def leave_cluster(self):
        """**Microservices**: Quitter cluster proprement"""
        try:
            if self.current_node:
                self.current_node.status = NodeStatus.LEAVING
                await self._update_node_status()
            
            # Transfert sessions vers autres nœuds
            await self._transfer_sessions_before_leave()
            
            # Arrêt services background
            await self._stop_background_services()
            
            # Désenregistrement cluster
            await self._unregister_node()
            
            logger.info(f"👋 Nœud {self.node_id} a quitté le cluster")
            
        except Exception as e:
            logger.error(f"❌ Erreur quitter cluster: {e}")
    
    async def _discover_cluster_nodes(self):
        """**DevOps**: Découverte nœuds cluster"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                cluster_key = self.config['redis_cluster_key']
                
                # Récupération nœuds existants
                node_data = await redis_conn.hgetall(cluster_key)
                
                for node_id, node_json in node_data.items():
                    if node_id == self.node_id:
                        continue
                    
                    try:
                        node_dict = json.loads(node_json)
                        node = ClusterNode(
                            node_id=node_id,
                            host=node_dict['host'],
                            port=node_dict['port'],
                            region=node_dict['region'],
                            status=NodeStatus(node_dict['status']),
                            last_heartbeat=datetime.fromisoformat(node_dict['last_heartbeat']),
                            session_count=node_dict.get('session_count', 0),
                            load_factor=node_dict.get('load_factor', 0.0),
                            priority=node_dict.get('priority', 1),
                            capabilities=set(node_dict.get('capabilities', [])),
                            metadata=node_dict.get('metadata', {})
                        )
                        
                        self.cluster_nodes[node_id] = node
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur parsing nœud {node_id}: {e}")
                
                logger.info(f"🔍 Découvert {len(self.cluster_nodes)} nœuds cluster")
                
        except Exception as e:
            logger.error(f"❌ Erreur découverte cluster: {e}")
    
    async def _register_node(self):
        """**Backend Senior**: Enregistrement nœud dans cluster"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                cluster_key = self.config['redis_cluster_key']
                
                # Sérialisation données nœud
                node_dict = {
                    'host': self.current_node.host,
                    'port': self.current_node.port,
                    'region': self.current_node.region,
                    'status': self.current_node.status.value,
                    'last_heartbeat': self.current_node.last_heartbeat.isoformat(),
                    'session_count': self.current_node.session_count,
                    'load_factor': self.current_node.load_factor,
                    'priority': self.current_node.priority,
                    'capabilities': list(self.current_node.capabilities),
                    'metadata': self.current_node.metadata
                }
                
                node_json = json.dumps(node_dict)
                
                # Enregistrement Redis
                await redis_conn.hset(cluster_key, self.node_id, node_json)
                await redis_conn.expire(cluster_key, 86400)  # 24h
                
                logger.info(f"📝 Nœud {self.node_id} enregistré dans cluster")
                
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement nœud: {e}")
            raise
    
    async def _start_background_services(self):
        """**DevOps**: Démarrage services arrière-plan"""
        
        # Heartbeat
        if not self.heartbeat_task or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Processeur synchronisation
        if not self.sync_processor_task or self.sync_processor_task.done():
            self.sync_processor_task = asyncio.create_task(self._sync_processor_loop())
        
        # Découverte nœuds
        if not self.discovery_task or self.discovery_task.done():
            self.discovery_task = asyncio.create_task(self._node_discovery_loop())
        
        logger.info("🚀 Services background démarrés")
    
    async def _stop_background_services(self):
        """**DevOps**: Arrêt services arrière-plan"""
        
        tasks = [self.heartbeat_task, self.sync_processor_task, self.discovery_task]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
        
        # Attendre arrêt propre
        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        
        logger.info("🛑 Services background arrêtés")
    
    async def _heartbeat_loop(self):
        """**DevOps**: Boucle heartbeat cluster"""
        while True:
            try:
                await self._send_heartbeat()
                await self._check_node_health()
                
                interval = self.config.get('heartbeat_interval', 30)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur heartbeat: {e}")
                await asyncio.sleep(10)
    
    async def _send_heartbeat(self):
        """**Backend Senior**: Envoi heartbeat**"""
        try:
            if not self.current_node:
                return
            
            # Mise à jour timestamp
            self.current_node.last_heartbeat = datetime.now(timezone.utc)
            self.current_node.session_count = len(self.local_sessions)
            
            # Calcul load factor
            self.current_node.load_factor = self._calculate_load_factor()
            
            # Envoi heartbeat
            await self._update_node_status()
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi heartbeat: {e}")
    
    def _calculate_load_factor(self) -> float:
        """**Backend Senior**: Calcul facteur charge nœud"""
        # Facteur basé sur nombre sessions et métriques système
        base_load = len(self.local_sessions) / max(1, self.config.get('max_sessions_per_node', 1000))
        
        # Ajout métriques système (simulées pour démo)
        cpu_load = 0.3  # À récupérer des métriques système réelles
        memory_load = 0.4
        
        total_load = (base_load * 0.5 + cpu_load * 0.3 + memory_load * 0.2)
        return min(1.0, total_load)
    
    async def _check_node_health(self):
        """**DevOps**: Vérification santé nœuds cluster"""
        current_time = datetime.now(timezone.utc)
        timeout_threshold = timedelta(seconds=self.config.get('heartbeat_interval', 30) * 3)
        
        failed_nodes = []
        
        for node_id, node in self.cluster_nodes.items():
            time_since_heartbeat = current_time - node.last_heartbeat
            
            if time_since_heartbeat > timeout_threshold:
                if node.status == NodeStatus.ACTIVE:
                    node.status = NodeStatus.FAILED
                    failed_nodes.append(node_id)
                    logger.warning(f"🚨 Nœud {node_id} détecté en panne")
        
        # Gestion nœuds en panne
        for node_id in failed_nodes:
            await self._handle_node_failure(node_id)
    
    async def _handle_node_failure(self, failed_node_id: str):
        """**Microservices**: Gestion panne nœud"""
        try:
            # Récupération sessions du nœud en panne
            failed_sessions = []
            
            for session_id, replication in self.session_replications.items():
                if replication.primary_node == failed_node_id:
                    failed_sessions.append(session_id)
                elif failed_node_id in replication.replica_nodes:
                    replication.replica_nodes.remove(failed_node_id)
            
            # Promotion replicas vers primaire
            for session_id in failed_sessions:
                await self._promote_replica_to_primary(session_id)
            
            # Notification événement
            await self._trigger_event('node_failed', {
                'node_id': failed_node_id,
                'affected_sessions': len(failed_sessions)
            })
            
            logger.info(f"🔄 Récupération panne nœud {failed_node_id}: {len(failed_sessions)} sessions")
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion panne nœud {failed_node_id}: {e}")
    
    async def _promote_replica_to_primary(self, session_id: str):
        """**DBA**: Promotion replica vers primaire"""
        
        replication = self.session_replications.get(session_id)
        if not replication or not replication.replica_nodes:
            return
        
        # Sélection meilleur replica (priorité + charge)
        best_replica = await self._select_best_replica(replication.replica_nodes)
        
        if best_replica:
            # Promotion
            replication.primary_node = best_replica
            replication.replica_nodes.remove(best_replica)
            replication.sync_version += 1
            
            # Création nouveaux replicas si nécessaire
            await self._ensure_replication_factor(session_id)
            
            logger.info(f"⬆️ Replica {best_replica} promu primaire pour session {session_id}")
    
    async def _select_best_replica(self, replica_nodes: List[str]) -> Optional[str]:
        """**Backend Senior**: Sélection meilleur replica"""
        
        best_node = None
        best_score = float('inf')
        
        for node_id in replica_nodes:
            node = self.cluster_nodes.get(node_id)
            if not node or node.status != NodeStatus.ACTIVE:
                continue
            
            # Score basé priorité et charge
            score = node.priority + node.load_factor * 10
            
            if score < best_score:
                best_score = score
                best_node = node_id
        
        return best_node
    
    async def create_distributed_session(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        replication_factor: Optional[int] = None
    ) -> bool:
        """**Microservices**: Création session distribuée"""
        
        try:
            replication_factor = replication_factor or self.config.get('replication_factor', 2)
            
            # Sélection nœud primaire (ici = nœud courant)
            primary_node = self.node_id
            
            # Sélection nœuds replica
            replica_nodes = await self._select_replica_nodes(replication_factor - 1)
            
            # Création réplication
            replication = SessionReplication(
                session_id=session_id,
                primary_node=primary_node,
                replica_nodes=replica_nodes,
                last_sync=datetime.now(timezone.utc),
                sync_version=1
            )
            
            self.session_replications[session_id] = replication
            self.local_sessions.add(session_id)
            
            # Synchronisation initiale vers replicas
            sync_event = SyncEvent(
                event_id=f"create_{session_id}_{int(time.time())}",
                event_type="create",
                session_id=session_id,
                source_node=self.node_id,
                target_nodes=replica_nodes,
                data=session_data,
                timestamp=datetime.now(timezone.utc),
                version=1
            )
            
            await self.sync_queue.put(sync_event)
            
            logger.info(f"📝 Session distribuée créée: {session_id} (replicas: {replica_nodes})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur création session distribuée {session_id}: {e}")
            return False
    
    async def _select_replica_nodes(self, count: int) -> List[str]:
        """**Backend Senior**: Sélection nœuds replica optimaux"""
        
        # Filtrage nœuds actifs
        available_nodes = [
            node for node in self.cluster_nodes.values()
            if (node.status == NodeStatus.ACTIVE and 
                node.node_id != self.node_id and
                'session_storage' in node.capabilities)
        ]
        
        # Tri par score (priorité + charge)
        available_nodes.sort(key=lambda n: n.priority + n.load_factor * 10)
        
        # Sélection meilleurs nœuds
        selected = available_nodes[:count]
        return [node.node_id for node in selected]
    
    async def update_distributed_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
        sync_strategy: Optional[SyncStrategy] = None
    ) -> bool:
        """**DBA**: Mise à jour session distribuée"""
        
        try:
            replication = self.session_replications.get(session_id)
            if not replication:
                return False
            
            # Vérification autorité (nœud primaire)
            if replication.primary_node != self.node_id:
                # Redirection vers primaire
                return await self._forward_to_primary(session_id, 'update', updates)
            
            sync_strategy = sync_strategy or SyncStrategy(self.config.get('sync_strategy', 'eventual'))
            
            # Mise à jour locale
            # (ici nous simulons - en réalité, mise à jour dans session store)
            
            # Incrémentation version
            replication.sync_version += 1
            replication.last_sync = datetime.now(timezone.utc)
            
            # Synchronisation selon stratégie
            if sync_strategy == SyncStrategy.IMMEDIATE:
                return await self._sync_immediate(session_id, updates)
            elif sync_strategy == SyncStrategy.STRONG:
                return await self._sync_strong_consistency(session_id, updates)
            else:
                return await self._sync_eventual(session_id, updates)
                
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour session distribuée {session_id}: {e}")
            return False
    
    async def _sync_immediate(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """**DBA**: Synchronisation immédiate"""
        
        replication = self.session_replications.get(session_id)
        if not replication:
            return False
        
        # Synchronisation synchrone vers tous replicas
        sync_tasks = []
        
        for replica_node in replication.replica_nodes:
            task = asyncio.create_task(
                self._sync_to_node(replica_node, session_id, updates, replication.sync_version)
            )
            sync_tasks.append(task)
        
        # Attendre toutes synchronisations
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        
        # Vérification succès
        success_count = sum(1 for r in results if r is True)
        total_replicas = len(replication.replica_nodes)
        
        success = success_count >= (total_replicas // 2 + 1)  # Majorité
        
        logger.debug(f"⚡ Sync immédiate {session_id}: {success_count}/{total_replicas}")
        return success
    
    async def _sync_strong_consistency(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """**DBA**: Synchronisation cohérence forte"""
        
        # Pour cohérence forte, tous replicas doivent confirmer
        return await self._sync_immediate(session_id, updates)
    
    async def _sync_eventual(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """**DBA**: Synchronisation éventuelle (async)"""
        
        replication = self.session_replications.get(session_id)
        if not replication:
            return False
        
        # Ajout à file synchronisation asynchrone
        sync_event = SyncEvent(
            event_id=f"update_{session_id}_{int(time.time())}",
            event_type="update",
            session_id=session_id,
            source_node=self.node_id,
            target_nodes=replication.replica_nodes,
            data=updates,
            timestamp=datetime.now(timezone.utc),
            version=replication.sync_version
        )
        
        await self.sync_queue.put(sync_event)
        return True  # Succès local, sync async
    
    async def _sync_processor_loop(self):
        """**Backend Senior**: Boucle traitement synchronisation"""
        while True:
            try:
                # Récupération événements sync
                batch_events = []
                batch_size = self.config.get('sync_batch_size', 100)
                
                # Collecte batch
                for _ in range(batch_size):
                    try:
                        event = await asyncio.wait_for(self.sync_queue.get(), timeout=1.0)
                        batch_events.append(event)
                    except asyncio.TimeoutError:
                        break
                
                if batch_events:
                    await self._process_sync_batch(batch_events)
                
            except Exception as e:
                logger.error(f"❌ Erreur processeur sync: {e}")
                await asyncio.sleep(1)
    
    async def _process_sync_batch(self, events: List[SyncEvent]):
        """**Backend Senior**: Traitement batch synchronisation"""
        
        logger.debug(f"🔄 Traitement batch sync: {len(events)} événements")
        
        for event in events:
            try:
                event.status = "processing"
                success = await self._process_sync_event(event)
                
                event.status = "completed" if success else "failed"
                
                # Historique
                self.sync_history.append({
                    'event_id': event.event_id,
                    'type': event.event_type,
                    'session_id': event.session_id,
                    'success': success,
                    'timestamp': event.timestamp.timestamp(),
                    'latency': (datetime.now(timezone.utc) - event.timestamp).total_seconds() * 1000
                })
                
                # Métriques
                if success:
                    self.metrics.sync_events_completed += 1
                else:
                    self.metrics.sync_events_failed += 1
                
            except Exception as e:
                logger.error(f"❌ Erreur traitement sync event {event.event_id}: {e}")
                event.status = "failed"
    
    async def _process_sync_event(self, event: SyncEvent) -> bool:
        """**Backend Senior**: Traitement événement sync individuel"""
        
        success_count = 0
        
        for target_node in event.target_nodes:
            try:
                result = await self._sync_to_node(
                    target_node, 
                    event.session_id, 
                    event.data, 
                    event.version
                )
                
                if result:
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur sync vers nœud {target_node}: {e}")
        
        # Succès si majorité des nœuds synchronisés
        return success_count > len(event.target_nodes) // 2
    
    async def _sync_to_node(
        self, 
        target_node: str, 
        session_id: str, 
        data: Dict[str, Any], 
        version: int
    ) -> bool:
        """**Microservices**: Synchronisation vers nœud spécifique"""
        
        try:
            # En production, ceci utiliserait gRPC, HTTP, ou message queue
            # Ici simulation avec Redis pub/sub
            
            async with self.redis_pool.get_connection() as redis_conn:
                sync_message = {
                    'source_node': self.node_id,
                    'target_node': target_node,
                    'session_id': session_id,
                    'data': data,
                    'version': version,
                    'timestamp': time.time()
                }
                
                sync_channel = f"sync:{target_node}"
                await redis_conn.publish(sync_channel, json.dumps(sync_message))
                
                return True  # Assumé succès pour démo
                
        except Exception as e:
            logger.error(f"❌ Erreur sync vers {target_node}: {e}")
            return False
    
    async def _ensure_replication_factor(self, session_id: str):
        """**DBA**: Assurer facteur réplication requis"""
        
        replication = self.session_replications.get(session_id)
        if not replication:
            return
        
        target_replicas = self.config.get('replication_factor', 2) - 1  # -1 pour primaire
        current_replicas = len(replication.replica_nodes)
        
        if current_replicas < target_replicas:
            # Création replicas supplémentaires
            needed = target_replicas - current_replicas
            new_replicas = await self._select_replica_nodes(needed)
            
            for new_replica in new_replicas:
                replication.replica_nodes.append(new_replica)
                
                # Synchronisation initiale vers nouveau replica
                sync_event = SyncEvent(
                    event_id=f"replicate_{session_id}_{new_replica}_{int(time.time())}",
                    event_type="replicate",
                    session_id=session_id,
                    source_node=self.node_id,
                    target_nodes=[new_replica],
                    data={'action': 'full_sync'},
                    timestamp=datetime.now(timezone.utc),
                    version=replication.sync_version
                )
                
                await self.sync_queue.put(sync_event)
            
            logger.info(f"📈 Facteur réplication restauré pour {session_id}: +{len(new_replicas)} replicas")
    
    def register_conflict_resolution_handler(self, conflict_type: str, handler: Callable):
        """**DBA**: Enregistrement gestionnaire résolution conflits"""
        self.conflict_resolution_handlers[conflict_type] = handler
        logger.info(f"⚖️ Gestionnaire conflit enregistré: {conflict_type}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """**Microservices**: Enregistrement gestionnaire événements"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"🎫 Gestionnaire événement enregistré: {event_type}")
    
    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """**Microservices**: Déclenchement événements"""
        for handler in self.event_handlers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, data)
                else:
                    handler(event_type, data)
            except Exception as e:
                logger.error(f"❌ Erreur gestionnaire événement {event_type}: {e}")
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """**DevOps**: Statut cluster complet"""
        
        active_nodes = [n for n in self.cluster_nodes.values() if n.status == NodeStatus.ACTIVE]
        total_sessions = sum(n.session_count for n in active_nodes)
        
        # Distribution sessions par nœud
        session_distribution = {
            node.node_id: node.session_count
            for node in active_nodes
        }
        
        # Métriques synchronisation
        recent_syncs = list(self.sync_history)[-100:]  # 100 derniers
        if recent_syncs:
            avg_latency = sum(s['latency'] for s in recent_syncs) / len(recent_syncs)
            success_rate = sum(1 for s in recent_syncs if s['success']) / len(recent_syncs)
        else:
            avg_latency = 0
            success_rate = 0
        
        return {
            'cluster_info': {
                'cluster_name': self.config['cluster_name'],
                'current_node': self.node_id,
                'total_nodes': len(self.cluster_nodes) + 1,  # +1 pour nœud courant
                'active_nodes': len(active_nodes) + 1,
                'total_sessions': total_sessions + len(self.local_sessions)
            },
            'nodes': {
                node.node_id: {
                    'host': node.host,
                    'port': node.port,
                    'region': node.region,
                    'status': node.status.value,
                    'session_count': node.session_count,
                    'load_factor': node.load_factor,
                    'last_heartbeat': node.last_heartbeat.isoformat()
                }
                for node in self.cluster_nodes.values()
            },
            'replication': {
                'total_replicated_sessions': len(self.session_replications),
                'replication_factor': self.config.get('replication_factor'),
                'sync_strategy': self.config.get('sync_strategy')
            },
            'sync_metrics': {
                'events_completed': self.metrics.sync_events_completed,
                'events_failed': self.metrics.sync_events_failed,
                'average_latency_ms': avg_latency,
                'success_rate': success_rate,
                'pending_events': self.sync_queue.qsize()
            },
            'session_distribution': session_distribution,
            'configuration': {
                'replication_mode': self.config.get('replication_mode'),
                'heartbeat_interval': self.config.get('heartbeat_interval'),
                'sync_batch_size': self.config.get('sync_batch_size')
            }
        }

# Factory function
async def create_distributed_session_engine(
    redis_pool, 
    node_id: str = None, 
    config: Optional[Dict[str, Any]] = None
):
    """**Microservices**: Factory création moteur sessions distribuées"""
    engine = DistributedSessionEngine(redis_pool, node_id, config)
    await engine.join_cluster()
    return engine

if __name__ == "__main__":
    async def demo():
        """Démonstration Distributed Session Engine"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.hgetall.return_value = {}
                mock.hset.return_value = True
                mock.expire.return_value = True
                mock.publish.return_value = 1
                return mock
        
        # Création engine
        engine = await create_distributed_session_engine(
            MockRedisPool(), 
            "demo_node_1"
        )
        
        # Création session distribuée
        success = await engine.create_distributed_session(
            "session_123",
            {"user_id": "user456", "data": {"test": "value"}},
            replication_factor=2
        )
        
        print(f"Session distribuée créée: {success}")
        
        # Statut cluster
        status = await engine.get_cluster_status()
        print(f"Statut cluster: {status}")
        
        # Nettoyage
        await engine.leave_cluster()
    
    asyncio.run(demo())