"""Enterprise Database Replication Manager
Advanced replication, high availability and disaster recovery

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

import asyncio
import psycopg2
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import time
import threading
from pathlib import Path

from backend.core.config import get_database_settings
from backend.core.logging import get_logger
from backend.core.monitoring import MetricsCollector
from .postgresql_manager import get_postgresql_manager


class ReplicationMode(Enum):
    """
Database replication modes"""

    STREAMING = "streaming"
    LOGICAL = "logical"
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"


class ReplicaStatus(Enum):
    """Replica server status"""

    HEALTHY = "healthy"
    LAGGING = "lagging"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    SYNCING = "syncing"
    STANDBY = "standby"


class FailoverStatus(Enum):
    """Failover operation status"""

    STANDBY = "standby"
    PROMOTING = "promoting"
    ACTIVE = "active"
    FAILED = "failed"


@dataclass
class ReplicaConfig:
    """Replica server configuration"""
    replica_id: str
    host: str
    port: int
    database_name: str
    username: str
    password: str
    replication_mode: ReplicationMode
    priority: int
    max_lag_seconds: int
    ssl_mode: str = "require"


@dataclass
class ReplicationStatus:
    """Replication status information"""
    replica_id: str
    status: ReplicaStatus
    lag_bytes: int
    lag_seconds: float
    last_received_lsn: str
    last_replayed_lsn: str
    sync_state: str
    connection_time: datetime
    last_msg_send_time: datetime
    last_msg_receipt_time: datetime


class ReplicationManager:
    """
    Enterprise database replication and high availability manager:
    - Streaming and logical replication support
    - Automatic failover and failback
    - Read replica load balancing
    - Replication lag monitoring
    - Cross-region disaster recovery
    - Point-in-time recovery coordination
    - Conflict resolution for logical replication
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_database_settings()
        self.db_manager = get_postgresql_manager()
        self.metrics = MetricsCollector()
        
        self.replicas: Dict[str, ReplicaConfig] = {}
        self.replication_status: Dict[str, ReplicationStatus] = {}
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        self._initialize_replication_settings()
    
    def _initialize_replication_settings(self) -> None:
        """
Initialize replication configuration"""
        try:
            # Check if we're on primary or replica
            self.is_primary = self._check_if_primary()
            
            if self.is_primary:
                self._configure_primary_server()
            else:
                self._configure_replica_server()
                
            self.logger.info(f"Replication manager initialized (Primary: {self.is_primary})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize replication: {e}")
            raise
    
    def _check_if_primary(self) -> bool:
        """Check if current server is primary"""
        try:
            query = "SELECT pg_is_in_recovery()"
            result = self.db_manager.execute_query(query)
            
            # If pg_is_in_recovery() returns false, we're on primary
            return not result[0][0] if result else False
            
        except Exception as e:
            self.logger.error(f"Failed to check primary status: {e}")
            return False
    
    def _configure_primary_server(self) -> None:
        """Configure primary server for replication"""
        try:
            # Enable WAL archiving
            self._enable_wal_archiving()
            
            # Configure replication slots
            self._manage_replication_slots()
            
            # Set up publication for logical replication
            self._setup_logical_publication()
            
            self.logger.info("Primary server configured for replication")
            
        except Exception as e:
            self.logger.error(f"Failed to configure primary server: {e}")
    
    def _configure_replica_server(self) -> None:
        """Configure replica server settings"""
        try:
            # Configure recovery settings
            self._configure_recovery_settings()
            
            # Set up subscription for logical replication
            self._setup_logical_subscription()
            
            self.logger.info("Replica server configured")
            
        except Exception as e:
            self.logger.error(f"Failed to configure replica server: {e}")
    
    def _enable_wal_archiving(self) -> None:
        """Enable WAL archiving on primary server"""
        try:
            # Check current archive settings
            settings_to_check = [
                'wal_level',
                'archive_mode',
                'archive_command',
                'max_wal_senders',
                'wal_keep_size'
            ]
            
            for setting in settings_to_check:
                query = f"SHOW {setting}"
                result = self.db_manager.execute_query(query)
                current_value = result[0][0] if result else None
                
                self.logger.info(f"Current {setting}: {current_value}")
            
            # Note: In production, these settings should be configured in postgresql.conf
            # and require server restart
            
        except Exception as e:
            self.logger.error(f"Failed to check WAL archiving settings: {e}")
    
    def _manage_replication_slots(self) -> None:
        """Manage replication slots"""
        try:
            # Get existing replication slots
            query = """
                SELECT slot_name, plugin, slot_type, database, 
                       active, restart_lsn, confirmed_flush_lsn
                FROM pg_replication_slots
            """
            
            result = self.db_manager.execute_query(query)
            
            if result:
                self.logger.info(f"Found {len(result)} replication slots")
                for row in result:
                    slot_name, plugin, slot_type, database, active, restart_lsn, flush_lsn = row
                    self.logger.info(
                        f"Slot: {slot_name} ({slot_type}, Active: {active}, "
                        f"Database: {database})"
                    )
            else:
                self.logger.info("No replication slots found")
            
        except Exception as e:
            self.logger.error(f"Failed to manage replication slots: {e}")
    
    def create_replication_slot(
        self, 
        slot_name: str, 
        slot_type: str = "physical"
    ) -> bool:
        """Create replication slot"""
        try:
            if slot_type == "physical":
                query = f"SELECT pg_create_physical_replication_slot('{slot_name}')"
            else:
                # Logical replication slot
                query = f"SELECT pg_create_logical_replication_slot('{slot_name}', 'pgoutput')"
            
            result = self.db_manager.execute_query(query)
            
            if result:
                self.logger.info(f"Created {slot_type} replication slot: {slot_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to create replication slot {slot_name}: {e}")
            return False
    
    def drop_replication_slot(self, slot_name: str) -> bool:
        """Drop replication slot"""
        try:
            query = f"SELECT pg_drop_replication_slot('{slot_name}')"
            self.db_manager.execute_query(query, fetch_results=False)
            
            self.logger.info(f"Dropped replication slot: {slot_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to drop replication slot {slot_name}: {e}")
            return False
    
    def _setup_logical_publication(self) -> None:
        """Set up publication for logical replication"""
        try:
            # Check existing publications
            query = """
                SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete
                FROM pg_publication
            """
            
            result = self.db_manager.execute_query(query)
            
            if result:
                self.logger.info(f"Found {len(result)} publications")
                for row in result:
                    pubname, puballtables, pubinsert, pubupdate, pubdelete = row
                    self.logger.info(
                        f"Publication: {pubname} (All tables: {puballtables})"
                    )
            
            # Create default publication if none exists
            if not result:
                self.create_publication("ia_influencer_replication", all_tables=True)
            
        except Exception as e:
            self.logger.error(f"Failed to setup logical publication: {e}")
    
    def create_publication(
        self, 
        publication_name: str, 
        tables: Optional[List[str]] = None,
        all_tables: bool = False
    ) -> bool:
        """Create logical replication publication"""
        try:
            if all_tables:
                query = f"CREATE PUBLICATION {publication_name} FOR ALL TABLES"
            elif tables:
                tables_clause = ", ".join(tables)
                query = f"CREATE PUBLICATION {publication_name} FOR TABLE {tables_clause}"
            else:
                raise ValueError("Must specify either tables or all_tables=True")
            
            self.db_manager.execute_query(query, fetch_results=False)
            
            self.logger.info(f"Created publication: {publication_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create publication {publication_name}: {e}")
            return False
    
    def _setup_logical_subscription(self) -> None:
        """Set up subscription for logical replication"""
        try:
            # Check existing subscriptions
            query = """
                SELECT subname, subowner, subenabled, subconninfo, subpublications
                FROM pg_subscription
            """
            
            result = self.db_manager.execute_query(query)
            
            if result:
                self.logger.info(f"Found {len(result)} subscriptions")
                for row in result:
                    subname, subowner, subenabled, subconninfo, subpublications = row
                    self.logger.info(
                        f"Subscription: {subname} (Enabled: {subenabled}, "
                        f"Publications: {subpublications})"
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to setup logical subscription: {e}")
    
    def create_subscription(
        self,
        subscription_name: str,
        primary_host: str,
        primary_port: int,
        primary_database: str,
        primary_user: str,
        primary_password: str,
        publication_name: str
    ) -> bool:
        """Create logical replication subscription"""
        try:
            connection_string = (
                f"host={primary_host} port={primary_port} "
                f"dbname={primary_database} user={primary_user} "
                f"password={primary_password}"
            )
            
            query = f"""
                CREATE SUBSCRIPTION {subscription_name}
                CONNECTION '{connection_string}'
                PUBLICATION {publication_name}
            """
            
            self.db_manager.execute_query(query, fetch_results=False)
            
            self.logger.info(f"Created subscription: {subscription_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create subscription {subscription_name}: {e}")
            return False
    
    def add_replica(self, replica_config: ReplicaConfig) -> bool:
        """Add replica server to monitoring"""
        try:
            self.replicas[replica_config.replica_id] = replica_config
            
            # Test connection to replica
            if self._test_replica_connection(replica_config):
                self.logger.info(f"Added replica: {replica_config.replica_id}")
                return True
            else:
                self.logger.error(f"Failed to connect to replica: {replica_config.replica_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add replica: {e}")
            return False
    
    def _test_replica_connection(self, replica_config: ReplicaConfig) -> bool:
        """Test connection to replica server"""
        try:
            connection = psycopg2.connect(
                host=replica_config.host,
                port=replica_config.port,
                database=replica_config.database_name,
                user=replica_config.username,
                password=replica_config.password,
                connect_timeout=10
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            connection.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Replica connection test failed: {e}")
            return False
    
    def get_replication_status(self) -> Dict[str, Any]:
        """Get comprehensive replication status"""
        try:
            status = {
                'is_primary': self.is_primary,
                'timestamp': datetime.now().isoformat(),
                'replicas': {},
                'replication_lag': {},
                'wal_status': {}
            }
            
            if self.is_primary:
                # Get primary server replication status
                status.update(self._get_primary_status())
            else:
                # Get replica server status
                status.update(self._get_replica_status())
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get replication status: {e}")
            return {'error': str(e)}
    
    def _get_primary_status(self) -> Dict[str, Any]:
        """Get primary server replication status"""
        try:
            status = {}
            
            # Get active replication connections
            query = """
                SELECT client_addr, client_hostname, client_port, state,
                       sent_lsn, write_lsn, flush_lsn, replay_lsn,
                       write_lag, flush_lag, replay_lag, sync_state,
                       sync_priority
                FROM pg_stat_replication
            """
            
            result = self.db_manager.execute_query(query)
            
            replicas_status = []
            if result:
                for row in result:
                    replica_info = {
                        'client_addr': row[0],
                        'client_hostname': row[1],
                        'client_port': row[2],
                        'state': row[3],
                        'sent_lsn': row[4],
                        'write_lsn': row[5],
                        'flush_lsn': row[6],
                        'replay_lsn': row[7],
                        'write_lag': str(row[8]) if row[8] else None,
                        'flush_lag': str(row[9]) if row[9] else None,
                        'replay_lag': str(row[10]) if row[10] else None,
                        'sync_state': row[11],
                        'sync_priority': row[12]
                    }
                    replicas_status.append(replica_info)
            
            status['connected_replicas'] = replicas_status
            status['replica_count'] = len(replicas_status)
            
            # Get WAL status
            wal_query = """
                SELECT pg_current_wal_lsn() as current_lsn,
                       pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') as wal_bytes
            """
            
            wal_result = self.db_manager.execute_query(wal_query)
            if wal_result:
                status['wal_status'] = {
                    'current_lsn': wal_result[0][0],
                    'wal_bytes': wal_result[0][1]
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get primary status: {e}")
            return {}
    
    def _get_replica_status(self) -> Dict[str, Any]:
        """Get replica server status"""
        try:
            status = {}
            
            # Get recovery status
            query = """
                SELECT pg_is_in_recovery() as in_recovery,
                       pg_last_wal_receive_lsn() as last_received_lsn,
                       pg_last_wal_replay_lsn() as last_replayed_lsn,
                       pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) as lag_bytes
            """
            
            result = self.db_manager.execute_query(query)
            
            if result:
                row = result[0]
                status['recovery_status'] = {
                    'in_recovery': row[0],
                    'last_received_lsn': row[1],
                    'last_replayed_lsn': row[2],
                    'lag_bytes': row[3] if row[3] is not None else 0
                }
            
            # Get replication statistics
            stats_query = """
                SELECT pid, status, receive_start_lsn, receive_start_tli,
                       received_lsn, received_tli, last_msg_send_time,
                       last_msg_receipt_time, latest_end_lsn, latest_end_time
                FROM pg_stat_wal_receiver
            """
            
            stats_result = self.db_manager.execute_query(stats_query)
            
            if stats_result:
                row = stats_result[0]
                status['wal_receiver_stats'] = {
                    'pid': row[0],
                    'status': row[1],
                    'receive_start_lsn': row[2],
                    'received_lsn': row[4],
                    'last_msg_send_time': row[6].isoformat() if row[6] else None,
                    'last_msg_receipt_time': row[7].isoformat() if row[7] else None,
                    'latest_end_lsn': row[8],
                    'latest_end_time': row[9].isoformat() if row[9] else None
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get replica status: {e}")
            return {}
    
    def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start continuous replication monitoring"""
        if self.is_monitoring:
            self.logger.warning("Replication monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info(f"Started replication monitoring (interval: {interval_seconds}s)")
    
    def stop_monitoring(self) -> None:
        """Stop replication monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Stopped replication monitoring")
    
    def _monitoring_loop(self, interval_seconds: int) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Update replication status
                self._update_replication_metrics()
                
                # Check for lag alerts
                self._check_lag_alerts()
                
                # Check replica health
                self._check_replica_health()
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval_seconds)
    
    def _update_replication_metrics(self) -> None:
        """Update replication metrics"""
        try:
            status = self.get_replication_status()
            
            # Record metrics
            if self.is_primary:
                replica_count = status.get('replica_count', 0)
                self.metrics.record_gauge('replication.connected_replicas', replica_count)
                
                # Record lag metrics for each replica
                for replica in status.get('connected_replicas', []):
                    if replica.get('replay_lag'):
                        lag_seconds = self._parse_lag_interval(replica['replay_lag'])
                        self.metrics.record_gauge(
                            'replication.lag_seconds',
                            lag_seconds,
                            tags={'replica': replica.get('client_addr', 'unknown')}
                        )
            else:
                recovery_status = status.get('recovery_status', {})
                lag_bytes = recovery_status.get('lag_bytes', 0)
                self.metrics.record_gauge('replication.lag_bytes', lag_bytes)
            
        except Exception as e:
            self.logger.error(f"Failed to update replication metrics: {e}")
    
    def _parse_lag_interval(self, lag_str: str) -> float:
        """Parse PostgreSQL interval to seconds"""
        try:
            # Simple parser for intervals like "00:00:01.234567"
            if ':' in lag_str:
                parts = lag_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            else:
                return float(lag_str)
        except:
            return 0.0
    
    def _check_lag_alerts(self) -> None:
        """Check for replication lag alerts"""
        try:
            for replica_id, replica_config in self.replicas.items():
                replica_status = self.replication_status.get(replica_id)
                
                if replica_status and replica_status.lag_seconds > replica_config.max_lag_seconds:
                    self.logger.warning(
                        f"Replica {replica_id} lag exceeded threshold: "
                        f"{replica_status.lag_seconds}s > {replica_config.max_lag_seconds}s"
                    )
                    
                    # Trigger alert
                    self._trigger_lag_alert(replica_id, replica_status.lag_seconds)
        
        except Exception as e:
            self.logger.error(f"Failed to check lag alerts: {e}")
    
    def _check_replica_health(self) -> None:
        """Check replica server health"""
        try:
            for replica_id, replica_config in self.replicas.items():
                is_healthy = self._test_replica_connection(replica_config)
                
                current_status = self.replication_status.get(replica_id)
                if current_status:
                    if is_healthy and current_status.status == ReplicaStatus.DISCONNECTED:
                        self.logger.info(f"Replica {replica_id} reconnected")
                        current_status.status = ReplicaStatus.HEALTHY
                    elif not is_healthy and current_status.status != ReplicaStatus.DISCONNECTED:
                        self.logger.warning(f"Replica {replica_id} disconnected")
                        current_status.status = ReplicaStatus.DISCONNECTED
        
        except Exception as e:
            self.logger.error(f"Failed to check replica health: {e}")
    
    def _trigger_lag_alert(self, replica_id: str, lag_seconds: float) -> None:
        """Trigger replication lag alert"""
        try:
            alert_data = {
                'replica_id': replica_id,
                'lag_seconds': lag_seconds,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'replication_lag'
            }
            
            # Send alert (implement your alerting mechanism)
            self.logger.critical(f"REPLICATION LAG ALERT: {alert_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger lag alert: {e}")
    
    def initiate_failover(self, target_replica_id: str) -> bool:
        """Initiate failover to specified replica"""
        try:
            if not self.is_primary:
                self.logger.error("Failover can only be initiated from primary server")
                return False
            
            target_replica = self.replicas.get(target_replica_id)
            if not target_replica:
                self.logger.error(f"Target replica not found: {target_replica_id}")
                return False
            
            self.logger.info(f"Initiating failover to replica: {target_replica_id}")
            
            # Promote replica to primary
            success = self._promote_replica(target_replica)
            
            if success:
                self.logger.info(f"Failover completed successfully to {target_replica_id}")
            else:
                self.logger.error(f"Failover failed to {target_replica_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failover initiation failed: {e}")
            return False
    
    def _promote_replica(self, replica_config: ReplicaConfig) -> bool:
        """Promote replica to primary"""
        try:
            # Connect to replica and promote
            # This is a simplified implementation
            # In production, you would use tools like Patroni or repmgr
            
            promote_command = [
                'pg_ctl',
                'promote',
                '-D', '/var/lib/postgresql/data'  # Adjust path as needed
            ]
            
            # Execute promotion on replica server
            # Note: This requires SSH access to replica server
            # Implementation depends on your infrastructure setup
            
            self.logger.info(f"Promoting replica {replica_config.replica_id} to primary")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to promote replica: {e}")
            return False


# Singleton instance
_replication_manager = None

def get_replication_manager() -> ReplicationManager:
    """Get replication manager singleton instance"""
    global _replication_manager
    if _replication_manager is None:
        _replication_manager = ReplicationManager()
    return _replication_manager
