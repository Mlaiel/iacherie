"""MongoDB Sync Coordinator
=========================

Multi-service synchronization orchestration and coordination system
for the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import json

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from . import SyncConfiguration, SyncStatus, SyncDirection, SyncEvent

logger = logging.getLogger(__name__)

class SyncState(Enum):
    """Synchronization states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    RECOVERING = "recovering"

@dataclass
class SyncSession:
    """Active synchronization session."""
    session_id: str
    config: SyncConfiguration
    state: SyncState
    started_at: datetime
    last_sync: Optional[datetime]
    total_synced: int
    errors_count: int
    last_error: Optional[str]

class SyncCoordinator:
    """Enterprise-grade multi-service synchronization coordinator."""
    
    def __init__(self, coordinator_config: Dict[str, Any]):
        """Initialize sync coordinator."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for sync coordination")
            
        self.config = coordinator_config
        self.active_sessions: Dict[str, SyncSession] = {}
        self.sync_configurations: Dict[str, SyncConfiguration] = {}
        
        # Coordination state
        self.coordinator_running = False
        self.coordination_thread = None
        self.health_check_interval = 30  # seconds
        
        # Dependencies tracking
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.execution_order: List[str] = []
        
        # Performance tracking
        self.sync_metrics = {}
        self.bottleneck_detection = True
        
    def register_sync_configuration(self, config: SyncConfiguration):
        """Register a synchronization configuration."""
        self.sync_configurations[config.sync_id] = config
        logger.info(f"Registered sync configuration: {config.sync_id}")
        
        # Update dependency graph
        self._update_dependency_graph(config)
        self._calculate_execution_order()
    
    def _update_dependency_graph(self, config: SyncConfiguration):
        """Update dependency graph for execution ordering."""
        sync_id = config.sync_id
        
        if sync_id not in self.dependency_graph:
            self.dependency_graph[sync_id] = set()
        
        # Analyze dependencies based on collections and direction
        for other_id, other_config in self.sync_configurations.items():
            if other_id == sync_id:
                continue
            
            # Check for collection overlaps
            common_collections = set(config.collections) & set(other_config.collections)
            
            if common_collections:
                # Determine dependency based on sync direction
                if (config.direction == SyncDirection.SOURCE_TO_TARGET and
                    other_config.direction == SyncDirection.TARGET_TO_SOURCE):
                    # Create dependency: target sync should happen after source sync
                    self.dependency_graph[other_id].add(sync_id)
                elif (config.direction == SyncDirection.BIDIRECTIONAL or
                      other_config.direction == SyncDirection.BIDIRECTIONAL):
                    # Bidirectional syncs need careful ordering
                    self.dependency_graph[sync_id].add(other_id)
    
    def _calculate_execution_order(self):
        """Calculate optimal execution order using topological sort."""
        # Simple topological sort
        in_degree = {sync_id: 0 for sync_id in self.dependency_graph}
        
        for sync_id in self.dependency_graph:
            for dependency in self.dependency_graph[sync_id]:
                if dependency in in_degree:
                    in_degree[dependency] += 1
        
        # Start with nodes with no dependencies
        queue = [sync_id for sync_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            # Remove this node and update in-degrees
            for dependency in self.dependency_graph.get(current, set()):
                if dependency in in_degree:
                    in_degree[dependency] -= 1
                    if in_degree[dependency] == 0:
                        queue.append(dependency)
        
        self.execution_order = execution_order
        logger.info(f"Calculated execution order: {execution_order}")
    
    async def start_coordination(self):
        """Start synchronization coordination."""
        if self.coordinator_running:
            logger.warning("Sync coordinator already running")
            return
        
        self.coordinator_running = True
        
        # Start coordination thread
        self.coordination_thread = threading.Thread(
            target=self._coordination_loop,
            daemon=True
        )
        self.coordination_thread.start()
        
        logger.info("Sync coordination started")
    
    def _coordination_loop(self):
        """Main coordination loop."""
        logger.info("Sync coordination loop started")
        
        while self.coordinator_running:
            try:
                # Check health of active sessions
                self._check_session_health()
                
                # Handle failed sessions
                self._handle_failed_sessions()
                
                # Optimize sync performance
                self._optimize_sync_performance()
                
                # Detect and resolve bottlenecks
                if self.bottleneck_detection:
                    self._detect_bottlenecks()
                
                # Sleep before next iteration
                threading.Event().wait(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in coordination loop: {e}")
                threading.Event().wait(self.health_check_interval)
        
        logger.info("Sync coordination loop stopped")
    
    async def start_sync_session(self, sync_id: str) -> bool:
        """Start a synchronization session."""
        if sync_id not in self.sync_configurations:
            logger.error(f"Sync configuration not found: {sync_id}")
            return False
        
        if sync_id in self.active_sessions:
            logger.warning(f"Sync session already active: {sync_id}")
            return True
        
        try:
            config = self.sync_configurations[sync_id]
            
            # Check dependencies
            if not self._check_dependencies(sync_id):
                logger.error(f"Dependencies not met for sync: {sync_id}")
                return False
            
            # Create sync session
            session = SyncSession(
                session_id=f"{sync_id}_{int(datetime.now().timestamp())}",
                config=config,
                state=SyncState.INITIALIZING,
                started_at=datetime.now(),
                last_sync=None,
                total_synced=0,
                errors_count=0,
                last_error=None
            )
            
            # Initialize sync process
            success = await self._initialize_sync_process(session)
            
            if success:
                session.state = SyncState.ACTIVE
                self.active_sessions[sync_id] = session
                logger.info(f"Started sync session: {sync_id}")
                return True
            else:
                session.state = SyncState.ERROR
                logger.error(f"Failed to start sync session: {sync_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting sync session {sync_id}: {e}")
            return False
    
    def _check_dependencies(self, sync_id: str) -> bool:
        """Check if all dependencies are satisfied."""
        dependencies = self.dependency_graph.get(sync_id, set())
        
        for dep_id in dependencies:
            if dep_id not in self.active_sessions:
                logger.debug(f"Dependency not active: {dep_id}")
                return False
            
            session = self.active_sessions[dep_id]
            if session.state not in [SyncState.ACTIVE, SyncState.PAUSED]:
                logger.debug(f"Dependency not in valid state: {dep_id} ({session.state})")
                return False
        
        return True
    
    async def _initialize_sync_process(self, session: SyncSession) -> bool:
        """Initialize synchronization process for a session."""
        try:
            config = session.config
            
            # Establish connections
            source_client = MongoClient(config.source_connection)
            target_client = MongoClient(config.target_connection)
            
            # Test connections
            source_client.admin.command("isMaster")
            target_client.admin.command("isMaster")
            
            # Store clients in session (simplified - would use proper connection management)
            session.source_client = source_client
            session.target_client = target_client
            
            # Perform initial synchronization if needed
            if config.direction in [SyncDirection.SOURCE_TO_TARGET, SyncDirection.BIDIRECTIONAL]:
                await self._perform_initial_sync(session, "source_to_target")
            
            if config.direction in [SyncDirection.TARGET_TO_SOURCE, SyncDirection.BIDIRECTIONAL]:
                await self._perform_initial_sync(session, "target_to_source")
            
            logger.info(f"Initialized sync process for session: {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sync process: {e}")
            session.last_error = str(e)
            return False
    
    async def _perform_initial_sync(self, session: SyncSession, direction: str):
        """Perform initial synchronization."""
        logger.info(f"Performing initial sync: {session.session_id} ({direction})")
        
        config = session.config
        
        if direction == "source_to_target":
            source_client = session.source_client
            target_client = session.target_client
        else:
            source_client = session.target_client
            target_client = session.source_client
        
        # Sync each configured collection
        for collection_name in config.collections:
            try:
                # Get source and target collections
                source_db_name = self._extract_db_from_connection(config.source_connection)
                target_db_name = self._extract_db_from_connection(config.target_connection)
                
                source_collection = source_client[source_db_name][collection_name]
                target_collection = target_client[target_db_name][collection_name]
                
                # Apply filters if configured
                query = config.filters.get(collection_name, {})
                
                # Batch synchronization
                batch_size = config.batch_size
                skip = 0
                
                while True:
                    # Get batch from source
                    documents = list(source_collection.find(query).skip(skip).limit(batch_size))
                    
                    if not documents:
                        break
                    
                    # Insert/update in target
                    for doc in documents:
                        try:
                            # Apply transformations
                            transformed_doc = self._apply_transformations(doc, config.transformations)
                            
                            # Upsert to target
                            target_collection.replace_one(
                                {"_id": transformed_doc["_id"]},
                                transformed_doc,
                                upsert=True
                            )
                            
                            session.total_synced += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to sync document {doc.get('_id')}: {e}")
                            session.errors_count += 1
                    
                    skip += batch_size
                    
                    # Update last sync time
                    session.last_sync = datetime.now()
                
                logger.info(f"Initial sync completed for collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Failed to sync collection {collection_name}: {e}")
                session.errors_count += 1
                session.last_error = str(e)
    
    def _extract_db_from_connection(self, connection_string: str) -> str:
        """Extract database name from connection string."""
        # Simplified extraction - in production, use proper URI parsing
        if "/" in connection_string:
            return connection_string.split("/")[-1].split("?")[0]
        return "default"
    
    def _apply_transformations(self, document: Dict[str, Any], transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply transformations to a document."""
        transformed = document.copy()
        
        for transformation in transformations:
            transform_type = transformation.get("type")
            
            if transform_type == "field_rename":
                old_field = transformation.get("from")
                new_field = transformation.get("to")
                if old_field in transformed:
                    transformed[new_field] = transformed.pop(old_field)
            
            elif transform_type == "field_map":
                field = transformation.get("field")
                mapping = transformation.get("mapping", {})
                if field in transformed and transformed[field] in mapping:
                    transformed[field] = mapping[transformed[field]]
            
            elif transform_type == "add_field":
                field = transformation.get("field")
                value = transformation.get("value")
                transformed[field] = value
            
            # Add more transformation types as needed
        
        return transformed
    
    def _check_session_health(self):
        """Check health of all active sessions."""
        for sync_id, session in list(self.active_sessions.items()):
            try:
                # Check if session is stale
                if session.last_sync:
                    time_since_sync = datetime.now() - session.last_sync
                    if time_since_sync > timedelta(minutes=session.config.sync_interval_seconds / 60 * 2):
                        logger.warning(f"Session appears stale: {sync_id}")
                        session.state = SyncState.ERROR
                
                # Check error rate
                if session.total_synced > 0:
                    error_rate = session.errors_count / session.total_synced
                    if error_rate > 0.1:  # 10% error rate threshold
                        logger.warning(f"High error rate in session {sync_id}: {error_rate:.2%}")
                        session.state = SyncState.ERROR
                
            except Exception as e:
                logger.error(f"Error checking session health for {sync_id}: {e}")
    
    def _handle_failed_sessions(self):
        """Handle failed synchronization sessions."""
        for sync_id, session in list(self.active_sessions.items()):
            if session.state == SyncState.ERROR:
                logger.info(f"Attempting to recover failed session: {sync_id}")
                
                try:
                    # Attempt recovery
                    session.state = SyncState.RECOVERING
                    
                    # Reset error count
                    session.errors_count = 0
                    session.last_error = None
                    
                    # Restart session
                    asyncio.create_task(self._restart_session(sync_id))
                    
                except Exception as e:
                    logger.error(f"Failed to recover session {sync_id}: {e}")
                    session.state = SyncState.STOPPED
    
    async def _restart_session(self, sync_id: str):
        """Restart a failed session."""
        # Stop current session
        await self.stop_sync_session(sync_id)
        
        # Wait a bit before restart
        await asyncio.sleep(5)
        
        # Restart session
        await self.start_sync_session(sync_id)
    
    def _optimize_sync_performance(self):
        """Optimize synchronization performance."""
        for sync_id, session in self.active_sessions.items():
            config = session.config
            
            # Adjust batch size based on performance
            if session.total_synced > 1000:  # Have enough data
                avg_time_per_doc = self._calculate_avg_sync_time(session)
                
                if avg_time_per_doc > 100:  # Slow sync, reduce batch size
                    new_batch_size = max(10, config.batch_size // 2)
                    config.batch_size = new_batch_size
                    logger.info(f"Reduced batch size for {sync_id}: {new_batch_size}")
                
                elif avg_time_per_doc < 10:  # Fast sync, increase batch size
                    new_batch_size = min(1000, config.batch_size * 2)
                    config.batch_size = new_batch_size
                    logger.info(f"Increased batch size for {sync_id}: {new_batch_size}")
    
    def _calculate_avg_sync_time(self, session: SyncSession) -> float:
        """Calculate average sync time per document."""
        if session.total_synced == 0:
            return 0
        
        total_time = (datetime.now() - session.started_at).total_seconds()
        return (total_time / session.total_synced) * 1000  # milliseconds
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks in synchronization."""
        # Analyze sync performance across sessions
        slow_sessions = []
        
        for sync_id, session in self.active_sessions.items():
            avg_time = self._calculate_avg_sync_time(session)
            if avg_time > 500:  # 500ms per document is considered slow
                slow_sessions.append((sync_id, avg_time))
        
        if slow_sessions:
            logger.warning(f"Detected slow sync sessions: {slow_sessions}")
            
            # Take corrective action
            for sync_id, avg_time in slow_sessions:
                session = self.active_sessions[sync_id]
                
                # Reduce batch size for slow sessions
                session.config.batch_size = max(10, session.config.batch_size // 2)
                
                # Increase sync interval
                session.config.sync_interval_seconds = min(300, session.config.sync_interval_seconds * 1.5)
    
    async def stop_sync_session(self, sync_id: str) -> bool:
        """Stop a synchronization session."""
        if sync_id not in self.active_sessions:
            logger.warning(f"Sync session not active: {sync_id}")
            return False
        
        try:
            session = self.active_sessions[sync_id]
            session.state = SyncState.STOPPED
            
            # Close connections
            if hasattr(session, 'source_client'):
                session.source_client.close()
            if hasattr(session, 'target_client'):
                session.target_client.close()
            
            # Remove from active sessions
            del self.active_sessions[sync_id]
            
            logger.info(f"Stopped sync session: {sync_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping sync session {sync_id}: {e}")
            return False
    
    async def pause_sync_session(self, sync_id: str) -> bool:
        """Pause a synchronization session."""
        if sync_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[sync_id]
        session.state = SyncState.PAUSED
        logger.info(f"Paused sync session: {sync_id}")
        return True
    
    async def resume_sync_session(self, sync_id: str) -> bool:
        """Resume a paused synchronization session."""
        if sync_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[sync_id]
        if session.state == SyncState.PAUSED:
            session.state = SyncState.ACTIVE
            logger.info(f"Resumed sync session: {sync_id}")
            return True
        
        return False
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get comprehensive coordination status."""
        active_count = len(self.active_sessions)
        total_synced = sum(session.total_synced for session in self.active_sessions.values())
        total_errors = sum(session.errors_count for session in self.active_sessions.values())
        
        session_states = {}
        for state in SyncState:
            session_states[state.value] = len([
                s for s in self.active_sessions.values() if s.state == state
            ])
        
        return {
            'coordinator_running': self.coordinator_running,
            'active_sessions': active_count,
            'total_configurations': len(self.sync_configurations),
            'total_synced_documents': total_synced,
            'total_errors': total_errors,
            'session_states': session_states,
            'execution_order': self.execution_order,
            'dependency_count': len(self.dependency_graph)
        }
    
    def get_session_details(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a sync session."""
        if sync_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[sync_id]
        return {
            'session_id': session.session_id,
            'sync_id': sync_id,
            'state': session.state.value,
            'started_at': session.started_at,
            'last_sync': session.last_sync,
            'total_synced': session.total_synced,
            'errors_count': session.errors_count,
            'last_error': session.last_error,
            'config': asdict(session.config)
        }
    
    def stop_coordination(self):
        """Stop synchronization coordination."""
        if not self.coordinator_running:
            return
        
        self.coordinator_running = False
        
        # Stop all active sessions
        for sync_id in list(self.active_sessions.keys()):
            asyncio.create_task(self.stop_sync_session(sync_id))
        
        # Wait for coordination thread
        if self.coordination_thread:
            self.coordination_thread.join(timeout=10)
        
        logger.info("Sync coordination stopped")

# Export the main class
__all__ = ['SyncCoordinator', 'SyncSession', 'SyncState']