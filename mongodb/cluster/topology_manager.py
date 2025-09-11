"""MongoDB Topology Manager
========================

Advanced topology management and configuration for MongoDB clusters
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger(__name__)

class TopologyType(Enum):
    """MongoDB topology types."""
    STANDALONE = "standalone"
    REPLICA_SET = "replica_set"
    SHARDED_CLUSTER = "sharded_cluster"

@dataclass
class TopologyNode:
    """Topology node information."""
    node_id: str
    host: str
    port: int
    node_type: str  # mongod, mongos, config
    role: str
    tags: Dict[str, str]
    priority: int
    votes: int

@dataclass
class TopologyConfig:
    """Complete topology configuration."""
    topology_type: TopologyType
    replica_sets: List[Dict[str, Any]]
    config_servers: List[Dict[str, Any]]
    mongos_routers: List[Dict[str, Any]]
    shard_zones: List[Dict[str, Any]]

class TopologyManager:
    """Enterprise-grade MongoDB topology management system."""
    
    def __init__(self, connection_string: str):
        """Initialize topology manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for topology management")
            
        self.connection_string = connection_string
        self.client = None
        self.current_topology = None
    
    def connect(self) -> bool:
        """Connect to MongoDB cluster."""
        try:
            self.client = MongoClient(self.connection_string)
            self.client.admin.command("isMaster")
            logger.info("Connected to MongoDB cluster")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to cluster: {e}")
            return False
    
    def discover_topology(self) -> Optional[TopologyConfig]:
        """Discover current cluster topology."""
        try:
            if not self.client:
                self.connect()
            
            # Determine topology type
            is_master = self.client.admin.command("isMaster")
            
            if is_master.get("msg") == "isdbgrid":
                topology_type = TopologyType.SHARDED_CLUSTER
                return self._discover_sharded_topology()
            elif "setName" in is_master:
                topology_type = TopologyType.REPLICA_SET
                return self._discover_replica_set_topology()
            else:
                topology_type = TopologyType.STANDALONE
                return self._discover_standalone_topology()
                
        except Exception as e:
            logger.error(f"Failed to discover topology: {e}")
            return None
    
    def _discover_sharded_topology(self) -> TopologyConfig:
        """Discover sharded cluster topology."""
        # Get shard information
        shards_result = self.client.admin.command("listShards")
        replica_sets = []
        
        for shard in shards_result.get("shards", []):
            shard_config = {
                "shard_id": shard["_id"],
                "hosts": shard["host"].split(","),
                "tags": shard.get("tags", [])
            }
            replica_sets.append(shard_config)
        
        # Get config server information
        config_servers = self._get_config_servers()
        
        # Get mongos router information
        mongos_routers = self._get_mongos_routers()
        
        # Get shard zones
        shard_zones = self._get_shard_zones()
        
        return TopologyConfig(
            topology_type=TopologyType.SHARDED_CLUSTER,
            replica_sets=replica_sets,
            config_servers=config_servers,
            mongos_routers=mongos_routers,
            shard_zones=shard_zones
        )
    
    def _discover_replica_set_topology(self) -> TopologyConfig:
        """Discover replica set topology."""
        status = self.client.admin.command("replSetGetStatus")
        config = self.client.admin.command("replSetGetConfig")
        
        replica_set_config = {
            "name": status["set"],
            "members": []
        }
        
        for member in config["config"]["members"]:
            member_info = {
                "id": member["_id"],
                "host": member["host"],
                "priority": member.get("priority", 1),
                "votes": member.get("votes", 1),
                "arbiter": member.get("arbiterOnly", False),
                "hidden": member.get("hidden", False),
                "tags": member.get("tags", {})
            }
            replica_set_config["members"].append(member_info)
        
        return TopologyConfig(
            topology_type=TopologyType.REPLICA_SET,
            replica_sets=[replica_set_config],
            config_servers=[],
            mongos_routers=[],
            shard_zones=[]
        )
    
    def _discover_standalone_topology(self) -> TopologyConfig:
        """Discover standalone topology."""
        return TopologyConfig(
            topology_type=TopologyType.STANDALONE,
            replica_sets=[],
            config_servers=[],
            mongos_routers=[],
            shard_zones=[]
        )
    
    def _get_config_servers(self) -> List[Dict[str, Any]]:
        """Get config server information."""
        # This would connect to config servers to get their configuration
        return []
    
    def _get_mongos_routers(self) -> List[Dict[str, Any]]:
        """Get mongos router information."""
        # This would discover mongos routers in the cluster
        return []
    
    def _get_shard_zones(self) -> List[Dict[str, Any]]:
        """Get shard zone configurations."""
        try:
            zones = list(self.client.config.tags.find())
            return zones
        except:
            return []
    
    def create_replica_set_config(self, 
                                 replica_set_name: str,
                                 members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create replica set configuration."""
        config = {
            "_id": replica_set_name,
            "version": 1,
            "members": []
        }
        
        for i, member in enumerate(members):
            member_config = {
                "_id": i,
                "host": f"{member['host']}:{member['port']}",
                "priority": member.get("priority", 1),
                "votes": member.get("votes", 1)
            }
            
            # Optional settings
            if member.get("arbiter"):
                member_config["arbiterOnly"] = True
                member_config["priority"] = 0
            
            if member.get("hidden"):
                member_config["hidden"] = True
                member_config["priority"] = 0
            
            if member.get("slave_delay"):
                member_config["slaveDelay"] = member["slave_delay"]
                member_config["priority"] = 0
            
            if member.get("tags"):
                member_config["tags"] = member["tags"]
            
            config["members"].append(member_config)
        
        return config
    
    def create_shard_config(self, shards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create sharding configuration."""
        shard_configs = []
        
        for shard in shards:
            config = {
                "shard_id": shard["shard_id"],
                "replica_set": shard["replica_set"],
                "host": shard["host"],
                "tags": shard.get("tags", []),
                "max_size": shard.get("max_size")
            }
            shard_configs.append(config)
        
        return shard_configs
    
    def validate_topology(self, config: TopologyConfig) -> Tuple[bool, List[str]]:
        """Validate topology configuration."""
        issues = []
        
        if config.topology_type == TopologyType.REPLICA_SET:
            issues.extend(self._validate_replica_set_config(config))
        elif config.topology_type == TopologyType.SHARDED_CLUSTER:
            issues.extend(self._validate_sharded_config(config))
        
        return len(issues) == 0, issues
    
    def _validate_replica_set_config(self, config: TopologyConfig) -> List[str]:
        """Validate replica set configuration."""
        issues = []
        
        for rs_config in config.replica_sets:
            members = rs_config.get("members", [])
            
            # Check minimum members
            if len(members) < 3:
                issues.append(f"Replica set '{rs_config.get('name')}' has less than 3 members")
            
            # Check odd number of voting members
            voting_members = len([m for m in members if m.get("votes", 1) > 0])
            if voting_members % 2 == 0:
                issues.append(f"Replica set '{rs_config.get('name')}' has even number of voting members")
            
            # Check for at least one non-arbiter
            non_arbiters = len([m for m in members if not m.get("arbiter", False)])
            if non_arbiters < 2:
                issues.append(f"Replica set '{rs_config.get('name')}' needs at least 2 data-bearing members")
        
        return issues
    
    def _validate_sharded_config(self, config: TopologyConfig) -> List[str]:
        """Validate sharded cluster configuration."""
        issues = []
        
        # Check config servers
        if len(config.config_servers) == 0:
            issues.append("Sharded cluster requires config servers")
        
        # Check mongos routers
        if len(config.mongos_routers) == 0:
            issues.append("Sharded cluster requires mongos routers")
        
        # Check shards
        if len(config.replica_sets) == 0:
            issues.append("Sharded cluster requires at least one shard")
        
        return issues
    
    def optimize_topology(self, config: TopologyConfig) -> TopologyConfig:
        """Optimize topology configuration for performance."""
        optimized_config = config
        
        if config.topology_type == TopologyType.REPLICA_SET:
            optimized_config = self._optimize_replica_set(config)
        elif config.topology_type == TopologyType.SHARDED_CLUSTER:
            optimized_config = self._optimize_sharded_cluster(config)
        
        return optimized_config
    
    def _optimize_replica_set(self, config: TopologyConfig) -> TopologyConfig:
        """Optimize replica set configuration."""
        # Implement replica set optimization logic
        # - Adjust priorities based on hardware
        # - Configure read preferences
        # - Set appropriate write concerns
        return config
    
    def _optimize_sharded_cluster(self, config: TopologyConfig) -> TopologyConfig:
        """Optimize sharded cluster configuration."""
        # Implement sharded cluster optimization logic
        # - Balance shard distribution
        # - Configure zone sharding
        # - Optimize chunk sizes
        return config
    
    def generate_deployment_script(self, config: TopologyConfig) -> str:
        """Generate deployment script for the topology."""
        script_lines = []
        
        script_lines.append("#!/bin/bash")
        script_lines.append("# MongoDB Topology Deployment Script")
        script_lines.append("# Generated by Ainflue Platform")
        script_lines.append(f"# Timestamp: {datetime.now()}")
        script_lines.append("")
        
        if config.topology_type == TopologyType.REPLICA_SET:
            script_lines.extend(self._generate_replica_set_script(config))
        elif config.topology_type == TopologyType.SHARDED_CLUSTER:
            script_lines.extend(self._generate_sharded_script(config))
        
        return "\n".join(script_lines)
    
    def _generate_replica_set_script(self, config: TopologyConfig) -> List[str]:
        """Generate replica set deployment script."""
        lines = []
        
        for rs_config in config.replica_sets:
            lines.append(f"# Replica Set: {rs_config.get('name')}")
            
            # Start mongod instances
            for member in rs_config.get("members", []):
                host, port = member["host"].split(":")
                lines.append(f"mongod --replSet {rs_config.get('name')} --port {port} --dbpath /data/db/{port} --fork --logpath /var/log/mongodb/{port}.log")
            
            lines.append("")
            
            # Initialize replica set
            lines.append("# Initialize replica set")
            rs_init_config = self.create_replica_set_config(
                rs_config.get("name"),
                rs_config.get("members", [])
            )
            lines.append(f"mongo --eval 'rs.initiate({rs_init_config})'")
            lines.append("")
        
        return lines
    
    def _generate_sharded_script(self, config: TopologyConfig) -> List[str]:
        """Generate sharded cluster deployment script."""
        lines = []
        
        # Config servers
        lines.append("# Start config servers")
        for cs in config.config_servers:
            lines.append(f"mongod --configsvr --replSet configReplSet --port {cs['port']} --dbpath /data/configdb --fork")
        lines.append("")
        
        # Mongos routers
        lines.append("# Start mongos routers")
        for mongos in config.mongos_routers:
            lines.append(f"mongos --configdb configReplSet/{','.join([f'{cs[\"host\"]}:{cs[\"port\"]}' for cs in config.config_servers])} --port {mongos['port']} --fork")
        lines.append("")
        
        # Shards
        lines.append("# Add shards")
        for shard in config.replica_sets:
            lines.append(f"mongo --eval 'sh.addShard(\"{shard['name']}/{','.join([m['host'] for m in shard['members']])}\")'")
        
        return lines
    
    def get_topology_summary(self) -> Dict[str, Any]:
        """Get comprehensive topology summary."""
        current_topology = self.discover_topology()
        
        if not current_topology:
            return {"error": "Could not discover topology"}
        
        summary = {
            "topology_type": current_topology.topology_type.value,
            "replica_sets": len(current_topology.replica_sets),
            "config_servers": len(current_topology.config_servers),
            "mongos_routers": len(current_topology.mongos_routers),
            "shard_zones": len(current_topology.shard_zones),
            "discovered_at": datetime.now()
        }
        
        # Add detailed information
        if current_topology.topology_type == TopologyType.REPLICA_SET:
            rs_details = []
            for rs in current_topology.replica_sets:
                rs_details.append({
                    "name": rs.get("name"),
                    "members": len(rs.get("members", [])),
                    "voting_members": len([m for m in rs.get("members", []) if m.get("votes", 1) > 0])
                })
            summary["replica_set_details"] = rs_details
        
        return summary
    
    def close(self):
        """Close topology manager connections."""
        if self.client:
            self.client.close()

# Export the main class
__all__ = ['TopologyManager', 'TopologyConfig', 'TopologyType', 'TopologyNode']