"""Advanced Vector Database Management
High-performance similarity search using FAISS with intelligent indexing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import os
import pickle
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime

# FAISS for vector similarity search
import faiss

from ..config import settings
from ..core.logging import logger
from ..core.cache import cache_manager


class VectorIndex:
    """Manages a single FAISS vector index for a specific content type"""    
    def __init__(self, content_type: str, dimension: int):
        self.content_type = content_type
        self.dimension = dimension
        self.index = None
        self.metadata = {}  # Maps vector IDs to metadata
        self.id_mapping = {}  # Maps external IDs to internal FAISS IDs
        self.reverse_mapping = {}  # Maps internal FAISS IDs to external IDs
        self.next_id = 0
        
        # Index configuration
        self.index_type = "IVF"  # Default to IVF for large datasets
        self.nlist = 100  # Number of clusters for IVF
        self.nprobe = 10  # Number of clusters to search
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index based on content type and size"""        if self.content_type in ["audio", "text"]:
            # For high-dimensional data, use IVF with PQ
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFPQ(quantizer, self.dimension, self.nlist, 8, 8)
        elif self.content_type in ["image", "video"]:
            # For image/video, use HNSW for better recall
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 200
            self.index.hnsw.efSearch = 50
        else:
            # Default to flat index for small datasets
            self.index = faiss.IndexFlatL2(self.dimension)
        
        logger.info(f"Initialized {self.index.__class__.__name__} for {self.content_type} content")
    
    async def add_vector(self, vector: np.ndarray, external_id: str, metadata: Dict[str, Any]) -> bool:
        """Add a vector to the index"""        try:
            # Normalize vector
            vector = vector.astype(np.float32)
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            
            # Check dimension
            if vector.shape[1] != self.dimension:
                logger.error(f"Vector dimension {vector.shape[1]} doesn't match index dimension {self.dimension}")
                return False
            
            # Train index if necessary (for IVF indexes)
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                if self.index.ntotal < self.nlist:
                    # Not enough vectors to train, use flat index temporarily
                    temp_index = faiss.IndexFlatL2(self.dimension)
                    temp_index.add(vector)
                    self.index = temp_index
                else:
                    self.index.train(vector)
            
            # Add vector to index
            internal_id = self.next_id
            self.index.add(vector)
            
            # Update mappings and metadata
            self.id_mapping[external_id] = internal_id
            self.reverse_mapping[internal_id] = external_id
            self.metadata[external_id] = metadata
            self.next_id += 1
            
            logger.info(f"Added vector for {external_id} to {self.content_type} index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector to index: {str(e)}")
            return False
    
    async def search_similar(self, query_vector: np.ndarray, k: int = 10, 
                           threshold: float = None) -> List[Dict[str, Any]]:
        """Search for similar vectors"""        try:
            # Normalize query vector
            query_vector = query_vector.astype(np.float32)
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Check if index is empty
            if self.index.ntotal == 0:
                return []
            
            # Set search parameters for IVF indexes
            if hasattr(self.index, 'nprobe'):
                self.index.nprobe = min(self.nprobe, self.index.ntotal)
            
            # Search
            distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Process results
            results = []
            for distance, internal_id in zip(distances[0], indices[0]):
                if internal_id == -1:  # No more results
                    break
                
                # Apply threshold if specified
                similarity_score = 1.0 / (1.0 + distance)  # Convert distance to similarity
                if threshold and similarity_score < threshold:
                    continue
                
                # Get external ID and metadata
                external_id = self.reverse_mapping.get(internal_id)
                if external_id:
                    result = {
                        "id": external_id,
                        "similarity_score": float(similarity_score),
                        "distance": float(distance),
                        "metadata": self.metadata.get(external_id, {})
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def remove_vector(self, external_id: str) -> bool:
        """Remove a vector from the index (marks as removed)"""        try:
            if external_id not in self.id_mapping:
                return False
            
            # Remove from mappings and metadata
            internal_id = self.id_mapping.pop(external_id)
            self.reverse_mapping.pop(internal_id, None)
            self.metadata.pop(external_id, None)
            
            # Note: FAISS doesn't support direct removal, so we mark as removed
            # For production, consider rebuilding index periodically
            
            logger.info(f"Removed vector {external_id} from {self.content_type} index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove vector: {str(e)}")
            return False
    
    async def update_metadata(self, external_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a vector"""        try:
            if external_id in self.metadata:
                self.metadata[external_id].update(metadata)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""        return {
            "content_type": self.content_type,
            "dimension": self.dimension,
            "total_vectors": self.index.ntotal,
            "index_type": self.index.__class__.__name__,
            "is_trained": getattr(self.index, 'is_trained', True),
            "memory_usage_mb": self.index.ntotal * self.dimension * 4 / (1024 * 1024)  # Approximate
        }
    
    async def save_to_disk(self, path: str) -> bool:
        """Save index and metadata to disk"""        try:
            # Create directory if not exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{path}.index")
            
            # Save metadata and mappings
            metadata_dict = {
                "metadata": self.metadata,
                "id_mapping": self.id_mapping,
                "reverse_mapping": {str(k): v for k, v in self.reverse_mapping.items()},
                "next_id": self.next_id,
                "content_type": self.content_type,
                "dimension": self.dimension
            }
            
            with open(f"{path}.meta", 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            
            logger.info(f"Saved {self.content_type} index to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            return False
    
    async def load_from_disk(self, path: str) -> bool:
        """Load index and metadata from disk"""        try:
            # Load FAISS index
            if not os.path.exists(f"{path}.index"):
                return False
            
            self.index = faiss.read_index(f"{path}.index")
            
            # Load metadata and mappings
            if os.path.exists(f"{path}.meta"):
                with open(f"{path}.meta", 'r') as f:
                    metadata_dict = json.load(f)
                
                self.metadata = metadata_dict.get("metadata", {})
                self.id_mapping = metadata_dict.get("id_mapping", {})
                self.reverse_mapping = {int(k): v for k, v in metadata_dict.get("reverse_mapping", {}).items()}
                self.next_id = metadata_dict.get("next_id", 0)
            
            logger.info(f"Loaded {self.content_type} index from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            return False


class VectorDatabase:
    """Main vector database manager handling multiple content types"""    
    def __init__(self):
        self.indexes = {}
        self.base_path = Path(settings.ai.faiss_index_path)
        self.dimension = settings.ai.vector_dimension
        self.similarity_threshold = settings.ai.similarity_threshold
        
        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize indexes for each content type
        self.content_types = ["audio", "video", "image", "text"]
    
    async def initialize(self):
        """Initialize vector database and load existing indexes"""        try:
            for content_type in self.content_types:
                # Create index
                index = VectorIndex(content_type, self.dimension)
                
                # Try to load existing index
                index_path = self.base_path / f"{content_type}_index"
                await index.load_from_disk(str(index_path))
                
                self.indexes[content_type] = index
            
            logger.info("Vector database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            raise
    
    async def add_fingerprint(self, content_type: str, content_id: str, 
                            fingerprint_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Add a content fingerprint to the appropriate index"""        try:
            if content_type not in self.indexes:
                logger.error(f"Unsupported content type: {content_type}")
                return False
            
            # Extract vector from fingerprint data
            vector = await self._extract_vector_from_fingerprint(content_type, fingerprint_data)
            if vector is None:
                return False
            
            # Add to index
            index = self.indexes[content_type]
            success = await index.add_vector(vector, content_id, metadata)
            
            # Cache the fingerprint for quick access
            if success:
                cache_key = f"fingerprint:{content_type}:{content_id}"
                await cache_manager.set(cache_key, fingerprint_data, ttl=86400)  # 24 hours
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add fingerprint: {str(e)}")
            return False
    
    async def search_similar_content(self, content_type: str, fingerprint_data: Dict[str, Any],
                                   k: int = 10, threshold: float = None) -> List[Dict[str, Any]]:
        """Search for similar content using fingerprint"""        try:
            if content_type not in self.indexes:
                logger.error(f"Unsupported content type: {content_type}")
                return []
            
            # Extract vector from fingerprint
            query_vector = await self._extract_vector_from_fingerprint(content_type, fingerprint_data)
            if query_vector is None:
                return []
            
            # Use default threshold if not provided
            if threshold is None:
                threshold = self.similarity_threshold
            
            # Search in index
            index = self.indexes[content_type]
            results = await index.search_similar(query_vector, k, threshold)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {str(e)}")
            return []
    
    async def _extract_vector_from_fingerprint(self, content_type: str, 
                                             fingerprint_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract vector representation from fingerprint data"""        try:
            if content_type == "audio":
                # Combine audio features into a single vector
                vector_parts = []
                
                if "mfcc" in fingerprint_data and fingerprint_data["mfcc"]:
                    vector_parts.extend(fingerprint_data["mfcc"][0][:13])  # First 13 MFCCs
                
                if "spectral" in fingerprint_data:
                    vector_parts.extend(fingerprint_data["spectral"][:50])  # First 50 spectral features
                
                if "chroma" in fingerprint_data:
                    vector_parts.extend(fingerprint_data["chroma"][:24])  # 24 chroma features
                
                # Pad or truncate to target dimension
                vector = self._normalize_vector(vector_parts)
                
            elif content_type == "video":
                # Use histogram and edge features
                vector_parts = []
                
                if "histogram" in fingerprint_data and fingerprint_data["histogram"]:
                    # Average histograms across frames
                    avg_hist = np.mean(fingerprint_data["histogram"], axis=0)
                    vector_parts.extend(avg_hist.tolist())
                
                if "edge" in fingerprint_data:
                    vector_parts.extend(fingerprint_data["edge"][:100])  # First 100 edge features
                
                vector = self._normalize_vector(vector_parts)
                
            elif content_type == "image":
                # Use semantic features if available, otherwise use color histogram
                if "semantic" in fingerprint_data and fingerprint_data["semantic"]:
                    vector = np.array(fingerprint_data["semantic"])
                elif "color_histogram" in fingerprint_data:
                    vector = np.array(fingerprint_data["color_histogram"])
                else:
                    return None
                
                vector = self._normalize_vector(vector.tolist())
                
            elif content_type == "text":
                # Use semantic features if available
                if "semantic" in fingerprint_data and fingerprint_data["semantic"]:
                    vector = np.array(fingerprint_data["semantic"])
                else:
                    # Fallback to lexical features
                    vector_parts = []
                    if "lexical" in fingerprint_data:
                        lexical = fingerprint_data["lexical"]
                        vector_parts.extend([
                            lexical.get("vocabulary_size", 0),
                            lexical.get("total_words", 0)
                        ])
                    
                    vector = self._normalize_vector(vector_parts)
                
            else:
                return None
            
            return vector
            
        except Exception as e:
            logger.error(f"Failed to extract vector from fingerprint: {str(e)}")
            return None
    
    def _normalize_vector(self, vector_data: List[float]) -> np.ndarray:
        """Normalize vector to target dimension"""        if not vector_data:
            return np.zeros(self.dimension, dtype=np.float32)
        
        vector = np.array(vector_data, dtype=np.float32)
        
        # Pad or truncate to target dimension
        if len(vector) < self.dimension:
            # Pad with zeros
            padded = np.zeros(self.dimension, dtype=np.float32)
            padded[:len(vector)] = vector
            vector = padded
        elif len(vector) > self.dimension:
            # Truncate
            vector = vector[:self.dimension]
        
        # Normalize to unit length
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    async def remove_content(self, content_type: str, content_id: str) -> bool:
        """Remove content from the vector database"""        try:
            if content_type not in self.indexes:
                return False
            
            index = self.indexes[content_type]
            success = await index.remove_vector(content_id)
            
            # Remove from cache
            if success:
                cache_key = f"fingerprint:{content_type}:{content_id}"
                await cache_manager.delete(cache_key)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove content: {str(e)}")
            return False
    
    async def update_content_metadata(self, content_type: str, content_id: str, 
                                    metadata: Dict[str, Any]) -> bool:
        """Update metadata for existing content"""        try:
            if content_type not in self.indexes:
                return False
            
            index = self.indexes[content_type]
            return await index.update_metadata(content_id, metadata)
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {str(e)}")
            return False
    
    async def get_content_by_id(self, content_type: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content metadata by ID"""        try:
            if content_type not in self.indexes:
                return None
            
            index = self.indexes[content_type]
            return index.metadata.get(content_id)
            
        except Exception as e:
            logger.error(f"Failed to get content: {str(e)}")
            return None
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""        stats = {
            "total_content": 0,
            "content_by_type": {},
            "indexes": {}
        }
        
        for content_type, index in self.indexes.items():
            index_stats = index.get_stats()
            stats["indexes"][content_type] = index_stats
            stats["content_by_type"][content_type] = index_stats["total_vectors"]
            stats["total_content"] += index_stats["total_vectors"]
        
        return stats
    
    async def save_all_indexes(self) -> bool:
        """Save all indexes to disk"""        try:
            success = True
            for content_type, index in self.indexes.items():
                index_path = self.base_path / f"{content_type}_index"
                result = await index.save_to_disk(str(index_path))
                success = success and result
            
            logger.info("All indexes saved to disk")
            return success
            
        except Exception as e:
            logger.error(f"Failed to save indexes: {str(e)}")
            return False
    
    async def optimize_indexes(self) -> bool:
        """Optimize indexes for better performance"""        try:
            for content_type, index in self.indexes.items():
                # For large indexes, consider rebuilding with better parameters
                if index.index.ntotal > 10000:
                    logger.info(f"Optimizing {content_type} index with {index.index.ntotal} vectors")
                    
                    # Adjust nprobe for IVF indexes
                    if hasattr(index.index, 'nprobe'):
                        index.nprobe = min(20, index.index.ntotal // 100)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize indexes: {str(e)}")
            return False
    
    async def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the entire vector database"""        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Save each index with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for content_type, index in self.indexes.items():
                backup_file = backup_dir / f"{content_type}_index_{timestamp}"
                await index.save_to_disk(str(backup_file))
            
            logger.info(f"Database backup created at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return False
    
    async def restore_from_backup(self, backup_path: str, timestamp: str) -> bool:
        """Restore database from backup"""        try:
            backup_dir = Path(backup_path)
            
            for content_type in self.content_types:
                backup_file = backup_dir / f"{content_type}_index_{timestamp}"
                
                if backup_file.with_suffix('.index').exists():
                    index = VectorIndex(content_type, self.dimension)
                    success = await index.load_from_disk(str(backup_file))
                    
                    if success:
                        self.indexes[content_type] = index
                    else:
                        logger.error(f"Failed to restore {content_type} index")
                        return False
            
            logger.info(f"Database restored from backup {timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {str(e)}")
            return False


# Global vector database instance
vector_database = VectorDatabase()