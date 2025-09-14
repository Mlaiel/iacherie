"""MongoDB Replica Set Manager
============================

Advanced replica set management with intelligent configuration, monitoring,
and automatic optimization for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    pymongo = None

from . import ClusterNode, ClusterStatus, ReplicaRole, ClusterState

logger = logging.getLogger(__name__)

class ReplicaManager:
    """Enterprise-grade replica set management system."""
    
    def __init__(self, connection_string -> None: str, replica_set_name -> None: str) -> None:
        """Initialize replica manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for replica set management")
            
        self.connection_string = connection_string
        self.replica_set_name = replica_set_name
        self.client = None
        self._health_check_interval = 30
        self._election_timeout = 10000
        self._heartbeat_interval = 2000
        
    async def initialize_replica_set(self, nodes: List[Dict[str, Any]]) -> bool:
        """Initialize a new replica set with the given nodes."""
        try:
            # Connect to the first node to initiate replica set
            first_node = nodes[0]
            client = MongoClient(f"mongodb://{first_node['host']}:{first_node['port']}")
            
            # Prepare replica set configuration
            config = {
                "_id": self.replica_set_name,
                "version": 1,
                "members": []
            }
            
            for i, node in enumerate(nodes):
                member = {
                    "_id": i,
                    "host": f"{node['host']}:{node['port']}",
                    "priority": node.get('priority', 1),
                    "votes": node.get('votes', 1),
                    "arbiterOnly": node.get('arbiter', False),
                    "hidden": node.get('hidden', False),
                    "buildIndexes": node.get('build_indexes', True)
                }
                
                if node.get('slave_delay', 0) > 0:
                    member["slaveDelay"] = node['slave_delay']
                    member["priority"] = 0
                    
                config["members"].append(member)
            
            # Initiate replica set
            result = client.admin.command("replSetInitiate", config)
            
            if result.get("ok") == 1:
                logger.info(f"Replica set '{self.replica_set_name}' initialized successfully")
                
                # Wait for replica set to stabilize
                await self._wait_for_primary_election(client)
                return True
            else:
                logger.error(f"Failed to initialize replica set: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing replica set: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    async def add_member(self, host: str, port: int, **options) -> bool:
        """Add a new member to the replica set."""
        try:
            client = MongoClient(self.connection_string)
            
            # Get current config
            config = client.admin.command("replSetGetConfig")["config"]
            
            # Find next available member ID
            max_id = max(member["_id"] for member in config["members"])
            new_id = max_id + 1
            
            # Prepare new member
            new_member = {
                "_id": new_id,
                "host": f"{host}:{port}",
                "priority": options.get('priority', 1),
                "votes": options.get('votes', 1),
                "arbiterOnly": options.get('arbiter', False),
                "hidden": options.get('hidden', False),
                "buildIndexes": options.get('build_indexes', True)
            }
            
            if options.get('slave_delay', 0) > 0:
                new_member["slaveDelay"] = options['slave_delay']
                new_member["priority"] = 0
            
            # Add member to config
            config["members"].append(new_member)
            config["version"] += 1
            
            # Reconfigure replica set
            result = client.admin.command("replSetReconfig", config)
            
            if result.get("ok") == 1:
                logger.info(f"Successfully added member {host}:{port} to replica set")
                return True
            else:
                logger.error(f"Failed to add member: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding replica set member: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    async def remove_member(self, host: str, port: int) -> bool:
        """Remove a member from the replica set."""
        try:
            client = MongoClient(self.connection_string)
            
            # Get current config
            config = client.admin.command("replSetGetConfig")["config"]
            
            # Find and remove the member
            target_host = f"{host}:{port}"
            config["members"] = [
                member for member in config["members"] 
                if member["host"] != target_host
            ]
            
            # Renumber member IDs to maintain sequence
            for i, member in enumerate(config["members"]):
                member["_id"] = i
            
            config["version"] += 1
            
            # Reconfigure replica set
            result = client.admin.command("replSetReconfig", config)
            
            if result.get("ok") == 1:
                logger.info(f"Successfully removed member {host}:{port} from replica set")
                return True
            else:
                logger.error(f"Failed to remove member: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing replica set member: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    async def get_replica_status(self) -> Optional[ClusterStatus]:
        """Get comprehensive replica set status."""
        try:
            client = MongoClient(self.connection_string)
            
            # Get replica set status
            status = client.admin.command("replSetGetStatus")
            
            # Parse status information
            cluster_status = ClusterStatus(
                cluster_id=status["set"],
                state=self._determine_cluster_state(status),
                primary_node=self._find_primary_node(status),
                total_nodes=len(status["members"]),
                healthy_nodes=self._count_healthy_nodes(status),
                last_election=self._get_last_election_time(status),
                oplog_size_mb=self._get_oplog_size(client),
                replication_lag_ms=self._calculate_max_lag(status),
                write_concern_timeout=self._get_write_concern_timeout()
            )
            
            return cluster_status
            
        except Exception as e:
            logger.error(f"Error getting replica set status: {e}")
            return None
        finally:
            if 'client' in locals():
                client.close()
    
    async def get_member_details(self) -> List[ClusterNode]:
        """Get detailed information about all replica set members."""
        try:
            client = MongoClient(self.connection_string)
            status = client.admin.command("replSetGetStatus")
            
            nodes = []
            for member in status["members"]:
                node = ClusterNode(
                    node_id=str(member["_id"]),
                    host=member["name"].split(":")[0],
                    port=int(member["name"].split(":")[1]),
                    role=ReplicaRole(member["stateStr"].lower()),
                    state=member["stateStr"],
                    health=member.get("health", 0),
                    lag_ms=self._calculate_member_lag(member, status),
                    priority=member.get("priority", 1),
                    votes=member.get("votes", 1),
                    hidden=member.get("hidden", False),
                    arbiter=member.get("arbiterOnly", False)
                )
                nodes.append(node)
            
            return nodes
            
        except Exception as e:
            logger.error(f"Error getting member details: {e}")
            return []
        finally:
            if 'client' in locals():
                client.close()
    
    async def force_primary_step_down(self, step_down_seconds: int = 60) -> bool:
        """Force the current primary to step down."""
        try:
            client = MongoClient(self.connection_string)
            
            result = client.admin.command(
                "replSetStepDown", 
                step_down_seconds,
                force=True
            )
            
            if result.get("ok") == 1:
                logger.info("Primary successfully stepped down")
                return True
            else:
                logger.error(f"Failed to step down primary: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error forcing primary step down: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    async def _wait_for_primary_election(self, client -> None: MongoClient, timeout -> None: int = 120) -> None:
        """Wait for primary election to complete."""
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < timeout:
            try:
                status = client.admin.command("replSetGetStatus")
                if self._find_primary_node(status):
                    logger.info("Primary election completed")
                    return
            except:
                pass
            await asyncio.sleep(2)
        
        logger.warning("Primary election timed out")
    
    def _determine_cluster_state(self, status: Dict[str, Any]) -> ClusterState:
        """Determine overall cluster health state."""
        healthy_count = self._count_healthy_nodes(status)
        total_count = len(status["members"])
        
        if healthy_count == total_count:
            return ClusterState.HEALTHY
        elif healthy_count >= (total_count // 2) + 1:
            return ClusterState.DEGRADED
        else:
            return ClusterState.CRITICAL
    
    def _find_primary_node(self, status: Dict[str, Any]) -> Optional[str]:
        """Find the current primary node."""
        for member in status["members"]:
            if member["stateStr"] == "PRIMARY":
                return member["name"]
        return None
    
    def _count_healthy_nodes(self, status: Dict[str, Any]) -> int:
        """Count healthy nodes in the replica set."""
        healthy_states = ["PRIMARY", "SECONDARY", "ARBITER"]
        return sum(1 for member in status["members"] 
                  if member["stateStr"] in healthy_states and member.get("health", 0) == 1)
    
    def _get_last_election_time(self, status: Dict[str, Any]) -> Optional[datetime]:
        """Get the time of the last election."""
        try:
            election_date = status.get("electionDate")
            if election_date:
                return election_date
        except:
            pass
        return None
    
    def _get_oplog_size(self, client: MongoClient) -> int:
        """Get oplog size in MB."""
        try:
            oplog_stats = client.local.oplog.rs.stats()
            return int(oplog_stats["size"] / (1024 * 1024))
        except:
            return 0
    
    def _calculate_max_lag(self, status: Dict[str, Any]) -> int:
        """Calculate maximum replication lag in milliseconds."""
        primary_optime = None
        max_lag = 0
        
        # Find primary optime
        for member in status["members"]:
            if member["stateStr"] == "PRIMARY":
                primary_optime = member.get("optimeDate")
                break
        
        if not primary_optime:
            return 0
        
        # Calculate lag for each secondary
        for member in status["members"]:
            if member["stateStr"] == "SECONDARY":
                member_optime = member.get("optimeDate")
                if member_optime:
                    lag_ms = int((primary_optime - member_optime).total_seconds() * 1000)
                    max_lag = max(max_lag, lag_ms)
        
        return max_lag
    
    def _calculate_member_lag(self, member: Dict[str, Any], status: Dict[str, Any]) -> int:
        """Calculate replication lag for a specific member."""
        if member["stateStr"] != "SECONDARY":
            return 0
        
        # Find primary optime
        primary_optime = None
        for m in status["members"]:
            if m["stateStr"] == "PRIMARY":
                primary_optime = m.get("optimeDate")
                break
        
        if not primary_optime:
            return 0
        
        member_optime = member.get("optimeDate")
        if member_optime:
            return int((primary_optime - member_optime).total_seconds() * 1000)
        
        return 0
    
    def _get_write_concern_timeout(self) -> int:
        """Get write concern timeout."""
        return 10000  # Default 10 seconds

# Export the main class
__all__ = ['ReplicaManager']