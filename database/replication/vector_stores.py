"""
Vector Store Replication Handler - IA Influencer Agent Platform

Advanced vector database replication for FAISS, Pinecone, Chroma, and Weaviate
supporting content fingerprinting, similarity search, and AI embeddings replication.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timedelta
import numpy as np
import faiss
import pickle
import os
from pathlib import Path
import aiofiles
import gzip
import json
from .config import ReplicationConfig


class VectorStoreReplicationHandler:
    """
    Vector store replication handler for multiple vector database systems.
    
    Supports replication for:
    - FAISS (Facebook AI Similarity Search)
    - Pinecone vector database
    - Chroma vector database
    - Weaviate vector database
    - Custom vector storage systems
    
    Provides capabilities for:
    - Index backup and synchronization
    - Cross-region vector replication
    - Incremental vector updates
    - Conflict resolution for vector data
    - Performance monitoring
    """
    
    def __init__(self, config: Dict[str, Any], replication_config: ReplicationConfig):
        """
        Initialize vector store replication handler.
        
        Args:
            config: Vector store specific configuration
            replication_config: Global replication configuration
        """
        self.config = config
        self.replication_config = replication_config
        self.logger = logging.getLogger(f"{__name__}.VectorStoreReplicationHandler")
        
        # Vector store configuration
        self.store_type = config.get("store_type", "faiss")
        self.dimension = config.get("dimension", 512)
        self.index_type = config.get("index_type", "IVFFlat")
        self.backup_path = config.get("backup_path", "/tmp/vector_backups")
        
        # Replication settings
        self.sync_frequency = config.get("sync_frequency", 3600)  # seconds
        self.compression_enabled = config.get("compression_enabled", True)
        self.incremental_sync = config.get("incremental_sync", True)
        
        # Store connections
        self.primary_store: Optional[Any] = None
        self.secondary_stores: Dict[str, Any] = {}
        
        # FAISS specific
        self.faiss_index: Optional[faiss.Index] = None
        self.faiss_id_map: Dict[str, int] = {}
        self.faiss_metadata: Dict[int, Dict[str, Any]] = {}
        
        # External stores
        self.pinecone_client = None
        self.chroma_client = None
        self.weaviate_client = None
        
        # Monitoring
        self.is_monitoring = False
        self.last_sync_timestamp: Optional[datetime] = None
        self.sync_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.metrics = {
            "vectors_count": 0,
            "vectors_replicated": 0,
            "last_backup_size": 0,
            "sync_duration_ms": 0,
            "last_sync_time": None,
            "error_count": 0,
            "index_size_bytes": 0,
            "query_performance_ms": 0
        }
        
        # Ensure backup directory exists
        os.makedirs(self.backup_path, exist_ok=True)
        
        self.logger.info(f"VectorStoreReplicationHandler initialized for {self.store_type}")
    
    async def initialize(self) -> bool:
        """
        Initialize vector store replication connections and configuration.
        
        Returns:
            bool: True if initialization successful
        """



        try:
            self.logger.info("Initializing vector store replication handler...")
            
            # Initialize primary store
            await self._initialize_primary_store()
            
            # Initialize secondary stores
            await self._initialize_secondary_stores()
            
            # Load existing indices if available
            await self._load_existing_indices()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            self.logger.info("Vector store replication handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store replication handler: {e}")
            return False
    
    async def _initialize_primary_store(self) -> None:
        """Initialize primary vector store connection"""



        try:
            if self.store_type == "faiss":
                await self._initialize_faiss()
            elif self.store_type == "pinecone":
                await self._initialize_pinecone()
            elif self.store_type == "chroma":
                await self._initialize_chroma()
            elif self.store_type == "weaviate":
                await self._initialize_weaviate()
            else:
                raise ValueError(f"Unsupported vector store type: {self.store_type}")
            
            self.logger.info(f"Primary {self.store_type} store initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize primary store: {e}")
            raise
    
    async def _initialize_faiss(self) -> None:
        """Initialize FAISS vector store"""



        try:
            # Create FAISS index based on configuration
            if self.index_type == "IVFFlat":
                # Create IVF (Inverted File) index
                quantizer = faiss.IndexFlatL2(self.dimension)
                nlist = self.config.get("nlist", 100)
                self.faiss_index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
                
            elif self.index_type == "IVFPQ":
                # Create IVF with Product Quantization
                quantizer = faiss.IndexFlatL2(self.dimension)
                nlist = self.config.get("nlist", 100)
                m = self.config.get("pq_m", 8)  # Number of subquantizers
                self.faiss_index = faiss.IndexIVFPQ(quantizer, self.dimension, nlist, m, 8)
                
            elif self.index_type == "HNSW":
                # Create Hierarchical Navigable Small World index
                m = self.config.get("hnsw_m", 16)
                self.faiss_index = faiss.IndexHNSWFlat(self.dimension, m)
                
            else:
                # Default to flat L2 index
                self.faiss_index = faiss.IndexFlatL2(self.dimension)
            
            # Set to GPU if available and configured
            if self.config.get("use_gpu", False) and faiss.get_num_gpus() > 0:
                res = faiss.StandardGpuResources()
                self.faiss_index = faiss.index_cpu_to_gpu(res, 0, self.faiss_index)
                self.logger.info("FAISS index moved to GPU")
            
            self.primary_store = self.faiss_index
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FAISS: {e}")
            raise
    
    async def _initialize_pinecone(self) -> None:
        """Initialize Pinecone vector store"""



        try:
            import pinecone
            
            api_key = self.config.get("api_key")
            environment = self.config.get("environment", "us-east1-gcp")
            
            if not api_key:
                raise ValueError("Pinecone API key not provided")
            
            pinecone.init(api_key=api_key, environment=environment)
            
            index_name = self.config.get("index_name", "ia-influencer-vectors")
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=self.dimension,
                    metric=self.config.get("metric", "cosine"),
                    shards=self.config.get("shards", 1),
                    replicas=self.config.get("replicas", 1)
                )
                self.logger.info(f"Created Pinecone index: {index_name}")
            
            self.pinecone_client = pinecone.Index(index_name)
            self.primary_store = self.pinecone_client
            
        except ImportError:
            self.logger.error("Pinecone library not installed")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    async def _initialize_chroma(self) -> None:
        """Initialize Chroma vector store"""



        try:
            import chromadb
            
            # Create Chroma client
            if self.config.get("persist_directory"):
                self.chroma_client = chromadb.PersistentClient(
                    path=self.config["persist_directory"]
                )
            else:
                self.chroma_client = chromadb.Client()
            
            collection_name = self.config.get("collection_name", "ia_influencer_vectors")
            
            # Get or create collection
            try:
                self.primary_store = self.chroma_client.get_collection(collection_name)
            except:
                self.primary_store = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"dimension": self.dimension}
                )
                self.logger.info(f"Created Chroma collection: {collection_name}")
            
        except ImportError:
            self.logger.error("Chroma library not installed")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Chroma: {e}")
            raise
    
    async def _initialize_weaviate(self) -> None:
        """Initialize Weaviate vector store"""



        try:
            import weaviate
            
            url = self.config.get("url", "http://localhost:8080")
            auth_config = None
            
            if self.config.get("api_key"):
                auth_config = weaviate.AuthApiKey(api_key=self.config["api_key"])
            
            self.weaviate_client = weaviate.Client(
                url=url,
                auth_client_secret=auth_config
            )
            
            # Check connection
            if not self.weaviate_client.is_ready():
                raise ConnectionError("Weaviate server not ready")
            
            self.primary_store = self.weaviate_client
            
        except ImportError:
            self.logger.error("Weaviate library not installed")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Weaviate: {e}")
            raise
    
    async def _initialize_secondary_stores(self) -> None:
        """Initialize secondary vector store connections"""
        secondary_configs = self.config.get("secondaries", [])
        
        for idx, secondary_config in enumerate(secondary_configs):
            try:
                store_name = f"secondary_{idx}"
                
                if secondary_config.get("store_type") == "faiss":
                    # Initialize secondary FAISS store
                    secondary_store = await self._create_faiss_index(secondary_config)
                    self.secondary_stores[store_name] = secondary_store
                    
                elif secondary_config.get("store_type") == "pinecone":
                    # Initialize secondary Pinecone store
                    secondary_store = await self._create_pinecone_client(secondary_config)
                    self.secondary_stores[store_name] = secondary_store
                
                self.logger.info(f"Secondary store initialized: {store_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize secondary store {idx}: {e}")
    
    async def _create_faiss_index(self, config: Dict[str, Any]) -> faiss.Index:
        """Create FAISS index from configuration"""
        # Similar to _initialize_faiss but for secondary stores
        dimension = config.get("dimension", self.dimension)
        index_type = config.get("index_type", "IndexFlatL2")
        
        if index_type == "IVFFlat":
            quantizer = faiss.IndexFlatL2(dimension)
            nlist = config.get("nlist", 100)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        else:
            index = faiss.IndexFlatL2(dimension)
        
        return index
    
    async def _create_pinecone_client(self, config: Dict[str, Any]):
        """Create Pinecone client from configuration"""
        import pinecone
        
        api_key = config.get("api_key")
        environment = config.get("environment", "us-east1-gcp")
        index_name = config.get("index_name")
        
        pinecone.init(api_key=api_key, environment=environment)
        return pinecone.Index(index_name)
    
    async def _load_existing_indices(self) -> None:
        """Load existing vector indices from backup"""



        try:
            backup_files = list(Path(self.backup_path).glob("*.faiss"))
            
            if backup_files and self.store_type == "faiss":
                # Load the most recent backup
                latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                
                self.logger.info(f"Loading FAISS index from backup: {latest_backup}")
                
                # Load index
                loaded_index = faiss.read_index(str(latest_backup))
                
                if self.faiss_index.d == loaded_index.d:
                    self.faiss_index = loaded_index
                    self.primary_store = self.faiss_index
                    
                    # Load metadata if available
                    metadata_file = latest_backup.with_suffix('.metadata.pkl')
                    if metadata_file.exists():
                        with open(metadata_file, 'rb') as f:
                            self.faiss_metadata = pickle.load(f)
                    
                    # Load ID mapping
                    id_map_file = latest_backup.with_suffix('.idmap.pkl')
                    if id_map_file.exists():
                        with open(id_map_file, 'rb') as f:
                            self.faiss_id_map = pickle.load(f)
                    
                    self.metrics["vectors_count"] = self.faiss_index.ntotal
                    self.logger.info(f"Loaded {self.faiss_index.ntotal} vectors from backup")
                else:
                    self.logger.warning("Backup dimension mismatch, starting with empty index")
            
        except Exception as e:
            self.logger.error(f"Failed to load existing indices: {e}")
    
    async def _setup_monitoring(self) -> None:
        """Setup vector store replication monitoring"""
        self.is_monitoring = True
        self.sync_task = asyncio.create_task(self._periodic_sync())
        self.logger.info("Vector store replication monitoring started")
    
    async def start_replication(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any], 
        mode: str = "backup_sync"
    ) -> bool:
        """
        Start vector store replication process.
        
        Args:
            source_config: Source vector store configuration
            target_config: Target vector store configuration
            mode: Replication mode (backup_sync, real_time, incremental)
            
        Returns:
            bool: True if replication started successfully
        """



        try:
            self.logger.info(f"Starting vector store replication in {mode} mode")
            
            if mode == "backup_sync":
                return await self._start_backup_sync(source_config, target_config)
            elif mode == "real_time":
                return await self._start_real_time_sync(source_config, target_config)
            elif mode == "incremental":
                return await self._start_incremental_sync(source_config, target_config)
            else:
                self.logger.error(f"Unsupported replication mode: {mode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start vector store replication: {e}")
            return False
    
    async def _start_backup_sync(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start backup-based synchronization"""



        try:
            # Create initial backup
            backup_file = await self._create_backup()
            
            if backup_file:
                # Schedule periodic backups
                asyncio.create_task(self._schedule_backups())
                
                # Sync to target stores
                for store_name, store in self.secondary_stores.items():
                    asyncio.create_task(self._sync_backup_to_store(backup_file, store_name, store))
                
                self.logger.info("Backup-based replication started")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start backup sync: {e}")
            return False
    
    async def _start_real_time_sync(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start real-time synchronization"""



        try:
            # Real-time sync not directly supported by FAISS
            # We'll use incremental sync with shorter intervals
            self.sync_frequency = 60  # 1 minute for real-time feel
            
            asyncio.create_task(self._real_time_sync_loop())
            
            self.logger.info("Real-time replication started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time sync: {e}")
            return False
    
    async def _start_incremental_sync(
        self, 
        source_config: Dict[str, Any], 
        target_config: Dict[str, Any]
    ) -> bool:
        """Start incremental synchronization"""



        try:
            # Track changes for incremental sync
            self.incremental_sync = True
            
            # Start periodic incremental sync
            asyncio.create_task(self._incremental_sync_loop())
            
            self.logger.info("Incremental replication started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start incremental sync: {e}")
            return False
    
    async def _create_backup(self) -> Optional[str]:
        """Create backup of current vector index"""



        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_path, f"vector_index_{timestamp}.faiss")
            
            if self.store_type == "faiss" and self.faiss_index:
                # Save FAISS index
                faiss.write_index(self.faiss_index, backup_file)
                
                # Save metadata
                metadata_file = backup_file.replace('.faiss', '.metadata.pkl')
                with open(metadata_file, 'wb') as f:
                    pickle.dump(self.faiss_metadata, f)
                
                # Save ID mapping
                id_map_file = backup_file.replace('.faiss', '.idmap.pkl')
                with open(id_map_file, 'wb') as f:
                    pickle.dump(self.faiss_id_map, f)
                
                # Compress if enabled
                if self.compression_enabled:
                    compressed_file = backup_file + '.gz'
                    with open(backup_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    os.remove(backup_file)
                    backup_file = compressed_file
                
                backup_size = os.path.getsize(backup_file)
                self.metrics["last_backup_size"] = backup_size
                self.metrics["last_sync_time"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"Created vector backup: {backup_file} ({backup_size} bytes)")
                return backup_file
            
            elif self.store_type == "pinecone":
                # For Pinecone, we'll export vectors to a backup file
                backup_data = await self._export_pinecone_vectors()
                
                with open(backup_file.replace('.faiss', '.pkl'), 'wb') as f:
                    pickle.dump(backup_data, f)
                
                self.logger.info(f"Created Pinecone backup: {backup_file}")
                return backup_file
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    async def _export_pinecone_vectors(self) -> Dict[str, Any]:
        """Export vectors from Pinecone for backup"""



        try:
            # Pinecone doesn't support full export, so we'll track inserted vectors
            # This is a simplified implementation
            vectors = {}
            
            # Get index stats
            stats = self.pinecone_client.describe_index_stats()
            
            return {
                "stats": stats,
                "vectors": vectors,  # Would need to track insertions
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export Pinecone vectors: {e}")
            return {}
    
    async def _periodic_sync(self) -> None:
        """Periodic synchronization task"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(self.sync_frequency)
                
                # Create backup
                backup_file = await self._create_backup()
                
                if backup_file:
                    # Sync to all secondary stores
                    for store_name, store in self.secondary_stores.items():
                        await self._sync_backup_to_store(backup_file, store_name, store)
                
                # Update metrics
                self.metrics["vectors_count"] = self._get_vector_count()
                
                # Clean old backups
                await self._cleanup_old_backups()
                
            except Exception as e:
                self.logger.error(f"Error in periodic sync: {e}")
                self.metrics["error_count"] += 1
    
    async def _sync_backup_to_store(self, backup_file: str, store_name: str, store: Any) -> None:
        """Sync backup to specific store"""



        try:
            if backup_file.endswith('.gz'):
                # Decompress first
                temp_file = backup_file.replace('.gz', '')
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        f_out.write(f_in.read())
                backup_file = temp_file
            
            # Load and sync to target store
            if isinstance(store, faiss.Index):
                # Sync to secondary FAISS store
                loaded_index = faiss.read_index(backup_file)
                
                # Clear existing index
                store.reset()
                
                # Add vectors from backup
                if loaded_index.ntotal > 0:
                    vectors = []
                    for i in range(loaded_index.ntotal):
                        vector = loaded_index.reconstruct(i)
                        vectors.append(vector)
                    
                    if vectors:
                        vectors_array = np.array(vectors)
                        store.add(vectors_array)
                
                self.metrics["vectors_replicated"] += loaded_index.ntotal
                self.logger.info(f"Synced {loaded_index.ntotal} vectors to {store_name}")
            
            # Clean up temp file if created
            if backup_file.endswith('.faiss'):
                os.remove(backup_file)
                
        except Exception as e:
            self.logger.error(f"Failed to sync backup to {store_name}: {e}")
    
    def _get_vector_count(self) -> int:
        """Get current vector count from primary store"""



        try:
            if self.store_type == "faiss" and self.faiss_index:
                return self.faiss_index.ntotal
            elif self.store_type == "pinecone" and self.pinecone_client:
                stats = self.pinecone_client.describe_index_stats()
                return stats.get("total_vector_count", 0)
            elif self.store_type == "chroma" and self.primary_store:
                return self.primary_store.count()
            else:
                return 0
        except Exception:
            return 0
    
    async def _cleanup_old_backups(self) -> None:
        """Clean up old backup files"""



        try:
            backup_files = list(Path(self.backup_path).glob("vector_index_*.faiss*"))
            
            # Keep only the last N backups
            max_backups = self.config.get("max_backups", 10)
            
            if len(backup_files) > max_backups:
                # Sort by modification time and remove oldest
                backup_files.sort(key=lambda p: p.stat().st_mtime)
                files_to_remove = backup_files[:-max_backups]
                
                for file_path in files_to_remove:
                    os.remove(file_path)
                    
                    # Remove associated metadata files
                    metadata_file = str(file_path).replace('.faiss', '.metadata.pkl')
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)
                    
                    id_map_file = str(file_path).replace('.faiss', '.idmap.pkl')
                    if os.path.exists(id_map_file):
                        os.remove(id_map_file)
                
                self.logger.info(f"Cleaned up {len(files_to_remove)} old backup files")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    async def stop_replication(self, graceful: bool = True) -> bool:
        """
        Stop vector store replication.
        
        Args:
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if stopped successfully
        """



        try:
            self.logger.info(f"Stopping vector store replication (graceful={graceful})")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
            
            if graceful:
                # Create final backup
                await self._create_backup()
                
                # Wait for pending operations
                await asyncio.sleep(2)
            
            self.logger.info("Vector store replication stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop vector store replication: {e}")
            return False
    
    async def pause_replication(self) -> bool:
        """
        Pause vector store replication.
        
        Returns:
            bool: True if paused successfully
        """



        try:
            self.logger.info("Pausing vector store replication")
            
            # Cancel sync task but keep monitoring
            if self.sync_task:
                self.sync_task.cancel()
                self.sync_task = None
            
            self.logger.info("Vector store replication paused")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause vector store replication: {e}")
            return False
    
    async def resume_replication(self) -> bool:
        """
        Resume vector store replication.
        
        Returns:
            bool: True if resumed successfully
        """



        try:
            self.logger.info("Resuming vector store replication")
            
            # Restart sync task
            if not self.sync_task or self.sync_task.cancelled():
                self.sync_task = asyncio.create_task(self._periodic_sync())
            
            self.logger.info("Vector store replication resumed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume vector store replication: {e}")
            return False
    
    async def trigger_sync(self, force: bool = False) -> bool:
        """
        Trigger manual synchronization.
        
        Args:
            force: Whether to force synchronization
            
        Returns:
            bool: True if sync triggered successfully
        """



        try:
            self.logger.info(f"Triggering vector store sync (force={force})")
            
            start_time = datetime.utcnow()
            
            # Create backup
            backup_file = await self._create_backup()
            
            if backup_file:
                # Sync to all secondary stores
                for store_name, store in self.secondary_stores.items():
                    await self._sync_backup_to_store(backup_file, store_name, store)
            
            # Update sync metrics
            sync_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics["sync_duration_ms"] = sync_duration
            self.metrics["last_sync_time"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Vector store sync completed in {sync_duration:.1f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger vector store sync: {e}")
            return False
    
    async def prepare_maintenance(self, duration: timedelta) -> bool:
        """
        Prepare for maintenance mode.
        
        Args:
            duration: Expected maintenance duration
            
        Returns:
            bool: True if preparation successful
        """



        try:
            self.logger.info(f"Preparing vector store for maintenance (duration: {duration})")
            
            # Create backup before maintenance
            backup_file = await self._create_backup()
            
            if not backup_file:
                self.logger.error("Failed to create maintenance backup")
                return False
            
            # Pause replication
            await self.pause_replication()
            
            self.logger.info("Vector store prepared for maintenance")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare vector store for maintenance: {e}")
            return False
    
    async def exit_maintenance(self) -> bool:
        """
        Exit maintenance mode.
        
        Returns:
            bool: True if exit successful
        """



        try:
            self.logger.info("Exiting vector store maintenance mode")
            
            # Resume replication
            await self.resume_replication()
            
            # Trigger sync to ensure consistency
            await self.trigger_sync(force=True)
            
            self.logger.info("Vector store maintenance mode exited successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to exit vector store maintenance mode: {e}")
            return False
    
    async def get_replication_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive replication metrics.
        
        Returns:
            Dict containing replication metrics
        """



        try:
            # Update current metrics
            self.metrics["vectors_count"] = self._get_vector_count()
            
            if self.store_type == "faiss" and self.faiss_index:
                # Calculate index size
                temp_file = os.path.join(self.backup_path, "temp_size_check.faiss")
                faiss.write_index(self.faiss_index, temp_file)
                self.metrics["index_size_bytes"] = os.path.getsize(temp_file)
                os.remove(temp_file)
                
                # Test query performance
                if self.faiss_index.ntotal > 0:
                    test_vector = np.random.random((1, self.dimension)).astype('float32')
                    start_time = datetime.utcnow()
                    self.faiss_index.search(test_vector, 1)
                    query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    self.metrics["query_performance_ms"] = query_time
            
            self.metrics["last_sync_time"] = datetime.utcnow().isoformat()
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get vector store replication metrics: {e}")
            return self.metrics
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check vector store replication health.
        
        Returns:
            Dict containing health status
        """
        health = {
            "healthy": False,
            "store_available": False,
            "backups_recent": False,
            "secondaries_synced": False,
            "issues": []
        }
        
        try:
            # Check primary store availability
            if self.primary_store is not None:
                health["store_available"] = True
                
                # Check if we can query the store
                if self.store_type == "faiss" and self.faiss_index:
                    if self.faiss_index.ntotal > 0:
                        test_vector = np.random.random((1, self.dimension)).astype('float32')
                        self.faiss_index.search(test_vector, 1)
                elif self.store_type == "pinecone" and self.pinecone_client:
                    self.pinecone_client.describe_index_stats()
            else:
                health["issues"].append("Primary store not available")
            
            # Check backup recency
            if self.last_sync_timestamp:
                time_since_backup = datetime.utcnow() - self.last_sync_timestamp
                if time_since_backup < timedelta(hours=24):
                    health["backups_recent"] = True
                else:
                    health["issues"].append(f"Last backup was {time_since_backup} ago")
            else:
                health["issues"].append("No backup timestamp available")
            
            # Check secondary stores
            if self.secondary_stores:
                healthy_secondaries = 0
                for store_name, store in self.secondary_stores.items():
                    try:
                        if isinstance(store, faiss.Index):
                            # Simple health check for FAISS
                            if store.ntotal >= 0:
                                healthy_secondaries += 1
                        else:
                            healthy_secondaries += 1
                    except Exception as e:
                        health["issues"].append(f"Secondary store {store_name} unhealthy: {e}")
                
                health["secondaries_synced"] = healthy_secondaries == len(self.secondary_stores)
                health["healthy_secondaries"] = healthy_secondaries
            else:
                health["secondaries_synced"] = True  # No secondaries to check
            
            # Overall health
            health["healthy"] = (
                health["store_available"] and
                health["backups_recent"] and
                health["secondaries_synced"] and
                len(health["issues"]) == 0
            )
            
        except Exception as e:
            health["issues"].append(f"Health check error: {str(e)}")
        
        return health
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed vector store replication status.
        
        Returns:
            Dict containing detailed status information
        """



        try:
            status = {
                "handler_type": "vector_store",
                "store_type": self.store_type,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "backup_path": self.backup_path,
                "compression_enabled": self.compression_enabled,
                "incremental_sync": self.incremental_sync,
                "sync_frequency": self.sync_frequency,
                "monitoring_active": self.is_monitoring,
                "vectors_count": self._get_vector_count(),
                "secondary_stores": len(self.secondary_stores),
                "metrics": self.metrics
            }
            
            if self.store_type == "faiss" and self.faiss_index:
                status["faiss_trained"] = self.faiss_index.is_trained
                status["faiss_ntotal"] = self.faiss_index.ntotal
            
            return status
            
        except Exception as e:
            return {
                "handler_type": "vector_store",
                "error": str(e),
                "metrics": self.metrics
            }
    
    async def shutdown(self) -> None:
        """Shutdown vector store replication handler"""



        try:
            self.logger.info("Shutting down vector store replication handler...")
            
            # Stop monitoring
            self.is_monitoring = False
            
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
            
            # Create final backup
            await self._create_backup()
            
            # Close connections
            if self.weaviate_client:
                # Weaviate doesn't have explicit close method
                self.weaviate_client = None
            
            if self.chroma_client:
                # Chroma doesn't have explicit close method
                self.chroma_client = None
            
            # FAISS and Pinecone don't require explicit connection closing
            
            self.logger.info("Vector store replication handler shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during vector store handler shutdown: {e}")
