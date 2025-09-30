"""MongoDB Sharding Manager
========================

Advanced MongoDB sharding configuration and management for horizontal scaling
of the Ainflue platform database infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    pymongo = None

logger = logging.getLogger(__name__)

class ShardState(Enum):
    """Shard state enumeration."""
    ACTIVE = "active"
    DRAINING = "draining"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

@dataclass
class ShardInfo:
    """Shard information."""
    shard_id: str
    host: str
    state: ShardState
    size_mb: int
    chunks: int
    collections: int
    tags: List[str]
    max_size_mb: Optional[int] = None

@dataclass
class ChunkInfo:
    """Chunk information."""
    namespace: str
    min_key: Dict[str, Any]
    max_key: Dict[str, Any]
    shard: str
    estimated_size_mb: int
    object_count: int

class ShardManager:
    """Enterprise-grade MongoDB sharding management system."""
    
    def __init__(self, mongos_connection_string: str, config_server_string: str):
        """Initialize shard manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for shard management")
            
        self.mongos_connection = mongos_connection_string
        self.config_connection = config_server_string
        self.mongos_client = None
        self.config_client = None
        
    def connect(self):
        """Establish connections to mongos and config servers."""
        try:
            self.mongos_client = MongoClient(self.mongos_connection)
            self.config_client = MongoClient(self.config_connection)
            
            # Test connections
            self.mongos_client.admin.command("isMaster")
            self.config_client.admin.command("isMaster")
            
            logger.info("Successfully connected to mongos and config servers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to sharding infrastructure: {e}")
            return False
    
    def add_shard(self, shard_connection_string: str, shard_name: Optional[str] = None) -> bool:
        """Add a new shard to the cluster."""
        try:
            if not self.mongos_client:
                self.connect()
            
            command = {"addShard": shard_connection_string}
            if shard_name:
                command["name"] = shard_name
            
            result = self.mongos_client.admin.command(command)
            
            if result.get("ok") == 1:
                logger.info(f"Successfully added shard: {shard_connection_string}")
                return True
            else:
                logger.error(f"Failed to add shard: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding shard: {e}")
            return False
    
    def remove_shard(self, shard_name: str, force: bool = False) -> bool:
        """Remove a shard from the cluster."""
        try:
            if not self.mongos_client:
                self.connect()
            
            # Start shard removal process
            result = self.mongos_client.admin.command("removeShard", shard_name)
            
            if result.get("state") == "started":
                logger.info(f"Shard removal started for: {shard_name}")
                
                if force:
                    # Force immediate removal (dangerous - only for empty shards)
                    final_result = self.mongos_client.admin.command("removeShard", shard_name)
                    if final_result.get("state") == "completed":
                        logger.info(f"Shard {shard_name} removed successfully")
                        return True
                else:
                    logger.info(f"Shard {shard_name} is draining. Run remove again when complete.")
                    return True
            elif result.get("state") == "completed":
                logger.info(f"Shard {shard_name} removed successfully")
                return True
            else:
                logger.error(f"Failed to remove shard: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing shard: {e}")
            return False
    
    def enable_sharding(self, database_name: str) -> bool:
        """Enable sharding for a database."""
        try:
            if not self.mongos_client:
                self.connect()
            
            result = self.mongos_client.admin.command("enableSharding", database_name)
            
            if result.get("ok") == 1:
                logger.info(f"Sharding enabled for database: {database_name}")
                return True
            else:
                logger.error(f"Failed to enable sharding: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error enabling sharding: {e}")
            return False
    
    def shard_collection(self, 
                        namespace: str, 
                        shard_key: Dict[str, int],
                        unique: bool = False,
                        pre_split: bool = False) -> bool:
        """Shard a collection with the specified shard key."""
        try:
            if not self.mongos_client:
                self.connect()
            
            command = {
                "shardCollection": namespace,
                "key": shard_key
            }
            
            if unique:
                command["unique"] = True
                
            result = self.mongos_client.admin.command(command)
            
            if result.get("ok") == 1:
                logger.info(f"Collection {namespace} sharded successfully")
                
                if pre_split:
                    self._create_initial_chunks(namespace, shard_key)
                
                return True
            else:
                logger.error(f"Failed to shard collection: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error sharding collection: {e}")
            return False
    
    def get_shard_status(self) -> List[ShardInfo]:
        """Get comprehensive status of all shards."""
        try:
            if not self.mongos_client:
                self.connect()
            
            # Get shard list
            shards_result = self.mongos_client.admin.command("listShards")
            shards = []
            
            for shard in shards_result["shards"]:
                # Get shard statistics
                shard_stats = self._get_shard_stats(shard["_id"])
                
                shard_info = ShardInfo(
                    shard_id=shard["_id"],
                    host=shard["host"],
                    state=ShardState(shard.get("state", "active")),
                    size_mb=shard_stats.get("size_mb", 0),
                    chunks=shard_stats.get("chunks", 0),
                    collections=shard_stats.get("collections", 0),
                    tags=shard.get("tags", []),
                    max_size_mb=shard.get("maxSize")
                )
                
                shards.append(shard_info)
            
            return shards
            
        except Exception as e:
            logger.error(f"Error getting shard status: {e}")
            return []
    
    def balance_shards(self, enable: bool = True) -> bool:
        """Enable or disable the balancer."""
        try:
            if not self.mongos_client:
                self.connect()
            
            if enable:
                result = self.mongos_client.admin.command("balancerStart")
                action = "enabled"
            else:
                result = self.mongos_client.admin.command("balancerStop")
                action = "disabled"
            
            if result.get("ok") == 1:
                logger.info(f"Balancer {action} successfully")
                return True
            else:
                logger.error(f"Failed to {action.replace('ed', '')} balancer: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error controlling balancer: {e}")
            return False
    
    def get_balancer_status(self) -> Dict[str, Any]:
        """Get balancer status and statistics."""
        try:
            if not self.mongos_client:
                self.connect()
            
            # Check if balancer is running
            balancer_status = self.mongos_client.admin.command("balancerStatus")
            
            # Get balancer collection locks
            locks = list(self.config_client.config.locks.find())
            
            # Get recent balancer rounds
            balancer_history = list(
                self.config_client.config.actionlog.find(
                    {"what": {"$in": ["balancer.round", "moveChunk.commit"]}},
                    sort=[("time", -1)],
                    limit=10
                )
            )
            
            return {
                "enabled": balancer_status.get("mode") == "full",
                "running": balancer_status.get("inBalancerRound", False),
                "locks": locks,
                "recent_activity": balancer_history
            }
            
        except Exception as e:
            logger.error(f"Error getting balancer status: {e}")
            return {}
    
    def move_chunk(self, namespace: str, chunk_bounds: Dict[str, Any], to_shard: str) -> bool:
        """Move a specific chunk to a target shard."""
        try:
            if not self.mongos_client:
                self.connect()
            
            result = self.mongos_client.admin.command(
                "moveChunk",
                namespace,
                bounds=[chunk_bounds["min"], chunk_bounds["max"]],
                to=to_shard
            )
            
            if result.get("ok") == 1:
                logger.info(f"Chunk moved successfully to shard: {to_shard}")
                return True
            else:
                logger.error(f"Failed to move chunk: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error moving chunk: {e}")
            return False
    
    def split_chunk(self, namespace: str, split_point: Dict[str, Any]) -> bool:
        """Split a chunk at the specified point."""
        try:
            if not self.mongos_client:
                self.connect()
            
            result = self.mongos_client.admin.command(
                "splitChunk",
                namespace,
                middle=split_point
            )
            
            if result.get("ok") == 1:
                logger.info("Chunk split successfully")
                return True
            else:
                logger.error(f"Failed to split chunk: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error splitting chunk: {e}")
            return False
    
    def get_chunk_distribution(self, namespace: str) -> List[ChunkInfo]:
        """Get chunk distribution for a sharded collection."""
        try:
            if not self.config_client:
                self.connect()
            
            chunks = list(
                self.config_client.config.chunks.find(
                    {"ns": namespace},
                    sort=[("min", 1)]
                )
            )
            
            chunk_info = []
            for chunk in chunks:
                # Estimate chunk size (simplified)
                estimated_size = self._estimate_chunk_size(namespace, chunk)
                
                info = ChunkInfo(
                    namespace=chunk["ns"],
                    min_key=chunk["min"],
                    max_key=chunk["max"],
                    shard=chunk["shard"],
                    estimated_size_mb=estimated_size,
                    object_count=0  # Would need additional query to get accurate count
                )
                chunk_info.append(info)
            
            return chunk_info
            
        except Exception as e:
            logger.error(f"Error getting chunk distribution: {e}")
            return []
    
    def add_shard_tag(self, shard_name: str, tag: str) -> bool:
        """Add a tag to a shard for zone sharding."""
        try:
            if not self.mongos_client:
                self.connect()
            
            result = self.mongos_client.admin.command("addShardTag", shard_name, tag)
            
            if result.get("ok") == 1:
                logger.info(f"Tag '{tag}' added to shard: {shard_name}")
                return True
            else:
                logger.error(f"Failed to add shard tag: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding shard tag: {e}")
            return False
    
    def remove_shard_tag(self, shard_name: str, tag: str) -> bool:
        """Remove a tag from a shard."""
        try:
            if not self.mongos_client:
                self.connect()
            
            result = self.mongos_client.admin.command("removeShardTag", shard_name, tag)
            
            if result.get("ok") == 1:
                logger.info(f"Tag '{tag}' removed from shard: {shard_name}")
                return True
            else:
                logger.error(f"Failed to remove shard tag: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing shard tag: {e}")
            return False
    
    def _get_shard_stats(self, shard_id: str) -> Dict[str, Any]:
        """Get statistics for a specific shard."""
        try:
            # Connect directly to the shard to get detailed stats
            # This is simplified - in production, you'd need shard-specific connections
            return {
                "size_mb": 0,
                "chunks": 0,
                "collections": 0
            }
        except:
            return {}
    
    def _create_initial_chunks(self, namespace: str, shard_key: Dict[str, int]):
        """Create initial chunks for better distribution."""
        try:
            # This would implement pre-splitting logic based on shard key type
            # For example, if shard key is _id, create chunks based on ObjectId ranges
            logger.info(f"Creating initial chunks for {namespace}")
        except Exception as e:
            logger.error(f"Error creating initial chunks: {e}")
    
    def _estimate_chunk_size(self, namespace: str, chunk: Dict[str, Any]) -> int:
        """Estimate the size of a chunk in MB."""
        # Simplified estimation - in production, this would use collection stats
        return 64  # Default chunk size estimate
    
    def close(self):
        """Close database connections."""
        if self.mongos_client:
            self.mongos_client.close()
        if self.config_client:
            self.config_client.close()

# Export the main class
__all__ = ['ShardManager', 'ShardInfo', 'ChunkInfo', 'ShardState']