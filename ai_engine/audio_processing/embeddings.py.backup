"""🧠 Audio Embeddings Module - Advanced Audio Similarity Engine

Professional audio embeddings generation and similarity matching for the IA Influencer Agent platform.
Implements state-of-the-art deep learning models for audio representation learning.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import pickle
from pathlib import Path
import hashlib
from dataclasses import dataclass
import time

from .core import AudioFeatures, AudioProcessor
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


@dataclass
class AudioEmbedding:
    """Audio embedding representation with metadata"""
    embedding: np.ndarray
    audio_id: str
    features: Optional[AudioFeatures] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = None
    model_version: str = "1.0"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class SimilarityResult:
    """Audio similarity matching result"""
    target_id: str
    similarity_score: float
    distance: float
    features_similarity: Optional[Dict[str, float]] = None
    embedding_dimension: int = 0


class AudioEmbeddingModel(nn.Module):
    """
    🧠 Deep Audio Embedding Neural Network
    
    Advanced CNN-based architecture for learning audio representations:
    - Multi-scale temporal convolutions
    - Attention mechanisms
    - Residual connections
    - Contrastive learning optimization
    """
    
    def __init__(self, 
                 input_features: int = 128,
                 embedding_dim: int = 512,
                 hidden_dims: List[int] = [256, 256, 256],
                 dropout: float = 0.3):
        super().__init__()
        
        self.embedding_dim = embedding_dim
        
        # Feature preprocessing
        self.input_norm = nn.BatchNorm1d(input_features)
        
        # Convolutional encoder
        self.conv_layers = nn.ModuleList()
        in_channels = 1
        
        for hidden_dim in hidden_dims:
            self.conv_layers.append(
                nn.Sequential(
                    nn.Conv1d(in_channels, hidden_dim, kernel_size=3, padding=1),
                    nn.BatchNorm1d(hidden_dim),
                    nn.ReLU(inplace=True),
                    nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1),
                    nn.BatchNorm1d(hidden_dim),
                    nn.ReLU(inplace=True),
                    nn.MaxPool1d(2),
                    nn.Dropout(dropout)
                )
            )
            in_channels = hidden_dim
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dims[-1],
            num_heads=8,
            dropout=dropout,
            batch_first=True
        )
        
        # Final embedding projection
        self.embedding_head = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(hidden_dims[-1], embedding_dim * 2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim * 2, embedding_dim),
            nn.Tanh()  # Bounded output for stable embeddings
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize model weights using Xavier initialization"""
        for module in self.modules():
            if isinstance(module, (nn.Conv1d, nn.Linear)):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the embedding model
        
        Args:
            x: Input audio features [batch_size, features, time]
            
        Returns:
            Audio embeddings [batch_size, embedding_dim]
        """
        batch_size = x.size(0)
        
        # Normalize input features
        x = self.input_norm(x)
        
        # Add channel dimension if needed
        if x.dim() == 2:
            x = x.unsqueeze(1)
        
        # Convolutional encoding
        for conv_layer in self.conv_layers:
            residual = x
            x = conv_layer(x)
            
            # Residual connection if dimensions match
            if residual.shape == x.shape:
                x = x + residual
        
        # Prepare for attention
        x = x.transpose(1, 2)  # [batch, time, features]
        
        # Self-attention
        attended, _ = self.attention(x, x, x)
        x = x + attended  # Residual connection
        
        # Back to conv format
        x = x.transpose(1, 2)  # [batch, features, time]
        
        # Generate final embedding
        embedding = self.embedding_head(x)
        
        # L2 normalize for cosine similarity
        embedding = F.normalize(embedding, p=2, dim=1)
        
        return embedding


class AudioEmbeddingGenerator:
    """
    🎵 Professional Audio Embedding Generator
    
    High-performance audio embedding generation system:
    - Deep learning-based feature extraction
    - Batch processing optimization
    - Model versioning and management
    - GPU acceleration support
    - Cached embedding storage
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None,
                 model_path: Optional[Path] = None):
        self.config = config or AudioProcessingConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize model
        self.model = AudioEmbeddingModel(
            embedding_dim=self.config.embedding_dim,
            dropout=0.1  # Lower dropout for inference
        ).to(self.device)
        
        self.audio_processor = AudioProcessor(config)
        
        # Load pre-trained model if available
        if model_path and model_path.exists():
            self._load_model(model_path)
        else:
            logger.warning("No pre-trained model found. Using random initialization.")
        
        # Embedding cache
        self.embedding_cache: Dict[str, AudioEmbedding] = {}
        
        logger.info(f"AudioEmbeddingGenerator initialized on {self.device}")
    
    def _load_model(self, model_path: Path):
        """Load pre-trained model weights"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            logger.info(f"Loaded model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def _save_model(self, model_path: Path, metadata: Dict[str, Any] = None):
        """Save model checkpoint"""
        try:
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            checkpoint = {
                'model_state_dict': self.model.state_dict(),
                'config': {
                    'embedding_dim': self.config.embedding_dim,
                    'model_version': "1.0"
                },
                'metadata': metadata or {}
            }
            
            torch.save(checkpoint, model_path)
            logger.info(f"Saved model to {model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    async def generate_embedding(self,
                               audio_data: np.ndarray,
                               sample_rate: int,
                               audio_id: Optional[str] = None,
                               use_cache: bool = True) -> AudioEmbedding:
        """
        Generate audio embedding for input audio
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            audio_id: Unique identifier for caching
            use_cache: Whether to use cached embeddings
            
        Returns:
            AudioEmbedding object
        """
        try:
            # Generate audio ID if not provided
            if audio_id is None:
                audio_hash = hashlib.md5(audio_data.tobytes()).hexdigest()
                audio_id = f"audio_{audio_hash[:12]}"
            
            # Check cache first
            if use_cache and audio_id in self.embedding_cache:
                logger.debug(f"Using cached embedding for {audio_id}")
                return self.embedding_cache[audio_id]
            
            # Extract features for embedding
            features = await self._extract_embedding_features(audio_data, sample_rate)
            
            # Convert to tensor
            feature_tensor = torch.from_numpy(features).float().unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                self.model.eval()
                embedding_tensor = self.model(feature_tensor)
                embedding = embedding_tensor.cpu().numpy().squeeze()
            
            # Create embedding object
            audio_embedding = AudioEmbedding(
                embedding=embedding,
                audio_id=audio_id,
                model_version="1.0"
            )
            
            # Cache the embedding
            if use_cache:
                self.embedding_cache[audio_id] = audio_embedding
            
            logger.debug(f"Generated embedding for {audio_id}, dimension: {len(embedding)}")
            return audio_embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    async def _extract_embedding_features(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int) -> np.ndarray:
        """Extract features optimized for embedding generation"""
        try:
            import librosa
            
            # Ensure consistent length for embedding
            target_length = int(30 * sample_rate)  # 30 seconds max
            if len(audio_data) > target_length:
                # Take middle section for consistency
                start = (len(audio_data) - target_length) // 2
                audio_data = audio_data[start:start + target_length]
            elif len(audio_data) < target_length:
                # Pad with zeros
                padding = target_length - len(audio_data)
                audio_data = np.pad(audio_data, (0, padding), mode='constant')
            
            # Extract comprehensive features
            # MFCC features (26 coefficients for richer representation)
            mfcc = librosa.feature.mfcc(
                y=audio_data, 
                sr=sample_rate, 
                n_mfcc=26,
                hop_length=512
            )
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data,
                sr=sample_rate,
                n_mels=64,
                hop_length=512
            )
            mel_spec_db = librosa.power_to_db(mel_spec)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(
                y=audio_data,
                sr=sample_rate,
                hop_length=512
            )
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(
                y=audio_data,
                sr=sample_rate,
                hop_length=512
            )
            
            # Tonnetz (harmonic network)
            tonnetz = librosa.feature.tonnetz(
                y=audio_data,
                sr=sample_rate
            )
            
            # Combine all features
            features = np.vstack([
                mfcc,
                mel_spec_db,
                chroma,
                contrast,
                tonnetz
            ])
            
            # Normalize features
            features = (features - np.mean(features, axis=1, keepdims=True)) / (
                np.std(features, axis=1, keepdims=True) + 1e-8
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction for embedding failed: {e}")
            raise
    
    async def generate_batch_embeddings(self,
                                      audio_files: List[Tuple[str, np.ndarray, int]],
                                      batch_size: int = 8) -> List[AudioEmbedding]:
        """Generate embeddings for multiple audio files efficiently"""
        try:
            embeddings = []
            
            for i in range(0, len(audio_files), batch_size):
                batch = audio_files[i:i + batch_size]
                batch_embeddings = []
                
                # Process batch
                for audio_id, audio_data, sample_rate in batch:
                    embedding = await self.generate_embedding(
                        audio_data, sample_rate, audio_id
                    )
                    batch_embeddings.append(embedding)
                
                embeddings.extend(batch_embeddings)
                
                # Log progress
                logger.info(f"Processed {min(i + batch_size, len(audio_files))}/{len(audio_files)} audio files")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise
    
    def save_embeddings(self, embeddings: List[AudioEmbedding], output_path: Path):
        """Save embeddings to disk"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                pickle.dump(embeddings, f)
            
            logger.info(f"Saved {len(embeddings)} embeddings to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
    
    def load_embeddings(self, input_path: Path) -> List[AudioEmbedding]:
        """Load embeddings from disk"""
        try:
            with open(input_path, 'rb') as f:
                embeddings = pickle.load(f)
            
            logger.info(f"Loaded {len(embeddings)} embeddings from {input_path}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return []


class SimilarityMatcher:
    """
    🔍 Advanced Audio Similarity Matcher
    
    Professional similarity matching system:
    - Multi-metric similarity calculation
    - Efficient nearest neighbor search
    - Similarity threshold filtering
    - Batch similarity computation
    - Advanced ranking algorithms
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        self.embeddings_db: List[AudioEmbedding] = []
        self.embedding_matrix: Optional[np.ndarray] = None
        self.audio_ids: List[str] = []
        
        # PCA for dimensionality reduction if needed
        self.pca: Optional[PCA] = None
        self.use_pca = False
        
        logger.info("SimilarityMatcher initialized")
    
    def add_embeddings(self, embeddings: List[AudioEmbedding]):
        """Add embeddings to the similarity database"""
        try:
            self.embeddings_db.extend(embeddings)
            self._rebuild_embedding_matrix()
            
            logger.info(f"Added {len(embeddings)} embeddings. Total: {len(self.embeddings_db)}")
            
        except Exception as e:
            logger.error(f"Failed to add embeddings: {e}")
    
    def _rebuild_embedding_matrix(self):
        """Rebuild the embedding matrix for efficient similarity computation"""
        try:
            if not self.embeddings_db:
                return
            
            # Extract embeddings and IDs
            embeddings = [emb.embedding for emb in self.embeddings_db]
            self.audio_ids = [emb.audio_id for emb in self.embeddings_db]
            
            # Create matrix
            self.embedding_matrix = np.vstack(embeddings)
            
            # Apply PCA if dimensionality is too high
            if self.embedding_matrix.shape[1] > 1024 and len(self.embeddings_db) > 100:
                if self.pca is None:
                    self.pca = PCA(n_components=512, random_state=42)
                    self.embedding_matrix = self.pca.fit_transform(self.embedding_matrix)
                    self.use_pca = True
                    logger.info("Applied PCA for dimensionality reduction")
                else:
                    self.embedding_matrix = self.pca.transform(self.embedding_matrix)
            
            # Normalize for cosine similarity
            self.embedding_matrix = self.embedding_matrix / (
                np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True) + 1e-8
            )
            
            logger.debug(f"Rebuilt embedding matrix: {self.embedding_matrix.shape}")
            
        except Exception as e:
            logger.error(f"Failed to rebuild embedding matrix: {e}")
    
    async def find_similar(self,
                         query_embedding: AudioEmbedding,
                         top_k: int = 10,
                         similarity_threshold: float = 0.5,
                         exclude_self: bool = True) -> List[SimilarityResult]:
        """
        Find similar audio tracks based on embedding similarity
        
        Args:
            query_embedding: Query audio embedding
            top_k: Number of top similar tracks to return
            similarity_threshold: Minimum similarity score
            exclude_self: Whether to exclude the query track itself
            
        Returns:
            List of similarity results sorted by similarity score
        """
        try:
            if self.embedding_matrix is None or len(self.embeddings_db) == 0:
                logger.warning("No embeddings in database")
                return []
            
            # Prepare query embedding
            query_vector = query_embedding.embedding.reshape(1, -1)
            
            # Apply PCA if used for database
            if self.use_pca and self.pca is not None:
                query_vector = self.pca.transform(query_vector)
            
            # Normalize query
            query_vector = query_vector / (np.linalg.norm(query_vector) + 1e-8)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_vector, self.embedding_matrix)[0]
            
            # Calculate distances (1 - similarity for easier interpretation)
            distances = 1 - similarities
            
            # Create results
            results = []
            for i, (similarity, distance) in enumerate(zip(similarities, distances)):
                audio_id = self.audio_ids[i]
                
                # Skip self if requested
                if exclude_self and audio_id == query_embedding.audio_id:
                    continue
                
                # Filter by threshold
                if similarity >= similarity_threshold:
                    result = SimilarityResult(
                        target_id=audio_id,
                        similarity_score=float(similarity),
                        distance=float(distance),
                        embedding_dimension=self.embedding_matrix.shape[1]
                    )
                    results.append(result)
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Return top-k results
            results = results[:top_k]
            
            logger.debug(f"Found {len(results)} similar tracks for {query_embedding.audio_id}")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    async def find_similar_batch(self,
                               query_embeddings: List[AudioEmbedding],
                               top_k: int = 10,
                               similarity_threshold: float = 0.5) -> Dict[str, List[SimilarityResult]]:
        """Find similar tracks for multiple queries efficiently"""
        try:
            results = {}
            
            for query_embedding in query_embeddings:
                similar_tracks = await self.find_similar(
                    query_embedding, top_k, similarity_threshold
                )
                results[query_embedding.audio_id] = similar_tracks
            
            logger.info(f"Processed similarity search for {len(query_embeddings)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Batch similarity search failed: {e}")
            return {}
    
    def get_similarity_statistics(self) -> Dict[str, Any]:
        """Get statistics about the similarity database"""
        try:
            if not self.embeddings_db:
                return {"total_embeddings": 0}
            
            embeddings = [emb.embedding for emb in self.embeddings_db]
            embedding_matrix = np.vstack(embeddings)
            
            stats = {
                "total_embeddings": len(self.embeddings_db),
                "embedding_dimension": embedding_matrix.shape[1],
                "mean_norm": float(np.mean(np.linalg.norm(embedding_matrix, axis=1))),
                "std_norm": float(np.std(np.linalg.norm(embedding_matrix, axis=1))),
                "pca_applied": self.use_pca,
                "pca_components": self.pca.n_components_ if self.pca else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get similarity statistics: {e}")
            return {"error": str(e)}
    
    def clear_database(self):
        """Clear the similarity database"""
        self.embeddings_db = []
        self.embedding_matrix = None
        self.audio_ids = []
        self.pca = None
        self.use_pca = False
        
        logger.info("Cleared similarity database")
    
    async def compute_similarity_matrix(self, 
                                      embeddings: List[AudioEmbedding]) -> np.ndarray:
        """Compute full similarity matrix for a set of embeddings"""
        try:
            if not embeddings:
                return np.array([])
            
            # Extract embeddings
            embedding_matrix = np.vstack([emb.embedding for emb in embeddings])
            
            # Normalize
            embedding_matrix = embedding_matrix / (
                np.linalg.norm(embedding_matrix, axis=1, keepdims=True) + 1e-8
            )
            
            # Compute similarity matrix
            similarity_matrix = cosine_similarity(embedding_matrix)
            
            logger.debug(f"Computed similarity matrix: {similarity_matrix.shape}")
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Similarity matrix computation failed: {e}")
            return np.array([])
